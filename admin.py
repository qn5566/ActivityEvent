#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本機內容管理頁面（先支援 rankings.json）。

啟動後開啟瀏覽器 http://127.0.0.1:8765 即可檢視/編輯 content/<lang>/rankings.json。

用法
----
  python3 admin.py                 # 預設埠 8765
  python3 admin.py --port 9000     # 指定埠
  python3 admin.py --open          # 啟動後自動開啟瀏覽器

安全範圍：只能讀寫 content/、klook/ 底下的 .json，以及根目錄的 links.json、info.json。
"""

import argparse
import json
import os
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PORT = 8765

ALLOWED_DIRS = (
    os.path.join(HERE, "content"),
    os.path.join(HERE, "klook"),
)
ALLOWED_ROOT_FILES = {
    "links.json",
    "info.json",
}

# 這些檔在 11 種語言間完全一樣（無翻譯），存檔時「整份」同步到其他語言。
SYNC_ALL_FILES = {"charter.json"}

JSON_INDENT = 2
JSON_ENSURE_ASCII = False


def resolve_json(rel):
    """把相對路徑解析成絕對路徑，只允許白名單內的 .json。不合規則回傳 None。"""
    if not rel or not rel.endswith(".json"):
        return None
    if rel in ALLOWED_ROOT_FILES:
        return os.path.join(HERE, rel)
    cand = os.path.normpath(os.path.join(HERE, rel))
    for d in ALLOWED_DIRS:
        if cand == d or cand.startswith(d + os.sep):
            return cand
    return None


def detect_format(raw):
    """偵測原始 JSON 格式：minified（單行）與縮排空格數。"""
    minified = raw.count("\n") <= 1
    indent = 2
    if not minified:
        for line in raw.split("\n")[1:]:
            stripped = line.lstrip(" ")
            if stripped and stripped[0] not in " \n":
                indent = len(line) - len(stripped)
                break
    return minified, indent


def dump_json(data, minified, indent):
    if minified:
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(data, ensure_ascii=False, indent=indent)


def should_sync(key, value):
    """同步規則：http 開頭的字串，以及 links 內的 type 欄位。

    flight（themes.json 的 bookingCta.flight）例外：其 URL 依語言不同
    （出發城市 TPE/SIN/TYO/BKK…），故不做跨語言同步。
    """
    if key == "flight":
        return False
    if isinstance(value, str) and value.startswith("http"):
        return True
    if key == "type" and isinstance(value, str):
        return True
    return False


def sync_node(src, tgt):
    """把 src 中應同步的欄位（http / type）就地合併進 tgt（並行結構）。"""
    if isinstance(src, dict) and isinstance(tgt, dict):
        for key, sval in src.items():
            if should_sync(key, sval):
                tgt[key] = sval
            elif isinstance(sval, (dict, list)) and isinstance(tgt.get(key), (dict, list)):
                sync_node(sval, tgt[key])
    elif isinstance(src, list) and isinstance(tgt, list):
        for i, sval in enumerate(src):
            if i < len(tgt):
                sync_node(sval, tgt[i])


def sync_to_other_langs(rel, data):
    """把 data 的 http/type 欄位同步到其他語言同型檔案，回傳已同步的相對路徑清單。"""
    if not rel.startswith("content/"):
        return []
    parts = rel.split("/")
    if len(parts) != 3:
        return []
    _, lang, filename = parts
    synced = []
    content_root = os.path.join(HERE, "content")
    for other_lang in sorted(os.listdir(content_root)):
        if other_lang == lang or other_lang == "_translations":
            continue
        target_dir = os.path.join(content_root, other_lang)
        if not os.path.isdir(target_dir):
            continue
        target_path = os.path.join(target_dir, filename)
        if not os.path.isfile(target_path):
            continue
        with open(target_path, encoding="utf-8") as fh:
            raw = fh.read()
        try:
            target_data = json.loads(raw)
        except Exception:  # noqa: BLE001
            continue
        minified, indent = detect_format(raw)
        if filename in SYNC_ALL_FILES:
            import copy
            target_data = copy.deepcopy(data)
        else:
            sync_node(data, target_data)
        tmp = target_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(dump_json(target_data, minified, indent) + "\n")
        os.replace(tmp, target_path)
        synced.append("content/%s/%s" % (other_lang, filename))
    return synced


def list_files():
    """回傳 {相對資料夾: [files]} 清單，供前端下拉選單使用。"""
    result = {}
    content_root = os.path.join(HERE, "content")
    if os.path.isdir(content_root):
        for lang in sorted(os.listdir(content_root)):
            if lang == "_translations":
                continue
            lang_dir = os.path.join(content_root, lang)
            if not os.path.isdir(lang_dir):
                continue
            files = sorted(
                f for f in os.listdir(lang_dir)
                if f.endswith(".json") and os.path.isfile(os.path.join(lang_dir, f))
            )
            if files:
                result["content/" + lang] = files
    klook_root = os.path.join(HERE, "klook")
    if os.path.isdir(klook_root):
        files = sorted(
            f for f in os.listdir(klook_root)
            if f.endswith(".json") and os.path.isfile(os.path.join(klook_root, f))
        )
        if files:
            result["klook"] = files
    result["."] = sorted(ALLOWED_ROOT_FILES)
    return result


class Handler(BaseHTTPRequestHandler):
    server_version = "ActivityEventAdmin/1.0"

    def _send(self, code, payload, ctype="application/json; charset=utf-8"):
        body = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/" or path == "/admin.html":
            return self._serve_index()
        if path == "/api/files":
            return self._send(200, list_files())
        if path == "/api/file":
            qs = parse_qs(parsed.query)
            rel = qs.get("path", [""])[0]
            abs_path = resolve_json(rel)
            if not abs_path:
                return self._send(400, {"error": "不允許的路徑：%s" % rel})
            if not os.path.isfile(abs_path):
                return self._send(404, {"error": "檔案不存在：%s" % rel})
            try:
                with open(abs_path, encoding="utf-8") as fh:
                    data = json.load(fh)
            except Exception as exc:  # noqa: BLE001
                return self._send(500, {"error": "讀取失敗：%s" % exc})
            return self._send(200, {"path": rel, "data": data})
        if path == "/api/links":
            abs_path = os.path.join(HERE, "links.json")
            try:
                with open(abs_path, encoding="utf-8") as fh:
                    return self._send(200, json.load(fh))
            except Exception as exc:  # noqa: BLE001
                return self._send(500, {"error": str(exc)})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/file":
            qs = parse_qs(parsed.query)
            rel = qs.get("path", [""])[0]
            abs_path = resolve_json(rel)
            if not abs_path:
                return self._send(400, {"error": "不允許的路徑：%s" % rel})
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                data = json.loads(raw.decode("utf-8"))
            except Exception as exc:  # noqa: BLE001
                return self._send(400, {"error": "JSON 解析失敗：%s" % exc})
            try:
                with open(abs_path, encoding="utf-8") as fh:
                    orig_raw = fh.read()
                minified, indent = detect_format(orig_raw)
            except Exception:  # noqa: BLE001
                minified, indent = False, JSON_INDENT
            try:
                tmp = abs_path + ".tmp"
                with open(tmp, "w", encoding="utf-8") as fh:
                    fh.write(dump_json(data, minified, indent) + "\n")
                os.replace(tmp, abs_path)
            except Exception as exc:  # noqa: BLE001
                return self._send(500, {"error": "寫入失敗：%s" % exc})
            try:
                synced = sync_to_other_langs(rel, data)
            except Exception as exc:  # noqa: BLE001
                synced = []
                sys.stderr.write("[admin] 同步失敗：%s\n" % exc)
            return self._send(200, {"ok": True, "path": rel, "synced": synced})
        return self._send(404, {"error": "not found"})

    def _serve_index(self):
        html_path = os.path.join(HERE, "admin.html")
        if not os.path.isfile(html_path):
            return self._send(404, {"error": "找不到 admin.html"})
        with open(html_path, "rb") as fh:
            body = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("[admin] %s\n" % (fmt % args))


def main():
    parser = argparse.ArgumentParser(description="本機內容管理頁面")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--open", action="store_true", help="啟動後自動開啟瀏覽器")
    args = parser.parse_args()

    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = "http://127.0.0.1:%d" % args.port
    print("ActivityEvent 管理頁面已啟動：%s" % url)
    print("按 Ctrl-C 結束。")
    if args.open:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()
