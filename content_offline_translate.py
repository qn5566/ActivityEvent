#!/usr/bin/env python3
"""離線翻譯 content/ 改版內容（argos-translate，不需網路、不需 API key）。

策略：
  - 英文 = zh→en 直譯。
  - 其他語言 = 從完整英文對照表 en→target 中轉。

特性：
  - 斷點續傳：每次執行只翻譯對照表中缺失的文字，可隨時 Ctrl-C / 關機後續跑。
  - 原子寫入：對照表先寫暫存檔再 rename。
  - 超長文本分段翻譯。
  - 全程寫入 content/translate.log。

用法：
  python3 content_offline_translate.py             # 翻譯全部 10 種語言並寫檔
  python3 content_offline_translate.py en ja       # 只翻譯指定語言
"""

import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content_translate as ct  # noqa: E402
import argostranslate.translate  # noqa: E402

# 資料夾名稱 → argos 語言代碼（Filipino 用 tl）
ARGOS_CODE = {
    "en": "en", "ja": "ja", "ko": "ko", "vi": "vi", "ms": "ms",
    "fil": "tl", "hi": "hi", "id": "id", "es": "es", "th": "th",
}
ALL_FOLDERS = ["en", "ja", "ko", "th", "vi", "ms", "fil", "hi", "id", "es"]

SEGMENT_LIMIT = 200


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
            result.append(chunk)
    return "\n".join(result)


_HAN_RUN = re.compile(r"([\u4e00-\u9fff]+)")


def _is_han_run(s):
    return bool(s) and all("\u4e00" <= c <= "\u9fff" for c in s)


def _clean_trailing_period(text, src):
    """argos 會在中文片段後自動補句點；短標籤/名稱不該有，去掉多餘結尾句點。"""
    if not text or not src:
        return text
    src_tail = src.rstrip()
    if src_tail and "\u4e00" <= src_tail[-1] <= "\u9fff" and text.endswith("."):
        return text[:-1].rstrip()
    return text


def safe_translate(text, src, dst):
    """翻譯；僅翻譯「連續漢字」片段，emoji／ASCII／數字／分隔符（·｜等）原樣保留，
    避免 argos 對符號亂翻或掉字。"""
    try:
        parts = _HAN_RUN.split(text)
        if len(parts) == 1:
            return _clean_trailing_period(argos_segmented(text, src, dst), text)
        out = []
        for part in parts:
            if _is_han_run(part):
                out.append(_clean_trailing_period(argos_segmented(part, src, dst), part))
            else:
                out.append(part)
        return "".join(out)
    except Exception:
        return text


def log(msg):
    ct.log(msg)


def collect_all_texts():
    texts = set()
    for path in sorted(ct.SOURCE_DIR.glob("*.json")):
        texts.update(ct.collect_texts(ct.read_json(path), path.name))
    return texts


def load_table(folder):
    path = ct.TRANSLATION_DIR / f"{folder}.json"
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
    """翻譯 folder 語言缺失的文字。source_table 為 None 時從 zh 直譯，否則從英文中轉。"""
    table, path = load_table(folder)
    texts = collect_all_texts()
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

    lock_path = ct.CONTENT_DIR / ".offline_translate.lock"
    if lock_path.exists():
        try:
            old_pid = int(lock_path.read_text(encoding="utf-8").strip())
            os.kill(old_pid, 0)
            log(f"偵測到另一個翻譯程序正在執行（PID {old_pid}），本次不啟動。")
            log(f"若要強制重新啟動，請先執行：rm {lock_path}")
            sys.exit(1)
        except (ValueError, ProcessLookupError, OSError):
            lock_path.unlink()
            log(f"清除殘留的 lock 檔案 {lock_path}")
    lock_path.write_text(str(os.getpid()), encoding="utf-8")

    try:
        log(f"=== 開始離線翻譯 content：{', '.join(folders)} ===")

        # 1. 英文：zh→en 直譯
        en_table, _ = load_table("en")
        log(f"英文對照表已有 {len(en_table)} 筆")
        fill_language("en", "zh", "en")
        en_table, _ = load_table("en")

        # 2. 其他語言：從英文中轉
        for folder in folders:
            if folder == "en":
                continue
            fill_language(folder, "en", ARGOS_CODE[folder], source_table=en_table)

        # 3. 套用寫檔
        log("翻譯完成，開始套用寫檔 ...")
        for folder in folders:
            ct.build_language(folder)
        log("=== 全部完成 ===")
    finally:
        try:
            lock_path.unlink()
        except Exception:
            pass


if __name__ == "__main__":
    main()
