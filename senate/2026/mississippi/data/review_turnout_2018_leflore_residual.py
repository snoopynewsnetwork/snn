"""Compare an independently read source without forcing its printed control closed."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json,struct

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/leflore-2018-independent-replay'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 QA.mkdir(parents=True,exist_ok=True);q=QA/(p.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def main():
 jb,jp=freeze(DATA/'turnout/2018-leflore-Nov6-native-original-readings.json');cb,cp=freeze(DATA/'turnout/2018-leflore-Nov6-native-original-cells.csv');own=json.loads(jb)
 sp=DATA/'baselines/source/native-2018-98views-v2/snapshot.json';assert pin(sp)['sha256']=='2ac5c3d1c708fbb0245a58b8ad89c01b533f589e9fdaeec5cba0effab58e9eaf';s=json.loads(sp.read_bytes());entry=next(p for p in s['pins']if p['original_path'].endswith('native-2018-original-candidate-votes.csv'));z=(ROOT/entry['stored_path']).read_bytes();b=gzip.decompress(z);assert len(z)==entry['stored_bytes']and sha(z)==entry['stored_sha256']and len(b)==entry['original_bytes']and sha(b)==entry['original_sha256']
 peer={(int(r['source_page']),int(r['source_column']),r['candidate']):r for r in csv.DictReader(io.StringIO(b.decode()))if r['source_id']==own['source_id']}
 flat={(int(r['source_pdf_page']),int(r['physical_source_column']),r['candidate']):r for r in csv.DictReader(io.StringIO(cb.decode()))};assert len(flat)==len(peer)==len(own['rows'])==88
 proof_path=DATA/'coordinator-leflore-2018-original-native-residual-review.json';proof=json.loads(proof_path.read_bytes());assert proof['source_id']==own['source_id']
 raw=gzip.decompress((ROOT/own['source_original_path']).read_bytes());assert sha(raw)==own['source_raw_sha256']==proof['raw_original_sha256']
 rasters=[]
 for p in own['pages']:
  path=ROOT/p['original_raster'];im=path.read_bytes();assert sha(im)==p['raster_sha256']and list(struct.unpack('>II',im[16:24]))==p['render_size'];rasters.append(pin(path))
 counts=collections.Counter();sums=collections.Counter();totals={};units={};aliases=[]
 for r in own['rows']:
  key=r['source_pdf_page'],r['physical_source_column'],r['candidate'];f,p=flat[key],peer[key]
  assert r['source_raw_sha256']==f['source_raw_sha256']==p['source_raw_sha256']==sha(raw)and r['county_fips']==f['county_fips']==p['county_fips']
  role={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL','unused_template_column':'unused'}[r['role']];assert f['role']==r['role']and p['role']==role
  assert r['votes']==(None if f['votes']==''else int(f['votes']))==(None if p['votes']==''else int(p['votes']))
  assert r['literal_source_header']==f['literal_source_header']and' '.join(r['literal_source_header'].split())==' '.join(p['literal_native_label'].split())
  if r['literal_source_header']!=p['literal_native_label']:aliases.append(dict(source_components=list(key),turnout_literal=r['literal_source_header'],baseline_literal=p['literal_native_label']))
  units[key[:2]]=role
  if role=='unused':assert r['votes']is None;counts['unused_null_positions']+=1
  else:
   assert type(r['votes'])is int;counts['numeric_positions']+=1
   if role=='native':
    sums[r['candidate']]+=r['votes'];assert r['votes']==proof['source_native_candidate_values_by_actual_page'][r['candidate']][str(key[0])][key[1]-1]
   else:assert key[:2]==(3,8);totals[r['candidate']]=r['votes'];assert r['votes']==proof['checks'][r['candidate']]['printed_TOTAL']
 assert sum(r=='native'for r in units.values())==18 and sum(r=='TOTAL'for r in units.values())==1 and sum(r=='unused'for r in units.values())==3
 residual={n:sums[n]-totals[n]for n in totals};assert residual=={'Tobey Bernard Bartee':0,'Mike Espy':-10,'Cindy Hyde-Smith':0,'Chris McDaniel':0}
 for n,c in own['candidate_checks'].items():assert c['native_sum']==sums[n]and c['printed_TOTAL']==totals[n]and c['native_minus_printed_TOTAL']==residual[n]
 out=dict(status='pass_bounded_independent_original_replay_with_explicit_unallocated_source_control_difference',source_id=own['source_id'],frozen_transcripts=[jp,cp],immutable_peer_snapshot=pin(sp),peer_flat_source=entry,independent_coordinator_original_reading=pin(proof_path),own_original_raster_pins=rasters,native_constituents=18,compared_candidate_positions=88,counts=dict(counts),native_candidate_sums=dict(sums),printed_TOTALs=totals,native_minus_printed_TOTAL=residual,all_vectors_close=False,whitespace_only_source_header_representations=aliases,qualification='All88 raw-source/page/physical-column/value/role/FIPS/whitespace-literal-header positions agree the independently read transcript and immutable98v2 source. Coordinator freshly read all four native vectors from its separately rendered complete originals after the discrepancy was known. Espy5853native versus5863printed remains unallocated10. Other three vectors close; closure is not a reason to edit source numbers. Different raster/reading windows and historical/current geographic identities are not asserted equal. This closes no whole historical-native-method or native887 dispatch gate.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-turnout-2018-leflore-source-residual-review.json';body=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==body
 else:p.write_bytes(body)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
