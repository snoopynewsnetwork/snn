"""Check a bounded independent original replay against an immutable peer view."""
from pathlib import Path
import argparse,collections,csv,gzip,io,json,re
from review_allfield_milestone import DATA,ROOT,NAMES,load,sources,sha,pin

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--batch',required=True);ap.add_argument('--sha256',required=True)
 ap.add_argument('--baseline-version',required=True);ap.add_argument('--baseline-sha256',required=True);args=ap.parse_args()
 dest=DATA/'coordinator-qa'/f'presidential-{args.batch}-replay';dest.mkdir(exist_ok=True)
 decoded={};pins=[]
 for tail in ['original-readings.json','original-cells.csv']:
  name=f'{args.batch}-presidential-{tail}';p=dest/(name+'.gz')
  if not p.exists():
   b=(DATA/'turnout'/name).read_bytes();assert (DATA/'turnout'/name).read_bytes()==b
   p.write_bytes(gzip.compress(b,mtime=0))
  decoded[tail]=gzip.decompress(p.read_bytes());pins.append(pin(p))
 assert sha(decoded['original-readings.json'])==args.sha256
 own=json.loads(decoded['original-readings.json']);snapshot,items,sp=load(args.baseline_version,args.baseline_sha256);peer=sources(items)
 roles=collections.Counter();basis=collections.Counter();details=[];rasters={};diffrenders={};allrows={};natives=0;visual=0
 for s in own['sources']:
  sid=s['source_id'];p=peer[sid];assert s['source_raw_sha256']==p['raw_sha256']
  original=ROOT/s['source_original_path'];raw=gzip.decompress(original.read_bytes());assert sha(raw)==p['raw_sha256']and len(raw)==s['source_original_bytes']
  pages={p0['source_page']:p0 for p0 in s['pages']};c=collections.Counter();sums={n:0 for n in NAMES[:9]};totals={}
  for row in s['rows']:
   key=(sid,row['source_page'],row['source_column'],row['candidate']);assert key not in allrows;allrows[key]=row
   bp=next(p0 for p0 in p['pages']if p0['page']==row['source_page']);j=row['source_column']-1
   name=row['candidate'];assert name in NAMES[:9]
   f=next(f for f in bp['fields']if f['candidate']==name);role={'native_reporting_constituent':'source_native_reporting_constituent'}.get(row['role'],row['role'])
   assert role==bp['roles'][j]and row['direct_original_value']==f['values'][j]
   assert row['source_raw_sha256']==p['raw_sha256']and row['source_header_bounds']==bp['headers'][j]['header_bounds']
   assert re.sub(r'\s+','',row['label_literal'])==re.sub(r'\s+','',bp['headers'][j]['label_literal'])
   if row['original_aid_bounds_status']=='no_original_aid_crop_full_page_direct_read':
    assert row['original_aid_cell_bounds']is None and row['provisional_original_OCR_value']is None
    assert row['original_reading_basis']=='direct_visual_full_original_page_missing_aid_position'
   else:assert row['original_aid_bounds_status']=='provisional_OCR_target_not_accepted_numeric_polygon'
   page=pages[row['source_page']];rp=page.get('render_path',page.get('full_original_raster'));rh=page.get('render_sha256',page.get('raster_sha256'))
   if rp not in rasters:assert pin(ROOT/rp)['sha256']==rh;rasters[rp]=pin(ROOT/rp)
   if rh!=bp['render_sha256']:
    diffrenders[(sid,row['source_page'])]={'source_id':sid,'actual_PDF_page':row['source_page'],
      'turnout_render_path':rp,'turnout_sha256':rh,'turnout_size':page['render_size'],
      'peer_render_path':bp['full_original_render_path'],'peer_sha256':bp['render_sha256'],'peer_size':bp['render_size'],
      'turnout_applied_deskew_ccw':page.get('applied_deskew_ccw'),'peer_stated_deskew_ccw':bp.get('deskew_angle_ccw')}
   v=row['direct_original_value'];c[role]+=1;basis[row['original_reading_basis']]+=1
   if role=='source_native_reporting_constituent':assert type(v)is int;sums[name]+=v
   elif role=='source_TOTAL':assert name not in totals;totals[name]=v
   else:assert role=='unused_template_column'and v is None
  assert sums==totals
  for name,check in s['candidate_checks'].items():assert check['native_sum']==check['printed_TOTAL']==check.get('county_CSV',check.get('official_county_CSV'))==sums[name]
  assert c['source_native_reporting_constituent']==s['native_constituents']*9
  roles.update(c);natives+=s['native_constituents'];visual+=s['original_OCR_visual_correction_count']
  details.append({'source_id':sid,'source_raw_sha256':p['raw_sha256'],'native_constituents':s['native_constituents'],
    'source_position_role_counts':dict(c),'native_sums_and_printed_TOTALs':sums,
    'original_visual_corrections':s['original_OCR_visual_correction_count']})
 flat=list(csv.DictReader(io.StringIO(decoded['original-cells.csv'].decode())))
 assert len(flat)==len(allrows)==own['source_position_count']
 for row in flat:
  r=allrows[(row['source_id'],int(row['source_page']),int(row['source_column']),row['candidate'])]
  assert (None if row['direct_original_value']==''else int(row['direct_original_value']))==r['direct_original_value']
  for k in ['source_raw_sha256','source_native_key','role','label_literal','original_reading_basis','original_aid_bounds_status','original_full_page_raster']:assert row[k]==r[k]
 assert natives==own['native_constituent_count']and visual==own['visual_correction_count']
 assert visual==basis['direct_visual_full_original_page_after_OCR_error']+basis['direct_visual_full_original_page_missing_aid_position']
 result={'status':'pass_bounded_independent_original_presidential_batch_source_positions',
  'batch':args.batch,'frozen_input_pins':pins,'immutable_peer_snapshot_pin':sp,'source_views':len(own['sources']),
  'native_constituents':natives,'candidate_positions':len(flat),'position_role_counts':dict(roles),
  'reading_basis_position_counts':dict(basis),'direct_visual_OCR_error_corrections':basis['direct_visual_full_original_page_after_OCR_error'],
  'source_results':details,'whole_original_render_pins':list(rasters.values()),'separate_render_differences':list(diffrenders.values()),
  'qualification':'Every bounded original source value,role,page and whitespace-folded literal header agrees after independent extraction with the exact immutable peer source view. Original OCR and direct visual corrections remain separate reading bases; complete source PDFs and raster hashes are checked. Header bounds are source-grid references, not accepted numeric polygons. Independent render pipelines may have different raster pixels, height or deskew, all explicitly recorded; exact raster/crop equivalence is not asserted. No peer vote import, residual allocation, cross-year/name identity join or whole-state/historical-native/method/current-geography approval follows.',
  'whole_state_presidential_complete':False,'historical_native_complete':False,'formal_dispatch_accepted':False,'current2026_geography_approved':False}
 if basis['direct_visual_full_original_page_missing_aid_position']:
  result['direct_visual_missing_aid_position_readings']=basis['direct_visual_full_original_page_missing_aid_position']
  result['direct_visual_readings_total']=visual
  result['missing_aid_position_qualification']='These positions had no original numeric aid crop or OCR value; explicit nulls and full-page direct visual basis are retained. No aid polygon was fabricated.'
 target=DATA/f'coordinator-presidential-{args.batch}-replay-review.json';out=(json.dumps(result,indent=2)+'\n').encode()
 if target.exists():assert target.read_bytes()==out,'Frozen review changed'
 else:target.write_bytes(out)
 print(json.dumps({'status':result['status'],'sources':len(own['sources']),'native':natives,'positions':len(flat),'roles':dict(roles),'render_differences':len(diffrenders),'output_pin':pin(target)}))
if __name__=='__main__':main()
