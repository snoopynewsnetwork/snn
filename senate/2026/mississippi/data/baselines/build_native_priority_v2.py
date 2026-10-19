"""New immutable complete-named-field887 proposal; never mutate Senate-onlyv1."""
import collections,csv,gzip,io,json
from sources import OUT,BASE,sha,save

def pin(p):return dict(path=str(p.relative_to(BASE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
def load_own():
 sp=OUT/'source/native-allfield-82views/snapshot.json';snap=json.loads(sp.read_text());docs={}
 for p in snap['pins']:
  z=(BASE/p['frozen_path']).read_bytes();r=gzip.decompress(z);assert len(z)==p['stored_bytes'] and sha(z)==p['stored_sha256'] and len(r)==p['original_bytes'] and sha(r)==p['original_sha256'];docs[p['original_path'].split('/')[-1]]=json.loads(r) if p['original_path'].endswith('.json') else r
 columns={}
 def put(sid,n,i,name,v,role,label,h,fips=None):
  k=(sid,n,i);rr='TOTAL' if role in ['summary_TOTAL','source_TOTAL','TOTAL'] else 'unused' if role in ['unused','unused_template_column'] else 'parallel' if role=='parallel_native_observation' else 'native';d=columns.setdefault(k,dict(source_id=sid,PDFpage=n,physical_source_column=i,source_raw_sha256=h,role=rr,label_literal=label,candidate_votes={},county_fips=fips));assert d['source_raw_sha256']==h and d['role']==rr and d['label_literal']==label and name not in d['candidate_votes'];d['candidate_votes'][name]=v
  if fips:
   assert d['county_fips'] in [None,fips];d['county_fips']=fips
 for fn in ['native-allfield-additional-candidate-votes.csv','winston-native-allfield-candidate-votes.csv']:
  for r in csv.DictReader(io.StringIO(docs[fn].decode())):put(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate'],None if r['value']=='' else int(r['value']),r['role'],r.get('literal_native_label',r.get('label_literal')),r['raw_sha256'],r['county_fips'])
 for fn in ['alcorn-readings.json','coahoma-updated-readings.json','native-source-exception-readings.json']:
  doc=docs[fn]
  for s in doc.get('sources',[doc]):
   for pg in s['pages']:
    cols=pg.get('columns');roles=pg.get('roles');labels=pg.get('labels_literal')
    for field in pg['fields']:
     for i,v in enumerate(field['values']):
      c=cols[i] if cols is not None else {};put(s['source_id'],pg['page'],c.get('source_column',i+1),field.get('candidate',field.get('field')),v,c.get('unit_type',roles[i] if roles else None),c.get('label_literal',c.get('native_label_literal',labels[i] if labels and i<len(labels) else '')),s['raw_sha256'],s.get('fips',s.get('county_fips')))
 assert len(columns)==2266 and all(len(c['candidate_votes'])==11 for c in columns.values());return sp,columns

def main():
 v1sp=OUT/'source/native-priority-v1/snapshot.json';v1snap=json.loads(v1sp.read_text());v1docs={}
 for p in v1snap['pins']:
  z=(BASE/p['frozen_path']).read_bytes();r=gzip.decompress(z);assert len(z)==p['stored_bytes'] and sha(z)==p['stored_sha256'] and len(r)==p['original_bytes'] and sha(r)==p['original_sha256'];v1docs[p['original_path'].split('/')[-1]]=r
 v1=json.loads(v1docs['native-priority-contract.json']);order=list(csv.DictReader(io.StringIO(v1docs['native-full-order.csv'].decode())));ownsp,cols=load_own();all11proof=OUT/'native-2024-all11-complete-peer-reconciliation.json';proof=json.loads(all11proof.read_text());assert proof['positions']==24926 and not proof['value_role_differences'];fieldsp=OUT/'printed-field-source-scope.json';scope=json.loads(fieldsp.read_text());assert not scope['additional_required_panel_pending_in_inventory']
 native={};allcols=[];roles=collections.Counter();sums=collections.Counter()
 fipsbysource={r['source_id']:r['parent_county_fips'] for r in order}
 for c in cols.values():
  if c['county_fips'] is None:c['county_fips']=fipsbysource[c['source_id']]
  c['source_position_key']=f"{c['county_fips']}:{c['source_id']}:p{c['PDFpage']}:c{c['physical_source_column']}";roles[c['role']]+=1;assert (all(v is None for v in c['candidate_votes'].values()) if c['role']=='unused' else all(type(v) is int and v>=0 for v in c['candidate_votes'].values()))
  if c['role']=='native':native[c['source_position_key']]=c;sums.update(c['candidate_votes'])
  allcols.append(c)
 assert roles==dict(native=1736,TOTAL=82,unused=437,parallel=11);assert sums['Ty Pinkins']==451980 and sums['Roger F. Wicker']==763420 and sum(sums.values())==1215400+1228007
 assert sorted(native,key=lambda k:(-native[k]['candidate_votes']['Ty Pinkins']-native[k]['candidate_votes']['Roger F. Wicker'],k))==v1['ordered_native_keys'];cum=0;nr=[]
 for i,r in enumerate(order,1):
  c=native[r['key']];vv=c['candidate_votes'];pair=vv['Ty Pinkins']+vv['Roger F. Wicker'];cum+=pair;assert int(r['rank'])==i and int(r['cumulative_votes'])==cum and int(r['Pinkins'])==vv['Ty Pinkins'] and int(r['Wicker'])==vv['Roger F. Wicker'];nr.append(dict(rank=i,key=r['key'],parent_county_fips=c['county_fips'],source_id=c['source_id'],source_raw_sha256=c['source_raw_sha256'],PDFpage=c['PDFpage'],physical_source_column=c['physical_source_column'],all11_literal_header=c['label_literal'],frozen_v1_order_literal_header=r['label_literal'],printed_native_id_frozen_v1=r['printed_native_id'],named_Senate_pair_votes=pair,cumulative_named_Senate_votes=cum,primary_priority=i<=887,candidate_votes=json.dumps(vv,ensure_ascii=False,sort_keys=True)))
 assert cum==1215400 and nr[885]['cumulative_named_Senate_votes']==972157 and nr[886]['cumulative_named_Senate_votes']==972656 and nr[886]['key']=='28075:sos-2024-county-lauderdale:p9:c5'
 assert len({r['parent_county_fips'] for r in nr})==82 and len({r['parent_county_fips'] for r in nr[:887]})==77 and set(native)==set(v1['ordered_priority_native_keys'])|set(v1['ordered_nonpriority_native_keys'])
 out=OUT/'native-priority-contract-v2.json';contract=dict(v1);contract.pop('full_all_candidate_method_historical_native_gate');contract.update(version='complete_named_source_v2_proposal',coordinator_accepted=False,current2026_geography_approved=False,qualification='New complete retained-field proposal, never coordinator/currentgeography approval. Same887primary native order in77parents, county41sensitivity only; all11named fields and located required additional controls now source-reviewed. Oldv1bytes unchanged.',previous_v1=pin(v1sp),own_all11_original_witness=pin(ownsp),own_all11_peer_proof=pin(all11proof),printed_available_field_scope=pin(fieldsp),historical_original_witnesses=[pin(OUT/'source/native-2020-104views-v1/snapshot.json'),pin(OUT/'source/native-2018-164views-v1/snapshot.json')],complete_owned_retained_source_candidate_and_located_control_review=True,all_unprinted_fields_known=False,source_native_candidate_sums=dict(sums),source_presidential_named_denominator=1228007,certified_presidential_named_denominator=1228008,source_presidential_disagreement=dict(county='Tunica',candidate='Kamala D. Harris',native_minus_certified=-1,allocation=None),all_preferred_source_columns=sorted(allcols,key=lambda c:(c['county_fips'],c['source_id'],c['PDFpage'],c['physical_source_column'])),printed_method_native_control_evidence=dict(county_summaries='data/baselines/canvass-readings.json',county_statistics='data/baselines/canvass-statistics-readings.json',vendor_profiles=['data/baselines/union-native-profile-readings.json','data/baselines/pike-native-profile-readings.json'],administrative_split_styles='data/baselines/union-split-ballot-style-readings.json'),full_source_scope_limits=['Unprinted native generic/validwritein/method/blank/under/over/ballot/registration fields unavailable, not0','Union58BP009candidateallocations unknown; no registered-voter-based vote allocation','Tunica−1Pinkins/−1Harris andLeflore2018Espy−10 unallocated','Six2018literalX numeric cells unknown; stages/alternatives/parallels separate','Independent historicalpeer bounded41/1042020 and41/1642018; no full historical peer replay claim','No final2026ballot/withdrawal/validwritein/resultID/currentgeography or exhaustive later-law approval'],optional_printed_ID_metadata_scope=v1['optional_printed_ID_metadata_scope']+'; complete all11 source labels do not silently fill old optional IDs or normalize Holmes hyphen-wrap variants.')
 save(out,contract);csvpath=OUT/'native-priority-source-fields-v2.csv';f=io.StringIO();w=csv.DictWriter(f,fieldnames=list(nr[0]));w.writeheader();w.writerows(nr);csvpath.write_text(f.getvalue());folder=OUT/'source/native-priority-v2';folder.mkdir(exist_ok=True);pins=[]
 for p in [out,csvpath,all11proof,fieldsp]:
  r=p.read_bytes();z=gzip.compress(r,mtime=0);dest=folder/(p.name+'.gz');assert len(z)<40000000
  if dest.exists():assert dest.read_bytes()==z,'New change requires another immutable version'
  else:dest.write_bytes(z)
  pins.append(dict(original_path=str(p.relative_to(BASE)),original_bytes=len(r),original_sha256=sha(r),frozen_path=str(dest.relative_to(BASE)),stored_bytes=len(z),stored_sha256=sha(z),reconstruction='Exact ordered original bytes by losslessgzip; no normalization'))
 snapshot=dict(status='complete_named_source_887proposal_pending_coordinator_acceptance',version='v2',previous_v1=pin(v1sp),own_all11_original_witness=pin(ownsp),source_columns=2266,native_units=1736,candidate_positions=24926,priority_native_units=887,priority_parent_authorities=77,preceding886=972157,priority887=972656,source_Senate_pair_denominator=1215400,certified_Senate_denominator=1215401,unallocated_Tunica_pair_difference=1,source_presidential_named_denominator=1228007,certified_presidential_named_denominator=1228008,unallocated_Tunica_Harris_difference=1,alternative84_orders_reused_readonly_from_v1=True,pins=pins,coordinator_accepted=False,current2026_geography_approved=False)
 sp=folder/'snapshot.json'
 if sp.exists():assert json.loads(sp.read_text())==snapshot
 else:save(sp,snapshot)
 save(OUT/'native-priority-v2-validation.json',dict(status='pass_complete_named_source_proposal_arithmetic_not_external_acceptance',snapshot=pin(sp),source_columns_by_role=dict(roles),candidate_positions=24926,all11_native_candidate_sums=dict(sums),all1736keys_order_parent_and_887arrays_unchanged_from_v1=True,all82_parent_maps_unchanged=True,priority_parent_authorities=77,all_original_and_stored_v2_pins_verified=True,previous_v1_unchanged=pin(v1sp),coordinator_accepted=False,current2026_geography_approved=False))
 print('PASSv2proposal all24926fields/1736ordered/887priority/77parents; v1unchanged')
if __name__=='__main__':main()
