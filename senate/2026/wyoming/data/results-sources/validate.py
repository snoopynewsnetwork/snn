"""Validate the Wyoming official-results package offline.

Usage (from the repository root, after build.py):
    uv run --with pypdf==6.21.1 python3 -I senate/2026/wyoming/data/results-sources/validate.py

Writes validation.json and exits non-zero if any check fails. Checks:
  * source ids unique; every source has a manifest entry with an allowed HTTP
    status and no transport error; hash_only entries keep no bytes;
  * every stored file exists, matches its stored SHA-256/size and decompresses
    to the recorded original SHA-256 (and decoded SHA-256 for Wayback gzip);
    no orphan files under raw/; every owned file is below 40,000,000 bytes;
  * the SOS clerk directory yields exactly 23 election-page links equal to the
    23 county landing URLs requested;
  * official-results-sources.csv has exactly one row per county (23 FIPS equal
    to the turnout file), state rows only for FIPS 56, ranks/flags equal to the
    accepted priority set (15 deep, 12 in the 80% set) and no DRAFT values;
  * every deep county has a landing/results observation and >= 1 tested
    sample, and every parent->child link resolves in the retained parent;
  * SOS 2024 election-night versions: reporting counts never decrease, Total
    rows equal county sums, the night-final version covers 23 counties and the
    official version equals the certified county values;
  * county-PDF cross-checks: any difference from official values occurs only in
    documents labeled UNOFFICIAL;
  * read-only dependency hashes and relative Markdown links in official-results.md.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

HERE = Path(__file__).resolve().parent
DATA = HERE.parent
WY = DATA.parent
SOURCES = json.loads((HERE / "sources.json").read_text())["sources"]
SRC = {s["id"]: s for s in SOURCES}
MAN = json.loads((HERE / "acquisition-manifest.json").read_text())["entries"]
LINKS = json.loads((HERE / "link-extracts.json").read_text())
RECORDS = json.loads((HERE / "county-records.json").read_text())
EN = json.loads((HERE / "sos-election-night.json").read_text())
NOTES = json.loads((HERE / "county-notes.json").read_text())
TURNOUT = {r["county_fips"]: r for r in csv.DictReader((DATA / "county-turnout.csv").open(newline=""))}
INV = list(csv.DictReader((DATA / "official-results-sources.csv").open(newline="")))
checks: list[dict] = []


def check(name: str, ok: bool, detail=None) -> None:
    checks.append({"check": name, "passed": bool(ok), "detail": detail})


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def link_key(url: str) -> str:
    """Normalize for link matching: host case, percent-encoding, trailing slash; CivicPlus DocumentCenter ids."""
    u = urlsplit(unquote(url.strip()))
    path = u.path.rstrip("/")
    m = re.search(r"/DocumentCenter/View/(\d+)", path)
    if m:
        return f"{u.netloc.lower().removeprefix('www.')}/DocumentCenter/View/{m.group(1)}"
    q = f"?{u.query}" if u.query else ""
    return f"{u.netloc.lower().removeprefix('www.')}{path}{q}"


# ---------------------------------------------------------------- sources and manifest
ids = [s["id"] for s in SOURCES]
check("source ids unique", len(ids) == len(set(ids)), len(ids))
missing = [i for i in ids if i not in MAN]
check("every source has a manifest entry", not missing, missing)
errors = [i for i, e in MAN.items() if "error" in e]
check("no transport errors", not errors, errors)
bad_status = [i for i in ids if i in MAN and "error" not in MAN[i]
              and MAN[i]["http_status"] not in set(SRC[i].get("allow_status", [])) | {200}]
check("every HTTP status is allowed for its source", not bad_status, bad_status)
check("non-200 statuses are explicitly allowed and recorded",
      all(MAN[i]["http_status"] == 200 or MAN[i]["http_status"] in SRC[i].get("allow_status", []) for i in ids if i in MAN),
      {i: MAN[i]["http_status"] for i in ids if i in MAN and MAN[i]["http_status"] != 200})

hash_problems, referenced = [], set()
for i, e in MAN.items():
    if SRC[i]["mode"] == "hash_only":
        if e.get("stored_path"):
            hash_problems.append(f"{i}: hash_only but stored")
        continue
    p = HERE / e["stored_path"]
    referenced.add(p.name)
    if not p.exists():
        hash_problems.append(f"{i}: missing file")
        continue
    stored = p.read_bytes()
    if len(stored) != e["stored_bytes"] or sha256(stored) != e["stored_sha256"]:
        hash_problems.append(f"{i}: stored hash/size mismatch")
    raw = gzip.decompress(stored)
    if len(raw) != e["original_bytes"] or sha256(raw) != e["original_sha256"]:
        hash_problems.append(f"{i}: original hash/size mismatch")
    if "decoded_sha256" in e and sha256(gzip.decompress(raw)) != e["decoded_sha256"]:
        hash_problems.append(f"{i}: decoded hash mismatch")
check("stored files match manifest hashes and decompress to original bytes", not hash_problems, hash_problems)
orphans = sorted(p.name for p in (HERE / "raw").iterdir() if p.name not in referenced)
check("no orphan files in raw/", not orphans, orphans)
big = sorted(str(p.relative_to(WY)) for p in list(HERE.rglob("*")) + [DATA / "official-results-sources.csv", WY / "official-results.md"]
             if p.is_file() and p.stat().st_size >= 40_000_000)
check("every owned file is below 40,000,000 bytes", not big, big)
wb = [i for i in ids if SRC[i].get("via") == "wayback"]
check("Wayback entries carry Memento-Datetime and capture timestamp",
      all(MAN[i]["headers"].get("memento-datetime") and SRC[i].get("wayback_ts") for i in wb), len(wb))

# ---------------------------------------------------------------- authority directory and inventory
d = RECORDS["clerk_directory"]
landing_urls = {SRC[f"county-{f}-landing"]["url"] for f in TURNOUT}
check("SOS clerk directory has 23 election-page links equal to the requested county landings",
      d["link_count"] == 23 and set(d["election_page_links"]) == landing_urls,
      {"link_count": d["link_count"], "version": d["version"], "moddate": d["pdf_moddate"]})

county_rows = [r for r in INV if r["row_type"] == "county"]
state_rows = [r for r in INV if r["row_type"] == "state"]
fips = [r["county_fips"] for r in county_rows]
check("inventory covers all 23 counties exactly once", len(fips) == 23 and set(fips) == set(TURNOUT) and len(set(fips)) == 23,
      {"rows": len(fips), "unique": len(set(fips))})
check("county names match the turnout file", all(r["county"] == TURNOUT[r["county_fips"]]["county"] for r in county_rows))
check("state channel rows use FIPS 56 only", bool(state_rows) and all(r["county_fips"] == "56" for r in state_rows), len(state_rows))
flag_problems = []
for r in county_rows:
    t = TURNOUT[r["county_fips"]]
    if int(r["rank_2024_senate"]) != int(t["rank_sen2024"]) or int(r["sen2024_contest_votes"]) != int(t["sen2024_contest_votes"]):
        flag_problems.append(f"{r['county']}: rank/votes")
    if (r["investigation_scope"] == "deep") != (t["in_priority_union"] == "yes"):
        flag_problems.append(f"{r['county']}: deep flag")
    if (r["priority_group"] == "80pct_set") != (t["in_minimum80_sen2024"] == "yes"):
        flag_problems.append(f"{r['county']}: 80% flag")
check("priority flags equal the accepted set", not flag_problems, flag_problems)
deep = [r for r in county_rows if r["investigation_scope"] == "deep"]
check("15 deep counties, 12 in the 80% set",
      len(deep) == 15 and sum(r["priority_group"] == "80pct_set" for r in county_rows) == 12,
      sorted(r["county"] for r in deep))
drafts = [f"{r['scope_id']}:{k}" for r in INV for k, v in r.items() if v and "DRAFT" in v]
check("no DRAFT values in the inventory", not drafts and not NOTES.get("_draft"), drafts[:10])
check("no November 2026 counts claimed", all(r["november_2026_counts_verified"] == "no" for r in INV))

deep_gaps = []
for f, rec in RECORDS["counties"].items():
    if rec["investigation_scope"] != "deep":
        continue
    if not rec["pages_observed"]:
        deep_gaps.append(f"{rec['county']}: no page observation")
    if not rec["samples_tested"]:
        deep_gaps.append(f"{rec['county']}: no tested sample")
check("every deep county has page observations and >=1 tested sample", not deep_gaps, deep_gaps)

# ---------------------------------------------------------------- link resolution
def all_anchor_keys(sid: str) -> set[str]:
    """Every href in the retained parent page (live or commented), resolved against <base href>."""
    raw = gzip.decompress((HERE / MAN[sid]["stored_path"]).read_bytes())
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    t = raw.decode("utf-8", "replace")
    base = SRC[sid]["url"] if SRC[sid].get("via") == "wayback" else MAN[sid]["final_url"]
    m = re.search(r"<base\b[^>]*href\s*=\s*[\"']([^\"']+)[\"']", t, re.I)
    if m:
        base = urljoin(base, html.unescape(m.group(1)))
    return {link_key(urljoin(base, html.unescape(h.strip())))
            for h in re.findall(r"<a\b[^>]*?href\s*=\s*[\"']([^\"']+)[\"']", t, re.I | re.S)}


unresolved, resolved, skipped = [], 0, []
for s in SOURCES:
    par = s.get("parent")
    if not par:
        continue
    if par == "sos-county-clerk-directory":
        ok = s["url"] in d["election_page_links"]
    elif par in LINKS:
        ok = link_key(s["url"]) in all_anchor_keys(par)
    else:
        skipped.append(f"{s['id']} (parent {par} not a retained HTML page)")
        continue
    if ok:
        resolved += 1
    else:
        unresolved.append(f"{s['id']} <- {par}")
check("every child URL is linked from its retained parent page", not unresolved,
      {"resolved": resolved, "unresolved": unresolved, "skipped": skipped})
commented = [x for x in LINKS["sos-results-index"]["links"] if "2026GeneralResults" in x["url"]]
check("SOS 2026 general link exists only inside an HTML comment",
      bool(commented) and all(x["commented_out"] for x in commented), commented)
check("SOS 2026 general page returns 404", MAN["sos-2026-general-page"]["http_status"] == 404)

# ---------------------------------------------------------------- SOS election night
vers = [v for v in EN["versions"] if v.get("counties_reporting")]
counts = [v["counties_reporting"][0] for v in vers]
check("SOS 2024 counties-reporting never decreases across archived versions", counts == sorted(counts), counts)
check("SOS 2024 Total rows equal county sums in every version",
      all(v.get("total_row_equals_county_sum") for v in EN["versions"] if "total_row" in v))
check("rows present equal counties reporting in each unofficial version",
      all(v["counties_with_rows"] == v["counties_reporting"][0] for v in vers),
      [(v["id"][-14:], v["counties_with_rows"], v["counties_reporting"]) for v in vers])
check("night-final unofficial version covers 23 of 23", any(v["counties_reporting"] == [23, 23] for v in vers))
check("official 2024 SOS version equals certified county values (23 rows)",
      EN["official_version_matches_certified_county_values"] and EN["official_version_county_rows"] == 23)
check("archived official 2024 file is byte-identical to the turnout worker's current copy",
      EN["official_wayback_equals_current_turnout_copy"])
p = EN["primary_2026_tbc"]
check("2026 primary unofficial vs official ballots-cast comparison parsed for 23 counties",
      sum(1 for c in p["counties"] if c["unofficial"] and c["official"]) == 23 and p["official_total"][-1] == 150385,
      {"unofficial_total": p["unofficial_total"], "official_total": p["official_total"], "changed": p["counties_changed"]})

# ---------------------------------------------------------------- county PDF cross-checks
cross = RECORDS["senate_county_pdf_crosscheck"]
diffs = [c for c in cross if c["status"] == "differs"]
check("county PDF differences occur only in UNOFFICIAL-labeled documents",
      all(c["document_status_label"] and "UNOFFICIAL" in c["document_status_label"] for c in diffs),
      [(c["id"], c["delta_pdf_minus_official"]) for c in diffs])
check("at least one text-layer county PDF matches official values in 10+ deep counties",
      len({c["county_fips"] for c in cross if c["status"] == "match"}) >= 10,
      sorted({c["county"] for c in cross if c["status"] == "match"}))

# ---------------------------------------------------------------- dependencies and Markdown
dep = {}
for rel in ("county-turnout.csv", "baselines/primary-2026-us-senate.csv"):
    dep[rel] = sha256((DATA / rel).read_bytes())
tm = json.loads((DATA / "turnout" / "source-manifest.json").read_text())["entries"]["pdf-2026-primary-tbc"]
dep_ok = sha256((DATA / "turnout" / tm["stored_path"]).read_bytes()) == tm["original_sha256"]
check("read-only dependency hashes recorded and turnout original verified", dep_ok, dep)
md = WY / "official-results.md"
bad_links = []
if md.exists():
    for target in re.findall(r"\]\((?!https?://|#|mailto:)([^)\s]+)\)", md.read_text()):
        path = (md.parent / target.split("#")[0]).resolve()
        if not path.exists():
            bad_links.append(target)
check("official-results.md exists and its relative links resolve", md.exists() and not bad_links, bad_links)

out = {"passed": all(c["passed"] for c in checks), "checks": checks,
       "counts": {"sources": len(SOURCES), "stored": sum(1 for e in MAN.values() if e.get("stored_path")),
                  "county_rows": len(county_rows), "state_rows": len(state_rows), "deep": len(deep)}}
(HERE / "validation.json").write_text(json.dumps(out, indent=1) + "\n")
for c in checks:
    print(("PASS " if c["passed"] else "FAIL ") + c["check"])
sys.exit(0 if out["passed"] else 1)
