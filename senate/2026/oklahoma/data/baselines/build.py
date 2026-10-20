#!/usr/bin/env python3
"""Build Oklahoma county partisanship baselines and scenarios (offline).

Run: ``uv run --with pypdf==5.1.0 python3 -I build.py`` from any directory.
Reads only ``raw/`` evidence listed in ``sources.json`` and writes CSV/JSON
outputs next to this script plus ``../county-baselines.csv``.

Conventions
-----------
* Counts are exact source integers.  Derived shares are fractions in [0, 1];
  margins are reported in percentage points (pp) where a column says ``_pp``.
* ``pair`` = Democratic candidate + Republican candidate votes in the named
  contest.  ``allcand`` = every candidate's votes in the contest (Oklahoma
  prints no write-in line; under/over votes are not in these files).
* D share ``s = D/(D+R)``.  D-minus-R pair margin ``2s-1``.  A +1 pp change in
  D share is +2 pp of margin and ``0.02*T`` net votes at fixed pair volume T.
* Independents and Libertarians are never assigned to either party.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE
WIDE = HERE.parent / "county-baselines.csv"

SOURCES = {s["source_id"]: s for s in json.loads((HERE / "sources.json").read_text())["sources"]}


def raw_bytes(sid: str) -> bytes:
    s = SOURCES[sid]
    p = HERE / s["stored_path"]
    b = p.read_bytes()
    if hashlib.sha256(b).hexdigest() != s["stored_sha256"]:
        raise SystemExit(f"stored hash mismatch for {sid}")
    if s["stored_encoding"] == "gzip":
        b = gzip.decompress(b)
    if hashlib.sha256(b).hexdigest() != s["entity_sha256"]:
        raise SystemExit(f"entity hash mismatch for {sid}")
    return b


def nkey(name: str) -> str:
    return re.sub(r"[^A-Z]", "", name.upper())


# --------------------------------------------------------------------------
# County key: Census 2020 county reference.  The SEB county code is read from
# the leading digits of SEB precinct IDs (precinct // 10000) and must form a
# one-to-one map onto 1..77 consistently across every source file.  (SEB
# numbering collates Mc- counties before Major, so it is not strict A-Z.)
# --------------------------------------------------------------------------
census_rows = list(csv.DictReader(io.StringIO(raw_bytes("census-ok-counties-2020").decode()), delimiter="|"))
COUNTIES = []
for r in census_rows:
    name = re.sub(r" County$", "", r["COUNTYNAME"])
    COUNTIES.append({"county": name, "fips": r["STATEFP"] + r["COUNTYFP"]})
COUNTIES.sort(key=lambda c: c["fips"])
PREFIXES = defaultdict(lambda: defaultdict(set))  # source -> fips -> {prefix}
BY_KEY = {nkey(c["county"]): c for c in COUNTIES}
BY_FIPS = {c["fips"]: c for c in COUNTIES}
assert len(COUNTIES) == 77 and len(BY_FIPS) == 77 and len(BY_KEY) == 77


def county_of(name: str) -> dict:
    k = nkey(name)
    if k not in BY_KEY:
        raise SystemExit(f"unmatched county name {name!r}")
    return BY_KEY[k]


# --------------------------------------------------------------------------
# Contest definitions
# --------------------------------------------------------------------------
CONTESTS = {
    "2022-senate-special": {
        "election_date": "2022-11-08", "office": "U.S. Senator, unexpired term ending 2027-01-03",
        "seat": "Class II (same seat as 2026)", "role": "same-seat baseline (primary)",
        "source_id": "medsl-2022-ok", "D": "KENDRA HORN", "R": "MARKWAYNE MULLIN",
        "status": "secondary transcription (MEDSL) of SEB OKER precinct export; statewide reconciled to House Clerk",
    },
    "2022-senate-regular": {
        "election_date": "2022-11-08", "office": "U.S. Senator, full term beginning 2023-01-03",
        "seat": "Class III (other seat)", "role": "same-ballot midterm Senate comparator",
        "source_id": "medsl-2022-ok", "D": "MADISON HORN", "R": "JAMES LANKFORD",
        "status": "secondary transcription (MEDSL) of SEB OKER precinct export; statewide reconciled to House Clerk",
    },
    "2020-senate": {
        "election_date": "2020-11-03", "office": "U.S. Senator, full term beginning 2021-01-03",
        "seat": "Class II (same seat, previous regular election; history)", "role": "same-seat history",
        "source_id": "openelections-2020-county", "D": "ABBY BROYLES", "R": "JIM INHOFE",
        "status": "secondary transcription (OpenElections) of SEB county export; statewide reconciled to House Clerk and archived SEB official JSON",
    },
    "2024-president": {
        "election_date": "2024-11-05", "office": "Electors for President and Vice President",
        "seat": "n/a (no 2024 Senate contest in Oklahoma)", "role": "recent presidential comparator",
        "source_id": "medsl-2024-ok", "D": "KAMALA D HARRIS", "R": "DONALD J TRUMP",
        "status": "secondary transcription (MEDSL) of SEB OKER precinct export; statewide reconciled to House Clerk",
    },
    "2022-governor": {
        "election_date": "2022-11-08", "office": "Governor",
        "seat": "n/a (statewide midterm non-Senate contest)", "role": "midterm non-Senate context",
        "source_id": "medsl-2022-ok", "D": "JOY HOFMEISTER", "R": "KEVIN STITT",
        "status": "secondary transcription (MEDSL) of SEB OKER precinct export; no primary statewide control retrieved",
    },
}
ORDER = list(CONTESTS)

# county_candidates[(contest, fips, candidate)] = {party, absentee, early, election_day, total}
cand = {}
precinct_counts = defaultdict(set)
checks = []  # (check_id, passed, detail)


def add(contest, fips, candidate, party, method, votes):
    k = (contest, fips, candidate)
    rec = cand.setdefault(k, {"party": party, "absentee": 0, "early": 0, "election_day": 0, "total": 0})
    if rec["party"] != party:
        raise SystemExit(f"party conflict {k}")
    rec[method] += votes


def check(cid, ok, detail=""):
    checks.append({"check": cid, "passed": bool(ok), "detail": detail})
    if not ok:
        print("CHECK FAILED", cid, detail, file=sys.stderr)


# --------------------------------------------------------------------------
# MEDSL 2022 (no TOTAL mode: ABSENTEE + EARLY + IN-PERSON)
# --------------------------------------------------------------------------
MODE22 = {"ABSENTEE": "absentee", "EARLY": "early", "IN-PERSON": "election_day"}
z = zipfile.ZipFile(io.BytesIO(raw_bytes("medsl-2022-ok")))
assert z.namelist() == ["ok22_cleaned.csv"]

fips_name_bad = 0
for r in csv.DictReader(io.TextIOWrapper(z.open("ok22_cleaned.csv"), encoding="utf-8")):
    if r["office"] == "US SENATE":
        contest = "2022-senate-special" if r["special"] == "TRUE" else "2022-senate-regular"
    elif r["office"] == "GOVERNOR":
        contest = "2022-governor"
    else:
        continue
    c = county_of(r["county_name"])
    if c["fips"] != r["county_fips"]:
        fips_name_bad += 1
    PREFIXES["medsl-2022-ok"][c["fips"]].add(int(r["precinct"]) // 10000)
    assert r["writein"] == "FALSE" and r["mode"] in MODE22, r
    precinct_counts[(contest, c["fips"])].add(r["precinct"])
    add(contest, c["fips"], r["candidate"], r["party_detailed"], MODE22[r["mode"]], int(r["votes"]))
check("medsl2022.county_fips_matches_census_name", fips_name_bad == 0, f"{fips_name_bad} rows")
for k, v in cand.items():
    v["total"] = v["absentee"] + v["early"] + v["election_day"]

# --------------------------------------------------------------------------
# MEDSL 2024 (TOTAL and split modes both present: use TOTAL, verify splits)
# --------------------------------------------------------------------------
MODE24 = {"ABSENTEE": "absentee", "EARLY": "early", "IN-PERSON": "election_day", "TOTAL": "total"}
z = zipfile.ZipFile(io.BytesIO(raw_bytes("medsl-2024-ok")))
assert z.namelist() == ["ok24.csv"]
unit = defaultdict(lambda: defaultdict(int))
fips_name_bad = 0
for r in csv.DictReader(io.TextIOWrapper(z.open("ok24.csv"), encoding="utf-8")):
    if r["office"] != "US PRESIDENT":
        continue
    c = county_of(r["county_name"])
    if c["fips"] != r["county_fips"]:
        fips_name_bad += 1
    PREFIXES["medsl-2024-ok"][c["fips"]].add(int(r["precinct"]) // 10000)
    assert r["writein"] == "FALSE" and r["mode"] in MODE24, r
    precinct_counts[("2024-president", c["fips"])].add(r["precinct"])
    key = (c["fips"], r["precinct"], r["candidate"], r["party_detailed"])
    unit[key][MODE24[r["mode"]]] += int(r["votes"])
check("medsl2024.county_fips_matches_census_name", fips_name_bad == 0, f"{fips_name_bad} rows")
mode_bad = 0
for (fips, _p, cname, party), m in unit.items():
    if m["total"] != m["absentee"] + m["early"] + m["election_day"]:
        mode_bad += 1
    for meth in ("absentee", "early", "election_day", "total"):
        k = ("2024-president", fips, cname)
        rec = cand.setdefault(k, {"party": party, "absentee": 0, "early": 0, "election_day": 0, "total": 0})
        rec[meth] += m[meth]
check("medsl2024.total_mode_equals_sum_of_split_modes", mode_bad == 0,
      f"{len(unit)} precinct-candidate units; {mode_bad} mismatches")

# --------------------------------------------------------------------------
# OpenElections 2020 county file (methods + votes) and precinct file
# --------------------------------------------------------------------------
OE_OFF = {"U.S. Senate": "2020-senate", "President": "2020-president-context"}
oe_bad = 0
for r in csv.DictReader(io.StringIO(raw_bytes("openelections-2020-county").decode("utf-8"))):
    contest = OE_OFF.get(r["office"])
    if contest != "2020-senate":
        continue
    c = county_of(r["county"])
    a, e, d, t = (int(r[x]) for x in ("absentee_mail", "early_voting", "election_day", "votes"))
    if a + e + d != t:
        oe_bad += 1
    k = (contest, c["fips"], r["candidate"])
    assert k not in cand, k
    cand[k] = {"party": r["party"], "absentee": a, "early": e, "election_day": d, "total": t}
check("oe2020.county_methods_sum_to_votes", oe_bad == 0, f"{oe_bad} rows")

oe_prec = defaultdict(int)
for r in csv.DictReader(io.StringIO(raw_bytes("openelections-2020-precinct").decode("utf-8"))):
    if r["office"] != "U.S. Senate":
        continue
    c = county_of(r["county"])
    precinct_counts[("2020-senate", c["fips"])].add(r["precinct"])
    PREFIXES["openelections-2020-precinct"][c["fips"]].add(int(r["precinct"]) // 10000)
    oe_prec[(c["fips"], r["candidate"])] += int(r["votes"])
cross2020 = []
for (contest, fips, cname), v in sorted(cand.items()):
    if contest == "2020-senate":
        p = oe_prec.get((fips, cname))
        cross2020.append({"county_fips": fips, "candidate": cname, "county_file_votes": v["total"],
                          "precinct_file_sum": p, "difference": None if p is None else p - v["total"]})
n_diff = sum(1 for x in cross2020 if x["difference"] != 0)
check("oe2020.precinct_file_aggregates_to_county_file", n_diff == 0,
      f"{len(cross2020)} county-candidate cells; {n_diff} differ")

ref = PREFIXES["medsl-2022-ok"]
codes = {f: next(iter(v)) for f, v in ref.items() if len(v) == 1}
check("seb_code.one_prefix_per_county_2022", len(codes) == 77, str({f: sorted(v) for f, v in ref.items() if len(v) != 1}))
check("seb_code.codes_are_1_to_77_unique", sorted(codes.values()) == list(range(1, 78)))
for src, m in PREFIXES.items():
    bad = {f: sorted(v) for f, v in m.items() if v != {codes.get(f)}}
    check(f"seb_code.consistent_{src}", not bad and len(m) == 77, json.dumps(bad))
for c in COUNTIES:
    c["seb_code"] = codes[c["fips"]]
alpha = sorted(COUNTIES, key=lambda c: nkey(c["county"]))
SEB_CODE_NOTES = [f"{c['county']}={c['seb_code']:02d} (A-Z position {i})" for i, c in enumerate(alpha, 1) if c["seb_code"] != i]

# --------------------------------------------------------------------------
# Candidate metadata and role labels
# --------------------------------------------------------------------------
PARTY_LABEL = {"DEMOCRAT": "DEM", "REPUBLICAN": "REP", "LIBERTARIAN": "LIB", "INDEPENDENT": "IND",
               "DEM": "DEM", "REP": "REP", "LIB": "LIB", "IND": "IND"}
cands_by_contest = defaultdict(dict)
for (contest, fips, cname), v in cand.items():
    cands_by_contest[contest][cname] = PARTY_LABEL[v["party"]]
for contest, meta in CONTESTS.items():
    cc = cands_by_contest[contest]
    assert cc[meta["D"]] == "DEM" and cc[meta["R"]] == "REP", (contest, cc)
    assert sum(1 for p in cc.values() if p in ("DEM", "REP")) == 2, (contest, cc)
    meta["candidates"] = {n: p for n, p in sorted(cc.items(), key=lambda x: (x[1] not in ("REP", "DEM"), x[1], x[0]))}
    meta["others"] = [n for n in meta["candidates"] if n not in (meta["D"], meta["R"])]
    for f in BY_FIPS:
        missing = [n for n in cc if (contest, f, n) not in cand]
        check(f"{contest}.all_candidates_present_county_{f}", not missing, ",".join(missing))

# --------------------------------------------------------------------------
# Statewide controls: House Clerk PDFs and archived SEB OKER JSON
# --------------------------------------------------------------------------
from pypdf import PdfReader  # noqa: E402


def clerk_ok_text(sid: str) -> str:
    rd = PdfReader(io.BytesIO(raw_bytes(sid)))
    pages = [p.extract_text() or "" for p in rd.pages]
    for i, t in enumerate(pages):
        m = re.search(r"\nOKLAHOMA\n", t)
        if m:
            seg = t[m.start():] + "\n" + pages[i + 1]
            return re.sub(r"\.{4,}", " ... ", seg), i + 1
    raise SystemExit("Oklahoma section not found " + sid)


def nums(seg, pattern):
    return {m.group(1).strip(): int(m.group(2).replace(",", "")) for m in re.finditer(pattern, seg)}


clerk_text = {}
CLERK = {}
t20, pg20 = clerk_ok_text("clerk-2020")
clerk_text["clerk-2020"] = {"pdf_page": pg20, "text": t20[:1600]}
sen20 = t20.split("FOR UNITED STATES SENATOR")[1].split("FOR UNITED STATES REPRESENTATIVE")[0]
CLERK["2020-senate"] = nums(sen20, r"([A-Z][A-Za-z\. ]+?), (?:Democrat|Republican|Libertarian|Independent)\s+\.\.\.\s+([\d,]+)")
t22, pg22 = clerk_ok_text("clerk-2022")
clerk_text["clerk-2022"] = {"pdf_page": pg22, "text": t22[:900]}
sp = t22.split("(For unexpired term ending January 3, 2027)")[1].split("(For full term beginning January 3, 2023)")
CLERK["2022-senate-special"] = nums(sp[0], r"([A-Z][A-Za-z\. ]+?), (?:Democrat|Republican|Libertarian|Independent)\s+\.\.\.\s+([\d,]+)")
CLERK["2022-senate-regular"] = nums(sp[1], r"([A-Z][A-Za-z\. ]+?), (?:Democrat|Republican|Libertarian|Independent)\s+\.\.\.\s+([\d,]+)")
t24, pg24 = clerk_ok_text("clerk-2024")
clerk_text["clerk-2024"] = {"pdf_page": pg24, "text": t24[:400]}
pres24 = t24.split("FOR PRESIDENTIAL ELECTORS")[1].split("FOR UNITED STATES REPRESENTATIVE")[0]
CLERK["2024-president-by-party"] = nums(pres24, r"(Republican|Democratic|Independent|Libertarian)\s+\.\.\.\s+([\d,]+)")
(OUT / "clerk-oklahoma-text.json").write_text(json.dumps(clerk_text, indent=1) + "\n")

CLERK_NAME = {  # Clerk display name -> source candidate label
    "2020-senate": {"Abby Broyles": "ABBY BROYLES", "James M. Inhofe": "JIM INHOFE", "Robert Murphy": "ROBERT MURPHY",
                    "Joan Farr": "JOAN FARR", "A. D. Nesbit": "A. D. NESBIT"},
    "2022-senate-special": {"Markwayne Mullin": "MARKWAYNE MULLIN", "Kendra Horn": "KENDRA HORN",
                            "Robert Murphy": "ROBERT MURPHY", "Ray Woods": "RAY WOODS"},
    "2022-senate-regular": {"James Lankford": "JAMES LANKFORD", "Madison Horn": "MADISON HORN",
                            "Michael L. Delaney": "MICHAEL L DELANEY", "Kenneth D. Blevins": "KENNETH D BLEVINS"},
}


def oker(sid):
    d = json.loads(raw_bytes(sid))
    races = {r["raceID"]: r for r in d["races"]}
    out = {}
    for res in d["results"]:
        r = races[res["raceID"]]
        if r["raceTag"] in ("PRESIDENT", "UNITEDSTATESSENATOR"):
            out[r["raceTag"]] = {
                "raceID": r["raceID"], "raceTitle": r["raceTitle"],
                "precincts": [res["reportingPrecincts"], res["totalPrecincts"]],
                "cands": {c["candName"]: v for c, v in zip(r["raceCandidates"], res["candResults"])},
                "total": res["totResults"],
            }
    meta = {k: d[k] for k in ("electionDate", "Title1", "isOfficial", "lastUpdate", "serverTLU")}
    return meta, out


OKER20_META, OKER20 = oker("wayback-seb-oker-2020")
OKER24_META, OKER24 = oker("wayback-seb-oker-2024")
OKER_NAME = {
    "2020-senate": {"JIM INHOFE (REP)": "JIM INHOFE", "ROBERT MURPHY (LIB)": "ROBERT MURPHY", "ABBY BROYLES (DEM)": "ABBY BROYLES",
                    "JOAN FARR (IND)": "JOAN FARR", "A. D. NESBIT (IND)": "A. D. NESBIT"},
    "2024-president": {"CHASE OLIVER | MIKE TER MAAT (LIB)": "CHASE OLIVER", "DONALD J. TRUMP | JD VANCE (REP)": "DONALD J TRUMP",
                       "KAMALA D. HARRIS | TIM WALZ (DEM)": "KAMALA D HARRIS",
                       "ROBERT F. KENNEDY JR. | NICOLE SHANAHAN (IND)": "ROBERT F KENNEDY JR",
                       "CHRIS GARRITY | CODY BALLARD (IND)": "CHRIS GARRITY"},
}


def statesum(contest, cname, meth="total"):
    return sum(cand[(contest, f, cname)][meth] for f in BY_FIPS)


controls = []
for contest in ORDER:
    for cname, party in CONTESTS[contest]["candidates"].items():
        row = {"contest_id": contest, "candidate": cname, "party": party,
               "county_sum_total": statesum(contest, cname),
               "county_sum_absentee": statesum(contest, cname, "absentee"),
               "county_sum_early": statesum(contest, cname, "early"),
               "county_sum_election_day": statesum(contest, cname, "election_day"),
               "clerk_total": None, "clerk_diff": None,
               "seb_archive_total": None, "seb_archive_status": None, "seb_archive_diff": None,
               "seb_archive_method_diffs": None}
        if contest in CLERK_NAME:
            inv = {v: k for k, v in CLERK_NAME[contest].items()}
            row["clerk_total"] = CLERK[contest][inv[cname]]
            row["clerk_diff"] = row["county_sum_total"] - row["clerk_total"]
        if contest == "2024-president":
            bp = CLERK["2024-president-by-party"]
            pm = {"REP": "Republican", "DEM": "Democratic", "LIB": "Libertarian"}
            if party in pm:
                row["clerk_total"] = bp[pm[party]]
                row["clerk_diff"] = row["county_sum_total"] - row["clerk_total"]
        src = {"2020-senate": (OKER20, OKER20_META, "UNITEDSTATESSENATOR"),
               "2024-president": (OKER24, OKER24_META, "PRESIDENT")}.get(contest)
        if src:
            data, meta, tag = src
            inv = {v: k for k, v in OKER_NAME[contest].items()}
            v = data[tag]["cands"][inv[cname]]
            row["seb_archive_total"] = v["totalVotes"]
            row["seb_archive_status"] = f"{meta['Title1']} (isOfficial={meta['isOfficial']}, serverTLU={meta['serverTLU']})"
            row["seb_archive_diff"] = row["county_sum_total"] - v["totalVotes"]
            row["seb_archive_method_diffs"] = json.dumps({
                "absentee": row["county_sum_absentee"] - v["absVotes"],
                "early": row["county_sum_early"] - v["earlyVotes"],
                "election_day": row["county_sum_election_day"] - v["elecDayVotes"]})
        controls.append(row)

# Clerk prints 2024 independents as one combined line.
ind24 = sum(r["county_sum_total"] for r in controls if r["contest_id"] == "2024-president" and r["party"] == "IND")
clerk_ind24 = CLERK["2024-president-by-party"]["Independent"]
controls.append({"contest_id": "2024-president", "candidate": "(all Independent tickets combined)", "party": "IND",
                 "county_sum_total": ind24, "clerk_total": clerk_ind24, "clerk_diff": ind24 - clerk_ind24})
for r in controls:
    if r.get("clerk_diff") is not None:
        check(f"{r['contest_id']}.clerk.{r['candidate']}", r["clerk_diff"] == 0, f"diff {r['clerk_diff']}")
    if r["contest_id"] == "2020-senate" and r.get("seb_archive_diff") is not None:
        md = json.loads(r["seb_archive_method_diffs"])
        check(f"2020-senate.seb_official_archive.{r['candidate']}",
              r["seb_archive_diff"] == 0 and all(x == 0 for x in md.values()), r["seb_archive_method_diffs"])
# every reconcilable contest has Clerk coverage for all candidates
for contest in ("2022-senate-special", "2022-senate-regular", "2020-senate"):
    n = sum(1 for r in controls if r["contest_id"] == contest and r.get("clerk_total") is not None)
    check(f"{contest}.clerk_covers_every_candidate", n == len(CONTESTS[contest]["candidates"]), str(n))
check("2020-senate.seb_archive_official_flag", OKER20_META["isOfficial"] is True, json.dumps(OKER20_META))
check("2020-senate.seb_archive_contest_total",
      sum(statesum("2020-senate", n) for n in CONTESTS["2020-senate"]["candidates"]) == OKER20["UNITEDSTATESSENATOR"]["total"]["totalVotes"])


def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0].keys())
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})


write_csv(OUT / "state-controls.csv", controls, [
    "contest_id", "candidate", "party", "county_sum_total", "county_sum_absentee", "county_sum_early",
    "county_sum_election_day", "clerk_total", "clerk_diff", "seb_archive_total", "seb_archive_status",
    "seb_archive_diff", "seb_archive_method_diffs"])
write_csv(OUT / "cross-check-2020-precinct-vs-county.csv", cross2020)

# --------------------------------------------------------------------------
# Long county-candidate table
# --------------------------------------------------------------------------
long_rows = []
for contest in ORDER:
    for c in COUNTIES:
        for cname, party in CONTESTS[contest]["candidates"].items():
            v = cand[(contest, c["fips"], cname)]
            role = "D" if cname == CONTESTS[contest]["D"] else "R" if cname == CONTESTS[contest]["R"] else "other"
            long_rows.append({"contest_id": contest, "county": c["county"], "county_fips": c["fips"],
                              "seb_county_code": f"{c['seb_code']:02d}", "candidate": cname, "party": party,
                              "role": role, "absentee": v["absentee"], "early": v["early"],
                              "election_day": v["election_day"], "total": v["total"],
                              "source_id": CONTESTS[contest]["source_id"]})
write_csv(OUT / "county-candidates.csv", long_rows)

# --------------------------------------------------------------------------
# County contest table
# --------------------------------------------------------------------------
BASE = {}  # BASE[contest][fips] = dict(D,R,O,A,...)
for contest in ORDER:
    meta = CONTESTS[contest]
    BASE[contest] = {}
    for c in COUNTIES:
        f = c["fips"]
        D = cand[(contest, f, meta["D"])]["total"]
        R = cand[(contest, f, meta["R"])]["total"]
        others = {n: cand[(contest, f, n)]["total"] for n in meta["others"]}
        O = sum(others.values())
        BASE[contest][f] = {"D": D, "R": R, "O": O, "A": D + R + O, "others": others,
                            "precincts": len(precinct_counts.get((contest, f), ()))}
    tot = {k: sum(BASE[contest][f][k] for f in BY_FIPS) for k in ("D", "R", "O", "A")}
    meta["state"] = tot


def band(m_pp):
    a = abs(m_pp)
    return "<=5 margin pp" if a <= 5 else ">5-10 margin pp" if a <= 10 else ">10 margin pp"


contest_rows = []
for contest in ORDER:
    st = CONTESTS[contest]["state"]
    P = st["D"] + st["R"]
    net_state = st["D"] - st["R"]
    for c in COUNTIES:
        b = BASE[contest][c["fips"]]
        pair = b["D"] + b["R"]
        net = b["D"] - b["R"]
        s = b["D"] / pair
        contest_rows.append({
            "contest_id": contest, "election_date": CONTESTS[contest]["election_date"],
            "county": c["county"], "county_fips": c["fips"], "seb_county_code": f"{c['seb_code']:02d}",
            "d_candidate": CONTESTS[contest]["D"], "r_candidate": CONTESTS[contest]["R"],
            "d_votes": b["D"], "r_votes": b["R"], "other_votes": b["O"],
            "other_detail": json.dumps(b["others"], sort_keys=True),
            "allcand_votes": b["A"], "pair_votes": pair, "pair_participation": pair / b["A"],
            "d_pair_share": s, "d_minus_r_net": net, "pair_margin_pp": 100 * (2 * s - 1),
            "allcand_margin_pp": 100 * net / b["A"], "historical_pair_leader": "D" if net > 0 else "R" if net < 0 else "tie",
            "closeness_band": band(100 * (2 * s - 1)), "pair_weight": pair / P, "allcand_weight": b["A"] / st["A"],
            "statewide_pair_margin_contribution_pp": 100 * net / P,
            "share_of_statewide_net": net / net_state, "precinct_ids_in_source": b["precincts"],
            "source_id": CONTESTS[contest]["source_id"], "source_status": CONTESTS[contest]["status"],
        })
write_csv(OUT / "county-contests.csv", contest_rows)

# --------------------------------------------------------------------------
# Scenarios
# --------------------------------------------------------------------------
PREFS = ORDER
MIXES = ["native-pair", "2022-senate-special-volume", "2024-president-volume", "2020-senate-volume"]
GOALS = ["tie", "pair-d+1", "allcand-d+1"]


def clip(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def solve(s, T, target):
    """Return (unbounded_delta, bounded_delta or None, status)."""
    sumT = sum(T)
    M0 = sum(t * (2 * si - 1) for si, t in zip(s, T))
    du = (target - M0) / (2 * sumT)
    if not (-sumT <= target <= sumT):
        return du, None, "impossible"
    if all(0 <= si + du <= 1 for si in s):
        return du, du, "feasible/unbounded"

    def f(d):
        return sum(t * (2 * clip(si + d) - 1) for si, t in zip(s, T)) - target
    lo, hi = -1.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return du, (lo + hi) / 2, "feasible/bounded"


def mix_inputs(pref, mix):
    """Per-county (s, T, O_expected, V) for a preference contest and volume mix."""
    rows = []
    for c in COUNTIES:
        f = c["fips"]
        b = BASE[pref][f]
        s = b["D"] / (b["D"] + b["R"])
        p = (b["D"] + b["R"]) / b["A"]
        if mix == "native-pair":
            V = b["A"]
            T = b["D"] + b["R"]
        else:
            vol_contest = mix.replace("-volume", "")
            V = BASE[vol_contest][f]["A"]
            T = V * p
        rows.append({"fips": f, "county": c["county"], "s": s, "T": T, "V": V, "O": V - T, "p": p})
    return rows


state_rows, county_rows, cid = [], [], 0
SC = {}
for pref in PREFS:
    for mix in MIXES:
        rows = mix_inputs(pref, mix)
        s = [r["s"] for r in rows]
        T = [r["T"] for r in rows]
        sumT, sumV = sum(T), sum(r["V"] for r in rows)
        M0 = sum(t * (2 * si - 1) for si, t in zip(s, T))
        for goal in GOALS:
            target = 0.0 if goal == "tie" else 0.01 * sumT if goal == "pair-d+1" else 0.01 * sumV
            du, db, status = solve(s, T, target)
            sid = f"{pref}|{mix}|{goal}"
            SC[sid] = {"du": du, "db": db, "M0": M0, "sumT": sumT, "sumV": sumV, "target": target}
            state_rows.append({
                "scenario_id": sid, "preference_contest": pref, "volume_mix": mix, "goal": goal,
                "allcand_volume": sumV, "pair_volume": sumT, "baseline_d_minus_r_net": M0,
                "baseline_pair_margin_pp": 100 * M0 / sumT, "target_net": target,
                "unbounded_d_share_shift_pp": 100 * du,
                "bounded_d_share_shift_pp": None if db is None else 100 * db, "status": status,
                "required_net_gain": target - M0,
                "required_pair_margin_change_pp": 100 * (target - M0) / sumT,
            })
            d = db if db is not None else du
            for r in rows:
                q = clip(r["s"] + d) if db is not None else r["s"] + du
                county_rows.append({
                    "scenario_id": sid, "county": r["county"], "county_fips": r["fips"],
                    "baseline_d_pair_share": r["s"], "baseline_pair_margin_pp": 100 * (2 * r["s"] - 1),
                    "pair_participation": r["p"], "scenario_allcand_volume": r["V"], "scenario_pair_volume": r["T"],
                    "scenario_other_volume_fixed": r["O"], "pair_weight": r["T"] / sumT,
                    "allcand_weight": r["V"] / sumV, "baseline_net": r["T"] * (2 * r["s"] - 1),
                    "net_per_plus1pp_d_share": 0.02 * r["T"], "target_d_pair_share": q,
                    "target_pair_margin_pp": 100 * (2 * q - 1), "required_d_share_change_pp": 100 * (q - r["s"]),
                    "target_net": r["T"] * (2 * q - 1), "net_gain": 2 * r["T"] * (q - r["s"]),
                    "clipped": db is not None and (r["s"] + d < 0 or r["s"] + d > 1),
                })
write_csv(OUT / "state-scenarios.csv", state_rows)
write_csv(OUT / "county-target-scenarios.csv", county_rows)

# --------------------------------------------------------------------------
# Selected-county break-even (all other counties fixed at baseline)
# --------------------------------------------------------------------------
sel_rows = []
for pref in ("2022-senate-special", "2020-senate", "2022-senate-regular", "2024-president", "2022-governor"):
    for mix in ("native-pair", "2024-president-volume"):
        rows = mix_inputs(pref, mix)
        sumT = sum(r["T"] for r in rows)
        sumV = sum(r["V"] for r in rows)
        net = {r["fips"]: r["T"] * (2 * r["s"] - 1) for r in rows}
        tot = sum(net.values())
        for goal in ("tie", "pair-d+1"):
            target = 0.0 if goal == "tie" else 0.01 * sumT
            for r in rows:
                other = tot - net[r["fips"]]
                q = (target - other + r["T"]) / (2 * r["T"])
                sel_rows.append({
                    "preference_contest": pref, "volume_mix": mix, "goal": goal, "county": r["county"],
                    "county_fips": r["fips"], "selected_pair_volume": r["T"], "fixed_other_net": other,
                    "baseline_d_pair_share": r["s"], "required_d_pair_share": q,
                    "status": "already secured" if q <= 0 else "impossible" if q > 1 else "feasible",
                })
write_csv(OUT / "selected-county-break-even.csv", sel_rows)

# --------------------------------------------------------------------------
# Turnout sensitivity (synthetic multipliers, fixed 2022-special preferences)
# --------------------------------------------------------------------------
METRO = {"40109", "40143", "40027"}  # Oklahoma, Tulsa, Cleveland
sens = []
base_rows = mix_inputs("2022-senate-special", "native-pair")
for label, mult in [("observed 2022 special pair volumes", lambda f: 1.0),
                    ("all counties x0.80 (uniform)", lambda f: 0.8),
                    ("all counties x1.20 (uniform)", lambda f: 1.2),
                    ("Oklahoma+Tulsa+Cleveland x1.10, others x1.00", lambda f: 1.1 if f in METRO else 1.0),
                    ("Oklahoma+Tulsa+Cleveland x0.90, others x1.00", lambda f: 0.9 if f in METRO else 1.0),
                    ("all except Oklahoma+Tulsa+Cleveland x1.10", lambda f: 1.0 if f in METRO else 1.1),
                    ("all except Oklahoma+Tulsa+Cleveland x0.90", lambda f: 1.0 if f in METRO else 0.9)]:
    s = [r["s"] for r in base_rows]
    T = [r["T"] * mult(r["fips"]) for r in base_rows]
    du, db, status = solve(s, T, 0.0)
    M0 = sum(t * (2 * si - 1) for si, t in zip(s, T))
    sens.append({"scenario": label, "pair_volume": sum(T), "baseline_net": M0,
                 "baseline_pair_margin_pp": 100 * M0 / sum(T), "tie_d_share_shift_pp": 100 * du,
                 "pair_d+1_d_share_shift_pp": 100 * du + 0.5,
                 "metro_pair_weight": sum(t for t, r in zip(T, base_rows) if r["fips"] in METRO) / sum(T)})
write_csv(OUT / "turnout-sensitivity.csv", sens)

# --------------------------------------------------------------------------
# Wide county baseline (77 rows)
# --------------------------------------------------------------------------
PFX = {"2022-senate-special": "2022_senate_special", "2022-senate-regular": "2022_senate_regular",
       "2020-senate": "2020_senate", "2024-president": "2024_president", "2022-governor": "2022_governor"}
head_sid = "2022-senate-special|native-pair|"
head = {(r["scenario_id"], r["county_fips"]): r for r in county_rows if r["scenario_id"].startswith(head_sid)}
wide = []
cr = {(r["contest_id"], r["county_fips"]): r for r in contest_rows}
for c in COUNTIES:
    f = c["fips"]
    row = {"county": c["county"], "county_fips": f, "seb_county_code": f"{c['seb_code']:02d}"}
    for contest in ORDER:
        x = cr[(contest, f)]
        p = PFX[contest]
        for k in ("d_votes", "r_votes", "other_votes", "allcand_votes", "pair_votes", "pair_participation",
                  "d_pair_share", "d_minus_r_net", "pair_margin_pp", "allcand_margin_pp", "historical_pair_leader",
                  "closeness_band", "pair_weight", "statewide_pair_margin_contribution_pp", "share_of_statewide_net"):
            row[f"{p}_{k}"] = x[k]
        row[f"{p}_source_id"] = x["source_id"]
    t = head[(head_sid + "tie", f)]
    d1 = head[(head_sid + "pair-d+1", f)]
    row.update({
        "scenario_basis": "2022-senate-special preferences at native 2022-special pair weights",
        "scenario_net_per_plus1pp_d_share": t["net_per_plus1pp_d_share"],
        "scenario_tie_target_d_pair_share": t["target_d_pair_share"],
        "scenario_tie_target_net": t["target_net"],
        "scenario_d1_target_d_pair_share": d1["target_d_pair_share"],
        "scenario_d1_target_pair_margin_pp": d1["target_pair_margin_pp"],
        "scenario_d1_target_net": d1["target_net"],
        "scenario_d1_net_gain": d1["net_gain"],
    })
    wide.append(row)
write_csv(WIDE, wide)

# --------------------------------------------------------------------------
# 2026 slate evidence (official filings; nominee outcome secondary)
# --------------------------------------------------------------------------
fil = json.loads(raw_bytes("seb-filings-us-senator"))["data"]
book = PdfReader(io.BytesIO(raw_bytes("seb-2026-candidate-list-book")))
book_p3 = book.pages[2].extract_text()
book_sen = re.sub(r"\s+", " ", book_p3.split("UNITED STATES SENATOR")[1])
book_ids = [(f"{r['FilingID']:05d}", r["CandidateCombinedName"].upper()) for r in fil
            if f"{r['FilingID']:05d} {r['CandidateCombinedName'].upper()}" in book_sen]
slate = {
    "office": "UNITED STATES SENATOR (one office listed in SEB general-election notice)",
    "filings_official": [{"filing_id": r["FilingID"], "candidate": r["CandidateCombinedName"],
                          "affiliation": r["CandidateAffiliation"], "filing_date": r["FilingDate"][:10],
                          "is_removed": r["IsRemoved"]} for r in fil],
    "candidate_list_book_page3_ids": [{"filing_id": int(i), "ballot_name": n.strip()} for i, n in book_ids],
    "withdrawals_for_us_senator": [],
    "contests_of_candidacy_for_us_senator": [],
    "nominations": {
        "Republican": {"candidate": "Kevin Hern", "how": "won June 16, 2026 primary outright (newsroom reports; official count not retrieved)"},
        "Democratic": {"candidate": "N'Kiyla Jasmine Thomas", "how": "won August 25, 2026 runoff over Jim Priest (AP call reported by KOKH; News 9 reports 61.2%; official count not retrieved)"},
        "Libertarian": {"candidate": "Sevier White", "how": "sole Libertarian filer; no primary"},
        "Independent": [{"candidate": "Curtis Stinnett", "how": "independent filer; no primary"},
                        {"candidate": "Ron Meinhardt", "how": "independent filer; no primary; News 9 describes him as a registered Republican"}],
    },
    "november_ballot_expected": ["Kevin Hern (REP)", "N'Kiyla Jasmine Thomas (DEM)", "Sevier White (LIB)",
                                 "Curtis Stinnett (IND)", "Ron Meinhardt (IND)"],
}
(OUT / "slate-2026.json").write_text(json.dumps(slate, indent=1) + "\n")
check("slate.filings_count_13", len(fil) == 13, str(len(fil)))
check("slate.no_filing_removed", all(not r["IsRemoved"] for r in fil))
check("slate.book_ids_match_portal", sorted(int(i) for i, _ in book_ids) == sorted(r["FilingID"] for r in fil),
      json.dumps(book_ids))

# --------------------------------------------------------------------------
# Summary for the report
# --------------------------------------------------------------------------
summary = {"contests": {}, "scenarios": {k: v for k, v in SC.items()}, "seb_archive_meta": {
    "2020": OKER20_META, "2024": OKER24_META,
    "2020_precincts": OKER20["UNITEDSTATESSENATOR"]["precincts"], "2024_precincts": OKER24["PRESIDENT"]["precincts"]},
    "clerk_pages": {k: v["pdf_page"] for k, v in clerk_text.items()}, "seb_code_non_alpha": SEB_CODE_NOTES}
for contest in ORDER:
    m = CONTESTS[contest]
    st = m["state"]
    summary["contests"][contest] = {k: m[k] for k in ("election_date", "office", "seat", "role", "source_id", "D", "R", "status")}
    summary["contests"][contest].update({
        "candidates": m["candidates"], "state": st,
        "other_by_candidate": {n: statesum(contest, n) for n in m["others"]},
        "d_counties": sum(1 for f in BY_FIPS if BASE[contest][f]["D"] > BASE[contest][f]["R"]),
        "precinct_ids": sum(len(precinct_counts.get((contest, f), ())) for f in BY_FIPS),
    })
(OUT / "build-summary.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
(OUT / "build-checks.json").write_text(json.dumps({"n": len(checks), "failed": [c for c in checks if not c["passed"]],
                                                   "checks": checks}, indent=1) + "\n")
nf = sum(1 for c in checks if not c["passed"])
print(f"build checks: {len(checks)} run, {nf} failed", file=sys.stderr)
sys.exit(1 if nf else 0)
