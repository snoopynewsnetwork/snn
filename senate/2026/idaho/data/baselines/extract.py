#!/usr/bin/env python3
"""Independent source-position extraction. stdlib only; no peer derivatives."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json,posixpath,re,zipfile
import xml.etree.ElementTree as ET

D=Path(__file__).resolve().parent; STATE=D.parent.parent; NEWS=D.parent/'news'
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,obj):
 p=D/name;p.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def csvout(name,rows):
 rows=list(rows);p=D/name;p.parent.mkdir(parents=True,exist_ok=True)
 s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 b=s.getvalue().encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def workbook(raw):
 z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
 strings=[]
 if 'xl/sharedStrings.xml' in z.namelist():
  strings=[''.join(t.text or ''for t in si.iter('{'+NS['s']+'}t'))for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
 rel={a.get('Id'):a.get('Target')for a in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
 sheets={}
 for s in ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS):
  target=rel[s.get('{'+REL+'}id')];member=target.lstrip('/')if target.startswith('/')else posixpath.normpath('xl/'+target)
  rows=[]
  for r in ET.fromstring(z.read(member)).findall('s:sheetData/s:row',NS):
   cells={}
   for c in r.findall('s:c',NS):
    v=c.find('s:v',NS);rawv=None if v is None else v.text;value=rawv
    if c.get('t')=='s'and rawv is not None:value=strings[int(rawv)]
    if c.get('t')=='inlineStr':value=''.join(t.text or ''for t in c.iter('{'+NS['s']+'}t'))
    cells[re.sub('[0-9]','',c.get('r'))]=dict(address=c.get('r'),value=value,type=c.get('t'),style=c.get('s'),raw_v=rawv,formula=None if c.find('s:f',NS)is None else c.find('s:f',NS).text)
   rows.append(dict(row=int(r.get('r')),cells=cells))
  sheets[s.get('name')]=dict(member=member,rows=rows)
 return sheets
def v(r,c):return r['cells'].get(c,{}).get('value')
def integer(x):return int(x)if x is not None and re.fullmatch(r'[0-9]+',str(x))else None
def method(label):
 # Literal lexical inventory, deliberately not an official method partition.
 x=label.lower()
 hits=[t for t in ['absentee','early','mail','provisional','central','election day']if t in x]
 return ';'.join(hits)if hits else 'method_not_explicit_in_label'

def main():
 ledger={a['id']:a for a in json.loads((NEWS/'manifest.json').read_text())};refs=[];raw={};zips={};books={};pins=[]
 ids=['sos-results','sos-2024-all-races-xlsx','sos-2024-turnout-xlsx','sos-2024-canvass','sos-2020-general-canvass-zip','sos-2020-general-abstracts-zip','sos-2022-general-canvass-zip']
 for sid in ids:
  if sid not in ledger:continue
  a=ledger[sid];p=NEWS/a['asset'];stored=p.read_bytes();b=gzip.decompress(stored)
  assert sha(b)==a['raw_sha256'] and sha(stored)==a['stored_sha256']
  refs.append(dict(**a,relative_path=posixpath.relpath(p,D),reuse='read_only_exact_hash_original',raw_bytes=len(b),stored_bytes=len(stored)))
  raw[sid]=b
  if b[:2]==b'PK'and'zip'in sid:
   zips[sid]=zipfile.ZipFile(io.BytesIO(b));assert zips[sid].testzip() is None
   for i in zips[sid].infolist():pins.append(dict(source_id=sid,member=i.filename,bytes=i.file_size,crc32=f'{i.CRC:08x}',sha256=sha(zips[sid].read(i))))
 for year in [2020,2022]:
  sid=f'sos-{year}-general-canvass-zip'
  for f in zips[sid].namelist():
   if f.endswith('.xlsx')and('stwd'in f.lower()or'Statewide'in f):
    scope='native'if'_pct'in f or'Precinct'in f else'county'
    books[(year,scope)]=(sid,f,workbook(zips[sid].read(f)),sha(zips[sid].read(f)))
 save('source/reused-originals.json',refs);save('source/archive-members.json',pins)
 units=[];positions=[];controls=[];stats=[];summaries=[]
 races=workbook(raw['sos-2024-all-races-xlsx']);rs=next(iter(races.values()));groups=collections.OrderedDict()
 for r in rs['rows'][1:]:
  if v(r,'D')=='United States President':groups.setdefault((v(r,'A'),v(r,'B')),[]).append(r)
 assert len(groups)==985
 for (county,label),rr in groups.items():
  candidates=[];othercats=[]
  uid=f'2024-president:{rr[0]["row"]}'
  for r in rr:
   non=v(r,'F') in ['Overvotes','Undervotes'];cand=dict(key='F:'+str(r['row']-rr[0]['row']),name=v(r,'F'),party=v(r,'E'),votes=integer(v(r,'G')),source_row=r['row'],cell=f'G{r["row"]}',header_literal=v(r,'F'))
   (othercats if non else candidates).append(cand)
   positions.append(dict(contest='2024-president',source_id='sos-2024-all-races-xlsx',archive_member=None,worksheet=next(iter(races)),worksheet_member=rs['member'],row=r['row'],column='G',unit_id=uid,county=county,label=label,role='noncandidate_category'if non else'native_candidate',raw_cells=r['cells'],candidate=cand))
  assert len(candidates)==11 and len(othercats)==2
  units.append(dict(contest='2024-president',year=2024,scope='native',unit_id=uid,county=county,label=label,source_id='sos-2024-all-races-xlsx',archive_member=None,worksheet=next(iter(races)),row=rr[0]['row'],source_rows=[r['row']for r in rr],method_label_evidence=method(label),candidates=candidates,noncandidate=othercats))
 # County aggregation retains raw counties; no precinct-label equivalence.
 for county in sorted({u['county']for u in units}):
  uu=[u for u in units if u['county']==county];cands=[];cats=[]
  for target,key in [(cands,'candidates'),(cats,'noncandidate')]:
   for j,c in enumerate(uu[0][key]):
    assert all(u[key][j]['name']==c['name']and u[key][j]['party']==c['party']for u in uu)
    target.append(dict(c,votes=sum(u[key][j]['votes']for u in uu),source_row=None,cell=None))
  controls.append(dict(contest='2024-president',year=2024,scope='county',unit_id='2024-president:county:'+county,county=county,label=county,source_id='sos-2024-all-races-xlsx',archive_member=None,worksheet=next(iter(races)),row=None,source_rows=[r for u in uu for r in u['source_rows']],method_label_evidence='all_published_native_contexts',candidates=cands,noncandidate=cats))
 stbook=workbook(raw['sos-2024-turnout-xlsx']);sh=next(iter(stbook.values()))
 for r in sh['rows'][1:]:
  stats.append(dict(year=2024,source_id='sos-2024-turnout-xlsx',worksheet=next(iter(stbook)),row=r['row'],county=v(r,'A'),label=v(r,'B'),role='overlapping_county_footer'if v(r,'B')=='Total'else'native',cutoff=integer(v(r,'C')),day=integer(v(r,'D')),registered=integer(v(r,'E')),ballots=integer(v(r,'F')),source_turnout=v(r,'G'),raw_cells=r['cells']))
 specs=[(2020,'2020-senate-II','Federal','IJKL',6,5,5,4),(2020,'2020-president','Federal','BCDEFGH',6,5,5,4),(2022,'2022-senate-III','US Sen','BCDEF',6,5,4,3),(2022,'2022-governor','Gov','BCDEFG',7,6,5,4)]
 for year,contest,sheet,cols,cn,cp,pn,pp in specs:
  sid,cm,cb,chash=books[year,'county'];_,pm,pb,phash=books[year,'native'];cr={r['row']:r for r in cb[sheet]['rows']};pr={r['row']:r for r in pb[sheet]['rows']}
  names=[v(cr[cn],c)for c in cols];parties=[v(cr[cp],c)for c in cols]
  counties={};state=None
  for r in cb[sheet]['rows']:
   if r['row']<=cn:continue
   if v(r,'A')=='TOTAL':state=r;break
   if v(r,'A')and all(integer(v(r,c))is not None for c in cols):counties[v(r,'A')]=r
  assert len(counties)==44 and state
  def unit(r,county,scope,member,rows,role):
   cs=[dict(key=c,name=names[j],party=parties[j],header_literal=v(rows[pn if scope=='native'else cn],c),party_header_literal=v(rows[pp if scope=='native'else cp],c),votes=integer(v(r,c)),source_row=r['row'],cell=f'{c}{r["row"]}')for j,c in enumerate(cols)]
   u=dict(contest=contest,year=year,scope=scope,unit_id=f'{contest}:{scope}:{r["row"]}',county=county,label=v(r,'A'),source_id=sid,archive_member=member,workbook_sha256=phash if scope=='native'else chash,worksheet=sheet,row=r['row'],source_rows=[r['row']],method_label_evidence=method(v(r,'A')or''),candidates=cs,noncandidate=[])
   for c,cc in zip(cols,cs):positions.append(dict(contest=contest,source_id=sid,archive_member=member,worksheet=sheet,worksheet_member=(pb if scope=='native'else cb)[sheet]['member'],row=r['row'],column=c,unit_id=u['unit_id'],county=county,label=u['label'],role=role,candidate=cc,raw_cell=r['cells'].get(c),raw_label_cell=r['cells'].get('A')))
   return u
  for county,r in counties.items():controls.append(unit(r,county,'county',cm,cr,'separate_county_control'))
  controls.append(unit(state,None,'state',cm,cr,'separate_state_control'))
  parent=None;footed=set();native=[];footers=[]
  for r in pb[sheet]['rows']:
   if r['row']<=pn:continue
   label=v(r,'A');vals=[v(r,c)for c in cols]
   if label is None and all(a is None for a in vals):continue
   h=re.sub(r'(?: \(continued\)|, cont\.)$','',label or'',flags=re.I)
   if h in {c.upper()for c in counties}and all(a is None for a in vals):parent=next(c for c in counties if c.upper()==h);continue
   if len(footed)==44:
    controls.append(unit(r,None,'native',pm,pr,'post_county_control_or_appendix'));continue
   if label in ['TOTAL','Percentage','Plurality']:continue
   assert parent and label is not None
   if label=='CO. TOTAL':
    assert parent not in footed;footed.add(parent);u=unit(r,parent,'native',pm,pr,'overlapping_county_footer');controls.append(u);footers.append(u)
   else:u=unit(r,parent,'native',pm,pr,'native_candidate');units.append(u);native.append(u)
  assert len(footed)==44
  balances=[]
  for county,r in counties.items():
   rows=[u for u in native if u['county']==county];f=next(u for u in footers if u['county']==county)
   known=[sum(u['candidates'][j]['votes']for u in rows if u['candidates'][j]['votes']is not None)for j in range(len(cols))]
   expected=[integer(v(r,c))for c in cols];assert known==expected==[c['votes']for c in f['candidates']]
   balances.append(dict(county=county,native_rows=len(rows),known_candidate_sums=known,county_control=expected,footer_row=f['row'],missing_cells=[c for u in rows for c in u['candidates']if c['votes']is None]))
  sums=[sum(integer(v(r,c))for r in counties.values())for c in cols];assert sums==[integer(v(state,c))for c in cols]
  summaries.append(dict(contest=contest,candidates=[dict(name=n,party=p,votes=t)for n,p,t in zip(names,parties,sums)],native_rows=len(native),county_controls=44,county_balances=balances))
 # 2020 voting stats, independently scoped from its own headings/footers.
 for scope in ['county','native']:
  sid,mem,b,wh=books[2020,scope];ss=b['Amend & Stats'];parent=None;footed=set()
  for r in ss['rows']:
   label=v(r,'A')
   if r['row']<=(6 if scope=='county'else 5):continue
   h=re.sub(r'(?: \(continued\)|, cont\.)$','',label or'',flags=re.I)
   if scope=='native'and h in {c.upper()for c in counties}and all(v(r,c)is None for c in 'DEFG'):parent=next(c for c in counties if c.upper()==h);continue
   if label is None:continue
   role='county_control'if scope=='county'else'native'
   if scope=='native'and len(footed)==44:role='post_county_control'
   elif label=='CO. TOTAL':role='overlapping_county_footer';footed.add(parent)
   elif label in ['TOTAL','STATE TOTAL']:role='state_control'
   if all(integer(v(r,c))is not None for c in 'DEFG')or(role=='native'and parent and label not in ['Percentage','Plurality']):
    stats.append(dict(year=2020,source_id=sid,archive_member=mem,worksheet='Amend & Stats',row=r['row'],county=label if scope=='county'else(parent if role!='post_county_control'else None),label=label,role=role,cutoff=integer(v(r,'D')),day=integer(v(r,'E')),registered=integer(v(r,'F')),ballots=integer(v(r,'G')),source_turnout=v(r,'H'),raw_cells=r['cells']))
 save('source/native-units.json.gz',units);save('source/candidate-positions.json.gz',positions);save('source/controls.json.gz',controls);save('source/statistics-positions.json.gz',stats);save('source/historical-reconciliation.json',summaries)
 # source-native full descending priority, using named valid candidate total.
 p=[u for u in units if u['contest']=='2024-president'];p.sort(key=lambda u:(-sum(c['votes']for c in u['candidates']),u['county'],u['label'],u['row']))
 total=sum(sum(c['votes']for c in u['candidates'])for u in p);cum=0;order=[]
 for i,u in enumerate(p,1):
  n=sum(c['votes']for c in u['candidates']);before=cum;cum+=n
  order.append(dict(rank=i,unit_id=u['unit_id'],county=u['county'],literal_unit=u['label'],first_source_row=u['row'],source_rows=';'.join(map(str,u['source_rows'])),candidate_votes=n,cumulative=cum,state_named_total=total,priority_minimum80=before*5<total*4,top15=i<=15))
 csvout('native-priority-order.csv',order)
 st={ (r['county'],r['label']):r for r in stats if r['year']==2024 and r['role']=='native'}
 pairs=[]
 for u in p:
  s=st[u['county'],u['label']];cats=sum(c['votes']for c in u['candidates']+u['noncandidate'])
  pairs.append(dict(county=u['county'],label=u['label'],race_rows=u['source_rows'],stats_row=s['row'],all_category=cats,ballots=s['ballots'],ballots_minus_all_category=s['ballots']-cats))
 save('source/2024-statistics-disagreements.json',dict(literal_pairs=len(pairs),nonzero=[r for r in pairs if r['ballots_minus_all_category']],stats_only=[s for k,s in st.items()if k not in {(u['county'],u['label'])for u in p}],no_physical_or_method_equivalence_inferred=True))
 save('independent-extraction-summary.json',dict(native_counts=dict(collections.Counter(u['contest']for u in units)),candidate_totals={t:sum(c['votes']for u in units if u['contest']==t for c in u['candidates']if c['votes']is not None)for t in {u['contest']for u in units}},priority=dict(named_total=total,count=sum(r['priority_minimum80']for r in order),votes=sum(r['candidate_votes']for r in order if r['priority_minimum80']),before_crossing=next(r['cumulative']for r in order if r['rank']==sum(q['priority_minimum80']for q in order)-1),crossing=next(r for r in order if r['rank']==sum(q['priority_minimum80']for q in order)),top15=sum(r['candidate_votes']for r in order[:15])),peer_derivatives_read=False))
 print((D/'independent-extraction-summary.json').read_text())
if __name__=='__main__':main()
