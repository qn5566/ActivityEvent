#!/usr/bin/env python3
"""
App Store & Google Play Promotional Screenshot Generator (International English Edition)
for 'Taiwan Travel Map' (台灣吃喝玩樂地圖)

Complies with:
- Apple App Store Guidelines (6.7" Super Retina Display, 1290 x 2796 px)
- Google Play Store Guidelines (1080 x 2400 px Phone + 1024 x 500 px Feature Graphic)
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshot")
OUTPUT_DIR = os.path.join(BASE_DIR, "store_assets")

IOS_DIR = os.path.join(OUTPUT_DIR, "apple_app_store_6.7_inch")
ANDROID_DIR = os.path.join(OUTPUT_DIR, "google_play_phone")
FEATURE_DIR = os.path.join(OUTPUT_DIR, "google_play_feature")

for d in [IOS_DIR, ANDROID_DIR, FEATURE_DIR]:
    os.makedirs(d, exist_ok=True)

# System Font Paths
EN_TITLE_FONT = "/System/Library/Fonts/Helvetica.ttc"          # Index 1 = Bold
EN_SUB_FONT = "/System/Library/Fonts/Supplemental/Georgia.ttf"
EN_SANS_FONT = "/System/Library/Fonts/Helvetica.ttc"          # Index 0 = Regular
ZH_FALLBACK = "/System/Library/Fonts/Hiragino Sans GB.ttc"

def get_font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()

# Theme Colors (Aurora & Japanese Magazine Palette)
INK_COLOR = (45, 49, 66)            # #2D3142
INK_SOFT = (108, 117, 125)          # #6C757D
CHERRY_PINK = (232, 141, 150)       # #E88D96
SKY_BLUE = (109, 179, 242)          # #6DB3F2
LAVENDER = (216, 180, 248)          # #D8B4F8
PILL_BG = (255, 255, 255, 240)
PILL_BORDER = (232, 141, 150, 180)
FRAME_DARK = (26, 30, 38)
FRAME_BORDER = (55, 62, 75)

def create_aurora_background(width, height, blobs_config=None):
    """Creates a smooth aurora wave gradient background with glowing ambient light orbs."""
    base = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(base)
    
    top_c = (230, 239, 253)   # Soft Sky Blue tint
    mid_c = (245, 238, 252)   # Soft Lavender tint
    bot_c = (255, 234, 238)   # Soft Cherry Blossom tint
    
    half = height // 2
    for y in range(height):
        if y < half:
            t = y / half
            r = int(top_c[0] * (1 - t) + mid_c[0] * t)
            g = int(top_c[1] * (1 - t) + mid_c[1] * t)
            b = int(top_c[2] * (1 - t) + mid_c[2] * t)
        else:
            t = (y - half) / (height - half)
            r = int(mid_c[0] * (1 - t) + bot_c[0] * t)
            g = int(mid_c[1] * (1 - t) + bot_c[1] * t)
            b = int(mid_c[2] * (1 - t) + bot_c[2] * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    blobs_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(blobs_layer)
    
    if not blobs_config:
        blobs_config = [
            {"center": (int(width * 0.12), int(height * 0.22)), "radius": int(width * 0.45), "color": (109, 179, 242, 90)},
            {"center": (int(width * 0.88), int(height * 0.42)), "radius": int(width * 0.50), "color": (232, 141, 150, 95)},
            {"center": (int(width * 0.20), int(height * 0.82)), "radius": int(width * 0.48), "color": (216, 180, 248, 85)},
        ]
        
    for blob in blobs_config:
        cx, cy = blob["center"]
        r = blob["radius"]
        color = blob["color"]
        bdraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
        
    blur_radius = int(width * 0.12)
    blobs_layer = blobs_layer.filter(ImageFilter.GaussianBlur(blur_radius))
    
    return Image.alpha_composite(base, blobs_layer)

def polish_status_bar(screen_img, is_dark_bg=True, is_ios=True):
    """
    Cleans up any Android status bar relics from the original screenshot
    and overlays an official, crisp status bar (9:41, clean battery, cellular).
    """
    polished = screen_img.copy().convert("RGBA")
    draw = ImageDraw.Draw(polished)
    W, H = polished.size
    
    # Status bar area: top 95px
    sb_height = int(H * (95 / 2340))
    
    sample_y = min(H - 1, sb_height + 4)
    bg_left = polished.getpixel((60, sample_y))
    bg_mid = polished.getpixel((W // 2, sample_y))
    bg_right = polished.getpixel((W - 60, sample_y))
    
    for y in range(sb_height):
        for x_span, fill_c in [((0, int(W * 0.35)), bg_left),
                               ((int(W * 0.35), int(W * 0.65)), bg_mid),
                               ((int(W * 0.65), W), bg_right)]:
            draw.line([(x_span[0], y), (x_span[1], y)], fill=fill_c)
            
    color = (255, 255, 255, 245) if is_dark_bg else (35, 40, 50, 245)
    font_time = get_font(EN_TITLE_FONT, int(W * 0.035), index=1)
    
    # 1. Time (9:41)
    time_x = int(W * 0.075)
    time_y = int(sb_height * 0.35)
    draw.text((time_x, time_y), "9:41", fill=color, font=font_time)
    
    # 2. Cellular Signal Bars (4 bars)
    cell_x = int(W * 0.81)
    cell_base_y = int(sb_height * 0.68)
    for i in range(4):
        bar_h = int(sb_height * (0.16 + i * 0.08))
        draw.rounded_rectangle([cell_x + i * 10, cell_base_y - bar_h, cell_x + i * 10 + 6, cell_base_y],
                               radius=2, fill=color)
                               
    # 3. Battery Outline & Level
    bat_x = int(W * 0.88)
    bat_y = int(sb_height * 0.40)
    bat_w = int(W * 0.052)
    bat_h = int(sb_height * 0.28)
    draw.rounded_rectangle([bat_x, bat_y, bat_x + bat_w, bat_y + bat_h], radius=5, outline=color, width=3)
    draw.rounded_rectangle([bat_x + bat_w + 2, bat_y + int(bat_h * 0.25),
                            bat_x + bat_w + 4, bat_y + int(bat_h * 0.75)], radius=1, fill=color)
    fill_w = int((bat_w - 6) * 0.85)
    draw.rounded_rectangle([bat_x + 3, bat_y + 3, bat_x + 3 + fill_w, bat_y + bat_h - 3], radius=2, fill=color)
    
    return polished

def build_phone_mockup(screen_img, target_width, target_height, is_dark_top=True, is_ios=True):
    """
    Renders an edge-to-edge device frame around the polished screen image.
    """
    polished_screen = polish_status_bar(screen_img, is_dark_bg=is_dark_top, is_ios=is_ios)
    polished_screen = polished_screen.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    bezel = int(target_width * 0.024)
    device_w = target_width + bezel * 2
    device_h = target_height + bezel * 2
    
    corner_outer = int(device_w * 0.125)
    corner_inner = int(target_width * 0.105)
    
    screen_mask = Image.new("L", (target_width, target_height), 0)
    mask_draw = ImageDraw.Draw(screen_mask)
    mask_draw.rounded_rectangle([0, 0, target_width, target_height], radius=corner_inner, fill=255)
    
    screen_masked = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
    screen_masked.paste(polished_screen, (0, 0), screen_mask)
    
    device_canvas = Image.new("RGBA", (device_w, device_h), (0, 0, 0, 0))
    dev_draw = ImageDraw.Draw(device_canvas)
    
    dev_draw.rounded_rectangle([0, 0, device_w, device_h], radius=corner_outer, fill=FRAME_DARK)
    dev_draw.rounded_rectangle([0, 0, device_w, device_h], radius=corner_outer, outline=FRAME_BORDER, width=2)
    device_canvas.paste(screen_masked, (bezel, bezel), screen_mask)
    
    dev_screen_draw = ImageDraw.Draw(device_canvas)
    if is_ios:
        island_w = int(target_width * 0.29)
        island_h = int(target_height * 0.032)
        island_x = bezel + (target_width - island_w) // 2
        island_y = bezel + int(target_height * 0.015)
        dev_screen_draw.rounded_rectangle(
            [island_x, island_y, island_x + island_w, island_y + island_h],
            radius=island_h // 2,
            fill=(0, 0, 0, 255)
        )
        lens_r = island_h // 5
        lens_x = island_x + island_w - int(island_h * 0.55)
        lens_y = island_y + island_h // 2
        dev_screen_draw.ellipse(
            [lens_x - lens_r, lens_y - lens_r, lens_x + lens_r, lens_y + lens_r],
            fill=(25, 30, 45, 255)
        )
    else:
        hole_r = int(target_width * 0.018)
        hole_x = bezel + target_width // 2
        hole_y = bezel + int(target_height * 0.022)
        dev_screen_draw.ellipse(
            [hole_x - hole_r, hole_y - hole_r, hole_x + hole_r, hole_y + hole_r],
            fill=(0, 0, 0, 255)
        )
        
    shadow_pad = int(device_w * 0.18)
    shadow_w = device_w + shadow_pad * 2
    shadow_h = device_h + shadow_pad * 2
    
    shadow_canvas = Image.new("RGBA", (shadow_w, shadow_h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_canvas)
    
    sdraw.rounded_rectangle(
        [shadow_pad, shadow_pad + int(device_h * 0.035),
         shadow_pad + device_w, shadow_pad + device_h + int(device_h * 0.035)],
        radius=corner_outer,
        fill=(30, 35, 50, 110)
    )
    sdraw.rounded_rectangle(
        [shadow_pad, shadow_pad + int(device_h * 0.015),
         shadow_pad + device_w, shadow_pad + device_h + int(device_h * 0.015)],
        radius=corner_outer,
        fill=(216, 180, 248, 70)
    )
    
    blur_r = int(device_w * 0.075)
    shadow_canvas = shadow_canvas.filter(ImageFilter.GaussianBlur(blur_r))
    shadow_canvas.paste(device_canvas, (shadow_pad, shadow_pad), device_canvas)
    return shadow_canvas

def render_store_slide(spec, output_path, format_type="ios"):
    """
    Renders an all-English promotional screenshot sheet.
    """
    if format_type == "ios":
        W, H = 1290, 2796
        is_ios = True
        font_pill = get_font(EN_TITLE_FONT, 34, index=1)
        font_title = get_font(EN_TITLE_FONT, 66, index=1)
        font_sub = get_font(EN_SUB_FONT, 36)
        font_tags = get_font(EN_SANS_FONT, 32, index=0)
        
        phone_w = 980
        phone_h = int(phone_w * (2340 / 1080))
    else:
        W, H = 1080, 2400
        is_ios = False
        font_pill = get_font(EN_TITLE_FONT, 30, index=1)
        font_title = get_font(EN_TITLE_FONT, 56, index=1)
        font_sub = get_font(EN_SUB_FONT, 32)
        font_tags = get_font(EN_SANS_FONT, 28, index=0)
        
        phone_w = 840
        phone_h = int(phone_w * (2340 / 1080))

    # 1. Aurora Background
    bg = create_aurora_background(W, H)
    draw = ImageDraw.Draw(bg)
    
    # 2. Typography Header
    # Pill Badge
    pill_text = spec["pill"]
    pill_bbox = draw.textbbox((0, 0), pill_text, font=font_pill)
    pill_tw = pill_bbox[2] - pill_bbox[0]
    pill_th = pill_bbox[3] - pill_bbox[1]
    
    pad_x = int(W * 0.035)
    pad_y = int(H * 0.007)
    pill_w = pill_tw + pad_x * 2
    pill_h = pill_th + pad_y * 2
    pill_x = (W - pill_w) // 2
    pill_y = int(H * 0.060)
    
    draw.rounded_rectangle(
        [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
        radius=pill_h // 2,
        fill=PILL_BG,
        outline=PILL_BORDER,
        width=2
    )
    pill_tx = pill_x + (pill_w - pill_tw) // 2 - pill_bbox[0]
    pill_ty = pill_y + (pill_h - pill_th) // 2 - pill_bbox[1]
    draw.text((pill_tx, pill_ty), pill_text, fill=CHERRY_PINK, font=font_pill)
    
    # Main Title
    title_text = spec["title"]
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_tw = title_bbox[2] - title_bbox[0]
    title_x = (W - title_tw) // 2
    title_y = pill_y + pill_h + int(H * 0.020)
    draw.text((title_x, title_y), title_text, fill=INK_COLOR, font=font_title)
    
    # Subtitle
    sub_text = spec["subtitle"]
    sub_bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    sub_tw = sub_bbox[2] - sub_bbox[0]
    sub_x = (W - sub_tw) // 2
    sub_y = title_y + (title_bbox[3] - title_bbox[1]) + int(H * 0.016)
    draw.text((sub_x, sub_y), sub_text, fill=INK_SOFT, font=font_sub)
    
    # Bullet Tags
    tags_text = spec["tags"]
    tags_bbox = draw.textbbox((0, 0), tags_text, font=font_tags)
    tags_tw = tags_bbox[2] - tags_bbox[0]
    tags_x = (W - tags_tw) // 2
    tags_y = sub_y + (sub_bbox[3] - sub_bbox[1]) + int(H * 0.015)
    draw.text((tags_x, tags_y), tags_text, fill=(70, 80, 105), font=font_tags)
    
    # 3. Build & Paste Phone Mockup
    src_img = Image.open(spec["src"])
    mockup = build_phone_mockup(
        src_img, phone_w, phone_h,
        is_dark_top=spec.get("is_dark_top", False),
        is_ios=is_ios
    )
    
    mockup_x = (W - mockup.width) // 2
    mockup_y = tags_y + (tags_bbox[3] - tags_bbox[1]) + int(H * 0.028)
    
    bg.paste(mockup, (mockup_x, mockup_y), mockup)
    
    final_output = bg.convert("RGB")
    final_output.save(output_path, "PNG", quality=95)
    print(f"[{format_type.upper()}] Generated: {os.path.basename(output_path)} ({W}x{H})")

def render_feature_graphic(output_path):
    """
    Renders Google Play Store Feature Graphic (1024 x 500 px) in English.
    """
    W, H = 1024, 500
    bg = create_aurora_background(W, H, blobs_config=[
        {"center": (int(W * 0.20), int(H * 0.40)), "radius": 220, "color": (109, 179, 242, 120)},
        {"center": (int(W * 0.78), int(H * 0.50)), "radius": 250, "color": (232, 141, 150, 110)},
        {"center": (int(W * 0.45), int(H * 0.85)), "radius": 200, "color": (216, 180, 248, 100)},
    ])
    draw = ImageDraw.Draw(bg)
    
    font_brand = get_font(EN_TITLE_FONT, 42, index=1)
    font_en = get_font(EN_SUB_FONT, 20)
    font_lead = get_font(EN_SANS_FONT, 21, index=0)
    font_badge = get_font(EN_TITLE_FONT, 16, index=1)
    font_note = get_font(EN_SANS_FONT, 16, index=0)
    
    # App Icon (New Icon from screenshot/icon.png)
    icon_path = os.path.join(SCREENSHOT_DIR, "icon.png")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(BASE_DIR, "res", "images", "icon", "main_icon.webp")
        
    if os.path.exists(icon_path):
        icon_size = 96
        icon = Image.open(icon_path).convert("RGBA").resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        
        # Soft shadow matching icon's actual alpha silhouette
        shadow_pad = 20
        shadow_w = icon_size + shadow_pad * 2
        shadow_h = icon_size + shadow_pad * 2
        icon_shadow = Image.new("RGBA", (shadow_w, shadow_h), (0, 0, 0, 0))
        
        r, g, b, a = icon.split()
        shadow_alpha = a.point(lambda p: int(p * 0.35))
        shadow_layer = Image.new("RGBA", (icon_size, icon_size), (30, 35, 50, 255))
        shadow_layer.putalpha(shadow_alpha)
        
        icon_shadow.paste(shadow_layer, (shadow_pad, shadow_pad + 4), shadow_layer)
        icon_shadow = icon_shadow.filter(ImageFilter.GaussianBlur(8))
        
        icon_x = 50
        icon_y = 65
        bg.paste(icon_shadow, (icon_x - shadow_pad, icon_y - shadow_pad), icon_shadow)
        bg.paste(icon, (icon_x, icon_y), icon)
    
    # Left Brand Text
    tx = 175
    draw.text((tx, 72), "TAIWAN TRAVEL MAP", fill=INK_COLOR, font=font_brand)
    draw.text((tx, 130), "EXPLORE TAIWAN LIKE A LOCAL", fill=CHERRY_PINK, font=font_en)
    draw.text((65, 200), "Discover Hidden Attractions, Festivals & Vintage Cafes", fill=INK_COLOR, font=font_lead)
    
    # Feature Badges
    pills = ["📍 Hidden Gems", "🎪 Live Events", "☕ Historic Cafes", "🚗 Charters"]
    px = 65
    py = 258
    for p in pills:
        pb = draw.textbbox((0, 0), p, font=font_badge)
        pw = pb[2] - pb[0] + 30
        ph = 40
        draw.rounded_rectangle([px, py, px + pw, py + ph], radius=20, fill=PILL_BG, outline=PILL_BORDER, width=1)
        draw.text((px + 15, py + 10), p, fill=INK_COLOR, font=font_badge)
        px += pw + 12
        
    draw.text((65, 340), "✦ Available in 11 Languages  •  Nationwide Guide  •  Free Download", fill=INK_SOFT, font=font_note)
    
    # Right Side: Dual Floating Phone Devices
    src_1 = os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_114613.png") # Taiping Mountain
    src_2 = os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_114636.png") # Curated Themes
    
    if os.path.exists(src_1) and os.path.exists(src_2):
        im1 = Image.open(src_1)
        im2 = Image.open(src_2)
        
        m1 = build_phone_mockup(im1, 230, int(230 * 2.16), is_dark_top=True, is_ios=False)
        m2 = build_phone_mockup(im2, 230, int(230 * 2.16), is_dark_top=False, is_ios=False)
        
        bg.paste(m2, (765, 45), m2)
        bg.paste(m1, (635, 75), m1)
        
    final_output = bg.convert("RGB")
    final_output.save(output_path, "PNG", quality=95)
    print(f"[FEATURE GRAPHIC] Generated: {os.path.basename(output_path)} ({W}x{H})")

# 5 All-English Curated Storyline Screens
SCREEN_SPECS = [
    {
        "pill": "01 • DESTINATIONS",
        "title": "Discover Hidden Taiwan Gems",
        "subtitle": "Forest trails, hot springs & in-depth historical stories",
        "tags": "📍 Forest Trails   •   ♨ Hot Springs   •   📖 Local Heritage",
        "src": os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_114613.png"),
        "is_dark_top": True,
        "filename": "01_destinations.png"
    },
    {
        "pill": "02 • CURATED THEMES",
        "title": "Curated Travel Experiences",
        "subtitle": "Jiufen coast, Taroko gorge, island hopping & glamping",
        "tags": "🌊 Coastal Roadtrips   •   🏕 Glamping   •   🏝 Island Escapes",
        "src": os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_114636.png"),
        "is_dark_top": False,
        "filename": "02_themes.png"
    },
    {
        "pill": "03 • EVENTS & FESTIVALS",
        "title": "Top Nationwide Events",
        "subtitle": "Marathons, cultural festivals & direct private transfers",
        "tags": "🏃 Global Marathons   •   🚗 Private Transfers   •   📅 Live Calendar",
        "src": os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_115128.png"),
        "is_dark_top": True,
        "filename": "03_events.png"
    },
    {
        "pill": "04 • CAFES & LIFESTYLE",
        "title": "Historic Cafes & City Walks",
        "subtitle": "Explore Chihfeng vintage alleys, artisan coffee & desserts",
        "tags": "☕ Specialty Coffee   •   🍮 Artisan Desserts   •   📸 City Walks",
        "src": os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_115414.png"),
        "is_dark_top": True,
        "filename": "04_lifestyle.png"
    },
    {
        "pill": "05 • TRAVEL ESSENTIALS",
        "title": "All Your Travel Essentials",
        "subtitle": "11 languages supported • SIM & eSIM, charters & tickets",
        "tags": "📶 SIM & eSIM Cards   •   🌐 11 Languages   •   🚖 Airport Transfers",
        "src": os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_114548.png"),
        "is_dark_top": False,
        "filename": "05_essentials.png"
    }
]

def main():
    print("=" * 65)
    print("Generating English International Store Assets for 'Taiwan Travel Map'...")
    print("=" * 65)
    
    # 1. Apple App Store 6.7" (1290 x 2796)
    print("\n[1/3] Generating Apple App Store 6.7\" Screenshots (1290x2796)...")
    for spec in SCREEN_SPECS:
        out_path = os.path.join(IOS_DIR, spec["filename"])
        render_store_slide(spec, out_path, format_type="ios")
        
    # 2. Google Play Phone (1080 x 2400)
    print("\n[2/3] Generating Google Play Store Phone Screenshots (1080x2400)...")
    for spec in SCREEN_SPECS:
        out_path = os.path.join(ANDROID_DIR, spec["filename"])
        render_store_slide(spec, out_path, format_type="android")
        
    # 3. Google Play Feature Graphic (1024 x 500)
    print("\n[3/3] Generating Google Play Feature Graphic (1024x500)...")
    fg_path = os.path.join(FEATURE_DIR, "google_play_feature_graphic_1024x500.png")
    render_feature_graphic(fg_path)
    
    # 4. Synchronize new icon to res/images/icon/main_icon.webp and feature graphic
    icon_new_path = os.path.join(SCREENSHOT_DIR, "icon.png")
    if os.path.exists(icon_new_path):
        res_icon = os.path.join(BASE_DIR, "res", "images", "icon", "main_icon.webp")
        Image.open(icon_new_path).convert("RGBA").save(res_icon, "WEBP", quality=95)
        print(f"[SYNC] Updated {os.path.relpath(res_icon, BASE_DIR)} with new icon.png")
        
    res_fg = os.path.join(BASE_DIR, "res", "images", "pics", "feature_graphic.webp")
    if os.path.exists(fg_path):
        Image.open(fg_path).save(res_fg, "WEBP", quality=95)
        print(f"[SYNC] Updated {os.path.relpath(res_fg, BASE_DIR)} with new feature graphic")
    
    print("\n" + "=" * 65)
    print("All English store assets successfully created!")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 65)

if __name__ == "__main__":
    main()
