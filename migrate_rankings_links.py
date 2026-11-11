#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 rankings.json 的單一 ctaType 升級成 links[]（支援每筆商品多條分潤連結）。

背景
----
原本每筆商品只有 ctaType（map/klook/dining/trip/owlting/souvenir），且
App 端其實沒在讀它（排行榜點擊是開 Google 地圖）。此腳本為每筆商品產生
links 陣列，讓 App 能真正按連結類型開啟對應的分潤網址，也讓管理頁可
逐筆新增/編輯多條連結（例如同一商品同時掛 Klook + Trip）。

links 元素結構
--------------
{"type": "klook", "label": "Klook 預訂", "url": "https://..."}

type 對應的預設網址（搜尋型用商品名稱，聯盟參數取自 links.json）：
  map      -> Google 地圖搜尋
  klook    -> Klook 搜尋（aid=klook_aid）
  dining   -> Klook 搜尋（aid=klook_aid）
  trip     -> Trip.com 訂房（Allianceid/SID/trip_sub*）
  owlting  -> OwlTing 搜尋
  souvenir -> 該主題的 ctaUrl（購物聯盟連結）

用法
----
  python3 migrate_rankings_links.py                # 正式寫入
  python3 migrate_rankings_links.py --dry-run      # 只預覽統計，不寫檔
"""

import argparse
import glob
import json
import os
import sys
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))

LINKS_PATH = os.path.join(HERE, "links.json")

# type -> (label, url 模板，{name} 與聯盟參數會被替換)
def build_templates(links):
    klook_aid = links.get("klook_aid", "106452")
    trip_allianceid = links.get("trip_allianceid", "9507030")
    trip_sid = links.get("trip_sid", "325761227")
    trip_sub1 = links.get("trip_sub1", "app")
    trip_sub3 = links.get("trip_sub3", "")
    return {
        "map": (
            "Google 地圖",
            "https://www.google.com/maps/search/?api=1&query={name}",
        ),
        "klook": (
            "Klook 預訂",
            "https://www.klook.com/search/?query={name}&aid=" + klook_aid,
        ),
        "dining": (
            "Klook 訂餐",
            "https://www.klook.com/search/?query={name}&aid=" + klook_aid,
        ),
        "trip": (
            "Trip 訂房",
            "https://tw.trip.com/hotels/?Allianceid=%s&SID=%s&trip_sub1=%s&trip_sub3=%s"
            % (trip_allianceid, trip_sid, trip_sub1, trip_sub3),
        ),
        "owlting": (
            "OwlTing 預訂",
            "https://www.owlting.com/market/search?keyword={name}",
        ),
        "souvenir": (
            "購買伴手禮",
            None,  # 用主題 ctaUrl
        ),
    }


def discover_files():
    files = []
    for path in sorted(glob.glob(os.path.join(HERE, "content", "*", "rankings.json"))):
        files.append(path)
    return files


def load_links():
    with open(LINKS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def migrate_file(path, templates, dry_run):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    data = json.loads(raw)
    minified = raw.count("\n") <= 1

    topics = {t.get("id"): t for t in data.get("topics", [])}
    items = data.get("items", {})
    changed = 0
    skipped = 0

    for topic_id, item_list in items.items():
        topic = topics.get(topic_id, {})
        for item in item_list:
            # 已存在 links 就跳過（冪等）
            if "links" in item:
                skipped += 1
                continue
            cta = item.get("ctaType", "")
            template = templates.get(cta)
            if not template:
                continue
            label, url_tpl = template
            name = item.get("name", "")
            if url_tpl is None:
                url = topic.get("ctaUrl", "")
            else:
                url = url_tpl.format(name=quote(name))
            item["links"] = [{"type": cta, "label": label, "url": url}]
            changed += 1

    if dry_run:
        return changed, skipped
    with open(path, "w", encoding="utf-8") as fh:
        if minified:
            json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return changed, skipped


def main():
    parser = argparse.ArgumentParser(description="rankings.json 升級為 links[]")
    parser.add_argument("--dry-run", action="store_true", help="只預覽，不寫檔")
    args = parser.parse_args()

    links = load_links()
    templates = build_templates(links)

    total_changed = 0
    total_skipped = 0
    for path in discover_files():
        changed, skipped = migrate_file(path, templates, args.dry_run)
        total_changed += changed
        total_skipped += skipped
        rel = os.path.relpath(path, HERE)
        print("%-28s 產生 %3d 筆 links，跳過 %3d 筆" % (rel, changed, skipped))

    action = "預覽（dry-run，未寫檔）" if args.dry_run else "已完成"
    print("\n%s：共產生 %d 筆 links，跳過 %d 筆（已存在）。" % (action, total_changed, total_skipped))


if __name__ == "__main__":
    main()
