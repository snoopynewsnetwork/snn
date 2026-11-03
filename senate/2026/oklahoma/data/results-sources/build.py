#!/usr/bin/env python3
"""Build the Oklahoma official-results inventory offline from retained evidence.

Reads: raw/ + source-manifest.json (this directory), manual-observations.json,
and pinned read-only dependencies from sibling first-wave outputs
(../county-turnout.csv, ../turnout/raw/oker-2024* retained OKER capture,
../baselines/raw/wayback-seb-oker-2024/ archived OKER response). Dependency
hashes are checked against those workers' own manifests and pinned in
dependencies.json.

Writes: ../official-results-sources.csv, county-records.json,
state-channels.json, november-2026-ballot.json, eis-absentee.json,
historical-checks.json, dependencies.json.

Run from the repository root:
  PYTHONDONTWRITEBYTECODE=1 uv run --with pypdf==5.1.0 python3 -I senate/2026/oklahoma/data/results-sources/build.py
"""
import csv
import gzip
import hashlib
import html
import io
import json
import re
import urllib.parse
import zipfile
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent
MAN = {r['id']: r for r in json.loads((ROOT / 'source-manifest.json').read_text())}
PRIORITY = ['40109', '40143', '40027', '40017', '40131', '40145', '40031', '40037', '40119', '40125', '40051', '40101', '40083',
            '40147', '40047', '40087', '40113', '40019', '40079', '40137', '40041', '40021', '40013', '40121', '40097', '40071']
SENATE_EXPECTED = [('KEVIN HERN', 'REPUBLICAN'), ("N'KIYLA JASMINE THOMAS", 'DEMOCRAT'), ('SEVIER WHITE', 'LIBERTARIAN'),
                   ('RON MEINHARDT', 'INDEPENDENT'), ('CURTIS STINNETT', 'INDEPENDENT')]
OKER_NOV = 'https://results.okelections.us/OKER/?elecDate=20261103'
CEBINFO = 'https://okvoterportal.okelections.gov/cebinfo'
ELIST = 'https://hosting.okelections.gov/electionlist.html'
MANUAL = 'Open the SEB results page for the election (oklahoma.gov/elections > Election Results > 2026), follow its OK Election Results link in a browser, select the county, and record race, candidate, method columns, precincts reporting, Unofficial/Official label and the time shown, with a screenshot or the Export-tab file kept by hand. If the app is unavailable, call the county election board (number in the SEB /cebinfo table).'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def raw(key):
    r = MAN[key]
    b = (ROOT / r['path']).read_bytes()
    return gzip.decompress(b) if r['path'].endswith('.gz') else b


def text(key):
    return raw(key).decode('utf-8', 'replace')


def strip(t):
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', t, flags=re.S | re.I)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t))).strip()


def anchors(key):
    r = MAN[key]
    base = r['final_url']
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', text(key), flags=re.S | re.I)
    out = []
    for m in re.finditer(r'<a\b[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>', t, re.S | re.I):
        out.append((urllib.parse.urljoin(base, html.unescape(m.group(1).strip())), re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', m.group(2)))).strip()))
    return out


def aem_meta(key):
    t = text(key)
    vis = re.search(r'Last Modified on\s*(?:<[^>]+>\s*)*([A-Z][a-z]{2} \d{2}, \d{4})', t)
    comp = None
    for m in re.finditer(r'data-cmp-data-layer="([^"]*)"', t):
        layer = html.unescape(m.group(1))
        if 'xdm:text' in layer and re.search(r'elecDate=|November 3|General Elections?|RESULTS', layer):
            d = re.search(r'"repo:modifyDate":"([^"]+)"', layer)
            if d and (comp is None or d.group(1) > comp):
                comp = d.group(1)
    return {'results_text_component_modify_date': comp, 'visible_last_modified': vis.group(1) if vis else None,
            'note': 'AEM data-layer date of the page text component holding the results table/links; site chrome dates are ignored.'}


def main_text(key):
    t = re.sub(r'data-cmp-data-layer="[^"]*"', '', text(key))
    m = re.search(r'<main\b.*?</main>', t, re.S | re.I)
    return strip(m.group(0) if m else t)


# ---------------------------------------------------------------- dependencies
def dependencies():
    tm = {r['id']: r for r in json.loads((DATA / 'turnout' / 'source-manifest.json').read_text())}
    bs = {r['source_id']: r for r in json.loads((DATA / 'baselines' / 'sources.json').read_text())['sources']}
    deps = []
    for rid in ['oker-20241105-getconfig', 'oker-20241105-getelec-sw', 'oker-20241105-county-csv', 'oker-20241105-precinct-csv',
                'oker-20241105-cntyresults-10001', 'oker-config']:
        r = tm[rid]
        p = DATA / 'turnout' / r['path']
        b = p.read_bytes()
        deps.append({'id': rid, 'owner': 'turnout worker (read-only)', 'path': p.relative_to(DATA).as_posix(), 'url': r['url'],
                     'retrieval_utc': r['retrieval_utc'], 'stored_sha256': sha(b), 'manifest_stored_sha256': r['stored_sha256'],
                     'match': sha(b) == r['stored_sha256'], 'note': r.get('note')})
    r = bs['wayback-seb-oker-2024']
    p = DATA / 'baselines' / r['stored_path']
    b = p.read_bytes()
    deps.append({'id': 'wayback-seb-oker-2024', 'owner': 'partisanship worker (read-only)', 'path': p.relative_to(DATA).as_posix(), 'url': r['url'],
                 'retrieval_utc': r['retrieved_utc'], 'stored_sha256': sha(b), 'manifest_stored_sha256': r['stored_sha256'],
                 'match': sha(b) == r['stored_sha256'], 'note': r['role'] + ' (third-party archive copy of a sign-in-gated API response).'})
    b = (DATA / 'county-turnout.csv').read_bytes()
    deps.append({'id': 'county-turnout-csv', 'owner': 'turnout worker (read-only)', 'path': 'county-turnout.csv', 'stored_sha256': sha(b), 'match': None,
                 'note': '77-county FIPS, OSEB code, OKER label, 2024 president method splits.'})
    return deps


def dep_bytes(deps, rid):
    d = next(x for x in deps if x['id'] == rid)
    b = (DATA / d['path']).read_bytes()
    return gzip.decompress(b) if d['path'].endswith('.gz') else b


# ---------------------------------------------------------------- parsers
def parse_cebinfo():
    t = text('seb-cebinfo')
    out = {}
    for tr in re.findall(r'<tr\b.*?</tr>', t, re.S | re.I):
        cells = [strip(c).replace('\xa0', ' ') for c in re.findall(r'<t[hd]\b.*?</t[hd]>', tr, re.S | re.I)]
        if len(cells) == 8 and re.match(r'^\d+ - ', cells[0]):
            code, name = cells[0].split(' - ', 1)
            out[int(code)] = {'ceb_label': cells[0], 'phone': cells[1], 'fax': cells[2], 'secretary': cells[3], 'physical_address': cells[4],
                              'mailing_address': cells[5], 'hours': cells[6], 'email': cells[7]}
    return out


def parse_election_list():
    t = text('seb-election-list-nov2026')
    parts = re.split(r'<A NAME=(\d\d)>([^<]+)</A>', t)
    out = {}
    for i in range(1, len(parts), 3):
        code, name, body = int(parts[i]), parts[i + 1].strip(), parts[i + 2]
        items = []
        for m in re.finditer(r'WIDTH=9(80|70|90)>\s*(.*?)</TD>', body, re.S):
            level = {'90': 'section', '80': 'office', '70': 'candidate'}[m.group(1)]
            items.append((level, strip(m.group(2))))
        offices, cur = [], None
        for level, val in items:
            if level == 'office':
                cur = {'office': val, 'candidates': []}
                offices.append(cur)
            elif level == 'candidate' and cur is not None:
                cur['candidates'].append(val)
        sen = [o for o in offices if 'SENATOR' in o['office'] and 'STATE SENATOR' not in o['office']]
        rep = [o['office'] for o in offices if o['office'].startswith('UNITED STATES REPRESENTATIVE')]
        out[code] = {'list_county_label': name, 'office_count': len(offices), 'us_senate_blocks': sen, 'us_representative': rep,
                     'unexpired_labels': [o['office'] for o in offices if 'UNEXPIRED' in o['office'].upper()]}
    return out


def parse_earlyvote():
    t = text('seb-earlyvote-nov2026')
    parts = re.split(r'<A NAME=(\d\d)>([^<]+)</A>', t)
    out = {}
    for i in range(1, len(parts), 3):
        body = parts[i + 2]
        sites = [strip(x) for x in re.findall(r'WIDTH=970>\s*<B>(.*?)</B>', body, re.S) if 'Early Voting Dates' not in x]
        days = sorted(set(strip(x) for x in re.findall(r'WIDTH=970>\s*((?:Wed|Thu|Fri|Sat)\.,[^<]*)</TD>', body)))
        out[int(parts[i])] = {'label': parts[i + 1].strip(), 'sites': sites, 'site_count': len(sites), 'days': days}
    return out


def dx_pivot(key):
    d = json.loads(raw(key))
    ds = d['ItemData']['DataStorageDTO']
    md = d['ItemData']['MetaData']
    names = {m['ID']: m['Name'] for m in md['MeasureDescriptors']}
    sl = next(s for s in ds['Slices'] if s['KeyIds'] == ['DataItem6'])
    pos = {v: k for k, v in sl['ValueIds'].items()}
    counties = ds['EncodeMaps']['DataItem6']
    out = {}
    for k, vals in sl['Data'].items():
        idx = int(k.strip('[]'))
        out[counties[idx]] = {names[pos[int(p)]]: v for p, v in vals.items()}
    return out


def dx_card(key):
    d = json.loads(raw(key))
    return d['ItemData']['DataStorageDTO']['Slices'][0]['Data']['[]']['0']


def dx_pie(key):
    d = json.loads(raw(key))
    ds = d['ItemData']['DataStorageDTO']
    labels = ds['EncodeMaps']['DataItem1']
    sl = ds['Slices'][0]
    vpos = sl['ValueIds']['DataItem2']
    return {labels[int(k.strip('[]'))]: v[str(vpos)] for k, v in sl['Data'].items()}


def pdf_layout_pages(key):
    r = PdfReader(io.BytesIO(raw(key)))
    return r, [p.extract_text(extraction_mode='layout') for p in r.pages]


def certificate_contest(pages, title):
    """Return (header names in column order, {precinct: [ints]}, total row ints) for one contest."""
    rows, total, header = {}, None, None
    for t in pages:
        lines = [l for l in t.splitlines() if l.strip()]
        if len(lines) < 5 or lines[3].strip() != title:
            continue
        hl = [l for l in lines[4:8] if not l.strip().startswith('CLEVELAND COUNTY PCT') and l.strip() not in ('Precinct', 'DEMOCRAT', 'REPUBLICAN')]
        for l in lines:
            m = re.match(r'\s*CLEVELAND COUNTY PCT (\d{6})\s+([\d,\s]+)$', l)
            if m:
                rows[m.group(1)] = [int(x.replace(',', '')) for x in m.group(2).split()]
            m = re.match(r'\s*Total:\s+([\d,\s]+)$', l)
            if m:
                total = [int(x.replace(',', '')) for x in m.group(1).split()]
        if header is None:
            header = hl
    return header, rows, total


# ---------------------------------------------------------------- historical checks
def historical(deps):
    out = {}
    # Retained OKER capture formats (turnout worker; read-only).
    cfg = json.loads(dep_bytes(deps, 'oker-20241105-getconfig'))
    gel = json.loads(dep_bytes(deps, 'oker-20241105-getelec-sw'))
    cty = json.loads(dep_bytes(deps, 'oker-20241105-cntyresults-10001'))
    z = zipfile.ZipFile(io.BytesIO(dep_bytes(deps, 'oker-20241105-precinct-csv')))
    prec = list(csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding='utf-8')))
    zc = zipfile.ZipFile(io.BytesIO(dep_bytes(deps, 'oker-20241105-county-csv')))
    ccsv = list(csv.DictReader(io.TextIOWrapper(zc.open(zc.namelist()[0]), encoding='utf-8')))
    out['retained_oker_format'] = {
        'source': 'turnout worker retained one-time OKER capture (2026-10-18), read-only; this worker made no OKER API call',
        'getconfig_fields': {k: cfg[k] for k in ['pollingInterval', 'showAbs', 'showEarly', 'showElecDay', 'elecState', 'absVoteDesc', 'earlyVoteDesc',
                                                 'elecDayVoteDesc', 'apiVersion', 'mapsEnabled', 'elecValid']},
        'getconfig_county_options': len([x for x in cfg['counties']['Options'] if x]),
        'getelec_top_level_keys': sorted(gel.keys()),
        'getelec_status_fields_2024_official': {k: gel[k] for k in ['Title1', 'isOfficial', 'lastUpdate', 'serverTLU', 'turnoutPerc']},
        'getelec_result_fields': sorted(gel['results'][0].keys()),
        'getelec_cand_result_fields': sorted(gel['results'][0]['candResults'][0].keys()),
        'cntyresults_fields': sorted(cty.keys()), 'cntyresults_county_fields': sorted(cty['summaryCandResults'][0].keys()),
        'extract_csv_header': list(prec[0].keys())[:16],
        'note': 'lastUpdate is the fetch-time clock of the API response (UTC offset printed). serverTLU has no zone; the 2024 election-morning archive value 2024-11-06T00:45:47 only makes sense as Central time (all 1,984 precincts reported), so treat serverTLU as local Central time, inferred, not documented.',
    }
    # Completion denominators exclude the countywide 9999 units.
    pc = {}
    for code, label in (('55', 'OKLAHOMA'), ('72', 'TULSA')):
        crow = next(r for r in ccsv if r['county'] == label and r['race_number'] == '10001')
        units = sorted(set(r['precinct'] for r in prec if r['race_number'] == '10001' and r['precinct'].startswith(code)))
        pc[label] = {'county_csv_tot_race_prec': int(crow['tot_race_prec']), 'distinct_units_in_precinct_export': len(units),
                     'nine999_units': [u for u in units if u.endswith('9999')]}
    out['precinct_denominator_vs_9999'] = pc
    # Wayback election-morning OKER copy vs official retained capture.
    wb = json.loads(dep_bytes(deps, 'wayback-seb-oker-2024'))
    off = {r['raceID']: r for r in gel['results']}
    diffs = []
    for r in wb['results']:
        o = off.get(r['raceID'])
        if not o:
            continue
        d = {k: o['totResults'][k] - r['totResults'][k] for k in ['absVotes', 'earlyVotes', 'elecDayVotes', 'totalVotes']}
        diffs.append({'raceID': r['raceID'], 'reporting_wayback': f"{r['reportingPrecincts']}/{r['totalPrecincts']}", 'official_minus_wayback': d})
    pres = next(x for x in diffs if x['raceID'] == 10001)
    out['wayback_vs_official_2024'] = {
        'wayback': {k: wb[k] for k in ['Title1', 'isOfficial', 'lastUpdate', 'serverTLU', 'turnoutPerc']},
        'official': {k: gel[k] for k in ['Title1', 'isOfficial', 'serverTLU', 'turnoutPerc']},
        'races_compared': len(diffs), 'races_with_any_change': sum(1 for x in diffs if any(x['official_minus_wayback'].values())),
        'races_at_100pct_in_wayback': sum(1 for r in wb['results'] if r['reportingPrecincts'] == r['totalPrecincts']),
        'races_in_wayback': len(wb['results']),
        'president_10001': pres,
        'president_totals': {'wayback': next(r for r in wb['results'] if r['raceID'] == 10001)['totResults'], 'official': off[10001]['totResults']},
        'net_decreases': [x for x in diffs if any(v < 0 for v in x['official_minus_wayback'].values())][:10],
    }
    # Cleveland County certificate (county publication) vs OKER official precinct export.
    r, pages = pdf_layout_pages('cty-40027-certificate-2024-general')
    header, rows, total = certificate_contest(pages, 'ELECTORS FOR PRESIDENT AND VICE PRESIDENT')
    order = ['CHASE OLIVER | MIKE TER MAAT', 'DONALD J. TRUMP | JD VANCE', 'KAMALA D. HARRIS | TIM WALZ', 'ROBERT F. KENNEDY JR. | NICOLE SHANAHAN', 'CHRIS GARRITY | CODY BALLARD']
    ok = {}
    for x in prec:
        if x['race_number'] == '10001' and x['precinct'].startswith('14'):
            ok.setdefault(x['precinct'], {})[x['cand_name']] = int(x['cand_tot_votes'])
    mism = [p for p in rows if [ok.get(p, {}).get(n) for n in order] != rows[p]]
    sig = re.search(r'DATED AT ([A-Z ]+), OKLAHOMA, THIS (\w+) DAY OF (\w+), (\d{4})', pages[-1].replace('\n', ' '))
    out['cleveland_certificate_2024_president'] = {
        'evidence': 'cty-40027-certificate-2024-general', 'pdf_pages': len(pages), 'pdf_creation_date': str(r.metadata.get('/CreationDate')),
        'report_title': str(r.metadata.get('/Title')), 'header_lines': [h.strip() for h in header] if header else None,
        'precinct_rows': len(rows), 'oker_cleveland_precincts': len(ok), 'rows_not_matching_oker': mism, 'certificate_total_row': total,
        'certificate_total': sum(total) if total else None, 'oker_total': sum(sum(v.values()) for v in ok.values()),
        'oker_candidate_totals': [sum(ok[p][n] for p in ok) for n in order],
        'signature_line': sig.group(0) if sig else None,
        'note': 'The county certificate has precinct rows only (absentee and early votes are inside precinct rows in Cleveland, as in OKER); no method split, no provisional row.',
    }
    r2, pages2 = pdf_layout_pages('cty-40027-certificate-2026-runoff')
    h2, rows2, total2 = certificate_contest(pages2, 'FOR UNITED STATES SENATOR')
    cols = [c for line in (h2 or []) for c in re.split(r'\s{2,}', line.strip()) if c and c not in ('DEMOCRAT', 'REPUBLICAN', 'Precinct')]
    out['cleveland_certificate_2026_runoff_us_senate'] = {
        'evidence': 'cty-40027-certificate-2026-runoff', 'pdf_creation_date': str(r2.metadata.get('/CreationDate')), 'columns_in_order': cols,
        'precinct_rows': len(rows2), 'total_row': total2, 'precinct_sum_matches_total': [sum(v[i] for v in rows2.values()) for i in range(len(total2))] == total2,
        'note': 'Democratic runoff for U.S. Senator, Cleveland County only. Official county certificate; statewide runoff totals are only in the sign-in-gated OKER app.',
    }
    return out


# ---------------------------------------------------------------- state channels
def state_channels(elist, ev, abs26):
    res2026 = text('seb-results-2026')
    nov_row = re.search(r'<tr><td>(?:<a [^>]*>)?November 3(?:</a>)?</td>', res2026)
    nov_linked = bool(re.search(r'<a [^>]*>November 3</a>', res2026))
    shells = {k: MAN[k]['original_sha256'] for k in ['oker-shell-20261103', 'oker-shell-20260825']}
    bundle = json.loads((ROOT / 'oker-bundle-endpoints.json').read_text())
    meetings = main_text('seb-meetings-2026')
    nov10 = re.search(r'November 10, 2026 Meeting Notice\s*\[?[^\]]*\]?\s*(Agenda - TBA)?', meetings)
    wb_pages = {}
    for k in ['wb-seb-2024-november-20241105223112', 'wb-seb-2024-november-20241106020407', 'wb-seb-2024-november-20241108164759',
              'wb-seb-2026-august-20260827122028', 'wb-seb-2026-august-20260910093956']:
        mt = main_text(k)
        wb_pages[k] = {'heading': re.search(r'(UNOFFICIAL RESULTS|OFFICIAL RESULTS)', mt).group(1),
                       'provisional_sentence': (re.search(r'will not include provisional ballot results until after .*?p\.m\. [A-Z][a-z]+, [A-Z][a-z]+ \d+\.', mt) or [None])[0],
                       'certification_sentence': (re.search(r'Unless a contest of election.*?(?:recount has been completed)\.', mt) or [None])[0],
                       'continuous_update_sentence': 'Results will be updated continuously throughout the evening' in mt,
                       'memento': MAN[k]['response_headers'].get('memento-datetime')}
    cdx = json.loads(raw('wb-cdx-oker-enrapi'))[1:]
    statutes = {}
    for k in [x for x in MAN if x.startswith('statute-26-') or x.startswith('statute-51-')]:
        t = strip(text(k))
        m = re.search(r'Cite as:(.*?)(Historical Data|Citationizer)', t)
        statutes[k] = m.group(1).strip()[:6000] if m else ('OSCN CHALLENGE PAGE (not source text)' if 'OSCN Turnstile' in t else None)
    leg = {}
    for k in ('statute-os26-legislature', 'statute-os51-legislature'):
        r = PdfReader(io.BytesIO(raw(k)))
        t = re.sub(r'\s+', ' ', ' '.join((pg.extract_text() or '') for pg in r.pages))
        leg[k] = re.sub(r'Oklahoma Statutes - Title \d+\. [A-Za-z, ]+? Page \d+ ', '', t)
    phrase_checks = []
    for sec, key, lk, phrase in STATUTE_PHRASES:
        o = re.sub(r'\s+', ' ', statutes.get(key) or '')
        phrase_checks.append({'section': sec, 'phrase': phrase, 'oscn_record': key, 'in_oscn': phrase in o,
                              'oscn_is_challenge_page': o.startswith('OSCN CHALLENGE'), 'in_legislature_pdf': phrase in leg[lk]})
    ch = [
        {'channel_id': 'seb-results-pages', 'channel': 'SEB election results pages (oklahoma.gov)', 'url': MAN['seb-results-index']['url'], 'access_class': 'public_tested',
         'evidence': ['seb-results-index', 'seb-results-2026', 'seb-results-2026-june', 'seb-results-2026-august', 'seb-results-2024', 'seb-results-2024-november'],
         'status': MAN['seb-results-2026']['status'], 'source_timestamps': {k: aem_meta(k) for k in ['seb-results-2026', 'seb-results-2026-june', 'seb-results-2026-august', 'seb-results-2024', 'seb-results-2024-november']},
         'finding': f"2026 page lists 'November 3 General Elections' {'with' if nov_linked else 'without'} a link; June 16 and August 25 pages read OFFICIAL RESULTS and link OKER elecDate=20260616 / 20260825. Pages carry no vote counts; data download is 'Export' inside OKER.",
         'november_2026_row_present': bool(nov_row), 'november_2026_row_linked': nov_linked},
        {'channel_id': 'oker-app', 'channel': 'OK Election Results (OKER) app', 'url': OKER_NOV, 'access_class': 'sign_in_gated_not_tested',
         'evidence': ['oker-shell-20261103', 'oker-shell-20260825', 'oker-static-config', 'oker-main-bundle'], 'status': MAN['oker-shell-20261103']['status'],
         'shell_sha256_identical_across_dates': len(set(shells.values())) == 1, 'shell_last_modified': MAN['oker-shell-20261103']['response_headers'].get('last-modified'),
         'redirects': MAN['oker-shell-20261103']['redirects'], 'bundle_routes': sorted(bundle['routes']), 'bundle_sha256': bundle['bundle_sha256'],
         'finding': 'Public shell, static config and bundle fetched. Every data route (getconfig, getelec, GetResults, GetCntyResults, GetPctResults, GetExtract, GetFile, map and proposition routes) is called with a bearer token from the app sign-in, which this research did not perform. Whether 2026-11-03 is configured cannot be observed without it: the shell is byte-identical for every elecDate.'},
        {'channel_id': 'oker-retained-capture', 'channel': 'Retained one-time OKER capture (turnout worker, 2026-10-18)', 'url': 'data/turnout/raw/', 'access_class': 'retained_capture_sign_in_gated',
         'evidence': ['dependencies.json'], 'status': None,
         'finding': 'Format evidence only: getconfig pollingInterval 30000 ms; getelec Title1/isOfficial/lastUpdate/serverTLU; per-race totalPrecincts/reportingPrecincts/reportingPercent and candidate absVotes/earlyVotes/elecDayVotes; county and precinct CSV exports with tot_race_prec/race_prec_reporting. Elections 2020/2022/2024 only; nothing for 2026.'},
        {'channel_id': 'seb-election-list', 'channel': 'SEB November 2026 list of elections (hosting.okelections)', 'url': ELIST, 'access_class': 'public_tested',
         'evidence': ['seb-next-election', 'seb-election-list-nov2026'], 'status': MAN['seb-election-list-nov2026']['status'],
         'source_timestamps': {k: MAN['seb-election-list-nov2026']['response_headers'].get(k) for k in ['last-modified', 'x-amz-meta-s3b-last-modified', 'x-amz-version-id']},
         'redirects': MAN['seb-election-list-nov2026']['redirects'],
         'finding': f"{len(elist)} county sections; U.S. Senator block in {sum(1 for v in elist.values() if v['us_senate_blocks'])}; identical five-candidate list in each. Ballot identity only, no counts."},
        {'channel_id': 'seb-early-vote-list', 'channel': 'SEB November 3 early-voting locations', 'url': MAN['seb-earlyvote-nov2026']['final_url'], 'access_class': 'public_tested',
         'evidence': ['seb-early-voting-page', 'seb-earlyvote-nov2026'], 'status': MAN['seb-earlyvote-nov2026']['status'],
         'source_timestamps': {'last-modified': MAN['seb-earlyvote-nov2026']['response_headers'].get('last-modified')},
         'finding': f"{len(ev)} county sections, {sum(v['site_count'] for v in ev.values())} sites; days {sorted(set(d for v in ev.values() for d in v['days']))}."},
        {'channel_id': 'seb-ceb-directory', 'channel': 'SEB county election board directory (OK Voter Portal /cebinfo)', 'url': CEBINFO, 'access_class': 'public_tested',
         'evidence': ['seb-county-election-boards', 'seb-cebinfo', 'seb-ceb-addresses-pdf'], 'status': MAN['seb-cebinfo']['status'],
         'finding': '77 boards with SEB code, phone, fax, secretary, addresses, hours and @elections.ok.gov email. No county web-site column.'},
        {'channel_id': 'eis-absentee', 'channel': 'SEB Interactive Statistics, Absentee Statistics By County', 'url': EIS_PAGE, 'access_class': 'public_tested',
         'evidence': ['eis-page-AbsByCounty', 'eis-dashboard-AbsStatsByCounty', 'eis-abs-election-dates', 'eis-abs-20261103-pivot'], 'status': MAN['eis-abs-20261103-pivot']['status'],
         'finding': f"Election Date list includes 2026-11-03. County pivot: Total, Sent, Received, Rejected for all 77 counties ({abs26['statewide']['sent']} sent, {abs26['statewide']['received']} received statewide at retrieval). Administrative mail-absentee counts, not votes or candidate choice; no as-of clock printed."},
        {'channel_id': 'seb-news', 'channel': 'SEB newsroom releases (2026)', 'url': MAN['seb-newsroom']['url'], 'access_class': 'public_tested',
         'evidence': ['seb-newsroom'] + [k for k in MAN if k.startswith('seb-news-')], 'status': MAN['seb-newsroom']['status'],
         'finding': 'June 12 release: results on the SEB website after polls close at 7 p.m., auto-refresh recommended. July 8: November ballot order Republican, Democratic, Libertarian, then Independents by lot. Oct 7: Nov 3 deadlines. Oct 13: office evacuation, Secretary says no impact on conducting elections. The newsroom index is script-rendered; releases were located by web search, so the release list is not exhaustive.'},
        {'channel_id': 'seb-certification', 'channel': 'SEB board meetings (certification)', 'url': MAN['seb-meetings-2026']['url'], 'access_class': 'public_tested',
         'evidence': ['seb-meetings-2026', 'seb-minutes-2026-06-23', 'seb-meetings-2024'], 'status': MAN['seb-meetings-2026']['status'],
         'november_10_2026_listed': bool(nov10), 'november_10_agenda_tba': bool(nov10 and nov10.group(1)),
         'finding': 'Meeting list includes November 10, 2026 (Tuesday after the election; agenda TBA). June 23, 2026 minutes (scanned) record the 3-0 vote certifying the June 16 primary results at a 5 p.m. meeting; the minutes print no totals. Minutes were posted in September.'},
        {'channel_id': 'statutes', 'channel': 'OSCN statute text', 'url': MAN['statute-26-7-136']['url'], 'access_class': 'public_tested',
         'evidence': sorted(k for k in MAN if k.startswith('statute-')), 'status': 200, 'extracts': statutes, 'phrase_checks': phrase_checks,
         'legislature_pdf_last_modified': {k: MAN[k]['response_headers'].get('last-modified') for k in ('statute-os26-legislature', 'statute-os51-legislature')},
         'finding': 'Polls 7 a.m.-7 p.m.; absentee mail by 7 p.m.; absentee results not released before 7 p.m.; county certifies after 5 p.m. Friday; SEB certifies after 5 p.m. the Tuesday after; provisional information withheld until 1 p.m. Friday; U.S. Senate vacancy with a full term already on the ballot needs no special election.'},
        {'channel_id': 'wayback', 'channel': 'Internet Archive copies (third party)', 'url': MAN['wb-cdx-oker-enrapi']['url'], 'access_class': 'third_party_archive',
         'evidence': [k for k in MAN if k.startswith('wb-')], 'status': 200, 'pages': wb_pages,
         'oker_api_captures': [{'timestamp': r[0], 'path': r[1].split('/enrapi/')[1], 'status': r[2]} for r in cdx],
         'finding': f"CDX lists {len(cdx)} archived OKER API URLs, none for a 2026 election. Archived SEB 2024 general and 2026 runoff pages show the unofficial-phase wording (provisional ballots after 5 p.m. Friday; county certification not earlier than 5 p.m. Friday; SEB certification Tuesday)."},
        {'channel_id': 'county-discovery-directory', 'channel': 'OKCounties county list (KellPro; vendor directory)', 'url': MAN['okcounties-countydata']['url'], 'access_class': 'public_tested_non_authority',
         'evidence': ['okcounties-countydata'], 'status': MAN['okcounties-countydata']['status'],
         'finding': 'Used only to find county home pages. It is not an election authority; county board pages found through it link back to SEB results.'},
    ]
    return ch, wb_pages


STATUTE_PHRASES = [
    ('26 O.S. 7-136', 'statute-26-7-136', 'statute-os26-legislature', 'after 5 p.m. on Friday following the election'),
    ('26 O.S. 7-136', 'statute-26-7-136', 'statute-os26-legislature', 'after 5 p.m. on Tuesday next succeeding the election'),
    ('26 O.S. 12-101(C)(3)', 'statute-26-12-101', 'statute-os26-legislature', 'then no special election shall be called'),
    ('26 O.S. 12-101(C)(3)', 'statute-26-12-101', 'statute-os26-legislature', 'deemed to also have been elected to fill the vacancy'),
    ('26 O.S. 14-104', 'statute-26-14-104', 'statute-os26-legislature', 'no later than 7:00 p.m. the day of the election'),
    ('26 O.S. 14-125', 'statute-26-14-125', 'statute-os26-legislature', 'made known to any person nor announced earlier than 7:00 p.m.'),
    ('26 O.S. 14-123', 'statute-26-14-123', 'statute-os26-legislature', 'At 10:00 a.m. on Thursday preceding the election'),
    ('26 O.S. 7-104', 'statute-26-7-104', 'statute-os26-legislature', 'shall open at 7:00 a.m. and shall remain open continuously until 7:00 p.m.'),
    ('26 O.S. 7-116.1', 'statute-26-7-116.1', 'statute-os26-legislature', 'prior to 1:00 p.m. on Friday following the election'),
    ('26 O.S. 14-115.4', 'statute-26-14-115.4', 'statute-os26-legislature', 'without obtaining a printout of results, remove the electronic results storage media'),
    ('51 O.S. 10(C)', 'statute-51-10', 'statute-os51-legislature', 'to serve in such office until a successor is elected'),
]
EIS_PAGE = 'https://stats.okelections.gov/Home/AbsByCounty'
SEB_NEWSROOM = 'https://oklahoma.gov/elections/newsroom.html'

COUNTY_NOTES = {
    '40109': 'Board page on the county site posts board press-release PDFs (for Nov 3, 2026: sample ballots via OK Voter Portal, absentee deadlines, remote early-voting sites) and links the OK Voter Portal. It publishes no results. Absentee-mail and early votes report as countywide unit 559999, outside the precinct denominator.',
    '40143': 'www.tulsacounty.org is a script redirect to www2.tulsacounty.org. The board Election Results page links the SEB 2026, 2025 and 2024 results pages and the SEB archive; no county-hosted counts. The press-release list is script-rendered and was not parsed. Absentee-mail and early votes report as countywide unit 729999, outside the precinct denominator.',
    '40027': "Independent board site. It posts each election's signed county 'Official Certificate of Votes' PDF (precinct x candidate, generated the Friday after the election) and per-precinct sample-ballot PDFs for Nov 3, 2026. The 2024 certificate reconciles to OKER's official precinct export; the Aug 25, 2026 certificate gives the county's Democratic U.S. Senate runoff. Its list also carries a separate 'Runoff Primary August 27, 2024 SS 15 and SH 20 After Recount' entry, so recount corrections appear as new entries. The June 16, 2026 primary is not in its list. Certificates arrive after election night, not as a live feed.",
    '40017': 'County-site Election Board page links the SEB results index, absentee and registration pages. No county results.',
    '40131': "Independent board site. Its Election Results page links the OKER app for the latest election (elecDate=20260825, labeled 'HERE') and the SEB archive. The home page notes early voting Oct 28-31 and a Sept 22 audit of the Aug 25 runoff.",
    '40145': "County-site page tells voters to use the SEB website for 'election day results'. Early voting at First Baptist Church (Wagoner) and NSU Broken Arrow.",
    '40031': "County directory entry only; the home page 'Election Board' tile links oklahoma.gov/elections.html.",
    '40037': "County-site board page with an 'Oklahoma Election Results' page that links the SEB results index. Board meeting notices posted (special meeting Oct 15, 2026).",
    '40119': 'Independent board site (votepaynecounty.com). Election Results links the SEB results index. Its sample-ballot page lists earlier 2026 local ballots only.',
    '40125': 'County-site board page; describes duties and links the SEB site. No results.',
    '40051': 'County staff-directory entry only (names, email). No results or election pages.',
    '40101': 'OKCounties-hosted board page linking www.elections.ok.gov (legacy SEB host) and a Precincts page.',
    '40083': "County-site board page with an 'Election Night Reporting' link to the SEB results index.",
    '40147': 'County-site board page; links the legacy SEB host www.ok.gov/elections/. No results.',
    '40047': 'No county election board page found: the county home page has no election link (raw and web-tool reads) and searches found only news and third-party directories.',
    '40087': "Raw fetches of the county home and board pages returned 403 to the research agent. A web-tool read shows an 'Election Returns' link to oklahoma.gov/elections.html and no results.",
    '40113': 'OKCounties-hosted board page; duties, contact and OK Voter Portal link. No results.',
    '40019': "No board page of its own. The county site's County Boards page lists 'Election Board' as a link to the legacy SEB host https://www.ok.gov/elections/. That host sends an incomplete certificate chain (Python's default store rejects it); verified against the operating-system store it redirects (301) to oklahoma.gov/elections.html.",
    '40079': 'No county home page in the OKCounties list and no board web page found by search. Contact via SEB /cebinfo only.',
    '40137': 'No county home page in the OKCounties list and no board web page found; a search-suggested host did not resolve. Contact via SEB /cebinfo only.',
    '40041': 'OKCounties-hosted board page linking the SEB results index, upcoming elections and the OK Voter Portal.',
    '40021': 'OKCounties-hosted board page; describes duties only.',
    '40013': "OKCounties-hosted board page linking SEB 'Election Info' (oklahoma.gov/elections/elections-results) and the polling-place locator.",
    '40121': 'OKCounties-hosted board page with Precincts and voter precinct map links. No results.',
    '40097': 'OKCounties-hosted board page linking the legacy SEB host elections.ok.gov, precincts and polling locations.',
    '40071': "County-site board page: polling places (updated Dec 2025), 2026 meeting schedule, SEB absentee/registration links, and an 'Election Returns' quick link to the legacy SEB host www.ok.gov/elections/.",
}


def classify_links(lst):
    kinds = set()
    for u, _ in lst:
        h = urllib.parse.urlparse(u).netloc.lower()
        if 'results.okelections' in h:
            kinds.add('links OKER app')
        elif h.endswith('oklahoma.gov') and '/elections/elections-results' in u:
            kinds.add('links SEB results pages')
        elif (h.endswith('oklahoma.gov') and '/elections' in u) or h in ('elections.ok.gov', 'www.elections.ok.gov') or (h == 'www.ok.gov' and '/elections' in u):
            kinds.add('links SEB site')
        elif 'okvoterportal' in h:
            kinds.add('links OK Voter Portal')
    return sorted(kinds)


def results_links(lst):
    out = []
    for u, t in lst:
        u = u.split('#')[0]
        if u.startswith('mailto:') or not u or re.search(r'Candidacy', u + t, re.I):
            continue
        if re.search(r'results\.okelections|elections-results|election-results|Official_Certificate|Certificate%20of%20Votes|/elections\.html|elections\.ok\.gov|ok\.gov/elections', u, re.I) or re.search(r'result|returns', t, re.I):
            if u not in [x[0] for x in out]:
                out.append((u, t))
    return out


# ---------------------------------------------------------------- main
def main():
    deps = dependencies()
    turnout = {r['county_fips']: r for r in csv.DictReader(open(DATA / 'county-turnout.csv', newline=''))}
    ceb = parse_cebinfo()
    elist = parse_election_list()
    ev = parse_earlyvote()
    a26 = dx_pivot('eis-abs-20261103-pivot')
    a24 = dx_pivot('eis-abs-20241105-pivot')
    okc = json.loads(raw('okcounties-countydata'))
    okc_by = {c['name'].replace(' ', '').lower(): c for c in okc}
    zc = zipfile.ZipFile(io.BytesIO(dep_bytes(deps, 'oker-20241105-county-csv')))
    ccsv = {r['county']: r for r in csv.DictReader(io.TextIOWrapper(zc.open(zc.namelist()[0]), encoding='utf-8')) if r['race_number'] == '10001'}
    cfg = json.loads(dep_bytes(deps, 'oker-20241105-getconfig'))
    oker_opts = dict(zip(cfg['counties']['Values'], cfg['counties']['Options']))
    abs26 = {'statewide': {'sent': dx_card('eis-abs-20261103-card-sent'), 'received': dx_card('eis-abs-20261103-card-received'),
                           'rejected': dx_card('eis-abs-20261103-card-rejected'), 'ballot_types': dx_pie('eis-abs-20261103-ballot-types'),
                           'application_sources': dx_pie('eis-abs-20261103-app-sources')},
             'retrieval_utc': MAN['eis-abs-20261103-pivot']['retrieval_utc']}
    records, eis_rows, ballot_rows = [], [], []
    for fips, t in sorted(turnout.items(), key=lambda kv: int(kv[1]['rank_pres2024'])):
        code = int(t['oseb_county_code'])
        label = t['oker_county_label']
        key = label.replace(' ', '').lower()
        c = okc_by[key]
        home_id = f'home-{fips}'
        home = MAN.get(home_id)
        home_links = anchors(home_id) if home and home.get('path') else []
        elect_links = [(u, x) for u, x in home_links if re.search(r'elect', u + ' ' + x, re.I) and 'email-protection' not in u]
        pages = [k for k in MAN if k.startswith(f'cty-{fips}-')]
        board_id = next((k for k in (f'cty-{fips}-board', f'cty-{fips}-board-link') if k in MAN), None)
        page_links = []
        for k in pages:
            if MAN[k].get('path') and MAN[k]['kind'] == 'html':
                page_links += anchors(k)
        el = elist.get(code, {})
        sen = el.get('us_senate_blocks', [])
        sen_ok = len(sen) == 1 and [tuple(x.rsplit(', ', 1)) for x in sen[0]['candidates']] == SENATE_EXPECTED
        e26 = a26.get(label) or a26.get(label.replace(' ', ''))
        e24 = a24.get(label) or a24.get(label.replace(' ', ''))
        crow = ccsv[label.upper().replace(' ', '')] if label.upper().replace(' ', '') in ccsv else ccsv.get(label.upper())
        nine = {'55': '559999', '72': '729999'}.get(t['oseb_county_code'])
        deep = fips in PRIORITY
        if not home:
            home_status = 'no county home page listed by OKCounties'
        else:
            home_status = home['status'] if home['status'] else home.get('error')
        if deep:
            if fips == '40027':
                kind = 'independent board site; posts county certificate PDFs and precinct sample ballots'
            elif board_id and MAN[board_id]['status'] == 200 and urllib.parse.urlparse(MAN[board_id]['final_url']).netloc not in urllib.parse.urlparse(c.get('link') or '').netloc:
                kind = 'independent board site' if fips in ('40131', '40119', '40143') else 'board page on separate host'
            elif board_id and MAN[board_id]['status'] == 200:
                kind = 'board page on county site'
            elif board_id:
                kind = f"board page not retrieved (HTTP {MAN[board_id]['status'] or MAN[board_id].get('error')})"
            else:
                kind = 'no board page found'
            if fips == '40143':
                kind = 'independent board section on county host (www2.tulsacounty.org)'
            if fips == '40087':
                kind = 'board page on county site; raw HTTP 403; web-tool read only'
            if fips == '40019':
                kind = 'no board page; County Boards page links legacy SEB host'
        else:
            kind = 'discovery only: home-page election links listed, board pages not followed'
        rl = results_links(page_links if deep else elect_links)
        rec = {
            'county': t['county'], 'county_fips': fips, 'oseb_county_code': t['oseb_county_code'], 'rank_pres2024': int(t['rank_pres2024']),
            'investigation_scope': 'deep_priority' if deep else 'discovery',
            'seb_ceb_directory': {'url': CEBINFO, **ceb.get(code, {})},
            'oker': {'county_option_label': oker_opts.get(t['oseb_county_code']), 'county_option_value': t['oseb_county_code'],
                     'nov2026_route': OKER_NOV, 'nov2026_access': 'sign-in-gated; not tested',
                     'precincts_2024_president': int(crow['tot_race_prec']), 'reporting_2024_final': int(crow['race_prec_reporting']),
                     'absentee_early_reporting': f'countywide unit {nine} (outside the precinct count)' if nine else 'inside geographic precinct rows',
                     'pres2024_methods': {'absentee_mail': int(t['pres2024_absentee_mail_votes']), 'early': int(t['pres2024_early_votes']),
                                          'election_day': int(t['pres2024_election_day_votes']), 'total': int(t['pres2024_contest_votes'])}},
            'nov2026_election_list': {'url': ELIST, 'anchor': f'#{code:02d}', 'list_county_label': el.get('list_county_label'),
                                      'us_senate_block_count': len(sen), 'us_senate_candidates': sen[0]['candidates'] if sen else [],
                                      'matches_expected_slate_and_order': sen_ok, 'us_representative': el.get('us_representative'),
                                      'office_count': el.get('office_count'), 'unexpired_term_offices': el.get('unexpired_labels')},
            'early_voting_nov2026': {'site_count': ev.get(code, {}).get('site_count'), 'sites': ev.get(code, {}).get('sites'), 'days': ev.get(code, {}).get('days')},
            'eis_absentee_2026_11_03': e26, 'eis_absentee_2024_11_05': e24,
            'county_home': {'directory_link': c.get('link'), 'on_okcounties_platform': c.get('on_okcs'), 'evidence': home_id if home else None,
                            'status': home_status, 'final_url': home['final_url'] if home else None,
                            'election_links': [u for u, _ in elect_links][:12]},
            'county_board': {'kind': kind, 'evidence': pages, 'board_page': MAN[board_id]['url'] if board_id else None,
                             'board_status': (MAN[board_id]['status'] or MAN[board_id].get('error')) if board_id else None,
                             'link_classes': classify_links(page_links if deep else elect_links),
                             'results_related_links': [u for u, _ in rl][:12],
                             'last_modified_headers': {k: MAN[k]['response_headers'].get('last-modified') for k in pages if MAN[k]['response_headers'].get('last-modified')}},
            'november_2026': {'county_counts_url_verified': False, 'senate_counts_verified': False, 'cadence': 'not demonstrated',
                              'exact_senate_remaining_votes': None, 'results_authority': 'SEB OKER app (sign-in-gated data; not tested)'},
            'manual_fallback': MANUAL,
            'finding': COUNTY_NOTES.get(fips, ''),
        }
        if deep and fips == '40087':
            rec['county_board']['web_tool_observations'] = ['webtool-mcclain-home', 'webtool-mcclain-board']
        records.append(rec)
        eis_rows.append({'county': t['county'], 'county_fips': fips, 'eis_label': label, '2026_11_03': e26, '2024_11_05': e24,
                         'oker_2024_absentee_mail_votes_president': int(t['pres2024_absentee_mail_votes'])})
        ballot_rows.append({'county_fips': fips, 'county': t['county'], 'oseb_code': code, **rec['nov2026_election_list']})
    # sample ballot corroboration
    sb = PdfReader(io.BytesIO(raw('cty-40027-sample-ballot-140100')))
    sbt = '\n'.join(p.extract_text() for p in sb.pages)
    m = re.search(r'FOR UNITED STATES\s*SENATOR\s*\(Vote for One\)(.*?)FOR UNITED STATES\s*REPRESENTATIVE', sbt, re.S)
    sb_lines = [x.strip() for x in m.group(1).splitlines() if x.strip()] if m else []
    hist = historical(deps)
    channels, wb_pages = state_channels(elist, ev, abs26)
    unexpired_us = [r['county'] for r in records if any('SENATOR' in u and 'STATE' not in u for u in (r['nov2026_election_list']['unexpired_term_offices'] or []))]
    ballot = {
        'source': ELIST, 'evidence': 'seb-election-list-nov2026', 'last_modified': MAN['seb-election-list-nov2026']['response_headers'].get('last-modified'),
        'expected_slate': [f'{n}, {p}' for n, p in SENATE_EXPECTED],
        'counties_with_exactly_one_us_senate_block': sum(1 for r in ballot_rows if r['us_senate_block_count'] == 1),
        'counties_matching_expected_slate_and_order': sum(1 for r in ballot_rows if r['matches_expected_slate_and_order']),
        'counties_with_unexpired_us_senate_contest': unexpired_us,
        'cleveland_sample_ballot_140100': {'evidence': 'cty-40027-sample-ballot-140100', 'senate_block_lines': sb_lines,
                                           'pdf_creation_date': str(sb.metadata.get('/CreationDate')), 'straight_party_section': 'STRAIGHT PARTY VOTING' in sbt},
        'uocava_notice_offices_line': (re.search(r'U\.S\. Senator \(1 office\)', main_text('seb-uocava-2026-general')) or [None])[0],
        'uocava_notice_special_line': (re.search(r'State Senator, District 17 \(Special Election [^)]*\)', main_text('seb-uocava-2026-general')) or [None])[0],
        'ballot_order_release': 'seb-news-2026-07-08-ballot-order',
        'counties': ballot_rows,
    }
    eis = {'dashboard': 'AbsStatsByCounty', 'page': EIS_PAGE, 'retrieval_utc_2026': MAN['eis-abs-20261103-pivot']['retrieval_utc'],
           'retrieval_utc_2024': MAN['eis-abs-20241105-pivot']['retrieval_utc'], 'statewide_2026_11_03': abs26['statewide'],
           'measure_meaning': 'Dashboard labels only: Total, Sent, Received, Rejected (mail absentee ballots, all types). No as-of time is printed. Early (in-person absentee) voting is not in this dashboard.',
           'counties': eis_rows}
    (ROOT / 'county-records.json').write_text(json.dumps(records, indent=1) + '\n')
    (ROOT / 'november-2026-ballot.json').write_text(json.dumps(ballot, indent=1) + '\n')
    (ROOT / 'eis-absentee.json').write_text(json.dumps(eis, indent=1) + '\n')
    (ROOT / 'historical-checks.json').write_text(json.dumps(hist, indent=1) + '\n')
    (ROOT / 'state-channels.json').write_text(json.dumps(channels, indent=1) + '\n')
    (ROOT / 'dependencies.json').write_text(json.dumps(deps, indent=1) + '\n')
    write_csv(records, channels)
    print('records', len(records), 'priority', sum(r['investigation_scope'] == 'deep_priority' for r in records))
    print('senate blocks ok', ballot['counties_matching_expected_slate_and_order'], 'unexpired', unexpired_us)
    print('cleveland cert', {k: hist['cleveland_certificate_2024_president'][k] for k in ['precinct_rows', 'oker_cleveland_precincts', 'certificate_total', 'oker_total']},
          'mismatch', len(hist['cleveland_certificate_2024_president']['rows_not_matching_oker']))
    print('runoff', hist['cleveland_certificate_2026_runoff_us_senate']['columns_in_order'], hist['cleveland_certificate_2026_runoff_us_senate']['total_row'])
    print('wayback pres', hist['wayback_vs_official_2024']['president_10001'])


COLS = ['row_type', 'county', 'county_fips', 'oseb_county_code', 'rank_pres2024', 'investigation_scope', 'channel', 'channel_url', 'access_class',
        'http_status', 'ceb_email', 'ceb_phone', 'ceb_physical_address', 'oker_county_label', 'oker_nov2026_route', 'oker_nov2026_access',
        'precincts_2024', 'absentee_early_reporting', 'pres2024_absentee_mail', 'pres2024_early', 'pres2024_election_day',
        'nov2026_list_senate_block', 'nov2026_list_us_representative', 'early_vote_sites_nov2026',
        'eis_abs_2026_total', 'eis_abs_2026_sent', 'eis_abs_2026_received', 'eis_abs_2026_rejected', 'eis_abs_2026_retrieval_utc',
        'county_home_url', 'county_home_status', 'county_board_kind', 'county_board_page', 'county_board_status', 'county_link_classes',
        'county_results_related_links', 'november_2026_counts_verified', 'cadence_status', 'exact_senate_remaining_votes',
        'finding', 'gap', 'manual_fallback', 'evidence']


def write_csv(records, channels):
    out = []
    for r in records:
        e = r['eis_absentee_2026_11_03'] or {}
        gap = ('November 2026 county counts, Senate race ID and candidate IDs are only in the sign-in-gated OKER app (not tested); no publication cadence, completion timestamp or remaining-vote estimate is published by any tested channel.'
               if r['investigation_scope'] == 'deep_priority' else
               'Discovery only: board web pages were not followed; county counts come only through the sign-in-gated OKER app (not tested).')
        out.append({
            'row_type': 'county', 'county': r['county'], 'county_fips': r['county_fips'], 'oseb_county_code': r['oseb_county_code'],
            'rank_pres2024': r['rank_pres2024'], 'investigation_scope': r['investigation_scope'], 'channel': 'county election board',
            'channel_url': r['county_board']['board_page'] or r['county_home']['directory_link'] or CEBINFO,
            'access_class': ('public_tested' if r['county_board']['board_status'] == 200 else 'blocked_or_absent') if r['investigation_scope'] == 'deep_priority' else 'public_landing_inspected',
            'http_status': r['county_board']['board_status'] if r['county_board']['board_page'] else r['county_home']['status'],
            'ceb_email': r['seb_ceb_directory'].get('email'), 'ceb_phone': r['seb_ceb_directory'].get('phone'),
            'ceb_physical_address': r['seb_ceb_directory'].get('physical_address'), 'oker_county_label': r['oker']['county_option_label'],
            'oker_nov2026_route': r['oker']['nov2026_route'], 'oker_nov2026_access': r['oker']['nov2026_access'],
            'precincts_2024': r['oker']['precincts_2024_president'], 'absentee_early_reporting': r['oker']['absentee_early_reporting'],
            'pres2024_absentee_mail': r['oker']['pres2024_methods']['absentee_mail'], 'pres2024_early': r['oker']['pres2024_methods']['early'],
            'pres2024_election_day': r['oker']['pres2024_methods']['election_day'],
            'nov2026_list_senate_block': 'present; 5 candidates match' if r['nov2026_election_list']['matches_expected_slate_and_order'] else 'MISMATCH',
            'nov2026_list_us_representative': '; '.join(r['nov2026_election_list']['us_representative'] or []),
            'early_vote_sites_nov2026': r['early_voting_nov2026']['site_count'],
            'eis_abs_2026_total': e.get('Total'), 'eis_abs_2026_sent': e.get('Sent'), 'eis_abs_2026_received': e.get('Received'),
            'eis_abs_2026_rejected': e.get('Rejected'), 'eis_abs_2026_retrieval_utc': MAN['eis-abs-20261103-pivot']['retrieval_utc'],
            'county_home_url': r['county_home']['directory_link'] if str(r['county_home']['directory_link']).startswith('http') else '',
            'county_home_status': r['county_home']['status'], 'county_board_kind': r['county_board']['kind'],
            'county_board_page': r['county_board']['board_page'] or '', 'county_board_status': r['county_board']['board_status'] or '',
            'county_link_classes': '; '.join(r['county_board']['link_classes']),
            'county_results_related_links': ' | '.join(r['county_board']['results_related_links'][:6]),
            'november_2026_counts_verified': False, 'cadence_status': 'not_demonstrated', 'exact_senate_remaining_votes': '',
            'finding': r['finding'] or 'County results publish through the SEB OKER app; see county-records.json for the discovery-level home-page links.',
            'gap': gap, 'manual_fallback': MANUAL, 'evidence': f"results-sources/county-records.json#{r['county_fips']}",
        })
    for c in channels:
        out.append({'row_type': 'state_channel', 'channel': c['channel'], 'channel_url': c['url'], 'access_class': c['access_class'],
                    'http_status': c.get('status') or '', 'november_2026_counts_verified': False, 'cadence_status': 'not_demonstrated',
                    'finding': c['finding'], 'evidence': 'results-sources/state-channels.json#' + c['channel_id']})
    with open(DATA / 'official-results-sources.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator='\n')
        w.writeheader()
        for row in out:
            w.writerow({k: row.get(k, '') for k in COLS})


if __name__ == '__main__':
    main()
