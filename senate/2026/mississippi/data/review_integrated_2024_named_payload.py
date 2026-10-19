"""Check all preferred named-source columns against the immutable independent82 ledger."""
from pathlib import Path
import collections,gzip,json,re
from review_allfield_milestone import DATA,ROOT,NAMES,load,sources,sha,pin

QA=DATA/'coordinator-qa/integrated-named2024-v1'
def freeze(p):
 QA.mkdir(parents=True,exist_ok=True);q=QA/(p.name+'.gz')
 b=gzip.decompress(q.read_bytes())if q.exists()else p.read_bytes()
 if not q.exists():q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def main():
 path=DATA/'turnout/source/2024-preferred-all11-source-fields-v1.json.gz';z=path.read_bytes();raw=gzip.decompress(z)
 assert len(z)==96203 and sha(z)=='d066e45bebca7ba66163989165a430164f5b84cef61d9e2cda7e4bc4e1d23b6b'
 assert len(raw)==2048366 and sha(raw)=='b2a7e234eeb226bd13f35d3a4c32c867f88f7d59a680ec059a7378c036f1fbae';dep=json.loads(raw)
 cb,cp=freeze(DATA/'turnout/priority-set.json');contract=json.loads(cb);dp=contract['preferred_2024_all11_source_fields_dependency'];assert dp['raw_sha256']==sha(raw)and dp['stored_sha256']==sha(z)and dp['path']==str(path.relative_to(ROOT))and dp['raw_bytes']==len(raw)and dp['stored_bytes']==len(z)
 _,items,sp=load('82views','94576fcfa4b7b245e2d5baa9e8366e4489594804f41694ea04a9f6315e46b336');ss=sources(items);expected={};roles=collections.Counter();aliases=[];count=collections.Counter();state=collections.Counter();sums=collections.defaultdict(collections.Counter);totals={}
 for sid,s in ss.items():
  for p in s['pages']:
   rs=p.get('roles')
   if rs is None:rs=[{'summary_TOTAL':'source_TOTAL','unused':'unused_template_column'}.get(c['unit_type'],'source_native_reporting_constituent')for c in p['columns']]
   for j,role in enumerate(rs):
    label=p['headers'][j]['label_literal']if'headers'in p else p['columns'][j]['native_label_literal']if'columns'in p else p['labels_literal'][j]if j<len(p['labels_literal'])else''
    fields={f.get('candidate',f.get('field')):f['values'][j]for f in p['fields']};assert set(fields)==set(NAMES)
    expected[sid,p['page'],j+1]=dict(role={'source_native_reporting_constituent':'native_reporting_constituent'}.get(role,role),label=label,fields=fields,raw=s['raw_sha256'])
 embedded={(r['source_id'],r['source_page'],r['source_column']):r for r in contract['source_native_constituents']};seen=set();readpins={}
 for c in dep['columns']:
  k=(c['source_id'],c['source_page'],c['source_column']);assert k in expected and k not in seen;seen.add(k);e=expected[k];assert c['source_raw_sha256']==e['raw']and c['role']==e['role'];roles[c['role']]+=1
  if re.sub(r'\s+','',c['label_literal'])!=re.sub(r'\s+','',e['label']):
   assert k[0]=='sos-2024-county-holmes'and{re.sub(r'\s+','',c['label_literal']),re.sub(r'\s+','',e['label'])}=={'WaldenChapel(A-Z','WaldenChapel(A-Z)'}
   raise AssertionError('Unexpected parenthesis alias requires explicit source review')
  if c['label_literal']!=e['label']:aliases.append(dict(source_position=list(k),turnout_literal=c['label_literal'],independent_literal=e['label']))
  allfields={**c['Senate_candidate_votes'],**c['president_candidate_votes']};assert allfields==e['fields']and len(c['Senate_candidate_votes'])==2 and len(c['president_candidate_votes'])==9
  r=embedded[k];assert r['key']==c['key']and r['parent_county_fips']==c['parent_county_fips']and r['source_raw_sha256']==c['source_raw_sha256']and r['role']==c['role']and r['label_literal']==c['label_literal'];assert r['candidate_votes']==c['Senate_candidate_votes']and r['separately_scoped_contests']['2024-president']['candidate_votes']==c['president_candidate_votes']
  for n,v in allfields.items():
   if c['role']=='unused_template_column':assert v is None;count['unused_null_fields']+=1
   else:
    assert type(v)is int and v>=0;count['numeric_fields']+=1
    if c['role']=='native_reporting_constituent':sums[k[0]][n]+=v;state[n]+=v
    elif c['role']=='source_TOTAL':assert(k[0],n)not in totals;totals[k[0],n]=v
    else:assert c['role']=='parallel_native_observation'
  rp=ROOT/c['presidential_original_reading_path'];readpins[str(rp)]=dict(pin(rp),expected_sha256=c['presidential_original_reading_sha256']);assert readpins[str(rp)]['sha256']==c['presidential_original_reading_sha256']
 assert seen==set(expected)and len(seen)==2266 and roles=={'native_reporting_constituent':1736,'source_TOTAL':82,'unused_template_column':437,'parallel_native_observation':11}
 for sid in ss:assert dict(sums[sid])=={n:totals[sid,n]for n in NAMES}
 assert count=={'numeric_fields':20119,'unused_null_fields':4807}and sum(state[n]for n in NAMES[:9])==1228007 and sum(state[n]for n in NAMES[-2:])==1215400
 assert dep['explicit_unprinted_template_positions_absent_from_two_older_direct_ledgers']==126 and dep['explicit_unprinted_template_positions_by_source']=={'sos-2024-county-perry':45,'sos-2024-county-tunica':81}
 assert contract['status']=='in_progress_not_coordinator_accepted'and contract['current_2026_geographic_approval']is False and contract['peer_agreement']['native_fields_complete']is False
 out=dict(status='pass_bounded_complete_preferred82_named_source_payload_integration_not_dispatch',frozen_working_contract=cp,complete_external_dependency=pin(path),dependency_raw_sha256=sha(raw),immutable_independent_original82=sp,source_columns=len(seen),source_role_counts=dict(roles),candidate_field_counts=dict(count),named_candidate_fields=24926,Senate_candidate_fields=4532,presidential_candidate_fields=20394,all_source_values_and_embedded_payload_match=True,source_literal_whitespace_representations=aliases,verified_original_reading_references=list(readpins.values()),native_named_source_vectors=dict(state),explicit_old_unrepresented_template_nulls=126,qualification='All2266preferred source columns,1736native/82TOTAL/437unused/11nonadditiveKemperparallel, carry all11named values in both captured contract and exact external dependency. All24926value/null fields, roles, raw source hashes and physical locators match immutable independent82 source readings; source whitespace wraps are retained explicitly. Former126unrepresented unused positions are explicit null and match original peer blanks, never zero. Tunica Harris/Pinkins missing1each remains unallocated against signed controls; named-presidential source1228007 and Senate1215400 stay separate. This supersedes only the earlier observed incomplete working payload, preserves its bytes and original887v1, and does not approve historical/method/current-geography or formal dispatch completeness.',complete_preferred2024_named_payload=True,formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-integrated-preferred82-all11-payload-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
