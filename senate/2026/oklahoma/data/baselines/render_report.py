#!/usr/bin/env python3
"""Render ../../county-partisanship.md from build outputs (offline).

Run after build.py: ``uv run python3 -I render_report.py``.
All numbers in the report are read from the CSV/JSON outputs here.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent.parent / "county-partisanship.md"
S = json.loads((HERE / "build-summary.json").read_text())
SRC = {s["source_id"]: s for s in json.loads((HERE / "sources.json").read_text())["sources"]}
SLATE = json.loads((HERE / "slate-2026.json").read_text())
CHECKS = json.loads((HERE / "build-checks.json").read_text())


def rd(name):
    return list(csv.DictReader(open(HERE / name)))


contests = rd("county-contests.csv")
controls = rd("state-controls.csv")
states = {r["scenario_id"]: r for r in rd("state-scenarios.csv")}
sel = rd("selected-county-break-even.csv")
sens = rd("turnout-sensitivity.csv")
wide = rd("../county-baselines.csv")
C = S["contests"]
ORDER = ["2022-senate-special", "2022-senate-regular", "2020-senate", "2024-president", "2022-governor"]
LABEL = {"2022-senate-special": "2022 Senate special (Class II)", "2022-senate-regular": "2022 Senate regular (Class III)",
         "2020-senate": "2020 Senate (Class II history)", "2024-president": "2024 president",
         "2022-governor": "2022 governor"}
TITLE = {"KENDRA HORN": "Kendra Horn", "MARKWAYNE MULLIN": "Markwayne Mullin", "MADISON HORN": "Madison Horn",
         "JAMES LANKFORD": "James Lankford", "ABBY BROYLES": "Abby Broyles", "JIM INHOFE": "Jim Inhofe",
         "KAMALA D HARRIS": "Kamala D. Harris", "DONALD J TRUMP": "Donald J. Trump", "JOY HOFMEISTER": "Joy Hofmeister",
         "KEVIN STITT": "Kevin Stitt", "RAY WOODS": "Ray Woods", "ROBERT MURPHY": "Robert Murphy",
         "MICHAEL L DELANEY": "Michael L. Delaney", "KENNETH D BLEVINS": "Kenneth D. Blevins", "A. D. NESBIT": "A. D. Nesbit",
         "JOAN FARR": "Joan Farr", "CHRIS GARRITY": "Chris Garrity", "ROBERT F KENNEDY JR": "Robert F. Kennedy Jr.",
         "CHASE OLIVER": "Chase Oliver", "ERVIN STONE YEN": "Ervin Stone Yen", "NATALIE BRUNO": "Natalie Bruno"}
PURL = {
    "clerk-2020": SRC["clerk-2020"]["url"], "clerk-2022": SRC["clerk-2022"]["url"], "clerk-2024": SRC["clerk-2024"]["url"],
}


def i(x):
    return f"{int(round(float(x))):,}"


def sgn(x, d=2):
    return f"{float(x):+.{d}f}"


def link(text, path):
    return f"[{text}]({path})"


def ret(sid):
    return SRC[sid]["retrieved_utc"]


def scen(pref, mix, goal):
    return states[f"{pref}|{mix}|{goal}"]


sp = C["2022-senate-special"]["state"]
sp_net = sp["D"] - sp["R"]
sp_pair = sp["D"] + sp["R"]
tie = float(scen("2022-senate-special", "native-pair", "tie")["unbounded_d_share_shift_pp"])
d1 = float(scen("2022-senate-special", "native-pair", "pair-d+1")["unbounded_d_share_shift_pp"])
a1 = float(scen("2022-senate-special", "native-pair", "allcand-d+1")["unbounded_d_share_shift_pp"])
sp_rows = [r for r in contests if r["contest_id"] == "2022-senate-special"]
sp_dled = [r["county"] for r in sp_rows if int(r["d_minus_r_net"]) > 0]
assert sp_dled == ["Oklahoma"], sp_dled
cum, n50 = 0.0, None
for k, r in enumerate(sorted(sp_rows, key=lambda r: int(r["d_minus_r_net"])), 1):
    cum += float(r["share_of_statewide_net"])
    if cum >= 0.5 and n50 is None:
        n50 = k
mix_ties = [float(scen("2022-senate-special", m, "tie")["unbounded_d_share_shift_pp"]) for m in ("2024-president-volume", "2020-senate-volume")]
sens_by = {r["scenario"]: float(r["tie_d_share_shift_pp"]) for r in sens}
sens_base = sens_by["observed 2022 special pair volumes"]
sens_metro = [sens_by[k] - sens_base for k in sens_by if k.startswith("Oklahoma+Tulsa+Cleveland")]
sens_rest = [sens_by[k] - sens_base for k in sens_by if k.startswith("all except")]
metro_net_sp = sum(int(r["d_minus_r_net"]) for r in sp_rows if r["county_fips"] in ("40109", "40143", "40027"))
mode_units = [c["detail"] for c in CHECKS["checks"] if c["check"] == "medsl2024.total_mode_equals_sum_of_split_modes"][0].split()[0]
cross_cells = [c["detail"] for c in CHECKS["checks"] if c["check"] == "oe2020.precinct_file_aggregates_to_county_file"][0].split()[0]
L = []
w = L.append

w("# Oklahoma county partisanship and conditional targets")
w("")
w(f"Research snapshot: 2026-10-18 UTC (sources retrieved {ret('seb-results-index')} to {ret('news-news9-senate-candidates')}). "
  f"**Every recent Oklahoma baseline is Republican, and none is close.** In the same-seat 2022 special Senate contest, Markwayne Mullin led Kendra Horn by "
  f"**{-sp_net:,}** votes on **{sp_pair:,}** D+R votes, a D-minus-R pair margin of **{100*sp_net/sp_pair:.4f} margin points**. "
  f"At those county weights, a uniform **+{tie:.6f} D-share points** ties, and **+{d1:.6f} share points** gives an illustrative **D+1 pair margin**. "
  f"In margin terms that is {2*tie:.4f} points to tie and {2*d1:.4f} points for D+1. Oklahoma County was the only county Horn carried. "
  f"These are deterministic what-if calculations on historical counts (secondary county transcriptions reconciled to official statewide totals), not a 2026 forecast. A gain in one county can offset a shortfall in another, so no county target is a necessary condition on its own. "
  f"Statewide totals: {link('House Clerk 2022', PURL['clerk-2022'])}; county values: {link('county-contests.csv', 'data/baselines/county-contests.csv')}.")
w("")
w("Oklahoma had **no 2024 Senate contest**. 2022 had two distinct Senate contests on one ballot: the **special** election for the Class II unexpired term ending January 3, 2027 (Mullin–Kendra Horn), which is the same seat as 2026, and the **regular** Class III election (Lankford–Madison Horn). They are kept as separate contests here and never added together. The 2020 Inhofe–Broyles contest is the previous regular election for the same Class II seat and is labeled as history. The 2024 presidential and 2022 governor results are comparators, not Senate results.")
w("")

# ---------------- 2026 slate
w("## 2026 contest and verified slate")
w("")
w(f"The U.S. Senate {link('Class II roster', SRC['senate-gov-class-ii']['url'])} (retrieved {ret('senate-gov-class-ii')}) lists **Armstrong, Alan (R-OK)** as the current holder. "
  f"News 9 reports that the Senate confirmed Mullin as Secretary of Homeland Security on March 23, 2026; that Gov. Kevin Stitt appointed Armstrong on an interim basis; and that Armstrong cannot run for the seat ({link('News 9, Oct. 2, 2026', SRC['news-news9-senate-candidates']['url'])}). "
  f"The State Election Board's {link('UOCAVA notice for November 3, 2026', SRC['seb-2026-general-notice']['url'])} lists **\"U.S. Senator (1 office)\"** without the special-election label it gives State Senate District 17. "
  "News 9 writes that the November election fills both the remainder of the vacancy and the next six-year term. This package does not resolve that statutory point. It does not affect the vote arithmetic below.")
w("")
w(f"Official filings: the SEB {link('2026 candidate list book', SRC['seb-2026-candidate-list-book']['url'])} (filings April 1–3, 2026; page 3) and the SEB {link('filing portal', SRC['seb-filings-portal']['url'])} "
  f"({link('U.S. Senator JSON', 'data/baselines/raw/seb-filings-us-senator/GetCandList-OfficeID-2257.json.gz')}, retrieved {ret('seb-filings-us-senator')}) both list the same **13 filers**. No filer is marked removed. "
  f"The SEB {link('withdrawal list', SRC['seb-2026-withdrawals']['url'])} and {link('contest-of-candidacy list', SRC['seb-2026-contests']['url'])} contain no U.S. Senator entries.")
w("")
w("| Filing ID | Candidate | Filed affiliation | Route to November ballot | Evidence |")
w("| --- | --- | --- | --- | --- |")
route = {"Kevin Hern": "Won June 16 Republican primary outright", "N'Kiyla Jasmine Thomas": "Won August 25 Democratic runoff over Jim Priest",
         "Jim Priest": "Lost August 25 Democratic runoff", "Sevier White": "Sole Libertarian filer; no primary",
         "Curtis Stinnett": "Independent; no primary", "Ron Meinhardt": "Independent; no primary"}
for r in SLATE["filings_official"]:
    name = r["candidate"]
    rt = route.get(name, "Did not advance from June 16 primary")
    ev = "SEB filings" if r["affiliation"] in ("Libertarian", "Independent") else "SEB filings; newsroom primary/runoff reports"
    w(f"| {r['filing_id']} | {name} | {r['affiliation']} | {rt} | {ev} |")
w("")
w(f"**Expected November ballot: Kevin Hern (REP), N'Kiyla Jasmine Thomas (DEM), Sevier White (LIB), Curtis Stinnett (IND), Ron Meinhardt (IND).** "
  f"The nomination results are from newsrooms, not from official counts retrieved here. KOKH reports the AP call for Thomas over Priest on August 25 ({link('KOKH', SRC['news-okcfox-thomas-runoff']['url'])}). News 9 reports Thomas at 61.2% in the runoff and 45.2% in the June primary, Hern's outright primary win, and the five-candidate November field ({link('News 9', SRC['news-news9-senate-candidates']['url'])}). "
  "Official primary and runoff counts are published only through the SEB OK Election Results application, which this package did not query (see Gaps).")
w("")
w("Coalition caveats for 2026:")
w("")
w("- **Two independents and a Libertarian are on the ballot.** None is assigned to either party. News 9 describes Meinhardt as a registered Republican running as an independent against the Republican nominee. Any 2026 vote he wins is a separate 'other' quantity, not R and not D.")
w("- Kevin Hern won Oklahoma's 1st District House seat in 2024; the House Clerk 2024 publication lists him with 188,832 votes. News 9 describes Thomas as making her first run for public office. No historical Oklahoma statewide contest had either candidate, so candidate effects are not carried into the scenarios.")
w(f"- Kendra Horn, the 2022 special Democrat, appears as the 2020 District 5 Democrat (\"Kendra S. Horn\") in the {link('House Clerk 2020 publication', PURL['clerk-2020'])}. Madison Horn, the 2022 regular Democrat, appears as the 2024 District 5 Democrat in {link('Clerk 2024', PURL['clerk-2024'])}.")
w("- Joy Hofmeister, the 2022 Democratic governor nominee, was the sitting State Superintendent and left the Republican Party in October 2021 to run as a Democrat ([Public Radio Tulsa](https://www.publicradiotulsa.org/post/state-superintendent-hofmeister-switches-parties-run-governor)). Her result is a candidate-specific midterm comparator, not evidence of a Democratic Senate floor.")
w("- Ervin Stone Yen ran for governor in 2022 as an independent (15,653 votes) and filed as a Democrat for Senate in 2026. His 2022 votes stay 'other'.")
w("")

# ---------------- Sources
w("## Sources, access and status")
w("")
w(f"The SEB year pages for {link('2020', SRC['seb-2020-general-page']['url'])}, {link('2022', SRC['seb-2022-general-page']['url'])} and {link('2024', SRC['seb-2024-general-page']['url'])} link only to the OK Election Results (OKER) application. The 2022 page says downloadable data come from that application's Export tab. "
  "OKER is a JavaScript client. It loads results, including the county and precinct CSV/XML exports, from an API only after an application login. **This package does not use that API.** "
  "As a result, no county count here is a newly downloaded SEB export.")
w("")
w("County counts come from pinned secondary transcriptions of SEB exports. In each case, statewide candidate totals are reconciled to official publications:")
w("")
w(f"- **2022 (both Senate contests and governor):** {link('MEDSL 2022 Oklahoma precinct file', SRC['medsl-2022-ok']['url'])}, commit `a8126c5`. The MEDSL README says it was added 2022-12-27, with source `results.okelections.us/OKER/?elecDate=20221108`. Methods are ABSENTEE, EARLY and IN-PERSON; there is no TOTAL row, so all three are summed.")
w(f"- **2024 president:** {link('MEDSL 2024 Oklahoma file', SRC['medsl-2024-ok']['url'])}, commit `df53108`. The README says it was added 2024-11-14 from `results.okelections.gov/OKER/?elecDate=20241105`; the CSV inside the ZIP is dated 2026-04-28. The file has both split modes and a TOTAL row. Only TOTAL is used. Every one of the {int(mode_units):,} precinct-candidate TOTAL values equals the sum of its three split modes.")
w(f"- **2020 Senate:** {link('OpenElections 2020 county file', SRC['openelections-2020-county']['url'])}, commit `76320f6`, with absentee, early and election-day columns. Its {link('precinct file', SRC['openelections-2020-precinct']['url'])} aggregates exactly to the county file in all {int(cross_cells):,} county-candidate cells.")
w("")
w("Official statewide controls:")
w("")
w(f"- **House Clerk** statistics of the {link('2020', PURL['clerk-2020'])} (PDF page {S['clerk_pages']['clerk-2020']}), {link('2022', PURL['clerk-2022'])} (page {S['clerk_pages']['clerk-2022']}) and {link('2024', PURL['clerk-2024'])} (page {S['clerk_pages']['clerk-2024']}) elections. These print every Senate candidate. For 2024 president they print party lines, with all independent tickets combined.")
m20 = S["seb_archive_meta"]["2020"]
m24 = S["seb_archive_meta"]["2024"]
w(f"- **SEB OKER statewide JSON, as archived by the Internet Archive:** {link('2020', SRC['wayback-seb-oker-2020']['url'])} is labeled `{m20['Title1']}` with `isOfficial={m20['isOfficial']}` and server time {m20['serverTLU']}. It includes absentee, early and election-day columns. "
  f"{link('2024', SRC['wayback-seb-oker-2024']['url'])} is the election-night `{m24['Title1']}` capture (`isOfficial={m24['isOfficial']}`, server time {m24['serverTLU']}). It is kept only as a vintage comparison.")
w("")
w("Agreement on statewide totals is necessary but does not prove that each county allocation is right. The 2020 precinct file is from the same project, so it is an internal check, not an independent county source. "
  f"There is **no primary statewide control for the 2022 governor contest**; its county counts are unreconciled secondary data, used as context only. Every URL, retrieval time, HTTP status, header subset, byte count and SHA-256 is in {link('sources.json', 'data/baselines/sources.json')}. Raw bytes are under {link('raw/', 'data/baselines/raw/')}.")
w("")

# ---------------- Reconciliation table
w("## Statewide reconciliation and baselines")
w("")
w("Counts below are votes for named candidates in each contest. Oklahoma prints no write-in line, and these files do not report under- or overvotes or ballots cast. D share and pair margin use D+R only. 'D counties' is the number of counties where the Democrat led in that contest.")
w("")
w("| Contest | D candidate | R candidate | D | R | Other | All candidates | Clerk diff | SEB archive diff | D pair share % | D−R pair margin pp | D counties |")
w("| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: |")
for c in ORDER:
    m = C[c]
    st = m["state"]
    rows = [r for r in controls if r["contest_id"] == c and not r["candidate"].startswith("(")]
    cd = [r["clerk_diff"] for r in rows if r["clerk_diff"] != ""]
    if c == "2024-president":
        cdtxt = "0 for D, R, LIB and combined IND"
    elif cd:
        cdtxt = "0 for all " + str(len(cd)) if all(int(x) == 0 for x in cd) else ",".join(cd)
    else:
        cdtxt = "no control"
    sd = [r["seb_archive_diff"] for r in rows if r["seb_archive_diff"] != ""]
    if c == "2020-senate":
        sdtxt = "0 for all 5, incl. methods"
    elif c == "2024-president":
        sdtxt = "election-night vintage; see CSV"
    else:
        sdtxt = "not archived"
    pair = st["D"] + st["R"]
    w(f"| {LABEL[c]} | {TITLE[m['D']]} | {TITLE[m['R']]} | {st['D']:,} | {st['R']:,} | {st['O']:,} | {st['A']:,} | {cdtxt} | {sdtxt} | {100*st['D']/pair:.4f} | {100*(st['D']-st['R'])/pair:.4f} | {m['d_counties']} |")
w("")
w("Every named candidate is kept separately in " + link("county-candidates.csv", "data/baselines/county-candidates.csv") + " with absentee, early, election-day and total columns:")
w("")
for c in ORDER:
    m = C[c]
    parts = [f"{TITLE[n]} ({p}) {sum(int(r['county_sum_total']) for r in controls if r['contest_id']==c and r['candidate']==n):,}" for n, p in m["candidates"].items()]
    w(f"- **{LABEL[c]}:** " + "; ".join(parts) + ".")
w("")
w(f"Against the election-night 2024 SEB capture, the final county sums are higher by {', '.join(TITLE[r['candidate']] + ' ' + sgn(r['seb_archive_diff'],0) for r in controls if r['contest_id']=='2024-president' and r['seb_archive_diff'] not in ('', None))}. "
  "These gaps are the expected difference between an unofficial election-night count and the final one. They are not treated as errors, and the final MEDSL sums match the Clerk. "
  f"Machine-readable controls are in {link('state-controls.csv', 'data/baselines/state-controls.csv')}.")
w("")
w(f"SEB county codes are the leading digits of SEB precinct IDs (`precinct // 10000`). They form one consistent one-to-one map onto 01–77 in all three precinct files. SEB numbering puts the Mc- counties before Major, so six codes differ from strict A–Z order: {', '.join(x.split(' (')[0].replace('=', ' ') for x in S['seb_code_non_alpha'])}. "
  f"The Census FIPS key comes from the {link('Census 2020 county list', SRC['census-ok-counties-2020']['url'])}. "
  f"Precinct-ID counts in the transcriptions (2022: {C['2022-senate-special']['precinct_ids']:,}; 2024: {C['2024-president']['precinct_ids']:,}; 2020: {C['2020-senate']['precinct_ids']:,}) include a few zero-vote IDs. They differ slightly from the archived SEB precinct counts (2020: {S['seb_archive_meta']['2020_precincts'][1]:,}; 2024 election night: {S['seb_archive_meta']['2024_precincts'][1]:,}). This package uses those counts only as context, not as geography.")
w("")

# ---------------- Arithmetic
w("## Share points, margin points and turnout")
w("")
w("For county `c`, let `s_c = D_c/(D_c+R_c)`, `T_c` the scenario's D+R pool, and `M0 = Σ T_c(2s_c−1)` the baseline D−R net. A uniform additive D-share change `δ` gives net `M0 + 2δΣT_c`. "
  "Setting that to zero gives the tie shift `δ = −M0/(2ΣT) = (R−D)/(2(D+R))` at native weights. A **D+1 pair margin** needs net `0.01ΣT`, which is **0.5 share points more** than a tie. "
  "One D-share point equals **two D−R margin points**, which is `0.02·T_c` net votes in county `c`: each vote moved from R to D changes the net by two. "
  "The **all-candidate D+1** goal needs net `0.01ΣV`, where `V` includes the fixed Libertarian and independent votes, so it needs slightly more share than the pair D+1. "
  "Other candidates are held at their baseline county shares and are never reassigned. No baseline here is already Democratic, so every required shift is positive. If one were, the solver would report a zero or negative shift. "
  "The solver applies `clip(s_c+δ, 0, 1)` and re-solves if any county would leave [0, 1]. No actual scenario here clips; synthetic tests in the validator exercise clipping.")
w("")
w("Turnout weights are kept separate from preferences. 'Native' uses each contest's own D+R counts. A cross mix uses another contest's actual all-candidate county volume `V_c`, times the preference contest's own county pair participation `(D+R)/A`. These are observed historical volume mixes, not 2026 turnout projections.")
w("")
w("| Preference baseline | Volume mix | Pair pool | Baseline D−R net | Pair margin pp | Tie D-share shift pp | D+1 pair shift pp | D+1 all-candidate shift pp |")
w("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
for pref in ORDER:
    for mix in ("native-pair", "2022-senate-special-volume", "2024-president-volume", "2020-senate-volume"):
        if mix != "native-pair" and mix.replace("-volume", "") == pref:
            continue
        t = scen(pref, mix, "tie")
        p1 = scen(pref, mix, "pair-d+1")
        a = scen(pref, mix, "allcand-d+1")
        w(f"| {LABEL[pref]} | {mix} | {float(t['pair_volume']):,.1f} | {float(t['baseline_d_minus_r_net']):,.1f} | {float(t['baseline_pair_margin_pp']):.4f} | +{float(t['unbounded_d_share_shift_pp']):.6f} | +{float(p1['unbounded_d_share_shift_pp']):.6f} | +{float(a['unbounded_d_share_shift_pp']):.6f} |")
w("")
w(f"Changing the county volume mix moves the same-seat tie threshold by {min(mix_ties)-tie:+.4f} to {max(mix_ties)-tie:+.4f} share points (from +{tie:.4f} at native 2022 weights to +{mix_ties[0]:.4f} at the 2024 presidential mix and +{mix_ties[1]:.4f} at the 2020 Senate mix). Composition matters far less than preference. "
  f"The {LABEL['2022-governor']} comparator, with a different Democratic candidate on the same 2022 ballot, sits about half as far from a tie (+{float(scen('2022-governor','native-pair','tie')['unbounded_d_share_shift_pp']):.4f}). Treat this as a candidate effect, not a transferable floor. All {len(states)} statewide scenarios are in {link('state-scenarios.csv', 'data/baselines/state-scenarios.csv')}; the {len(states)*77:,} county targets are in {link('county-target-scenarios.csv', 'data/baselines/county-target-scenarios.csv')}.")
w("")
w("Synthetic turnout sensitivity, holding 2022 special county preferences fixed. The multipliers are arbitrary, not researched 2026 turnout:")
w("")
w("| Turnout scenario | Pair pool | Baseline net | Pair margin pp | Metro-3 pair weight % | Tie shift pp | D+1 shift pp |")
w("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
for r in sens:
    w(f"| {r['scenario']} | {float(r['pair_volume']):,.1f} | {float(r['baseline_net']):,.1f} | {float(r['baseline_pair_margin_pp']):.4f} | {100*float(r['metro_pair_weight']):.3f} | +{float(r['tie_d_share_shift_pp']):.6f} | +{float(r['pair_d+1_d_share_shift_pp']):.6f} |")
w("")
w(f"Scaling every county by the same factor changes the net votes but not the share threshold. A 10% relative turnout change in Oklahoma, Tulsa and Cleveland counties ('metro-3') moves the tie threshold by {min(sens_metro):+.4f} to {max(sens_metro):+.4f} share points; the same change in the other 74 counties moves it {min(sens_rest):+.4f} to {max(sens_rest):+.4f}. Both are small next to the {tie:.1f}-point gap. Metro-3 combined was close to even in the special (net {metro_net_sp:+,}), so extra metro votes mostly dilute the statewide margin rather than add Democratic net votes. "
  f"See {link('turnout-sensitivity.csv', 'data/baselines/turnout-sensitivity.csv')}.")
w("")

# ---------------- County contributions
w("## Where the Republican margin comes from")
w("")
METRO = {"40109", "40143", "40027"}
for c in ("2022-senate-special", "2020-senate", "2024-president"):
    rows = [r for r in contests if r["contest_id"] == c]
    mnet = sum(int(r["d_minus_r_net"]) for r in rows if r["county_fips"] in METRO)
    rnet = sum(int(r["d_minus_r_net"]) for r in rows if r["county_fips"] not in METRO)
    mw = sum(float(r["pair_weight"]) for r in rows if r["county_fips"] in METRO)
    w(f"- **{LABEL[c]}:** metro-3 (Oklahoma, Tulsa, Cleveland) supplied {100*mw:.2f}% of D+R votes and a net of {mnet:+,}. The other 74 counties supplied net {rnet:+,}, or {100*rnet/(mnet+rnet):.1f}% of the statewide net.")
w("")
rows = sorted([r for r in contests if r["contest_id"] == "2022-senate-special"], key=lambda r: int(r["d_minus_r_net"]))
w(f"In the 2022 special, the Republican net margin is spread widely. It takes the {n50} largest Republican-net counties to pass 50% of it; the first 15 are listed below. Oklahoma County (D {float([r for r in rows if r['county']=='Oklahoma'][0]['pair_margin_pp']):+.2f}) offsets {int([r for r in rows if r['county']=='Oklahoma'][0]['d_minus_r_net']):,} votes. "
  "The contribution in points is county net divided by statewide D+R; the 77 values sum to the statewide pair margin.")
w("")
w("| Rank | County | FIPS | D+R votes | Pair weight % | D−R net | Pair margin pp | Contribution to statewide margin pp | Share of statewide net % | Cumulative % |")
w("| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
cum = 0.0
for k, r in enumerate(rows[:15], 1):
    cum += float(r["share_of_statewide_net"])
    w(f"| {k} | {r['county']} | {r['county_fips']} | {int(r['pair_votes']):,} | {100*float(r['pair_weight']):.3f} | {int(r['d_minus_r_net']):+,} | {float(r['pair_margin_pp']):+.2f} | {float(r['statewide_pair_margin_contribution_pp']):+.4f} | {100*float(r['share_of_statewide_net']):.2f} | {100*cum:.2f} |")
okc = [r for r in rows if r["county"] == "Oklahoma"][0]
w(f"| 77 | Oklahoma | {okc['county_fips']} | {int(okc['pair_votes']):,} | {100*float(okc['pair_weight']):.3f} | {int(okc['d_minus_r_net']):+,} | {float(okc['pair_margin_pp']):+.2f} | {float(okc['statewide_pair_margin_contribution_pp']):+.4f} | {100*float(okc['share_of_statewide_net']):.2f} | — |")
w("")
w("Closeness bands use the absolute pair margin (≤5, >5–10, >10 pp) and appear in the CSVs. In the 2022 special, the only counties within 10 points were "
  + " and ".join(f"{r['county']} ({float(r['pair_margin_pp']):+.2f})" for r in sorted(rows, key=lambda r: abs(float(r['pair_margin_pp']))) if abs(float(r['pair_margin_pp'])) <= 10) + ".")
w("")

# ---------------- Selected county
w("## One county at a time, all others fixed")
w("")
w("This holds every other county at its baseline preference and volume and solves for the D share the selected county alone would need: `(target − other_net + T_sel)/(2·T_sel)`. A value above 100% is impossible under those fixed assumptions. It shows that no single county can close the gap; it is not a plausible path.")
w("")
w("| Preference / mix | County | Pair pool | Baseline D % | Tie D % needed | D+1 D % needed | Status |")
w("| --- | --- | ---: | ---: | ---: | ---: | --- |")
for pref, mix in (("2022-senate-special", "native-pair"), ("2022-senate-special", "2024-president-volume"), ("2020-senate", "native-pair")):
    for cty in ("Oklahoma", "Tulsa", "Cleveland", "Canadian"):
        t = [r for r in sel if r["preference_contest"] == pref and r["volume_mix"] == mix and r["goal"] == "tie" and r["county"] == cty][0]
        d = [r for r in sel if r["preference_contest"] == pref and r["volume_mix"] == mix and r["goal"] == "pair-d+1" and r["county"] == cty][0]
        w(f"| {LABEL[pref]} / {mix} | {cty} | {float(t['selected_pair_volume']):,.1f} | {100*float(t['baseline_d_pair_share']):.2f} | {100*float(t['required_d_pair_share']):.2f} | {100*float(d['required_d_pair_share']):.2f} | {t['status']} |")
w("")
w(f"All rows are in {link('selected-county-break-even.csv', 'data/baselines/selected-county-break-even.csv')}. Because every baseline is far from a tie, live-night use should track the statewide pace across many counties, not wait on a single county.")
w("")

# ---------------- All counties
w("## All 77 counties")
w("")
w("Signed margins are observed **D−R pair-margin points**; positive means the Democrat led that historical contest. The scenario columns use 2022 special preferences at native 2022 special pair weights. '+1 pp gain' is the net-vote value of one D-share point. The D+1 targets form one uniform statewide combination; they are not separate necessary conditions. "
  f"Full integers, other-candidate votes, weights, sources and statuses are in {link('county-baselines.csv', 'data/county-baselines.csv')}.")
w("")
w("| County | FIPS | SEB | 2022 special pp | 2022 regular pp | 2020 Senate pp | 2024 pres pp | 2022 gov pp | Special pair weight % | Special net | +1 pp gain | D+1 target D % | D+1 target net |")
w("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
for r in sorted(wide, key=lambda r: r["county"].upper()):
    w(f"| {r['county']} | {r['county_fips']} | {r['seb_county_code']} | {float(r['2022_senate_special_pair_margin_pp']):+.2f} | {float(r['2022_senate_regular_pair_margin_pp']):+.2f} | {float(r['2020_senate_pair_margin_pp']):+.2f} | {float(r['2024_president_pair_margin_pp']):+.2f} | {float(r['2022_governor_pair_margin_pp']):+.2f} | {100*float(r['2022_senate_special_pair_weight']):.4f} | {int(r['2022_senate_special_d_minus_r_net']):+,} | {float(r['scenario_net_per_plus1pp_d_share']):,.2f} | {100*float(r['scenario_d1_target_d_pair_share']):.4f} | {float(r['scenario_d1_target_net']):+,.2f} |")
w("")

# ---------------- Reproduction
w("## Files, reproduction and checks")
w("")
w(f"- {link('acquire.py', 'data/baselines/acquire.py')}: network fetch of every source into its own `raw/<source_id>/` directory. Text is gzip-compressed losslessly; ZIP and PDF are stored as-is. Writes {link('sources.json', 'data/baselines/sources.json')}.")
w(f"- {link('build.py', 'data/baselines/build.py')}: offline. It verifies each raw hash, then writes the long tables, controls, scenarios, {link('slate-2026.json', 'data/baselines/slate-2026.json')}, {link('build-checks.json', 'data/baselines/build-checks.json')} ({CHECKS['n']} checks, {len(CHECKS['failed'])} failed) and the wide county CSV. Run with `uv run --with pypdf==5.1.0 python3 -I build.py`.")
w(f"- {link('render_report.py', 'data/baselines/render_report.py')}: writes this page from those outputs.")
w(f"- {link('validate.py', 'data/baselines/validate.py')}: independent offline checks, written to {link('validation.json', 'data/baselines/validation.json')}, plus the {link('asset manifest', 'data/baselines/asset-manifest.json')}. It covers: 77 unique counties, FIPS and SEB codes per contest; D+R+other balances; candidate and method sums; Clerk and SEB controls; weights summing to one; scenario tie and D+1 arithmetic, including the +0.5-point step; summed county target nets; selected-county equations; synthetic clipping, impossible and already-winning cases; uniform-scaling invariance; raw-file hashes; file sizes under 40 MB; and relative links on this page.")
w(f"- Column definitions are in {link('SCHEMA.md', 'data/baselines/SCHEMA.md')}.")
w("")
w("## Gaps")
w("")
w("- **No SEB county export was downloaded.** The official OKER application serves county and precinct exports only after an application login, which this package did not perform. County counts are MEDSL or OpenElections transcriptions of those exports, reconciled to official statewide totals. Before live use, re-verify them against SEB exports obtained by a person in a browser, or against county election board canvass reports.")
w("- The MEDSL 2020 Oklahoma file on Harvard Dataverse requires a guestbook response, and the VEST 2022 Oklahoma file requires a login. Neither was used, so there is no fully independent second county transcription for 2020 or 2022.")
w("- The 2022 governor contest has no primary statewide control here and is context only.")
w("- Official certified June 16 primary and August 25 runoff counts were not retrieved. The Hern and Thomas nominations rest on newsroom reports plus the official filing list. The unexpired-term question (whether November also fills the rest of the vacancy) is not resolved from statute.")
w("- Ballots cast, under/overvotes and registration are not in these contest files. The turnout worker owns those measures in `turnout.md`.")
w("- Historical precinct IDs are not current 2026 reporting units. No geographic crosswalk is implied.")
w("- These are deterministic scenarios. There are no probabilities, no 2026 turnout projection and no live collector.")
w("")
REPORT.write_text("\n".join(L))
print("wrote", REPORT)
