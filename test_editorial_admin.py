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
