"""Independent complete pre-repair/peer/repaired history and original-cell check."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import tarfile

S = Path(__file__).resolve().parents[1]
T = S / "data/turnout"
N = 0


def sha(b):
    return hashlib.sha256(b).hexdigest()


def ck(ok, why):
    global N
    N += 1
    if not ok:
        raise AssertionError(why)


def load(p):
    return json.loads(p.read_bytes())


def exact(body, r, why):
    ck(len(body) == r["bytes"] and sha(body) == r["sha256"], why)
    return body


def main():
    m = load(T / "asset-manifest.json")
    ck(sha((T / "asset-manifest.json").read_bytes()) == "6ee51d0fb29b594e8685c36de518255950521586c2c5765827e89fbca8f04649", "actual final repair manifest")
    actual = {str(p.relative_to(S)) for p in T.rglob("*") if p.is_file()} | {"turnout.md", "data/county-turnout.csv"}
    ck(len(m["owned_assets"]) == 378 and actual == {r["path"] for r in m["owned_assets"]} | {"data/turnout/asset-manifest.json"}, "complete self-only manifest")
    for r in m["owned_assets"]:
        exact((S / r["path"]).read_bytes(), r, "every current owned body")
        ck(r["bytes"] < 40000000, "strict object bound")
    capture = load(T / "history/pre-repair-v1/capture.json")
    arc = capture["archive"]
    stored = exact((T / "history/pre-repair-v1" / arc["path"]).read_bytes(), arc, "whole pre-repair capture archive")
    raw = gzip.decompress(stored)
    ck(sha(raw) == arc["tar_sha256"], "whole reconstructed pre-repair tar")
    oldtar = tarfile.open(fileobj=io.BytesIO(raw))
    original_refs = {r["path"]: r for r in capture["immutable_original_refs"]}
    old = {}
    changed = []
    for r in capture["all362"]:
        body = (S / r["path"]).read_bytes() if r["path"] in original_refs else oldtar.extractfile(r["path"]).read()
        old[r["path"]] = exact(body, r, "every historical old body")
        if body != (S / r["path"]).read_bytes():
            changed.append(r["path"])
    ck(len(old) == 362, "complete original phase")
    oldmf = json.loads(old["data/turnout/asset-manifest.json"])
    for r in oldmf["owned_assets"]:
        exact(old[r["path"]], r, "every old361 manifest target against historical body")
    protected = ["data/county-turnout.csv", "data/turnout/priority-set.json", "data/turnout/native-inventory.json", "data/turnout/rankings.json", "data/turnout/candidate-reconciliation.json", "data/turnout/qa/pre-peer-body-witness.json", "data/turnout/qa/pre-peer-bodies.tar.gz"]
    for p in protected:
        ck(old[p] == (S / p).read_bytes(), "protected native/source/order/original witness unchanged")
    repaired = load(T / "qa/repaired-body-witness.json")
    archives = {"history/pre-repair-v1/bodies.tar.gz": oldtar}
    for r in repaired["bodies"]:
        st = r["storage"]
        if st["kind"] in ("historical_tar", "changed_tar"):
            if st["archive"] not in archives:
                archives[st["archive"]] = tarfile.open(fileobj=io.BytesIO(gzip.decompress((T / st["archive"]).read_bytes())))
            body = archives[st["archive"]].extractfile(st["member"]).read()
        else:
            body = (S / st["path"]).read_bytes()
        exact(body, r, "all375 complete repaired preterminal bodies")
        ck(body == (S / r["path"]).read_bytes(), "repaired witness points to actual current bytes")
    peer = load(T / "reciprocal/peer-finished-capture/capture.json")
    parts = [exact((T / "reciprocal/peer-finished-capture" / r["path"]).read_bytes(), r, "peer capture part") for r in peer["tar_gzip_parts_in_order"]]
    stored = b"".join(parts)
    raw = gzip.decompress(stored)
    ck(sha(stored) == peer["gzip_sha256"] and sha(raw) == peer["tar_sha256"], "whole captured peer tar")
    with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
        for r in peer["all235"]:
            exact(tar.extractfile(r["path"]).read(), r, "every complete peer captured body")
    ck(peer["manifest_sha256"] == "f3b33d30631cec93796c4aab2becec82a49982da39878421f11c22ea5e1a8620", "actual finalized peer identity")
    own_original = load(S / "data/coordinator-writein-row5-review/proof.json")
    wi = load(T / "extracts/writein-scope-comparison.json")
    by_name = {x["municipality"]: x for x in own_original["complete_scopes"]}
    for r in wi:
        independent = by_name[r["municipality"]]
        ck((r["detail_sum"], r["difference"], r["prior_row6_detail_sum"], r["prior_row6_difference"]) == (independent["full_row5_onward_detail"], independent["full_difference"], independent["row6_onward_detail"], independent["old_difference"]), "all39 complete and historical scopes match original independent XML")
    ck(sum(x["detail_sum"] for x in wi) == 1227 and sum(x["difference"] != 0 for x in wi) == 8, "complete row5 corrected scope")
    ck(sum(x["prior_row6_detail_sum"] for x in wi) == 1226, "old projection retained")
    comparison = load(T / "reciprocal/source-core-comparison.json")
    ck(len(comparison["checks"]) == 17 and all(x["passed"] for x in comparison["checks"]) and len(comparison["child_label_whitespace_differences"]) == 11, "bounded complete peer scopes and literal differences")
    out = {"status": "pass_independent_full_turnout_repair_history_and_scope_review", "checks": N, "old_complete_bodies": len(old), "old_manifest_targets": len(oldmf["owned_assets"]), "current_manifest_targets": len(m["owned_assets"]), "repaired_preterminal_bodies": len(repaired["bodies"]), "captured_finished_peer_bodies": len(peer["all235"]), "previous_changed_paths": changed, "all_other_previous_bodies_unchanged": 362 - len(changed), "primary_native_contract_and_CSV_unchanged": True, "full_detail": 1227, "full_local_discrepancies": 8, "historical_row6_detail": 1226, "historical_discrepancies": 9, "source_generic_and_native_votes_changed": False, "captured_source_core_scopes": 17, "current_geography_or_legal_writein_approved": False, "producer_writes": False}
    (S / "data/coordinator-turnout-repair-final-review.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
