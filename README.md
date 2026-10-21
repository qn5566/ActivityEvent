# ActivityEvent
台灣活動展覽資訊

## 一鍵翻譯（推薦）

到任何一台新電腦，只需把整個專案資料夾複製過去，然後執行：

```sh
bash run.sh
```

`run.sh` 會自動完成六件事：

1. 檢查 Python 3
2. 建立虛擬環境（`.venv`）
3. 安裝依賴（argostranslate、pypinyin）
4. 下載語言模型（約 10 個，每個數十 MB，首次需連網）
5. 前置處理（專名音譯、食物/物種查表、符號保留，避免 argos 亂翻）
6. 離線翻譯並打包 ZIP（斷點續傳，可隨時 Ctrl-C，再次執行會接續）

全程不需 API key、不需付費。進度寫入 `data/translate.log`，用 `tail -f data/translate.log` 查看。

## 搬移到新電腦

複製這幾個東西即可（模型與依賴不用搬，`run.sh` 會自動處理）：

- 程式碼：`run.sh`、`preprocess.py`、`offline_translate.py`、`translate.py`、`update_data.py`、`README.md`
- 資料：`data/zh/`（原始中文）、`data/glossary.json`（食物/物種查表）、`data/_translations/`（翻譯成果，搬了才可斷點續傳）

一鍵打包（在舊電腦執行）：

```sh
tar czf /tmp/activityevent_migrate.tar.gz \
  run.sh preprocess.py offline_translate.py translate.py update_data.py README.md \
  data/zh data/glossary.json data/_translations
```

新電腦解壓後，直接 `bash run.sh` 即可接續。

## 前置處理

`preprocess.py` 在 argos 翻譯前，先用確定性規則預填對照表，避免 argos 把專名、食物、符號翻壞：

- 無漢字（符號／數字／ASCII）→ 保留原樣
- 食物／物種 → 查 `data/glossary.json`
- 地名／建物 → `pypinyin` 音譯 + 英文後綴（如 `七堵區 → Qidu District`）
- 圖片授權（`【姓名/拍攝】`）→ `Photo by 姓名`

正典策略：專名、食物、物種、授權的結果套用所有語言共用同一英文/拼音值。可單獨執行：

```sh
python3 preprocess.py --dry-run   # 只列統計與樣本，不寫檔
python3 preprocess.py             # 預填所有語言對照表（補缺漏）
python3 preprocess.py --force     # 連已有人工值也覆寫（謹慎）
```

## 翻譯說明

- 讀取 `data/zh/*.json`，翻譯到 `data/en/`、`data/ja/`、`data/ko/`、`data/th/`、`data/vi/`、`data/ms/`、`data/fil/`、`data/hi/`、`data/id/`、`data/es/`。
- 英文保留人工翻譯（地名、景點名、地址等），描述用離線翻譯補齊；其餘語言從英文中轉。
- 對照表存於 `data/_translations/<lang>.json`，斷點續傳靠它。
- 單一語言完成後自動打包：`Attraction` 三個 JSON 合併為 `Attraction-json.zip`，`Event`、`Restaurant` 各自打包。

## 只翻譯部分語言 / 手動打包

```sh
python3 offline_translate.py en ja    # 只翻譯指定語言
python3 translate.py en               # 手動套用並打包 en
```

## 更新原始繁體中文資料

```sh
python3 update_data.py --source-only
```

下載觀光署最新的景點、活動、餐飲 ZIP 到 `data/` 根目錄，並更新 `data/zh/` 的 JSON。
