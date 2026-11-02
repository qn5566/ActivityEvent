import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORE_DES_DIR = os.path.join(BASE_DIR, "store_des")

DESCRIPTIONS = {
    "desc_zh.txt": """【版本更新說明 / What's New】
全新 UI 介面改版，探索台灣更美好！
感謝大家對「台灣吃喝玩樂地圖」的喜愛！本次重大更新帶來更優雅、順暢的旅居體驗：
1. 全新介面設計：極光美學與日系雜誌風排版，圖文瀏覽更舒適精緻。
2. 精選旅遊主題企劃：新增九份山城、跳島慢旅、秘境步道與溫泉療癒路線。
3. 私房老宅咖啡漫步：巷弄深度探索，收錄人氣冠軍咖啡與手作焦糖布丁。
4. 全台熱門活動日曆：台北馬拉松、文化節慶與在地展演即時一手掌握。
5. 自由行一站式整合：SIM與eSIM網卡推薦、專車接送預訂，行前免煩惱。
6. 11國多語言體驗升級：全面優化全球語系介面與翻譯精準度。
7. 效能優化與問題修正：提升地圖載入速度與操作順暢度。

---

【簡短描述 / Promotional Text】
探索全台私房景點、展覽盛事與老宅咖啡！支援11國語言，自由行必備地圖。

---

【完整應用程式描述 / Full Description】
「台灣吃喝玩樂地圖」是一款集結全台灣美食、旅遊景點與休閒活動的全方位指南。
專為深度慢遊、獨旅放空、親子旅行與國際自由行旅人打造，不只提供最完整的景點情報，還有超多貼心功能，讓你輕鬆掌握最新推薦、一鍵收藏夢幻口袋名單，隨時隨地開啟專屬的台灣旅程！

核心功能亮點：
- 熱門景點即時更新：觀光署最新資料庫同步，私房打卡點不漏接。
- 精選旅遊主題企劃：北海岸九份、花東海岸、山林露營與跳島漫遊靈感。
- 全台活動與節慶展演：馬拉松、音樂季、傳統慶典與展覽資訊一手掌握。
- 在地風格老宅散步：探訪赤峰街等特色老宅、手作甜點與冠軍精品咖啡。
- 自由行交通行前準備：整合eSIM網卡、包車接送與交通預訂，出行更無憂。
- 跑馬燈即時旅人動態：查看最新評論與旅友實用回饋，旅行更有共鳴。
- 靈感隨機推薦：不知道下一站去哪？點擊隨機推薦，為你帶來出遊新點子！
- 收藏口袋名單：一鍵收藏心儀景點、活動與美食，打造專屬旅行計畫。
- 支援11國多語系切換：中、英、日、韓、泰、越、馬、菲、印尼、印地、西語無縫切換。

這是一款專為旅行愛好者打造的隨身地圖指南，
無論精心規劃長假，或是假日說走就走的微旅行，
都能隨時找到最適合你的台灣好去處。
立即免費下載，開啟你的下一場精彩台灣旅程！

特別感謝：
感謝政府資料開放平台及相關觀光單位提供公開資料。

關鍵字：
台灣旅遊,台灣吃喝玩樂地圖,台灣景點,台北景點,九份,台灣美食,老宅咖啡,台灣活動,台北馬拉松,台灣自由行,台灣包車,eSIM台灣""",

    "desc_en.txt": """【What's New in this Version】
Major UI Revamp - Explore Taiwan with Fresh Inspiration!
Thank you for using Taiwan Travel Map! This major release brings a completely redesigned, more elegant, and seamless travel experience:
1. Brand New UI/UX Design: Fresh aurora aesthetics and modern editorial layout for an effortless browsing experience.
2. Curated Travel Themes: Explore Jiufen coastline, island hopping, forest trails, and relaxing hot spring retreats.
3. Vintage Cafes and Neighborhood Walks: Discover historic house cafes, champion coffee, and artisan caramel pudding.
4. Nationwide Live Events: Stay updated with top cultural festivals, exhibitions, and sports like the Taipei Marathon.
5. One-Stop Travel Essentials: Quick access to SIM and eSIM cards, private charter bookings, and airport transfers.
6. Enhanced 11-Language Support: Refined translations and localized interface for travelers worldwide.
7. Performance Improvements: Faster map rendering and bug fixes for smoother navigation.

---

【Short Description / Promotional Text】
Explore hidden attractions, vibrant festivals, and vintage cafes across Taiwan in 11 languages!

---

【Full Description】
Taiwan Travel Map is your all-in-one companion for exploring Taiwan's finest food, attractions, and cultural experiences. Designed for slow travelers, solo adventurers, families, and international visitors, this app goes far beyond basic maps - bringing you curated stories, real-time event schedules, and hassle-free travel essentials.

Key Features:
- Real-Time Attractions Database: Sourced directly from official tourism databases to bring you popular and off-the-beaten-path destinations.
- Curated Travel Themes: Inspiring routes including Jiufen old street, East Coast Pacific drives, island escapes, and mountain glamping.
- Nationwide Festivals and Exhibitions: Live schedules for sports events (Taipei Marathon), music festivals, and traditional cultural ceremonies.
- Historic Cafes and City Walks: Wander through nostalgic alleys like Chihfeng Street to find artisan roasters and handmade desserts.
- Seamless Travel Essentials: Built-in guides and booking access for eSIM data, airport pickups, and chartered private drivers.
- Traveler Community Wall: Read real-time traveler reviews and tips on popular destinations.
- Random Destination Generator: Cannot decide where to go? Tap for instant inspiration and surprise your next trip!
- Personalized Wishlist: Bookmark your favorite spots, must-try restaurants, and upcoming events with one tap.
- 11 Languages Supported: English, Traditional Chinese, Japanese, Korean, Thai, Vietnamese, Bahasa Melayu, Filipino, Hindi, Indonesian, and Spanish.

Whether you are meticulously planning a vacation or hopping on a spontaneous weekend getaway, Taiwan Travel Map helps you discover the authentic beauty of Taiwan.
Download now and start your unforgettable journey!

Special Thanks:
Government Open Data Platform and tourism bureau contributors.

Keywords:
Taiwan travel,Taiwan map,Taipei attractions,Jiufen,Taroko,Taiwan guide,Taipei events,Taipei Marathon,Taiwan charter,Taiwan cafes,eSIM Taiwan,Taiwan food""",

    "desc_ja.txt": """【新機能 / バージョン更新情報】
大幅UIリニューアル・台湾旅行がもっと楽しく、快適に！
「台湾食べ歩き遊びマップ」をご利用いただきありがとうございます！今回の大型アップデートでは、デザインと機能性を一新しました：
1. 洗練された新UI/UX：オーロラグラデーションと雑誌スタイルのレイアウトで、より美しく快適な閲覧体験を提供。
2. 厳選テーマ旅行プラン：九份の絶景海岸線、離島めぐり、山林ハイキング、温泉の癒やし旅などを新特集。
3. 古民家カフェと街歩き：赤峰街などのレトロな路地裏に佇むチャンピオンコーヒーや手作りプリンの名店を厳選。
4. 台湾全土の最新イベント情報：台北マラソン、伝統祭り、アート展覧会などの最新日程を網羅。
5. 旅行の必需品もワンストップ：台湾SIM・eSIMの予約や、貸切チャーター車・空港送迎の手配もサポート。
6. 11言語対応の多言語最適化：日本語をはじめ、世界11言語の表示精度を大幅に向上。
7. パフォーマンス向上：地図の読み込み速度アップと細かな不具合を修正。

---

【簡単な説明 / プロモーションテキスト】
穴場スポット、人気イベント、古民家カフェまで台湾を網羅！11言語対応の旅行必須アプリ。

---

【詳細な説明】
「台湾食べ歩き遊びマップ」は、台湾全土のグルメ、観光名所、季節のイベント情報を一つにまとめたオールインワンの台湾旅行ガイドアプリです。
一人旅、女子旅、家族旅行から本格的な台湾リピーターまで、あらゆる旅行者のために設計されました。観光地情報だけでなく、旅のインスピレーションや便利な機能が満載です！

主な機能と特徴：
- 台湾観光署公認の最新スポットデータ：有名な王道スポットから隠れた穴場まで網羅。
- 充実の特集テーマ：ノスタルジックな九份、太魯閣渓谷、台湾一周鉄道旅、秘境グランピングなど。
- リアルタイムなイベント情報：マラソン大会、ランタンフェスティバル、文化祭、音楽イベントなどを掲載。
- レトロな古民家カフェ散歩：伝統とモダンが交差する路地裏カフェや絶品スイーツをチェック。
- 移動と通信も安心：台湾用eSIMデータ通信や貸切プライベートチャーター車の予約案内。
- 旅人のリアルタイム掲示板：他の旅行者のクチコミや最新レビューをすぐに確認可能。
- ランダムおすすめ機能：行き先に迷ったらワンタップで新しい旅のアイデアを発見！
- お気に入り保存機能：行きたいスポットや食べたいグルメをマイリストにワンタップ保存。
- 世界11言語に対応：日本語、繁体字中国語、英語、韓国語、タイ語、ベトナム語、マレー語、フィリピン語、ヒンディー語、インドネシア語、スペイン語。

週末の気軽な台湾弾丸旅行から、じっくり巡る長期滞在まで、
あなたの旅を最高の思い出にするお手伝いをします。
今すぐ無料ダウンロードして、新しい台湾の魅力を発見しましょう！

特別謝辞：
台湾政府オープンデータプラットフォームおよび観光関連機関の皆様

キーワード：
台湾旅行,台湾観光,台北観光,九份,台湾グルメ,古民家カフェ,台湾イベント,台北マラソン,台湾チャーター,eSIM台湾,台湾地図""",

    "desc_ko.txt": """【새로운 기능 / 업데이트 소식】
대규모 UI 개편 - 더 아름답고 편리해진 대만 여행!
대만 맛집 및 여행 지도를 이용해 주셔서 감사합니다! 이번 대규모 업데이트를 통해 더욱 우아하고 매끄러운 여행 경험을 선사합니다:
1. 완전히 새로워진 UI/UX 디자인: 오로라 그라데이션과 감성 매거진 스타일로 가독성과 심미성을 극대화했습니다.
2. 테마별 엄선 여행 코스: 지우펀 해안선, 섬 투어, 피톤치드 숲길 트레킹, 힐링 온천 코스 신규 추가.
3. 감성 옛 가옥 카페 산책: 츠펑지에 골목길의 챔피언 바리스타 커피와 수제 카라멜 푸딩 명소를 엄선했습니다.
4. 대만 전역 축제 및 이벤트: 타이베이 마라톤, 계절별 문화 축제, 전시회 실시간 일정 확인.
5. 자유여행 필수 준비 원스톱: 대만 SIM 및 eSIM 데이터 예약, 전용 기사 렌터카 투어 안내.
6. 11개 국어 다국어 환경 강화: 한국어를 포함한 글로벌 11개 언어 인터페이스 및 번역 품질 최적화.
7. 성능 최적화: 지도 로딩 속도 향상 및 버그 수정.

---

【간단한 설명 / 프로모션 텍스트】
숨은 명소, 인기 축제, 레트로 카페까지! 11개 언어를 지원하는 대만 자유여행 필수 지도 앱.

---

【상세 설명】
대만 맛집 및 여행 지도는 대만 전역의 대표 미식, 명소, 레저 및 문화 활동 정보를 하나로 모은 종합 대만 여행 가이드 앱입니다.
혼자 떠나는 힐링 여행, 친구와의 감성 투어, 가족 여행 및 자유여행객을 위해 기획되었으며, 단순한 장소 안내를 넘어 여행의 영감과 실시간 팁을 제공합니다.

주요 기능 및 특징:
- 대만 관광청 공식 데이터 실시간 연동: 최신 핫플레이스부터 현지인만 아는 숨은 명소까지.
- 테마별 여행 추천: 지우펀 옛길, 동해안 태평양 드라이브, 섬 투어, 감성 글램핑.
- 전국 축제 및 이벤트 정보: 타이베이 마라톤, 등불 축제, 뮤직 페스티벌, 예술 전시회 일정.
- 골목길 옛 가옥 카페 탐방: 레트로 감성의 골목길에 숨겨진 스페셜티 커피와 수제 디저트.
- 여행 필수품 원스톱 연결: 대만 eSIM 데이터 유심 및 전용 프라이빗 투어 예약 지원.
- 여행자 실시간 리뷰 보드: 여행자들의 생생한 후기와 꿀팁을 실시간으로 확인.
- 랜덤 명소 추천: 어디로 갈지 고민될 때 클릭 한 번으로 떠나는 깜짝 여행 추천.
- 나만의 위시리스트 저장: 가고 싶은 장소와 맛집을 원터치로 북마크.
- 11개 국어 지원: 한국어, 번체 중국어, 영어, 일본어, 태국어, 베트남어, 말레이어, 필리핀어, 힌디어, 인도네시아어, 스페인어.

철저한 여행 계획부터 즉흥적인 주말 나들이까지,
당신의 완벽한 대만 여행을 함께합니다.
지금 무료로 다운로드하고 특별한 대만 여행을 시작하세요!

특별 감사:
대만 정부 공공데이터 포털 및 관광청 관계자 여러분

키워드:
대만여행,대만지도,타이베이여행,지우펀,타이베이맛집,대만카페,대만축제,타이베이마라톤,대만자유여행,대만eSIM,대만투어""",

    "desc_th.txt": """【มีอะไรใหม่ในเวอร์ชันนี้】
ปรับโฉม UI ใหม่ครั้งใหญ่ - เที่ยวไต้หวันได้สนุกและง่ายขึ้นกว่าเดิม!
ขอบคุณที่ใช้งาน Taiwan Travel Map (แผนที่เที่ยว กิน ดื่ม ไต้หวัน)! การอัปเดตครั้งใหญ่นี้มาพร้อมประสบการณ์ที่สวยงามและราบรื่นยิ่งขึ้น:
1. ดีไซน์ UI/UX ใหม่ทั้งหมด: โทนสีแสงเหนือไล่ระดับและเลย์เอาต์สไตล์นิตยสารญี่ปุ่น อ่านง่าย สบายตา
2. แผนเที่ยวธีมพิเศษ: เส้นทางเลียบชายฝั่งจิ่วเฟิ่น, ทริปเที่ยวเกาะ, เส้นทางเดินป่าธรรมชาติ และแช่น้ำพุร้อนบำบัด
3. คาเฟ่บ้านโบราณและเดินเล่นในย่านวินเทจ: คัดสรรคาเฟ่กาแฟระดับแชมป์และพุดดิ้งคาราเมลโฮมเมดในตรอกโบราณชื่อดังอย่าง Chihfeng
4. เทศกาลและอีเวนต์ทั่วไต้หวัน: อัปเดตตารางงานมาราธอนไทเป, เทศกาลวัฒนธรรม และนิทรรศการล่าสุด
5. ครบเครื่องเรื่องเตรียมตัวเที่ยว: แนะนำการจองซิมหรือ eSIM ไต้หวัน และบริการเหมารถพร้อมคนขับรับส่งสนามบิน
6. รองรับ 11 ภาษาทั่วโลก: ปรับปรุงคุณภาพการแปลภาษาไทยและอีก 10 ภาษาทั่วโลกให้แม่นยำยิ่งขึ้น
7. เพิ่มประสิทธิภาพและความเสถียร: แผนที่โหลดเร็วขึ้นและแก้ไขข้อบกพร่องต่างๆ

---

【คำอธิบายสั้นๆ / ข้อความโปรโมต】
ค้นพบที่เที่ยวลับ งานเทศกาล และคาเฟ่สไตล์วินเทจทั่วไต้หวัน รองรับ 11 ภาษา แผนที่คู่ใจสายเที่ยวอิสระ!

---

【คำอธิบายแบบเต็ม】
Taiwan Travel Map คือแอปพลิเคชันคู่มือท่องเที่ยวไต้หวันแบบครบวงจร ที่รวบรวมร้านอาหารอร่อย ที่เที่ยวลับ และกิจกรรมยอดนิยมทั่วเกาะไต้หวัน
ออกแบบมาเพื่อนักเดินทางทุกสไตล์ ไม่ว่าจะเป็นการเที่ยวคนเดียว ทริปครอบครัว หรือสายแบกเป้ลุยเดี่ยว แอปนี้มีฟังก์ชันครบครันที่จะช่วยให้คุณวางแผนทริปในฝันได้อย่างง่ายดาย!

ฟังก์ชันเด่นที่น่าสนใจ:
- ข้อมูลสถานที่ท่องเที่ยวอัปเดตแบบเรียลไทม์: เชื่อมต่อข้อมูลโดยตรงจากกรมการท่องเที่ยวไต้หวัน ไม่พลาดจุดเช็กอินยอดฮิต
- ธีมท่องเที่ยวคัดสรรพิเศษ: เส้นทางเมืองโบราณจิ่วเฟิ่น, วิวแปซิฟิกชายฝั่งตะวันออก, แคมปิ้งธรรมชาติ และเกาะสวรรค์ไต้หวัน
- งานกิจกรรมและเทศกาลทั่วไต้หวัน: เช็กตารางงานไทเปมาราธอน, เทศกาลโคมไฟ, คอนเสิร์ต และงานแสดงศิลปะ
- เดินชิลคาเฟ่บ้านเก่า: สัมผัสเสน่ห์ตรอกวินเทจ ลิ้มลองกาแฟรสเลิศและขนมหวานทำมือ
- ตัวช่วยเดินทางครบวงจร: ลิงก์จองอินเทอร์เน็ต eSIM และบริการรถยนต์ส่วนตัวพร้อมคนขับพาเที่ยว
- กระดานคอมเมนต์นักเดินทาง: อ่านรีวิวและข้อเสนอแนะจริงจากเพื่อนร่วมทางแบบเรียลไทม์
- สุ่มสถานที่ท่องเที่ยว: นึกไม่ออกว่าจะไปไหน แตะปุ่มสุ่มเพื่อรับแรงบันดาลใจใหม่ๆ ทันที!
- บันทึกรายการโปรด: กดเซฟสถานที่ ร้านอาหาร และกิจกรรมที่อยากไปไว้ในลิสต์ส่วนตัว
- รองรับ 11 ภาษา: ไทย, จีนตัวเต็ม, อังกฤษ, ญี่ปุ่น, เกาหลี, เวียดนาม, มาเลย์, ฟิลิปปินส์, ฮินดี, อินโดนีเซีย และสเปน

ไม่ว่าคุณจะวางแผนท่องเที่ยววันหยุดยาว หรือแค่อยากออกเดินทางแบบกะทันหัน
Taiwan Travel Map จะพาคุณไปค้นพบความงดงามที่แท้จริงของไต้หวัน
ดาวน์โหลดฟรีได้แล้ววันนี้ แล้วออกเดินทางไปด้วยกัน!

ขอขอบคุณเป็นพิเศษ:
ศูนย์ข้อมูลเปิดภาครัฐไต้หวันและหน่วยงานส่งเสริมการท่องเที่ยว

คำค้นหา (Keywords):
เที่ยวไต้หวัน,แผนที่ไต้หวัน,ที่เที่ยวไทเป,จิ่วเฟิ่น,ของกินไต้หวัน,คาเฟ่ไต้หวัน,ไทเปมาราธอน,eSIMไต้หวัน,เหมารถเที่ยวไต้หวัน,เที่ยวไต้หวันด้วยตัวเอง""",

    "desc_vi.txt": """【Có gì mới trong phiên bản này】
Nâng cấp giao diện hoàn toàn mới - Khám phá Đài Loan tuyệt vời hơn!
Cảm ơn bạn đã tin tưởng sử dụng Bản đồ Du lịch và Ẩm thực Đài Loan (Taiwan Travel Map)! Bản cập nhật lớn này mang đến trải nghiệm thẩm mỹ và mượt mà hơn bao giờ hết:
1. Thiết kế UI/UX mới tinh tế: Hiệu ứng chuyển màu cực quang kết hợp phong cách tạp chí Nhật Bản thanh lịch.
2. Chủ đề du lịch chọn lọc: Bổ sung cung đường ven biển Cửu Phần (Jiufen), du lịch đảo, đi bộ đường rừng và suối nước nóng thư giãn.
3. Khám phá cà phê nhà cổ: Dạo bước trong ngõ Chihfeng hoài cổ, thưởng thức cà phê đoạt giải và bánh pudding caramel thủ công.
4. Lịch sự kiện và lễ hội toàn Đài Loan: Cập nhật nhanh giải chạy Taipei Marathon, các lễ hội truyền thống và triển lãm nghệ thuật.
5. Tiện ích du lịch tự túc trọn gói: Hỗ trợ đặt SIM và eSIM 4G/5G cùng dịch vụ xe riêng đưa đón sân bay, tham quan theo yêu cầu.
6. Tối ưu hóa trải nghiệm 11 ngôn ngữ: Nâng cao độ chính xác bản dịch tiếng Việt và 10 ngôn ngữ quốc tế khác.
7. Nâng cao hiệu suất: Tải bản đồ nhanh hơn và sửa các lỗi nhỏ.

---

【Mô tả ngắn / Đoạn quảng bá】
Khám phá điểm check-in bí mật, lễ hội sôi động và cà phê nhà cổ Đài Loan! Hỗ trợ 11 ngôn ngữ, cẩm nang du lịch tự túc số 1.

---

【Mô tả đầy đủ】
Taiwan Travel Map là ứng dụng cẩm nang toàn diện tổng hợp ẩm thực, điểm tham quan và các hoạt động văn hóa giải trí trên khắp Đài Loan.
Được thiết kế dành riêng cho những người yêu thích du lịch chậm, khám phá một mình, du lịch gia đình và khách quốc tế tự túc, ứng dụng không chỉ cung cấp thông tin bản đồ mà còn mang đến nguồn cảm hứng bất tận cho mỗi chuyến đi!

Điểm nổi bật và Tính năng chính:
- Dữ liệu cập nhật liên tục từ Cục Du lịch Đài Loan: Nắm bắt các địa điểm nổi tiếng và danh lam thắng cảnh ẩn giấu.
- Cung đường du lịch theo chủ đề: Phố cổ Cửu Phần, ngắm biển Thái Bình Dương bờ Đông, cắm trại glamping trên núi và khám phá đảo.
- Lịch lễ hội và sự kiện sôi động: Taipei Marathon, lễ hội hoa đăng, tuần lễ âm nhạc và triển lãm văn hóa.
- Dạo bước quán cà phê phong cách hoài cổ: Tìm kiếm những góc quán yên bình trong nhà cổ, cà phê hảo hạng và tráng miệng tuyệt ngon.
- Chuẩn bị hành trang dễ dàng: Hỗ trợ đặt SIM và eSIM cùng dịch vụ thuê xe riêng có tài xế tiện lợi.
- Bảng tin chia sẻ thực tế: Xem các đánh giá, trải nghiệm mới nhất từ cộng đồng du khách.
- Gợi ý điểm đến ngẫu nhiên: Bạn chưa biết đi đâu hôm nay? Nhấn nút ngẫu nhiên để nhận ngay gợi ý thú vị!
- Lưu danh sách yêu thích: Đánh dấu các địa điểm, quán ăn muốn thử chỉ với một chạm.
- Hỗ trợ 11 ngôn ngữ: Tiếng Việt, Tiếng Trung phồn thể, Tiếng Anh, Tiếng Nhật, Tiếng Hàn, Tiếng Thái, Tiếng Mã Lai, Tiếng Philippines, Tiếng Hindi, Tiếng Indonesia và Tiếng Tây Ban Nha.

Dù bạn đang lên kế hoạch cho kỳ nghỉ dài ngày hay chỉ là chuyến đi ngẫu hứng cuối tuần,
Taiwan Travel Map sẽ luôn là người bạn đồng hành tin cậy trên mọi nẻo đường Đài Loan.
Tải xuống miễn phí ngay hôm nay và bắt đầu hành trình đáng nhớ!

Đặc biệt cảm ơn:
Cổng dữ liệu mở chính phủ Đài Loan và các cơ quan xúc tiến du lịch.

Từ khóa (Keywords):
Du lịch Đài Loan,bản đồ Đài Loan,địa điểm du lịch Đài Bắc,Cửu Phần,ẩm thực Đài Loan,cà phê Đài Loan,Taipei Marathon,du lịch tự túc Đài Loan,thuê xe Đài Loan,eSIM Đài Loan""",

    "desc_ms.txt": """【Apa Yang Baharu dalam Versi Ini】
Pembaruan Antara Muka UI Baharu - Terokai Taiwan dengan Lebih Indah!
Terima kasih kerana memilih Peta Pelancongan dan Makanan Taiwan (Taiwan Travel Map)! Kemas kini utama ini membawakan reka bentuk baharu yang lebih elegan dan lancar:
1. Reka Bentuk UI/UX Serba Baharu: Gabungan gradien aurora yang menawan dan susun atur gaya majalah estetik Jepun.
2. Tema Pelancongan Terpilih: Terokai laluan pesisir pantai Jiufen, percutian pulau, denai hutan simpan dan kolam air panas semula jadi.
3. Kafe Rumah Lama dan Jejak Warisan: Nikmati kopi bertaraf juara dan puding karamel buatan tangan di lorong nostalgia Chihfeng.
4. Kalendar Acara dan Festival Seluruh Taiwan: Maklumat terkini tentang Maraton Taipei, festival kebudayaan dan pameran seni.
5. Keperluan Perjalanan Sehenti: Akses mudah untuk tempahan kad SIM atau eSIM dan perkhidmatan sewa kereta persendirian bersama pemandu.
6. Sokongan 11 Bahasa Dipertingkat: Terjemahan Bahasa Melayu dan antara muka pelbagai bahasa yang lebih tepat.
7. Peningkatan Prestasi dan Pembetulan Pepijat: Pemuatan peta lebih pantas dan operasi aplikasi yang lebih lancar.

---

【Penerangan Ringkas / Teks Promosi】
Terokai tarikan tersembunyi, festival meriah dan kafe vintaj di Taiwan! Menyokong 11 bahasa, teman perjalanan bebas terbaik.

---

【Penerangan Penuh】
Taiwan Travel Map ialah aplikasi panduan perjalanan lengkap yang menghimpunkan makanan enak, tempat menarik dan aktiviti rekreasi di seluruh Taiwan.
Direka khas untuk pengembara santai, pengembara solo, percutian keluarga dan pelancong antarabangsa, aplikasi ini bukan sekadar peta biasa - ia memberi inspirasi dan panduan praktikal untuk setiap perjalanan anda!

Ciri-ciri Utama dan Keistimewaan:
- Pangkalan Data Tarikan Masa Nyata: Diselaraskan dengan data rasmi Lembaga Pelancongan Taiwan untuk maklumat destinasi popular dan tersembunyi.
- Tema Perjalanan Berinspirasi: Menampilkan pekan bersejarah Jiufen, pemanduan indah di pesisir Lautan Pasifik, percutian pulau dan glamping.
- Jadual Acara dan Festival Seluruh Negara: Ketahui tarikh Maraton Taipei, festival tanglung, festival muzik dan pesta kebudayaan tempatan.
- Jejak Santai Kafe Vintaj: Lawati kafe rumah lama yang tenang dan nikmati pencuci mulut istimewa buatan tangan.
- Persediaan Perjalanan Lengkap: Bantuan tempahan internet eSIM dan perkhidmatan kenderaan persendirian dari lapangan terbang.
- Papan Maklum Balas Pengembara: Baca ulasan dan tip terkini daripada komuniti pelancong lain.
- Cadangan Rawak Destinasi: Buntu memikirkan ke mana hendak pergi? Tekan butang rawak untuk mendapatkan idea perjalanan baharu secara spontan!
- Simpan Senarai Hajat: Simpan destinasi dan restoran impian anda dengan satu sentuhan.
- Menyokong 11 Bahasa: Bahasa Melayu, Bahasa Cina Tradisional, Bahasa Inggeris, Bahasa Jepun, Bahasa Korea, Bahasa Thai, Bahasa Vietnam, Bahasa Filipina, Bahasa Hindi, Bahasa Indonesia dan Bahasa Sepanyol.

Sama ada anda merancang percutian panjang atau sekadar lawatan santai hujung minggu,
Taiwan Travel Map sedia membantu anda meneroka keindahan sebenar Taiwan.
Muat turun secara percuma hari ini dan mulakan pengembaraan anda!

Penghargaan Khas:
Platform Data Terbuka Kerajaan Taiwan dan agensi pelancongan berkaitan.

Kata Kunci (Keywords):
Pelancongan Taiwan,peta Taiwan,tempat menarik Taipei,Jiufen,makanan Taiwan,kafe Taiwan,Maraton Taipei,eSIM Taiwan,sewa kereta Taiwan,panduan melancong Taiwan""",

    "desc_fil.txt": """【Ano ang Bago sa Bersyong Ito】
Malaking Pagbabago sa UI - Tuklasin ang Ganda ng Taiwan nang Mas Madali!
Salamat sa pagtangkilik sa Taiwan Travel Map (Mapa ng Pagkain at Pasyalan sa Taiwan)! Ang bagong bersyon na ito ay nagtatampok ng mas elegante at modernong karanasan:
1. Bagong Disenyo ng UI/UX: Magandang aurora gradient at magazine-style layout para sa komportableng pag-browse.
2. Mga Espesyal na Tema sa Paglalakbay: Bagong ruta para sa baybayin ng Jiufen, island hopping, trail sa kagubatan, at hot spring retreats.
3. Vintage Cafes at Lakad sa Kalsada: Tuklasin ang mga champion coffee shop at masasarap na caramel pudding sa makasaysayang eskinita ng Chihfeng.
4. Mga Kaganapan at Pista sa Buong Taiwan: Maging updated sa Taipei Marathon, mga kultural na kapistahan, at mga eksibisyon.
5. Kumpletong Gabay sa Pagbiyahe: Mabilis na pag-access para sa pag-book ng Taiwan eSIM at private charter transfers.
6. Pinahusay na Suporta sa 11 Wika: Mas tumpak na pagsasalin sa Filipino at 10 iba pang pandaigdigang wika.
7. Mas Mabilis at Mas Maayos: Mas mabilis na pag-load ng mapa at pag-aayos sa mga bug.

---

【Maikling Paglalarawan / Promotional Text】
Tuklasin ang mga lihim na pasyalan, makukulay na pista, at vintage cafe sa Taiwan! May 11 wika, gabay para sa sariling biyahe.

---

【Buong Paglalarawan】
Ang Taiwan Travel Map ay ang iyong all-in-one na gabay sa paglalakbay na nagtitipon ng mga masasarap na pagkain, magagandang tanawin, at mga kapana-panabik na aktibidad sa buong Taiwan.
Binuo para sa mga solo traveler, pamilya, at mga dayuhang turista, hindi lang ito basta mapa - nagbibigay ito ng inspirasyon at praktikal na impormasyon para sa iyong pangarap na bakasyon!

Mga Pangunahing Tampok:
- Real-Time na Impormasyon ng mga Atraksyon: Direktang konektado sa opisyal na data ng Taiwan Tourism Bureau.
- Mga Temang Ruta: Baybayin ng Jiufen, Pacific Coast drive sa Silangan, island hopping, at glamping sa bundok.
- Listahan ng mga Pista at Kaganapan: Iskedyul ng Taipei Marathon, lantern festival, konsiyerto, at mga tradisyonal na pagdiriwang.
- Pamamasyal sa mga Lumang Cafe: Pumasok sa mga makasaysayang lumang bahay na ginawang cafe para sa de-kalidad na kape at panghimagas.
- Mga Mahalagang Gamit sa Paglalakbay: Suporta sa pagbili ng internet eSIM at pribadong sasakyan na may drayber mula sa airport.
- Mensahe mula sa Kapwa Biyahero: Basahin ang mga totoong karanasan at tips ng iba pang turista.
- Random Destination Generator: Hindi alam kung saan pupunta? Pindutin ang random button para sa agarang inspirasyon!
- Personal Wishlist: I-save sa iyong listahan ang mga paboritong kainan at pasyalan sa isang tap lang.
- Sumusuporta sa 11 Wika: Filipino, Tradisyonal na Tsino, Ingles, Hapones, Koreano, Thai, Vietnamese, Malay, Hindi, Indonesian, at Espanyol.

Nagluluto ka man ng mahabang bakasyon o biglaang lakad lang sa weekend,
narito ang Taiwan Travel Map upang tulungan kang maranasan ang tunay na ganda ng Taiwan.
I-download nang libre ngayon at simulan ang iyong bagong pakikipagsapalaran!

Espesyal na Pasasalamat:
Taiwan Government Open Data Platform at mga ahensya ng turismo.

Mga Keyword:
Taiwan travel,Taiwan mapa,pasyalan sa Taipei,Jiufen,pagkain sa Taiwan,cafe sa Taiwan,Taipei Marathon,Taiwan private tour,eSIM Taiwan,gabay sa Taiwan""",

    "desc_hi.txt": """【इस संस्करण में नया क्या है】
बड़ा UI नया रूप - ताइवान की यात्रा को और भी आसान और सुंदर बनाएं!
Taiwan Travel Map (ताइवान यात्रा और भोजन मानचित्र) का उपयोग करने के लिए धन्यवाद! यह बड़ा अपडेट अधिक सुरुचिपूर्ण और सहज यात्रा अनुभव लाता है:
1. बिल्कुल नया UI/UX डिज़ाइन: सुंदर ऑरोरा ग्रेडिएंट और जापानी पत्रिका शैली का लेआउट, जिससे ब्राउज़िंग बेहद आसान हो जाती है।
2. विशेष यात्रा थीम: जिउफेन तटीय मार्ग, द्वीप की सैर, वन ट्रेल्स और आरामदायक हॉट स्प्रिंग्स की नई यात्रा योजनाएं।
3. ऐतिहासिक कैफे और वॉक: चिहफेंग की पुरानी गलियों में स्थित पुरस्कार विजेता कॉफी और हस्तनिर्मित कारमेल पुडिंग का अन्वेषण करें।
4. ताइवान भर के लाइव कार्यक्रम: ताइपे मैराथन, सांस्कृतिक उत्सवों और कला प्रदर्शनियों की लाइव तिथियां।
5. यात्रा की सभी आवश्यक चीजें: ताइवान सिम या eSIM कार्ड और निजी ड्राइवर चार्टर सेवाओं की आसान बुकिंग।
6. 11 भाषाओं में बेहतर अनुभव: हिंदी और अन्य 10 अंतरराष्ट्रीय भाषाओं में अधिक सटीक अनुवाद।
7. बेहतर प्रदर्शन: तेज़ मानचित्र लोडिंग और बग समाधान।

---

【संक्षिप्त विवरण / प्रचार पाठ】
ताइवान के छिपे हुए आकर्षण, जीवंत त्योहार और पुराने कैफे खोजें! 11 भाषाओं का समर्थन, स्वतंत्र यात्रा के लिए सर्वोत्तम मानचित्र।

---

【पूर्ण विवरण】
Taiwan Travel Map ताइवान के बेहतरीन भोजन, पर्यटन स्थलों और मनोरंजक गतिविधियों की खोज के लिए आपका संपूर्ण यात्रा गाइड ऐप है।
एकल यात्रियों, परिवारों और वैश्विक पर्यटकों के लिए विशेष रूप से डिज़ाइन किया गया, यह ऐप केवल एक मानचित्र नहीं है - यह आपको हर यात्रा के लिए प्रेरणा और व्यावहारिक जानकारी प्रदान करता है!

प्रमुख विशेषताएं:
- रीयल-टाइम आकर्षण डेटाबेस: ताइवान पर्यटन ब्यूरो के आधिकारिक डेटा से सीधे जुड़ा हुआ, ताकि आप लोकप्रिय और गुप्त स्थलों को कभी न चूकें।
- क्यूरेटेड यात्रा थीम: जिउफेन की पुरानी सड़कें, पूर्वी तट ड्राइव, द्वीप की छुट्टियां और प्राकृतिक कैंपिंग।
- राष्ट्रव्यापी कार्यक्रम और उत्सव: ताइपे मैराथन, लालटेन उत्सव, संगीत कार्यक्रम और पारंपरिक समारोह।
- विंटेज कैफे वॉक: पुरानी इमारतों में स्थित विशेष कैफे और स्वादिष्ट डेसर्ट का आनंद लें।
- यात्रा की आवश्यक वस्तुएं: हाई-स्पीड eSIM इंटरनेट और हवाई अड्डे से निजी कार सेवाओं की आसान व्यवस्था।
- यात्रियों का लाइव बोर्ड: अन्य यात्रियों की वास्तविक समीक्षाएं और सुझाव पढ़ें।
- रैंडम स्थल सुझाव: तय नहीं कर पा रहे कि कहाँ जाएं? तुरंत नए विचारों के लिए रैंडम बटन दबाएं!
- व्यक्तिगत पसंदीदा सूची: अपनी पसंदीदा जगहों और रेस्तरां को एक टैप में सहेजें।
- 11 भाषाओं का समर्थन: हिंदी, पारंपरिक चीनी, अंग्रेजी, जापानी, कोरियाई, थाई, वियतनामी, मलय, फिलिपिनो, इंडोनेशियाई और स्पेनिश।

चाहे आप लंबी छुट्टी की योजना बना रहे हों या सप्ताहांत की त्वरित यात्रा,
Taiwan Travel Map आपको ताइवान की वास्तविक सुंदरता खोजने में मदद करेगा।
आज ही मुफ्त डाउनलोड करें और अपनी अगली यात्रा शुरू करें!

विशेष आभार:
ताइवान सरकार ओपन डेटा प्लेटफॉर्म और पर्यटन ब्यूरो।

कीवर्ड (Keywords):
ताइवान यात्रा,ताइवान मानचित्र,ताइपे पर्यटन स्थल,जिउफेन,ताइवान भोजन,ताइवान कैफे,ताइपे मैराथन,ताइवान चार्टर कार,eSIM ताइवान,ताइवान गाइड""",

    "desc_id.txt": """【Apa yang Baru di Versi Ini】
Pembaruan Antarmuka UI Besar-besaran - Jelajahi Taiwan Lebih Mudah dan Indah!
Terima kasih telah menggunakan Peta Wisata dan Kuliner Taiwan (Taiwan Travel Map)! Pembaruan besar ini menghadirkan pengalaman visual yang lebih elegan dan praktis:
1. Desain UI/UX Baru: Sentuhan gradasi aurora memikat dan tata letak majalah estetis Jepang yang nyaman dipandang.
2. Rute Wisata Bertema: Jelajahi garis pantai Jiufen, wisata keliling pulau, jalur hutan alam, dan pemandian air panas.
3. Kafe Rumah Tua dan Jalan Santai: Temukan kopi juara dan puding karamel buatan tangan di lorong nostalgia Chihfeng.
4. Kalender Acara Seluruh Taiwan: Informasi langsung untuk Taipei Marathon, festival budaya musiman, dan pameran seni.
5. Kebutuhan Perjalanan Lengkap: Kemudahan pemesanan internet eSIM dan layanan sewa mobil pribadi dengan pengemudi.
6. Peningkatan Dukungan 11 Bahasa: Terjemahan Bahasa Indonesia dan antarmuka multibahasa yang semakin akurat.
7. Peningkatan Kinerja: Pemuatan peta lebih cepat dan perbaikan bug untuk kelancaran navigasi.

---

【Deskripsi Singkat / Teks Promosi】
Temukan surga tersembunyi, festival meriah dan kafe vintage di Taiwan! Mendukung 11 bahasa, peta wajib liburan mandiri.

---

【Deskripsi Lengkap】
Taiwan Travel Map adalah aplikasi panduan wisata lengkap yang menyajikan ragam kuliner lezat, tempat wisata favorit, dan kegiatan rekreasi di seluruh pelosok Taiwan.
Dirancang khusus untuk solo traveler, liburan santai, wisata keluarga, dan turis mancanegara, aplikasi ini bukan sekadar peta - ini adalah inspirasi tanpa batas untuk merancang liburan impian Anda!

Fitur Utama dan Keunggulan:
- Database Tempat Wisata Real-Time: Terhubung langsung dengan data resmi Biro Pariwisata Taiwan untuk rekomendasi tempat populer dan tersembunyi.
- Inspirasi Rute Bertema: Kota bersejarah Jiufen, pesona Samudra Pasifik di Pesisir Timur, pulau-pulau eksotis, dan glamping pegunungan.
- Jadwal Festival dan Acara Nasional: Cek jadwal Taipei Marathon, festival lampion, konser musik, dan tradisi lokal.
- Jelajah Kafe Rumah Kuno: Masuki lorong-lorong bersejarah dan nikmati secangkir kopi khas di bangunan antik bernilai seni tinggi.
- Kebutuhan Wisata Mandiri: Tersedia tautan pemesanan internet eSIM dan transportasi antar-jemput bandara tanpa ribet.
- Ulasan Komunitas Pengelana: Baca ulasan jujur dan tips terkini dari sesama pelancong secara langsung.
- Generator Rekomendasi Acak: Bingung mau ke mana hari ini? Cukup sentuh tombol acak untuk mendapatkan ide liburan spontan!
- Simpan Daftar Impian: Tandai tempat wisata, kafe, dan restoran favorit dengan satu sentuhan mudah.
- Mendukung 11 Bahasa: Bahasa Indonesia, Bahasa Tionghoa Tradisional, Bahasa Inggris, Bahasa Jepang, Bahasa Korea, Bahasa Thai, Bahasa Vietnam, Bahasa Melayu, Bahasa Filipino, Bahasa Hindi, dan Bahasa Spanyol.

Baik Anda sedang menyusun rencana liburan panjang atau sekadar jalan-jalan santai di akhir pekan,
Taiwan Travel Map siap memandu Anda menemukan keindahan sejati Taiwan.
Unduh gratis sekarang dan mulailah petualangan mengagumkan Anda!

Ucapan Terima Kasih:
Platform Data Terbuka Pemerintah Taiwan dan seluruh lembaga pariwisata terkait.

Kata Kunci (Keywords):
Wisata Taiwan,peta Taiwan,tempat wisata Taipei,Jiufen,kuliner Taiwan,kafe Taiwan,Taipei Marathon,sewa mobil Taiwan,eSIM Taiwan,panduan jalan Taiwan""",

    "desc_es.txt": """【Novedades de esta versión】
Gran renovación de interfaz - Explora Taiwán con nueva inspiración!
Gracias por usar Taiwan Travel Map (Mapa de Viajes y Gastronomía de Taiwán)! Esta importante actualización ofrece una experiencia visual más elegante y fluida:
1. Nuevo diseño de UI/UX: Estilo estético de revista japonesa con degradados de aurora para una navegación intuitiva y relajante.
2. Rutas temáticas seleccionadas: Nueva costa de Jiufen, escapadas a islas, senderos forestales y baños termales relajantes.
3. Cafeterías históricas y paseos urbanos: Descubre cafés de baristas galardonados y flanes de caramelo artesanal en los nostálgicos callejones de Chihfeng.
4. Eventos y festivales en vivo: Calendario en tiempo real del Maratón de Taipéi, festividades culturales y exposiciones artísticas.
5. Todo para tu viaje en un solo lugar: Reserva rápida de tarjetas eSIM y servicios de traslado privado con chofer.
6. Compatibilidad mejorada con 11 idiomas: Traducciones al español perfeccionadas e interfaz internacional optimizada.
7. Mayor rendimiento y estabilidad: Carga de mapas más rápida y corrección de pequeños errores.

---

【Descripción breve / Texto promocional】
Descubre tesoros ocultos, festivales y cafeterías vintage en Taiwán! Compatible con 11 idiomas, tu mapa de viaje ideal.

---

【Descripción completa】
Taiwan Travel Map es tu guía de viaje integral que reúne lo mejor de la gastronomía, los puntos turísticos y las actividades culturales de todo Taiwán.
Diseñada para viajeros independientes, mochileros, familias y turistas internacionales, esta aplicación va mucho más allá de un mapa común: te brinda inspiración y herramientas útiles para cada paso de tu aventura!

Características principales:
- Base de datos de atracciones en tiempo real: Sincronizada con la Oficina de Turismo de Taiwán para mostrarte lugares populares y secretos.
- Rutas temáticas recomendadas: El encanto de Jiufen, vistas al Océano Pacífico en la Costa Este, islas paradisíacas y glamping en la montaña.
- Agenda de eventos y festivales: Sigue el Maratón de Taipéi, el festival de los faroles, eventos musicales y celebraciones tradicionales.
- Paseo por cafeterías de casas antiguas: Disfruta de una taza de café de especialidad en edificios históricos preservados con encanto.
- Esenciales de viaje integrados: Información directa para contratar datos móviles eSIM y traslados privados desde y hacia el aeropuerto.
- Muro de reseñas en directo: Lee comentarios y recomendaciones útiles de otros viajeros en tiempo real.
- Generador de destinos al azar: Indeciso sobre adónde ir? Toca el botón aleatorio y déjate sorprender con nuevas ideas.
- Lista de favoritos personal: Guarda tus atracciones, restaurantes y eventos preferidos con un solo toque.
- Compatible con 11 idiomas: Español, Chino tradicional, Inglés, Japonés, Coreano, Tailandés, Vietnamita, Malayo, Filipino, Hindi e Indonesio.

Tanto si estás planificando unas vacaciones largas como si se trata de una escapada espontánea de fin de semana,
Taiwan Travel Map te acompaña para descubrir la auténtica magia de Taiwán.
Descárgala gratis hoy mismo y comienza tu viaje inolvidable!

Agradecimientos especiales:
Plataforma de Datos Abiertos del Gobierno de Taiwán y organismos oficiales de turismo.

Palabras clave (Keywords):
Viajar a Taiwán,mapa de Taiwán,turismo en Taipéi,Jiufen,comida taiwanesa,cafeterías en Taiwán,Maratón de Taipéi,coche privado Taiwán,eSIM Taiwán,guía de viaje Taiwán"""
}

for filename, content in DESCRIPTIONS.items():
    path = os.path.join(STORE_DES_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Cleaned {filename}")

print("All 11 description files cleaned of special symbols successfully!")

