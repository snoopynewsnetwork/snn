"""One bounded dated newsroom recheck; append observations without replacing originals."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip, hashlib, json, re
import requests

ROOT = Path(__file__).resolve().parent
OBSERVATION = 'coordinator-oct19-2026'
SOURCES = {
    'wowt-results': 'https://www.wowt.com/politics/election-results/',
    'wowt-nebraska': 'https://www.wowt.com/nebraska-election-results/',
    'koln-results': 'https://www.1011now.com/politics/election-results/',
    'knop-results': 'https://www.knopnews2.com/politics/election-results/',
    'ketv-primary': 'https://www.ketv.com/article/nebraska-primary-election-results-2026/71151712',
    'nyt-elections': 'https://www.nytimes.com/section/politics/elections',
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fetch(item):
    source, url = item
    row = dict(id=source + '-' + OBSERVATION, url=url, requested_url=url, method='GET', retrieved_at_utc=datetime.now(timezone.utc).isoformat(), bounded_current_recheck_of=source)
    try:
        r = requests.get(url, timeout=35)
        b = r.content
        p = ROOT / (row['id'] + '.html.gz')
        assert not p.exists()
        p.write_bytes(gzip.compress(b, mtime=0))
        row.update(status=r.status_code, final_url=r.url, headers=dict(r.headers), redirect_chain=[dict(url=x.url, status=x.status_code, headers=dict(x.headers)) for x in r.history], asset=p.name, raw_sha256=sha(b), stored_sha256=sha(p.read_bytes()), bytes=len(b), stored_bytes=p.stat().st_size, body_representation='Complete requests response.content entity bytes after HTTP Content-Encoding decoding; headers preserve encoded wire lengths/encoding separately, gzip is lossless storage.')
    except requests.RequestException as e:
        row.update(error=str(e), status=0, final_url=None)
    return row


def main():
    mp = ROOT / 'manifest.json'
    before = mp.read_bytes()
    old = json.loads(before)
    ids = {r['id'] for r in old}
    assert len(ids) == len(old)
    todo = [(k, u) for k, u in SOURCES.items() if k + '-' + OBSERVATION not in ids]
    rows = list(ThreadPoolExecutor(max_workers=4).map(fetch, todo))
    body_index = {r['raw_sha256']: r for r in old if 'asset' in r}
    for row in rows:
        if 'asset' not in row:
            continue
        if row['raw_sha256'] in body_index:
            prior = body_index[row['raw_sha256']]
            assert (ROOT / prior['asset']).read_bytes() == (ROOT / row['asset']).read_bytes()
            (ROOT / row['asset']).unlink()
            row.update(asset=prior['asset'], stored_sha256=prior['stored_sha256'], storage_reuse_source_id=prior['id'], identical_complete_original_reused=True)
        else:
            body_index[row['raw_sha256']] = row
    if rows:
        assert mp.read_bytes() == before
        temporary = mp.with_suffix('.refresh.tmp')
        temporary.write_text(json.dumps(old + rows, indent=2) + '\n')
        temporary.replace(mp)
    manifest = json.loads(mp.read_bytes())
    assert manifest[:len(old)] == old
    observations = []
    for source, url in SOURCES.items():
        row = next(r for r in manifest if r['id'] == source + '-' + OBSERVATION)
        finding = dict(id=row['id'], url=url, retrieval_UTC=row['retrieved_at_utc'], HTTP_status=row['status'], admitted_November_Senate_counts=False)
        if 'asset' in row:
            z = (ROOT / row['asset']).read_bytes()
            raw = gzip.decompress(z)
            assert sha(z) == row['stored_sha256'] and sha(raw) == row['raw_sha256']
            text = raw.decode(errors='replace')
            finding.update(original_asset=row['asset'], complete_entity_bytes=len(raw), raw_sha256=sha(raw), selectedElection_literals=sorted(set(re.findall(r'"selectedElection":(\{[^}]*\})', text))), displayTestData_literals=sorted(set(re.findall(r'"displayTestData":(true|false)', text))), older_chancery_label_present='MS Chancery Court Judicial Races' in text, body_contains_challenge_marker=bool(re.search(r'access denied|captcha|perimeterx|cf-chl|datadome', text, re.I)))
        observations.append(finding)
    result = dict(scope='One bounded October19 coordinator observation per actual regional/national results page, separate from earlier entity captures and web-reader observations.', previous_captures=len(manifest)-len(rows), newly_appended_captures=len(rows), total_captures=len(manifest), observations=observations, qualification='Raw public page observations only; selected election/test flags and HTTP responses are retained literally. No genuine November source counts, contestIDs, update cadence or current-unit compatibility inferred. Identical complete entities reused once, old receipt rows unchanged.')
    p = ROOT / 'current-results-recheck-oct19.json'
    b = (json.dumps(result, indent=2) + '\n').encode()
    if p.exists():
        prior = json.loads(p.read_bytes())
        assert prior['observations'] == observations and prior['total_captures'] == len(manifest)
    else:
        p.write_bytes(b)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
