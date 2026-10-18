"""Verify retained newsroom observations and isolate test/old products."""
import gzip,hashlib,json,pathlib,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 rows=json.loads((ROOT/'manifest.json').read_text())
 by_id={r['id']:r for r in rows}
 for r in rows:
  if not r.get('asset'):continue
  stored=(ROOT/r['asset']).read_bytes();raw=gzip.decompress(stored)
  assert sha(stored)==r['stored_sha256'] and sha(raw)==r['raw_sha256']
 def raw(name):return gzip.decompress((ROOT/by_id[name]['asset']).read_bytes())
 xml=[]
 for source_id in ['wptv-published-xml','wtxl-published-xml']:
  root=ET.fromstring(raw(source_id));races=root.findall('RACE')
  race_rows=[]
  for ordinal,race in enumerate(races):
   info={x.tag:x.text for x in race.find('RACE_INFO')}
   candidates=[{x.tag:x.text for x in row} for row in race.findall('CANDIDATE_INFO/CANDIDATE')]
   race_rows.append({'ordinal':ordinal,'race_info':info,'candidates':candidates})
  parent='wptv-results-current' if source_id.startswith('wptv') else 'wtxl-results-current'
  has_notice='testing purposes' in raw(parent).decode()
  if source_id.startswith('wptv'):assert has_notice
  xml.append({'source_id':source_id,'parent_source_id':parent,'root_clocks':[{x.tag:x.text} for x in root if x.tag!='RACE'],'race_count':len(races),'all_race_positions':race_rows,'parent_original_has_explicit_test_notice':has_notice,'admission':'excluded_parent_explicit_test_notice' if has_notice else 'excluded_zero_setup_no_genuine_November_counts'})
 assert len(xml[0]['all_race_positions'])==144 and len(xml[1]['all_race_positions'])==4
 widget=json.loads(raw('wesh-august-local-widget'))
 results=widget['results']
 assert results
 out={'status':'pass_original_hashes_and_exclusion','capture_count':len(rows),'entity_count':sum(bool(r.get('asset')) for r in rows),'scripps_xml':xml,'wtxl_magis_body_literal':raw('wtxl-magis-observed').decode(),'wesh_primary_widget':{'items':len(results),'titles':[x.get('title') for x in results],'publisher_times':[x.get('last_updated') for x in results],'sources':[x.get('source') for x in results],'current_november_admitted':False},'genuine_november_counts_admitted':False,'scope':'Actual published routes only; test parent overrides fresh source clock/positive counts. Newsroom candidate keys are not ballot authority or ENR identities. Separate official publications verify the printed three; no genuine November count admission.'}
 (ROOT/'inspection.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k not in ['scripps_xml','wesh_primary_widget']}))
if __name__=='__main__':main()
