#!/usr/bin/env python3
"""Acquire Oklahoma turnout evidence from official public channels.

Writes only inside this directory: raw/ (original bytes, gzip-compressed for
text types) and source-manifest.json (URL, request, redirects, HTTP status and
headers, UTC retrieval time, original/stored SHA-256 and byte counts).

Channels fetched by this script (public pages, no sign-in of any kind):
  * oklahoma.gov State Election Board (OSEB) results landing pages, which link
    the OKER results application for each election date, and the public OKER
    app page and static configuration file those links lead to.
  * OSEB official pre-election (November 1) county registration PDFs for
    2024/2022/2020, located through the registration-statistics archive page.
  * OSEB Interactive Statistics (EIS, stats.okelections.us -> .gov): voter
    history credit by county and voter registration totals by status, through
    the dashboard's own item-data endpoint with an explicit master filter.
  * Census 2020 county codes; NARA 2024 certificate of ascertainment; U.S.
    House Clerk 2022/2020 election statistics (certified statewide controls).

OKER export records (ids "oker-YYYYMMDD-*": race/county/precinct CSV exports
and the app's election and county-results JSON) are a RETAINED ONE-TIME CAPTURE
made 2026-10-18. The app's exports are behind an app-level sign-in; by decision
of the research owner this script performs no sign-in and never re-acquires
them. A fresh run verifies those retained files by SHA-256, carries their
manifest records forward unchanged, and prints a SKIP line for each. A person
can re-download the exports by hand from the app's Export tab in a browser.

Run from the repository root:
  uv run python3 -I senate/2026/oklahoma/data/turnout/acquire.py           # refetch public sources
  uv run python3 -I senate/2026/oklahoma/data/turnout/acquire.py --verify  # offline: hash-check every file
A fresh run overwrites the public-source files in raw/ and rewrites the manifest.
"""
import gzip
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'raw'
MANIFEST = ROOT / 'source-manifest.json'
# The OKER/EIS load balancers return 403 to non-browser agents; this agent
# string is accepted and still identifies the research client.
UA = 'Mozilla/5.0 (compatible; election-research/1.0)'
OKER_ROOT = 'https://results.okelections.gov/'
EIS = 'https://stats.okelections.gov'
ELECTIONS = ['20241105', '20221108', '20201103']
OSEB_PAGES = {
    'oseb-results-index': 'https://oklahoma.gov/elections/elections-results/election-results.html',
    'oseb-2024-general-page': 'https://oklahoma.gov/elections/elections-results/election-results/2024-election-results/november-general-election.html',
    'oseb-2022-general-page': 'https://oklahoma.gov/elections/elections-results/election-results/2022-election-results/2022-november-general-election.html',
    'oseb-2020-general-page': 'https://oklahoma.gov/elections/elections-results/election-results/2020-election-results/2020-november-general-election.html',
    'oseb-registration-statistics-page': 'https://oklahoma.gov/elections/voter-registration/voter-registration-statistics.html',
    'oseb-registration-archive-page': 'https://oklahoma.gov/elections/voter-registration/voter-registration-statistics/voter-registration-statistics-archive.html',
    'oseb-2024-11-04-registration-release': 'https://oklahoma.gov/elections/newsroom/2024/november/oklahoma-voter-registration-numbers-surpass-2-4-million-ahead-of.html',
}
# Official pre-election (November 1) county registration reports, located by
# their href on the archive page (pattern -> evidence id).
VR_PDFS = {
    r'/2024-vr-statistics/vrstats-county-nov1-2024\.pdf': 'oseb-vrstats-county-2024-11-01',
    r'/2022-vr-statistics/vrstats-county-nov1-2022\.pdf': 'oseb-vrstats-county-2022-11-01',
    r'/2020-vr-statistics/vrstatsbycounty-11012020\.pdf': 'oseb-vrstats-county-2020-11-01',
}
# Retained one-time OKER capture (2026-10-18): verified, never re-fetched.
RETAINED = re.compile(r'^oker-\d{8}-')
RETAINED_NOTE = ('Retained one-time capture (2026-10-18). The app\'s exports are behind an app-level sign-in; '
                 're-acquisition by script is intentionally not supported.')
VH_DATES = ['2024-11-05', '2022-11-08', '2020-11-03']
VH_METHODS = ['Absentee', 'Early Voting', 'Election Day']
# Last month-end statistics date before each general, plus latest available.
VR_DATES = ['2024-10-31', '2022-10-31', '2020-10-31', '2026-09-30']
OTHER = {
    'census-county-codes-2020': 'https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt',
    'nara-2024-ascertainment-oklahoma': 'https://www.archives.gov/files/electoral-college/2024/ascertainment-oklahoma.pdf',
    'clerk-2022-statistics': 'https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf',
    'clerk-2020-statistics': 'https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf',
}
# CloudFront request IDs and edge locations identify the requester, not the source.
DROP_HEADERS = {'set-cookie', 'x-amz-cf-id', 'x-amz-cf-pop'}
rows = []


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Recorder(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.chain = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append({'status': code, 'from': req.full_url, 'location': headers.get('Location'), 'to': newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def http(url, method='GET', body=None, headers=None):
    rec = Recorder()
    opener = urllib.request.build_opener(rec)
    h = {'User-Agent': UA, 'Accept': '*/*'}
    h.update(headers or {})
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    start = now()
    try:
        r = opener.open(req, timeout=180)
        status, rh, data = r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        status, rh, data = e.code, e.headers, e.read()
    meta = {'retrieval_utc': start, 'completed_utc': now(), 'method': method, 'url': url,
            'request_headers': h,
            'redirects': rec.chain, 'status': status,
            'response_headers': {k: v for k, v in rh.items() if k.lower() not in DROP_HEADERS}}
    return meta, data


def store(key, ext, meta, data, parent=None, note=None, params=None):
    if ext in ('zip', 'pdf'):
        stored, name, storage = data, f'{key}.{ext}', 'original HTTP entity bytes (already compressed format)'
    else:
        stored, name, storage = gzip.compress(data, mtime=0), f'{key}.{ext}.gz', 'gzip (mtime=0) of original HTTP entity bytes'
    assert len(stored) < 40_000_000, key
    (RAW / name).write_bytes(stored)
    row = {'id': key, **meta, 'parent': parent, 'params': params, 'note': note,
           'path': f'raw/{name}', 'storage': storage,
           'original_bytes': len(data), 'original_sha256': sha(data),
           'stored_bytes': len(stored), 'stored_sha256': sha(stored)}
    rows.append(row)
    print(key, meta['status'], len(data), flush=True)
    if meta['status'] != 200:
        raise SystemExit(f'{key}: HTTP {meta["status"]}')
    return data


def oker_public():
    """Public OKER pages only: the app page each OSEB link opens, and its static config."""
    for d in ELECTIONS:
        page = rows_by_id(f'oseb-{d[:4]}-general-page')
        link = re.search(r'href="(https://results\.okelections\.(?:us|gov)/OKER/\?elecDate=' + d + ')"',
                         gzip.decompress((ROOT / page['path']).read_bytes()).decode('utf-8', 'replace'))
        assert link, f'OSEB page for {d} does not link OKER'
        meta, b = http(link.group(1), headers={'Accept': 'text/html'})
        store(f'oker-app-shell-{d}', 'html', meta, b, parent=page['id'],
              note='Exact OKER link printed on the OSEB election page; redirect chain retained.')
    meta, b = http(OKER_ROOT + 'OKER/assets/config.json')
    store('oker-config', 'json', meta, b, parent='oker-app-shell-20241105', note='Static public app configuration file.')


def verify_row(r):
    if r.get('path') is None:
        raise SystemExit(f'{r["id"]}: manifest record has no stored file')
    stored = (ROOT / r['path']).read_bytes()
    data = gzip.decompress(stored) if r['path'].endswith('.gz') else stored
    if sha(stored) != r['stored_sha256'] or sha(data) != r['original_sha256'] or len(data) != r['original_bytes']:
        raise SystemExit(f'{r["id"]}: SHA-256/size mismatch for {r["path"]}')


def retained_oker(old):
    keep = [r for r in old if RETAINED.match(r['id'])]
    if not keep:
        raise SystemExit('No retained OKER capture in source-manifest.json; OKER exports are intentionally not '
                         're-acquired by this script (re-download them by hand from the app Export tab).')
    for r in keep:
        verify_row(r)
        how = ("a person can re-download it by hand from the app's Export tab in a browser"
               if re.search(r'-(state|county|precinct)-csv$', r['id']) else 'app data response, not an Export-tab file; values are displayed by the app in a browser')
        print(f'SKIP {r["id"]}: {RETAINED_NOTE} Verified by SHA-256; {how}.', flush=True)
    rows.extend(keep)


def eis_item(dash, item, filters, key, note):
    q = {'dashboardId': dash, 'itemId': item}
    if filters:
        q['query'] = json.dumps({'Filter': filters}, separators=(',', ':'))
    url = EIS + '/dashboardControl/data/DashboardItemGetAction?' + urllib.parse.urlencode(q)
    meta, b = http(url, headers={'Accept': 'application/json'})
    return json.loads(store(key, 'json', meta, b, parent=f'eis-dashboard-{dash}', note=note, params=q))


def flt(member, interval, value):
    d = {'@DataMember': member, '@DefaultId': 'DataItem0', '@ItemType': 'Dimension'}
    if interval:
        d['@DateTimeGroupInterval'] = interval
    return {'dimensions': [d], 'values': [[value]]}


def eis():
    # eis-home uses the exact link printed on the OSEB registration-statistics page.
    for key, url, ext in [('eis-home', 'https://stats.okelections.us/', 'html'), ('eis-page-VHCountsByCounty', EIS + '/Home/VHCountsByCounty', 'html'),
                          ('eis-page-VrStatsByStatus', EIS + '/Home/VrStatsByStatus', 'html'), ('eis-guide', EIS + '/Home/EISGuide', 'pdf')]:
        meta, b = http(url)
        store(key, ext, meta, b, parent='oseb-registration-statistics-page' if key == 'eis-home' else 'eis-home',
              note='EIS Guide 10/2023 (definitions of voter history, registration status, voting methods).' if key == 'eis-guide' else None)
    for dash in ['VHCountsByCounty', 'VrStatsByStatus']:
        meta, b = http(f'{EIS}/dashboardControl/dashboards/{dash}', headers={'Accept': 'application/json'})
        store(f'eis-dashboard-{dash}', 'json', meta, b, parent=f'eis-page-{dash}', note='DevExpress dashboard definition (items, data members).')
    dates = eis_item('VHCountsByCounty', 'comboBoxDashboardItem1', None, 'eis-vh-election-dates', 'Election Date combo values.')
    avail = dates['ItemData']['DataStorageDTO']['EncodeMaps']['DataItem0']
    for d in VH_DATES:
        assert d + 'T00:00:00.0000000' in avail, d
        f = flt('ElectionDate', 'DayMonthYear', d + 'T00:00:00.000')
        eis_item('VHCountsByCounty', 'pivotDashboardItem1', [f], f'eis-vh-{d}-pivot', f'Voter history credit pivot (county x affiliation), Election Date = {d}.')
        eis_item('VHCountsByCounty', 'cardDashboardItem1', [f], f'eis-vh-{d}-card', f'Total Voter History card, Election Date = {d}.')
        eis_item('VHCountsByCounty', 'pieDashboardItem1', [f], f'eis-vh-{d}-methods', f'Voting Methods pie, Election Date = {d}.')
        for m in VH_METHODS:
            eis_item('VHCountsByCounty', 'pivotDashboardItem1', [f, flt('VotingMethod', None, m)],
                     f'eis-vh-{d}-pivot-{m.lower().replace(" ", "-")}', f'Voter history pivot, Election Date = {d}, Voting Method = {m}.')
    sdates = eis_item('VrStatsByStatus', 'comboBoxDashboardItem1', None, 'eis-vr-statistic-dates', 'Statistics Date combo values (month-end).')
    avail = sdates['ItemData']['DataStorageDTO']['EncodeMaps']['DataItem0']
    for d in VR_DATES:
        assert d + 'T00:00:00.0000000' in avail, d
        f = flt('StatisticDate', 'None', d + 'T00:00:00.000')
        eis_item('VrStatsByStatus', 'pivotDashboardItem1', [f], f'eis-vr-{d}-pivot', f'Registration by status pivot (county x affiliation; Active/Inactive), Statistics Date = {d}.')
        eis_item('VrStatsByStatus', 'cardDashboardItem4', [f], f'eis-vr-{d}-card-total', f'TotalVoters card, Statistics Date = {d}.')


def rows_by_id(key):
    return next(r for r in rows if r['id'] == key)


def main():
    old = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []
    if '--verify' in sys.argv[1:]:
        for r in old:
            verify_row(r)
        print(f'verified {len(old)} manifest records offline; no network access')
        return 0
    RAW.mkdir(exist_ok=True)
    for key, url in OSEB_PAGES.items():
        meta, b = http(url, headers={'Accept': 'text/html'})
        store(key, 'html', meta, b, parent='oseb-results-index' if key.endswith('general-page') else None)
    archive = gzip.decompress((ROOT / rows_by_id('oseb-registration-archive-page')['path']).read_bytes()).decode('utf-8', 'replace')
    for pat, key in VR_PDFS.items():
        hrefs = sorted(set(re.findall(r'href="([^"]*' + pat + ')"', archive)))
        assert len(hrefs) == 1, (pat, hrefs)
        meta, b = http(urllib.parse.urljoin(OSEB_PAGES['oseb-registration-archive-page'], hrefs[0]))
        store(key, 'pdf', meta, b, parent='oseb-registration-archive-page', note='Official pre-election county registration report (Current Registration Statistics by County).')
    oker_public()
    retained_oker(old)
    eis()
    for key, url in OTHER.items():
        meta, b = http(url)
        store(key, 'pdf' if url.endswith('.pdf') else 'txt', meta, b)
    MANIFEST.write_text(json.dumps(rows, indent=1) + '\n')
    print('manifest rows', len(rows))


if __name__ == '__main__':
    sys.exit(main())
