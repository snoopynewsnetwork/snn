"""Audit complete original manual-grid replays without inventing numeric OCR targets."""
from pathlib import Path
import argparse,collections,csv,gzip,io,json,re
from review_allfield_milestone import DATA,ROOT,NAMES,load,sources,sha,pin

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--batch',required=True);ap.add_argument('--sha256',required=True);args=ap.parse_args()
 dest=DATA/'coordinator-qa'/f'presidential-{args.batch}-replay';dest.mkdir(exist_ok=True);decoded={};pins=[]
 for tail in ['original-readings.json','original-cells.csv']:
  name=f'{args.batch}-presidential-{tail}';p=dest/(name+'.gz')
  if not p.exists():p.write_bytes(gzip.compress((DATA/'turnout'/name).read_bytes(),mtime=0))
  decoded[tail]=gzip.decompress(p.read_bytes());pins.append(pin(p))
 assert sha(decoded['original-readings.json'])==args.sha256
 own=json.loads(decoded['original-readings.json']);_,items,sp=load('82views','94576fcfa4b7b245e2d5baa9e8366e4489594804f41694ea04a9f6315e46b336');peer=sources(items)
 rows={};rasters={};diffs={};roles=collections.Counter();findings=[];totnative=0;totmissing=0;toterrors=0;headerlimited=[]
 for s in own['sources']:
  sid=s['source_id'];p=peer[sid];raw=gzip.decompress((ROOT/s['source_original_path']).read_bytes());assert sha(raw)==s['source_raw_sha256']==p['raw_sha256']and len(raw)==s['source_original_bytes']
  pages={x['source_page']:x for x in s['pages']};c=collections.Counter();sums={n:0 for n in NAMES[:9]};totals={};missing=0;errors=0
  for r in s['rows']:
   key=(sid,r['source_page'],r['source_column'],r['candidate']);assert key not in rows;rows[key]=r
   pp=next(x for x in p['pages']if x['page']==r['source_page']);col=r['source_column']-1;assert 0<=col<len(pp['roles']);f=next(x for x in pp['fields']if x['candidate']==r['candidate']);v=r['direct_original_value'];role={'native_reporting_constituent':'source_native_reporting_constituent'}.get(r['role'],r['role'])
   assert role==pp['roles'][col]and v==f['values'][col]
   if 'headers'in pp:
    label=pp['headers'][col]['label_literal'];assert r['source_header_bounds']==pp['headers'][col]['header_bounds']
   else:
    assert sid=='sos-2024-county-kemper'and 'labels_literal'in pp
    label=pp['labels_literal'][col]if col<len(pp['labels_literal'])else''
    if col>=len(pp['labels_literal']):assert role=='unused_template_column'
    assert len(r['source_header_bounds'])==4;headerlimited.append(key)
   assert re.sub(r'\s+','',r['label_literal'])==re.sub(r'\s+','',label)
   assert r['source_raw_sha256']==p['raw_sha256']
   if role=='unused_template_column':assert v is None and r['original_reading_basis']=='direct_visual_unprinted_unused_template_position'
   else:assert type(v)is int and v>=0 and r['original_reading_basis']=='direct_visual_complete_original_page_grid'
   if r['original_aid_bounds_status']=='no_original_aid_crop_full_page_direct_read':
    assert r['original_aid_cell_bounds']is None and r['provisional_original_OCR_value']is None;missing+=1
   else:
    assert r['original_aid_bounds_status']=='provisional_OCR_target_not_accepted_numeric_polygon'and len(r['original_aid_cell_bounds'])==4
    errors+=r['provisional_original_OCR_value']!=v
   page=pages[r['source_page']];rp=page['full_original_raster'];rh=page['raster_sha256'];assert rp==r['original_full_page_raster']
   if rp not in rasters:assert pin(ROOT/rp)['sha256']==rh;rasters[rp]=pin(ROOT/rp)
   if rh!=pp['render_sha256']:diffs[(sid,r['source_page'])]={'source_id':sid,'actual_PDFpage':r['source_page'],'turnout_render_path':rp,'turnout_sha256':rh,'turnout_size':page['render_size'],'peer_render_path':pp['full_original_render_path'],'peer_sha256':pp['render_sha256'],'peer_size':pp['render_size'],'turnout_applied_deskew_ccw':page.get('applied_deskew_ccw'),'peer_stated_deskew_ccw':pp.get('deskew_angle_ccw')}
   c[role]+=1
   if role=='source_native_reporting_constituent':sums[r['candidate']]+=v
   elif role=='source_TOTAL':assert r['candidate']not in totals;totals[r['candidate']]=v
  assert sums==totals and len(s['rows'])==s['source_position_rows']and c['source_native_reporting_constituent']==9*s['native_constituents']
  for n,x in s['candidate_checks'].items():assert sums[n]==x['native_sum']==x['printed_TOTAL']==x['county_CSV']and x['passes']
  assert missing==s['original_aid_missing_position_count']and errors==s['original_OCR_visual_correction_count']and not s['independent_peer_position_differences']
  findings.append({'source_id':sid,'raw_sha256':p['raw_sha256'],'native_constituents':s['native_constituents'],'position_roles':dict(c),'native_sums_and_printed_TOTALs':sums,'missing_original_aid_positions_including_unused':missing,'provisional_OCR_disagreements_visually_superseded':errors})
  roles.update(c);totnative+=s['native_constituents'];totmissing+=missing;toterrors+=errors
 flat=list(csv.DictReader(io.StringIO(decoded['original-cells.csv'].decode())))
 assert len(flat)==len(rows)==own['source_position_count']and totnative==own['native_constituent_count']and len(own['sources'])==own['source_view_count']and totmissing==own['original_aid_missing_position_count']
 for f in flat:
  r=rows[(f['source_id'],int(f['source_page']),int(f['source_column']),f['candidate'])];assert(None if f['direct_original_value']==''else int(f['direct_original_value']))==r['direct_original_value']
  for k in ['source_raw_sha256','source_native_key','role','label_literal','original_reading_basis','original_aid_bounds_status','original_full_page_raster']:assert f[k]==r[k]
 out={'status':'pass_bounded_independent_complete_original_manual_grid_replay','batch':args.batch,'frozen_input_pins':pins,'immutable_peer_snapshot_pin':sp,'source_views':len(own['sources']),'native_constituents':totnative,'candidate_positions':len(rows),'position_role_counts':dict(roles),'complete_original_manual_grid_numeric_positions':len(rows)-roles['unused_template_column'],'direct_observation_unused_null_positions':roles['unused_template_column'],'missing_original_aid_positions_including_unused':totmissing,'provisional_OCR_disagreements_visually_superseded':toterrors,'source_results':findings,'whole_original_render_pins':list(rasters.values()),'separate_render_differences':list(diffs.values()),'qualification':'All nine candidate rows and source columns use direct whole-original grid readings. Missing OCR aid and observed unused blanks remain distinct from literal numeric zeros; no missing numeric polygon is invented. Raw PDF and raster pins, exact source roles, candidate vectors, flat positions and whitespace-only literal labels agree the immutable independent peer only after original extraction. This bounded source/basis audit is not a fresh coordinator visual reading of every glyph, a cross-publication/geographic join, whole historical-method completion or dispatch approval.','formal_dispatch_accepted':False,'historical_native_complete':False,'current2026_geography_approved':False}
 if headerlimited:
  out['peer_schema_missing_exact_header_box_comparison_positions']=len(headerlimited)
  out['header_box_qualification']='The frozen Kemper peer pages retain exact literal labels/roles/physical ordinals but no headers/bounds array. All297positions agree on source/hash/page/ordinal/label/role/value; own header boxes are retained without claiming shared exact polygons or box agreement.'
 if roles['parallel_native_observation']:
  out['parallel_observation_positions_excluded_from_native_sums']=roles['parallel_native_observation']
  out['parallel_observation_qualification']='KemperPDF6eleven unofficial observations remain nonadditive; disjoint officialPDF7-8fourteen native constituents and one TOTAL alone form source controls.'
 target=DATA/f'coordinator-presidential-{args.batch}-replay-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if target.exists():assert target.read_bytes()==b,'Immutable bounded review changed'
 else:target.write_bytes(b)
 print(json.dumps({'status':out['status'],'native':totnative,'positions':len(rows),'missing_aid':totmissing,'OCR_disagreements':toterrors,'render_differences':len(diffs),'output_pin':pin(target)}))
if __name__=='__main__':main()
