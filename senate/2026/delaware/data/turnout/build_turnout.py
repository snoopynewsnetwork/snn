#!/usr/bin/env python3
"""Build disjoint historical ranks, full native priority contract and scoped sensitivities."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,gzip,csv,collections,hashlib,re
from decimal import Decimal
from extract import clean
D=Path(__file__).resolve().parent;X=D/'extracts';ROOT=D.parent.parent
FIPS={'KENT':'10001','NEW CASTLE':'10003','SUSSEX':'10005'}
def load(n):return json.loads((X/n).read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def pc(n,d):return f'{Decimal(n)*100/Decimal(d):.10f}'
def output_csv(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def rank(volumes):
 ordered=sorted(volumes,key=lambda k:(-volumes[k],k));total=sum(volumes.values());cum=0;full=[];cut=None
 for i,k in enumerate(ordered,1):
  prev=cum;cum+=volumes[k];full.append({'rank':i,'native_key':k,'votes':volumes[k],'cumulative_votes':cum,'share_fraction':[volumes[k],total],'cumulative_share_fraction':[cum,total]})
  if cut is None and 5*cum>=4*total:cut=i
 assert cut is not None
 return {'total':total,'unit_count':len(ordered),'top15_votes':sum(volumes[k] for k in ordered[:15]),'top15_share_fraction':[sum(volumes[k] for k in ordered[:15]),total],'minimum80_count':cut,'preceding_count':cut-1,'preceding_votes':sum(volumes[k] for k in ordered[:cut-1]),'crossing_key':ordered[cut-1],'crossing_votes':volumes[ordered[cut-1]],'priority_votes':sum(volumes[k] for k in ordered[:cut]),'remainder_count':len(ordered)-cut,'remainder_votes':sum(volumes[k] for k in ordered[cut:]),'ordered_priority_keys':ordered[:max(cut,min(15,len(ordered)))],'ordered_top15_keys':ordered[:15],'ordered_remainder_keys':ordered[cut:],'full_order':full}
def main():
 rows=[json.loads(l) for l in gzip.decompress((X/'candidate-rows.jsonl.gz').read_bytes()).splitlines()];inv=load('native-inventory.json');hier=load('historical-hierarchy.json');participation=load('participation-totals.json');monthly=load('registration-november.json');wi=load('writein-rows.json')
 hi={(r['year'],r['native_key']):r for r in hier};edinv={(y['year'],k):v for y in inv for k,v in y['election_districts'].items()};parents={}
 for (year,key),ed in edinv.items():
  p=hi.get((year,key));county=p['county'] if p else ed['county'].upper() if ed['county'] else None
  if p and ed['county']:assert ed['county'].upper()==p['county']
  parents[(year,key)]={'county':county,'county_fips':FIPS.get(county),'source_id':p['source_id'] if p else ed['source_id'],'source_line':p['source_line'] if p else None,'evidence':'explicit county/RD/ED nesting in participation report' if p else ed['county_scope'],'rd':p['rd'] if p else None,'ed':p['ed'] if p else None}
 # Actual structure table: explicit rows and footnotes. Not a geometry crosswalk.
 structure={};page=1
 for li,line in enumerate((D/'source/district-structure.txt').read_text().splitlines(),1):
  m=re.match(r'^\s*(KENT|NEW CASTLE|SUSSEX)\s+(\d{2})-(\d{2})([12]?)\s+(\d{2})\b(.*)',line)
  if m:
   c,rd,ed,note,rdcol,tail=m.groups();assert rd==rdcol
   key='ElectionDistrict'+rd+ed;assert key not in structure
   structure[key]={'native_key':key,'county':c,'county_fips':FIPS[c],'rd':rd,'ed':ed,'footnote':note or None,'source_line':li,'raw_line':line,'kind':'statutory administrative district' if note else 'election district; physical polling-site equivalence unverified','statutory_reference':{'1':'15 Del. C. §1901(b)(3)','2':'42 U.S.C. §1973aa-1'}.get(note),'source_id':'district-structure','source_vintage':'Last Updated 2/13/2024; printed 2022 through 2032 title / note through 2030 General Election','geometry_approved':False}
 assert len(structure)==537
 for k,v in structure.items():
  if (2024,k) in parents:
   if parents[(2024,k)]['county']:assert parents[(2024,k)]['county']==v['county']
 # All candidate/method and all county controls, no county-range inference.
 county_controls=[];context_ranks=[];fullrank=[];method_ranks=[];native_coverage=[]
 for y,o in [(2024,'USSenator'),(2024,'PresidentandVicePresident'),(2022,'RepresentativeinCongress'),(2020,'USSenator'),(2020,'PresidentandVicePresident')]:
  rr=[r for r in rows if r['year']==y and r['office_key']==o];edr=[r for r in rr if r['view']=='byelectiondist'];vol=collections.Counter()
  for r in edr:vol[r['native_key']]+=r['numeric']['Total Votes']
  ranked=rank(vol);context_ranks.append({'year':y,'office_key':o,'scope':'report named candidates; separate WI not allocated to EDs',**ranked})
  for r in ranked['full_order']:fullrank.append({'year':y,'office_key':o,**r})
  for method in ['Machine Votes','Absentee Votes','Early Voting Votes']:
   if y==2020 and method=='Early Voting Votes':method_ranks.append({'year':y,'office_key':o,'method':method,'available':False,'reason':'column unprinted at native level; separate CSV prints statewide0'});continue
   mv=collections.Counter()
   for r in edr:mv[r['native_key']]+=r['numeric'][method]
   method_ranks.append({'year':y,'office_key':o,'method':method,'available':True,**rank(mv)})
  for r in rr:
   if r['view']!='bycounty':continue
   for c in ['New Castle','Kent','Sussex']:
    v=int(r['raw_fields'][c].replace(',',''));er=[a for a in edr if parents[(y,a['native_key'])]['county']==c.upper() and a['candidate']==r['candidate']]
    known=sum(a['numeric']['Total Votes'] for a in er);unknown=sum(a['numeric']['Total Votes'] for a in edr if parents[(y,a['native_key'])]['county'] is None and a['candidate']==r['candidate'])
    assert known<=v
    if unknown==0:assert known==v,(y,o,c,r['candidate'],known,v)
    county_controls.append({'year':y,'office_key':o,'county':c,'county_fips':FIPS[c.upper()],'candidate':r['candidate'],'party':r['party'],'reported_votes':v,'ed_sum_known_parent':known,'unallocated_statewide_candidate_votes':unknown,'county_method_scope':'native-derived only; county view prints no method columns','source_id':r['source_id'],'source_row_start':r['row_start']})
 primary=context_ranks[0];porder=[r['native_key'] for r in primary['full_order']];priority=set(primary['ordered_priority_keys']);pt={(r['year'],r['native_key']):r for r in participation if r['level']=='ed'};mr={(r['year'],r['native_key']):r for r in monthly}
 csvrows=[]
 for r in primary['full_order']:
  key=r['native_key'];pr=parents[(2024,key)];cr=[a for a in rows if a['year']==2024 and a['view']=='byelectiondist' and a['office_key']=='USSenator' and a['native_key']==key];assert len(cr)==3
  p=pt.get((2024,key));m=mr.get((2024,key));st=structure.get(key)
  a={'rank':r['rank'],'state':'DE','year':2024,'election_date':'2024-11-05','office_key':'USSenator','native_key':key,'native_label':cr[0]['native_name'],'county':pr['county'],'county_fips':pr['county_fips'],'rd':pr['rd'],'ed':pr['ed'],'unit_kind':st['kind'] if st else 'unavailable','senate_candidate_votes':r['votes'],'blunt_rochester':next(a['numeric']['Total Votes'] for a in cr if a['candidate']=='LISA BLUNT ROCHESTER'),'hansen':next(a['numeric']['Total Votes'] for a in cr if a['candidate']=='ERIC HANSEN'),'katz':next(a['numeric']['Total Votes'] for a in cr if a['candidate']=='MICHAEL "DR. MIKE" KATZ'),'machine_candidate_votes':sum(a['numeric']['Machine Votes'] for a in cr),'absentee_candidate_votes':sum(a['numeric']['Absentee Votes'] for a in cr),'early_candidate_votes':sum(a['numeric']['Early Voting Votes'] for a in cr),'generic_writein_votes':None,'blank_ballots':None,'undervotes':None,'overvotes':None,'ballots_cast':None,'participation_voted_2024':p['values']['Total']['voted'] if p else None,'participation_registered_2024':p['values']['Total']['registered'] if p else None,'nov1_registered_2024':m['registered'] if m else None,'state_share_percent':pc(r['votes'],primary['total']),'cumulative_votes':r['cumulative_votes'],'cumulative_percent':pc(r['cumulative_votes'],primary['total']),'top15':r['rank']<=15,'minimum80':r['rank']<=primary['minimum80_count'],'priority':key in priority,'source_id':cr[0]['source_id'],'source_heading_start':cr[0]['heading_start'],'county_evidence_source':pr['source_id'],'county_evidence_line':pr['source_line']}
  csvrows.append(a)
 output_csv(D.parent/'county-turnout.csv',csvrows)
 # Complete all-year identities across candidate reports and separate registration/participation universes.
 constituents=[];unavailable=[]
 for year in [2024,2022,2020]:
  yinv=next(v for v in inv if v['year']==year)
  keys=sorted(set(yinv['election_districts'])|{r['native_key'] for r in hier if r['year']==year}|{r['native_key'] for r in monthly if r['year']==year})
  for key in keys:
   e=edinv.get((year,key));p=hi.get((year,key));m=mr.get((year,key));parent=parents.get((year,key))
   if parent is None and p:parent={'county':p['county'],'county_fips':p['county_fips'],'source_id':p['source_id'],'source_line':p['source_line'],'rd':p['rd'],'ed':p['ed'],'evidence':'explicit county/RD/ED nesting'}
   record={'key':f'DE|{year}|{key}','year':year,'native_key':key,'report_offices':e['offices'] if e else [],'report_present':e is not None,'participation_present':p is not None,'november_registration_present':m is not None,'parent':parent,'structure_2024':structure.get(key) if year==2024 else None,'senate_2024_present':year==2024 and key in porder,'senate_2024_rank':porder.index(key)+1 if year==2024 and key in porder else None,'priority':year==2024 and key in priority,'scope':'same-year literal source key; cross-source count/registration definitions retained; no cross-year or current geometry equivalence'}
   constituents.append(record)
   if parent is None or parent['county'] is None or (year==2024 and key not in porder):unavailable.append(record)
 county_ranks=[]
 for y,o in [(2024,'USSenator'),(2024,'PresidentandVicePresident'),(2022,'RepresentativeinCongress'),(2020,'USSenator'),(2020,'PresidentandVicePresident')]:
  cv=collections.Counter()
  for a in county_controls:
   if a['year']==y and a['office_key']==o:cv[a['county']]+=a['reported_votes']
  county_ranks.append({'year':y,'office_key':o,'scope':'report named candidates, inclusive county view; WI separate',**rank(cv)})
 # Same-year alternative participation/registration ranks; all units kept.
 sensitivity=[]
 for y in [2024,2022,2020]:
  for field in ['registered','voted']:
   volumes={r['native_key']:r['values']['Total'][field] for r in participation if r['year']==y and r['level']=='ed'}
   sensitivity.append({'year':y,'measure':f'participation_report_{field}','scope':'source i.Total; not candidate votes; extract registration status/date unspecified',**rank(volumes)})
  pres=[r for r in participation if r['year']==y and r['level']=='state'][0]
  yinv=next(v for v in inv if v['year']==y);source_text=gzip.decompress((D.parent/'news'/next(a['asset'] for a in json.loads((D/'source/original-inputs.json').read_text()) if a['id']==yinv['source_id'])).read_bytes()).decode('utf-8-sig')
  literal=re.search(r'([\d,]+)\s+of\s+([\d,]+)\s+Registered\s+Votes',clean(source_text));assert literal
  enr_v,enr_r=[int(x.replace(',','')) for x in literal.groups()]
  named=next(r['total'] for r in context_ranks if r['year']==y and r['office_key']==('USSenator' if y!=2022 else 'RepresentativeinCongress'))
  sensitivity.append({'year':y,'measure':'state_scope_comparison','results_report_voted_literal':enr_v,'results_report_registered_literal':enr_r,'results_report_clock':yinv['source_clock'],'participation_report_voted':pres['values']['Total']['voted'],'participation_report_registered':pres['values']['Total']['registered'],'voted_difference':enr_v-pres['values']['Total']['voted'],'registration_difference':enr_r-pres['values']['Total']['registered'],'named_priority_context_votes':named,'enr_voted_minus_named_context':enr_v-named,'ballots_cast':None,'blank':None,'under':None,'over':None,'scope':'literal results-header participation not relabeled exact cast-ballot count; difference not allocated to categories'})
 # No arbitrary ED allocation of separately published write-ins.
 wi_controls=[]
 for y,o in [(2024,'PresidentandVicePresident'),(2022,'RepresentativeinCongress'),(2020,'PresidentandVicePresident')]:
  wr=[r for r in wi if r['year']==y and r['office_key']==o];v=sum(r['values']['Grand Total'] for r in wr);named=next(r['total'] for r in context_ranks if r['year']==y and r['office_key']==o)
  wi_controls.append({'year':y,'office_key':o,'named_report_votes':named,'separate_named_writeins':v,'arithmetic_combined_context':named+v,'writein_rows':len(wr),'ed_allocation':None,'county_allocation':'printed county scope' if y==2024 else 'unavailable statewide only','blank_method_cells':'null, not invented0','generic_writeins':None})
  if y==2024:
   for c in FIPS:
    wc=[r for r in wr if r['county']==c];wi_controls.append({'year':y,'office_key':o,'county':c,'total':sum(r['values']['Grand Total'] for r in wc),'reported_method_cells_sums':{f:(sum(r['values'][f] for r in wc if r['values'][f] is not None) if any(r['values'][f] is not None for r in wc) else None) for f in ['Absentee','Early Voting','Machine','Provisional']},'method_scope':'sum of numeric printed cells; empty cells preserved per row; no generic0 or precinct allocation'})
 # Source-native hierarchy, not geographic permission. Composite source IDs kept separately.
 contract={'schema_version':'DE-turnout-priority-v1','state':'DE','election_date':'2024-11-05','contest':'U.S. Senator','contest_id':'USSenator','priority_basis':'sum of all three reported named Senate candidate rows per election district; no Senate declared-WI or WI-tally rows; generic writein/blank/under/over fields unavailable, not manufactured zeros','disjoint_level':'Election District; county/RD/Wilmington/state are overlapping controls','key_schema':'literal ElectionDistrictRR EE concatenation as printed; use DE|year|office_key|native_key for cross-year/contest storage','tie_break':'descending integer reported_candidate_votes; ascending literal native_key','status':'historical_primary_reconciled_peer_raw_and_all_five_full_orders_agree_coordinator_acceptance_pending','current_geography_approved':False,'complete_native_count':530,'county_count':3,**primary,'county_control_order':county_ranks[0],'county_native_hierarchy':{c:{'fips':f,'ordered_senate_native_keys':[k for k in porder if parents[(2024,k)]['county']==c]} for c,f in FIPS.items()},'administrative_cases':[v for v in structure.values() if v['footnote']],'all_available_source_constituents':constituents,'unavailable_administrative_cases':unavailable,'additional_native_sources':{'sample_ballot_index_2024':load('sample-ballot-identities.json')},'other_native_levels':{'representative_districts':{str(v['year']):v['representative_districts'] for v in inv},'county_control_rows_path':'extracts/county-controls.csv','county_alternative_views':'county New Castle inclusive; alternative Wilmington+Rest of New Castle partitions New Castle; never add both','central_reporting_identity':'No separately labeled central absentee/early board/polling-place identities in these report tables; methods are columns. Statutory special EDs explicit from structure; no polygons approved.'},'statistics_unavailable':['exact native ballots cast','generic/write-in category counts not printed in report','blank ballots','contest undervotes','contest overvotes','native provisional method outside separate named WI sheet','2020 native early-voting column absent','2020 president-only0218/3117/4117 county parent source unavailable'],'peer_agreement':{'original_extraction':'peer/reconciliation-v1.json','rank_comparison':'peer/rank-reconciliation.json','reciprocal_rank_agreement':True},'formal_coordinator_acceptance':False}
 save(D/'priority-set.json',contract);save(X/'historical-rankings.json',context_ranks);save(X/'method-rankings.json',method_ranks);save(X/'county-rankings.json',county_ranks);save(X/'participation-sensitivity.json',sensitivity);save(X/'writein-controls.json',wi_controls);save(X/'structure-2024.json',structure);save(X/'native-coverage.json',constituents);output_csv(X/'county-controls.csv',county_controls)
 # Canonical simple peer comparison order, independent of extended dispatch contract fields.
 stable={f"{r['year']}|{r['office_key']}":{'total':r['total'],'order':[[a['native_key'],a['votes']] for a in r['full_order']],'minimum80_count':r['minimum80_count'],'preceding_votes':r['preceding_votes'],'priority_votes':r['priority_votes'],'top15_votes':r['top15_votes']} for r in context_ranks};save(D/'stable-ranking-v1.json',stable)
 (D/'source/stable-ranking-v1.sha256').write_text(hashlib.sha256((D/'stable-ranking-v1.json').read_bytes()).hexdigest()+'  stable-ranking-v1.json\n')
 print(json.dumps({k:primary[k] for k in ['total','unit_count','top15_votes','minimum80_count','preceding_votes','crossing_key','crossing_votes','priority_votes','remainder_votes']}));print('stable sha256',hashlib.sha256((D/'stable-ranking-v1.json').read_bytes()).hexdigest())
if __name__=='__main__':main()
