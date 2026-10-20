#!/usr/bin/env python3
"""Independent original HTML parser. No coordinator/peer derivative input."""
from pathlib import Path
import csv,gzip,hashlib,html,io,json,re,collections
P=Path(__file__).resolve().parent
SPECS={2020:('sos-observed-2020-general-report','sos-observed-2020-state-csv',['USSenator','PresidentandVicePresident']),2022:('official-2022-report','sos-observed-2022-state-csv',['RepresentativeinCongress']),2024:('sos-2024-general-report','sos-2024-csv',['USSenator','PresidentandVicePresident'])}
METHODS=['Machine Votes','Absentee Votes','Early Voting Votes','Total Votes']
COUNTIES={'New Castle':'10003','Kent':'10001','Sussex':'10005'}
def clean(s):return html.unescape(re.sub('<[^>]+>','',s)).strip()
def num(s):return int(s.replace(',','')) if s not in [None,''] else None
def writejson(path,o):path.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def writecsv(path,rows):
 if not rows:return
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def raw(sid):
 a=next(a for a in json.loads((P/'source/shared-sources.json').read_text()) if a['id']==sid);z=(P/a['shared_asset']).read_bytes();b=gzip.decompress(z)
 assert hashlib.sha256(b).hexdigest()==a['raw_sha256'] and hashlib.sha256(z).hexdigest()==a['stored_sha256'];return b

def parse(year,sid):
 b=raw(sid);t=b.decode('utf-8-sig');views=[]
 for m in re.finditer(r'<div\b[^>]*id="(statewide|byrepdist|byelectiondist|bycounty|bycountyw)"[^>]*>',t):views.append((m.start(),m[1]))
 office=geo=None;tables=[];inventory=[]
 for m in re.finditer(r'<h[34]\b[^>]*>.*?</h[34]>|<table\b[^>]*>.*?</table>',t,re.S):
  v=[v for pos,v in views if pos<m.start()]
  if not v:continue
  view=v[-1];s=m[0]
  if s.startswith('<h3'):
   cl=re.search(r'class="contest-title ([^"]+)"',s)
   office=(cl[1],clean(s)) if cl else None;geo=None
  elif s.startswith('<h4'):
   cl=re.search(r'class="([^"]+)"',s);geo=(cl[1].split()[-1],clean(s)) if cl else None
  elif office:
   heads=[clean(x) for x in re.findall(r'<th(?:\s[^>]*)?>(.*?)</th>',s,re.S)];rows=[]
   for ri,r in enumerate(re.finditer(r'<tr(?:\s[^>]*)?>(.*?)</tr>',s,re.S) if office[0] in SPECS[year][2] else []):
    cells=list(re.finditer(r'<td(?:\s[^>]*)?>(.*?)</td>',r[1],re.S))
    if not cells:continue
    vals=[clean(x[1]) for x in cells];assert len(vals)==len(heads),(year,view,office,heads,vals)
    rows.append(dict(row_index=ri,source_char_start=m.start()+r.start(),source_char_end=m.start()+r.end(),cells=vals,fields=dict(zip(heads,vals)),data_labels=[(re.search(r'data-label="([^"]*)"',x[0])[1] if re.search(r'data-label="([^"]*)"',x[0]) else None) for x in cells]))
   tb=dict(year=year,source_id=sid,source_sha256=hashlib.sha256(b).hexdigest(),view=view,office_key=office[0],office_label=office[1],geo_key=geo[0] if geo else ('State' if view=='statewide' else None),geo_label=geo[1] if geo else None,source_char_start=m.start(),source_char_end=m.end(),headers=heads,rows=rows)
   tables.append(tb)
   inventory.append({k:val for k,val in tb.items() if k not in ['rows']})
 return tables,inventory,t

def main():
 allrows=[];tbout=[];invent=[];parents=[];checks=[];statistics=[];statecsv=[]
 for year,(sid,cid,offices) in SPECS.items():
  tables,iv,t=parse(year,sid);invent+=iv
  controls=list(csv.DictReader(io.StringIO(raw(cid).decode('utf-8-sig'))));statecsv.extend(dict(source_id=cid,source_row=i+2,**r) for i,r in enumerate(controls))
  office_labels={x['office_key']:x['office_label'].strip() for x in tables if x['view']=='statewide'}
  # Countywide contests print their county scope in office title. All memberships retained.
  memberships=collections.defaultdict(list)
  for tb in tables:
   if tb['view']!='byelectiondist':continue
   label=tb['office_label']
   matches=[c for c in COUNTIES if re.search(r'\b'+c+r'(?: County)?\b',label,re.I)]
   if not matches:
    if re.match(r'NCC\b',label):matches=['New Castle']
    elif re.match(r'KC\b',label):matches=['Kent']
    elif re.match(r'SC\b',label):matches=['Sussex']
   for c in matches:memberships[tb['geo_key']].append(dict(county=c,office_key=tb['office_key'],office_label=label,source_char_start=tb['source_char_start']))
  native=set(tb['geo_key'] for tb in tables if tb['view']=='byelectiondist')
  pmap={}
  for key in sorted(native):
   evidence=memberships[key];cs=sorted(set(e['county'] for e in evidence));assert len(cs)<=1,(year,key,cs)
   pmap[key]=cs[0] if cs else None
   parents.append(dict(year=year,geo_key=key,county=pmap[key],fips=COUNTIES.get(pmap[key]),basis='Actual county-office election-district table membership; no numeric range inference' if cs else 'No county-scoped office membership available',evidence=evidence))
  for office in offices:
   selected=[tb for tb in tables if tb['office_key']==office];tbout+=selected
   ed=[tb for tb in selected if tb['view']=='byelectiondist']; st=[r for r in controls if r['office'].strip()==office_labels[office]]
   assert len({tb['geo_key'] for tb in ed})==len(ed)
   for cr in st:
    name=cr['candidatename'];party=cr['partyname']
    for method,col in zip(METHODS,['machinevotessum','absenteevotessum','earlyvotessum','totalvotessum']):
     vals=[num(r['fields'].get(method)) for tb in ed for r in tb['rows'] if r['fields']['Candidate']==name]
     observed=sum(x for x in vals if x is not None);expected=int(cr[col]);nulls=sum(x is None for x in vals)
     assert observed==expected,(year,office,name,method,observed,expected)
     checks.append(dict(year=year,office_key=office,candidate=name,party=party,method=method,ed_sum_available=observed,state_control=expected,difference=observed-expected,null_native_cells=nulls,scope='unprinted native method; available sum only' if nulls else 'all native cells printed'))
   co=next(tb for tb in selected if tb['view']=='bycounty');cw=next(tb for tb in selected if tb['view']=='bycountyw')
   for r in co['rows']:
    f=r['fields'];cr=next(x for x in st if x['candidatename']==f['Candidate']);assert sum(num(f[c]) for c in COUNTIES)==int(cr['totalvotessum'])==num(f['State'])
    wr=next(x['fields'] for x in cw['rows'] if x['fields']['Candidate']==f['Candidate'])
    assert num(wr['Wilmington'])+num(wr['Rest of New Castle'])==num(f['New Castle'])
    for c in COUNTIES:
     if all(pmap[tb['geo_key']] for tb in ed):assert sum(num(r2['fields']['Total Votes']) for tb in ed if pmap[tb['geo_key']]==c for r2 in tb['rows'] if r2['fields']['Candidate']==f['Candidate'])==num(f[c]),(year,office,c)
   for tb in selected:
    for rr in tb['rows']:
     f=dict(rr['fields']);f['Candidate']=f.get('Candidate',f.get('Candidate Name'));f['Party']=f.get('Party',f.get('Party Name'));name=f['Candidate'];party=f['Party'];nmethods=[num(f.get(x)) for x in METHODS]
     if tb['view'] in ['statewide','byrepdist','byelectiondist']:assert sum(x for x in nmethods[:3] if x is not None)==nmethods[3]
     gs=list(COUNTIES)+['State'] if tb['view']=='bycounty' else (['Wilmington','Rest of New Castle','Kent','Sussex','State'] if tb['view']=='bycountyw' else [tb['geo_key']])
     for geo in gs:
      county=geo if geo in COUNTIES else (pmap.get(geo) if tb['view']=='byelectiondist' else ('New Castle' if geo in ['Wilmington','Rest of New Castle'] else None))
      allrows.append(dict(year=year,election_date=st[0]['electiondate'][:10],office_key=office,office_label=office_labels[office],view=tb['view'],geo_key=geo,geo_label=tb['geo_label'] if len(gs)==1 else geo,county=county,fips=COUNTIES.get(county),candidate=name,party=party,machine=num(f.get('Machine Votes')),absentee=num(f.get('Absentee Votes')),early=num(f.get('Early Voting Votes')),total=num(f.get('Total Votes')) if len(gs)==1 else num(f[geo]),percentage_raw=f.get('Percentage'),source_id=sid,source_char_start=rr['source_char_start'],source_char_end=rr['source_char_end'],row_index=rr['row_index']))
  stat=re.search(r'([\d,]+) of ([\d,]+) Registered\s+Votes',clean(t));pr=re.search(r'(\d+)\s+of\s+(\d+)\s+Precincts\s+Reporting',clean(t));clock=re.search(r'Last Updated.*?(?:</[^>]+>)',t,re.S)
  statistics.append(dict(year=year,source_id=sid,reported_votes_literal=num(stat[1]),registered_votes_literal=num(stat[2]),registered_scope='Report literal Registered Votes; active/inactive and registration as-of date unprinted',precincts_reporting=int(pr[1]),precincts_total=int(pr[2]),native_inventory=len(native),county_parent_available=sum(bool(pmap[k]) for k in native),source_csv_xmlreporttime=controls[0]['xmlreporttime'],ballots_label_qualification='reported header numerator; not contest valid-vote total'))
 writejson(P/'extracted/contest-tables.json',tbout);writejson(P/'extracted/table-inventory.json',invent);writejson(P/'extracted/county-parent-evidence.json',parents)
 writecsv(P/'extracted/candidate-geography.csv',allrows);writecsv(P/'extracted/candidate-method-controls.csv',checks);writecsv(P/'extracted/state-original-csv-rows.csv',statecsv);writejson(P/'extracted/report-statistics.json',statistics)
 print(json.dumps(dict(candidate_geography_rows=len(allrows),tables=len(tbout),inventory_tables=len(invent),controls=len(checks),statistics=statistics),indent=2))
if __name__=='__main__':main()
