# 台灣吃喝玩樂 (Taiwan Wanderlust)
## 全球 IP 智能分流、多語系多幣別分潤架構與完整參數總規格書

本規格書整合了網站所有的**國際與亞洲分潤帳號**、**全球 IP 自動偵測分流引擎**（支援 8 大區域語系與幣別）、**全台縣市與雙北城鎮深層導購連結**，以及**全品類聯盟行銷變現矩陣**。

---

### 一、 全球 8 大區域 IP 智能分流與分潤對照表

系統會自動在背景透過地理位置 API 偵測訪客 IP，並依據下表自動分流到對應的語言、幣別與分潤通道：

| 區域代碼 / 國家 | ✈️ 機票搜尋 (Flights) | 🏨 住宿訂房 (Hotels) | 🚗 包車 / 導覽 (Charter/Activity) | 🚄 交通 / 網卡 (Transit / eSIM) |
| :--- | :--- | :--- | :--- | :--- |
| **🇹🇼 台灣本地 (TW/CN)** | Trip.com 繁中版<br>`Allianceid=9507030&SID=325761227&trip_sub3=D20272275` | Trip.com 22縣市直達<br>`Allianceid=9507030&SID=325761227&trip_sub3=D20272275` | Klook 台灣繁中版<br>`?aid=123436` | 12Go Asia / Klook eSIM<br>`https://12go.tpk.lu/HJqlAUCV` |
| **🇭🇰🇲🇴 港澳區 (HK/MO)** | Trip.com 香港繁中版 (HKD) | Trip.com 香港繁中版 | Klook 香港繁中版 (`zh-HK`) | 12Go Asia / Klook 網卡 |
| **🇸🇬🇲🇾 星馬區 (SG/MY)** | Trip.com 新加坡英文版 (SGD) | Trip.com 新加坡英文版 | Klook 英文版 (高客單包車) (`en-SG`) | 12Go Asia / Klook eSIM (`en-SG`) |
| **🇯🇵 日本 (JP)** | Trip.com 日本版 (日文/日圓) | Trip.com 日本版溫泉飯店 | Klook 日本版包車 (`ja`) | Trip.com 高鐵 / Klook eSIM (`ja`) |
| **🇰🇷 韓國 (KR)** | Trip.com 韓國版 (韓文/韓元) | Trip.com 韓國版西門町 | Klook 韓國版包車 (`ko`) | Klook 韓國版高鐵周遊券 (`ko`) |
| **🇹🇭🇻🇳🇮🇩 泰越印 (TH/VN/ID)** | Trip.com 在地母語版 (泰/越/印) | Trip.com 在地母語版 | Klook 在地語系版 (`th`/`vi`/`id`) | 12Go Asia 交通票券 |
| **🇵🇭🇮🇳 菲印及南亞 (PH/IN等)** | Trip.com 國際英文版 | Trip.com 國際英文版 | Klook 國際英文版 (`en-US`) | 12Go Asia / Klook 英文 eSIM |
| **🌍 歐美及全球非亞洲** | **Expedia**<br>`https://expedia.tpk.lu/64QomGwo` | **Hotels.com / Tripadvisor**<br>`https://hotels.tpk.lu/uK6ia0Jf` | **Viator**<br>`https://viator.tpk.lu/j9gLhFjQ` | **Yesim / 12Go Asia / Discover Cars** |

---

### 二、 台北市與新北市各城鎮 Trip.com 飯店搜尋分潤直達表

全台縣市（以雙北行政區為例，參數均帶入 `Allianceid=9507030&SID=325761227&trip_sub3=D20272275`）：

* **台北市 (city=617)**：
  * 全市總覽：`https://tw.trip.com/hotels/list?city=617&Allianceid=9507030&SID=325761227&trip_sub3=D20272275`
  * 台北車站/中正區：`https://tw.trip.com/hotels/list?city=617&keyword=%E5%8F%B0%E5%8C%97%E8%BB%8A%E7%AB%99&Allianceid=9507030&SID=325761227&trip_sub3=D20272275`
  * 西門町/萬華區：`https://tw.trip.com/hotels/list?city=617&keyword=%E8%A5%BF%E9%96%80%E7%94%BA&Allianceid=9507030&SID=325761227&trip_sub3=D20272275`
  * 信義區/101：`https://tw.trip.com/hotels/list?city=617&keyword=%E4%BF%A1%E7%BE%A9%E5%8D%80&Allianceid=9507030&SID=325761227&trip_sub3=D20272275`
  * 大安區/東區：`https://tw.trip.com/hotels/list?city=617&keyword=%E5%A4%A7%E5%AE%89%E5%8D%80&Allianceid=9507030&SID=325761227&trip_sub3=D20272275`
  * 北投溫泉區：`https://tw.trip.com/hotels/list?city=617&keyword=%E5%8C%97%E6%8A%95%E6%BA%AB%E6%B3%89&Allianceid=9507030&SID=325761227&trip_sub3=D20272275`

* **新北市 (city=7662)**：
  * 全新北總覽：`https://tw.trip.com/hotels/list?city=7662&Allianceid=9507030&SID=325761227&trip_sub3=D20272275`
  * 九份/金瓜石 (瑞芳區)：`https://tw.trip.com/hotels/list?city=7662&keyword=%E4%B9%9D%E4%BB%BD&Allianceid=9507030&SID=325761227&trip_sub3=D20272275`
  * 淡水區：`https://tw.trip.com/hotels/list?city=7662&keyword=%E6%B7%A1%E6%B0%B4&Allianceid=9507030&SID=325761227&trip_sub3=D20272275`
  * 烏來溫泉：`https://tw.trip.com/hotels/list?city=7662&keyword=%E7%83%8F%E4%BE%86&Allianceid=9507030&SID=325761227&trip_sub3=D20272275`
  * 板橋區 (耶誕城)：`https://tw.trip.com/hotels/list?city=7662&keyword=%E6%9D%BF%E6%A9%8B&Allianceid=9507030&SID=325761227&trip_sub3=D20272275`

---

### 三、 全專案分潤平台與商務參數總對齊表

```text
================================================================================
全專案分潤平台最新總覽表（完整版）
品牌：HiMyDream Studio
官方商務／資料聯繫信箱：himydream.studio0220@gmail.com
適用專案：【台灣吃喝玩樂 WEB/APP】＆【台灣寵物生活 APP】
================================================================================

【國際與亞洲旅遊平台】
01. Travelpayouts 活動備用短鏈 1：https://tpk.lu/BTY5qbO6
02. Travelpayouts 活動備用短鏈 2：https://tpk.lu/kF64e7qm
03. Expedia 智遊網（歐美機票主力）：https://expedia.tpk.lu/64QomGwo
04. Hotels.com（歐美住宿主力）：https://hotels.tpk.lu/uK6ia0Jf
05. Tripadvisor（全球評價比價）：https://tripadvisor.tpk.lu/EaPQmZiF
06. Viator（歐美包車/一日遊）：https://viator.tpk.lu/j9gLhFjQ
07. KKday（亞洲體驗票券）：https://kkday.tpk.lu/SZ7kd8Gl
08. 12Go Asia（火車、客運、離島船票）：https://12go.tpk.lu/HJqlAUCV
09. Discover Cars（全球自駕租車比價）：https://discovercars.tpk.lu/sUldB222
10. Yesim 國際 eSIM：https://yesim.tpk.lu/uMFlbh7Z
11. Trip.com 官方聯盟：Allianceid=9507030 & SID=325761227 & trip_sub3=D20272275
12. Klook 官方聯盟：?aid=123436
13. Klook 聯盟網台幣通道：https://affone.site/track/clicks/3731/c627c2b79e0620dbfe9cab248d219d46266e5b9633e0e5f30461a44125095ff88635aca3163d8e

【美食、伴手禮、生活選物與寵物 APP 電商】
14. 台灣訂餐與餐券 (affckr 4127)：https://affckr.site/track/clicks/4127/c627c2bc980126defc88ec23d62e9d47266c4cdf2aabebf00662b513234652eed671a3ea103a9e71?subid_1=台灣吃喝玩樂&subid_2=日本報報
15. 萬家福生鮮伴手禮 (afftck 4459)：https://afftck.com/track/clicks/4459/c627c2bc980522defc8dec23d62e9d47266c4cdf2aabebf00365bb13234652eed671a3ea103a9e71?subid_1=台灣吃喝玩樂&subid_2=日本報報
16. 露營生鮮食材箱 (aftck 1489)：https://aftck.com/track/clicks/1489/c627c2bc980522defc82ec23d62e9d47266c4cdf2aabebf50368bb13234652eed671a3ea103a9e71?subid_1=台灣吃喝玩樂&subid_2=日本報報
17. 台灣熱門藥妝店 (affckr 5891)：https://affckr.site/track/clicks/5891/c627c2bc9b0428dbf188ec23d62e9d47266c4cdf2aabebf10f69b313234652eed671a3ea103a9e71?subid_1=台灣吃喝玩樂&subid_2=日本報報
18. 質感選物店與文創 (affclkr 5686)：https://affclkr.online/track/clicks/5686/c627c2bf910421d7fb8dec23d62e9d47266c4cdf2aabebf10168b413234652eed671a3ea103a9e71?subid_1=台灣吃喝玩樂&subid_2=日本報報
19. 保健食品導購 (afftkr 2498)：https://afftkr.site/track/clicks/2498/c627c2bc900729d8fd9cab248d219d46266e5b9633e0e4f00e68a44125095ff88635aca3163d8e?subid_1=台灣吃喝玩樂
20. 奧丁丁在地深度體驗 (linkgo)：https://linkgo.one/s/ikCjF
21. Uber Eats 美食外送 (linkgo)：https://linkgo.one/s/qYLKx
22. 教育學習平台 (vbtrax 9445)：https://vbtrax.com/track/clicks/9445/c627c2bc9b0428dbf189ec23d62e9d47266c4cdf2aabebfd0364b713234652eed671a3ea103a9e71?subid_1=台灣吃喝玩樂&subid_2=日本報報
23. 線上學英文 (affckr 6826)：https://affckr.site/track/clicks/6826/c627c2bc9b0428dbf18eec23d62e9d47266c4cdf2aabebf20f62b413234652eed671a3ea103a9e71?subid_1=台灣吃喝&subid_2=日本報報&subid_3=學英文ＡＰＰ
24. 寵物嚴選品牌群（歸毛家族、汪咪寺、ParkCat、口碑嚴選、寵物配件、團購網卡）：均已帶入 `subid_1=寵物app` 追蹤參數。
================================================================================
```

---

### 四、 網頁版首頁 IP 智能分流與多語系 JavaScript 引擎

您可以直接將此程式碼交給 AI 或工程師部署至網頁前端：

```javascript
/**
 * 台灣吃喝玩樂 WEB - 全球 8 大區域 IP 智能分流與多語系引擎
 */
const TRIP_PARAMS = 'Allianceid=9507030&SID=325761227&trip_sub3=D20272275';
const KLOOK_AID = '123436';

const GLOBAL_AFFILIATE_MATRIX = {
  TW: {
    flights: `https://tw.trip.com/flights/?${TRIP_PARAMS}`,
    hotelBase: `https://tw.trip.com/hotels/list?${TRIP_PARAMS}`,
    charter: `https://www.klook.com/zh-TW/car-rentals/?aid=${KLOOK_AID}`,
    esim: `https://www.klook.com/zh-TW/search/result/?query=%E5%8F%B0%E7%81%A3eSIM%E7%B6%B2%E5%8D%A1&aid=${KLOOK_AID}`,
    transit: 'https://12go.tpk.lu/HJqlAUCV',
    carRental: 'https://discovercars.tpk.lu/sUldB222'
  },
  HK_MO: {
    flights: `https://hk.trip.com/flights/?${TRIP_PARAMS}`,
    hotelBase: `https://hk.trip.com/hotels/list?${TRIP_PARAMS}`,
    charter: `https://www.klook.com/zh-HK/car-rentals/?aid=${KLOOK_AID}`,
    esim: `https://www.klook.com/zh-HK/search/result/?query=%E5%8F%B0%E7%81%A3eSIM&aid=${KLOOK_AID}`,
    transit: 'https://12go.tpk.lu/HJqlAUCV',
    carRental: 'https://discovercars.tpk.lu/sUldB222'
  },
  SG_MY: {
    flights: `https://sg.trip.com/flights/?${TRIP_PARAMS}`,
    hotelBase: `https://sg.trip.com/hotels/list?${TRIP_PARAMS}`,
    charter: `https://www.klook.com/en-SG/search/result/?query=Taiwan%20Private%20Car%20Charter&aid=${KLOOK_AID}`,
    esim: `https://www.klook.com/en-SG/search/result/?query=Taiwan%20eSIM&aid=${KLOOK_AID}`,
    transit: 'https://12go.tpk.lu/HJqlAUCV',
    carRental: 'https://discovercars.tpk.lu/sUldB222'
  },
  JP: {
    flights: `https://jp.trip.com/flights/?${TRIP_PARAMS}`,
    hotelBase: `https://jp.trip.com/hotels/list?${TRIP_PARAMS}`,
    charter: `https://www.klook.com/ja/search/result/?query=%E5%8F%B0%E6%B9%BE%20%E8%B2%B8%E5%88%87%E3%83%81%E3%83%A3%E3%83%BC%E3%82%BF%E3%83%BC&aid=${KLOOK_AID}`,
    esim: `https://www.klook.com/ja/search/result/?query=%E5%8F%B0%E6%B9%BE%20eSIM&aid=${KLOOK_AID}`,
    transit: `https://jp.trip.com/trains/taiwan-high-speed-rail/?${TRIP_PARAMS}`,
    carRental: 'https://discovercars.tpk.lu/sUldB222'
  },
  KR: {
    flights: `https://kr.trip.com/flights/?${TRIP_PARAMS}`,
    hotelBase: `https://kr.trip.com/hotels/list?${TRIP_PARAMS}`,
    charter: `https://www.klook.com/ko/search/result/?query=%EB%8C%80%EB%A7%8C%20%ED%83%9D%EC%8B%9C%ED%88%AC%EC%96%B4&aid=${KLOOK_AID}`,
    esim: `https://www.klook.com/ko/search/result/?query=%EB%8C%80%EB%A7%8C%20eSIM&aid=${KLOOK_AID}`,
    transit: `https://www.klook.com/ko/activity/382-thsr-3-day-pass-taipei/?aid=${KLOOK_AID}`,
    carRental: 'https://discovercars.tpk.lu/sUldB222'
  },
  GLOBAL: {
    flights: 'https://expedia.tpk.lu/64QomGwo',
    hotelBase: 'https://hotels.tpk.lu/uK6ia0Jf',
    charter: 'https://viator.tpk.lu/j9gLhFjQ',
    esim: 'https://yesim.tpk.lu/uMFlbh7Z',
    transit: 'https://12go.tpk.lu/HJqlAUCV',
    carRental: 'https://discovercars.tpk.lu/sUldB222'
  }
};
```