#!/usr/bin/env python3
"""Independently parse newly recovered historical Senate native export originals."""
import csv,json
from extract import BASE,SRC,PEER,original,workbook,values,gz,js,csvout
def main():
 fips=json.loads((SRC/'county-identities.json').read_text());counties=list(csv.DictReader((BASE.parent/'county-baselines.csv').open()));books={};proof={};all_diff=[];receipts=[]
 for year in [2022,2020]:
  key=f'public-native-senate-{year}';a=json.loads((PEER/(key+'.receipt.json')).read_text());receipts.append(a);book=workbook(original(a,PEER));books[key]=book
  rows=[];footers=[];cols='CDE'if year==2022 else'CD';vote_keys=['a_votes','lesnar_lib','b_votes']if year==2022 else['b_votes','a_votes']
  for s in book['sheets']:
   name=s['name'];rr={r['row']:r for r in s['rows']};h=values(rr[7]);footer=next(r for r in s['rows']if values(r).get('B')=='TOTALS');local=[]
   assert values(rr[1])['A']==f'{year} Unofficial General Election Results'
   assert ('Bengs' in h['C'] and 'Lesnar'in h['D'] and 'Thune'in h['E'])if year==2022 else('Rounds'in h['C'] and 'Ahlers'in h['D'])
   for r in s['rows']:
    if not 7<r['row']<footer['row']:continue
    v=values(r);counts=[int(v[c])for c in cols];mapped=dict(zip(vote_keys,counts));A=mapped['a_votes'];B=mapped['b_votes'];O=mapped.get('lesnar_lib',0);total=sum(counts)
    row=dict(native_key=f"sd:{year}:senate:{fips[name]}:sheet{s['ordinal']}:row{r['row']}",year=year,contest='Senate',county=name,county_fips=fips[name],sheet=s['ordinal'],sheet_member=s['member'],source_row=r['row'],native_label=v['B'],official_native_id='',method_label='literal_absentee_unit'if 'absentee'in v['B'].lower()else'not_separately_identified',a_votes=A,b_votes=B,other_named_votes=O,pair_votes=A+B,all_named_votes=total,pair_participation=(A+B)/total if total else '',a_pair_share=A/(A+B)if A+B else'',source_id=key,raw_source_sha256=a['raw_sha256'],source_status='published_unofficial',blank_votes='',undervotes='',overvotes='',ballots_cast='',registered_voters='')
    if year==2022:row['lesnar_lib']=O
    rows.append(row);local.append(row)
   footercounts=[int(values(footer)[c])for c in cols];assert footercounts==[sum(r[k]for r in local)for k in vote_keys]
   signed=next(r for r in counties if int(r['year'])==year and r['county']==name);expected={'a_votes':int(signed['a_votes']),'b_votes':int(signed['b_votes']),'lesnar_lib':int(signed['other_named_votes'])}
   diffs=[footercounts[j]-expected[k]for j,k in enumerate(vote_keys)]
   footers.append(dict(county=name,header_literals=h,footer=footercounts,source_footer_row=footer['row'],signed=[expected[k]for k in vote_keys],difference=diffs,native_rows=len(local),headings=[values(rr[i])for i in range(1,8)if i in rr]))
   for k,v in zip(vote_keys,diffs):all_diff.append(dict(year=year,county=name,candidate_column=k,public_minus_signed=v,source_id=key))
  assert len(book['sheets'])==66 and len({r['county']for r in rows})==66
  csvout(BASE/f'native-{year}-public.csv',rows);js(SRC/f'native-{year}-public-footers.json',footers)
  proof[str(year)]=dict(source_id=key,raw_sha256=a['raw_sha256'],native_rows=len(rows),county_parents=66,candidate_columns=[h[c]for c in cols],candidate_totals=[sum(r[k]for r in rows)for k in vote_keys],candidate_totals_minus_signed=[sum(c['difference'][j]for c in footers)for j in range(len(cols))],counties_with_disagreement=[c['county']for c in footers if any(c['difference'])])
 gz(SRC/'senate-public-workbooks-complete-cells.json.gz',books);js(SRC/'senate-public-controls.json',proof);js(SRC/'senate-public-original-receipts.json',receipts);csvout(BASE/'public-senate-signed-differences.csv',all_diff);print(json.dumps(proof))
if __name__=='__main__':main()
