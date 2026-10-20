#!/usr/bin/env python3
"""Finer source-only controls; no peer dependency."""
import json,gzip,re,collections
from extract_originals import D,E,save
def own(name):return json.loads(gzip.decompress((E/name).read_bytes()))
def main():
 b=own('bergen-required-rows.json.gz');m=own('morris-required-worksheets.json.gz');s=own('salem-required-dom.json.gz')
 # Fine aggregates are source scopes, not additions to the state municipal universe.
 summary={};bergen={}
 for scope in ['senate','president']:
  summaries=[r for r in b['rows'] if r['scope']==scope and r['method']=='Total' and not re.search(r'\d|Provisional|Federal|Grand|Total',r['native_label'],re.I)]
  sums={name:sum(r['candidate_values'][j] for r in summaries if type(r['candidate_values'][j]) is int) for j,name in enumerate(summaries[0]['candidates'])}
  bergen[scope]={'municipal_summary_rows':len(summaries),'numeric_only_candidate_sums':sums,'scope':'nonadditive municipal Total rows selected by literal absence of district digits/administrative labels; blank/protected cells remain unallocated','suppressed_rows':sum(any(isinstance(v,str) and '*' in v for v in r['candidate_values']) for r in b['rows'] if r['scope']==scope)}
 salem={}
 for contest in ['1','2']:
  sums=collections.defaultdict(int)
  for r in s:
   if r['native_contest_id']==contest:
    for a in r['candidates']:sums[a['literal_name']]+=a['votes']
  salem[contest]=dict(sums)
 mt=gzip.decompress((E/'morris-2024-8.layout.txt.gz').read_bytes()).decode();section=mt.split('UNITED STATES SENATE',1)[1].split('HOUSE OF REPRESENTATIVES',1)[0];generic_wi=int(re.search(r'Write-In Totals\s+([\d,]+)',section)[1].replace(',',''))
 summary={'Bergen':bergen,'Salem_DOM':salem,'Morris':{'worksheets':len(m),'source_native_admin_labels':['7TH CD STATE/FED','11TH CD STATE/FED','REMOVED RESIDENT'],'protected_cells':sum(c['value']=='protected' for sh in m for r in sh['rows'] for c in r['cells']),'generic_senate_write_in_from_summary_PDF':generic_wi,'summary_source':'morris-2024-8 page1; retained literal full page','generic_WI_is_not_statewide_eligible_allocation':True},'all_pdf_inventory':json.loads((E/'finer-pdf-inventory.json').read_text()),'limitations':['Raw protected/suppressed/wrapped PDF constituents are complete in original bytes/full layouts/required pages; no inferred values.','Atlantic/Morris/Sussex/Union/Salem finer PDFs are nonadditive overlapping page/method/statistic universes. Specialized complete legal eligible-WI allocation/current precinct roster not established.','Bergen numerical row comparison is Senate only; independent president row evidence also retained.','Own Morris ToC and Registered Voters sheets extend beyond peer candidate-sheet derivative, read directly from original OOXML.']}
 save(D/'finer-controls.json',summary);
if __name__=='__main__':main()
