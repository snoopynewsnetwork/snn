#!/usr/bin/env python3
"""Source-scoped write-in/identity audit and incomplete-scope priority sensitivity.
Never treats generic marks as eligible candidates or missing generic fields as observed0.
"""
import sys
sys.dont_write_bytecode=True
from extract import BASE,DATA,Originals,pdftext,jsonl,dump,sha
import csv,gzip,io,json,re,math
def jl(p):return [json.loads(x)for x in gzip.decompress(p.read_bytes()).splitlines()]
def main():
 tables=json.loads((BASE/'extracts/state-controls.json').read_text());native=jl(BASE/'extracts/native-special.jsonl.gz');scans=jl(BASE/'extracts/independent-scan-contexts.jsonl.gz');summaries=[];o=Originals()
 for county in ['nemaha','clay','nance','gosper']:
  pages=jl(BASE/f'extracts/extra-{county}-pages.jsonl.gz')
  for page in pages:
   text=page['text'];hh=list(re.finditer(r'^\s*US (President|Senator [26] YR)\s*$',text,re.M))
   for i,h in enumerate(hh):
    block=text[h.end():hh[i+1].start()if i+1<len(hh)else len(text)];block=re.split(r'Congress Dist\.',block)[0];f={};rawrows=[]
    for ln,line in enumerate(block.splitlines(),1):
     m=re.fullmatch(r'\s*(.*?)\s{2,}(\d[\d,]*(?:\s+\d[\d,]*)*)\s*',line)
     if m:
      values=[int(v.replace(',',''))for v in m[2].split()]
      if len(values)in[1,4]and m[1].strip()not in['Vote For']:f[m[1].strip()]=values;rawrows.append(dict(line_in_block=ln,raw_line=line,label=m[1].strip(),values=values))
    summaries.append(dict(source_id=page['source_id'],county=county.title(),page=page['page'],contest=h[0].strip(),fields=f,original_rows=rawrows,kind='county_summary',label=None))
 assert len(summaries)==12;jsonl('extracts/extra-text-summary-contexts.jsonl.gz',summaries)
 mapping={'US President':'president2024','US Senator 6 YR':'senate2024regular','US Senator 2 YR':'senate2024special'}
 cand={'US President':['Rep Trump/Vance','Dem Harris/Walz','Lib Oliver/ter Maat','Lmn West/Abdullah','Pet Stein/Kpadenou','Write-In Totals'],'US Senator 6 YR':['Rep Deb Fischer','Pet Dan Osborn','Write-In Totals'],'US Senator 2 YR':['Rep Pete Ricketts','Dem Preston Love Jr.','Write-In Totals']}
 allrows=scans+summaries;methodcells=0
 for r in allrows:
  f=r['fields'];required=cand[r['contest']];assert all(n in f and f[n]is not None for n in required),(r['county'],r['page'],r['contest'],f)
  for v in f.values():
   assert v is not None
   if len(v)==4 and all(n is not None for n in v):assert v[0]==sum(v[1:]),(r,v)
   methodcells+=len(v)
  for j in range(len(next(iter(f.values())))):
   if not all(f[n][j]is not None for n in required):continue
   candidate_sum=sum(f[n][j]for n in required)
   if 'Total Votes Cast'in f:assert candidate_sum==f['Total Votes Cast'][j],(r['county'],r['page'],r['contest'],j)
   if 'Contest Totals'in f:assert candidate_sum+f['Overvotes'][j]+f['Undervotes'][j]==f['Contest Totals'][j]
  if 'Not Assigned'in f:assert f['Not Assigned']==f['Write-In Totals']
 # Source rows, not a join between alternate native IDs.
 for county in ['York','Garfield','Deuel','Nemaha','Clay','Nance','Gosper']:
  for label,contest in mapping.items():
   selected=[r for r in allrows if r['county'].title()==county and r['contest']==label]
   values=[sum(r['fields'][n][0]for r in selected)for n in cand[label]]
   if contest=='senate2024special':values=values[:2]
   assert values==tables[contest]['county'][county],(county,label,values)
 generic={c:sum(r['fields']['Write-In Totals'][0]for r in allrows if r['county'].title()==c and r['contest']=='US Senator 2 YR')for c in ['York','Garfield','Deuel','Nemaha','Clay','Nance','Gosper']}
 generic.update({c:sum(r['generic_writeins']for r in native if r['county']==c)for c in ['Douglas','Lancaster']})
 assert generic=={'York':12,'Garfield':2,'Deuel':0,'Nemaha':10,'Clay':8,'Nance':5,'Gosper':2,'Douglas':701,'Lancaster':377}
 assert sum(generic.values())==1117
 registration_controls=[]
 for c in ['nemaha','clay','nance','gosper']:
  p=jl(BASE/f'extracts/extra-{c}-pages.jsonl.gz')[0];line=next(x for x in p['text'].splitlines()if 'Registered Voters - Total'in x)
  local=int(re.search(r'(\d[\d,]*)\s*$',line)[1].replace(',',''));state=tables['registration2024']['county'][c.title()][-1]
  registration_controls.append(dict(county=c.title(),source_id=p['source_id'],page=1,local_registered=local,state_canvass_registered=state,difference=local-state,raw_line=line,scope='Local county summary versus separate state canvass; common status/snapshot date unproved'))
 local=sum(s['registered']for s in json.loads((BASE/'extracts/lancaster-statistics.json').read_text()));state=tables['registration2024']['county']['Lancaster'][-1]
 registration_controls.append(dict(county='Lancaster',source_id='county-lancaster-2024-final-precinct-pdf-actual-archive',local_registered=local,state_canvass_registered=state,difference=local-state,scope='Sum199native statistics, resident registered0; no unproved cross-source equality imposed'))
 registration_controls.append(dict(county='Deuel',source_id='sos-2024-county-deuel-indexed-unofficial',page=1,local_registered=1412,state_canvass_registered=tables['registration2024']['county']['Deuel'][-1],difference=1412-tables['registration2024']['county']['Deuel'][-1],scope='Original rotated fullpage manually read,1412; unofficial summary versus state canvass'))
 dump('extracts/registration-source-disagreements.json',dict(observations=registration_controls,allocation=None,common_status_date_established=False,county_ballots_agree=True))
 # Independently compare local PDF named/generic fields with all five BIFF tables.
 dc=jl(BASE/'extracts/douglas-native-contexts.jsonl.gz');douglas_checks=[];volume_disagreements=[]
 configs=[(2024,'senate2024special','For United States Senator Two-Year Term',['Pete Ricketts','Preston Love Jr.','Write-In Totals']),
  (2024,'senate2024regular','For United States Senator',['Deb Fischer','Dan Osborn','Write-In Totals']),
  (2024,'president2024','For President And Vice President Of The United States',['Donald J. Trump','Kamala D. Harris','Chase Oliver','Cornel West','Jill Stein','Write-In Totals']),
  (2022,'governor2022','For Governor',['Jim Pillen','Carol Blood','Scott Zimmerman','Write-In Totals']),
  (2020,'senate2020','For United States Senator',['Ben Sasse','Chris Janicek','Gene Siadek','Preston Love, Jr.','Not Assigned'])]
 for y,contest,section,names in configs:
  pages=jl(BASE/f'extracts/douglas-{y}-summary-pages.jsonl.gz');text='\n'.join(p['text']for p in pages)
  m=re.search(r'^\s*'+re.escape(section)+r'\s*$',text,re.M);assert m;block=re.split(r'^\s*For ',text[m.end():],maxsplit=1,flags=re.M)[0]
  values=[];rawlines=[]
  for name in names:
   found=[line for line in block.splitlines()if re.match(r'^\s*'+re.escape(name)+r'(?:\s|\()',line)];assert len(found)==1,(contest,name)
   v=int(re.search(r'(\d[\d,]*)\s*$',found[0])[1].replace(',',''));values.append(v);rawlines.append(found[0])
  chosen=[r for r in dc if r['contest']==contest];actual=[sum(r['candidate_counts'][i]for r in chosen)for i in range(len(names))];assert values==actual
  if y==2020:
   parent=int(re.search(r'Write-In Totals\s+(\d[\d,]*)',block)[1].replace(',',''));assert parent==values[-1]+values[-2]==29275
  ballots=int(re.search(r'Ballots Cast - Total\s+(\d[\d,]*)',text)[1].replace(',',''));reconstructed=sum(r['ballot_reconstruction']for r in chosen)
  douglas_checks.append(dict(year=y,contest=contest,PDF_candidate_values=values,BIFF_candidate_sums=actual,PDF_raw_lines=rawlines))
  state_ballots=tables[f'votingmethod{y}']['county']['Douglas'][-1]
  volume_disagreements.append(dict(year=y,contest=contest,PDF_ballots=ballots,state_canvass_TotalVoting=state_ballots,PDF_minus_state=ballots-state_ballots,BIFF_total_votes_plus_over_plus_under=reconstructed,difference=reconstructed-ballots,BIFF_minus_state=reconstructed-state_ballots,allocation=None))
 dump('extracts/douglas-summary-controls.json',dict(candidate_fields_checked=sum(len(r['PDF_candidate_values'])for r in douglas_checks),candidate_checks=douglas_checks,source_volume_observations=volume_disagreements))
 exports=[]
 for sid in ['sos-2024-observed-public-all-csv-archive','sos-2024-observed-public-statewide-csv-archive']:
  data=list(csv.reader(io.StringIO(o.get(sid).decode('utf-8-sig'))));header=data[0];assert len(header)==15
  for n,row in enumerate(data[1:],2):
   assert len(row)==16 and row[-1]==''
   if row[0]in ['12464','12246']:
    exports.append(dict(source_id=sid,source_row=n,header=header,original_cells=row,record=dict(zip(header,row[:15])),unheaded_final_cell=row[15]))
 jsonl('extracts/historical-Senate-export-rows.jsonl.gz',exports)
 source_names=[]
 for row in json.loads((BASE/'source/acquisition.json').read_text()):
  if row['id'].startswith('historical-lists'):
   raw=gzip.decompress((BASE/row['asset']).read_bytes());text=pdftext(raw);jsonl('extracts/'+row['id']+'-pages.jsonl.gz',[dict(page=i+1,text=p)for i,p in enumerate(text.split('\f')[:-1])]);source_names.append(dict(id=row['id'],raw_sha256=sha(raw),Senate_header_count=text.count('For United States Senator'),source_clock=text.splitlines()[:3]))
 known=[r for r in native if r['generic_writeins']is not None];assert len(known)==431 and sum(r['generic_writeins']for r in known)==1078
 sensitivity=[dict(key=r['key'],named=r['pair_votes'],generic_observed=r['generic_writeins'],conditional_volume=r['pair_votes']+(r['generic_writeins']if r['generic_writeins']is not None else 0))for r in native]
 sensitivity.sort(key=lambda x:(-x['conditional_volume'],x['key']));D=sum(r['conditional_volume']for r in sensitivity);cum=0
 for i,r in enumerate(sensitivity,1):
  cum+=r['conditional_volume']
  if cum*5>=D*4:break
 assert(i,cum,D)==(765,749234,936083)
 old={r['key']for r in native if r['priority']};new={r['key']for r in sensitivity[:i]}
 bound=dict(extra_eligible_outside_fixed765_to_drop_below80=math.floor(748190/.8-935005)+1,extra_eligible_inside_fixed764_to_reach80=4*935005-5*747645,
  coarse_ballot_capacity=965236-935005,scope='Conditional algebra only; unknown generic/eligible marks not allocated; coarse capacity also includes under/over/blank and non-Senate eligibility')
 assert bound['extra_eligible_outside_fixed765_to_drop_below80']==233 and bound['extra_eligible_inside_fixed764_to_reach80']==1795
 result=dict(current_final_roster=json.loads((BASE/'extracts/current-final-roster.json').read_text()),historical_candidate_lists=source_names,
  local_generic_special_marks=generic,nine_county_total=1117,selected_native_observed_generic_contexts=431,selected_native_observed_generic_marks=1078,selected_native_unknown_generic_contexts=895,
  statewide_generic_total=None,statewide_eligible_named_writein_total=None,
  bounds=bound,partial_generic_sensitivity=dict(conditional_denominator=D,minimum_count=i,priority_votes=cum,removed=sorted(old-new),added=sorted(new-old),crossing=sensitivity[i-1],
   assumption='Add observed generic marks in Douglas/Lancaster; assume no extra marks in895unavailable HTML contexts solely for this sensitivity, not a zero observation, legal denominator, or candidate allocation',
   primary_membership_proven_robust=False,full_order=sensitivity),
  scan_contexts=46,text_summary_contexts=12,additional_count_fields_checked=methodcells,source_references=list(o.used.values()))
 dump('candidate-universe.json',result)
 # Independent peer QA only after original extraction above.
 peerpath=DATA/'turnout/extracts/candidate-universe.json';peer=json.loads(peerpath.read_text())
 assert peer['local_special_generic_writein_marks_nine_counties']==1117 and peer['source_native_missing_generic_contexts']==895 and peer['selected_source_native_observed_generic_contexts']==431
 assert {k:v['generic_writein_marks']for k,v in peer['local_special_generic_writein_observations'].items()}==generic
 assert {r['candidate']:r['party_literal']for r in result['current_final_roster']['rows']}=={r['name']:r['party_printed']for r in peer['current_final_roster']}
 assert peer['current_list_raw_sha256']=='d27a071715896b8c82b8cce8d48200b4207ba10c44f1778f56f92c4efcd7cf96'
 ownexport={(r['source_id'],r['source_row']):r for r in exports}
 for publication in peer['historical_public_Senate_exports']:
  for r in publication['Senate_rows']:
   own=ownexport[(publication['source_id'],r['source_row_1based'])]
   assert own['record']==r['fields']and own['header']==publication['header']and own['unheaded_final_cell']==r['unheaded_trailing_field']
 pb=peer['writein_bounds'];assert pb['conditional_extra_eligible_outside_fixed765_to_drop_below80']==233 and pb['conditional_extra_eligible_inside_fixed764_to_reach80']==1795 and pb['coarse_additional_ballot_capacity_upper_bound']==30231 and not pb['membership_robustness_established']
 ps=peer['incomplete_observed_generic_sensitivity'];assert(ps['named_plus_available_generic_sum'],ps['minimum80_count'],ps['minimum80_votes'])==(D,i,cum)
 assert set(ps['priority_key_symmetric_difference'])==old^new and ps['crossing_key']==sensitivity[i-1]['key']
 pm={'US President':'2024-president','US Senator 6 YR':'2024-senate-regular','US Senator 2 YR':'2024-senate-special'}
 peer_scans=jl(DATA/'turnout/extracts/scan-verified-contexts.jsonl.gz');ownidx={(r['county'].title(),r['page'],pm[r['contest']]):r for r in scans}
 for p in peer_scans:
  r=ownidx[(p['county'],p['actual_pdf_page'],p['contest'])];assert r['fields']=={f['label_literal']:f['counts']for f in p['fields']}
 dump('universe-peer-QA.json',dict(status='pass',peer_path=str(peerpath.relative_to(DATA.parent)),peer_sha256=sha(peerpath.read_bytes()),own_universe_sha256=sha((BASE/'candidate-universe.json').read_bytes()),nine_county_generic=generic,
  checks=['46 independently rendered/OCR/manual scan contexts all candidate/method cells match peer; all21 local county/contest vectors close canvass','12 fourcounty text summary contexts close canvass','431observed generic1078;895unknown','partial sensitivity exact765/749234/936083 and sourcekeyswap','233outside/1795inside algebra;30231coarsecapacity','five final primary roster identities and historical sourceID/PartyCode preserved separately'],
  qualification='Complete named-scope historical arithmetic; legal generic/writein universe and native priority membership robustness remain unproved. Coordinator acceptance false.'))
 print(json.dumps(dict(scan_contexts=46,text_contexts=12,generic9=sum(generic.values()),methodcells=methodcells,peer_QA='pass')))
if __name__=='__main__':main()
