#!/usr/bin/env python3
"""Extract only required registration/participation totals, list universe and WI rows.
All other original content is retained byte-exact, not turned into demographic derivatives.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import re,json,gzip,csv,io,collections,subprocess,hashlib
from extract import clean,num,dump
D=Path(__file__).resolve().parent;S=D/'source';X=D/'extracts'
def raw(sid):
 r=json.loads((S/(sid+'.receipt.json')).read_text());p=(S/r['body_path']).resolve();z=p.read_bytes();assert hashlib.sha256(z).hexdigest()==r['stored_sha256'];b=gzip.decompress(z);assert hashlib.sha256(b).hexdigest()==r['raw_sha256'];return b
FIPS={'KENT':'10001','NEW CASTLE':'10003','SUSSEX':'10005'}
def participation():
 out=[];hier=[];check=[]
 for year in [2024,2022,2020]:
  s=raw(f'participation-{year}').decode('utf-8-sig');county=rd=ed=None;level=None;pos=0;seen=set();rows=[]
  for ln,line in enumerate(s.splitlines(keepends=True),1):
   t=line.strip()
   if t.upper() in [c+' COUNTY' for c in FIPS]:county=t[:-7].upper();rd=ed=None;level='county'
   if t=='STATEWIDE':county=rd=ed=None;level='state'
   m=re.fullmatch(r'Representative District (\d+)',t)
   if m:rd=m[1].zfill(2);ed=None;level='rd'
   m=re.fullmatch(r'Election District (\d+)-(\d+)',t)
   if m:
    assert rd==m[1].zfill(2),(year,county,rd,m[0]);ed=m[2].zfill(2);level='ed'
   if re.match(r'i\. Total\s+',t):
    vals=t.split()[2:];assert len(vals)==12,(year,ln,vals)
    values={group:{'registered':num(vals[i*3]),'voted':num(vals[i*3+1]),'percentage_raw':vals[i*3+2]} for i,group in enumerate(['Democrat','Republican','All Others','Total'])}
    for field in ['registered','voted']:assert sum(values[k][field] for k in ['Democrat','Republican','All Others'])==values['Total'][field]
    key=f'ElectionDistrict{rd}{ed}' if level=='ed' else f'RepresentativeDistrict{rd}' if level=='rd' else county if level=='county' else 'State'
    identity=(level,county,key);assert identity not in seen,(year,identity);seen.add(identity)
    a={'year':year,'source_id':f'participation-{year}','level':level,'county':county,'county_fips':FIPS.get(county),'rd':rd,'ed':ed,'native_key':key,'values':values,'source_line':ln,'source_char_start':pos,'source_char_end':pos+len(line),'raw_line':line,'scope':'Registered Voters by Age Group and Party / General Election; i. Total; status/date of registration extract not specified in entity; Voted is source participation, not a certified ballot-count claim'}
    out.append(a);rows.append(a)
    if level=='ed':hier.append({k:a[k] for k in ['year','source_id','county','county_fips','rd','ed','native_key','source_line','source_char_start','source_char_end']})
   pos+=len(line)
  state=[r for r in rows if r['level']=='state'];assert len(state)==1
  for field in ['registered','voted']:
   total=state[0]['values']['Total'][field]
   assert sum(r['values']['Total'][field] for r in rows if r['level']=='county')==total
   assert sum(r['values']['Total'][field] for r in rows if r['level']=='ed')==total
   assert sum(r['values']['Total'][field] for r in rows if r['level']=='rd')==total
   for c in FIPS:
    assert sum(r['values']['Total'][field] for r in rows if r['level']=='ed' and r['county']==c)==next(r['values']['Total'][field] for r in rows if r['level']=='county' and r['county']==c)
   check.append({'year':year,'field':field,'state':total,'ed_count':sum(r['level']=='ed' for r in rows),'all_ed_rd_county_sums_pass':True})
 dump('participation-totals.json',out);dump('historical-hierarchy.json',hier);dump('participation-checks.json',check)
 return out,hier

def registration():
 out=[]
 for year in [2024,2022]:
  sid=f'registration-{year}-november';text=raw(sid).decode('utf-8-sig');rr=list(csv.DictReader(io.StringIO(text)))
  for ln,r in enumerate(rr,2):
   assert r['County'] in FIPS
   out.append({'year':year,'source_id':sid,'source_row':ln,'county':r['County'],'county_fips':FIPS[r['County']],'rd':r['RepresentativeDistrict'][2:],'ed':r['ElectionDistrict'][2:],'native_key':'ElectionDistrict'+r['RepresentativeDistrict'][2:]+r['ElectionDistrict'][2:],'registered':sum(int(r[k]) for k in ['DEMOCRATIC','REPUBLICAN','OTHERS']) if all(r[k]!='' for k in ['DEMOCRATIC','REPUBLICAN','OTHERS']) else None,'raw_fields':r,'date':f'{year}-11-01','scope':'registered-voter monthly stock; status not specified in CSV; not election-day denominator'})
 year=2020;sid='registration-2020-november';s=raw(sid).decode('utf-8-sig')
 for tm in list(re.finditer(r'<table\b[^>]*>(.*?)</table>',s,re.S|re.I))[1:]:
  county=None;rd=None
  for rm in re.finditer(r'<tr\b[^>]*>(.*?)</tr>',tm[1],re.S|re.I):
   vals=[clean(v) for v in re.findall(r'<td\b[^>]*>(.*?)</td>',rm[1],re.S|re.I)]
   if not vals:continue
   if vals[0] in FIPS:county=vals[0]
   if re.fullmatch('RD\d+',vals[0]):rd=vals[0][2:]
   if re.fullmatch('ED\d+',vals[0]):
    assert county in FIPS,(county,vals)
    n=[num(x) for x in vals[1:]];assert sum(n[:3])==n[3]
    out.append({'year':year,'source_id':sid,'source_char_start':s.index(tm[1],tm.start())+rm.start(),'source_char_end':s.index(tm[1],tm.start())+rm.end(),'county':county,'county_fips':FIPS[county],'rd':rd,'ed':vals[0][2:],'native_key':'ElectionDistrict'+rd+vals[0][2:],'registered':n[3],'raw_fields':dict(zip(['Election District','DEMOCRATIC','REPUBLICAN','OTHERS','Grand Total'],vals)),'date':'2020-11-01','scope':'registered-voter monthly stock; status not specified in report; not election-day denominator'})
 dump('registration-november.json',out)
 return out

def monthly_controls():
 out=[]
 for y in [2024,2022]:
  text=(S/f'registration-{y}-november.txt').read_text();offset=0
  for ln,line in enumerate(text.splitlines(keepends=True),1):
   m=re.match(r'^\s*(KENT|NEW CASTLE|SUSSEX|Statewide) Total\s+(.*)',line)
   if m:
    vals=m[2].split();assert len(vals)==4;nn=[num(x) for x in vals];assert sum(nn[:3])==nn[3]
    out.append({'year':y,'source_id':f'registration-{y}-november-pdf','geography':m[1],'source_line':ln,'source_char_start':offset,'raw_line':line,'date':f'{y}-11-01','values':dict(zip(['Democratic','Republican','Others','Grand Total'],nn)),'status':'registered stock; active/inactive status unprinted'})
   offset+=len(line)
  rr=[r for r in json.loads((X/'registration-november.json').read_text()) if r['year']==y]
  for c in ['KENT','NEW CASTLE','SUSSEX','Statewide']:
   rs=[r for r in rr if c=='Statewide' or r['county']==c];ctl=next(a for a in out if a['year']==y and a['geography']==c)
   assert sum(int(r['raw_fields'][k]) for r in rs for k in ['DEMOCRATIC','REPUBLICAN','OTHERS'] if r['raw_fields'][k]!='')==ctl['values']['Grand Total']
   ctl['sum_of_numeric_csv_party_cells_matches']=True;ctl['blank_csv_party_cells']=sum(r['raw_fields'][k]=='' for r in rs for k in ['DEMOCRATIC','REPUBLICAN','OTHERS'])
   ctl['blank_scope']='numeric-cell sums reconcile; individual absent cells stay null; no fabricated0 or exact total in sparse native rows'
 s=raw('registration-2020-november').decode('utf-8-sig');tm=next(re.finditer(r'<table\b[^>]*>(.*?)</table>',s,re.S|re.I))
 for m in re.finditer(r'<tr\b[^>]*>(.*?)</tr>',tm[1],re.S|re.I):
  vals=[clean(x) for x in re.findall(r'<td\b[^>]*>(.*?)</td>',m[1],re.S|re.I)]
  if vals:
   nn=[num(x) for x in vals[1:]];assert len(nn)==4 and sum(nn[:3])==nn[3]
   out.append({'year':2020,'source_id':'registration-2020-november','geography':vals[0],'source_char_start':s.index(tm[1],tm.start())+m.start(),'source_char_end':s.index(tm[1],tm.start())+m.end(),'raw_values':vals,'date':'2020-11-01','values':dict(zip(['Democratic','Republican','Others','Grand Total'],nn)),'status':'registered stock; active/inactive status unprinted'})
 dump('monthly-registration-controls.json',out)

def sample_ballot_inventory():
 text=raw('sample-ballot-index-2024').decode('utf-8-sig');out=[]
 for m in re.finditer(r'<tr\b[^>]*>(.*?)</tr>',text,re.S):
  cells=[' '.join(clean(v).split()) for v in re.findall(r'<td\b[^>]*>(.*?)</td>',m[1],re.S)]
  if len(cells)==4 and cells[0] in ['Kent','New Castle','Sussex']:
   out.append({'source_id':'sample-ballot-index-2024','source_char_start':m.start(),'source_char_end':m.end(),'county_literal':cells[0],'rd_literal':cells[1],'ed_literal':cells[2],'native_key':'ElectionDistrict'+cells[1].zfill(2)+cells[2].zfill(2),'hrefs':re.findall('href="([^\"]+)"',m[1]),'scope':'historical 2024 machine sample-ballot index row; no claim that ballot PDF downloaded or polygons approved'})
 assert len(out)==533 and len({r['native_key'] for r in out})==533
 dump('sample-ballot-identities.json',out)

def candidate_lists():
 out=[];summaries=[]
 for y in [2024,2022,2020]:
  for typ in ['f','w']:
   sid=f'candidates-{y}-{typ}';s=raw(sid).decode('utf-8-sig');rows=[]
   for m in re.finditer(r'<tr\b[^>]*>(.*?)</tr>',s,re.S|re.I):
    cells=[clean(v) for v in re.findall(r'<td\b[^>]*>(.*?)</td>',m[1],re.S|re.I)]
    if not cells:continue
    office=' '.join(cells[0].upper().split())
    if office in ['PRESIDENT','PRESIDENTVICE PRESIDENT','PRESIDENT VICE PRESIDENT','PRESIDENT AND VICE PRESIDENT','U.S. SENATOR','REPRESENTATIVE IN CONGRESS']:
     r={'year':y,'source_id':sid,'list_type':'qualified' if typ=='f' else 'declared write-in','office_literal':cells[0],'source_char_start':m.start(),'source_char_end':m.end(),'raw_cells':cells};out.append(r);rows.append(r)
   summaries.append({'year':y,'source_id':sid,'list_type':typ,'offices':dict(collections.Counter(r['office_literal'].upper() for r in rows)),'senate_declared_writein_rows':sum(r['office_literal'].upper()=='U.S. SENATOR' for r in rows) if typ=='w' else None})
 dump('candidate-list-rows.json',out);dump('candidate-universe.json',summaries)

def writeins():
 # Column positions come from pdftotext layout; visual review ledger retained separately.
 rows=[]
 for year in [2024,2022,2020]:
  text=(S/f'writeins-{year}.txt').read_text();page=1;county=None;office=None;pos=0
  for ln,line in enumerate(text.splitlines(keepends=True),1):
   if '\f' in line:page+=1
   st=line.strip()
   if year==2024:
    if st in ['NEW CASTLE County','KENT County','SUSSEX County']:county=st[:-7].upper()
    if st=='City of Wilmington':county='City of Wilmington'
    if st=='President and Vice President':office='PresidentandVicePresident'
    # Header line is usually combined with column titles.
    if 'President and Vice President' in line:office='PresidentandVicePresident'
    if 'City Council District 3' in line:office='CityCouncilDistrict3'
    if 'State Senator District 16' in line:office='StateSenatorDistrict16'
   elif year==2022:
    if st=='Statewide':county='State'
    if st=='New Castle County':county='NEW CASTLE'
    if 'Representative in Congress' in line:office='RepresentativeinCongress'
    if 'State Representative District 22' in line:office='StateRepresentativeDistrict22'
   else:
    if st=='STATEWIDE':county='State'
    if st=='NEW CASTLE COUNTY':county='NEW CASTLE'
    if st=='SUSSEX COUNTY':county='SUSSEX'
    if st=='PRESIDENT':office='PresidentandVicePresident'
    if st.startswith(('STATE REP','CNTY CNCL','COUNTY EXEC','CITY CNCL')):office=st
   # Target only required contests; all PDF bytes including other offices remain retained.
   if office not in ['PresidentandVicePresident','RepresentativeinCongress'] or (year==2022 and county!='State'):pos+=len(line);continue
   if st.startswith('Page ') or not re.match(r'^ {3,12}[A-Z].*?\s+\d+\s*$',line):pos+=len(line);continue
   if year==2024 or year==2022:
    # First numeric column starts at char43 in layout; names may extend into this area.
    total=re.search(r'(\d[\d,]*)\s*$',line)
    if not total:pos+=len(line);continue
    # Fixed aligned numeric column starts inferred from header and inspected layout.
    candidates=list(re.finditer(r'\d[\d,]*',line))
    first=candidates[0].start();name=line[:first].strip()
    if first<40:pos+=len(line);continue
    cols=[(43,55),(55,68),(68,81),(81,94)] if year==2024 else [(43,55),(55,68),(68,81),(81,94)]
    # Robustly map token right edges to visually checked column endpoints.
    vals={'Absentee':None,'Early Voting':None,'Machine':None,'Provisional':None,'Grand Total':num(total[1])}
    ends=[m.end() for m in candidates[:-1]]
    # 2024 end positions:51,65,78,92;2022:51,65,78,92.
    for m in candidates[:-1]:
     key=min(zip(([51,65,78,92] if year==2024 else [44,57,70,84]),['Absentee','Early Voting','Machine','Provisional']),key=lambda kv:abs(kv[0]-m.end()))[1];assert vals[key] is None,(year,repr(line),[(n[0],n.end()) for n in candidates],vals);vals[key]=num(m[0])
   else:
    candidates=list(re.finditer(r'\d[\d,]*',line));first=candidates[0].start();name=line[:first].strip()
    if first<50:pos+=len(line);continue
    vals={'Absentee':None,'Early Voting':None,'Machine':None,'Provisional':None,'Grand Total':num(candidates[-1][0])}
    for m in candidates[:-1]:
     key='Absentee' if m.end()<80 else 'Machine';vals[key]=num(m[0])
   assert sum(v for k,v in vals.items() if k!='Grand Total' and v is not None)==vals['Grand Total'],(year,line,vals)
   rows.append({'year':year,'office_key':office,'county':county,'candidate':name,'page':page,'source_line':ln,'source_char_start':pos,'raw_line':line,'values':vals,'scope':'named official write-in sheet; blanks remain null; no ED allocation'})
   pos+=len(line)
 dump('writein-rows.json',rows)
 print('WI',[(y,len([r for r in rows if r['year']==y]),sum(r['values']['Grand Total'] for r in rows if r['year']==y)) for y in [2024,2022,2020]])
if __name__=='__main__':
 p,h=participation();r=registration();monthly_controls();candidate_lists();writeins();sample_ballot_inventory();print('participation',len(p),'hierarchy',len(h),'monthly registration',len(r))
