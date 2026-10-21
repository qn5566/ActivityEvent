#!/usr/bin/env python3
"""離線翻譯所有語言（argos-translate，不需網路、不需 API key、無速率限制）。

策略：
  - 英文 = 人工對照表（data/_translations/en.json）+ argos zh→en 補齊描述。
  - 其他語言 = 從完整英文對照表 argos en→target 中轉（音譯名可保留）。

特性：
  - 斷點續傳：每次執行只翻譯對照表中缺失的文字，可隨時 Ctrl-C / 關機後續跑。
  - 原子寫入：對照表先寫暫存檔再 rename，中斷不會損壞資料。
  - 超長文本分段翻譯，避免 argos 對長序列卡住。
  - 全程寫入 data/translate.log。

用法：
  python3 offline_translate.py            # 翻譯全部 10 種語言並打包
  python3 offline_translate.py en ja      # 只翻譯指定語言
  建議後台執行：
  nohup python3 offline_translate.py > data/offline.out 2>&1 &
"""

import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import translate  # noqa: E402
import argostranslate.translate  # noqa: E402

# 資料夾名稱 → argos 語言代碼（Filipino 用 tl）
ARGOS_CODE = {
    "en": "en", "ja": "ja", "ko": "ko", "vi": "vi", "ms": "ms",
    "fil": "tl", "hi": "hi", "id": "id", "es": "es", "th": "th",
}
ALL_FOLDERS = ["en", "ja", "ko", "th", "vi", "ms", "fil", "hi", "id", "es"]

SEGMENT_LIMIT = 200  # 超過此長度按換行/句子分段翻譯


def argos(text, src, dst):
    return argostranslate.translate.translate(text, src, dst)


def argos_segmented(text, src, dst):
    """超長文本分段翻譯後拼接，單段失敗回退為原文。"""
    if len(text) <= SEGMENT_LIMIT:
        return argos(text, src, dst)
    chunks = []
    for line in text.split("\n"):
        if len(line) <= SEGMENT_LIMIT:
            chunks.append(line)
        else:
            chunks.extend(s for s in re.split(r"(?<=[。！？；])", line) if s)
    result = []
    for chunk in chunks:
        if not chunk.strip():
            result.append("")
            continue
        try:
            result.append(argos(chunk.strip(), src, dst))
        except Exception:
            result.append(chunk)  # 失敗保留原文，不中斷
    return "\n".join(result)


def safe_translate(text, src, dst):
    try:
        return argos_segmented(text, src, dst)
    except Exception:
        return text  # 失敗保留原文


def log(msg):
    translate.log(msg)


def collect_all_texts():
    texts = set()
    for path in sorted(translate.SOURCE_DIR.glob("*.json")):
        texts.update(translate.collect_texts(translate.read_json(path)))
    return texts


def load_table(folder):
    path = translate.TRANSLATION_DIR / f"{folder}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")), path
    return {}, path


def save_table(path, table):
    """原子寫入：先寫暫存檔再 rename。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(table, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def progress_str(done, total, start):
    elapsed = time.time() - start
    rate = done / elapsed if elapsed > 0 else 0
    remain = (total - done) / rate if rate > 0 else 0
    return f"{done}/{total} ({done * 100 // total}%)，已耗時 {elapsed / 60:.1f} 分，預計剩餘 {remain / 60:.1f} 分"


def fill_language(folder, src_lang, dst_lang, source_table=None):
    """翻譯 folder 語言缺失的文字。source_table 為 None 時從 zh 直譯，否則從 source_table 中轉。"""
    table, path = load_table(folder)
    texts = collect_all_texts()
    # 短文本優先，讓使用者能快速看到進度
    missing = sorted(texts - set(table), key=lambda t: (len(t), t))
    log(f"語言 {folder}（argos {src_lang}->{dst_lang}）：待翻譯 {len(missing)} 筆")
    if not missing:
        log(f"語言 {folder} 已完整，跳過")
        return

    start = time.time()
    for i, text in enumerate(missing, 1):
        if source_table is not None:
            src_text = source_table.get(text) or safe_translate(text, "zh", "en")
        else:
            src_text = text
        table[text] = safe_translate(src_text, src_lang, dst_lang)
        if i % 50 == 0 or i == len(missing):
            save_table(path, table)
            log(f"  {folder}: {progress_str(i, len(missing), start)}")
    save_table(path, table)
    log(f"語言 {folder} 完成，共 {len(table)} 筆")


def main():
    args = sys.argv[1:]
    folders = [f for f in args if f in ARGOS_CODE] or ALL_FOLDERS

    # 防止重複啟動（lock 檔案，記錄 PID，啟動時檢查是否存活）
    lock_path = translate.DATA_DIR / ".offline_translate.lock"
    if lock_path.exists():
        try:
            old_pid = int(lock_path.read_text(encoding="utf-8").strip())
            os.kill(old_pid, 0)  # PID 仍存活
            log(f"偵測到另一個翻譯程序正在執行（PID {old_pid}），本次不啟動。")
            log(f"若要強制重新啟動，請先執行：rm {lock_path}")
            sys.exit(1)
        except (ValueError, ProcessLookupError, OSError):
            lock_path.unlink()
            log(f"清除殘留的 lock 檔案 {lock_path}")
    lock_path.write_text(str(os.getpid()), encoding="utf-8")

    try:
        log(f"=== 開始離線翻譯：{', '.join(folders)} ===")

        # 1. 英文：人工 + argos zh->en 補齊
        en_table, _ = load_table("en")
        log(f"英文對照表已有 {len(en_table)} 筆")
        fill_language("en", "zh", "en")
        en_table, _ = load_table("en")

        # 2. 其他語言：從英文中轉
        for folder in folders:
            if folder == "en":
                continue
            fill_language(folder, "en", ARGOS_CODE[folder], source_table=en_table)

        # 3. 套用 + 打包
        log("翻譯完成，開始套用與打包 ...")
        for folder in folders:
            translate.build_language(folder)
        log("=== 全部完成 ===")
    finally:
        try:
            lock_path.unlink()
        except Exception:
            pass


if __name__ == "__main__":
    main()
