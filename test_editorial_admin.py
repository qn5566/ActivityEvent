import copy
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer

import admin
from editorial_reports import prepare_reports


class ReportAdminTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.web = self.root / 'web'
        self.web.mkdir()
        (self.web / 'journals.html').write_text('<html><head></head><body>preview</body></html>')
        self.reports = [{'id':'r1','slug':'sample','title':'中文報導','language':'zh',
                         'status':'published','published':True,'summary':'摘要',
                         'sections':[{'heading':'說明','content':'stale fallback',
                                      'blocks':[{'tag':'p','children':[{'text':'完整內容'},
                                          {'tag':'a','href':'https://maps.google.com/?q=test',
                                           'children':[{'text':'地圖'}]}]}]}]}]
        self.zh = self.root / 'content/zh/editorial_reports.json'
        self.en = self.root / 'content/en/editorial_reports.json'
        for path,language in [(self.zh,'zh'),(self.en,'en')]:
            path.parent.mkdir(parents=True)
            data=copy.deepcopy(self.reports);data[0]['language']=language
            path.write_text(json.dumps(data,ensure_ascii=False))
        self.english = self.en.read_bytes()
        self.patches = [patch.object(admin,'HERE',str(self.root)),
                        patch.object(admin,'WEB_ROOT',str(self.web)),
                        patch.object(admin,'ALLOWED_DIRS',(str(self.root/'content'),)),
                        patch.object(admin.Handler,'log_message')]
        for item in self.patches:item.start()
        self.server=ThreadingHTTPServer(('127.0.0.1',0),admin.Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base='http://127.0.0.1:%d'%self.server.server_port

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
        for item in reversed(self.patches):item.stop()
        self.temp.cleanup()

    def request(self,path,data=None):
        request=Request(self.base+path,data=None if data is None else json.dumps(data).encode(),
                        headers={'Content-Type':'application/json'})
        try:
            with urlopen(request) as response:return response.status,response.read()
        except HTTPError as error:return error.code,error.read()

    def save(self,data):return self.request('/api/file?path=content/zh/editorial_reports.json',data)

    def test_save_regenerates_text_and_updates_frontend_without_overwriting_translation(self):
        self.reports[0]['title']='已編輯的報導'
        code,raw=self.save(self.reports);result=json.loads(raw)
        self.assertEqual(code,200);self.assertEqual(result['synced'],[])
        self.assertTrue(result['snapshotUpdated'])
        saved=json.loads(self.zh.read_text())
        self.assertEqual(saved[0]['sections'][0]['content'],'完整內容地圖')
        self.assertEqual(saved,json.loads((self.web/'data/editorial_reports/zh.json').read_text()))
        self.assertEqual(self.en.read_bytes(),self.english)

    def test_unpublishing_one_language_stays_independent(self):
        self.reports[0].update(status='draft',published=False)
        self.assertEqual(self.save(self.reports)[0],200)
        self.assertFalse(json.loads(self.zh.read_text())[0]['published'])
        self.assertEqual(self.en.read_bytes(),self.english)

    def test_invalid_reports_are_rejected_without_mutation(self):
        original=self.zh.read_bytes()
        cases=[{},self.reports+self.reports]
        for field,value in [('title',''),('published',False),('language','en'),('coverImg','javascript:alert(1)')]:
            data=copy.deepcopy(self.reports);data[0][field]=value;cases.append(data)
        data=copy.deepcopy(self.reports);data[0]['sections'][0]['blocks']=[{'tag':'script','children':[]}];cases.append(data)
        data=copy.deepcopy(self.reports);data[0]['sections'][0]['blocks'][0]['children'][1]['href']='javascript:alert(1)';cases.append(data)
        for data in cases:
            with self.subTest(data=data):
                self.assertEqual(self.save(data)[0],400)
                self.assertEqual(self.zh.read_bytes(),original)

    def test_preview_uses_live_json_and_keeps_file_boundaries(self):
        code,body=self.request('/preview/journals.html?type=reports')
        self.assertEqual(code,200);self.assertIn(b'window.CONTENT_BASE_URL="/content"',body)
        code,raw=self.request('/content/zh/editorial_reports.json')
        self.assertEqual(code,200);self.assertEqual(json.loads(raw)[0]['title'],'中文報導')
        for path in ['/preview/%2e%2e/admin.py','/content/_translations/private.json','/content/zh/../../admin.py']:
            self.assertEqual(self.request(path)[0],404)

    def michelin_fixture(self):
        for language in ['zh','en']:
            (self.root/f'content/{language}/michelin.json').write_text(json.dumps({'stars':[{'id':'star-1','name':'Le Palais'},{'id':'star-2','name':'Other'}],'bib':[]}))
        article=copy.deepcopy(self.reports[0]);article.update(restaurantId='star-1',honors={'years':['2025 ★★★']},menuVariants=[{'language':'zh','items':[{'id':'dish-1','name':'烤鴨','price':'NT$ 4,280+','description':'需預訂'}]}])
        for language in ['zh','en']:
            translated=copy.deepcopy(article);translated['language']=language
            (self.root/f'content/{language}/michelin_articles.json').write_text(json.dumps([translated]))
        return [article]

    def test_themes_add_delete_preserves_translations_and_locale_flight(self):
        for language in ('zh', 'en'):
            data = [{'id': key, 'name': language + key, 'spots': [{'name': language + key}],
                     'bookingCta': {'flight': 'https://flight.example/' + language,
                                    'hotel': 'https://hotel.example/original'}} for key in ('a', 'b', 'c')]
            (self.root / f'content/{language}/themes.json').write_text(json.dumps(data))
        new_theme = {'id': 'new', 'name': '新主題', 'spots': [], 'experiences': [], 'itineraries': [],
                     'subCategories': [{'id': 'general', 'name': '精選'}], 'bookingCta': {}}
        source = [{'id': 'c', 'name': '中文丙', 'spots': [{'name': '中文景點'}],
                   'bookingCta': {'flight': 'https://flight.example/zh',
                                  'hotel': 'https://hotel.example/updated'}}, new_theme]
        path = '/api/file?path=content/zh/themes.json'
        self.assertEqual(self.request(path, source)[0], 200)
        translated_path = self.root / 'content/en/themes.json'
        translated = json.loads(translated_path.read_text())
        self.assertEqual([theme['id'] for theme in translated], ['c', 'new'])
        self.assertEqual(translated[0]['name'], 'enc')
        self.assertEqual(translated[0]['spots'][0]['name'], 'enc')
        self.assertEqual(translated[0]['bookingCta']['flight'], 'https://flight.example/en')
        self.assertEqual(translated[0]['bookingCta']['hotel'], 'https://hotel.example/updated')
        self.assertEqual(translated[1], new_theme)
        self.assertEqual(self.request(path, [])[0], 200)
        self.assertEqual(json.loads(translated_path.read_text()), [])

    def test_themes_rejects_invalid_structure_without_writing(self):
        path = self.root / 'content/zh/themes.json'
        path.write_text('[{"id":"original","spots":[]}]')
        original = path.read_bytes()
        for data in [{}, [{'id': ''}], [{'id': 'same'}, {'id': 'same'}],
                     [{'id': 'a', 'spots': {}}], [{'id': 'a', 'bookingCta': []}]]:
            self.assertEqual(self.request('/api/file?path=content/zh/themes.json', data)[0], 400)
            self.assertEqual(path.read_bytes(), original)

    def test_souvenirs_nested_add_delete_preserves_translations(self):
        for language in ('zh', 'en'):
            data = [{'id': key, 'name': language + key, 'items': [
                {'rank': rank, 'name': language + str(rank), 'buyUrl': 'https://shop.example/' + str(rank)}
                for rank in (1, 2, 3)]} for key in ('a', 'b', 'c')]
            (self.root / f'content/{language}/souvenirs.json').write_text(json.dumps(data))
        new_item = {'id': 'new-item', 'rank': 4, 'name': '新商品'}
        source = [{'id': 'c', 'name': '中文分類', 'items': [
            {'rank': 3, 'name': '中文商品', 'buyUrl': 'https://shop.example/updated'}, new_item]},
            {'id': 'new-category', 'name': '新分類', 'items': []}]
        path = '/api/file?path=content/zh/souvenirs.json'
        self.assertEqual(self.request(path, source)[0], 200)
        translated_path = self.root / 'content/en/souvenirs.json'
        translated = json.loads(translated_path.read_text())
        self.assertEqual([category['id'] for category in translated], ['c', 'new-category'])
        self.assertEqual(translated[0]['name'], 'enc')
        self.assertEqual(translated[0]['items'][0]['name'], 'en3')
        self.assertEqual(translated[0]['items'][0]['buyUrl'], 'https://shop.example/updated')
        self.assertEqual(translated[0]['items'][1], new_item)
        # New IDs distinguish replacements even when a deleted last item's rank is reused.
        source[0]['items'] = [{'id': 'replacement', 'rank': 4, 'name': '替代商品'}]
        self.assertEqual(self.request(path, source)[0], 200)
        self.assertEqual(json.loads(translated_path.read_text())[0]['items'], source[0]['items'])
        source[0]['items'] = []
        self.assertEqual(self.request(path, source)[0], 200)
        self.assertEqual(json.loads(translated_path.read_text())[0]['items'], [])
        self.assertEqual(self.request(path, [])[0], 200)
        self.assertEqual(json.loads(translated_path.read_text()), [])

    def test_souvenirs_rejects_invalid_structure_without_writing(self):
        path = self.root / 'content/zh/souvenirs.json'
        path.write_text('[{"id":"a","items":[]}]')
        original = path.read_bytes()
        for data in [{}, [{'id': 'a', 'items': {}}], [{'id': '', 'items': []}],
                     [{'id': 'a', 'items': []}, {'id': 'a', 'items': []}],
                     [{'id': 'a', 'items': [{'rank': 1}, {'rank': 1}]}],
                     [{'id': 'a', 'items': [{'rank': 1, 'id': 'same'}, {'rank': 2, 'id': 'same'}]}]]:
            self.assertEqual(self.request('/api/file?path=content/zh/souvenirs.json', data)[0], 400)
            self.assertEqual(path.read_bytes(), original)

    def test_activities_add_delete_preserves_translations_by_activity_id(self):
        for language in ('zh', 'en'):
            (self.root / f'content/{language}/activities.json').write_text(json.dumps([
                {'activityId': key, 'name': language + key, 'desc': language + ' description',
                 'img': 'https://img.example/' + key} for key in ('a', 'b', 'c')]))
        data = [{'activityId': 'c', 'name': '中文活動', 'desc': '中文介紹',
                 'img': 'https://img.example/updated'},
                {'activityId': 'new-tour', 'name': '新增活動', 'rank': 4}]
        path = '/api/file?path=content/zh/activities.json'
        self.assertEqual(self.request(path, data)[0], 200)
        translated = json.loads((self.root / 'content/en/activities.json').read_text())
        self.assertEqual([item['activityId'] for item in translated], ['c', 'new-tour'])
        self.assertEqual(translated[0]['name'], 'enc')
        self.assertEqual(translated[0]['desc'], 'en description')
        self.assertEqual(translated[0]['img'], data[0]['img'])
        self.assertEqual(translated[1], data[1])
        self.assertEqual(self.request(path, [])[0], 200)
        for language in ('zh', 'en'):
            self.assertEqual(json.loads((self.root / f'content/{language}/activities.json').read_text()), [])

    def test_activities_rejects_invalid_data_without_writing(self):
        path = self.root / 'content/zh/activities.json'
        path.write_text('[{"activityId":"original","name":"活動"}]')
        original = path.read_bytes()
        for data in [{}, [{'activityId': '', 'name': '活動'}], [{'name': '活動'}],
                     [{'activityId': 'a', 'name': ''}],
                     [{'activityId': 'a', 'name': '甲'}, {'activityId': 'a', 'name': '乙'}]]:
            self.assertEqual(self.request('/api/file?path=content/zh/activities.json', data)[0], 400)
            self.assertEqual(path.read_bytes(), original)

    def test_blog_add_delete_preserves_translated_articles_by_id(self):
        for language in ('zh', 'en'):
            path = self.root / f'content/{language}/blog.json'
            path.write_text(json.dumps([
                {'id': key, 'title': language + key, 'heroImg': 'https://img.example/' + key,
                 'fullHtmlArticle': '<p>' + language + key + '</p>'}
                for key in ('a', 'b', 'c')]))
        data = [{'id': 'c', 'title': '中文丙', 'heroImg': 'https://img.example/updated',
                 'fullHtmlArticle': '<p>中文</p>'},
                {'id': 'new', 'title': '新文章', 'spotInfo': {'links': []}}]
        code, _ = self.request('/api/file?path=content/zh/blog.json', data)
        self.assertEqual(code, 200)
        translated = json.loads((self.root / 'content/en/blog.json').read_text())
        self.assertEqual([article['id'] for article in translated], ['c', 'new'])
        self.assertEqual(translated[0]['title'], 'enc')
        self.assertEqual(translated[0]['fullHtmlArticle'], '<p>enc</p>')
        self.assertEqual(translated[0]['heroImg'], data[0]['heroImg'])
        self.assertEqual(translated[1], data[1])
        self.assertEqual(self.request('/api/file?path=content/zh/blog.json', [])[0], 200)
        for language in ('zh', 'en'):
            self.assertEqual(json.loads((self.root / f'content/{language}/blog.json').read_text()), [])

    def test_blog_rejects_invalid_and_duplicate_ids_without_writing(self):
        path = self.root / 'content/zh/blog.json'
        path.write_text('[{"id":"original"}]')
        original = path.read_bytes()
        for data in [{}, [{'id': ''}], [{'title': 'missing ID'}], [{'id': 'a'}, {'id': 'a'}]]:
            self.assertEqual(self.request('/api/file?path=content/zh/blog.json', data)[0], 400)
            self.assertEqual(path.read_bytes(), original)

    def test_michelin_directory_add_delete_preserves_translations_by_id(self):
        self.michelin_fixture()
        english_path = self.root / 'content/en/michelin.json'
        english = json.loads(english_path.read_text())
        english['stars'][0]['name'] = 'Translated restaurant'
        english_path.write_text(json.dumps(english))
        data = {'stars': [{'id': 'star-1', 'name': '中文餐廳'},
                          {'id': 'star-new', 'name': '新店'}],
                'bib': [{'id': 'bib-new', 'name': '新必比登'}]}
        code, _ = self.request('/api/file?path=content/zh/michelin.json', data)
        self.assertEqual(code, 200)
        saved = json.loads(english_path.read_text())
        self.assertEqual([r['id'] for r in saved['stars']], ['star-1', 'star-new'])
        self.assertEqual(saved['stars'][0]['name'], 'Translated restaurant')
        self.assertEqual(saved['stars'][1], data['stars'][1])
        self.assertEqual(saved['bib'], data['bib'])

    def test_michelin_directory_rejects_deleting_restaurant_linked_in_other_language(self):
        self.michelin_fixture()
        (self.root / 'content/zh/michelin_articles.json').write_text('[]')
        paths = [self.root / f'content/{lang}/michelin.json' for lang in ('zh', 'en')]
        original = [path.read_bytes() for path in paths]
        code, body = self.request('/api/file?path=content/zh/michelin.json', {'stars': [], 'bib': []})
        self.assertEqual(code, 400)
        self.assertIn('en', json.loads(body)['error'])
        self.assertEqual([path.read_bytes() for path in paths], original)

    def test_michelin_directory_rejects_duplicate_ids_across_groups(self):
        self.michelin_fixture()
        path = self.root / 'content/zh/michelin.json'
        original = path.read_bytes()
        for data in [{'stars': [], 'bib': None},
                     {'stars': [{'id': 'same'}], 'bib': [{'id': 'same'}]},
                     {'stars': [{'id': ''}], 'bib': []}]:
            self.assertEqual(self.request('/api/file?path=content/zh/michelin.json', data)[0], 400)
            self.assertEqual(path.read_bytes(), original)

    def test_michelin_save_preserves_restaurant_link_menu_and_other_language(self):
        data=self.michelin_fixture();english=(self.root/'content/en/michelin_articles.json').read_bytes()
        data[0]['menuVariants'][0]['items'][0]['price']='NT$ 4,500+'
        code,raw=self.request('/api/file?path=content/zh/michelin_articles.json',data)
        self.assertEqual(code,200);self.assertTrue(json.loads(raw)['snapshotUpdated']);self.assertEqual(json.loads(raw)['synced'],[])
        saved=json.loads((self.web/'data/michelin_articles/zh.json').read_text())
        self.assertEqual(saved[0]['restaurantId'],'star-1');self.assertEqual(saved[0]['menuVariants'][0]['items'][0]['price'],'NT$ 4,500+')
        self.assertEqual((self.root/'content/en/michelin_articles.json').read_bytes(),english)

    def test_michelin_rejects_orphaned_or_duplicated_links_and_bad_menu_data(self):
        data=self.michelin_fixture();path=self.root/'content/zh/michelin_articles.json';original=path.read_bytes();cases=[]
        bad=copy.deepcopy(data);bad[0]['restaurantId']='missing';cases.append(bad)
        bad=copy.deepcopy(data);extra=copy.deepcopy(bad[0]);extra.update(id='other',slug='other');bad.append(extra);cases.append(bad)
        bad=copy.deepcopy(data);bad[0]['menuVariants'][0]['items'][0]['price']=4500;cases.append(bad)
        bad=copy.deepcopy(data);bad[0]['sections'][0]['layout']='script';cases.append(bad)
        for bad in cases:
            self.assertEqual(self.request('/api/file?path=content/zh/michelin_articles.json',bad)[0],400)
            self.assertEqual(path.read_bytes(),original)


if __name__=='__main__':unittest.main()
