#!/usr/bin/env python3
"""Acquire Oklahoma partisanship baseline evidence.

Run from anywhere with ``uv run python3 -I acquire.py`` (network required).
Every source is written into its own directory under ``raw/<source_id>/``.
Text-like payloads are stored gzip-compressed (lossless, mtime=0); binary
payloads that are already compressed (ZIP, PDF) are stored unchanged.
``sources.json`` records URL, final URL, retrieval UTC, HTTP status and
selected response headers, entity byte count, entity SHA-256, stored path,
stored byte count and stored SHA-256.

No source in this script requires credentials.  The State Election Board's
OK Election Results application (results.okelections.gov/OKER) loads data
only after an application login; this package does not call that API.  The
two State Election Board statewide JSON documents used here are Internet
Archive captures of responses the application served to the public.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import http.cookiejar
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
)
KEEP_HEADERS = (
    "content-type", "content-length", "last-modified", "etag", "date",
    "content-disposition", "x-archive-src", "memento-datetime", "link",
    "x-archive-orig-last-modified", "x-archive-orig-date", "server",
)

MEDSL22 = "a8126c5790b8d1f438a3e63c3506cdcdc7406d9f"
MEDSL24 = "df531089c78e6d0098db1a6bfb3849a066a06995"
OE_OK = "76320f6588780002f8c0beb4acd641cf019b0489"
SEB = "https://oklahoma.gov"
ER = SEB + "/elections/elections-results/election-results"

# (source_id, url, filename, compress, role)
SOURCES = [
    # --- State Election Board landing pages (official channel inventory)
    ("seb-results-index", ER + ".html", "election-results.html", True,
     "SEB election-results index; links each year page"),
    ("seb-2020-general-page", ER + "/2020-election-results/2020-november-general-election.html",
     "2020-november-general-election.html", True,
     "SEB 2020 general page; only results link is the OKER app"),
    ("seb-2022-general-page", ER + "/2022-election-results/2022-november-general-election.html",
     "2022-november-general-election.html", True,
     "SEB 2022 general page; says downloads are via the OKER export tab"),
    ("seb-2024-general-page", ER + "/2024-election-results/november-general-election.html",
     "november-general-election.html", True,
     "SEB 2024 general page; only results link is the OKER app"),
    ("seb-oker-app-shell", "https://results.okelections.us/OKER/?elecDate=20221108",
     "oker-index.html", True,
     "OKER single-page application shell (JS app; no results in HTML)"),
    # --- Archived SEB statewide results served by the OKER application
    ("wayback-seb-oker-cdx", "https://web.archive.org/cdx/search/cdx?url=results.okelections.gov/OKERS/enrapi/*&output=json&fl=timestamp,original,statuscode,mimetype,length,digest",
     "cdx.json", True, "Internet Archive capture inventory for the OKER API"),
    ("wayback-seb-oker-2020", "https://web.archive.org/web/20250629165738id_/https://results.okelections.gov/OKERS/enrapi/getelec/20201103/SW/xx",
     "getelec-20201103-SW.json", True,
     "SEB OKER statewide 2020 results, 'Official Results', archived capture"),
    ("wayback-seb-oker-2024", "https://web.archive.org/web/20241106133100id_/https://results.okelections.gov/OKERS/enrapi/getelec/20241105/SW/xx",
     "getelec-20241105-SW.json", True,
     "SEB OKER statewide 2024 results, 'Unofficial Results', election-night capture"),
    # --- Official federal compilation of state-certified statewide totals
    ("clerk-2020", "https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf",
     "statistics2020.pdf", False, "House Clerk statistics of the 2020 election"),
    ("clerk-2022", "https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf",
     "statistics2022.pdf", False, "House Clerk statistics of the 2022 election"),
    ("clerk-2024", "https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf",
     "statistics2024.pdf", False, "House Clerk statistics of the 2024 election"),
    # --- County-level secondary transcriptions of SEB OKER exports (pinned)
    ("medsl-2022-ok", f"https://raw.githubusercontent.com/MEDSL/2022-elections-official/{MEDSL22}/individual_states/2022-ok-local-precinct-general.zip",
     "2022-ok-local-precinct-general.zip", False,
     "MEDSL 2022 Oklahoma precinct returns (source: SEB OKER)"),
    ("medsl-2022-readme", f"https://raw.githubusercontent.com/MEDSL/2022-elections-official/{MEDSL22}/README.md",
     "README.md", True, "MEDSL 2022 README (Oklahoma source/added date)"),
    ("medsl-2024-ok", f"https://raw.githubusercontent.com/MEDSL/2024-elections-official/{MEDSL24}/individual_states/ok24.zip",
     "ok24.zip", False, "MEDSL 2024 Oklahoma precinct returns (source: SEB OKER)"),
    ("medsl-2024-readme", f"https://raw.githubusercontent.com/MEDSL/2024-elections-official/{MEDSL24}/README.md",
     "README.md", True, "MEDSL 2024 README (Oklahoma source/added date)"),
    ("openelections-2020-county", f"https://raw.githubusercontent.com/openelections/openelections-data-ok/{OE_OK}/2020/20201103__ok__general__county.csv",
     "20201103__ok__general__county.csv", True,
     "OpenElections 2020 Oklahoma county returns (SEB export transcription)"),
    ("openelections-2020-precinct", f"https://raw.githubusercontent.com/openelections/openelections-data-ok/{OE_OK}/2020/20201103__ok__general__precinct.csv",
     "20201103__ok__general__precinct.csv", True,
     "OpenElections 2020 Oklahoma precinct returns (internal county cross-check)"),
    # --- County key
    ("census-ok-counties-2020", "https://www2.census.gov/geo/docs/reference/codes2020/cou/st40_ok_cou2020.txt",
     "st40_ok_cou2020.txt", False, "Census 2020 Oklahoma county FIPS reference"),
    # --- 2026 contest and slate verification
    ("seb-2026-filing-info", SEB + "/elections/candidates/2026-candidate-filing-information.html",
     "2026-candidate-filing-information.html", True, "SEB 2026 filing information page"),
    ("seb-2026-candidate-list-book", SEB + "/content/dam/ok/en/elections/candidate-filing-archives/2026-candidate-filing-archives/2026-candidate-list-book.pdf",
     "2026-candidate-list-book.pdf", False, "SEB 2026 candidate list book (filings April 1-3, 2026)"),
    ("seb-2026-withdrawals", SEB + "/elections/candidates/2026-candidate-filing-information/2026-candidate-withdrawals.html",
     "2026-candidate-withdrawals.html", True, "SEB 2026 candidate withdrawals"),
    ("seb-2026-contests", SEB + "/elections/candidates/2026-candidate-filing-information/2026-contests-of-candidacy.html",
     "2026-contests-of-candidacy.html", True, "SEB 2026 contests of candidacy"),
    ("seb-2026-general-notice", SEB + "/elections/voters/military-overseas-voters/2026-election-notice-general-election.html",
     "2026-election-notice-general-election.html", True,
     "SEB UOCAVA notice for the November 3, 2026 general election"),
    ("seb-filings-portal", "https://filings.okelections.gov/ViewCandidates/2026040120260403/99/all",
     "ViewCandidates-2026040120260403-99-all.html", True,
     "SEB candidate filing portal page (public)"),
    ("seb-filings-offices", "https://filings.okelections.gov/api/Home/GetOfficeList",
     "GetOfficeList.json", True, "SEB filing portal office list (public JSON)"),
    ("seb-filings-us-senator", "https://filings.okelections.gov/api/Home/GetCandList?OfficeID=2257",
     "GetCandList-OfficeID-2257.json", True,
     "SEB filing portal U.S. Senator filings (public JSON)"),
    ("senate-gov-class-ii", "https://www.senate.gov/senators/Class_II.htm",
     "Class_II.htm", True, "U.S. Senate Class II roster (current seat holder)"),
    ("news-okcfox-thomas-runoff", "https://okcfox.com/news/local/nkiyla-thomas-wins-democratic-nomination-for-us-senate-in-oklahoma",
     "okcfox-thomas-wins.html", True,
     "Newsroom report of the August 25, 2026 Democratic runoff call (secondary)"),
    ("news-news9-senate-candidates", "https://www.news9.com/oklahoma-politics/oklahoma-us-senate-election-candidates-2026",
     "news9-senate-candidates-2026.html", True,
     "Newsroom list of November 2026 Senate candidates (secondary)"),
]


# Sources fetched for their metadata/hash only; body deliberately not retained.
NO_STORE = {
    "seb-filings-portal": ("page HTML embeds a third-party UI-library license key; body not retained. "
                           "The candidate data come from the public JSON endpoints stored alongside."),
}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch(opener, url: str, tries: int = 4):
    last = None
    for i in range(tries):
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/json,application/pdf,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        try:
            with opener.open(req, timeout=120) as r:
                return r.status, r.geturl(), dict(r.headers.items()), r.read()
        except urllib.error.HTTPError as e:
            body = e.read() if hasattr(e, "read") else b""
            last = (e.code, url, dict(e.headers.items()) if e.headers else {}, body)
            if e.code in (403, 404, 410):
                return last
        except Exception as e:  # network error; retry with backoff
            last = (None, url, {"error": repr(e)}, b"")
        time.sleep(2 * (i + 1))
    return last


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="source ids to refresh")
    args = ap.parse_args()
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    manifest_path = HERE / "sources.json"
    existing = {}
    if manifest_path.exists():
        existing = {s["source_id"]: s for s in json.loads(manifest_path.read_text())["sources"]}
    out = []
    for sid, url, fname, compress, role in SOURCES:
        if args.only and sid not in args.only:
            if sid in existing:
                out.append(existing[sid])
            continue
        d = RAW / sid
        d.mkdir(parents=True, exist_ok=True)
        t0 = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        status, final, headers, body = fetch(opener, url)
        hdr = {k.lower(): v for k, v in headers.items() if k.lower() in KEEP_HEADERS or k == "error"}
        rec = {
            "source_id": sid, "role": role, "url": url, "final_url": final,
            "retrieved_utc": t0, "http_status": status, "headers": hdr,
            "entity_bytes": len(body), "entity_sha256": sha256(body),
        }
        if status == 200 and body and sid in NO_STORE:
            for old in d.glob("*"):
                old.unlink()
            rec.update({"stored_path": None, "not_stored_reason": NO_STORE[sid]})
        elif status == 200 and body:
            stored = gzip.compress(body, mtime=0) if compress else body
            p = d / (fname + (".gz" if compress else ""))
            p.write_bytes(stored)
            rec.update({
                "stored_path": str(p.relative_to(HERE)),
                "stored_encoding": "gzip" if compress else "identity",
                "stored_bytes": len(stored), "stored_sha256": sha256(stored),
            })
        else:
            rec.update({"stored_path": None, "error_excerpt": body[:300].decode("utf-8", "replace")})
        print(sid, status, len(body), file=sys.stderr)
        out.append(rec)
    manifest = {
        "schema": 1,
        "generated_by": "acquire.py",
        "pins": {"medsl_2022_commit": MEDSL22, "medsl_2024_commit": MEDSL24,
                 "openelections_ok_commit": OE_OK},
        "not_used": [{
            "channel": "SEB OK Election Results (OKER) API, results.okelections.gov/OKERS/enrapi/",
            "reason": ("County/precinct exports (CLCSV/PLCSV/CSV/XML) are served only after an "
                       "application login performed by the OKER JavaScript client. This package "
                       "does not perform that login. County values therefore come from pinned "
                       "secondary transcriptions of those exports, reconciled to official statewide totals."),
        }, {
            "channel": "MEDSL 2020 precinct returns, Harvard Dataverse doi:10.7910/DVN/NT66Z3 file 6100437",
            "reason": "Download requires a Dataverse guestbook response; not submitted.",
        }, {
            "channel": "VEST 2022 Oklahoma precinct results, UF Election Lab",
            "reason": "Download requires site login or subscription.",
        }],
        "sources": out,
    }
    manifest_path.write_text(json.dumps(manifest, indent=1) + "\n")
    bad = [s["source_id"] for s in out if s.get("http_status") != 200]
    if bad:
        print("non-200 sources:", bad, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
