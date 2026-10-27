#!/usr/bin/env python3
"""content/ 改版內容的多語翻譯工作流（翻譯由 Codex agent / 離線腳本提供，本腳本負責套用與寫檔）。

用法：
  python3 content_translate.py en              # 套用 en 對照表，寫出 content/en/*.json
  python3 content_translate.py en --check      # 只檢查進度，列出尚缺的待譯文字
  python3 content_translate.py --pending en    # 把待譯文字輸出到 content/_translations/en.pending.txt

工作方式：
  - 翻譯對照表存放於 content/_translations/<lang>.json，格式 {"原文": "譯文", ...}。
  - 執行後：讀取 content/zh/*.json → 套用對照表 → 寫出 content/<lang>/*.json。
  - 只翻譯「內容文字」欄位（依 FILE_FIELDS 定義），id / URL / 價格 / 評分 / 顏色 /
    表情符號 / 分類代碼，以及原本已是英文的欄位（enTitle、enName、city_en 等）一律保留。
  - 全程寫入 content/translate.log。
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent / "content"
SOURCE_DIR = CONTENT_DIR / "zh"
TRANSLATION_DIR = CONTENT_DIR / "_translations"
LOG_PATH = CONTENT_DIR / "translate.log"

# 資料夾名稱 → 目標語言代碼（也是 Google / argos 對照用）
LANGUAGES = {
    "en": "En", "ja": "Ja", "ko": "Ko", "vi": "Vi", "ms": "Ms",
    "fil": "Fil", "hi": "Hi", "id": "Id", "es": "Es", "th": "Th",
}

# 各內容檔需要翻譯的文字欄位（只列「中文顯示文字」，其餘保留）。
FILE_FIELDS = {
    "blog.json": {
        "title", "subtitle", "category", "author", "date", "readTime", "content",
        "name", "address", "signature", "hours", "transport", "mapQuery",
    },
    "cafes.json": {
        "name", "city", "district", "address", "features", "status", "tags",
    },
    "michelin.json": {
        "name", "stars", "categoryName", "cuisine", "city", "address", "feature",
        "badge", "region", "desc", "dishes",
    },
    "rankings.json": {
        "zhName", "meaning", "categoryName", "title", "shortName", "heroAlt",
        "ctaText", "desc", "badge", "name", "city", "highlight", "tag",
    },
    "souvenirs.json": {
        "name", "shortName", "channel", "badge", "desc", "cta",
        "brand", "origin", "painPoint", "ctaText",
    },
    "themes.json": {
        "shortTitle", "zhTitle", "name", "subtitle", "title",
        "desc", "subName", "tag", "planName", "duration", "day", "text",
    },
}


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def is_translatable(file_name, keys):
    """依欄位（keys 為從根到葉的鍵路徑）判斷是否該翻譯。"""
    if not keys:
        return False
    key = keys[-1]
    fields = FILE_FIELDS.get(file_name, ())
    if key not in fields:
        return False
    # themes.json 頂層的 title 已是英文（ex: "North Coast Ocean Panorama..."），
    # 只有 experiences[].title 是中文，需要翻譯。
    if file_name == "themes.json" and key == "title":
        return len(keys) >= 2 and keys[-2] == "experiences"
    return True


def walk(node, keys=()):
    """遞迴走訪，產出 (keys 元組, 葉值)。"""
    if isinstance(node, dict):
        for child_key, child in node.items():
            yield from walk(child, keys + (child_key,))
    elif isinstance(node, list):
        for child in node:
            yield from walk(child, keys)
    else:
        yield keys, node


def collect_texts(node, file_name):
    found = set()
    for keys, value in walk(node):
        if isinstance(value, str) and value.strip() and is_translatable(file_name, keys):
            found.add(value)
    return found


def translated_copy(node, translations, file_name, keys=()):
    if isinstance(node, dict):
        return {
            k: translated_copy(v, translations, file_name, keys + (k,))
            for k, v in node.items()
        }
    if isinstance(node, list):
        return [translated_copy(v, translations, file_name, keys) for v in node]
    if isinstance(node, str) and is_translatable(file_name, keys):
        return translations.get(node, node)
    return node


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")


def load_translations(language):
    path = TRANSLATION_DIR / f"{language}.json"
    if not path.exists():
        return {}, path
    return json.loads(path.read_text(encoding="utf-8")), path


def build_language(folder, force=False):
    """套用對照表寫出 content/<folder>/*.json（供 offline 腳本複用）。"""
    language = LANGUAGES[folder]
    sources = sorted(SOURCE_DIR.glob("*.json"))
    documents = {path.name: read_json(path) for path in sources}

    texts = set()
    for name, document in documents.items():
        texts.update(collect_texts(document, name))

    translations, _ = load_translations(folder)
    missing = sorted(texts - set(translations))
    if missing and not force:
        log(f"{folder} 尚缺 {len(missing)} 筆，略過套用")
        return False
    if missing and force:
        log(f"警告：{folder} 缺 {len(missing)} 筆將保留原文")

    language_dir = CONTENT_DIR / folder
    language_dir.mkdir(parents=True, exist_ok=True)
    for name, document in documents.items():
        content = translated_copy(document, translations, name)
        write_json(language_dir / name, content)
        log(f"  套用翻譯並寫出：{name}")

    log(f"=== {folder} 套用完成（{language}） ===")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("language", nargs="?", choices=sorted(LANGUAGES),
                        help="目標語言資料夾（例如 en）")
    parser.add_argument("--check", action="store_true", help="只檢查進度不寫檔")
    parser.add_argument("--pending", action="store_true", help="輸出待譯文字到 pending 檔")
    parser.add_argument("--force", action="store_true", help="即使有缺漏仍套用")
    args = parser.parse_args()

    if not args.language:
        parser.error("請指定語言，例如 python3 content_translate.py en")

    folder = args.language
    log(f"=== 開始處理 content/{folder}（{'檢查模式' if args.check else '套用模式'}） ===")

    sources = sorted(SOURCE_DIR.glob("*.json"))
    if not sources:
        log("錯誤：content/zh/ 下沒有 JSON 檔案")
        sys.exit(1)

    documents = {path.name: read_json(path) for path in sources}
    texts = set()
    for name, document in documents.items():
        texts.update(collect_texts(document, name))
    log(f"共收集 {len(texts)} 筆不同文字")

    translations, table_path = load_translations(folder)
    log(f"讀取翻譯對照表 {table_path}：已有 {len(translations)} 筆")

    missing = sorted(texts - set(translations))
    log(f"待翻譯：{len(missing)} 筆")

    if missing and (args.pending or args.check):
        pending_path = TRANSLATION_DIR / f"{folder}.pending.txt"
        if args.pending:
            pending_path.write_text("\n".join(missing), encoding="utf-8")
            log(f"已輸出待譯清單到 {pending_path}")

    if missing and not args.force:
        log(f"對照表尚缺 {len(missing)} 筆，未套用。補齊後再執行一次。")
        log(f"可執行：python3 content_translate.py {folder} --pending 以輸出待譯清單")
        sys.exit(2)

    if missing and args.force:
        log(f"警告：--force，{len(missing)} 筆缺譯將保留原文")

    build_language(folder, force=args.force)


if __name__ == "__main__":
    main()
