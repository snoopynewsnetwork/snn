"""Coordinator external qualified source dispatch; immutable producer bytes untouched."""
from pathlib import Path
from collections import Counter
import csv
import gzip
import hashlib
import io
import json

S = Path(__file__).resolve().parents[1]
D = S / "data"
T = D / "turnout"
B = D / "baselines"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sem(v):
    return sha(canon(v))


def pin(p):
    b = p.read_bytes()
    assert len(b) < 40000000
    return {"path": str(p.relative_to(S)), "bytes": len(b), "sha256": sha(b)}


def read(p):
    b = p.read_bytes()
    if p.suffix == ".gz":
        b = gzip.decompress(b)
    if p.name.endswith((".csv", ".csv.gz")):
        return list(csv.reader(io.StringIO(b.decode("utf-8-sig"))))
    reject = lambda s: (_ for _ in ()).throw(ValueError("intentional invalid JSON constant " + s))
    if ".jsonl" in p.name:
        return [json.loads(x, parse_constant=reject) for x in b.splitlines() if x]
    return json.loads(b, parse_constant=reject)


class Ledger:
    def __init__(self):
        self.parts = []
        self.total = 0
        self.by_file = Counter()
        self.start()

    def start(self):
        self.buffer = io.BytesIO()
        self.gz = gzip.GzipFile(fileobj=self.buffer, mode="wb", filename="", mtime=0)
        self.digest = hashlib.sha256()
        self.size = self.count = 0

    def emit(self, file, pointer, value):
        if self.count >= 150000:
            self.close()
            self.start()
        line = canon({"file": file, "pointer": pointer, "full_recursive_semantic_sha256": sem(value)}) + b"\n"
        self.gz.write(line)
        self.digest.update(line)
        self.size += len(line)
        self.count += 1
        self.total += 1
        self.by_file[file] += 1

    def walk(self, file, value, pointer=""):
        if isinstance(value, (dict, list)):
            self.emit(file, pointer, value)
            for k, v in value.items() if isinstance(value, dict) else enumerate(value):
                if isinstance(v, (dict, list)):
                    self.walk(file, v, pointer + "/" + str(k).replace("~", "~0").replace("/", "~1"))

    def close(self):
        self.gz.close()
        body = self.buffer.getvalue()
        assert len(body) < 40000000
        p = D / f"coordinator-full-source-object-refs-v1-{len(self.parts) + 1:04}.jsonl.gz"
        if p.exists():
            assert p.read_bytes() == body
        else:
            p.write_bytes(body)
        self.parts.append({**pin(p), "complete_reconstructed_bytes": self.size, "complete_reconstructed_sha256": self.digest.hexdigest(), "complete_object_count": self.count, "format": "Every ordered JSONL reference in every complete partition; not a sample."})


def main():
    c = read(T / "priority-set.json")
    assert pin(T / "priority-set.json")["sha256"] == "7d788cf5c2efa884b86332833cb18a54e481b261f2f6cbab5206ac9d20e10aac"
    assert len(c) == 23 and len(c["complete_descending_order"]) == 458 and len(c["ordered_priority_keys"]) == 242
    assert (c["minimum80"]["preceding_votes"], c["minimum80"]["minimum80_votes"], c["minimum80"]["remainder_votes"]) == (393066, 394072, 97876)
    reviews = ["coordinator-turnout-original-review.json", "coordinator-writein-row5-review/proof.json", "coordinator-turnout-repair-final-review.json", "coordinator-baseline-final-review.json", "coordinator-baseline-cli-review.json"]
    for p in reviews:
        assert read(D / p)["status"].startswith(("pass", "confirmed_original"))
    frozen = {}
    seals = []
    for root, n, expected, extra in [(T, 378, "6ee51d0fb29b594e8685c36de518255950521586c2c5765827e89fbca8f04649", ["turnout.md", "data/county-turnout.csv"]), (B, 234, "f3b33d30631cec93796c4aab2becec82a49982da39878421f11c22ea5e1a8620", ["county-partisanship.md", "data/county-baselines.csv"])]:
        mf = read(root / "asset-manifest.json")
        rows = mf["owned_assets"]
        assert len(rows) == n and pin(root / "asset-manifest.json")["sha256"] == expected
        actual = {str(p.relative_to(S)) for p in root.rglob("*") if p.is_file() and p != root / "asset-manifest.json"} | set(extra)
        assert actual == {r["path"] for r in rows}
        for r in rows:
            assert pin(S / r["path"]) == r
            frozen[r["path"], r["sha256"]] = r
        r = pin(root / "asset-manifest.json")
        frozen[r["path"], r["sha256"]] = r
        seals.append({**r, "owned_field": "owned_assets", "owned_entries": n, "every_complete_listed_body_required": True, "path_resolution": "state-relative"})
    for r in read(B / "source/inputs.json"):
        p = S / r["body_path"]
        rpin = pin(p)
        assert rpin["sha256"] == r["stored_sha256"] and sha(gzip.decompress(p.read_bytes())) == r["raw_sha256"]
        frozen[rpin["path"], rpin["sha256"]] = rpin
    # Exact historical bodies resolve through complete immutable archive members.
    history = []
    capture = read(T / "history/pre-repair-v1/capture.json")
    orig = {r["path"] for r in capture["immutable_original_refs"]}
    archive = pin(T / "history/pre-repair-v1/bodies.tar.gz")
    for r in capture["all362"]:
        storage = {"kind": "immutable_original_reference", "file": pin(S / r["path"])} if r["path"] in orig else {"kind": "tar_gzip_member", "archive": archive, "member": r["path"]}
        history.append({**r, "storage": storage, "capture_role": "complete_pre_repair362"})
    witness = read(T / "qa/pre-peer-body-witness.json")
    archive = pin(T / witness["body_archive"]["path"])
    for r in witness["frozen_bodies"]:
        history.append({**r, "storage": {"kind": "tar_gzip_member", "archive": archive, "member": r["path"]}, "capture_role": "original_first227"})
    peer = read(T / "reciprocal/peer-finished-capture/capture.json")
    archives = [pin(T / "reciprocal/peer-finished-capture" / r["path"]) for r in peer["tar_gzip_parts_in_order"]]
    for r in peer["all235"]:
        history.append({**r, "storage": {"kind": "ordered_tar_gzip_member", "parts": archives, "gzip_sha256": peer["gzip_sha256"], "tar_sha256": peer["tar_sha256"], "member": r["path"]}, "capture_role": "finished_baseline235"})
    bw = read(B / "witness/pre-peer-body-witness.json")
    archive = pin(B / bw["archive"])
    for r in bw["bodies"]:
        history.append({"path": "data/baselines/" + r["path"], "bytes": r["bytes"], "sha256": r["sha256"], "storage": {"kind": "tar_gzip_member", "archive": archive, "member": r["path"]}, "capture_role": "baseline_pre_peer53"})
    ledger = Ledger()
    for k, v in c.items():
        ledger.emit("data/turnout/priority-set.json", "/" + k, v)
    companions, opaque = [], []
    for r in sorted(frozen.values(), key=lambda r: r["path"]):
        p = S / r["path"]
        if not p.name.endswith((".json", ".json.gz", ".jsonl.gz", ".csv", ".csv.gz")):
            continue
        try:
            value = read(p)
        except (ValueError, UnicodeError) as exc:
            opaque.append({**r, "role": "Complete intentionally invalid CLI fixture; raw bytes retained, not coerced into valid JSON.", "parse_error": str(exc)})
            continue
        row = {**r, "full_semantic_sha256": sem(value), "complete_length": len(value) if isinstance(value, (dict, list)) else None, "semantic_type": type(value).__name__, "complete_body_required": True, "projection_or_subset_substitution": False, "format": "csv_full_header_and_all_rows" if ".csv" in p.name else "jsonl_full_ordered_array" if ".jsonl" in p.name else "json"}
        companions.append(row)
        ledger.walk(r["path"], value)
    ledger.close()
    full = c["complete_descending_order"]
    priority = set(c["ordered_priority_keys"])
    priorityparents = list(dict.fromkeys(r["parent_key"] for r in full if r["key"] in priority))
    assert len(priorityparents) == 37
    parents = {}
    for p in c["municipal_and_administrative_parent_sensitivity"]["full_inventory"]:
        ranked = [r for r in full if r["parent_key"] == p["key"]]
        parents[p["key"]] = {"original_ordered_native_inventory_keys": p["native_keys"], "full_source_rank_ordered_children": [r["key"] for r in ranked], "ordered_priority_children": [r["key"] for r in ranked if r["key"] in priority], "ordered_remainder_children": [r["key"] for r in ranked if r["key"] not in priority], "complete_parent_contract_pointer": "/municipal_and_administrative_parent_sensitivity/full_inventory/" + str(len(parents))}
    out = {"schema": "RI-external-complete-historical-source-dispatch-v1", "status": "accepted_complete_historical_reported_candidate_plus_generic_source_research_only", "state": "RI", "coordinator_agent_id": "d0fc3534-1613-4883-b48b-21a233fcfd9e", "authority": "PATH ONLY in downstream owned packages. Never copy/hash/reverse-pin this acceptance. Frozen producer flags remain untouched.", "frozen_contract": pin(T / "priority-set.json"), "producer_seals": seals, "independent_coordinator_reviews": [pin(D / p) for p in reviews], "frozen_file_pins": sorted(frozen.values(), key=lambda r: (r["path"], r["sha256"])), "historical_full_body_resolvers": history, "complete_root_field_semantics": [{"pointer": "/" + k, "full_recursive_semantic_sha256": sem(v)} for k, v in c.items()], "complete_source_companion_files": companions, "complete_opaque_invalid_fixture_files": opaque, "complete_source_object_reference_bodies": ledger.parts, "complete_source_object_count": ledger.total, "source_objects_by_file": dict(ledger.by_file), "full_native_contexts": 458, "full_inventory_contexts": 497, "unavailable_Senate_contexts": 39, "municipal_parents": 39, "separate_state_admin_contexts": 4, "primary_source_denominator": 491948, "top15_votes": 34697, "minimum80": {"count": 242, "votes": 394072, "preceding_count": 241, "preceding_votes": 393066, "crossing_code": "0804", "crossing_votes": 1006, "crossing_line": 4061, "crossing_byte_offset": 1075900}, "remainder": {"count": 216, "votes": 97876}, "ordered_full_keys": [r["key"] for r in full], "ordered_priority_keys": c["ordered_priority_keys"], "ordered_remainder_keys": [r["key"] for r in full if r["key"] not in priority], "all_parent_ordered_child_arrays": parents, "ordered_priority_parent_keys": priorityparents, "priority_municipal_parents": 37, "source_qualifications": ["Reported printed candidate+generic historical scope; generic1244 is not eligible named-writein completeness/legalnative80 proof.", "Original Cranston D5 Mario Frioli trailing space/E5=1 corrected detail coverage1227/eight, prior row6-only1226/nine retained. Municipal printed/generic1239+stateadmin5=1244 unchanged; no detail allocation/dedup/eligibility inference.", "Full458source order/242keys/216remainder and497inventory/39absentSenateNULL/15observedzero/all39municipal+4federal contexts preserved. Federal1473 outside municipal490475;43parent21prefix is sensitivity only, not dispatch.", "Frozen contract peer_agreement string remains historical pending metadata by design; external bounded reciprocal proofs independently pass and are authoritative only for their exact captured source-core scope. Do not mutate producer flags or claim future peer outcome equality.", "2020sameClassIIReed/Waters,2024otherClassIWhitehouse/Morgan plus separatepresidents,2022actualGovernor. All14slots retained;2020slot3 unlabelled technical versus Emergency officialHTML/XLSX,2022Early;4-14unlabelled. No crossyear/native/current method join.", "Current final ballot/declaredwritein/currentoperational IDs/geography and laterlegal changes require bounded independent research. Reporting status/registration/ballot/accepted/candidate counts never exact outstanding pool or live probability."], "dispatch_requirements": ["Inventory actual stateBOE/Secretary plus all39municipal authorities/raw fields; deep bounded investigations for all37prioritymunicipal parents and242ordered complete source contexts,216remainder/full458/497inventory/fourstateadmin retained.", "Maps acquire actual qualified assets for all37priorityparent chains with complete statewidefallback where available; no fabricated observation/polygon/physical/current/legal joins or vote allocation.", "First independently verify exact acceptance/contract bytes then consume entire authority in memory; owned authority PATH ONLY. Replay every full root/companion/orderedledger/object/history/original/filepin and preserve candidate/party/method/null/admin/raw-position schemas. No producer writers/mutable aggregate/unfinished peer or optional coordinator proof build dependencies."], "current_geography_approved": False, "current_November_returns_admitted": False, "current_choice_or_reporting_IDs_approved": False, "legal_native80_robustness_approved": False, "live_cadence_or_exact_remainder_approved": False, "collector_or_probability_approval": False}
    p = D / "coordinator-priority-acceptance.json"
    body = json.dumps(out, ensure_ascii=False, indent=2).encode() + b"\n"
    assert len(body) < 40000000
    if p.exists():
        assert p.read_bytes() == body
    else:
        p.write_bytes(body)
    print(json.dumps({"acceptance": pin(p), "root_fields": len(c), "companions": len(companions), "objects": ledger.total, "partitions": len(ledger.parts), "file_pins": len(frozen), "historical_bodies": len(history), "priority_parents": len(priorityparents)}))


if __name__ == "__main__":
    main()
