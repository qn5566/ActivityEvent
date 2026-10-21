#!/usr/bin/env python3
"""一次性修正：地名/建物名正規化為「專名 + 英文後綴」，並清除拼音殘留與幻覺。
乾跑預設；--apply 套用。"""
import json, sys, re
from pypinyin import lazy_pinyin

LANGS = ['en','ja','ko','vi','es','fil','hi','id','ms','th']
DRY = '--apply' not in sys.argv

FULL = {
 '九族文化村':'Formosan Aboriginal Culture Village','國立故宮博物院':'National Palace Museum',
 '淡水老街':'Tamsui Old Street','愛河':'Love River','日月潭':'Sun Moon Lake',
 '拉魯島':'Lalu Island','西門町':'Ximending','阿里山':'Alishan','太平山':'Taiping Mountain',
 '翠峰湖':'Cuifeng Lake','滿月圓':'Manyueyuan','墾丁':'Kenting','九份':'Jiufen','集集':'Jiji',
 '伊達邵':'Ita Thao','淡水':'Tamsui','東眼山':'Dongyan Mountain','內洞':'Neidong','拉拉山':'Lala Mountain',
 '雪霸':'Shei-Pa','玉山':'Jade Mountain','合歡山':'Hehuan Mountain','太魯閣':'Taroko',
 '台灣':'Taiwan','小台灣':'Little Taiwan','奮起湖':'Fenqihu','綠島':'Green Island',
 '永浴愛河':'Eternal Love','民眾參拜指南宮':'Worshipers at Zhinan Temple',
 '中區':'Central District','東區':'East District','西區':'West District','南區':'South District','北區':'North District',
 '中西區':'West Central District',
 '新市區':'Xinshi District','台北市':'Taipei City','臺北市':'Taipei City',
}

# 官方專名 + 常見描述詞（最長優先替換）
PROPER = [
 ('日月潭國家風景區','Sun Moon Lake National Scenic Area'),
 ('九族文化村','Formosan Aboriginal Culture Village'),('國立故宮博物院','National Palace Museum'),
 ('日月潭','Sun Moon Lake'),('太平山','Taiping Mountain'),('阿里山','Alishan'),('伊達邵','Ita Thao'),
 ('翠峰湖','Cuifeng Lake'),('滿月圓','Manyueyuan'),('墾丁','Kenting'),('淡水','Tamsui'),('西門町','Ximending'),
 ('拉魯島','Lalu Island'),('愛河','Love River'),('集集','Jiji'),('內洞','Neidong'),('羅東','Luodong'),
 ('土場','Tuchang'),('車埕','Checheng'),('星巴克','Starbucks'),('太魯閣','Taroko'),('玉山','Jade Mountain'),
 ('合歡山','Hehuan Mountain'),('拉拉山','Lala Mountain'),('台灣','Taiwan'),('綠島','Green Island'),
 ('奮起湖','Fenqihu'),('芒果樹','Mango Tree'),('夫妻樹','Couple Tree'),('樟樹','Camphor Tree'),
 ('紅樹林','Mangrove'),('巨木群','Giant Trees'),('博物館','Museum'),('美術館','Art Museum'),
 ('生態','Ecological'),('森林','Forest'),('濕地','Wetland'),('文化','Cultural'),('文創','Cultural Creative'),
 ('創意','Creative'),('產業','Industrial'),('休閒','Leisure'),('觀光','Tourism'),('藝術','Art'),
 ('教育','Education'),('親水','Waterfront'),('茶葉','Tea'),('咖啡','Coffee'),('陶瓷','Ceramics'),
 ('木雕','Woodcarving'),('石雕','Stone Carving'),('燈塔','Lighthouse'),('漁人','Fisherman'),
 ('戶外','Outdoor'),('浮潛','Snorkeling'),('稻田','Paddy Field'),('草坪','Lawn'),('景觀','Landscape'),('藝文','Arts'),
 ('自然','Nature'),('地質','Geological'),('海洋','Ocean'),('海濱','Seaside'),('濱海','Seaside'),
 ('縣立','County'),
 ('縣','County'),
 ('國立','National'),
 ('市立','Municipal'),
 ('新北投','Xinbeitou'),('北投','Beitou'),('臺北','Taipei'),('台北','Taipei'),('新北','New Taipei'),('桃園','Taoyuan'),('臺中','Taichung'),('台中','Taichung'),
 ('臺南','Tainan'),('台南','Tainan'),('高雄','Kaohsiung'),('基隆','Keelung'),('新竹','Hsinchu'),('嘉義','Chiayi'),
 ('苗栗','Miaoli'),('彰化','Changhua'),('南投','Nantou'),('雲林','Yunlin'),('屏東','Pingtung'),('宜蘭','Yilan'),
 ('花蓮','Hualien'),('臺東','Taitung'),('台東','Taitung'),('澎湖','Penghu'),('金門','Kinmen'),('連江','Lienchiang'),
]

SUFFIX = [
 ('國家森林遊樂區','National Forest Recreation Area'),('自然教育園區','Nature Education Area'),
 ('地震紀念園區','Earthquake Memorial Park'),('綠色隧道','Green Tunnel'),('高空觀景步道','Skywalk'),
 ('七彩吊橋','Rainbow Suspension Bridge'),('碼頭商圈','Wharf Commercial District'),('風景區','Scenic Area'),
 ('火車站','Railway Station'),('漁港','Fishing Harbor'),('老街','Old Street'),('吊橋','Suspension Bridge'),
 ('車站','Station'),('商圈','Commercial District'),('碼頭','Wharf'),('書院','Academy'),('新村','New Village'),
 ('渡假村','Resort'),('度假村','Resort'),('生態村','Ecological Village'),('部落','Tribe'),('遊憩區','Recreation Area'),
 ('森林遊樂區','Forest Recreation Area'),('遊樂區','Recreation Area'),
 ('園區','Park'),('公園','Park'),('農場','Farm'),('牧場','Ranch'),('美術館','Art Museum'),('博物館','Museum'),
 ('紀念館','Memorial Hall'),('文化館','Culture Center'),('陳列館','Exhibition Hall'),('展示館','Exhibition Hall'),
 ('圖書館','Library'),('總館','Main Library'),('水庫','Reservoir'),('水壩','Dam'),('瀑布','Waterfall'),
 ('步道','Trail'),('古道','Ancient Trail'),('隧道','Tunnel'),('大橋','Bridge'),('橋','Bridge'),('島','Island'),
 ('港','Harbor'),('寺','Temple'),('廟','Temple'),('宮','Temple'),('神社','Shrine'),('溫泉','Hot Spring'),
 ('縣','County'),('鄉','Township'),('自然保留區','Nature Reserve'),('保留區','Nature Reserve'),('溫泉區','Hot Spring Area'),('潛水區','Diving Area'),('休息區','Rest Area'),('生態區','Ecological Area'),('漁業區','Fishing Area'),('地質區','Geological Area'),('度假區','Resort Area'),('渡假區','Resort Area'),('戶外區','Outdoor Area'),('浮潛區','Snorkeling Area'),('稻田區','Paddy Field Area'),('草坪區','Lawn Area'),('景觀區','Landscape Area'),('賞櫻區','Cherry Blossom Viewing Area'),('花卉區','Flower Area'),('小吃區','Snack Area'),('營區','Camp Area'),('校區','Campus'),('廠區','Factory Area'),('院區','Branch'),('地區','Area'),('市區','Downtown'),('街區','Street District'),('特區','Special District'),('風景特定區','Scenic Special Area'),('野生動物保護區','Wildlife Conservation Area'),('紅樹林保護區','Mangrove Conservation Area'),('保護區','Conservation Area'),('保存區','Preservation Area'),('保育區','Conservation Area'),('露營區','Camping Area'),('服務區','Service Area'),('賞鳥區','Bird Watching Area'),('農業區','Agricultural Area'),('展演區','Exhibition Area'),('閱覽區','Reading Area'),('體驗區','Experience Area'),('休憩區','Rest Area'),('展示區','Exhibition Area'),('展售區','Sales Area'),('社區','Community'),('區','District'),('村','Village'),('山','Mountain'),('湖','Lake'),
 ('溪','Creek'),('河','River'),('灣','Bay'),('谷','Valley'),('洞','Cave'),('石','Stone'),('岩','Rock'),
 ('百年老樹','Century-old Tree'),('大樟樹','Giant Camphor Tree'),('夫妻樹','Couple Tree'),('芒果樹','Mango Tree'),
 ('老樟樹','Old Camphor Tree'),('樟樹','Camphor Tree'),('老樹','Old Tree'),('樹','Tree'),
]

STOP_MARKERS = ['眺','鳥瞰','遠眺','俯瞰','一座','群山','自導','全景','日出','空拍','滿足','門市','超市','夜市','漁市','市場','之']

def is_han(s): return bool(s) and all('\u4e00' <= c <= '\u9fff' for c in s)

def suffix_of(k):
    for suf, en in SUFFIX:
        if k.endswith(suf): return suf, en
    return None, None

def render_proper(prefix):
    for zh, en in PROPER:
        if zh in prefix:
            prefix = prefix.replace(zh, ' ' + en + ' ')
    toks = prefix.split()
    out = []
    for t in toks:
        out.append(''.join(lazy_pinyin(t)).capitalize() if is_han(t) else t)
    return ' '.join(out) if out else ''.join(lazy_pinyin(prefix)).capitalize()

def compute(k):
    if k in FULL: return FULL[k]
    suf, en = suffix_of(k)
    if not suf: return None
    prefix = k[:-len(suf)]
    if not prefix: return en
    if not is_han(prefix): return None
    if len(k) > 12: return None
    if prefix[-1] == '之': return None
    for m in STOP_MARKERS:
        if m in prefix: return None
    return render_proper(prefix) + ' ' + en

# 偵測壞值：純拼音，或值中殘留「中文詞的拼音」
TERMS = SUFFIX + PROPER
def pinyin_of(zh): return ''.join(lazy_pinyin(zh))
def has_pinyin_residue(v):
    s = re.sub(r'[^a-z]', '', v.lower())
    for zh, _ in TERMS:
        py = pinyin_of(zh)
        if len(py) >= 4 and py in s:
            return True
    return False

def is_broken(v):
    return bool(re.fullmatch(r'[A-Za-z]+', v)) or has_pinyin_residue(v)

def main():
    data = {l: json.load(open(f'data/_translations/{l}.json', encoding='utf-8-sig')) for l in LANGS}
    changes = []
    for k, old in data['en'].items():
        new = compute(k)
        if not new or new == old: continue
        if not is_broken(old): continue
        changes.append((k, old, new))
    changes.sort(key=lambda x: x[0])
    print(f'proposed changes: {len(changes)}')
    if DRY:
        for k, o, n in changes:
            print(f'{k}\t{o}\t->\t{n}')
    else:
        for k, o, n in changes:
            for l in LANGS:
                data[l][k] = n
        for l in LANGS:
            json.dump(data[l], open(f'data/_translations/{l}.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
        print('applied to', len(LANGS), 'langs; changed', len(changes), 'keys')

main()
