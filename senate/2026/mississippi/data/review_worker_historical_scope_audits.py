"""Retain new full-peer audits without relabelling their direct-original coverage."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/historical-full-peer-scope-v1'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 q=QA/(p.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0));assert p.read_bytes()==b
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def unpack(path):
 j=json.loads(path.read_bytes());out={}
 for a in j['pins']:
  z=(ROOT/a['stored_path']).read_bytes();b=gzip.decompress(z);assert len(z)==a['stored_bytes']and sha(z)==a['stored_sha256']and len(b)==a['original_bytes']and sha(b)==a['original_sha256'];out[Path(a['original_path']).name]=b
 return out
def main():
 QA.mkdir(parents=True,exist_ok=True);audits={};pins=[];sources_by_year={}
 for year,version,h in [(2020,104,'1ff6e98fd18f70ec473ce0b5adac5e082f4f1900a7d03d6090e9181150a71568'),(2018,164,'90e14d7f6f34992c39b3d9370e954cc2d56ad7a58147103eaa0607bc139288d0')]:
  b,p=freeze(DATA/f'turnout/{year}-full-peer-native-scope-audit.json');a=json.loads(b);assert a['accepted_new_own_original_native_cells_from_this_audit']==0;sp=ROOT/a['peer_snapshot_path'];assert sha(sp.read_bytes())==h==a['peer_snapshot_sha256'];docs=unpack(sp);audits[year]=a;pins.append(p)
  if year==2020:
   ss={s['source_id']:s for name in ['coahoma-2020-amendment-readings.json','native-2020-additional-readings.json']for s in json.loads(docs[name])['sources']}
   own,pp=freeze(ROOT/a['own_original_publication_control_path']);assert sha(own)==a['own_original_publication_control_sha256'];controls={r['source_id']:r for r in json.loads(own)['sources']};pins.append(pp);assert set(ss)==set(controls)and len(ss)==104
   fields=0
   for sid,s in ss.items():
    c=controls[sid];assert s['raw_sha256']==c['source_raw_sha256'];total={}
    for page in s['pages']:
     for i,col in enumerate(page['columns']):
      if col['role']=='source_TOTAL':total={f['candidate']:f['values'][i]for f in page['fields']};assert page['page']==c['source_page']
    assert total==c['candidate_values'];fields+=len(total)
   assert fields==312==a['candidate_source_controls'];assert a['publication_views']==104 and a['native_observations_across_distinct_publications']==2131 and a['combined104_candidate_or_null_positions']==8316
   assert a['selected82_native_candidate_state_controls']=={'Mike Espy':578691,'Cindy Hyde-Smith':709511,'Jimmy L. Edwards':23152}
  else:
   ss={s['source_id']:s for s in json.loads(docs['native-2018-original-readings.json'])['sources']};own,pp=freeze(ROOT/a['own_independent_county_controls_path']);assert sha(own)==a['own_independent_county_controls_sha256'];pins.append(pp);controls=collections.defaultdict(dict);controlhash={};controlpage={}
   for r in csv.DictReader(io.StringIO(own.decode())):assert r['candidate']not in controls[r['source_id']];controls[r['source_id']][r['candidate']]=int(r['votes']);controlhash[r['source_id']]=r['raw_sha256'];controlpage[r['source_id']]=int(r['source_page'])
   assert set(ss)==set(controls)and len(ss)==164
   for sid,s in ss.items():
    assert s['raw_sha256']==controlhash[sid]and s['controls']['printed_TOTAL']==controls[sid]
    page=next(page for page in s['pages']if any(c['role']=='TOTAL'for c in page['columns']));assert page['page']==controlpage[sid]
   assert sum(len(v)for v in controls.values())==492==a['candidate_source_controls'];assert a['native_observations_across_distinct_stages']==3545 and a['candidate_or_null_positions']==13662 and a['full_original_render_count_hash_checked']==414
  sources_by_year[year]=len(ss)
 out=dict(status='pass_bounded_new_historical_full_peer_scope_audits_and_independent_county_TOTAL_controls',complete_frozen_audits_and_control_inputs=pins,source_publications=sources_by_year,independently_original_read_county_TOTAL_candidate_comparisons=804,accepted_new_direct_original_native_cells=0,prior_direct_original_source_scope=dict(year2020_publications=44,year2020_native_observations_across_versions=621,year2018_stage_views=43,year2018_native_observations_across_stages=598),qualification='The newly supplied read-only full-peer scope audits retain exact immutable original-derived source references and all312/492countyTOTALs agree the separate independent original-control ledgers. This checks the audit/control link, not another coordinator glyph reading or a new independent transcription of all2131/3545native observations. Existing coordinator fullsource/raster/field/role reviews remain separate. Direct-original scopes stay44of104publications and43of164stages; no0-new-cell audit is relabelled complete independent native extraction. Leflore−10unallocated, literalXnumericalnull, alternatepublications/admin/currentgeometry/method qualifications survive. No native887approval follows.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-worker-historical-full-peer-scope-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
