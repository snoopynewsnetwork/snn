"""Independent fixed-source arithmetic audit of new complete-field887 proposal.
Does not import the producer. Uses separately pinned peer all11 original-read
body only after own all82 transcription and source-position comparison.
"""
import collections,csv,gzip,io,json
from sources import OUT,BASE,sha,save

def main():
 sp=OUT/'source/native-priority-v2/snapshot.json';s=json.loads(sp.read_text());docs={}
 for p in s['pins']:
  z=(BASE/p['frozen_path']).read_bytes();r=gzip.decompress(z);assert sha(z)==p['stored_sha256'] and len(z)==p['stored_bytes']<40000000 and sha(r)==p['original_sha256'] and len(r)==p['original_bytes'];assert r==(BASE/p['original_path']).read_bytes();docs[p['original_path'].split('/')[-1]]=r
 d=json.loads(docs['native-priority-contract-v2.json']);flat=list(csv.DictReader(io.StringIO(docs['native-priority-source-fields-v2.csv'].decode())));peerpath=BASE/'data/turnout/source/2024-preferred-all11-source-fields-v1.json.gz';z=peerpath.read_bytes();r=gzip.decompress(z);assert sha(z)=='d066e45bebca7ba66163989165a430164f5b84cef61d9e2cda7e4bc4e1d23b6b' and sha(r)=='b2a7e234eeb226bd13f35d3a4c32c867f88f7d59a680ec059a7378c036f1fbae';peer=json.loads(r);pb={(c['source_id'],c['source_page'],c['source_column']):c for c in peer['columns']};assert len(pb)==2266
 native={};seen=set();counts=collections.Counter();sums=collections.Counter();aliases=[]
 for c in d['all_preferred_source_columns']:
  k=(c['source_id'],c['PDFpage'],c['physical_source_column']);assert k not in seen;seen.add(k);p=pb[k];assert c['source_raw_sha256']==p['source_raw_sha256'] and c['county_fips']==p['parent_county_fips'];assert c['candidate_votes']==p['Senate_candidate_votes']|p['president_candidate_votes'];pr='TOTAL' if p['role'] in ['TOTAL','source_TOTAL'] else 'unused' if p['role'] in ['unused','unused_template_column'] else 'parallel' if p['role']=='parallel_native_observation' else 'native';assert c['role']==pr;counts[pr]+=1
  if ' '.join(c['label_literal'].split())!=' '.join(p['label_literal'].split()):
   assert k in [('sos-2024-county-holmes',3,1),('sos-2024-county-holmes',3,4)];aliases.append(dict(source_key=k,own=c['label_literal'],peer=p['label_literal']))
  if pr=='native':native[c['source_position_key']]=c;sums.update(c['candidate_votes'])
 assert seen==set(pb) and counts==dict(native=1736,TOTAL=82,unused=437,parallel=11)
 pair=lambda k:native[k]['candidate_votes']['Ty Pinkins']+native[k]['candidate_votes']['Roger F. Wicker'];order=sorted(native,key=lambda k:(-pair(k),k));assert order==d['ordered_native_keys'];D=sum(map(pair,order));assert D==1215400;cum=0;minimum=None;parents=collections.defaultdict(list);priorityparents=collections.defaultdict(list)
 for i,(key,row) in enumerate(zip(order,flat),1):
  cum+=pair(key);assert key==row['key'] and i==int(row['rank']) and cum==int(row['cumulative_named_Senate_votes']) and pair(key)==int(row['named_Senate_pair_votes']) and json.loads(row['candidate_votes'])==native[key]['candidate_votes'];f=native[key]['county_fips'];parents[f].append(key)
  if 5*cum>=4*D and minimum is None:minimum=i
  if i<=887:priorityparents[f].append(key)
 assert len(flat)==len(order)==1736 and minimum==887 and sum(map(pair,order[:886]))==972157 and sum(map(pair,order[:887]))==972656 and pair(order[886])==499 and sum(map(pair,order[:15]))==60019 and sum(map(pair,order[887:]))==242744
 assert d['ordered_priority_native_keys']==order[:887] and d['ordered_nonpriority_native_keys']==order[887:] and len(priorityparents)==77 and len(parents)==82
 assert d['parent_all_native_keys']==dict(parents) and d['parent_priority_native_keys']=={f:priorityparents.get(f,[]) for f in parents}
 assert 5*(972157+1)<4*1215400 and 5*(972157+1)<4*1215401 and max(pair(k) for k in order if native[k]['source_id']=='sos-2024-county-tunica')+1<499
 vp=BASE/d['previous_v1']['path'];assert sha(vp.read_bytes())==d['previous_v1']['sha256'];assert not d['coordinator_accepted'] and not d['current2026_geography_approved'];assert sums==d['source_native_candidate_sums'];assert sum(v for n,v in sums.items() if n not in ['Ty Pinkins','Roger F. Wicker'])==1228007
 save(OUT/'native-priority-v2-independent-validation.json',dict(status='pass_independent_source_position_order_and_integer_prefix_audit',snapshot_path=str(sp.relative_to(BASE)),snapshot_bytes=sp.stat().st_size,snapshot_sha256=sha(sp.read_bytes()),source_columns=2266,all11_candidate_positions=24926,native_units=1736,full_order_matches=True,exact_minimum80=887,preceding886=972157,priority887=972656,top15native=60019,nonpriority849=242744,all82_parent_allchild_maps_match=True,priority_parent_authorities=77,blank_and_Kemper_parallel_roles_preserved=True,Holmes_label_representation_aliases=aliases,source_pair_denominator=1215400,separate_certified_pair_denominator=1215401,Tunica1_unallocated_upper_bound_passes=True,source_presidential_named_denominator=1228007,certified_presidential_named_denominator=1228008,previous_v1_byte_hash_verified=True,coordinator_accepted=False,current2026_geography_approved=False,qualification='Independent producer-free reciprocal numerical/source-role comparison to frozen peer all11 after own original82. No full new glyph reread, raster/window/optionalID/currentgeography or dispatch approval.'))
 print('PASSindependentv2 all24926/1736/887/77parents; unallocatedTunica limits')
if __name__=='__main__':main()
