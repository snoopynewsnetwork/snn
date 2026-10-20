#!/usr/bin/env python3
"""Independent offline validation of the Oklahoma partisanship package.

Run after build.py and render_report.py: ``uv run python3 -I validate.py``.
This script does not import build.py.  It re-aggregates county D/R/all
votes directly from the raw source files, compares statewide sums with
House Clerk totals transcribed by hand from the Clerk PDFs (also checked to
appear in the extracted Clerk text), re-solves every scenario with its own
solver, and checks report links, hashes and sizes.  Writes validation.json
and asset-manifest.json.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_DIR = HERE.parent.parent
REPORT = STATE_DIR / "county-partisanship.md"
WIDE = HERE.parent / "county-baselines.csv"
MAX_BYTES = 40_000_000
results = []


def check(cid, ok, detail=""):
    results.append({"check": cid, "passed": bool(ok), "detail": str(detail)[:500]})


def rd(p):
    return list(csv.DictReader(open(p)))


def close(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(a)), abs(float(b)))


# ---------------------------------------------------------------- sources
man = json.loads((HERE / "sources.json").read_text())
SRC = {s["source_id"]: s for s in man["sources"]}
for s in man["sources"]:
    if s.get("not_stored_reason"):
        d = HERE / "raw" / s["source_id"]
        check(f"source.{s['source_id']}.metadata_only_by_design",
              s["http_status"] == 200 and s.get("stored_path") is None and not (d.exists() and any(d.iterdir())),
              s["not_stored_reason"])
        continue
    ok = s["http_status"] == 200 and s.get("stored_path")
    if ok:
        p = HERE / s["stored_path"]
        b = p.read_bytes()
        ok = hashlib.sha256(b).hexdigest() == s["stored_sha256"] and len(b) == s["stored_bytes"]
        ent = gzip.decompress(b) if s["stored_encoding"] == "gzip" else b
        ok = ok and hashlib.sha256(ent).hexdigest() == s["entity_sha256"] and len(ent) == s["entity_bytes"]
        ok = ok and p.parent.name == s["source_id"]
    check(f"source.{s['source_id']}.status_and_hashes", ok, s.get("stored_path"))


def raw(sid):
    s = SRC[sid]
    b = (HERE / s["stored_path"]).read_bytes()
    return gzip.decompress(b) if s["stored_encoding"] == "gzip" else b


# ---------------------------------------------------------------- geography
census = [r for r in csv.DictReader(io.StringIO(raw("census-ok-counties-2020").decode()), delimiter="|")]
CFIPS = {r["STATEFP"] + r["COUNTYFP"]: re.sub(r" County$", "", r["COUNTYNAME"]) for r in census}
check("census.77_counties", len(CFIPS) == 77)
wide = rd(WIDE)
check("wide.77_rows", len(wide) == 77, len(wide))
check("wide.unique_fips", len({r["county_fips"] for r in wide}) == 77)
check("wide.unique_county", len({r["county"] for r in wide}) == 77)
check("wide.fips_equal_census", {r["county_fips"] for r in wide} == set(CFIPS))
check("wide.names_equal_census", all(CFIPS[r["county_fips"]] == r["county"] for r in wide))
check("wide.seb_codes_01_77", sorted(r["seb_county_code"] for r in wide) == [f"{i:02d}" for i in range(1, 78)])
SEB = {r["county_fips"]: int(r["seb_county_code"]) for r in wide}
NAME2FIPS = {re.sub(r"[^A-Z]", "", v.upper()): k for k, v in CFIPS.items()}

# ---------------------------------------------------------------- independent re-aggregation from raw
DR = {"2022-senate-special": ("KENDRA HORN", "MARKWAYNE MULLIN"), "2022-senate-regular": ("MADISON HORN", "JAMES LANKFORD"),
      "2022-governor": ("JOY HOFMEISTER", "KEVIN STITT"), "2024-president": ("KAMALA D HARRIS", "DONALD J TRUMP"),
      "2020-senate": ("ABBY BROYLES", "JIM INHOFE")}
agg = defaultdict(lambda: {"D": 0, "R": 0, "A": 0})
cand_state = defaultdict(int)
prefix_ok = True


def put(contest, fips, name, votes):
    d, r = DR[contest]
    a = agg[(contest, fips)]
    a["A"] += votes
    if name == d:
        a["D"] += votes
    elif name == r:
        a["R"] += votes
    cand_state[(contest, name)] += votes


z = zipfile.ZipFile(io.BytesIO(raw("medsl-2022-ok")))
for r in csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8")):
    if r["office"] == "US SENATE":
        contest = "2022-senate-special" if r["special"] == "TRUE" else "2022-senate-regular"
    elif r["office"] == "GOVERNOR":
        contest = "2022-governor"
    else:
        continue
    f = NAME2FIPS[re.sub(r"[^A-Z]", "", r["county_name"].upper())]
    prefix_ok &= int(r["precinct"]) // 10000 == SEB[f] and f == r["county_fips"]
    put(contest, f, r["candidate"], int(r["votes"]))
z = zipfile.ZipFile(io.BytesIO(raw("medsl-2024-ok")))
for r in csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8")):
    if r["office"] == "US PRESIDENT" and r["mode"] == "TOTAL":
        f = NAME2FIPS[re.sub(r"[^A-Z]", "", r["county_name"].upper())]
        prefix_ok &= int(r["precinct"]) // 10000 == SEB[f] and f == r["county_fips"]
        put("2024-president", f, r["candidate"], int(r["votes"]))
for r in csv.DictReader(io.StringIO(raw("openelections-2020-county").decode())):
    if r["office"] == "U.S. Senate":
        put("2020-senate", NAME2FIPS[re.sub(r"[^A-Z]", "", r["county"].upper())], r["candidate"], int(r["votes"]))
check("raw.precinct_prefix_and_fips_consistent_with_wide_seb_codes", prefix_ok)

contests = rd(HERE / "county-contests.csv")
check("contests.385_rows", len(contests) == 385, len(contests))
by_c = defaultdict(list)
for r in contests:
    by_c[r["contest_id"]].append(r)
for c, rows in by_c.items():
    check(f"{c}.77_unique_fips", len({r['county_fips'] for r in rows}) == 77 and {r['county_fips'] for r in rows} == set(CFIPS))
    bad = [r["county"] for r in rows if (int(r["d_votes"]), int(r["r_votes"]), int(r["allcand_votes"])) !=
           (agg[(c, r["county_fips"])]["D"], agg[(c, r["county_fips"])]["R"], agg[(c, r["county_fips"])]["A"])]
    check(f"{c}.county_counts_equal_independent_raw_reaggregation", not bad, bad)
    bal = [r["county"] for r in rows if int(r["d_votes"]) + int(r["r_votes"]) + int(r["other_votes"]) != int(r["allcand_votes"])
           or int(r["pair_votes"]) != int(r["d_votes"]) + int(r["r_votes"])
           or sum(json.loads(r["other_detail"]).values()) != int(r["other_votes"])]
    check(f"{c}.d_r_other_balance", not bal, bal)
    sh = [r["county"] for r in rows if not (0 <= float(r["d_pair_share"]) <= 1)
          or not close(float(r["pair_margin_pp"]), 100 * (2 * float(r["d_pair_share"]) - 1))
          or not close(float(r["d_pair_share"]), int(r["d_votes"]) / int(r["pair_votes"]))]
    check(f"{c}.share_margin_arithmetic", not sh, sh)
    D = sum(int(r["d_votes"]) for r in rows)
    R = sum(int(r["r_votes"]) for r in rows)
    check(f"{c}.pair_weights_sum_1", close(sum(float(r["pair_weight"]) for r in rows), 1.0, 1e-12))
    check(f"{c}.allcand_weights_sum_1", close(sum(float(r["allcand_weight"]) for r in rows), 1.0, 1e-12))
    check(f"{c}.contributions_sum_to_statewide_margin",
          close(sum(float(r["statewide_pair_margin_contribution_pp"]) for r in rows), 100 * (D - R) / (D + R), 1e-10))
    check(f"{c}.net_shares_sum_1", close(sum(float(r["share_of_statewide_net"]) for r in rows), 1.0, 1e-10))

# hand transcription of the Clerk PDFs (see clerk-oklahoma-text.json for the extracted text)
CLERK = {
    ("2022-senate-special", "MARKWAYNE MULLIN"): 710643, ("2022-senate-special", "KENDRA HORN"): 405389,
    ("2022-senate-special", "ROBERT MURPHY"): 17386, ("2022-senate-special", "RAY WOODS"): 17063,
    ("2022-senate-regular", "JAMES LANKFORD"): 739960, ("2022-senate-regular", "MADISON HORN"): 369370,
    ("2022-senate-regular", "MICHAEL L DELANEY"): 20907, ("2022-senate-regular", "KENNETH D BLEVINS"): 20495,
    ("2020-senate", "JIM INHOFE"): 979140, ("2020-senate", "ABBY BROYLES"): 509763, ("2020-senate", "ROBERT MURPHY"): 34435,
    ("2020-senate", "JOAN FARR"): 21652, ("2020-senate", "A. D. NESBIT"): 11371,
    ("2024-president", "DONALD J TRUMP"): 1036213, ("2024-president", "KAMALA D HARRIS"): 499599,
    ("2024-president", "CHASE OLIVER"): 9198,
}
ctext = json.dumps(json.loads((HERE / "clerk-oklahoma-text.json").read_text()))
for (c, n), v in CLERK.items():
    check(f"clerk.{c}.{n}", cand_state[(c, n)] == v and f"{v:,}" in ctext, f"raw {cand_state[(c, n)]} clerk {v}")
ind24 = cand_state[("2024-president", "CHRIS GARRITY")] + cand_state[("2024-president", "ROBERT F KENNEDY JR")]
check("clerk.2024-president.independents_combined", ind24 == 21163 and "21,163" in ctext, ind24)
for c in ("2022-senate-special", "2022-senate-regular", "2020-senate"):
    names = {n for (cc, n) in cand_state if cc == c}
    check(f"clerk.{c}.covers_all_candidates", names == {n for (cc, n) in CLERK if cc == c}, sorted(names))
# archived SEB official 2020
seb20 = json.loads(raw("wayback-seb-oker-2020"))
race = [r for r in seb20["races"] if r["raceTag"] == "UNITEDSTATESSENATOR"][0]
res = [r for r in seb20["results"] if r["raceID"] == race["raceID"]][0]
sebv = {c["candName"].rsplit(" (", 1)[0]: v["totalVotes"] for c, v in zip(race["raceCandidates"], res["candResults"])}
check("seb2020.official_flag", seb20["isOfficial"] is True and seb20["Title1"] == "Official Results")
check("seb2020.senate_candidates_match", all(cand_state[("2020-senate", n)] == v for n, v in sebv.items()) and len(sebv) == 5, sebv)

# candidates long table
cc = rd(HERE / "county-candidates.csv")
meth = [r for r in cc if int(r["absentee"]) + int(r["early"]) + int(r["election_day"]) != int(r["total"])]
check("candidates.methods_sum_to_total", not meth, len(meth))
g = defaultdict(lambda: [0, 0, 0])
for r in cc:
    k = (r["contest_id"], r["county_fips"])
    g[k][0 if r["role"] == "D" else 1 if r["role"] == "R" else 2] += int(r["total"])
mm = [k for k in g if g[k] != [int(x[f]) for x in [next(y for y in by_c[k[0]] if y["county_fips"] == k[1])] for f in ("d_votes", "r_votes", "other_votes")]]
check("candidates.roles_sum_to_contest_rows", not mm, mm[:5])
check("candidates.one_D_one_R_per_county_contest",
      all(sum(1 for r in cc if r["contest_id"] == c and r["county_fips"] == f and r["role"] == x) == 1
          for c in by_c for f in list(CFIPS)[:5] for x in ("D", "R")))
x20 = rd(HERE / "cross-check-2020-precinct-vs-county.csv")
check("oe2020.precinct_vs_county_zero_diff", len(x20) == 385 and all(r["difference"] == "0" for r in x20), len(x20))

# ---------------------------------------------------------------- scenarios
st = {r["scenario_id"]: r for r in rd(HERE / "state-scenarios.csv")}
ct = defaultdict(list)
for r in rd(HERE / "county-target-scenarios.csv"):
    ct[r["scenario_id"]].append(r)
check("scenarios.60_state_rows", len(st) == 60, len(st))
check("scenarios.77_counties_each", all(len(v) == 77 for v in ct.values()) and set(ct) == set(st))


def clip(x):
    return min(1.0, max(0.0, x))


def solve(s, T, target):
    sT = sum(T)
    M0 = sum(t * (2 * a - 1) for a, t in zip(s, T))
    du = (target - M0) / (2 * sT) if sT > 0 else None
    if sT <= 0:
        return du, None, "no-positive-pool"
    if abs(target) > sT:
        return du, None, "impossible"
    if all(0 <= a + du <= 1 for a in s):
        return du, du, "feasible/unbounded"
    lo, hi = -1.0, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        if sum(t * (2 * clip(a + m) - 1) for a, t in zip(s, T)) < target:
            lo = m
        else:
            hi = m
    return du, (lo + hi) / 2, "feasible/bounded"


for sid, srow in st.items():
    rows = ct[sid]
    s = [float(r["baseline_d_pair_share"]) for r in rows]
    T = [float(r["scenario_pair_volume"]) for r in rows]
    V = [float(r["scenario_allcand_volume"]) for r in rows]
    goal = srow["goal"]
    target = 0.0 if goal == "tie" else 0.01 * sum(T) if goal == "pair-d+1" else 0.01 * sum(V)
    du, db, status = solve(s, T, target)
    ok = (close(du * 100, srow["unbounded_d_share_shift_pp"]) and status == srow["status"]
          and close(target, srow["target_net"], 1e-9)
          and close(sum(float(r["pair_weight"]) for r in rows), 1.0, 1e-12)
          and close(sum(float(r["allcand_weight"]) for r in rows), 1.0, 1e-12)
          and close(sum(float(r["baseline_net"]) for r in rows), srow["baseline_d_minus_r_net"], 1e-9)
          and close(sum(float(r["target_net"]) for r in rows), target, 1e-7)
          and close(sum(float(r["net_gain"]) for r in rows), float(srow["required_net_gain"]), 1e-7)
          and all(close(float(r["net_per_plus1pp_d_share"]), 0.02 * float(r["scenario_pair_volume"])) for r in rows)
          and all(r["clipped"] == "False" for r in rows)
          and all(close(float(r["target_d_pair_share"]), float(r["baseline_d_pair_share"]) + du) for r in rows))
    # D exceeds every other candidate in the D+1 scenarios (others fixed): D_expected vs total other volume
    if goal != "tie":
        d_exp = (sum(T) + target) / 2
        ok = ok and d_exp > sum(float(r["scenario_other_volume_fixed"]) for r in rows)
    check(f"scenario.{sid}", ok, f"du={du} status={status}")
for pref in ("2022-senate-special", "2022-senate-regular", "2020-senate", "2024-president", "2022-governor"):
    for mix in ("native-pair", "2022-senate-special-volume", "2024-president-volume", "2020-senate-volume"):
        t = float(st[f"{pref}|{mix}|tie"]["unbounded_d_share_shift_pp"])
        d1 = float(st[f"{pref}|{mix}|pair-d+1"]["unbounded_d_share_shift_pp"])
        a1 = float(st[f"{pref}|{mix}|allcand-d+1"]["unbounded_d_share_shift_pp"])
        check(f"scenario.{pref}|{mix}.d1_minus_tie_is_0.5pp", close(d1 - t, 0.5, 1e-9), d1 - t)
        check(f"scenario.{pref}|{mix}.allcand_d1_ge_pair_d1", a1 >= d1)
    rows = by_c[pref]
    D = sum(int(r["d_votes"]) for r in rows)
    R = sum(int(r["r_votes"]) for r in rows)
    check(f"scenario.{pref}.native_tie_equals_(R-D)/(2(D+R))",
          close(float(st[f"{pref}|native-pair|tie"]["unbounded_d_share_shift_pp"]), 100 * (R - D) / (2 * (D + R))), (R - D) / (2 * (D + R)))
# mixes that equal native by construction
for pref, mix in (("2022-senate-special", "2022-senate-special-volume"), ("2020-senate", "2020-senate-volume"),
                  ("2024-president", "2024-president-volume")):
    check(f"scenario.{pref}.own_volume_mix_equals_native",
          close(st[f"{pref}|{mix}|tie"]["unbounded_d_share_shift_pp"], st[f"{pref}|native-pair|tie"]["unbounded_d_share_shift_pp"], 1e-9))

# selected county
sel = rd(HERE / "selected-county-break-even.csv")
check("selected.row_count", len(sel) == 5 * 2 * 2 * 77, len(sel))
bad = []
for r in sel:
    T = float(r["selected_pair_volume"])
    q = float(r["required_d_pair_share"])
    rows = ct[f"{r['preference_contest']}|{r['volume_mix']}|tie"]
    sumT = sum(float(x["scenario_pair_volume"]) for x in rows)
    target = 0.0 if r["goal"] == "tie" else 0.01 * sumT
    eq = close(float(r["fixed_other_net"]) + T * (2 * q - 1), target, 1e-7)
    stt = "already secured" if q <= 0 else "impossible" if q > 1 else "feasible"
    if not (eq and stt == r["status"]):
        bad.append((r["county"], r["preference_contest"], r["volume_mix"], r["goal"]))
check("selected.equation_and_status", not bad, bad[:5])

# synthetic solver tests
du, db, s_ = solve([0.6, 0.55], [100, 100], 0.0)
check("synthetic.already_winning_negative_shift", s_ == "feasible/unbounded" and du < 0 and close(du, -0.075), du)
du, db, s_ = solve([0.98, 0.10], [100, 300], 0.0)
fx = sum(t * (2 * clip(a + db) - 1) for a, t in zip([0.98, 0.10], [100, 300]))
check("synthetic.clipping_resolves_bounded", s_ == "feasible/bounded" and abs(fx) < 1e-9 and not close(du, db), (du, db, fx))
du, db, s_ = solve([0.2, 0.3], [10, 10], 25.0)
check("synthetic.impossible_target", s_ == "impossible" and db is None)
du, db, s_ = solve([0.5], [0.0], 0.0)
check("synthetic.zero_pool", s_ == "no-positive-pool")
du, db, s_ = solve([0.4, 0.45], [500, 500], 0.0)
du1, _, _ = solve([0.4, 0.45], [500, 500], 10.0)
check("synthetic.d1_is_tie_plus_half_point", close(du1 - du, 0.005))

# turnout sensitivity: uniform scaling invariance
sens = {r["scenario"]: r for r in rd(HERE / "turnout-sensitivity.csv")}
base = float(sens["observed 2022 special pair volumes"]["tie_d_share_shift_pp"])
check("sensitivity.uniform_scaling_invariant",
      all(close(float(sens[k]["tie_d_share_shift_pp"]), base, 1e-9) for k in sens if "(uniform)" in k))
check("sensitivity.observed_equals_native_scenario",
      close(base, st["2022-senate-special|native-pair|tie"]["unbounded_d_share_shift_pp"], 1e-12))

# wide scenario columns consistent with headline scenario
head = {r["county_fips"]: r for r in ct["2022-senate-special|native-pair|pair-d+1"]}
check("wide.scenario_columns_match_headline",
      all(close(w["scenario_d1_target_d_pair_share"], head[w["county_fips"]]["target_d_pair_share"])
          and close(w["scenario_d1_target_net"], head[w["county_fips"]]["target_net"]) for w in wide))

# slate
slate = json.loads((HERE / "slate-2026.json").read_text())
fil = {r["candidate"]: r["affiliation"] for r in slate["filings_official"]}
check("slate.13_filings", len(fil) == 13)
check("slate.book_matches_portal", len(slate["candidate_list_book_page3_ids"]) == 13)
ballot = {"Kevin Hern": "Republican", "N'Kiyla Jasmine Thomas": "Democrat", "Sevier White": "Libertarian",
          "Curtis Stinnett": "Independent", "Ron Meinhardt": "Independent"}
check("slate.expected_ballot_subset_of_filings", all(fil.get(k) == v for k, v in ballot.items()))
check("slate.single_libertarian_filer", sum(1 for v in fil.values() if v == "Libertarian") == 1)

# ---------------------------------------------------------------- report links and key numbers
text = REPORT.read_text()
links = re.findall(r"\]\(([^)]+)\)", text)
rel = [l for l in links if not re.match(r"https?://", l)]
SELF_OUT = {"data/baselines/validation.json", "data/baselines/asset-manifest.json"}  # written by this script below
missing = [l for l in rel if l not in SELF_OUT and not (STATE_DIR / l.split("#")[0]).exists()]
check("report.relative_links_exist", not missing and rel, missing)
for key in (f"{float(st['2022-senate-special|native-pair|tie']['unbounded_d_share_shift_pp']):.6f}",
            f"{float(st['2022-senate-special|native-pair|pair-d+1']['unbounded_d_share_shift_pp']):.6f}", "305,254", "1,116,032"):
    check(f"report.contains.{key}", key in text)
check("report.77_county_rows", len(re.findall(r"^\| [A-Z][A-Za-z ]+ \| 40\d{3} \| \d\d \|", text, re.M)) == 77)

# ---------------------------------------------------------------- sizes and manifest
owned = [REPORT, WIDE] + sorted(p for p in HERE.rglob("*") if p.is_file())
skip = {HERE / "asset-manifest.json", HERE / "validation.json"}
big = [str(p) for p in owned if p.stat().st_size >= MAX_BYTES]
check("files.all_under_40MB", not big, big)
pyc = [str(p) for p in owned if "__pycache__" in p.parts or p.suffix == ".pyc"]
check("files.no_bytecode_caches", not pyc, pyc)
assets = [{"path": str(p.relative_to(STATE_DIR)), "bytes": p.stat().st_size,
           "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in owned if p not in skip]
(HERE / "asset-manifest.json").write_text(json.dumps({"schema": 1, "excluded": ["data/baselines/asset-manifest.json", "data/baselines/validation.json"],
                                                      "assets": assets}, indent=1) + "\n")
failed = [r for r in results if not r["passed"]]
(HERE / "validation.json").write_text(json.dumps({"n_checks": len(results), "n_failed": len(failed), "failed": failed,
                                                  "checks": results}, indent=1) + "\n")
print(f"validation: {len(results)} checks, {len(failed)} failed")
for f in failed:
    print("FAILED", f["check"], f["detail"])
raise SystemExit(1 if failed else 0)
