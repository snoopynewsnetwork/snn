"""Bounded official map authority discovery; not a completed map assignment."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import gzip
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
OUT = HERE / 'map-preflight'
URLS = {
    'rfa-mapping': 'https://rfa.sc.gov/resources/mapping',
    'rfa-jurisdictional': 'https://www.rfa.sc.gov/resources/mapping/jurisdictional-maps',
    'rfa-precincts': 'https://www.rfa.sc.gov/resources/mapping/jurisdictional-maps/sc-voting-precincts',
    'rfa-gis-hub': 'https://gis-rfa.hub.arcgis.com/pages/districts',
    'rfa-district-app-parent': 'https://rfa.sc.gov/resources/mapping/jurisdictional-maps/district-information',
}

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.href = None
        self.label = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self.href = attrs.get('href')
            self.label = []
        if tag == 'iframe':
            self.rows.append({'kind': 'iframe', 'target': attrs.get('src'), 'label': attrs.get('title')})
    def handle_data(self, text):
        if self.href is not None:
            self.label.append(text)
    def handle_endtag(self, tag):
        if tag == 'a' and self.href is not None:
            self.rows.append({'kind': 'anchor', 'target': self.href, 'label': ' '.join(''.join(self.label).split())})
            self.href = None

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    spec = importlib.util.spec_from_file_location('capture', HERE / 'news/fetch_evidence.py')
    capture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(capture)
    capture.ROOT = OUT
    manifest = OUT / 'manifest.json'
    receipts = json.loads(manifest.read_text()) if manifest.exists() else []
    existing = {row['id'] for row in receipts}
    receipts.extend(capture.fetch(item) for item in URLS.items() if item[0] not in existing)
    for row in receipts:
        if 'asset' in row:
            stored = (OUT / row['asset']).read_bytes()
            assert hashlib.sha256(stored).hexdigest() == row['stored_sha256']
            assert hashlib.sha256(gzip.decompress(stored)).hexdigest() == row['raw_sha256']
    discoveries = []
    for row in receipts:
        if row.get('status') != 200 or 'asset' not in row:
            continue
        parser = Links()
        parser.feed(gzip.decompress((OUT / row['asset']).read_bytes()).decode(errors='replace'))
        for link in parser.rows:
            if link['target']:
                link['target'] = urljoin(row['final_url'], link['target'])
                discoveries.append({'parent_source': row['id'], **link})
    manifest.write_text(json.dumps(receipts, indent=2) + '\n')
    (OUT / 'observed-links.json').write_text(json.dumps(discoveries, indent=2) + '\n')
    print(json.dumps({'observations': [(r['id'], r.get('status')) for r in receipts], 'links': len(discoveries)}, indent=2))
