#!/usr/bin/env python3
"""Independent turnout/registration extraction; source table differences remain."""
import csv,gzip,json,re
from extract import BASE,SRC,csvout,js
def main():
 fips=json.loads((SRC/'county-identities.json').read_text());out=[];regrows=[];summary={}
 for y,tp,rps in [(2024,23,[20,21]),(2022,25,[22,23]),(2020,15,[13])]:
  pp=gzip.decompress((SRC/f'returns-{y}-archive.txt.gz').read_bytes()).decode().split('\f');t=pp[tp-1]
  pattern=r'(?P<name>'+('|'.join(re.escape(s)for s in sorted(fips,key=len,reverse=True)))+r'|Lakota|TOTAL)\s+(?P<registered>[\d,]+)\s+(?P<votes>[\d,]+)\s+(?P<pct>[\d.]+)\s*%'
  local=[];footer=None
  for line,lit in enumerate(t.splitlines(),1):
   for m in re.finditer(pattern,lit):
    d=m.groupdict();name=d['name'];v=[int(d[s].replace(',',''))for s in ['registered','votes']]
    if name=='TOTAL':footer=v;continue
    if name=='Lakota':name='Oglala Lakota';assert re.search(r'Oglala\s*\n',t)
    local.append(dict(year=y,county=name,county_fips=fips[name],turnout_table_registered=v[0],votes_cast_source_label=v[1],turnout_percent_literal=d['pct'],turnout_pdf_page=tp,turnout_pdf_line=line,turnout_raw_line=lit,source_id=f'returns-{y}-archive'))
  assert len(local)==66 and len({r['county']for r in local})==66
  assert [sum(r[s]for r in local)for s in ['turnout_table_registered','votes_cast_source_label']]==footer
  rr=[]
  for p in rps:
   for line,lit in enumerate(pp[p-1].splitlines(),1):
    for name in sorted(fips,key=len,reverse=True):
     if not re.match(r'^\s*'+re.escape(name)+r'\s+\d',lit):continue
     nums=re.findall(r'[\d,]+',lit[len(lit)-len(lit.lstrip())+len(name):]);assert len(nums)>=2
     # Rightmost source columns are Inactive, Total Active. No blank party cell converted to zero.
     inactive,active=[int(s.replace(',',''))for s in nums[-2:]]
     rr.append(dict(year=y,county=name,registration_active=active,registration_inactive=inactive,registration_pdf_page=p,registration_pdf_line=line,registration_raw_line=lit,registration_as_of={2024:'2024-11-05',2022:'2022-11-08',2020:'2020-11-03'}[y]));break
  assert len(rr)==66,(y,len(rr))
  for r in local:
   rg=next(s for s in rr if s['county']==r['county']);r.update({k:v for k,v in rg.items()if k not in ['year','county']});r['turnout_registered_minus_registration_active']=r['turnout_table_registered']-rg['registration_active']
  out.extend(local);regrows.extend(rr)
  summary[str(y)]=dict(turnout_registered=sum(r['turnout_table_registered']for r in local),votes_cast=sum(r['votes_cast_source_label']for r in local),registration_active=sum(r['registration_active']for r in local),registration_inactive=sum(r['registration_inactive']for r in local),table_registered_difference=sum(r['turnout_registered_minus_registration_active']for r in local))
 csvout(BASE/'turnout-registration-controls.csv',out);js(SRC/'turnout-controls.json',summary)
 rows=list(csv.DictReader((BASE.parent/'county-baselines.csv').open()))
 for r in rows:
  c=next(x for x in out if x['year']==int(r['year']) and x['county']==r['county'])
  r.update({k:v for k,v in c.items()if k not in ['year','county','county_fips','source_id']})
  r['votes_cast_minus_named_contest']=int(c['votes_cast_source_label'])-int(r['all_named_votes'])
  r['residual_scope']='unclassified Votes Cast minus named contest votes; not separately proven blank/under/over'
 csvout(BASE.parent/'county-baselines.csv',rows)
 print(json.dumps(summary))
if __name__=='__main__':main()
