#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 blog.json 每篇 spotInfo 的單一 bookingUrl 升級成 links[]（多條分潤連結）。

背景
----
原本每篇文章的 spotInfo 只有一個 bookingUrl（klook），加上 mapQuery（地圖）。
此腳本在 spotInfo 下新增 links 陣列，讓同一景點可同時掛 Klook + Trip 等
多條預訂連結，也讓管理頁可逐篇新增/編輯。

links 元素結構
--------------
{"type": "klook", "label": "Klook 預訂", "url": "https://..."}

保留 bookingUrl / mapQuery（向後相容），App 端優先讀 links、無 links 時
退回 bookingUrl。

用法
----
  python3 migrate_blog_links.py            # 正式寫入
  python3 migrate_blog_links.py --dry-run  # 只預覽統計
"""

import argparse
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def detect_indent(raw):
    """偵測原本的縮排空格數（2 / 4 / ...），保留原格式。"""
    for line in raw.split("\n")[1:]:
        stripped = line.lstrip(" ")
        if stripped and stripped[0] not in " \n":
            return len(line) - len(stripped)
    return 2


def discover_files():
    return sorted(glob.glob(os.path.join(HERE, "content", "*", "blog.json")))


def migrate_file(path, dry_run):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    data = json.loads(raw)
    minified = raw.count("\n") <= 1
    indent = detect_indent(raw)

    changed = 0
    skipped = 0
    for article in data:
        spot = article.get("spotInfo")
        if not isinstance(spot, dict):
            continue
        if "links" in spot:
            skipped += 1
            continue
        booking = spot.get("bookingUrl", "")
        links = []
        if booking:
            links.append({"type": "klook", "label": "Klook 預訂", "url": booking})
        spot["links"] = links
        changed += 1

    if dry_run:
        return changed, skipped
    with open(path, "w", encoding="utf-8") as fh:
        if minified:
            json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(data, fh, ensure_ascii=False, indent=indent)
        fh.write("\n")
    return changed, skipped


def main():
    parser = argparse.ArgumentParser(description="blog.json spotInfo 升級為 links[]")
    parser.add_argument("--dry-run", action="store_true", help="只預覽，不寫檔")
    args = parser.parse_args()

    total_changed = 0
    total_skipped = 0
    for path in discover_files():
        changed, skipped = migrate_file(path, args.dry_run)
        total_changed += changed
        total_skipped += skipped
        rel = os.path.relpath(path, HERE)
        print("%-24s 產生 %2d 筆 links，跳過 %2d 筆" % (rel, changed, skipped))

    action = "預覽（dry-run，未寫檔）" if args.dry_run else "已完成"
    print("\n%s：共產生 %d 筆 links，跳過 %d 筆。" % (action, total_changed, total_skipped))


if __name__ == "__main__":
    main()
