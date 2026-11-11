#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 northcoast（北海岸）主題裡的 railway（人氣鐵路）與 cinema（影視朝聖）
景點拆出，另建獨立主題；同時移除 culture（節慶文化）裡重複的 cinema。

背景
----
northcoast 主題原本混入 3 類景點：
  - coast   10 筆（真正的北海岸）
  - railway 10 筆（全台經典鐵道，NO.1~NO.10 人氣鐵路）
  - cinema  40 筆（影視朝聖，與 culture 主題完全重複）

本腳本：
  1. northcoast 只保留 coast。
  2. 新增 railway、cinema 兩個主題（景點、subCategories、分潤 bookingCta 從
     northcoast 沿用；標題/副標題/體驗/行程先留空，再於管理頁補翻譯）。
  3. culture 移除重複的 cinema 景點與 subCategory。

用法
----
  python3 migrate_themes_split.py            # 正式寫入（11 種語言）
  python3 migrate_themes_split.py --dry-run  # 只預覽統計
"""

import argparse
import copy
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def detect_indent(raw):
    for line in raw.split("\n")[1:]:
        stripped = line.lstrip(" ")
        if stripped and stripped[0] not in " \n":
            return len(line) - len(stripped)
    return 2


def discover_files():
    return sorted(glob.glob(os.path.join(HERE, "content", "*", "themes.json")))


def strip_icon_and_paren(name, icon):
    """去掉名稱前綴的 emoji 與結尾括號註記（中英文全半形括號都處理）。"""
    s = (name or "").strip()
    if icon and s.startswith(icon):
        s = s[len(icon):].lstrip()
    s = re.sub(r"[（(][^（）()]*[）)]\s*$", "", s).strip()
    return s


def build_theme(theme_id, sc, all_sc, spots, northcoast):
    icon = sc.get("icon", "")
    short = strip_icon_and_paren(sc.get("name", ""), icon) or theme_id
    first_img = (spots[0].get("img", "") if spots else "")
    return {
        "id": theme_id,
        "icon": icon,
        "shortTitle": short,
        "zhTitle": short,
        "enTitle": short,
        "name": short,
        "bannerImg": first_img,
        "deckBg": first_img,
        "title": "",
        "subtitle": "",
        "bookingCta": copy.deepcopy(northcoast.get("bookingCta", {})),
        "experiences": [],
        "itineraries": [],
        "spots": spots,
        "subCategories": [copy.deepcopy(all_sc), copy.deepcopy(sc)],
        "iconImg": first_img,
    }


def migrate_file(path, dry_run):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    data = json.loads(raw)
    minified = raw.count("\n") <= 1
    indent = detect_indent(raw)

    northcoast = next((t for t in data if t.get("id") == "northcoast"), None)
    culture = next((t for t in data if t.get("id") == "culture"), None)
    if northcoast is None or culture is None:
        return {"error": "找不到 northcoast / culture 主題"}

    # 先抓出 subCategory 定義與景點分組（在移除前）
    sc_by_id = {sc.get("id"): sc for sc in northcoast.get("subCategories", [])}
    all_sc = sc_by_id.get("all", {"id": "all", "name": "全部景點 All", "icon": "✨"})
    railway_sc = sc_by_id.get("railway")
    cinema_sc = sc_by_id.get("cinema")

    railway_spots = [s for s in northcoast.get("spots", []) if s.get("subCategory") == "railway"]
    cinema_spots = [s for s in northcoast.get("spots", []) if s.get("subCategory") == "cinema"]
    coast_spots = [s for s in northcoast.get("spots", []) if s.get("subCategory") == "coast"]

    # 1) northcoast 只留 coast
    northcoast["spots"] = coast_spots
    northcoast["subCategories"] = [sc for sc in northcoast.get("subCategories", [])
                                   if sc.get("id") in ("all", "coast")]

    # 2) culture 移除 cinema
    culture["spots"] = [s for s in culture.get("spots", []) if s.get("subCategory") != "cinema"]
    culture["subCategories"] = [sc for sc in culture.get("subCategories", [])
                                if sc.get("id") != "cinema"]

    # 3) 新增 railway / cinema 主題（插在 northcoast 之後）
    new_themes = []
    if railway_sc is not None and railway_spots:
        new_themes.append(build_theme("railway", railway_sc, all_sc, railway_spots, northcoast))
    if cinema_sc is not None and cinema_spots:
        new_themes.append(build_theme("cinema", cinema_sc, all_sc, cinema_spots, northcoast))

    idx = data.index(northcoast)
    for offset, theme in enumerate(new_themes):
        data.insert(idx + 1 + offset, theme)

    result = {
        "northcoast_spots": len(northcoast["spots"]),
        "railway_spots": len(railway_spots),
        "cinema_spots": len(cinema_spots),
        "culture_spots": len(culture["spots"]),
        "new_themes": [t["id"] for t in new_themes],
    }

    if dry_run:
        return result

    with open(path, "w", encoding="utf-8") as fh:
        if minified:
            json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(data, fh, ensure_ascii=False, indent=indent)
        fh.write("\n")
    return result


def main():
    parser = argparse.ArgumentParser(description="拆出 railway / cinema 主題")
    parser.add_argument("--dry-run", action="store_true", help="只預覽，不寫檔")
    args = parser.parse_args()

    for path in discover_files():
        rel = os.path.relpath(path, HERE)
        r = migrate_file(path, args.dry_run)
        if "error" in r:
            print("%-24s 錯誤：%s" % (rel, r["error"]))
            continue
        print("%-24s northcoast=%2d railway=%2d cinema=%2d culture=%2d 新主題=%s" % (
            rel, r["northcoast_spots"], r["railway_spots"], r["cinema_spots"],
            r["culture_spots"], ",".join(r["new_themes"])))

    action = "預覽（dry-run，未寫檔）" if args.dry_run else "已完成"
    print("\n%s。" % action)


if __name__ == "__main__":
    main()
