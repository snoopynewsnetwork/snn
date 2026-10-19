"""Audit sixteen immutable source views, retaining prior bounded witnesses."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json
from review_allfield_tenview_snapshot import NAMES,sha,pin

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent

def load(version,expected):
 p=DATA/f'baselines/source/native-allfield-{version}/snapshot.json'
 assert sha(p.read_bytes())==expected
 snapshot=json.loads(p.read_bytes());items={}
 for entry in snapshot['pins']:
  b=(ROOT/entry['frozen_path']).read_bytes();raw=gzip.decompress(b)
  assert len(b)==entry['stored_bytes']and sha(b)==entry['stored_sha256']
  assert len(raw)==entry['original_bytes']and sha(raw)==entry['original_sha256']
  items[Path(entry['original_path']).name]=raw
 return snapshot,items,pin(p)

def sources(items):
 result={}
 for name,raw in items.items():
  if not name.endswith('.json')or name=='native-allfield-coverage.json':continue
  d=json.loads(raw);ss=d.get('sources',[d]);ss=ss.values()if isinstance(ss,dict)else ss
  for s in ss:assert s['source_id']not in result;result[s['source_id']]=s
 return result

def main():
 new,items,newpin=load('16views','698283c2081970d5388b1270123172a11bfc3282ffd3593cd50949f879a3b194')
 old,olditems,oldpin=load('10views','ca68221a306e86a4566bdb2187cf74edbfdfba125bf36ae1a05e450f6699252c')
 ss=sources(items);prior=sources(olditems);assert len(ss)==16
 assert all(ss[k]==v for k,v in prior.items())
 coverage=json.loads(items['native-allfield-coverage.json'])
 c=collections.Counter();details=[]
 for sid,s in ss.items():
  sums={n:0 for n in NAMES};totals={};counts=collections.Counter()
  for page in s['pages']:
   counts['source_pages']+=1;roles=page.get('roles')
   if roles is None:
    alias={'summary_TOTAL':'source_TOTAL','unused':'unused_template_column'}
    roles=[alias.get(x['unit_type'],'source_native_reporting_constituent')for x in page['columns']]
   rc=collections.Counter(roles)
   for out,role in [('native_constituents','source_native_reporting_constituent'),('source_TOTAL_columns','source_TOTAL'),('unused_blank_columns','unused_template_column'),('nonadditive_parallel_columns','parallel_native_observation')]:counts[out]+=rc[role]
   assert [f.get('candidate',f.get('field'))for f in page['fields']]==NAMES
   for f in page['fields']:
    name=f.get('candidate',f.get('field'));assert len(f['values'])==len(roles)
    for role,v in zip(roles,f['values']):
     if role=='unused_template_column':assert v is None;counts['unused_null_positions']+=1
     else:
      assert type(v)is int and v>=0;counts['numeric_positions']+=1
      if role=='source_native_reporting_constituent':sums[name]+=v
      elif role=='source_TOTAL':assert name not in totals;totals[name]=v
      else:assert role=='parallel_native_observation'
  assert sums==totals
  listed=next(x for x in coverage['sources']if x['source_id']==sid)
  assert all(listed[k]==v for k,v in counts.items())and listed['all11_source_native_sums']==sums
  c.update(counts);details.append({'source_id':sid,'raw_sha256':s['raw_sha256'],**counts,'native_sums_and_source_TOTALs':totals})
 c['source_views']=len(ss)
 pp=coverage['all82_preferred_source_parent_status'];assert len(pp)==82 and sum(p['source_native_constituents']for p in pp)==1736
 assert {p['source_id']for p in pp if p['all11_original_review_complete']}==set(ss)
 unknown=[p for p in pp if not p['all11_original_review_complete']]
 c['preferred_unreviewed_county_views']=len(unknown);c['preferred_unreviewed_native_constituents']=sum(p['source_native_constituents']for p in unknown)
 assert dict(c)==new['counts']==coverage['counts']
 flat=0;seen=set()
 for filename in ['native-allfield-additional-candidate-votes.csv','winston-native-allfield-candidate-votes.csv']:
  rows=list(csv.DictReader(io.StringIO(items[filename].decode())))
  index={(r['source_id'],r['source_page'],r['source_column'],r['candidate']):r for r in rows};assert len(index)==len(rows)
  for priorrow in csv.DictReader(io.StringIO(olditems[filename].decode())):
   key=tuple(priorrow[k]for k in ['source_id','source_page','source_column','candidate']);assert index[key]==priorrow
  for row in rows:
   s=ss[row['source_id']];page=next(p for p in s['pages']if p['page']==int(row['source_page']));j=int(row['source_column'])-1
   f=next(f for f in page['fields']if f['candidate']==row['candidate'])
   assert (None if row['value']==''else int(row['value']))==f['values'][j]
   assert row['raw_sha256']==s['raw_sha256']and row['role']==page['roles'][j]
   label=page['headers'][j]['label_literal']if'headers'in page else page['labels_literal'][j]
   assert row.get('literal_native_label',row.get('label_literal'))==label
   raster=ROOT/row['full_original_render_path'];key=(str(raster),row['render_sha256'])
   if key not in seen:assert pin(raster)['sha256']==key[1];seen.add(key)
   flat+=1
 # Hinds prior Senate readings must be the exact same publication and positions.
 frozen=DATA/'coordinator-qa/native-replay-84views/native-2024-senate-reviewed-84views.json.gz'
 raw=gzip.decompress(frozen.read_bytes());assert sha(raw)=='fbc0f8caedc6be263b13a433c74f36df373720d290d8aa8674b0d2d9c91e09a7'
 priorh=next(s for s in json.loads(raw)['sources']if s['source_id']=='sos-2024-county-hinds')
 h=ss['sos-2024-county-hinds'];assert h['raw_sha256']==priorh['raw_sha256']
 reused=0;presnumeric=0;presnull=0
 for page in h['pages']:
  oldpage=next(p for p in priorh['pages']if p['page']==page['page'])
  assert page['render_sha256']==oldpage['raster_sha256']and page['rotation_ccw']==oldpage['rotation_ccw']
  assert page['render_size']==oldpage['render_size']
  for j,head in enumerate(page['headers']):
   oldcol=oldpage['columns'][j]
   assert head['source_column']==oldcol['source_column']and head['header_bounds']==oldcol['header_bounds']
   assert head['label_literal']==oldcol['label_literal']and head['role']==oldcol['role']
   for field in page['fields'][-2:]:
    assert field['values'][j]==oldcol['fields'][field['candidate']]['value'];reused+=1
    assert field['basis'].startswith('Earlier own independently original-reviewed Senate candidate cells reused')
   for field in page['fields'][:9]:
    assert field['basis'].startswith('Every original numeric glyph')
    if field['values'][j]is None:presnull+=1
    else:presnumeric+=1
 assert reused==220 and presnumeric==981 and presnull==9
 output={'status':'pass_immutable_sixteen_view_pins_and_source_coverage_arithmetic',
  'snapshot_pin':newpin,'prior_tenview_snapshot_pin':oldpin,'lossless_pins':new['pins'],
  'counts':dict(c),'all_prior_ten_source_ledgers_unchanged':True,'flat_CSV_positions_checked':flat,
  'source_results':details,'Hinds_same_original_Senate_reuse':{
   'prior_frozen_pin':pin(frozen),'raw_sha256':h['raw_sha256'],'pages':10,
   'two_Senate_numeric_or_null_fields_checked':reused,'new_presidential_numeric_positions':presnumeric,
   'presidential_unused_null_positions':presnull,'header_boxes_and_render_hashes_exact':True,
   'scope':'Prior two Senate fields are explicitly reused own original readings at exact same source hash/page/physical header positions.981 presidential numeric positions and9 unused blanks are new worker original readings, not claimed newly independent coordinator visual reads.'},
  'scope':'All eight lossless pins,36 pages,16 original source partitions and3487 numeric/869 null positions pass coverage and source-vector arithmetic. Previous ten-view ledger semantics and flat rows remain unchanged. No acceptance based on residual fitting or arithmetic closure is inferred.1446 native presidential scopes across66 preferred parent views remain explicitly unknown; historical native/method and current reporting/geographic equivalence remain open. The immutable native887 proposal and all earlier witnesses remain unchanged.',
  'complete_statewide_presidential':False,'historical_native_complete':False,
  'current2026_geography_approved':False,'formal_dispatch_accepted':False}
 target=DATA/'coordinator-allfield-sixteenview-snapshot-review.json';target.write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'status':output['status'],'counts':dict(c),'flat_positions':flat,'output_pin':pin(target)}))

if __name__=='__main__':main()
