/* Shared affiliate configuration: affiliate_config.json. No automatic navigation. */
(function (scope) {
  'use strict';
  function regionForCountry(config, country) {
    country = String(country || '').toUpperCase();
    return Object.keys(config.regions).find(key => config.regions[key].countries.includes(country)) || 'GLOBAL';
  }

  function buildLink(config, regionKey, category, destination = {}) {
    const region = config.regions[regionKey] || config.regions.GLOBAL;
    const platform = key => config.platforms[key].url;
    if (category === 'carRental' || category === 'transit' && !['JP', 'KR'].includes(regionKey)) return platform(category);
    if (!region.tripHost) return platform({flights:'expedia', hotel:'hotels', charter:'viator', tour:'viator', esim:'esim', transit:'transit'}[category] || category);
    if (category === 'flights' || category === 'hotel' || category === 'transit' && regionKey === 'JP') {
      const path = {flights:'/flights/', hotel:'/hotels/list', transit:'/trains/taiwan-high-speed-rail/'}[category];
      const url = new URL('https://' + region.tripHost + path);
      Object.entries(config.tracking.trip).forEach(([key, value]) => url.searchParams.set(key, value));
      url.searchParams.set('curr', region.currency);
      if (category === 'hotel') {
        const city = config.cities.find(c => c.name === destination.city || c.nameEn === destination.city);
        const district = config.districts.find(d => d.city === city?.name && d.name === destination.district);
        if (city?.tripCityId) url.searchParams.set('city', city.tripCityId);
        const keyword = district?.keyword || destination.keyword || (city?.tripCityId ? '' : city?.keyword);
        if (keyword) url.searchParams.set('keyword', keyword);
      }
      return url.href;
    }
    if (['charter','tour','esim','transit'].includes(category)) {
      const queries = {charter:'Taiwan Private Car Charter', tour:'Taiwan Day Tour', esim:'Taiwan eSIM'};
      const path = category === 'transit' ? '/activity/382-thsr-3-day-pass-taipei/' : '/search/result/';
      const url = new URL('https://www.klook.com/' + region.klookLocale + path);
      if (queries[category]) url.searchParams.set('query', queries[category]);
      url.searchParams.set('aid', config.tracking.klookAid);
      url.searchParams.set('currency', region.currency);
      return url.href;
    }
    return platform(category);
  }

  function languageFallback(config, language) {
    const code = String(language || '').toLowerCase();
    if (code.startsWith('zh-hk') || code.startsWith('zh-mo')) return 'HK_MO';
    if (code.startsWith('zh')) return 'TW';
    if (code.startsWith('en-sg') || code.startsWith('ms')) return 'SG_MY';
    return {ja:'JP', ko:'KR', th:'TH', vi:'VN', id:'ID', fil:'SOUTH_ASIA', hi:'SOUTH_ASIA'}[code.split('-')[0]] || 'GLOBAL';
  }

  async function fetchJson(url, timeoutMs) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, {signal:controller.signal});
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return await response.json();
    } finally { clearTimeout(timer); }
  }

  async function detectRegion(config, language, storage) {
    const read = key => { try { return storage?.getItem(key); } catch (_) { return null; } };
    const manual = read('twfun-affiliate-region');
    if (config.regions[manual]) return manual;
    try {
      const cached = JSON.parse(read('twfun-affiliate-geo') || 'null');
      if (cached && /^[A-Z]{2}$/.test(cached.country) && Date.now() - cached.time >= 0 && Date.now() - cached.time < config.geo.cacheTtlMs) return regionForCountry(config, cached.country);
      const geo = await fetchJson(config.geo.endpoint, config.geo.timeoutMs);
      const country = String(geo.country_code || '').toUpperCase();
      if (geo.error || !/^[A-Z]{2}$/.test(country)) throw new Error('Invalid country');
      try { storage?.setItem('twfun-affiliate-geo', JSON.stringify({country, time:Date.now()})); } catch (_) {}
      return regionForCountry(config, country);
    } catch (_) { return languageFallback(config, language); }
  }

  const labels = {
    zh:['旅程預訂','市場與幣別','目的地','區域','全市','機票','住宿','包車／導覽','eSIM 網卡','交通票券','租車','評價比價','部分連結為分潤連結；透過連結預訂可支持我們。','以預訂平台實際顯示的幣別與價格為準。'],
    en:['Plan your trip','Market & currency','Destination','District','All districts','Flights','Hotels','Private tours','eSIM','Transport','Car rental','Compare reviews','Some links are affiliate links. Booking through them supports us.','Final currency and prices are shown by the booking platform.'],
    ja:['旅の予約','地域・通貨','目的地','エリア','市内全域','航空券','ホテル','貸切ツアー','eSIM','交通チケット','レンタカー','口コミ比較','一部はアフィリエイトリンクです。予約が運営の支援になります。','最終的な通貨と料金は予約サイトでご確認ください。'],
    ko:['여행 예약','지역 및 통화','목적지','지역','전체','항공권','호텔','프라이빗 투어','eSIM','교통 티켓','렌터카','리뷰 비교','일부 링크는 제휴 링크이며 예약 시 운영에 도움이 됩니다.','최종 통화 및 가격은 예약 사이트에서 확인하세요.'],
    th:['จองการเดินทาง','ภูมิภาคและสกุลเงิน','จุดหมาย','เขต','ทั้งหมด','เที่ยวบิน','โรงแรม','ทัวร์ส่วนตัว','eSIM','ตั๋วเดินทาง','เช่ารถ','เปรียบเทียบรีวิว','บางลิงก์เป็นลิงก์พันธมิตร การจองช่วยสนับสนุนเรา','ราคาและสกุลเงินสุดท้ายแสดงบนเว็บไซต์จอง'],
    vi:['Đặt chuyến đi','Khu vực và tiền tệ','Điểm đến','Quận','Tất cả','Vé máy bay','Khách sạn','Tour riêng','eSIM','Vé di chuyển','Thuê xe','So sánh đánh giá','Một số liên kết là liên kết tiếp thị. Đặt dịch vụ giúp hỗ trợ chúng tôi.','Giá và tiền tệ cuối cùng do nền tảng đặt dịch vụ hiển thị.'],
    id:['Pesan perjalanan','Wilayah & mata uang','Tujuan','Distrik','Semua','Penerbangan','Hotel','Tur pribadi','eSIM','Transportasi','Sewa mobil','Bandingkan ulasan','Sebagian tautan adalah tautan afiliasi. Pemesanan mendukung kami.','Harga dan mata uang akhir ditampilkan di platform pemesanan.']
  };
  const partnerNames = {kkday:['亞洲體驗','Asia experiences'], dining:['餐券與訂餐','Dining'], souvenirs:['生鮮伴手禮','Food & gifts'], camping:['露營食材','Camping food'], drugstore:['藥妝','Beauty & drugstores'], design:['生活選物','Design & lifestyle'], health:['保健食品','Health supplements'], owlting:['在地體驗','Local experiences'], delivery:['美食外送','Food delivery'], education:['教育學習','Learning'], english:['學英文','Learn English']};

  async function init() {
    const panel = document.querySelector('[data-affiliate-panel]');
    if (!panel) return;
    const script = document.querySelector('script[src*="affiliate.js"]');
    const configUrl = panel.dataset.configUrl || new URL('affiliate_config.json', script?.src || document.baseURI).href;
    let config;
    try { config = await fetchJson(configUrl, 4000); } catch (_) { return; }
    let storage;
    try { storage = scope.localStorage; } catch (_) {}
    let selected = languageFallback(config, navigator.language);
    let interacted = false;
    let revision = 0;
    const market = panel.querySelector('[data-market]');
    const city = panel.querySelector('[data-city]');
    const district = panel.querySelector('[data-district]');
    const option = (select, value, text) => { const o = document.createElement('option'); o.value = value; o.textContent = text; select.appendChild(o); };
    option(market, 'AUTO', 'Automatic / 自動偵測');
    Object.entries(config.regions).forEach(([key, r]) => option(market, key, `${key.replace(/_/g,' / ')} · ${r.currency}`));
    function render() {
      const region = config.regions[selected];
      const text = labels[region.language.split('-')[0]] || labels.en;
      panel.lang = region.language;
      panel.querySelectorAll('[data-affiliate-text]').forEach(el => { el.textContent = text[Number(el.dataset.affiliateText)]; });
      market.value = selected;
      const previousCity = city.value;
      city.replaceChildren();
      config.cities.forEach(c => option(city, c.name, region.language.startsWith('zh') ? c.name : c.nameEn));
      if (config.cities.some(c => c.name === previousCity)) city.value = previousCity;
      const previousDistrict = district.value;
      district.replaceChildren();
      option(district, '', text[4]);
      config.districts.filter(d => d.city === city.value).forEach(d => option(district, d.name, d.name));
      if (Array.from(district.options).some(o => o.value === previousDistrict)) district.value = previousDistrict;
      district.disabled = district.options.length === 1;
      panel.querySelectorAll('[data-affiliate]').forEach(link => { link.href = buildLink(config, selected, link.dataset.affiliate, {city:city.value, district:district.value}); });
      const extras = panel.querySelector('[data-partner-links]');
      if (extras && !extras.childElementCount) {
        Object.keys(partnerNames).forEach(key => {
          const link = document.createElement('a');
          link.dataset.partner = key;
          link.href = config.platforms[key].url;
          link.target = '_blank';
          link.rel = 'sponsored noopener noreferrer';
          extras.appendChild(link);
        });
      }
      if (extras) {
        extras.querySelectorAll('[data-partner]').forEach(link => { link.textContent = partnerNames[link.dataset.partner][region.language.startsWith('zh') ? 0 : 1]; });
      }
    }
    market.addEventListener('change', () => {
      interacted = true;
      const version = ++revision;
      if (market.value === 'AUTO') {
        try { storage?.removeItem('twfun-affiliate-region'); } catch (_) {}
        detectRegion(config, navigator.language, storage).then(region => {
          if (version === revision) { selected = region; render(); }
        });
        return;
      }
      selected = market.value;
      try { storage?.setItem('twfun-affiliate-region', selected); } catch (_) {}
      render();
    });
    city.addEventListener('change', () => { district.value = ''; render(); });
    district.addEventListener('change', render);
    render();
    const detected = await detectRegion(config, navigator.language, storage);
    if (!interacted) { selected = detected; render(); }
  }

  const api = {regionForCountry, buildLink, languageFallback, detectRegion};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  scope.TaiwanAffiliate = api;
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
  }
})(typeof window !== 'undefined' ? window : globalThis);
