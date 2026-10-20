"""Offline bounded newsroom-source review; --seal writes only this exact pack."""
from pathlib import Path
from html.parser import HTMLParser
import argparse
import gzip
import hashlib
import json
import re
import xml.etree.ElementTree as ET

R = Path(__file__).resolve().parent
STATE = R.parents[2].name


def sha(b):
    return hashlib.sha256(b).hexdigest()


def js(x):
    return (json.dumps(x, ensure_ascii=False, indent=2) + "\n").encode()


class Nodes(HTMLParser):
    def __init__(self, b):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.active = []
        self.feed(b.decode("utf-8", errors="replace"))

    def handle_starttag(self, t, a):
        if t in ("a", "script", "iframe", "meta", "section", "div", "article"):
            row = {"tag": t, "attributes": a, "position": list(self.getpos()), "text": ""}
            self.rows.append(row)
            if t in ("script", "a"):
                self.active.append(row)

    def handle_data(self, s):
        for row in self.active:
            row["text"] += s

    def handle_endtag(self, t):
        for i in range(len(self.active) - 1, -1, -1):
            if self.active[i]["tag"] == t:
                self.active.pop(i)
                break


def xmltree(node):
    return {"tag": node.tag, "attributes": dict(node.attrib), "text": node.text, "tail": node.tail, "children": [xmltree(x) for x in node]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seal", action="store_true")
    args = parser.parse_args()
    receipts = {p.name.removesuffix(".receipt.json"): json.loads(p.read_bytes()) for p in R.glob("*.receipt.json")}
    expected = {"tennessee": 9, "west-virginia": 9, "wyoming": 5}[STATE]
    assert len(receipts) == expected
    bodies, statuses, partpaths = {}, [], set()
    for key, receipt in receipts.items():
        assert receipt["id"] == key and receipt["started_utc"] and receipt["finished_utc"]
        for hop in receipt["hops"]:
            assert hop["method"] == "GET" and hop["request_headers"] and hop["started_utc"]
            if "body" not in hop:
                assert hop.get("error")
                continue
            p = hop["body"]
            stored = (R / p["path"]).read_bytes()
            raw = gzip.decompress(stored)
            assert sha(stored) == p["stored_sha256"] and len(stored) == p["stored_bytes"]
            assert sha(raw) == p["raw_sha256"] and len(raw) == p["raw_bytes"]
            statuses.append(hop["status"])
            partpaths.add(p["path"])
            assert hop["response_headers"] and hop["final_url"]
        if receipt.get("body"):
            raw = gzip.decompress((R / receipt["body"]["path"]).read_bytes())
            enc = dict((k.lower(), v) for k, v in receipt["hops"][-1]["response_headers"]).get("content-encoding", "")
            bodies[key] = gzip.decompress(raw) if enc.lower() == "gzip" else raw
    inv = json.loads((R / "acquisition-complete-v1.json").read_bytes())
    assert inv["receipts"] == [receipts[k] for k in sorted(receipts)]
    evidence = {"whole_request_receipts": sorted(receipts), "current_November_counts_admitted": False}
    gray = {}
    for key in ["wmc-results", "wsaz-results", "wdtv-results"]:
        if key not in bodies:
            continue
        text = bodies[key].decode()
        i = text.index("Fusion.contentCache=") + len("Fusion.contentCache=")
        cache = json.JSONDecoder().raw_decode(text[i:])[0]
        subset = {k: v for k, v in cache.items() if k in ("gsync-elections-featured", "gsync-elections")}
        assert len(subset) == 2
        for name, queries in subset.items():
            assert len(queries) == 1
            query, record = next(iter(queries.items()))
            assert json.loads(query)["includeTestResults"] is False
            data = record["data"]
            assert data["updatedDate"] is None
            assert data.get("races", data.get("elections")) == []
        gray[key] = subset
    evidence["complete_gray_election_cache_records"] = gray
    summary = {"state": STATE, "complete_request_receipts": len(receipts), "whole_response_hops": len(statuses), "unique_original_entity_objects": len(partpaths), "HTTP_statuses": {str(k): statuses.count(k) for k in sorted(set(statuses))}, "genuine_November_counts_admitted": False, "current_choice_or_leaf_ID_approved": False, "measured_cadence": None, "exact_eligible_remaining_pool": None, "browser_render_claimed": False}
    if STATE == "tennessee":
        nodes = Nodes(bodies["wtvf-results-primary-search"]).rows
        modules = [n for n in nodes if dict(n["attributes"]).get("data-xml-file-location")]
        assert len(modules) == 1
        assert dict(modules[0]["attributes"])["data-xml-file-location"] == receipts["wtvf-literal-results-xml"]["requested_url"]
        root = ET.fromstring(bodies["wtvf-literal-results-xml"])
        races = root.findall("Race")
        choices = [c for r in races for c in r.findall("Candidate")]
        senate = [r for r in races if r.findtext("Name1") == "US Senate"]
        assert len(races) == 64 and len(choices) == 168 and len(senate) == 1
        assert all(c.findtext("Votes") == "0" for c in choices)
        assert root.attrib == {"Time": "10/05/2026 12:03pm"}
        assert senate[0].findtext("TotalPrecincts") == "1911" and senate[0].findtext("PrecinctsReported") == "0"
        evidence.update(actual_publisher_XML_module=modules[0], complete_XML_tree=xmltree(root), literal_Senate_tree=xmltree(senate[0]), XML_scope="All zero; source clock lacks timezone and explicit election date. No native, final roster or registered-voter inference. No source names trimmed.")
        summary.update(XML_races=64, XML_candidates=168, XML_Senate_candidate_rows=len(senate[0].findall("Candidate")), source_clock=root.attrib["Time"], source_clock_timezone=None, explicit_election_date=None, candidate_votes_all_zero=True)
        client = bodies["wtvf-literal-client"].decode()
        at = client.index("this.refreshInt = setInterval(function(){")
        token = client[at:at + 150]
        assert "}, 30000);" in token
        evidence["actual_public_client"] = {"receipt": "wtvf-literal-client.receipt.json", "decoded_character_offset": at, "exact_timer_context": token, "source_XML_constructor": 'this.ajaxCall(this.xmlFileLocation + "?d=" + this.ranNum, this.renderResults, this);', "timer_scope": "30-second client refresh plan plus delayed click handler, not observed publisher vote-change cadence or an active browser render."}
        summary["observed_client_refresh_plan_ms"] = 30000
        text = bodies["chattanooga-home"].decode()
        assert "https://newschannel9.com/news/election-results" in text
        evidence["Chattanooga_scope"] = "Literal home client-navigation route followed; complete public page retained. No verified structured November numeric dataset in bounded inspection."
        evidence["WBIR_scope"] = "Complete home and actual election links only; local charter article's November6 wording is not a verified2026 date or a statewide count feed."
    elif STATE == "west-virginia":
        parent = Nodes(bodies["wdtv-state-interactive"]).rows
        urls = {dict(n["attributes"]).get("src") for n in parent if n["tag"] == "iframe"}
        configs = []
        for key in ["wdtv-actual-ap-2", "wdtv-actual-ap-state"]:
            assert receipts[key]["requested_url"] in urls
            node = next(n for n in Nodes(bodies[key]).rows if n["tag"] == "script" and dict(n["attributes"]).get("id") == "layout-config")
            outer = json.loads(node["text"])
            configs.append({"receipt": key + ".receipt.json", "literal_script": node, "complete_outer_JSON": outer, "complete_grid_JSON": json.loads(outer["grid"])})
        slots = configs[1]["complete_grid_JSON"]["slots"]
        senate = next(x for x in slots if x.get("label") == "Map of General for U.S. Senate, Class II in West Virginia")
        assert senate["date"] == "2026-11-03" and senate["props"]["raceID"] == "20261103WV49137"
        assert len(slots) == 3 and senate["props"]["state"] == "WV"
        evidence.update(complete_AP_layout_configs=configs, AP_scope="National balance and WV November3 setup only; no candidate counts fetched/admitted or browser render. Same AP supplier as other consumers.", Martinsburg_scope="Current home HTTP200; no election-labelled anchor in this bounded parsed home. No numeric-feed absence/exhaustion claim.", MetroNews_scope="Current home links October19 voter-information coverage; reporting context only, no measured cadence/count import.")
        summary.update(observed_AP_Senate_setup="20261103WV49137", AP_configured_date="2026-11-03", AP_layout_slots=[1, 3], AP_independent_from_other_AP_consumers=False)
    else:
        nodes = Nodes(bodies["jackson-home"]).rows
        anchors = [n for n in nodes if n["tag"] == "a" and dict(n["attributes"]).get("href") == "/special/general_election/"]
        assert anchors and receipts["jackson-general-section"]["status"] == 200
        evidence.update(Jackson_actual_general_section_anchors=anchors, qualified_access="Sheridan/Jackson/K2/WyomingNewsNow homes and literal Jackson general-election section retained. No complete November Senate numeric feed/supplier/cadence verified.", Sheridan_false_positive="Results10/12/26 and a poll Results action are unclassified home links, not accepted election counts; javascript action was not invoked.", WyomingNewsNow_scope="A Wisconsin suspicious-mail headline is another state's news, not a Wyoming count dataset.")
    products = {"literal-runtime-evidence.json": js(evidence), "review.json": js({"status": "pass_bounded_primary_newsroom_source_review", **summary})}
    for name, body in products.items():
        if args.seal:
            (R / name).write_bytes(body)
        else:
            assert (R / name).read_bytes() == body
    paths = sorted(p for p in R.rglob("*") if p.is_file() and p.name != "asset-manifest.json")
    assert all(p.suffix != ".pyc" and "__pycache__" not in p.parts for p in paths)
    rows = [{"path": str(p.relative_to(R)), "bytes": p.stat().st_size, "sha256": sha(p.read_bytes())} for p in paths]
    assert all(r["bytes"] < 40000000 for r in rows)
    manifest = js({"excludes_only": "asset-manifest.json", "owned_files": rows, "scope": "Bounded coordinator newsroom-source research; no live/current admission"})
    if args.seal:
        (R / "asset-manifest.json").write_bytes(manifest)
    else:
        assert (R / "asset-manifest.json").read_bytes() == manifest
    print(json.dumps({"status": "pass", **summary, "owned_targets": len(rows), "maximum": max(r["bytes"] for r in rows)}))


if __name__ == "__main__":
    main()
