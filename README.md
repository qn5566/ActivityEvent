# ActivityEvent
台灣活動展覽資訊

## 全球分潤分流

官網 `index.html` 與 WordPress 區塊 `taiwan-travel-map.html` 已加入旅程預訂區。
`affiliate.js` 讀取 `affiliate_config.json`，依 IP 國家分流到台灣／港澳／星馬／日本／韓國／泰越印／南亞／全球；泰、越、印尼各自保留母語與幣別。
使用者可以手動選擇市場，或選「Automatic / 自動偵測」恢復自動分流。IP 偵測限時 2.5 秒，國家結果快取 24 小時；失敗時依瀏覽器／手機系統語系備援。只快取國家碼與時間，不儲存 IP。

- `affiliate_config.json`：最新帳號、平台網址、區域語系與幣別、22 縣市與雙北指定行政區的共同來源。
- `links.json`：既有 App／腳本相容參數。Klook 統一 `123436`，Trip 機票與其他服務統一 `trip_sub3=D20272275`。
- 本機後台可從檔案選單編輯 `affiliate_config.json`；存檔會驗證必要欄位。修改後請執行 `python3 migrate_affiliate_links.py --apply`，更新內容內的舊連結及 `links.json`。不帶 `--apply` 只預覽。
- 原有 `python3 update_links.py --set KEY=VALUE` 也會同步共同設定中的追蹤參數；主帳號／包車、機票／其他 Trip 的相容別名會一起更新。
- 雙北使用規格提供的城市 ID（617、765）與行政區關鍵字；其餘 20 縣市使用關鍵字搜尋，尚未填入未經確認的城市 ID。
- 歐美預設 Expedia／Hotels.com／Viator／Yesim；12Go、Discover Cars、Tripadvisor 及生活服務使用規格提供的原始短鏈。短鏈沒有已確認的目的地參數，因此全球住宿不附加推測的城市參數。
- 幣別參數控制預訂網站的顯示偏好；既有內容的台幣參考價不做匯率換算，最終成交價格／幣別以平台顯示為準。
- 寵物品牌只提供了追蹤標籤，沒有實際網址，列於 `unconfigured`，待補網址後再開啟。

本機預覽官網：`python3 -m http.server 8000 --bind 127.0.0.1`，開啟 `http://127.0.0.1:8000/`。
WordPress 需同時部署 `affiliate.js`、`affiliate_config.json` 與 CSS；若 JSON 不在 JS 同目錄，請在 `data-affiliate-panel` 元素設定 `data-config-url="完整 HTTPS 網址"`，跨網域需允許 CORS。

Flutter 專案：`../ActivityEventFlutter`。App 已加入 `AffiliateService` 並接到共用 `launchExternal`；「好玩的」首頁可展開旅程預訂，調整市場與幣別、縣市／行政區。App 使用內附 `assets/affiliate_config.json` 備援，背景讀取本專案 main 分支發布的同名檔案。修改共同設定時，請同步更新 App 的內附備援副本。既有 App 語言偏好不會被 IP 偵測覆蓋；商品的特定目的地保留，只調整語系與追蹤參數；一般服務入口則依市場切換平台。

發布時需一併部署官網 JS／CSS／JSON、更新遠端內容，並重新建置與發行 Flutter App，既有安裝版本不會自動取得新程式功能。此修改不包含推送、官網部署或商店發行。

本專案驗證：`node --test test_affiliate.js test_affiliate_panel.js` 與 `python3 -m unittest test_affiliate_migration.py test_admin.py`。
Flutter 專案依其 `AGENTS.md` 規則，只有明確要求時才執行格式化、分析、測試或建置。

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
