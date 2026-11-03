# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf==6.21.1"]
# ///
"""Independent offline validation of the Wyoming turnout package.

Run after build.py:
    uv run --with pypdf==6.21.1 python3 -I senate/2026/wyoming/data/turnout/validate.py

build.py reads the SOS Excel workbooks; this script re-reads the separately
published SOS PDF renderings and checks every county value in
../county-turnout.csv against them. It also checks hashes against
source-manifest.json, the source link chain, 23 unique counties/FIPS, sums to
official statewide totals, ballot identities, ranks, cumulative shares,
top-15/minimum-80% arithmetic (integer form), registration controls, file
sizes, and the relative links and generated table in ../../turnout.md.
Writes validation.json and exits non-zero if any check fails.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import logging
import re
import sys
from decimal import ROUND_HALF_EVEN, Decimal, getcontext
from pathlib import Path
from urllib.parse import urlparse

import pypdf

logging.getLogger("pypdf").setLevel(logging.ERROR)
getcontext().prec = 50

HERE = Path(__file__).resolve().parent
ORIG = HERE / "originals"
STATE_DIR = HERE.parent.parent
CSV_PATH = HERE.parent / "county-turnout.csv"
MD_PATH = STATE_DIR / "turnout.md"
RESULTS: list[dict] = []


def check(name, ok, detail=None):
    RESULTS.append({"check": name, "pass": bool(ok), "detail": detail})
    return ok


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def pct(num: int, den: int, places: int = 10) -> str:
    return str((Decimal(num) * 100 / Decimal(den)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_EVEN))


# ------------------------------------------------------------- manifest / hashes
manifest = json.loads((HERE / "source-manifest.json").read_text())["entries"]
sources = json.loads((HERE / "sources.json").read_text())["sources"]
check("manifest has an entry for every source in sources.json", set(manifest) == {s["id"] for s in sources},
      sorted(set(s["id"] for s in sources) ^ set(manifest)))
listed = set()
for sid, e in manifest.items():
    check(f"manifest {sid}: HTTP status recorded and allowed", e.get("http_status") in (200, 404)
          and (e["http_status"] == 200 or sid == "sos-2026-general-page"), e.get("http_status"))
    if e.get("stored_path"):
        p = HERE / e["stored_path"]
        listed.add(p.name)
        data = p.read_bytes()
        check(f"hash {sid}: stored bytes match manifest", sha(data) == e["stored_sha256"] and len(data) == e["stored_bytes"])
        orig = gzip.decompress(data) if e["stored_encoding"].startswith("gzip") else data
        check(f"hash {sid}: original response bytes match manifest", sha(orig) == e["original_sha256"]
              and len(orig) == e["original_bytes"])
    else:
        check(f"hash-only {sid}: digest recorded", bool(e.get("original_sha256")) and e.get("mode") == "hash_only")
on_disk = {p.name for p in ORIG.iterdir() if p.is_file()}
check("every file under originals/ is listed in the manifest", on_disk == listed, sorted(on_disk ^ listed))


def stored_text(sid: str) -> str:
    e = manifest[sid]
    data = (HERE / e["stored_path"]).read_bytes()
    if e["stored_encoding"].startswith("gzip"):
        data = gzip.decompress(data)
    return data.decode("utf-8", "replace")


# source chain: each child URL path appears in its stored parent page
for s in sources:
    if s.get("parent"):
        path = urlparse(s["url"]).path
        check(f"link chain {s['id']}: linked from {s['parent']}", path.lower() in stored_text(s["parent"]).lower(), path)
check("2026 general results page not yet published (HTTP 404 at retrieval)",
      manifest["sos-2026-general-page"]["http_status"] == 404, manifest["sos-2026-general-page"]["retrieved_utc"])

# ------------------------------------------------------------- geography
counties = []
for rec in csv.DictReader(open(ORIG / "st56_wy_cou2020.txt", newline=""), delimiter="|"):
    counties.append((rec["COUNTYNAME"].removesuffix(" County"), rec["STATEFP"] + rec["COUNTYFP"], rec["COUNTYNS"]))
NAMES = [c[0] for c in counties]
rows = list(csv.DictReader(open(CSV_PATH, newline="")))
byc = {r["county"]: r for r in rows}
check("CSV: exactly 23 rows", len(rows) == 23, len(rows))
check("CSV: 23 unique county names equal to Census list", sorted(byc) == sorted(NAMES))
check("CSV: 23 unique FIPS equal to Census (name, FIPS, GNIS) triples",
      sorted((r["county"], r["county_fips"], r["census_countyns"]) for r in rows) == sorted(counties))
check("CSV: FIPS are 5-character strings beginning 56", all(re.fullmatch(r"56\d{3}", r["county_fips"]) for r in rows))
I = lambda r, k: int(r[k])  # noqa: E731

# ------------------------------------------------------------- PDF re-extraction
NUM = r"\d{1,3}(?:,\d{3})*"


def pdf_pages(name):
    return [(p.extract_text(extraction_mode="layout") or "") for p in pypdf.PdfReader(ORIG / name).pages]


def parse_county_lines(text: str, width: int):
    out = {}
    for line in text.splitlines():
        s = line.strip()
        for name in NAMES + ["Total"]:
            if s.startswith(name + " "):
                rest = s[len(name):].split()
                if rest and all(re.fullmatch(NUM, t) for t in rest):
                    out[name] = [int(t.replace(",", "")) for t in rest]
    bad = {k: v for k, v in out.items() if len(v) != width}
    return out, bad


def contest_from_pdf(name, title, width):
    for page in pdf_pages(name):
        if any(l.strip() == title for l in page.splitlines()):
            got, bad = parse_county_lines(page, width)
            return got, bad
    return {}, {"missing": title}


PDF_CONTESTS = {
    "sen2024": ("2024_General_Statewide_Candidates_Summary.pdf", "United States Senator",
                ["sen2024_barrasso_r", "sen2024_morrow_d", "sen2024_write_ins", "sen2024_overvotes", "sen2024_undervotes"]),
    "gov2022": ("2022_General_Statewide_Candidates_Summary.pdf", "Governor",
                ["gov2022_gordon_r", "gov2022_livingston_d", "gov2022_baldes_l", "gov2022_write_ins",
                 "gov2022_overvotes", "gov2022_undervotes"]),
    "sen2020": ("2020_General_Statewide_Candidates_Summary.pdf", "United States Senator",
                ["sen2020_lummis_r", "sen2020_ben_david_d", "sen2020_write_ins", "sen2020_overvotes", "sen2020_undervotes"]),
}
pdf_totals = {}
for key, (fname, title, cols) in PDF_CONTESTS.items():
    got, bad = contest_from_pdf(fname, title, len(cols))
    check(f"PDF {key}: 23 county rows + Total parsed with {len(cols)} values each", not bad and set(got) == set(NAMES) | {"Total"},
          bad or sorted(set(NAMES) ^ set(got) - {"Total"}))
    mism = [(n, got.get(n), [I(byc[n], c) for c in cols]) for n in NAMES if got.get(n) != [I(byc[n], c) for c in cols]]
    check(f"PDF {key}: every county cell equals CSV (XLSX-derived)", not mism, mism)
    colsum = [sum(got[n][i] for n in NAMES) for i in range(len(cols))] if not bad else None
    check(f"PDF {key}: county rows sum to PDF Total row", colsum == got.get("Total"), [colsum, got.get("Total")])
    pdf_totals[key] = got.get("Total")

# president 2024 contest volume (PDF) vs CSV aggregate
got, bad = contest_from_pdf("2024_General_Statewide_Candidates_Summary.pdf", "United States President", 6)
check("PDF pres2024: parsed", not bad and set(got) >= set(NAMES) | {"Total"}, bad)
mism = [(n, sum(got[n][:4]), I(byc[n], "pres2024_contest_votes")) for n in NAMES
        if sum(got[n][:4]) != I(byc[n], "pres2024_contest_votes") or got[n][4] != I(byc[n], "pres2024_overvotes")
        or got[n][5] != I(byc[n], "pres2024_undervotes")]
check("PDF pres2024: county contest votes and over/under equal CSV", not mism, mism)
pdf_totals["pres2024"] = got["Total"]

TBC = {"2024": ("2024_General_Statewide_Total_Ballots_Cast_Summary.pdf", "ballots2024_total_ballots_cast"),
       "2022": ("2022_General_Statewide_Total_Ballots_Cast_Summary.pdf", "ballots2022_total_ballots_cast"),
       "2020": ("2020_General_Statewide_Total_Ballots_Cast_Summary.pdf", "ballots2020_total_ballots_cast")}
for year, (fname, col) in TBC.items():
    got, bad = parse_county_lines("\n".join(pdf_pages(fname)), 1)
    check(f"PDF ballots{year}: 23 counties + Total", not bad and set(got) == set(NAMES) | {"Total"}, bad)
    mism = [(n, got.get(n), byc[n][col]) for n in NAMES if got.get(n) != [I(byc[n], col)]]
    check(f"PDF ballots{year}: every county equals CSV", not mism, mism)
    check(f"PDF ballots{year}: counties sum to PDF Total", sum(got[n][0] for n in NAMES) == got["Total"][0])
    pdf_totals[f"ballots{year}"] = got["Total"][0]
got, bad = parse_county_lines("\n".join(pdf_pages("2026_Primary_Statewide_Total_Ballots_Cast_Summary.pdf")), 4)
pcols = ["primary2026_republican_ballots", "primary2026_democratic_ballots", "primary2026_nonpartisan_ballots",
         "primary2026_total_ballots_cast"]
check("PDF primary2026: 23 counties + Total, 4 values", not bad and set(got) == set(NAMES) | {"Total"}, bad)
mism = [(n, got.get(n)) for n in NAMES if got.get(n) != [I(byc[n], c) for c in pcols]]
check("PDF primary2026: every county party/total ballots equal CSV", not mism, mism)
pdf_totals["primary2026"] = got["Total"]

# 2022 Natrona precinct ballots PDF: printed Total vs its own rows (documented source discrepancy)
text = "\n".join(pdf_pages("2022_Natrona_County_General_PbP_TBC.pdf"))
prec = [int(m.group(2).replace(",", "")) for m in re.finditer(r"^\s*(\d+-\d+)\s+(" + NUM + r")\s*$", text, re.M)]
tot = re.search(r"^\s*Total\s+(" + NUM + r")\s*$", text, re.M)
natrona = {"precinct_rows": len(prec), "precinct_sum": sum(prec), "printed_total": int(tot.group(1).replace(",", "")),
           "statewide_summary": I(byc["Natrona"], "ballots2022_total_ballots_cast")}
check("2022 Natrona precinct ballots PDF: discrepancy reproduced (rows sum to statewide value; printed Total is +2)",
      natrona["precinct_sum"] == natrona["statewide_summary"] == 22955 and natrona["printed_total"] == 22957, natrona)

# ------------------------------------------------------------- CSV arithmetic
def comp_sum(r, parts):
    return sum(I(r, p) for p in parts)


for key, parts in {"sen2024": ["sen2024_barrasso_r", "sen2024_morrow_d", "sen2024_write_ins"],
                   "gov2022": ["gov2022_gordon_r", "gov2022_livingston_d", "gov2022_baldes_l", "gov2022_write_ins"],
                   "sen2020": ["sen2020_lummis_r", "sen2020_ben_david_d", "sen2020_write_ins"]}.items():
    check(f"CSV {key}: contest_votes = named candidates + aggregated write-ins (all counties)",
          all(comp_sum(r, parts) == I(r, f"{key}_contest_votes") for r in rows))
ident = []
for key, year in (("sen2024", "2024"), ("pres2024", "2024"), ("gov2022", "2022"), ("sen2020", "2020")):
    for r in rows:
        lhs = I(r, f"{key}_contest_votes") + I(r, f"{key}_overvotes") + I(r, f"{key}_undervotes")
        if lhs != I(r, f"ballots{year}_total_ballots_cast"):
            ident.append((key, r["county"], lhs, r[f"ballots{year}_total_ballots_cast"]))
check("CSV identity: contest votes + overvotes + undervotes = total ballots cast (4 contests x 23 counties)", not ident, ident)

STATE = {
    "sen2024_contest_votes": sum(pdf_totals["sen2024"][:3]),
    "pres2024_contest_votes": sum(pdf_totals["pres2024"][:4]),
    "ballots2024_total_ballots_cast": pdf_totals["ballots2024"],
    "gov2022_contest_votes": sum(pdf_totals["gov2022"][:4]),
    "ballots2022_total_ballots_cast": pdf_totals["ballots2022"],
    "sen2020_contest_votes": sum(pdf_totals["sen2020"][:3]),
    "ballots2020_total_ballots_cast": pdf_totals["ballots2020"],
    "primary2026_total_ballots_cast": pdf_totals["primary2026"][3],
}
for col, total in STATE.items():
    s = sum(I(r, col) for r in rows)
    check(f"CSV {col}: sums to official statewide total from PDF ({total:,})", s == total, [s, total])

RANKS = {
    "sen2024_contest_votes": ("rank_sen2024", "in_minimum80_sen2024", "in_top15_sen2024"),
    "pres2024_contest_votes": ("rank_pres2024", "in_minimum80_pres2024", None),
    "ballots2024_total_ballots_cast": ("rank_ballots2024", "in_minimum80_ballots2024", None),
    "gov2022_contest_votes": ("rank_gov2022", "in_minimum80_gov2022", "in_top15_gov2022"),
    "ballots2022_total_ballots_cast": ("rank_ballots2022", "in_minimum80_ballots2022", None),
    "sen2020_contest_votes": ("rank_sen2020", "in_minimum80_sen2020", None),
    "ballots2020_total_ballots_cast": ("rank_ballots2020", "in_minimum80_ballots2020", None),
    "primary2026_total_ballots_cast": ("rank_primary2026_ballots", None, None),
}
summary = {}
for col, (rcol, f80, f15) in RANKS.items():
    order = sorted(rows, key=lambda r: (-I(r, col), r["county_fips"]))
    check(f"rank {rcol}: ranks equal descending {col} with FIPS tie-break",
          all(I(r, rcol) == i for i, r in enumerate(order, 1)))
    T = sum(I(r, col) for r in rows)
    cum, k = 0, None
    for i, r in enumerate(order, 1):
        cum += I(r, col)
        if k is None and 5 * cum >= 4 * T:
            k, at = i, cum
    before = sum(I(r, col) for r in order[: k - 1])
    check(f"80% {col}: minimal k by integer test 5*cum_(k-1) < 4*T <= 5*cum_k", 5 * before < 4 * T <= 5 * at,
          [before, T, at, k])
    if f80:
        check(f"80% {col}: CSV flag {f80} marks exactly the first k counties",
              {r["county"] for r in rows if r[f80] == "yes"} == {r["county"] for r in order[:k]})
    top15 = sum(I(r, col) for r in order[:15])
    if f15:
        check(f"top15 {col}: CSV flag {f15} marks exactly the 15 largest",
              {r["county"] for r in rows if r[f15] == "yes"} == {r["county"] for r in order[:15]})
    summary[col] = {"total": T, "top15_votes": top15, "top15_pct": pct(top15, T), "k80": k,
                    "set80": [r["county"] for r in order[:k]], "votes80": at, "pct80": pct(at, T),
                    "before80": before, "pct_before80": pct(before, T), "crossing": order[k - 1]["county"]}

# sensitivity measures (named candidates only), recomputed from CSV components
for key, parts in (("sen2024_named_candidate_votes", ["sen2024_barrasso_r", "sen2024_morrow_d"]),
                   ("gov2022_named_candidate_votes", ["gov2022_gordon_r", "gov2022_livingston_d", "gov2022_baldes_l"])):
    v = {r["county"]: sum(I(r, c) for c in parts) for r in rows}
    T = sum(v.values())
    order = sorted(rows, key=lambda r: (-v[r["county"]], r["county_fips"]))
    cum, k = 0, None
    for i, r in enumerate(order, 1):
        cum += v[r["county"]]
        if k is None and 5 * cum >= 4 * T:
            k, at = i, cum
    b = json.loads((HERE / "rankings.json").read_text())["rankings"][key]
    check(f"rankings.json {key}: sensitivity total/minimum-80 set agree with recomputation",
          (T, k, [r["county"] for r in order[:k]], at) == (b["statewide_total"], b["minimum80_k"], b["minimum80_set"], b["minimum80_votes"]))
    summary[key] = {"total": T, "k80": k, "set80": [r["county"] for r in order[:k]], "votes80": at, "pct80": pct(at, T),
                    "top15": [r["county"] for r in order[:15]]}

base = sorted(rows, key=lambda r: I(r, "rank_sen2024"))
cum = 0
okc = True
for r in base:
    cum += I(r, "sen2024_contest_votes")
    okc &= cum == I(r, "sen2024_cumulative_contest_votes")
    okc &= r["sen2024_cumulative_pct"] == pct(cum, STATE["sen2024_contest_votes"])
    okc &= r["sen2024_share_pct"] == pct(I(r, "sen2024_contest_votes"), STATE["sen2024_contest_votes"])
check("CSV sen2024 shares/cumulative votes/cumulative pct recomputed from integers", okc)
for col, scol in (("ballots2024_total_ballots_cast", "ballots2024_share_pct"), ("gov2022_contest_votes", "gov2022_share_pct"),
                  ("ballots2022_total_ballots_cast", "ballots2022_share_pct"), ("sen2020_contest_votes", "sen2020_share_pct")):
    check(f"CSV {scol} recomputed", all(r[scol] == pct(I(r, col), STATE[col]) for r in rows))
union = {r["county"] for r in rows if r["in_top15_sen2024"] == "yes" or r["in_minimum80_sen2024"] == "yes"}
check("CSV in_priority_union = top15 OR minimum80 (2024 Senate)", union == {r["county"] for r in rows if r["in_priority_union"] == "yes"})

# rankings.json agrees with independent recomputation
rk = json.loads((HERE / "rankings.json").read_text())["rankings"]
mapping = {"sen2024_contest_votes": "sen2024_contest_votes", "pres2024_contest_votes": "pres2024_contest_votes",
           "ballots2024_total_ballots_cast": "ballots2024", "gov2022_contest_votes": "gov2022_contest_votes",
           "ballots2022_total_ballots_cast": "ballots2022", "sen2020_contest_votes": "sen2020_contest_votes",
           "ballots2020_total_ballots_cast": "ballots2020", "primary2026_total_ballots_cast": "primary2026_ballots"}
for col, key in mapping.items():
    a, b = summary[col], rk[key]
    check(f"rankings.json {key}: total/top15/minimum-80 agree with recomputation",
          (a["total"], a["top15_votes"], a["k80"], a["set80"], a["votes80"], a["crossing"]) ==
          (b["statewide_total"], b["top15_votes"], b["minimum80_k"], b["minimum80_set"], b["minimum80_votes"], b["crossing_county"]))

# ------------------------------------------------------------- registration
reg = list(csv.DictReader(open(HERE / "registration-snapshots.csv", newline="")))
REGCOL = {"reg2024": "reg2024_11_05_general_election_day_total", "reg2022": "reg2022_11_08_general_election_day_total",
          "reg2020": "reg2020_11_03_general_election_day_total", "reg2026_10_01": "reg2026_10_01_total"}
vp = "\n".join((p.extract_text() or "") for p in pypdf.PdfReader(ORIG / "VoterProfile.pdf").pages)
vp_years = {}
for line in vp.splitlines():
    m = re.match(r"^(20\d\d)\s+(.*)$", line.strip())
    if m:
        vp_years[m.group(1)] = [int(t.replace(",", "")) for t in re.findall(NUM + r"(?![\d.%])", m.group(2))]
for snap, col in REGCOL.items():
    sub = {r["county"]: int(r["TOTAL"]) for r in reg if r["snapshot"] == snap}
    check(f"registration {snap}: 23 counties and CSV column equals snapshot TOTAL",
          sorted(sub) == sorted(NAMES) and all(sub[n] == I(byc[n], col) for n in NAMES))
for year in ("2024", "2022", "2020"):
    col = REGCOL[f"reg{year}"]
    s = sum(I(r, col) for r in rows)
    check(f"registration {year}: county sum equals VoterProfile general registered", s == vp_years[year][3],
          [s, vp_years[year]])
    check(f"ballots {year}: statewide total equals VoterProfile general turnout",
          STATE[f"ballots{year}_total_ballots_cast"] == vp_years[year][4], vp_years[year])
check("2026 primary ballots equal VoterProfile 2026 primary turnout", STATE["primary2026_total_ballots_cast"] == vp_years["2026"][2],
      vp_years["2026"])
over_reg = {y: sorted(r["county"] for r in rows if I(r, f"ballots{y}_total_ballots_cast") > I(r, REGCOL[f"reg{y}"]))
            for y in ("2024", "2022", "2020")}

# ------------------------------------------------------------- precinct reconciliation summary
pr = list(csv.DictReader(open(HERE / "precinct-reconciliation.csv", newline="")))
contest_fail = [(r["contest"], r["county"]) for r in pr if r["contest_rows_reconciled"] == "no"]
ballot_fail = [(r["contest"], r["county"], r["ballots_precinct_sum"], r["ballots_sheet_total"], r["statewide_summary_ballots"])
               for r in pr if r["ballots_rows_reconciled"] == "no"]
check("precinct workbooks: every contest block reconciles precinct rows -> county Total -> statewide county row",
      not contest_fail and len([r for r in pr if r["contest_rows_reconciled"] == "yes"]) == 4 * 23, contest_fail)
check("precinct ballots workbooks: only the documented 2022 Natrona Total-row exception fails",
      ballot_fail == [("gov2022", "Natrona", "22955", "22957", "22955")], ballot_fail)

# ------------------------------------------------------------- sizes
big = [(str(p.relative_to(STATE_DIR)), p.stat().st_size) for p in HERE.rglob("*") if p.is_file() and p.stat().st_size >= 40_000_000]
check("every owned file is below 40,000,000 bytes", not big, big)

# ------------------------------------------------------------- markdown
if MD_PATH.exists():
    md = MD_PATH.read_text()
    links = re.findall(r"\]\(([^)\s]+)\)", md)
    rel = [l for l in links if not re.match(r"^[a-z]+://", l) and not l.startswith("#")]
    missing = [l for l in rel if not (MD_PATH.parent / l.split("#")[0]).exists()]
    check("turnout.md: every relative link resolves", not missing and rel, missing)
    table = [l for l in (HERE / "ranking-table.md").read_text().splitlines() if l.startswith("|")]
    check("turnout.md: contains the generated all-county ranking table verbatim", all(l in md.splitlines() for l in table),
          [l for l in table if l not in md.splitlines()])
    s = summary["sen2024_contest_votes"]
    for needle in (f"{s['top15_votes']:,} / {s['total']:,}", f"{Decimal(s['top15_pct']).quantize(Decimal('0.0001'))}%",
                   f"{s['votes80']:,} / {s['total']:,}", f"{Decimal(s['pct80']).quantize(Decimal('0.0001'))}%",
                   f"5 * {s['before80']:,}", ", ".join(s["set80"])):
        check(f"turnout.md mentions {needle!r}", needle in md)
else:
    check("turnout.md exists", False)

failed = [r for r in RESULTS if not r["pass"]]
out = {
    "generated_by": "validate.py",
    "checks_total": len(RESULTS),
    "checks_failed": len(failed),
    "pdf_statewide_totals": pdf_totals,
    "summary": summary,
    "counties_with_ballots_above_pre_election_registration": over_reg,
    "natrona_2022_precinct_ballots_pdf": natrona,
    "checks": RESULTS,
}
(HERE / "validation.json").write_text(json.dumps(out, indent=2) + "\n")
print(f"{len(RESULTS)} checks, {len(failed)} failed")
for f in failed:
    print("FAIL", f["check"], str(f["detail"])[:300])
print("ballots > pre-election registration:", {k: len(v) for k, v in over_reg.items()})
sys.exit(1 if failed else 0)
