import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import admin
from admin_translation import AddedContentTranslator


class AddedTranslationTests(unittest.TestCase):
    def test_saved_translation_table_is_used_without_loading_engine(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / 'content/_translations'
            folder.mkdir(parents=True)
            (folder / 'en.json').write_text(json.dumps({'新店': 'New cafe'}))
            translator = AddedContentTranslator(tmp, 'content/zh/cafes.json')
            result = translator.translate({'id': 'new', 'name': '新店', 'mapUrl': 'https://example.com/新店', 'price': '100'}, 'en')
            self.assertEqual(result['name'], 'New cafe')
            self.assertEqual(result['mapUrl'], 'https://example.com/新店')
            self.assertEqual(result['price'], '100')
            self.assertEqual(translator.engines, {})

    def test_engine_translates_new_text_and_reuses_result(self):
        translator = AddedContentTranslator('.', 'content/zh/cafes.json')
        with patch('argostranslate.translate.get_installed_languages') as installed:
            source, target = unittest.mock.Mock(code='zh'), unittest.mock.Mock(code='en')
            installed.return_value = [source, target]
            engine = source.get_translation.return_value
            engine.translate.return_value = 'A new cafe'
            translator.tables['en'] = {}
            self.assertEqual(translator.text('全新咖啡店', 'en'), 'A new cafe')
            self.assertEqual(translator.text('全新咖啡店', 'en'), 'A new cafe')
            engine.translate.assert_called_once_with('全新咖啡店')
            self.assertEqual(translator.warnings, [])

    def test_html_links_and_native_menu_editions_are_preserved(self):
        translator = AddedContentTranslator('.', 'content/zh/cafe_articles.json')
        translator.tables['en'] = {'新店': 'New cafe'}
        menu = [{'language': 'zh', 'items': [{'name': '新店'}]}]
        result = translator.translate({'fullHtmlArticle': '<p> 新店 <a href="https://example.com/新店">新店</a></p>', 'menuVariants': menu}, 'en')
        self.assertEqual(result['fullHtmlArticle'], '<p> New cafe <a href="https://example.com/新店">New cafe</a></p>')
        self.assertEqual(result['menuVariants'], menu)

    def test_missing_model_aborts_translation_and_warns(self):
        translator = AddedContentTranslator('.', 'content/zh/cafes.json')
        with patch('argostranslate.translate.get_installed_languages', return_value=[]):
            with self.assertRaises(ValueError):
                translator.translate({'name': '新店'}, 'de')
        self.assertEqual(len(translator.warnings), 1)
        self.assertIn('de', translator.warnings[0])

    def test_nested_deletion_and_addition_match_ids_before_translation(self):
        source = {'spots': [{'id': 'c', 'name': '丙'}, {'id': 'new', 'name': '新店'}]}
        target = {'spots': [{'id': key, 'name': 'Translated ' + key} for key in ('a', 'b', 'c')]}
        translated = []
        def new_item(item):
            translated.append(item['id'])
            return dict(item, name='New cafe')
        admin.sync_node(source, target, new_item)
        self.assertEqual([item['name'] for item in target['spots']], ['Translated c', 'New cafe'])
        self.assertEqual(translated, ['new'])

    def test_new_reports_translate_and_deleted_reports_sync_without_touching_existing_editions(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / 'content/en'
            folder.mkdir(parents=True)
            original = {'id': 'keep', 'title': 'Existing English', 'language': 'en', 'status': 'draft', 'published': False}
            (folder / 'editorial_reports.json').write_text(json.dumps([original, dict(original, id='remove')]))
            source = [dict(original, title='已修改', language='zh'), dict(original, id='new', title='新店', language='zh')]
            translator = AddedContentTranslator(tmp, 'content/zh/editorial_reports.json')
            translator.tables['en'] = {'新店': 'New cafe'}
            with patch.object(admin, 'HERE', tmp), patch.object(admin, 'mirror_report_snapshot') as mirror:
                admin.sync_to_other_langs('content/zh/editorial_reports.json', source, translator)
            result = json.loads((folder / 'editorial_reports.json').read_text())
            self.assertEqual(result[0], original)
            self.assertEqual([r['id'] for r in result], ['keep', 'new'])
            self.assertEqual(result[1]['title'], 'New cafe')
            self.assertEqual(result[1]['language'], 'en')
            mirror.assert_called_once()
