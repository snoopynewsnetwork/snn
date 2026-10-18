"""Independent original ENR XML/JSON position and native-scope audit."""
import collections
import gzip
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TURNOUT = HERE / "turnout"


def sha(value):
    return hashlib.sha256(value).hexdigest()


def json_pointer(value, path):
    for key in path.lstrip("/").split("/"):
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def xml_pointer(root, path):
    parts = path.lstrip("/").split("/")
    assert parts.pop(0) == root.tag
    node = root
    for part in parts:
        match = re.fullmatch(r"([^\[]+)(?:\[(\d+)\])?", part)
        tag, ordinal = match.groups()
        node = list(node)[int(ordinal)] if ordinal is not None else node.find(tag)
        assert node is not None and node.tag == tag, path
    return node


def originals(observations, is_xml):
    result = {}
    pins = []
    for source_id, observation in observations.items():
        stored = (TURNOUT / observation["body_path"]).read_bytes()
        assert sha(stored) == observation["stored_sha256"]
        assert len(stored) == observation["stored_bytes"] < 40_000_000
        raw = gzip.decompress(stored)
        assert sha(raw) == observation["original_sha256"]
        assert len(raw) == observation["original_bytes"]
        if is_xml:
            archive = zipfile.ZipFile(io.BytesIO(raw))
            assert archive.testzip() is None
            body = archive.read(observation["zip_member"])
            assert sha(body) == observation["xml_member_sha256"]
            assert len(body) == observation["xml_member_bytes"]
            result[source_id] = ET.fromstring(body)
        elif observation.get("zip_member"):
            archive = zipfile.ZipFile(io.BytesIO(raw))
            assert archive.testzip() is None
            member = archive.read(observation["zip_member"])
            assert sha(member) == observation["member_sha256"]
            assert len(member) == observation["member_bytes"]
            result[source_id] = member
        else:
            result[source_id] = json.loads(raw)
        pins.append({"source_id": source_id, "original_sha256": sha(raw)})
    return result, pins


def main():
    contract_bytes = (TURNOUT / "priority-set.json").read_bytes()
    contract = json.loads(contract_bytes)
    xml_sources, xml_pins = originals(contract["legacy_source_observations"], True)
    json_sources, json_pins = originals(contract["original_combined_json_observations"], False)
    xml_count = 0
    xml_seen = set()
    with gzip.open(TURNOUT / "extracts/legacy-source-positions.jsonl.gz", "rt") as stream:
        for line in stream:
            record = json.loads(line)
            key = record["source_id"], record["source_pointer"], record["contest_label"]
            assert key not in xml_seen
            xml_seen.add(key)
            node = xml_pointer(xml_sources[record["source_id"]], record["source_pointer"])
            assert record["tag"] == node.tag
            assert record["attributes"] == node.attrib
            assert record["text"] == node.text
            xml_count += 1
    assert xml_count == 290542
    json_count = 0
    json_seen = set()
    with gzip.open(TURNOUT / "extracts/legacy-json-source-positions.jsonl.gz", "rt") as stream:
        for line in stream:
            record = json.loads(line)
            key = record["source_id"], record["source_pointer"], record["contest_label"]
            assert key not in json_seen
            json_seen.add(key)
            assert record["raw_object"] == json_pointer(json_sources[record["source_id"]], record["source_pointer"])
            json_count += 1
    assert json_count == 368

    xml_leaf_count = 0
    json_leaf_count = 0
    json_candidate_cells = 0
    unavailable_xml = []
    for county in contract["counties"]:
        for label, leaves in county["original_enr_constituents"].items():
            if not leaves:
                unavailable_xml.append({"contest": label, "county_fips": county["county_fips"]})
                continue
            root = xml_sources[leaves[0]["source_id"]]
            matches = [node for node in root.findall("Contest") if node.attrib.get("key") == leaves[0]["contest_key"]]
            assert len(matches) == 1
            contest_node = matches[0]
            native_names = []
            counts = collections.defaultdict(dict)
            for candidate in contest_node.findall("Choice"):
                for method in candidate.findall("VoteType"):
                    for native in method:
                        name = native.attrib["name"]
                        if name not in native_names:
                            native_names.append(name)
                        key = candidate.attrib["key"], method.attrib["name"]
                        assert key not in counts[name]
                        counts[name][key] = int(native.attrib["votes"])
            assert [leaf["name"] for leaf in leaves] == native_names
            for ordinal, leaf in enumerate(leaves):
                assert leaf["native_ordinal"] == ordinal
                values = counts[leaf["name"]]
                assert leaf["available_candidate_method_cells"] == len(values)
                assert leaf["expected_candidate_method_cells"] == len(contest_node.findall("Choice"))*6
                expected = sum(values.values()) if len(values) == leaf["expected_candidate_method_cells"] else None
                assert leaf["candidate_votes"] == expected
                for path in leaf["source_pointers"]:
                    assert xml_pointer(root, path).attrib["name"] == leaf["name"]
                xml_leaf_count += 1
        for label, leaves in county["original_enr_combined_json_constituents"].items():
            assert leaves
            details = json_pointer(json_sources[leaves[0]["source_id"]], leaves[0]["source_pointer"])
            summary = json_pointer(json_sources[leaves[0]["summary_source_id"]], leaves[0]["summary_source_pointer"])
            assert len(leaves) == len(details["P"]) == len(details["V"])
            assert [leaf["native_name"] for leaf in leaves] == details["P"]
            for ordinal, leaf in enumerate(leaves):
                assert leaf["native_ordinal"] == ordinal
                assert leaf["raw_identity"] == {"P": details["P"][ordinal], "source_ordinal": ordinal}
                vector = json_pointer(json_sources[leaf["source_id"]], leaf["candidate_vector_pointer"])
                assert vector == details["V"][ordinal]
                assert leaf["native_name"] == json_pointer(json_sources[leaf["source_id"]], leaf["native_name_pointer"])
                assert len(vector) == len(summary["CH"])
                assert all(isinstance(value, int) for value in vector)
                assert leaf["candidate_votes"] == sum(vector)
                json_candidate_cells += len(vector)
                json_leaf_count += 1
            for candidate_ordinal, total in enumerate(summary["V"]):
                assert total == sum(vector[candidate_ordinal] for vector in details["V"])
            if label == "2024-pres":
                assert sum(summary["V"]) == county["candidate_votes"]
    assert xml_leaf_count == 9579
    assert json_leaf_count == 9635
    assert json_candidate_cells == 43483
    assert unavailable_xml == [{"contest": "2022-senate", "county_fips": "45027"}, {"contest": "2022-governor", "county_fips": "45027"}]
    administrative_controls = []
    for year in [2024, 2022, 2020]:
        root = xml_sources[f"legacy{year}-detailxml"]
        turnout = root.find("ElectionVoterTurnout")
        counties = list(turnout.find("Counties"))
        assert len(counties) == 46
        record = {"year": year}
        for field in ["totalVoters", "ballotsCast"]:
            state = int(turnout.attrib[field])
            county_sum = sum(int(row.attrib[field]) for row in counties)
            record[field] = {"state": state, "county_sum": county_sum, "county_minus_state": county_sum-state}
        assert record["ballotsCast"]["county_minus_state"] == 0
        administrative_controls.append(record)
    result = {"status": "pass_original_XML_JSON_positions_and_separate_native_rosters", "contract_sha256": sha(contract_bytes), "contract_bytes": len(contract_bytes), "xml_originals": len(xml_sources), "json_entities": sum(not isinstance(value, bytes) for value in json_sources.values()), "related_text_archives": sum(isinstance(value, bytes) for value in json_sources.values()), "xml_positions": xml_count, "json_complete_objects": json_count, "xml_native_objects": xml_leaf_count, "json_native_objects": json_leaf_count, "json_native_candidate_cells": json_candidate_cells, "unavailable_xml": unavailable_xml, "administrative_election_controls": administrative_controls, "source_pins": xml_pins+json_pins, "scope": "Distinct historical original views; no physical, cross-year or November join from source names, ordinals or totals."}
    (HERE / "coordinator-legacy-review.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "source_pins"}, indent=2))


if __name__ == "__main__":
    main()
