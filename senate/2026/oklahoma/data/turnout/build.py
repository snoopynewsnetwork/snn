#!/usr/bin/env python3
"""Offline Oklahoma turnout build and validation.

Reads only raw/ evidence listed in source-manifest.json (verifying every
original and stored SHA-256), then writes:
  ../county-turnout.csv          one row per county (77), ranked by 2024 president votes
  county-candidate-method.csv    every county x candidate x method cell for the six contests
  statewide-controls.csv         statewide candidate controls and certified cross-checks
  priority-set.json              exact ranking/top-15/minimum-80% arithmetic per measure
  reporting-units.json           precinct-export unit counts and non-geographic 9999 units
  ranking-table.md               the Markdown ranking table embedded in ../../turnout.md
  validation.json                every check with pass/fail and details

Run from the repository root:
  PYTHONDONTWRITEBYTECODE=1 uv run --with pypdf==6.21.1 python3 -I senate/2026/oklahoma/data/turnout/build.py
pypdf is used only to re-extract text from the three certified PDFs.
Any failed check exits non-zero after writing validation.json.
"""
import csv
import gzip
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_EVEN, getcontext
from pathlib import Path

getcontext().prec = 60
ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent
STATE_DIR = DATA.parent
MANIFEST = json.loads((ROOT / 'source-manifest.json').read_text())
BY_ID = {r['id']: r for r in MANIFEST}
CHECKS = []

CONTESTS = {
    # id: (OKER date, exact OKER race title, label, seat note)
    'pres2024': ('20241105', 'ELECTORS FOR PRESIDENT AND VICE PRESIDENT', '2024 president', 'primary ranking contest; no 2024 U.S. Senate contest in Oklahoma'),
    'sen2022s': ('20221108', 'FOR UNITED STATES SENATOR (UNEXPIRED TERM)', '2022 U.S. Senate special (unexpired term ending 2027-01-03)', 'same Class II seat as 2026; midterm comparator'),
    'sen2022r': ('20221108', 'FOR UNITED STATES SENATOR', '2022 U.S. Senate regular (full term from 2023-01-03)', 'other (Class III) seat; midterm comparator'),
    'gov2022': ('20221108', 'FOR GOVERNOR', '2022 governor', 'highest-volume 2022 statewide contest; context only'),
    'sen2020': ('20201103', 'FOR UNITED STATES SENATOR', '2020 U.S. Senate regular', 'previous regular election for the same Class II seat; context only'),
    'pres2020': ('20201103', 'FOR ELECTORS FOR PRESIDENT AND VICE PRESIDENT', '2020 president', 'context only'),
}
VH = {'vh2024': '2024-11-05', 'vh2022': '2022-11-08', 'vh2020': '2020-11-03'}
VH_METHODS = [('absentee', 'Absentee'), ('early_voting', 'Early Voting'), ('election_day', 'Election Day')]
VR = {'reg20241031': '2024-10-31', 'reg20221031': '2022-10-31', 'reg20201031': '2020-10-31', 'reg20260930': '2026-09-30'}
RANKED = ['pres2024', 'sen2022s', 'sen2022r', 'gov2022', 'sen2020', 'pres2020', 'vh2024', 'vh2022', 'vh2020']


def check(name, ok, **details):
    CHECKS.append({'check': name, 'passed': bool(ok), **details})
    return ok


def raw(key):
    r = BY_ID[key]
    stored = (ROOT / r['path']).read_bytes()
    data = gzip.decompress(stored) if r['path'].endswith('.gz') else stored
    ok = hashlib.sha256(stored).hexdigest() == r['stored_sha256'] and hashlib.sha256(data).hexdigest() == r['original_sha256'] \
        and len(stored) == r['stored_bytes'] and len(data) == r['original_bytes'] and len(stored) < 40_000_000
    if not ok:
        raise SystemExit(f'checksum/size mismatch for {key}')
    return data


def jraw(key):
    return json.loads(raw(key))


def norm(name):
    return re.sub('[^A-Z]', '', name.upper().removesuffix(' COUNTY'))


def zipped_csv(key):
    z = zipfile.ZipFile(io.BytesIO(raw(key)))
    names = z.namelist()
    assert len(names) == 1, names
    member = z.read(names[0])
    rows = list(csv.reader(io.StringIO(member.decode('utf-8-sig'), newline='')))
    return names[0], hashlib.sha256(member).hexdigest(), rows


def records(rows):
    """OKER CSV rows: data rows may add exactly one trailing empty field beyond the header."""
    hdr, out, extra = rows[0], [], 0
    n = len(hdr)
    assert hdr[0] == 'elec_date' and hdr[-1] == 'race_county_owner', hdr
    for r in rows[1:]:
        if len(r) == n + 1:
            assert r[n] == '', r
            r, extra = r[:n], extra + 1
        assert len(r) == n, r
        out.append(dict(zip(hdr, r)))
    return out, extra


def col_sum(rs, field):
    return sum(int(r[field]) for r in rs)


def pct(n, d, places=10):
    q = Decimal(1).scaleb(-places)
    return str((Decimal(n) * 100 / Decimal(d)).quantize(q, rounding=ROUND_HALF_EVEN))


# ---------------------------------------------------------------- geography
census = [l.split('|') for l in raw('census-county-codes-2020').decode('utf-8-sig').splitlines()]
chdr = census[0]
ok_census = [dict(zip(chdr, l)) for l in census[1:] if len(l) == len(chdr) and l[chdr.index('STATEFP')] == '40']
check('census: Oklahoma has 77 county rows with unique FIPS', len(ok_census) == 77 and len({c['COUNTYFP'] for c in ok_census}) == 77, rows=len(ok_census))
FIPS = {norm(c['COUNTYNAME']): '40' + c['COUNTYFP'] for c in ok_census}
CENSUS_NAME = {norm(c['COUNTYNAME']): c['COUNTYNAME'] for c in ok_census}
check('census: normalized county names unique', len(FIPS) == 77)

COUNTY = {}  # norm -> dict
for date in ['20241105', '20221108', '20201103']:
    cfg = jraw(f'oker-{date}-getconfig')
    pairs = [(n, v) for n, v in zip(cfg['counties']['Options'], cfg['counties']['Values']) if v]
    check(f'oker {date}: getconfig lists 77 counties coded 01-77', len(pairs) == 77 and [v for _, v in pairs] == [f'{i:02d}' for i in range(1, 78)])
    for n, v in pairs:
        k = norm(n)
        assert k in FIPS, n
        c = COUNTY.setdefault(k, {'oseb_code': v, 'oker_label': n})
        assert c['oseb_code'] == v and c['oker_label'] == n, (date, n, v)
check('join: all 77 OKER county codes/names match a Census FIPS by normalized name', len(COUNTY) == 77 and set(COUNTY) == set(FIPS),
      aliases={'LeFlore (OKER/EIS)': 'Le Flore County (Census)', 'Roger Mills': 'Roger Mills County'})
CODE2K = {c['oseb_code']: k for k, c in COUNTY.items()}
# Consistency observation; joins use names, never this arithmetic.
odd = sorted(k for k in COUNTY if int(FIPS[k][2:]) != 2 * int(COUNTY[k]['oseb_code']) - 1)
check('consistency: Census county code = 2*OSEB county code - 1 for all 77 name-joined counties', not odd, counties_differing=[CENSUS_NAME[k] for k in odd])

# ---------------------------------------------------------------- contests
contest_rows = {}   # cid -> {norm: [row dicts]}
contest_cands = {}  # cid -> list of (cand_number, name, party)
state_rows = {}
long_rows = []
units = {}
for cid, (date, title, label, note) in CONTESTS.items():
    elec = jraw(f'oker-{date}-getelec-sw')
    check(f'{cid}: OKER election flagged official', elec['isOfficial'] is True and elec['Title1'] == 'Official Results', serverTLU=elec['serverTLU'], turnoutPerc_display=elec['turnoutPerc'])
    rid = [r['raceID'] for r in elec['races'] if r['raceTitle'] == title]
    check(f'{cid}: exactly one statewide race with exact title', len(rid) == 1, race_id=rid)
    rid = rid[0]
    # statewide CSV
    srecs, sextra = records(list(csv.reader(io.StringIO(raw(f'oker-{date}-state-csv').decode('utf-8-sig'), newline=''))))
    sw = [r for r in srecs if r['race_description'] == title and r['race_party'] == '']
    check(f'{cid}: statewide CSV race number equals getelec race ID', {int(r['race_number']) for r in sw} == {rid})
    cands = [(int(r['cand_number']), r['cand_name'], r['cand_party']) for r in sw]
    contest_cands[cid] = cands
    state_rows[cid] = sw
    check(f'{cid}: statewide precinct reporting complete', all(r['tot_race_prec'] == r['race_prec_reporting'] for r in sw), precincts=sw[0]['tot_race_prec'])
    # getelec statewide candResults (no names) vs CSV, compared as a multiset
    res = next(r for r in elec['results'] if r['raceID'] == rid)
    a = sorted((c['absVotes'], c['earlyVotes'], c['elecDayVotes'], c['totalVotes']) for c in res['candResults'])
    b = sorted((int(r['cand_absmail_votes']), int(r['cand_early_votes']), int(r['cand_elecday_votes']), int(r['cand_tot_votes'])) for r in sw)
    check(f'{cid}: getelec statewide candidate/method totals equal statewide CSV', a == b and res['totResults']['totalVotes'] == sum(x[3] for x in b))
    # county CSV
    member, msha, rows = zipped_csv(f'oker-{date}-county-csv')
    crecs, cextra = records(rows)
    cr = [r for r in crecs if r['race_description'] == title and r['race_party'] == '' and int(r['race_number']) == rid]
    by = defaultdict(list)
    for r in cr:
        by[norm(r['county'])].append(r)
    contest_rows[cid] = by
    check(f'{cid}: county CSV covers all 77 counties', set(by) == set(COUNTY), counties=len(by), zip_member=member, member_sha256=msha)
    bad = [r for r in cr if int(r['cand_absmail_votes']) + int(r['cand_early_votes']) + int(r['cand_elecday_votes']) != int(r['cand_tot_votes'])]
    check(f'{cid}: every county row total = absentee mail + early + election day', not bad, bad=len(bad))
    check(f'{cid}: every county has the identical statewide candidate list',
          all(sorted((int(r['cand_number']), r['cand_name'], r['cand_party']) for r in by[k]) == sorted(cands) for k in by))
    check(f'{cid}: every county reports all precincts', all(r['tot_race_prec'] == r['race_prec_reporting'] for r in cr))
    sums = defaultdict(lambda: [0, 0, 0, 0])
    for r in cr:
        s = sums[int(r['cand_number'])]
        for i, f in enumerate(['cand_absmail_votes', 'cand_early_votes', 'cand_elecday_votes', 'cand_tot_votes']):
            s[i] += int(r[f])
    diff = {n: (sums[n], [int(r['cand_absmail_votes']), int(r['cand_early_votes']), int(r['cand_elecday_votes']), int(r['cand_tot_votes'])])
            for n, *_ in cands for r in sw if int(r['cand_number']) == n and sums[n] != [int(r['cand_absmail_votes']), int(r['cand_early_votes']), int(r['cand_elecday_votes']), int(r['cand_tot_votes'])]}
    check(f'{cid}: 77-county candidate x method sums equal statewide CSV exactly', not diff, differences=diff)
    # GetCntyResults JSON (separate API path)
    cj = jraw(f'oker-{date}-cntyresults-{rid}')
    jby = {norm(c['countyName']): c for c in cj['summaryCandResults']}
    mism = [k for k in by if sorted(c['totalVotes'] for c in jby[k]['candResults']) != sorted(int(r['cand_tot_votes']) for r in by[k])
            or jby[k]['totResults']['totalVotes'] != sum(int(r['cand_tot_votes']) for r in by[k])]
    check(f'{cid}: GetCntyResults county totals equal county CSV', set(jby) == set(by) and not mism, mismatched=mism)
    # Precinct CSV -> county
    pm, psha, prow = zipped_csv(f'oker-{date}-precinct-csv')
    precs, _ = records(prow)
    pr = [r for r in precs if r['race_description'] == title and r['race_party'] == '' and int(r['race_number']) == rid]
    psum = defaultdict(int)
    pu = defaultdict(set)
    for r in pr:
        psum[(r['precinct'][:2], int(r['cand_number']), 'tot')] += int(r['cand_tot_votes'])
        psum[(r['precinct'][:2], int(r['cand_number']), 'abs')] += int(r['cand_absmail_votes'])
        psum[(r['precinct'][:2], int(r['cand_number']), 'early')] += int(r['cand_early_votes'])
        psum[(r['precinct'][:2], int(r['cand_number']), 'eday')] += int(r['cand_elecday_votes'])
        pu[r['precinct'][:2]].add(r['precinct'])
    pm_bad = []
    for k, rs in by.items():
        code = COUNTY[k]['oseb_code']
        for r in rs:
            n = int(r['cand_number'])
            for f, key in [('cand_tot_votes', 'tot'), ('cand_absmail_votes', 'abs'), ('cand_early_votes', 'early'), ('cand_elecday_votes', 'eday')]:
                if psum[(code, n, key)] != int(r[f]):
                    pm_bad.append((k, n, key))
    check(f'{cid}: precinct CSV unit sums equal county CSV for every county/candidate/method', not pm_bad and set(pu) == {c['oseb_code'] for c in COUNTY.values()}, mismatches=pm_bad[:10], zip_member=pm, member_sha256=psha)
    nine = sorted(u for us in pu.values() for u in us if u.endswith('9999'))
    nine_detail = {}
    for u in nine:
        rr = [r for r in pr if r['precinct'] == u]
        nine_detail[u] = {'county': CENSUS_NAME[CODE2K[u[:2]]], 'absentee_mail': sum(int(r['cand_absmail_votes']) for r in rr),
                          'early': sum(int(r['cand_early_votes']) for r in rr), 'election_day': sum(int(r['cand_elecday_votes']) for r in rr),
                          'total': sum(int(r['cand_tot_votes']) for r in rr)}
        k = CODE2K[u[:2]]
        others = [r for r in pr if r['precinct'][:2] == u[:2] and r['precinct'] != u]
        nine_detail[u].update({'county_absentee_mail': col_sum(by[k], 'cand_absmail_votes'), 'county_early': col_sum(by[k], 'cand_early_votes'),
                               'geographic_precincts_absentee_mail_plus_early': sum(int(r['cand_absmail_votes']) + int(r['cand_early_votes']) for r in others)})
    check(f'{cid}: each 9999 unit holds all of its county absentee-mail and early votes; geographic precincts there hold election-day votes only',
          all(v['election_day'] == 0 and v['absentee_mail'] == v['county_absentee_mail'] and v['early'] == v['county_early'] and v['geographic_precincts_absentee_mail_plus_early'] == 0
              for v in nine_detail.values()), units=list(nine_detail))
    no9999 = [k for k in by if COUNTY[k]['oseb_code'] not in {u[:2] for u in nine}]
    alloc = sum(1 for k in no9999 if sum(int(r['cand_absmail_votes']) + int(r['cand_early_votes']) for r in pr if r['precinct'][:2] == COUNTY[k]['oseb_code']) == col_sum(by[k], 'cand_absmail_votes') + col_sum(by[k], 'cand_early_votes'))
    check(f'{cid}: in the other counties absentee-mail and early votes are carried on precinct rows', alloc == len(no9999), counties=len(no9999))
    counted = {k: int(rs[0]['tot_race_prec']) for k, rs in by.items()}
    excess = {CENSUS_NAME[CODE2K[c]]: [len(us), counted[CODE2K[c]]] for c, us in pu.items() if len(us) != counted[CODE2K[c]]}
    check(f'{cid}: precinct units exceed race precinct count only by the 9999 units', all(v[0] - v[1] == sum(1 for u in nine if CENSUS_NAME[CODE2K[u[:2]]] == c) for c, v in excess.items()),
          units_vs_precinct_count=excess, units_9999=nine_detail)
    units[cid] = {'precinct_export_units': sum(len(v) for v in pu.values()), 'race_precinct_count': sum(counted.values()),
                  'non_precinct_9999_units': nine_detail, 'note': 'Units ending 9999 carry only absentee-mail and early votes (zero election-day) and are outside the race precinct count; they are countywide reporting units without a precinct polygon.'}
    for k, rs in sorted(by.items(), key=lambda kv: FIPS[kv[0]]):
        for r in sorted(rs, key=lambda r: int(r['cand_number'])):
            long_rows.append({'contest_id': cid, 'election_date': date, 'race_number': rid, 'race_title': title, 'county': CENSUS_NAME[k].removesuffix(' County'),
                              'county_fips': FIPS[k], 'oseb_county_code': COUNTY[k]['oseb_code'], 'oker_county_label': r['county'],
                              'cand_number': r['cand_number'], 'cand_name': r['cand_name'], 'cand_party': r['cand_party'],
                              'absentee_mail_votes': r['cand_absmail_votes'], 'early_votes': r['cand_early_votes'],
                              'election_day_votes': r['cand_elecday_votes'], 'total_votes': r['cand_tot_votes']})

VOTES = {cid: {k: sum(int(r['cand_tot_votes']) for r in rs) for k, rs in contest_rows[cid].items()} for cid in CONTESTS}
METHOD = {cid: {k: [sum(int(r[f]) for r in rs) for f in ['cand_absmail_votes', 'cand_early_votes', 'cand_elecday_votes']] for k, rs in contest_rows[cid].items()} for cid in CONTESTS}
STATE = {cid: sum(int(r['cand_tot_votes']) for r in state_rows[cid]) for cid in CONTESTS}
for cid in CONTESTS:
    check(f'{cid}: county contest votes sum to statewide total', sum(VOTES[cid].values()) == STATE[cid], statewide=STATE[cid])

# ---------------------------------------------------------------- certified cross-checks
import pypdf  # noqa: E402  (only needed here)


def pdf_pages(key):
    return [p.extract_text() for p in pypdf.PdfReader(io.BytesIO(raw(key))).pages]


def surname(name):
    return re.sub(r'[^A-Z]', '', name.split('|')[0].split()[-1].upper())


controls = []
# NARA 2024 certificate of ascertainment: party/ticket headers paired with "N VOTES" in order.
nara = '\n'.join(pdf_pages('nara-2024-ascertainment-oklahoma'))
heads = re.findall(r'\(([A-Z. ]+?) for President', nara)
votes = [int(v.replace(',', '')) for v in re.findall(r'([\d,]{3,}) VOTES', nara)]
nara_map = {surname(h): v for h, v in zip(heads, votes)}
cert = {'pres2024': ('nara-2024-ascertainment-oklahoma', nara_map)}
# House Clerk statistics: Oklahoma section lines "Name, Party ....... N".
for key, cids in [('clerk-2022-statistics', ['sen2022s', 'sen2022r']), ('clerk-2020-statistics', ['sen2020', 'pres2020'])]:
    pages = pdf_pages(key)
    text = next(p for p in pages if re.search(r'^OKLAHOMA\n', p, re.M) and 'FOR UNITED STATES SENATOR' in p[p.index('OKLAHOMA\n'):])
    sec = text[text.index('OKLAHOMA\n'):]
    if 'FOR UNITED STATES REPRESENTATIVE' in sec:  # 2022: the House table starts on the next page
        sec = sec[:sec.index('FOR UNITED STATES REPRESENTATIVE')]
    if key == 'clerk-2022-statistics':
        un, full = sec.index('(For unexpired term ending January 3, 2027)'), sec.index('(For full term beginning January 3, 2023)')
        parts = {'sen2022s': sec[un:full], 'sen2022r': sec[full:]}
    else:
        parts = {'pres2020': sec[sec.index('FOR PRESIDENTIAL ELECTORS'):sec.index('FOR UNITED STATES SENATOR')], 'sen2020': sec[sec.index('FOR UNITED STATES SENATOR'):]}
    for cid in cids:
        lines = re.findall(r'^(.+?)\s*\.{3,}\s*([\d,]+)\s*$', parts[cid], re.M)
        if cid == 'pres2020':
            m = {party.strip().upper(): int(v.replace(',', '')) for party, v in lines}
        else:
            m = {surname(n.split(',')[0]): int(v.replace(',', '')) for n, v in lines}
        cert[cid] = (key, m)
for cid in ['pres2024', 'sen2022s', 'sen2022r', 'sen2020', 'pres2020']:
    src, m = cert[cid]
    if cid == 'pres2020':
        okp = defaultdict(int)
        for r in state_rows[cid]:
            okp[{'DEM': 'DEMOCRATIC', 'REP': 'REPUBLICAN', 'LIB': 'LIBERTARIAN', 'IND': 'INDEPENDENT'}[r['cand_party']]] += int(r['cand_tot_votes'])
        good = dict(okp) == m
        for p, v in okp.items():
            controls.append({'contest_id': cid, 'candidate_or_group': f'all {p} electors', 'party': p, 'oker_total': v, 'certified_source': src, 'certified_value': m.get(p), 'match': m.get(p) == v})
    else:
        good = len(m) == len(state_rows[cid])
        for r in state_rows[cid]:
            v = m.get(surname(r['cand_name']))
            good &= v == int(r['cand_tot_votes'])
            controls.append({'contest_id': cid, 'candidate_or_group': r['cand_name'], 'party': r['cand_party'], 'oker_total': int(r['cand_tot_votes']),
                             'certified_source': src, 'certified_value': v, 'match': v == int(r['cand_tot_votes'])})
    check(f'{cid}: every statewide candidate total equals certified federal publication ({src})', good, certified=m)
for r in state_rows['gov2022']:
    controls.append({'contest_id': 'gov2022', 'candidate_or_group': r['cand_name'], 'party': r['cand_party'], 'oker_total': int(r['cand_tot_votes']),
                     'certified_source': None, 'certified_value': None, 'match': None})

# ---------------------------------------------------------------- EIS voter history and registration
def county_slice(d, dim, measures):
    ds = d['ItemData']['DataStorageDTO']
    names = ds['EncodeMaps'][dim]
    sl = next(s for s in ds['Slices'] if s['KeyIds'] == [dim])
    vid = [sl['ValueIds'][m] for m in measures]
    out = {}
    for key, vals in sl['Data'].items():
        i = json.loads(key)[0]
        out[norm(names[i])] = (names[i], [vals[str(v)] for v in vid])
    grand = next(s for s in ds['Slices'] if s['KeyIds'] == [])
    return out, [grand['Data']['[]'][str(v)] for v in vid], ds


def party_total(ds, dim, measures):
    sl = next(s for s in ds['Slices'] if s['KeyIds'] == [dim])
    return [sum(v[str(sl['ValueIds'][m])] for v in sl['Data'].values()) for m in measures]


PART = {}
EIS_LABEL = {}
for vid, d in VH.items():
    piv = jraw(f'eis-vh-{d}-pivot')
    tot, grand, ds = county_slice(piv, 'DataItem0', ['DataItem3'])
    check(f'{vid}: EIS voter history pivot has 77 counties matching OKER', set(tot) == set(COUNTY))
    card = jraw(f'eis-vh-{d}-card')['ItemData']['DataStorageDTO']['Slices'][0]['Data']['[]']['0']
    pie = jraw(f'eis-vh-{d}-methods')['ItemData']['DataStorageDTO']
    pie_vals = dict(zip(pie['EncodeMaps']['DataItem0'], [pie['Slices'][0]['Data'][f'[{i}]']['0'] for i in range(len(pie['EncodeMaps']['DataItem0']))]))
    check(f'{vid}: county credits sum = pivot grand total = card = method pie sum = affiliation sum',
          sum(v[1][0] for v in tot.values()) == grand[0] == card == sum(pie_vals.values()) == party_total(ds, 'DataItem4', ['DataItem3'])[0],
          statewide=card, methods=pie_vals)
    meth = {}
    for mk, ml in VH_METHODS:
        mp, mg, _ = county_slice(jraw(f'eis-vh-{d}-pivot-{mk.replace("_", "-")}'), 'DataItem0', ['DataItem3'])
        absent = sorted(set(COUNTY) - set(mp))
        check(f'{vid}: {ml} filtered pivot grand total equals method pie', mg[0] == pie_vals[ml], counties_absent_from_filtered_pivot=[CENSUS_NAME[k] for k in absent])
        meth[mk] = {k: mp[k][1][0] if k in mp else 0 for k in COUNTY}
    check(f'{vid}: per-county method credits sum to county total', all(sum(meth[m][k] for m, _ in VH_METHODS) == tot[k][1][0] for k in COUNTY))
    PART[vid] = {k: tot[k][1][0] for k in COUNTY}
    PART[vid + '_methods'] = meth
    for k in COUNTY:
        EIS_LABEL.setdefault(k, tot[k][0])
        assert EIS_LABEL[k] == tot[k][0]
for rid, d in VR.items():
    piv = jraw(f'eis-vr-{d}-pivot')
    cnt, grand, ds = county_slice(piv, 'DataItem3', ['DataItem0', 'DataItem1'])
    card = jraw(f'eis-vr-{d}-card-total')['ItemData']['DataStorageDTO']['Slices'][0]['Data']['[]']['0']
    check(f'{rid}: EIS registration pivot has 77 counties', set(cnt) == set(COUNTY))
    check(f'{rid}: county active/inactive sums = grand total = affiliation sums; active+inactive = TotalVoters card',
          [sum(v[1][0] for v in cnt.values()), sum(v[1][1] for v in cnt.values())] == grand == party_total(ds, 'DataItem2', ['DataItem0', 'DataItem1']) and sum(grand) == card,
          active=grand[0], inactive=grand[1], total_card=card)
    PART[rid] = {k: cnt[k][1] for k in COUNTY}
    for k in COUNTY:
        assert EIS_LABEL[k] == cnt[k][0]
check('EIS county labels identical across voter-history and registration dashboards', len(EIS_LABEL) == 77)
# Official OSEB pre-election (November 1) county registration reports vs EIS month-end snapshots.
VR_PDF = {'reg20241031': 'oseb-vrstats-county-2024-11-01', 'reg20221031': 'oseb-vrstats-county-2022-11-01', 'reg20201031': 'oseb-vrstats-county-2020-11-01'}
VR_REPORT = {}
for rid, key in VR_PDF.items():
    text = '\n'.join(pdf_pages(key))
    parties = re.search(r'County \(1\) (\w+) \(2\) (\w+) \(3\) (\w+) \(4\) (\w+) Total', text).groups()
    run = re.search(r'by County\s*MESA (\d+/\d+/\d{4} \d+:\d\d [AP]M)', text).group(1)
    lines = re.findall(r'^(\d\d) ([A-Z][A-Z ]*?) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+)\s*$', text, re.M)
    gt = [int(x.replace(',', '')) for x in re.search(r'^Grand Total ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+)\s*$', text, re.M).groups()]
    rep = {}
    for code, name, *vals in lines:
        vals = [int(v.replace(',', '')) for v in vals]
        k = norm(name)
        assert COUNTY[k]['oseb_code'] == code, (code, name)
        rep[k] = {'parties': dict(zip(parties, vals[:4])), 'total': vals[4]}
    VR_REPORT[rid] = {'run': run, 'grand_total': gt[4], 'party_order': parties, 'counties': rep}
    check(f'{rid}: official Nov 1 county report has 77 counties coded 01-77; each party sum = county total; counties sum to Grand Total',
          len(rep) == 77 and set(rep) == set(COUNTY) and all(sum(v['parties'].values()) == v['total'] for v in rep.values())
          and sum(v['total'] for v in rep.values()) == gt[4] and [sum(v['parties'][p_] for v in rep.values()) for p_ in parties] == gt[:4],
          report_run=run, grand_total=gt[4])
    diff = {CENSUS_NAME[k]: (rep[k]['total'], sum(PART[rid][k])) for k in COUNTY if rep[k]['total'] != sum(PART[rid][k])}
    check(f'{rid}: every county total in the official Nov 1 report equals EIS month-end active+inactive', not diff, differences=diff)
release = raw('oseb-2024-11-04-registration-release').decode('utf-8', 'replace')
rel = dict(re.findall(r'<li>(20\d\d): ([\d,]+)', release))
check('2024-11-04 OSEB release Nov 1 totals equal the county reports (2024, 2020)',
      int(rel['2024'].replace(',', '')) == VR_REPORT['reg20241031']['grand_total'] and int(rel['2020'].replace(',', '')) == VR_REPORT['reg20201031']['grand_total'],
      release_values=rel)

# ---------------------------------------------------------------- rankings
MEASURES = {cid: VOTES[cid] for cid in CONTESTS}
MEASURES.update({vid: PART[vid] for vid in VH})
DESC = {cid: f'{CONTESTS[cid][2]} contest votes (all candidates)' for cid in CONTESTS}
DESC.update({vid: f'EIS voter history credits, election {d}' for vid, d in VH.items()})


def rank(values):
    order = sorted(values, key=lambda k: (-values[k], FIPS[k]))
    total = sum(values.values())
    cum, out, k80 = 0, [], None
    for i, k in enumerate(order, 1):
        cum += values[k]
        out.append((i, k, values[k], cum))
        if k80 is None and 5 * cum >= 4 * total:
            k80 = i
    return order, total, out, k80


PRI = {}
RANKS = {}
for m in RANKED:
    order, total, rows_, k80 = rank(MEASURES[m])
    RANKS[m] = {k: (i, cum) for i, k, v, cum in rows_}
    top15 = rows_[14][3]
    pre = rows_[k80 - 2][3]
    cross = rows_[k80 - 1]
    ok = 5 * pre < 4 * total <= 5 * cross[3]
    check(f'{m}: minimum-80% integer proof 5*S(k-1) < 4*T <= 5*S(k)', ok, k=k80, S_k_minus_1=pre, S_k=cross[3], T=total)
    check(f'{m}: ranking covers 77 unique counties and sums to denominator', len(order) == 77 and rows_[-1][3] == total)
    PRI[m] = {'measure': DESC[m], 'denominator': total,
              'ordering': 'descending value; ties by ascending county FIPS (no ties affect any boundary below)',
              'ties': sorted({v for v in MEASURES[m].values() if list(MEASURES[m].values()).count(v) > 1}),
              'top15': {'counties': [CENSUS_NAME[k].removesuffix(' County') for k in order[:15]], 'numerator': top15, 'pct': pct(top15, total)},
              'minimum_80pct': {'k': k80, 'counties': [CENSUS_NAME[k].removesuffix(' County') for k in order[:k80]], 'fips': [FIPS[k] for k in order[:k80]],
                                'numerator': cross[3], 'pct': pct(cross[3], total), 'preceding_numerator': pre, 'preceding_pct': pct(pre, total),
                                'crossing_county': CENSUS_NAME[cross[1]].removesuffix(' County'), 'crossing_fips': FIPS[cross[1]], 'crossing_value': cross[2],
                                'integer_proof': f'5*{pre}={5*pre} < 4*{total}={4*total} <= 5*{cross[3]}={5*cross[3]}',
                                'remainder_counties': 77 - k80, 'remainder_value': total - cross[3], 'remainder_pct': pct(total - cross[3], total)},
              'full_order': [{'rank': i, 'county': CENSUS_NAME[k].removesuffix(' County'), 'fips': FIPS[k], 'value': v, 'cumulative': cum, 'cumulative_pct': pct(cum, total)} for i, k, v, cum in rows_]}
base80 = set(PRI['pres2024']['minimum_80pct']['counties'])
base15 = set(PRI['pres2024']['top15']['counties'])
comparison = {}
for m in RANKED:
    s80 = set(PRI[m]['minimum_80pct']['counties'])
    s15 = set(PRI[m]['top15']['counties'])
    comparison[m] = {'min80_size': len(s80), 'min80_added_vs_pres2024': sorted(s80 - base80), 'min80_dropped_vs_pres2024': sorted(base80 - s80),
                     'top15_added_vs_pres2024': sorted(s15 - base15), 'top15_dropped_vs_pres2024': sorted(base15 - s15)}
union = sorted(set().union(*[set(PRI[m]['minimum_80pct']['counties']) for m in ['pres2024', 'sen2022s', 'sen2022r']]),
               key=lambda c: RANKS['pres2024'][norm(c)][0])
# The pres2024 minimum-80% set's share of each other measure (fixed-set coverage).
cover = {m: {'numerator': sum(MEASURES[m][norm(c)] for c in base80), 'denominator': PRI[m]['denominator'],
             'pct': pct(sum(MEASURES[m][norm(c)] for c in base80), PRI[m]['denominator'])} for m in RANKED}
union_cover = {m: {'numerator': sum(MEASURES[m][norm(c)] for c in union), 'denominator': PRI[m]['denominator'],
                   'pct': pct(sum(MEASURES[m][norm(c)] for c in union), PRI[m]['denominator'])} for m in RANKED}
check('top 15 (pres2024) contained in its minimum-80% set', base15 <= base80)

# ---------------------------------------------------------------- outputs
order = [k for k, _ in sorted(RANKS['pres2024'].items(), key=lambda kv: kv[1][0])]
fields = ['rank_pres2024', 'county', 'county_fips', 'census_county_name', 'oseb_county_code', 'oker_county_label', 'eis_county_label',
          'pres2024_contest_votes', 'pres2024_absentee_mail_votes', 'pres2024_early_votes', 'pres2024_election_day_votes',
          'pres2024_share_pct', 'pres2024_cumulative_votes', 'pres2024_cumulative_pct', 'pres2024_top15', 'pres2024_min80', 'pres2024_statewide_denominator',
          'vh2024_credits', 'vh2024_absentee', 'vh2024_early_voting', 'vh2024_election_day', 'vh2024_rank',
          'reg20241031_active', 'reg20241031_inactive', 'reg20241031_total',
          'sen2022s_contest_votes', 'sen2022s_absentee_mail_votes', 'sen2022s_early_votes', 'sen2022s_election_day_votes',
          'sen2022s_rank', 'sen2022s_share_pct', 'sen2022s_cumulative_pct', 'sen2022s_top15', 'sen2022s_min80', 'sen2022s_statewide_denominator',
          'sen2022r_contest_votes', 'sen2022r_rank', 'sen2022r_share_pct', 'sen2022r_top15', 'sen2022r_min80',
          'gov2022_contest_votes', 'vh2022_credits', 'vh2022_absentee', 'vh2022_early_voting', 'vh2022_election_day', 'vh2022_rank',
          'reg20221031_active', 'reg20221031_inactive', 'reg20221031_total',
          'sen2020_contest_votes', 'pres2020_contest_votes', 'vh2020_credits', 'vh2020_absentee', 'vh2020_early_voting', 'vh2020_election_day',
          'reg20201031_active', 'reg20201031_inactive', 'reg20201031_total',
          'reg20260930_active', 'reg20260930_inactive', 'reg20260930_total', 'research_date']
min80 = {m: set(norm(c) for c in PRI[m]['minimum_80pct']['counties']) for m in RANKED}
top15 = {m: set(norm(c) for c in PRI[m]['top15']['counties']) for m in RANKED}
with (DATA / 'county-turnout.csv').open('w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=fields, lineterminator='\n')
    w.writeheader()
    for k in order:
        row = {'rank_pres2024': RANKS['pres2024'][k][0], 'county': CENSUS_NAME[k].removesuffix(' County'), 'county_fips': FIPS[k], 'census_county_name': CENSUS_NAME[k],
               'oseb_county_code': COUNTY[k]['oseb_code'], 'oker_county_label': COUNTY[k]['oker_label'], 'eis_county_label': EIS_LABEL[k], 'research_date': '2026-10-18'}
        for cid in ['pres2024', 'sen2022s']:
            row[f'{cid}_contest_votes'] = VOTES[cid][k]
            row[f'{cid}_absentee_mail_votes'], row[f'{cid}_early_votes'], row[f'{cid}_election_day_votes'] = METHOD[cid][k]
            row[f'{cid}_share_pct'] = pct(VOTES[cid][k], STATE[cid])
            row[f'{cid}_cumulative_pct'] = pct(RANKS[cid][k][1], STATE[cid])
            row[f'{cid}_top15'] = k in top15[cid]
            row[f'{cid}_min80'] = k in min80[cid]
            row[f'{cid}_statewide_denominator'] = STATE[cid]
        row['pres2024_cumulative_votes'] = RANKS['pres2024'][k][1]
        row['sen2022s_rank'] = RANKS['sen2022s'][k][0]
        row.update({'sen2022r_contest_votes': VOTES['sen2022r'][k], 'sen2022r_rank': RANKS['sen2022r'][k][0], 'sen2022r_share_pct': pct(VOTES['sen2022r'][k], STATE['sen2022r']),
                    'sen2022r_top15': k in top15['sen2022r'], 'sen2022r_min80': k in min80['sen2022r'], 'gov2022_contest_votes': VOTES['gov2022'][k],
                    'sen2020_contest_votes': VOTES['sen2020'][k], 'pres2020_contest_votes': VOTES['pres2020'][k]})
        for vid in VH:
            row[f'{vid}_credits'] = PART[vid][k]
            for mk, _ in VH_METHODS:
                row[f'{vid}_{mk}'] = PART[vid + '_methods'][mk][k]
        row['vh2024_rank'], row['vh2022_rank'] = RANKS['vh2024'][k][0], RANKS['vh2022'][k][0]
        for rid in VR:
            a, i = PART[rid][k]
            row[f'{rid}_active'], row[f'{rid}_inactive'], row[f'{rid}_total'] = a, i, a + i
        w.writerow(row)
with (ROOT / 'county-candidate-method.csv').open('w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(long_rows[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(long_rows)
with (ROOT / 'statewide-controls.csv').open('w', newline='') as fh:
    srows = []
    for cid in CONTESTS:
        for r in state_rows[cid]:
            c = next((x for x in controls if x['contest_id'] == cid and x['candidate_or_group'] == r['cand_name']), None)
            srows.append({'contest_id': cid, 'election_date': CONTESTS[cid][0], 'race_title': CONTESTS[cid][1], 'cand_number': r['cand_number'], 'cand_name': r['cand_name'],
                          'cand_party': r['cand_party'], 'absentee_mail_votes': r['cand_absmail_votes'], 'early_votes': r['cand_early_votes'],
                          'election_day_votes': r['cand_elecday_votes'], 'total_votes': r['cand_tot_votes'],
                          'certified_source_id': c['certified_source'] if c else None, 'certified_value': c['certified_value'] if c else None,
                          'certified_match': c['match'] if c else None})
    for x in controls:
        if x['contest_id'] == 'pres2020':
            srows.append({'contest_id': 'pres2020', 'election_date': '20201103', 'race_title': CONTESTS['pres2020'][1], 'cand_number': '', 'cand_name': x['candidate_or_group'],
                          'cand_party': x['party'], 'absentee_mail_votes': '', 'early_votes': '', 'election_day_votes': '', 'total_votes': x['oker_total'],
                          'certified_source_id': x['certified_source'], 'certified_value': x['certified_value'], 'certified_match': x['match']})
    w = csv.DictWriter(fh, fieldnames=list(srows[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(srows)
(ROOT / 'priority-set.json').write_text(json.dumps({
    'primary_measure': 'pres2024', 'research_date': '2026-10-18',
    'note': 'Oklahoma has no 2024 U.S. Senate contest; 2024 president is the primary recent statewide volume measure. 2022 special Senate is the same-seat midterm comparator.',
    'measures': PRI, 'comparison_to_pres2024': comparison,
    'union_min80_pres2024_sen2022s_sen2022r': union,
    'pres2024_min80_fixed_set_coverage': cover, 'union_fixed_set_coverage': union_cover,
    'statewide_turnout_percent_display_only': {d: jraw(f'oker-{d}-getelec-sw')['turnoutPerc'] for d in ['20241105', '20221108', '20201103']}}, indent=1) + '\n')
(ROOT / 'reporting-units.json').write_text(json.dumps(units, indent=1) + '\n')
# Observation (not a pass/fail check): contest votes and voter-history credits are different measures.
pdiff = {}
for cid, vid in [('pres2024', 'vh2024'), ('sen2022s', 'vh2022'), ('sen2022r', 'vh2022'), ('gov2022', 'vh2022'), ('sen2020', 'vh2020'), ('pres2020', 'vh2020')]:
    over = sorted(((CENSUS_NAME[k].removesuffix(' County'), FIPS[k], VOTES[cid][k], PART[vid][k], PART[vid][k] - VOTES[cid][k]) for k in COUNTY if VOTES[cid][k] > PART[vid][k]), key=lambda x: x[4])
    pdiff[f'{cid}_vs_{vid}'] = {'statewide_contest_votes': STATE[cid], 'statewide_credits': sum(PART[vid].values()), 'statewide_credits_minus_votes': sum(PART[vid].values()) - STATE[cid],
                                'counties_with_contest_votes_above_credits': [dict(zip(['county', 'fips', 'contest_votes', 'credits', 'credits_minus_votes'], x)) for x in over]}
(ROOT / 'participation-differences.json').write_text(json.dumps({'note': 'Voter-history credits are voter-file participation records, not tabulated ballots. A county with more contest votes than credits shows the two cannot be subtracted to obtain undervotes or ballots.',
                                                                  'registration_reports': {r: {k: v for k, v in VR_REPORT[r].items() if k != 'counties'} for r in VR_REPORT},
                                                                  'comparisons': pdiff}, indent=1) + '\n')
# Markdown table
lines = ['| Rank | County | FIPS | 2024 president votes | Share | Cumulative | 80% set | 2022 special Senate votes | 2022 special rank | 2022 regular Senate votes | 2024 voter-history credits | Registered 2024-10-31 (active + inactive) |',
         '| ---: | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |']
for k in order:
    i, cum = RANKS['pres2024'][k]
    a, b = PART['reg20241031'][k]
    lines.append(f"| {i} | {CENSUS_NAME[k].removesuffix(' County')} | {FIPS[k]} | {VOTES['pres2024'][k]:,} | {pct(VOTES['pres2024'][k], STATE['pres2024'], 4)}% | {pct(cum, STATE['pres2024'], 4)}% | "
                 f"{'yes' if k in min80['pres2024'] else ''} | {VOTES['sen2022s'][k]:,} | {RANKS['sen2022s'][k][0]} | {VOTES['sen2022r'][k]:,} | {PART['vh2024'][k]:,} | {a + b:,} |")
table = '\n'.join(lines) + '\n'
(ROOT / 'ranking-table.md').write_text(table)
md = STATE_DIR / 'turnout.md'
if md.exists():
    check('turnout.md embeds the generated ranking table verbatim', table in md.read_text())
    links = re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)', md.read_text())
    missing = [l for l in links if not l.startswith('http') and not (STATE_DIR / l).exists()]
    check('turnout.md relative links resolve', not missing, missing=missing)
check('evidence: every manifest file verified by SHA-256 and < 40,000,000 bytes', all(r.get('path') is None or raw(r['id']) is not None for r in MANIFEST), files=sum(1 for r in MANIFEST if r.get('path')))
(ROOT / 'validation.json').write_text(json.dumps({'passed': all(c['passed'] for c in CHECKS), 'count': len(CHECKS),
                                                   'failed': [c['check'] for c in CHECKS if not c['passed']], 'checks': CHECKS}, indent=1) + '\n')
print('checks', len(CHECKS), 'failed', [c['check'] for c in CHECKS if not c['passed']])
for m in RANKED:
    p = PRI[m]
    print(m, p['denominator'], 'top15', p['top15']['pct'], 'min80 k', p['minimum_80pct']['k'], p['minimum_80pct']['pct'])
sys.exit(0 if all(c['passed'] for c in CHECKS) else 1)
