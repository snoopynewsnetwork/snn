"""Build the Wyoming official-results inventory from retained evidence (offline).

Usage (from the repository root):
    uv run --with pypdf==6.21.1 python3 -I senate/2026/wyoming/data/results-sources/build.py

Reads only files in this directory plus read-only first-wave dependencies
(../county-turnout.csv, ../baselines/primary-2026-us-senate.csv and
../turnout/source-manifest.json with the turnout originals it lists). Writes:

  link-extracts.json            results-related links in every retained HTML page
                                (honouring <base href>, live vs commented-out anchors)
  sample-extracts.json          metadata, status labels, reporting fields, printed
                                clocks and U.S. Senate lines from every retained PDF
  sos-election-night-2024.csv   SOS 2024 U.S. Senate county rows in each archived
                                version of the statewide candidates summary
  sos-election-night.json       version timeline, revisions against the certified
                                county values, 2026 primary ballots-cast revisions
  county-records.json           one record per county (all 23) with evidence ids
  build-summary.json            counts used by validate.py
  ../official-results-sources.csv   the inventory (state channel rows + 23 county rows)
"""

from __future__ import annotations

import csv
import datetime as dt
import gzip
import hashlib
import html
import io
import json
import re
from pathlib import Path
from urllib.parse import urljoin, quote

import pypdf

HERE = Path(__file__).resolve().parent
DATA = HERE.parent
SOURCES = json.loads((HERE / "sources.json").read_text())["sources"]
SRC = {s["id"]: s for s in SOURCES}
MAN = json.loads((HERE / "acquisition-manifest.json").read_text())["entries"]
NOTES = json.loads((HERE / "county-notes.json").read_text())
TURNOUT = list(csv.DictReader((DATA / "county-turnout.csv").open(newline="")))
TURNOUT_MAN = json.loads((DATA / "turnout" / "source-manifest.json").read_text())["entries"]
PRIMARY26 = list(csv.DictReader((DATA / "baselines" / "primary-2026-us-senate.csv").open(newline="")))

COUNTIES = {r["county_fips"]: r for r in TURNOUT}
NAMES = {r["county"]: r["county_fips"] for r in TURNOUT}
NAME_RE = "|".join(sorted((re.escape(n) for n in NAMES), key=len, reverse=True))
RESULT_WORDS = re.compile(
    r"result|unofficial|official|canvass|election night|summary|precinct|return|abstract|recount|test|placeholder|"
    r"clarity|scytl|electionstats|knowink|enhanced voting|enr\b", re.I)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def body(sid: str) -> bytes:
    e = MAN[sid]
    raw = gzip.decompress((HERE / e["stored_path"]).read_bytes())
    assert sha256(raw) == e["original_sha256"], sid
    if raw[:2] == b"\x1f\x8b":  # Wayback passes through original gzip transfer encoding
        raw = gzip.decompress(raw)
    return raw


def stored(sid: str) -> bool:
    e = MAN.get(sid)
    return bool(e and e.get("stored_path") and "error" not in e)


# ----------------------------------------------------------------- HTML links
ANCHOR = re.compile(r"<a\b[^>]*?href\s*=\s*[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", re.S | re.I)


def page_links(sid: str) -> dict:
    t = body(sid).decode("utf-8", "replace")
    base = MAN[sid]["final_url"] if SRC[sid].get("via") != "wayback" else SRC[sid]["url"]
    m = re.search(r"<base\b[^>]*href\s*=\s*[\"']([^\"']+)[\"']", t, re.I)
    base_href = None
    if m:
        base_href = html.unescape(m.group(1))
        base = urljoin(base, base_href)
    comments = [(c.start(), c.end()) for c in re.finditer(r"<!--.*?-->", t, re.S)]

    def in_comment(pos: int) -> bool:
        return any(a <= pos < b for a, b in comments)

    page_url = (MAN[sid]["final_url"] if SRC[sid].get("via") != "wayback" else SRC[sid]["url"]).split("#")[0]
    out, seen = [], set()
    for a in ANCHOR.finditer(t):
        href = html.unescape(a.group(1).strip())
        text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", a.group(2))).split())
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        url = urljoin(base, href)
        if url.split("#")[0] in (page_url, base.split("#")[0]):
            continue
        if not (RESULT_WORDS.search(url) or RESULT_WORDS.search(text)):
            continue
        key = (url, text, in_comment(a.start()))
        if key in seen:
            continue
        seen.add(key)
        out.append({"text": text[:160], "href": href, "url": url, "commented_out": in_comment(a.start())})
    title = re.search(r"<title[^>]*>(.*?)</title>", t, re.S | re.I)
    h = re.search(r"<h3[^>]*panel-heading[^>]*>(.*?)</h3>", t, re.S | re.I)
    return {"id": sid, "base_href": base_href, "resolved_base": base,
            "title": " ".join(html.unescape(title.group(1)).split()) if title else None,
            "panel_heading": " ".join(re.sub(r"<[^>]+>", " ", h.group(1)).split()) if h else None,
            "links": out}


def normalized(url: str) -> str:
    return quote(html.unescape(url), safe=":/?&=%#+,;@!$'()*~")


# ----------------------------------------------------------------- PDFs
PRINTED_CLOCK = re.compile(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*([AP]\.?M\.?)?\s*(M[DS]T|MT)?", re.I)
REPORTING = re.compile(
    r"(Election Day Precincts Reporting|Precincts Complete|Precincts Partially Reported|Absentee/ ?Early Precincts Reporting|"
    r"Precincts Reported|Precincts Reporting|Counties Reporting:?)\s*(\d+)\s+of\s+(\d+)", re.I)
STATUS = re.compile(r"\b(UNOFFICIAL|OFFICIAL|PRELIMINARY|TEST|ZERO|RECOUNT|PLACEHOLDER|CERTIFIED|CANVASS(?:ED)?)\b", re.I)
INT = re.compile(r"(?<![\d.,%])\d{1,3}(?:,\d{3})*(?![\d.,]*%)")


def pdf_text(raw: bytes) -> tuple[pypdf.PdfReader, list[str]]:
    r = pypdf.PdfReader(io.BytesIO(raw))
    return r, [(p.extract_text() or "") for p in r.pages]


def candidate_line(text: str, surname: str) -> list[int] | None:
    for line in text.splitlines():
        if re.search(rf"\b{surname}\b", line, re.I):
            tail = re.split(rf"\b{surname}\b", line, flags=re.I, maxsplit=1)[1]
            nums = [int(x.replace(",", "")) for x in INT.findall(tail)]
            if nums:
                return nums
    return None


def pdf_extract(sid: str) -> dict:
    raw = body(sid)
    rec = {"id": sid, "scope": SRC[sid]["scope"], "kind": SRC[sid]["kind"], "election": SRC[sid]["election"],
           "stage_in_source_list": SRC[sid]["stage"], "bytes": len(raw), "sha256": sha256(raw)}
    try:
        r, pages = pdf_text(raw)
    except Exception as err:  # malformed PDFs are recorded, not dropped
        rec["error"] = repr(err)
        return rec
    meta = {k: str(v) for k, v in (r.metadata or {}).items()}
    rec["pages"] = len(pages)
    rec["metadata"] = {k: meta[k] for k in ("/Title", "/Author", "/Creator", "/Producer", "/CreationDate", "/ModDate") if k in meta}
    first = pages[0] if pages else ""
    alltext = "\n".join(pages)
    rec["text_chars"] = len("".join(alltext.split()))
    rec["text_layer"] = rec["text_chars"] >= 40 * max(1, len(pages))
    rec["first_page_head"] = " ".join(first.split())[:400]
    rec["status_labels_first_page"] = sorted({m.group(1).upper() for m in STATUS.finditer(first)})
    rec["reporting_fields"] = [" ".join(m.groups()) for m in REPORTING.finditer(alltext)][:12]
    rec["printed_clocks"] = sorted({" ".join(x for x in m.groups() if x) for m in PRINTED_CLOCK.finditer(alltext)})[:12]
    rec["mentions"] = sorted({w for w in ("Electionware", "JasperReports", "ES&S", "Election Systems", "DS200", "DS450", "DS850",
                                          "ExpressVote", "Google Sheets", "Skia/PDF") if w.lower() in (alltext + json.dumps(meta)).lower()})
    if SRC[sid]["election"] == "2024-general":
        rec["senate_2024"] = {"barrasso": candidate_line(alltext, "BARRASSO"), "morrow": candidate_line(alltext, "MORROW")}
    if SRC[sid]["election"] == "2026-primary":
        rec["senate_2026_primary"] = {"hageman": candidate_line(alltext, "HAGEMAN"), "byrd": candidate_line(alltext, "BYRD")}
    if SRC[sid]["election"] == "2026-general":
        rec["senate_2026_general_test_lines"] = {"hageman": candidate_line(alltext, "HAGEMAN"), "byrd": candidate_line(alltext, "BYRD")}
    return rec


# ----------------------------------------------------------------- SOS election-night parsing
COUNTY_ROW = re.compile(rf"^\s*({NAME_RE}|Total)\b(.*)$")


def sos_section(raw: bytes, header: str) -> dict:
    """Parse one contest page of the SOS statewide summary in layout mode."""
    r = pypdf.PdfReader(io.BytesIO(raw))
    for p in r.pages:
        t = p.extract_text(extraction_mode="layout")
        if header.lower() not in t.lower():
            continue
        lines = t.splitlines()
        out = {"counties_reporting": None, "last_updated_printed": None, "rows": {}, "status_line": None}
        for i, line in enumerate(lines):
            s = line.strip()
            m = re.search(r"(\d+)\s+of\s+(\d+)", s)
            if out["counties_reporting"] is None and m and any("Counties Reporting" in x for x in lines[max(0, i - 2):i + 1]):
                out["counties_reporting"] = [int(m.group(1)), int(m.group(2))]
            if "Last Updated" in s:
                tail = s.split("Last Updated:", 1)[-1].strip() or (lines[i + 1].strip() if i + 1 < len(lines) else "")
                out["last_updated_printed"] = tail
            if re.search(r"\b(UNOFFICIAL|OFFICIAL) RESULTS\b", s):
                out["status_line"] = s
            cm = COUNTY_ROW.match(line)
            if cm and not re.search(r"Counties Reporting", s):
                nums = [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3})*", cm.group(2))]
                out["rows"][cm.group(1)] = nums
        return out
    return {}


def to_utc(printed: str | None) -> dict:
    """Interpret the SOS 'Last Updated' clock. The label says MDT but 2024-11-05 was MST."""
    if not printed:
        return {}
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2})\s+(\d{1,2}):(\d{2}):(\d{2})\s*(\w+)?", printed)
    if not m:
        return {"printed": printed}
    mo, d, y, hh, mm, ss, tz = m.groups()
    local = dt.datetime(2000 + int(y), int(mo), int(d), int(hh), int(mm), int(ss))
    return {"printed": printed, "printed_zone_label": tz,
            "utc_if_label_mdt": (local + dt.timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "utc_if_mst": (local + dt.timedelta(hours=7)).strftime("%Y-%m-%dT%H:%M:%SZ")}


def http_date_utc(s: str | None) -> str | None:
    if not s:
        return None
    return dt.datetime.strptime(s, "%a, %d %b %Y %H:%M:%S GMT").strftime("%Y-%m-%dT%H:%M:%SZ")


def election_night() -> tuple[list[dict], dict]:
    rows, versions = [], []
    official = {r["county"]: r for r in TURNOUT}
    ids = sorted(k for k in MAN if k.startswith("wb-sos-2024-candidates-") and stored(k))
    for sid in ids:
        e = MAN[sid]
        raw = body(sid)
        r = pypdf.PdfReader(io.BytesIO(raw))
        meta = {k: str(v) for k, v in (r.metadata or {}).items()}
        sec = sos_section(raw, "United States Senator")
        v = {"id": sid, "memento_utc": http_date_utc(e["headers"].get("memento-datetime")),
             "orig_last_modified_utc": http_date_utc(e["headers"].get("x-archive-orig-last-modified")),
             "pdf_title": meta.get("/Title"), "pdf_creation": meta.get("/CreationDate"), "pages": len(r.pages),
             "sha256": sha256(raw)}
        if not sec:
            v["content"] = "placeholder text only: " + " ".join((r.pages[0].extract_text() or "").split())[:300]
            versions.append(v)
            continue
        v.update({"counties_reporting": sec["counties_reporting"], "status_line": sec["status_line"],
                  "last_updated": to_utc(sec["last_updated_printed"])})
        reported = [c for c in NAMES if sec["rows"].get(c)]
        v["counties_with_rows"] = len(reported)
        tot = sec["rows"].get("Total")
        if tot:
            sums = [sum(sec["rows"][c][i] for c in reported) for i in range(len(tot))]
            v["total_row"] = tot
            v["total_row_equals_county_sum"] = sums == tot
        v["blank_counties"] = [c for c in NAMES if not sec["rows"].get(c)]
        for c in sorted(NAMES, key=lambda n: NAMES[n]):
            vals = sec["rows"].get(c) or []
            o = official[c]
            rec = {"version_id": sid, "memento_utc": v["memento_utc"], "orig_last_modified_utc": v["orig_last_modified_utc"],
                   "printed_last_updated": (v.get("last_updated") or {}).get("printed"),
                   "counties_reporting": "/".join(map(str, sec["counties_reporting"] or [])),
                   "county": c, "county_fips": NAMES[c], "reported": "yes" if vals else "blank"}
            for i, k in enumerate(("barrasso_r", "morrow_d", "write_ins", "overvotes", "undervotes")):
                rec[k] = vals[i] if len(vals) == 5 else ""
            if len(vals) == 5:
                rec["delta_vs_certified_barrasso"] = vals[0] - int(o["sen2024_barrasso_r"])
                rec["delta_vs_certified_morrow"] = vals[1] - int(o["sen2024_morrow_d"])
                rec["delta_vs_certified_write_ins"] = vals[2] - int(o["sen2024_write_ins"])
                rec["delta_vs_certified_under"] = vals[4] - int(o["sen2024_undervotes"])
            else:
                rec.update({k: "" for k in ("delta_vs_certified_barrasso", "delta_vs_certified_morrow",
                                            "delta_vs_certified_write_ins", "delta_vs_certified_under")})
            rows.append(rec)
        versions.append(v)
    # first-appearance and revision summary per county
    first_seen, last_unofficial = {}, {}
    for rec in rows:
        if rec["reported"] != "yes":
            continue
        vid = rec["version_id"]
        if "20241127" in vid:
            continue
        first_seen.setdefault(rec["county"], rec)
        last_unofficial[rec["county"]] = rec
    revisions = []
    for c in sorted(NAMES, key=lambda n: NAMES[n]):
        f, l = first_seen.get(c), last_unofficial.get(c)
        revisions.append({
            "county": c, "county_fips": NAMES[c],
            "first_seen_version": f and f["version_id"], "first_seen_printed": f and f["printed_last_updated"],
            "first_seen_vs_certified": f and [f["delta_vs_certified_barrasso"], f["delta_vs_certified_morrow"],
                                              f["delta_vs_certified_write_ins"], f["delta_vs_certified_under"]],
            "last_unofficial_version": l and l["version_id"],
            "last_unofficial_vs_certified": l and [l["delta_vs_certified_barrasso"], l["delta_vs_certified_morrow"],
                                                   l["delta_vs_certified_write_ins"], l["delta_vs_certified_under"]],
            "changed_between_archived_unofficial_versions": bool(f and l and (f["barrasso_r"], f["morrow_d"], f["write_ins"], f["undervotes"])
                                                                != (l["barrasso_r"], l["morrow_d"], l["write_ins"], l["undervotes"])),
        })
    off_rows = [r for r in rows if "20241127" in r["version_id"] and r["reported"] == "yes"]
    summary = {"versions": versions, "county_revisions": revisions,
               "official_version_matches_certified_county_values": bool(off_rows) and all(
                   r["delta_vs_certified_barrasso"] == 0 and r["delta_vs_certified_morrow"] == 0 and
                   r["delta_vs_certified_write_ins"] == 0 and r["delta_vs_certified_under"] == 0 for r in off_rows),
               "official_version_county_rows": len(off_rows)}
    # official-version bytes against the turnout worker's current retrieval of the same URL
    tm = TURNOUT_MAN.get("pdf-2024-candidates", {})
    wbo = [v for v in versions if "20241127" in v["id"]]
    summary["official_wayback_equals_current_turnout_copy"] = bool(wbo and tm and wbo[0]["sha256"] == tm.get("original_sha256"))
    return rows, summary


def tbc_versions() -> dict:
    out = []
    for sid in sorted(k for k in MAN if k.startswith("wb-sos-2024-tbc-") and stored(k)):
        raw = body(sid)
        r = pypdf.PdfReader(io.BytesIO(raw))
        sec = None
        for p in r.pages:
            t = p.extract_text(extraction_mode="layout")
            if "Counties Reporting" in t or "Total Ballots" in t:
                sec = t
                break
        cr = re.search(r"Counties Reporting:?\s*(?:\n\s*)?(\d+)\s+of\s+(\d+)", sec or "")
        lu = re.search(r"Last Updated:?\s*(?:\n\s*)?([0-9/]+\s+[0-9:]+\s*\w*)", sec or "")
        rows = {}
        for line in (sec or "").splitlines():
            m = COUNTY_ROW.match(line)
            if m:
                rows[m.group(1)] = [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3})*", m.group(2))]
        e = MAN[sid]
        out.append({"id": sid, "memento_utc": http_date_utc(e["headers"].get("memento-datetime")),
                    "orig_last_modified_utc": http_date_utc(e["headers"].get("x-archive-orig-last-modified")),
                    "counties_reporting": [int(cr.group(1)), int(cr.group(2))] if cr else None,
                    "last_updated": to_utc(lu.group(1).strip()) if lu else None,
                    "total_row": rows.get("Total"), "county_rows_nonblank": sum(1 for c in NAMES if rows.get(c))})
    return {"versions": out}


def primary_tbc_revisions() -> dict:
    sid = "wb-sos-2026-primary-tbc-20260820035058"
    if not stored(sid):
        return {"error": "unofficial version not retained"}

    def parse(raw: bytes) -> dict:
        r = pypdf.PdfReader(io.BytesIO(raw))
        rows = {}
        for p in r.pages:
            for line in p.extract_text(extraction_mode="layout").splitlines():
                m = COUNTY_ROW.match(line)
                if m:
                    nums = [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3})*", m.group(2))]
                    if nums:
                        rows[m.group(1)] = nums
        return rows
    un = parse(body(sid))
    tm = TURNOUT_MAN["pdf-2026-primary-tbc"]
    off_raw = (DATA / "turnout" / tm["stored_path"]).read_bytes()
    assert sha256(off_raw) == tm["original_sha256"]
    off = parse(off_raw)
    diffs = []
    for c in sorted(NAMES, key=lambda n: NAMES[n]):
        u, o = un.get(c), off.get(c)
        diffs.append({"county": c, "county_fips": NAMES[c], "unofficial": u, "official": o,
                      "delta_last_column": (u[-1] - o[-1]) if u and o else None})
    return {"unofficial_id": sid, "official_dependency": "../turnout/" + tm["stored_path"],
            "unofficial_memento_utc": http_date_utc(MAN[sid]["headers"].get("memento-datetime")),
            "unofficial_orig_last_modified_utc": http_date_utc(MAN[sid]["headers"].get("x-archive-orig-last-modified")),
            "official_last_modified": TURNOUT_MAN["pdf-2026-primary-tbc"]["headers"].get("last-modified"),
            "unofficial_total": un.get("Total"), "official_total": off.get("Total"), "counties": diffs,
            "counties_changed": [d["county"] for d in diffs if d["delta_last_column"] not in (0, None)]}


# ----------------------------------------------------------------- clerk directory
def clerk_directory() -> dict:
    raw = body("sos-county-clerk-directory")
    r = pypdf.PdfReader(io.BytesIO(raw))
    uris = []
    for p in r.pages:
        for a in p.get("/Annots") or []:
            o = a.get_object()
            act = o.get("/A")
            if act and act.get("/URI"):
                uris.append(str(act["/URI"]))
    web = [u for u in uris if not u.lower().startswith("mailto:") and "sos.wyo.gov" not in u]
    meta = {k: str(v) for k, v in (r.metadata or {}).items()}
    version = re.search(r"Version\s+([\d.]+)", r.pages[0].extract_text() or "")
    return {"pdf_title": meta.get("/Title"), "pdf_moddate": meta.get("/ModDate"), "version": version and version.group(1),
            "election_page_links": web, "link_count": len(web)}


# ----------------------------------------------------------------- assemble
def main() -> None:
    html_ids = [k for k, e in MAN.items() if stored(k) and e["stored_path"].endswith(".html.gz")]
    pdf_ids = [k for k, e in MAN.items() if stored(k) and e["stored_path"].endswith(".pdf.gz")]
    links = {k: page_links(k) for k in html_ids}
    samples = {k: pdf_extract(k) for k in pdf_ids}
    (HERE / "link-extracts.json").write_text(json.dumps(links, indent=1) + "\n")
    (HERE / "sample-extracts.json").write_text(json.dumps(samples, indent=1) + "\n")

    en_rows, en = election_night()
    en["tbc_2024"] = tbc_versions()
    en["primary_2026_tbc"] = primary_tbc_revisions()
    with (HERE / "sos-election-night-2024.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(en_rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(en_rows)
    (HERE / "sos-election-night.json").write_text(json.dumps(en, indent=1) + "\n")
    directory = clerk_directory()

    # county-PDF U.S. Senate cross-checks against the SOS official county values
    p26 = {}
    for r in PRIMARY26:
        if r["native_header"] in ("Harriet Hageman", "James Byrd"):
            p26[(r["county_fips"], r["native_header"].split()[-1].lower())] = int(r["votes"])
    cross = []
    for k, s in samples.items():
        if s["scope"] == "56" or s["kind"] == "county_setup_test" or s["kind"] == "county_setup_placeholder":
            continue
        o = COUNTIES[s["scope"]]
        if "senate_2024" in s:
            pair, ref = s["senate_2024"], {"barrasso": int(o["sen2024_barrasso_r"]), "morrow": int(o["sen2024_morrow_d"])}
            contest = "2024 general U.S. Senate (certified SOS county row)"
        elif "senate_2026_primary" in s:
            pair, ref = s["senate_2026_primary"], {"hageman": p26.get((s["scope"], "hageman")), "byrd": p26.get((s["scope"], "byrd"))}
            contest = "2026 primary U.S. Senate, Hageman (REP) and Byrd (DEM) (SOS official primary ZIP county row)"
        else:
            continue
        got = {c: (v[0] if v else None) for c, v in pair.items()}
        if not s.get("text_layer"):
            status = "not_parsed_no_text_layer"
        elif any(v is None for v in got.values()):
            status = "not_found_in_text"
        elif all(got[c] == ref[c] for c in ref):
            status = "match"
        else:
            status = "differs"
        cross.append({"id": k, "county": o["county"], "county_fips": s["scope"], "contest": contest,
                      "document_status_label": "/".join(s.get("status_labels_first_page") or []) or None,
                      "pdf_first_integer": got, "sos_official": ref,
                      "delta_pdf_minus_official": {c: (got[c] - ref[c]) if got[c] is not None and ref[c] is not None else None for c in ref},
                      "status": status})

    records, csv_rows = {}, []
    for fips, o in sorted(COUNTIES.items(), key=lambda kv: int(kv[1]["rank_sen2024"])):
        note = NOTES["counties"][fips]
        src_ids = [s["id"] for s in SOURCES if s["scope"] == fips]
        landing = MAN.get(f"county-{fips}-landing", {})
        tested = [i for i in src_ids if i in MAN and "error" not in MAN[i] and MAN[i]["http_status"] == 200
                  and SRC[i]["kind"] in ("county_sample", "county_setup_test", "county_setup_placeholder", "wayback_county_sample")]
        pages = [i for i in src_ids if i in MAN and "error" not in MAN[i] and SRC[i]["kind"] in ("county_landing", "county_results_page", "wayback_county_page")]
        rec = {
            "county": o["county"], "county_fips": fips, "rank_2024_senate": int(o["rank_sen2024"]),
            "sen2024_contest_votes": int(o["sen2024_contest_votes"]),
            "priority_group": "80pct_set" if o["in_minimum80_sen2024"] == "yes" else ("top15_only" if o["in_top15_sen2024"] == "yes" else "inventory_only"),
            "investigation_scope": "deep" if o["in_priority_union"] == "yes" else "discovery",
            "sos_directory_link": SRC[f"county-{fips}-landing"]["url"],
            "sos_directory_link_present": SRC[f"county-{fips}-landing"]["url"] in directory["election_page_links"],
            "landing": {k: landing.get(k) for k in ("http_status", "final_url", "retrieved_utc", "html_title", "original_sha256", "stored_path")},
            "pages_observed": pages, "samples_tested": tested,
            "sample_summaries": {i: {k: samples[i].get(k) for k in ("status_labels_first_page", "reporting_fields", "printed_clocks", "mentions", "metadata", "first_page_head")}
                                 for i in tested if i in samples},
            "senate_crosscheck": [c for c in cross if c["county_fips"] == fips],
            **note,
        }
        records[fips] = rec
        csv_rows.append({
            "row_type": "county", "scope_id": fips, "county": o["county"], "county_fips": fips,
            "rank_2024_senate": rec["rank_2024_senate"], "sen2024_contest_votes": rec["sen2024_contest_votes"],
            "priority_group": rec["priority_group"], "investigation_scope": rec["investigation_scope"],
            "authority_chain": note["authority_chain"], "sos_directory_url": "https://sos.wyo.gov/Elections/Docs/WYCountyClerks.pdf",
            "primary_url": rec["sos_directory_link"], "landing_http_status": landing.get("http_status"),
            "landing_final_url": landing.get("final_url"), "landing_retrieved_utc": landing.get("retrieved_utc"),
            "landing_access": note["landing_access"], "results_page_url": note.get("results_page_url", ""),
            "web_platform": note["web_platform"], "tabulation_system_evidence": note["tabulation_system_evidence"],
            "results_publication_format": note["results_publication_format"], "linked_results_vendor": note["linked_results_vendor"],
            "election_night_product_evidence": note["election_night_product_evidence"], "official_product": note["official_product"],
            "url_behavior_unofficial_to_official": note["url_behavior_unofficial_to_official"],
            "completion_fields": note["completion_fields"], "timestamp_evidence": note["timestamp_evidence"],
            "corrections_revisions": note["corrections_revisions"], "november_2026_setup": note["november_2026_setup"],
            "november_2026_counts_verified": "no", "november_2026_results_url_verified": note["november_2026_results_url_verified"],
            "cadence_status": note["cadence_status"], "tested_feeds": " | ".join(tested),
            "senate_crosscheck": "; ".join(f"{c['id']}: {c['status']}" for c in rec["senate_crosscheck"]),
            "access_issues": note["access_issues"], "manual_fallback": note["manual_fallback"], "gaps": note["gaps"],
            "evidence_record": "results-sources/county-records.json#" + fips,
        })
    state_rows = []
    for s in NOTES["state_channels"]:
        row = {k: "" for k in csv_rows[0]}
        row.update({"row_type": "state", "scope_id": s["id"], "county": "(statewide)", "county_fips": "56"})
        for k, v in s.items():
            if k in row and k not in ("row_type", "scope_id"):
                row[k] = v
        row["tested_feeds"] = " | ".join(i for i in s.get("evidence", []) if i in MAN and "error" not in MAN[i])
        row["november_2026_counts_verified"] = "no"
        state_rows.append(row)
    with (DATA / "official-results-sources.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(csv_rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(state_rows + csv_rows)
    (HERE / "county-records.json").write_text(json.dumps({"clerk_directory": directory, "senate_county_pdf_crosscheck": cross,
                                                          "counties": records}, indent=1) + "\n")
    groups: dict[str, list[str]] = {}
    for k, e in MAN.items():
        if "error" not in e and e.get("http_status") == 200:
            groups.setdefault(SRC[k]["url"], []).append(k)
    same_url = []
    for url, ids in groups.items():
        if len(ids) > 1:
            hashes = {k: MAN[k].get("decoded_sha256") or MAN[k]["original_sha256"] for k in ids}
            same_url.append({"url": url, "ids": ids, "distinct_payloads": len(set(hashes.values())),
                             "identical": len(set(hashes.values())) == 1})
    summary = {
        "sources": len(SOURCES), "manifest_entries": len(MAN),
        "manifest_errors": sorted(k for k, e in MAN.items() if "error" in e),
        "stored_files": sum(1 for k in MAN if stored(k)),
        "status_counts": {str(st): sum(1 for e in MAN.values() if e.get("http_status") == st) for st in sorted({e.get("http_status") for e in MAN.values()}, key=str)},
        "county_rows": len(csv_rows), "state_rows": len(state_rows),
        "deep_counties": sum(1 for r in records.values() if r["investigation_scope"] == "deep"),
        "deep_counties_with_tested_sample": sum(1 for r in records.values() if r["investigation_scope"] == "deep" and r["samples_tested"]),
        "senate_crosscheck": {s: sum(1 for c in cross if c["status"] == s) for s in ("match", "differs", "not_found_in_text", "not_parsed_no_text_layer")},
        "clerk_directory_links": directory["link_count"],
        "election_night_versions": len(en["versions"]),
        "same_url_comparisons": same_url,
    }
    (HERE / "build-summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
