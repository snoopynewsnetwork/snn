#!/usr/bin/env python3
import pathlib,json,gzip,csv,collections,re,datetime,hashlib
from extract import ROOT,STATE,writejson,textfile
inv=json.loads((ROOT/'authority-inventory.json').read_text());notes=json.loads((ROOT/'priority-notes.json').read_text());assert len(notes)==24
rows=textfile('export-general201-counties');pct=textfile('export-general201-precincts');hist=textfile('export-2024-precinct');state201=textfile('export-general201-state');priorities=[]
for c in inv:
 c['test201_county_table_positions']=[x for x in rows if x['fields'][1].casefold()==c['name'].casefold() or (x['fields'][1].casefold()=='mcleod' and c['name']=='McLeod')]
 assert len(c['test201_county_table_positions'])==1,(c['name'],c['test201_county_table_positions'])
 tc=c['test201_county_table_positions'][0];code=tc['fields'][0];c['test201_precinct_table_count']=sum(x['fields'][0]==code for x in pct);assert c['test201_precinct_table_count']==int(tc['fields'][2])
 c['historical_2024_export_positions']={'source':'export-2024-precinct','lines':[x['line'] for x in hist if int(x['fields'][1])==int(c['source_county_code'])],'semantics':'complete candidate rows for county; no physical boundary/current join asserted'}
 if c['in_priority']:
  n=dict(notes[c['name']]);n.update({k:c[k] for k in ['key','rank','name','county_fips','source_county_code','historical_votes_2024','native_context_object','native_counts','late_opening_rows','test201_county_table_positions','test201_precinct_table_count','historical_2024_export_positions']});n['source_records']=[json.loads((ROOT/'raw'/f'{id}.meta.json').read_text()) for id in n['evidence']];n['gaps_current']='No live count admission, exact outstanding Senate-vote quantity, measured changing live cadence or approved historical/current native join.';priorities.append(n)
writejson(ROOT/'authority-inventory.json',inv);writejson(ROOT/'priority-investigations.json',priorities)
# Preserve contract authority plus exact read-only source references, no peer aggregate dependency.
refs=json.loads((ROOT/'original-references.json').read_text());known={x['path'] for x in refs}
paths=['data/turnout/priority-set.json','data/coordinator-priority-acceptance.json','data/coordinator-native-contract-review.json','data/news/sos-2020-canvass-original.html.gz','data/news/sos-2024-canvass-detail.html.gz','data/news/sos-november-observed201.html.gz','data/baselines/source/current-ballot.json','data/coordinator-current-ballot-visual-review.json','data/baselines/source/delano-general-ballot-2026.body.gz','data/baselines/source/westonka-general-ballot-2026.body.gz','data/baselines/source/delano-general-ballot-2026-page1.png']
for path in paths:
 if path in known:continue
 p=STATE/path;b=p.read_bytes();v={'path':path,'stored_bytes':len(b),'stored_sha256':hashlib.sha256(b).hexdigest(),'role':'read-only original/contract/current-ballot authority; no mutable peer aggregate input'}
 if path.endswith('.gz'):
  raw=gzip.decompress(b);v.update(raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest())
 refs.append(v)
writejson(ROOT/'input-pins.json',refs)
# New GET records combined without collapsing observation vintages.
metas=[json.loads(f.read_text()) for f in sorted((ROOT/'raw').glob('*.meta.json'))];writejson(ROOT/'acquisition.json',metas)
web=[]
for p in sorted(ROOT.glob('web-*.json')):web.append({'path':p.name,'capture_completed_file_mtime_utc':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),'retrieval_utc':'not exposed by web tool; completion time retained, not substituted for source retrieval','scope':'exact tool-returned text, provider line positions/ref chains; not original HTTP entity or its headers'})
writejson(ROOT/'web-observation-ledger.json',web)
# CSV all87, ordered by contract, exact depth not inflated.
columns=['rank','county','county_fips','historical_source_county_id','priority','senate2024_votes','native2024','native2022','native2020','authority_directory_url','directory_website','direct_root_status','election_results_urls_observed','discovery_depth','test201_precinct_count','current_count_feed_configured','candidate_method_rows','exact_outstanding_senate_votes','cadence','full_context_locator','evidence_ids','gaps']
with (STATE/'data/official-results-sources.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
 for c in inv:
  root=next(x for x in c['evidence'] if x['id'].endswith('-root'));links=list(dict.fromkeys(x['url'] for x in c['observed_results_links']));gap=notes[c['name']]['gap'] if c['in_priority'] else 'Local detailed feed not deeply investigated; no guaranteed cadence/current-ID/method or outstanding approval.'
  if c['name']=='Kittson':gap+=' Separately fetched2024pctstats differs from workbook in56fields; netTOTVOTING-172 retained without baseline edit.'
  w.writerow(dict(zip(columns,[c['rank'],c['name'],c['county_fips'],c['source_county_code'],str(c['in_priority']).lower(),c['historical_votes_2024'],*[c['native_counts'][str(y)] for y in [2024,2022,2020]],'https://www.sos.mn.gov/elections-voting/find-county-election-office/',c['directory']['website'],root['status'],' | '.join(links),c['depth'],c['test201_precinct_table_count'],'false','unavailable in inspected Senate flatfiles/workbooks','','not measured','county-native-contexts.jsonl.gz line '+str(c['rank']),' | '.join(x['id'] for x in c['evidence']),gap])))
# Render report-owned appendix, used by complete report.
parts=[]
for n in priorities:
 c=inv[n['rank']-1];parts.append(f"### {n['rank']}. {n['name']} — {n['county_fips']}\n\n")
 parts.append(f"Historical2024 Senate **{n['historical_votes_2024']:,}** votes; native rows2024/2022/2020 **{n['native_counts']['2024']}/{n['native_counts']['2022']}/{n['native_counts']['2020']}**. Source county code `{n['source_county_code']}` is separate from FIPS. The201 **test** county table has{n['test201_precinct_table_count']} precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line{n['rank']}; all source cells at `native-<year>.jsonl.gz`.\n\n")
 parts.append(n['finding']+'\n\n')
 urls=[f"[{x['id']}]({x['requested_url']}) ({x.get('status')}, {x.get('entity_check')})" for x in n['source_records']];parts.append('Evidence: '+'; '.join(urls)+'. Full parent/position/redirect/clock records: [individual investigation](priority-investigations.json).\n\n')
 exceptions=[x for x in n['late_opening_rows'] if x['general_opening_local']]
 if exceptions:parts.append('November late-opening rows: '+ '; '.join(x['precinct_name']+' '+x['general_opening_local']+f" (sheet row{x['source_row']})" for x in exceptions)+'. All close20:00 local subject to statutory in-line/relocation provisions.\n\n')
 else:parts.append('No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.\n\n')
 parts.append('Gap: '+n['gap']+'\n\n')
(ROOT/'priority-appendix.md').write_text(''.join(parts))
print('built87CSV/24records; inputpins',len(refs),'GETobservations',len(metas))
