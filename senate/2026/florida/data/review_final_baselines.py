"""Read-only independent manifest and final-denominator arithmetic review."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual, expected):
    assert actual is not None and math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-8), (actual, expected)


manifest_checks = []
for folder, report, csv_path in [
    ("turnout", "turnout.md", "data/county-turnout.csv"),
    ("baselines", "county-partisanship.md", "data/county-baselines.csv"),
]:
    directory = ROOT / "data" / folder
    manifest_path = directory / "asset-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    entries = manifest["assets"] if folder == "turnout" else manifest["owned"]
    expected = {str(p.relative_to(ROOT)) for p in directory.rglob("*") if p.is_file() and p != manifest_path}
    expected.update([report, csv_path])
    assert len(entries) == len({row["path"] for row in entries})
    assert expected == {row["path"] for row in entries}
    for row in entries:
        path = ROOT / row["path"]
        assert path.stat().st_size == row["bytes"] < 40000000
        assert sha(path) == row["sha256"], str(path)
        assert "__pycache__" not in path.parts and path.suffix != ".pyc"
    manifest_checks.append({"path": str(manifest_path.relative_to(ROOT)), "sha256": sha(manifest_path), "files": len(entries), "largest_bytes": max(row["bytes"] for row in entries)})

inputs_path = ROOT / "data/baselines/synthetic-live-inputs.json"
outputs_path = ROOT / "data/baselines/synthetic-live-results.json"
inputs = json.loads(inputs_path.read_text())
outputs = json.loads(outputs_path.read_text())
assert len(inputs) == len(outputs) == 15
expected_status = {
    "unknown_pool": "unknown_remaining_pool", "negative_pool": "invalid_remaining_pool",
    "no_pool_lost": "no_pool", "unknown_preference": "unknown_remaining_preference",
    "impossible": "calculated", "clipped_high": "calculated", "clipped_low": "calculated",
    "no_positive_pair_pool": "calculated", "secured": "calculated", "no_pool_tie": "no_pool",
    "all_zero": "no_pool", "other_wins": "calculated", "selected_pool_final_all_denominator": "calculated",
    "unknown_other_identity": "unknown_other_candidate_allocation",
    "invalid_negative_counted": "invalid_negative_or_nonfinite_counted",
}
checked = []
for case, result in zip(inputs, outputs):
    assert case["id"] == result["id"] and result["status"] == expected_status[case["id"]]
    assert result["counted_fixed"] == case["counted"]
    if case["id"] in ("unknown_pool", "negative_pool", "invalid_negative_counted"):
        checked.append({"id": case["id"], "status": result["status"]})
        continue
    counted = case["counted"]
    a, b = case["A"], case["B"]
    pools = case["remaining"]
    pair_pool = math.fsum(p["contest_votes"] * p["pair_fraction"] for p in pools)
    final_all = math.fsum(counted.values()) + math.fsum(p["contest_votes"] for p in pools)
    final_pair = counted[a] + counted[b] + pair_pool
    target = case.get("target_margin_pp", 0) / 100 * (final_all if case.get("target_denominator") == "all" else final_pair)
    close(result["final_denominator"], final_all)
    close(result["final_pair_denominator"], final_pair)
    close(result["target_net_votes"], target)
    if pair_pool:
        # Fixed counted net plus remaining pair net must equal the FINAL target.
        required = (target - counted[a] + counted[b] + pair_pool) / (2 * pair_pool)
        close(result["required_A_pair_share"], required)
        close(result["required_A_pair_share_clipped"], min(1, max(0, required)))
    else:
        assert result["required_A_pair_share"] is None and result["threshold_status"] == "no_positive_pool"
    if case["id"] in ("unknown_preference", "unknown_other_identity"):
        assert result["projected_candidates"] is None and result["legal_plurality_outcome"] == "unknown"
        checked.append({"id": case["id"], "status": result["status"]})
        continue
    projected = dict(counted)
    for p in pools:
        pair = p["contest_votes"] * p["pair_fraction"]
        share = min(1, max(0, p["A_pair_share"])) if p["A_pair_share"] is not None else 0.5
        projected[a] += pair * share
        projected[b] += pair * (1 - share)
        for candidate, fraction in p.get("other_allocation", {}).items():
            projected[candidate] = projected.get(candidate, 0) + (p["contest_votes"] - pair) * fraction
    assert set(projected) == set(result["projected_candidates"])
    for candidate, votes in projected.items():
        close(result["projected_candidates"][candidate], votes)
    close(math.fsum(projected.values()), final_all)
    max_votes = max(projected.values())
    winners = [name for name, votes in projected.items() if abs(votes - max_votes) < 1e-8]
    outcome = "no_votes" if final_all == 0 else "tie_requires_legal_resolution" if len(winners) > 1 else winners[0]
    assert outcome == result["legal_plurality_outcome"]
    if case.get("selected_pool"):
        selected = next(p for p in pools if p["id"] == case["selected_pool"])
        selected_pair = selected["contest_votes"] * selected["pair_fraction"]
        fixed_a, fixed_b = counted[a], counted[b]
        for p in pools:
            if p is selected:
                continue
            pair = p["contest_votes"] * p["pair_fraction"]
            share = min(1, max(0, p["A_pair_share"]))
            fixed_a += pair * share
            fixed_b += pair * (1 - share)
        pair_requirement = (target - fixed_a + fixed_b + selected_pair) / (2 * selected_pair)
        close(result["selected_only"]["required_share_unbounded"], pair_requirement)
        third_requirements = {name: (votes - fixed_a) / selected_pair for name, votes in projected.items() if name not in (a, b)}
        for name, value in third_requirements.items():
            close(result["selected_only"]["required_share_to_tie_each_other"][name], value)
        close(result["selected_only"]["plurality_required_share_unbounded"], max([pair_requirement] + list(third_requirements.values())))
    checked.append({"id": case["id"], "status": result["status"], "final_all_candidate_denominator": final_all, "plurality_outcome": outcome})

review = {
    "status": "pass", "manifest_checks": manifest_checks,
    "live_inputs": {"path": str(inputs_path.relative_to(ROOT)), "sha256": sha(inputs_path)},
    "live_outputs": {"path": str(outputs_path.relative_to(ROOT)), "sha256": sha(outputs_path)},
    "independent_live_cases": checked,
    "scope": "Independent algebra and exact manifests only. Synthetic contest votes and assumed pools do not estimate actual outstanding votes or win probabilities.",
}
(ROOT / "data/coordinator-final-baseline-review.json").write_text(json.dumps(review, indent=2) + "\n")
print(json.dumps({"status": "pass", "manifest_files": sum(x["files"] for x in manifest_checks), "independent_live_cases": len(checked)}))
