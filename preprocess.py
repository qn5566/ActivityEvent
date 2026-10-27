#!/usr/bin/env python3
"""前置處理：在 argos 翻譯前，用確定性規則預填對照表 data/_translations/*.json。

規則（依序）：
  1. 無漢字（符號／數字／ASCII 代碼）→ 保留原樣，不丟給 argos
  2. 黑名單（已知 argos 會幻覺的輸入）→ 保留原樣
  3. 食物／物種查表（data/glossary.json）→ 查表值
  4. 專名（地名／建物）→ pypinyin 音譯 + 英文後綴
  5. 圖片授權（【姓名/拍攝】等）→ Photo by 姓名
  其餘（描述）→ 留給 offline_translate.py 用 argos 翻譯。

正典策略：專名（地名／建物名）與圖片授權不再全語言共用英文，而是：
  - 拉丁文字語言（en/es/vi/ms/fil/id）沿用英文/拼音；
  - ja 轉片假名、ko 轉諺文（常見後綴／場所詞另查 transliterate.py 的對照表）。
  食物／物種仍全語言共用英文（glossary 查表）；描述句留給 offline_translate.py 用 argos 翻譯。

用法：
  python3 preprocess.py --dry-run   # 只列分類統計與樣本，不寫檔
  python3 preprocess.py             # 預填所有語言對照表（僅補缺漏，不動已有人工值）
  python3 preprocess.py --force     # 連已存在的人工值也覆寫（謹慎使用）

注意：只補「缺漏」，不覆寫人工校正過的對照表；純符號/數字（identity）一律覆寫，
因為它們本來就不該被翻譯。
"""

import json
import re
import sys
from pathlib import Path

from pypinyin import lazy_pinyin

sys.path.insert(0, str(Path(__file__).resolve().parent))
import translate  # noqa: E402
import transliterate  # noqa: E402

LANGS = ["en", "ja", "ko", "vi", "es", "fil", "hi", "id", "ms", "th"]
DATA_DIR = Path(__file__).resolve().parent / "data"
GLOSSARY_PATH = DATA_DIR / "glossary.json"

# ---------------------------------------------------------------------------
# 完整鍵官方英文（優先於後綴邏輯）
# ---------------------------------------------------------------------------
FULL = {
    "九族文化村": "Formosan Aboriginal Culture Village", "國立故宮博物院": "National Palace Museum",
    "淡水老街": "Tamsui Old Street", "愛河": "Love River", "日月潭": "Sun Moon Lake",
    "拉魯島": "Lalu Island", "西門町": "Ximending", "阿里山": "Alishan", "太平山": "Taiping Mountain",
    "翠峰湖": "Cuifeng Lake", "滿月圓": "Manyueyuan", "墾丁": "Kenting", "九份": "Jiufen", "集集": "Jiji",
    "伊達邵": "Ita Thao", "淡水": "Tamsui", "東眼山": "Dongyan Mountain", "內洞": "Neidong", "拉拉山": "Lala Mountain",
    "雪霸": "Shei-Pa", "玉山": "Jade Mountain", "合歡山": "Hehuan Mountain", "太魯閣": "Taroko",
    "台灣": "Taiwan", "小台灣": "Little Taiwan", "奮起湖": "Fenqihu", "綠島": "Green Island",
    "永浴愛河": "Eternal Love", "民眾參拜指南宮": "Worshipers at Zhinan Temple",
    "中區": "Central District", "東區": "East District", "西區": "West District", "南區": "South District", "北區": "North District",
    "中西區": "West Central District", "新市區": "Xinshi District", "台北市": "Taipei City", "臺北市": "Taipei City",
}

# ---------------------------------------------------------------------------
# 官方專名 + 常見描述詞（最長優先替換）
# ---------------------------------------------------------------------------
PROPER = [
    ("日月潭國家風景區", "Sun Moon Lake National Scenic Area"),
    ("九族文化村", "Formosan Aboriginal Culture Village"), ("國立故宮博物院", "National Palace Museum"),
    ("日月潭", "Sun Moon Lake"), ("太平山", "Taiping Mountain"), ("阿里山", "Alishan"), ("伊達邵", "Ita Thao"),
    ("翠峰湖", "Cuifeng Lake"), ("滿月圓", "Manyueyuan"), ("墾丁", "Kenting"), ("淡水", "Tamsui"), ("西門町", "Ximending"),
    ("拉魯島", "Lalu Island"), ("愛河", "Love River"), ("集集", "Jiji"), ("內洞", "Neidong"), ("羅東", "Luodong"),
    ("土場", "Tuchang"), ("車埕", "Checheng"), ("星巴克", "Starbucks"), ("太魯閣", "Taroko"), ("玉山", "Jade Mountain"),
    ("合歡山", "Hehuan Mountain"), ("拉拉山", "Lala Mountain"), ("台灣", "Taiwan"), ("綠島", "Green Island"),
    ("奮起湖", "Fenqihu"), ("芒果樹", "Mango Tree"), ("夫妻樹", "Couple Tree"), ("樟樹", "Camphor Tree"),
    ("紅樹林", "Mangrove"), ("巨木群", "Giant Trees"), ("博物館", "Museum"), ("美術館", "Art Museum"),
    ("生態", "Ecological"), ("森林", "Forest"), ("濕地", "Wetland"), ("文化", "Cultural"), ("文創", "Cultural Creative"),
    ("創意", "Creative"), ("產業", "Industrial"), ("休閒", "Leisure"), ("觀光", "Tourism"), ("藝術", "Art"),
    ("教育", "Education"), ("親水", "Waterfront"), ("茶葉", "Tea"), ("咖啡", "Coffee"), ("陶瓷", "Ceramics"),
    ("木雕", "Woodcarving"), ("石雕", "Stone Carving"), ("燈塔", "Lighthouse"), ("漁人", "Fisherman"),
    ("戶外", "Outdoor"), ("浮潛", "Snorkeling"), ("稻田", "Paddy Field"), ("草坪", "Lawn"), ("景觀", "Landscape"), ("藝文", "Arts"),
    ("自然", "Nature"), ("地質", "Geological"), ("海洋", "Ocean"), ("海濱", "Seaside"), ("濱海", "Seaside"),
    ("縣立", "County"), ("縣", "County"), ("國立", "National"), ("市立", "Municipal"),
    ("新北投", "Xinbeitou"), ("北投", "Beitou"), ("臺北", "Taipei"), ("台北", "Taipei"), ("新北", "New Taipei"),
    ("桃園", "Taoyuan"), ("臺中", "Taichung"), ("台中", "Taichung"), ("臺南", "Tainan"), ("台南", "Tainan"),
    ("高雄", "Kaohsiung"), ("基隆", "Keelung"), ("新竹", "Hsinchu"), ("嘉義", "Chiayi"), ("苗栗", "Miaoli"),
    ("彰化", "Changhua"), ("南投", "Nantou"), ("雲林", "Yunlin"), ("屏東", "Pingtung"), ("宜蘭", "Yilan"),
    ("花蓮", "Hualien"), ("臺東", "Taitung"), ("台東", "Taitung"), ("澎湖", "Penghu"), ("金門", "Kinmen"), ("連江", "Lienchiang"),
]

# ---------------------------------------------------------------------------
# 後綴 → 英文（長→短，先比對長者）
# ---------------------------------------------------------------------------
SUFFIX = [
    ("國家森林遊樂區", "National Forest Recreation Area"), ("自然教育園區", "Nature Education Area"),
    ("地震紀念園區", "Earthquake Memorial Park"), ("綠色隧道", "Green Tunnel"), ("高空觀景步道", "Skywalk"),
    ("七彩吊橋", "Rainbow Suspension Bridge"), ("碼頭商圈", "Wharf Commercial District"), ("風景區", "Scenic Area"),
    ("火車站", "Railway Station"), ("漁港", "Fishing Harbor"), ("老街", "Old Street"), ("吊橋", "Suspension Bridge"),
    ("車站", "Station"), ("商圈", "Commercial District"), ("碼頭", "Wharf"), ("書院", "Academy"), ("新村", "New Village"),
    ("渡假村", "Resort"), ("度假村", "Resort"), ("生態村", "Ecological Village"), ("部落", "Tribe"), ("遊憩區", "Recreation Area"),
    ("森林遊樂區", "Forest Recreation Area"), ("遊樂區", "Recreation Area"),
    ("園區", "Park"), ("公園", "Park"), ("農場", "Farm"), ("牧場", "Ranch"), ("美術館", "Art Museum"), ("博物館", "Museum"),
    ("紀念館", "Memorial Hall"), ("文化館", "Culture Center"), ("陳列館", "Exhibition Hall"), ("展示館", "Exhibition Hall"),
    ("圖書館", "Library"), ("總館", "Main Library"), ("水庫", "Reservoir"), ("水壩", "Dam"), ("瀑布", "Waterfall"),
    ("步道", "Trail"), ("古道", "Ancient Trail"), ("隧道", "Tunnel"), ("大橋", "Bridge"), ("橋", "Bridge"), ("島", "Island"),
    ("港", "Harbor"), ("寺", "Temple"), ("廟", "Temple"), ("宮", "Temple"), ("神社", "Shrine"), ("溫泉", "Hot Spring"),
    ("縣", "County"), ("鄉", "Township"),
    ("自然保留區", "Nature Reserve"), ("保留區", "Nature Reserve"), ("溫泉區", "Hot Spring Area"),
    ("潛水區", "Diving Area"), ("休息區", "Rest Area"), ("生態區", "Ecological Area"), ("漁業區", "Fishing Area"),
    ("地質區", "Geological Area"), ("度假區", "Resort Area"), ("渡假區", "Resort Area"), ("戶外區", "Outdoor Area"),
    ("浮潛區", "Snorkeling Area"), ("稻田區", "Paddy Field Area"), ("草坪區", "Lawn Area"), ("景觀區", "Landscape Area"),
    ("賞櫻區", "Cherry Blossom Viewing Area"), ("花卉區", "Flower Area"), ("小吃區", "Snack Area"), ("營區", "Camp Area"),
    ("校區", "Campus"), ("廠區", "Factory Area"), ("院區", "Branch"), ("地區", "Area"), ("市區", "Downtown"),
    ("街區", "Street District"), ("特區", "Special District"), ("風景特定區", "Scenic Special Area"),
    ("野生動物保護區", "Wildlife Conservation Area"), ("紅樹林保護區", "Mangrove Conservation Area"),
    ("保護區", "Conservation Area"), ("保存區", "Preservation Area"), ("保育區", "Conservation Area"),
    ("露營區", "Camping Area"), ("服務區", "Service Area"), ("賞鳥區", "Bird Watching Area"), ("農業區", "Agricultural Area"),
    ("展演區", "Exhibition Area"), ("閱覽區", "Reading Area"), ("體驗區", "Experience Area"), ("休憩區", "Rest Area"),
    ("展示區", "Exhibition Area"), ("展售區", "Sales Area"), ("社區", "Community"), ("區", "District"),
    ("村", "Village"), ("山", "Mountain"), ("湖", "Lake"), ("溪", "Creek"), ("河", "River"), ("灣", "Bay"),
    ("谷", "Valley"), ("洞", "Cave"), ("石", "Stone"), ("岩", "Rock"),
    ("百年老樹", "Century-old Tree"), ("大樟樹", "Giant Camphor Tree"), ("夫妻樹", "Couple Tree"), ("芒果樹", "Mango Tree"),
    ("老樟樹", "Old Camphor Tree"), ("樟樹", "Camphor Tree"), ("老樹", "Old Tree"), ("樹", "Tree"),
]

# 前綴含這些標記視為「描述/圖說」而非專名，跳過
STOP_MARKERS = ["眺", "鳥瞰", "遠眺", "俯瞰", "一座", "群山", "自導", "全景", "日出", "空拍", "滿足", "門市", "超市", "夜市", "漁市", "市場", "之"]

# 已知 argos 會幻覺、應保留原樣的輸入（可持續擴充）
BLACKLIST = set()


def is_han(s):
    return bool(s) and all("\u4e00" <= c <= "\u9fff" for c in s)


def has_han(s):
    return any("\u4e00" <= c <= "\u9fff" for c in s)


_GLOSSARY_CACHE = None


def load_glossary():
    global _GLOSSARY_CACHE
    if _GLOSSARY_CACHE is None:
        if GLOSSARY_PATH.exists():
            _GLOSSARY_CACHE = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
        else:
            _GLOSSARY_CACHE = {}
    return _GLOSSARY_CACHE


def suffix_of(k):
    for suf, en in SUFFIX:
        if k.endswith(suf):
            return suf, en
    return None, None


def render_proper(prefix, lang):
    if lang in transliterate.LATIN:
        for zh, en in PROPER:
            if zh in prefix:
                prefix = prefix.replace(zh, " " + en + " ")
        toks = prefix.split()
        out = []
        for t in toks:
            out.append("".join(lazy_pinyin(t)).capitalize() if is_han(t) else t)
        return " ".join(out) if out else "".join(lazy_pinyin(prefix)).capitalize()
    # ja/ko：專名音譯，常見詞翻譯
    placeholders = []
    for i, (zh, en) in enumerate(PROPER):
        if zh in prefix:
            ph = f"zplh{i}z"
            placeholders.append((ph, transliterate.localize_proper(zh, en, lang, lazy_pinyin(zh))))
            prefix = prefix.replace(zh, " " + ph + " ")
    ph_map = dict(placeholders)
    if lang == "ja":
        result = ""
        for tok in prefix.split():
            if tok in ph_map:
                result += ph_map[tok]
            elif is_han(tok):
                result += transliterate.transliterate_syllables(lazy_pinyin(tok), lang)
            else:
                result += tok
        return result
    out = []
    for tok in prefix.split():
        if tok in ph_map:
            out.append(ph_map[tok])
        elif is_han(tok):
            out.append(transliterate.transliterate_syllables(lazy_pinyin(tok), lang))
        else:
            out.append(tok)
    return " ".join(out)


def render_name(k, lang):
    """地名/建物名 → 專名音譯 + 英文後綴；若非專名則回傳 None。"""
    if k in FULL:
        return transliterate.localize_proper(k, FULL[k], lang, lazy_pinyin(k))
    suf, en = suffix_of(k)
    if not suf:
        return None
    prefix = k[: -len(suf)]
    if not prefix:
        return transliterate.localize_word(en, lang)
    if not is_han(prefix):
        return None
    if len(k) > 12:
        return None
    if prefix[-1] == "之":
        return None
    for m in STOP_MARKERS:
        if m in prefix:
            return None
    sep = transliterate.word_sep(lang)
    return render_proper(prefix, lang) + sep + transliterate.localize_word(en, lang)


def render_person(name, lang):
    """中文姓名 → 拼音（姓 + 名）。"""
    py = lazy_pinyin(name)
    if not py:
        return name
    if lang not in transliterate.LATIN:
        return transliterate.transliterate_syllables(py, lang)
    if len(py) == 1:
        return py[0].capitalize()
    return py[0].capitalize() + " " + "".join(py[1:]).capitalize()


def render_photo_credit(text, lang):
    """【姓名/拍攝】或 姓名/拍攝 → Photo by 姓名。"""
    m = re.fullmatch(r"【?(.+?)[/／]拍攝】?", text)
    if not m:
        return None
    name = m.group(1).strip("【】").strip()
    if not name or not is_han(name) or len(name) > 6:
        return None
    if lang == "ja":
        return "写真：" + render_person(name, lang)
    if lang == "ko":
        return "사진: " + render_person(name, lang)
    return "Photo by " + render_person(name, lang)


def classify(text, lang="en"):
    """回傳 (kind, value)；kind=None 表示留給 argos。"""
    t = text.strip()
    if not has_han(t):
        return ("identity", t)
    if t in BLACKLIST:
        return ("blacklist", t)
    g = load_glossary().get(t)
    if isinstance(g, str):
        return ("glossary", g)
    v = render_name(t, lang)
    if v:
        return ("proper", v)
    v = render_photo_credit(t, lang)
    if v:
        return ("photo", v)
    return (None, None)


def collect_all_texts():
    texts = set()
    for path in sorted(translate.SOURCE_DIR.glob("*.json")):
        texts.update(translate.collect_texts(translate.read_json(path)))
    return texts


def main():
    dry = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    glossary = load_glossary()
    texts = sorted(collect_all_texts())

    stats = {}
    samples = {}
    plans = []  # (text, kind, value)
    for text in texts:
        kind, value = classify(text)
        if kind is None:
            continue
        stats[kind] = stats.get(kind, 0) + 1
        samples.setdefault(kind, []).append((text, value))
        plans.append((text, kind))

    print("=== 前置處理分類統計 ===")
    for kind in ("identity", "blacklist", "glossary", "proper", "photo"):
        if kind in stats:
            print(f"  {kind:<9} {stats[kind]} 筆")

    for kind in ("identity", "glossary", "proper", "photo"):
        if kind in samples:
            print(f"\n[{kind}] 樣本：")
            for text, value in samples[kind][:10]:
                print(f"  {text}  ->  {value}")

    if dry:
        print(f"\n（--dry-run）共 {len(plans)} 筆將預填，未寫入。")
        return

    # 讀取現有對照表
    tables = {}
    for lang in LANGS:
        path = translate.TRANSLATION_DIR / f"{lang}.json"
        tables[lang] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    FORCE_OVERWRITE = {"identity", "blacklist"}
    changed = 0
    value_cache = {}
    for text, kind in plans:
        for lang in LANGS:
            key = (text, "en") if lang in transliterate.LATIN else (text, lang)
            if key not in value_cache:
                value_cache[key] = classify(text, key[1])[1]
            value = value_cache[key]
            table = tables[lang]
            if force or kind in FORCE_OVERWRITE or text not in table:
                if table.get(text) != value:
                    table[text] = value
                    changed += 1

    translate.TRANSLATION_DIR.mkdir(parents=True, exist_ok=True)
    for lang in LANGS:
        path = translate.TRANSLATION_DIR / f"{lang}.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(tables[lang], ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(path)

    print(f"\n已寫入 {len(plans)} 筆 × {len(LANGS)} 語言，實際異動 {changed} 格。")


if __name__ == "__main__":
    main()
