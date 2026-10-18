"""Independent coordinator check of original historical bytes and dispatch scope.

Uses no worker parser. This review does not approve current geographic joins.
"""
import collections
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

HERE = Path(__file__).resolve().parent
TURNOUT = HERE / "turnout"
LABELS = ["2024-pres", "2020-senate", "2022-senate", "2022-governor"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pointer(value, path):
    for key in path.lstrip("/").split("/"):
        key = key.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def walk(node, path="/data/contestGranularData/divisions", parents=()):
    native_path = parents + (node["division"]["id"],)
    yield path, native_path, node
    for ordinal, child in enumerate(node.get("children") or []):
        yield from walk(child, f"{path}/children/{ordinal}", native_path)


def read_csv(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="") as stream:
        return list(csv.DictReader(stream))


def as_text(value):
    return "" if value is None else str(value)


def audit():
    contract_bytes = (TURNOUT / "priority-set.json").read_bytes()
    contract = json.loads(contract_bytes)
    sources = {}
    source_checks = []
    for source_id, observation in contract["source_observations"].items():
        stored = (TURNOUT / observation["body_path"]).read_bytes()
        assert len(stored) == observation["stored_bytes"] < 40_000_000
        assert sha(stored) == observation["stored_sha256"], source_id
        original = gzip.decompress(stored)
        assert len(original) == observation["original_bytes"]
        assert sha(original) == observation["original_sha256"], source_id
        metadata = json.loads((TURNOUT / observation["metadata_path"]).read_bytes())
        for key in ["original_sha256", "original_bytes", "stored_sha256", "stored_bytes"]:
            assert metadata[key] == observation[key], (source_id, key)
        assert metadata["requested_url"] == observation["requested_url"]
        sources[source_id] = json.loads(original)
        source_checks.append({"source_id": source_id, "original_sha256": sha(original)})

    census_meta = json.loads((TURNOUT / "source/census-county.meta.json").read_bytes())
    census_stored = (TURNOUT / "source/census-county.body.gz").read_bytes()
    assert sha(census_stored) == census_meta["stored_sha256"]
    census_bytes = gzip.decompress(census_stored)
    assert sha(census_bytes) == census_meta["original_sha256"]
    fips = {
        r["COUNTYNAME"].removesuffix(" County"): r["STATEFP"] + r["COUNTYFP"]
        for r in csv.DictReader(io.StringIO(census_bytes.decode()), delimiter="|")
        if r["STATE"] == "SC"
    }
    assert len(fips) == 46
    nodes = {}
    candidates = {}
    expected_positions = collections.Counter()
    expected_county = {}
    expected_leaf_keys = collections.defaultdict(set)
    rollup_residuals = []
    for label in LABELS:
        combined = sources[label + "-combined"]["data"]["contestGranularData"]
        candidates[label] = {int(r["candidateId"]): r for r in combined["candidates"]}
        actual_ids = {
            key for key, row in candidates[label].items()
            if row["candidate"]["pseudocandidate"] in (None, "ALL_OTHER_CANDIDATES")
        }
        for scope in ["combined", "methods"]:
            document = sources[f"{label}-{scope}"]
            root = document["data"]["contestGranularData"]["divisions"]
            for path, native_path, node in walk(root):
                nodes[label, scope, path] = (native_path, node)
                expected_positions[label, scope] += len(node["granularRow"])
                assert len({(r["candidateId"], r["partyId"], r["voteChannelId"]) for r in node["granularRow"]}) == len(node["granularRow"])
                if scope == "combined" and len(native_path) == 2:
                    name = node["division"]["name"]
                    assert name in fips
                    total = sum(r["votes"] for r in node["granularRow"] if r["candidateId"] in actual_ids)
                    expected_county[label, fips[name]] = (node, total, path)
                if scope == "combined" and len(native_path) == 3:
                    expected_leaf_keys[label].add(path)
                if node.get("children"):
                    for cell in node["granularRow"]:
                        key = (cell["candidateId"], cell["partyId"], cell["voteChannelId"])
                        parts = [next((r["votes"] for r in c["granularRow"] if (r["candidateId"], r["partyId"], r["voteChannelId"]) == key), None) for c in node["children"]]
                        if cell["votes"] is not None and all(v is not None for v in parts):
                            residual = cell["votes"] - sum(parts)
                            if residual:
                                rollup_residuals.append({"contest": label, "scope": scope, "source_pointer": path, "key": key, "difference": residual})
        assert contract["source_state_divisions"][label] == combined["divisions"]["division"]

    seen = set()
    position_count = 0
    with gzip.open(TURNOUT / "extracts/source-positions.jsonl.gz", "rt") as stream:
        for line in stream:
            record = json.loads(line)
            label, scope, path = record["contest_label"], record["observation_scope"], record["source_pointer"]
            ordinal = record["raw_ordinal"]
            node_path = path.rsplit("/granularRow/", 1)[0]
            native_path, node = nodes[label, scope, node_path]
            key = label, scope, path
            assert key not in seen
            seen.add(key)
            assert path == f"{node_path}/granularRow/{ordinal}"
            assert record["division_path"] == list(native_path)
            assert record["division"] == node["division"]
            assert record["raw_value"] == node["granularRow"][ordinal]
            position_count += 1
    assert position_count == sum(expected_positions.values()) == 516586

    units = read_csv(TURNOUT / "extracts/native-units.csv.gz")
    assert len(units) == 9823
    unit_seen = set()
    for row in units:
        label, path = row["contest_label"], row["source_pointer"]
        native_path, node = nodes[label, "combined", path]
        key = label, path
        assert key not in unit_seen
        unit_seen.add(key)
        assert json.loads(row["raw_division"]) == node["division"]
        assert row["native_division_path"] == "/".join(native_path)
        raw_cells = [{"candidate_id": r["candidateId"], "party_id": r["partyId"], "method_id": r["voteChannelId"], "votes": r["votes"]} for r in node["granularRow"]]
        assert json.loads(row["raw_candidate_cells"]) == raw_cells
    assert unit_seen == {(label, path) for label, scope, path in nodes if scope == "combined"}

    csv_rows = read_csv(HERE / "county-turnout.csv")
    assert len(csv_rows) == 46
    csv_by_fips = {r["county_fips"]: r for r in csv_rows}
    fields_compared = 0
    for (label, county_fips), (node, total, path) in expected_county.items():
        row = csv_by_fips[county_fips]
        assert row["county"] == node["division"]["name"]
        assert row["native_county_id"] == node["division"]["id"]
        prefix = label.replace("-", "_")
        assert int(row[prefix + "_candidate_votes"]) == total
        for cell in node["granularRow"]:
            field = f"{prefix}_c{cell['candidateId']}_p{cell['partyId']}"
            assert row[field] == as_text(cell["votes"]), (county_fips, field)
            fields_compared += 1

    historical_count = 0
    vhm_count = 0
    contract_leaves = collections.defaultdict(set)
    for county in contract["counties"]:
        county_fips = county["county_fips"]
        assert fips[county["name"]] == county_fips
        for label, leaves in county["historical_constituents"].items():
            node, county_total, county_path = expected_county[label, county_fips]
            assert len(leaves) == len(node.get("children") or [])
            actual_ids = {cid for cid, c in candidates[label].items() if c["candidate"]["pseudocandidate"] in (None, "ALL_OTHER_CANDIDATES")}
            for leaf in leaves:
                path = leaf["source_pointer"]
                native_path, original = nodes[label, "combined", path]
                assert path.startswith(county_path + "/children/")
                assert leaf["raw_division"] == original["division"]
                assert leaf["native_path"] == "/".join(native_path)
                assert leaf["native_id"] == original["division"]["id"]
                assert leaf["combined_source_ref"] == label + "-combined"
                assert leaf["method_source_ref"] == label + "-methods"
                assert leaf["method_source_pointer"] == path
                assert leaf["candidate_votes"] == sum(r["votes"] for r in original["granularRow"] if r["candidateId"] in actual_ids)
                assert path not in contract_leaves[label]
                contract_leaves[label].add(path)
                historical_count += 1
        for year, records in county["voter_history_constituents"].items():
            for record in records:
                original = pointer(sources[record["source_id"]], record["source_pointer"])
                assert record["raw_identity"] == {key: original[key] for key in ["county", "precinct", "precinctCode", "isSummary"]}
                assert record["native_name"] == original["precinct"]
                assert record["precinct_code"] == original["precinctCode"]
                assert record["total_registered"] == original["totalRegistered"]
                assert record["total_participating"] == original["totalVoting"]
                vhm_count += 1
    assert dict(contract_leaves) == dict(expected_leaf_keys)
    assert historical_count == 9635
    assert vhm_count == 7078

    registration = read_csv(TURNOUT / "extracts/registration-participation.csv.gz")
    registration_seen = set()
    for row in registration:
        source_id, path = row["source_id"], row["source_pointer"]
        key = source_id, path
        assert key not in registration_seen
        registration_seen.add(key)
        original = pointer(sources[source_id], path)
        for field, source_field in [("total_registered", "totalRegistered"), ("raw_total_voting", "totalVoting"), ("source_percent_voting", "percentVoting"), ("precinct", "precinct"), ("precinct_code", "precinctCode"), ("is_summary", "isSummary")]:
            assert row[field] == as_text(original[source_field]), (source_id, path, field)
        query_county = parse_qs(urlsplit(contract["source_observations"][source_id]["requested_url"]).query).get("county", [None])[0]
        expected_county_name = original["county"] if query_county is None else query_county
        assert row["county"].upper() == as_text(expected_county_name).upper()
        expected_participating = as_text(original["totalVoting"]) if row["data_type"] == "VOT" else ""
        assert row["total_participating"] == expected_participating
    expected_vhm = {(sid, f"/voterHistoryResults/countyPrecinctResults/{i}") for sid, doc in sources.items() if sid.startswith("vhm-") for i in range(len(doc["voterHistoryResults"]["countyPrecinctResults"]))}
    assert registration_seen == expected_vhm
    assert len(registration) == 7500

    ranked = sorted([(fips, total, node["division"]["name"]) for (label, fips), (node, total, path) in expected_county.items() if label == "2024-pres"], key=lambda r: (-r[1], r[2]))
    total = sum(r[1] for r in ranked)
    cumulative = 0
    minimum = None
    for rank, (county_fips, votes, name) in enumerate(ranked, 1):
        cumulative += votes
        row = csv_by_fips[county_fips]
        assert int(row["rank_2024_pres"]) == rank
        assert int(row["votes_2024_pres"]) == votes
        assert int(row["cumulative_2024_pres"]) == cumulative
        if minimum is None and cumulative * 5 >= total * 4:
            minimum = rank
    keys = ["SC:" + r[0] for r in ranked]
    top15 = sum(r[1] for r in ranked[:15])
    priority_votes = sum(r[1] for r in ranked[:minimum])
    assert contract["ordered_keys"] == keys
    assert contract["priority_keys"] == keys[:minimum]
    assert contract["remainder_keys"] == keys[minimum:]
    assert (total, top15, minimum, priority_votes) == (2548140, 1974167, 17, 2061601)
    assert sum(r[1] for r in ranked[:minimum - 1]) == 2019337
    assert ranked[minimum - 1] == ("45073", 42264, "Oconee")
    assert contract["coordinator_acceptance_path"] == "data/coordinator-priority-acceptance.json"
    result = {
        "status": "pass_original_review_not_current_geographic_approval",
        "contract_sha256": sha(contract_bytes), "contract_bytes": len(contract_bytes),
        "source_entities": len(source_checks), "sources": source_checks,
        "original_source_positions": position_count, "original_hierarchy_nodes": len(units),
        "historical_leaf_objects": historical_count, "vhm_leaf_objects": vhm_count,
        "vhm_source_positions": len(registration), "county_candidate_cells": fields_compared,
        "county_count": 46, "denominator": total, "top15": top15,
        "minimum80_count": minimum, "minimum80_votes": priority_votes,
        "previous_votes": 2019337, "crossing_fips": "45073", "priority_keys": keys[:minimum],
        "method_hierarchy_residuals": rollup_residuals,
        "limitations": ["Historical DB precincts, VHM requested-county history labels and current physical/election reporting units have no approved crosswalk.", "Raw status flags and pseudo-options remain original; this review does not establish certification chronology or November publication admission."]
    }
    output = HERE / "coordinator-native-review.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in ["sources", "method_hierarchy_residuals", "priority_keys"]}, indent=2))


if __name__ == "__main__":
    audit()
