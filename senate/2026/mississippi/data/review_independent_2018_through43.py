"""Freeze and replay announced43-stage independent original native transcripts."""
from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,io,json,struct
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/turnout2018-43stage-replay-v1'
COUNTIES='benton calhoun clay coahoma franklin george greene issaquena kemper montgomery neshoba noxubee perry quitman sharkey smith sunflower tunica union winston yalobusha'.split()
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 q=QA/(p.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0));assert p.read_bytes()==b
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def main():
 QA.mkdir(parents=True,exist_ok=True);sp=DATA/'baselines/source/native-2018-164views-v1/snapshot.json';assert pin(sp)['sha256']=='90e14d7f6f34992c39b3d9370e954cc2d56ad7a58147103eaa0607bc139288d0';manifest=json.loads(sp.read_bytes());a=manifest['pins'][0];z=(ROOT/a['stored_path']).read_bytes();raw=gzip.decompress(z);assert sha(z)==a['stored_sha256']and sha(raw)==a['original_sha256'];peer={s['source_id']:s for s in json.loads(raw)['sources']};peer_fields={}
 for sid,s in peer.items():
  for p in s['pages']:
   for f in p['fields']:
    for c,v in zip(p['columns'],f['values']):peer_fields[sid,p['page'],c['source_column'],f['candidate']]=(c,v,f.get('source_marks',{}).get(str(c['source_column'])))
 inputs=[];findings=[];counts=Counter();seen_sources=set();aliases=[];rasters={};allfields=set();rolemap={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL','unused_template_column':'unused'}
 names=[f'2018-{name}-two-stage-native-original-readings.json'for name in COUNTIES]+['2018-leflore-Nov6-native-original-readings.json']
 for name in names:
  jb,jpin=freeze(DATA/'turnout'/name);cb,cpin=freeze(DATA/'turnout'/name.replace('-readings.json','-cells.csv'));inputs.extend([jpin,cpin]);j=json.loads(jb);ss=j.get('sources',[j]);flat=list(csv.DictReader(io.StringIO(cb.decode())));flat_keys={}
  for r in flat:
   key=(r['source_id'],int(r['source_pdf_page']),int(r['physical_source_column']),r['candidate']);assert key not in flat_keys;flat_keys[key]=r
  found=set()
  for s in ss:
   sid=s['source_id'];assert sid not in seen_sources;seen_sources.add(sid);assert sha(gzip.decompress((ROOT/s['source_original_path']).read_bytes()))==s['source_raw_sha256']==peer[sid]['raw_sha256'];sums=Counter();total={};units={};source_fields=0
   pp=s.get('pages')or[dict(original_raster=s['full_original_raster'],raster_sha256=s['full_original_raster_sha256'],render_size=s['render_size'])]
   for p in pp:
    path=ROOT/p['original_raster'];b=path.read_bytes();assert sha(b)==p['raster_sha256']and list(struct.unpack('>II',b[16:24]))==p['render_size'];rasters[str(path.relative_to(ROOT))]=pin(path)
   for r in s['rows']:
    key=(sid,r['source_pdf_page'],r['physical_source_column'],r['candidate']);assert key not in allfields;allfields.add(key);assert key not in found;found.add(key);f=flat_keys[key];c,v,mark=peer_fields[key];assert mark is None;assert r['votes']==v==(None if f['votes']==''else int(f['votes']));assert rolemap[r['role']]==c['role']and r['role']==f['role'];assert r['source_raw_sha256']==f['source_raw_sha256']==s['source_raw_sha256']and r['county_fips']==f['county_fips'];assert r['literal_source_header']==f['literal_source_header'];assert ' '.join(r['literal_source_header'].split())==' '.join(c['label_literal'].split())
    if r['literal_source_header']!=c['label_literal']:aliases.append(dict(source_key=list(key),own_literal=r['literal_source_header'],peer_literal=c['label_literal']))
    units[key[1:3]]=c['role'];source_fields+=1
    if c['role']=='unused':assert v is None;counts['unused_null_positions']+=1
    else:
     assert type(v)is int and v>=0;counts['numeric_positions']+=1
     if c['role']=='native':sums[r['candidate']]+=v
     else:assert c['role']=='TOTAL'and r['candidate']not in total;total[r['candidate']]=v
   assert sum(role=='native'for role in units.values())==s['native_constituents'];assert sum(role=='TOTAL'for role in units.values())==1
   assert total==peer[sid]['controls']['printed_TOTAL']and dict(sums)==peer[sid]['controls']['native_candidate_sums'];delta={n:sums[n]-v for n,v in total.items()}
   if any(delta.values()):assert sid=='sos-2018-county-leflore'and delta=={'Tobey Bernard Bartee':0,'Mike Espy':-10,'Cindy Hyde-Smith':0,'Chris McDaniel':0}
   counts.update(source_stage_grids=1,native_observations_across_distinct_stages=s['native_constituents'],TOTAL_columns=1,unused_columns=sum(role=='unused'for role in units.values()),candidate_positions=source_fields)
   findings.append(dict(source_id=sid,raw_original_sha256=s['source_raw_sha256'],source_native_observations=s['native_constituents'],source_candidate_positions=source_fields,native_candidate_sums=dict(sums),printed_TOTAL=total,known_native_minus_printed_TOTAL=delta,allocated=False))
  assert found==set(flat_keys)
 assert len(seen_sources)==43 and counts['candidate_positions']==len(allfields)==counts['numeric_positions']+counts['unused_null_positions']
 out=dict(status='pass_bounded43stage_independent_original2018_native_transcript_replay',immutable164_source_witness=pin(sp),complete_frozen_worker_derivative_bodies=inputs,counts=dict(counts),source_findings=findings,original_raster_pins=list(rasters.values()),whitespace_only_header_representations=aliases,unreviewed_independent_stage_native_grids=164-len(seen_sources),qualification='Exactly21announced two-stage county transcripts plus LefloreNov6 are frozen losslessly and recomputed against immutable164source fields. Every candidate value/null, role, rawPDFhash, actualPDFpage, physicalcolumn and whitespace-folded literal header agrees; no numerical/source-mark value is inferred. Leflore nativeEspy5853vsprinted5863 remainsunallocated−10. Exact current source header representations are not retrospectively substituted into prior coordinator/witness bodies; all old individual comparisons remain. This aggregates independent original transcripts after their source readings; it is not fresh coordinator glyph transcription of all fields or raster/crop/currentID equivalence. Another121independent stage grids, printed-method/ballot/registration and native887approval remain separate.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-independent-2018-through43-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(dict(output=pin(p),counts=dict(counts))))
if __name__=='__main__':main()
