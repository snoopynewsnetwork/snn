#!/usr/bin/env python3
"""Offline build of the Wyoming precinct-map index from the retained raw/ snapshot.

Run from the repository root (no network access is used):

    uv run --with shapely==2.0.6 --with pyproj==3.7.0 --with pillow==11.0.0 \
        --with pyshp==2.3.1 --with pypdfium2==4.30.0 --with pypdf==6.21.1 \
        python3 -I senate/2026/wyoming/maps/build.py

Outputs (all regenerated): derived/*.geojson (OGC:CRS84 copies of every GIS
original, full coordinate precision, no simplification), previews/*.png,
sos-2026-roster.csv, features.csv, id-reconciliation.csv, geometry-checks.json,
pdf-audit.json, wfs-render-join.json, manifest.csv, manifest.json,
map-index.json, index.html, build-summary.json and the generated county table
inside ../precinct-maps.md. Originals under raw/ are only read.
"""
from __future__ import annotations

import collections
import csv
import datetime as dt
import gzip
import hashlib
import html
import io
import json
import pathlib
import re
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
import pypdf
import pypdfium2
import pyproj
import shapefile
import shapely
from PIL import Image, ImageDraw, ImageFont
from pyproj import CRS, Transformer
from shapely.geometry import LinearRing, MultiPolygon, Polygon, mapping
from shapely.strtree import STRtree

HERE = pathlib.Path(__file__).resolve().parent
WY = HERE.parent
RAW = HERE / "raw"
DERIVED = HERE / "derived"
PREVIEWS = HERE / "previews"
REPORT = WY / "precinct-maps.md"
LABELS = WY / "data" / "baselines" / "precinct-labels.csv"
TURNOUT = WY / "data" / "county-turnout.csv"
GML = "{http://www.opengis.net/gml/3.2}"
WFSNS = "{http://www.opengis.net/wfs/2.0}"
SLD = "{http://www.opengis.net/sld}"
OGC = "{http://www.opengis.net/ogc}"
DP = re.compile(r"(\d{1,4})-(\d{1,3})(?:[-.](\d+))?([A-Za-z]*)")
COUNTY_UPPER = {"BIG HORN": "Big Horn", "HOT SPRINGS": "Hot Springs"}
OVERLAP_MIN_M2 = 1.0
TABLE_BEGIN = "<!-- BEGIN generated county table (build.py) -->"
TABLE_END = "<!-- END generated county table -->"


# ----------------------------------------------------------------------------- utilities
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: pathlib.Path) -> str:
    return sha256_bytes(p.read_bytes())


def rel(p: pathlib.Path) -> str:
    return p.relative_to(HERE).as_posix()


def write_json(path: pathlib.Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=1, sort_keys=False, ensure_ascii=False) + "\n")


def safe_xml(data: bytes):
    if b"<!DOCTYPE" in data or b"<!ENTITY" in data:
        raise SystemExit("refusing XML with a DTD or entity declaration")
    return ET.fromstring(data)


class Source:
    def __init__(self, spec: dict):
        self.spec = spec
        self.id = spec["id"]
        self.dir = RAW / self.id
        self.retrieval = json.loads((self.dir / "retrieval.json").read_text())
        self.by_name = {r["name"]: r for r in self.retrieval["requests"]}

    def raw(self, name: str) -> bytes:
        rec = self.by_name[name]
        data = (HERE / rec["stored_path"]).read_bytes()
        return gzip.decompress(data) if rec["store"] == "gzip" else data

    def json(self, name: str):
        return json.loads(self.raw(name).decode("utf-8"))

    def url(self, name: str) -> str:
        return self.by_name[name]["request_url"]

    def when(self, name: str) -> str:
        return self.by_name[name]["retrieved_utc"]


def parse_code(value, census: bool = False):
    if value is None:
        return None
    s = str(value).strip()
    if s.startswith("excel-date:"):  # Excel coerced '01-02' to 2022-01-02: rebuild MM-DD
        s = s.split(":", 1)[1][5:]
    if census and re.fullmatch(r"\d{6}", s):
        return {"district": int(s[:4]), "precinct": int(s[4:]), "split": "", "suffix": ""}
    m = DP.search(s)
    if not m:
        return None
    return {"district": int(m.group(1)), "precinct": int(m.group(2)), "split": m.group(3) or "",
            "suffix": m.group(4) or ""}


def key_of(p):
    return f"{p['district']}-{p['precinct']}" if p else None


def sort_key(k: str):
    a, b = k.split("-")
    return (int(a), int(b))


# ----------------------------------------------------------------------------- geometry decoding
def assemble_rings(rings):
    """Esri JSON / shapefile rings: clockwise = exterior, counter-clockwise = hole."""
    anomalies, ext, holes, unclosed = [], [], [], 0
    for r in rings:
        pts = [tuple(p[:2]) for p in r]
        if len(pts) and pts[0] != pts[-1]:
            unclosed += 1
        if len(pts) < 4:
            anomalies.append("ring with fewer than 4 positions")
            continue
        (holes if LinearRing(pts).is_ccw else ext).append(pts)
    if not ext and holes:
        ext, holes = holes, []
        anomalies.append("no clockwise exterior ring; rings treated as exteriors")
    shells = [Polygon(e) for e in ext]
    parts = [[e, []] for e in ext]
    for h in holes:
        pt = Polygon(h).representative_point()
        idx = next((i for i, s in enumerate(shells) if s.contains(pt)), None)
        if idx is None:
            parts.append([h, []])
            anomalies.append("counter-clockwise ring outside every exterior; treated as exterior")
        else:
            parts[idx][1].append(h)
    polys = [Polygon(s, hs) for s, hs in parts]
    if not polys:
        return Polygon(), anomalies, unclosed
    return (polys[0] if len(polys) == 1 else MultiPolygon(polys)), anomalies, unclosed


def topo_decode(topo: dict, object_name: str | None):
    t = topo.get("transform")
    arcs = []
    for a in topo["arcs"]:
        if t:
            x = y = 0
            pts = []
            for p in a:
                x += p[0]
                y += p[1]
                pts.append((x * t["scale"][0] + t["translate"][0], y * t["scale"][1] + t["translate"][1]))
        else:
            pts = [tuple(p[:2]) for p in a]
        arcs.append(pts)

    def ring(idxs):
        pts = []
        for i in idxs:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return pts

    objs = topo["objects"]
    name = object_name or next(iter(objs))
    out = []
    for g in objs[name]["geometries"]:
        if g["type"] == "Polygon":
            polys = [g["arcs"]]
        elif g["type"] == "MultiPolygon":
            polys = g["arcs"]
        else:
            out.append((g.get("properties") or {}, Polygon(), [f"unsupported type {g['type']}"], 0))
            continue
        geoms = [Polygon(ring(p[0]), [ring(h) for h in p[1:]]) for p in polys]
        geom = geoms[0] if len(geoms) == 1 else MultiPolygon(geoms)
        out.append((g.get("properties") or {}, geom, [], 0))
    return name, list(objs), out


def gml_decode(data: bytes):
    root = safe_xml(data)
    out = []

    def pos(el):
        dim = int(el.get("srsDimension", "2"))
        v = [float(x) for x in el.text.split()]
        return [tuple(v[i:i + 2]) for i in range(0, len(v), dim)]

    meta = {"numberMatched": root.get("numberMatched"), "numberReturned": root.get("numberReturned"),
            "srs": sorted({e.get("srsName") for e in root.iter(GML + "Polygon") if e.get("srsName")})}
    for m in root.iter(WFSNS + "member"):
        polys, unclosed = [], 0
        for poly in m.iter(GML + "Polygon"):
            ext = pos(poly.find(f"{GML}exterior/{GML}LinearRing/{GML}posList"))
            ints = [pos(e) for e in poly.findall(f"{GML}interior/{GML}LinearRing/{GML}posList")]
            for r in [ext] + ints:
                unclosed += int(r[0] != r[-1])
            polys.append(Polygon(ext, ints))
        out.append(({}, polys[0] if len(polys) == 1 else MultiPolygon(polys), [], unclosed))
    return meta, out


def esri_crs(layer_meta: dict, features_sr: dict | None):
    sr = features_sr or (layer_meta.get("extent") or {}).get("spatialReference") or {}
    if sr.get("latestWkid"):
        return CRS.from_epsg(sr["latestWkid"]), f"EPSG:{sr['latestWkid']}"
    if sr.get("wkid") and sr["wkid"] < 100000:
        return CRS.from_epsg(sr["wkid"]), f"EPSG:{sr['wkid']}"
    if sr.get("wkt"):
        c = CRS.from_wkt(sr["wkt"])
        return c, f"WKT:{c.name}"
    raise SystemExit(f"no usable spatial reference: {sr}")


def to_crs(geom, transformer):
    return shapely.transform(geom, lambda xy: np.column_stack(transformer.transform(xy[:, 0], xy[:, 1])))


def counts(geom):
    polys = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    parts = len(polys)
    rings = sum(1 + len(p.interiors) for p in polys)
    verts = sum(len(p.exterior.coords) + sum(len(i.coords) for i in p.interiors) for p in polys)
    return parts, rings, verts


# ----------------------------------------------------------------------------- reference rosters
def load_results_labels():
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    with LABELS.open() as f:
        for r in csv.DictReader(f):
            out[r["year"]][r["county_fips"]].append(r["native_precinct_label"])
    return out


def parse_sos_roster(pdf_bytes: bytes, fips_by_upper: dict):
    rows = []
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    names = sorted(fips_by_upper, key=len, reverse=True)
    county = dist = None
    unparsed = []
    for pi, page in enumerate(reader.pages, 1):
        for line in page.extract_text(extraction_mode="layout").splitlines():
            s = line.strip()
            if (not s or s.startswith(("County:", "User Name", "WyoReg")) or "Districts By County" in s
                    or (s.startswith("County ") and "Precinct Code" in s)):
                continue
            m = re.match(r"^(" + "|".join(re.escape(n) for n in names) + r")\b\s*(.*)$", s)
            if m:
                county, s = m.group(1), m.group(2).strip()
            m = re.match(r"^((?:Senate|House) District \d+)\s*(.*)$", s)
            if m:
                dist, s = m.group(1), m.group(2).strip()
            for tok in s.split():
                if re.fullmatch(r"\d{1,2}-\d{1,2}(?:-\d+)?", tok):
                    rows.append({"county": COUNTY_UPPER.get(county, county.title()), "county_fips": fips_by_upper[county],
                                 "district": dist, "precinct_code": tok, "canonical_key": key_of(parse_code(tok)),
                                 "page": pi})
                else:
                    unparsed.append({"page": pi, "line": line})
    meta = {k: str(v) for k, v in (reader.metadata or {}).items()}
    return rows, unparsed, len(reader.pages), meta


# ----------------------------------------------------------------------------- WFS render join
def parse_sld(data: bytes):
    root = safe_xml(data)
    classes = []
    for rule in root.iter(SLD + "Rule"):
        name = rule.findtext(SLD + "Name")
        prop = rule.find(f".//{OGC}PropertyName")
        lit = rule.find(f".//{OGC}Literal")
        fill = None
        for sym in rule.iter(SLD + "PolygonSymbolizer"):
            for p in sym.iter(SLD + "CssParameter"):
                if p.get("name") == "fill":
                    fill = p.text
        if fill:
            rgb = tuple(int(fill[i:i + 2], 16) for i in (1, 3, 5))
            classes.append({"name": name, "property": prop.text if prop is not None else None,
                            "literal": lit.text if lit is not None else None, "fill": fill, "rgb": rgb})
    return classes


def classify_colour(rgb, classes):
    """Best SLD class for an observed pixel assuming fill alpha a over a white background."""
    o = np.array(rgb, float) - 255.0
    best = None
    for c in classes:
        d = np.array(c["rgb"], float) - 255.0
        nn = float(d @ d)
        if nn == 0:
            continue
        a = float(o @ d) / nn
        resid = float(np.linalg.norm(o - a * d))
        if 0.3 <= a <= 1.05 and (best is None or resid < best[1]):
            best = (c["name"], resid, a)
    return best


def render_join(src: Source, geoms_native, classes):
    renders = src.retrieval["paging"]["renders"]
    results = []
    for r in renders:
        i = r["feature_index"]
        geom = geoms_native[i]
        img = Image.open(io.BytesIO(src.raw(r["file"]))).convert("RGB")
        w, h = img.size
        minx, miny, maxx, maxy = r["bbox"]
        px = (maxx - minx) / w
        inner = geom.buffer(-2.5 * px)
        if inner.is_empty:
            inner = geom
        xs = np.linspace(minx, maxx, 61)[1:-1]
        ys = np.linspace(miny, maxy, 61)[1:-1]
        pts = shapely.points(np.array([(x, y) for x in xs for y in ys]))
        inside = pts[shapely.contains(inner, pts)]
        if len(inside) < 5:
            inside = np.array([inner.representative_point()])
        votes, alphas, skipped = collections.Counter(), [], 0
        pix = img.load()
        for p in inside:
            cx = min(w - 1, max(0, int((p.x - minx) / (maxx - minx) * w)))
            cy = min(h - 1, max(0, int((maxy - p.y) / (maxy - miny) * h)))
            rgb = pix[cx, cy]
            if max(rgb) < 80 or rgb == (255, 255, 255):  # dark label text or white background
                skipped += 1
                continue
            best = classify_colour(rgb, classes)
            if best and best[1] <= 8.0:
                votes[best[0]] += 1
                alphas.append(best[2])
            else:
                skipped += 1
        top = votes.most_common(2)
        winner = top[0][0] if top else None
        share = top[0][1] / sum(votes.values()) if top else 0.0
        cls = next((c for c in classes if c["name"] == winner), None)
        results.append({"feature_index": i, "render": r["file"], "samples": int(len(inside)),
                        "skipped_text_background_or_unmatched": skipped, "votes": dict(votes),
                        "winner_class": winner, "winner_share": round(share, 4),
                        "runner_up": top[1][0] if len(top) > 1 else None,
                        "inferred_value": cls["literal"] if cls else None,
                        "alpha_median": round(float(np.median(alphas)), 4) if alphas else None})
    return results


# ----------------------------------------------------------------------------- previews
def palette(k: str):
    h = int(hashlib.md5(k.encode()).hexdigest()[:6], 16)
    hue = (h % 360) / 360.0
    import colorsys
    r, g, b = colorsys.hls_to_rgb(hue, 0.78, 0.55)
    return (int(r * 255), int(g * 255), int(b * 255))


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def draw_preview(path, title, subtitle, feats84, county84, labels, size=1000):
    """feats84: list of (geom CRS84, colour key, label). Generated research preview, no basemap."""
    allg = [g for g, _, _ in feats84 if not g.is_empty] + ([county84] if county84 is not None else [])
    minx = min(g.bounds[0] for g in allg); miny = min(g.bounds[1] for g in allg)
    maxx = max(g.bounds[2] for g in allg); maxy = max(g.bounds[3] for g in allg)
    k = np.cos(np.radians((miny + maxy) / 2))
    top, margin = 70, 20
    sx = (size - 2 * margin) / max(1e-9, (maxx - minx) * k)
    sy = (size - top - 2 * margin - 30) / max(1e-9, (maxy - miny))
    s = min(sx, sy)
    W = int((maxx - minx) * k * s + 2 * margin)
    H = int((maxy - miny) * s + top + 2 * margin + 30)
    img = Image.new("RGB", (max(W, 900), H), "white")
    d = ImageDraw.Draw(img)

    def xy(coords):
        return [(margin + (x - minx) * k * s, top + margin + (maxy - y) * s) for x, y in coords]

    def polys(g):
        return list(g.geoms) if isinstance(g, MultiPolygon) else [g]

    for g, ck, _ in feats84:
        if g.is_empty:
            continue
        for p in polys(g):
            d.polygon(xy(p.exterior.coords), fill=palette(ck or "none"), outline=(70, 70, 70))
            for hole in p.interiors:
                d.polygon(xy(hole.coords), fill="white", outline=(70, 70, 70))
    if county84 is not None:
        for p in polys(county84):
            d.line(xy(p.exterior.coords), fill=(0, 0, 0), width=2)
    f = font(12)
    if labels:
        for g, _, lab in feats84:
            if g.is_empty or not lab:
                continue
            pt = g.representative_point()
            x, y = xy([(pt.x, pt.y)])[0]
            d.text((x, y), lab, fill=(0, 0, 0), font=f, anchor="mm")
    d.rectangle([0, 0, img.width, top - 8], fill=(245, 245, 245))
    d.text((10, 8), title, fill=(0, 0, 0), font=font(18))
    d.text((10, 34), subtitle, fill=(60, 60, 60), font=font(11))
    d.text((10, H - 24), "Generated research preview from the retained source file; not an official map; no basemap; "
           "black line = 2020 Census county extent.", fill=(90, 90, 90), font=font(11))
    img = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
    img.save(path, optimize=True)


def render_pdf_preview(pdf_bytes, path, max_px=1400):
    doc = pypdfium2.PdfDocument(pdf_bytes)
    page = doc[0]
    w, h = page.get_size()
    scale = max_px / max(w, h)
    pil = page.render(scale=scale).to_pil().convert("RGB")
    pil = pil.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
    pil.save(path, optimize=True)
    n = len(doc)
    doc.close()
    return n, (round(w, 2), round(h, 2))


# ----------------------------------------------------------------------------- main build
def main():
    reg = json.loads((HERE / "sources.json").read_text())
    specs = {s["id"]: s for s in reg["sources"]}
    priority = reg["priority_counties_in_order"]
    fips_name = {f: n for n, f in priority}
    DERIVED.mkdir(exist_ok=True)
    PREVIEWS.mkdir(exist_ok=True)
    for old in list(DERIVED.glob("*")) + list(PREVIEWS.glob("*")):
        old.unlink()

    # priority check against the turnout worker's CSV (read-only)
    with TURNOUT.open() as f:
        trows = list(csv.DictReader(f))
    union = [(r["county"], r["county_fips"]) for r in sorted(trows, key=lambda r: int(r["rank_sen2024"]))
             if r["in_priority_union"] == "yes"]
    in80 = {r["county_fips"] for r in trows if r["in_minimum80_sen2024"] == "yes"}
    rank = {r["county_fips"]: int(r["rank_sen2024"]) for r in trows}
    assert [list(x) for x in union] == priority, (union, priority)
    all_fips_upper = {r["county"].upper(): r["county_fips"] for r in trows}

    # results rosters and SOS 2026 roster
    labels = load_results_labels()
    sos = Source(specs["statewide-sos-2026-precinct-roster"])
    roster_rows, roster_unparsed, roster_pages, roster_meta = parse_sos_roster(
        sos.raw("2026_Districts_and_Precincts_by_County.pdf"), all_fips_upper)
    with (HERE / "sos-2026-roster.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["county", "county_fips", "district", "precinct_code", "canonical_key", "page"])
        w.writeheader()
        w.writerows(roster_rows)
    sos_codes = collections.defaultdict(set)
    for r in roster_rows:
        sos_codes[r["county_fips"]].add(r["precinct_code"])

    # Census 2020 VTDs and county extents
    cen = Source(specs["statewide-census-2020-vtd"])
    z = zipfile.ZipFile(io.BytesIO(cen.raw("tl_2020_56_vtd20.zip")))
    shp = shapefile.Reader(shp=io.BytesIO(z.read("tl_2020_56_vtd20.shp")), shx=io.BytesIO(z.read("tl_2020_56_vtd20.shx")),
                           dbf=io.BytesIO(z.read("tl_2020_56_vtd20.dbf")))
    prj = z.read("tl_2020_56_vtd20.prj").decode()
    to_alb_4269 = Transformer.from_crs(CRS.from_epsg(4269), CRS.from_epsg(5070), always_xy=True)
    vtd = collections.defaultdict(list)
    for sr in shp.iterShapeRecords():
        rec = sr.record.as_dict()
        pts = sr.shape.points
        parts = list(sr.shape.parts) + [len(pts)]
        geom, anom, _ = assemble_rings([pts[parts[i]:parts[i + 1]] for i in range(len(parts) - 1)])
        vtd["56" + rec["COUNTYFP20"]].append((rec, geom))
    county_alb, county_84 = {}, {}
    for fips, items in vtd.items():
        u = shapely.union_all([shapely.make_valid(g) for _, g in items])
        county_84[fips] = u  # EPSG:4269 lon/lat, treated as CRS84 for previews only
        county_alb[fips] = to_crs(u, to_alb_4269)

    # ------------------------------------------------------------------ GIS sources
    gis_specs = [s for s in reg["sources"] if s.get("role") in ("primary-gis", "alternate-gis")]
    geometry_checks, feature_rows, recon_rows, render_joins = {}, [], [], {}
    keyed_alb = {}
    derived_info = {}
    for spec in gis_specs:
        src = Source(spec)
        fips = spec["fips"]
        kind = spec["kind"]
        paging, notes = {}, []
        if kind == "arcgis-layer":
            layer = src.json("layer.json")
            feats_raw = []
            sr = None
            exceeded = []
            for name in sorted(n for n in src.by_name if n.startswith("features-")):
                page = src.json(name)
                sr = sr or page.get("spatialReference")
                exceeded.append(bool(page.get("exceededTransferLimit", False)))
                feats_raw.extend(page["features"])
            crs, crs_label = esri_crs(layer, sr)
            oid = next((f["name"] for f in layer.get("fields", []) if f["type"] == "esriFieldTypeOID"), None)
            ids = sorted(src.json("objectids.json").get("objectIds") or [])
            got = sorted(f["attributes"].get(oid) for f in feats_raw) if oid else []
            paging = {"maxRecordCount": layer.get("maxRecordCount"),
                      "supportsPagination": (layer.get("advancedQueryCapabilities") or {}).get("supportsPagination"),
                      "returnCountOnly": src.json("count.json").get("count"), "objectIds": len(ids),
                      "features_returned": len(feats_raw), "batch_size": src.retrieval["paging"]["batch_size"],
                      "batches": len(exceeded), "exceededTransferLimit_any": any(exceeded),
                      "oid_field": oid, "returned_oids_equal_objectIds": got == ids,
                      "duplicate_oids": len(got) - len(set(got))}
            feats = []
            for f in feats_raw:
                g, anom, unc = assemble_rings((f.get("geometry") or {}).get("rings") or [])
                feats.append((f["attributes"], g, anom, unc))
            editing = layer.get("editingInfo") or {}
            paging["editingInfo"] = {k: dt.datetime.fromtimestamp(v / 1000, dt.UTC).isoformat(timespec="seconds")
                                     for k, v in editing.items() if isinstance(v, (int, float))}
            paging["layer_description"] = layer.get("description")
            paging["copyrightText"] = layer.get("copyrightText")
            native_label = crs_label
        elif kind == "topojson":
            topo = src.json(spec["topojson_request"])
            obj, all_objs, feats = topo_decode(topo, spec.get("topojson_object"))
            crs = CRS.from_user_input(spec["native_crs"])
            native_label = spec["native_crs"] + " (inferred from viewer config)"
            paging = {"static_file": True, "topology_objects": all_objs, "object_used": obj,
                      "geometries": len(feats), "quantized": "transform" in topo,
                      "transform": topo.get("transform"),
                      "content_length_header": src.by_name[spec["topojson_request"]]["headers"].get("content-length"),
                      "entity_bytes": src.by_name[spec["topojson_request"]]["entity_bytes"],
                      "last_modified": src.by_name[spec["topojson_request"]]["headers"].get("last-modified")}
        elif kind == "wfs-gml":
            meta, feats = gml_decode(src.raw("features.gml"))
            hits = safe_xml(src.raw("wfs-hits.xml"))
            caps = src.raw("wfs-capabilities.xml").decode("utf-8", "replace")
            crs = CRS.from_user_input(spec["native_crs"])
            native_label = spec["native_crs"]
            paging = {"numberMatched_hits": hits.get("numberMatched"), "numberMatched": meta["numberMatched"],
                      "numberReturned": meta["numberReturned"], "members_parsed": len(feats),
                      "ImplementsResultPaging": "ImplementsResultPaging" in caps,
                      "geometry_srsName": meta["srs"]}
        else:
            continue

        to84 = Transformer.from_crs(crs, CRS.from_user_input("OGC:CRS84"), always_xy=True)
        to_alb = Transformer.from_crs(crs, CRS.from_epsg(5070), always_xy=True)
        id_field = spec.get("id_field")
        joins = None
        if kind == "wfs-gml":
            classes = parse_sld(src.raw("wms-getstyles.sld.xml"))
            joins = render_join(src, [g for _, g, _, _ in feats], classes)
            render_joins[spec["id"]] = {"classes": [{k: v for k, v in c.items() if k != "rgb"} for c in classes],
                                        "features": joins}
        per_feature, alb_geoms, geo84 = [], [], []
        for i, (attrs, g, anom, unc) in enumerate(feats):
            raw_id = attrs.get(id_field) if id_field else (joins[i]["inferred_value"] if joins else None)
            parsed = parse_code(raw_id)
            g84 = to_crs(g, to84)
            ga = to_crs(g, to_alb)
            valid = bool(shapely.is_valid(g))
            parts, rings, verts = counts(g) if not g.is_empty else (0, 0, 0)
            per_feature.append({"i": i, "raw_id": raw_id, "parsed": parsed, "key": key_of(parsed),
                                "valid": valid, "reason": None if valid else shapely.is_valid_reason(g),
                                "empty": g.is_empty, "parts": parts, "rings": rings, "vertices": verts,
                                "unclosed_input_rings": unc, "assembly_anomalies": anom,
                                "area_km2": round(ga.area / 1e6, 6)})
            alb_geoms.append(ga)
            geo84.append((attrs, g84))
        # county containment / coverage / overlap (EPSG:5070 diagnostics; originals untouched)
        cty = county_alb.get(fips)
        cty_buf = cty.buffer(100)
        outside_rep = [pf["i"] for pf, ga in zip(per_feature, alb_geoms)
                       if not ga.is_empty and not cty_buf.contains(ga.representative_point())]
        valid_alb = [ga if pf["valid"] else shapely.make_valid(ga) for pf, ga in zip(per_feature, alb_geoms)]
        uni = shapely.union_all(valid_alb)
        cov = {"county_area_km2": round(cty.area / 1e6, 3), "layer_union_area_km2": round(uni.area / 1e6, 3),
               "layer_area_inside_county_km2": round(uni.intersection(cty).area / 1e6, 3),
               "layer_area_outside_county_km2": round(uni.difference(cty).area / 1e6, 3),
               "county_area_not_covered_km2": round(cty.difference(uni).area / 1e6, 3)}
        cov["covered_share_of_county"] = round(cov["layer_area_inside_county_km2"] / cov["county_area_km2"], 6)
        tree = STRtree([g if pf["valid"] else Polygon() for pf, g in zip(per_feature, alb_geoms)])
        pairs = []
        for a, b in zip(*tree.query([g if pf["valid"] else Polygon() for pf, g in zip(per_feature, alb_geoms)],
                                    predicate="intersects")):
            if a < b:
                area = alb_geoms[a].intersection(alb_geoms[b]).area
                if area > OVERLAP_MIN_M2:
                    pairs.append({"a": int(a), "b": int(b), "a_id": per_feature[a]["raw_id"],
                                  "b_id": per_feature[b]["raw_id"], "area_m2": round(area, 1),
                                  "same_key": per_feature[a]["key"] is not None and per_feature[a]["key"] == per_feature[b]["key"]})
        invalid = [{"i": pf["i"], "id": pf["raw_id"], "reason": pf["reason"]} for pf in per_feature if not pf["valid"]]
        dup = collections.defaultdict(list)
        for pf, (_, g, _, _) in zip(per_feature, feats):
            dup[hashlib.sha256(shapely.to_wkb(shapely.normalize(g))).hexdigest()].append(pf["i"])
        dup_groups = [{"features": v, "ids": [per_feature[i]["raw_id"] for i in v]} for v in dup.values() if len(v) > 1]
        keyed_alb[spec["id"]] = [(pf["key"], ga) for pf, ga in zip(per_feature, alb_geoms)]
        geometry_checks[spec["id"]] = {
            "county": spec["county"], "fips": fips, "role": spec["role"], "kind": kind,
            "native_crs": native_label, "native_crs_name": crs.name, "features": len(feats),
            "empty": sum(pf["empty"] for pf in per_feature), "invalid": invalid,
            "parts": sum(pf["parts"] for pf in per_feature), "rings": sum(pf["rings"] for pf in per_feature),
            "vertices": sum(pf["vertices"] for pf in per_feature),
            "unclosed_input_rings": sum(pf["unclosed_input_rings"] for pf in per_feature),
            "ring_assembly_anomalies": sum(len(pf["assembly_anomalies"]) for pf in per_feature),
            "representative_points_outside_county_100m": outside_rep,
            "coverage_vs_2020_census_county_extent": cov,
            "overlap_pairs_over_1m2": len(pairs), "overlap_total_m2": round(sum(p["area_m2"] for p in pairs), 1),
            "overlap_cross_key_pairs": sum(1 for p in pairs if not p["same_key"]),
            "overlap_cross_key_m2": round(sum(p["area_m2"] for p in pairs if not p["same_key"]), 1),
            "overlap_same_key_m2": round(sum(p["area_m2"] for p in pairs if p["same_key"]), 1),
            "overlap_pairs": sorted(pairs, key=lambda p: -p["area_m2"])[:25],
            "exact_duplicate_geometry_groups": dup_groups,
            "paging": paging,
            "bbox_crs84": [round(v, 6) for v in shapely.total_bounds(np.array([g for _, g in geo84], dtype=object))],
        }
        # derived GeoJSON (CRS84, full precision, original attributes; inferred fields prefixed)
        fc = {"type": "FeatureCollection",
              "name": spec["id"],
              "x_provenance": {"source_id": spec["id"], "county": spec["county"], "fips": fips,
                               "native_crs": native_label, "transform": f"pyproj {pyproj.__version__} / PROJ {pyproj.proj_version_str} to OGC:CRS84, always_xy",
                               "derived_by": "build.py", "simplified": False,
                               "inferred_fields": "inferred_* properties come from WMS renders and SLD colours, not the WFS" if joins else None},
              "features": []}
        for (attrs, g84), pf in zip(geo84, per_feature):
            props = dict(attrs)
            if joins:
                j = joins[pf["i"]]
                props.update({"wfs_member_index": pf["i"], "inferred_class": j["winner_class"],
                              "inferred_precinct_value": j["inferred_value"], "inferred_vote_share": j["winner_share"]})
            fc["features"].append({"type": "Feature", "properties": props, "geometry": mapping(g84)})
        dpath = DERIVED / f"{spec['id']}.geojson"
        dpath.write_text(json.dumps(fc, separators=(",", ":")) + "\n")
        derived_info[spec["id"]] = dpath
        # preview
        draw_preview(PREVIEWS / f"{spec['id']}.png",
                     f"{spec['county']} County ({fips}) - {spec['role']} - {len(feats)} features",
                     f"{spec['id']}  |  retrieved {src.retrieval['requests'][-1]['retrieved_utc'][:10]}  |  native {native_label}"
                     + ("  |  labels inferred from county WMS colours" if joins else ""),
                     [(g84, pf["key"], pf["key"]) for (_, g84), pf in zip(geo84, per_feature)],
                     county_84.get(fips), labels=True)
        # feature rows + reconciliation
        y24 = {key_of(parse_code(x)) for x in labels["2024"][fips]}
        y22 = {key_of(parse_code(x)) for x in labels["2022"][fips]}
        s26 = {key_of(parse_code(x)) for x in sos_codes[fips]}
        for pf in per_feature:
            feature_rows.append({"source_id": spec["id"], "county": spec["county"], "county_fips": fips, "role": spec["role"],
                                 "feature_index": pf["i"], "id_field": id_field or ("inferred:wms-sld" if joins else ""),
                                 "raw_id": pf["raw_id"], "district": pf["parsed"]["district"] if pf["parsed"] else "",
                                 "precinct": pf["parsed"]["precinct"] if pf["parsed"] else "",
                                 "split_or_suffix": ((pf["parsed"]["split"] + pf["parsed"]["suffix"]) if pf["parsed"] else ""),
                                 "canonical_key": pf["key"] or "", "id_is_inferred": bool(joins),
                                 "in_2024_results": pf["key"] in y24, "in_2022_results": pf["key"] in y22,
                                 "in_sos_2026_roster": pf["key"] in s26, "valid": pf["valid"],
                                 "area_km2": pf["area_km2"]})
        recon_rows.append(reconcile(spec, per_feature, labels, sos_codes, bool(joins)))

    # Alternate county layers compared with the primary, dissolved by canonical key (EPSG:5070)
    comparisons = {}
    for spec in gis_specs:
        if spec["role"] != "alternate-gis":
            continue
        prim = next(s for s in gis_specs if s["fips"] == spec["fips"] and s["role"] == "primary-gis")
        comparisons[spec["id"]] = cmp = compare_layers(keyed_alb[prim["id"]], keyed_alb[spec["id"]])
        cmp["primary"] = prim["id"]
        geometry_checks[spec["id"]]["comparison_with_primary"] = cmp
        if cmp["geometry_equivalent"]:
            # Same keys and every dissolved key differs by < 1 m2: keep the raw original, omit duplicate derivatives.
            derived_info[spec["id"]].unlink()
            (PREVIEWS / f"{spec['id']}.png").unlink()
            derived_info[spec["id"]] = None
    write_json(HERE / "layer-comparisons.json", comparisons)

    # Census VTD alternative reconciliation for every priority county
    for name, fips in priority:
        items = vtd[fips]
        pf = [{"raw_id": rec["VTDST20"], "parsed": parse_code(rec["VTDST20"], census=True)} for rec, _ in items]
        for x in pf:
            x["key"] = key_of(x["parsed"])
        spec = {"id": "statewide-census-2020-vtd", "county": name, "fips": fips, "role": "census-alternative"}
        row = reconcile(spec, pf, labels, sos_codes, False)
        row["vtd_pseudo_count"] = sum(1 for rec, _ in items if rec["VTDI20"] == "P")
        recon_rows.append(row)

    # WFS inferred labels cross-checked against Census VTD overlap (diagnostic only)
    for sid, rj in render_joins.items():
        spec = specs[sid]
        src = Source(spec)
        _, feats = gml_decode(src.raw("features.gml"))
        to_alb = Transformer.from_crs(CRS.from_user_input(spec["native_crs"]), CRS.from_epsg(5070), always_xy=True)
        vt = [(key_of(parse_code(rec["VTDST20"], census=True)), to_crs(shapely.make_valid(g), to_alb_4269))
              for rec, g in vtd[spec["fips"]]]
        agree = 0
        for j, (_, g, _, _) in zip(rj["features"], feats):
            ga = to_crs(shapely.make_valid(g), to_alb)
            best = max(vt, key=lambda kv: kv[1].intersection(ga).area)
            share = best[1].intersection(ga).area / ga.area if ga.area else 0
            j["census_vtd_max_overlap_key"] = best[0]
            j["census_vtd_max_overlap_share"] = round(share, 4)
            j["agrees_with_census_vtd"] = best[0] == key_of(parse_code(j["inferred_value"]))
            agree += j["agrees_with_census_vtd"]
        rj["agreement_with_census_vtd"] = f"{agree}/{len(rj['features'])}"
        rj["classes_matched"] = sorted({j["winner_class"] for j in rj["features"] if j["winner_class"]})
        rj["classes_unmatched"] = sorted({c["name"] for c in rj["classes"]} - set(rj["classes_matched"]))
        rj["min_winner_share"] = min(j["winner_share"] for j in rj["features"])
    write_json(HERE / "wfs-render-join.json", render_joins)

    # ------------------------------------------------------------------ PDFs
    pdf_audit = []
    for spec in reg["sources"]:
        if spec.get("role") not in ("reference-pdf", "reference-roster"):
            continue
        src = Source(spec)
        for r in src.retrieval["requests"]:
            if not r["name"].endswith(".pdf"):
                continue
            data = src.raw(r["name"])
            rd = pypdf.PdfReader(io.BytesIO(data))
            meta = {k: str(v) for k, v in (rd.metadata or {}).items()}
            prev = PREVIEWS / f"{spec['id']}--{r['name'][:-4]}.png"
            n, size_pt = render_pdf_preview(data, prev)
            boxes = sorted({(round(float(p.mediabox.width)), round(float(p.mediabox.height))) for p in rd.pages})
            pdf_audit.append({"source_id": spec["id"], "county": spec["county"], "fips": spec["fips"], "file": r["stored_path"],
                              "url": r["request_url"], "content_disposition": r["headers"].get("content-disposition"),
                              "last_modified_header": r["headers"].get("last-modified"), "sha256": r["entity_sha256"],
                              "bytes": r["entity_bytes"], "pages": len(rd.pages), "pdfium_pages": n,
                              "page_sizes_pt": boxes, "metadata": meta, "preview": rel(prev),
                              "retrieved_utc": r["retrieved_utc"]})
    write_json(HERE / "pdf-audit.json", pdf_audit)

    # Goshen has no vector layer: preview of the labeled Census alternative
    for fips in ("56015",):
        feats84 = [(g, key_of(parse_code(rec["VTDST20"], census=True)), rec["NAME20"][:14]) for rec, g in vtd[fips]]
        draw_preview(PREVIEWS / f"census-2020-vtd-{fips}.png", f"{fips_name[fips]} County ({fips}) - Census 2020 VTDs (alternative, not current precincts)",
                     "statewide-census-2020-vtd | TIGER/Line 2020 PL | pseudo VTDs flagged VTDI20=P", feats84, county_84[fips], labels=True)

    # ------------------------------------------------------------------ tables
    with (HERE / "features.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(feature_rows[0]))
        w.writeheader()
        w.writerows(feature_rows)
    rcols = list(recon_rows[0]) + ["vtd_pseudo_count"]
    with (HERE / "id-reconciliation.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rcols, extrasaction="ignore")
        w.writeheader()
        w.writerows(recon_rows)
    write_json(HERE / "geometry-checks.json", geometry_checks)

    # ------------------------------------------------------------------ county index
    by_county = collections.defaultdict(list)
    for spec in reg["sources"]:
        by_county[spec["fips"]].append(spec)
    recon_by = {(r["source_id"], r["county_fips"]): r for r in recon_rows}
    counties = []
    for name, fips in priority:
        srcs = by_county[fips]
        prim = next((s for s in srcs if s["role"] == "primary-gis"), None)
        alts = [s for s in srcs if s["role"] == "alternate-gis"]
        pdfs = [p for p in pdf_audit if p["fips"] == fips and p["source_id"] in {s["id"] for s in srcs if s["role"] == "reference-pdf"}]
        pr = recon_by.get((prim["id"], fips)) if prim else None
        cr = recon_by[("statewide-census-2020-vtd", fips)]
        status = classify(prim, pr, geometry_checks.get(prim["id"]) if prim else None, pdfs)
        counties.append({
            "rank_sen2024": rank[fips], "county": name, "fips": fips, "in_80pct_set": fips in in80,
            "status": status["status"], "status_basis": status["basis"],
            "current_cycle_evidence": prim.get("current_cycle_evidence") if prim else None,
            "primary": None if not prim else {
                "source_id": prim["id"], "kind": prim["kind"], "publisher": prim["publisher"],
                "vintage_statement": prim["vintage_statement"],
                "url": prim.get("layer_url") or Source(prim).url(prim.get("topojson_request") or "features.gml"),
                "retrieved_utc": Source(prim).retrieval["requests"][-1]["retrieved_utc"],
                "native_crs": geometry_checks[prim["id"]]["native_crs"],
                "features": geometry_checks[prim["id"]]["features"],
                "invalid": len(geometry_checks[prim["id"]]["invalid"]),
                "overlap_pairs_over_1m2": geometry_checks[prim["id"]]["overlap_pairs_over_1m2"],
                "covered_share_of_county": geometry_checks[prim["id"]]["coverage_vs_2020_census_county_extent"]["covered_share_of_county"],
                "derived_geojson": rel(derived_info[prim["id"]]), "preview": f"previews/{prim['id']}.png",
                "reconciliation": pr},
            "alternates": [{"source_id": a["id"], "features": geometry_checks[a["id"]]["features"],
                            "url": a["layer_url"] if a.get("layer_url") else None,
                            "derived_geojson": rel(derived_info[a["id"]]) if derived_info[a["id"]] else None,
                            "preview": f"previews/{a['id']}.png" if derived_info[a["id"]] else None,
                            "comparison_with_primary": {k: v for k, v in geometry_checks[a["id"]]["comparison_with_primary"].items()
                                                        if k != "by_key"},
                            "reconciliation": recon_by[(a["id"], fips)]} for a in alts],
            "pdfs": [{"file": p["file"], "pages": p["pages"], "preview": p["preview"], "url": p["url"]} for p in pdfs],
            "census_2020_vtd_alternative": cr,
        })
    write_json(HERE / "map-index.json", {"generated_by": "build.py", "priority_order": "2024 U.S. Senate contest votes (turnout.md)",
                                          "counties": counties})

    # ------------------------------------------------------------------ manifest of every file
    manifest = build_manifest(reg, specs, geometry_checks, derived_info, pdf_audit)
    write_json(HERE / "manifest.json", manifest)
    with (HERE / "manifest.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0]))
        w.writeheader()
        w.writerows(manifest)

    write_index_html(counties, reg)
    table = county_table(counties)
    update_report_table(table)
    summary = {
        "built_utc_note": "build is offline; times below come from raw/ retrieval records",
        "libraries": {"shapely": shapely.__version__, "geos": shapely.geos_version_string, "pyproj": pyproj.__version__,
                      "proj": pyproj.proj_version_str, "pyshp": shapefile.__version__, "pypdf": pypdf.__version__,
                      "pypdfium2": pypdfium2.V_PYPDFIUM2, "numpy": np.__version__},
        "read_only_inputs": {rel_wy(p): {"sha256": sha256_file(p), "bytes": p.stat().st_size} for p in (LABELS, TURNOUT)},
        "sos_roster": {"rows": len(roster_rows), "pages": roster_pages, "unparsed_lines": roster_unparsed,
                       "metadata": roster_meta,
                       "unique_codes_by_county": {f: len(v) for f, v in sorted(sos_codes.items())}},
        "census_vtd_prj": prj,
        "gis_sources": len(geometry_checks), "pdfs": len(pdf_audit), "manifest_rows": len(manifest),
        "county_status": {c["county"]: c["status"] for c in counties},
    }
    write_json(HERE / "build-summary.json", summary)
    print(table)
    print(json.dumps(summary["county_status"], indent=1))


def compare_layers(a, b, tol_m2=1.0):
    """Dissolve two [(key, geom EPSG:5070)] lists by key and compare areas, symmetric differences and IoU."""
    def dissolve(items):
        groups = collections.defaultdict(list)
        for k, g in items:
            groups[k].append(shapely.make_valid(g))
        return {k: shapely.union_all(v) for k, v in groups.items()}
    da, db = dissolve(a), dissolve(b)
    rows = []
    for k in sorted(set(da) & set(db), key=lambda x: sort_key(x) if x else (999, 999)):
        ga, gb = da[k], db[k]
        sd = ga.symmetric_difference(gb).area
        un = ga.union(gb).area
        per = (ga.length + gb.length) / 2
        rows.append({"key": k, "primary_km2": round(ga.area / 1e6, 4), "alternate_km2": round(gb.area / 1e6, 4),
                     "symmetric_difference_m2": round(sd, 1), "iou": round(ga.intersection(gb).area / un, 6) if un else None,
                     "symdiff_per_perimeter_m": round(sd / per, 3) if per else None})
    only_a = sorted(set(da) - set(db), key=str)
    only_b = sorted(set(db) - set(da), key=str)
    equivalent = (not only_a and not only_b and len(a) == len(b) and all(r["symmetric_difference_m2"] < tol_m2 for r in rows))
    return {"keys_in_both": len(rows), "keys_only_in_primary": only_a, "keys_only_in_alternate": only_b,
            "features_primary": len(a), "features_alternate": len(b),
            "max_symmetric_difference_m2": max((r["symmetric_difference_m2"] for r in rows), default=None),
            "min_iou": min((r["iou"] for r in rows if r["iou"] is not None), default=None),
            "median_symdiff_per_perimeter_m": float(np.median([r["symdiff_per_perimeter_m"] for r in rows])) if rows else None,
            "max_symdiff_per_perimeter_m": max((r["symdiff_per_perimeter_m"] for r in rows), default=None),
            "keys_with_symmetric_difference_over_1000m2": [r["key"] for r in rows if r["symmetric_difference_m2"] > 1000],
            "geometry_equivalent": equivalent, "by_key": rows}


def rel_wy(p: pathlib.Path) -> str:
    return "../" + p.relative_to(WY).as_posix()


def reconcile(spec, per_feature, labels, sos_codes, inferred):
    fips = spec["fips"]
    keys = [pf["key"] for pf in per_feature]
    kset = {k for k in keys if k}
    r24 = labels["2024"][fips]
    r22 = labels["2022"][fips]
    k24 = [key_of(parse_code(x)) for x in r24]
    k22 = {key_of(parse_code(x)) for x in r22}
    s26 = sorted(sos_codes[fips])
    k26 = {key_of(parse_code(x)) for x in s26}
    raw_strings = {str(pf["raw_id"]).strip() for pf in per_feature if pf["raw_id"] is not None}
    rebuilt24 = [x.split(":", 1)[1][5:] if x.startswith("excel-date:") else x for x in r24]
    return {
        "source_id": spec["id"], "county": spec["county"], "county_fips": fips, "role": spec["role"],
        "ids_inferred": inferred, "features": len(per_feature), "features_without_parsable_id": sum(1 for k in keys if not k),
        "distinct_keys": len(kset),
        "results2024_rows": len(r24), "results2024_rows_matched": sum(1 for k in k24 if k in kset),
        "results2024_match_rate": round(sum(1 for k in k24 if k in kset) / len(r24), 4) if r24 else None,
        "results2024_exact_string_matches": sum(1 for x in rebuilt24 if x in raw_strings),
        "results2024_missing_from_map": " ".join(sorted({k for k in k24 if k not in kset}, key=sort_key)),
        "map_keys_not_in_2024": " ".join(sorted(kset - set(k24), key=sort_key)),
        "results2022_rows": len(r22), "results2022_keys_matched": len(k22 & kset),
        "sos2026_codes": len(s26), "sos2026_codes_matched": sum(1 for x in s26 if key_of(parse_code(x)) in kset),
        "sos2026_missing_from_map": " ".join(sorted(k26 - kset, key=sort_key)),
        "map_keys_not_in_sos2026": " ".join(sorted(kset - k26, key=sort_key)),
        "results2024_vs_sos2026_key_sets_equal": set(k24) == k26,
    }


def classify(prim, pr, gc, pdfs):
    if prim is None:
        if pdfs:
            return {"status": "pdf-only (baseline vintage)", "basis": "no county vector layer found; official PDF maps retained"}
        return {"status": "none", "basis": "no county asset found"}
    full26 = pr["sos2026_codes"] > 0 and pr["sos2026_codes_matched"] == pr["sos2026_codes"] and not pr["map_keys_not_in_sos2026"]
    if pr["ids_inferred"]:
        st = "vector, IDs inferred; equal to 2026 roster" if full26 else "vector, IDs inferred; differ from 2026 roster"
    else:
        st = "vector; IDs equal 2026 roster" if full26 else "vector; IDs differ from 2026 roster"
    return {"status": st, "basis": f"{pr['distinct_keys']} distinct keys; SOS 2026 {pr['sos2026_codes_matched']}/{pr['sos2026_codes']}; "
                                   f"2024 rows {pr['results2024_rows_matched']}/{pr['results2024_rows']}"}


def build_manifest(reg, specs, geometry_checks, derived_info, pdf_audit):
    rows = []
    pdf_by_path = {p["file"]: p for p in pdf_audit}
    for spec in reg["sources"]:
        src = Source(spec)
        gc = geometry_checks.get(spec["id"])
        for r in src.retrieval["requests"]:
            name = r["name"]
            if spec.get("kind") == "arcgis-layer" and name.startswith("features-"):
                cls, fmt = "gis-original", "Esri JSON (native SR) gzip"
            elif spec.get("kind") == "topojson" and name == spec.get("topojson_request"):
                cls, fmt = "gis-original", "TopoJSON gzip"
            elif spec.get("kind") == "wfs-gml" and name == "features.gml":
                cls, fmt = "gis-original", "GML 3.2 (WFS 2.0) gzip"
            elif name.startswith("render-"):
                cls, fmt = "render-evidence", "PNG (WMS GetMap)"
            elif name.endswith(".pdf"):
                cls, fmt = ("pdf-map" if spec["role"] == "reference-pdf" else "pdf-roster"), "PDF"
            elif name.endswith(".zip"):
                cls, fmt = "census-alternative", "ZIP (shapefile)"
            elif r["http_status"] != 200:
                cls, fmt = "blocked-attempt", "HTTP response body gzip"
            else:
                cls, fmt = "provenance", ("gzip of " + name.rsplit(".", 1)[-1].upper()) if r["store"] == "gzip" else name.rsplit(".", 1)[-1].upper()
            rows.append(manifest_row(spec, cls, r["stored_path"], fmt,
                                     gc["native_crs"] if (gc and cls == "gis-original") else "",
                                     gc["features"] if (gc and cls == "gis-original") else "",
                                     r["stored_sha256"], r["stored_bytes"], r["request_url"], r["retrieved_utc"],
                                     r["http_status"], pdf_by_path.get(r["stored_path"], {}).get("pages", "")))
        if derived_info.get(spec["id"]):
            p = derived_info[spec["id"]]
            rows.append(manifest_row(spec, "derived-geojson", rel(p), "GeoJSON (OGC:CRS84, full precision)", "OGC:CRS84",
                                     gc["features"], sha256_file(p), p.stat().st_size, "", "", "", ""))
            pv = PREVIEWS / f"{spec['id']}.png"
            rows.append(manifest_row(spec, "preview", rel(pv), "PNG preview", "display only", gc["features"],
                                     sha256_file(pv), pv.stat().st_size, "", "", "", ""))
        for p in pdf_audit:
            if p["source_id"] == spec["id"]:
                pv = HERE / p["preview"]
                rows.append(manifest_row(spec, "preview", p["preview"], "PNG preview (PDF page 1)", "display only", "",
                                         sha256_file(pv), pv.stat().st_size, "", "", "", ""))
    pv = PREVIEWS / "census-2020-vtd-56015.png"
    rows.append(manifest_row(specs["statewide-census-2020-vtd"] | {"county": "Goshen", "fips": "56015"}, "preview", rel(pv),
                             "PNG preview (Census alternative)", "display only", "", sha256_file(pv), pv.stat().st_size, "", "", "", ""))
    return rows


def manifest_row(spec, cls, path, fmt, crs, features, sha, size, url, when, status, pages):
    return {"county": spec["county"], "fips": spec["fips"], "source_id": spec["id"], "role": spec["role"],
            "asset_class": cls, "local_path": path, "format": fmt, "crs": crs, "feature_count": features,
            "pdf_pages": pages, "sha256": sha, "bytes": size, "source_url": url, "http_status": status,
            "retrieved_utc": when, "publisher": spec.get("publisher", ""),
            "vintage_statement": spec.get("vintage_statement", "")}


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


def update_report_table(table):
    if not REPORT.exists():
        return
    text = REPORT.read_text()
    if TABLE_BEGIN in text and TABLE_END in text:
        a = text.index(TABLE_BEGIN) + len(TABLE_BEGIN)
        b = text.index(TABLE_END)
        REPORT.write_text(text[:a] + "\n" + table + "\n" + text[b:])


def write_index_html(counties, reg):
    h = ["<!doctype html><html lang='en'><meta charset='utf-8'><title>Wyoming precinct map index</title>",
         "<style>body{font-family:system-ui,sans-serif;margin:1.5rem;max-width:1100px}figure{display:inline-block;margin:.4rem;"
         "vertical-align:top;width:300px}img{width:300px;border:1px solid #ccc}section{border-top:1px solid #999;margin-top:1rem}"
         "code{font-size:.85em}</style>",
         "<h1>Wyoming 2026 Senate research: precinct map index</h1>",
         "<p>Offline index of retained county precinct assets for the 15-county priority set (2024 U.S. Senate contest votes). "
         "Previews are generated research aids, not official maps. See <a href='../precinct-maps.md'>precinct-maps.md</a>, "
         "<a href='manifest.csv'>manifest.csv</a> and <a href='map-index.json'>map-index.json</a>.</p>"]
    for c in counties:
        h.append(f"<section><h2>{c['rank_sen2024']}. {html.escape(c['county'])} ({c['fips']})"
                 f"{' - 80% set' if c['in_80pct_set'] else ''}</h2><p><b>{html.escape(c['status'])}</b>. "
                 f"{html.escape(c['status_basis'])}</p>")
        if c["primary"]:
            p = c["primary"]
            h.append(f"<figure><a href='{p['preview']}'><img src='{p['preview']}' alt='preview'></a><figcaption>Primary "
                     f"<code>{p['source_id']}</code>: {p['features']} features; <a href='{p['derived_geojson']}'>GeoJSON</a>; "
                     f"<a href='{html.escape(p['url'])}'>source</a></figcaption></figure>")
        for a in c["alternates"]:
            if a["preview"]:
                h.append(f"<figure><a href='{a['preview']}'><img src='{a['preview']}' alt='preview'></a><figcaption>Alternate "
                         f"<code>{a['source_id']}</code>: {a['features']} features; <a href='{a['derived_geojson']}'>GeoJSON</a></figcaption></figure>")
            else:
                h.append(f"<p>Alternate <code>{a['source_id']}</code>: {a['features']} features, geometry-equivalent to the primary "
                         f"(max symmetric difference {a['comparison_with_primary']['max_symmetric_difference_m2']} m&sup2;); raw original retained, "
                         f"no duplicate derivative.</p>")
        for p in c["pdfs"]:
            h.append(f"<figure><a href='{p['file']}'><img src='{p['preview']}' alt='PDF preview'></a><figcaption>PDF "
                     f"<a href='{p['file']}'>{html.escape(pathlib.Path(p['file']).name)}</a> ({p['pages']} p.)</figcaption></figure>")
        if c["fips"] == "56015":
            h.append("<figure><img src='previews/census-2020-vtd-56015.png' alt='Census VTD preview'><figcaption>Census 2020 VTDs "
                     "(labeled alternative, not current precincts)</figcaption></figure>")
        h.append("</section>")
    (HERE / "index.html").write_text("\n".join(h) + "\n</html>\n")


if __name__ == "__main__":
    main()
