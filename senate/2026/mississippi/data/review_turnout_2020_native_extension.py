"""Check an announced disjoint extension of the independent original2020 replay."""
from pathlib import Path
import argparse,collections,csv,gzip,hashlib,io,json,struct
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
OUT=DATA/'coordinator-qa/turnout-2020-native-extensions'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 q=OUT/(p.name+'.gz');OUT.mkdir(parents=True,exist_ok=True)
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0));assert p.read_bytes()==b
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def unpack(s):
 out={}
 for a in s['pins']:
  z=(ROOT/a['stored_path']).read_bytes();assert sha(z)==a['stored_sha256']and len(z)==a['stored_bytes'];b=gzip.decompress(z);assert sha(b)==a['original_sha256']and len(b)==a['original_bytes'];out[Path(a['original_path']).name]=b
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prior-proof',required=True);ap.add_argument('--tags',nargs='+',required=True);ap.add_argument('--snapshot-version',type=int,required=True);ap.add_argument('--comparison-snapshot-version',type=int);ap.add_argument('--hint-version',type=int,required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
 priorpath=ROOT/args.prior_proof;prior=json.loads(priorpath.read_bytes());assert not prior.get('formal_native887_dispatch_accepted',True)
 seen={r['source_id']for r in prior['source_findings']};snapshot=DATA/f'baselines/source/native-2020-{args.snapshot_version}views-v1/snapshot.json';s=json.loads(snapshot.read_bytes());items=unpack(s)
 hint_sources={r['source_id']:r for r in json.loads(items['native-2020-additional-readings.json'])['sources']};comparison=snapshot
 if args.comparison_snapshot_version is not None:comparison=DATA/f'baselines/source/native-2020-{args.comparison_snapshot_version}views-v1/snapshot.json'
 compared=items if comparison==snapshot else unpack(json.loads(comparison.read_bytes()));sources={r['source_id']:r for r in json.loads(compared['native-2020-additional-readings.json'])['sources']};coverage=json.loads(compared['native-2020-coverage.json']);selected={r['source_id']for r in coverage['all104_publication_status']if r['selected_for_82_county_amended_where_explicit_control']}
 hraw,hpin=freeze(DATA/f'turnout/source/2020-native-position-hints-v{args.hint_version}.json');h=json.loads(hraw);assert h['peer_source_sha256']==sha(items['native-2020-additional-readings.json'])
 expected=[]
 for a in hint_sources.values():expected.append(dict(source_id=a['source_id'],source_raw_sha256=a['raw_sha256'],pages=[dict(page=p['page'],render_size=p['render_size'],render_scale=p['render_scale'],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p['deskew_angle_ccw'],columns=[dict(source_column=c['source_column'],header_bounds=c['header_bounds'],role=c['role'])for c in p['columns']],candidate_rows=[dict(candidate=f['candidate'],row_bounds=f['row_bounds'])for f in p['fields']])for p in a['pages']]))
 assert h['sources']==expected;hints={r['source_id']:r for r in h['sources']};fields={}
 for sid,a in sources.items():
  for p in a['pages']:
   for f in p['fields']:
    for c,v in zip(p['columns'],f['values']):fields[sid,p['page'],c['source_column'],f['candidate']]=(c,v)
 counts=collections.Counter();findings=[];inputpins=[hpin];rasterpins={}
 for tag in args.tags:
  b,jp=freeze(DATA/f'turnout/{tag}-2020-native-original-readings.json');c,cp=freeze(DATA/f'turnout/{tag}-2020-native-original-cells.csv');a=json.loads(b);sid=a['source_id'];assert sid not in seen;seen.add(sid);assert a['position_hint_sha256']==sha(hraw);inputpins.extend([jp,cp])
  if a['peer_differences']:
   assert sid=='sos-2020-county-kemper'and args.comparison_snapshot_version==70 and len(a['peer_differences'])==3
   for d,n,v in zip(a['peer_differences'],['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards'],[133,180,2]):assert d==dict(page=2,column=9,candidate=n,own_value=v,peer_value=str(v),own_label='Lynville',peer_label='Lynnville',own_role='source_native_reporting_constituent',peer_role='source_native_reporting_constituent')
   assert pin(DATA/'coordinator-kemper-2020-original-header-review.json')['sha256']=='c28cae19bb9c414c315b369cef9fdf15b79e6c5fa8d4196923666813649accf2'
  rawpath=ROOT/a['source_original_path'];raw=gzip.decompress(rawpath.read_bytes());assert raw.startswith(b'%PDF-')and sha(raw)==a['source_raw_sha256']==sources[sid]['raw_sha256']
  for p in a['pages']:
   rp=ROOT/p['full_original_raster'];rb=rp.read_bytes();assert sha(rb)==p['raster_sha256']and rb.startswith(b'\x89PNG\r\n\x1a\n');assert list(struct.unpack('>II',rb[16:24]))==p['render_size'];rasterpins[str(rp.relative_to(ROOT))]=pin(rp)
  flat=list(csv.DictReader(io.StringIO(c.decode())));assert len(flat)==len(a['rows'])==a['source_positions'];units={};seenkeys=set();sums=collections.Counter();totals={};aliases=[]
  for r,f in zip(a['rows'],flat):
   key=sid,r['source_page'],r['source_column'],r['candidate'];assert key not in seenkeys;seenkeys.add(key);col,v=fields[key];assert v==r['votes']and col['role']==r['role']and ' '.join(col['label_literal'].split())==' '.join(r['literal_native_label'].split())
   if col['label_literal']!=r['literal_native_label']:aliases.append(dict(source_page=r['source_page'],source_column=r['source_column'],candidate=r['candidate'],turnout_literal=r['literal_native_label'],baseline_literal=col['label_literal']))
   assert r['source_raw_sha256']==a['source_raw_sha256']and r['native_source_key']==f'{sid}:p{r["source_page"]}:c{r["source_column"]}'
   for k in ['source_id','source_raw_sha256','native_source_key','literal_native_label','role','candidate','reading_basis','full_original_raster']:assert f[k]==r[k]
   assert int(f['source_page'])==r['source_page']and int(f['source_column'])==r['source_column']and(None if f['votes']==''else int(f['votes']))==r['votes']
   hp=next(p for p in hints[sid]['pages']if p['page']==r['source_page']);hc=next(c for c in hp['columns']if c['source_column']==r['source_column']);assert r['header_position_hint']==hc['header_bounds']and r['role']==hc['role'];assert r['candidate_row_band_hint']==next(f['row_bounds']for f in hp['candidate_rows']if f['candidate']==r['candidate'])
   assert json.loads(f['header_position_hint'])==r['header_position_hint']and json.loads(f['candidate_row_band_hint'])==r['candidate_row_band_hint']
   units[r['source_page'],r['source_column']]=r['role']
   if r['role']=='unused_template_column':assert r['votes']is None;counts['unused_null_positions']+=1
   else:
    assert type(r['votes'])is int and r['votes']>=0;counts['numeric_positions']+=1
    if r['role']=='source_native_reporting_constituent':sums[r['candidate']]+=r['votes']
    else:assert r['role']=='source_TOTAL'and r['candidate']not in totals;totals[r['candidate']]=r['votes']
  assert dict(sums)==totals=={k:v['native_sum']for k,v in a['candidate_checks'].items()};assert all(v['passes']and v['printed_TOTAL']==v['native_sum']for v in a['candidate_checks'].values())
  native=sum(r=='source_native_reporting_constituent'for r in units.values());assert native==a['native_constituents'];total=sum(r=='source_TOTAL'for r in units.values());assert total==1
  counts.update(native_constituents=native,TOTAL_columns=total,unused_columns=sum(r=='unused_template_column'for r in units.values()),publication_views=1,source_positions=len(a['rows']))
  if sid in selected:counts.update(selected82_publications=1,selected82_native_constituents=native)
  finding=dict(source_id=sid,raw_PDF_sha256=sha(raw),raw_PDF_bytes=len(raw),stored_original_pin=pin(rawpath),native_constituents=native,source_positions=len(a['rows']),source_candidate_sums_and_TOTAL=dict(sums),whitespace_only_label_representations=aliases,worker_declared_earlier_peer_CSV_sha256=a['peer_file_sha256'])
  if a['peer_differences']:finding['earlier_peer_literal_label_differences_retained']=a['peer_differences'];finding['current_compared70_original_literal_agrees']=True
  findings.append(finding)
 cumulative=collections.Counter(prior['counts']);cumulative.update(counts)
 out=dict(status='pass_bounded_disjoint_independent_original2020_native_extension',prior_immutable_review=pin(priorpath),immutable_original_source_witness=pin(comparison),exact_frozen_turnout_inputs=inputpins,new_counts=dict(counts),counts=dict(cumulative),source_findings=prior['source_findings']+findings,new_original_raster_pins=list(rasterpins.values()),qualification='New announced JSON/CSV originals are frozen losslessly before comparison; physical hint metadata is exactly a vote/label/ID-free projection of the immutable source witness. All source hashes/pages/physical columns/candidate values/roles and whitespace-folded literal headers match the independent source ledger; original rasters survive by hash. Amended publications stay separate, selected82 is not a cross-publication identity join. Broad row bands and provisional OCR windows are not certified numeric polygons or current boundaries. This is not a fresh coordinator glyph read of every field or complete statewide historical/method/dispatch acceptance.',formal_native887_dispatch_accepted=False,historical_native_complete=False,current_geography_approved=False)
 if comparison!=snapshot:out['separate_immutable_position_hint_source_witness']=pin(snapshot)
 p=DATA/args.output;b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable proof changed'
 else:p.write_bytes(b)
 print(json.dumps(dict(output_pin=pin(p),new_counts=dict(counts),cumulative_counts=dict(cumulative))))
if __name__=='__main__':main()
