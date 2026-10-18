#!/usr/bin/env python3
"""Read-only package checks; only the coordinator's final result is written."""
from pathlib import Path
import ast
import datetime
import gzip
import hashlib
from html.parser import HTMLParser
import json
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
load = lambda p: json.loads((ROOT / p).read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
def verify(p, item):
    b = p.read_bytes()
    assert len(b) == item['bytes'] < 40_000_000 and sha(b) == item['sha256'], p

worker_assets = {}
for file, key, expected in [
    ('data/turnout/asset-manifest.json', 'owned_assets', 1720),
    ('data/baselines/asset-manifest.json', 'assets', 77),
    ('data/results-sources/asset-manifest.json', 'owned', 1289),
    ('maps/manifest.json', 'artifacts', 846),
]:
    entries = load(file)[key]
    assert len(entries) == len({r['path'] for r in entries}) == expected
    for r in entries:
        verify(ROOT / r['path'], r)
    worker_assets[file] = {'assets': len(entries), 'manifest_sha256': sha((ROOT / file).read_bytes())}
for r in load('data/results-sources/frozen-inputs.json'):
    verify(ROOT / r['path'], r)
for path, r in load('maps/manifest.json')['read_only_inputs'].items():
    verify(ROOT / path, r)
news = load('data/news/manifest.json')
for r in news:
    if 'asset' not in r:
        continue
    b = (ROOT / 'data/news' / r['asset']).read_bytes()
    assert sha(b) == r['stored_sha256']
    assert sha(gzip.decompress(b)) == r['raw_sha256']
accept = load('data/coordinator-priority-acceptance.json')
assert accept['accepted']
contract = (ROOT / 'data/turnout/priority-set.json').read_bytes()
assert sha(contract) == accept['contract_sha256'] == '1f589d2785d985af2eb33de50adad5a398924ab55f9343deaf79ac5c7378d97a'
assert len(contract) == accept['contract_bytes'] == 2293339
assert len(json.loads(contract)['coverage']) == 159

reviews = {
    'native': load('data/coordinator-native-contract-review.json'),
    'baseline': load('data/coordinator-baseline-source-review.json'),
    'targets': load('data/coordinator-target-review.json'),
    'maps': load('data/coordinator-map-review.json'),
    'official': load('data/coordinator-results-review.json'),
}
assert all(str(v['status']).startswith('pass') for v in reviews.values())
assert (reviews['targets']['state_scenarios'], reviews['targets']['county_targets'],
        reviews['targets']['native_targets'], reviews['targets']['method_targets']) == (50, 7950, 5402, 27968)
assert reviews['maps']['binary_archive']['records'] == 2724
assert reviews['maps']['binary_archive']['vertices'] == 1775333
assert reviews['maps']['priority_selected_shapes'] == 1934
assert reviews['official']['source_positions'] == 76400
assert reviews['official']['official_report_sha256'] == sha((ROOT / 'official-results.md').read_bytes())
assert reviews['official']['official_manifest_sha256'] == worker_assets['data/results-sources/asset-manifest.json']['manifest_sha256']
subprocess.run([sys.executable, '-S', str(ROOT / 'data/results-sources/scripts/validate.py'), '--manifest-only'],
               capture_output=True, check=True)

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        self.urls.extend(v for k, v in attrs if k in ['src', 'href'] and v)

links = 0
for p in [*ROOT.rglob('*.md'), *ROOT.rglob('*.html')]:
    if p.suffix == '.md':
        urls = re.findall(r'\]\(([^)]+)\)', p.read_text())
    else:
        parser = Links()
        parser.feed(p.read_text())
        urls = parser.urls
    for u in urls:
        u = u.strip().strip('<>')
        parsed = urlsplit(u)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        target = p.parent / unquote(parsed.path)
        assert target.exists() or target.resolve() == (ROOT / 'data/coordinator-validation.json').resolve(), (p, u)
        links += 1
files = [p for p in ROOT.rglob('*') if p.is_file()]
assert all(p.stat().st_size < 40_000_000 and p.suffix != '.pyc' for p in files)
assert not any(p.name in ['__pycache__', 'node_modules', '.venv'] for p in ROOT.rglob('*'))
for p in ROOT.rglob('*.py'):
    ast.parse(p.read_text(), filename=str(p))
out = {
    'status': 'pass_with_explicit_source_and_current_admission_gaps',
    'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'counties': 159, 'priority_counties': 44, 'native_identities': 2701,
    'priority_native_identities': 1938, 'remainder_native_identities': 763,
    'full_valid_2024_presidential_votes': 5250905, 'unallocated_qualified_writeins': 858,
    'priority_membership_proved': True, 'full_candidate_internal_order_known': False,
    'historical_election_stages': 5, 'county_election_controls': 795,
    'original_candidate_method_positions': 76400, 'candidate_nulls': 40, 'method_nulls': 22416,
    'state_scenarios': 50, 'county_targets': 7950, 'native_targets': 5402, 'method_targets': 27968,
    'synthetic_fixed_counted_cases': 13, 'official_http_receipts': 417,
    'historical_exports': 6, 'current_count_admissions': 0,
    'state_map_records': 2724, 'state_map_vertices': 1775333,
    'unassigned_state_shapes': 27, 'priority_state_map_records': 1934,
    'complete_county_GIS_snapshots': 12, 'county_GIS_features': 1044,
    'map_original_PDFs': 30, 'map_original_PDF_pages': 152,
    'worker_assets': worker_assets, 'total_worker_asset_hashes': sum(x['assets'] for x in worker_assets.values()),
    'news_captures': len(news), 'local_links': links, 'stored_files': len(files),
    'largest_stored_object': max(p.stat().st_size for p in files),
    'priority_contract_sha256': sha(contract),
    'collector_implemented': False, 'current_geographic_crosswalk_approved': False,
    'november_feed_approved': False, 'exact_remaining_senate_votes_available': False,
    'calibrated_forecast': False,
}
(ROOT / 'data/coordinator-validation.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
