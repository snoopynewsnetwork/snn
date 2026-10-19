"""Independently verify bounded reciprocal CSV positions against immutable original-derived views."""
from pathlib import Path
import collections,csv,gzip,io,json,re
from review_allfield_milestone import DATA,ROOT,NAMES,load,sources,sha,pin

def main():
 p=DATA/'baselines/source/presidential-peer-through-batch26-v3/snapshot.json';b=p.read_bytes();assert sha(b)=='19b49aa4c79b631115df62751fc0f245f52a619ab2db8e6c4affac059fc2717f';m=json.loads(b);recp=p.parent/'reconciliation.json';rb=recp.read_bytes();assert sha(rb)=='5fc0efdb27a8e4e05c41706c22e4c7e46fb17d2e878a932546b43a8bb22fcfb3';rec=json.loads(rb)
 _,ownitems,ownpin=load('82views','94576fcfa4b7b245e2d5baa9e8366e4489594804f41694ea04a9f6315e46b336');ss=sources(ownitems);flat=[];bodypins=[];rawrefs={};keys=set();roles=collections.Counter();by=collections.defaultdict(collections.Counter)
 assert len(m['pins'])==60
 for item in m['pins']:
  q=ROOT/item['stored_path'];z=q.read_bytes();assert len(z)==item['stored_bytes']and sha(z)==item['stored_sha256'];raw=gzip.decompress(z);assert len(raw)==item['original_bytes']and sha(raw)==item['original_sha256'];bodypins.append(pin(q))
  if item['original_path'].endswith('.csv'):flat.extend(csv.DictReader(io.StringIO(raw.decode())))
  else:assert isinstance(json.loads(raw),dict)
 for item in rec['own_original_reading_inputs']:
  name=Path(item['path']).name;assert len(ownitems[name])==item['bytes']and sha(ownitems[name])==item['sha256']
 for row in flat:
  if row['candidate']not in NAMES[:9]:continue
  sid=row['source_id'];page=int(row['source_page']);col=int(row['source_column'])-1;key=(sid,page,col,row['candidate']);assert key not in keys;keys.add(key);s=ss[sid];p0=next(x for x in s['pages']if x['page']==page);f=next(x for x in p0['fields']if x['candidate']==row['candidate']);v=row.get('direct_original_value',row.get('direct_original_visual_value'));v=None if v==''else int(v);assert v==f['values'][col]and row['source_raw_sha256']==s['raw_sha256']
  role={'native_reporting_constituent':'source_native_reporting_constituent'}.get(row['role'],row['role']);assert role==p0['roles'][col]
  label=p0['headers'][col]['label_literal']if'headers'in p0 else p0['labels_literal'][col]if col<len(p0['labels_literal'])else'';assert re.sub(r'\s+','',label)==re.sub(r'\s+','',row['label_literal'])
  short={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL','unused_template_column':'unused'}[role];roles[short]+=1;by[sid][short]+=1
  if sid not in rawrefs:
   rr=next(x for x in json.loads((DATA/'baselines/source/references.json').read_bytes())if x['id']==sid);r=gzip.decompress((ROOT/rr['path']).read_bytes());assert sha(r)==s['raw_sha256'];rawrefs[sid]={'source_id':sid,'raw_sha256':sha(r)}
 assert len(keys)==rec['compared_positions']==17991 and len(by)==rec['source_views']==73 and dict(roles)==rec['candidate_positions_by_role']=={'native':13995,'TOTAL':657,'unused':3339}
 assert {k:dict(v)for k,v in by.items()}==rec['source_counts']
 for k in ['value_differences','label_differences_after_whitespace_only','role_differences','missing_own_positions']:assert not rec[k]
 assert rec['bounded_preferred_source_views_including_separate_two']==75 and rec['bounded_preferred_native_constituents_including_separate_two']==1590 and rec['remaining_preferred_source_views']==7 and rec['remaining_preferred_native_constituents']==146
 out={'status':'pass_bounded_reciprocal_through_batch26_frozen_bodies_and_source_positions','snapshot_pin':pin(p),'reconciliation_pin':pin(recp),'independent_own_original82_snapshot_pin':ownpin,'complete_frozen_derivative_body_pins':bodypins,'compared_positions':len(keys),'source_views':len(by),'candidate_positions_by_role':dict(roles),'source_raw_hashes_verified':list(rawrefs.values()),'combined_with_separately_pinned_Alcorn_Coahoma_all11_scope':{'preferred_views':75,'native_constituents':1590,'remaining_preferred_views':7,'remaining_preferred_native':146},'qualification':'All60lossless derivative bodies, five own original-input byte pins, and all17991nine-presidential positions match the immutable82-source original-derived ledger at raw source hash/page/physical ordinal/value/role/whitespace-only label. Separate original two-view all11scope is not silently merged into this comparison count. This witness predates later independent batches27-33 and remains unchanged; numeric polygons, optionalIDs and raster equivalence are not asserted. No new glyph transcription or whole historical/method/current-geography/dispatch acceptance follows.','formal_dispatch_accepted':False,'current_geography_approved':False}
 p=DATA/'coordinator-presidential-peer-through26-v3-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable reciprocal review drift'
 else:p.write_bytes(b)
 print(json.dumps({'status':out['status'],'positions':len(keys),'output_pin':pin(p)}))
if __name__=='__main__':main()
