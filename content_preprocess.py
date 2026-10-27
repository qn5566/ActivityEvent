#!/usr/bin/env python3
"""content/ 改版內容的前置處理：在 argos 翻譯前，先用確定性規則預填對照表。

規則（沿用 data/preprocess.py 的專名/後綴/glossary 字典，再加 content 補充詞）：
  1. 無漢字（符號／數字／ASCII／emoji）→ 保留原樣
  2. 食物／物種查表（data/glossary.json）→ 查表值
  3. 專名欄位（店名／品牌／地名／地址等）→ jieba 分詞 + pinyin 音譯 + 常見詞英文替換
  其餘（描述句）→ 留給 content_offline_translate.py 用 argos 翻譯。

正典策略：上述結果對所有語言共用同一英文/拼音值（同 data 管線）。

用法：
  python3 content_preprocess.py --dry-run   # 只列分類統計與樣本，不寫檔
  python3 content_preprocess.py             # 預填所有語言對照表（補缺漏）
  python3 content_preprocess.py --force     # 連已有人工值也覆寫（謹慎）
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content_translate as ct  # noqa: E402
from preprocess import (  # noqa: E402
    FULL, PROPER, SUFFIX, load_glossary, is_han, has_han,
)
from pypinyin import lazy_pinyin  # noqa: E402
import jieba  # noqa: E402

LANGS = list(ct.LANGUAGES)

# content 補充的常見詞（專名欄位在 pinyin 前先替換；PROPER/SUFFIX 已有者不重複）
CONTENT_PROPER = [
    ("旗艦店", "Flagship Store"), ("中餐廳", "Chinese Restaurant"), ("餐廳", "Restaurant"),
    ("咖啡館", "Cafe"), ("書店", "Bookstore"), ("茶樓", "Teahouse"), ("茶館", "Teahouse"),
    ("旅宿", "Hostel"), ("民宿", "B&B"), ("酒店", "Hotel"), ("飯店", "Hotel"),
    ("旅店", "Hotel"), ("飯館", "Restaurant"), ("夜市", "Night Market"),
    ("米其林", "Michelin"), ("必比登", "Bib Gourmand"), ("景點", "Attraction"),
    ("地標", "Landmark"), ("秘境", "Hidden Gem"), ("山城", "Mountain Town"),
    ("海景", "Seaview"), ("觀景", "Viewing"), ("老宅", "Old House"),
    ("精選", "Selected"), ("天井", "Courtyard"), ("沙龍", "Salon"),
    ("手沖", "Pour-over"), ("甜點", "Dessert"), ("老屋", "Old House"),
]

# 地址後綴（SUFFIX 沒有者補上）
CONTENT_SUFFIX = [
    ("街", "Street"), ("路", "Road"), ("巷", "Lane"), ("弄", "Alley"),
    ("號", "No."), ("樓", "F"), ("段", "Section"), ("市", "City"), ("鎮", "Town"),
]

# 專名欄位（pinyin 音譯）；其餘文字欄位留給 argos。
NAME_FIELDS = {
    "name", "brand", "city", "district", "address", "origin",
    "region", "zhName", "shortName", "shortTitle", "subName", "mapQuery",
}


def all_proper():
    merged = list(PROPER) + list(CONTENT_PROPER)
    merged.sort(key=lambda pair: -len(pair[0]))
    return merged


def all_suffix():
    merged = list(SUFFIX) + list(CONTENT_SUFFIX)
    merged.sort(key=lambda pair: -len(pair[0]))
    return merged


_PROP_CACHE = None
_SUFFIX_CACHE = None


def proper_table():
    global _PROP_CACHE
    if _PROP_CACHE is None:
        _PROP_CACHE = all_proper()
    return _PROP_CACHE


def suffix_table():
    global _SUFFIX_CACHE
    if _SUFFIX_CACHE is None:
        _SUFFIX_CACHE = all_suffix()
    return _SUFFIX_CACHE


def render_word(word):
    """單一漢字詞 → 英文（後綴對應）或 pinyin；無法處理回 pinyin。"""
    for suf, en in suffix_table():
        if word.endswith(suf):
            prefix = word[: -len(suf)]
            if not prefix:
                return en
            if is_han(prefix):
                return "".join(lazy_pinyin(prefix)).capitalize() + " " + en
    return "".join(lazy_pinyin(word)).capitalize()


def render_content_name(text):
    """店名／品牌／地名 → 官方英文 + pinyin（保留內嵌英文/ASCII/emoji/符號）。"""
    t = text.strip()
    if t in FULL:
        return FULL[t]
    for zh, en in proper_table():
        if zh in t:
            t = t.replace(zh, " " + en + " ")
    out = []
    for seg in jieba.cut(t):
        s = seg.strip()
        if not s:
            continue
        if not is_han(s):
            out.append(s)
        else:
            out.append(render_word(s))
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def classify(text, leaf_key):
    """回傳 (kind, value)；kind=None 表示留給 argos。"""
    t = text.strip()
    if not has_han(t):
        return ("identity", t)
    g = load_glossary().get(t)
    if isinstance(g, str) and g:
        return ("glossary", g)
    if leaf_key in NAME_FIELDS:
        return ("proper", render_content_name(t))
    return (None, None)


def collect_items():
    items = []
    seen = set()
    for path in sorted(ct.SOURCE_DIR.glob("*.json")):
        file_name = path.name
        data = ct.read_json(path)
        for keys, value in ct.walk(data):
            if isinstance(value, str) and value.strip() and ct.is_translatable(file_name, keys):
                leaf_key = keys[-1]
                if value not in seen:
                    seen.add(value)
                    items.append((value, file_name, leaf_key))
    return items


def main():
    dry = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    items = collect_items()
    plans = []
    stats = {}
    samples = {}
    for text, file_name, leaf_key in items:
        kind, value = classify(text, leaf_key)
        if kind is None:
            continue
        stats[kind] = stats.get(kind, 0) + 1
        samples.setdefault(kind, []).append((text, value))
        plans.append((text, kind, value))

    print("=== content 前置處理分類統計（共 %d 筆待譯文字） ===" % len(items))
    for kind in ("identity", "glossary", "proper"):
        print(f"  {kind:<9} {stats.get(kind, 0)} 筆")

    for kind in ("identity", "glossary", "proper"):
        if kind in samples:
            print(f"\n[{kind}] 樣本：")
            for text, value in samples[kind][:14]:
                print(f"  {text}  ->  {value}")

    argos_count = len(items) - len(plans)
    print(f"\n留給 argos（描述句）：{argos_count} 筆")

    if dry:
        print(f"\n（--dry-run）共 {len(plans)} 筆將預填，未寫入。")
        return

    tables = {}
    for lang in LANGS:
        path = ct.TRANSLATION_DIR / f"{lang}.json"
        tables[lang] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    FORCE_OVERWRITE = {"identity"}
    changed = 0
    for text, kind, value in plans:
        for lang in LANGS:
            table = tables[lang]
            if force or kind in FORCE_OVERWRITE or text not in table:
                if table.get(text) != value:
                    table[text] = value
                    changed += 1

    ct.TRANSLATION_DIR.mkdir(parents=True, exist_ok=True)
    for lang in LANGS:
        path = ct.TRANSLATION_DIR / f"{lang}.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(tables[lang], ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(path)

    print(f"\n已寫入 {len(plans)} 筆 × {len(LANGS)} 語言，實際異動 {changed} 格。")


if __name__ == "__main__":
    main()
