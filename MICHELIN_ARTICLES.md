# 米其林餐廳文章

啟動新版後台：`python3 admin.py --port 8772`。

- [專刊編輯](http://127.0.0.1:8772/admin.html?file=content/zh/michelin_articles.json)
- [餐廳資料](http://127.0.0.1:8772/admin.html?file=content/zh/michelin.json)
- [前台頤宮專刊](http://127.0.0.1:8772/preview/michelin_info.html?id=star-1&lang=zh-TW)

專刊存在 `content/<lang>/michelin_articles.json`，文章的 `restaurantId` 對應 `michelin.json` 固定 ID。同一語言的每間餐廳只能有一篇；後端驗證餐廳存在、對應不重複、發布狀態與安全內容結構。

餐廳後台提供「新增餐廳」與「刪除餐廳」，新增可選米其林星級或必比登，固定 ID 自動產生。按存檔後，新增與刪除依 ID 同步至其他語言，保留既有餐廳譯文。若任一語言仍有對應文章，須先刪除該文章並存檔，才能刪除餐廳。

餐廳列表會標示「有專文」。可從餐廳表單按「檢視/編輯深度文章」開啟同語言的對應文章；沒有文章時按「為此餐廳建立專題報導」建立草稿。文章內可按「前往對應餐廳」返回該店，星級與必比登皆適用。也可直接在專刊編輯器新增後選擇對應餐廳。新增預設草稿，選「已發布」並存檔才會顯示。欄位包括餐廳故事、段落版型、圖片、獲獎紀錄、原生多語菜單與價格、用餐須知、SEO、店家資訊及官網訂位。

新增／刪除文章會在存檔時依 ID 跨語言同步，新增文字自動翻譯；既有文章的文字與發布狀態仍各語言獨立儲存。存檔後會更新相鄰 taiwan-travel 的 `data/michelin_articles/<lang>.json`；本機 `/preview/` 直接讀本機後台。若正在使用修改前就啟動的後台程序，請重啟以載入新的 Python 驗證與同步邏輯。

目前頤宮範例已有十二種內容語言；中英日七道菜單保留原稿。原稿照片是 Unsplash 設計示意，獲獎紀錄截至 2025 年，價格與訂位等內容仍待查核，前台保留範例提示。沒有文章的餐廳顯示缺省頁與店家資訊。

完整資料分析、欄位規格、重建流程在相鄰前端 `docs/michelin-articles.md`。一般 `content_translate.py` 會略過此資料集，避免覆寫翻譯。正式網站仍需依既有流程推送與部署。

```sh
python3 -m unittest test_admin.py test_editorial_admin.py test_editorial_translation.py test_admin_translation.py
```
