"""Coordinator arithmetic review using original counts and an event-slope solver."""
import collections
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / "baselines"
LABELS = ["2024-pres", "2020-senate", "2022-senate", "2022-governor"]


def rows(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as stream:
        return list(csv.DictReader(stream))


def close(actual, expected, tolerance=2e-7):
    assert math.isclose(float(actual), expected, rel_tol=2e-11, abs_tol=tolerance), (actual, expected)


def clipped(value):
    return min(1.0, max(0.0, value))


def solve(weights, shares, target):
    """Walk exact piecewise-linear intervals; independent of worker bisection."""
    events = collections.defaultdict(float)
    for weight, share in zip(weights, shares):
        if weight:
            events[-share] += 2*weight
            events[1-share] -= 2*weight
    total = sum(weights)
    ordered = sorted(events)
    left = ordered[0]
    net = -total
    slope = events[left]
    for right in ordered[1:]:
        next_net = net+slope*(right-left)
        if slope and net-1e-7 <= target <= next_net+1e-7:
            return left + (target-net)/slope
        net = next_net
        slope += events[right]
        left = right
    raise AssertionError((total, target, "no feasible interval"))


def main():
    originals = {}
    for label in LABELS:
        document = json.loads(gzip.decompress((HERE / "history-api" / f"history-{label}-granular-combined.body.gz").read_bytes()))["data"]["contestGranularData"]
        actual = {int(c["candidateId"]) for c in document["candidates"] if c["candidate"]["pseudocandidate"] in (None, "ALL_OTHER_CANDIDATES")}
        def visit(node, parents=()):
            path = parents + (node["division"]["id"],)
            raw = node["granularRow"]
            a = sum(r["votes"] for r in raw if r["candidateId"] in actual and r["partyId"] == 1)
            b = sum(r["votes"] for r in raw if r["candidateId"] in actual and r["partyId"] == 2)
            all_votes = sum(r["votes"] for r in raw if r["candidateId"] in actual)
            originals[label, "/".join(path)] = {"A": a, "B": b, "other": all_votes-a-b, "pair": a+b, "all": all_votes, "name": node["division"]["name"], "type": node["division"]["divisionTypeName"]}
            for child in node.get("children") or []:
                visit(child, path)
        visit(document["divisions"])
    county_by_label = {label: {v["name"]: v for (lab, key), v in originals.items() if lab == label and v["type"] == "County"} for label in LABELS}
    states = {(r["scenario"], r["target"]): r for r in rows(BASE / "state-scenarios.csv")}
    maximum_error = 0
    group_count = 0
    row_count = 0
    clipped_groups = 0
    for filename in ["county-targets.csv.gz", "native-targets.csv.gz"]:
        groups = collections.defaultdict(list)
        for row in rows(BASE / filename):
            groups[row["scenario"], row["target"]].append(row)
        for (scenario, target_name), group in groups.items():
            pref = group[0]["preference_anchor"]
            volume_basis = group[0]["volume_basis"]
            weights, shares, others = [], [], []
            for row in group:
                if filename.startswith("county"):
                    history = county_by_label[pref][row["county"]]
                    alternatives = [county_by_label[label][row["county"]] for label in LABELS]
                    if volume_basis in LABELS:
                        volume = county_by_label[volume_basis][row["county"]]
                    elif volume_basis == "low_historical_county_min":
                        volume = min(alternatives, key=lambda v: v["pair"])
                    else:
                        assert volume_basis == "high_historical_county_max"
                        volume = max(alternatives, key=lambda v: v["pair"])
                else:
                    # Source-native paths are read from the independent primary locator table.
                    leaf = native_lookup[pref, row["geography_key"]]
                    history = originals[pref, leaf["native_path"]]
                    volume = history
                for field, expected in [("historical_A", history["A"]), ("historical_B", history["B"]), ("historical_other", history["other"]), ("pair_pool", volume["pair"]), ("other_pool", volume["other"]), ("all_candidate_pool", volume["all"])]:
                    close(row[field], expected)
                share = history["A"] / history["pair"] if history["pair"] else 0.0
                if history["pair"]:
                    close(row["baseline_A_pair_share"], share)
                else:
                    assert row["baseline_A_pair_share"] == ""
                weights.append(volume["pair"])
                shares.append(share)
                others.append(volume["other"])
            total = sum(weights)
            net = sum(w*(2*s-1) for w, s in zip(weights, shares))
            target = 0.0 if target_name == "tie" else 0.01*total
            delta = solve(weights, shares, target)
            unbounded = (target-net)/(2*total)
            achieved = 0.0
            for row, w, s, other in zip(group, weights, shares, others):
                q = clipped(s+delta)
                expected_net = w*(2*q-1)
                for field, value in [("weight", w/total), ("baseline_net", w*(2*s-1)), ("bounded_shift_pp", 100*delta), ("unbounded_shift_pp", 100*unbounded), ("target_net", expected_net), ("share_pp1_unbounded_net_gain", .02*w), ("share_pp1_clipped_net_gain", 2*w*(clipped(s+.01)-s))]:
                    close(row[field], value)
                if w:
                    close(row["bounded_target_share"], q)
                    selected = (w+target-(net-w*(2*s-1)))/(2*w)
                    close(row["selected_required_share"], selected)
                else:
                    assert row["selected_status"] == "no_positive_pool"
                achieved += expected_net
                row_count += 1
            maximum_error = max(maximum_error, abs(achieved-target))
            assert abs(achieved-target) < 2e-6
            if any(w and not 0 <= s+unbounded <= 1 for w, s in zip(weights, shares)):
                clipped_groups += 1
            if filename.startswith("county"):
                state = states[scenario, target_name]
                close(state["bounded_shift_pp"], 100*delta)
                close(state["pair_pool"], total)
                close(state["A"], (total+target)/2)
                close(state["B"], (total-target)/2)
                close(state["other_pool"], sum(others))
            group_count += 1
    result = {"status": "pass_independent_original_counts_and_event_slope_solver", "state_scenarios": len(states), "groups": group_count, "target_rows": row_count, "groups_requiring_clipping": clipped_groups, "maximum_target_error_votes": maximum_error, "scope": "Historical conditional arithmetic; no current candidate/geographic approval or calibrated forecast."}
    (HERE / "coordinator-target-review.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    json_contract = json.loads((HERE / "turnout/priority-set.json").read_bytes())
    native_lookup = {(label, leaf["geography_key"]): leaf for county in json_contract["counties"] for label, leaves in county["historical_constituents"].items() for leaf in leaves}
    main()
