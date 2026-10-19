"""Cross-check independently read original source positions, not crop-based joins."""
from pathlib import Path
import collections,csv,gzip,io,json,re
from review_allfield_milestone import DATA,ROOT,NAMES,load,sources,sha,pin

DEST=DATA/'coordinator-qa/presidential-six-source-replay'
def freeze(name):
 target=DEST/(name+'.gz')
 if not target.exists():
  body=(DATA/'turnout'/name).read_bytes();assert (DATA/'turnout'/name).read_bytes()==body
  target.write_bytes(gzip.compress(body,mtime=0))
 return gzip.decompress(target.read_bytes()),pin(target)
def fold(s):return re.sub(r'\s+','',s)
def main():
 DEST.mkdir(exist_ok=True)
 inputs={};frozen=[]
 for name in ['hinds-presidential-original-readings.json','small-presidential-original-readings.json','hinds-presidential-original-cells.csv','small-presidential-original-cells.csv']:
  body,p=freeze(name);inputs[name]=body;frozen.append(p)
 h=json.loads(inputs['hinds-presidential-original-readings.json']);small=json.loads(inputs['small-presidential-original-readings.json'])
 ledger=[h]+small['sources'];assert len(ledger)==6
 snapshot,items,sp=load('25views','081fb0875fb6e53ce298765fccf739363764899affc299d47a4aca796ccedfb4');peer=sources(items)
 aliases={'native_reporting_constituent':'source_native_reporting_constituent'}
 roles=collections.Counter();basis=collections.Counter();details=[];renderpins={};render_differences={};native=0;corrected=0;allrows={}
 for s in ledger:
  sid=s['source_id'];p=peer[sid];assert s['source_raw_sha256']==p['raw_sha256']
  original=ROOT/s['source_original_path'];raw=gzip.decompress(original.read_bytes());assert sha(raw)==p['raw_sha256']and len(raw)==s['source_original_bytes']
  pages={pg.get('source_page'):pg for pg in s['pages']};counts=collections.Counter();sums={n:0 for n in NAMES[:9]};totals={};seen=set()
  for r in s['rows']:
   key=(r['source_page'],r['source_column'],r['candidate']);assert key not in seen;seen.add(key)
   pp=next(pg for pg in p['pages']if pg['page']==r['source_page']);j=r['source_column']-1
   field=next(f for f in pp['fields']if f['candidate']==r['candidate']);assert r['candidate']in NAMES[:9]
   role=aliases.get(r['role'],r['role']);assert role==pp['roles'][j]
   assert r['direct_original_value']==field['values'][j]
   assert fold(r['label_literal'])==fold(pp['headers'][j]['label_literal'])
   assert r['source_header_bounds']==pp['headers'][j]['header_bounds']
   assert r['source_raw_sha256']==p['raw_sha256']
   assert r['original_aid_bounds_status']=='provisional_OCR_target_not_accepted_numeric_polygon'
   pg=pages[r['source_page']];renderpath=pg.get('render_path',pg.get('full_original_raster'));renderhash=pg.get('render_sha256',pg.get('raster_sha256'))
   if renderpath not in renderpins:assert pin(ROOT/renderpath)['sha256']==renderhash;renderpins[renderpath]=pin(ROOT/renderpath)
   if pp['render_sha256']!=renderhash:
    render_differences[(sid,r['source_page'])]={'source_id':sid,'actual_PDF_page':r['source_page'],
     'turnout_render_path':renderpath,'turnout_render_sha256':renderhash,'turnout_render_size':pg['render_size'],
     'baseline_render_path':pp['full_original_render_path'],'baseline_render_sha256':pp['render_sha256'],
     'baseline_render_size':pp['render_size'],'turnout_applied_deskew_ccw':pg.get('applied_deskew_ccw'),
     'baseline_stated_deskew_ccw':pp.get('deskew_angle_ccw'),
     'qualification':'Same exact PDF publication/page, separate original renders. Shared header-grid references do not establish identical raster pixels or accepted numeric crop polygons.'}
   value=r['direct_original_value'];counts[role]+=1;basis[r['original_reading_basis']]+=1
   if role=='source_native_reporting_constituent':assert type(value)is int;sums[r['candidate']]+=value
   elif role=='source_TOTAL':assert r['candidate']not in totals;totals[r['candidate']]=value
   else:assert role=='unused_template_column'and value is None
   allrows[(sid,*key)]=r
  assert sums==totals
  for name,v in s['candidate_checks'].items():
   assert v['native_sum']==v['printed_TOTAL']==v.get('official_county_CSV',v.get('county_CSV'))==sums[name]
  assert counts['source_native_reporting_constituent']==s['native_constituents']*9
  native+=s['native_constituents'];corrected+=s['original_OCR_visual_correction_count'];roles.update(counts)
  details.append({'source_id':sid,'raw_sha256':p['raw_sha256'],'native_constituents':s['native_constituents'],
    'role_position_counts':dict(counts),'original_visual_corrections':s['original_OCR_visual_correction_count'],
    'original_nine_candidate_native_sums_and_TOTALs':sums})
 flat=0
 for name in ['hinds-presidential-original-cells.csv','small-presidential-original-cells.csv']:
  for r in csv.DictReader(io.StringIO(inputs[name].decode())):
   old=allrows[(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate'])]
   assert (None if r['direct_original_value']==''else int(r['direct_original_value']))==old['direct_original_value']
   for k in ['source_raw_sha256','source_native_key','role','label_literal','original_reading_basis','original_aid_bounds_status','original_full_page_raster']:assert r[k]==old[k]
   flat+=1
 assert flat==len(allrows)==1584 and native==148 and corrected==28
 assert dict(roles)=={'source_native_reporting_constituent':1332,'source_TOTAL':54,'unused_template_column':198}
 output={'status':'pass_bounded_1584_source_candidate_positions_six_independent_original_replays',
  'turnout_frozen_input_pins':frozen,'baseline_immutable_snapshot_pin':sp,'source_views':6,'native_constituents':148,
  'candidate_positions':flat,'role_position_counts':dict(roles),'source_reading_basis_counts':dict(basis),
  'worker_original_visual_corrections':28,'source_results':details,'complete_original_render_pins':list(renderpins.values()),
  'separate_original_render_differences':list(render_differences.values()),
  'qualification':'All1584 source positions agree in values,source hash,page,referenced physical header grid,roles and whitespace-folded literal labels with the independent immutable baseline25-view source readings.1332 native and54 TOTAL positions are numeric;198 unused positions remain null. Five original renders differ between independent pipelines, including one pixel of height in Greene and stated deskew differences. Exact raster or accepted numeric-box agreement is not claimed. Prior own original OCR inputs and28 direct-original visual corrections are retained, not imported from peer values. Numeric OCR crop windows stay explicitly provisional, never accepted numeric polygons. These six source partitions do not imply whole-state presidential or historical-native/method/current reporting/geographic completion. No approved ID join, residual allocation, dispatch acceptance or fresh coordinator visual reading of every cell is claimed.',
  'whole_state_presidential_complete':False,'historical_native_complete':False,'formal_dispatch_accepted':False,'current2026_geography_approved':False}
 target=DATA/'coordinator-presidential-six-source-replay-review.json';target.write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'status':output['status'],'candidate_positions':flat,'native':native,'roles':dict(roles),'output_pin':pin(target)}))
if __name__=='__main__':main()
