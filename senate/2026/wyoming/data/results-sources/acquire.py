"""Fetch the Wyoming official-results evidence listed in sources.json.

Usage (from the repository root):
    uv run python3 -I senate/2026/wyoming/data/results-sources/acquire.py [--only ID[,ID...]]

For every source this records the observed link (``url``), the request URL
(spaces percent-encoded, nothing else changed), the redirect chain, HTTP
status, selected response headers, UTC start/finish times, and the size and
SHA-256 of the exact response body. ``mode: store`` keeps gzip(mtime=0) of the
exact body under raw/ (lossless; HTML CRLFs would otherwise trip Git
whitespace checks). ``mode: hash_only`` keeps metadata only; it is used where
a block page echoes the requesting IP address or where the document is not
needed byte-for-byte.

``via: wayback`` requests the Wayback Machine raw capture
``https://web.archive.org/web/<wayback_ts>id_/<url>``. Those responses carry
Memento-Datetime and X-Archive-Orig-* headers; the original server's
Last-Modified is kept from X-Archive-Orig-Last-Modified. Wayback may return
the original gzip transfer encoding; such bodies are stored as received and a
decoded SHA-256 is added.

A non-allowed HTTP status, a network error, or an Internet Archive
"Temporarily Offline" page is retried three times and then recorded as an
error entry; it is never converted into an empty or zero result. Entries not
fetched in this run are kept unchanged in acquisition-manifest.json.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources.json"
RAW = HERE / "raw"
MANIFEST = HERE / "acquisition-manifest.json"
USER_AGENT = "Mozilla/5.0 (compatible; snn-election-research/1.0; Wyoming official-results inventory)"
KEEP_HEADERS = (
    "content-type", "content-length", "content-encoding", "content-disposition", "last-modified",
    "etag", "date", "server", "cache-control", "location", "x-reference-error", "cf-ray",
    "memento-datetime", "x-archive-orig-last-modified", "x-archive-orig-content-type",
    "x-archive-orig-date", "x-archive-src", "x-archive-orig-content-length",
)
SAFE = ":/?&=%#+,;@!$'()*~"


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


def request_url(src: dict) -> str:
    url = urllib.parse.quote(src["url"], safe=SAFE)
    if src.get("via") == "wayback":
        return f"https://web.archive.org/web/{src['wayback_ts']}id_/{url}"
    return url


def ext_for(content_type: str | None, body: bytes) -> str:
    ct = (content_type or "").lower()
    if body[:5] == b"%PDF-" or "pdf" in ct:
        return "pdf"
    if "html" in ct:
        return "html"
    if "json" in ct:
        return "json"
    return "bin"


def decoded(body: bytes) -> bytes:
    if body[:2] == b"\x1f\x8b":
        try:
            return gzip.decompress(body)
        except OSError:
            return body
    return body


def fetch(url: str) -> dict:
    redirects = RecordingRedirects()
    opener = urllib.request.build_opener(redirects)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    started = dt.datetime.now(dt.timezone.utc)
    try:
        with opener.open(req, timeout=120) as resp:
            body, status, final_url, headers = resp.read(), resp.status, resp.geturl(), resp.headers
    except urllib.error.HTTPError as err:
        body, status, final_url, headers = err.read(), err.code, err.geturl(), err.headers
    finished = dt.datetime.now(dt.timezone.utc)
    return {
        "final_url": final_url,
        "redirects": redirects.chain,
        "http_status": status,
        "headers": {k: headers.get(k) for k in KEEP_HEADERS if headers.get(k) is not None},
        "retrieved_utc": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "completed_utc": finished.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "body": body,
    }


def html_title(body: bytes) -> str | None:
    m = re.search(rb"<title[^>]*>(.*?)</title>", decoded(body), re.S | re.I)
    if not m:
        return None
    return " ".join(m.group(1).decode("utf-8", "replace").split())[:200]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", help="comma-separated source ids to fetch")
    args = parser.parse_args()

    sources = json.loads(SOURCES.read_text())["sources"]
    wanted = set(args.only.split(",")) if args.only else None
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"entries": {}}
    entries = manifest.setdefault("entries", {})
    RAW.mkdir(parents=True, exist_ok=True)
    last_host_time: dict[str, float] = {}

    for src in sources:
        if wanted and src["id"] not in wanted:
            continue
        url = request_url(src)
        host = urllib.parse.urlsplit(url).netloc
        wait = (2.0 if "archive.org" in host else 1.0) - (time.time() - last_host_time.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        allow = set(src.get("allow_status", [])) | {200}
        got, last_err = None, None
        for attempt in range(4):
            try:
                got = fetch(url)
                if got["http_status"] not in allow:
                    raise RuntimeError(f"HTTP {got['http_status']}")
                if "archive.org" in host and b"Temporarily Offline" in decoded(got["body"])[:4000]:
                    raise RuntimeError("Internet Archive temporarily offline page")
                break
            except Exception as err:  # retried; recorded if persistent
                last_err, got = err, None
                time.sleep(5 * (attempt + 1))
        last_host_time[host] = time.time()
        if got is None:
            entries[src["id"]] = {
                "id": src["id"], "url": src["url"], "request_url": url, "error": repr(last_err),
                "attempted_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            print(f"FAILED {src['id']}: {last_err!r}")
            continue

        body = got.pop("body")
        entry = {
            "id": src["id"], "scope": src["scope"], "kind": src["kind"], "via": src.get("via", "direct"),
            "wayback_ts": src.get("wayback_ts"), "mode": src["mode"], "url": src["url"], "request_url": url,
            **got, "original_bytes": len(body), "original_sha256": sha256(body),
        }
        dec = decoded(body)
        if dec is not body:
            entry["decoded_bytes"] = len(dec)
            entry["decoded_sha256"] = sha256(dec)
        ext = ext_for(got["headers"].get("content-type") or got["headers"].get("x-archive-orig-content-type"), dec)
        if ext == "html":
            entry["html_title"] = html_title(body)
        if src["mode"] == "store":
            stored = gzip_bytes(body)
            rel = f"raw/{src['id']}.{ext}.gz"
            (HERE / rel).write_bytes(stored)
            entry.update({"stored_path": rel, "stored_encoding": "gzip(mtime=0) of the exact response body",
                          "stored_bytes": len(stored), "stored_sha256": sha256(stored)})
        else:
            entry["stored_path"] = None
        entries[src["id"]] = entry
        print(f"{entry['http_status']} {len(body):>9} {src['id']}")

    order = [s["id"] for s in sources]
    manifest["generated_by"] = "acquire.py"
    manifest["user_agent"] = USER_AGENT
    manifest["updated_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest["entries"] = {k: entries[k] for k in order if k in entries}
    MANIFEST.write_text(json.dumps(manifest, indent=1) + "\n")


if __name__ == "__main__":
    main()
