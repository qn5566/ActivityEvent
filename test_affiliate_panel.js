const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const config = require('./affiliate_config.json');

function element() {
  let value = '';
  return {
    dataset:{}, children:[], events:{},
    get value() {return value;}, set value(next) {value = next;},
    get options() {return this.children;},
    get childElementCount() {return this.children.length;},
    appendChild(child) {this.children.push(child); if (this.children.length === 1) value = child.value;},
    replaceChildren() {this.children = []; value = '';},
    addEventListener(name, fn) {this.events[name] = fn;},
    querySelectorAll() {return this.children;}
  };
}

test('booking panel initializes, switches markets and builds destination links', async () => {
  const market = element(), city = element(), district = element(), extras = element();
  const links = ['flights','hotel','charter','esim','transit','carRental','tripadvisor'].map(category => ({dataset:{affiliate:category}}));
  const texts = Array.from({length:14}, (_,i) => ({dataset:{affiliateText:String(i)}}));
  const panel = {dataset:{},querySelector:selector=>({'[data-market]':market,'[data-city]':city,'[data-district]':district,'[data-partner-links]':extras}[selector]),querySelectorAll:selector=>selector==='[data-affiliate]' ? links : texts};
  let init;
  const storage = new Map();
  const context = vm.createContext({
    URL, AbortController, setTimeout, clearTimeout, navigator:{language:'en-US'},
    window:{localStorage:{getItem:key=>storage.get(key),setItem:(key,val)=>storage.set(key,val),removeItem:key=>storage.delete(key)}},
    document:{readyState:'loading',baseURI:'https://example.test/',createElement:element,addEventListener:(name,fn)=>{init=fn;},querySelector:selector=>selector==='[data-affiliate-panel]' ? panel : {src:'https://example.test/affiliate.js'}},
    fetch:async url=>({ok:true,json:async()=>String(url).endsWith('affiliate_config.json') ? config : {country_code:'JP'}})
  });
  vm.runInContext(fs.readFileSync('./affiliate.js','utf8'), context);
  await init();
  assert.equal(panel.lang,'ja');
  assert.equal(market.value,'JP');
  assert.equal(city.options.length,22);
  assert.equal(new URL(links[0].href).hostname,'jp.trip.com');
  assert.equal(extras.children.length,11);
  market.value='HK_MO';market.events.change();
  assert.equal(storage.get('twfun-affiliate-region'),'HK_MO');
  assert.equal(panel.lang,'zh-HK');
  city.value='新北市';city.events.change();
  district.value='瑞芳區';district.events.change();
  const hotel = new URL(links[1].href);
  assert.equal(hotel.hostname,'hk.trip.com');
  assert.equal(hotel.searchParams.get('city'),'7662');
  assert.equal(hotel.searchParams.get('keyword'),'九份');
  market.value='GLOBAL';market.events.change();
  assert.equal(new URL(links[1].href).hostname,'hotels.tpk.lu');
  assert.equal(extras.children.length,11);
  market.value='AUTO';market.events.change();
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(market.value,'JP');
  assert.equal(storage.has('twfun-affiliate-region'),false);
});
