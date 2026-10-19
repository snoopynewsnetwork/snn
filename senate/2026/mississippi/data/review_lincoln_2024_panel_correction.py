"""Verify the owned source correction against original evidence and retained old bytes."""
from pathlib import Path
import copy,gzip,hashlib,json

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/lincoln-2024-original-panels'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 hp=DATA/'turnout/source/2024-lincoln-ballots-original-correction-v1/correction-history.json';h=json.loads(hp.read_bytes());assert pin(hp)['sha256']=='a3194bc8b06c052b6bc9cc28e66aa58d0c9b50124b787af84671986bc4ea8214';bodies={}
 for k,p in h['frozen_initial_artifacts'].items():
  if p.get('stored_path'):
   z=(ROOT/p['stored_path']).read_bytes();b=gzip.decompress(z);assert len(z)==p['stored_bytes']and sha(z)==p['stored_sha256']and len(b)==p['raw_bytes']and sha(b)==p['raw_sha256'];bodies[k]=b
  else:assert pin(ROOT/p['original_path'])['sha256']==p['raw_sha256']and pin(ROOT/p['original_path'])['bytes']==p['raw_bytes']
 assert len(bodies)==11 and bodies['initial_reading']==gzip.decompress((QA/'initial-worker-readings.json.gz').read_bytes())
 p=DATA/'turnout/2024-lincoln-original-panel-readings.json';np=QA/'corrected-worker-readings.json.gz'
 if np.exists():b=gzip.decompress(np.read_bytes())
 else:b=p.read_bytes();np.write_bytes(gzip.compress(b,mtime=0))
 old=json.loads(bodies['initial_reading']);new=json.loads(b);expected=copy.deepcopy(old);expected['statistics']['ballots_cast_total']=15898;expected['source_arithmetic']['statistics_ballots_cast']=15898;expected['source_arithmetic']['statistics_ballots_minus_contest_total']=0;assert expected==new
 coor=json.loads((DATA/'coordinator-lincoln-2024-original-panel-disagreement.json').read_bytes());assert new['source_raw_sha256']==coor['raw_original_sha256'];assert new['statistics']['ballots_cast_total']==coor['statistics_original_direct_reading']['ballots_cast_printed']
 assert new['source_arithmetic']==dict(senate_named=15679,president_named=15802,senate_generic=47,president_generic=27,both_printed_contest_totals=15898,Senate_unallocated_after_named_and_generic=172,president_unallocated_after_named_and_generic=69,statistics_ballots_cast=15898,statistics_ballots_minus_contest_total=0)
 out=dict(status='pass_owned_Lincoln2024_original_ballots_correction_exact_three_panel_fields',worker_correction_history=pin(hp),initial_artifact_pins=h['frozen_initial_artifacts'],verified_complete_initial_artifacts=11,initial_panel_sha256=sha(bodies['initial_reading']),corrected_panel=dict(original_path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b),lossless_copy=pin(np)),fresh_coordinator_original_review=pin(DATA/'coordinator-lincoln-2024-original-panel-disagreement.json'),changed_panel_fields=[dict(path='/statistics/ballots_cast_total',old=15909,new=15898),dict(path='/source_arithmetic/statistics_ballots_cast',old=15909,new=15898),dict(path='/source_arithmetic/statistics_ballots_minus_contest_total',old=11,new=0)],all_other_panel_fields_exact=True,qualification='Worker independently reread the exact original after the coordinator source finding. Complete prior panel/script/control/report/SCHEMA/validator/validation bytes survive losslessly; exactly three panel fields change. All named/generic candidate fields, printed contest totals, original raw/page/raster pointers and clocks remain exact. Ballots15898 equals contest15898; residual172Sen/69Pres remains unallocated, registration0 unusable. The earlier358-field14summary/12statistics peer proof is not upgraded to this new15/13scope; no native/ranking/currentgeo/formal887 acceptance follows.',formal_native887_dispatch_accepted=False)
 p=DATA/'coordinator-lincoln-2024-owned-correction-review.json';body=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==body
 else:p.write_bytes(body)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
