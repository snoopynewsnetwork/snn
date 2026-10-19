#!/usr/bin/env python3
"""Independent Idaho source extraction. Standard library only; no preflight imports.
Run from any directory: python3 path/to/build.py
"""
from pathlib import Path
from collections import Counter,defaultdict
from html.parser import HTMLParser
from fractions import Fraction
import csv,gzip,hashlib,io,json,posixpath,re,zipfile,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parent; STATE=D.parent.parent; NEWS=D.parent/'news'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}; R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
H=lambda b:hashlib.sha256(b).hexdigest()
def js(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def gz(p,obj):p.write_bytes(gzip.compress((json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
def csvout(p,rows):
 assert rows
 with p.open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def number(v):
 if v is None:return None
 assert re.fullmatch(r'\d+',str(v)),repr(v)
 return int(v)
def total(values):return sum(x for x in values if x is not None)
class Table(HTMLParser):
 def __init__(self):super().__init__();self.cell=None;self.row=[];self.tables=[];self.table=[]
 def handle_starttag(self,t,a):
  if t=='table':self.table=[]
  if t=='tr':self.row=[]
  if t in ['td','th']:self.cell=[]
 def handle_data(self,s):
  if self.cell is not None:self.cell.append(s)
 def handle_endtag(self,t):
  if t in ['td','th']and self.cell is not None:self.row.append(''.join(self.cell).strip());self.cell=None
  if t=='tr'and self.row:self.table.append(self.row)
  if t=='table':self.tables.append(self.table)
def book(raw,sid,member=None):
 z=zipfile.ZipFile(io.BytesIO(raw)); assert z.testzip()is None
 strings=[]
 if 'xl/sharedStrings.xml'in z.namelist():
  strings=[''.join(n.itertext())for n in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
 rel={n.get('Id'):n.get('Target')for n in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))};out=[]
 for sh in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',NS):
  path=rel[sh.get('{'+R+'}id')];path=path.lstrip('/')if path.startswith('/')else posixpath.normpath('xl/'+path);rows=[]
  for r in ET.fromstring(z.read(path)).findall('m:sheetData/m:row',NS):
   cells={};types={}
   for c in r:
    col=re.sub('[0-9]','',c.get('r'));v=c.find('m:v',NS);x=None if v is None else v.text
    if c.get('t')=='s'and x is not None:x=strings[int(x)]
    if c.get('t')=='inlineStr':x=''.join(c.itertext())
    cells[col]=x;types[col]=dict(address=c.get('r'),type=c.get('t'),style=c.get('s'),raw_value=None if v is None else v.text,formula=None if c.find('m:f',NS)is None else c.find('m:f',NS).text)
   rows.append(dict(row=int(r.get('r')),cells=cells,cell_metadata=types))
  out.append(dict(sheet=sh.get('name'),member=path,rows=rows))
 return dict(source_id=sid,archive_member=member,original_sha256=H(raw),sheets=out)
def sheet(b,name):return next(s for s in b['sheets']if s['sheet']==name)
def val(r,c):return r['cells'].get(c)
def method(label):
 # Literal flags only: not a certified vote-method or physical classification.
 return '|'.join(x for x,p in [('absentee',r'absentee|\babs\b'),('early',r'early'),('mail',r'mail'),('provisional',r'provisional'),('central',r'central')]if re.search(p,label,re.I)) or None

def main():
 m={x['id']:x for x in json.loads((NEWS/'manifest.json').read_text())};used=[];archive_inventory=[]
 def raw(sid):
  rec=m[sid];stored=(NEWS/rec['asset']).read_bytes();b=gzip.decompress(stored)
  assert H(stored)==rec['stored_sha256']and H(b)==rec['raw_sha256']and len(b)==rec['bytes']
  if sid not in [x['id']for x in used]:used.append(dict(rec,reused_path='../news/'+rec['asset'],parent_authority_url='https://voteidaho.gov/election-results/'))
  return b
 raw('sos-2024-canvass')
 races=book(raw('sos-2024-all-races-xlsx'),'sos-2024-all-races-xlsx');stats=book(raw('sos-2024-turnout-xlsx'),'sos-2024-turnout-xlsx')
 # Original bytes cover every unrelated office/field; the raw row derivative is only needed for selected source sheets.
 gz(D/'source/2024-races-rows.json.gz',races);gz(D/'source/2024-stats-rows.json.gz',stats)
 pres=[r for r in races['sheets'][0]['rows'][1:]if val(r,'D')=='United States President']
 assert not [r for r in races['sheets'][0]['rows']if val(r,'D')and 'Senat' in val(r,'D')and val(r,'C')=='Federal']
 county_names=sorted(set(val(r,'A') for r in pres)); assert len(county_names)==44
 # Idaho county FIPS sequence follows the actual alphabetical 001..087 list.
 fips_source=list(csv.DictReader(io.StringIO(gzip.decompress((D/'source/fips2020.gz').read_bytes()).decode()),delimiter='|'))
 fips={r['COUNTYNAME']:r['STATEFP']+r['COUNTYFP']for r in fips_source if r['STATE']=='ID'}
 assert set(fips)==set(county_names) and len(fips)==44
 st={};footers={}
 for r in stats['sheets'][0]['rows'][1:]:
  k=(val(r,'A'),val(r,'B'));assert k not in st and k not in footers
  if k[1]=='Total':footers[k[0]]=r
  else:st[k]=r
 candidate_order=[];native=defaultdict(list);sums=Counter();cc=defaultdict(Counter)
 for r in pres:
  c,p,party,name,v=[val(r,x)for x in 'ABEFG'];v=number(v);k=(party,name)
  if k not in candidate_order:candidate_order.append(k)
  native[(c,p)].append(r);sums[k]+=v;cc[c][k]+=v
 non={'Overvotes','Undervotes'};candidates=[k for k in candidate_order if k[1]not in non]
 assert len(candidates)==11 and len(native)==985 and len(st)==986
 for k,rr in native.items():
  assert len(rr)==13 and len({(val(r,'E'),val(r,'F')) for r in rr})==13
  assert set((val(r,'E'),val(r,'F'))for r in rr)==set(candidate_order)
 summary=[];native_rows=[];candidate_rows=[];stats_rows=[];pairings=[]
 for c in county_names:
  controls={col:number(val(footers[c],col))for col in 'CDEF'}
  assert all(sum(number(val(r,col))for k,r in st.items()if k[0]==c)==controls[col]for col in 'CDEF')
  summary.append(dict(county=c,county_fips=fips[c],president_2024_candidate_votes=sum(cc[c][k]for k in candidates),president_2024_overvotes=cc[c][(None,'Overvotes')],president_2024_undervotes=cc[c][(None,'Undervotes')],president_2024_all_categories=sum(cc[c].values()),registration_2024_cutoff=controls['C'],registration_2024_election_day=controls['D'],registration_2024_total=controls['E'],ballots_2024=controls['F'],president_2024_contexts=sum(k[0]==c for k in native),stats_2024_contexts=sum(k[0]==c for k in st),stats_2024_footer_row=footers[c]['row']))
 for k,r in st.items():
  c,p=k;v={f:number(val(r,col))for f,col in [('cutoff','C'),('election_day','D'),('registered','E'),('ballots','F')]};assert v['cutoff']+v['election_day']==v['registered']
  stats_rows.append(dict(source_id=stats['source_id'],sheet=stats['sheets'][0]['sheet'],source_row=r['row'],county=c,county_fips=fips[c],literal_precinct=p,stats_context_key=f"ID:2024:stats:{fips[c]}:{r['row']}",literal_method_flags=method(p),**v,raw_turnout=val(r,'G'),has_presidential_context=k in native,polling_place=None,source_numeric_precinct_id=None))
 for (c,p),rr in native.items():
  start=rr[0]['row'];key=f'ID:2024:pres:{fips[c]}:{start}';stat=st[(c,p)]
  cv=sum(number(val(r,'G'))for r in rr if val(r,'F')not in non);ov=next(number(val(r,'G'))for r in rr if val(r,'F')=='Overvotes');uv=next(number(val(r,'G'))for r in rr if val(r,'F')=='Undervotes')
  native_rows.append(dict(key=key,county=c,county_fips=fips[c],literal_precinct=p,source_first_row=start,source_last_row=rr[-1]['row'],candidate_votes=cv,overvotes=ov,undervotes=uv,all_categories=cv+ov+uv,literal_method_flags=method(p),source_native_id=p,source_id_scope='literal Precinct field; may be a name or administrative label, not a universal numeric ID',polling_place=None,stats_literal_pair_row=stat['row'],stats_ballots=number(val(stat,'F')),stats_pair_approved=False))
  pairings.append(dict(key=key,county=c,literal_precinct=p,president_source_first_row=start,president_source_last_row=rr[-1]['row'],stats_source_row=stat['row'],race_all_categories=cv+ov+uv,stats_ballots=number(val(stat,'F')),ballots_minus_race=number(val(stat,'F'))-cv-ov-uv))
  for r in rr:candidate_rows.append(dict(year=2024,contest='President',source_id=races['source_id'],archive_member=None,sheet=races['sheets'][0]['sheet'],source_row=r['row'],cell='G'+str(r['row']),key=key,county=c,county_fips=fips[c],literal_precinct=p,literal_party=val(r,'E'),literal_candidate=val(r,'F'),value=number(val(r,'G')),role='noncandidate'if val(r,'F')in non else'named_write_in'if'(Write-In)'in val(r,'F')else'candidate',literal_method_flags=method(p)))
 historical_books={}
 for year in [2020,2022]:
  sid=f'sos-{year}-general-canvass-zip';z=zipfile.ZipFile(io.BytesIO(raw(sid)));assert z.testzip()is None
  for inf in z.infolist():
   archive_inventory.append(dict(source_id=sid,member=inf.filename,bytes=inf.file_size,crc32=f'{inf.CRC:08x}',sha256=H(z.read(inf))))
   name=inf.filename
   if name.endswith('.xlsx')and ('stwd'in name.lower()or'Statewide'in name):
    role='county'if 'cnty'in name.lower()or'County'in name else'precinct';historical_books[(year,role)]=book(z.read(name),sid,name)
 # Abstract archive preserved and CRC verified; not an additive dataset.
 sid='sos-2020-general-abstracts-zip';z=zipfile.ZipFile(io.BytesIO(raw(sid)));assert z.testzip()is None
 for inf in z.infolist():archive_inventory.append(dict(source_id=sid,member=inf.filename,bytes=inf.file_size,crc32=f'{inf.CRC:08x}',sha256=H(z.read(inf))))
 gz(D/'source/historical-workbook-rows.json.gz',list(historical_books.values()));js(D/'source/archive-members.json',archive_inventory)
 shortcounty={c.removesuffix(' County'):c for c in county_names};bycounty={r['county']:r for r in summary};hist_native=[];hist_positions=[];hist_controls=[];hist_findings=[];hist_admin=[]
 specs=[(2020,'Senate_Class_II','Federal','IJKL',6,5,5,4),(2020,'President','Federal','BCDEFGH',6,5,5,4),(2022,'Senate_Class_III','US Sen','BCDEF',6,5,4,3),(2022,'Governor','Gov','BCDEFG',7,6,5,4)]
 for year,contest,sname,columns,cn,cp,pn,pp in specs:
  cb=historical_books[(year,'county')];pb=historical_books[(year,'precinct')];cs=sheet(cb,sname);ps=sheet(pb,sname);cr={r['row']:r for r in cs['rows']};pr={r['row']:r for r in ps['rows']}
  names=[val(cr[cn],col)for col in columns];parties=[val(cr[cp],col)for col in columns]
  assert names==[val(pr[pn],col).strip()for col in columns]and parties==[val(pr[pp],col)for col in columns]
  controls={};state=None
  for r in cs['rows']:
   label=val(r,'A')
   if label=='TOTAL':state=r;break
   if label in shortcounty:controls[shortcounty[label]]=r
  assert len(controls)==44
  parent=None;done=set();known=defaultdict(Counter);foot={};nulls=[];counts=Counter()
  for r in ps['rows']:
   if r['row']<=pn:continue
   label=val(r,'A');vv=[val(r,col)for col in columns]
   if label is None and all(v is None for v in vv):continue
   heading=re.sub(r'(?: \(Continued\)|, cont\.)$','',str(label),flags=re.I)
   if heading in {c.upper()for c in shortcounty}and all(v is None for v in vv):parent=shortcounty[next(c for c in shortcounty if c.upper()==heading)];continue
   role='native'
   if len(done)==44:role='state_or_appendix_control'
   elif label in ['TOTAL','Percentage','Plurality']:role='nonadditive_control'
   elif label=='CO. TOTAL':
    assert parent not in done;done.add(parent);foot[parent]=r;role='county_footer'
   elif label is None:raise ValueError((year,contest,r))
   key=f'ID:{year}:{contest}:{fips[parent]}:{r["row"]}'if role in ['native','county_footer']else f'ID:{year}:{contest}:administrative:{r["row"]}'
   values=[number(x)if re.fullmatch(r'\d+',str(x))else None for x in vv]
   record=dict(year=year,contest=contest,key=key,county=parent if role in ['native','county_footer']else None,county_fips=fips[parent]if role in ['native','county_footer']else None,literal_precinct=label,source_row=r['row'],source_id=pb['source_id'],archive_member=pb['archive_member'],sheet=sname,role=role,literal_method_flags=method(label or ''),candidate_values=values,candidate_votes_known_sum=total(values),candidate_total_complete=all(v is not None for v in values),polling_place=None)
   if role=='native':
    hist_native.append(record);counts[parent]+=1
    for name,v in zip(names,values):
     if v is not None:known[parent][name]+=v
    if None in values:nulls.append(record)
   else:hist_admin.append(record)
   for col,name,party,v in zip(columns,names,parties,values):
    hist_positions.append(dict(year=year,contest=contest,key=key,county=record['county'],literal_precinct=label,source_id=pb['source_id'],archive_member=pb['archive_member'],sheet=sname,source_row=r['row'],cell=col+str(r['row']),literal_candidate=val(pr[pn],col),county_candidate_header=name,literal_party=party,value=v,raw_cell_present=col in r['cells'],raw_resolved_value=val(r,col),role=role,literal_method_flags=record['literal_method_flags']))
  assert len(done)==44 and len(counts)==44
  candidate_totals=[]
  for col,name,party in zip(columns,names,parties):
   value=sum(number(val(r,col))for r in controls.values());assert value==number(val(state,col));candidate_totals.append(dict(candidate=name,literal_party=party,votes=value))
   for c,r in controls.items():
    v=number(val(r,col));assert v==known[c][name]==number(val(foot[c],col)),(year,contest,c,name)
    hist_controls.append(dict(year=year,contest=contest,county=c,county_fips=fips[c],literal_candidate=name,literal_party=party,votes=v,source_id=cb['source_id'],archive_member=cb['archive_member'],sheet=sname,source_row=r['row'],cell=col+str(r['row']),native_known_sum=known[c][name],native_footer_row=foot[c]['row'],native_footer_cell=col+str(foot[c]['row'])))
  prefix={ (2020,'Senate_Class_II'):'senate_2020',(2020,'President'):'president_2020',(2022,'Senate_Class_III'):'senate_2022',(2022,'Governor'):'governor_2022'}[(year,contest)]
  for c in county_names:bycounty[c][prefix+'_candidate_votes']=sum(known[c].values());bycounty[c][prefix+'_native_contexts']=counts[c]
  hist_findings.append(dict(year=year,contest=contest,counties=44,native_rows=sum(counts.values()),candidates=candidate_totals,candidate_votes=sum(x['votes']for x in candidate_totals),null_candidate_cells=sum(v is None for r in nulls for v in r['candidate_values']),null_rows=nulls,all_candidate_native_known_sums_and_footers_equal_county_controls=True))
 # 2020 separate county statistics, independent of contest totals.
 b=historical_books[(2020,'county')];s=sheet(b,'Amend & Stats');cstats={};control=None
 for r in s['rows']:
  label=val(r,'A')
  if label in shortcounty:cstats[shortcounty[label]]=r
  if label=='TOTAL':control=r
 assert len(cstats)==44
 for c,r in cstats.items():
  for field,col in [('registration_2020_cutoff','D'),('registration_2020_election_day','E'),('registration_2020_total','F'),('ballots_2020','G')]:bycounty[c][field]=number(val(r,col))
  bycounty[c]['stats_2020_county_row']=r['row']
 assert all(sum(number(val(r,col))for r in cstats.values())==number(val(control,col))for col in 'DEFG')
 # Native 2020 statistical rows remain source-position identities; duplicate labels are not deduplicated.
 ps=sheet(historical_books[(2020,'precinct')],'Amend & Stats');parent=None;done=set();native20stats=[];admin20stats=[];sf={};ss=defaultdict(Counter)
 for r in ps['rows']:
  if r['row']<=5:continue
  label=val(r,'A');vv=[val(r,col)for col in 'DEFG'];head=re.sub(r'(?: \(Continued\)|, cont\.)$','',label or '',flags=re.I)
  if label is None and all(v is None for v in vv):continue
  if head in {c.upper()for c in shortcounty}and all(v is None for v in vv)and len(done)<44:
   parent=shortcounty[next(c for c in shortcounty if c.upper()==head)];continue
  role='native'if len(done)<44 and label!='CO. TOTAL'else 'state_or_appendix_control'if len(done)==44 else 'county_footer'
  values={field:number(v)if re.fullmatch(r'\d+',str(v))else None for field,v in zip(['cutoff','election_day','registered','ballots'],vv)}
  rec=dict(year=2020,source_id='sos-2020-general-canvass-zip',archive_member=historical_books[(2020,'precinct')]['archive_member'],sheet=ps['sheet'],source_row=r['row'],key=f'ID:2020:stats:{r["row"]}',county=parent if role!='state_or_appendix_control'else None,literal_precinct=label,role=role,literal_method_flags=method(label or ''),**values,raw_turnout=val(r,'H'),literal_cells=r['cells'])
  if role=='native':
   native20stats.append(rec)
   for col,v in zip('DEFG',vv):
    if v is not None:ss[parent][col]+=number(v)
  else:
   admin20stats.append(rec)
   if role=='county_footer':sf[parent]=r;done.add(parent)
 assert len(done)==44 and len(native20stats)==974
 stats20_differences=[]
 for c in county_names:
  for col in 'DEFG':
   expected=number(val(cstats[c],col));foot=number(val(sf[c],col))
   if ss[c][col]!=expected or foot!=expected:stats20_differences.append(dict(county=c,column=col,native_known_sum=ss[c][col],native_footer=foot,separate_county_control=expected))
 gz(D/'native-2020-stats.json.gz',native20stats);gz(D/'administrative-2020-stats.json.gz',admin20stats)
 js(D/'stats2020-reconciliation.json',dict(native_rows=len(native20stats),counties=44,null_cells_by_field={field:sum(r[field]is None for r in native20stats)for field in ['cutoff','election_day','registered','ballots']},differences=stats20_differences,duplicate_literal_labels=[dict(county=c,label=p,count=n)for(c,p),n in Counter((r['county'],r['literal_precinct'])for r in native20stats).items()if n>1],nulls_are_not_zero=True))
 # 2022 statistical registration/method tables; separate Write-In Totals table0 has unexplained stage/scope (Lisa Marie46 versus general67).
 t=Table();t.feed(gzip.decompress((D/'source/stats2022.gz').read_bytes()).decode());gz(D/'source/stats2022-tables.json.gz',t.tables)
 general=next(tab for tab in t.tables if tab[0][1]=='Registered Voters at Cutoff');methods=next(tab for tab in t.tables if tab[0][1]=='Total Ballots Cast');stats22=[]
 for ix,row in enumerate(general[1:],2):
  c=row[0]; vals=[int(v.replace(',',''))for v in row[1:5]]
  stats22.append(dict(table='general_registration',table_row=ix,literal_county=c,cutoff=vals[0],election_day=vals[1],registered=vals[2],ballots=vals[3],raw_turnout=row[5],raw_registration_share=row[6]))
  assert vals[0]+vals[1]==vals[2]
  if c in shortcounty:
   for field,v in zip(['registration_2022_cutoff','registration_2022_election_day','registration_2022_total','ballots_2022'],vals):bycounty[shortcounty[c]][field]=v
 for j in range(1,5):assert sum(int(r[j].replace(',',''))for r in general[1:-1])==int(general[-1][j].replace(',',''))
 for ix,row in enumerate(methods[1:],2):
  c=row[0];values=[int(v.replace(',',''))if re.fullmatch(r'[\d,]+',v)else None for v in row[1:4]]
  stats22.append(dict(table='general_method',table_row=ix,literal_county=c,ballots=values[0],absentee=values[1],early=values[2],raw_ballots=row[1],raw_absentee=row[2],raw_early=row[3],raw_method_share=row[4]))
  if c in shortcounty:
   assert values[0]==bycounty[shortcounty[c]]['ballots_2022']
   bycounty[shortcounty[c]]['absentee_2022']=values[1];bycounty[shortcounty[c]]['early_2022']=values[2];bycounty[shortcounty[c]]['early_2022_raw']=row[3]
 for j in range(1,4):assert sum(int(r[j].replace(',',''))for r in methods[1:-1]if r[j]!='-')==int(methods[-1][j].replace(',',''))
 def rank(rows,field,key):
  ordered=sorted(rows,key=lambda r:(-r[field],r[key]));den=sum(r[field]for r in rows);cum=0;order=[]
  for i,r in enumerate(ordered,1):
   cum+=r[field];order.append(dict(rank=i,key=r[key],votes=r[field],cumulative_votes=cum,share_numerator=r[field],share_denominator=den,cumulative_share_numerator=cum))
  k=next(i for i,r in enumerate(order,1)if 5*r['cumulative_votes']>=4*den);top=sum(r['votes']for r in order[:15]);pre=sum(r['votes']for r in order[:k-1]);cross=order[k-1]
  return dict(denominator=den,unit_count=len(rows),field=field,top15_votes=top,top15_share_exact=f'{top}/{den}',top15_percent=100*top/den,minimum80_count=k,minimum80_votes=cross['cumulative_votes'],minimum80_percent=100*cross['cumulative_votes']/den,preceding_count=k-1,preceding_votes=pre,preceding_percent=100*pre/den,crossing_key=cross['key'],crossing_votes=cross['votes'],remainder_count=len(rows)-k,remainder_votes=den-cross['cumulative_votes'],ordered_priority_keys=[x['key']for x in order[:max(15,k)]],minimum80_keys=[x['key']for x in order[:k]],full_order=order)
 for r in summary:r['key']=r['county_fips']
 rankings={field:rank(summary,field,'key')for field in ['president_2024_candidate_votes','president_2024_all_categories','ballots_2024','registration_2024_total','registration_2024_cutoff','senate_2020_candidate_votes','president_2020_candidate_votes','ballots_2020','registration_2020_total','senate_2022_candidate_votes','governor_2022_candidate_votes','ballots_2022','registration_2022_total']}
 native_rank=rank(native_rows,'candidate_votes','key')
 native_rankings={'2024_president_candidates':native_rank,'2024_president_all_categories':rank(native_rows,'all_categories','key'),'2024_stats_ballots':rank(stats_rows,'ballots','stats_context_key'),'2024_stats_registered':rank(stats_rows,'registered','stats_context_key'),'2024_stats_cutoff':rank(stats_rows,'cutoff','stats_context_key')}
 for contest in ['Senate_Class_III','Governor']:
  nn=[r for r in hist_native if r['year']==2022 and r['contest']==contest];assert all(r['candidate_total_complete']for r in nn)
  native_rankings['2022_'+contest]=rank(nn,'candidate_votes_known_sum','key')
 js(D/'native-rankings.json',native_rankings)
 lookup={r['key']:r for r in native_rows};ordered_rows=[]
 for r in native_rank['full_order']:
  rr=dict(lookup[r['key']],rank=r['rank'],cumulative_votes=r['cumulative_votes'],weight_numerator=r['votes'],weight_denominator=native_rank['denominator'],cumulative_share_numerator=r['cumulative_votes'],minimum80_priority=r['rank']<=native_rank['minimum80_count'])
  ordered_rows.append(rr)
 csvout(D/'native-order.csv',ordered_rows)
 csvout(D/'administrative-2024-stats.csv',[dict(source_id=stats['source_id'],sheet=stats['sheets'][0]['sheet'],source_row=r['row'],county=c,county_fips=fips[c],literal_precinct='Total',role='overlapping_county_statistics_footer',cutoff=number(val(r,'C')),election_day=number(val(r,'D')),registered=number(val(r,'E')),ballots=number(val(r,'F')),raw_turnout=val(r,'G'))for c,r in footers.items()])
 csvout(D/'native-2024-president.csv',native_rows);csvout(D/'native-2024-candidate-positions.csv',candidate_rows);csvout(D/'native-2024-stats.csv',stats_rows);csvout(D/'literal-stats-race-comparisons.csv',pairings)
 gz(D/'historical-native.json.gz',hist_native);gz(D/'historical-candidate-positions.json.gz',hist_positions);gz(D/'historical-administrative-controls.json.gz',hist_admin);csvout(D/'historical-county-candidate-controls.csv',hist_controls);gz(D/'stats2022.json.gz',stats22)
 csvout(D/'county-candidate-2024.csv',[dict(county=c,county_fips=fips[c],literal_party=k[0],literal_candidate=k[1],votes=cc[c][k],role='noncandidate'if k[1]in non else'named_write_in'if'(Write-In)'in k[1]else'candidate')for c in county_names for k in candidate_order])
 rankmap={x['key']:x for x in rankings['president_2024_candidate_votes']['full_order']}
 summary=sorted(summary,key=lambda r:rankmap[r['key']]['rank'])
 for r in summary:r['rank_2024_president']=rankmap[r['key']]['rank'];r['cumulative_2024_president']=rankmap[r['key']]['cumulative_votes']
 csvout(D.parent/'county-turnout.csv',summary)
 p=rankings['president_2024_candidate_votes'];const=[]
 for c in county_names:
  const.append(dict(county=c,county_fips=fips[c],key=fips[c],priority=fips[c]in p['ordered_priority_keys'],president_contexts=[r for r in native_rows if r['county']==c],stats_only_contexts=[r for r in stats_rows if r['county']==c and not r['has_presidential_context']],overlapping_stats_footer_row=footers[c]['row'],native_precinct_id_field='literal Precinct value retained; no separate universal ID supplied',polling_place_status='unavailable in statewide workbooks',current_2026_crosswalk_status='unavailable and not approved',method_partition_status='no separate method field; literal label flags are inventory only'))
 contract=dict(schema_version='idaho-turnout-2',state='ID',election='2024-11-05 General',contest='United States President',status='independently_extracted_pending_peer_and_coordinator_acceptance',candidate_denominator=sum(sums[k]for k in candidates),ranking_geography='985 source-native county/Precinct contexts; 44 county parents are nonadditive grouping only',primary_priority=native_rank,top15_votes=native_rank['top15_votes'],top15_share_exact=native_rank['top15_share_exact'],minimum80_count=native_rank['minimum80_count'],minimum80_votes=native_rank['minimum80_votes'],preceding_count=native_rank['preceding_count'],preceding_votes=native_rank['preceding_votes'],crossing_key=native_rank['crossing_key'],remainder_count=native_rank['remainder_count'],remainder_votes=native_rank['remainder_votes'],ordered_priority_keys=native_rank['ordered_priority_keys'],complete_order=native_rank['full_order'],ordered_remainder_keys=[r['key']for r in native_rank['full_order'][native_rank['minimum80_count']:]],county_sensitivity=p,complete_county_order=p['full_order'],native_priority=native_rank,all_county_constituents=const,source_candidate_universe=[dict(party=k[0],candidate=k[1],votes=sums[k])for k in candidates],noncandidate_categories=[dict(party=k[0],category=k[1],votes=sums[k])for k in candidate_order if k[1]in non],stats_only_contexts=[r for r in stats_rows if not r['has_presidential_context']],historical_native_path='historical-native.json.gz',historical_administrative_path='historical-administrative-controls.json.gz',historical_nulls_do_not_become_zero=True,current_geography_approved=False,priority_accepted=False)
 native_lookup={r['key']:r for r in native_rows};ordered_native=native_rank['full_order'];priority_keys=set(native_rank['ordered_priority_keys'])
 contract['top15_keys']=[r['key']for r in ordered_native[:15]]
 contract['ordered_parent_keys']=list(dict.fromkeys(native_lookup[r['key']]['county_fips']for r in ordered_native))
 contract['ordered_child_keys_by_parent']={fips[c]:[r['key']for r in ordered_native if native_lookup[r['key']]['county']==c]for c in county_names}
 contract['ordered_priority_child_keys_by_parent']={fips[c]:[r['key']for r in ordered_native if native_lookup[r['key']]['county']==c and r['key']in priority_keys]for c in county_names}
 contract['ordered_remainder_child_keys_by_parent']={fips[c]:[r['key']for r in ordered_native if native_lookup[r['key']]['county']==c and r['key']not in priority_keys]for c in county_names}
 contract['source_object_paths']=dict(full_native_order='native-order.csv',candidate_positions='native-2024-candidate-positions.csv',statistics_administrative='administrative-2024-stats.csv',stats='native-2024-stats.csv',literal_pair_residuals='literal-stats-race-comparisons.csv',complete_races_OOXML='source/2024-races-rows.json.gz',complete_stats_OOXML='source/2024-stats-rows.json.gz',historical_candidate_positions='historical-candidate-positions.json.gz',historical_county_controls='historical-county-candidate-controls.csv',historical_native='historical-native.json.gz',historical_administrative='historical-administrative-controls.json.gz',historical_nulls='historical-reconciliation.json',native2020stats='native-2020-stats.json.gz',administrative2020stats='administrative-2020-stats.json.gz',county2022method_stats='stats2022.json.gz',raw_original_references='source/reused-originals.json')
 contract['tie_rule']='Descending candidate votes, then full source-position key in ascending Unicode lexical order. County FIPS precedes source row within that key; source row is a string. No tie at the 527/528/529 crossing.'
 contract['coverage']=dict(counties=44,primary_contexts=985,stats_contexts=986,stats_only_contexts=1,primary_category_positions=12805,named_candidate_positions=10835,native_minimum80=528,native_remainder=457)
 for c in const:
  c['county_sensitivity_priority']=c.pop('priority');c['primary_priority_child_count']=len(contract['ordered_priority_child_keys_by_parent'][c['key']]);c['primary_remainder_child_count']=len(contract['ordered_remainder_child_keys_by_parent'][c['key']])
 js(D/'priority-set.json',contract);js(D/'rankings.json',rankings);js(D/'historical-reconciliation.json',hist_findings);js(D/'source/reused-originals.json',used)
 # Reconcile with coordinator preflight only after independent extraction.
 preflight=json.loads((D.parent/'coordinator-primary-preflight.json').read_text());hp=json.loads((D.parent/'coordinator-historical-native-preflight.json').read_text())
 assert preflight['candidate_total']==p['denominator']==905057
 assert {(x['raw_party'],x['literal_candidate']):x['votes']for x in preflight['president_candidate_categories']}=={k:sums[k]for k in candidates}
 assert sorted((r['county'],r['literal_precinct'],r['ballots_minus_race'])for r in pairings if r['ballots_minus_race'])==sorted((r['literal_key'][0],r['literal_key'][1],r['ballot_minus_president_category'])for r in preflight['paired_nonzero_residuals'])
 for f in hist_findings:
  x=next(x for x in hp['selected_contests']if x['year']==f['year']and x['contest']==f['contest']);assert f['native_rows']==x['native_source_rows']and f['candidate_votes']==x['statewide_candidate_total']and f['null_candidate_cells']==x['missing_native_candidate_cells']
 js(D/'independent-control-check.json',dict(preflight_primary_sha256=H((D.parent/'coordinator-primary-preflight.json').read_bytes()),preflight_historical_sha256=H((D.parent/'coordinator-historical-native-preflight.json').read_bytes()),independent_extraction=True,primary_candidate_category_agreement=True,all_7_native_residuals_exact_agreement=True,historical_controls_and_null_counts_agree=True,peer_agreement_status='pending actual peer ID and independently published files',nonzero_native_residuals=[r for r in pairings if r['ballots_minus_race']],stats_only=[r for r in stats_rows if not r['has_presidential_context']]))
 js(D/'method-label-inventory.json',dict(qualifier='Literal text flags only. Numeric/geographic contexts may already include absentee/early votes. Do not sum methods from label flags or infer Election Day as remainder.',primary_2024=[r for r in native_rows if r['literal_method_flags']],stats_2024=[r for r in stats_rows if r['literal_method_flags']],historical=[r for r in hist_native if r['literal_method_flags']],stats2020=[r for r in native20stats if r['literal_method_flags']],county2022_methods=[r for r in stats22 if r['table']=='general_method']))
 js(D/'summary.json',dict(county_rank=p,native_rank=native_rank,statewide_fields={k:total(r[k]for r in summary)for k in summary[0]if isinstance(summary[0][k],int)and k not in ['rank_2024_president','cumulative_2024_president','stats_2024_footer_row','stats_2020_county_row']},candidate_universe=contract['source_candidate_universe'],historical=hist_findings))
 print(json.dumps(dict(county_priority={k:v for k,v in p.items()if k!='full_order'},native_priority={k:v for k,v in native_rank.items()if k not in ['full_order','ordered_priority_keys','minimum80_keys']},historical=[{k:v for k,v in x.items()if k!='null_rows'}for x in hist_findings]),indent=2))
if __name__=='__main__':main()
