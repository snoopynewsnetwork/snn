"""Verify a versioned physical-column repair against fresh original evidence."""
from pathlib import Path
import copy,csv,gzip,hashlib,io,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/issaquena-2018-physical-columns'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def frozen(path):
 q=QA/('independent-'+path.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:
  b=path.read_bytes();q.write_bytes(gzip.compress(b,mtime=0));assert path.read_bytes()==b
 return b,dict(original_path=str(path.relative_to(ROOT)),original_bytes=len(b),original_sha256=sha(b),lossless_copy=pin(q))
def main():
 evidence=DATA/'coordinator-issaquena-2018-physical-column-review.json';original=json.loads(evidence.read_bytes());expected={r['source_id']:r for r in original['original_findings']};b,lp=frozen(DATA/'baselines/native-2018-original-readings.json');ledger=json.loads(b);b,fp=frozen(DATA/'baselines/native-2018-original-candidate-votes.csv');flat=list(csv.DictReader(io.StringIO(b.decode())));b,cp=frozen(DATA/'baselines/county-2018-readings.json');county=json.loads(b)
 priorpin=DATA/'baselines/source/2018-physical-column-corrections-v1/prior-ledger-pin.json';pp=json.loads(priorpin.read_bytes());z=(ROOT/pp['stored_path']).read_bytes();assert sha(z)==pp['stored']['sha256']and len(z)==pp['stored']['bytes'];priorraw=gzip.decompress(z);assert sha(priorraw)==pp['original']['sha256']=='e891bb039a0bee656fd33beb34310d1c801e7db1560aab6f1346b6b819ce1222';assert priorraw==gzip.decompress((QA/'earlier-baseline-county-2018-readings.json.gz').read_bytes());prior=json.loads(priorraw)
 assert len(prior['readings'])==len(county['readings'])==164
 count=0;unchanged=0
 for old,new in zip(prior['readings'],county['readings']):
  assert old['source_id']==new['source_id']and old['candidate_values']==new['candidate_values']and old['raw_sha256']==new['raw_sha256'];count+=len(old['candidate_values'])
  if old==new:unchanged+=1;continue
  assert old['source_id']=='sos-2018-county-issaquena';a=copy.deepcopy(old);h=new['physical_column_correction_history'];assert h['prior_source_positions']==old['source_positions']and h['actual_physical_source_column']==6;assert h['prior_ledger_pin']==str(priorpin.relative_to(ROOT));assert h['native_original_evidence']=='data/baselines/native-2018-original-readings.json'
  a['source_positions']['source_column']=6;a['source_positions']['source_column_scope']=new['source_positions']['source_column_scope'];a['physical_column_correction_history']=h;assert a==new
 assert count==492 and unchanged==163
 for k in prior:
  if k!='readings':assert prior[k]==county[k]
 values={};rasters=[]
 assert {s['source_id']for s in ledger['sources']}==set(expected)
 for s in ledger['sources']:
  original_source=expected[s['source_id']];assert s['raw_sha256']==original_source['raw_PDF_sha256']and s['physical_TOTAL_column']==6
  p=s['pages'][0];assert len(s['pages'])==1 and p['page']==2 and len(p['columns'])==11
  rp=ROOT/p['full_original_render_path'];assert pin(rp)['sha256']==p['render_sha256'];rasters.append(pin(rp))
  for c,label in zip(p['columns'],original_source['physical_headers_in_original_order']):assert ' '.join(c['label_literal'].split())==' '.join(label.split())
  assert [c['role']for c in p['columns']]==['native']*5+['TOTAL']+['unused']*5
  for f in p['fields']:
   assert f['party_literal']is None and f['values']==original_source['direct_original_candidate_vectors_in_physical_order'][f['candidate']]
   for col,v in zip(p['columns'],f['values']):values[s['source_id'],2,col['source_column'],f['candidate']]=(col,v,f,p)
 assert len(values)==len(flat)==66
 for r in flat:
  key=r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate'];col,v,f,p=values[key];assert r['role']==col['role']and r['literal_native_label']==col['label_literal']and r['party_literal']==''and r['literal_printed_id']=='';assert(None if r['votes']==''else int(r['votes']))==v
  assert json.loads(r['header_bounds_pixels'])==col['header_bounds'];assert json.loads(r['candidate_reading_window_pixels'])==[col['header_bounds'][0],f['row_bounds'][1],col['header_bounds'][2],f['row_bounds'][3]];assert r['render_sha256']==p['render_sha256']and r['full_original_render_path']==p['full_original_render_path']
 assert ledger['counts']==dict(numeric_positions=36,unused_null_positions=30,source_views=2,native_constituents_across_separate_stages=10,TOTAL_columns=2,unused_columns=10)
 out=dict(status='pass_bounded_original2018_native_fields_and_metadata_only_physical_repair',independent_original_review=pin(evidence),frozen_worker_inputs=[lp,fp,cp],prior_worker_ledger_pin=pin(priorpin),prior_lossless_ledger_stored_pin=pin(ROOT/pp['stored_path']),all164_county_candidate_values_checked=492,other_county_readings_exactly_unchanged=163,physical_TOTAL_column=6,prior_Nov6_merged_machine_ordinal=4,worker_native_counts=ledger['counts'],worker_original_raster_pins=rasters,qualification='All36 original numeric and30 unused/null native source positions match the fresh coordinator original-page transcript, and flat fields reconstruct every source role/header/window. Party and printed-ID fields unprinted beside these selected rows remain null/blank rather than inferred. The exact prior complete county ledger is losslessly preserved; only one Nov6 reading gains physical6 plus explicit source-column scope/history, with all492 values/raw/page fields and other163 readings unchanged. The older peer CSV still using4 is a known metadata difference, not a false ordinal agreement. Both stage partitions remain separate, rasters/windows are separately retained, and no cross-stage/current identity, complete2018native/method or native887 approval follows.',whole2018_native_complete=False,current_geography_approved=False,formal_native887_dispatch_accepted=False)
 p=DATA/'coordinator-issaquena-2018-worker-repair-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable proof changed'
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
