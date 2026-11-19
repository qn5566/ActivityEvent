# 採訪報導管理

啟動 `python3 admin.py --port 8770`，開啟：

- 管理：<http://127.0.0.1:8770/admin.html?file=content/zh/editorial_reports.json>
- 前台：<http://127.0.0.1:8770/preview/journals.html?type=reports&lang=zh-TW>

檔案為 `content/<lang>/editorial_reports.json`，十二種語言各十篇範例，目前均為 `published`，保留範例與待查核標記。前台顯示需要同時有 `status: "published"` 與 `published: true`；表單發布狀態會同時更新兩者。

表單支援搜尋、新增／排序／刪除報導、發布／草稿／封存、查核與範例標記、標題摘要、城市、封面、SEO、段落、表格、圖片集、周邊推薦與探訪資訊。固定 ID 保持不變。新增／刪除會在存檔時依 ID 跨語言同步，新增文字自動翻譯；既有文章仍各語言獨立編輯與發布，不透過位置同步覆寫譯文；切換語言時以固定 ID 保持同一篇報導。

段落可直接編輯文字、表格儲存格、清單與連結，也可在進階 JSON 修改結構。無效 JSON 會阻止儲存，後端拒絕重複 ID、矛盾發布狀態、錯誤結構及非 HTTP(S) 網址。`blocks` 存在時，儲存會自動重建完整純文字 `content`。

「查看前台」會開啟相鄰 taiwan-travel 專案的 `/preview/` 頁面，直接讀本機 JSON。儲存同時更新相鄰前端的 `data/editorial_reports/<lang>.json`，所以本機靜態前台也能看到變更。前端專案不存在時，後台仍可正常儲存。

正式站優先讀取 ActivityEvent 遠端內容，需依既有流程推送與部署才能更新。本機「已發布」是內容狀態，不會自動執行 Git 或部署。

原始資料與機器譯文仍待人工查核；沒有捏造作者、實訪日期或照片。匯入／翻譯來源及十二語完整性檢查位於 taiwan-travel 的 `scripts/build_editorial_reports.py`、`scripts/check_editorial_reports.py`；舊的 `content_translate.py` 會略過報導檔，避免覆寫獨立譯文。

驗證：

```sh
python3 -m unittest test_admin.py test_editorial_admin.py test_editorial_translation.py test_admin_translation.py
```
