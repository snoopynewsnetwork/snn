#!/usr/bin/env python3
"""Coordinator integration checks. First-wave scope is explicitly incomplete."""
import argparse
import contextlib
import datetime
import hashlib
import io
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'


def load(path):
    return json.loads((ROOT / path).read_text())


def verify(path, entry):
    data = path.read_bytes()
    assert len(data) == entry['bytes'] < 40000000, path
    assert hashlib.sha256(data).hexdigest() == entry['sha256'], path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--first-wave', action='store_true')
    args = parser.parse_args()
    for script in ['reconcile_counties.py', 'review_native_contract.py', 'review_targets.py', 'news/inspect_evidence.py']:
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(DATA / script), run_name='__main__')
    turnout = load('data/turnout/validation.json')
    assert turnout['status'] == 'pass' and len(turnout['checks']) == 37
    assert all(c['pass'] for c in turnout['checks'])
    assert (turnout['county_count'], turnout['native_identities'], turnout['detail_observations'], turnout['footer_observations']) == (105, 22031, 121053, 96)
    baseline = load('data/baselines/validation.json')
    assert baseline['status'] == 'pass_with_documented_source_gaps'
    assert len(baseline['checks']) == 12 and all(c['status'] == 'pass' for c in baseline['checks'])
    hashes = {}
    for folder, key, count in [('turnout', 'assets', 70), ('baselines', 'owned_assets', 57)]:
        manifest = load('data/'+folder+'/asset-manifest.json')
        entries = manifest[key]
        assert len(entries) == len({e['path'] for e in entries}) == count
        for entry in entries:
            verify(ROOT / entry['path'], entry)
        hashes[folder] = len(entries)
    acceptance = load('data/coordinator-priority-acceptance.json')
    assert acceptance['accepted'] is True
    body = (DATA / acceptance['contract']).read_bytes()
    contract_sha = hashlib.sha256(body).hexdigest()
    assert len(body) == acceptance['contract_bytes'] == 20297853
    assert contract_sha == acceptance['contract_sha256'] == 'dcdc1457a5b08851ef76b5372435d56788f647708da5ff9a6ef35435f92fa6a7'
    native = load('data/coordinator-native-contract-checks.json')
    assert native['input_hashes']['turnout/priority-set.json'] == contract_sha
    assert native['source_scoped_native_identities'] == 22031
    assert native['candidate_and_total_original_cells'] == 121053 and native['county_footer_original_cells'] == 96
    target = load('data/coordinator-target-review.json')
    assert target['status'] == 'pass' and target['county_scenarios'] == 22
    documents = [ROOT / p for p in ['turnout.md', 'county-partisanship.md',
                 'data/turnout/source/SCHEMA.md', 'data/baselines/source/SCHEMA.md']]
    links = 0
    for path in documents:
        for dest in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            dest = dest.strip().strip('<>')
            if not dest or dest.startswith(('http:', 'https:', '#', 'mailto:', 'data:')):
                continue
            assert (path.parent / unquote(dest.split('#')[0])).exists(), (path, dest)
            links += 1
    for folder in ['turnout', 'baselines']:
        for path in (DATA / folder).rglob('*'):
            assert path.name not in ['node_modules', '__pycache__', '.venv'], path
            if path.is_file():
                assert path.stat().st_size < 40000000 and path.suffix != '.pyc', path
    result = dict(status='pass', checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  scope='First-wave historical baselines/targets/native contract only; source/maps research and complete publication pending.',
                  counties=105, priority_counties=23, native_identities=22031,
                  original_detail_cells=121053, original_footer_positions=96,
                  state_scenarios=22, county_target_rows=2310, native_target_rows=44062,
                  additional_Sumner_method_targets=12, synthetic_fixed_counted_live_cases=15,
                  worker_asset_hashes=hashes, first_wave_relative_links=links,
                  priority_contract_sha256=contract_sha, implemented_collector=False,
                  calibrated_forecast=False, current_geography_approved=False)
    output = DATA / 'coordinator-first-wave-checks.json'
    if output.exists():
        previous = json.loads(output.read_text())
        if {k:v for k,v in previous.items() if k != 'checked_utc'} == {k:v for k,v in result.items() if k != 'checked_utc'}:
            result['checked_utc'] = previous['checked_utc']
    output.write_text(json.dumps(result, indent=2)+'\n')
    if args.first_wave:
        print(json.dumps(result, indent=2))
        return
    for script in ['review_maps.py', 'review_results.py']:
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(DATA / script), run_name='__main__')
    source = load('data/results-sources/validation.json')
    assert source['status'] == 'PASS' and source['check_count'] == 46
    assert all(c['pass'] for c in source['checks'])
    maps = load('maps/validation.json')
    assert maps['status'] == 'pass' and maps['checks_passed'] == 3677
    assert all(c['pass'] for c in maps['checks'])
    assert not load('data/coordinator-map-review.json')['mutable_source_metadata_mismatches_pending_final_peer_freeze']
    subprocess.run([sys.executable, '-S', str(DATA / 'results-sources/validate.py'), '--check-only'], check=True, capture_output=True)
    for folder, manifest_name, count in [('maps', 'asset-manifest.json', 699),
                                         ('data/results-sources', 'artifact-manifest.json', 1607)]:
        entries = load(folder + '/' + manifest_name)['assets']
        assert len(entries) == count
        for entry in entries:
            verify(ROOT / folder / entry['path'], entry)
        hashes[folder] = len(entries)
    # Every relative reference in the integrated prose and offline HTML must resolve.
    from html.parser import HTMLParser
    from urllib.parse import urlsplit
    class Links(HTMLParser):
        def __init__(self):
            super().__init__(); self.urls = []
        def handle_starttag(self, tag, attrs):
            self.urls.extend(v for k, v in attrs if k in ['href', 'src'] and v)
    all_links = 0
    for path in list(ROOT.rglob('*.md')) + list(ROOT.rglob('*.html')):
        if path.suffix == '.md':
            destinations = re.findall(r'\]\(([^)]+)\)', path.read_text())
        else:
            parser = Links(); parser.feed(path.read_text()); destinations = parser.urls
        for dest in destinations:
            dest = dest.strip().strip('<>'); parsed = urlsplit(dest)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = path.parent / unquote(parsed.path)
            # This report is emitted after these checks in the same successful run.
            assert target.exists() or target.resolve() == (DATA / 'coordinator-validation.json').resolve(), (path, dest)
            all_links += 1
    files = [p for p in ROOT.rglob('*') if p.is_file()]
    assert all(p.stat().st_size < 40000000 and p.suffix != '.pyc' for p in files)
    assert not any(p.name in ['__pycache__', 'node_modules', '.venv'] for p in ROOT.rglob('*'))
    complete = dict(status='pass_with_documented_source_gaps',
                    checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    counties=105, priority_counties=23, native_historical_identities=22031,
                    worker_asset_hashes=hashes, total_worker_asset_hashes=sum(hashes.values()),
                    integrated_relative_links=all_links, state_scenarios=22,
                    county_target_rows=2310, native_target_rows=44062,
                    additional_Sumner_method_targets=12, synthetic_live_cases=15,
                    official_requests=422, original_official_entities=417,
                    map_service_layers=12, map_shapefile_archives=2,
                    map_original_PDF_documents=23, map_original_PDF_pages=61,
                    priority_contract_sha256=contract_sha,
                    current_geography_approved=False, november_count_feed_approved=False,
                    exact_remaining_senate_votes_available=False,
                    collector_implemented=False, calibrated_forecast=False)
    final = DATA / 'coordinator-validation.json'
    if final.exists():
        previous = json.loads(final.read_text())
        if {k:v for k,v in previous.items() if k != 'checked_utc'} == {k:v for k,v in complete.items() if k != 'checked_utc'}:
            complete['checked_utc'] = previous['checked_utc']
    final.write_text(json.dumps(complete, indent=2)+'\n')
    print(json.dumps(complete, indent=2))


if __name__ == '__main__':
    main()
