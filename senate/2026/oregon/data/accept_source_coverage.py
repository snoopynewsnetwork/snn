"""Freeze complete available source research; unavailable native priority is never fabricated.

Producer bodies and flags are read-only. JSON/CSV companions retain complete fields;
ordered ledgers reference every dict/list container, never a selected-votes projection.
"""
from pathlib import Path
import csv,gzip,hashlib,io,json,collections
S=Path(__file__).resolve().parents[1];D=S/'data';T=D/'turnout';B=D/'baselines'

def sha(b):return hashlib.sha256(b).hexdigest()
def enc(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sem(x):return sha(enc(x))
def pin(p):
 b=p.read_bytes();assert len(b)<40000000
 return {'path':str(p.relative_to(S)),'bytes':len(b),'sha256':sha(b)}
def load(p):return json.loads(p.read_bytes())
def walk(x,path=''):
 if isinstance(x,(dict,list)):
  yield path,x
  it=x.items() if isinstance(x,dict) else enumerate(x)
  for k,v in it:
   if isinstance(v,(dict,list)):
    yield from walk(v,path+'/'+str(k).replace('~','~0').replace('/','~1'))
def parsed(p):
 raw=p.read_bytes();raw=gzip.decompress(raw) if p.name.endswith('.gz') else raw
 if '.jsonl' in p.name:return [json.loads(l) for l in raw.splitlines() if l]
 if '.json' in p.name:return json.loads(raw)
 return list(csv.reader(io.StringIO(raw.decode('utf-8-sig'),newline='')))
def select():
 out=[]
 for folder,excluded in [(T,{'history','peer-capture-v1','review-development'}),(B,{'history','pre-peer-bodies','peer-comparison','fixtures'})]:
  for p in sorted(folder.rglob('*')):
   if p.is_file() and not excluded.intersection(p.relative_to(folder).parts) and (p.suffix in ['.json','.csv'] or p.name.endswith(('.json.gz','.jsonl.gz'))):out.append(p)
 # Compatibility CSVs are full bodies too, not selected voting fields.
 out.extend([D/'county-turnout.csv',D/'county-baselines.csv'])
 contract=T/'priority-set.json';return [contract]+[p for p in out if p!=contract]
def snapshot_resolvers():
 out=[]
 for base in [T/'source/history/pre-reciprocal-v1',T/'source/peer-capture-v1']:
  inv=load(base/'inventory.json');records=[]
  for r in inv['entries']:
   o={'original_path':r['path'],'original_bytes':r['bytes'],'original_sha256':r['sha256']}
   if 'archive' in r:o.update(storage='tar_gzip_member',immutable_container=pin(base/r['archive']),member=r['member'])
   else:o.update(storage='immutable_original_reference',immutable_stored_body=pin(S/r['immutable_original_path']))
   records.append(o)
  out.append({'capture':pin(base/'inventory.json'),'complete_records':records})
 base=B/'source/history/seal-input-repair-v1';inv=load(base/'inventory.json');records=[]
 for r in inv['owned_files']+inv['external_read_only_evidence']:
  records.append({'original_path':r['path'],'original_bytes':r['bytes'],'original_sha256':r['sha256'],'storage':'lossless_gzip_body','immutable_stored_body':pin(B/r['body'])})
 out.append({'capture':pin(base/'inventory.json'),'complete_records':records})
 records=[]
 for r in load(B/'source/pre-peer-body-map.json'):
  z=(B/r['frozen_body']).read_bytes();raw=gzip.decompress(z);assert sha(raw)==r['raw_sha256']
  records.append({'original_path':str((B/r['witness_path']).resolve().relative_to(S.resolve())),'literal_witness_path':r['witness_path'],'original_bytes':len(raw),'original_sha256':r['raw_sha256'],'storage':'lossless_gzip_body','immutable_stored_body':pin(B/r['frozen_body'])})
 out.append({'capture':pin(B/'source/pre-peer-body-map.json'),'complete_records':records});return out

def main():
 c=load(T/'priority-set.json');tm=load(T/'asset-manifest.json');bm=load(B/'asset-manifest.json')
 assert sha((T/'asset-manifest.json').read_bytes())=='2ebe89804819e1accc04c80c96800f3e2a9cf49b777e1139f321fcbb99444a76'
 assert sha((B/'asset-manifest.json').read_bytes())=='c725c0069e8409d9667ef0ce674a14bea20456410bdee4e50eb0e44b4e5846b9'
 assert len(c)==23 and len(c['all_36_county_parents'])==36 and c['complete_coverage'] is False
 assert c['complete_order'] is c['ordered_priority_keys'] is c['top15'] is c['minimum80'] is c['remainder'] is None
 refs={}
 for row in tm['owned_assets']+bm['assets']+tm['shared_assets']+load(B/'source/shared-assets.json'):
  p=S/row['path'];actual=pin(p);assert actual=={k:row[k] for k in ['path','bytes','sha256']},row['path'];refs[(row['path'],row['sha256'])]=actual
 for p in [T/'asset-manifest.json',B/'asset-manifest.json']:r=pin(p);refs[(r['path'],r['sha256'])]=r
 companions=[];counts=collections.Counter();parts=[];chunk=[];global_i=0
 def flush():
  nonlocal chunk
  if not chunk:return
  raw=b''.join(chunk);p=D/f'coordinator-full-source-object-refs-v1-{len(parts)+1:04d}.jsonl.gz';p.write_bytes(gzip.compress(raw,mtime=0));rows=[json.loads(l) for l in chunk];parts.append({**pin(p),'complete_reconstructed_bytes':len(raw),'complete_reconstructed_sha256':sha(raw),'complete_object_count':len(chunk),'source_objects_by_file':dict(collections.Counter(x['source_path'] for x in rows)),'format':'Replay every ordered reference in the complete partition; no sampling or votes-only projection.'});chunk=[]
 for p in select():
  x=parsed(p);name=str(p.relative_to(S));companions.append({**pin(p),'full_semantic_sha256':sem(x),'semantic_type':type(x).__name__,'complete_length':len(x) if isinstance(x,(dict,list)) else None,'format':'jsonl_array' if '.jsonl' in p.name else 'csv_complete_rows_with_header' if p.suffix=='.csv' else 'json','complete_body_required':True,'projection_or_subset_substitution':False})
  for pointer,obj in walk(x):
   row={'ordinal':global_i,'source_path':name,'pointer':pointer,'full_recursive_semantic_sha256':sem(obj),'semantic_type':type(obj).__name__,'complete_length':len(obj)};chunk.append(enc(row)+b'\n');global_i+=1;counts[name]+=1
   if len(chunk)>=150000:flush()
  print('companion',len(companions),'objects',global_i,name,flush=True) if len(companions)%200==0 else None
 flush();known=load(T/'known-native-ranking.json');unknown=[p for p in c['all_36_county_parents'] if p['unknown_native_membership']];assert len(known['full_order'])==510 and len(unknown)==31
 roots=[{'pointer':'/'+k.replace('~','~0').replace('/','~1'),'full_recursive_semantic_sha256':sem(v)} for k,v in c.items()]
 reviews=['coordinator-turnout-original-review.json','coordinator-turnout-reciprocal-final-review.json','coordinator-baseline-source-review.json','coordinator-baseline-math-review.json','coordinator-baseline-input-review/review.json','coordinator-baseline-repair-review.json']
 a={'schema':'OR-qualified-complete-available-source-research-authority-v1','status':'accepted_complete_available_source_research_canonical_native_priority_unavailable','state':'OR','coordinator_agent_id':'d0fc3534-1613-4883-b48b-21a233fcfd9e','authority':'PATH ONLY in downstream owned outputs; consume the full external authority in memory, never copy/reverse-pin its body/hash or mutate producer flags.','frozen_contract':pin(T/'priority-set.json'),'producer_seals':[pin(T/'asset-manifest.json'),pin(B/'asset-manifest.json')],'frozen_first_pair_assets':list(refs.values()),'independent_coordinator_reviews':[pin(D/n) for n in reviews],'all_county_research_parents':36,'all_known_2024_native_observations':510,'unavailable_2024_county_native_universes':31,'statewide_reported_choice_votes':2244493,'statewide_named_candidate_votes':2229467,'generic_Misc_eligibility':'unknown; reported15026 not allocated to eligible named choices','known_source_votes':1128521,'unknown_native_parent_votes':1115972,'ordered_research_parent_keys':[p['county_key'] for p in c['all_36_county_parents']],'all_complete_parent_objects':c['all_36_county_parents'],'known_ordered_native_keys':c['known_source_universe']['full_ordered_keys'],'known_source_scope_only':c['known_source_universe'],'unavailable_parent_keys':[p['county_key'] for p in unknown],'certified_native_full_order':None,'certified_native_top15':None,'certified_native_minimum80':None,'ordered_priority_keys':None,'canonical_remainder_keys':None,'coverage_sequence_is_certified_vote_order':False,'complete_root_field_semantics':roots,'complete_source_companion_files':companions,'complete_source_object_reference_bodies':parts,'complete_source_object_count':global_i,'source_objects_by_file':dict(counts),'immutable_historical_snapshot_body_resolvers':snapshot_resolvers(),'full_field_rule':'Reconstruct every23rootfield, everywhole companion/header/candidate/method/control/null/rawposition/schema object and every ordered container across all complete ledger partitions. Every original full byte remains independently pinned; histories resolve oldpath+expectedSHA through exact captured bodies. No current replacement, truncation/projection, mutable news aggregate/helper/peer directory, producer writer or optional unfinished coordinator/peer dependency.','source_partitions':{'all_county_candidate_Misc_positions':864,'counties_each':36,'known_2024_native':510,'known_2024_parents':5,'unavailable_2024_parents':31,'turnout_native_observed_publications':3138,'baseline_native_observed_publications':3031,'ZIP_members':72,'baseline_original_text_entities':113,'baseline_historical_closure_counts':[16,13,13],'turnout_historical_closure_counts':[16,13,12],'unclosed_Douglas2022_differences':'Onecandidate/17mappedcontrols including16literalreverse differences. Unknown/unclosed, excluded closed scenarios, no peer/source repair.'},'dispatch_requirements':['Official-source inventories actual state/all36county roles/links/blanks and bounded public chains, then preserves all510complete known contexts and all31unknown-parent cases. These are qualified shared-parent investigations, not510livefeeds or a certified native priority.','Maps acquires actual qualified resources across all36county chains, preserving all510known full contexts and all31unavailable native-parent cases; source/vintage/physical/current/finer/legal gaps stay explicit. No county/native213/11substitution, private/write-in residual allocation or inferred child/current join.'],'current_geography_approved':False,'current_November_returns_admitted':False,'current_choice_or_reporting_IDs_approved':False,'legal_native_80_robustness_approved':False,'live_cadence_or_exact_remainder_approved':False,'collector_or_probability_approval':False}
 p=D/'coordinator-source-research-acceptance.json';p.write_text(json.dumps(a,ensure_ascii=False,indent=2,allow_nan=False)+'\n');assert p.stat().st_size<40000000;print(json.dumps({'authority':pin(p),'root_fields':len(roots),'whole_companions':len(companions),'recursive_objects':global_i,'complete_partitions':len(parts),'frozen_file_pins':len(refs),'canonical_native_priority':None}))
if __name__=='__main__':main()
