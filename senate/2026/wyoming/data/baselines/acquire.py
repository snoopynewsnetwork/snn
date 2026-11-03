#!/usr/bin/env python3
"""Download the official Wyoming evidence used by the partisanship baselines.

Every response body is kept losslessly as gzip (mtime=0) under raw/, and
sources.json records the request URL, final URL, UTC retrieval time, HTTP
status, selected response headers, original and stored SHA-256/bytes.
Cookies are never stored.  A non-200 response is retained as evidence of the
attempt (for example the not-yet-published 2026 general-results page).

Usage (network):      uv run python3 -I acquire.py
Usage (offline check): uv run python3 -I acquire.py --verify-only
Standard library only.
"""
import argparse, datetime, gzip, hashlib, json, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'raw'
UA = 'Mozilla/5.0 (snn election-night research; county partisanship baselines)'
SOS = 'https://sos.wyo.gov/Elections'
GEN = SOS + '/Docs/{y}/Results/General/'
SOURCES = [
    # id, url, role
    ('sos-results-index', SOS + '/ElectionResults.aspx', 'SOS election-results index linking each year'),
    ('sos-2020-general-page', SOS + '/Docs/2020/2020GeneralResults.aspx', '2020 general results landing page (links zip and PDFs)'),
    ('sos-2022-general-page', SOS + '/Docs/2022/2022GeneralResults.aspx', '2022 general results landing page'),
    ('sos-2024-general-page', SOS + '/Docs/2024/2024GeneralResults.aspx', '2024 general results landing page'),
    ('sos-2020-general-zip', GEN.format(y=2020) + '2020_Wyoming_General_Results.zip', '2020 official XLSX summaries and county precinct-by-precinct workbooks'),
    ('sos-2022-general-zip', GEN.format(y=2022) + '2022_Wyoming_General_Results.zip', '2022 official XLSX summaries and precinct-by-precinct workbooks'),
    ('sos-2024-general-zip', GEN.format(y=2024) + '2024_Wyoming_General_Results.zip', '2024 official XLSX summaries and precinct-by-precinct workbooks'),
    ('sos-2020-statewide-candidates-pdf', GEN.format(y=2020) + '2020_General_Statewide_Candidates_Summary.pdf', '2020 Statewide Candidates Official Summary (PDF cross-check)'),
    ('sos-2022-statewide-candidates-pdf', GEN.format(y=2022) + '2022_General_Statewide_Candidates_Summary.pdf', '2022 Statewide Candidates Official Summary (PDF cross-check)'),
    ('sos-2024-statewide-candidates-pdf', GEN.format(y=2024) + '2024_General_Statewide_Candidates_Summary.pdf', '2024 Statewide Candidates Official Summary (PDF cross-check)'),
    ('sos-2020-total-ballots-pdf', GEN.format(y=2020) + '2020_General_Statewide_Total_Ballots_Cast_Summary.pdf', '2020 county total ballots cast (PDF cross-check)'),
    ('sos-2022-total-ballots-pdf', GEN.format(y=2022) + '2022_General_Statewide_Total_Ballots_Cast_Summary.pdf', '2022 county total ballots cast (PDF cross-check)'),
    ('sos-2024-total-ballots-pdf', GEN.format(y=2024) + '2024_General_Statewide_Total_Ballots_Cast_Summary.pdf', '2024 county total ballots cast (PDF cross-check)'),
    ('sos-2024-state-canvass-minutes', GEN.format(y=2024) + '2024_General_State_Canvassing_Board_Minutes.pdf', '2024 State Canvassing Board minutes and certification (scanned)'),
    ('sos-2026-election-info-page', SOS + '/2026ElectionInformation.aspx', '2026 election information page (links candidate rosters)'),
    ('sos-2026-general-candidates-csv', SOS + '/Docs/2026/2026_WY_General_Election_Candidates.csv', '2026 general election candidate roster (CSV)'),
    ('sos-2026-general-candidates-pdf', SOS + '/Docs/2026/2026_WY_General_Election_Candidates.pdf', '2026 general election candidate roster (PDF)'),
    ('sos-2026-primary-candidates-csv', SOS + '/Docs/2026/2026_WY_Primary_Election_Candidates.csv', '2026 primary candidate roster (CSV)'),
    ('sos-2026-withdrawn-primary-pdf', SOS + '/Docs/2026/2026_WY_Withdrawn_Primary_Election_Candidates.pdf', '2026 withdrawn primary candidates'),
    ('sos-2026-withdrawn-general-pdf', SOS + '/Docs/2026/2026_WY_Withdrawn_General_Election_Candidates.pdf', '2026 withdrawn general candidates (link present on info page)'),
    ('sos-2026-independent-candidates-page', SOS + '/IndependentCandidates.aspx', 'Independent candidate petition status page'),
    ('sos-2026-key-dates-pdf', SOS + '/Docs/2026/2026_Key_Election_Dates.pdf', '2026 key election dates'),
    ('sos-2026-primary-page', SOS + '/Docs/2026/2026PrimaryResults.aspx', '2026 primary results landing page'),
    ('sos-2026-primary-zip', SOS + '/Docs/2026/Results/Primary/2026_Wyoming_Primary_Results.zip', '2026 primary official XLSX summaries'),
    ('sos-2026-primary-statewide-candidates-pdf', SOS + '/Docs/2026/Results/Primary/2026_Statewide_Candidates_Summary.pdf', '2026 primary statewide candidates summary (PDF)'),
    ('sos-2026-general-page', SOS + '/Docs/2026/2026GeneralResults.aspx', '2026 general results page (expected unpublished before 2026-11-03)'),
    ('wyoleg-title22-pdf', 'https://wyoleg.gov/statutes/compress/title22.pdf', 'Wyoming Statutes Title 22 (Elections): W.S. 22-2-117, 22-16-105, 22-16-109'),
    ('census-wy-county-codes', 'https://www2.census.gov/geo/docs/reference/codes2020/cou/st56_wy_cou2020.txt', 'Census 2020 county FIPS reference for Wyoming'),
]
KEEP_HEADERS = ['content-type', 'content-length', 'last-modified', 'etag', 'date', 'server', 'location']
EXT = {'application/pdf': '.pdf', 'text/html': '.html', 'text/plain': '.txt'}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def ext_for(url, ctype):
    tail = url.rsplit('/', 1)[-1].lower()
    for e in ('.zip', '.pdf', '.csv', '.txt', '.aspx'):
        if tail.endswith(e):
            return '.html' if e == '.aspx' else e
    return EXT.get((ctype or '').split(';')[0].strip(), '.bin')

def fetch(sid, url, role):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    started = datetime.datetime.now(datetime.timezone.utc)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body, status, final, headers = resp.read(), resp.status, resp.geturl(), resp.headers
    except urllib.error.HTTPError as e:
        body, status, final, headers = e.read(), e.code, url, e.headers
    hdr = {k: headers.get(k) for k in KEEP_HEADERS if headers.get(k) is not None}
    ext = ext_for(url, hdr.get('content-type')) if status == 200 else '.html'
    path = f'raw/{sid}{ext}.gz'
    stored = gzip.compress(body, compresslevel=9, mtime=0)
    assert len(stored) < 40_000_000, sid
    (ROOT / path).write_bytes(stored)
    return {'id': sid, 'role': role, 'requested_url': url, 'final_url': final,
            'retrieval_utc': started.isoformat(timespec='seconds'), 'http_status': status,
            'headers': hdr, 'original_sha256': sha(body), 'original_bytes': len(body),
            'path': path, 'stored_sha256': sha(stored), 'stored_bytes': len(stored),
            'stored_encoding': 'gzip(mtime=0) of the exact response body'}

def verify():
    meta = json.loads((ROOT / 'sources.json').read_text())
    for m in meta:
        stored = (ROOT / m['path']).read_bytes()
        assert sha(stored) == m['stored_sha256'] and len(stored) == m['stored_bytes'], m['id']
        body = gzip.decompress(stored)
        assert sha(body) == m['original_sha256'] and len(body) == m['original_bytes'], m['id']
    print('verified', len(meta), 'retained source bodies; no network request')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verify-only', action='store_true')
    args = ap.parse_args()
    if args.verify_only:
        return verify()
    RAW.mkdir(exist_ok=True)
    out = []
    for sid, url, role in SOURCES:
        rec = fetch(sid, url, role)
        print(rec['http_status'], rec['original_bytes'], sid, file=sys.stderr)
        out.append(rec)
    (ROOT / 'sources.json').write_text(json.dumps(out, indent=2) + '\n')
    verify()

if __name__ == '__main__':
    main()
