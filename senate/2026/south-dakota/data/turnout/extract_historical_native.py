#!/usr/bin/env python3
"""Independently decode all native Senate2020/2022 workbook cells and source controls.
Separate public vintages from signed county/precinct canvasses; never fill their gaps.
"""
from extract import *
def main():
 controls=json.loads((D/'certified-controls.json').read_text());fips=json.loads((D/'county-fips.json').read_text())['counties'];report={}
 for year,headers,cols,fields in [(2022,['Brian L. Bengs ','Tamara J Lesnar ','John R. Thune '],'CDE',['bengs_dem','lesnar_lib','thune_rep']),(2020,['Mike Rounds','Dan  Ahlers '],'CD',['rounds_rep','ahlers_dem'])]:
  sid=f'public-native-senate-{year}';w=book(sid,True);rows=[];parents=[]
  for s in w['sheets']:
   hr=next(r for r in s['rows']if values(r).get('B')=='Precinct');assert [values(hr)[c]for c in cols]==headers
   total=next(r for r in s['rows']if values(r).get('B')=='TOTALS');rr=[]
   for r in s['rows']:
    if not hr['row']<r['row']<total['row']:continue
    v=values(r);vv=[int(v[c])for c in cols];label=v['B'];row={'key':f"sd:{year}:senate:{fips[s['name']]}:public-sheet{s['ordinal']}:row{r['row']}",'county':s['name'],'county_fips':fips[s['name']],'sheet_ordinal':s['ordinal'],'sheet_member':s['member'],'source_row':r['row'],'native_label':label,**dict(zip(fields,vv)),'contest_votes':sum(vv),'official_native_numeric_id':None,'method_scope':'source_label_absentee_unsplit'if label.strip()in ('Absentee','Absentee Precinct')else 'unavailable_not_assumed_election_day','ballots_cast':None,'registered_voters':None,'blank_ballots':None,'undervotes':None,'overvotes':None,'source_id':sid,'source_sha256':w['source_sha256'],'status':'unofficial','source_cells':','.join(c+str(r['row'])for c in cols)};rows.append(row);rr.append(row)
   sums=[sum(r[k]for r in rr)for k in fields];footer=[int(values(total)[c])for c in cols];assert sums==footer
   certified=controls[str(year)]['counties'][s['name']]['candidate_votes'];parents.append({'county':s['name'],'county_fips':fips[s['name']],'source_rows':len(rr),'candidate_footer':footer,'certified_county_control':certified,'public_minus_certified':[x-y for x,y in zip(footer,certified)],'source_heading_rows':[values(r)for r in s['rows']if r['row']<=hr['row']]})
  assert len(parents)==66 and len(rows)==(687 if year==2022 else 693)
  csvout(f'native-{year}-public.csv',rows);gzjson(f'extracts/native{year}-public-complete-OOXML.json.gz',w)
  report[str(year)]={'source_id':sid,'source_sha256':w['source_sha256'],'native_rows':len(rows),'county_parents':66,'candidate_headers':headers,'candidate_fields':fields,'candidate_totals':[sum(r[k]for r in rows)for k in fields],'signed_candidate_controls':controls[str(year)]['candidate_controls'],'county_reconciliation':parents}
 dump('historical-public-native-reconciliation.json',report)
 print(json.dumps({y:{k:v for k,v in r.items()if k!='county_reconciliation'}for y,r in report.items()}))
if __name__=='__main__':main()
