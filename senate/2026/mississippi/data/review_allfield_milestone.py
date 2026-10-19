"""Check a named immutable all-field milestone without mutating prior proofs."""
from pathlib import Path
import argparse,collections,csv,gzip,io,json
from review_allfield_sixteenview_snapshot import load,sources,NAMES,sha,pin,DATA,ROOT

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--version',required=True);parser.add_argument('--sha256',required=True)
 parser.add_argument('--prior',required=True);parser.add_argument('--prior-sha256',required=True);args=parser.parse_args()
 new,items,newpin=load(args.version,args.sha256);old,prioritems,oldpin=load(args.prior,args.prior_sha256)
 ss=sources(items);prior=sources(prioritems);assert set(prior)<set(ss)
 assert all(ss[k]==v for k,v in prior.items())
 coverage=json.loads(items['native-allfield-coverage.json']);counts=collections.Counter();details=[]
 for sid,s in ss.items():
  sums={n:0 for n in NAMES};totals={};c=collections.Counter()
  for p in s['pages']:
   c['source_pages']+=1;roles=p.get('roles')
   if roles is None:
    alias={'summary_TOTAL':'source_TOTAL','unused':'unused_template_column'}
    roles=[alias.get(x['unit_type'],'source_native_reporting_constituent')for x in p['columns']]
   rc=collections.Counter(roles)
   for key,role in [('native_constituents','source_native_reporting_constituent'),('source_TOTAL_columns','source_TOTAL'),('unused_blank_columns','unused_template_column'),('nonadditive_parallel_columns','parallel_native_observation')]:c[key]+=rc[role]
   assert [f.get('candidate',f.get('field'))for f in p['fields']]==NAMES
   for f in p['fields']:
    name=f.get('candidate',f.get('field'));assert len(f['values'])==len(roles)
    for role,v in zip(roles,f['values']):
     if role=='unused_template_column':assert v is None;c['unused_null_positions']+=1
     else:
      assert type(v)is int and v>=0;c['numeric_positions']+=1
      if role=='source_native_reporting_constituent':sums[name]+=v
      elif role=='source_TOTAL':assert name not in totals;totals[name]=v
      else:assert role=='parallel_native_observation'
  assert sums==totals
  recorded=next(x for x in coverage['sources']if x['source_id']==sid)
  assert all(recorded[k]==v for k,v in c.items())and recorded['all11_source_native_sums']==sums
  counts.update(c);details.append({'source_id':sid,'raw_sha256':s['raw_sha256'],**c,'named_vectors':sums})
 counts['source_views']=len(ss);parents=coverage['all82_preferred_source_parent_status']
 assert len(parents)==82 and sum(p['source_native_constituents']for p in parents)==1736
 assert {p['source_id']for p in parents if p['all11_original_review_complete']}==set(ss)
 unknown=[p for p in parents if not p['all11_original_review_complete']]
 counts['preferred_unreviewed_county_views']=len(unknown)
 counts['preferred_unreviewed_native_constituents']=sum(p['source_native_constituents']for p in unknown)
 assert dict(counts)==new['counts']==coverage['counts']
 flat=0;rasters=set()
 for filename in ['native-allfield-additional-candidate-votes.csv','winston-native-allfield-candidate-votes.csv']:
  rows=list(csv.DictReader(io.StringIO(items[filename].decode())));index={tuple(r[k]for k in ['source_id','source_page','source_column','candidate']):r for r in rows}
  assert len(index)==len(rows)
  for r in csv.DictReader(io.StringIO(prioritems[filename].decode())):assert index[tuple(r[k]for k in ['source_id','source_page','source_column','candidate'])]==r
  for r in rows:
   s=ss[r['source_id']];p=next(p for p in s['pages']if p['page']==int(r['source_page']));j=int(r['source_column'])-1
   field=next(f for f in p['fields']if f['candidate']==r['candidate'])
   assert (None if r['value']==''else int(r['value']))==field['values'][j]
   assert r['raw_sha256']==s['raw_sha256']and r['role']==p['roles'][j]
   label=p['headers'][j]['label_literal']if'headers'in p else p['labels_literal'][j]
   assert r.get('literal_native_label',r.get('label_literal'))==label
   key=(r['full_original_render_path'],r['render_sha256'])
   if key not in rasters:assert pin(ROOT/key[0])['sha256']==key[1];rasters.add(key)
   flat+=1
 old84=DATA/'coordinator-qa/native-replay-84views/native-2024-senate-reviewed-84views.json.gz'
 raw=gzip.decompress(old84.read_bytes());assert sha(raw)=='fbc0f8caedc6be263b13a433c74f36df373720d290d8aa8674b0d2d9c91e09a7'
 prior84={s['source_id']:s for s in json.loads(raw)['sources']};reuse=[]
 for sid,s in ss.items():
  reused=0
  for p in s['pages']:
   fields=p['fields']
   if not any(f.get('basis','').startswith('Earlier own independently original-reviewed Senate')for f in fields):continue
   oldsource=prior84[sid];op=next(p0 for p0 in oldsource['pages']if p0['page']==p['page'])
   assert s['raw_sha256']==oldsource['raw_sha256']and p['render_sha256']==op['raster_sha256']
   assert p['rotation_ccw']==op['rotation_ccw']and p['render_size']==op['render_size']
   for j,h in enumerate(p['headers']):
    oc=op['columns'][j]
    assert h['source_column']==oc['source_column']and h['header_bounds']==oc['header_bounds']
    assert h['label_literal']==oc['label_literal']and h['role']==oc['role']
    for f in fields[-2:]:
     assert f['basis'].startswith('Earlier own independently original-reviewed Senate')
     assert f['values'][j]==oc['fields'][f['candidate']]['value'];reused+=1
   assert all(f['basis'].startswith('Every original numeric glyph')for f in fields[:9])
  if reused:reuse.append({'source_id':sid,'same_source_Senate_numeric_or_null_positions':reused})
 output={'status':'pass_bounded_frozen_allfield_milestone_pins_and_source_coverage',
  'snapshot_pin':newpin,'previous_snapshot_pin':oldpin,'lossless_pins':new['pins'],
  'counts':dict(counts),'all_prior_source_ledgers_and_flat_rows_unchanged':True,
  'flat_CSV_source_positions_checked':flat,'unique_complete_render_hashes_checked':len(rasters),
  'source_controls':details,'same_publication_prior_Senate_reuse':reuse,
  'prior_original_Senate_witness_pin':pin(old84),
  'qualification':'Bounded byte/source/position/basis and arithmetic review only. All newly claimed presidential cells retain worker direct-original basis, separate from explicitly reused own exact-publication Senate readings. Exact raw hash/page/raster/header bounds verify reuse, not a cross-year/name/geographic join. Arithmetic closure is not blanket fresh coordinator visual acceptance or a completion guarantee. All earlier immutable milestones remain unchanged; unknown preferred units stay explicitly unknown. Whole-state presidential, historical-native/method and current reporting/geographic gates remain open.',
  'whole_state_presidential_complete':False,'historical_native_complete':False,
  'formal_dispatch_accepted':False,'current2026_geography_approved':False}
 target=DATA/f'coordinator-allfield-{args.version}-snapshot-review.json'
 rendered=(json.dumps(output,indent=2)+'\n').encode()
 if target.exists():assert target.read_bytes()==rendered,'Immutable coordinator milestone changed'
 else:target.write_bytes(rendered)
 print(json.dumps({'status':output['status'],'counts':dict(counts),'flat_positions':flat,'reuse_sources':len(reuse),'reused_numeric_or_null_positions':sum(r['same_source_Senate_numeric_or_null_positions']for r in reuse),'output_pin':pin(target)}))

if __name__=='__main__':main()
