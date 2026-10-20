"""Coordinator external qualified source dispatch; immutable producer bytes untouched."""
from pathlib import Path
from collections import Counter
import csv
import gzip
import hashlib
import io
import tarfile
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
    assert pin(T / "priority-set.json")["sha256"] == "5a832915bfb054111f59759503a6024cfa8696588b6dacd62cbee54d15b74f0c"
    assert len(c["ordered_units"]) == 2669 and len(c["parent_inventory"]) == 133
    assert len(c["ordered_priority_keys"]) == 1538 and len(c["ordered_remainder_keys"]) == 1131
    assert c["denominator"] == 4445535 and c["minimum80"]["votes"] == 3557034
    assert c["minimum80"]["preceding"]["votes"] == 3555604 and c["minimum80"]["remainder_votes"] == 888501
    reviews = ["coordinator-turnout-original-review.json", "coordinator-baseline-final-review.json", "coordinator-baseline-cli-review.json", "coordinator-turnout-repair-final-review.json", "coordinator-first-pair-validation.json"]
    for p in reviews:
        assert read(D / p)["status"].startswith("pass")
    frozen, seals = {}, []
    for root, field, n, expected, extra in [
        (T, "owned_assets", 411, "48d24f1395d8339a3d7e5989bb4a7ae54f39ca19d8ebc791f63f310e31d0a4bb", ["turnout.md", "data/county-turnout.csv"]),
        (B, "files", 299, "9b93b5ebf5c4e6d20c7e1216b992886d265c343021f8a10c48f982ecd2e74cbf", ["county-partisanship.md", "data/county-baselines.csv"])]:
        mf = read(root / "asset-manifest.json")
        rows = mf[field]
        assert len(rows) == n and pin(root / "asset-manifest.json")["sha256"] == expected
        actual = {str(p.relative_to(S)) for p in root.rglob("*") if p.is_file() and p != root / "asset-manifest.json"} | set(extra)
        assert actual == {r["path"] for r in rows}
        for r in rows:
            assert pin(S / r["path"]) == r
            frozen[r["path"], r["sha256"]] = r
        r = pin(root / "asset-manifest.json")
        frozen[r["path"], r["sha256"]] = r
        seals.append({**r, "owned_field": field, "owned_entries": n, "every_complete_listed_body_required": True, "path_resolution": "state-relative"})
    sourcepins = read(B / "source/input-pins.json")["sources"]
    additional = read(B / "source/additional-pins.json")
    sourcepins += [{"receipt_path": additional["receipt_path"], "receipt_sha256": additional["receipt_sha256"], "entities": [additional["entity"]]}]
    for r in sourcepins:
        q = pin(S / r["receipt_path"])
        assert q["sha256"] == r["receipt_sha256"]
        frozen[q["path"], q["sha256"]] = q
        for e in r["entities"]:
            q = pin(S / e["path"])
            assert (q["bytes"], q["sha256"]) == (e["bytes"], e["sha256"])
            raw = gzip.decompress((S / e["path"]).read_bytes())
            assert (len(raw), sha(raw)) == (e["raw_bytes"], e["raw_sha256"])
            frozen[q["path"], q["sha256"]] = q
    for r in read(T / "source/pinned-originals.json"):
        q = pin(S / r["body_path"])
        assert q["sha256"] == r["stored_sha256"]
        raw = gzip.decompress((S / r["body_path"]).read_bytes())
        assert len(raw) == r["raw_bytes"] and sha(raw) == r["raw_sha256"]
        frozen[q["path"], q["sha256"]] = q
    # Enumerate EVERY regular member of every retained complete historical archive,
    # including original-first, captured peer, checker failure and complete old package.
    history = []
    for r in sorted(frozen.values(), key=lambda r: r["path"]):
        if not r["path"].endswith(".tar.gz"):
            continue
        with tarfile.open(S / r["path"], mode="r:gz") as tf:
            for member in tf:
                if not member.isfile():
                    assert member.isdir(), (r["path"], member.name, "unexpected nonregular archive member")
                    continue
                body = tf.extractfile(member).read()
                history.append({"path": member.name, "bytes": len(body), "sha256": sha(body), "storage": {"kind": "tar_gzip_member", "archive": r, "member": member.name}, "capture_role": "every_exact_member_of_complete_retained_archive"})
    # Large immutable references deliberately not duplicated in the old-package tar.
    for name in ["turnout-original-first", "baseline-final-peer"]:
        captured = read(T / "history/resume-citation-reciprocal" / (name + ".json"))
        for r in captured["bodies"]:
            if r["reference_path"]:
                q = pin(S / r["reference_path"])
                assert (q["bytes"], q["sha256"]) == (r["bytes"], r["sha256"])
                history.append({"path": r["path"], "bytes": r["bytes"], "sha256": r["sha256"], "storage": {"kind": "immutable_original_reference", "file": q}, "capture_role": name + "_full_immutable_body_reference"})
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
            fullsem = sem(value)
        except (ValueError, UnicodeError) as exc:
            opaque.append({**r, "role": "Complete intentionally invalid CLI fixture retained literally, never coerced into valid JSON.", "parse_error": str(exc)})
            continue
        companions.append({**r, "full_semantic_sha256": fullsem, "complete_length": len(value) if isinstance(value, (dict, list)) else None, "semantic_type": type(value).__name__, "complete_body_required": True, "projection_or_subset_substitution": False, "format": "csv_full_header_and_all_rows" if ".csv" in p.name else "jsonl_full_ordered_array" if ".jsonl" in p.name else "json"})
        ledger.walk(r["path"], value)
    ledger.close()
    full = c["ordered_units"]
    priority = set(c["ordered_priority_keys"])
    priorityparents = list(dict.fromkeys(r["parent_key"] for r in full if r["key"] in priority))
    assert len(priorityparents) == 108
    parents = {}
    for i, p in enumerate(c["parent_inventory"]):
        ranked = [r for r in full if r["parent_key"] == p["historical_parent_key"]]
        assert p["all_native_keys"] == [r["key"] for r in ranked]
        parents[p["historical_parent_key"]] = {"original_ordered_native_inventory_keys": p["all_native_keys"], "full_source_rank_ordered_children": [r["key"] for r in ranked], "ordered_priority_children": [r["key"] for r in ranked if r["key"] in priority], "ordered_remainder_children": [r["key"] for r in ranked if r["key"] not in priority], "complete_parent_contract_pointer": "/parent_inventory/" + str(i)}
    out = {"schema": "VA-external-complete-historical-source-dispatch-v1", "status": "accepted_complete_historical_reported_candidate_plus_generic_source_research_only", "state": "VA", "coordinator_agent_id": "d0fc3534-1613-4883-b48b-21a233fcfd9e", "authority": "PATH ONLY in downstream owned packages. Never copy/hash/reverse-pin this acceptance. Frozen producer flags remain untouched.", "frozen_contract": pin(T / "priority-set.json"), "producer_seals": seals, "independent_coordinator_reviews": [pin(D / p) for p in reviews], "frozen_file_pins": sorted(frozen.values(), key=lambda r: (r["path"], r["sha256"])), "historical_full_body_resolvers": history, "complete_root_field_semantics": [{"pointer": "/" + k, "full_recursive_semantic_sha256": sem(v)} for k, v in c.items()], "complete_source_companion_files": companions, "complete_opaque_invalid_fixture_files": opaque, "complete_source_object_reference_bodies": ledger.parts, "complete_source_object_count": ledger.total, "source_objects_by_file": dict(ledger.by_file), "full_native_contexts": 2669, "county_equivalent_parents": 133, "counties": 95, "independent_cities": 38, "primary_source_denominator": 4445535, "top15_votes": 80617, "minimum80": c["minimum80"], "ordered_full_keys": c["full_all_unit_order"], "ordered_priority_keys": c["ordered_priority_keys"], "ordered_remainder_keys": c["ordered_remainder_keys"], "all_parent_ordered_child_arrays": parents, "ordered_priority_parent_keys": priorityparents, "priority_parent_count": 108, "source_qualifications": [
        "Reported2024otherClassI Kaine/Cao+generic8509 historical scope; generic is not eligible named-writein completeness/legalnative80 proof.2020Warner/Gade sameClassII;2018Kaine/Stewart/Waters actualmidterm; separate2024president all7 columns retained. No2026ID/crossyear/native-method/geometric join.",
        "All2669native/133localities95counties38cities/full1538priority1131remainder/108priorityparent chains required; 44parent prefix is sensitivity only, never dispatch. Every source-native virtual/central/post-election/provisional and blank-ID export constituent retained, never a physical-site assumption.",
        "API full2669candidate vectors uniquely associate within explicit source parent for count controls only; 40035whole candidate-method observations and five exact group scopes retained. State metadata ballotsCast0 is literal source metadata, not an actual statewide zero.16extra allzero export groups/48blank-ID rows remain separate.",
        "2018native/state generic5509 vs locality5473 +36 unallocated, with FairfaxCity1/RichmondCity10/RoanokeCounty25 retained; no rescaling.2024nVotesParty1 alternate conflicts retained; source republishing/verification clocks are not certification chronology.",
        "NativeAPI ballotsCast4407747 vs localitymetadata4526538 vs officialturnoutCSV4537976 vs annual4535314 remain separate. Native registration6434637 vs localitymetadata6482067/datedregistration sources differ; absent/null virtual/admin fields never invented0. Older Local/Congressional administrative repeated tuples retained, no dedup/disjointballot claim.",
        "URL defect a931/a5f7 was caused by old report prose formatter; exact old report/script/finding/checker failures retained, prior validator did not catch it. Correct literal request URL and production protected-renderer regression passed. No source/numeric/native key/order/schema repair; frozen source contract peer metadata only changed.",
        "Every original-first and captured final peer body remains exact in full archive or immutable body reference. Bounded source-core agreement does not extend to peer calculators, scenarios, targets, outcomes, president results outside shared turnover scope, later/future bytes or current approvals.",
        "Current final-election federal workbookOct6 listsWarnerD/MizusawaR but is not signed statewide facsimile/final later roster or eligible-writein exhaustion. Independently research current rules/calendar/enacted-effective-date/latercourt scope and actual linked current sources; no primary or old-ID substitution."
    ], "dispatch_requirements": [
        "Inventory actual ELECT/stateboard and all133local registrars/electoralboard authorities with complete raw fields, keeping cities/counties distinct. Deep bounded actual public-chain investigations for all108priorityparents and1538ordered complete source contexts; explicit1131remainder/full2669hierarchy. Do not guess endpoints, IDs or run auth/account/challenge actions.",
        "Maps acquire actual qualified assets for all108priorityparent chains with complete statewidefallback when available; no fabricated observation/polygon/physical/current/legal joins or vote allocation. Native virtual/nonphysical records require explicit unavailable geography cases.",
        "FIRST independently verify exact acceptance/contract bytes then consume entire authority in memory; owned authority PATH ONLY. Replay every full root/companion/orderedledger/object/history/original/filepin and preserve candidate/party/method/null/admin/raw-position schemas. No producer writers/mutable news aggregate/unfinished peer or optional coordinator proof build dependencies. Complete bounded substantive report/source/QA, manifestLAST, final readonly audit, then actuallyend."
    ], "current_geography_approved": False, "current_November_returns_admitted": False, "current_choice_or_reporting_IDs_approved": False, "legal_native80_robustness_approved": False, "live_cadence_or_exact_remainder_approved": False, "collector_or_probability_approval": False}
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
