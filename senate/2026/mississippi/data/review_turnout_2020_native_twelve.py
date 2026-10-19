"""Freeze and check the announced twelve-publication independent 2020 replay.

This is a source/pin/role/value comparison, not a fresh coordinator glyph read.
All candidate evidence and source-specific reading bases stay in exact inputs.
"""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json,re,struct

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
OUT=DATA/'coordinator-qa/turnout-2020-native-twelve'
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
FILES=[('2020-native-alcorn-original-readings.json','2020-native-alcorn-original-candidate-votes.csv')]+[(f'{s}-2020-native-original-readings.json',f'{s}-2020-native-original-cells.csv') for s in ['benton','benton-amended','greene','wilkinson','issaquena','noxubee','sharkey-original','sharkey-amended','calhoun','tishomingo','smith']]
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def norm(s):return ' '.join(s.split())
def load_snapshot(version):
 p=DATA/f'baselines/source/native-2020-{version}views-v1/snapshot.json';s=json.loads(p.read_bytes());items={}
 for a in s['pins']:
  z=(ROOT/a['stored_path']).read_bytes();assert len(z)==a['stored_bytes'] and sha(z)==a['stored_sha256'];b=gzip.decompress(z);assert len(b)==a['original_bytes'] and sha(b)==a['original_sha256'];items[Path(a['original_path']).name]=b
 return s,items,pin(p)
def freeze(p):
 q=OUT/(p.name+'.gz');OUT.mkdir(parents=True,exist_ok=True)
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def main():
 s40,i40,p40=load_snapshot(40);s50,i50,p50=load_snapshot(50)
 b,hpin=freeze(DATA/'turnout/source/2020-native-position-hints-v1.json');h=json.loads(b)
 assert sha(b)=='06f6964a02ec5fa6d54a642b23fa2fe30200e6c9be5b19d9af5ad3caeb0a8c02'
 assert h['peer_source_sha256']==sha(i40['native-2020-additional-readings.json'])
 original=json.loads(i40['native-2020-additional-readings.json']);expected=[]
 for s in original['sources']:
  expected.append(dict(source_id=s['source_id'],source_raw_sha256=s['raw_sha256'],pages=[dict(page=p['page'],render_size=p['render_size'],render_scale=p['render_scale'],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p['deskew_angle_ccw'],columns=[dict(source_column=c['source_column'],header_bounds=c['header_bounds'],role=c['role'])for c in p['columns']],candidate_rows=[dict(candidate=f['candidate'],row_bounds=f['row_bounds'])for f in p['fields']])for p in s['pages']]))
 assert expected==h['sources']
 hints={s['source_id']:s for s in h['sources']}
 peers={s['source_id']:s for s in json.loads(i50['native-2020-additional-readings.json'])['sources']}
 coverage=json.loads(i50['native-2020-coverage.json']);selected={s['source_id'] for s in coverage['all104_publication_status'] if s['selected_for_82_county_amended_where_explicit_control']}
 peerfields={}
 for sid,s in peers.items():
  for p in s['pages']:
   for f in p['fields']:
    for c,v in zip(p['columns'],f['values']):peerfields[sid,p['page'],c['source_column'],f['candidate']]=(c,v)
 total=collections.Counter();first7=collections.Counter();findings=[];inputs=[hpin];rasters={};rows_all=[];reading_bases=collections.Counter();prior_peer_hashes=set()
 for ix,(jname,cname) in enumerate(FILES):
  b,jpin=freeze(DATA/'turnout'/jname);c,cpin=freeze(DATA/'turnout'/cname);inputs.extend([jpin,cpin]);a=json.loads(b);sid=a['source_id'];assert sid in hints and sid in peers
  assert a['position_hint_sha256']==sha((DATA/'turnout/source/2020-native-position-hints-v1.json').read_bytes())
  rawpath=ROOT/a['source_original_path'];raw=gzip.decompress(rawpath.read_bytes());assert raw.startswith(b'%PDF-') and sha(raw)==a['source_raw_sha256']==peers[sid]['raw_sha256'];sourcepin=pin(rawpath)
  prior_peer_hashes.add(a['peer_file_sha256']);assert not a['peer_differences']
  page_map={p['source_page']:p for p in a['pages']}
  for p in a['pages']:
   rp=p.get('full_original_raster',p.get('original_raster'));rb=(ROOT/rp).read_bytes();assert sha(rb)==p['raster_sha256'];assert rb.startswith(b'\x89PNG\r\n\x1a\n');assert list(struct.unpack('>II',rb[16:24]))==p['render_size'];rasters[rp]=pin(ROOT/rp)
  rows=a['rows'];flat=list(csv.DictReader(io.StringIO(c.decode())));assert len(flat)==len(rows)
  assert len(rows)==sum(len(p['columns'])*3 for p in hints[sid]['pages'])
  counts=collections.Counter();sums={n:0 for n in NAMES};totals={};units={};aliases=[];seen=set()
  for r,f in zip(rows,flat):
   key=(sid,r['source_page'],r['source_column'],r['candidate']);assert key not in seen;seen.add(key);col,value=peerfields[key]
   label=r.get('literal_native_label',r.get('label_literal'));assert r['role']==col['role'] and r['votes']==value and norm(label)==norm(col['label_literal'])
   if label!=col['label_literal']:aliases.append(dict(source_page=r['source_page'],source_column=r['source_column'],candidate=r['candidate'],turnout_literal=label,baseline_literal=col['label_literal']))
   assert r['native_source_key']==f'{sid}:p{r["source_page"]}:c{r["source_column"]}'
   assert r['source_raw_sha256']==a['source_raw_sha256']
   for k in ['source_id','source_raw_sha256','native_source_key','role','candidate','reading_basis']:assert f[k]==r[k]
   assert int(f['source_page'])==r['source_page'] and int(f['source_column'])==r['source_column']
   assert (None if f['votes']=='' else int(f['votes']))==r['votes'];assert f.get('literal_native_label',f.get('label_literal'))==label
   rp=r.get('full_original_raster',r.get('original_full_page_raster'));assert rp==page_map[r['source_page']].get('full_original_raster',page_map[r['source_page']].get('original_raster'))
   hp=next(p for p in hints[sid]['pages'] if p['page']==r['source_page']);hc=next(c for c in hp['columns'] if c['source_column']==r['source_column']);assert hc['role']==r['role']
   if 'header_position_hint' in r:assert r['header_position_hint']==hc['header_bounds'] and json.loads(f['header_position_hint'])==r['header_position_hint']
   if 'candidate_row_band_hint' in r:assert r['candidate_row_band_hint']==next(f['row_bounds']for f in hp['candidate_rows']if f['candidate']==r['candidate']) and json.loads(f['candidate_row_band_hint'])==r['candidate_row_band_hint']
   if 'original_window' in r:assert json.loads(f['original_window'])==r['original_window']
   units[r['source_page'],r['source_column']]=r['role'];reading_bases[r['reading_basis']]+=1
   if r['role']=='unused_template_column':assert r['votes'] is None;counts['unused_null_positions']+=1
   else:
    assert type(r['votes'])is int and r['votes']>=0;counts['numeric_positions']+=1
    if r['role']=='source_native_reporting_constituent':sums[r['candidate']]+=r['votes']
    else:assert r['role']=='source_TOTAL' and r['candidate']not in totals;totals[r['candidate']]=r['votes']
  assert sums==totals=={n:a['candidate_checks'][n]['native_sum']for n in NAMES}
  for n,v in a['candidate_checks'].items():assert v['passes'] and v.get('printed_TOTAL',v.get('original_printed_TOTAL'))==sums[n]
  counts['native_constituents']=sum(v=='source_native_reporting_constituent'for v in units.values());assert counts['native_constituents']==a['native_constituents']
  counts['TOTAL_columns']=sum(v=='source_TOTAL'for v in units.values());assert counts['TOTAL_columns']==1
  counts['unused_columns']=sum(v=='unused_template_column'for v in units.values());counts['publication_views']=1;counts['source_positions']=len(rows)
  if sid in selected:counts['selected82_publications']=1;counts['selected82_native_constituents']=a['native_constituents']
  total.update(counts)
  if ix<7:first7.update(counts)
  rows_all.extend(rows)
  findings.append(dict(source_id=sid,original_PDF_stored_pin=sourcepin,raw_PDF_bytes=len(raw),raw_PDF_sha256=sha(raw),counts=dict(counts),source_candidate_sums_and_TOTAL=sums,whole_original_raster_paths=[p.get('full_original_raster',p.get('original_raster'))for p in a['pages']],whitespace_only_header_representation_differences=aliases,selected_for_82_county_publication_controls=sid in selected))
 assert total['publication_views']==12 and total['native_constituents']==124 and total['source_positions']==528 and total['numeric_positions']==408 and total['unused_null_positions']==120
 assert first7['publication_views']==7 and first7['native_constituents']==62 and first7['source_positions']==297 and first7['numeric_positions']==207 and first7['unused_null_positions']==90
 out=dict(status='pass_bounded_independent_original2020_native_twelve_publication_source_comparison',immutable_baseline40_snapshot=p40,immutable_baseline50_snapshot=p50,exact_frozen_turnout_inputs=inputs,counts=dict(total),prior_first7_scope=dict(first7),source_findings=findings,complete_turnout_raster_pins=list(rasters.values()),reading_bases=dict(reading_bases),recorded_earlier_worker_peer_CSV_hashes=sorted(prior_peer_hashes),qualification='Every announced original JSON and CSV is frozen losslessly before comparison. The vote-free hint is exactly a whitelist projection of immutable baseline40 source geometry, with no labels, candidate values, totals or native IDs. Native roles, values, literal headers after whitespace collapse, original PDF hashes and physical positions agree immutable baseline50. The earlier worker-recorded mutable peer CSV hashes are retained as historical declarations, not relabelled as the later frozen snapshot hash. Original/amended publications remain separate, selected82 is amended-where-linked only; distinct rasters and broad row bands are not identical numeric polygons, current geography or a cross-publication identity join. This is not a fresh coordinator visual reading of every new glyph or complete statewide historical/method acceptance.',historical_native_complete=False,formal_native887_dispatch_accepted=False,current_geography_approved=False)
 dest=DATA/'coordinator-turnout-native-2020-twelve-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if dest.exists():assert dest.read_bytes()==b,'Immutable review changed'
 else:dest.write_bytes(b)
 print(json.dumps(dict(status=out['status'],counts=dict(total),prior_first7_scope=dict(first7),output_pin=pin(dest))))
if __name__=='__main__':main()
