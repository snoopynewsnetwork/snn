"""Coordinator checks of complete frozen objects and raw Polk alternate exports."""
from pathlib import Path
import collections,csv,gzip,hashlib,html,io,json,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/results-sources'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_bytes())
def raw(name):
 r=load(OUT/'source'/f'{name}.receipt.json');p=ROOT/r['body_path'];stored=p.read_bytes();b=gzip.decompress(stored)
 assert sha(stored)==r['stored_sha256'] and sha(b)==r['raw_sha256'] and len(b)==r['raw_bytes']
 assert r['status']==200 and r['complete']
 return b,r
def main():
 mfpath=OUT/'asset-manifest.json';mfraw=mfpath.read_bytes()
 assert sha(mfraw)=='0b68e2a10d9d4c4ec88cad5989aaa97b186b04c464dfb40e4e1b9afc74ab927e'
 mf=json.loads(mfraw);assert len(mf['assets'])==1057
 actual={p.resolve() for p in OUT.rglob('*') if p.is_file() and p!=mfpath}|{(ROOT/'official-results.md').resolve(),(ROOT/'data/official-results-sources.csv').resolve()}
 assert actual=={(ROOT/r['path']).resolve() for r in mf['assets']}
 for row in mf['assets']:
  b=(ROOT/row['path']).read_bytes();assert len(b)==row['bytes']<40000000 and sha(b)==row['sha256']
 c=load(ROOT/'data/turnout/priority-set.json')
 f=json.loads(gzip.decompress((OUT/'frozen-context.json.gz').read_bytes()));assert f['frozen_contract']==c
 records=[json.loads(l) for l in gzip.decompress((OUT/'county-investigations.jsonl.gz').read_bytes()).splitlines()]
 assert [r['frozen_parent'] for r in records]==c['all_unit_order']
 assert [r['frozen_primary_constituent_object'] for r in records]==c['native_constituents']
 native=[json.loads(l) for l in gzip.decompress((ROOT/'data/turnout/extracts/native-units.jsonl.gz').read_bytes()).splitlines()]
 copied=sorted((u for r in records for u in r['full_historical_native_contexts_in_source_order']),key=lambda r:r['global_source_position_1based'])
 assert len(copied)==len(native)==23532 and [x['full_native_object'] for x in copied]==native
 csvrows=list(csv.DictReader((ROOT/'data/official-results-sources.csv').open(newline='')));assert len(csvrows)==68
 exports={};pins=[]
 for sid in ['polk2024-report-16','polk2024-report-18']:
  b,r=raw(sid);rows=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))));exports[sid]=rows
  pins.append({'id':sid,'url':r['final_url'],'bytes':len(b),'raw_sha256':sha(b),'records':len(rows)})
 summary=exports['polk2024-report-16'];precinct=exports['polk2024-report-18'];assert len(summary)==82 and len(precinct)==9249
 sen=[r for r in summary if r['Contest']=='United States Senator'];units=[r for r in precinct if r['Contest']=='United States Senator']
 expected={'Rick Scott':201722,'Debbie Mucarsel-Powell':135475,'Feena Bonoan':1920,'Tuan TQ Nguyen':1721,'Ben Everidge':2473,'WRITE-IN':383}
 observed={r['Candidate Issue']:int(r['Total Votes']) for r in sen};assert observed==expected,(observed,expected)
 assert len(units)==1032 and len({r['Precinct Name'] for r in units})==172
 sums=collections.Counter();pairs=set();masked=collections.Counter()
 for r in units:
  pair=(r['Precinct Name'],r['Candidate Issue']);assert pair not in pairs;pairs.add(pair)
  sums[r['Candidate Issue']]+=int(r['Total Votes'])
  for k in ['Mail Votes','Early Votes','Election Day Votes']:
   if r[k]=='-':masked[k]+=1
 assert dict(sums)==expected
 primary=load(ROOT/'data/coordinator-primary-table-review.json')['tables']['2024_senate']
 polk=next(r for r in primary['counties'] if r['county_literal']=='Polk')
 for name,n in expected.items():
  if name=='WRITE-IN':continue
  index=next(i for i,h in enumerate(primary['headers']) if name.casefold() in h.casefold());assert polk['votes'][index]==n
 htmlvector={'Rick Scott':201487,'Debbie Mucarsel-Powell':135295,'Feena Bonoan':1912,'Tuan TQ Nguyen':1715,'Ben Everidge':2471}
 b,hr=raw('follow-POL2024');plain=' '.join(html.unescape(re.sub('<[^>]*>',' ',b.decode(errors='replace'))).split())
 section=plain[plain.index('United States Senator'):plain.index('Representative in Congress',plain.index('United States Senator'))]
 for name,n in htmlvector.items():
  assert re.search(re.escape(name)+r' \([^)]*\) - - - '+f'{n:,}'+r' ',section),(name,n)
  assert re.search(re.escape(name)+r' \([^)]*\) [\d.]+% '+f"{expected[name]:,}"+r' ',section),(name,expected[name])
 assert sum(htmlvector.values())-sum(expected[n] for n in htmlvector)==-431
 out={'status':'pass_with_retained_HTML_CSV_disagreement','owned_manifest_sha256':sha(mfraw),'exact_manifest_assets':1057,'complete_frozen_parents':67,'complete_frozen_native_contexts':23532,'source_inventory_rows_including_state':68,'Polk_raw_export_pins':pins,'Polk_Senate_summary':expected,'Polk_Senate_precinct_positions':len(units),'Polk_Senate_unit_labels':172,'Polk_precinct_sums_equal_summary_and_DOS_five_named_choices':True,'Polk_HTML_detailed_table_five_printed':htmlvector,'Polk_HTML_detailed_table_minus_CSV_five_printed':-431,'Polk_same_HTML_Choice_Percent_Votes_chart_matches_CSV':True,'Polk_HTML_raw_sha256':hr['raw_sha256'],'generic_WRITE_IN_not_added_to_valid_named_denominator':383,'masked_method_cells':dict(masked),'qualification':'Raw published complete CSV alternate supports usable named controls. Detailed HTML table is lower, while its separate Choice/Percent/Votes chart uses the CSV vector. Both remain as published; no cause, chronology, physical equivalence, exact outstanding votes or cadence inferred.'}
 (ROOT/'data/coordinator-results-final-review.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k not in ['Polk_raw_export_pins']}))
if __name__=='__main__':main()
