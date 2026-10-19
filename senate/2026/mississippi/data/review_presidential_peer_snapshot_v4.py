"""Independently verify bounded reciprocal CSV positions against immutable original-derived views."""
from pathlib import Path
import collections,csv,gzip,io,json,re
from review_allfield_milestone import DATA,ROOT,NAMES,load,sources,sha,pin

def main():
 p=DATA/'baselines/source/presidential-peer-through-batch33-v4/snapshot.json';b=p.read_bytes();assert sha(b)=='ef8ab766c1edf4f1d7b8c21041548f96480c887717a98fd61a01def7bad56a1e';m=json.loads(b);recp=p.parent/'reconciliation.json';rb=recp.read_bytes();assert sha(rb)=='0bef68d069e6999edd784bfcf55718729210dbd5408b5240548dc6b61b78848b';rec=json.loads(rb)
 _,ownitems,ownpin=load('82views','94576fcfa4b7b245e2d5baa9e8366e4489594804f41694ea04a9f6315e46b336');ss=sources(ownitems);flat=[];bodypins=[];rawrefs={};keys=set();roles=collections.Counter();by=collections.defaultdict(collections.Counter)
 assert len(m['pins'])==74
 for item in m['pins']:
  q=ROOT/item['stored_path'];z=q.read_bytes();assert len(z)==item['stored_bytes']and sha(z)==item['stored_sha256'];raw=gzip.decompress(z);assert len(raw)==item['original_bytes']and sha(raw)==item['original_sha256'];bodypins.append(pin(q))
  if item['original_path'].endswith('.csv'):flat.extend(csv.DictReader(io.StringIO(raw.decode())))
  else:assert isinstance(json.loads(raw),dict)
 for item in rec['own_original_reading_inputs']:
  name=Path(item['path']).name;assert len(ownitems[name])==item['bytes']and sha(ownitems[name])==item['sha256']
 aliases=[]
 for row in flat:
  if row['candidate']not in NAMES[:9]:continue
  sid=row['source_id'];page=int(row['source_page']);col=int(row['source_column'])-1;key=(sid,page,col,row['candidate']);assert key not in keys;keys.add(key);s=ss[sid];p0=next(x for x in s['pages']if x['page']==page);f=next(x for x in p0['fields']if x['candidate']==row['candidate']);v=row.get('direct_original_value',row.get('direct_original_visual_value'));v=None if v==''else int(v);assert v==f['values'][col]and row['source_raw_sha256']==s['raw_sha256']
  role={'native_reporting_constituent':'source_native_reporting_constituent'}.get(row['role'],row['role']);assert role==p0['roles'][col]
  label=p0['headers'][col]['label_literal']if'headers'in p0 else p0['labels_literal'][col]if col<len(p0['labels_literal'])else'';assert re.sub(r'\s+','',label)==re.sub(r'\s+','',row['label_literal'])
  if re.sub(r'\s+',' ',label).strip()!=re.sub(r'\s+',' ',row['label_literal']).strip():aliases.append({'key':[sid,page,col+1,row['candidate']],'own':label,'peer':row['label_literal']})
  short={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL','unused_template_column':'unused','parallel_native_observation':'parallel'}[role];roles[short]+=1;by[sid][short]+=1
  if sid not in rawrefs:
   rr=next(x for x in json.loads((DATA/'baselines/source/references.json').read_bytes())if x['id']==sid);r=gzip.decompress((ROOT/rr['path']).read_bytes());assert sha(r)==s['raw_sha256'];rawrefs[sid]={'source_id':sid,'raw_sha256':sha(r)}
 assert len(keys)==rec['compared_positions']==19872 and len(by)==rec['source_views']==80 and dict(roles)==rec['candidate_positions_by_role']=={'native':15309,'TOTAL':720,'unused':3744,'parallel':99}
 assert {k:dict(v)for k,v in by.items()}==rec['source_counts']
 for k in ['value_differences','label_differences_after_whitespace_only','role_differences','missing_own_positions']:assert not rec[k]
 assert rec['bounded_preferred_source_views_including_separate_two']==82 and rec['bounded_preferred_native_constituents_including_separate_two']==1736 and rec['remaining_preferred_source_views']==0 and rec['remaining_preferred_native_constituents']==0
 assert len(aliases)==rec['label_representation_alias_count']==18
 recorded={tuple(x['key']):(x['own'],x['peer'])for x in rec['label_representation_aliases_after_whitespace_only']}
 assert {tuple(x['key']):(x['own'],x['peer'])for x in aliases}==recorded
 assert {tuple(x['key'][:3])for x in aliases}=={('sos-2024-county-holmes',3,1),('sos-2024-county-holmes',3,4)}
 outside=rec['own_positions_outside_peer_flat_scope'];assert len(outside)==rec['own_positions_outside_peer_flat_scope_count']==126
 for x in outside:
  sid,page,column,name=x['key'];assert (sid,page,column-1,name)not in keys and x['role']=='unused'and x['value']is None
  pp=next(p for p in ss[sid]['pages']if p['page']==page);f=next(f for f in pp['fields']if f['candidate']==name);assert pp['roles'][column-1]=='unused_template_column'and f['values'][column-1]is None
 assert not rec['complete_all_blank_position_peer_scope']and not rec['all_labels_identical_after_whitespace_only']
 out={'status':'pass_reciprocal_through_batch33_frozen_bodies_with_explicit_blank_and_label_scope','snapshot_pin':pin(p),'reconciliation_pin':pin(recp),'independent_own_original82_snapshot_pin':ownpin,'complete_frozen_derivative_body_pins':bodypins,'compared_positions':len(keys),'source_views':len(by),'candidate_positions_by_role':dict(roles),'source_raw_hashes_verified':list(rawrefs.values()),'combined_with_separately_pinned_Alcorn_Coahoma_all11_scope':{'preferred_views':82,'native_constituents':1736,'remaining_preferred_views':0,'remaining_preferred_native':0},'explicit_literal_label_representation_aliases':aliases,'unused_null_positions_outside_peer_scope':outside,'qualification':'All74lossless derivative bodies, five own original-input pins, and19872nine-presidential positions across80views match immutable82-source original readings at raw hash/page/physical ordinal/value/role. Combining the separately pinned original Alcorn/Coahoma scope covers all82preferred native vectors.126older Perry/Tunica unprinted null fields remain outside peer CSV scope, not filled.18Holmes candidate positions retain exactly two A-hyphen-line-wrap-Z versus A-hyphen-Z representations: ordinary whitespace collapse differs while deletion of whitespace agrees. Both raw forms are recorded without rewriting source ledgers or claiming identical labels. No exact polygons, optionalIDs/raster agreement, full historical-method/current-geography or dispatch acceptance follows.','formal_dispatch_accepted':False,'current_geography_approved':False}
 p=DATA/'coordinator-presidential-peer-through33-v4-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable reciprocal review drift'
 else:p.write_bytes(b)
 print(json.dumps({'status':out['status'],'positions':len(keys),'output_pin':pin(p)}))
if __name__=='__main__':main()
