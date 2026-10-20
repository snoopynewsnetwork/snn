"""Coordinator actual CLI cases; no producer writes or imported calculator code."""
from pathlib import Path
import copy
import json
import math
import os
import subprocess
import sys
import tempfile

S = Path(__file__).resolve().parents[1]
C = S / "data/baselines/scripts/calculate.py"


def main():
    live = {"mode": "live", "pair": {"A": "a", "B": "b"}, "candidate_universe_complete": True, "target_margin": 0, "selected_unit": "x", "units": [{"key": "x", "counted": {"A": 80, "B": 120, "others": {"c": 10}}, "remaining": 100, "pair_participation": .8, "a_share": .7, "other_shares": {"c": 1}}, {"key": "y", "counted": {"A": 20, "B": 10, "others": {"c": 5}}, "remaining": 50, "pair_participation": .6, "a_share": .4, "other_shares": {"c": 1}}]}
    hist = {"mode": "historical", "pair": {"A": "a", "B": "b"}, "candidate_universe_complete": True, "target_margin": .01, "units": [{"key": "x", "pair_volume": 100, "all_volume": 110, "a_share": 1, "others": {"c": 10}}, {"key": "y", "pair_volume": 100, "all_volume": 100, "a_share": 0}], "selected_unit": "x"}
    cases = []

    def add(name, data, rc, status, checks=None):
        cases.append((name, copy.deepcopy(data), rc, status, checks or {}))

    add("known_counted_plus_remainder", live, 0, "calculated", {"forecast_A": 168, "forecast_B": 172, "final_pair_denominator": 340, "final_all_candidate_denominator": 395})
    add("bounded_historical_clipping", hist, 0, "solved", {"final_net_votes": 2})
    h = copy.deepcopy(hist)
    h["units"][0]["a_share"] = None
    add("unknown_historical_preference", h, 0, "unknown_preference")
    h = copy.deepcopy(live)
    h["units"][1]["a_share"] = None
    add("unknown_other_remaining_preference", h, 0, "unknown_preference")
    h = copy.deepcopy(live)
    for r in h["units"]:
        r["remaining"] = 0
    add("all_counted_no_pool", h, 0, "no_positive_pool", {"forecast_A": 100, "forecast_B": 130})
    h = copy.deepcopy(live)
    h["units"][0]["counted"]["A"] = 500
    add("secured_pool_requirement", h, 0, "calculated")
    h = copy.deepcopy(live)
    h["units"][0]["counted"]["B"] = 800
    add("impossible_pool_requirement", h, 0, "calculated")
    h = copy.deepcopy(live)
    h["units"][0]["counted"]["A"] = 300
    h["units"][0]["counted"]["others"]["c"] = 1000
    add("pair_leader_loses_full_field", h, 0, "calculated")
    for value in [None, True, "0", -1.00001, 1.00001, float("nan"), float("inf"), -float("inf")]:
        for mode, data in [("live", live), ("historical", hist)]:
            h = copy.deepcopy(data)
            h["target_margin"] = value
            add(mode + "_invalid_target_" + repr(value), h, 2, "invalid_input")
    for value in ["", "   ", None, 5, False]:
        h = copy.deepcopy(live)
        h["units"][1]["key"] = value
        h["units"][0]["a_share"] = None
        h.pop("selected_unit")
        add("global_bad_key_before_unknown_" + repr(value), h, 2, "invalid_input")
    h = copy.deepcopy(live)
    h["units"][1]["key"] = "x"
    h["units"][0]["a_share"] = None
    h.pop("selected_unit")
    add("global_duplicate_before_unknown", h, 2, "invalid_input")
    for field, values in [("remaining", [-1, None, True, "5", float("inf")]), ("pair_participation", [-.01, 1.01, False, None]), ("a_share", [-.01, 1.01, True, "0.5"])]:
        for value in values:
            h = copy.deepcopy(live)
            h["units"][0][field] = value
            add("invalid_" + field + "_" + repr(value), h, 2, "invalid_input")
    h = copy.deepcopy(live)
    h["units"][0]["other_shares"] = {"c": .5}
    add("unallocated_positive_other_pool", h, 2, "invalid_input")
    h = copy.deepcopy(live)
    h["units"][0]["counted"]["A"] = -1
    add("negative_counted_votes", h, 2, "invalid_input")
    h = copy.deepcopy(hist)
    h["units"][0]["all_volume"] = 99
    add("pair_larger_than_all", h, 2, "invalid_input")
    h = copy.deepcopy(live)
    h["selected_unit"] = "absent"
    add("missing_selected_key", h, 2, "invalid_input")
    evidence = []
    with tempfile.TemporaryDirectory(prefix="ri-coordinator-cli-") as tmp:
        for i, (name, data, rc, status, expected) in enumerate(cases):
            path = Path(tmp) / (str(i) + ".json")
            path.write_text(json.dumps(data, allow_nan=True))
            run = subprocess.run([sys.executable, "-B", "-S", str(C), str(path)], capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=20)
            out = json.loads(run.stdout, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
            assert run.returncode == rc and out["status"] == status and not run.stderr, (name, run.returncode, run.stderr, out)
            for key, value in expected.items():
                assert math.isclose(out[key], value, abs_tol=1e-8), (name, key, out[key], value)
            if name == "secured_pool_requirement":
                assert out["pooled_tie_or_margin_requirement"]["status"] == "secured"
            if name == "impossible_pool_requirement":
                assert out["pooled_tie_or_margin_requirement"]["status"] == "impossible"
            if name == "pair_leader_loses_full_field":
                assert out["forecast_A"] > out["forecast_B"] and out["fullfield"]["full_field_result"] == "A_not_strict_plurality"
            if name == "bounded_historical_clipping":
                assert out["clipped_keys"] and abs(out["uniform_share_shift"] - out["unbounded_share_shift"]) > 1e-4
            evidence.append({"case": name, "input_text": path.read_text(), "returncode": run.returncode, "stderr": run.stderr, "output": out})
    proof = {"status": "pass_actual_CLI_arithmetic_and_input_review", "actual_cases": len(evidence), "producer_writes": False, "cases": evidence}
    (S / "data/coordinator-baseline-cli-review.json").write_text(json.dumps(proof, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: v for k, v in proof.items() if k != "cases"}))


if __name__ == "__main__":
    main()
