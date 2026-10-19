"""Check immutable bounded coverage independently; do not approve unknown fields."""
from pathlib import Path
import collections, csv, gzip, hashlib, io, json

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
NAMES=['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump',
       'Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski',
       'Ty Pinkins','Roger F. Wicker']
# Fresh complete original PDF1, Poppler180dpi, independently read by coordinator.
# Actual PDF1 visibly prints footerPage2. This does not change its file ordinal.
ISSAQUENA=[
 [13,53,105,75,41,287], [1,1,1,1,1,5], [1,3,1,1,1,7], [1,1,1,1,1,5],
 [83,61,12,58,82,296], [1,1,1,1,1,5], [1,1,2,1,1,6], [1,1,2,1,1,6],
 [1,1,1,1,1,5], [74,44,111,49,13,291], [60,84,10,86,64,304]]

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}

def main():
 path=DATA/'baselines/source/native-allfield-10views/snapshot.json'
 raw=path.read_bytes();assert sha(raw)=='ca68221a306e86a4566bdb2187cf74edbfdfba125bf36ae1a05e450f6699252c'
 snapshot=json.loads(raw);decoded={};checks=[]
 for item in snapshot['pins']:
  p=ROOT/item['frozen_path'];stored=p.read_bytes();body=gzip.decompress(stored)
  assert len(stored)==item['stored_bytes'] and sha(stored)==item['stored_sha256']
  assert len(body)==item['original_bytes'] and sha(body)==item['original_sha256']
  decoded[Path(item['original_path']).name]=body;checks.append(item)
 coverage=json.loads(decoded['native-allfield-coverage.json'])
 sources=[]
 for name,body in decoded.items():
  if not name.endswith('.json') or name=='native-allfield-coverage.json':continue
  d=json.loads(body);ss=d.get('sources',[d]);sources.extend(ss.values() if isinstance(ss,dict)else ss)
 assert len(sources)==10 and len({s['source_id']for s in sources})==10
 results=[];counts=collections.Counter()
 for s in sources:
  sid=s['source_id'];sums={n:0 for n in NAMES};totals={};c=collections.Counter()
  for page in s['pages']:
   c['source_pages']+=1
   roles=page.get('roles')
   if roles is None:
    alias={'summary_TOTAL':'source_TOTAL','unused':'unused_template_column'}
    roles=[alias.get(x['unit_type'],'source_native_reporting_constituent')for x in page['columns']]
   role_counts=collections.Counter(roles)
   c['native_constituents']+=role_counts['source_native_reporting_constituent']
   c['source_TOTAL_columns']+=role_counts['source_TOTAL']
   c['unused_blank_columns']+=role_counts['unused_template_column']
   c['nonadditive_parallel_columns']+=role_counts['parallel_native_observation']
   fields=page['fields'];assert [f.get('candidate',f.get('field'))for f in fields]==NAMES
   for field in fields:
    name=field.get('candidate',field.get('field'));values=field['values'];assert len(values)==len(roles)
    for role,value in zip(roles,values):
     if role=='unused_template_column':assert value is None;c['unused_null_positions']+=1
     else:
      assert type(value)is int and value>=0;c['numeric_positions']+=1
      if role=='source_native_reporting_constituent':sums[name]+=value
      elif role=='source_TOTAL':assert name not in totals;totals[name]=value
      else:assert role=='parallel_native_observation'
   if sid=='sos-2024-county-issaquena':
    assert page['page']==1 and roles==['source_native_reporting_constituent']*5+['source_TOTAL']+['unused_template_column']*5
    assert [f['values']for f in fields]==[r+[None]*5 for r in ISSAQUENA]
  assert sums==totals and len(totals)==11
  listed=next(x for x in coverage['sources']if x['source_id']==sid)
  assert all(listed[k]==v for k,v in c.items())
  assert listed['all11_source_native_sums']==sums
  counts.update(c);results.append({'source_id':sid,'raw_sha256':s['raw_sha256'],**c,
      'recomputed_native_candidate_sums':sums,'recomputed_printed_TOTAL':totals})
 counts['source_views']=len(sources)
 parents=coverage['all82_preferred_source_parent_status'];assert len(parents)==82
 assert len({p['source_id']for p in parents})==82
 assert sum(p['source_native_constituents']for p in parents)==1736
 assert {p['source_id']for p in parents if p['all11_original_review_complete']}=={s['source_id']for s in sources}
 unreviewed=[p for p in parents if not p['all11_original_review_complete']]
 counts['preferred_unreviewed_county_views']=len(unreviewed)
 counts['preferred_unreviewed_native_constituents']=sum(p['source_native_constituents']for p in unreviewed)
 assert dict(counts)==snapshot['counts']==coverage['counts']
 assert counts['numeric_positions']==1441 and counts['unused_null_positions']==495
 flat_positions=0
 for name in ['native-allfield-additional-candidate-votes.csv','winston-native-allfield-candidate-votes.csv']:
  rr=list(csv.DictReader(io.StringIO(decoded[name].decode())));assert rr
  # Preserve all source field strings in their immutable lossless copies.
  assert len(rr)==(605 if name.startswith('native-allfield-additional') else 242)
  for row in rr:
   source=next(s for s in sources if s['source_id']==row['source_id'])
   page=next(p for p in source['pages']if p['page']==int(row['source_page']))
   col=int(row['source_column'])-1
   field=next(f for f in page['fields']if f.get('candidate',f.get('field'))==row['candidate'])
   assert (None if row['value']=='' else int(row['value']))==field['values'][col]
   assert row['raw_sha256']==source['raw_sha256'] and row['role']==page['roles'][col]
   label=page['headers'][col]['label_literal'] if 'headers'in page else page['labels_literal'][col]
   assert row.get('literal_native_label',row.get('label_literal'))==label
   raster=ROOT/row['full_original_render_path'];assert pin(raster)['sha256']==row['render_sha256']
   flat_positions+=1
 assert flat_positions==847
 source=json.loads((DATA/'coordinator-qa/issaquena-allfield-review/source-and-render.json').read_bytes())
 assert pin(ROOT/source['render']['path'])['sha256']==source['render']['sha256']
 assert source['source']['raw_sha256']==next(s['raw_sha256']for s in sources if s['source_id']=='sos-2024-county-issaquena')
 output={'status':'pass_immutable_eight_pins_and_bounded_coverage_arithmetic',
  'snapshot_pin':pin(path),'lossless_file_pins':checks,'recomputed_counts':dict(counts),
  'source_checks':results,'exact_flat_CSV_positions_checked':flat_positions,'fresh_coordinator_Issaquena_original_review':{
   'source_and_render':source,'candidate_order':NAMES,'independent_numeric_readings':ISSAQUENA,
   'native_columns':5,'physical_TOTAL_columns':1,'numeric_positions':66,'unused_null_positions':55,
   'actual_pdf_page':1,'printed_footer_page':2,
   'literal_headers':['Addie Voting Precinct','Grace Voting Precinct','Mayersville\nCourthouse','Tallula Community\nCenter','Valley Park\nCommunity Center','TOTAL']},
  'scope':'Eight exact frozen files and the ten-view coverage arithmetic pass. The coordinator freshly read all66 numeric Issaquena positions and55 unused nulls from complete originalPDF1, including printed minor-candidate1 glyphs; no inferred zeros or repairs. Prior coordinator original Alcorn/Coahoma and Tunica/Kemper reviews remain separate evidence. Arithmetic closure alone is not independent visual acceptance of every remaining new glyph.110 preferred native constituents are covered by worker all11 ledgers;1626 native scopes across72 parents remain explicitly unreviewed. Vendor profiles, parallel Kemper observations, whole historical native/method coverage and current reporting/geographic equivalence remain separate. No formal dispatch acceptance is made.',
  'formal_dispatch_accepted':False,'complete_statewide_presidential':False,
  'historical_native_complete':False,'current2026_geography_approved':False}
 target=DATA/'coordinator-allfield-tenview-snapshot-review.json'
 target.write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'status':output['status'],'counts':dict(counts),'output_pin':pin(target)}))

if __name__=='__main__':main()
