"""Source-specific independent native extraction. Never fill an absent cell with zero.
Raw required pages/CSV rows, including unparsed lanes, are retained for review.
"""
import csv,gzip,hashlib,io,json,re
from pathlib import Path
from collections import defaultdict
from county import R,COUNTIES,FIPS,SPECS,text,js,csvout
PEER=R.parent/'turnout/source'
PCT=re.compile(r'(\d[\d,]*)\s+\d+(?:\.\d+)?%')
NUM=re.compile(r'\d[\d,]*')
def ints(s):return [int(x.replace(',','')) for x in re.findall(r'(?<![\w.])\d[\d,]*(?![\w.%])',s)]
def identify(s,y):
 if re.search(r'(?:US|U\.S\.|United States)\s+Senat',s,re.I):return f'{y}-senate'
 if re.search(r'^\s*Governor(?:\s|$)',s,re.I):return '2022-governor' if y==2022 else None
 if y==2024 and re.search(r'President',s,re.I) and not re.search('Vice President\s*$',s,re.I):return '2024-president'
 return None
def choice(label,contest):
 s=re.sub(r'^(?:REP|DEM|PGP|LBT|PRO|NAV|CON|IND)\s+','',label.strip(),flags=re.I)
 for name,_ in SPECS[contest][2][:-1]:
  if name in s:return name
 if re.match(r'(?:Misc(?:ellaneous)?\.?\s*(?:Write[- ]?in)?(?: votes)?|Write[- ]?[iI]n(?: Totals|s)?)$',s,re.I):return 'Misc.'
 return None

def main():
 inv=json.loads((R/'source/independent-original-inventory.json').read_text());bykey={x['source_key']:x for x in inv}
 rawpages=[];rawrows=[];units={};observations=[];ocrpins=[];issues=[]
 def put(k,c,contest,unit,vals,loc,controls=None,method=None,raw=None):
  key=(k,contest,unit)
  if not unit or not isinstance(unit,str):return
  if key not in units:units[key]={'source_key':k,'county':c,'fips':FIPS[c],'contest':contest,'unit_label':unit,'unit_key':f'{k}|{contest}|{unit}','unit_kind':'source-native reporting identity; polygon/current equivalence unapproved','candidates':{},'controls':{},'source_positions':[],'method_source':method,'source_overlap':'alternative source publications never additive'}
  r=units[key];r['source_positions'].append(loc)
  for name,v in vals.items():
   if name in r['candidates'] and r['candidates'][name]!=v:
    issues.append({'type':'explicit_visual_replacement' if isinstance(loc,dict) and 'independent_visual_reading' in loc else 'conflicting_duplicate_cell','key':key,'candidate':name,'values':[r['candidates'][name],v],'loc':loc});
    if isinstance(loc,dict) and 'independent_visual_reading' in loc:r['candidates'][name]=v
    continue
   r['candidates'][name]=v
  if controls:
   r.setdefault('control_observations',[]).append({'values':controls,'position':loc})
   for field,value in controls.items():
    if field in r['controls'] and value!=r['controls'][field]:
     issues.append({'type':'explicit_visual_control_replacement' if isinstance(loc,dict) and 'independent_visual_reading' in loc else 'conflicting_control_observation','key':key,'field':field,'values':[r['controls'][field],value],'loc':loc})
     r['controls'][field]=value # working last observation only; every conflicting source observation retained above
    else:r['controls'][field]=value
  if raw is not None:rawrows.append({'source_key':k,'county':c,'contest':contest,'unit':unit,'position':loc,'raw':raw})
 # Decode every original page. OCR retained by turnout is source-transformation evidence,
 # independently parsed here; no numeric transcriptions/reconciliation files are read.
 def pages(k):
  t=text(k);out=[]
  for p,s in enumerate(t.split('\f')[:-1],1):
   orig={'source_key':k,'page':p,'extraction':'independent Poppler -layout'}
   if len(s.strip())<30:
    for folder in ['refined-ocr','ocr']:
     f=PEER/folder/f'{k}-p{p:03}.txt.gz'
     if f.exists():
      data=f.read_bytes();ocrpins.append({'path':str(f.relative_to(R.parent.parent)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'source_key':k,'page':p,'qualification':'retained OCR source transformation, independently parsed; uncertain glyphs not repaired'});s=gzip.decompress(data).decode(errors='replace');orig['extraction']=str(f.relative_to(R.parent.parent));break
   out.append((p,s,orig))
  return out
 def parse_vertical(k,c,y,pp):
  current=None;contest=None;block=[];locs=[]
  def flush():
   if not contest or not current:return
   vals={};controls={};rows=[]
   for line,pos in block:
    mm=re.match(r'^\s*(Misc\. write-in votes):\s+(\d[\d,]*)\s+(\d[\d,]*)\s*$',line,re.I)
    if mm and mm[2]==mm[3]:vals['Misc.']=int(mm[2].replace(',',''));rows.append({'label_source':mm[1],'candidate_mapped':'Misc.','votes':vals['Misc.'],'position':pos,'raw_line':line,'method_source':'Absentee Voting and Total equal parallel lanes; nonadditive'})
    m=re.match(r'^\s*(.*?)\s{2,}(\d[\d,]*)(?:\s+\d+(?:\.\d+)?%|\s*$)',line)
    if m:
     label=m[1].strip().rstrip(':');v=int(m[2].replace(',',''));ch=choice(label,contest)
     if ch:vals[ch]=v;rows.append({'label_source':label,'candidate_mapped':ch,'votes':v,'position':pos,'raw_line':line})
     elif re.fullmatch(r'Total|Total Votes Cast|Overvotes|Undervotes|Over Votes|Under Votes|Contest Totals?',label,re.I):controls[label]=v
    mb=re.search(r'(\d[\d,]*) ballots \((\d+) over voted ballots, (\d+) overvotes, (\d+) undervotes\), (\d[\d,]*) registered voters',line)
    if mb:controls.update(dict(zip(['ballots_source','over_voted_ballots_source','overvotes_source','undervotes_source','registered_voters_source'],[int(v.replace(',','')) for v in mb.groups()])))
   if vals:
    put(k,c,contest,current,vals,locs[:],controls,raw={'rows':rows,'raw_block':[l for l,p in block]})
  for p,s,origin in pp:
   if origin['extraction']!='independent Poppler -layout':continue
   for ln,line in enumerate(s.splitlines(),1):
    pos={'page':p,'line':ln,'extraction':origin['extraction']}
    unit=None
    m=re.match(r'^\s*(Precinct\s+\S+)\s*$',line)
    if m:unit=m[1]
    elif c=='Tillamook' and y==2022 and ln<12 and line.strip() and line.strip()==line.strip().upper() and re.fullmatch(r'[A-Z][A-Z0-9# .&/-]+',line.strip()) and line.strip() not in ['TOTAL','OFFICIAL RESULTS','STATISTICS']:unit=line.strip()
    elif re.match(r'^\s*\d+\s*-\s*[^\d]',line) and len(re.split(r'\s{2,}',line.strip()))==1:unit=line.strip()
    elif 'Tillamook County -' in line:unit=line.split('Tillamook County -',1)[1].strip()
    elif re.match(r'^\s*\d+\s+\d[\d,]* of \d[\d,]* registered voters',line):unit=line.split()[0]
    if re.match(r'^\s*(?:All Precincts|Grand Total|Precinct Totals)\s*$',line,re.I):flush();contest=None;current=None;block=[];locs=[]
    if unit:
     unit=re.sub(r'\s+', ' ',unit)
     if unit!=current:flush();contest=None;block=[];locs=[];current=unit
    hd=bool(re.search(r'\(Vote\s+for\s+\d+\)| - Vote for|^\s*(?:US Senator|U\.S\. Senator|Governor|US Representative|U\.S\. Representative|Secretary of State|Attorney General|State Treasurer|United States President)',line,re.I))
    ct=identify(line,y)
    if hd or ct:
     flush();contest=ct;block=[];locs=[pos]
    elif contest:
     block.append((line,pos))
     if re.match(r'^\s*(?:Contest Totals?)\s+',line,re.I) or (c=='Tillamook' and y==2022 and re.match(r'^\s*Undervotes\s+',line,re.I)):flush();contest=None;block=[];locs=[]
  flush()
 def parse_table(k,c,y,pp):
  for p,s,origin in pp:
   # Only tables with a precinct column and candidate percentage columns.
   if not re.search(r'Precinct\s+Ballots|Precinct\s+Total',s):continue
   if not re.search(r'Merkley|Wyden|Drazan|Kamala|Kennedy|Write-in|Kotek|Pulju',s):
    title=next((' '.join(l.split()) for l in s.splitlines() if re.search(r'(?:Senator|Governor|President).*Vote',l,re.I)),'')
    ct=identify(title,y)
    if ct and 'Over' in s and 'Under' in s:
     for ln,line in enumerate(s.splitlines(),1):
      m=re.match(r'^\s*(Precinct\s+\S+)\s+(.+)$',line)
      if not m:continue
      tok=m[2].split()
      if len(tok)==5 and all(re.fullmatch(r'\d[\d,]*',v) for v in tok):
       vals=[int(v.replace(',','')) for v in tok];put(k,c,ct,re.sub(r'\s+', ' ',m[1]),{}, {'page':p,'line':ln,'extraction':origin['extraction']},dict(zip(['ballots_source','registered_voters_source','Total','Overvotes','Undervotes'],vals)),raw=line)
    continue
   ct=None
   title=next((l for l in s.splitlines() if re.search(r'(?:Senator|Governor|President).*\(Vote for 1\)',l,re.I)),'')
   ct=identify(title,y)
   if ct:pass
   elif 'Merkley' in s:ct='2020-senate'
   elif 'Wyden' in s:ct='2022-senate'
   elif 'Drazan' in s:ct='2022-governor'
   elif y==2024 and re.search('Kennedy|Kamala',s):ct='2024-president'
   # Explicit continuation pane with only Write-in can belong to the current table title.
   elif 'Write-in' in s:ct=identify(next((l for l in s.splitlines() if identify(l,y)),''),y)
   if not ct:continue
   spec=SPECS[ct][2];names=[n for n,party in spec if n!='Misc.' and n.split()[-1] in s]
   if ct=='2024-president':
    names=[n for n,party in spec[:-1] if (n.split()[-1] in s or (n=='Robert F Kennedy Jr' and 'Kennedy' in s))]
   if re.search(r'Write-in',s):names+=['Misc.']
   for ln,line in enumerate(s.splitlines(),1):
    m=re.match(r'^\s*(Precinct\s+\S+)\s+(.+)$',line)
    if not m:continue
    matches=list(PCT.finditer(m[2]));nv=[int(v.group(1).replace(',','')) for v in matches]
    if len(nv)!=len(names) or not nv:continue
    prefix=m[2][:matches[0].start()];before=NUM.findall(prefix);after=NUM.findall(m[2][matches[-1].end():]);controls={}
    if len(before)==3:controls.update(dict(zip(['ballots_source','registered_voters_source','Total'],[int(v.replace(',','')) for v in before])))
    elif len(before)==1:controls['Total']=int(before[0].replace(',',''))
    if len(after)==2:controls.update({'Overvotes':int(after[0].replace(',','')),'Undervotes':int(after[1].replace(',',''))})
    put(k,c,ct,re.sub(r'\s+', ' ',m[1]),dict(zip(names,nv)),{'page':p,'line':ln,'extraction':origin['extraction']},controls,raw=line)
 def parse_integer_table(k,c,y,pp):
  for p,s,origin in pp:
   if origin['extraction']!='independent Poppler -layout':continue
   for ct in [f'{y}-senate','2022-governor'] if y==2022 else ['2020-senate']:
    needle='Governor' if ct.endswith('governor') else 'US Senator'
    start=s.find(needle)
    if start<0:continue
    tail=s[start:];other=re.search(r'(?:Governor|US Representative|U.S. Representative|Secretary of State)',tail[len(needle):])
    if other:tail=tail[:len(needle)+other.start()]
    n=len(SPECS[ct][2]);extra=1 if c=='Umatilla' and y==2022 else 0;nc=n+3+(1 if c in ['Columbia','Umatilla'] else 0)+extra
    for ln,line in enumerate(tail.splitlines(),1):
     if not re.match(r'^\s*\d',line):continue
     tok=line.split()
     if len(tok)<=nc:continue
     end=tok[-nc:]
     if not all(re.fullmatch(r'\d[\d,]*',v) for v in end):continue
     label=' '.join(tok[:-nc]);v=[int(v.replace(',','')) for v in end]
     controls=dict(zip(['Total Votes Cast','Overvotes','Undervotes','Contest Total'],v[n+extra:]))
     if extra:controls['Write-in: Not Assigned nonadditive']=v[n]
     put(k,c,ct,label,dict(zip([n for n,p in SPECS[ct][2]],v[:n])),{'page':p,'table_line':ln,'extraction':origin['extraction']},controls,raw=line)
 def parse_canvass(k,c):
  pp=pages(k)
  for p,s,origin in pp:
   if 'President' not in s:continue
   if 'Representative' in s and p>4:continue
   for ln,line in enumerate(s.splitlines(),1):
    m=re.match(r'^\s*(\d+(?:/\d+)?)\s+(.+)$',line)
    if not m:continue
    tok=m[2].split()
    if c=='Marion' and tok and tok[-1].endswith('%'):tok=tok[:-1]
    if len(tok)!=14 or not all(re.fullmatch(r'\d[\d,]*',t) for t in tok):continue
    v=[int(t.replace(',','')) for t in tok]
    if c=='Clackamas':
     vals=dict(zip([n for n,party in SPECS['2024-president'][2]],v[:7]+[v[10]]));ctl=dict(zip(['Cast Votes excluding Misc_source','Undervotes','Overvotes','Miscellaneous Write-In','Vote by Mail Ballots Cast','Total Ballots Cast','Registered Voters'],v[7:]));assert sum(v[:7])==v[7]
    else:vals=dict(zip([n for n,party in SPECS['2024-president'][2]],v[:8]));ctl=dict(zip(['Cast Votes','Undervotes','Overvotes','Vote by Mail Ballots Cast','Total Ballots Cast','Registered Voters'],v[8:]));assert sum(v[:8])==v[8]
    put(k,c,'2024-president',m[1],vals,{'page':p,'line':ln,'extraction':origin['extraction']},ctl,'Vote by Mail (parallel Total lane, not additive)',line)
  return pp
 def parse_csv(k,c,y):
  s=text(k);rr=list(csv.reader(io.StringIO(s)))
  if c=='Yamhill':
   headers=rr[1];records=[dict(zip(headers,r)) for r in rr[2:]]
  elif c=='Umatilla':
   headers=None
   for i,row in enumerate(rr):
    if any('Jeff Merkley' in v for v in row):headers=row;start=i+1;break
   if headers:
    for i,row in enumerate(rr[start:],start+1):
     if len(row)<10 or not re.match('^\d',row[0]):
      if row and row[0]=='Totals':break
      continue
     v=[int(x.replace(',','')) for x in row[1:10]];put(k,c,'2020-senate',row[0],dict(zip([n for n,p in SPECS['2020-senate'][2]],v[:5])),{'csv_record':i},dict(zip(['Total Votes Cast','Overvotes','Undervotes','Contest Total'],v[5:])),raw={'headers':headers,'fields':row})
   return
  else:records=list(csv.DictReader(io.StringIO(s)))
  for i,row in enumerate(records,3 if c=='Yamhill' else 2):
   title=row.get('Contest Title',row.get('Contest',''));ct=identify(title,y)
   if ct not in SPECS:continue
   label=row.get('Choice Name',row.get('Choice'));ch=choice(label,ct)
   unit=row.get('Precinct',row.get('#Precinct'))
   if not unit:continue
   rawrows.append({'source_key':k,'county':c,'contest':ct,'unit':unit,'position':{'csv_record':i},'raw':row})
   if ch is None:continue
   vote=row.get('Total Votes',row.get('Votes'))
   if vote is None or not re.fullmatch(r'\d[\d,]*',vote):continue
   controls={key:row[key] for key in ['BallotsWith Contest','Registered Voters','Ballots Cast','Precinct ID','Contest ID'] if key in row}
   put(k,c,ct,unit,{ch:int(vote.replace(',',''))},{'csv_record':i},controls,'Vote by Mail (parallel Total lane)' if c=='Yamhill' else None)
 # All archive members retained; each page inspected/indexed even if extraction cannot close.
 for y in [2020,2022]:
  for i,c in enumerate(COUNTIES):
   k=f'{y}-{i:02}'
   if bykey[k]['kind']=='CSV':parse_csv(k,c,y);continue
   pp=pages(k)
   for p,s,orig in pp:
    if re.search('Merkley|Wyden|Drazan|Senator|STATISTICS|Registered Voters',s,re.I):rawpages.append({**orig,'county':c,'raw_page':s,'required_contest_or_administrative_evidence':True})
   parse_vertical(k,c,y,pp);parse_table(k,c,y,pp)
   if c in ['Columbia','Clatsop','Umatilla']:parse_integer_table(k,c,y,pp)
 for k,c,y in [('benton-2020-precincts','Benton',2020),('benton-2022-precincts','Benton',2022),('2024-Wasco','Wasco',2024)]:
  pp=pages(k);parse_vertical(k,c,y,pp)
  for p,s,orig in pp:
   if re.search('Merkley|Wyden|Drazan|President|Registered Voters',s,re.I):rawpages.append({**orig,'county':c,'raw_page':s})
 for k,c in [('clackamas-2024-canvass','Clackamas'),('marion-2024-canvass','Marion')]:
  pp=parse_canvass(k,c)
  for p,s,orig in pp:
   if p<5:rawpages.append({**orig,'county':c,'raw_page':s})
 parse_csv('multnomah-2024-sovc2','Multnomah',2024)
 k='multnomah-2024-president';pp=pages(k);parse_table(k,'Multnomah',2024,pp)
 for p,s,origin in pp:rawpages.append({**origin,'county':'Multnomah','raw_page':s,'additive':False})
 # Preserve candidate-specific nonvote lanes in summary SOVC1 separately, never additive.
 sr=[]
 for i,row in enumerate(csv.DictReader(io.StringIO(text('multnomah-2024-sovc1'))),2):
  if 'President' in row.get('Contest',''):sr.append({'source_key':'multnomah-2024-sovc1','csv_record':i,'raw_fields':row,'additive':False})
 js('source/nonadditive-multnomah-summary.json',sr)
 # Washington 2024 is a scanned multi-pane table. Preserve every raw page; OCR-only
 # cells retain uncertainty until independent visual corrections are explicitly recorded.
 k='washington-2024-precincts';pp=pages(k);parse_table(k,'Washington',2024,pp[:9])
 for p,s,orig in pp[:9]:rawpages.append({**orig,'county':'Washington','raw_page':s})
 corrections=R/'source/visual-readings.json'
 if corrections.exists():
  for correction in json.loads(corrections.read_text()):
   put(correction['source_key'],correction['county'],correction['contest'],correction['unit_label'],correction['candidates'],{'independent_visual_reading':correction['evidence']},correction.get('controls'),correction.get('method_source'))
 conflictkeys={tuple(x['key']) for x in issues if x['type']=='conflicting_duplicate_cell'}
 if corrections.exists():
  for x in json.loads(corrections.read_text()):
   if x['source_key'] in ['washington-2024-precincts','2020-05']:conflictkeys.discard((x['source_key'],x['contest'],x['unit_label']))
 for r in units.values():
  r['unresolved_normalization_conflict']=(r['source_key'],r['contest'],r['unit_label']) in conflictkeys
  names=[n for n,p in SPECS[r['contest']][2]];r['missing_candidate_columns']=[n for n in names if n not in r['candidates']];r['reported_all_choice_votes']=sum(r['candidates'].values()) if not r['missing_candidate_columns'] else None
  a,b=SPECS[r['contest']][3:];A=names[a];B=names[b];r['A']=A;r['B']=B;r['A_votes']=r['candidates'].get(A);r['B_votes']=r['candidates'].get(B)
  r['pair_votes']=None if r['A_votes'] is None or r['B_votes'] is None else r['A_votes']+r['B_votes'];r['A_pair_share']=r['A_votes']/r['pair_votes'] if r['pair_votes'] else None
  r['current_source_accepted']=False;r['geography_accepted']=False
 # Record all36 parents x required contests; exact candidate-column differences are evidence.
 county=list(csv.DictReader((R/'county-candidates.csv').open()));recon=[]
 for ct in SPECS:
  for c in COUNTIES:
   sources=sorted({r['source_key'] for r in units.values() if r['contest']==ct and r['county']==c})
   if not sources:sources=[None]
   for k in sources:
    ur=[r for r in units.values() if r['contest']==ct and r['county']==c and r['source_key']==k];summed={n:sum(r['candidates'].get(n,0) for r in ur) for n,p in SPECS[ct][2]};control={r['candidate']:int(r['votes']) for r in county if r['contest']==ct and r['county']==c};missing=[r['unit_label'] for r in ur if r['missing_candidate_columns']];diff={n:summed[n]-control[n] for n in control}
    closed=bool(ur) and not missing and not any(diff.values()) and not any(r['unresolved_normalization_conflict'] for r in ur)
    recon.append({'contest':ct,'county':c,'source_key':k,'extracted_units':len(ur),'candidate_sums':summed if ur else None,'abstract_controls':control,'differences':diff if ur else None,'units_missing_columns':missing,'column_closed':closed,'qualification':'native normalization partial; no residual allocation; unknown source-universe outside extracted identities' if not closed else 'candidate column closure only, historical source-local identities; no 2026 crosswalk'})
 js('native-units.json',list(units.values()));js('native-reconciliation.json',recon);js('source/ocr-pins.json',ocrpins);js('source/extraction-issues.json',issues)
 for n,rows in [('raw-native-pages.jsonl.gz',rawpages),('raw-native-rows.jsonl.gz',rawrows)]:
  (R/'source'/n).write_bytes(gzip.compress((''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in rows)).encode(),mtime=0))
 print(json.dumps({'units':len(units),'raw_pages':len(rawpages),'raw_rows':len(rawrows),'closed_parents':{ct:len({r['county'] for r in recon if r['contest']==ct and r['column_closed']}) for ct in SPECS},'issues':len(issues)}))
if __name__=='__main__':main()
