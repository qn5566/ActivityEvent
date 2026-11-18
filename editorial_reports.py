"""Validation and plain-text fallback for the editable report document format."""
from urllib.parse import urlparse

TAGS = {'p', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'strong', 'em', 's',
        'code', 'blockquote', 'br', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'a'}


def validate_url(value):
    if value and (not isinstance(value, str) or urlparse(value).scheme not in ('http', 'https')
                  or not urlparse(value).netloc):
        raise ValueError('圖片與地圖網址必須是完整的 HTTP(S) 網址')


def validate_blocks(blocks, depth=0):
    if not isinstance(blocks, list) or depth > 32:
        raise ValueError('段落結構必須是陣列，且不可巢狀超過 32 層')
    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError('段落節點必須是物件')
        if 'text' in block:
            if not isinstance(block['text'], str) or 'tag' in block:
                raise ValueError('文字節點格式錯誤')
        else:
            if block.get('tag') not in TAGS:
                raise ValueError('不支援的段落標籤：%s' % block.get('tag'))
            if block['tag'] == 'a':
                validate_url(block.get('href'))
            if 'start' in block and (type(block['start']) is not int or block['start'] < 1):
                raise ValueError('清單起始編號必須是正整數')
            validate_blocks(block.get('children', []), depth + 1)


def plain(blocks):
    result = ''
    for block in blocks:
        if 'text' in block:
            result += block['text']
        else:
            result += plain(block.get('children', []))
            if block['tag'] in ('p', 'h3', 'h4', 'li', 'tr', 'blockquote', 'br', 'hr'):
                result += '\n'
            elif block['tag'] in ('th', 'td'):
                result += ' | '
    return result


def prepare_reports(data, language):
    """Validate before any write; keep metadata and regenerate content from blocks."""
    if not isinstance(data, list):
        raise ValueError('報導資料必須是陣列')
    ids, slugs = set(), set()
    for report in data:
        if not isinstance(report, dict):
            raise ValueError('每篇報導必須是物件')
        for key in ('id', 'title'):
            if not isinstance(report.get(key), str) or not report[key].strip():
                raise ValueError('報導 ID 與標題不可空白')
        if report['id'] in ids:
            raise ValueError('報導 ID 不可重複')
        ids.add(report['id'])
        slug = report.get('slug', '')
        if not isinstance(slug, str) or (slug and slug in slugs):
            raise ValueError('報導 slug 必須是文字且不可重複')
        if slug:
            slugs.add(slug)
        if report.get('status') not in ('draft', 'published', 'archived'):
            raise ValueError('發布狀態必須為 draft、published 或 archived')
        if type(report.get('published')) is not bool or report['published'] != (report['status'] == 'published'):
            raise ValueError('發布開關與狀態不一致')
        if report.get('language', language) != language:
            raise ValueError('報導語言與目前資料夾不一致')
        for key in ('summary', 'city', 'area', 'date', 'author', 'editorialNote'):
            if key in report and not isinstance(report[key], str):
                raise ValueError('%s 必須是文字' % key)
        validate_url(report.get('coverImg'))
        sections = report.get('sections', [])
        if not isinstance(sections, list):
            raise ValueError('報導段落必須是陣列')
        for section in sections:
            if not isinstance(section, dict):
                raise ValueError('每個段落必須是物件')
            for key in ('heading', 'content', 'caption'):
                if key in section and not isinstance(section[key], str):
                    raise ValueError('段落的 %s 必須是文字' % key)
            validate_url(section.get('image'))
            if 'blocks' in section:
                validate_blocks(section['blocks'])
                section['content'] = plain(section['blocks']).strip()
        for key in ('photos', 'nearby'):
            if not isinstance(report.get(key, []), list):
                raise ValueError('%s 必須是陣列' % key)
            for item in report.get(key, []):
                if not isinstance(item, dict):
                    raise ValueError('%s 項目必須是物件' % key)
                validate_url(item.get('image'))
                validate_url(item.get('mapUrl'))
        if not isinstance(report.get('practicalInfo', {}), dict):
            raise ValueError('探訪資訊必須是物件')
        validate_url(report.get('practicalInfo', {}).get('mapUrl'))
    return data
