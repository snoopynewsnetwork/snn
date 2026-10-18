#!/usr/bin/env python3
"""Offline, source-scoped inspection. Does not collect live data or allocate votes.
Run with requests/beautifulsoup4/pypdf installed outside the repository.
"""
import collections,csv,datetime,gzip,hashlib,io,json,pathlib,re,xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from pypdf import PdfReader
ROOT=pathlib.Path(__file__).resolve().parents[2];OUT=ROOT/'data/results-sources';SRC=OUT/'source';EX=OUT/'extracts';EX.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def js(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def gzwrite(p,x):p.write_bytes(gzip.compress(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
def body(r):
 p=ROOT/r['body_path'];return gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
def receipt(n):return js(SRC/(n+'.receipt.json'))
def shared_body_path(p,r):
 for k in ['stored_path','asset','original_path']:
  v=r.get(k)
  if not v:continue
  for q in [p.parent.parent/v,ROOT/v,p.parent/v]:
   if q.is_file():return q
 return None

def reuse_identical():
 # Canonical existing peer source entities; no mutable peer aggregates are dependencies.
 canonical={};refs={}
 for group in ['data/turnout/source','data/baselines/source']:
  for p in sorted((ROOT/group).glob('*.receipt.json')):
   r=js(p);q=shared_body_path(p,r)
   if q and r.get('raw_sha256'):
    canonical.setdefault(r['raw_sha256'],q);refs.setdefault(r['raw_sha256'],{'receipt_path':str(p.relative_to(ROOT)),'original_receipt':r})
 for r in js(ROOT/'data/news/manifest.json'):
  q=ROOT/'data/news'/r['asset']
  if q.exists():canonical.setdefault(r['raw_sha256'],q);refs.setdefault(r['raw_sha256'],{'receipt_path':'data/news/manifest.json','original_receipt':r})
 verified={};records=[js(p) for p in sorted(SRC.glob('*.receipt.json'))]
 for r in records:
  h=r.get('raw_sha256')
  if not h:continue
  current=ROOT/r['body_path'];target=canonical.get(h,current)
  if h not in verified:
   v=target.read_bytes();v=gzip.decompress(v) if target.suffix=='.gz' else v;assert sha(v)==h,(r['id'],target);assert len(v)==r['raw_bytes'];verified[h]=True
  canonical.setdefault(h,target)
  target=canonical[h]
  r.update(body_path=str(target.relative_to(ROOT)),stored_sha256=sha(target.read_bytes()),stored_bytes=target.stat().st_size)
  if target!=current:r['storage']='immutable exact SHA256 entity reuse; own observation receipt retained, no duplicate original'
  if h in refs:r['reused_original_reference']=refs[h]['receipt_path']
  dump(SRC/(r['id']+'.receipt.json'),r)
 used={r.get('body_path') for r in records}
 for p in SRC.glob('*.body.gz'):
  if str(p.relative_to(ROOT)) not in used:p.unlink()
 return records

def parse_vr(r):
 b=body(r);sp=BeautifulSoup(b,'html.parser');tables=sp.select('table.DetailResults')
 if not tables:return None
 containers=[]
 for i,t in enumerate(tables):
  parent=t
  while parent.parent and not parent.find('input',class_='favoriteCheckBox'):parent=parent.parent
  label=parent.find('label',attrs={'for':re.compile('^favorite-')});inp=parent.find('input',class_='favoriteCheckBox')
  cells=[]
  for ri,tr in enumerate(t.find_all('tr')):
   cells.append({'row_position_0based':ri,'attrs':dict(tr.attrs),'cells':[{'cell_position_0based':ci,'tag':td.name,'attrs':dict(td.attrs),'text':td.get_text(' ',strip=True),'text_native':td.get_text(),'html':td.decode_contents()} for ci,td in enumerate(tr.find_all(['td','th'],recursive=False))]})
  containers.append({'table_position_0based':i,'table_attrs':dict(t.attrs),'contest_label':label.find('label').get_text(' ',strip=True) if label and label.find('label') else label.get_text(' ',strip=True) if label else None,'contest_dom_input':dict(inp.attrs) if inp else None,'rows':cells})
 txt=sp.get_text(' ',strip=True);head=txt[:txt.find('Change View') if 'Change View' in txt else 1600]
 clock=sp.find(id='LastUpdated');title=sp.find('h1');date=sp.find('h2')
 return {'source_id':r['id'],'receipt_path':'data/results-sources/source/'+r['id']+'.receipt.json','url':r['final_url'],'raw_sha256':r['raw_sha256'],'election_heading':title.get_text(' ',strip=True) if title else None,'date_heading':date.get_text(' ',strip=True) if date else None,'header_text':head,'publisher_clock_literal':clock.get_text(' ',strip=True) if clock else None,'publisher_clock_timezone':None,'clock_note':'Displayed clock has no explicit offset/zone; do not infer it from host/county. HTTP Date is separate.','masked_detail_cells':sum(c['text']=='-' for t in containers for row in t['rows'] for c in row['cells']),'all_contest_tables':containers,'controls':[{'tag':x.name,'attrs':dict(x.attrs),'options':[{'attrs':dict(a.attrs),'text':a.get_text()} for a in x.find_all('option')]} for x in sp.find_all(['select','input'])],'november_returns_admitted':False}

def parse_state():
 result={};data={}
 for n in ['state-home-child-07-asset-02','state-home-child-07-asset-04','state-home-child-07-asset-05']:
  r=receipt(n);b=body(r);rows=[];offset=0
  for i,line in enumerate(b.splitlines(keepends=True),1):
   text=line.decode('utf-8-sig').rstrip('\r\n');f=text[1:-1].split('|') if text.startswith('[') else text.split('\t');rows.append({'source_line_1based':i,'byte_offset':offset,'line_bytes':len(line),'line_sha256':sha(line),'fields':f});offset+=len(line)
  data[n]=rows
  gzwrite(EX/(n+'.rows.json.gz'),{'source_receipt':'data/results-sources/source/'+n+'.receipt.json','rows':rows})
  result[n]={'rows':len(rows),'field_counts':dict(collections.Counter(len(x['fields']) for x in rows)),'raw_sha256':r['raw_sha256'],'source_clock':None,'clock_zone':None}
 info=data['state-home-child-07-asset-04'];votes=data['state-home-child-07-asset-05'];tsv=data['state-home-child-07-asset-02'];bytype=collections.defaultdict(list)
 for row in info:bytype[row['fields'][0]].append(row)
 races={x['fields'][5]:x['fields'][3:5] for x in bytype['r']};cands={(x['fields'][3],x['fields'][6]):x['fields'][4:6] for x in bytype['c']};units={x['fields'][4]:x['fields'][3] for x in bytype['u']};prec={(x['fields'][3],x['fields'][4]):x['fields'][5] for x in bytype['p']}
 orphan=[];seen=set()
 for row in votes:
  f=row['fields'];key=(f[4],f[5],f[7]);assert key not in seen;seen.add(key)
  if (f[4],f[7]) not in cands or f[5] not in units or f[4] not in races or (f[4],f[5]) not in prec:orphan.append(row)
 assert not orphan
 # Exact cross-format comparisons, preserving disagreements rather than reconciling by assumption.
 tmap={}
 for row in tsv[1:]:
  f=row['fields'];tmap[(f[6].casefold(),f[4],f[1],f[11],f[12])]=row
 party={'Republican':'REP','Democratic':'DEM','Nonpartisan':'NON','':'NON'};comparisons=0;mismatch=[]
 for row in votes:
  f=row['fields'];race,etype=races[f[4]];last,first=cands[(f[4],f[7])];key=(units[f[5]].casefold(),race,party.get(etype,etype),last,first);tr=tmap.get(key)
  if tr:
   comparisons+=1;tf=tr['fields']
   if (tf[14],tf[10],tf[9])!=(f[8],f[6],prec[(f[4],f[5])]):mismatch.append({'votes_source_row':row,'tsv_source_row':tr,'fields_compared':['candidate_votes','precincts_reporting','precincts_expected'],'pipe_values':[f[8],f[6],prec[(f[4],f[5])]],'tsv_values':[tf[14],tf[10],tf[9]]})
 result.update(info_types={k:len(v) for k,v in bytype.items()},county_units=len(units),county_unit_objects=bytype['u'],races=bytype['r'],candidate_objects=bytype['c'],vote_status_counts=dict(collections.Counter(x['fields'][3] for x in votes)),joins_checked=len(votes),cross_format_comparisons=comparisons,cross_format_mismatches=mismatch,scope='Selected August18,2026 primary, not November. One set of static observations, no synchronized-version/cadence guarantee. Status I preserved even where shell says Official; do not translate into certification.')
 dump(EX/'state-primary-controls.json',result)

def parse_broward():
 results=[]
 for n in ['broward-summary-236','broward-summary-228']:
  r=receipt(n);root=ET.fromstring(body(r));tables=[]
  for i,el in enumerate(root):
   if el.tag=='Table':tables.append({'source_child_position_0based':i,'tag':el.tag,'attrs':el.attrib,'fields':[{'tag':c.tag,'attrs':c.attrib,'text':c.text,'tail':c.tail} for c in el]})
  counts=[]
  for t in tables:
   d={c['tag']:c['text'] for c in t['fields']}
   vals=[d.get(k) for k in ['ElectionDayVotes','EarlyVotesVotes','VoteByMailVotes','ProvisionalVotingVotes','OTHERVotes']]
   if all(v is not None and v.isdecimal() for v in vals) and d.get('TotalVotes','').isdecimal():assert sum(map(int,vals))==int(d['TotalVotes'])
   if d.get('RaceName')=='United States Senator':counts.append(d)
  results.append({'source_id':n,'receipt_path':'data/results-sources/source/'+n+'.receipt.json','root_tag':root.tag,'root_attrs':root.attrib,'root_controls':[{'tag':c.tag,'attrs':c.attrib,'text':c.text} for c in root if c.tag!='Table'],'all_rows':tables,'senate_rows':counts,'scope':'Historical complete XML, full row fields including write-in/withdrawn/winner controls. GeneratedDate offset retained; no current IDs or actual election-night sequence implied.'})
 gzwrite(EX/'broward-complete-xml.json.gz',results)

def parse_pinellas():
 d={n:json.loads(body(receipt('pinellas-'+n))) for n in ['summary','details','sum','status','electionsettings','config']}
 # Keep complete objects; arrays are source-scoped and no key aliases are assumed.
 gzwrite(EX/'pinellas-complete-json.json.gz',d)
 summary=d['summary'];arr=summary if isinstance(summary,list) else summary.get('Contests',[])
 checks=[]
 for c in arr:
  if c.get('C')=='United States Senator':checks.append(c)
 dump(EX/'pinellas-controls.json',{'source_version':body(receipt('pinellas-version')).decode().strip(),'senate_summary':checks,'top_level_keys':{k:list(v) if isinstance(v,dict) else 'array' for k,v in d.items()},'scope':'Historical122583, fixedversion355096, never2026IDs. Full objects retained; completion and method interpretation require field-specific review.'})

def parse_candidates():
 r=receipt('current-candidate-all-status');sp=BeautifulSoup(body(r),'html.parser');tables=[]
 for i,t in enumerate(sp.find_all('table')):
  if 'Gillespie' in t.get_text() or 'Toulme' in t.get_text():tables.append({'table_position_0based':i,'attrs':dict(t.attrs),'html':str(t),'rows':[{'row_position_0based':j,'attrs':dict(tr.attrs),'cells':[{'tag':c.name,'attrs':dict(c.attrs),'text':c.get_text(' ',strip=True),'html':c.decode_contents()} for c in tr.find_all(['td','th'],recursive=False)]} for j,tr in enumerate(t.find_all('tr'))]})
 dump(EX/'current-candidate-all-status.json',{'source_receipt':'data/results-sources/source/current-candidate-all-status.receipt.json','tables':tables,'forms':[{'attrs':dict(f.attrs),'controls':[{'tag':a.name,'attrs':dict(a.attrs),'options':[{'attrs':dict(x.attrs),'text':x.get_text()} for x in a.find_all('option')]} for a in f.find_all(['input','select'])]} for f in sp.find_all('form')],'scope':'Actual all-status public query, including14filingrecords, DNQ/withdrawn/defeated status retained. Current qualified general choices3. Database filingIDs not ENR choiceIDs; recheck future legal substitutions.'})

if __name__=='__main__':
 records=reuse_identical();vr=[]
 for r in records:
  if r.get('status')==200 and re.search(r'enr(?:archive)?\.electionsfl\.org/.*/Summary',r.get('final_url',''),re.I):
   d=parse_vr(r)
   if d:vr.append(d)
 gzwrite(EX/'vr-complete-tables.json.gz',vr)
 parse_state();parse_broward();parse_pinellas();parse_candidates()
 # Independent complete PDF text layer, pages and order retained; visual previews separate.
 for n in ['hb991-primary-pdf','eo-district-injunction','eo-stay-order','watson-opinion','watson-docket-operative-85','state-dates-child-05','state-home-child-07-asset-03','alt-LEE-2','alt-LEE-3','results-SEM-02-follow-01-asset-134','results-SEM-02-follow-02-asset-134','orange2024-pdf-119','orange2024-pdf-120']:
  r=receipt(n);rd=PdfReader(io.BytesIO(body(r)));gzwrite(EX/(n+'.pages.json.gz'),{'source_receipt':'data/results-sources/source/'+n+'.receipt.json','pages':[{'page_1based':i+1,'text':pg.extract_text()} for i,pg in enumerate(rd.pages)]})
 print(json.dumps({'receipts':len(records),'vr_full_entities':len(vr),'vr_tables':sum(len(v['all_contest_tables']) for v in vr),'masked_cells':sum(v['masked_detail_cells'] for v in vr)}))
