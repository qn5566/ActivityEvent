#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""集中管理推薦連結（分潤 ID）的一鍵替換工具。

背景
----
分潤參數原本被寫死、重複散落在 11 種語言的 content/<lang>/*.json 以及
klook/ 的來源檔裡，改一個 ID 得手動全域取代、容易漏。

此腳本配合專案根目錄的 links.json（單一來源），只需改一個值即可一次重寫
所有檔案。

用法
----
  python3 update_links.py                              # 掃描並回報現況（不寫檔）
  python3 update_links.py --set klook_aid=999999       # 改值並套用到所有檔案
  python3 update_links.py --set klook_aid=999999 --dry-run  # 只預覽不動檔
  python3 update_links.py --files                      # 列出會被掃描到的檔案
"""

import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LINKS_PATH = os.path.join(HERE, "links.json")

# 每個 key 對應的「查詢參數名稱」（不含 = 與值）。
PARAM_OF_KEY = {
    "klook_aid": "aid",
    "klook_charter_aid": "aid",
    "trip_allianceid": "Allianceid",
    "trip_sid": "SID",
    "trip_sub3": "trip_sub3",
    "trip_flight_sub3": "trip_sub3",
}

# 額外的來源檔（除了 content/<lang>/*.json 之外也要一起同步）。
EXTRA_FILES = (
    os.path.join("klook", "klook_products_all.json"),
    os.path.join("klook", "car_page.csv"),
)


def discover_files():
    """回傳所有會被掃描/替換的檔案（絕對路徑）。"""
    files = []
    content_root = os.path.join(HERE, "content")
    for lang_dir in sorted(glob.glob(os.path.join(content_root, "*"))):
        if not os.path.isdir(lang_dir):
            continue
        if os.path.basename(lang_dir) == "_translations":
            continue
        for path in sorted(glob.glob(os.path.join(lang_dir, "*.json"))):
            files.append(path)
    for rel in EXTRA_FILES:
        path = os.path.join(HERE, rel)
        if os.path.isfile(path):
            files.append(path)
    return files


def load_links():
    with open(LINKS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def save_links(links):
    with open(LINKS_PATH, "w", encoding="utf-8") as fh:
        json.dump(links, fh, ensure_ascii=False, indent=4)
        fh.write("\n")


def allowed_values(links):
    """param 名稱 -> 允許值集合（aid 有兩個合法值）。"""
    by_param = {}
    for key, param in PARAM_OF_KEY.items():
        by_param.setdefault(param, set()).add(links[key])
    return by_param


def scan(links):
    """掃描所有檔案，回傳每個 key 的出現次數與漂移（drift）狀況。"""
    counts = {key: 0 for key in PARAM_OF_KEY}
    drift = []  # (file, param, value)
    allowed = allowed_values(links)
    for path in discover_files():
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for key, param in PARAM_OF_KEY.items():
            token = "%s=%s" % (param, links[key])
            counts[key] += text.count(token)
        # 偵測「參數存在但值不在允許集合」的漏網之魚。
        for param, vals in allowed.items():
            for match in re.finditer(re.escape(param) + r"=([A-Za-z0-9]+)", text):
                if match.group(1) not in vals:
                    drift.append((os.path.relpath(path, HERE), param, match.group(1)))
    return counts, drift


def report(links):
    counts, drift = scan(links)
    print("== 推薦連結分潤參數現況（來源 links.json）==\n")
    for key, param in PARAM_OF_KEY.items():
        value = links[key]
        print("  %-18s  %s=%-14s  %5d 處" % (key, param, value, counts[key]))
    if drift:
        print("\n== 警告：發現不在 links.json 裡的參數值 ==\n")
        seen = set()
        for path, param, value in drift:
            item = (param, value)
            if item in seen:
                continue
            seen.add(item)
            print("  %s=%s  （例：%s）" % (param, value, path))
    else:
        print("\n所有檔案的分潤參數都與 links.json 一致。")


def do_set(key, new_value, dry_run):
    links = load_links()
    if key not in PARAM_OF_KEY:
        sys.exit("錯誤：未知的 key「%s」，可用：%s" % (key, ", ".join(PARAM_OF_KEY)))
    param = PARAM_OF_KEY[key]
    old_value = links[key]
    if old_value == new_value:
        print("無需變更：%s 已是 %s=%s" % (key, param, new_value))
        return
    token_old = "%s=%s" % (param, old_value)
    token_new = "%s=%s" % (param, new_value)

    total = 0
    touched = []
    for path in discover_files():
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        n = text.count(token_old)
        if n == 0:
            continue
        total += n
        touched.append((path, n))
        if not dry_run:
            new_text = text.replace(token_old, token_new)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new_text)

    action = "預覽（dry-run，未寫檔）" if dry_run else "已套用"
    print("%s：%s=%s -> %s=%s，共 %d 處，%d 個檔案" %
          (action, param, old_value, param, new_value, total, len(touched)))
    if not dry_run and total:
        links[key] = new_value
        save_links(links)
        print("已更新 links.json：%s = %s" % (key, new_value))


def main():
    parser = argparse.ArgumentParser(description="集中管理推薦連結分潤 ID")
    parser.add_argument("--set", metavar="KEY=NEW", help="改值並套用，例如 klook_aid=999999")
    parser.add_argument("--dry-run", action="store_true", help="只預覽，不寫任何檔案")
    parser.add_argument("--files", action="store_true", help="列出會被掃描到的檔案")
    args = parser.parse_args()

    if args.files:
        for path in discover_files():
            print(os.path.relpath(path, HERE))
        return

    if args.set:
        if "=" not in args.set:
            sys.exit("錯誤：--set 格式應為 KEY=NEW，例如 --set klook_aid=999999")
        key, new_value = args.set.split("=", 1)
        do_set(key, new_value, args.dry_run)
        return

    report(load_links())


if __name__ == "__main__":
    main()
