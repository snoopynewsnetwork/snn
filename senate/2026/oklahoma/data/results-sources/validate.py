#!/usr/bin/env python3
"""Validate the Oklahoma official-results inventory offline; writes validation.json.

Run from the repository root after build.py:
  PYTHONDONTWRITEBYTECODE=1 uv run python3 -I senate/2026/oklahoma/data/results-sources/validate.py
Exit status 1 if any check fails.
"""
import csv
import gzip
import hashlib
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent
STATE = DATA.parent
REPORT = STATE / 'official-results.md'
PRIORITY = ['40109', '40143', '40027', '40017', '40131', '40145', '40031', '40037', '40119', '40125', '40051', '40101', '40083',
            '40147', '40047', '40087', '40113', '40019', '40079', '40137', '40041', '40021', '40013', '40121', '40097', '40071']
EXPECTED = ['KEVIN HERN, REPUBLICAN', "N'KIYLA JASMINE THOMAS, DEMOCRAT", 'SEVIER WHITE, LIBERTARIAN', 'RON MEINHARDT, INDEPENDENT', 'CURTIS STINNETT, INDEPENDENT']
# URLs the report cites that this worker deliberately did not fetch, with the reason.
NOT_FETCHED = {
    'https://results.okelections.gov/OKERS/enrapi/': 'API base path named to describe the sign-in-gated channel; never called.',
    'https://web.archive.org/web/20241106133100id_/https://results.okelections.gov/OKERS/enrapi/getelec/20241105/SW/xx': 'Archived copy retained by the partisanship worker (dependency wayback-seb-oker-2024).',
    'https://www.oscn.net/applications/oscn/index.asp?ftdb=STOKST26&level=1': 'OSCN Title 26 index used to locate CiteIDs during exploration; the sections themselves are retained.',
}
checks = []


def check(name, ok, detail=None):
    checks.append({'check': name, 'pass': bool(ok), 'detail': detail})


def sha(b):
    return hashlib.sha256(b).hexdigest()


man = json.loads((ROOT / 'source-manifest.json').read_text())
M = {r['id']: r for r in man}

# 1. manifest integrity and storage
bad, stored = [], 0
for r in man:
    if not r.get('path'):
        continue
    b = (ROOT / r['path']).read_bytes()
    d = gzip.decompress(b) if r['path'].endswith('.gz') else b
    stored += len(b)
    if sha(b) != r['stored_sha256'] or len(b) != r['stored_bytes'] or sha(d) != r['original_sha256'] or len(d) != r['original_bytes']:
        bad.append(r['id'])
check('manifest: every stored file matches stored and original SHA-256/byte counts', not bad, {'records': len(man), 'mismatch': bad})
on_disk = sorted(p.name for p in (ROOT / 'raw').iterdir())
listed = sorted(Path(r['path']).name for r in man if r.get('path'))
check('manifest: raw/ holds exactly the manifest files', on_disk == listed, {'files': len(on_disk)})
check('manifest: ids unique', len(M) == len(man))
unretained = [r['id'] for r in man if not r.get('path')]
check('manifest: only the OKER bundle (by design) and failed/empty responses are unretained',
      all(i == 'oker-main-bundle' or not M[i]['original_bytes'] for i in unretained), unretained)
sizes = {p.name: p.stat().st_size for p in ROOT.rglob('*') if p.is_file()}
check('size: every owned file below 40,000,000 bytes', max(sizes.values()) < 40_000_000, {'largest': max(sizes.items(), key=lambda kv: kv[1])})

# 2. access rule
api_calls = [r['id'] for r in man for u in [r['url'], r.get('final_url') or ''] + [x['location'] for x in r.get('redirects', [])]
             if 'okelections' in urllib.parse.urlparse(u).netloc and urllib.parse.urlparse(u).path.upper().startswith('/OKERS/')]
check('access: no request to an OKER API path (/OKERS/...)', not api_calls, api_calls)
auth_headers = [r['id'] for r in man if any(k.lower() in ('authorization', 'cookie') for k in r.get('request_headers', {}))]
check('access: no Authorization or Cookie request header sent', not auth_headers, auth_headers)
leak = []
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix in ('.gz', '.json', '.py', '.md'):
        b = p.read_bytes()
        b = gzip.decompress(b) if p.suffix == '.gz' else b
        if p.name != 'validate.py' and (b'obs_' + b'authenticate' in b or b'conn' + b'Key="' in b):
            leak.append(p.name)
check('access: no stored file contains the OKER bundle sign-in code', not leak, leak)
bundle = json.loads((ROOT / 'oker-bundle-endpoints.json').read_text())
check('oker: bundle not stored; every route attaches a bearer token', bundle['stored'] is False and all(v['bearer_header_in_context'] for v in bundle['routes'].values()),
      sorted(bundle['routes']))
check('oker: app shells for 20261103 and 20260825 are byte-identical (shell cannot show configuration)',
      M['oker-shell-20261103']['original_sha256'] == M['oker-shell-20260825']['original_sha256'])

# 3. coverage
turn = {r['county_fips']: r for r in csv.DictReader(open(DATA / 'county-turnout.csv', newline=''))}
recs = json.loads((ROOT / 'county-records.json').read_text())
fips = [r['county_fips'] for r in recs]
check('coverage: 77 county records, each FIPS exactly once, equal to the turnout county set', len(fips) == 77 and len(set(fips)) == 77 and set(fips) == set(turn), len(fips))
check('coverage: priority set is exactly the accepted 26', sorted(r['county_fips'] for r in recs if r['investigation_scope'] == 'deep_priority') == sorted(PRIORITY))
manual = {o['id'] for o in json.loads((ROOT / 'manual-observations.json').read_text())['observations']}
thin = []
for r in recs:
    if r['investigation_scope'] != 'deep_priority':
        continue
    got = [e for e in r['county_board']['evidence'] if M[e]['status'] == 200]
    documented_absence = r['county_fips'] in ('40047', '40079', '40137', '40019', '40087')
    if not r['finding'] or (not got and not documented_absence):
        thin.append(r['county'])
    for o in r['county_board'].get('web_tool_observations', []):
        if o not in manual:
            thin.append(r['county'] + ':' + o)
check('coverage: every priority county has retrieved board evidence or a documented absence/block, plus a finding', not thin, thin)
check('coverage: every county has a SEB directory entry with an @elections.ok.gov email', all(r['seb_ceb_directory'].get('email', '').lower().endswith('@elections.ok.gov') for r in recs))
codes = sorted(int(r['oseb_county_code']) for r in recs)
check('coverage: SEB codes 1..77 each once', codes == list(range(1, 78)))
names_ok = [r['county'] for r in recs if re.sub(r'[^a-z]', '', r['seb_ceb_directory']['ceb_label'].split(' - ', 1)[1].lower()) != re.sub(r'[^a-z]', '', r['county'].lower())]
check('coverage: SEB directory label matches county name for every code', not names_ok, names_ok)
homes = [r for r in recs if r['county_home']['evidence']]
check('discovery: every county home page listed by OKCounties was requested', all(M[r['county_home']['evidence']] for r in homes),
      {'listed_and_requested': len(homes), 'not_listed': 77 - len(homes), 'http_status': sorted({str(M[r['county_home']['evidence']]['status']) for r in homes})})

# 4. ballot identity
bal = json.loads((ROOT / 'november-2026-ballot.json').read_text())
rows = bal['counties']
check('ballot: 77 county sections in the SEB November 2026 list', len(rows) == 77 and len({r['oseb_code'] for r in rows}) == 77)
check('ballot: exactly one U.S. Senator block per county with the five expected names, parties and order',
      all(r['us_senate_block_count'] == 1 and r['us_senate_candidates'] == EXPECTED for r in rows))
check('ballot: no county lists an unexpired-term U.S. Senator contest', not bal['counties_with_unexpired_us_senate_contest'])
sb = [l for l in bal['cleveland_sample_ballot_140100']['senate_block_lines']]
check('ballot: Cleveland precinct 140100 sample ballot prints the same five candidates in the same order',
      ' '.join(sb).replace('\n', ' ') == "KEVIN HERN REPUBLICAN N'KIYLA JASMINE THOMAS DEMOCRAT SEVIER WHITE LIBERTARIAN RON MEINHARDT INDEPENDENT CURTIS STINNETT INDEPENDENT", sb)
check('ballot: UOCAVA notice lists "U.S. Senator (1 office)" and a separate special for State Senator District 17',
      bool(bal['uocava_notice_offices_line']) and bool(bal['uocava_notice_special_line']))

# 5. EIS absentee
eis = json.loads((ROOT / 'eis-absentee.json').read_text())
c26 = [r['2026_11_03'] for r in eis['counties']]
st = eis['statewide_2026_11_03']
check('eis: 2026-11-03 and 2024-11-05 county rows present for all 77 counties', all(c26) and all(r['2024_11_05'] for r in eis['counties']))
check('eis: county Sent and Received sum to the statewide cards', sum(c['Sent'] for c in c26) == st['sent'] and sum(c['Received'] for c in c26) == st['received'],
      {'sent': [sum(c['Sent'] for c in c26), st['sent']], 'received': [sum(c['Received'] for c in c26), st['received']]})
check('eis: county Total sums to the ballot-type pie total', sum(c['Total'] for c in c26) == sum(st['ballot_types'].values()), [sum(c['Total'] for c in c26), sum(st['ballot_types'].values())])
ratio = [(r['county'], r['2024_11_05']['Received'], r['oker_2024_absentee_mail_votes_president']) for r in eis['counties']]
check('eis: 2024 Received compared with 2024 OKER president absentee-mail votes for all 77 counties (exceptions recorded: Received is not a ceiling)',
      len(ratio) == 77, {'received_below_votes': [x for x in ratio if x[1] < x[2]], 'statewide_received': sum(x[1] for x in ratio), 'statewide_votes': sum(x[2] for x in ratio)})

# 6. historical checks
h = json.loads((ROOT / 'historical-checks.json').read_text())
cc = h['cleveland_certificate_2024_president']
check('county certificate: Cleveland 2024 president, all precinct rows equal OKER official precinct export', cc['precinct_rows'] == cc['oker_cleveland_precincts'] == 105 and not cc['rows_not_matching_oker'])
check('county certificate: Cleveland 2024 president total equals OKER county total 119,294', cc['certificate_total'] == cc['oker_total'] == int(turn['40027']['pres2024_contest_votes']) == 119294)
rr = h['cleveland_certificate_2026_runoff_us_senate']
check('county certificate: Cleveland 2026 Senate runoff precinct rows sum to its Total row', rr['precinct_sum_matches_total'], rr['total_row'])
wv = h['wayback_vs_official_2024']
check('history: archived election-morning OKER copy was Unofficial at 1984/1984 precincts and differs from the official total',
      wv['wayback']['Title1'] == 'Unofficial Results' and wv['official']['isOfficial'] is True and wv['president_10001']['official_minus_wayback']['totalVotes'] == 1600)
pd = h['precinct_denominator_vs_9999']
check('history: precinct denominators exclude 559999 and 729999', pd['OKLAHOMA']['county_csv_tot_race_prec'] + 1 == pd['OKLAHOMA']['distinct_units_in_precinct_export'] and pd['TULSA']['county_csv_tot_race_prec'] + 1 == pd['TULSA']['distinct_units_in_precinct_export'], pd)
deps = json.loads((ROOT / 'dependencies.json').read_text())
dep_bad = [d['id'] for d in deps if d['match'] is False or sha((DATA / d['path']).read_bytes()) != d['stored_sha256']]
check('dependencies: pinned read-only files unchanged and equal to their owners\' manifests', not dep_bad, dep_bad)

# 7. state channels and statutes
ch = {c['channel_id']: c for c in json.loads((ROOT / 'state-channels.json').read_text())}
check('seb: 2026 results page has a November 3 row and it carries no link yet', ch['seb-results-pages']['november_2026_row_present'] and not ch['seb-results-pages']['november_2026_row_linked'])
check('seb: November 10, 2026 board meeting listed', ch['seb-certification']['november_10_2026_listed'])
pc = ch['statutes']['phrase_checks']
check('statutes: every quoted operative phrase is in the Legislature compiled title PDF', all(p['in_legislature_pdf'] for p in pc),
      [p['phrase'] for p in pc if not p['in_legislature_pdf']])
check('statutes: OSCN section text also contains the phrase wherever OSCN served the section (challenge pages excluded)',
      all(p['in_oscn'] for p in pc if not p['oscn_is_challenge_page']),
      {'missing': [p['phrase'] for p in pc if not p['in_oscn'] and not p['oscn_is_challenge_page']],
       'oscn_challenge_pages': sorted({p['oscn_record'] for p in pc if p['oscn_is_challenge_page']})})
wp = ch['wayback']['pages']
check('wayback: 2024 election-night SEB page reads UNOFFICIAL with the Friday/Tuesday certification wording',
      wp['wb-seb-2024-november-20241106020407']['heading'] == 'UNOFFICIAL RESULTS' and 'Friday, November 8' in (wp['wb-seb-2024-november-20241106020407']['provisional_sentence'] or ''))
check('wayback: no archived OKER API capture for any 2026 election', not [c for c in ch['wayback']['oker_api_captures'] if '/2026' in c['path']])

# 8. CSV
rows = list(csv.DictReader(open(DATA / 'official-results-sources.csv', newline='')))
cty = [r for r in rows if r['row_type'] == 'county']
check('csv: 77 county rows, unique FIPS, plus state-channel rows', len(cty) == 77 and len({r['county_fips'] for r in cty}) == 77, {'county_rows': len(cty), 'state_rows': len(rows) - len(cty)})
known = {r['url'] for r in man} | {r.get('final_url') for r in man} | {x['location'] for r in man for x in r.get('redirects', [])}
csv_urls = {u for r in rows for k in ('channel_url', 'county_home_url', 'county_board_page') for u in [r[k]] if u.startswith('http')}
unfetched = sorted(u for u in csv_urls if u not in known)
check('csv: every channel, home and board URL in the CSV was actually requested (status recorded)', not unfetched, unfetched)
check('csv: no row claims verified November 2026 counts or a demonstrated cadence', all(r['november_2026_counts_verified'] == 'False' and r['cadence_status'] == 'not_demonstrated' for r in rows))

# 9. report links and cited URLs
if REPORT.exists():
    md = REPORT.read_text()
    rel = re.findall(r'\]\((?!https?:|#|mailto:)([^)]+)\)', md)
    broken = [l for l in rel if not (STATE / l.split('#')[0]).exists()]
    check('report: relative Markdown links resolve', not broken, {'links': len(rel), 'broken': broken})
    urls = set(re.findall(r'\((https?://[^)\s]+)\)', md))
    dep_urls = {d.get('url') for d in deps}
    uncited = sorted(u for u in urls if u not in known and u not in dep_urls and u not in NOT_FETCHED)
    check('report: every cited URL was requested by acquire.py, is a pinned dependency, or is listed as deliberately not fetched', not uncited, uncited)
    trailing = [i for i, l in enumerate(md.splitlines(), 1) if l != l.rstrip()]
    check('report: no trailing whitespace', not trailing, trailing[:10])
else:
    check('report: official-results.md exists', False)
ws = []
for p in list(ROOT.glob('*.py')) + list(ROOT.glob('*.json')) + [DATA / 'official-results-sources.csv']:
    for i, l in enumerate(p.read_text().splitlines(), 1):
        if l != l.rstrip():
            ws.append(f'{p.name}:{i}')
check('whitespace: no trailing whitespace in scripts, JSON and CSV', not ws, ws[:10])

out = {'checks': len(checks), 'failed': sum(not c['pass'] for c in checks), 'results': checks}
(ROOT / 'validation.json').write_text(json.dumps(out, indent=1) + '\n')
for c in checks:
    print('PASS' if c['pass'] else 'FAIL', c['check'])
print(f"{out['checks']} checks, {out['failed']} failed")
sys.exit(1 if out['failed'] else 0)
