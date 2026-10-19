"""Recompute immutable reciprocal extensions without replacing earlier bodies."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def body(a):
 z=(ROOT/a['stored_path']).read_bytes();b=gzip.decompress(z);assert len(z)==a['stored_bytes']and sha(z)==a['stored_sha256']and len(b)==a['original_bytes']and sha(b)==a['original_sha256'];return b
def write(name,out):
 p=DATA/name;b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
def main():
 specs=[(2018,'native-2018-peer-10views-v1','15d16b6616189bf08a0fb4d807ebacb2f2ff64669b8fabc3ac31eba4c790d470','8de6e52733e8c995cddb7c679108354b63b8707526b3782a1ed6437a5e067cbe',10,528,114),(2020,'native-2020-peer-41views-v3','11a6bc9555e055aa6e94ff2ab4f7f3aead02db890d6c81b0a686ed30ce92e2ab','8e9002b8e31562a89b396088853b51281f53cd9d05c8558f66ff1c4a6fcec8fb',41,2475,565),(2018,'native-2018-peer-12views-v2','8bc8e24cd8332a8d07fb4a22972b5c370e6d204e118b3f5967e3d65181dfa704','a540aa5952eb5cf6233d51afe39413716ff698851436d39d56247d4d489fdf7c',12,660,136)]
 for year,folder,expected_snapshot,expected_result,views,positions,native in specs:
  base=DATA/'baselines/source'/folder;sp=base/'snapshot.json';rp=base/'reconciliation.json';assert pin(sp)['sha256']==expected_snapshot and pin(rp)['sha256']==expected_result;s=json.loads(sp.read_bytes());result=json.loads(rp.read_bytes());assert result['peer_snapshot']==pin(sp)
  own_witness=s.get('own_original_witness',s.get('own_witness'));assert pin(ROOT/own_witness['path'])==own_witness;own_input=s.get('own_flat_input',s.get('own_flat'));own_raw=body(own_input);own={}
  for r in csv.DictReader(io.StringIO(own_raw.decode())):
   k=(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']);assert k not in own;own[k]=r
  inputs=[];captured={};allrows=[]
  for a in s['pins']:
   b=body(a);captured[a['original_path']]=b;inputs.append(dict(original_path=a['original_path'],original_bytes=len(b),original_sha256=sha(b),lossless_copy=pin(ROOT/a['stored_path'])))
   if a['original_path'].endswith('.csv'):allrows.extend(csv.DictReader(io.StringIO(b.decode())))
  roles=collections.Counter();sourcehashes={};seen=set();units=set();aliases=[];key_wrapper_examples={};rolemap={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL','unused_template_column':'unused'}
  for r in allrows:
   p=int(r['source_pdf_page']if year==2018 else r['source_page']);c=int(r['physical_source_column']if year==2018 else r['source_column']);k=(r['source_id'],p,c,r['candidate']);assert k not in seen;seen.add(k);a=own[k];role=rolemap[r['role']]if year==2018 else r['role'];assert role==a['role']and r['source_raw_sha256']==a['source_raw_sha256'];sourcehashes[r['source_id']]=r['source_raw_sha256'];roles[role]+=1
   value=None if r['votes']==''else int(r['votes']);assert value==(None if a['votes']==''else int(a['votes']))
   label=r.get('literal_source_header',r.get('literal_native_label',r.get('label_literal')));assert ' '.join(label.split())==' '.join(a['literal_native_label'].split())
   if label!=a['literal_native_label']:aliases.append(dict(source_key_components=list(k),turnout_literal=label,baseline_literal=a['literal_native_label']))
   if 'county_fips'in r:assert r['county_fips']==a['county_fips']
   if role in['native','source_native_reporting_constituent']:units.add(k[:3])
   if r['source_id']not in key_wrapper_examples:key_wrapper_examples[r['source_id']]=dict(turnout_key=r.get('source_native_key',r.get('native_source_key')),baseline_key=a['source_key'],compared_components=list(k[:3]))
  assert len(seen)==positions and len(sourcehashes)==views and len(units)==native
  if year==2018:
   expected_roles=dict(native=342,TOTAL=30,unused=156) if views==10 else dict(native=408,TOTAL=36,unused=216)
   assert dict(roles)==expected_roles and not result['differences'];assert result['source_candidate_positions']==positions and result['source_stage_views']==views and result['source_native_observations']==native
  else:
   assert dict(roles)==dict(source_native_reporting_constituent=1695,source_TOTAL=123,unused_template_column=657);assert not result['value_role_differences']and not result['label_differences_after_whitespace_only'];assert result['compared_positions']==positions and result['native_constituents']==native
  continuity={}
  if year==2018 and views==12:
   previous_path=ROOT/s['prior_witness']['path'];assert pin(previous_path)==s['prior_witness'];previous=json.loads(previous_path.read_bytes());old={a['original_path']:a for a in previous['pins']};assert len(old)==10
   new=[]
   for a in s['pins']:
    if a['original_path']in old:assert a==old[a['original_path']]and body(a)==body(old[a['original_path']])
    else:
     p=DATA/'coordinator-qa/turnout-2018-two-stage-replays'/(Path(a['original_path']).name+'.gz');assert gzip.decompress(p.read_bytes())==body(a);new.append(dict(original_path=a['original_path'],earlier_coordinator_copy=pin(p)))
   assert len(new)==2 and result['prior_ten_bodies_reused_byte_exact']
   continuity=dict(prior10_snapshot=pin(previous_path),exact_prior_derivative_bodies_reused=10,new_Yalobusha_bodies_matching_coordinator_transcripts=new,all12_current_working_body_identity_claimed=False)
  if year==2020:
   previous=json.loads((ROOT/s['prior38_witness']['path']).read_bytes());assert pin(ROOT/s['prior38_witness']['path'])==s['prior38_witness'];old={a['original_path']:a for a in previous['pins']};assert len(old)==76
   new=[]
   for a in s['pins']:
    if a['original_path']in old:assert a==old[a['original_path']]and body(a)==body(old[a['original_path']])
    else:
     p=DATA/'coordinator-qa/turnout-2020-native-extensions'/(Path(a['original_path']).name+'.gz');assert gzip.decompress(p.read_bytes())==body(a);new.append(dict(original_path=a['original_path'],earlier_coordinator_copy=pin(p)))
   assert len(new)==6
   continuity=dict(prior38_snapshot=pin(ROOT/s['prior38_witness']['path']),exact_prior_derivative_bodies_reused=76,new_derivative_bodies_matching_coordinator_transcripts=new,earlier17_JSON_comparison_metadata_history=pin(DATA/'coordinator-2020-peer-metadata-history-review.json'),all41_current_working_body_identity_claimed=False)
  rasterpins=[]
  for a in result['source_page_render_pairs']:
   for side in['own','peer']:
    p=ROOT/a[side+'_raster'];v=pin(p);assert v['sha256']==a[side+'_raster_sha256'];rasterpins.append(v)
  out=dict(status='pass_bounded_recomputed_immutable_reciprocal_extension',election_year=year,snapshot=pin(sp),worker_reconciliation=pin(rp),original_independent_witness=own_witness,original_flat_input=own_input,exact_captured_derivative_pins=inputs,source_views=views,source_native_observations_across_stages_or_versions=native,candidate_positions=positions,candidate_positions_by_role=dict(roles),source_original_hashes=sourcehashes,whitespace_only_literal_header_aliases=aliases,source_key_wrapper_examples=key_wrapper_examples,original_raster_pair_pins=rasterpins,earlier_body_continuity=continuity,qualification='All captured lossless bodies, own original witness/flat and represented candidate fields recompute at raw original hash/source/page/physical-column/value/role/whitespace-folded literal header. Keys are compared only by explicit components; different FIPS-prefix wrappers remain literal examples. Both raster hashes survive without raster/crop/parsedID/current identity equality. For2020,76 exact prior38 bodies are reused and only six new bodies added; their earlier peer declarations stay frozen, not a claim all41 currently mutable bodies match. For2018,ten represented stages are the bounded reciprocal scope, not every later turnout or baseline stage. This is source comparison rather than fresh coordinator glyph reading of all fields or whole historical/native-method/current-geography/native887 acceptance.',formal_native887_dispatch_accepted=False,complete_historical_native_peer_review=False,current_geography_approved=False)
  if year==2018 and views==12:out['qualification']=out['qualification'].replace('For2018,ten represented stages are the bounded reciprocal scope','For2018,twelve represented stages retain exactly ten earlier derivative bodies plus two new Yalobusha bodies and are the bounded reciprocal scope')
  write(f'coordinator-historical-native-{year}-reciprocal-{views}views-review.json',out)
if __name__=='__main__':main()
