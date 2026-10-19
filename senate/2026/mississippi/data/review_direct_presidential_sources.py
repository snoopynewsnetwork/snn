"""Original-bound Tunica/Perry nine-field proof; provisional aids excluded."""
from pathlib import Path
import gzip,hashlib,json

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
DEST=DATA/'coordinator-qa/direct-presidential-two-sources'
NAMES=['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump',
       'Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski']
# Coordinator directly read complete original Perry PDF2/3, including the
# full header grid, before looking at the newly supplied worker field ledger.
PERRY={2:[
 [64,296,26,4,33,14,76,118,49,78,72],
 [1,0,0,0,1,0,1,0,0,0,0],
 [1,2,0,0,1,0,1,0,0,0,0],
 [0,0,0,0,0,1,0,0,0,1,0],
 [407,97,107,118,181,68,196,247,483,33,82],
 [0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,1,0,0,0,0,0,0],
 [1,0,1,0,1,0,0,1,1,1,0],
 [0,0,0,0,0,0,0,0,0,0,0]],3:[
 [11,109,76,48,4,1078],[0,3,1,1,0,8],[0,1,1,1,0,8],
 [0,0,2,0,0,4],[155,1072,205,913,61,4425],[0,2,1,1,0,4],
 [0,1,0,0,0,2],[0,0,2,1,0,9],[0,0,1,0,0,1]]}
EXPECTED={
 'tunica-presidential-original-readings.json':'12582c174ded1c9950647525b5b410c0bf3f3650f13558909a3d81e99fef2e9f',
 'perry-presidential-original-readings.json':'4abc9b14489ec71d8d1c816040d5c2116cab739f46345e8247131e52a5c239e0',
 'direct-presidential-two-source-reconciliation.json':'bd69f2147763d996d61844d8949088524fd5a0d5cefb371781e9eda99c06dfa4'}
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}
def main():
 DEST.mkdir(exist_ok=True);snapshots=[];ledgers={}
 for name,expected in EXPECTED.items():
  path=DEST/(name+'.gz')
  if not path.exists():
   raw=(DATA/'turnout'/name).read_bytes();assert raw==(DATA/'turnout'/name).read_bytes()
   path.write_bytes(gzip.compress(raw,mtime=0))
  raw=gzip.decompress(path.read_bytes());assert sha(raw)==expected
  ledgers[name]=json.loads(raw);snapshots.append(pin(path)|{'raw_sha256':sha(raw),'raw_bytes':len(raw)})
 original_tk_path=DATA/'coordinator-qa/tunica-kemper-allfield-readings-snapshot.json.gz'
 original_tk=json.loads(gzip.decompress(original_tk_path.read_bytes()))
 prior=next(s for s in original_tk['sources']if s['source_id']=='sos-2024-county-tunica')
 tunica={p['page']:[list(f['values']) for f in p['fields']if f['candidate']in NAMES]for p in prior['pages']}
 for matrix in tunica.values():
  for vector in matrix:
   while vector and vector[-1] is None:vector.pop()
 own={'sos-2024-county-tunica':tunica,'sos-2024-county-perry':PERRY}
 source_pins=[];evidence={};results=[];positions=0
 receipts=json.loads((DATA/'turnout/source/acquisition.json').read_bytes())
 for county in ['tunica','perry']:
  ledger=ledgers[county+'-presidential-original-readings.json'];sid=ledger['source_id']
  receipt=next(r for r in receipts if r['id']==sid);stored=(ROOT/receipt['path']).read_bytes();raw=gzip.decompress(stored)
  assert sha(stored)==receipt['stored_sha256']and sha(raw)==receipt['raw_sha256']==ledger['source_raw_sha256']
  source_pins.append(receipt)
  vectors=own[sid];seen=set()
  for page in ledger['pages']:
   p=page['page'];assert page['candidate_values']==dict(zip(NAMES,vectors[p]))
   path=ROOT/page['render_path'];assert pin(path)['sha256']==page['render_sha256'];evidence[str(path.relative_to(ROOT))]=pin(path)
  for row in ledger['rows']:
   key=(row['source_page'],row['source_column'],row['candidate']);assert key not in seen;seen.add(key)
   assert row['source_raw_sha256']==sha(raw)
   value=vectors[key[0]][NAMES.index(key[2])][key[1]-1]
   assert row['direct_original_visual_value']==value;positions+=1
  total_page=max(vectors)
  totals={name:vectors[total_page][i][-1]for i,name in enumerate(NAMES)}
  sums={name:sum(vectors[p][i][c]for p in vectors for c in range(len(vectors[p][i])-(p==total_page)))for i,name in enumerate(NAMES)}
  assert sums==totals
  assert ledger['source_TOTAL_count']==1 and ledger['source_native_count']==(12 if county=='tunica' else 16)
  assert len(seen)==(117 if county=='tunica' else 153)
  for candidate,c in ledger['candidate_checks'].items():assert c['native_sum']==c['printed_TOTAL']==totals[candidate]
  results.append({'source_id':sid,'native_columns':ledger['source_native_count'],'physical_TOTAL_columns':1,
    'numeric_candidate_positions':len(seen),'own_independent_original_candidate_vectors':vectors,
    'source_native_sums':sums,'source_printed_TOTALs':totals})
 assert positions==270
 proof=ledgers['direct-presidential-two-source-reconciliation.json']
 assert proof['peer_tunica_original_readings_sha256']==sha(gzip.decompress(original_tk_path.read_bytes()))
 for source in proof['sources']:
  accepted=next(r for r in results if r['source_id']==source['source_id'])
  assert source['native_constituents']==accepted['native_columns']and source['candidate_positions']==accepted['numeric_candidate_positions']
  for c in source['candidate_controls']:
   assert c['original_native_sum']==c['original_printed_TOTAL']==accepted['source_printed_TOTALs'][c['candidate']]
   expected=1 if source['county']=='tunica' and c['candidate']=='Kamala D. Harris' else 0
   assert c['source_to_CSV_difference']==expected
 out={'status':'pass_bounded_270_original_presidential_numeric_positions_two_sources',
      'frozen_worker_proofs':snapshots,'source_receipts':source_pins,'prior_original_Tunica_witness':pin(original_tk_path),
      'source_results':results,'native_columns':28,'physical_TOTAL_columns':2,'numeric_positions':270,
      'worker_original_evidence':list(evidence.values()),
      'coordinator_original_Perry_evidence':[pin(DATA/f'coordinator-qa/presidential-aid-leads-v1/perry-independent-original-p{p}-upright.png')for p in [2,3]],
      'source_minus_county_Tunica_Harris':-1,'county_minus_source_Tunica_Harris':1,
      'qualification':'All9 source-native candidate vectors from each of two original packets close their own printed TOTAL. Perry was directly reread from fresh whole original pages; Tunica agrees with the prior complete-original coordinator witness. Provisional18,980-cell aids are not inputs or accepted replacements. Reading boxes across independent render scales remain distinct. Unused template columns, generic marks, methods and unprinted under/over are not inferred. Tunica Harris1836 versuscounty1837 remains unallocated, separate from its Senate discrepancy. No statewide presidential/historical-native/method gate, source-vintage/geographic join, current approval or native887 dispatch is accepted.'}
 (DATA/'coordinator-direct-presidential-two-source-review.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'numeric_positions':positions,'native_columns':28}))
if __name__=='__main__':main()
