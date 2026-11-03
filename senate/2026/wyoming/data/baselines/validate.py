#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["openpyxl==3.1.5", "pypdf==6.21.1"]
# ///
"""Offline validation of the Wyoming partisanship package.  No downloads.

Recomputes controls from the long candidate file rather than trusting the
derived tables, re-checks scenario arithmetic from county rows, runs solver
unit tests, checks the report (verbatim generated tables, relative links,
headline values) and writes validation.json plus asset-manifest.json.

  uv run --with openpyxl==3.1.5 --with pypdf==6.21.1 python3 -I validate.py
"""
import collections, csv, gzip, hashlib, json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent
STATE = DATA.parent
REPORT = STATE / 'county-partisanship.md'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
import build  # noqa: E402  (our own module; used only for the solver unit tests)

CHECKS = []


def check(name, cond, detail=''):
    CHECKS.append({'check': name, 'passed': bool(cond), 'detail': detail})
    if not cond:
        print('FAIL', name, detail, file=sys.stderr)


def rows(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def near(a, b, tol):
    return abs(float(a) - float(b)) <= tol


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    meta = json.loads((ROOT / 'sources.json').read_text())
    # 1. source integrity -----------------------------------------------------
    ok = True
    for m in meta:
        stored = (ROOT / m['path']).read_bytes()
        body = gzip.decompress(stored)
        ok &= sha(stored) == m['stored_sha256'] and len(stored) == m['stored_bytes'] and sha(body) == m['original_sha256'] and len(body) == m['original_bytes'] and len(stored) < 40_000_000
    check('sources: every retained body matches stored and original SHA-256/bytes; each < 40 MB', ok, f'{len(meta)} sources')
    non200 = sorted(m['id'] for m in meta if m['http_status'] != 200)
    check('sources: only the expected unpublished 2026 pages are non-200', non200 == ['sos-2026-general-page', 'sos-2026-withdrawn-general-pdf'], ', '.join(non200))

    # 2. geography ---------------------------------------------------------------
    census = {r['COUNTYNAME'].removesuffix(' County'): '56' + r['COUNTYFP'] for r in csv.DictReader(gzip.decompress((ROOT / next(m['path'] for m in meta if m['id'] == 'census-wy-county-codes')).read_bytes()).decode().splitlines(), delimiter='|')}
    wide = rows(DATA / 'county-baselines.csv')
    check('geography: county-baselines.csv has 23 unique counties and 23 unique FIPS', len(wide) == 23 and len({r['county'] for r in wide}) == 23 and len({r['county_fips'] for r in wide}) == 23)
    check('geography: FIPS equal Census 2020 Wyoming county codes', {r['county']: r['county_fips'] for r in wide} == census and all(re.fullmatch(r'56\d{3}', f) for f in census.values()))
    cc = rows(ROOT / 'county-contests.csv')
    keys = list(build.SELECTED)
    for k in keys:
        g = [r for r in cc if r['contest_key'] == k]
        check(f'geography: {k} has 23 county rows + 1 statewide row with unique FIPS', len(g) == 24 and len({r['county_fips'] for r in g}) == 24 and {r['county'] for r in g} == set(census) | {'Total'})

    # 3. candidate sums from the long file ----------------------------------------
    cand = rows(ROOT / 'county-candidates.csv')
    grp = collections.defaultdict(lambda: collections.defaultdict(int))
    for r in cand:
        grp[r['contest_key'], r['column_position']]['Total' if r['county'] == 'Total' else 'sum'] += int(r['votes'])
    bad = [k for k, v in grp.items() if v['sum'] != v['Total']]
    check('sums: every candidate/write-in/over/under column of every statewide contest: 23-county sum == published Total row', not bad, f'{len(grp)} columns; mismatches {bad}')
    controls = rows(ROOT / 'state-controls.csv')
    check('sums: state-controls.csv has zero differences (including total ballots cast)', all(r['difference'] == '0' for r in controls), f'{len(controls)} controls')
    by = collections.defaultdict(list)
    for r in cand:
        by[r['contest_key'], r['county']].append(r)
    ok = True
    for r in cc:
        cs = by[r['contest_key'], r['county']]
        d = sum(int(c['votes']) for c in cs if c['column_kind'] == 'candidate' and c['party_code'] == 'D')
        rr = sum(int(c['votes']) for c in cs if c['column_kind'] == 'candidate' and c['party_code'] == 'R')
        oth = sum(int(c['votes']) for c in cs if c['column_kind'] == 'candidate' and c['party_code'] not in 'DR')
        wi = sum(int(c['votes']) for c in cs if c['column_kind'] == 'writein')
        ou = sum(int(c['votes']) for c in cs if c['column_kind'] in ('over', 'under'))
        ok &= (d, rr, oth, wi) == (int(r['d_votes']), int(r['r_votes']), int(r['named_other_votes']), int(r['writein_votes']))
        ok &= d + rr + oth + wi == int(r['contest_votes_candidates_plus_writein'])
        ok &= d + rr + oth + wi + ou == int(r['ballots_cast']) and r['ballots_identity_holds'] == 'True'
        ok &= near(r['d_pair_share'], d / (d + rr), 1e-15) and int(r['d_minus_r_net']) == d - rr
        ok &= near(r['d_minus_r_pair_margin'], 2 * d / (d + rr) - 1, 1e-12)
    check('balances: D/R/named-other/write-in recomputed from long file; D+R+other+write-in+over+under == county Total Ballots Cast for every selected contest row', ok, f'{len(cc)} rows')
    for k in keys:
        g = [r for r in cc if r['contest_key'] == k and r['county'] != 'Total']
        check(f'weights: {k} pair weights total 1 and county net shares total 1', near(sum(float(r['pair_weight']) for r in g), 1, 1e-12) and near(sum(float(r['share_of_statewide_net']) for r in g), 1, 1e-12))

    # 4. precinct and PDF controls --------------------------------------------------
    pc = rows(ROOT / 'precinct-aggregation-checks.csv')
    ncols = sum(len({r['column_position'] for r in cand if r['contest_key'] == k}) for k in keys)
    check('precincts: precinct-row sums and PbP Total rows equal county summaries for every selected contest cell', len(pc) == ncols * 23 and all(r['precinct_sum_equals_summary'] == 'True' and r['pbp_total_equals_summary'] == 'True' for r in pc), f'{len(pc)} cells')
    odd = [r for r in pc if r['precinct_nonnumeric_cells']]
    check('precincts: non-numeric source cells are recorded, not coerced', all(r['precinct_row_sum'] == r['county_summary_value'] for r in odd), '; '.join(f"{r['contest_key']} {r['county']} {r['native_header']}: {r['precinct_nonnumeric_cells']}" for r in odd))
    pdfc = rows(ROOT / 'pdf-crosscheck.csv')
    check('pdf: no compared PDF row differs from the XLSX', not [r for r in pdfc if r['equal'] == 'False'], f"{sum(r['equal'] == 'True' for r in pdfc)} equal rows")
    cov = collections.Counter(r['contest_key'] for r in pdfc if r['equal'] == 'True')
    check('pdf: each selected contest has 24 PDF-verified geography rows; ballots 24 per year', all(cov[k] == 24 for k in keys) and cov['total-ballots-cast'] == 72, json.dumps({k: cov[k] for k in keys + ['total-ballots-cast']}))

    # 5. scenarios ----------------------------------------------------------------
    st = rows(ROOT / 'state-scenarios.csv')
    ct = rows(ROOT / 'county-target-scenarios.csv')
    cgrp = collections.defaultdict(list)
    for r in ct:
        cgrp[r['scenario_id'], r['goal']].append(r)
    ok_w = ok_sum = ok_d1 = ok_rc = ok_closed = True
    stg = {(r['scenario_id'], r['goal']): r for r in st}
    for (sid, goal), g in cgrp.items():
        s = stg[sid, goal]
        T = float(s['pair_pool'])
        ok_w &= len(g) == 23 and near(sum(float(r['pair_weight']) for r in g), 1, 1e-12) and near(sum(float(r['scenario_pair_votes']) for r in g), T, 1e-6)
        ok_sum &= near(sum(float(r['scenario_pair_votes']) * (2 * float(r['target_d_pair_share']) - 1) for r in g), float(s['target_net']), 1e-6)
        ok_sum &= near(sum(float(r['target_net']) for r in g), float(s['target_net']), 1e-6) and all(0 <= float(r['target_d_pair_share']) <= 1 for r in g)
        ok_closed &= near(s['solved_d_share_shift'], s['closed_form_shift'], 1e-12) and s['clipped_counties'] == '0'
    for sid in {r['scenario_id'] for r in st}:
        t, d, rc = (float(stg[sid, g]['solved_d_share_shift']) for g in ('tie', 'D+1-pair-margin', 'D-outside-automatic-recount'))
        ok_d1 &= near(d - t, 0.005, 1e-12)
        ok_rc &= near(rc - t, 0.5 / 199, 1e-12)
        T = float(stg[sid, 'D-outside-automatic-recount']['pair_pool'])
        net = float(stg[sid, 'D-outside-automatic-recount']['target_net'])
        D, R = (T + net) / 2, (T - net) / 2
        ok_rc &= near(D - R, 0.01 * D, 1e-6)
    check('scenarios: every scenario has 23 county pools whose weights total 1 and sum to the pair pool', ok_w, f'{len(cgrp)} scenario/goal groups')
    check('scenarios: county target nets sum to the statewide goal (tie 0, D+1 = 0.01*T, recount boundary = T/199)', ok_sum)
    check('scenarios: no county clipped; solved shift equals closed form (target-M0)/(2T)', ok_closed)
    check('scenarios: D+1 pair margin needs exactly +0.5 D-share pp beyond the tie', ok_d1)
    check('scenarios: W.S. 22-16-109(b) boundary D-R = 1% of D needs +0.5/199 share beyond the tie', ok_rc)
    ok = True
    for k in keys:
        s = next(r for r in cc if r['contest_key'] == k and r['county'] == 'Total')
        D, R = int(s['d_votes']), int(s['r_votes'])
        ok &= near(stg[f'{k}__native-pair', 'tie']['solved_d_share_shift'], (R - D) / (2 * (D + R)), 1e-15)
    check('scenarios: native tie shift equals (R-D)/(2*(D+R)) from statewide totals for every baseline', ok)
    sel = rows(ROOT / 'selected-county-break-even.csv')
    ok = all(near(float(r['fixed_other_counties_net']) + float(r['selected_pair_votes']) * (2 * float(r['required_d_pair_share']) - 1), float(r['target_net']), 1e-6) for r in sel)
    ok &= all(r['status'] == ('already-secured' if float(r['required_d_pair_share']) < 0 else 'impossible' if float(r['required_d_pair_share']) > 1 else 'feasible') for r in sel)
    check('selected county: required share reproduces the goal with all other counties fixed; status labels consistent', ok, json.dumps(collections.Counter(r['status'] for r in sel)))
    # solver unit tests (synthetic)
    q = build.bounded_uniform([.99, .1], [100.0, 900.0], 0.0)
    t1 = q['status'] == 'bounded-feasible' and q['clipped'] == 1 and near(sum(t * (2 * min(1, max(0, s + q['solved_shift'])) - 1) for s, t in zip([.99, .1], [100, 900])), 0, 1e-6)
    q = build.bounded_uniform([.7], [100.0], 0.0)
    t2 = near(q['solved_shift'], -.2, 1e-12)  # already-winning baseline: negative shift
    t3 = build.bounded_uniform([.5], [100.0], 101.0)['status'] == 'impossible'
    check('solver tests: clipping re-solve, already-winning negative shift, impossible target', t1 and t2 and t3)
    sens = json.loads((ROOT / 'turnout-sensitivity.json').read_text())['rows']
    check('turnout: uniformly scaled county pools leave the share threshold unchanged', all(near(v, x['tie_shift_native'], 1e-12) for x in sens for v in x['tie_shift_uniformly_scaled_turnout'].values()))

    # 6. wide <-> long consistency ------------------------------------------------
    ccd = {(r['contest_key'], r['county']): r for r in cc}
    ok = True
    for w in wide:
        for k in keys:
            p = k.replace('-', '_') + '_'
            for f in ('d_votes', 'r_votes', 'named_other_votes', 'writein_votes', 'over_votes', 'under_votes', 'ballots_cast', 'pair_votes', 'd_pair_share', 'd_minus_r_net', 'pair_weight'):
                ok &= w[p + f] == ccd[k, w['county']][f]
        tie = next(r for r in ct if r['scenario_id'] == '2020-senate__native-pair' and r['goal'] == 'tie' and r['county'] == w['county'])
        ok &= w['scn_2020senate_native_tie_target_d_share'] == tie['target_d_pair_share']
    check('consistency: wide county-baselines.csv equals long county-contests.csv and scenario rows', ok)
    pri = json.loads((ROOT / 'priority-check.json').read_text())
    v = sorted(((int(ccd['2024-senate', n]['contest_votes_candidates_plus_writein']), n) for n in census), reverse=True)
    cum = [sum(x for x, _ in v[:i]) for i in range(1, 24)]
    k80 = next(i for i, c in enumerate(cum, 1) if 5 * c >= 4 * cum[-1])
    check('priority: independent 2024 Senate 80% set recomputed', k80 == pri['minimum_count_reaching_80pct'] and [n for _, n in v[:k80]] == pri['counties_in_80pct_set'] and 5 * cum[k80 - 2] < 4 * cum[-1], f'{k80} counties')

    # 7. slate ----------------------------------------------------------------------
    sl = json.loads((ROOT / 'slate-2026.json').read_text())
    us = sl['general_roster_csv']['us_senate_rows']
    check('slate: 2026 general roster lists exactly Hageman (REP) and Byrd (DEM) for U.S. Senator, none withdrawn; PDF agrees',
          [(r['Party Affiliation'], r['Ballot Name'], r['Date Withdrawn']) for r in us] == [('REP', 'Harriet Hageman', ''), ('DEM', 'James Byrd', '')]
          and sl['general_roster_pdf']['us_senate_entries'] == [['Republican', 'Harriet Hageman'], ['Democratic', 'James Byrd']])
    w = sl['primary_official_results']['winners']
    check('slate: official 2026 primary winners match the general roster; no Senate withdrawal or independent petition',
          w['Republican']['winner_header'] == 'Harriet Hageman' and w['Democratic']['winner_header'] == 'James Byrd'
          and not sl['withdrawn_primary_pdf']['mentions_us_senator'] and not sl['independent_petitions_page']['mentions_senate'])
    prim = rows(ROOT / 'primary-2026-us-senate.csv')
    pg = collections.defaultdict(lambda: collections.defaultdict(int))
    for r in prim:
        pg[r['party_primary'], r['native_header']]['Total' if r['county'] == 'Total' else 'sum'] += int(r['votes'])
    check('slate: 2026 primary Senate county sums equal published totals', all(v['sum'] == v['Total'] for v in pg.values()), f'{len(pg)} columns')

    # 8. report ------------------------------------------------------------------------
    if REPORT.exists():
        md = REPORT.read_text()
        tables = (ROOT / 'report-tables.txt').read_text().split('\n\n')
        missing = [t.splitlines()[0] for t in tables if t.strip() and t.strip() not in md]
        check('report: every generated table appears verbatim in county-partisanship.md', not missing, ', '.join(missing))
        links = re.findall(r'\]\((?!https?://|#)([^)\s]+)\)', md)
        broken = [l for l in links if not (STATE / l.split('#')[0]).exists()]
        check('report: relative Markdown links resolve', links and not broken, f'{len(links)} links; broken {broken}')
        head = stg['2020-senate__native-pair', 'tie']
        need = [f"{100 * float(head['solved_d_share_shift']):+.6f}", f"{100 * float(stg['2020-senate__native-pair', 'D+1-pair-margin']['solved_d_share_shift']):+.6f}"]
        check('report: headline tie and D+1 shifts present', all(n in md for n in need), ', '.join(need))
    else:
        check('report: county-partisanship.md exists', False)

    # 9. manifest -----------------------------------------------------------------------
    owned = [REPORT, DATA / 'county-baselines.csv'] + sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name not in ('asset-manifest.json', 'validation.json') and '__pycache__' not in p.parts)
    man = [{'path': str(p.relative_to(STATE)), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())} for p in owned if p.exists()]
    (ROOT / 'asset-manifest.json').write_text(json.dumps(man, indent=2) + '\n')
    check('assets: every owned file < 40,000,000 bytes', all(m['bytes'] < 40_000_000 for m in man), f'{len(man)} files, {sum(m["bytes"] for m in man):,} bytes')
    out = {'passed': all(c['passed'] for c in CHECKS), 'checks': CHECKS}
    (ROOT / 'validation.json').write_text(json.dumps(out, indent=2) + '\n')
    print(f"{sum(c['passed'] for c in CHECKS)}/{len(CHECKS)} checks passed")
    sys.exit(0 if out['passed'] else 1)


if __name__ == '__main__':
    main()
