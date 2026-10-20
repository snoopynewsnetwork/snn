"""Independent coordinator whole-object, receipt and admission review; no producer imports."""
from pathlib import Path
import gzip
import hashlib
import json
import collections

S = Path(__file__).resolve().parents[1]
R = S / "data/results-sources"
N = 0
CACHE = {}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def ck(ok, why):
    global N
    N += 1
    if not ok:
        raise AssertionError(why)


def semantic(obj):
    return sha(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode())


def filebody(pin):
    p = S / pin["path"]
    b = p.read_bytes()
    ck(len(b) == pin["bytes"] and sha(b) == pin["sha256"], "whole file pin " + pin["path"])
    return b


def objectref(ref):
    pin = ref["file"]
    key = pin["path"], pin["sha256"]
    if key not in CACHE:
        b = filebody(pin)
        if pin["path"].endswith(".gz"):
            b = gzip.decompress(b)
        CACHE[key] = [json.loads(x) for x in b.splitlines()] if pin["path"].endswith((".jsonl.gz", ".jsonl")) else json.loads(b)
    obj = CACHE[key]
    for part in ref["pointer"].split("/")[1:]:
        part = part.replace("~1", "/").replace("~0", "~")
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    ck(semantic(obj) == ref["whole_object_semantic_sha256"], "complete recursive object semantics")
    return obj


def refs(obj):
    total = 0
    if isinstance(obj, dict):
        if {"file", "pointer", "whole_object_semantic_sha256"} <= set(obj):
            objectref(obj)
            total += 1
        for v in obj.values():
            total += refs(v)
    elif isinstance(obj, list):
        for v in obj:
            total += refs(v)
    return total


def main():
    mf = json.loads((R / "asset-manifest.json").read_bytes())
    ck(sha((R / "asset-manifest.json").read_bytes()) == "fcc6f5c41352a340fa7005ce8d1b9f3ae97e8d6fde373b030c4e7819a5558296", "actual final handoff manifest")
    actual = {str(p.relative_to(S)) for p in R.rglob("*") if p.is_file()} | {"official-results.md", "data/official-results-sources.csv"}
    ck(len(mf["files"]) == 766 and actual == {r["path"] for r in mf["files"]} | {"data/results-sources/asset-manifest.json"}, "exact complete self-only owned membership")
    for pin in mf["files"]:
        ck(pin["bytes"] < 40000000 and b"c7432b6121ea67857d03f88d6e4c9101d3b853c677834b47cb36cc55e6fc1c0b" not in filebody(pin), "strict size/path-only external acceptance authority")
    contract = json.loads((S / "data/turnout/priority-set.json").read_bytes())
    c = json.loads((R / "coverage.json").read_bytes())
    ck(all(contract[k] is None for k in ["complete_order", "ordered_priority_keys", "top15", "minimum80", "remainder"]), "canonical native dispatch remains unavailable")
    parents = [json.loads(x) for x in gzip.decompress((R / "parents.jsonl.gz").read_bytes()).splitlines()]
    unavailable = [json.loads(x) for x in gzip.decompress((R / "unavailable-parents.jsonl.gz").read_bytes()).splitlines()]
    known = [json.loads(x) for x in gzip.decompress((R / "known-contexts.jsonl.gz").read_bytes()).splitlines()]
    ck(len(parents) == 36 and len(unavailable) == 31 and len(known) == 510, "full distinct parent and native scopes")
    ck(len({p["parent_key"] for p in parents}) == 36 and len({p["historical_context_key"] for p in known}) == 510, "unique whole parent/context identities")
    count = refs(parents) + refs(known) + refs(unavailable)
    all_source = [x for p in contract["all_36_county_parents"] for x in p["source_native_constituents"]]
    ck({r["key"] for r in all_source} == {r["historical_context_key"] for r in known}, "every complete known source child retained")
    ck(sum(objectref(r["complete_source_context"])["reported_votes"] for r in known) == 1128521, "all known source votes")
    for p in parents:
        source = objectref(p["complete_original_parent"])
        ck(source["county_key"] == p["parent_key"] and source["county_fips"] == p["county_fips"], "full parent role and FIPS identity")
        ck(p["investigation"] and len(p["investigation"]) > 80 and p["complete_current_response_references"], "substantive bounded shared-parent investigation")
    for p in known:
        ck(p["current_leaf_ID"] is None and p["current_geometry_ID"] is None and p["method_identity_join"] is None and p["current_approval"] is False, "no inferred current leaf or method joins")
    index = json.loads((R / "acquisition-index.json").read_bytes())
    ck(len(index) == 235, "complete bounded source inventory")
    hops = 0
    statuses = collections.Counter()
    for r in index:
        req = json.loads(filebody(r["request"]))
        structure = json.loads(gzip.decompress(filebody(r["structure"])))
        ck(req["key"] == structure["key"] == r["key"], "complete receipt/structure binding")
        for e in req["entities"]:
            b = e["body"]
            stored = b"".join(filebody(p) for p in b["parts"])
            raw = gzip.decompress(stored)
            ck(len(stored) == b["stored_bytes"] and sha(stored) == b["stored_sha256"] and len(raw) == b["raw_bytes"] and sha(raw) == b["raw_sha256"], "entire source entity and ordered parts")
            ck(e["retrieved_utc"] and e["url"] and isinstance(e["headers"], dict), "received source clock/header provenance")
            hops += 1
            statuses[e["status"]] += 1
    obs = json.loads((R / "current-observations.json").read_bytes())
    ck(obs["staging"]["admitted"] is False and sum(x["votes"] for x in obs["staging"]["senate_rows"]) == 209, "positive staging values retained and rejected")
    ck(all(v in (False, None) for v in obs["qualifications"].values()), "all current operational approvals remain false/unknown")
    ck(c["known_native_reported_votes"] + c["unclosed_parent_reported_votes"] == c["statewide_president_reported_2024"] == 2244493, "statewide unknown-parent votes retained")
    out = {"status": "pass_coordinator_independent_whole_object_receipt_and_scope_review", "checks": N, "owned_manifest_targets": 766, "whole_parent_records": 36, "whole_known_contexts": 510, "whole_unavailable_cases": 31, "complete_semantic_object_references": count, "complete_acquisition_records": len(index), "whole_received_response_entities": hops, "statuses": dict(statuses), "canonical_native_priority": None, "genuine_November_admission": False, "request_metadata_gap": "Routine implicit outgoing GET headers/effective wire URLs unretained; received entity bytes/headers/clocks and explicit POST bodies retained. Not reconstructed as observations.", "visual_scope": "Coordinator actually viewed directive pages5/6 and zero-report page1. Signature/byline, four literal named party rows and generic-zero setup corroborated; later amendment/write-in exhaustion unproved.", "legal_scope": "Retained current temporary reporting rule and ORS254/258 selected sections independently read. Fresh web reader failed state-code routes, separately reached complete Watson primary opinion; no later legal/docket exhaustion or measured cadence inferred.", "producer_writes": False}
    (S / "data/coordinator-official-final-review.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
