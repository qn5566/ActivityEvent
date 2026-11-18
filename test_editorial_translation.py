"""Existing translation jobs must preserve the separately managed report editions."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import content_translate as ct


class EditorialTranslationTest(unittest.TestCase):
    def test_standard_translation_does_not_overwrite_report_editions(self):
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory)
            (content / 'zh').mkdir()
            (content / 'en').mkdir()
            (content / 'zh/blog.json').write_text('{}')
            (content / 'zh/editorial_reports.json').write_text('[{"title":"中文草稿"}]')
            target = content / 'en/editorial_reports.json'
            original = '[{"title":"Original English draft","status":"draft"}]\n'
            target.write_text(original)
            with patch.object(ct, 'SOURCE_DIR', content / 'zh'), \
                 patch.object(ct, 'CONTENT_DIR', content), \
                 patch.object(ct, 'load_translations', return_value=({}, None)), \
                 patch.object(ct, 'log'):
                self.assertTrue(ct.build_language('en'))
            self.assertEqual(target.read_text(), original)
            self.assertEqual(json.loads((content / 'en/blog.json').read_text()), {})


if __name__ == '__main__':
    unittest.main()
