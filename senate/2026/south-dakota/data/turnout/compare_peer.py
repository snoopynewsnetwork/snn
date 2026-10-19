#!/usr/bin/env python3
"""Read-only independent peer comparison with explicit semantic field mapping.
Never repairs either worker's output to match the other. Run after both freeze.
"""
import csv,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;B=D.parent/'baselines'
def read(p):return list(csv.DictReader(p.open()))
def pin(p):return {'path':str(p.relative_to(D.parent.parent)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 checks=[];differences=[];pins=[]
 def eq(label,a,b):
  ok=a==b;checks.append({'check':label,'pass':ok})
  if not ok:differences.append({'check':label,'own':a,'peer':b})
 def comparable(r,year,peer=False):
  # Row locator, not physical crosswalk. Public2024/22/20 sheets compare literal-native fields.
  common=(r['county'],r['county_fips'],int(r['sheet']if peer else r['sheet_ordinal']),r['sheet_member'],int(r['source_row']),r['native_label'])
  fields=(['harris_dem','oliver_lib','trump_rep','kennedy_ind']if year==2024 else['a_votes','lesnar_lib','b_votes']if peer and year==2022 else['bengs_dem','lesnar_lib','thune_rep']if year==2022 else['b_votes','a_votes']if peer else['rounds_rep','ahlers_dem'])
  return common+tuple(int(r[k])for k in fields)+(int(r['all_named_votes']if peer else r['contest_votes']),r['raw_source_sha256']if peer else r['source_sha256'])
 for y,ownname,peername in [(2024,'native-2024.csv','native-2024.csv'),(2022,'native-2022-public.csv','native-2022-public.csv'),(2020,'native-2020-public.csv','native-2020-public.csv')]:
  op=D/ownname;pp=B/peername;pins.extend([pin(op),pin(pp)]);a=read(op);b=read(pp)
  aa=sorted(comparable(r,y)for r in a);bb=sorted(comparable(r,y,True)for r in b);eq(f'{y} complete native county/FIPS/sheet/member/row/literal/counts/total/source-hash',aa,bb)
  eq(f'{y} complete source methods explicit absentee vs unspecified',sorted((r['county'],r['native_label'],r['native_label'].strip()in ('Absentee','Absentee Precinct'))for r in a),sorted((r['county'],r['native_label'],r['method_label']=='literal_absentee_unit')for r in b))
  eq(f'{y} unavailable ballot/registration/blank/under/over/nativeID retained null',all(not r.get(k)for r in a for k in ['ballots_cast','registered_voters','blank_ballots','undervotes','overvotes','official_native_numeric_id']),all(not r.get(k)for r in b for k in ['ballots_cast','registered_voters','blank_votes','undervotes','overvotes','official_native_id']))
  if y==2024:
   a.sort(key=lambda r:(-int(r['contest_votes']),r['county_fips'],int(r['sheet_ordinal']),int(r['source_row'])));b.sort(key=lambda r:(-int(r['all_named_votes']),r['county_fips'],int(r['sheet']),int(r['source_row'])))
   eq('2024 complete 691 descending keys',[r['key']for r in a],[r['native_key']for r in b]);cum=0
   for i,r in enumerate(b,1):
    cum+=int(r['all_named_votes'])
    if 5*cum>=4*sum(int(v['all_named_votes'])for v in b):break
   p=json.loads((D/'priority-set.json').read_text());eq('2024 exact minimum80 count/crossing/preceding/cumulative',[p['minimum80'][k]for k in ['count','crossing_key','preceding_votes','votes']],[i,r['native_key'],cum-int(r['all_named_votes']),cum]);eq('2024 ordered304 priority keys',p['ordered_priority_keys'],[r['native_key']for r in b[:i]])
 # Full signed counties/candidates, and source-specific ballot/registration controls.
 a=read(D/'county-sensitivities.csv');b=read(D.parent/'county-baselines.csv');pins.extend([pin(D/'county-sensitivities.csv'),pin(D.parent/'county-baselines.csv')]);bm={(r['year'],r['county_fips']):r for r in b}
 for r in a:
  q=bm[(str(r['year']),r['county_fips'])];y=int(r['year']);counts=json.loads(r['candidate_counts_in_source_order'])
  peer=[int(q['a_votes']),int(q['b_votes']),int(q['other_named_votes'])]
  own=[counts[0],counts[2],counts[1]+counts[3]]if y==2024 else[counts[0],counts[2],counts[1]]if y==2022 else[counts[1],counts[0],0]
  eq(f"{y} {r['county_fips']} full candidate vector and named balance",own+[int(r['contest_votes'])],peer+[int(q['all_named_votes'])])
  eq(f"{y} {r['county_fips']} ballot/turnout/active/inactive controls",[int(r[k])for k in ['votes_cast_book','turnout_table_registration','registration_table_total_active','registration_table_inactive']],[int(q[k])for k in ['votes_cast_source_label','turnout_table_registered','registration_active','registration_inactive']])
 # Full named minor candidates remain separate in signed county controls.
 cp=B/'county-candidates.csv';pins.append(pin(cp));pr=read(cp);ct=json.loads((D/'certified-controls.json').read_text());fp=json.loads((D/'county-fips.json').read_text())['counties'];vectors={}
 for r in pr:vectors.setdefault((r['year'],r['county']),[]).append(r)
 parties={'2024':['DEM','LIB','REP','IND'],'2022':['DEM','LIB','REP'],'2020':['REP','DEM']}
 for y,t in ct.items():
  for county,r in t['counties'].items():
   q=sorted(vectors[(y,county)],key=lambda r:int(r['printed_candidate_column']))
   eq(f'{y} {fp[county]} every printed candidate column/party/raw row',r['candidate_votes']+parties[y]+[r['literal_line']], [int(z['votes'])for z in q]+[z['ballot_party']for z in q]+[q[0]['raw_line']])
 # Signed2022 native PDF uses a bbox table-row locator; peer uses layout line locator.
 # Compare percounty source order, complete literal label and every candidate triple.
 op=D/'native-2022.csv';pp=B/'native-2022.csv';pins.extend([pin(op),pin(pp)]);a=read(op);b=read(pp)
 for county in sorted(set(r['county']for r in a)|set(r['county']for r in b)):
  aa=[(r['native_label'],int(r['bengs_dem']),int(r['lesnar_lib']),int(r['thune_rep']),int(r['source_pdf_page']))for r in a if r['county']==county]
  bb=[(r['native_label'],int(r['a_votes']),int(r['lesnar_lib']),int(r['b_votes']),int(r['pdf_page']))for r in b if r['county']==county]
  eq(f'2022 signedPDF {county} native-order labels/triples/page',aa,bb)
 eq('2022 signedPDF missingYankton preserved',not any(r['county']=='Yankton'for r in a),not any(r['county']=='Yankton'for r in b))
 result={'status':'pass'if all(c['pass']for c in checks)else'needs_reconciliation','actual_peer_id':'e6c0d1f7-5022-447d-9308-07988d70dad5','own_role':'turnout','peer_role':'partisanship','comparison_mode':'read-only independent originals-first outputs; no peer edits','checks':checks,'differences':differences,'pinned_inputs':pins,'scope':'All691/687/693publicnative rows;679signed2022native rows;198signedcounty vectors, every candidate preserved through explicit mapping; all198ballot/reg controls; methods/unavailable fields/full2024order/min80. Current geometry/legal approval and original2024/2020certified-nativeallocation remain unproved.'}
 (D/'peer-agreement.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':len(checks),'failed':[c['check']for c in checks if not c['pass']]}))
if __name__=='__main__':main()
