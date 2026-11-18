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


if __name__=='__main__':unittest.main()
