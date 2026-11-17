#!/usr/bin/env python3
"""Align existing content URLs with affiliate_config.json, keeping destinations.

Defaults to preview. Run --apply to update JSON/CSV and legacy links.json.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

from admin import detect_format, dump_json
from update_links import discover_files
from affiliate_config import validate_config

ROOT = Path(__file__).resolve().parent
URL_PATTERN = re.compile(r'https?://[^\s<>"\']+')


def normalize_url(raw, config):
    escaped = '&amp;' in raw
    url = raw.replace('&amp;', '&')
    parsed = urlsplit(url)
    host = (parsed.hostname or '').lower()
    query = parse_qsl(parsed.query, keep_blank_values=True)
    params = dict(query)
    replacements = {}
    if host == 'trip.com' or host.endswith('.trip.com'):
        replacements = config['tracking']['trip']
    elif host in {'klook.com', 'www.klook.com', 'affiliate.klook.com'}:
        replacements = {'aid': config['tracking']['klookAid']}
        if host == 'affiliate.klook.com' and 'k_site' in params:
            replacements['k_site'] = normalize_url(params['k_site'], config)
    else:
        for platform in config['platforms'].values():
            canonical = urlsplit(platform['url'])
            # Match full partner campaign paths, never guess a replacement
            # from a domain that may contain several unrelated campaigns.
            if host == canonical.hostname and parsed.path == canonical.path:
                return platform['url'].replace('&', '&amp;') if escaped else platform['url']
        return raw
    keys = {key.lower() for key in replacements}
    query = [(key, value) for key, value in query if key.lower() not in keys]
    query.extend(replacements.items())
    result = urlunsplit(parsed._replace(
        path=quote(parsed.path, safe="/:@!$&'()*+,;=-._~%"), query=urlencode(query)))
    return result.replace('&', '&amp;') if escaped else result


def rewrite(value, config):
    if isinstance(value, dict):
        return {key: rewrite(item, config) for key, item in value.items()}
    if isinstance(value, list):
        return [rewrite(item, config) for item in value]
    if isinstance(value, str):
        if value.startswith(('https://', 'http://')) and value.count('https://') + value.count('http://') == 1 and not any(char in value for char in '<>\n"'):
            return normalize_url(value, config)
        return URL_PATTERN.sub(lambda match: normalize_url(match[0], config), value)
    return value


def migrate(apply=False):
    config = json.loads((ROOT / 'affiliate_config.json').read_text())
    validate_config(config)
    changed = []
    for filename in discover_files():
        path = Path(filename)
        raw = path.read_text(encoding='utf-8')
        if path.suffix == '.json':
            data = json.loads(raw)
            updated = rewrite(data, config)
            if updated == data:
                continue
            minified, indent = detect_format(raw)
            output = dump_json(updated, minified, indent) + '\n'
        else:
            output = URL_PATTERN.sub(lambda match: normalize_url(match[0], config), raw)
            if output == raw:
                continue
        changed.append(str(path.relative_to(ROOT)))
        if apply:
            path.write_text(output, encoding='utf-8')
    path = ROOT / 'links.json'
    legacy = json.loads(path.read_text())
    updated = dict(legacy, klook_aid=config['tracking']['klookAid'],
                   klook_charter_aid=config['tracking']['klookAid'],
                   trip_allianceid=config['tracking']['trip']['Allianceid'],
                   trip_sid=config['tracking']['trip']['SID'],
                   trip_sub3=config['tracking']['trip']['trip_sub3'],
                   trip_flight_sub3=config['tracking']['trip']['trip_sub3'])
    if updated != legacy:
        changed.append('links.json')
        if apply:
            path.write_text(json.dumps(updated, ensure_ascii=False, indent=4) + '\n')
    print(('Updated' if apply else 'Preview') + ': %d files' % len(changed))
    for filename in changed:
        print('  ' + filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Write changes (default: preview only)')
    migrate(parser.parse_args().apply)
