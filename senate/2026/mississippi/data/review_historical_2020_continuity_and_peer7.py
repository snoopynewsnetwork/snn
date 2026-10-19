"""Check immutable historical source continuity and the first reciprocal replay."""
from pathlib import Path
import argparse,collections,copy,csv,gzip,hashlib,io,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
VERSIONS=[7,11,22,34,40,41,50,55,60,65,70,75,80,85,90,95,104]
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def unpack(s):
 out={}
 for a in s['pins']:
  z=(ROOT/a['stored_path']).read_bytes();assert len(z)==a['stored_bytes']and sha(z)==a['stored_sha256'];b=gzip.decompress(z);assert len(b)==a['original_bytes']and sha(b)==a['original_sha256'];out[Path(a['original_path']).name]=b
 return out
def save(name,out):
 p=DATA/name;b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable proof changed'
 else:p.write_bytes(b)
 return pin(p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--through',type=int,default=60,choices=VERSIONS);args=ap.parse_args()
 previous={};chain=[]
 for v in [v for v in VERSIONS if v<=args.through]:
  p=DATA/f'baselines/source/native-2020-{v}views-v1/snapshot.json';s=json.loads(p.read_bytes());items=unpack(s);sources={}
  for n in ['coahoma-2020-amendment-readings.json','native-2020-additional-readings.json']:
   for a in json.loads(items[n])['sources']:assert a['source_id']not in sources;sources[a['source_id']]=a
  assert set(previous)<=set(sources)
  corrections=[]
  for k,a in previous.items():
   if a!=sources[k]:
    assert v==70 and k=='sos-2020-county-kemper',(v,k)
    amended=copy.deepcopy(a);page=next(p for p in amended['pages']if p['page']==2);col=next(c for c in page['columns']if c['source_column']==9);assert col['label_literal']=='Lynnville';col['label_literal']='Lynville'
    newpage=next(p for p in sources[k]['pages']if p['page']==2);evidence=newpage['header_reading_evidence'];assert len(evidence)==1;e=evidence[0]
    assert e['source_column']==9 and e['bounds']==col['header_bounds']and e['rotate_ccw']==-90 and e['accepted_literal']=='Lynville'and e['initial_manual_literal']=='Lynnville'and e['correction_kind']=='literal_header_glyph_reread'and e['supersedes_immutable_versions']==['55views-v1','60views-v1','65views-v1']
    ep=pin(ROOT/e['evidence_path']);assert ep['sha256']==e['evidence_sha256']and ep['bytes']==e['evidence_bytes'];assert 'header_reading_evidence'not in page;page['header_reading_evidence']=copy.deepcopy(evidence);assert amended==sources[k],(v,k,'Unqualified source change')
    proof=DATA/'coordinator-kemper-2020-original-header-review.json';assert pin(proof)['sha256']=='c28cae19bb9c414c315b369cef9fdf15b79e6c5fa8d4196923666813649accf2'
    corrections.append(dict(source_id=k,actual_PDFpage=2,physical_column=9,field='label_literal',earlier='Lynnville',new_original_read='Lynville',original_source_review=pin(proof),new_worker_original_header_reading_evidence=ep,candidate_values_raw_render_and_original_positions_unchanged=True,all_other_source_semantics_unchanged_except_explicit_added_header_evidence=True))
  item=dict(version=v,snapshot=pin(p),preserved_predecessor_source_ledgers=len(previous)-len(corrections),source_publications=len(sources),counts=s['counts'])
  if corrections:item['explicit_original_label_corrections']=corrections
  chain.append(item)
  previous=sources
 continuity=dict(status='pass_exact_prior_original_source_ledger_continuity',chain=chain,qualification='Each lossless source ledger from every earlier announced witness is semantically unchanged in its successor. Counts across alternative publications and selected82 coverage remain separate. No historical same-vintage identity, statewide peer completion, complete native methods or native887 dispatch approval follows.',formal_native887_dispatch_accepted=False)
 if args.through>=70:
  continuity['status']='pass_prior_source_continuity_with_explicit_original_label_correction'
  continuity['qualification']='Every earlier source ledger survives unchanged except the precisely identified KemperPDF2physical9 literal-label correction Lynnville to original Lynville in70 and its explicit added original header-reading evidence. Both raw forms and independent original evidence remain, with all candidate values/raw/render hashes/positions/other source semantics unchanged. This is not an unconditional semantic-identity claim or label normalization. Alternative-publication versus selected82 counts remain separate; no same-vintage/current geographic join, full independent historical/method or native887 acceptance follows.'
 cp=save(f'coordinator-historical-native-2020-through{args.through}-continuity-review.json',continuity)
 folder=DATA/'baselines/source/native-2020-peer-seven-v1';sp=folder/'snapshot.json';rp=folder/'reconciliation.json';assert pin(sp)['sha256']=='1c77d9d6cff2bc158f71f2614ea11615d01ffd23216cbedd26542a045b0a88c1';assert pin(rp)['sha256']=='9ff4ffbe5f18845486f8f4107a6781d7ab103a487c5736fc370b2fe77853265d'
 snap=json.loads(sp.read_bytes());report=json.loads(rp.read_bytes());bodies=unpack(snap);assert len(bodies)==14
 sixty=DATA/'baselines/source/native-2020-60views-v1/snapshot.json';assert snap['own_original_witness']==pin(sixty)==report['own_original_witness'];ownitems=unpack(json.loads(sixty.read_bytes()));assert snap['own_flat_input']in json.loads(sixty.read_bytes())['pins']
 peer_own={}
 for row in csv.DictReader(io.StringIO(ownitems['native-2020-additional-candidate-votes.csv'].decode())):
  key=(row['source_id'],int(row['source_page']),int(row['source_column']),row['candidate']);assert key not in peer_own;peer_own[key]=row
 count=collections.Counter();sids=set();rasterpairs=[];bpin=[]
 for a in snap['pins']:
  name=Path(a['original_path']).name;b=bodies[name];local=DATA/'coordinator-qa/turnout-2020-native-twelve'/(name+'.gz');assert gzip.decompress(local.read_bytes())==b;bpin.append(dict(worker_snapshot_pin=a,matching_coordinator_copy=pin(local)))
  if not name.endswith('.csv'):continue
  rows=list(csv.DictReader(io.StringIO(b.decode())))
  for r in rows:
   key=(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']);q=peer_own[key]
   assert r['votes']==q['votes']and r['role']==q['role']and r['source_raw_sha256']==q['source_raw_sha256']and r['native_source_key']==q['source_key']
   assert ' '.join(r.get('literal_native_label',r.get('label_literal')).split())==' '.join(q['literal_native_label'].split())
   count[r['role']]+=1;sids.add(r['source_id'])
 assert len(sids)==7 and sum(count.values())==297 and count==report['candidate_positions_by_role'];assert not report['value_role_differences']and not report['label_differences_after_whitespace_only']
 assert report['source_publications']==7 and report['native_constituents']==62 and report['compared_positions']==297
 for p in report['source_page_render_pairs']:
  a=pin(ROOT/p['own_raster']);b=pin(ROOT/p['peer_raster']);assert a['sha256']==p['own_raster_sha256']and b['sha256']==p['peer_raster_sha256'];assert p['same_raster_bytes']==(a['sha256']==b['sha256']);rasterpairs.append(dict(source_id=p['source_id'],actual_PDFpage=p['PDFpage'],baseline_raster=a,turnout_raster=b,same_bytes=p['same_raster_bytes']))
 out=dict(status='pass_immutable_reciprocal_first_seven_original2020_publications',worker_snapshot=pin(sp),worker_reconciliation=pin(rp),own_original60_witness=pin(sixty),matching_exact_frozen_peer_bodies=bpin,compared_positions=297,publication_views=7,native_constituents_across_publications=62,candidate_positions_by_role=dict(count),source_page_raster_pairs=rasterpairs,qualification='Every fourteen exact peer bodies matches the separately frozen coordinator replay input. All297 source hashes/pages/physical columns/keys/candidate values/roles and whitespace-folded headers agree the immutable60-publication original ledger. Rasters are checked as declared and preserved separately. This is no claim of identical numeric polygons, unavailable party/parsed-ID fields, current geography, same publication chronology, statewide independent historical completeness or native-method/887 acceptance.',formal_native887_dispatch_accepted=False,historical_native_complete=False,current_geography_approved=False)
 print(json.dumps(dict(continuity=cp,reciprocal=save('coordinator-historical-native-2020-peer-seven-review.json',out))))
if __name__=='__main__':main()
