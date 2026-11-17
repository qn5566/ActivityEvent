"""Validate shared settings before the admin writes them to disk."""
import re
from urllib.parse import urlsplit


def validate_config(data):
    def require(condition, message):
        if not condition:
            raise ValueError(message)

    def https(value):
        if not isinstance(value, str):
            return False
        parsed = urlsplit(value)
        return parsed.scheme == 'https' and bool(parsed.hostname)

    require(isinstance(data, dict), '分潤設定必須為物件')
    require(data.get('version') == 1, '不支援的分潤設定版本')
    tracking = data.get('tracking', {})
    require(isinstance(tracking, dict), 'tracking 必須為物件')
    trip = tracking.get('trip', {})
    require(isinstance(trip, dict), 'Trip 追蹤參數必須為物件')
    for key in ('Allianceid', 'SID', 'trip_sub3'):
        require(isinstance(trip.get(key), str) and bool(trip[key].strip()), '缺少 Trip 參數：' + key)
    require(isinstance(tracking.get('klookAid'), str) and tracking['klookAid'].isdigit(), 'Klook aid 必須為數字字串')
    regions = data.get('regions', {})
    require(isinstance(regions, dict), 'regions 必須為物件')
    require(set(('TW', 'HK_MO', 'SG_MY', 'JP', 'KR', 'TH', 'VN', 'ID', 'SOUTH_ASIA', 'GLOBAL')) <= set(regions), '缺少必要分流區域')
    for key, region in regions.items():
        require(isinstance(region, dict), '區域必須為物件：' + key)
        require(isinstance(region.get('countries'), list) and all(
            isinstance(c, str) and re.fullmatch('[A-Z]{2}', c) for c in region['countries']), '國家代碼格式錯誤：' + key)
        require(isinstance(region.get('currency'), str) and re.fullmatch('[A-Z]{3}', region['currency']), '幣別格式錯誤：' + key)
        for field in ('language', 'klookLocale'):
            require(isinstance(region.get(field), str) and re.fullmatch('[a-zA-Z-]+', region[field]), '語系格式錯誤：' + key)
        host = region.get('tripHost')
        require(host is None or isinstance(host, str) and re.fullmatch(r'[a-z]+\.trip\.com', host), 'Trip 網域格式錯誤：' + key)
    geo = data.get('geo', {})
    require(isinstance(geo, dict) and https(geo.get('endpoint')), 'IP 偵測網址必須為 HTTPS')
    for field in ('timeoutMs', 'cacheTtlMs'):
        require(type(geo.get(field)) is int and geo[field] > 0, 'IP 偵測逾時／快取時間必須為大於 0 的整數')
    platforms = data.get('platforms', {})
    require(isinstance(platforms, dict), 'platforms 必須為物件')
    for key in ('expedia', 'hotels', 'viator', 'esim', 'transit', 'carRental', 'tripadvisor'):
        require(key in platforms, '缺少分潤平台：' + key)
    for key, platform in platforms.items():
        require(isinstance(platform, dict) and https(platform.get('url')), '分潤網址必須為 HTTPS：' + key)
    cities = data.get('cities')
    districts = data.get('districts')
    require(isinstance(cities, list) and len(cities) == 22, '縣市必須包含 22 筆')
    require(isinstance(districts, list), '行政區必須為陣列')
    for city in cities:
        require(isinstance(city, dict) and all(isinstance(city.get(k), str) and city[k] for k in ('name', 'nameEn', 'keyword')), '縣市欄位不完整')
    for district in districts:
        require(isinstance(district, dict) and all(isinstance(district.get(k), str) and district[k] for k in ('city', 'name', 'keyword')), '行政區欄位不完整')
