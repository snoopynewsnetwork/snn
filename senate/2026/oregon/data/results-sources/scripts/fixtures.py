"""Meaningful in-memory corruptions; never edit source/producer files."""
from pathlib import Path
from replay_inputs import load_catalogs,read,R,S,sha
from resolve import resolve_body,resolve_object
import check_coverage as cov
from packaging import validate_members,MANIFEST
import json,copy

def main():
 results=[]
 def reject(name,fn):
  try:fn()
  except (AssertionError,ValueError,KeyError,IndexError):results.append({'case':name,'rejected':True});return
  raise AssertionError('negative unexpectedly passed '+name)
 a=load_catalogs();c=json.loads(read(a['frozen_contract']));assert cov.validate_contract(c)
 for name,field,value in [('empty_native_priority','ordered_priority_keys',[]),('known213_substituted','minimum80',{'rows':213}),('county11_substituted','minimum80',{'counties':11}),('inferred_empty_remainder','remainder',[])]:
  bad=copy.deepcopy(c);bad[field]=value;reject(name,lambda:cov.validate_contract(bad))
 bad=copy.deepcopy(c);p=next(p for p in bad['all_36_county_parents'] if p['source_native_constituents']);p['source_native_constituents'].pop();reject('missing_one_known_context',lambda:cov.validate_contract(bad))
 bad=copy.deepcopy(c);p=next(p for p in bad['all_36_county_parents'] if p['native_reporting_unit_count'] is None);p['source_native_constituents']=[{'key':p['county_key']+':invented'}];reject('unknown_parent_fabricated_native_leaf',lambda:cov.validate_contract(bad))
 bad=copy.deepcopy(c);u=next(u for p in bad['all_36_county_parents'] for u in p['source_native_constituents'] if len(u['source_native_constituent_ids'])>1);u['count_allocation_to_constituents']='fabricated_even_split';reject('combined115_116_allocation',lambda:cov.validate_contract(bad))
 bad=copy.deepcopy(c);u=next(u for p in bad['all_36_county_parents'] for u in p['source_native_constituents']);u['current_result_id']='fabricated-current';reject('historical_id_promoted_current',lambda:cov.validate_contract(bad))
 oldrows=cov.rows
 try:
  cov.rows=lambda name:oldrows(name)[1:] if name=='known-contexts.jsonl.gz' else oldrows(name)
  reject('complete_owned510_ledger_omission',cov.main)
 finally:cov.rows=oldrows
 r=oldrows('known-contexts.jsonl.gz')[0]['complete_source_context'];wrong=copy.deepcopy(r);wrong['whole_object_semantic_sha256']='0'*64;reject('whole_object_field_loss_hash',lambda:resolve_object(wrong))
 wrong=copy.deepcopy(a['frozen_contract']);wrong['sha256']='0'*64;reject('wrong_full_body_sha',lambda:read(wrong))
 # Superseded old targets resolve their own entire bytes.
 historical=next(r for cap in a['immutable_historical_snapshot_body_resolvers'] for r in cap['complete_records'] if (S/r['original_path']).exists() and sha((S/r['original_path']).read_bytes())!=r['original_sha256'])
 b=resolve_body(historical['original_path'],historical['original_sha256']);assert sha(b)==historical['original_sha256'];results.append({'case':'superseded_path_full_old_body_positive','passed':True,'original_path':historical['original_path'],'original_sha256':historical['original_sha256']})
 reject('wrong_historical_expected_digest',lambda:resolve_body(historical['original_path'],'0'*64))
 validation=b'{}\n';vp='data/results-sources/validation.json';sp='data/results-sources/finalseal.json'
 seal={'fixed_inputs':[{'path':vp,'bytes':len(validation),'sha256':sha(validation)}]};payload={vp:validation,sp:json.dumps(seal).encode(),'official-results.md':b'research\n','data/results-sources/history/fixture.txt':b'prior body\n'}
 manifest={'excluded':[MANIFEST],'files':[{'path':k,'bytes':len(v),'sha256':sha(v)} for k,v in payload.items()]};assert validate_members(manifest,payload)==4
 missing=dict(payload);missing.pop(sp);reject('missing_finalseal',lambda:validate_members(manifest,missing))
 changed=dict(payload);changed[sp]+=b' ';reject('changed_finalseal',lambda:validate_members(manifest,changed))
 omitted=copy.deepcopy(manifest);omitted['files']=omitted['files'][:-1];reject('manifest_omitted_history_body',lambda:validate_members(omitted,payload))
 altered=copy.deepcopy(manifest);altered['excluded'].append(sp);reject('two_exclusions_rejected',lambda:validate_members(altered,payload))
 # Raw staging header/data width is intentionally not repaired to a votes projection.
 d=json.loads(__import__('gzip').decompress((R/'structures/sos-staging-csv-negative.json.gz').read_bytes()));rr=d['complete_rows'];assert len(rr[0])==15 and all(len(x)==16 and x[-1]=='' for x in rr[1:]);results.append({'case':'staging_extra_raw_field_preserved_positive','passed':True,'admitted':False})
 return {'status':'pass','cases':results,'case_count':len(results),'negative_count':sum(r.get('rejected',False) for r in results),'shared_mutations':False}
if __name__=='__main__':print(json.dumps(main(),indent=2))
