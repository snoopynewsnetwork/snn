"""Independent read-only full external authority/reference replay; writes proof only."""
from pathlib import Path
import collections
import csv
import gzip
import hashlib
import io
import json
import tarfile

S = Path(__file__).resolve().parents[1]
D = S / "data"
N = 0


def sha(b):
    return hashlib.sha256(b).hexdigest()


def ck(ok, why):
    global N
    N += 1
    if not ok:
        raise AssertionError(why)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def checked(pin):
    b = (S / pin["path"]).read_bytes()
    ck(len(b) == pin["bytes"] < 40000000 and sha(b) == pin["sha256"], "complete immutable body " + pin["path"])
    return b


def parsed(pin):
    b = checked(pin)
    name = pin["path"]
    if name.endswith(".gz"):
        b = gzip.decompress(b)
    if name.endswith((".csv", ".csv.gz")):
        return list(csv.reader(io.StringIO(b.decode("utf-8-sig"))))
    if ".jsonl" in name:
        return [json.loads(x) for x in b.splitlines() if x]
    return json.loads(b)


def main():
    a = json.loads((D / "coordinator-priority-acceptance.json").read_bytes())
    pins = {r["path"]: r for r in a["frozen_file_pins"]}
    for r in a["frozen_file_pins"]:
        checked(r)
    for r in a["independent_coordinator_reviews"]:
        checked(r)
    c = parsed(a["frozen_contract"])
    ck(len(c) == len(a["complete_root_field_semantics"]) == 25, "every complete contract root")
    for r in a["complete_root_field_semantics"]:
        ck(sha(canonical(c[r["pointer"][1:]])) == r["full_recursive_semantic_sha256"], "whole root semantics")
    for r in a["complete_source_companion_files"]:
        value = parsed(r)
        ck(sha(canonical(value)) == r["full_semantic_sha256"] and (len(value) if isinstance(value, (dict, list)) else None) == r["complete_length"], "whole companion semantics")
    archives = {}
    for r in a["historical_full_body_resolvers"]:
        st = r["storage"]
        if st["kind"] == "immutable_original_reference":
            b = checked(st["file"])
        else:
            archive_pins = st["parts"] if st["kind"] == "ordered_tar_gzip_member" else [st["archive"]]
            key = tuple((p["path"], p["sha256"]) for p in archive_pins)
            if key not in archives:
                stored = b"".join(checked(p) for p in archive_pins)
                raw = gzip.decompress(stored)
                if st["kind"] == "ordered_tar_gzip_member":
                    ck(sha(stored) == st["gzip_sha256"] and sha(raw) == st["tar_sha256"], "whole ordered historical archive")
                archives[key] = tarfile.open(fileobj=io.BytesIO(raw))
            b = archives[key].extractfile(st["member"]).read()
        ck(len(b) == r["bytes"] and sha(b) == r["sha256"], "complete historical path/hash body")
    by_file = collections.Counter()
    current = None
    value = None
    for part in a["complete_source_object_reference_bodies"]:
        stored = checked(part)
        raw = gzip.decompress(stored)
        ck(len(raw) == part["complete_reconstructed_bytes"] and sha(raw) == part["complete_reconstructed_sha256"], "whole ordered reference partition")
        count = 0
        for line in raw.splitlines():
            row = json.loads(line)
            if current != row["file"]:
                current = row["file"]
                value = parsed(pins[current])
            target = value
            for p in row["pointer"].split("/")[1:]:
                p = p.replace("~1", "/").replace("~0", "~")
                target = target[int(p)] if isinstance(target, list) else target[p]
            ck(sha(canonical(target)) == row["full_recursive_semantic_sha256"], "every complete ordered recursive source object")
            count += 1
            by_file[current] += 1
        ck(count == part["complete_object_count"], "every partition count")
    ck(sum(by_file.values()) == a["complete_source_object_count"] == sum(r["complete_object_count"] for r in a["complete_source_object_reference_bodies"]) and dict(by_file) == a["source_objects_by_file"], "complete reference graph across every source file")
    ck(len(a["ordered_full_keys"]) == 2669 and len(a["ordered_priority_keys"]) == 1538 and len(a["ordered_remainder_keys"]) == 1131, "full exact disjoint native orders")
    ck(not (set(a["ordered_priority_keys"]) & set(a["ordered_remainder_keys"])) and set(a["ordered_full_keys"]) == set(a["ordered_priority_keys"]) | set(a["ordered_remainder_keys"]), "priority remainder partition")
    ck(len(a["all_parent_ordered_child_arrays"]) == 133 and len(a["ordered_priority_parent_keys"]) == 108, "95 counties plus38 independent cities;108 priorityparents")
    ck(c["denominator"] == 4445535 and c["top15"]["votes"] == 80617, "exact original state denominator and top15")
    ck(c["minimum80"]["votes"] == 3557034 and c["minimum80"]["preceding"]["votes"] == 3555604, "native integer80 crossing")
    ck(5 * 3555604 < 4 * 4445535 <= 5 * 3557034, "strict preceding prefix fails; crossing succeeds")
    ck([r["key"] for r in c["ordered_units"]] == a["ordered_full_keys"], "entire source native object order")
    for parent, r in a["all_parent_ordered_child_arrays"].items():
        full = [v["key"] for v in c["ordered_units"] if v["parent_key"] == parent]
        priority = set(a["ordered_priority_keys"])
        ck(r["full_source_rank_ordered_children"] == full, "every full parent/child array")
        ck(r["ordered_priority_children"] == [k for k in full if k in priority] and r["ordered_remainder_children"] == [k for k in full if k not in priority], "every priority/remainder parent array")
    for r in a["producer_seals"]:
        mf = parsed(r)
        rows = mf[r["owned_field"]]
        ck(len(rows) == r["owned_entries"], "complete producer manifest list")
        root = S / Path(r["path"]).parent
        report = ["turnout.md", "data/county-turnout.csv"] if root.name == "turnout" else ["county-partisanship.md", "data/county-baselines.csv"]
        actual = {str(p.relative_to(S)) for p in root.rglob("*") if p.is_file() and p != S / r["path"]} | set(report)
        ck(actual == {v["path"] for v in rows}, "exact producer sealed membership; no exclusions")
        for v in rows:
            checked(v)
    out = {"status": "pass_independent_complete_historical_source_authority_replay", "checks": N, "complete_roots": 25, "complete_companions": len(a["complete_source_companion_files"]), "complete_recursive_objects": sum(by_file.values()), "complete_partitions": len(a["complete_source_object_reference_bodies"]), "frozen_file_pins": len(pins), "complete_historical_bodies": len(a["historical_full_body_resolvers"]), "full_native_contexts": 2669, "priority": 1538, "remainder": 1131, "all_parent_scopes": 133, "priority_parents": 108, "producer_writes": False, "current_or_legal_geography_approval": False}
    body = (json.dumps(out, indent=2) + "\n").encode()
    path = D / "coordinator-priority-validation.json"
    import sys
    if "--check" in sys.argv:
        ck(path.read_bytes() == body, "exact frozen proof replay")
    else:
        path.write_bytes(body)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
