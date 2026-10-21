#!/usr/bin/env python3
"""多語翻譯工作流（翻譯由 Codex agent 提供，本腳本負責套用、打包與記錄）。

用法：
  python3 translate.py en              # 套用 en 對照表並打包 ZIP
  python3 translate.py en --check      # 只檢查進度，列出尚缺的待譯文字
  python3 translate.py --pending en    # 把待譯文字輸出到 data/_translations/en.pending.txt

工作方式：
  - 翻譯對照表存放於 data/_translations/<lang>.json，格式 {"原文": "譯文", ...}，
    由 Codex agent 填寫。
  - 執行本腳本後：讀取 data/zh/*.json → 套用對照表 → 寫出 data/<lang>/*.json
    （Language 欄位更新）→ 打包 ZIP。
  - Attraction 的三個 JSON 合併為一個 Attraction-json.zip；
    Event、Restaurant 各自打包為 Event-json.zip、Restaurant-json.zip。
  - 全程寫入 data/translate.log。
"""

import argparse
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
SOURCE_DIR = DATA_DIR / "zh"
TRANSLATION_DIR = DATA_DIR / "_translations"
LOG_PATH = DATA_DIR / "translate.log"

# 資料夾名稱 → 目標語言代碼（也是 Google 翻譯 target），及 Language 欄位值
LANGUAGES = {
    "en": "En", "ja": "Ja", "ko": "Ko", "vi": "Vi", "ms": "Ms",
    "fil": "Fil", "hi": "Hi", "id": "Id", "es": "Es", "th": "Th",
}

# ZIP 分組：Attraction 三個 JSON 合併，Event / Restaurant 各自一個
ZIP_GROUPS = {
    "Attraction-json.zip": [
        "AttractionList.json",
        "AttractionFeeList.json",
        "AttractionServiceTimeList.json",
    ],
    "Event-json.zip": ["EventList.json"],
    "Restaurant-json.zip": ["RestaurantList.json"],
}

# 需要翻譯的文字欄位
TEXT_FIELDS = {
    "AttractionName", "EventName", "RestaurantName", "Name", "Description",
    "City", "Town", "StreetAddress", "TrafficInfo", "ParkingInfo", "FeeInfo",
    "ServiceTimeInfo", "Remarks", "Participant", "OrganizationName", "Title",
    "Content", "Address", "Keywords", "AlternateNames", "RestaurantFeatures",
}


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def collect_texts(value, key=None, found=None):
    if found is None:
        found = set()
    if isinstance(value, dict):
        for child_key, child in value.items():
            collect_texts(child, child_key, found)
    elif isinstance(value, list):
        for child in value:
            collect_texts(child, key, found)
    elif key in TEXT_FIELDS and isinstance(value, str) and value.strip():
        found.add(value)
    return found


def translated_copy(value, translations, key=None):
    if isinstance(value, dict):
        return {k: translated_copy(v, translations, k) for k, v in value.items()}
    if isinstance(value, list):
        return [translated_copy(v, translations, key) for v in value]
    if key in TEXT_FIELDS and isinstance(value, str):
        return translations.get(value, value)
    return value


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
    """套用對照表寫出 JSON 並打包 ZIP（供 auto_translate.py 複用）。"""
    language = LANGUAGES[folder]
    sources = sorted(SOURCE_DIR.glob("*.json"))
    documents = {path.name: read_json(path) for path in sources}
    texts = set()
    for document in documents.values():
        texts.update(collect_texts(document))
    translations, _ = load_translations(folder)
    missing = sorted(texts - set(translations))
    if missing and not force:
        log(f"{folder} 尚缺 {len(missing)} 筆，略過套用與打包")
        return False
    if missing and force:
        log(f"警告：{folder} 缺 {len(missing)} 筆將保留原文")

    language_dir = DATA_DIR / folder
    language_dir.mkdir(parents=True, exist_ok=True)
    for name, document in documents.items():
        log(f"套用翻譯：{name}")
        content = translated_copy(document, translations)
        if isinstance(content, dict) and "Language" in content:
            content["Language"] = language
        write_json(language_dir / name, content)

    log("打包 ZIP ...")
    for zip_name, files in ZIP_GROUPS.items():
        existing = [f for f in files if (language_dir / f).exists()]
        if not existing:
            log(f"  略過 {zip_name}（無對應 JSON）")
            continue
        log(f"  建立 {zip_name} <- {', '.join(existing)}")
        zip_path = language_dir / zip_name
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for f in existing:
                archive.write(language_dir / f, arcname=f)
        log(f"  完成 {zip_path}")
    log(f"=== {folder} 套用與打包完成 ===")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("language", nargs="?", choices=sorted(LANGUAGES),
                        help="目標語言資料夾（例如 en）")
    parser.add_argument("--check", action="store_true", help="只檢查進度不寫檔")
    parser.add_argument("--pending", action="store_true", help="輸出待譯文字到 pending 檔")
    parser.add_argument("--force", action="store_true", help="即使有缺漏仍套用並打包")
    args = parser.parse_args()

    if not args.language:
        parser.error("請指定語言，例如 python3 translate.py en")

    folder = args.language
    language = LANGUAGES[folder]
    log(f"=== 開始處理 {folder}（Language: {language}）{'（檢查模式）' if args.check else ''} ===")

    sources = sorted(SOURCE_DIR.glob("*.json"))
    if not sources:
        log("錯誤：data/zh/ 下沒有 JSON 檔案")
        sys.exit(1)

    documents = {path.name: read_json(path) for path in sources}
    log(f"讀取來源檔案：{', '.join(documents)}")

    texts = set()
    for document in documents.values():
        texts.update(collect_texts(document))
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
        log(f"對照表尚缺 {len(missing)} 筆，未套用。請由 agent 翻譯後補齊對照表，再執行一次。")
        log(f"可執行：python3 translate.py {folder} --pending 以輸出待譯清單")
        log(f"=== {folder} 處理中止（缺 {len(missing)} 筆） ===")
        sys.exit(2)

    if missing and args.force:
        log(f"警告：--force，{len(missing)} 筆缺譯將保留原文")

    build_language(folder, force=args.force)


if __name__ == "__main__":
    main()
