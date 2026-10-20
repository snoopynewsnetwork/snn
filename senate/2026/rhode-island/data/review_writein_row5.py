"""Independent original OOXML audit; writes coordinator evidence only."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET

S = Path(__file__).resolve().parents[1]
T = S / "data/turnout"
OUT = S / "data/coordinator-writein-row5-review"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def sha(body):
    return hashlib.sha256(body).hexdigest()


def pin(path):
    body = path.read_bytes()
    return {"path": str(path.relative_to(S)), "bytes": len(body), "sha256": sha(body)}


def main():
    receipt_path = T / "source/acquired/board2024-writeins-xlsx.receipt.json"
    receipt = json.loads(receipt_path.read_bytes())
    stored_path = T / receipt["stored_path"]
    stored = stored_path.read_bytes()
    raw = gzip.decompress(stored)
    assert len(raw) == 337123 == receipt["raw_bytes"]
    assert sha(raw) == receipt["raw_sha256"] == "71929b0ba569b546cbb3aad7c0427cfe7e94f15c42e2b15ea330cbd5b28b039c"
    assert len(stored) == receipt["stored_bytes"] and sha(stored) == receipt["stored_sha256"]
    z = zipfile.ZipFile(io.BytesIO(raw))
    assert z.testzip() is None
    ss_raw = z.read("xl/sharedStrings.xml")
    ss_nodes = ET.fromstring(ss_raw).findall("m:si", NS)
    strings = ["".join(t.text or "" for t in x.iter("{" + NS["m"] + "}t")) for x in ss_nodes]
    ss_spans = list(re.finditer(rb"<si(?:\s[^>]*)?>.*?</si>", ss_raw, re.S))
    assert len(ss_spans) == len(strings)
    rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    prior_summary = OUT / "writein-scope-comparison.json.prior.gz"
    old = json.loads(gzip.decompress(prior_summary.read_bytes()) if prior_summary.exists() else (T / "extracts/writein-scope-comparison.json").read_bytes())
    old_by_name = {r["municipality"]: r for r in old}
    summaries, omitted, cranston = [], [], None
    cell_count = 0
    for sheet in ET.fromstring(z.read("xl/workbook.xml")).findall("m:sheets/m:sheet", NS):
        target = rels[sheet.attrib[RID]]
        member = posixpath.normpath(target.lstrip("/") if target.startswith("/") else "xl/" + target)
        body = z.read(member)
        cells = {}
        for c in ET.fromstring(body).findall(".//m:sheetData/m:row/m:c", NS):
            a = c.attrib["r"]
            if not re.fullmatch(r"[DE]\d+", a):
                continue
            v = c.find("m:v", NS)
            raw_v = v.text if v is not None else None
            value = strings[int(raw_v)] if c.attrib.get("t") == "s" else raw_v
            cells[a] = {"value": value, "raw_v": raw_v, "xml_type": c.attrib.get("t"), "attributes": dict(c.attrib), "formula": c.findtext("m:f", None, NS)}
            cell_count += 1
        assert cells["D3"]["value"] == "U.S. Senator in Congress:"
        detail = []
        for address, name in cells.items():
            if address[0] != "D" or int(address[1:]) < 5:
                continue
            row = int(address[1:])
            count = cells.get("E" + str(row))
            if not name["value"] or name["value"].strip().lower() == "total" or not count or count["value"] in (None, ""):
                continue
            assert re.fullmatch(r"\d+", count["value"]), (sheet.attrib["name"], row, count)
            detail.append({"row": row, "name": name["value"], "votes": int(count["value"]), "name_cell": "D" + str(row), "count_cell": "E" + str(row)})
        full = sum(r["votes"] for r in detail)
        prior = sum(r["votes"] for r in detail if r["row"] >= 6)
        printed = int(cells["E4"]["value"])
        old_r = old_by_name[sheet.attrib["name"]]
        assert (prior, printed, prior - printed) == (old_r["detail_sum"], old_r["printed_top_total"], old_r["difference"])
        summaries.append({"municipality": sheet.attrib["name"], "member": member, "member_bytes": len(body), "member_sha256": sha(body), "member_crc32": z.getinfo(member).CRC, "printed_total": printed, "row6_onward_detail": prior, "full_row5_onward_detail": full, "old_difference": prior - printed, "full_difference": full - printed, "detail_rows": detail})
        omitted.extend({"municipality": sheet.attrib["name"], "member": member, **r} for r in detail if r["row"] < 6)
        if sheet.attrib["name"] == "Cranston":
            assert member == "xl/worksheets/sheet7.xml"
            assert cells["D5"]["value"] == "Mario Frioli " and cells["E5"]["value"] == "1"
            selected = {}
            for address in ["D3", "E4", "D5", "E5", "D78", "E78"]:
                spans = list(re.finditer(rb'<c\b[^>]*\br="' + address.encode() + rb'"[^>]*(?:/>|>.*?</c>)', body, re.S))
                assert len(spans) == 1, address
                span = spans[0]
                selected[address] = {**cells[address], "member_byte_offset": span.start(), "member_byte_end_exclusive": span.end(), "original_cell_xml": span.group().decode("utf-8")}
                if cells[address]["xml_type"] == "s":
                    i = int(cells[address]["raw_v"])
                    selected[address]["shared_string"] = {"index": i, "member": "xl/sharedStrings.xml", "member_sha256": sha(ss_raw), "byte_offset": ss_spans[i].start(), "byte_end_exclusive": ss_spans[i].end(), "original_xml": ss_spans[i].group().decode("utf-8")}
            cranston = {"sheet": sheet.attrib["name"], "sheet_attributes": dict(sheet.attrib), "relationship_id": sheet.attrib[RID], "relationship_target": target, "member": member, "member_bytes": len(body), "member_sha256": sha(body), "member_crc32": z.getinfo(member).CRC, "selected_original_cells": selected}
    assert len(summaries) == 39
    assert sum(r["printed_total"] for r in summaries) == 1239
    assert sum(r["row6_onward_detail"] for r in summaries) == 1226
    assert sum(r["full_row5_onward_detail"] for r in summaries) == 1227
    assert sum(r["old_difference"] != 0 for r in summaries) == 9
    assert sum(r["full_difference"] != 0 for r in summaries) == 8
    assert omitted == [{"municipality": "Cranston", "member": "xl/worksheets/sheet7.xml", "row": 5, "name": "Mario Frioli ", "votes": 1, "name_cell": "D5", "count_cell": "E5"}]
    protected = [T / p for p in ["asset-manifest.json", "priority-set.json", "native-inventory.json", "qa/pre-peer-body-witness.json"]] + [S / "data/county-turnout.csv"]
    prior_proof = OUT / "proof.json"
    original_review_pins = json.loads(prior_proof.read_bytes())["producer_files_unchanged"] if prior_proof.exists() else [pin(p) for p in protected]
    result = {"status": "confirmed_original_row5_omission_in_prior_detail_projection", "source_receipt": pin(receipt_path), "source_stored_body": pin(stored_path), "original_workbook_bytes": len(raw), "original_workbook_sha256": sha(raw), "source_url": receipt["final_url"], "source_members": [{"member": m, "bytes": len(z.read(m)), "sha256": sha(z.read(m)), "crc32": z.getinfo(m).CRC} for m in ["xl/workbook.xml", "xl/_rels/workbook.xml.rels", "xl/sharedStrings.xml"]], "municipalities": 39, "D_E_cells_independently_read": cell_count, "printed_municipal_senate_total": 1239, "prior_row6_projection_detail": 1226, "prior_local_discrepancies": 9, "complete_row5_onward_detail": 1227, "complete_local_discrepancies": 8, "omitted_original_rows": omitted, "cranston_original_xml_proof": cranston, "complete_scopes": summaries, "producer_files_unchanged": original_review_pins, "repair_scope": "Correct the detail summary/report coverage, preserving prior row6 projection and its complete historical seal. Original workbook/candidate/generic totals/native keys/order/242 membership require no correction. No write-in eligibility/allocation inference."}
    OUT.mkdir(exist_ok=True)
    for rel in ["writein_scopes.py", "extracts/writein-scope-comparison.json"]:
        p = T / rel
        target = OUT / (p.name + ".prior.gz")
        if target.exists():
            gzip.decompress(target.read_bytes())
        else:
            target.write_bytes(gzip.compress(p.read_bytes(), mtime=0))
    (OUT / "proof.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "municipalities": 39, "D_E_cells": cell_count, "complete_detail": 1227, "complete_discrepancies": 8, "prior_detail": 1226, "prior_discrepancies": 9, "omitted": omitted, "proof": str(OUT / "proof.json")}))


if __name__ == "__main__":
    main()
