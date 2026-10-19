#!/usr/bin/env python3
"""Independent original-byte NE extraction. Does not read coordinator/peer derivatives.
Requires Poppler; xlrd==2.0.2 (external environment, not vendored).
"""
import collections,csv,gzip,hashlib,html,io,json,re,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
if Path('/tmp/snn-xls-reading-libs').exists():sys.path.insert(0,'/tmp/snn-xls-reading-libs')
import xlrd
BASE=Path(__file__).resolve().parent;DATA=BASE.parent;NEWS=DATA/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(path,value):
 (BASE/path).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def jsonl(path,rows):
 (BASE/path).write_bytes(gzip.compress(b''.join((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode() for r in rows),mtime=0))
def csvout(path,rows):
 with (BASE/path).open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
class Originals:
 def __init__(self):
  self.manifest=json.loads((NEWS/'manifest.json').read_text());self.used={};self.byid={r['id']:r for r in self.manifest}
 def get(self,key):
  a=self.byid[key];p=NEWS/a['asset'];z=p.read_bytes();b=gzip.decompress(z)
  assert sha(z)==a['stored_sha256'] and sha(b)==a['raw_sha256'] and len(b)==a['bytes'],key
  self.used[key]={**a,'shared_path':str(p.relative_to(DATA.parent)),'stored_bytes':len(z),'reference_only':True}
  return b
def pdftext(b):
 with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
  f.write(b);f.flush()
  return subprocess.check_output(['pdftotext','-layout',f.name,'-']).decode()
def clean(s):return html.unescape(re.sub('<[^>]*>','',s)).replace('\xa0',' ').strip()
def attrs(s):return {m[1]:html.unescape(m[3])for m in re.finditer(r'([\w:-]+)\s*=\s*([\'"])(.*?)\2',s,re.S)}
def cells(s):return [{'attributes':attrs(m[1]),'text':clean(m[2]),'inner_html':m[2]}for m in re.finditer(r'<td\b([^>]*)>(.*?)</td>',s,re.S|re.I)]
def pairrow(key,county,label,A,B,source_id,pointer,**more):
 return dict(key=key,county=county,label=label,A=A,B=B,pair_votes=A+B,source_id=source_id,source_pointer=pointer,**more)
def canvasses(o):
 pages={};rawtables=[];tables={}
 for y in [2024,2022,2020]:
  text=pdftext(o.get(f'sos-{y}-canvass'));jsonl(f'extracts/canvass-{y}-pages.jsonl.gz',[dict(page=i+1,text=p)for i,p in enumerate(text.split('\f')[:-1])]);pages[y]=text.split('\f')
 # Explicit pages, never congressional district presidential tables.
 config=[('senate2024special',2024,[17],['Pete Ricketts|Republican','Preston Love Jr.|Democratic']),
  ('senate2024regular',2024,[16],['Deb Fischer|Republican','Dan Osborn|By Petition','Write-In Scatterings|']),
  ('president2024',2024,[11,12],['Donald J. Trump & JD Vance|Republican','Kamala D. Harris & Tim Walz|Democratic','Chase Oliver & Mike ter Maat|Libertarian','Cornel West & Melina Abdullah|Legal Marijuana NOW','Jill Stein & Samson Kpadenou|BY PETITION','Write-In Scatterings|']),
  ('governor2022',2022,[13,14],['Jim Pillen & Joe Kelly|Republican','Carol Blood & Al Davis|Democratic','Scott Zimmerman & Jason Blumenthal|Libertarian','Write-In Scatterings|']),
  ('senate2020',2020,[16,17],['Ben Sasse|Republican','Chris Janicek|Democratic','Gene Siadek|Libertarian','Preston Love Jr.|Write-In','Write-In Scatterings|'])]
 def parse(name,y,pp,columns):
  n=len(columns);entries={};control=None;positions=[]
  pat=re.compile(r'([A-Za-z][A-Za-z .\'-]*?)\s{2,}('+r'\s+'.join([r'\d[\d,]*']*n)+r')(?=\s{2,}|$)')
  for page in pp:
   for line_no,line in enumerate(pages[y][page-1].splitlines(),1):
    if line.startswith('General Election'):continue
    for m in pat.finditer(line):
     county=m[1].strip();v=[int(x.replace(',',''))for x in m[2].split()]
     r=dict(table=name,year=y,page=page,line=line_no,column_start=m.start()+1,county_literal=county,values=v,raw_line=line,columns=columns)
     positions.append(r)
     if county in ['Total','Statewide Total']:
      assert control is None;control=v
     else:
      assert county not in entries,(name,county);entries[county]=v
  assert len(entries)==93,(name,len(entries));assert control is not None
  sums=[sum(v[i]for v in entries.values())for i in range(n)];assert sums==control,(name,sums,control)
  rawtables.extend(positions);tables[name]=dict(year=y,pages=pp,columns=columns,county=entries,state=control)
 for args in config:parse(*args)
 for y,regpages,methpages,rc,mc in [
  (2024,[6,7],[8,9],['Precincts','Republican','Democratic','Libertarian','Legal Marijuana NOW','No Labels Nebraska','Nonpartisan','Total'],['Polling Place','Early Voting','All Mail Precincts','Provisional Ballot','Military & Overseas','New/Former Resident','Total Voting']),
  (2022,[6,7],[8,9],['Precincts','Republican','Democratic','Libertarian','Legal Marijuana NOW','Nonpartisan','Total'],['At Polls','All Mail Precincts','Provisional','Early Voting','Military & Overseas','Total Voting']),
  (2020,[7,8],[9,10],['Precincts','Republican','Democratic','Libertarian','Nonpartisan','Total'],['At Polls','All Mail Precincts','Provisional','Early Voting','Military & Overseas','New/Former Resident','Total Voting'])]:
  parse(f'registration{y}',y,regpages,rc);parse(f'votingmethod{y}',y,methpages,mc)
  assert all(sum(v[1:-1])==v[-1]for v in tables[f'registration{y}']['county'].values())
  assert all(sum(v[:-1])==v[-1]for v in tables[f'votingmethod{y}']['county'].values())
 jsonl('extracts/canvass-original-rows.jsonl.gz',rawtables);dump('extracts/state-controls.json',tables)
 return tables
def nativehtml(o,tables):
 observations=[];selected=[];source_summary=[]
 originals=[a for a in o.manifest if a['id'].startswith('sos-2024-special-native-archive-cty-') and a.get('status')==200]
 assert len(originals)==93
 for a in originals:
  b=o.get(a['id']);s=b.decode();cid=re.search(r'[?&]cty=(\d+)',html.unescape(a['url']))[1]
  h=re.search(r"<tr id='ContentPlaceHolder1xuwgCounty_r_0'.*?</tr>",s,re.S)[0]
  county=clean(re.search(r'<h1>(.*?)</h1>',h,re.S)[1]);assert county.endswith(' County');county=county[:-7]
  headers=list(re.finditer(r"<tr id='ContentPlaceHolder1xuwgPrecinct_r_(\d+)'[^>]*>.*?</tr>",s,re.S))
  complete=s.rstrip().endswith('</html>')
  if county in ['Douglas','Lancaster']:assert len(b)==1048576 and not complete
  else:assert complete
  for index,h in enumerate(headers):
   ordinal=h[1];hc=cells(h[0]);label=hc[0]['text'];native=hc[1]['text']
   tail=s[h.end():headers[index+1].start() if index+1<len(headers) else len(s)]
   children=[]
   for candidate in [0,1]:
    m=re.search(r"<tr id='ContentPlaceHolder1xuwgPrecinct_r_"+ordinal+'_'+str(candidate)+r"'[^>]*>(.*?)(?:</tr>|$)",tail,re.S)
    cc=cells(m[1])if m else [];closed=bool(m and '</tr>'in m[0]);vote=None
    if len(cc)>3 and re.fullmatch(r'[\d,]+',cc[3]['text']):vote=int(cc[3]['text'].replace(',',''))
    children.append(dict(row_id=f'ContentPlaceHolder1xuwgPrecinct_r_{ordinal}_{candidate}',complete=closed,cells=cc,
      candidate=cc[2]['text']if len(cc)>2 else None,party_code=cc[0]['text']if cc else None,votes=vote,
      raw_row=m[0]if m else None))
   r=dict(source_id=a['id'],raw_sha256=a['raw_sha256'],county=county,county_id_literal=cid,
    header_row_id=f'ContentPlaceHolder1xuwgPrecinct_r_{ordinal}',header_character_start=h.start(),header_character_end=h.end(),
    native_id_literal=native,label=label,header_cells=hc,raw_header=h[0],children=children,
    entity_complete=complete,role='administrative_countywide'if native=='_TOT'else'native',source_clock=clean(re.search(r'<span id="lblLastUpdated">(.*?)</span>',s)[1]),source_clock_zone=None)
   observations.append(r)
   if complete and native!='_TOT':
    assert all(c['complete'] and c['votes']is not None for c in children)
    assert [c['party_code']for c in children]==['REP','DEM']
    selected.append(pairrow(f'NE:2024-special:html:{cid}:{native}',county,label,children[1]['votes'],children[0]['votes'],a['id'],r['header_row_id'],native_id_literal=native,
     generic_writeins=None,ballots=None,method=None,under=None,over=None,registration=None))
  sums=[sum(c['children'][j]['votes']for c in observations if c['source_id']==a['id'] and c['role']=='native' and all(k['votes']is not None for k in c['children']))for j in [0,1]]
  if complete:assert sums==tables['senate2024special']['county'][county]
  admin=next(r for r in observations if r['source_id']==a['id'] and r['role']=='administrative_countywide')
  # _TOT is a literal administrative observation (often zero), not the county control.
  countycontrol=[]
  for j in [0,1]:
   cm=re.search(r"<tr id='ContentPlaceHolder1xuwgCounty_r_0_"+str(j)+r"'[^>]*>(.*?)</tr>",s,re.S);assert cm
   countycontrol.append(int(cells(cm[1])[3]['text'].replace(',','')))
  assert countycontrol==tables['senate2024special']['county'][county]
  source_summary.append(dict(source_id=a['id'],county=county,county_id_literal=cid,complete=complete,native_headers=len(headers)-1,known_complete_pair_sums=sums,county_control=countycontrol,administrative_countywide=[c['votes']for c in admin['children']]))
 jsonl('extracts/html-original-contexts.jsonl.gz',observations);dump('extracts/html-coverage.json',source_summary)
 assert len(selected)==895 and len(observations)==1224
 return selected,observations
def douglas(o,tables):
 rawrows=[];contexts=[];selected=[];bookmeta=[]
 configs={2024:[('U.S. Senator - 2-Yr Term','senate2024special'),('U.S. Senator','senate2024regular'),('U.S. President','president2024')],2022:[('Governor','governor2022')],2020:[('U.S. Senator','senate2020')]}
 for y,config in configs.items():
  sid=f'county-douglas-{y}-native-xls';book=xlrd.open_workbook(file_contents=o.get(sid),formatting_info=True)
  meta=dict(source_id=sid,sheets=[dict(name=s.name,rows=s.nrows,columns=s.ncols)for s in book.sheets()],instructions=[dict(row=i+1,values=book.sheet_by_name('Instructions').row_values(i))for i in range(book.sheet_by_name('Instructions').nrows)])
  bookmeta.append(meta)
  for sheet,contest in config:
   sh=book.sheet_by_name(sheet);head=sh.row_values(1);footer=[i for i in range(sh.nrows)if sh.cell_value(i,0)in ['Total','Totals']];assert len(footer)==1;end=footer[0]
   for i in range(sh.nrows):rawrows.append(dict(source_id=sid,contest=contest,sheet=sheet,row=i+1,values=sh.row_values(i),types=list(sh.row_types(i))))
   assert all(all(v==''for v in sh.row_values(i))for i in range(end+1,sh.nrows))
   countcols=[i for i,c in enumerate(head)if c and i>0 and c!='% of Vote']
   candcols=[i for i in countcols if head[i]not in ['Total Votes','Over Votes','Under Votes']]
   namedcols=candcols[:-1]if contest=='senate2024special'else candcols
   assert [int(sh.cell_value(end,j))for j in namedcols]==tables[contest]['county']['Douglas']
   for j in countcols:assert sum(sh.cell_value(i,j)for i in range(2,end))==sh.cell_value(end,j)
   totalcol=head.index('Total Votes');overcol=head.index('Over Votes');undercol=head.index('Under Votes')
   for i in range(2,end):
    v=sh.row_values(i);fields={head[j]:int(v[j])for j in countcols}
    assert sum(v[j]for j in candcols)==v[totalcol]
    ctx=dict(source_id=sid,county='Douglas',year=y,contest=contest,label=v[0],sheet=sheet,row=i+1,fields=fields,method=None,
     candidate_columns=[head[j]for j in candcols],candidate_counts=[int(v[j])for j in candcols],ballot_reconstruction=int(v[totalcol]+v[overcol]+v[undercol]))
    contexts.append(ctx)
    if contest=='senate2024special':
     selected.append(pairrow(f'NE:2024-special:douglas-biff:{v[0]}','Douglas',v[0],int(v[candcols[1]]),int(v[candcols[0]]),sid,dict(sheet=sheet,row=i+1),native_id_literal=None,
      generic_writeins=int(v[candcols[-1]]),ballots=None,ballot_reconstruction=ctx['ballot_reconstruction'],method=None,under=int(v[undercol]),over=int(v[overcol]),registration=None))
  summary=pdftext(o.get(f'county-douglas-{y}-summary-pdf'));jsonl(f'extracts/douglas-{y}-summary-pages.jsonl.gz',[dict(page=i+1,text=p)for i,p in enumerate(summary.split('\f')[:-1])])
 jsonl('extracts/douglas-original-rows.jsonl.gz',rawrows);jsonl('extracts/douglas-native-contexts.jsonl.gz',contexts);dump('extracts/douglas-workbooks.json',bookmeta)
 assert len(contexts)==1167 and len(selected)==233
 return selected,contexts
def lancaster(o,tables):
 sid='county-lancaster-2024-final-precinct-pdf-actual-archive';text=pdftext(o.get(sid));pp=text.split('\f')[:-1];assert len(pp)==1431
 jsonl('extracts/lancaster-pages.jsonl.gz',[dict(page=i+1,text=p)for i,p in enumerate(pp)])
 stats=[];contexts=[];selected=[]
 contests={'US President':'president2024','US Senator 6 YR':'senate2024regular','US Senator 2 YR':'senate2024special'}
 def fields(block):
  result={}
  for line in block.splitlines():
   m=re.fullmatch(r'\s*(.*?)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s*',line)
   if m:
    name=m[1];assert name not in result;result[name]=[int(m[j].replace(',',''))for j in range(2,6)]
  return result
 for page,p in enumerate(pp,1):
  label=re.search(r'Lancaster County, Nebraska\s*\n\s*\n([^\n]+)',p)[1].strip()
  foot=re.search(r'Precinct Summary - (.*?)\s+(\d[\d,]*) of 1,431',p);assert foot and int(foot[2].replace(',',''))==page
  if re.search(r'^Statistics\s+TOTAL',p,re.M):
   block=p.split('Statistics',1)[1].split('US President',1)[0];f=fields(block)
   reg=int(re.search(r'Registered Voters - Total\s+(\d[\d,]*)',block)[1].replace(',',''))
   stats.append(dict(label=label,page=page,registered=reg,methods=['TOTAL','Election Day','Early Voting','Provisional'],fields=f,raw_block=block,source_id=sid))
  for name,contest in contests.items():
   m=re.search(r'^\s*'+re.escape(name)+r'\s*$',p,re.M)
   if not m:continue
   end=re.search(r'^\s*Contest Totals\s+.*$',p[m.end():],re.M);assert end
   block=p[m.start():m.end()+end.end()];f=fields(block)
   candidates=[k for k in f if k not in ['Not Assigned','Total Votes Cast','Overvotes','Undervotes','Contest Totals']]
   for v in f.values():assert v[0]==sum(v[1:])
   for j in range(4):
    assert sum(f[k][j]for k in candidates)==f['Total Votes Cast'][j]
    assert f['Write-In Totals'][j]==f['Not Assigned'][j]
    assert sum(f[k][j]for k in ['Total Votes Cast','Overvotes','Undervotes'])==f['Contest Totals'][j]
   ctx=dict(source_id=sid,county='Lancaster',contest=contest,contest_literal=name,label=label,page=page,
    methods=['TOTAL','Election Day','Early Voting','Provisional'],fields=f,candidate_columns=candidates,
    raw_block=block,clock=foot[1],clock_zone=None)
   contexts.append(ctx)
   if contest=='senate2024special':
    selected.append(pairrow(f'NE:2024-special:lancaster-pdf:page-{page}','Lancaster',label,f['Dem Preston Love Jr.'][0],f['Rep Pete Ricketts'][0],sid,dict(page=page),native_id_literal=None,
     generic_writeins=f['Write-In Totals'][0],ballots=f['Contest Totals'][0],method='TOTAL; ED/Early/Provisional retained separately',under=f['Undervotes'][0],over=f['Overvotes'][0],registration=None))
 for contest in contests.values():
  subset=[c for c in contexts if c['contest']==contest];names=subset[0]['candidate_columns'];totals=[sum(c['fields'][n][0]for c in subset)for n in names]
  assert (totals[:-1]if contest=='senate2024special'else totals)==tables[contest]['county']['Lancaster']
 index={s['label']:s for s in stats};assert len(index)==199
 for ctx in contexts:assert ctx['fields']['Contest Totals']==index[ctx['label']]['fields']['Ballots Cast - Total']
 for r in selected:
  r['registration']=index[r['label']]['registered'];r['blank']=index[r['label']]['fields']['Ballots Cast - Blank'][0]
 jsonl('extracts/lancaster-native-contexts.jsonl.gz',contexts);dump('extracts/lancaster-statistics.json',stats)
 assert len(selected)==198 and len(contexts)==595
 resident=[c for c in contexts if c['label']=='New or Former Resident'];assert len(resident)==1
 dump('extracts/presidential-only-resident.json',dict(president=resident[0],Senate_special=None,Senate_regular=None,reason='No Senate section in original; unavailable, not imputed zero.'))
 return selected,contexts
def current(o):
 text=pdftext(o.get('sos-final-general-candidate-pdf'));page=text.split('\f')[0]
 jsonl('extracts/current-final-list-pages.jsonl.gz',[dict(page=i+1,text=p)for i,p in enumerate(text.split('\f')[:-1])])
 names=[('Pete Ricketts','Republican'),('Mike Marvin','Legal Marijuana NOW'),('Robin Richards','Nebraska Working People'),('Chuck Conboy','America First'),('Dan Osborn','By Petition')]
 rows=[]
 for n,party in names:
  lines=[(i,line)for i,line in enumerate(page.splitlines(),1)if n in line];assert len(lines)==1
  # The party column wraps NOW and People onto the following line.
  lineindex=lines[0][0]-1;partytext=page.splitlines()[lineindex][66:86].strip()
  following=page.splitlines()[lineindex+1]
  if following[66:86].strip()in ['NOW','People']:partytext+=' '+following[66:86].strip()
  assert party==partytext,(n,partytext)
  rows.append(dict(candidate=n,party_literal=party,source_id='sos-final-general-candidate-pdf',page=1,line=lines[0][0],raw_line=lines[0][1],party_continuation_line=following if partytext!=lines[0][1][66:86].strip() else None,candidate_result_id=None))
 # Preserve current source codes exactly, including shared contest ID and NOW/Now difference.
 catalog=json.loads(o.get('sos-enr-observed-candidates'));assert len(catalog['d'])==625
 setup=[r for r in catalog['d']if 'For United States Senator' in r.get('desc','')]
 assert len(setup)==5 and {r['ID']for r in setup}=={148}
 dump('extracts/current-catalog-original.json',catalog)
 dump('extracts/current-final-roster.json',dict(rows=rows,setup_rows=setup,publication='Final Statewide General Candidate Filing List 9.11.26',complete_later_withdrawal_or_writein_audit=False,legal_outcome='unique highest candidate total; equal highest requires statutory tie process',setup_is_counts=False))
 for key in ['sos-2026-election-parent','sos-2026-general-certification-notice-parent','sos-2026-general-certification-notice-pdf','sos-enr','sos-enr-statewide','sos-enr-linked-bundle','sos-previous-elections','county-results','county-douglas-current-linked-home','county-douglas-results-archive',
  'county-lancaster-2024-parent','county-lancaster-2024-precinct-final','county-lancaster-observed-final-pdf-cdx',
  'sos-2024-general-statewide-actual-archive-20241106','sos-2024-observed-special-county-archive-20241204','sos-2024-observed-native-special-pages-cdx','sos-2024-observed-turnout-archive-20241211','sos-2024-observed-media-archive-20241106','sos-2024-observed-public-csv-routes-cdx']:
  if key in o.byid:o.get(key)
 return rows
def main():
 o=Originals();tables=canvasses(o);h,obs=nativehtml(o,tables);d,dc=douglas(o,tables);l,lc=lancaster(o,tables);roster=current(o)
 selected=h+d+l;assert len(selected)==1326 and len({r['key']for r in selected})==1326
 counties=sorted(tables['senate2024special']['county']);assert len(counties)==93
 # Census original codes; never enumerate names to manufacture FIPS.
 census=DATA/'turnout/source/census-county-codes.body.gz';receipt=DATA/'turnout/source/census-county-codes.receipt.json'
 cr=json.loads(receipt.read_text());cz=census.read_bytes();cb=gzip.decompress(cz)
 assert sha(cb)==cr['raw_sha256']=='9f6e5f6eb6ac2f5e9a36d5fd01dec77991bddc75118f748a069441a4782970d6'and sha(cz)==cr['stored_sha256']
 censusrows=list(csv.DictReader(io.StringIO(cb.decode('utf-8-sig')),delimiter='|'))
 fips={r['COUNTYNAME'].removesuffix(' County'):r['STATEFP']+r['COUNTYFP']for r in censusrows if r['STATE']=='NE'}
 assert set(fips)==set(counties)and fips['McPherson']=='31117'and fips['Madison']=='31119'
 dump('source/census-original-reference.json',dict(receipt=cr,path=str(census.relative_to(DATA.parent)),receipt_path=str(receipt.relative_to(DATA.parent)),receipt_sha256=sha(receipt.read_bytes()),reference_only=True,independently_parsed=True,rows=[r for r in censusrows if r['STATE']=='NE']))
 for r in selected:r['county_fips']=fips[r['county']]
 for name in counties:
  unit=[r for r in selected if r['county']==name]
  assert [sum(r[k]for r in unit)for k in ['B','A']]==tables['senate2024special']['county'][name]
  assert len(unit)==tables['registration2024']['county'][name][0]
 selected.sort(key=lambda r:(-r['pair_votes'],r['key']));total=sum(r['pair_votes']for r in selected);cum=0
 for rank,r in enumerate(selected,1):
  cum+=r['pair_votes'];r.update(rank=rank,cumulative_pair_votes=cum,weight=r['pair_votes']/total,priority=(cum-r['pair_votes'])*5<total*4)
 jsonl('extracts/native-special.jsonl.gz',selected)
 csvout('native-baselines.csv',[{k:r.get(k)for k in ['key','county','county_fips','label','A','B','pair_votes','generic_writeins','ballots','ballot_reconstruction','blank','method','under','over','registration','rank','weight','priority']}for r in selected])
 # Raw administrative and incomplete alternate contexts retained in full.
 alternative=[r for r in obs if r['role']=='administrative_countywide'or not r['entity_complete']]
 assert len(alternative)==329;jsonl('extracts/administrative-partial-alternatives.jsonl.gz',alternative)
 countyrows=[];long=[]
 for name in counties:
  row=dict(county=name,county_fips=fips[name])
  for contest in ['senate2024special','senate2024regular','president2024','governor2022','senate2020']:
   t=tables[contest];v=t['county'][name]
   for i,col in enumerate(t['columns']):
    cand,party=col.split('|');long.append(dict(county=name,county_fips=fips[name],contest=contest,year=t['year'],candidate=cand,party_literal=party,votes=v[i],column_ordinal=i+1,all_source_candidate_votes=sum(v),source_id=f'sos-{t["year"]}-canvass',pages=';'.join(map(str,t['pages']))))
    row[f'{contest}_candidate{i+1}']=v[i]
   row[f'{contest}_source_total']=sum(v);row[f'{contest}_A']=v[1];row[f'{contest}_B']=v[0];row[f'{contest}_pair_votes']=v[0]+v[1]
   row[f'{contest}_A_share']=v[1]/(v[0]+v[1]);row[f'{contest}_A_minus_B']=v[1]-v[0]
  for y in [2024,2022,2020]:
   row[f'registered_{y}']=tables[f'registration{y}']['county'][name][-1];row[f'voting_total_{y}']=tables[f'votingmethod{y}']['county'][name][-1];row[f'precincts_{y}']=tables[f'registration{y}']['county'][name][0]
  row['special_generic_writeins_statewide_scope']='unknown; local observations separate';countyrows.append(row)
 csvout('../county-baselines.csv',countyrows);csvout('county-candidates.csv',long)
 dump('source/reused-originals.json',dict(receipts=list(o.used.values()),ledger=dict(path='data/news/manifest.json',sha256=sha((NEWS/'manifest.json').read_bytes()),bytes=(NEWS/'manifest.json').stat().st_size),selection='Independent extraction directly from these gzip originals; no coordinator/peer derived counts read.'))
 priority=[r for r in selected if r['priority']]
 dump('extracts/independent-controls.json',dict(counties=93,native=1326,A=sum(r['A']for r in selected),B=sum(r['B']for r in selected),pair=total,priority_count=len(priority),priority_sum=sum(r['pair_votes']for r in priority),previous_sum=sum(r['pair_votes']for r in priority[:-1]),top15=sum(r['pair_votes']for r in selected[:15]),crossing=priority[-1],administrative_partial=329,douglas_contexts=len(dc),lancaster_contexts=len(lc),current_candidates=len(roster)))
 print(json.dumps(dict(counties=93,native=len(selected),pair=total,priority=len(priority),sum=sum(r['pair_votes']for r in priority))))
if __name__=='__main__':main()
