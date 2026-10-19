"""Freeze and replay 41 independently original-read county-stage peer scopes.
New immutable evidence; earlier10/12 and their metadata remain unchanged.
"""
import argparse,csv,gzip,io,json
from collections import Counter
from sources import OUT,BASE,sha,save,original
COUNTIES=['benton','issaquena','franklin','smith','montgomery','yalobusha','greene','perry','coahoma','kemper','winston','tunica','neshoba','george','sunflower','clay','calhoun','noxubee','union','sharkey']
def read(pin):
 z=(BASE/pin['stored_path']).read_bytes();r=gzip.decompress(z);assert len(z)==pin['stored_bytes']<40000000 and sha(z)==pin['stored_sha256'] and len(r)==pin['original_bytes'] and sha(r)==pin['original_sha256'];return r
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--capture',action='store_true');a=ap.parse_args();folder=OUT/'source/native-2018-peer-41views-v3';sp=folder/'snapshot.json';ownsp=OUT/'source/native-2018-164views-v1/snapshot.json';os=json.loads(ownsp.read_text());flat=next(p for p in os['pins'] if p['original_path'].endswith('.csv'))
 if a.capture and not sp.exists():
  folder.mkdir(exist_ok=True);pins=[]
  for stem in ['2018-'+c+'-two-stage-native-original-' for c in COUNTIES]+['2018-leflore-Nov6-native-original-']:
   for suffix in ['readings.json','cells.csv']:
    p=BASE/'data/turnout'/(stem+suffix);r=p.read_bytes();z=gzip.compress(r,mtime=0);t=folder/(p.name+'.gz');t.write_bytes(z);pins.append(dict(original_path=str(p.relative_to(BASE)),original_bytes=len(r),original_sha256=sha(r),stored_path=str(t.relative_to(BASE)),stored_bytes=len(z),stored_sha256=sha(z)))
  save(sp,dict(own_witness=dict(path=str(ownsp.relative_to(BASE)),bytes=ownsp.stat().st_size,sha256=sha(ownsp.read_bytes())),own_flat=flat,pins=pins,qualification='Forty-one explicitly listed peer original-read stages after own164 originals complete. Separate new metadata/body version; prior first10/12 exact witnesses unchanged. No peer source values copied into own readings.'))
 snap=json.loads(sp.read_text());assert snap['own_flat']==flat and snap['own_witness']['sha256']==sha(ownsp.read_bytes()) and len(snap['pins'])==42
 rows=list(csv.DictReader(io.StringIO(read(flat).decode())));own={(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']):r for r in rows};assert len(own)==len(rows)==13662
 roles={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL','unused_template_column':'unused','administrative_column':'administrative'};seen=set();units=set();counts=Counter();sources={};pages={};diff=[]
 for pin in snap['pins']:
  r=read(pin)
  if not pin['original_path'].endswith('.csv'):continue
  for p in csv.DictReader(io.StringIO(r.decode())):
   k=(p['source_id'],int(p['source_pdf_page']),int(p['physical_source_column']),p['candidate']);assert k not in seen;seen.add(k);o=own[k];rr=roles[p['role']];counts[rr]+=1
   assert p['source_raw_sha256']==o['source_raw_sha256'] and p['county_fips']==o['county_fips'] and p['party_field_literal']==o['party_literal']==''
   if p['votes']!=o['votes'] or rr!=o['role'] or ' '.join(p['literal_source_header'].split())!=' '.join(o['literal_native_label'].split()):diff.append(dict(key=k,own=o,peer=p))
   if rr=='native':units.add(k[:3])
   sources[k[0]]=p['source_raw_sha256'];q=pages.setdefault(k[:2],dict(source_id=k[0],PDFpage=k[1],own_raster=o['full_original_render_path'],peer_raster=p['original_raster']));assert q['own_raster']==o['full_original_render_path'] and q['peer_raster']==p['original_raster']
 assert len(sources)==41 and not diff,(len(sources),diff[:8])
 for sid,h in sources.items():assert sha(original(sid))==h
 for q in pages.values():q.update(own_raster_sha256=sha((BASE/q['own_raster']).read_bytes()),peer_raster_sha256=sha((BASE/q['peer_raster']).read_bytes()))
 out=OUT/'native-2018-peer-41views-v3-reconciliation.json';save(out,dict(status='pass_bounded_post_original_41_stage_replay',peer_snapshot=dict(path=str(sp.relative_to(BASE)),bytes=sp.stat().st_size,sha256=sha(sp.read_bytes())),own_original_witness=snap['own_witness'],source_stage_views=len(sources),source_native_observations=len(units),source_candidate_positions=len(seen),candidate_positions_by_role=dict(counts),numeric_positions=sum(own[k]['votes']!='' for k in seen),source_hashes=sources,source_page_render_pairs=list(pages.values()),differences=diff,qualification='All41 peer original-read stages match own frozen164 at rawsource/FIPS/physicalpage/column/candidate/value/role and whitespace-folded literal label. Source-specific literal case/wrap corrections remain histories in both packages. LefloreEspy native5853 versus printed5863 remains unallocated. Both raster hashes retained separately; no exact raster/reading-window/currentID/cross-stage join or whole164 independent peer replay claimed.'))
 fp=folder/'reconciliation.json'
 if fp.exists():assert fp.read_bytes()==out.read_bytes()
 else:fp.write_bytes(out.read_bytes())
 print('PASS2018peer41',len(units),len(seen),dict(counts))
if __name__=='__main__':main()
