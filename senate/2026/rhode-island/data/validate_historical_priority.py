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
    ck(len(c) == len(a["complete_root_field_semantics"]) == 23, "every complete contract root")
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
    ck(sum(by_file.values()) == a["complete_source_object_count"] == 1699508 and dict(by_file) == a["source_objects_by_file"], "complete reference graph across every source file")
    ck(len(a["ordered_full_keys"]) == 458 and len(a["ordered_priority_keys"]) == 242 and len(a["ordered_remainder_keys"]) == 216, "full exact disjoint native orders")
    ck(not (set(a["ordered_priority_keys"]) & set(a["ordered_remainder_keys"])) and set(a["ordered_full_keys"]) == set(a["ordered_priority_keys"]) | set(a["ordered_remainder_keys"]), "priority remainder partition")
    ck(len(a["all_parent_ordered_child_arrays"]) == 43 and len(a["ordered_priority_parent_keys"]) == 37, "39 municipal plus4 administrative full parents")
    out = {"status": "pass_independent_complete_historical_source_authority_replay", "checks": N, "complete_roots": 23, "complete_companions": len(a["complete_source_companion_files"]), "complete_recursive_objects": sum(by_file.values()), "complete_partitions": len(a["complete_source_object_reference_bodies"]), "frozen_file_pins": len(pins), "complete_historical_bodies": len(a["historical_full_body_resolvers"]), "full_native_inventory": 497, "Senate_native": 458, "priority": 242, "remainder": 216, "all_parent_scopes": 43, "priority_municipal_parents": 37, "producer_writes": False, "current_or_legal_geography_approval": False}
    (D / "coordinator-priority-validation.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
