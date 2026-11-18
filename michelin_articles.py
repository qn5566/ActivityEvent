"""Restaurant-linked article validation; editions remain independent."""
from editorial_reports import prepare_reports, validate_url


def prepare_articles(data, language, restaurants):
    prepare_reports(data, language)
    known = {item['id'] for group in ('stars','bib') for item in restaurants.get(group,[]) if isinstance(item,dict) and 'id' in item}
    linked=set()
    for article in data:
        restaurant=article.get('restaurantId')
        if not isinstance(restaurant,str) or restaurant not in known:
            raise ValueError('請選擇存在的米其林餐廳 ID')
        if restaurant in linked:
            raise ValueError('同一語言的每間餐廳只能對應一篇文章')
        linked.add(restaurant)
        validate_url(article.get('bookingUrl'))
        for section in article.get('sections',[]):
            if section.get('layout','intro') not in ('intro','ambiance','dish','guide'):
                raise ValueError('段落類型必須為 intro、ambiance、dish 或 guide')
        if not isinstance(article.get('quickFacts',[]),list) or any(not isinstance(v,str) for v in article.get('quickFacts',[])):
            raise ValueError('餐廳重點必須是文字陣列')
        honors=article.get('honors',{})
        if not isinstance(honors,dict) or not isinstance(honors.get('years',[]),list) or any(not isinstance(v,str) for v in honors.get('years',[])):
            raise ValueError('獲獎紀錄格式錯誤')
        for key in ['heading','content','note']:
            if key in honors and not isinstance(honors[key],str):raise ValueError('獲獎說明必須是文字')
        variants=article.get('menuVariants',[])
        if not isinstance(variants,list):raise ValueError('菜單語言版本必須是陣列')
        languages=set()
        for variant in variants:
            if not isinstance(variant,dict) or variant.get('language') not in ('zh','en','ja','ko','es','th','vi','ms','fil','hi','id','de'):
                raise ValueError('菜單語言代碼錯誤')
            if variant['language'] in languages:raise ValueError('菜單語言不可重複')
            languages.add(variant['language'])
            items=variant.get('items',[])
            if not isinstance(items,list):raise ValueError('菜單項目必須是陣列')
            ids=set()
            for item in items:
                if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not item['id'].strip() or item['id'] in ids:
                    raise ValueError('菜色 ID 不可空白或重複')
                ids.add(item['id'])
                for key in ('name','description','price'):
                    if not isinstance(item.get(key,''),str):raise ValueError('菜名、說明與價格必須是文字')
    return data
