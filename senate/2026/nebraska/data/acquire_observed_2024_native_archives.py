"""Bounded93 actual CDX-returned primary native pages; retain archive defects."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.parse import urlsplit,parse_qs
import gzip,hashlib,importlib.util,json

DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
def main():
 spec=importlib.util.spec_from_file_location('ne_source_fetch',NEWS/'fetch_evidence.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 catalog_path=NEWS/'sos-2024-observed-native-special-pages-cdx.html.gz'
 raw=gzip.decompress(catalog_path.read_bytes());catalog=json.loads(raw)
 observations=[dict(zip(catalog[0],r))for r in catalog[1:]]
 assert len(observations)==93
 manifest_path=NEWS/'manifest.json';manifest=json.loads(manifest_path.read_bytes())
 prior={r['id']:r for r in manifest};seen=set();todo=[]
 for entry in observations:
  parsed=urlsplit(entry['original']);query=parse_qs(parsed.query)
  assert parsed.hostname=='electionresults.nebraska.gov'and parsed.path.lower()=='/resultsprec.aspx'
  assert query['type']==['SW']and query['rid']==['12464']and query['osn']==['102']and query['map']==['PREC']
  cty=query['cty'][0];assert cty not in seen;seen.add(cty)
  key='sos-2024-special-native-archive-cty-'+cty
  url='https://web.archive.org/web/'+entry['timestamp']+'id_/'+entry['original']
  if key in prior:continue
  todo.append((key,url,entry,cty))
 def one(item):
  key,url,entry,cty=item
  row=module.fetch((key,url))
  row.update(discovery_basis='Exact primary URL and timestamp returned by actual observed resultsPREC/rid12464 CDX catalog; historical capture only, not current geography or final certification.',
             archive_record=entry,historical_county_id_literal=cty)
  return row
 with ThreadPoolExecutor(max_workers=4)as pool:
  jobs=[pool.submit(one,item)for item in todo]
  for count,future in enumerate(as_completed(jobs),1):
   row=future.result();manifest.append(row);prior[row['id']]=row
   manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
   if count%10==0 or count==len(jobs):print('retained',count,'of',len(jobs),flush=True)
 selected=[]
 for row in manifest:
  if not row['id'].startswith('sos-2024-special-native-archive-cty-'):continue
  body=gzip.decompress((NEWS/row['asset']).read_bytes())if row.get('asset')else b''
  warning=row.get('headers',{}).get('warning','')
  truncated='truncat'in warning.lower()
  closed=b'</html>'in body.lower()
  row['archive_entity_completeness']={'declared_archive_truncation_warning':warning or None,
    'archive_truncated_by_length':truncated,'HTML_closing_tag_present':closed,
    'complete_entity_claimed':row.get('status')==200 and closed and not truncated,
    'qualification':'A successful200 archive response can be a capture truncated by length. Candidate-position completeness must be checked separately; no missing row is zero.'}
  selected.append({'id':row['id'],'status':row.get('status'),'bytes':row.get('bytes'),
                   **row['archive_entity_completeness']})
 manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
 report={'catalog_path':str(catalog_path.relative_to(DATA.parent)),
         'catalog_raw_sha256':hashlib.sha256(raw).hexdigest(),'catalog_observations':93,
         'source_captures':selected,'qualification':'Source recovery only; no all-state native/candidate completeness, accepted ranking or current identity follows. Raw entities/receipts remain original and error bodies are retained.'}
 (DATA/'coordinator-2024-native-archive-acquisition.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'observations':len(selected),'HTTP200':sum(r['status']==200 for r in selected),
  'complete_HTML_entities':sum(r['complete_entity_claimed']for r in selected),
  'declared_truncations':sum(r['archive_truncated_by_length']for r in selected)}),flush=True)
if __name__=='__main__':main()
