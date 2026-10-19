"""Independent complete-original Stone readings, with failed history retained."""
from pathlib import Path
import csv,gzip,io,json
from review_allfield_milestone import DATA,ROOT,NAMES,load,sources,sha,pin

# Typed from fresh complete Poppler160dpi originalPDF2/3 images before reading
# the worker's Stone vectors or correction-history values.
PAGE2=[
 [9,25,84,93,294,456,55,25,28,32,96], [0,1,1,4,0,3,2,0,2,0,1],
 [1,0,0,0,1,1,0,1,0,0,0], [0,2,1,0,3,1,0,0,1,0,3],
 [115,262,414,371,321,232,246,378,374,375,1037], [0,0,0,0,1,0,0,0,0,0,0],
 [0,0,2,0,0,0,0,0,0,0,1], [0,0,4,2,2,1,1,0,1,1,4],
 [1,2,0,1,2,0,0,0,0,1,3], [3,27,76,86,288,434,51,23,27,27,92],
 [115,262,424,379,322,250,248,371,373,378,1036]]
PAGE3=[
 [178,132,87,26,1620], [4,1,2,0,21], [0,0,0,0,4], [3,2,0,0,16],
 [589,715,559,226,6214], [0,0,1,0,2], [0,0,1,0,4], [7,3,0,0,26],
 [0,0,2,0,12], [161,105,87,23,1510], [603,739,555,227,6282]]

def main():
 dest=DATA/'coordinator-qa/stone-original-row-review';render=json.loads((dest/'source-and-page-pointers.json').read_bytes())
 src=render['source'];stored=(ROOT/src['path']).read_bytes();raw=gzip.decompress(stored)
 assert sha(stored)==src['stored_sha256']and sha(raw)==src['raw_sha256']
 previews=[pin(dest/f'original-p{n}.png')for n in [2,3]]
 manifest,items,sp=load('35views','3093119b93877c9403f6ea12956037622bea5c7acf2c6e44e87739cfd1c0a90f')
 stone=sources(items)['sos-2024-county-stone'];assert stone['raw_sha256']==src['raw_sha256']
 assert [p['page']for p in stone['pages']]==[2,3]
 for i,pg in enumerate(stone['pages']):
  assert [f['candidate']for f in pg['fields']]==NAMES
  assert [f['values']for f in pg['fields']]==(PAGE2 if i==0 else[r+[None]*6 for r in PAGE3])
 totals={n:PAGE3[i][4]for i,n in enumerate(NAMES)}
 assert all(sum(PAGE2[i])+sum(PAGE3[i][:4])==PAGE3[i][4]for i in range(11))
 news=json.loads((DATA/'news/manifest.json').read_bytes());csvsource=next(r for r in news if r['id']=='sos-2024-recap-csv')
 data=gzip.decompress((DATA/'news'/csvsource['asset']).read_bytes());assert sha(data)==csvsource['raw_sha256']
 rows=[r for r in csv.DictReader(io.StringIO(data.decode('utf-8-sig')))if r['County']=='Stone'and r['Office']in['United States-President','United States-Senate']]
 assert len(rows)==11;official={}
 for name in NAMES:
  rr=[r for r in rows if r['Candidate']==name or r['Candidate'].startswith('Presidential Electors for '+name+' for President')]
  assert len(rr)==1;official[name]=int(rr[0]['County Total'])
 assert totals==official
 history_path=dest/'original-correction-history-snapshot.json.gz'
 if not history_path.exists():
  p=DATA/'baselines/native-allfield-correction-history.json';b=p.read_bytes();assert p.read_bytes()==b
  history_path.write_bytes(gzip.compress(b,mtime=0))
 history=json.loads(gzip.decompress(history_path.read_bytes()))
 correction=next(c for c in history['corrections']if c['source_id']=='sos-2024-county-stone')
 assert correction['original_re_read_vector']==PAGE2[7]
 assert correction['prior_unaccepted_whole_page_manual_vector']!=PAGE2[7]
 for e in correction['evidence']:
  assert pin(ROOT/e['path'])['sha256']==e['sha256']
  assert pin(ROOT/e['original_raster_path'])['sha256']==e['original_raster_sha256']
 output={'status':'pass_bounded_independent_complete_original_Stone_all11_reading',
  'source_pin':src,'coordinator_fresh_complete_original_renders':previews,
  'immutable_peer_snapshot_pin':sp,'candidate_order':NAMES,
  'independent_original_PDF2_numeric_readings':PAGE2,'independent_original_PDF3_native_and_TOTAL_readings':PAGE3,
  'PDF3_unused_columns_per_candidate':6,'native_constituents':15,'numeric_positions':176,'unused_null_positions':66,
  'all11_native_sums_match_printed_TOTAL_and_original_county_CSV':True,'source_TOTALs':totals,
  'primary_county_CSV_pin':csvsource,'prior_failed_history_snapshot':pin(history_path),
  'Stone_Kennedy_corrected_row':correction,
  'scope':'Coordinator typed all11 candidate vectors from fresh complete originalPDF2/3 before reading worker Stone vectors/history.176 numeric and66 unused/null positions match the frozen independent35-view ledger and original county CSV. Kennedy originalPDF2 clearly prints0,0,4,2,2,1,1,0,1,1,4; the prior failed typed vector remains history, never fitted to a residual. Only15 source-native Stone constituents are covered. No current native-ID/map/cross-year/method equivalence, whole-state completion or dispatch acceptance follows.',
  'formal_dispatch_accepted':False,'current_geography_approved':False}
 p=DATA/'coordinator-stone-original-allfield-review.json';p.write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'status':output['status'],'numeric_positions':176,'unused_null_positions':66,'output_pin':pin(p)}))
if __name__=='__main__':main()
