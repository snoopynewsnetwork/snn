#!/usr/bin/env python3
"""Coordinator independently verifies original OOXML positions and dispatch scopes."""
from pathlib import Path
from collections import Counter, defaultdict
import datetime, gzip, hashlib, io, json, runpy, zipfile
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';TURNOUT=DATA/'turnout'
def sha(b):return hashlib.sha256(b).hexdigest()
def rows(p):return [json.loads(x) for x in gzip.decompress(p.read_bytes()).splitlines()]
ns=runpy.run_path(str(DATA/'preflight_primary_sources.py'))
units=rows(TURNOUT/'extracts/native-units.jsonl.gz')
observations=rows(TURNOUT/'extracts/candidate-observations.jsonl.gz')
controls=rows(TURNOUT/'extracts/county-summary-observations.jsonl.gz')
assert len(units)==22031 and len({u['unit_key']for u in units})==22031
assert len(observations)==121053
original={};n={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
for source in {u['source_id']for u in units}:
    z=zipfile.ZipFile(io.BytesIO(ns['raw'](source)));assert z.testzip()is None
    ss=[''.join(t.itertext())for t in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',n)]if'xl/sharedStrings.xml'in z.namelist()else[]
    sheets={u['xml_path']:u['sheet']for u in units if u['source_id']==source}
    for path,sheetname in sheets.items():
        cellmap={}
        for row in E.fromstring(z.read(path)).findall('m:sheetData/m:row',n):
            for cell in row:
                v=cell.find('m:v',n);value=v.text if v is not None else None
                if cell.get('t')=='s':value=ss[int(value)]
                elif cell.get('t')=='inlineStr':value=''.join(cell.find('m:is',n).itertext())
                cellmap[cell.get('r')]=value
        original[(source,sheetname)]=cellmap
for row in observations+controls:
    cell=f"{row['column']}{row['row']}"
    assert cell==row['cell']
    assert original[(row['source_id'],row['sheet'])].get(cell)==row['raw_value'],(row['source_id'],row['sheet'],cell)
grouped=defaultdict(list)
for row in observations:grouped[row['unit_key']].append(row)
families=defaultdict(list);unknown=Counter()
for u in units:
    fields=[u['source_id'],u['sheet'],u['county_native'],u['native_id_fields']]
    assert u['unit_key']==u['source_id']+':'+sha(json.dumps(fields,ensure_ascii=False,separators=(',',':')).encode())[:24]
    data=grouped[u['unit_key']];named=[r for r in data if r['category']=='named_candidate']
    missing=sum(r['votes']is None for r in named)
    numeric=sum(r['votes']for r in named if r['votes']is not None)
    assert missing==u['unknown_named_cells'] and numeric==u['named_candidate_numeric_sum']
    assert u['named_candidate_total']==(None if missing else numeric)
    assert u['geometry_status']=='unverified_historical_identity'
    families[(u['county_fips'],u['source_id'])].append(u)
    unknown[u['source_id']]+=bool(missing)
contract_bytes=(TURNOUT/'priority-set.json').read_bytes()
contract=json.loads(contract_bytes);actual=[]
fields=['unit_key','sheet','xml_path','source_rows','native_label','native_id_fields','named_candidate_total','unknown_named_cells','role','method','geometry_status']
for county in contract['all_geography_coverage']:
    assert county['current_2026_crosswalk_approval']=='unavailable; no name/count equivalence asserted'
    assert len(county['source_native_families'])==5
    for family in county['source_native_families']:
        expected=families[(county['county_fips'],family['source_id'])]
        assert family['constituents']==[{k:u[k]for k in fields}for u in expected]
        assert [u['unit_key']for u in family['unavailable_cases']]==[u['unit_key']for u in expected if u['unknown_named_cells']]
        assert 'overlapping' in family['relationship_to_other_source_families']
        actual.extend(u['unit_key']for u in family['constituents'])
assert len(actual)==len(set(actual))==22031 and set(actual)=={u['unit_key']for u in units}
assert dict(unknown)=={'sos-2024-president-county':0,'sos-2024-president-precinct':13,'sos-2022-senate-precinct':12,'sos-2020-senate-precinct':19,'sos-2026-senate-primary-precinct':31}
assert len({(u['county_fips'],u['source_id'])for u in units})==525
assert (TURNOUT/'priority-set.json').read_bytes()==contract_bytes, 'Contract changed during audit; rerun on stable input.'
result={'status':'pass','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':'Exact historical native key/object conservation and original OOXML source positions only; no current geographic approval, deduplication or residual allocation.',
        'source_scoped_native_identities':22031,'source_families':5,'county_family_groups':525,
        'candidate_and_total_original_cells':len(observations),'county_footer_original_cells':len(controls),
        'contract_constituent_fields_per_identity':len(fields),'unavailable_count_units':dict(unknown),
        'input_hashes':{'turnout/priority-set.json':sha(contract_bytes), **{str(p.relative_to(DATA)):sha(p.read_bytes())for p in [TURNOUT/'extracts/native-units.jsonl.gz',TURNOUT/'extracts/candidate-observations.jsonl.gz']}},
        'retained_source_gaps':['Detail/control residuals and blank/redacted counts remain unallocated.','County footers and overlapping alternate families are not summed with reporting detail.','Native source-key hashes identify historical rows, not authoritative physical precinct IDs.']}
out=DATA/'coordinator-native-contract-checks.json'
if out.exists():
    previous=json.loads(out.read_text())
    if {k:v for k,v in previous.items()if k!='checked_utc'}=={k:v for k,v in result.items()if k!='checked_utc'}:result['checked_utc']=previous['checked_utc']
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
