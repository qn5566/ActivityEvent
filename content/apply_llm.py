#!/usr/bin/env python3
"""把 LLM 高品質翻譯套用到 fullHtmlArticle，並重建 content/<lang>/blog.json。

用法：
  python3 content/apply_llm.py en      # 讀 _llm_out/en.json → 合併對照表 → 重建 blog.json
"""
import json
import re
import sys
from pathlib import Path

import content_translate as ct


def main():
    lang = sys.argv[1]
    llm_path = Path("content/_translations/_llm_out") / f"{lang}.json"
    if not llm_path.exists():
        print(f"找不到 {llm_path}")
        sys.exit(1)
    llm = json.loads(llm_path.read_text(encoding="utf-8"))

    table_path = ct.TRANSLATION_DIR / f"{lang}.json"
    table = json.loads(table_path.read_text(encoding="utf-8")) if table_path.exists() else {}
    table.update(llm)
    table_path.write_text(json.dumps(table, ensure_ascii=False, indent=1), encoding="utf-8")

    zh_blog = ct.read_json(ct.SOURCE_DIR / "blog.json")
    out = ct.translated_copy(zh_blog, table, "blog.json")
    ct.write_json(ct.CONTENT_DIR / lang / "blog.json", out)

    # 覆蓋率檢查：中文字段是否都有對照
    missing = 0
    for article in out:
        for node in ct.extract_html_texts(article["fullHtmlArticle"]):
            if re.search(r"[\u4e00-\u9fff]", node) and node.strip() not in table:
                missing += 1
    print(f"{lang}: merged {len(llm)}, table {len(table)}, missing zh nodes {missing}")


if __name__ == "__main__":
    main()
