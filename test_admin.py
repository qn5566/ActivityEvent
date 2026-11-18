import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import admin


class CafeSyncTests(unittest.TestCase):
    def setUp(self):
        self.source = [
            {"id": "a", "name": "甲店", "mapUrl": "https://maps.example/a"},
            {"id": "b", "name": "乙店", "mapUrl": "https://maps.example/b"},
            {"id": "c", "name": "丙店", "mapUrl": "https://maps.example/c"},
        ]
        self.target = [dict(cafe, name="Translated " + cafe["id"]) for cafe in self.source]

    def test_delete_middle_keeps_remaining_translations_with_correct_urls(self):
        source = [self.source[0], dict(self.source[2], mapUrl="https://maps.example/new-c")]
        result = admin.sync_cafes(source, self.target)
        self.assertEqual([c["id"] for c in result], ["a", "c"])
        self.assertEqual([c["name"] for c in result], ["Translated a", "Translated c"])
        self.assertEqual(result[1]["mapUrl"], source[1]["mapUrl"])

    def test_new_cafe_is_copied_and_existing_cafes_can_be_reordered(self):
        new = {"id": "d", "name": "新店", "tags": ["咖啡"], "links": []}
        result = admin.sync_cafes([self.source[2], new, self.source[0]], self.target)
        self.assertEqual([c["name"] for c in result], ["Translated c", "新店", "Translated a"])
        result[1]["tags"].append("甜點")
        self.assertEqual(new["tags"], ["咖啡"])

    def test_save_syncs_additions_deletions_and_empty_list_to_language_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for lang in ("zh", "en", "ja"):
                folder = root / "content" / lang
                folder.mkdir(parents=True)
                (folder / "cafes.json").write_text(json.dumps(self.target), encoding="utf-8")
            source = [copy.deepcopy(self.source[2]), {"id": "new", "name": "新店"}]
            with patch.object(admin, "HERE", tmp):
                synced = admin.sync_to_other_langs("content/zh/cafes.json", source)
                self.assertEqual(len(synced), 2)
                for rel in synced:
                    data = json.loads((root / rel).read_text())
                    self.assertEqual([c["id"] for c in data], ["c", "new"])
                    self.assertEqual(data[0]["name"], "Translated c")
                    self.assertEqual(data[1], source[1])
                admin.sync_to_other_langs("content/zh/cafes.json", [])
                for rel in synced:
                    self.assertEqual(json.loads((root / rel).read_text()), [])


class CafeArticleSyncTests(unittest.TestCase):
    def setUp(self):
        self.source = [
            {"id": "art_1", "cafeId": "cafe_1", "title": "文章一", "coverImg": "https://img.example/1"},
            {"id": "art_2", "cafeId": "cafe_2", "title": "文章二", "coverImg": "https://img.example/2"},
        ]
        self.target = [dict(art, title="Translated " + art["id"]) for art in self.source]

    def test_sync_cafe_articles_preserves_translation_and_updates_images(self):
        source = [dict(self.source[0], coverImg="https://img.example/updated")]
        result = admin.sync_cafe_articles(source, self.target)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "art_1")
        self.assertEqual(result[0]["title"], "Translated art_1")
        self.assertEqual(result[0]["coverImg"], "https://img.example/updated")

    def test_menu_html_stays_independent_in_each_language(self):
        source = [dict(self.source[0], menuHtml="<table><tr><td>中文菜單</td></tr></table>")]
        target = [dict(self.target[0], menuHtml="<table><tr><td>English menu</td></tr></table>")]
        result = admin.sync_cafe_articles(source, target)
        self.assertEqual(result[0]["menuHtml"], target[0]["menuHtml"])
        result = admin.sync_cafe_articles(source, [dict(self.target[0], menuHtml="")])
        self.assertEqual(result[0]["menuHtml"], "")


if __name__ == "__main__":
    unittest.main()
