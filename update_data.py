#!/usr/bin/env python3
"""下載觀光署資料，並用 Google Cloud Translation 建立多語 ZIP。"""

import argparse
import html
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

BASE_URL = "https://media.taiwan.net.tw/XMLReleaseALL_public/v2.0/Zh_tw"
KINDS = ("Attraction", "Event", "Restaurant")
# 目錄名稱：Google Translation API 的目標語言代碼
LANGUAGES = {
    "en": "en", "jp": "ja", "kr": "ko", "th": "th", "vi": "vi",
    "ph": "fil", "ms": "ms", "id": "id", "hi": "hi", "es": "es",
}
TEXT_FIELDS = {
    "AttractionName", "EventName", "RestaurantName", "Name", "Description",
    "City", "Town", "StreetAddress", "TrafficInfo", "ParkingInfo", "FeeInfo",
    "ServiceTimeInfo", "Remarks", "Participant", "OrganizationName", "Title",
    "Content", "Address", "Keywords", "AlternateNames", "RestaurantFeatures",
}
DATA_DIR = Path(__file__).resolve().parent / "data"


def download(url, destination):
    request = urllib.request.Request(url, headers={"User-Agent": "ActivityEvent-data-updater/2.0"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as output:
            shutil.copyfileobj(response, output)
    except urllib.error.URLError as error:
        # 部分 Python/OpenSSL 版本無法驗證此站憑證；curl 使用系統憑證庫。
        if "CERTIFICATE_VERIFY_FAILED" not in str(error):
            raise
        subprocess.run(
            ["curl", "--fail", "--location", "--silent", "--show-error", "--max-time", "120",
             "--output", str(destination), url], check=True,
        )


def check_zip(path, kind):
    with zipfile.ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.rsplit("/", 1)[-1] == f"{kind}List.json"]
        if len(names) != 1 or archive.testzip() is not None:
            raise ValueError(f"{path}: ZIP 缺少 {kind}List.json 或內容損壞")
        data = json.loads(archive.read(names[0]).decode("utf-8-sig"))
        if not isinstance(data, dict) or not data.get(f"{kind}s"):
            raise ValueError(f"{path}: 主資料清單為空")


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


def google_translate(texts, target, api_key):
    payload = json.dumps({"q": texts, "source": "zh-TW", "target": target, "format": "text"}).encode()
    url = "https://translation.googleapis.com/language/translate/v2?" + urllib.parse.urlencode({"key": api_key})
    request = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        items = json.load(response)["data"]["translations"]
    if len(items) != len(texts):
        raise ValueError("翻譯 API 回傳數量不符")
    return [html.unescape(item["translatedText"]) for item in items]


def make_translations(texts, target, api_key, cache):
    translations = {
        source: translated for source, translated in
        cache.execute("SELECT source, translated FROM translations WHERE target = ?", (target,))
        if source in texts
    }
    missing = sorted(texts - translations.keys())
    print(f"  {target}: {len(texts)} 筆不同文字，需翻譯 {len(missing)} 筆", flush=True)
    batch, chars = [], 0
    for source in missing + [None]:
        if batch and (source is None or len(batch) >= 100 or chars + len(source) > 20000):
            results = google_translate(batch, target, api_key)
            cache.executemany(
                "INSERT OR REPLACE INTO translations VALUES (?, ?, ?)",
                [(target, original, translated) for original, translated in zip(batch, results)],
            )
            cache.commit()
            translations.update(zip(batch, results))
            batch, chars = [], 0
        if source is not None:
            batch.append(source)
            chars += len(source)
    return translations


def read_json_files(path):
    with zipfile.ZipFile(path) as archive:
        return {
            name: json.loads(archive.read(name).decode("utf-8-sig"))
            for name in archive.namelist()
            if name.lower().endswith(".json") and not name.startswith("__MACOSX/")
        }


def write_translated_zip(source, destination, data, translations, language):
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(destination, "w") as output:
        for item in original.infolist():
            if item.is_dir() or item.filename.startswith("__MACOSX/"):
                continue
            if item.filename in data:
                content = translated_copy(data[item.filename], translations)
                if isinstance(content, dict) and "Language" in content:
                    content["Language"] = language
                raw = json.dumps(content, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            else:
                raw = original.read(item.filename)
            output.writestr(item.filename, raw, compress_type=zipfile.ZIP_DEFLATED)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--languages", nargs="+", choices=LANGUAGES, default=list(LANGUAGES),
                        help="指定目標語言目錄，例如 --languages en jp")
    parser.add_argument("--source-only", action="store_true", help="僅更新繁體中文原始 ZIP")
    args = parser.parse_args()
    api_key = os.environ.get("GOOGLE_TRANSLATE_API_KEY")
    if not args.source_only and not api_key:
        parser.error("請先設定 GOOGLE_TRANSLATE_API_KEY，或使用 --source-only")
    data_dir = args.data_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="activityevent-", dir=data_dir) as temporary:
        staged = Path(temporary)
        source_paths = {}
        for kind in KINDS:
            filename = f"{kind}-json.zip"
            path = staged / filename
            print(f"下載 {filename} ...", flush=True)
            download(f"{BASE_URL}/{filename}", path)
            check_zip(path, kind)
            source_paths[kind] = path

        if not args.source_only:
            datasets = {kind: read_json_files(path) for kind, path in source_paths.items()}
            texts = set()
            for files in datasets.values():
                for document in files.values():
                    texts.update(collect_texts(document))
            cache = sqlite3.connect(data_dir / ".translation_cache.sqlite3")
            cache.execute("CREATE TABLE IF NOT EXISTS translations (target TEXT, source TEXT, translated TEXT, PRIMARY KEY (target, source))")
            try:
                for folder in args.languages:
                    target = LANGUAGES[folder]
                    translations = make_translations(texts, target, api_key, cache)
                    language_dir = staged / folder
                    language_dir.mkdir()
                    for kind, source in source_paths.items():
                        write_translated_zip(source, language_dir / source.name, datasets[kind], translations, target)
            finally:
                cache.close()

        for source in source_paths.values():
            source.replace(data_dir / source.name)
        for folder in ([] if args.source_only else args.languages):
            destination_dir = data_dir / folder
            destination_dir.mkdir(exist_ok=True)
            for kind in KINDS:
                filename = f"{kind}-json.zip"
                (staged / folder / filename).replace(destination_dir / filename)
        print("資料更新完成")


if __name__ == "__main__":
    main()
