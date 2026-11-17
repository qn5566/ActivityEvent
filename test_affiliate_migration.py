import json
import copy
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from migrate_affiliate_links import normalize_url, rewrite
from affiliate_config import validate_config
import admin

CONFIG = json.loads(Path(__file__).with_name('affiliate_config.json').read_text())


class AffiliateMigrationTests(unittest.TestCase):
    def test_shared_config_is_valid(self):
        validate_config(CONFIG)

    def test_invalid_admin_settings_are_rejected(self):
        for key, value in [('regions', []), ('geo', {'endpoint': 'javascript:alert(1)'}), ('tracking', {'klookAid': 123})]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                data = copy.deepcopy(CONFIG)
                data[key] = value
                validate_config(data)

    def test_trip_keeps_city_airports_and_updates_missing_or_stale_tracking(self):
        result = normalize_url('https://jp.trip.com/flights/?dcity=TYO&acity=TPE&Allianceid=old&trip_sub3=old', CONFIG)
        query = parse_qs(urlsplit(result).query)
        self.assertEqual(query['dcity'], ['TYO'])
        self.assertEqual(query['acity'], ['TPE'])
        self.assertEqual(query['Allianceid'], ['9507030'])
        self.assertEqual(query['SID'], ['325761227'])
        self.assertEqual(query['trip_sub3'], ['D20272275'])
        self.assertEqual(normalize_url(result, CONFIG), result)

    def test_klook_product_and_nested_redirect_are_preserved(self):
        result = normalize_url('https://affiliate.klook.com/redirect?aid=old&k_site=https%3A%2F%2Fwww.klook.com%2Fja%2Factivity%2F9909-tour%3Faid%3Dold', CONFIG)
        query = parse_qs(urlsplit(result).query)
        self.assertEqual(query['aid'], ['123436'])
        destination = urlsplit(query['k_site'][0])
        self.assertEqual(destination.path, '/ja/activity/9909-tour')
        self.assertEqual(parse_qs(destination.query)['aid'], ['123436'])

    def test_html_links_and_unrelated_urls(self):
        html = '<a href="https://tw.trip.com/hotels/list?city=617&amp;SID=old">訂房</a>'
        result = rewrite({'html': html, 'map': 'https://maps.google.com/?q=Taipei'}, CONFIG)
        self.assertIn('city=617&amp;Allianceid=9507030', result['html'])
        self.assertIn('&amp;trip_sub3=D20272275', result['html'])
        self.assertEqual(result['map'], 'https://maps.google.com/?q=Taipei')

    def test_campaign_subids_align_with_exact_spec_url(self):
        url = CONFIG['platforms']['souvenirs']['url'].split('?')[0] + '?subid_1=old&subid_2=old'
        self.assertEqual(normalize_url(url, CONFIG), CONFIG['platforms']['souvenirs']['url'])

    def test_space_in_product_path_is_encoded_without_splitting_the_url(self):
        url = 'https://www.klook.com/zh-TW/activity/46198-Hualien River Kayaking Experience ?aid=106452'
        result = rewrite(url, CONFIG)
        self.assertNotIn(' ', result)
        self.assertIn('Hualien%20River%20Kayaking%20Experience%20', result)
        self.assertEqual(parse_qs(urlsplit(result).query)['aid'], ['123436'])
        self.assertEqual(rewrite(result, CONFIG), result)


class AffiliateAdminApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), admin.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:%d' % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_shared_config_is_available_in_admin_file_list_and_api(self):
        with urllib.request.urlopen(self.base + '/api/files', timeout=3) as response:
            self.assertIn('affiliate_config.json', json.load(response)['.'])
        with urllib.request.urlopen(self.base + '/api/file?path=affiliate_config.json', timeout=3) as response:
            self.assertEqual(json.load(response)['data'], CONFIG)

    def test_invalid_settings_return_400_before_writing(self):
        request = urllib.request.Request(self.base + '/api/file?path=affiliate_config.json',
            data=b'{"version":9}', headers={'Content-Type': 'application/json'}, method='POST')
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 400)
        self.assertEqual(json.loads(Path(__file__).with_name('affiliate_config.json').read_text()), CONFIG)


if __name__ == '__main__':
    unittest.main()
