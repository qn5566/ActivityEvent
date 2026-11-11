#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""補齊 railway / cinema 新主題的空缺欄位（title/subtitle/zhTitle/name/experiences/itineraries）。

title 與 enTitle 為全語言共用的英文文案；其餘欄位依語言各別填寫。
用法：python3 fill_themes_content.py [--dry-run]
"""

import argparse, glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))

RAILWAY = {
    "enTitle": "CLASSIC RAILWAYS",
    "title": "Riding Taiwan's Most Scenic Rail Lines",
}
CINEMA = {
    "enTitle": "MOVIE LOCATIONS",
    "title": "Step Into the Scenes of Your Favorite Films",
}

LOC = {
"railway": {
"zh": {
  "name": "全台經典鐵道巡禮",
  "zhTitle": "經典鐵道・山城海線與懷舊列車",
  "subtitle": "從阿里山森林鐵路到平溪天燈支線，搭上鳴日號與藍皮解憂號，沿著山城、海岸與縱谷，收藏全台最美的十條鐵道風景。",
  "experiences": [
    {"icon": "🚂", "title": "阿里山森林鐵路", "desc": "世界級高山鐵道，之字形爬升穿梭雲霧檜木林。"},
    {"icon": "🏮", "title": "平溪天燈支線", "desc": "山城瀑布與祈願天燈，鐵道旁的懷舊老街。"},
    {"icon": "🚃", "title": "鳴日號藍皮解憂號", "desc": "復古美饌列車，慢速漫遊東海岸與南迴。"},
  ],
  "itineraries": [
    {"planName": "【1 日輕旅】山城鐵道一日遊", "duration": "1 日經典", "days": [
      {"day": "精華動線", "text": "平溪支線十分車站放天燈 ➔ 猴硐貓村 ➔ 深澳八斗子海景車站。"},
    ]},
    {"planName": "【2 日漫遊】森林與海線鐵道慢活", "duration": "2 天 1 夜", "days": [
      {"day": "Day 1", "text": "阿里山森林鐵路日出 ➔ 嘉義檜意森活村 ➔ 奮起湖便當。"},
      {"day": "Day 2", "text": "集集支線車埕 ➔ 內灣山城老街 ➔ 平溪十分天燈夜。"},
    ]},
  ],
},
"en": {
  "name": "Classic Railway Tour",
  "zhTitle": "Classic Railways · Mountain, Coast & Vintage Trains",
  "subtitle": "From the Alishan Forest Railway to the Pingxi sky-lantern line, ride the Future and Lan-pi nostalgic trains through mountain towns, coasts and rift valleys.",
  "experiences": [
    {"icon": "🚂", "title": "Alishan Forest Railway", "desc": "A world-class mountain line zigzagging through misty cypress forests."},
    {"icon": "🏮", "title": "Pingxi Sky Lantern Line", "desc": "Waterfalls, mountain towns and sky lanterns beside the tracks."},
    {"icon": "🚃", "title": "Future & Lan-pi Trains", "desc": "Vintage dining trains cruising the east coast and south-link line."},
  ],
  "itineraries": [
    {"planName": "【1-Day】Mountain Rail Highlights", "duration": "1 Day", "days": [
      {"day": "Route", "text": "Pingxi Shifen sky lanterns ➔ Houtong Cat Village ➔ Badouzi seaside station."},
    ]},
    {"planName": "【2-Day】Forest & Coast Rail", "duration": "2 Days 1 Night", "days": [
      {"day": "Day 1", "text": "Alishan forest railway sunrise ➔ Chiayi Hinoki Village ➔ Fenchihu lunchbox."},
      {"day": "Day 2", "text": "Jiji line Checheng ➔ Neiwan old street ➔ Shifen lantern night."},
    ]},
  ],
},
"ja": {
  "name": "全台クラシック鉄道めぐり",
  "zhTitle": "クラシック鉄道・山城と海線と懐かしの列車",
  "subtitle": "阿里山森林鉄道から平渓の天燈支線まで、鳴日号や藍皮解憂号に乗って、山城・海岸・渓谷を巡る台湾で最も美しい10の鉄道風景を集めました。",
  "experiences": [
    {"icon": "🚂", "title": "阿里山森林鉄道", "desc": "世界的な高山鉄道、ジグザグに雲海とヒノキ林を登る。"},
    {"icon": "🏮", "title": "平渓天燈支線", "desc": "山城の滝と願いを込めた天燈、線路沿いの懐かしい老街。"},
    {"icon": "🚃", "title": "鳴日号と藍皮解憂号", "desc": "レトロな美食列車で東海岸と南廻線をゆっくり旅する。"},
  ],
  "itineraries": [
    {"planName": "【1日】山城鉄道の旅", "duration": "1日", "days": [
      {"day": "ルート", "text": "平渓線十分駅で天燈 ➔ 猴硐猫村 ➔ 八斗子の海景駅。"},
    ]},
    {"planName": "【2日】森林と海線の鉄道", "duration": "1泊2日", "days": [
      {"day": "1日目", "text": "阿里山森林鉄道の日の出 ➔ 嘉義檜意森活村 ➔ 奮起湖弁当。"},
      {"day": "2日目", "text": "集集線車埕 ➔ 内湾の老街 ➔ 十分の天燈ナイト。"},
    ]},
  ],
},
"ko": {
  "name": "전국 클래식 철도 여행",
  "zhTitle": "클래식 철도 · 산촌 해안과 추억의 열차",
  "subtitle": "아리산 삼림철도에서 핑시 천등 지선까지, 명일호와 남피해우호를 타고 산촌·해안·협곡을 지나는 대만 최고의 열차 풍경 10선을 만나보세요.",
  "experiences": [
    {"icon": "🚂", "title": "아리산 삼림철도", "desc": "세계적인 고산 철도, 지그재그로 운무와 삼나무 숲을 오른다."},
    {"icon": "🏮", "title": "핑시 천등 지선", "desc": "산촌 폭포와 소원 천등, 철길 옆 옛 거리."},
    {"icon": "🚃", "title": "명일호와 남피해우호", "desc": "복고풍 미식 열차로 동해안과 남회선을 느긋하게 여행한다."},
  ],
  "itineraries": [
    {"planName": "【1일】산촌 철도 여행", "duration": "1일", "days": [
      {"day": "코스", "text": "핑시선 스펀역 천등 ➔ 허우퉁 고양이 마을 ➔ 바더우쯔 해안역."},
    ]},
    {"planName": "【2일】숲과 해안 철도", "duration": "1박 2일", "days": [
      {"day": "1일차", "text": "아리산 삼림철도 일출 ➔ 자이 히노키 마을 ➔ 펀치후 도시락."},
      {"day": "2일차", "text": "지지선 처청 ➔ 네이완 옛 거리 ➔ 스펀 천등 밤."},
    ]},
  ],
},
"th": {
  "name": "ทริปรถไฟคลาสสิกทั่วไต้หวัน",
  "zhTitle": "รถไฟคลาสสิก · เมืองเขา ชายทะเล และรถไฟวินเทจ",
  "subtitle": "จากรถไฟป่าอาลีซานถึงรถไฟสายผิงซีโคมลอย นั่งรถไฟหมิงรื่อห่าวและรถไฟสีฟ้า เที่ยวเมืองเขา ชายฝั่ง และหุบเขา ชมวิวรถไฟที่สวยที่สุด 10 สายของไต้หวัน",
  "experiences": [
    {"icon": "🚂", "title": "รถไฟป่าอาลีซาน", "desc": "รถไฟภูเขาระดับโลก คดเคี้ยวผ่านป่าสนและทะเลหมอก"},
    {"icon": "🏮", "title": "สายผิงซีโคมลอย", "desc": "น้ำตกเมืองเขาและโคมลอยอธิษฐาน ริมรางรถไฟ"},
    {"icon": "🚃", "title": "รถไฟหมิงรื่อห่าว", "desc": "รถไฟอาหารวินเทจ ล่องช้าชายฝั่งตะวันออก"},
  ],
  "itineraries": [
    {"planName": "【1 วัน】ทริปรถไฟเมืองเขา", "duration": "1 วัน", "days": [
      {"day": "เส้นทาง", "text": "สถานีฉือเฟินปล่อยโคมลอย ➔ หมู่บ้านแมวโฮ่วถง ➔ สถานีปาโต่วจื่อ"},
    ]},
    {"planName": "【2 วัน】รถไฟป่าและชายฝั่ง", "duration": "2 วัน 1 คืน", "days": [
      {"day": "วันที่ 1", "text": "ชมพระอาทิตย์ขึ้นบนรถไฟอาลีซาน ➔ หมู่บ้านจางฮวา ➔ ข้าวกล่องเฟินฉีหู"},
      {"day": "วันที่ 2", "text": "สายจี๋จี๋ ➔ เมืองเก่าเน่ยวาน ➔ ค่ำคืนโคมลอยฉือเฟิน"},
    ]},
  ],
},
"vi": {
  "name": "Hành trình đường sắt cổ điển Đài Loan",
  "zhTitle": "Đường sắt cổ điển · Núi non, biển và những chuyến tàu hoài niệm",
  "subtitle": "Từ đường sắt rừng Alishan đến tuyến đèn trời Pingxi, lên tàu Mingrihao và tàu xanh, rong ruổi qua phố núi, bờ biển và thung lũng, thu trọn 10 cung đường sắt đẹp nhất Đài Loan.",
  "experiences": [
    {"icon": "🚂", "title": "Đường sắt rừng Alishan", "desc": "Tuyến đường sắt núi đẳng cấp thế giới, leo zíc zắc qua rừng bách mây mù."},
    {"icon": "🏮", "title": "Tuyến đèn trời Pingxi", "desc": "Thác nước phố núi và đèn trời cầu nguyện bên đường ray."},
    {"icon": "🚃", "title": "Tàu Mingrihao & tàu xanh", "desc": "Tàu ẩm thực cổ điển, thong thả dọc bờ biển phía đông."},
  ],
  "itineraries": [
    {"planName": "【1 ngày】Đường sắt phố núi", "duration": "1 ngày", "days": [
      {"day": "Lộ trình", "text": "Ga Shifen thả đèn trời ➔ Làng mèo Houtong ➔ Ga biển Badouzi."},
    ]},
    {"planName": "【2 ngày】Đường sắt rừng và biển", "duration": "2 ngày 1 đêm", "days": [
      {"day": "Ngày 1", "text": "Bình minh đường sắt Alishan ➔ Làng gỗ Hinoki Gia Nghĩa ➔ Cơm hộp Fenchihu."},
      {"day": "Ngày 2", "text": "Tuyến Jiji Checheng ➔ Phố cổ Neiwan ➔ Đêm đèn trời Shifen."},
    ]},
  ],
},
"ms": {
  "name": "Jelajah Kereta Api Klasik Taiwan",
  "zhTitle": "Kereta Api Klasik · Gunung, Pantai & Kereta Nostalgia",
  "subtitle": "Dari Kereta Api Hutan Alishan ke laluan tanglung Pingxi, naiki kereta Mingrihao dan kereta biru, meneroka pekan gunung, pantai dan lembah, mengumpul 10 laluan kereta api tercantik di Taiwan.",
  "experiences": [
    {"icon": "🚂", "title": "Kereta Api Hutan Alishan", "desc": "Laluan kereta api gunung bertaraf dunia, mendaki zigzag merentas hutan cemara berkabus."},
    {"icon": "🏮", "title": "Laluan Tanglung Pingxi", "desc": "Air terjun pekan gunung dan tanglung hajat di tepi landasan."},
    {"icon": "🚃", "title": "Kereta Mingrihao & Biru", "desc": "Kereta santapan vintaj, bersiar perlahan di pantai timur."},
  ],
  "itineraries": [
    {"planName": "【1 Hari】Kereta Api Pekan Gunung", "duration": "1 Hari", "days": [
      {"day": "Laluan", "text": "Stesen Shifen lepaskan tanglung ➔ Kampung Kucing Houtong ➔ Stesen pantai Badouzi."},
    ]},
    {"planName": "【2 Hari】Kereta Api Hutan & Pantai", "duration": "2 Hari 1 Malam", "days": [
      {"day": "Hari 1", "text": "Matahari terbit kereta api Alishan ➔ Kampung Hinoki Chiayi ➔ Bekal Fenchihu."},
      {"day": "Hari 2", "text": "Laluan Jiji Checheng ➔ Pekan lama Neiwan ➔ Malam tanglung Shifen."},
    ]},
  ],
},
"fil": {
  "name": "Classic Railway Tour ng Taiwan",
  "zhTitle": "Classic Railways · Bundok, Dagat at Vintage na Tren",
  "subtitle": "Mula sa Alishan Forest Railway hanggang sa Pingxi sky-lantern line, sumakay sa Mingrihao at asul na tren, libutin ang mga bayan sa bundok, baybayin at lambak, kolektahin ang 10 pinakamagandang riles ng Taiwan.",
  "experiences": [
    {"icon": "🚂", "title": "Alishan Forest Railway", "desc": "World-class mountain line na pa-zigzag sa maulap na kagubatan."},
    {"icon": "🏮", "title": "Pingxi Sky Lantern Line", "desc": "Talon, bayan sa bundok at sky lantern sa tabi ng riles."},
    {"icon": "🚃", "title": "Mingrihao at Asul na Tren", "desc": "Vintage dining train na mabagal sa silangang baybayin."},
  ],
  "itineraries": [
    {"planName": "【1 Araw】Riles ng Bayan sa Bundok", "duration": "1 Araw", "days": [
      {"day": "Ruta", "text": "Shifen station sky lantern ➔ Houtong Cat Village ➔ Badouzi seaside station."},
    ]},
    {"planName": "【2 Araw】Riles ng Gubat at Dagat", "duration": "2 Araw 1 Gabi", "days": [
      {"day": "Araw 1", "text": "Alishan railway sunrise ➔ Chiayi Hinoki Village ➔ Fenchihu lunchbox."},
      {"day": "Araw 2", "text": "Jiji line Checheng ➔ Neiwan old street ➔ Shifen lantern night."},
    ]},
  ],
},
"hi": {
  "name": "ताइवान क्लासिक रेलवे टूर",
  "zhTitle": "क्लासिक रेलवे · पर्वत, तट और पुरानी ट्रेनें",
  "subtitle": "अलीशान वन रेलवे से पिंगशी आकाश-दीप लाइन तक, मिंगरिहाओ और नीली ट्रेन में सवार होकर पर्वतीय कस्बों, तटों और घाटियों से होकर ताइवान की 10 सबसे सुंदर रेल लाइनें देखें।",
  "experiences": [
    {"icon": "🚂", "title": "अलीशान वन रेलवे", "desc": "विश्व स्तरीय पर्वतीय रेल, धुंध भरे देवदार वनों से होकर ज़िगज़ैग चढ़ाई।"},
    {"icon": "🏮", "title": "पिंगशी आकाश-दीप लाइन", "desc": "झरने, पर्वतीय कस्बे और पटरियों के किनारे आकाश-दीप।"},
    {"icon": "🚃", "title": "मिंगरिहाओ और नीली ट्रेन", "desc": "पुरानी भोजन ट्रेन, पूर्वी तट पर धीमी यात्रा।"},
  ],
  "itineraries": [
    {"planName": "【1 दिन】पर्वतीय रेल यात्रा", "duration": "1 दिन", "days": [
      {"day": "मार्ग", "text": "शिफेन स्टेशन आकाश-दीप ➔ हौतोंग बिल्ली गांव ➔ बादौज़ी तटीय स्टेशन।"},
    ]},
    {"planName": "【2 दिन】वन और तट रेल", "duration": "2 दिन 1 रात", "days": [
      {"day": "दिन 1", "text": "अलीशान रेल सूर्योदय ➔ चिआयी हिनोकी गांव ➔ फेनचिहु भोजन।"},
      {"day": "दिन 2", "text": "जीजी लाइन चेचेंग ➔ नेइवान पुरानी गली ➔ शिफेन दीप रात।"},
    ]},
  ],
},
"id": {
  "name": "Tur Kereta Api Klasik Taiwan",
  "zhTitle": "Kereta Klasik · Gunung, Pantai & Kereta Nostalgia",
  "subtitle": "Dari Kereta Api Hutan Alishan hingga jalur lampion Pingxi, naiki kereta Mingrihao dan kereta biru, jelajahi kota pegunungan, pantai, dan lembah, kumpulkan 10 jalur kereta terindah Taiwan.",
  "experiences": [
    {"icon": "🚂", "title": "Kereta Api Hutan Alishan", "desc": "Jalur kereta gunung kelas dunia, naik zigzag melintasi hutan cemara berkabut."},
    {"icon": "🏮", "title": "Jalur Lampion Pingxi", "desc": "Air terjun kota pegunungan dan lampion harapan di tepi rel."},
    {"icon": "🚃", "title": "Kereta Mingrihao & Biru", "desc": "Kereta santapan vintaj, berjalan santai di pantai timur."},
  ],
  "itineraries": [
    {"planName": "【1 Hari】Kereta Kota Pegunungan", "duration": "1 Hari", "days": [
      {"day": "Rute", "text": "Stasiun Shifen lepas lampion ➔ Kampung Kucing Houtong ➔ Stasiun pantai Badouzi."},
    ]},
    {"planName": "【2 Hari】Kereta Hutan & Pantai", "duration": "2 Hari 1 Malam", "days": [
      {"day": "Hari 1", "text": "Matahari terbit kereta Alishan ➔ Desa Hinoki Chiayi ➔ Bekal Fenchihu."},
      {"day": "Hari 2", "text": "Jalur Jiji Checheng ➔ Kota tua Neiwan ➔ Malam lampion Shifen."},
    ]},
  ],
},
"es": {
  "name": "Tour de Ferrocarriles Clásicos",
  "zhTitle": "Ferrocarriles Clásicos · Montaña, Costa y Trenes Nostálgicos",
  "subtitle": "Del ferrocarril forestal de Alishan a la línea de farolillos de Pingxi, sube al Mingrihao y al tren azul para recorrer pueblos de montaña, costas y valles, y descubre las 10 líneas más bonitas de Taiwán.",
  "experiences": [
    {"icon": "🚂", "title": "Ferrocarril Forestal de Alishan", "desc": "Línea de montaña de nivel mundial, en zigzag entre bosques de cipreses."},
    {"icon": "🏮", "title": "Línea de Farolillos de Pingxi", "desc": "Cascadas, pueblos de montaña y farolillos junto a las vías."},
    {"icon": "🚃", "title": "Trenes Mingrihao y Azul", "desc": "Trenes gastronómicos vintage que recorren la costa este."},
  ],
  "itineraries": [
    {"planName": "【1 día】Ferrocarril de Montaña", "duration": "1 día", "days": [
      {"day": "Ruta", "text": "Estación Shifen farolillos ➔ Aldea de los gatos Houtong ➔ Estación costera Badouzi."},
    ]},
    {"planName": "【2 días】Ferrocarril de Bosque y Costa", "duration": "2 días 1 noche", "days": [
      {"day": "Día 1", "text": "Amanecer en Alishan ➔ Aldea Hinoki de Chiayi ➔ Fiambrera de Fenchihu."},
      {"day": "Día 2", "text": "Línea Jiji Checheng ➔ Calle vieja de Neiwan ➔ Noche de farolillos Shifen."},
    ]},
  ],
},
},
"cinema": {
"zh": {
  "name": "影視朝聖之旅",
  "zhTitle": "影視朝聖・走進經典名場景",
  "subtitle": "跟著《不能說的秘密》《青春18×2》《刺客聶隱娘》等經典作品，走進台北101、大稻埕、淡水老街等銀幕名場景。",
  "experiences": [
    {"icon": "🎬", "title": "不能說的秘密", "desc": "淡水老街與八里左岸，重溫周杰倫的鋼琴初戀。"},
    {"icon": "🎞️", "title": "青春18×2", "desc": "台南保安車站，通往有你的旅程。"},
    {"icon": "🏙️", "title": "台北101", "desc": "信義商圈街區，多部電影的城市地標。"},
  ],
  "itineraries": [
    {"planName": "【1 日輕旅】台北影視地標巡禮", "duration": "1 日經典", "days": [
      {"day": "精華動線", "text": "台北101 ➔ 大稻埕永樂市場 ➔ 淡水老街與八里左岸。"},
    ]},
    {"planName": "【2 日漫遊】南北電影場景深度行", "duration": "2 天 1 夜", "days": [
      {"day": "Day 1", "text": "台北晶華酒店 ➔ 大稻埕 ➔ 台北101夜景。"},
      {"day": "Day 2", "text": "台南保安車站 ➔ 墾丁白沙灣 ➔ 佳樂水海景。"},
    ]},
  ],
},
"en": {
  "name": "Movie Location Tour",
  "zhTitle": "Movie Locations · Step Into Iconic Scenes",
  "subtitle": "Follow classic films like Secret, 18×2 and The Assassin to Taipei 101, Dadaocheng and Tamsui Old Street, and walk through the silver-screen scenes.",
  "experiences": [
    {"icon": "🎬", "title": "Secret", "desc": "Tamsui Old Street and Bali Left Bank, relive the piano romance."},
    {"icon": "🎞️", "title": "18×2", "desc": "Tainan Baoan Station, the journey to you."},
    {"icon": "🏙️", "title": "Taipei 101", "desc": "Xinyi district, the city landmark in many films."},
  ],
  "itineraries": [
    {"planName": "【1-Day】Taipei Film Landmarks", "duration": "1 Day", "days": [
      {"day": "Route", "text": "Taipei 101 ➔ Dadaocheng Yongle Market ➔ Tamsui Old Street."},
    ]},
    {"planName": "【2-Day】North & South Film Scenes", "duration": "2 Days 1 Night", "days": [
      {"day": "Day 1", "text": "Regent Taipei ➔ Dadaocheng ➔ Taipei 101 night view."},
      {"day": "Day 2", "text": "Tainan Baoan Station ➔ Kenting Baisha Bay ➔ Jialeshui coast."},
    ]},
  ],
},
"ja": {
  "name": "映画・ロケ地巡礼の旅",
  "zhTitle": "映画ロケ地巡礼・名シーンを歩く",
  "subtitle": "『言えない秘密』『青春18×2』『黒衣刺客』などの名作に登場する台北101、大稲埕、淡水老街など、映画の名シーンを実際に歩いてみましょう。",
  "experiences": [
    {"icon": "🎬", "title": "言えない秘密", "desc": "淡水老街と八里左岸で、ピアノの初恋を追体験。"},
    {"icon": "🎞️", "title": "青春18×2", "desc": "台南保安駅、あなたへ続く旅。"},
    {"icon": "🏙️", "title": "台北101", "desc": "信義地区、多くの映画に登場する都市のランドマーク。"},
  ],
  "itineraries": [
    {"planName": "【1日】台北映画ロケ地めぐり", "duration": "1日", "days": [
      {"day": "ルート", "text": "台北101 ➔ 大稲埕永楽市場 ➔ 淡水老街。"},
    ]},
    {"planName": "【2日】北と南の映画の舞台", "duration": "1泊2日", "days": [
      {"day": "1日目", "text": "台北晶華酒店 ➔ 大稲埕 ➔ 台北101の夜景。"},
      {"day": "2日目", "text": "台南保安駅 ➔ 墾丁白沙湾 ➔ 佳楽水の海。"},
    ]},
  ],
},
"ko": {
  "name": "영화 촬영지 순례 여행",
  "zhTitle": "영화 촬영지 순례 · 명장면 속으로",
  "subtitle": "《말할 수 없는 비밀》《청춘18×2》《자객섭은낭》등 명작 속 타이베이101, 다다오청, 단수이 옛거리를 직접 걸어보세요.",
  "experiences": [
    {"icon": "🎬", "title": "말할 수 없는 비밀", "desc": "단수이 옛거리와 발리 좌안에서 피아노 첫사랑을 다시."},
    {"icon": "🎞️", "title": "청춘18×2", "desc": "타이난 보안역, 당신에게 이어지는 여행."},
    {"icon": "🏙️", "title": "타이베이101", "desc": "신이 지구, 많은 영화에 등장한 도시 랜드마크."},
  ],
  "itineraries": [
    {"planName": "【1일】타이베이 영화 랜드마크", "duration": "1일", "days": [
      {"day": "코스", "text": "타이베이101 ➔ 다다오청 용러시장 ➔ 단수이 옛거리."},
    ]},
    {"planName": "【2일】남북 영화 촬영지", "duration": "1박 2일", "days": [
      {"day": "1일차", "text": "타이베이 리젠트 호텔 ➔ 다다오청 ➔ 타이베이101 야경."},
      {"day": "2일차", "text": "타이난 보안역 ➔ 컨딩 바이사완 ➔ 자러수이 해변."},
    ]},
  ],
},
"th": {
  "name": "ทัวร์ตามรอยสถานที่ถ่ายภาพยนตร์",
  "zhTitle": "ตามรอยภาพยนตร์ · เดินเข้าฉากดัง",
  "subtitle": "ตามรอยภาพยนตร์ดังอย่าง Secret, 18×2 และ The Assassin ไปยังไทเป 101, ต้าเต่าเฉิง และถนนเก่าตั้นสุ่ย เดินเข้าฉากบนจอเงิน",
  "experiences": [
    {"icon": "🎬", "title": "Secret", "desc": "ถนนเก่าตั้นสุ่ยและปาหลี รำลึกความรักแรกจากเปียโน"},
    {"icon": "🎞️", "title": "18×2", "desc": "สถานีเป่าอันไถหนาน การเดินทางที่มีคุณ"},
    {"icon": "🏙️", "title": "ไทเป 101", "desc": "ย่านซิ่นอี้ แลนด์มาร์กในภาพยนตร์หลายเรื่อง"},
  ],
  "itineraries": [
    {"planName": "【1 วัน】สถานที่ถ่ายภาพยนตร์ไทเป", "duration": "1 วัน", "days": [
      {"day": "เส้นทาง", "text": "ไทเป 101 ➔ ตลาดหย่งเล่อต้าเต่าเฉิง ➔ ถนนเก่าตั้นสุ่ย"},
    ]},
    {"planName": "【2 วัน】ฉากภาพยนตร์เหนือใต้", "duration": "2 วัน 1 คืน", "days": [
      {"day": "วันที่ 1", "text": "โรงแรมรีเจ้นท์ไทเป ➔ ต้าเต่าเฉิง ➔ วิวกลางคืนไทเป 101"},
      {"day": "วันที่ 2", "text": "สถานีเป่าอันไถหนาน ➔ หาดไป๋ซาเค็นติ้ง ➔ ชายฝั่งเจียเล่อสุ่ย"},
    ]},
  ],
},
"vi": {
  "name": "Hành trình phim trường",
  "zhTitle": "Theo dấu phim ảnh · Bước vào khung cảnh kinh điển",
  "subtitle": "Theo các tác phẩm kinh điển như Secret, 18×2 và The Assassin, ghé thăm Taipei 101, Dadaocheng và phố cổ Đạm Thủy, bước vào những khung cảnh trên màn bạc.",
  "experiences": [
    {"icon": "🎬", "title": "Secret", "desc": "Phố cổ Đạm Thủy và bờ trái Bali, sống lại mối tình piano."},
    {"icon": "🎞️", "title": "18×2", "desc": "Ga Bảo An Đài Nam, hành trình đến bên bạn."},
    {"icon": "🏙️", "title": "Taipei 101", "desc": "Khu Tín Nghĩa, biểu tượng thành phố trong nhiều bộ phim."},
  ],
  "itineraries": [
    {"planName": "【1 ngày】Địa danh phim ảnh Đài Bắc", "duration": "1 ngày", "days": [
      {"day": "Lộ trình", "text": "Taipei 101 ➔ Chợ Vĩnh Lạc Dadaocheng ➔ Phố cổ Đạm Thủy."},
    ]},
    {"planName": "【2 ngày】Bối cảnh phim Bắc Nam", "duration": "2 ngày 1 đêm", "days": [
      {"day": "Ngày 1", "text": "Khách sạn Regent Taipei ➔ Dadaocheng ➔ Đêm Taipei 101."},
      {"day": "Ngày 2", "text": "Ga Bảo An Đài Nam ➔ Bãi Bạch Sa Khẳng Đinh ➔ Bờ biển Giai Lạc Thủy."},
    ]},
  ],
},
"ms": {
  "name": "Jelajah Lokasi Filem",
  "zhTitle": "Jejak Filem · Melangkah ke Adegan Ikonik",
  "subtitle": "Ikuti filem klasik seperti Secret, 18×2 dan The Assassin ke Taipei 101, Dadaocheng dan Old Street Tamsui, melangkah ke adegan di layar perak.",
  "experiences": [
    {"icon": "🎬", "title": "Secret", "desc": "Old Street Tamsui dan tebing kiri Bali, hayati semula kisah cinta piano."},
    {"icon": "🎞️", "title": "18×2", "desc": "Stesen Baoan Tainan, perjalanan menuju anda."},
    {"icon": "🏙️", "title": "Taipei 101", "desc": "Daerah Xinyi, mercu tanda bandar dalam banyak filem."},
  ],
  "itineraries": [
    {"planName": "【1 Hari】Mercu Tanda Filem Taipei", "duration": "1 Hari", "days": [
      {"day": "Laluan", "text": "Taipei 101 ➔ Pasar Yongle Dadaocheng ➔ Old Street Tamsui."},
    ]},
    {"planName": "【2 Hari】Adegan Filem Utara & Selatan", "duration": "2 Hari 1 Malam", "days": [
      {"day": "Hari 1", "text": "Hotel Regent Taipei ➔ Dadaocheng ➔ Pemandangan malam Taipei 101."},
      {"day": "Hari 2", "text": "Stesen Baoan Tainan ➔ Teluk Baisha Kenting ➔ Pantai Jialeshui."},
    ]},
  ],
},
"fil": {
  "name": "Movie Location Tour",
  "zhTitle": "Mga Lokasyon ng Pelikula · Pasukin ang mga Iconic na Eksena",
  "subtitle": "Sundan ang mga klasikong pelikula tulad ng Secret, 18×2 at The Assassin patungong Taipei 101, Dadaocheng at Tamsui Old Street.",
  "experiences": [
    {"icon": "🎬", "title": "Secret", "desc": "Tamsui Old Street at Bali Left Bank, balikan ang piano romance."},
    {"icon": "🎞️", "title": "18×2", "desc": "Tainan Baoan Station, ang paglalakbay patungo sa iyo."},
    {"icon": "🏙️", "title": "Taipei 101", "desc": "Xinyi district, ang city landmark sa maraming pelikula."},
  ],
  "itineraries": [
    {"planName": "【1 Araw】Mga Landmark ng Pelikula sa Taipei", "duration": "1 Araw", "days": [
      {"day": "Ruta", "text": "Taipei 101 ➔ Dadaocheng Yongle Market ➔ Tamsui Old Street."},
    ]},
    {"planName": "【2 Araw】Mga Eksena sa Hilaga at Timog", "duration": "2 Araw 1 Gabi", "days": [
      {"day": "Araw 1", "text": "Regent Taipei ➔ Dadaocheng ➔ Taipei 101 night view."},
      {"day": "Araw 2", "text": "Tainan Baoan Station ➔ Kenting Baisha Bay ➔ Jialeshui coast."},
    ]},
  ],
},
"hi": {
  "name": "फ़िल्म लोकेशन टूर",
  "zhTitle": "फ़िल्म लोकेशन · मशहूर दृश्यों में कदम रखें",
  "subtitle": "सीक्रेट, 18×2 और द असैसिन जैसी फ़िल्मों की राह पर चलते हुए ताइपे 101, दादाओचेंग और तमसुई ओल्ड स्ट्रीट के चर्चित दृश्य देखें।",
  "experiences": [
    {"icon": "🎬", "title": "सीक्रेट", "desc": "तमसुई ओल्ड स्ट्रीट और बाली लेफ्ट बैंक, पियानो रोमांस को फिर जिएं।"},
    {"icon": "🎞️", "title": "18×2", "desc": "ताइनान बाओआन स्टेशन, आप तक पहुंचने की यात्रा।"},
    {"icon": "🏙️", "title": "ताइपे 101", "desc": "शिनयी ज़िला, कई फ़िल्मों का शहर प्रतीक।"},
  ],
  "itineraries": [
    {"planName": "【1 दिन】ताइपे फ़िल्म स्थल", "duration": "1 दिन", "days": [
      {"day": "मार्ग", "text": "ताइपे 101 ➔ दादाओचेंग योंगले बाज़ार ➔ तमसुई ओल्ड स्ट्रीट।"},
    ]},
    {"planName": "【2 दिन】उत्तर-दक्षिण फ़िल्म दृश्य", "duration": "2 दिन 1 रात", "days": [
      {"day": "दिन 1", "text": "रीजेंट ताइपे ➔ दादाओचेंग ➔ ताइपे 101 रात्रि दृश्य।"},
      {"day": "दिन 2", "text": "ताइनान बाओआन स्टेशन ➔ केंटिंग बैशा बे ➔ जियालेशुई तट।"},
    ]},
  ],
},
"id": {
  "name": "Tur Lokasi Film",
  "zhTitle": "Jejak Film · Melangkah ke Adegan Ikonik",
  "subtitle": "Ikuti film klasik seperti Secret, 18×2 dan The Assassin ke Taipei 101, Dadaocheng dan Tamsui Old Street, melangkah ke adegan di layar perak.",
  "experiences": [
    {"icon": "🎬", "title": "Secret", "desc": "Tamsui Old Street dan tebing kiri Bali, hidupkan kembali kisah piano."},
    {"icon": "🎞️", "title": "18×2", "desc": "Stasiun Baoan Tainan, perjalanan menuju dirimu."},
    {"icon": "🏙️", "title": "Taipei 101", "desc": "Kawasan Xinyi, ikon kota dalam banyak film."},
  ],
  "itineraries": [
    {"planName": "【1 Hari】Landmark Film Taipei", "duration": "1 Hari", "days": [
      {"day": "Rute", "text": "Taipei 101 ➔ Pasar Yongle Dadaocheng ➔ Tamsui Old Street."},
    ]},
    {"planName": "【2 Hari】Adegan Film Utara & Selatan", "duration": "2 Hari 1 Malam", "days": [
      {"day": "Hari 1", "text": "Hotel Regent Taipei ➔ Dadaocheng ➔ Pemandangan malam Taipei 101."},
      {"day": "Hari 2", "text": "Stasiun Baoan Tainan ➔ Teluk Baisha Kenting ➔ Pantai Jialeshui."},
    ]},
  ],
},
"es": {
  "name": "Tour de Localizaciones de Cine",
  "zhTitle": "Localizaciones de Cine · Entra en Escenas Icónicas",
  "subtitle": "Sigue clásicos como Secret, 18×2 y The Assassin hasta Taipei 101, Dadaocheng y la calle vieja de Tamsui, y camina por sus escenas de cine.",
  "experiences": [
    {"icon": "🎬", "title": "Secret", "desc": "Calle vieja de Tamsui y margen izquierda de Bali, revive el romance del piano."},
    {"icon": "🎞️", "title": "18×2", "desc": "Estación de Baoan, Tainan, el viaje hacia ti."},
    {"icon": "🏙️", "title": "Taipei 101", "desc": "Distrito de Xinyi, el símbolo de la ciudad en muchas películas."},
  ],
  "itineraries": [
    {"planName": "【1 día】Escenarios de Cine en Taipéi", "duration": "1 día", "days": [
      {"day": "Ruta", "text": "Taipei 101 ➔ Mercado Yongle de Dadaocheng ➔ Calle vieja de Tamsui."},
    ]},
    {"planName": "【2 días】Escenas del Norte y Sur", "duration": "2 días 1 noche", "days": [
      {"day": "Día 1", "text": "Regent Taipei ➔ Dadaocheng ➔ Vista nocturna de Taipei 101."},
      {"day": "Día 2", "text": "Estación Baoan de Tainan ➔ Bahía Baisha de Kenting ➔ Costa de Jialeshui."},
    ]},
  ],
},
},
}

LANG_MAP = {
  "zh": "zh", "en": "en", "ja": "ja", "ko": "ko", "th": "th", "vi": "vi",
  "ms": "ms", "fil": "fil", "hi": "hi", "id": "id", "es": "es",
}

def detect_indent(raw):
    for line in raw.split("\n")[1:]:
        s = line.lstrip(" ")
        if s and s[0] not in " \n":
            return len(line) - len(s)
    return 2

def apply_file(path, dry_run):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    data = json.loads(raw)
    minified = raw.count("\n") <= 1
    indent = detect_indent(raw)
    lang = os.path.basename(os.path.dirname(path))

    changed = 0
    for theme in data:
        tid = theme.get("id")
        if tid not in ("railway", "cinema"):
            continue
        base = RAILWAY if tid == "railway" else CINEMA
        loc = LOC[tid].get(lang)
        if loc is None:
            continue
        theme["enTitle"] = base["enTitle"]
        theme["title"] = base["title"]
        for k in ("name", "zhTitle", "subtitle"):
            theme[k] = loc[k]
        theme["experiences"] = loc["experiences"]
        theme["itineraries"] = loc["itineraries"]
        changed += 1

    if dry_run:
        return changed

    with open(path, "w", encoding="utf-8") as fh:
        if minified:
            json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(data, fh, ensure_ascii=False, indent=indent)
        fh.write("\n")
    return changed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    total = 0
    for path in sorted(glob.glob(os.path.join(HERE, "content", "*", "themes.json"))):
        lang = os.path.basename(os.path.dirname(path))
        c = apply_file(path, args.dry_run)
        total += c
        print("%-20s %d 個主題已補" % ("content/%s/themes.json" % lang, c))
    action = "預覽（dry-run）" if args.dry_run else "已完成"
    print("\n%s：共補 %d 個主題。" % (action, total))

if __name__ == "__main__":
    main()
