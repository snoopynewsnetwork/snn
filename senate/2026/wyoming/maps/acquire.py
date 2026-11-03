#!/usr/bin/env python3
"""Download every Wyoming precinct-map source listed in sources.json.

Run from the repository root:

    uv run python3 -I senate/2026/wyoming/maps/acquire.py

Each request is made with the system ``curl`` binary (some county sites refuse
other clients). Response bodies are the decoded HTTP entity. They are stored
under ``raw/<source id>/`` either unchanged (PDF, ZIP, PNG) or as deterministic
gzip (``mtime=0``), which is lossless. ``raw/<source id>/retrieval.json``
records the request and final URLs, every HTTP status in the redirect chain,
selected response headers, UTC retrieval time, entity SHA-256/bytes and stored
SHA-256/bytes. ArcGIS layers are paged explicitly: layer and service metadata,
``returnCountOnly``, ``returnIdsOnly`` and then object-ID batches no larger
than ``BATCH`` (always below the layer's maxRecordCount), in the layer's native
spatial reference (no ``outSR``). A refresh overwrites the working snapshot;
copy ``raw/`` first to keep an older one.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import time
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / "raw"
BATCH = 100
PAUSE = 0.4
KEEP_HEADERS = (
    "content-type", "content-length", "content-encoding", "last-modified", "etag",
    "date", "content-disposition", "server", "cache-control", "location",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_header_blocks(text: str) -> list[dict]:
    blocks, cur = [], None
    for line in text.splitlines():
        line = line.rstrip("\r")
        if line.startswith("HTTP/"):
            cur = {"status_line": line, "headers": {}}
            blocks.append(cur)
        elif cur is not None and ":" in line:
            k, v = line.split(":", 1)
            cur["headers"].setdefault(k.strip().lower(), v.strip())
    return blocks


def fetch(url: str) -> tuple[bytes, dict]:
    with tempfile.TemporaryDirectory() as td:
        body, hdr = pathlib.Path(td, "body"), pathlib.Path(td, "headers")
        started = dt.datetime.now(dt.UTC)
        proc = subprocess.run(
            ["curl", "-sS", "-L", "--max-redirs", "6", "--compressed", "-m", "300",
             "-D", str(hdr), "-o", str(body), "-w", "%{json}", url],
            capture_output=True, text=True,
        )
        info = {}
        try:
            info = json.loads(proc.stdout) if proc.stdout.strip() else {}
        except json.JSONDecodeError:
            info = {}
        data = body.read_bytes() if body.exists() else b""
        blocks = parse_header_blocks(hdr.read_text(errors="replace")) if hdr.exists() else []
    final = blocks[-1]["headers"] if blocks else {}
    rec = {
        "request_url": url,
        "final_url": info.get("url_effective", url),
        "http_status": info.get("http_code") or info.get("response_code"),
        "status_chain": [b["status_line"] for b in blocks],
        "retrieved_utc": started.isoformat(timespec="seconds"),
        "curl_exit": proc.returncode,
        "curl_error": proc.stderr.strip() or None,
        "headers": {k: final[k] for k in KEEP_HEADERS if k in final},
        "entity_sha256": sha256(data),
        "entity_bytes": len(data),
    }
    return data, rec


def store(src_dir: pathlib.Path, name: str, mode: str, data: bytes, rec: dict) -> dict:
    src_dir.mkdir(parents=True, exist_ok=True)
    if mode == "gzip":
        path = src_dir / (name + ".gz")
        blob = gzip.compress(data, compresslevel=9, mtime=0)
    else:
        path = src_dir / name
        blob = data
    path.write_bytes(blob)
    rec.update({
        "name": name,
        "store": mode,
        "stored_path": path.relative_to(HERE).as_posix(),
        "stored_sha256": sha256(blob),
        "stored_bytes": len(blob),
    })
    return rec


def get_json(data: bytes):
    try:
        return json.loads(data.decode("utf-8"))
    except Exception:
        return None


def run_request(src_dir, name, url, mode, expect, log):
    data, rec = fetch(url)
    rec["expected_status"] = expect
    rec["matches_expectation"] = rec["http_status"] == expect
    store(src_dir, name, mode, data, rec)
    log.append(rec)
    flag = "ok" if rec["matches_expectation"] else "UNEXPECTED"
    print(f"  {rec['http_status']} {flag} {rec['entity_bytes']:>9} {name}", flush=True)
    time.sleep(PAUSE)
    return data, rec


def arcgis_layer(src, src_dir, log):
    layer = src["layer_url"].rstrip("/")
    service = layer.rsplit("/", 1)[0]
    meta_raw, _ = run_request(src_dir, "layer.json", layer + "?f=json", "gzip", 200, log)
    meta = get_json(meta_raw) or {}
    run_request(src_dir, "service.json", service + "?f=json", "gzip", 200, log)
    q = layer + "/query?"
    cnt_raw, _ = run_request(src_dir, "count.json", q + urllib.parse.urlencode(
        {"where": "1=1", "returnCountOnly": "true", "f": "json"}), "gzip", 200, log)
    ids_raw, _ = run_request(src_dir, "objectids.json", q + urllib.parse.urlencode(
        {"where": "1=1", "returnIdsOnly": "true", "f": "json"}), "gzip", 200, log)
    ids = sorted((get_json(ids_raw) or {}).get("objectIds") or [])
    max_rec = meta.get("maxRecordCount") or 1000
    size = min(BATCH, max_rec)
    for i in range(0, len(ids), size):
        chunk = ids[i:i + size]
        url = q + urllib.parse.urlencode({
            "objectIds": ",".join(map(str, chunk)), "outFields": "*",
            "returnGeometry": "true", "returnZ": "false", "returnM": "false", "f": "json",
        })
        run_request(src_dir, f"features-{i // size + 1:04d}.json", url, "gzip", 200, log)
    return {"count": (get_json(cnt_raw) or {}).get("count"), "object_ids": len(ids), "batch_size": size,
            "max_record_count": max_rec}


RENDER_PX = 512
GML = "{http://www.opengis.net/gml/3.2}"
WFSNS = "{http://www.opengis.net/wfs/2.0}"


def wfs_layer(src, src_dir, log):
    """MapServer WFS/WMS layer: capabilities, schema, hits, all features, SLD, legend, per-feature renders.

    The WFS exposes geometry only, so build.py identifies each feature by
    sampling the county server's own WMS rendering inside that feature and
    matching the colour to the GetStyles SLD class fills. One small GetMap
    (longer side RENDER_PX) is requested per feature envelope (padded 3%).
    """
    import xml.etree.ElementTree as ET
    w = src["wfs"]

    def u(**kw):
        return w["endpoint"] + "?" + urllib.parse.urlencode({"map": w["map"], **kw})

    run_request(src_dir, "wfs-capabilities.xml", u(SERVICE="WFS", REQUEST="GetCapabilities"), "gzip", 200, log)
    run_request(src_dir, "wfs-describe.xml", u(SERVICE="WFS", VERSION="2.0.0", REQUEST="DescribeFeatureType",
                                               TYPENAMES=w["typename"]), "gzip", 200, log)
    run_request(src_dir, "wfs-hits.xml", u(SERVICE="WFS", VERSION="2.0.0", REQUEST="GetFeature",
                                           TYPENAMES=w["typename"], RESULTTYPE="hits"), "gzip", 200, log)
    gml, _ = run_request(src_dir, "features.gml", u(SERVICE="WFS", VERSION="2.0.0", REQUEST="GetFeature",
                                                    TYPENAMES=w["typename"]), "gzip", 200, log)
    run_request(src_dir, "wms-getstyles.sld.xml", u(SERVICE="WMS", VERSION="1.1.1", REQUEST="GetStyles",
                                                    LAYERS=w["wms_layer"]), "gzip", 200, log)
    run_request(src_dir, "wms-legend.png", u(version="1.3.0", service="WMS", request="GetLegendGraphic",
                                             sld_version="1.1.0", layer=w["legend_layer"], format="image/png",
                                             STYLE="default"), "raw", 200, log)
    if b"<!DOCTYPE" in gml or b"<!ENTITY" in gml:  # untrusted XML: refuse DTDs/entities outright
        raise SystemExit("refusing GML with a DTD or entity declaration")
    root = ET.fromstring(gml)
    renders = []
    for i, member in enumerate(root.iter(WFSNS + "member")):
        env = next(member.iter(GML + "Envelope"))
        lo = [float(v) for v in env.find(GML + "lowerCorner").text.split()]
        hi = [float(v) for v in env.find(GML + "upperCorner").text.split()]
        dx, dy = hi[0] - lo[0], hi[1] - lo[1]
        pad = 0.03 * max(dx, dy)
        bbox = [lo[0] - pad, lo[1] - pad, hi[0] + pad, hi[1] + pad]
        bx, by = bbox[2] - bbox[0], bbox[3] - bbox[1]
        width = max(16, round(RENDER_PX * bx / max(bx, by)))
        height = max(16, round(RENDER_PX * by / max(bx, by)))
        name = f"render-{i + 1:04d}.png"
        run_request(src_dir, name, u(SERVICE="WMS", VERSION="1.1.1", REQUEST="GetMap", LAYERS=w["wms_layer"],
                                     STYLES="", SRS=w["srs"], BBOX=",".join(f"{v:.6f}" for v in bbox),
                                     WIDTH=width, HEIGHT=height, FORMAT="image/png", TRANSPARENT="FALSE"),
                    "raw", 200, log)
        renders.append({"feature_index": i, "file": name, "bbox": bbox, "width": width, "height": height,
                        "srs": w["srs"]})
    return {"members": len(renders), "renders": renders}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", nargs="*", help="source ids to fetch (default: all)")
    args = ap.parse_args()
    reg = json.loads((HERE / "sources.json").read_text())
    summary = []
    for src in reg["sources"]:
        if args.only and src["id"] not in args.only:
            continue
        print(src["id"], flush=True)
        src_dir = RAW / src["id"]
        log: list[dict] = []
        extra = None
        for r in src.get("requests", []):
            run_request(src_dir, r["name"], r["url"], r.get("store", "gzip"), r.get("expect", 200), log)
        if src.get("kind") == "arcgis-layer":
            extra = arcgis_layer(src, src_dir, log)
        elif src.get("kind") == "wfs-gml":
            extra = wfs_layer(src, src_dir, log)
        (src_dir / "retrieval.json").write_text(json.dumps(
            {"source_id": src["id"], "acquire_script": "acquire.py", "requests": log, "paging": extra},
            indent=1, sort_keys=True) + "\n")
        summary.append({"source_id": src["id"], "requests": len(log),
                        "unexpected": [x["name"] for x in log if not x["matches_expectation"]], "paging": extra})
    # Merge with the previous summary so a partial (--only) refresh keeps the other sources' entries.
    summary_path = RAW / "acquisition-summary.json"
    previous = json.loads(summary_path.read_text())["sources"] if summary_path.exists() else []
    fetched = {s["source_id"] for s in summary}
    ordered = [s["id"] for s in reg["sources"]]
    merged = {s["source_id"]: s for s in previous if s["source_id"] in ordered and s["source_id"] not in fetched}
    merged.update({s["source_id"]: s for s in summary})
    summary_path.write_text(json.dumps(
        {"finished_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
         "last_run_sources": sorted(fetched),
         "sources": [merged[i] for i in ordered if i in merged]}, indent=1) + "\n")
    bad = [s for s in summary if s["unexpected"]]
    print(f"{len(summary)} sources; {sum(s['requests'] for s in summary)} requests; unexpected: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
