"""Fetch Wyoming turnout evidence listed in sources.json.

Usage (from any directory):
    uv run python3 -I senate/2026/wyoming/data/turnout/acquire.py [--only ID[,ID...]]

Each response is saved byte-for-byte under originals/ (HTML pages are gzip
compressed with a fixed header so the stored bytes are deterministic), and
source-manifest.json records request/final URL, redirect chain, HTTP status,
selected response headers, UTC retrieval time, and SHA-256/size of both the
original response and the stored file. Sources marked hash_only are fetched
and hashed but not retained. Existing manifest entries for sources that are
not fetched in this run are kept unchanged.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources.json"
ORIGINALS = HERE / "originals"
MANIFEST = HERE / "source-manifest.json"
USER_AGENT = (
    "Mozilla/5.0 (compatible; snn-election-research/1.0; "
    "Wyoming turnout evidence capture)"
)
KEEP_HEADERS = (
    "content-type",
    "content-length",
    "last-modified",
    "etag",
    "date",
    "cache-control",
    "server",
    "x-powered-by",
)


class RecordingRedirects(urllib.request.HTTPRedirectHandler):
    def __init__(self) -> None:
        super().__init__()
        self.chain: list[dict] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append({"status": code, "from": req.full_url, "to": newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def gzip_bytes(data: bytes) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, mtime=0, compresslevel=9) as gz:
        gz.write(data)
    return buf.getvalue()


def fetch(url: str, allow_status: set[int]) -> dict:
    redirects = RecordingRedirects()
    opener = urllib.request.build_opener(redirects)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    started = dt.datetime.now(dt.timezone.utc)
    try:
        with opener.open(req, timeout=120) as resp:
            body = resp.read()
            status = resp.status
            final_url = resp.geturl()
            headers = resp.headers
    except urllib.error.HTTPError as err:
        if err.code not in allow_status:
            raise
        body = err.read()
        status = err.code
        final_url = err.geturl()
        headers = err.headers
    finished = dt.datetime.now(dt.timezone.utc)
    return {
        "request_url": url,
        "final_url": final_url,
        "redirects": redirects.chain,
        "http_status": status,
        "headers": {k: headers.get(k) for k in KEEP_HEADERS if headers.get(k) is not None},
        "retrieved_utc": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "completed_utc": finished.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "body": body,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="comma-separated source ids to fetch")
    args = parser.parse_args()

    sources = json.loads(SOURCES.read_text())["sources"]
    wanted = set(args.only.split(",")) if args.only else None
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"entries": {}}
    entries = manifest.setdefault("entries", {})
    ORIGINALS.mkdir(parents=True, exist_ok=True)

    for src in sources:
        if wanted and src["id"] not in wanted:
            continue
        allow = set(src.get("allow_status", [])) | {200}
        last_err = None
        for attempt in range(3):
            try:
                got = fetch(src["url"], allow)
                break
            except Exception as err:  # retry transient network failures
                last_err = err
                time.sleep(3 * (attempt + 1))
        else:
            entries[src["id"]] = {
                "id": src["id"],
                "url": src["url"],
                "error": repr(last_err),
                "attempted_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            print(f"FAILED {src['id']}: {last_err!r}")
            continue

        body = got.pop("body")
        entry = {
            "id": src["id"],
            "role": src["role"],
            "parent": src.get("parent"),
            "mode": src["mode"],
            **got,
            "original_bytes": len(body),
            "original_sha256": sha256(body),
        }
        if src["mode"] == "store":
            stored = gzip_bytes(body) if src["file"].endswith(".gz") else body
            path = ORIGINALS / src["file"]
            path.write_bytes(stored)
            entry.update(
                {
                    "stored_path": f"originals/{src['file']}",
                    "stored_encoding": "gzip(mtime=0)" if src["file"].endswith(".gz") else "identity",
                    "stored_bytes": len(stored),
                    "stored_sha256": sha256(stored),
                }
            )
        else:
            entry["stored_path"] = None
        entries[src["id"]] = entry
        print(f"{entry['http_status']} {len(body):>9} {src['id']}")

    manifest["generated_by"] = "acquire.py"
    manifest["updated_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    order = [s["id"] for s in sources]
    manifest["entries"] = {k: entries[k] for k in order if k in entries}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
