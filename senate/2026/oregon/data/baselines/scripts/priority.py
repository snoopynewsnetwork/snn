"""Historical county and known-native complete descending orders; no approved dispatch."""
import csv,json,gzip,hashlib,re,datetime
from pathlib import Path
from county import R,SPECS,COUNTIES,text,js,csvout

def rank(rows):
 rows=sorted(rows,key=lambda r:(-r['votes'],r['key']));den=sum(r['votes'] for r in rows);target=(4*den+4)//5;cum=0;cross=None
 for i,r in enumerate(rows,1):
  before=cum;cum+=r['votes'];r.update(rank=i,cumulative_votes=cum,weight=r['votes']/den,cumulative_share=cum/den)
  if cross is None and cum>=target:cross={'minimum_units':i,'previous_cumulative_votes':before,'crossing_cumulative_votes':cum,'threshold_ceiling_integer':target}
 return rows,{'denominator':den,'unit_count':len(rows),'top15_votes':sum(r['votes'] for r in rows[:15]),'top15_share':sum(r['votes'] for r in rows[:15])/den,'exact80':cross,'full_order_sha256':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}
def main():
 wide=list(csv.DictReader((R.parent/'county-baselines.csv').open()));rs=[{'key':r['county'],'votes':int(r['reported_all_choice_votes'])} for r in wide if r['contest']=='2024-president'];order,c=rank(rs);csvout('county-priority-order.csv',order)
 n=[{'key':r['unit_key'],'county':r['county'],'label':r['unit_label'],'votes':r['reported_all_choice_votes']} for r in json.loads((R/'native-units.json').read_text()) if r['contest']=='2024-president' and not r['missing_candidate_columns'] and r['source_key']!='multnomah-2024-president']
 # All five parents independently close all eight columns. No other scope is substituted.
 order,k=rank(n);csvout('known-native-order.csv',order)
 js('priority-contract.json',{'priority_basis':'actual2024 president, all reported choices including generic Misc.','canonical_statewide_native_order':None,'canonical_top15':None,'canonical_minimum80':None,'known_native_only':k,'county_sensitivity_only':c,'native_closed_parents':['Clackamas','Marion','Multnomah','Wasco','Washington'],'unclosed_native_parents':[c for c in COUNTIES if c not in ['Clackamas','Marion','Multnomah','Wasco','Washington']],'accepted':False,'geography_accepted':False,'current_source_accepted':False})
 # Full original-page inventory retains identity evidence without extracting unrelated offices.
 inv=json.loads((R/'source/independent-original-inventory.json').read_text());index=[]
 for r in inv:
  if r['kind']!='PDF':continue
  for p,page in enumerate(text(r['source_key']).split('\f')[:-1],1):
   refs=[{'path':r['text_path'],'page':p,'kind':'independent Poppler text'}];identities=[]
   original=page
   if len(page.strip())<30:
    for folder in ['refined-ocr','ocr']:
     f=R.parent/'turnout/source'/folder/f"{r['source_key']}-p{p:03}.txt.gz"
     if f.exists():page=gzip.decompress(f.read_bytes()).decode(errors='replace');refs.append({'path':str(f.relative_to(R.parent.parent)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'kind':'retained OCR source transformation'});break
   for ln,line in enumerate(page.splitlines(),1):
    if re.search(r'Precinct|Absentee|Election Day|Early Voting|Central|Vote by Mail|Reporting Group|Ballot Style|ScanStation|Counter Group|STATISTICS|All Precincts',line,re.I):identities.append({'line':ln,'raw_line':line})
   index.append({'source_key':r['source_key'],'page':p,'original_sha256':r['raw_sha256'],'text_or_OCR_refs':refs,'identity_method_administrative_lines':identities,'required_candidate_text_present':bool(re.search('Merkley|Wyden|Drazan|Harris',page,re.I)),'qualification':'literal text/OCR evidence; unmatched/source-masked identities remain unresolved; text search absence is not source absence'})
 (R/'source/whole-original-page-index.jsonl.gz').write_bytes(gzip.compress((''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in index)).encode(),mtime=0))
 witness_files=['county-candidates.csv','native-units.json','native-reconciliation.json','participation-controls.csv','monthly-registration.csv','priority-contract.json','known-native-order.csv','county-priority-order.csv','source/independent-original-inventory.json','source/original-read-receipts.json','source/abstract-evidence.json','source/ocr-pins.json','source/raw-native-pages.jsonl.gz','source/raw-native-rows.jsonl.gz','source/whole-original-page-index.jsonl.gz','source/visual-readings.json']
 p=R/'source/pre-peer-witness.json'
 if not p.exists():
  rows=[]
  for name in witness_files:
   f=R/name;rows.append({'path':name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
  f=R.parent/'county-baselines.csv';rows.append({'path':'../county-baselines.csv','bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
  js('source/pre-peer-witness.json',{'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':'independent original-first source extraction completed before opening turnout numeric/control/order/transcription derivatives','peer_actual_id':'bd151c4c-70ea-4b72-9063-2012086b07e6','peer_status_at_launch':'finished; not contacted/restarted','files':rows})
 print(json.dumps({'known_native':k,'county':c,'pre_peer_witness_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
