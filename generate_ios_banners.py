#!/usr/bin/env python3
"""
App Store Connect Custom Product Page & Promotional Artwork Generator
Generates:
1. Header Banner (標題素材): 3840 x 1646 px (and optional 5244 x 2950)
2. Search Results Banner (搜尋結果素材): 3840 x 2560 px and 1920 x 1280 px
Strictly compliant with Apple App Store specifications:
- No emojis
- No price/badge imitation
- High-resolution RGB 24-bit PNG
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from generate_store_assets import (
    BASE_DIR, SCREENSHOT_DIR, OUTPUT_DIR,
    create_aurora_background, build_phone_mockup, get_font,
    EN_TITLE_FONT, EN_SUB_FONT, EN_SANS_FONT,
    INK_COLOR, INK_SOFT, CHERRY_PINK, SKY_BLUE, LAVENDER, PILL_BG, PILL_BORDER
)

BANNER_DIR = os.path.join(OUTPUT_DIR, "apple_app_store_banners")
os.makedirs(BANNER_DIR, exist_ok=True)

def render_header_banner(output_path):
    """
    Renders the Header Banner (標題素材) for App Store Connect.
    Supported size: 3840 x 1646 px (21:9 cinematic wide ratio).
    """
    W, H = 3840, 1646
    print(f"Rendering Header Banner ({W}x{H})...")
    
    # 1. Wide Aurora Background
    bg = create_aurora_background(W, H, blobs_config=[
        {"center": (int(W * 0.18), int(H * 0.35)), "radius": 750, "color": (109, 179, 242, 110)},
        {"center": (int(W * 0.55), int(H * 0.65)), "radius": 850, "color": (216, 180, 248, 100)},
        {"center": (int(W * 0.85), int(H * 0.35)), "radius": 900, "color": (232, 141, 150, 115)},
    ])
    draw = ImageDraw.Draw(bg)
    
    # Fonts
    font_pill = get_font(EN_TITLE_FONT, 38, index=1)
    font_brand = get_font(EN_TITLE_FONT, 118, index=1)
    font_sub = get_font(EN_SUB_FONT, 56)
    font_lead = get_font(EN_SANS_FONT, 42, index=0)
    font_badge = get_font(EN_TITLE_FONT, 32, index=1)
    font_footer = get_font(EN_SANS_FONT, 34, index=0)
    
    # Left Content Positioning
    left_x = 220
    
    # App Icon (New Icon from screenshot/icon.png)
    icon_path = os.path.join(SCREENSHOT_DIR, "icon.png")
    icon_size = 220
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert("RGBA").resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        
        # Soft shadow
        shadow_pad = 40
        shadow_w = icon_size + shadow_pad * 2
        shadow_h = icon_size + shadow_pad * 2
        icon_shadow = Image.new("RGBA", (shadow_w, shadow_h), (0, 0, 0, 0))
        
        r, g, b, a = icon.split()
        shadow_alpha = a.point(lambda p: int(p * 0.35))
        shadow_layer = Image.new("RGBA", (icon_size, icon_size), (30, 35, 50, 255))
        shadow_layer.putalpha(shadow_alpha)
        
        icon_shadow.paste(shadow_layer, (shadow_pad, shadow_pad + 10), shadow_layer)
        icon_shadow = icon_shadow.filter(ImageFilter.GaussianBlur(18))
        
        icon_y = 260
        bg.paste(icon_shadow, (left_x - shadow_pad, icon_y - shadow_pad), icon_shadow)
        bg.paste(icon, (left_x, icon_y), icon)
    
    # Pill Tag above title
    pill_text = "TAIWAN TRAVEL & LIFESTYLE GUIDE"
    pb = draw.textbbox((0, 0), pill_text, font=font_pill)
    pw = pb[2] - pb[0] + 60
    ph = 64
    py = 530
    draw.rounded_rectangle([left_x, py, left_x + pw, py + ph], radius=32, fill=PILL_BG, outline=PILL_BORDER, width=2)
    draw.text((left_x + 30, py + 14), pill_text, fill=CHERRY_PINK, font=font_pill)
    
    # Brand Main Title
    draw.text((left_x, 630), "TAIWAN TRAVEL MAP", fill=INK_COLOR, font=font_brand)
    
    # Subtitle
    draw.text((left_x, 775), "Explore Taiwan Like A Local", fill=CHERRY_PINK, font=font_sub)
    
    # Lead descriptive text
    draw.text((left_x, 865), "Discover Hidden Attractions, Vibrant Festivals & Historic Cafes", fill=INK_COLOR, font=font_lead)
    
    # Feature Badges
    pills = ["Hidden Gems", "Curated Themes", "Live Events", "Historic Cafes", "Private Charters"]
    bx = left_x
    by = 960
    for p in pills:
        bb = draw.textbbox((0, 0), p, font=font_badge)
        bw = bb[2] - bb[0] + 48
        bh = 60
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=30, fill=PILL_BG, outline=PILL_BORDER, width=2)
        draw.text((bx + 24, by + 13), p, fill=INK_COLOR, font=font_badge)
        bx += bw + 18
        
    # Multi-language & nationwide note
    draw.text((left_x, 1100), "Available in 11 Languages   -   Nationwide Guide   -   Travel Essentials", fill=INK_SOFT, font=font_footer)
    
    # Right Side: 3 Layered Floating iPhone Mockups
    src_1 = os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_114636.png") # Themes
    src_2 = os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_114613.png") # Taiping Mountain
    src_3 = os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_115414.png") # Cafes
    
    phone_w = 660
    phone_h = int(phone_w * (2340 / 1080))
    
    if os.path.exists(src_1) and os.path.exists(src_2) and os.path.exists(src_3):
        m1 = build_phone_mockup(Image.open(src_1), phone_w, phone_h, is_dark_top=False, is_ios=True)
        m2 = build_phone_mockup(Image.open(src_2), phone_w, phone_h, is_dark_top=True, is_ios=True)
        m3 = build_phone_mockup(Image.open(src_3), phone_w, phone_h, is_dark_top=True, is_ios=True)
        
        # Paste in depth order: Left (Themes), Right (Cafes), Center elevated (Taiping Mountain)
        bg.paste(m1, (2160, 200), m1)
        bg.paste(m3, (3000, 240), m3)
        bg.paste(m2, (2560, 100), m2)
        
    final_output = bg.convert("RGB")
    final_output.save(output_path, "PNG", quality=95)
    print(f"Header Banner saved to: {output_path}")

def render_search_results_banner(output_path, target_width=3840, target_height=2560):
    """
    Renders the Search Results Banner (搜尋結果素材) for App Store Connect.
    Supported sizes: 3840 x 2560 px (High-Res 3:2) and 1920 x 1280 px (Standard 3:2).
    """
    W, H = target_width, target_height
    scale = W / 3840.0
    print(f"Rendering Search Results Banner ({W}x{H}, scale={scale:.2f})...")
    
    # 1. Aurora Background
    bg = create_aurora_background(W, H, blobs_config=[
        {"center": (int(W * 0.20), int(H * 0.30)), "radius": int(800 * scale), "color": (109, 179, 242, 115)},
        {"center": (int(W * 0.50), int(H * 0.45)), "radius": int(900 * scale), "color": (216, 180, 248, 105)},
        {"center": (int(W * 0.80), int(H * 0.30)), "radius": int(850 * scale), "color": (232, 141, 150, 115)},
    ])
    draw = ImageDraw.Draw(bg)
    
    # Scaled Fonts
    font_brand = get_font(EN_TITLE_FONT, int(114 * scale), index=1)
    font_sub = get_font(EN_SUB_FONT, int(52 * scale))
    font_lead = get_font(EN_SANS_FONT, int(38 * scale), index=0)
    font_badge = get_font(EN_TITLE_FONT, int(30 * scale), index=1)
    font_note = get_font(EN_SANS_FONT, int(32 * scale), index=0)
    
    # Center Brand Header Block
    icon_path = os.path.join(SCREENSHOT_DIR, "icon.png")
    icon_size = int(180 * scale)
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert("RGBA").resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        
        shadow_pad = int(35 * scale)
        icon_shadow = Image.new("RGBA", (icon_size + shadow_pad * 2, icon_size + shadow_pad * 2), (0, 0, 0, 0))
        r, g, b, a = icon.split()
        shadow_alpha = a.point(lambda p: int(p * 0.35))
        shadow_layer = Image.new("RGBA", (icon_size, icon_size), (30, 35, 50, 255))
        shadow_layer.putalpha(shadow_alpha)
        icon_shadow.paste(shadow_layer, (shadow_pad, shadow_pad + int(8 * scale)), shadow_layer)
        icon_shadow = icon_shadow.filter(ImageFilter.GaussianBlur(int(16 * scale)))
        
        icon_x = (W - icon_size) // 2
        icon_y = int(140 * scale)
        bg.paste(icon_shadow, (icon_x - shadow_pad, icon_y - shadow_pad), icon_shadow)
        bg.paste(icon, (icon_x, icon_y), icon)
    
    # Main Brand Title
    title_text = "TAIWAN TRAVEL MAP"
    tb = draw.textbbox((0, 0), title_text, font=font_brand)
    tw = tb[2] - tb[0]
    draw.text(((W - tw) // 2, int(360 * scale)), title_text, fill=INK_COLOR, font=font_brand)
    
    # Subtitle
    sub_text = "Explore Taiwan Like A Local"
    sb = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw = sb[2] - sb[0]
    draw.text(((W - sw) // 2, int(495 * scale)), sub_text, fill=CHERRY_PINK, font=font_sub)
    
    # Descriptive Lead
    lead_text = "Discover Hidden Attractions, Vibrant Festivals & Historic Cafes"
    lb = draw.textbbox((0, 0), lead_text, font=font_lead)
    lw = lb[2] - lb[0]
    draw.text(((W - lw) // 2, int(575 * scale)), lead_text, fill=INK_COLOR, font=font_lead)
    
    # Feature Badges
    pills = ["Hidden Gems", "Curated Themes", "Live Events", "Historic Cafes", "Private Charters"]
    total_badge_w = 0
    badge_widths = []
    for p in pills:
        bb = draw.textbbox((0, 0), p, font=font_badge)
        w = bb[2] - bb[0] + int(48 * scale)
        badge_widths.append((p, w))
        total_badge_w += w
    total_badge_w += int(18 * scale) * (len(pills) - 1)
    
    bx = (W - total_badge_w) // 2
    by = int(655 * scale)
    bh = int(58 * scale)
    for p, bw in badge_widths:
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2, fill=PILL_BG, outline=PILL_BORDER, width=2)
        bb = draw.textbbox((0, 0), p, font=font_badge)
        ptw = bb[2] - bb[0]
        draw.text((bx + (bw - ptw) // 2, by + int(12 * scale)), p, fill=INK_COLOR, font=font_badge)
        bx += bw + int(18 * scale)
        
    # Lower Section: 4 Floating Phone Devices Showcase
    srcs = [
        (os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_114613.png"), True),   # Destinations
        (os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_114636.png"), False),  # Themes
        (os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_115128.png"), True),   # Events
        (os.path.join(SCREENSHOT_DIR, "Screenshot_20261102_115414.png"), True),   # Cafes
    ]
    
    phone_w = int(720 * scale)
    phone_h = int(phone_w * (2340 / 1080))
    
    mockups = []
    for path, dark_top in srcs:
        if os.path.exists(path):
            m = build_phone_mockup(Image.open(path), phone_w, phone_h, is_dark_top=dark_top, is_ios=True)
            mockups.append(m)
            
    if len(mockups) == 4:
        # 4 phones arranged horizontally with comfortable overlap
        # Center spacing
        center_x = W // 2
        y_pos = int(820 * scale)
        y_offset_outer = int(120 * scale)
        
        # Phone positions
        # Leftmost
        bg.paste(mockups[0], (center_x - int(1350 * scale), y_pos + y_offset_outer), mockups[0])
        # Rightmost
        bg.paste(mockups[3], (center_x + int(450 * scale), y_pos + y_offset_outer), mockups[3])
        # Mid-Left
        bg.paste(mockups[1], (center_x - int(850 * scale), y_pos), mockups[1])
        # Mid-Right
        bg.paste(mockups[2], (center_x - int(50 * scale), y_pos), mockups[2])
        
    final_output = bg.convert("RGB")
    final_output.save(output_path, "PNG", quality=95)
    print(f"Search Results Banner saved to: {output_path}")

def main():
    print("=" * 65)
    print("Generating Apple App Store Custom Product Page Banners...")
    print("=" * 65)
    
    # 1. Header Banner (3840 x 1646)
    out_header = os.path.join(BANNER_DIR, "header_banner_3840x1646.png")
    render_header_banner(out_header)
    
    # 2. Search Results Banner High-Res (3840 x 2560)
    out_search_hi = os.path.join(BANNER_DIR, "search_results_banner_3840x2560.png")
    render_search_results_banner(out_search_hi, 3840, 2560)
    
    # 3. Search Results Banner Standard (1920 x 1280)
    out_search_std = os.path.join(BANNER_DIR, "search_results_banner_1920x1280.png")
    render_search_results_banner(out_search_std, 1920, 1280)
    
    print("\n" + "=" * 65)
    print("All iOS Store Banners generated successfully!")
    print(f"Saved in: {BANNER_DIR}")
    print("=" * 65)

if __name__ == "__main__":
    main()

