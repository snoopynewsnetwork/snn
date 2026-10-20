"""Coordinator independent original fixed-width, native and bounded-math review."""
from pathlib import Path
import collections
import csv
import gzip
import hashlib
import io
import json
import math
import zipfile

S = Path(__file__).resolve().parents[1]
B = S / "data/baselines"
N = 0


def sha(b):
    return hashlib.sha256(b).hexdigest()


def ck(ok, why):
    global N
    N += 1
    if not ok:
        raise AssertionError(why)


def close(a, b, why, tol=2e-7):
    ck(math.isclose(a, b, abs_tol=tol, rel_tol=2e-11), why)


def load(path):
    return json.loads(path.read_bytes())


def gzrows(path):
    return [json.loads(x) for x in gzip.decompress(path.read_bytes()).splitlines()]


def independent_root(rows, goal):
    positive = [r for r in rows if r["pair_volume"] > 0]
    knots = sorted({-1., 1.} | {-r["a_share"] for r in positive} | {1 - r["a_share"] for r in positive})
    def net(d):
        return math.fsum(r["pair_volume"] * (2 * min(1., max(0., r["a_share"] + d)) - 1) for r in positive)
    for left, right in zip(knots, knots[1:]):
        nl, nr = net(left), net(right)
        if nl - 1e-8 <= goal <= nr + 1e-8 and nr > nl:
            return left + (right - left) * (goal - nl) / (nr - nl)
    raise AssertionError("piecewise root unavailable")


def main():
    manifest = load(B / "asset-manifest.json")
    ck(sha((B / "asset-manifest.json").read_bytes()) == "f3b33d30631cec93796c4aab2becec82a49982da39878421f11c22ea5e1a8620", "actual final baseline manifest pin")
    targets = manifest["owned_assets"]
    actual = {str(p.relative_to(S)) for p in B.rglob("*") if p.is_file()} | {"county-partisanship.md", "data/county-baselines.csv"}
    ck(len(targets) == 234 and actual == {r["path"] for r in targets} | {"data/baselines/asset-manifest.json"}, "complete self-only manifest")
    for r in targets:
        body = (S / r["path"]).read_bytes()
        ck(len(body) == r["bytes"] < 40000000 and sha(body) == r["sha256"], "exact owned body " + r["path"])
    inputs = load(B / "source/inputs.json")
    original = {}
    for r in inputs:
        stored = (S / r["body_path"]).read_bytes()
        raw = gzip.decompress(stored)
        ck(sha(stored) == r["stored_sha256"] and sha(raw) == r["raw_sha256"] and len(raw) == r["raw_bytes"], "entire original entity " + r["id"])
        original[r["id"]] = raw
    ck(len(inputs) == 148, "all fixed original receipts")
    saved = {(r["input"], r["member"], r["byte_start"]): r for r in gzrows(B / "witness/root-selected.jsonl.gz")}
    ck(len(saved) == 12997, "complete unique selected-root records")
    fields = [("contest_code", 0, 4), ("candidate_code", 4, 7), ("source_code", 7, 11), ("party", 101, 104), ("district_type_id", 104, 107), ("district_code", 107, 111), ("contest_title", 111, 167), ("candidate_name", 167, 205), ("source_name", 205, 235), ("district_name", 235, 260), ("votes_allowed", 260, 262), ("referendum_flag", 262, 263)]
    selected, raw_groups = {}, collections.defaultdict(list)
    for year, ident in [(2024, "ri-2024-layout-zip"), (2020, "ri-2020-observed-long-zip"), (2022, "ri-2022-observed-long-zip")]:
        arc = zipfile.ZipFile(io.BytesIO(original[ident]))
        ck(arc.testzip() is None, "complete ZIP CRC " + ident)
        member = next(n for n in arc.namelist() if "/" not in n and n.lower().endswith((".txt", ".asc")))
        offset = 0
        for line, rawline in enumerate(arc.read(member).splitlines(keepends=True), 1):
            b = rawline.rstrip(b"\r\n")
            title = b[111:167].decode("latin1").strip()
            if title in (["Governor"] if year == 2022 else ["Presidential Electors For:", "Senator in Congress"]):
                key = ident, member, offset
                r = saved[key]
                ck(r["year"] == year and r["line"] == line and r["byte_end"] == offset + len(rawline) and r["raw_record"] == b.decode("latin1") and r["raw_line_sha256"] == sha(rawline), "whole raw original/source positions")
                for name, lo, hi in fields:
                    ck(r[name] == b[lo:hi].decode("latin1"), "literal source field " + name)
                values = [int(b[i:i + 6]) for i in range(11, 101, 6)]
                ck(r["votes"] == values[0] == sum(values[1:]) and r["methods"] == values[1:], "all fourteen original method slots")
                selected[key] = r
                raw_groups[year, title, r["source_code"]].append(r)
            offset += len(rawline)
    ck(set(selected) == set(saved), "no omitted or added original candidate records")
    natives = gzrows(B / "extracts/native-baselines.jsonl.gz")
    ck(len(natives) == 2460, "all native inventories across five contests")
    observed = 0
    for r in natives:
        cr = raw_groups[r["year"], r["contest"], r["source_code"]]
        ck(r["observed"] == bool(cr), "observed versus absent source")
        if not cr:
            ck(all(r[k] is None for k in ["A_votes", "B_votes", "pair_votes", "all_reported_votes", "source_anchor", "source_unit_key", "methods"]), "unavailable preserves nulls")
            continue
        observed += 1
        a = sum(x["votes"] for x in cr if x["party"].strip() == "DEM")
        b = sum(x["votes"] for x in cr if x["party"].strip() == "REP")
        f = sum(x["votes"] for x in cr)
        ck((r["A_votes"], r["B_votes"], r["pair_votes"], r["all_reported_votes"], r["other_reported_votes"]) == (a, b, a + b, f, f - a - b), "independent native full candidate vector")
        ck(r["methods"] == [sum(x["methods"][i] for x in cr) for i in range(14)], "native full method vector")
        ck(len(r["candidates"]) == len(cr), "all candidate objects")
        for c, raw in zip(r["candidates"], cr):
            ck(c == {"candidate_code": raw["candidate_code"], "name_raw": raw["candidate_name"], "party_raw": raw["party"], "votes": raw["votes"], "methods": raw["methods"], "line": raw["line"], "byte_start": raw["byte_start"], "byte_end": raw["byte_end"]}, "entire candidate literal/control/position object")
    ck(observed == 2378, "complete observed five-contest universes")
    parents = load(B / "extracts/parent-baselines.json")
    for p in parents:
        children = [r for r in natives if r["election"] == p["election"] and r["parent_key"] == p["parent_key"]]
        ck(p["all_child_codes"] == [r["source_code"] for r in children], "every ordered child inventory")
        obs = [r for r in children if r["observed"]]
        ck(p["children"] == [r["source_unit_key"] for r in obs], "every ordered observed child key")
        if obs:
            ck(all(p[k] == sum(r[k] for r in obs) for k in ["A_votes", "B_votes", "pair_votes", "all_reported_votes"]), "all parent candidate controls")
    nm = {r["source_unit_key"]: r for r in natives if r["observed"]}
    max_residual = 0.
    max_shift = 0.
    unit_count = 0
    result_lookup = {}
    for path in sorted((B / "scenarios").glob("*.input.json")):
        inp = load(path)
        result = load(path.with_name(path.name.replace(".input.", ".result.")))
        units = inp["units"]
        T = math.fsum(u["pair_volume"] for u in units)
        F = math.fsum(u["all_volume"] for u in units)
        base = math.fsum(u["pair_volume"] * (2 * u["a_share"] - 1) for u in units if u["pair_volume"])
        goal = inp["target_margin"] * T
        delta = independent_root(units, goal)
        max_shift = max(max_shift, abs(delta - result["uniform_share_shift"]))
        close(result["uniform_share_shift"], delta, "independent piecewise clipped root", 1e-12)
        close(result["unbounded_share_shift"], (goal - base) / (2 * T), "uniform unclipped algebra", 1e-12)
        close(result["pair_denominator"], T, "full pair volume")
        close(result["all_candidate_denominator"], F, "full all-candidate volume")
        close(sum(x["pair_weight"] for x in result["units"]), 1, "all native pair weights", 1e-12)
        for u, x in zip(units, result["units"]):
            source = nm[u["key"]]
            ck(source["A_pair_share"] == u["a_share"], "declared source preference remains original")
            if "historical-mix" not in path.name:
                ck((u["pair_volume"], u["all_volume"]) == (source["pair_votes"], source["all_reported_votes"]), "own-electorate original volumes")
            t, q = u["pair_volume"], u["a_share"]
            ck(x["key"] == u["key"], "every unit retained in original scenario order")
            s = min(1., max(0., q + delta)) if q is not None else None
            ck(x["target_a_share"] is None if s is None else math.isclose(x["target_a_share"], s, abs_tol=1e-12), "bounded target share")
            close(x["target_net_votes"], t * (2 * s - 1) if s is not None else 0, "native net contribution")
            rest = base - (t * (2 * q - 1) if t else 0)
            raw = (goal - rest + t) / (2 * t) if t else None
            got = x["selected_only"]["raw_required_share"]
            ck(got is None if raw is None else math.isclose(got, raw, abs_tol=1e-8, rel_tol=2e-11), "selected-only fixed-rest algebra")
            close(x["plus1_share_point_net_vote_gain"], .02 * t, "share point versus margin points")
            unit_count += 1
        net = math.fsum(x["target_net_votes"] for x in result["units"])
        close(net, goal, "full bounded net target")
        max_residual = max(max_residual, abs(net - goal))
        result_lookup[path.name.removesuffix(".input.json")] = result
    ck(len(result_lookup) == 16 and unit_count == 7504, "all published historical scenarios and every native target")
    csv_rows = list(csv.DictReader((B / "native-targets.csv").open()))
    ck(len(csv_rows) == unit_count, "complete target CSV rows")
    for r in csv_rows:
        result = result_lookup[r["scenario"] + "-" + r["target"]]
        x = next(x for x in result["units"] if x["key"] == r["key"])
        for key in ["pair_volume", "all_volume", "target_net_votes", "net_vote_gain", "plus1_share_point_net_vote_gain"]:
            close(float(r[key]), x[key], "target CSV arithmetic " + key)
    result = {"status": "pass_independent_original_native_and_scenario_review", "checks": N, "exact_owned_targets": len(targets), "complete_original_inputs": len(inputs), "full_selected_original_records": len(selected), "all_native_inventory_rows": len(natives), "observed_native_contest_rows": observed, "complete_native_target_rows": unit_count, "full_state_scenarios": len(result_lookup), "maximum_independent_shift_difference": max_shift, "maximum_net_target_residual_votes": max_residual, "legal_current_or_coordinator_priority_approved": False, "scope": "Original fixed-width candidates/raw padded fields/14 methods/positions, full null/native/parent controls, independent piecewise bounded math and selected-only algebra; no producer import/writer or calibration claim."}
    (S / "data/coordinator-baseline-final-review.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
