"""Offline original-response and literal embed audit; --seal writes this pack only."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import re
import urllib.parse
from html.parser import HTMLParser

R = Path(__file__).resolve().parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def encoded_json(x):
    return (json.dumps(x, ensure_ascii=False, indent=2) + "\n").encode()


class Nodes(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.active = []
        self.feed(raw.decode("utf-8"))

    def handle_starttag(self, tag, attrs):
        if tag in ("a", "script", "iframe", "meta"):
            row = {"tag": tag, "attrs": attrs, "text": "", "position": self.getpos()}
            self.nodes.append(row)
            if tag in ("a", "script"):
                self.active.append(row)

    def handle_data(self, text):
        for row in self.active:
            row["text"] += text

    def handle_endtag(self, tag):
        for i in range(len(self.active) - 1, -1, -1):
            if self.active[i]["tag"] == tag:
                self.active.pop(i)
                break


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seal", action="store_true")
    args = ap.parse_args()
    receipts = {p.name.removesuffix(".receipt.json"): json.loads(p.read_bytes()) for p in R.glob("*.receipt.json")}
    assert len(receipts) == 11
    bodies, hop_count, body_paths = {}, 0, set()
    for key, receipt in receipts.items():
        assert receipt["id"] == key and receipt["status"] == 200
        for hop in receipt["hops"]:
            assert hop["method"] == "GET" and hop["started_utc"]
            b = hop["body"]
            stored = (R / b["path"]).read_bytes()
            wire = gzip.decompress(stored)
            assert len(stored) == b["stored_bytes"] and sha(stored) == b["stored_sha256"]
            assert len(wire) == b["raw_bytes"] and sha(wire) == b["raw_sha256"]
            body_paths.add(b["path"])
            hop_count += 1
        b = receipt["body"]
        wire = gzip.decompress((R / b["path"]).read_bytes())
        headers = {k.lower(): v for k, v in receipt["hops"][-1]["response_headers"]}
        bodies[key] = gzip.decompress(wire) if headers.get("content-encoding", "").lower() == "gzip" else wire
    inventory = json.loads((R / "acquisition-complete-v1.json").read_bytes())
    assert inventory["receipts"] == [receipts[k] for k in sorted(receipts)]
    assert inventory["actual_requests"] == 11
    # Follow the publisher's actual iframe/script and its public org-config constructor.
    interactive = Nodes(bodies["kswo-oklahoma-interactive"]).nodes
    layouts = []
    for key in ("kswo-linked-ap-1", "kswo-linked-ap-2"):
        url = receipts[key]["requested_url"]
        assert any(n["tag"] == "iframe" and dict(n["attrs"]).get("src") == url for n in interactive)
        nodes = Nodes(bodies[key]).nodes
        config = next(n for n in nodes if n["tag"] == "script" and dict(n["attrs"]).get("id") == "layout-config")
        outer = json.loads(config["text"])
        grid = json.loads(outer["grid"])
        saved = json.loads((R / (key + ".full-layout-config.json")).read_bytes())
        assert saved["complete_outer_JSON"] == outer and saved["complete_grid_JSON"] == grid
        assert any(n["tag"] == "script" and urllib.parse.urljoin(url, dict(n["attrs"]).get("src", "")) == receipts["ap-literal-layout-client"]["requested_url"] for n in nodes)
        layouts.append({"source_receipt": key + ".receipt.json", "outer": outer, "grid": grid})
    assert len(layouts[0]["grid"]["slots"]) == 1 and len(layouts[1]["grid"]["slots"]) == 5
    senate = next(x for x in layouts[1]["grid"]["slots"] if x.get("label") == "Map of General for U.S. Senate, Class II in Oklahoma")
    assert senate["date"] == "2026-11-03" and senate["props"]["raceID"] == "20261103OK37960"
    assert senate["props"]["state"] == "OK" and senate["props"]["officeID"] == "S"
    js = bodies["ap-literal-layout-client"]
    source_tokens = [b'w.slow=window.setInterval(i.bind(null,"slow"),12e4)', b'w.fast=window.setInterval(i.bind(null,"fast"),1e4)', b'fetch(`https://interactives.apelections.org/election-results/customers/layouts/organization-layouts/config/${e}/config.json`)', b'"true"===new URLSearchParams(n).get("test")', b'new URL(e,t).href']
    snippets = []
    for token in source_tokens:
        at = js.index(token)
        snippets.append({"decoded_byte_offset": at, "exact_token": token.decode(), "context": js[max(0, at - 130):at + len(token) + 180].decode()})
    org = json.loads(bodies["ap-observed-org-config"])
    assert org["id"] == "110246" and "www.kswo.com" in org["domains"]
    page = bodies["kswo-results"].decode()
    at = page.index("Fusion.contentCache=") + len("Fusion.contentCache=")
    cache, _ = json.JSONDecoder().raw_decode(page[at:])
    election_cache = {k: v for k, v in cache.items() if k in ("gsync-elections-featured", "gsync-elections")}
    assert len(election_cache) == 2
    for key, queries in election_cache.items():
        assert len(queries) == 1
        query, row = next(iter(queries.items()))
        assert json.loads(query)["includeTestResults"] is False
        assert row["data"]["updatedDate"] is None
        if key == "gsync-elections-featured":
            assert row["data"]["races"] == [] and row["data"]["isActive"] is False
        else:
            assert row["data"]["elections"] == [] and row["data"]["selectedElection"]["id"] is None
    news_nodes = Nodes(bodies["newson6-election-publication"]).nodes
    descriptions = [dict(n["attrs"]).get("content", "") for n in news_nodes if n["tag"] == "meta" and dict(n["attrs"]).get("name") == "description"]
    assert len(descriptions) == 1 and "June 16" in descriptions[0]
    schema_nodes = [json.loads(n["text"]) for n in news_nodes if n["tag"] == "script" and dict(n["attrs"]).get("type") == "application/ld+json"]
    assert schema_nodes
    products = {
        "ap-layoutClient.http-decoded.js.gz": gzip.compress(js, mtime=0),
        "literal-runtime-evidence.json": encoded_json({"AP_HTTP_decoding": {"receipt": "ap-literal-layout-client.receipt.json", "original_HTTP_content_encoding": "gzip", "archival_encoding": "additional gzip, separate from HTTP representation", "decoded_bytes": len(js), "decoded_sha256": sha(js)}, "actual_client_tokens": snippets, "full_AP_layouts": layouts, "complete_publisher_election_cache": election_cache, "NewsOn6_meta_description": descriptions[0], "complete_NewsOn6_schema": schema_nodes, "org_config_receipt": "ap-observed-org-config.receipt.json", "domain_registration_is_not_runtime_browser_verification": True}),
        "review.json": encoded_json({"status": "pass_bounded_newsroom_original_and_setup_review", "request_receipts": len(receipts), "whole_response_hops": hop_count, "unique_original_entity_objects": len(body_paths), "AP_layout_slots": [1, 5], "observed_Senate_setup_raceID": "20261103OK37960", "publisher_main_results_empty_at_retained_clock": True, "NewsOn6_scope": "June16 primary, not November", "AP_client_timer_ms": {"slow": 120000, "fast": 10000}, "timer_scope": "Public client code lanes; no active browser render or measured publisher data cadence", "genuine_November_counts_admitted": False, "current_choice_or_native_join_approved": False, "exact_eligible_remaining_pool": None, "AP_independent_from_other_AP_consumers": False, "Enid_scope": "Actual home and literal Politics/election category; no numerical November feed established", "source_receipts_retained_complete": True, "old_news_aggregate_modified": False})
    }
    for name, body in products.items():
        if args.seal:
            (R / name).write_bytes(body)
        else:
            assert (R / name).read_bytes() == body, name
    paths = sorted(p for p in R.rglob("*") if p.is_file() and p.name != "asset-manifest.json")
    assert not any(p.name.endswith(".pyc") or "__pycache__" in p.parts for p in paths)
    rows = [{"path": str(p.relative_to(R)), "bytes": p.stat().st_size, "sha256": sha(p.read_bytes())} for p in paths]
    assert all(r["bytes"] < 40000000 for r in rows)
    manifest = encoded_json({"scope": "Bounded primary newsroom public-source setup research only", "excludes_only": "asset-manifest.json", "owned_files": rows})
    if args.seal:
        (R / "asset-manifest.json").write_bytes(manifest)
    else:
        assert (R / "asset-manifest.json").read_bytes() == manifest
    print(json.dumps({"status": "pass", "receipts": len(receipts), "response_hops": hop_count, "owned_targets": len(rows), "maximum": max(r["bytes"] for r in rows), "genuine_November_counts_admitted": False}))


if __name__ == "__main__":
    main()
