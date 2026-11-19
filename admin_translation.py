"""Translate newly added admin content without rebuilding existing locale editions."""
import copy
import json
import re
from pathlib import Path

from content_translate import FILE_FIELDS, extract_html_texts, translate_html

ARGOS_CODES = {'fil': 'tl'}
ARTICLE_FIELDS = {
    'title', 'subtitle', 'summary', 'author', 'readTime', 'category', 'city',
    'area', 'audience', 'editorialNote', 'description', 'keywords', 'heading',
    'content', 'caption', 'text', 'name', 'address', 'hours', 'transport',
    'signature', 'quickFacts', 'note', 'dressCode', 'reservation',
    'businessHours', 'minOrder', 'nearestMrt', 'recommendedStay', 'wifiAndPower',
    'attribution', 'menuNote',
}
ARTICLE_FILES = {'cafe_articles.json', 'editorial_reports.json', 'michelin_articles.json'}
HTML_FIELDS = {'fullHtmlArticle', 'menuHtml'}


class AddedContentTranslator:
    def __init__(self, root, rel):
        self.root = Path(root)
        parts = rel.split('/')
        self.source = parts[1] if len(parts) == 3 and parts[0] == 'content' else None
        self.filename = parts[-1]
        self.tables = {}
        self.engines = {}
        self.cache = {}
        self.warnings = []
        self.failures = 0

    def warn(self, language, error):
        self.failures += 1
        message = '%s 新增文字翻譯失敗：%s' % (language, error)
        if message not in self.warnings:
            self.warnings.append(message)

    def text(self, value, language):
        if not value.strip() or value.startswith(('http://', 'https://')):
            return value
        if self.source == 'zh' and not re.search(r'[\u3400-\u9fff]', value):
            return value
        key = (language, value)
        if key in self.cache:
            return self.cache[key]
        try:
            if language not in self.tables:
                path = self.root / 'content' / '_translations' / (language + '.json')
                self.tables[language] = json.loads(path.read_text(encoding='utf-8')) if self.source == 'zh' and path.exists() else {}
            translated = self.tables[language].get(value)
            if not translated:
                if language not in self.engines:
                    import argostranslate.translate
                    installed = {item.code: item for item in argostranslate.translate.get_installed_languages()}
                    source = installed.get(ARGOS_CODES.get(self.source, self.source))
                    target = installed.get(ARGOS_CODES.get(language, language))
                    if source is None or target is None:
                        raise ValueError('缺少 %s → %s 離線語言模型' % (self.source, language))
                    self.engines[language] = source.get_translation(target)
                engine = self.engines[language]
                if engine is None:
                    raise ValueError('缺少可用的翻譯路徑')
                translated = engine.translate(value)
                if not translated or translated == value:
                    raise ValueError('翻譯引擎未產生譯文')
            self.cache[key] = translated
            return translated
        except Exception as exc:
            self.warn(language, str(exc))
            return value

    def translate(self, item, language):
        failures_before = self.failures
        fields = set(FILE_FIELDS.get(self.filename, ()))
        if self.filename in ARTICLE_FILES:
            fields.update(ARTICLE_FIELDS)
            fields.update(HTML_FIELDS)

        def visit(node, key=None):
            if isinstance(node, dict):
                # Native menu editions already contain their own language variants.
                return {k: copy.deepcopy(v) if k == 'menuVariants' else visit(v, k) for k, v in node.items()}
            if isinstance(node, list):
                return [visit(child, key) for child in node]
            if isinstance(node, str) and key in fields:
                if key in HTML_FIELDS:
                    table = {text.strip(): self.text(text.strip(), language)
                             for text in extract_html_texts(node)}
                    return translate_html(node, table)
                return self.text(node, language)
            return copy.deepcopy(node)

        result = visit(item)
        if self.failures != failures_before:
            raise ValueError("新增內容翻譯未完成，請修正翻譯環境後重新存檔")
        if self.filename in ('editorial_reports.json', 'michelin_articles.json') and isinstance(result, dict):
            result['language'] = language
        return result
