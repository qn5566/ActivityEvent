#!/usr/bin/env bash
# ActivityEvent 一鍵翻譯：建立虛擬環境 → 安裝依賴 → 下載模型 → 前置處理 → 斷點續傳翻譯 → 打包
# 用法：bash run.sh   （到新電腦只需執行這一個命令）
set -e
cd "$(dirname "$0")"

echo "===== [1/6] 檢查 Python ====="
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ 找不到 python3，請先安裝 Python 3 後再執行"
  exit 1
fi
python3 --version

# 用虛擬環境，避免動到系統 Python（PEP 668 externally-managed-environment）
VENV=".venv"
if [ ! -x "$VENV/bin/python" ]; then
  echo "===== [2/6] 建立虛擬環境 ====="
  python3 -m venv "$VENV" || {
    echo "❌ 建立虛擬環境失敗。若是 Debian/Ubuntu，請先執行："
    echo "   sudo apt install -y python3-venv python3-pip"
    exit 1
  }
fi
PY="$VENV/bin/python"
PIP="$VENV/bin/pip"

echo "===== [3/6] 安裝依賴（argostranslate / pypinyin）====="
if "$PY" -c "import argostranslate, pypinyin" >/dev/null 2>&1; then
  echo "✅ 依賴已安裝"
else
  echo "安裝中 ..."
  "$PIP" install --upgrade pip >/dev/null
  "$PIP" install argostranslate pypinyin
  echo "✅ 依賴安裝完成"
fi

echo "===== [4/6] 檢查並下載語言模型 ====="
"$PY" - <<'PYEOF'
import argostranslate.package as ap
import argostranslate.translate as at
installed = {l.code for l in at.get_installed_languages()}
need = {"zh", "en", "ja", "ko", "th", "vi", "tl", "ms", "id", "hi", "es"}
missing = need - installed
if not missing:
    print("✅ 語言模型已齊全")
else:
    print(f"下載 {len(missing)} 個缺失的語言模型（需連網，每個數十 MB）...")
    ap.update_package_index()
    pkgs = ap.get_available_packages()
    pairs = [("zh","en"),("en","ja"),("en","ko"),("en","th"),("en","vi"),
             ("en","tl"),("en","ms"),("en","id"),("en","hi"),("en","es")]
    for f, t in pairs:
        if f in installed and t in installed:
            continue
        cands = [x for x in pkgs if x.from_code == f and x.to_code == t]
        if cands:
            ap.install_from_path(cands[0].download())
            installed.add(t)
            print(f"  {f}->{t} 完成")
    print("✅ 語言模型下載完成")
PYEOF

echo "===== [5/6] 前置處理（專名音譯 / 食物查表 / 符號保留）====="
"$PY" preprocess.py

echo "===== [6/6] 開始翻譯（斷點續傳，可隨時 Ctrl-C）====="
exec "$PY" offline_translate.py
