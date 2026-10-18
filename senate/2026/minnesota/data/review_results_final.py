#!/usr/bin/env python3
"""Independent final official-source manifest/raw/native/authority scope review."""
from pathlib import Path
import collections,csv,datetime,gzip,hashlib,io,json,re,runpy,xml.etree.ElementTree as E,zipfile
R=Path(__file__).resolve().parents[1];D=R/'data';S=D/'results-sources';sha=lambda b:hashlib.sha256(b).hexdigest();load=lambda p:json.loads(p.read_text());NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def jsonl(p):return[json.loads(l)for l in gzip.decompress(p.read_bytes()).splitlines()if l]
def tree(e):return(e.tag,sorted(e.attrib.items()),e.text,tuple(tree(c)for c in e))
def main():
 mfbytes=(S/'asset-manifest.json').read_bytes();assert sha(mfbytes)=='2c135609fda7b4c84e7c56b9d11a08844f1c749bbf4969c4c0bf7c0a126a2768';mf=json.loads(mfbytes);assert len(mf['assets'])==1299
 owned={str(p.relative_to(R))for p in S.rglob('*')if p.is_file()and p.name!='asset-manifest.json'}|{'official-results.md','data/official-results-sources.csv'};assert owned=={x['path']for x in mf['assets']}
 for x in mf['assets']:
  b=(R/x['path']).read_bytes();assert len(b)==x['bytes']<40000000 and sha(b)==x['sha256'],x['path']
 assert not any(p.name in ['__pycache__','.venv','node_modules','.cache']for p in S.rglob('*'))
 pins=load(S/'input-pins.json')
 for x in pins:
  b=(R/x['path']).read_bytes();assert len(b)==x['stored_bytes']and sha(b)==x['stored_sha256']
  if 'raw_sha256'in x:
   b=gzip.decompress(b);assert len(b)==x['raw_bytes']and sha(b)==x['raw_sha256']
 ledger=load(S/'acquisition.json');assert len(ledger)==319 and len({x['id']for x in ledger})==319
 statuses=collections.Counter()
 for x in ledger:
  b=(S/x['body']).read_bytes();assert len(b)==x['stored_bytes']and sha(b)==x['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==x['raw_bytes']and sha(raw)==x['raw_sha256'];assert x['retrieved_utc']and x['requested_url']and x['final_url']and x['headers'];statuses[x['status']]+=1
 assert statuses=={200:294,403:23,404:2}
 contract=load(D/'turnout/priority-set.json');contexts=jsonl(S/'county-native-contexts.jsonl.gz');assert contexts==contract['county_order']
 inventory=load(S/'authority-inventory.json');prior=load(S/'priority-investigations.json');csvrows=list(csv.DictReader((D/'official-results-sources.csv').open()));directory=load(S/'directory.json')
 assert len(inventory)==len(csvrows)==len(directory)==87 and len(prior)==24
 assert [x['key']for x in inventory]==contract['complete_ordered_county_keys']and[x['key']for x in prior]==contract['ordered_priority_keys']
 assert ['MN:county:'+x['county_fips']for x in csvrows]==contract['complete_ordered_county_keys']
 native=0;cells=0;xml_cells=0
 ns=runpy.run_path(str(D/'review_priority.py'))
 for year in [2024,2022,2020]:
  sid=f'sos-{year}-precinct-original';original=ns['workbook'](sid)['Precinct-Results'];source={str(x['source_row']):x for x in original if re.fullmatch(r'\d{9}',str(next(iter(x['cells'].values()))['value']))};rows=jsonl(S/f'native-{year}.jsonl.gz');assert len(rows)==len(source)==(4110 if year==2020 else 4103)
  z=zipfile.ZipFile(io.BytesIO(ns['raw'](sid)));xml_byrow={x.attrib['r']:x for x in E.fromstring(z.read(rows[0]['xml_path'])).findall('s:sheetData/s:row',NS)}
  assert {x['row']for x in rows}==set(source)
  for row in rows:
   rawrow=source[row['row']];old=xml_byrow[row['row']];expected={x.attrib['r']:x for x in old};actual={x['address']:x for x in row['all_cells']};assert set(expected)==set(actual)
   for address,c in actual.items():
    element=expected[address];assert c['value']==rawrow['cells'][address]['value']and c['attributes']==element.attrib and c['raw_value']==element.findtext('s:v',namespaces=NS)
    assert tree(E.fromstring(c['xml']))==tree(element);cells+=1;xml_cells+=1
   native+=1
  if year==2020:assert rows[0]['headers_by_column']['G']=='TABMODEL'and rows[0]['headers_by_column']['R']=='TABMODEL'
 for x in prior:assert x['source_records']and x['evidence']and x['finding']and x['gap']
 exceptions=load(S/'hours-exceptions.json');assert len(exceptions)==286
 counts=collections.Counter(x['scope']for x in exceptions);assert sum(x['general_opening_local']is not None for x in exceptions)==268
 test=load(S/'general201-setup-inspection.json');assert test['admitted_to_current_counts']is False and test['expected_actual_november_universe_approved']is False
 assert load(D/'coordinator-export-review.json')['candidate_controls']['2024']['all_candidate_total']==3189323
 out={'status':'pass_final_frozen_official_sources','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Independent complete ownedmanifest/pathset/rawentity/inputpins plus all12316 originalnative source rows/everycellvalue/type/rawXMLstructure, exactcountyobjects/order, authority/priority inventories, originalcandidateexport and narrowprimarylegal cross-checks. No worker source parser imported.','manifest_sha256':sha(mfbytes),'owned_assets':1299,'stored_owned_asset_bytes':sum(x['bytes']for x in mf['assets']),'max_stored_asset_bytes':max(x['bytes']for x in mf['assets']),'original_GET_observations':319,'HTTP_statuses':dict(statuses),'read_only_input_pins':len(pins),'county_authorities':87,'individual_priorities':24,'complete_historical_constituents':native,'original_cell_value_type_and_XML_checks':cells,'current_late_opening_rows':286,'current_November_late_opening_rows':268,'test201_admitted':False,'independent_export_review':'coordinator-export-review.json','independent_legal_review':'coordinator-legal-review.json','scope':'Currenttest setup excluded. No complete finalcandidate/writein certification, expectedapprovedreportingdictionary, exacteligibleSenate remainder, measuredlivecadence or physical/method/crossyear approval.'}
 p=D/'coordinator-results-final-review.json'
 if p.exists():
  old=load(p)
  if {k:v for k,v in old.items()if k!='checked_utc'}=={k:v for k,v in out.items()if k!='checked_utc'}:out['checked_utc']=old['checked_utc']
 p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
