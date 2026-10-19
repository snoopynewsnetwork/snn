"""Check frozen source-stage native fields without combining stages or methods."""
from pathlib import Path
import argparse,collections,csv,gzip,hashlib,io,json,re,copy
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
NAMES={'special':['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],'runoff':['Mike Espy','Cindy Hyde-Smith']}
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def load(p):
 a=json.loads(p.read_bytes());out={}
 for r in a['pins']:
  z=(ROOT/r['stored_path']).read_bytes();b=gzip.decompress(z);assert len(z)==r['stored_bytes']and sha(z)==r['stored_sha256']and len(b)==r['original_bytes']and sha(b)==r['original_sha256'];out[Path(r['original_path']).name]=b
 return a,out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--views',type=int,required=True);ap.add_argument('--sha256',required=True);ap.add_argument('--version',type=int,default=1);ap.add_argument('--qualified-exceptions',action='store_true');args=ap.parse_args();qualified=args.version>=2 or args.qualified_exceptions;sp=DATA/f'baselines/source/native-2018-{args.views}views-v{args.version}/snapshot.json';assert pin(sp)['sha256']==args.sha256;snap,items=load(sp);ledger=json.loads(items['native-2018-original-readings.json']);sources={s['source_id']:s for s in ledger['sources']};assert len(sources)==args.views
 prior=gzip.decompress((DATA/'coordinator-qa/issaquena-2018-physical-columns/earlier-baseline-county-2018-readings.json.gz').read_bytes());old={r['source_id']:r for r in json.loads(prior)['readings']};assert len(old)==164
 refs={r['id']:r for r in json.loads((DATA/'baselines/source/references.json').read_bytes())};inventory=ledger['all164_source_status'];assert len(inventory)==164 and {r['source_id']for r in inventory}==set(old);assert {r['source_id']for r in inventory if r['native_original_review_complete']}==set(sources)
 counts=collections.Counter(source_views=len(sources));fields={};rasters={};findings=[];source_marks=[];administrative_positions=[];known_source_disagreements=[]
 for sid,s in sources.items():
  ref=refs[sid];z=(ROOT/ref['path']).read_bytes();raw=gzip.decompress(z);assert sha(z)==ref['stored_sha256']and sha(raw)==s['raw_sha256']==old[sid]['raw_sha256']and raw.startswith(b'%PDF-');sums=collections.Counter();totals={};native=0;totalcols=0
  assert s['stage']in NAMES
  for p in s['pages']:
   rp=ROOT/p['full_original_render_path'];assert pin(rp)['sha256']==p['render_sha256'];rasters[str(rp.relative_to(ROOT))]=pin(rp);assert [f['candidate']for f in p['fields']]==NAMES[s['stage']]
   assert len({c['source_column']for c in p['columns']})==len(p['columns'])
   for c in p['columns']:
    counts[{'native':'native_constituents_across_separate_stages','TOTAL':'TOTAL_columns','unused':'unused_columns','administrative':'administrative_columns'}[c['role']]]+=1;native+=c['role']=='native';totalcols+=c['role']=='TOTAL'
   for f in p['fields']:
    assert len(f['values'])==len(p['columns'])
    for c,v in zip(p['columns'],f['values']):
     mark=f.get('source_marks',{}).get(str(c['source_column']))
     key=(sid,p['page'],c['source_column'],f['candidate']);assert key not in fields;fields[key]=(c,v,s['raw_sha256'],f.get('party_literal'),mark)
     if c['role']=='unused':assert v is None and mark is None;counts['unused_null_positions']+=1
     elif v is None:
      assert c['role']=='native' and isinstance(mark,str) and mark.strip()
      counts['marked_native_positions']+=1
      source_marks.append(dict(source_id=sid,raw_PDF_sha256=s['raw_sha256'],actual_PDFpage=p['page'],physical_column=c['source_column'],literal_source_header=c['label_literal'],candidate=f['candidate'],raw_source_mark=mark,numerical_value=None))
     else:
      assert type(v)is int and v>=0 and mark is None;counts['numeric_positions']+=1
      if c['role']=='native':sums[f['candidate']]+=v
      elif c['role']=='administrative':
       assert v==0,'New nonzero administrative source scope requires explicit review'
       administrative_positions.append(dict(source_id=sid,raw_PDF_sha256=s['raw_sha256'],actual_PDFpage=p['page'],physical_column=c['source_column'],literal_source_header=c['label_literal'],candidate=f['candidate'],printed_numerical_value=v,source_native=False))
      else:assert c['role']=='TOTAL' and f['candidate']not in totals;totals[f['candidate']]=v
  assert totalcols==1 and totals==old[sid]['candidate_values']==s['controls']['printed_TOTAL']and dict(sums)==s['controls']['native_candidate_sums']
  if dict(sums)!=totals:
   assert qualified and sid=='sos-2018-county-leflore'
   proofpath=DATA/'coordinator-leflore-2018-original-native-residual-review.json';proof=json.loads(proofpath.read_bytes());assert s['raw_sha256']==proof['raw_original_sha256']
   assert {n:sums[n]-totals[n]for n in totals}=={'Tobey Bernard Bartee':0,'Mike Espy':-10,'Cindy Hyde-Smith':0,'Chris McDaniel':0}==s['controls']['native_minus_printed_TOTAL']
   assert s['controls']['all_vectors_close']is False
   for page in s['pages']:
    for f in page['fields']:
     native_values=[v for c,v in zip(page['columns'],f['values'])if c['role']=='native'];assert native_values==proof['source_native_candidate_values_by_actual_page'][f['candidate']][str(page['page'])]
   ep=s['controls']['unallocated_source_disagreement'];assert pin(ROOT/ep['path'])==ep;exception=json.loads((ROOT/ep['path']).read_bytes());assert exception['native_candidate_sums']==dict(sums)and exception['printed_TOTAL']==totals
   assert pin(ROOT/exception['initial_reading']['path'])==exception['initial_reading']
   for evidence in exception['complete_original_row_evidence']:
    assert pin(ROOT/evidence['crop_path'])['sha256']==evidence['sha256']and pin(ROOT/evidence['full_original_render_path'])['sha256']==evidence['render_sha256']
   known_source_disagreements.append(dict(source_id=sid,native_candidate_sums=dict(sums),printed_TOTAL=totals,native_minus_TOTAL=s['controls']['native_minus_printed_TOTAL'],fresh_coordinator_original_review=pin(proofpath),producer_original_exception=ep,allocated=False))
  status=next(r for r in inventory if r['source_id']==sid);assert status['reviewed_native_count']==native
  finding=dict(source_id=sid,raw_PDF_sha256=s['raw_sha256'],stage=s['stage'],actual_PDFpages=[p['page']for p in s['pages']],source_native_observations=native,candidate_sums_and_printed_TOTALs=totals)
  if dict(sums)!=totals:
   del finding['candidate_sums_and_printed_TOTALs'];finding['native_candidate_sums']=dict(sums);finding['printed_TOTALs']=totals
  findings.append(finding)
 for r in inventory:
  if r['source_id']not in sources:assert r['reviewed_native_count']is None
 flat=list(csv.DictReader(io.StringIO(items['native-2018-original-candidate-votes.csv'].decode())));assert len(flat)==len(fields)
 for r in flat:
  c,v,h,party,mark=fields[(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate'])];assert r['source_raw_sha256']==h and r['role']==c['role']and r['literal_native_label']==c['label_literal'];assert(None if r['votes']==''else int(r['votes']))==v;assert r.get('raw_source_mark','')==(mark or '')
 assert dict(counts)==ledger['counts']==snap['counts'];continuity=[]
 rejected=[]
 pattern='native-2018-*views-v*/snapshot.json'if qualified else'native-2018-*views-v1/snapshot.json'
 rejection_records={}
 if qualified:
  records=json.loads((DATA/'baselines/source/native-2018-witness-rejections.json').read_bytes())
  rejection_records={r['snapshot']['path']:r for r in records['rejected_witnesses']}
 for p in sorted((DATA/'baselines/source').glob(pattern)):
  m=re.fullmatch(r'native-2018-(\d+)views-v(\d+)',p.parent.name)
  if not m or(int(m[1]),int(m[2]))>=(args.views,args.version):continue
  if str(p.relative_to(ROOT))in rejection_records:
   record=rejection_records[str(p.relative_to(ROOT))];assert pin(p)==record['snapshot'];rejected.append(record);continue
  _,previous=load(p);a=json.loads(previous['native-2018-original-readings.json']);assert len(a['sources'])==int(m[1])
  changed=[];spelling_changed=[]
  for s in a['sources']:
   now=sources[s['source_id']]
   if now!=s:
    assert qualified
    previous_source=copy.deepcopy(s)
    if s['source_id']in['sos-2018-county-greene','sos-2018-runoff-county-greene']:
     target=next(c for page in previous_source['pages']if page['page']==3 for c in page['columns']if c['source_column']==1);assert target['label_literal']=='McLain';target['label_literal']='Mclain';assert previous_source==now;changed.append(s['source_id'])
    else:
     assert 'literal_header_spelling_correction_history'in ledger and s['source_id']in['sos-2018-county-tunica','sos-2018-runoff-county-tunica']
     target=next(c for page in previous_source['pages']if page['page']==2 for c in page['columns']if c['source_column']==2);assert target['label_literal']=='Moon Landing';target['label_literal']='Mhoon Landing';assert previous_source==now;spelling_changed.append(s['source_id'])
   else:assert now==s
  row=dict(snapshot=pin(p),predecessor_source_objects_unchanged=len(a['sources'])-len(changed)-len(spelling_changed))
  if changed:row['only_qualified_original_case_corrections']=changed
  if spelling_changed:row['only_qualified_original_spelling_corrections']=spelling_changed
  continuity.append(row)
 out=dict(status='pass_bounded_immutable_original2018_stage_native_fields_and_source_controls',snapshot=pin(sp),counts=dict(counts),flat_candidate_positions=len(flat),all164_source_inventory_retained=True,unreviewed_stage_native_views=164-len(sources),source_findings=findings,original_raster_pins=list(rasters.values()),prior_witness_continuity=continuity,qualification='Every frozen raw original/render/field/role/count/vector and prior source-object continuity check passes. This is original source and arithmetic validation, not fresh coordinator glyph reading of all new cells or complete independent native replay. Actual PDF page numbers stay distinct from printed page footers; source windows are not certified digit/geographic polygons. Four-candidate special and two-candidate runoff electorates remain separate; regularClassI rows are excluded, and unprinted parties/method/ballot/registration/generic fields are unknown. Remaining source-stage native counts stay null, not replaced with counties or other-year/stage rows. Whole historical methods/current geography/native887dispatch remain open.',whole2018_native_complete=False,formal_native887_dispatch_accepted=False,current_geography_approved=False)
 if source_marks:
  out['explicit_non_numeric_native_source_positions']=source_marks
  out['qualification']+=' Non-numeric original marks are retained literally with numerical null, never zero or a status/geographic inference. Known numeric native sums close printed TOTAL without allocating marked cells; closure does not prove a numerical value for any mark.'
 if administrative_positions:
  out['explicit_administrative_source_positions']=administrative_positions
  out['qualification']+=' Separately printed administrative columns remain outside native/unused counts and retain explicit observed integers. The current PURGED VOTERS0/0 source observation establishes neither an unprinted administrative meaning nor a reporting/geographic identity.'
 if qualified:
  hp=ledger['literal_header_correction_history'];assert pin(ROOT/hp['path'])==hp;history=json.loads((ROOT/hp['path']).read_bytes());assert len(history['changed_candidate_header_fields'])==6 and history['changed_source_header_objects']==2 and history['votes_roles_positions_raw_hashes_unchanged']
  for h in history['changed_candidate_header_fields']:
   assert h['PDFpage']==3 and h['physical_column']==1 and h['prior_literal_header']=='McLain'and h['accepted_literal_header']=='Mclain';assert fields[h['source_id'],3,1,h['candidate']][1]==h['votes']
  out['qualified_original_header_case_history']=hp;out['independent_original_header_review']=pin(DATA/'coordinator-greene-2018-original-header-review.json');out['explicit_unallocated_source_control_disagreements']=known_source_disagreements;out['rejected_misnamed_witnesses_excluded']=rejected
  out['all_native_vectors_close_printed_TOTAL']=not known_source_disagreements
  out['qualification']+=' Source continuity preserves the exact six Greene McLain-to-original-Mclain header corrections with prior bytes unchanged. Leflore special has nativeEspy5853 versus printed5863, unallocated10; this known original-source difference is retained, not forced closed. Explicitly rejected stale98v1 is excluded from accepted continuity and cannot satisfy98-stage scope.'
  if 'literal_header_spelling_correction_history'in ledger:
   tp=ledger['literal_header_spelling_correction_history'];assert pin(ROOT/tp['path'])==tp;th=json.loads((ROOT/tp['path']).read_bytes());assert len(th['changed_candidate_header_fields'])==6 and th['changed_source_header_objects']==2 and th['votes_roles_positions_raw_hashes_unchanged'];assert pin(ROOT/th['prior_witness']['path'])==th['prior_witness']
   for rp in th['prior_pins']:
    z=(ROOT/rp['stored_path']).read_bytes();b=gzip.decompress(z);assert len(z)==rp['stored_bytes']and sha(z)==rp['stored_sha256']and len(b)==rp['original_bytes']and sha(b)==rp['original_sha256']
   for h in th['changed_candidate_header_fields']:
    assert h['PDFpage']==2 and h['physical_column']==2 and h['prior_literal_header']=='Moon Landing'and h['accepted_literal_header']=='Mhoon Landing';assert fields[h['source_id'],2,2,h['candidate']][1]==h['votes']
   for r in th['original_readings']:
    assert pin(ROOT/r['full_original_render_path'])['sha256']==r['render_sha256']and pin(ROOT/r['crop']['path'])=={k:r['crop'][k]for k in ['path','bytes','sha256']};assert r['literal_header']=='Mhoon Landing'and sources[r['source_id']]['raw_sha256']==r['raw_sha256']
   out['qualified_original_spelling_history']=tp;out['qualification']+=' Later Tunica2018 continuity allows only two source-header objects/six candidate-label fields MoonLanding-to-original-MhoonLanding. Exact142v1 prior bodies and independent original crop evidence remain; counts/values/raw/raster/roles/physical positions are unchanged and no geographic alias is inferred.'
 if args.views==164:
  assert set(sources)==set(old)and len(inventory)==164
  out['all164_named_candidate_source_grids_reviewed']=True
  out['qualification']+=' All164 actual stage grids are now present in this one-producer named-candidate source witness. The broader whole2018_native_complete flag remains false because independent replay and printed method/ballot/registration controls are separate scopes. Three administrative columns and six literalX candidate positions retain their exact original roles and marks.'
 target=DATA/f'coordinator-historical-native-2018-{args.views}views-v{args.version}-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if target.exists():assert target.read_bytes()==b
 else:target.write_bytes(b)
 print(json.dumps(dict(output=pin(target),counts=dict(counts))))
if __name__=='__main__':main()
