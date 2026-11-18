const assert = require('node:assert/strict');
const {test} = require('node:test');
const config = require('./affiliate_config.json');
const {regionForCountry, buildLink, languageFallback, detectRegion} = require('./affiliate.js');

test('all specified countries map to their regional markets', () => {
  for (const [country, market] of Object.entries({TW:'TW', CN:'TW', HK:'HK_MO', MO:'HK_MO', SG:'SG_MY', MY:'SG_MY', JP:'JP', KR:'KR', TH:'TH', VN:'VN', ID:'ID', PH:'SOUTH_ASIA', IN:'SOUTH_ASIA', NP:'SOUTH_ASIA', US:'GLOBAL', DE:'GLOBAL'})) {
    assert.equal(regionForCountry(config, country.toLowerCase()), market);
  }
});

test('all regional travel categories are HTTPS links with the correct tracking and currency', () => {
  for (const [key, region] of Object.entries(config.regions)) {
    for (const category of ['flights','hotel','charter','esim','transit','carRental','tripadvisor']) {
      const url = new URL(buildLink(config, key, category));
      assert.equal(url.protocol, 'https:');
      if (url.hostname.endsWith('.trip.com')) {
        assert.equal(url.hostname, region.tripHost);
        for (const [param, value] of Object.entries(config.tracking.trip)) assert.equal(url.searchParams.get(param), value);
        assert.equal(url.searchParams.get('curr'), region.currency);
      }
      if (url.hostname === 'www.klook.com') {
        assert.ok(url.pathname.startsWith('/' + region.klookLocale + '/'));
        assert.equal(url.searchParams.get('aid'), '123436');
        assert.equal(url.searchParams.get('currency'), region.currency);
      }
    }
  }
  assert.equal(new URL(buildLink(config, 'GLOBAL', 'flights')).hostname, 'expedia.tpk.lu');
  assert.equal(new URL(buildLink(config, 'GLOBAL', 'hotel')).hostname, 'hotels.tpk.lu');
  assert.equal(new URL(buildLink(config, 'GLOBAL', 'charter')).hostname, 'viator.tpk.lu');
  assert.equal(new URL(buildLink(config, 'GLOBAL', 'esim')).hostname, 'yesim.tpk.lu');
});

test('22 cities and specified districts preserve destinations without fabricated IDs', () => {
  assert.equal(config.cities.length, 22);
  for (const district of config.districts) {
    const url = new URL(buildLink(config, 'JP', 'hotel', {city:district.city, district:district.name}));
    assert.equal(url.searchParams.get('city'), district.city === '臺北市' ? '617' : '7662');
    assert.equal(url.searchParams.get('keyword'), district.keyword);
  }
  const url = new URL(buildLink(config, 'TW', 'hotel', {city:'臺南市'}));
  assert.equal(url.searchParams.get('city'), '3847');
  const keywordOnly = structuredClone(config);
  delete keywordOnly.cities.find(city => city.name === '臺南市').tripCityId;
  const fallback = new URL(buildLink(keywordOnly, 'TW', 'hotel', {city:'臺南市'}));
  assert.equal(fallback.searchParams.get('keyword'), '臺南市');
  assert.equal(fallback.searchParams.has('city'), false);
});

test('all 22 Taiwan cities have distinct numeric Trip IDs and county/city pairs stay separate', () => {
  assert.equal(new Set(config.cities.map(city=>city.tripCityId)).size,22);
  for (const city of config.cities) {
    assert.match(city.tripCityId,/^\d+$/);
    const url=new URL(buildLink(config,'TW','hotel',{city:city.name}));
    assert.equal(url.searchParams.get('city'),city.tripCityId);
  }
  const ids=Object.fromEntries(config.cities.map(city=>[city.name,city.tripCityId]));
  assert.equal(ids['新竹市'],'3845');
  assert.equal(ids['新竹縣'],'669328');
  assert.equal(ids['嘉義市'],'5152');
  assert.equal(ids['嘉義縣'],'650358');
  assert.equal(ids['連江縣'],'7808');
});

test('manual selection and unexpired geo cache avoid network requests', async () => {
  const storage = data => ({getItem:key=>data[key] || null});
  assert.equal(await detectRegion(config, 'en', storage({'twfun-affiliate-region':'JP'})), 'JP');
  assert.equal(await detectRegion(config, 'en', storage({'twfun-affiliate-geo':JSON.stringify({country:'MY',time:Date.now()})})), 'SG_MY');
});

test('geo errors, corrupt cache and denied storage fall back to browser language', async () => {
  const originalFetch = global.fetch;
  global.fetch = async () => { throw new Error('offline'); };
  try {
    const denied = {getItem(){throw new Error('denied');}};
    assert.equal(await detectRegion(config, 'ja-JP', denied), 'JP');
    assert.equal(await detectRegion(config, 'ko', {getItem:()=>'{broken'}), 'KR');
    assert.equal(languageFallback(config, 'zh-HK'), 'HK_MO');
    assert.equal(languageFallback(config, 'en-US'), 'GLOBAL');
  } finally {global.fetch = originalFetch;}
});

test('successful geo detection caches only the country and timestamp', async () => {
  const originalFetch = global.fetch;
  const data = {};
  global.fetch = async () => ({ok:true,json:async()=>({country_code:'VN',ip:'unused'})});
  try {
    const region = await detectRegion(config,'en',{getItem:key=>data[key],setItem:(key,value)=>data[key]=value});
    assert.equal(region,'VN');
    assert.deepEqual(Object.keys(JSON.parse(data['twfun-affiliate-geo'])).sort(),['country','time']);
  } finally {global.fetch=originalFetch;}
});
