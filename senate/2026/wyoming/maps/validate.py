#!/usr/bin/env python3
"""Offline validation of the Wyoming precinct-map package (standard library only).

    uv run python3 -I senate/2026/wyoming/maps/validate.py

Checks: raw entity/stored hashes and sizes against every retrieval record;
expected HTTP statuses; ArcGIS paging completeness (count = objectIds =
returned features, no exceededTransferLimit, batch < maxRecordCount); WFS
hits = numberMatched = numberReturned = parsed members = per-feature renders;
TopoJSON geometry counts; manifest hashes/sizes for every listed file; derived
GeoJSON feature counts, unmodified attributes and full vertex counts (no
simplification); recomputed precinct-ID reconciliation against the read-only
results labels and the SOS 2026 roster; render-join quality; the priority set;
the generated county table in ../precinct-maps.md; relative links in the
report and index.html; and that every file is below 40 MB. Writes
validation.json and exits non-zero on any failure.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import html.parser
import json
import pathlib
import re
import sys
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
WY = HERE.parent
REPORT = WY / "precinct-maps.md"
LIMIT = 40 * 1000 * 1000
DP = re.compile(r"(\d{1,4})-(\d{1,3})(?:[-.](\d+))?([A-Za-z]*)")
results = []


def check(name, ok, detail=None):
    results.append({"check": name, "ok": bool(ok), "detail": detail})
    if not ok:
        print("FAIL", name, detail)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def key(value, census=False):
    if value is None or value == "":
        return None
    s = str(value).strip()
    if s.startswith("excel-date:"):
        s = s.split(":", 1)[1][5:]
    if census and re.fullmatch(r"\d{6}", s):
        return f"{int(s[:4])}-{int(s[4:])}"
    m = DP.search(s)
    return f"{int(m.group(1))}-{int(m.group(2))}" if m else None


def raw_bytes(rec):
    data = (HERE / rec["stored_path"]).read_bytes()
    return gzip.decompress(data) if rec["store"] == "gzip" else data


def main():
    reg = json.loads((HERE / "sources.json").read_text())
    specs = {s["id"]: s for s in reg["sources"]}
    checks = json.loads((HERE / "geometry-checks.json").read_text())

    # 1. raw snapshot integrity
    n_files = 0
    for spec in reg["sources"]:
        rpath = HERE / "raw" / spec["id"] / "retrieval.json"
        check(f"retrieval record exists: {spec['id']}", rpath.exists())
        if not rpath.exists():
            continue
        rr = json.loads(rpath.read_text())
        names = [r["name"] for r in rr["requests"]]
        for r in spec.get("requests", []):
            check(f"declared request retrieved: {spec['id']}/{r['name']}", r["name"] in names)
        for r in rr["requests"]:
            p = HERE / r["stored_path"]
            blob = p.read_bytes()
            n_files += 1
            ok = sha(blob) == r["stored_sha256"] and len(blob) == r["stored_bytes"]
            ent = gzip.decompress(blob) if r["store"] == "gzip" else blob
            ok = ok and sha(ent) == r["entity_sha256"] and len(ent) == r["entity_bytes"]
            check(f"raw hash: {r['stored_path']}", ok)
            check(f"expected HTTP status: {r['stored_path']}", r["matches_expectation"],
                  {"status": r["http_status"], "expected": r["expected_status"]})
            if r["store"] == "gzip":
                check(f"deterministic gzip header (mtime 0): {r['stored_path']}", blob[4:8] == b"\0\0\0\0")
    check("raw files checked", n_files > 0, n_files)

    # 2. paging / completeness
    for sid, g in checks.items():
        p = g["paging"]
        if g["kind"] == "arcgis-layer":
            ok = (p["returnCountOnly"] == p["objectIds"] == p["features_returned"] == g["features"]
                  and p["returned_oids_equal_objectIds"] and not p["exceededTransferLimit_any"]
                  and p["duplicate_oids"] == 0 and p["batch_size"] < p["maxRecordCount"])
            check(f"ArcGIS paging complete: {sid}", ok, {k: p[k] for k in ("returnCountOnly", "objectIds", "features_returned",
                                                                             "maxRecordCount", "batch_size", "batches")})
        elif g["kind"] == "wfs-gml":
            rr = json.loads((HERE / "raw" / sid / "retrieval.json").read_text())
            n_r = len(rr["paging"]["renders"])
            ok = int(p["numberMatched_hits"]) == int(p["numberMatched"]) == int(p["numberReturned"]) == p["members_parsed"] == g["features"] == n_r
            check(f"WFS complete (hits = matched = returned = parsed = renders): {sid}", ok, {**p, "renders": n_r})
        elif g["kind"] == "topojson":
            check(f"TopoJSON geometries decoded: {sid}", p["geometries"] == g["features"] > 0, p["geometries"])
        check(f"no empty geometries: {sid}", g["empty"] == 0)
        check(f"input rings closed: {sid}", g["unclosed_input_rings"] == 0)
        check(f"features fall in their county (rep. points within 100 m): {sid}",
              not g["representative_points_outside_county_100m"], g["representative_points_outside_county_100m"])
        cov = g["coverage_vs_2020_census_county_extent"]["covered_share_of_county"]
        check(f"layer covers >= 99.5% of 2020 Census county extent: {sid}", cov >= 0.995, cov)

    # 3. manifest
    man = list(csv.DictReader((HERE / "manifest.csv").open()))
    mj = json.loads((HERE / "manifest.json").read_text())
    check("manifest.csv and manifest.json rows agree", len(man) == len(mj), (len(man), len(mj)))
    for r in man:
        p = HERE / r["local_path"]
        ok = p.exists() and sha(p.read_bytes()) == r["sha256"] and p.stat().st_size == int(r["bytes"])
        check(f"manifest hash: {r['local_path']}", ok)
    listed = {r["local_path"] for r in man}
    for sub in ("raw", "derived", "previews"):
        for p in (HERE / sub).rglob("*"):
            if p.is_file() and not p.name.endswith("retrieval.json") and p.name != "acquisition-summary.json":
                check(f"file listed in manifest: {p.relative_to(HERE)}", p.relative_to(HERE).as_posix() in listed)

    # 4. derived GeoJSON: counts, attributes, vertices
    for sid, g in checks.items():
        d = HERE / "derived" / f"{sid}.geojson"
        equivalent = (g.get("comparison_with_primary") or {}).get("geometry_equivalent")
        if equivalent:
            check(f"equivalent alternate has no duplicate derivative: {sid}", not d.exists())
            continue
        fc = json.loads(d.read_text())
        check(f"derived feature count: {sid}", len(fc["features"]) == g["features"], (len(fc["features"]), g["features"]))
        nverts = 0
        for f in fc["features"]:
            geom = f["geometry"]
            polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
            nverts += sum(len(r) for poly in polys for r in poly)
        check(f"derived vertex count equals native (no simplification): {sid}", nverts == g["vertices"], (nverts, g["vertices"]))
        if g["kind"] == "arcgis-layer":
            rr = json.loads((HERE / "raw" / sid / "retrieval.json").read_text())
            raw_feats = []
            for r in rr["requests"]:
                if r["name"].startswith("features-"):
                    raw_feats += json.loads(raw_bytes(r))["features"]
            check(f"derived attributes identical to source: {sid}",
                  [f["attributes"] for f in raw_feats] == [f["properties"] for f in fc["features"]])

    # 5. reference rosters and ID reconciliation (recomputed)
    labels = {}
    for r in csv.DictReader((WY / "data" / "baselines" / "precinct-labels.csv").open()):
        labels.setdefault((r["year"], r["county_fips"]), []).append(r["native_precinct_label"])
    roster = list(csv.DictReader((HERE / "sos-2026-roster.csv").open()))
    sos = {}
    for r in roster:
        sos.setdefault(r["county_fips"], set()).add(r["precinct_code"])
    check("SOS 2026 roster: 23 counties", len(sos) == 23, len(sos))
    check("SOS 2026 roster: 433 unique county-precinct codes", sum(len(v) for v in sos.values()) == 433,
          sum(len(v) for v in sos.values()))
    bs = json.loads((HERE / "build-summary.json").read_text())
    check("SOS 2026 roster: no unparsed lines", not bs["sos_roster"]["unparsed_lines"])
    check("2024 results labels: 432 precinct rows", sum(len(v) for (y, _), v in labels.items() if y == "2024") == 432)
    feats = list(csv.DictReader((HERE / "features.csv").open()))
    recon = {(r["source_id"], r["county_fips"]): r for r in csv.DictReader((HERE / "id-reconciliation.csv").open())}
    by_src = {}
    for f in feats:
        by_src.setdefault(f["source_id"], []).append(f)
    for sid, rows in by_src.items():
        fips = rows[0]["county_fips"]
        kset = {r["canonical_key"] for r in rows if r["canonical_key"]}
        k24 = [key(x) for x in labels.get(("2024", fips), [])]
        k26 = {key(x) for x in sos.get(fips, ())}
        r = recon[(sid, fips)]
        ok = (int(r["results2024_rows_matched"]) == sum(k in kset for k in k24)
              and int(r["sos2026_codes_matched"]) == sum(key(x) in kset for x in sos.get(fips, ()))
              and int(r["distinct_keys"]) == len(kset) and int(r["features"]) == len(rows)
              and r["map_keys_not_in_sos2026"] == " ".join(sorted(kset - k26, key=lambda k: tuple(map(int, k.split("-"))))))
        check(f"ID reconciliation reproduces: {sid}", ok)
        for row in rows:
            check(f"feature key parses from raw ID: {sid}#{row['feature_index']}", key(row["raw_id"]) == (row["canonical_key"] or None))

    # 6. render join quality (WFS sources without attributes)
    rj = json.loads((HERE / "wfs-render-join.json").read_text())
    for sid, j in rj.items():
        check(f"render join: every feature classified with >= 95% of votes: {sid}", j["min_winner_share"] >= 0.95, j["min_winner_share"])
        check(f"render join: every SLD class matched by a feature: {sid}", not j["classes_unmatched"], j["classes_unmatched"])

    # 7. priority set and county index
    mi = json.loads((HERE / "map-index.json").read_text())
    order = [[c["county"], c["fips"]] for c in mi["counties"]]
    check("priority counties in turnout order", order == reg["priority_counties_in_order"])
    check("12 counties flagged in the 80% set", sum(c["in_80pct_set"] for c in mi["counties"]) == 12)
    for c in mi["counties"]:
        check(f"county has an actual downloaded asset: {c['county']}", bool(c["primary"] or c["pdfs"]))
    table = county_table(mi["counties"])
    text = REPORT.read_text() if REPORT.exists() else ""
    begin, end = "<!-- BEGIN generated county table (build.py) -->", "<!-- END generated county table -->"
    block = text[text.index(begin) + len(begin):text.index(end)].strip() if begin in text and end in text else None
    check("generated county table in precinct-maps.md matches map-index.json", block == table)

    # 8. links
    for path in (REPORT, HERE / "index.html"):
        if not path.exists():
            check(f"exists: {path.name}", False)
            continue
        txt = path.read_text()
        links = re.findall(r"\]\(([^)\s]+)\)", txt) if path.suffix == ".md" else re.findall(r"(?:href|src)='([^']+)'", txt)
        bad = []
        for link in links:
            if re.match(r"^[a-z]+:", link) or link.startswith("#"):
                continue
            target = (path.parent / urllib.parse.unquote(link.split("#")[0])).resolve()
            if not target.exists() and target != (HERE / "validation.json").resolve():  # written by this script
                bad.append(link)
        check(f"relative links resolve: {path.name}", not bad, bad[:10])

    # 9. object sizes
    big = [(p.relative_to(HERE).as_posix(), p.stat().st_size) for p in HERE.rglob("*") if p.is_file() and p.stat().st_size >= LIMIT]
    check("every file below 40 MB", not big, big)
    if REPORT.exists():
        check("report below 40 MB", REPORT.stat().st_size < LIMIT)

    failed = [r for r in results if not r["ok"]]
    (HERE / "validation.json").write_text(json.dumps({"checks": len(results), "failed": len(failed),
                                                      "failures": failed, "results": results}, indent=1) + "\n")
    print(f"{len(results)} checks, {len(failed)} failed")
    return 1 if failed else 0


def county_table(counties):
    out = ["| Rank | County | FIPS | Status | Primary asset (features) | 2024 results rows matched | SOS 2026 codes matched | Census 2020 VTD keys vs 2024 rows | Preview |",
           "| ---: | --- | --- | --- | --- | ---: | ---: | ---: | --- |"]
    for c in counties:
        p = c["primary"]
        cr = c["census_2020_vtd_alternative"]
        if p:
            r = p["reconciliation"]
            prim = f"`{p['source_id']}` ({p['features']})"
            m24 = f"{r['results2024_rows_matched']}/{r['results2024_rows']}"
            m26 = f"{r['sos2026_codes_matched']}/{r['sos2026_codes']}"
            prev = f"[preview](maps/{p['preview']})"
        else:
            prim = "none (PDF maps only)" if c["pdfs"] else "none"
            m24 = m26 = "n/a"
            prev = f"[PDF preview](maps/{c['pdfs'][0]['preview']})" if c["pdfs"] else ""
        out.append(f"| {c['rank_sen2024']} | {c['county']} | {c['fips']} | {c['status']} | {prim} | {m24} | {m26} | "
                   f"{cr['results2024_rows_matched']}/{cr['results2024_rows']} | {prev} |")
    return "\n".join(out)


if __name__ == "__main__":
    sys.exit(main())
