"""Reconcile a new independent original TOTAL replay with frozen publication data."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
DEST=DATA/'coordinator-qa/2020-publication-original-replay'
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}
def freeze(name):
 path=DEST/(name+'.gz')
 if not path.exists():
  b=(DATA/'turnout'/name).read_bytes();assert (DATA/'turnout'/name).read_bytes()==b
  path.write_bytes(gzip.compress(b,mtime=0))
 return gzip.decompress(path.read_bytes()),pin(path)

def main():
 DEST.mkdir(exist_ok=True)
 raw,readpin=freeze('2020-publication-original-total-readings.json')
 readings=json.loads(raw)
 flatraw,flatpin=freeze('2020-publication-original-total-candidate-votes.csv')
 flat=list(csv.DictReader(io.StringIO(flatraw.decode())))
 recr,reconpin=freeze('2020-publication-original-peer-reconciliation.json');recon=json.loads(recr)
 baseline_path=DATA/'coordinator-qa/county-2020-publication-controls.json.gz'
 baseline_raw=gzip.decompress(baseline_path.read_bytes());baseline=json.loads(baseline_raw)
 assert recon['original_readings_sha256']==sha(raw)
 assert recon['peer_readings_sha256']==sha(baseline_raw)=='be574f1c108aff82d76f1f71912e80aae108dc75c737183c71f67598685d11ce'
 old={r['source_id']:r for r in baseline['readings']};new={r['source_id']:r for r in readings['sources']}
 assert set(old)==set(new)and len(new)==104
 assert len(flat)==312 and len({(r['source_id'],r['candidate'])for r in flat})==312
 refs={r['id']:r for r in json.loads((DATA/'baselines/source/references.json').read_bytes())}
 basis=collections.Counter();ordinal_status=collections.Counter();corrected=[];comparisons=[]
 groups=collections.defaultdict(list);fieldcount=0;evidence={}
 for sid,row in new.items():
  original=old[sid];meta=refs[sid]
  assert row['source_raw_sha256']==original['raw_sha256']==meta['raw_sha256']
  stored=(ROOT/meta['path']).read_bytes();rawsource=gzip.decompress(stored)
  assert sha(stored)==meta['stored_sha256']and sha(rawsource)==meta['raw_sha256']
  assert rawsource.startswith(b'%PDF-')
  assert row['source_page']==original['source_page']
  assert row['candidate_values']==original['candidate_values']
  assert set(row['candidate_values'])==set(NAMES)
  basis[row['original_reading_basis']]+=1;ordinal_status[row['source_column_ordinal_status']]+=1
  for key in ['original_evidence','original_card']:
   p=ROOT/row[key];assert pin(p)['sha256']==row[key+'_sha256'];evidence[str(p.relative_to(ROOT))]=pin(p)
  if row['direct_original_corrected_column']is not None:
   assert row['source_column_ordinal_status']=='direct_original_header_numeric_count_verified'
   assert type(row['direct_original_corrected_column'])is int
   corrected.append({k:row[k]for k in ['source_id','source_page','position_hint_column_before_correction','direct_original_corrected_column']})
  else:assert row['source_column_ordinal_status']=='peer_locator_hint_not_asserted_as_final_ordinal'
  for name in NAMES:
   f=next(f for f in flat if f['source_id']==sid and f['candidate']==name)
   assert int(f['votes'])==row['candidate_values'][name]
   assert int(f['source_page'])==row['source_page']and f['source_raw_sha256']==row['source_raw_sha256']
   assert f['reading_basis']==row['original_reading_basis']
   assert f['source_column_ordinal_status']==row['source_column_ordinal_status']
   assert f['source_column_ordinal']==(''if row['direct_original_corrected_column']is None else str(row['direct_original_corrected_column']))
   fieldcount+=1
  groups[original['county_key']].append(original)
  comparisons.append({'source_id':sid,'raw_sha256':row['source_raw_sha256'],'actual_pdf_page':row['source_page'],
    'candidate_values':row['candidate_values'],'reading_basis':row['original_reading_basis'],
    'ordinal_status':row['source_column_ordinal_status']})
 assert fieldcount==312 and len(groups)==82 and sum(len(v)==2 for v in groups.values())==22
 assert readings['direct_visual_source_count']==basis['direct_visual_full_original_candidate_band']==54
 assert readings['dual_PSM_original_OCR_source_count']==basis['two_independent_PSM_readings_of_original_total_cell']==50
 assert len(corrected)==readings['manual_corrected_ordinal_count']==10
 selected={n:0 for n in NAMES};before={n:0 for n in NAMES};changed=[]
 for county,rows in groups.items():
  first=next(r for r in rows if r['publication_variant']=='original county-index publication')
  after=next((r for r in rows if r['publication_variant']=='Amended'),first)
  assert after['candidate_values']==after['county_csv_control']
  for n in NAMES:before[n]+=first['candidate_values'][n];selected[n]+=after['candidate_values'][n]
  delta={n:after['candidate_values'][n]-first['candidate_values'][n]for n in NAMES}
  if any(delta.values()):changed.append({'county':county,'delta':delta})
 assert list(selected.values())==[578691,709511,23152]
 assert list(before.values())==[578332,709491,23150]
 originalstate=dict(zip(NAMES,[578806,709539,23152]));difference={n:before[n]-originalstate[n]for n in NAMES}
 assert list(difference.values())==[-474,-48,-2]
 assert len(changed)==3
 assert recon['source_value_page_hash_differences']==recon['selected_county_CSV_differences']==[]
 output={'status':'pass_104_publication_312_field_independent_original_TOTAL_replay_only',
  'turnout_frozen_input_pins':[readpin,flatpin,reconpin],
  'baseline_prior_frozen_publication_controls':pin(baseline_path),
  'basis_source_counts':dict(basis),'ordinal_status_source_counts':dict(ordinal_status),
  'worker_direct_original_ordinal_corrections':corrected,'source_count':104,'county_count':82,
  'amended_alternatives':22,'candidate_field_comparisons':fieldcount,'original_evidence_pins':list(evidence.values()),
  'publication_comparisons':comparisons,'all_original_county_publication_sum':before,
  'selected_amended_where_linked_sum':selected,'all_original_minus_original_state':difference,
  'changed_county_publications':changed,
  'qualification':'The independent replay agrees at all312 printed county Senate TOTAL candidate values, raw source hashes and actual PDF pages with the prior frozen publication ledger.54 vectors have original-image visual basis and50 require two original-pixel OCR passes; this is not312 fresh coordinator visual readings. Ten worker-corrected printed TOTAL ordinals remain explicit;94 other source-column values remain unaccepted locator hints. Neither numeric closure nor a printed publication amendment establishes native-unit/method completion or a common statewide release vintage. All prior proofs remain unchanged; complete presidential/historical-native/method and current reporting/geographic gates stay open.',
  'historical_native_complete':False,'formal_dispatch_accepted':False,'current2026_geography_approved':False}
 target=DATA/'coordinator-2020-publication-original-replay-review.json'
 target.write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'status':output['status'],'sources':104,'fields':fieldcount,'basis_counts':dict(basis),'locator_status_counts':dict(ordinal_status),'output_pin':pin(target)}))

if __name__=='__main__':main()
