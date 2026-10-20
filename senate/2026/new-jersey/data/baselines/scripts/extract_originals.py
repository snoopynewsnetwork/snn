#!/usr/bin/env python3
"""Independent original-byte extraction. No peer votes/ranks are read here."""
from pathlib import Path
import csv,gzip,hashlib,json,re,subprocess,tempfile,os,zipfile,io,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parents[1]; STATE=D.parents[1]; S=D/'source'; E=D/'extract'
COUNTIES=['Atlantic','Bergen','Burlington','Camden','Cape May','Cumberland','Essex','Gloucester','Hudson','Hunterdon','Mercer','Middlesex','Monmouth','Morris','Ocean','Passaic','Salem','Somerset','Sussex','Union','Warren']
SLUGS=[c.lower().replace(' ','') for c in COUNTIES]
FIPS={c:f'34{2*i+1:03}' for i,c in enumerate(COUNTIES)}
CANDIDATES={
 '2024-senate':[('Andy Kim','Democratic'),('Curtis Bashaw','Republican'),('Christina Khalil','Green Party'),('Kenneth R. Kaplan','Libertarian Party'),('Patricia G. Mooneyham','Vote Better'),('Joanne Kuniansky','Socialist Workers Party')],
 '2020-senate':[('Cory Booker','Democratic'),('Rikin "Rik" Mehta','Republican'),('Daniel Burke','LaRouche Was Right'),('Veronica Fernandez','Of, By, For!'),('Madelyn R. Hoffman','Green Party')],
 '2018-senate':[('Robert Menendez','Democratic'),('Bob Hugin','Republican'),('Tricia Flanagan','New Day NJ'),('Madelyn R. Hoffman','Green Party'),('Kevin Kimple','Make It Simple'),('Natalie Lynn Rivera','For the People'),('Murray Sabrin','Libertarian Party'),('Hank Schroeder','Economic Growth')],
 '2024-president':[('Kamala D. Harris','Democratic'),('Donald J. Trump','Republican'),('Jill Stein','Green Party'),('Robert F. Kennedy Jr.','Independent'),('Chase Oliver','Libertarian Party'),('Claudia De la Cruz','Socialism and Liberation'),('Randall A. Terry','U.S. Constitution Party'),('Joseph Kishore','Socialist Equality'),('Rachele Fruit','Socialist Workers Party')]
}
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def gzsave(p,b):p.write_bytes(gzip.compress(b,mtime=0))
def pin_originals():
 out=S/'original-references.json'
 if out.exists():return json.loads(out.read_text())
 refs=[]; base=STATE/'data/turnout/source'
 for p in sorted(base.glob('*.receipt.json')):
  r=json.loads(p.read_text());ref=r.get('reference_path',r.get('asset')); bp=(p.parent/ref).resolve() if ref else None
  entry={'receipt_filename':p.name,'receipt':r,'inherited_receipt_path':os.path.relpath(p,S),'inherited_receipt_sha256':sha(p.read_bytes()),'body_reference':os.path.relpath(bp,S) if bp and bp.is_file() else None}
  if bp and bp.is_file():
   z=bp.read_bytes();b=gzip.decompress(z) if bp.suffix=='.gz' else z
   assert r.get('raw_sha256',sha(b))==sha(b),p
   assert r.get('stored_sha256',sha(z))==sha(z),p
   entry.update(raw_sha256=sha(b),raw_bytes=len(b),stored_sha256=sha(z),stored_bytes=len(z))
  refs.append(entry)
 # Clerk body is independently read, no inherited candidate values.
 p=STATE.parent/'michigan/data/baselines/house-statistics2020.pdf';b=p.read_bytes()
 refs.append({'receipt_filename':'clerk-2020-original-reference','receipt':{'id':'clerk-2020','url':'https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf','acquisition':'inherited read-only original; no new HTTP retrieval claimed'},'body_reference':os.path.relpath(p,S),'raw_sha256':sha(b),'raw_bytes':len(b),'stored_sha256':sha(b),'stored_bytes':len(b)})
 save(out,refs);return refs
REFS=pin_originals();BY={r['receipt'].get('id',r['receipt_filename']):r for r in REFS if r['body_reference']}
def body(r):
 p=S/r['body_reference'];z=p.read_bytes();b=gzip.decompress(z) if p.suffix=='.gz' else z
 assert sha(z)==r['stored_sha256'] and sha(b)==r['raw_sha256'];return b
def textof(sid):
 r=BY[sid];b=body(r);p=E/(sid+'.layout.txt.gz')
 if not b.startswith(b'%PDF'):raise ValueError(sid+' not PDF')
 with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
  f.write(b);f.flush();t=subprocess.run(['pdftotext','-layout',f.name,'-'],capture_output=True,check=True).stdout
 gzsave(p,t);return t.decode('utf-8')
NUM=re.compile(r'(?<![\w.,])[0-9]+(?:,[0-9]{3})*(?![\w.,])')
def integer(s):return int(s.replace(',',''))
def contest_id(scope,slug):
 year,kind=scope.split('-');return (f'2018-general-election-results-us-senate-{slug}' if year=='2018' else f'{year}-official-general-results-'+('us-senate' if kind=='senate' else 'president')+'-'+slug)
def native_contest(sid,scope,county):
 t=textof(sid);pages=t.split('\f');n=len(CANDIDATES[scope]); allrows=[];footers=[];headers=[]
 # Each numeric footer provides actual column right-edge positions; blank cells stay null.
 totals=[]
 for pn,page in enumerate(pages,1):
  for ln,line in enumerate(page.splitlines(),1):
   if re.match(r'^\s*(?:Total|COUNTY TOTAL)\s+',line,re.I):
    tokens=list(NUM.finditer(line));
    if len(tokens)==n:totals.append(([m.end() for m in tokens],line,pn,ln))
 assert totals,(sid,'no complete footer')
 ends=totals[-1][0]
 for pn,page in enumerate(pages,1):
  for ln,line in enumerate(page.splitlines(),1):
   toks=list(NUM.finditer(line));vec=[None]*n; cells=[]
   # Data labels start before first candidate column and have at least two-space separation.
   if not toks:continue
   if len(toks)!=n and not re.search('federal|overse|hand count',line[:toks[0].start()],re.I):continue
   label=line[:toks[0].start()].strip()
   if not label or not re.search('[A-Za-z]',label) or 'NJDOE' in label:continue
   if not re.search(r'\S\s{2,}$',line[:toks[0].start()]):continue
   for m in toks:
    j=toks.index(m) if len(toks)==n else min(range(n),key=lambda j:abs(m.end()-ends[j]));dist=abs(m.end()-ends[j])
    assert len(toks)==n or dist<=12,(sid,pn,ln,m.group(),dist,line,ends)
    assert vec[j] is None,(sid,line)
    vec[j]=integer(m.group());cells.append({'column':j,'start':m.start(),'end':m.end(),'literal':m.group()})
   row={'key':f'{sid}:p{pn:04}:l{ln:04}','source_id':sid,'page':pn,'line':ln,'county':county,'county_fips':FIPS[county],'label':label,'scope':scope,'votes':vec,'numeric_sum':sum(v for v in vec if v is not None),'raw':line,'numeric_cells':cells,'type':'administrative' if re.search('federal|overse|hand count',label,re.I) else 'municipal-labelled'}
   if label.lower() in ['total','county total']:footers.append(row)
   else:allrows.append(row)
  headers.append({'source_id':sid,'page':pn,'lines':[{'line':i,'raw':l} for i,l in enumerate(page.splitlines(),1) if l.strip() and (not allrows or i<min((r['line'] for r in allrows if r['page']==pn),default=999))]})
 assert len(footers)==1,(sid,len(footers))
 sums=[sum(r['votes'][j] or 0 for r in allrows) for j in range(n)]
 assert sums==footers[0]['votes'],(sid,len(allrows),sums,footers[0]['votes'])
 return {'source_id':sid,'county':county,'scope':scope,'candidates':[{'name':a,'party_ballot_label':b} for a,b in CANDIDATES[scope]],'rows':allrows,'footer':footers[0],'headers':headers,'column_right_edges':ends}
def county_controls(sid,scope):
 t=textof(sid);out=[]
 for pn,page in enumerate(t.split('\f'),1):
  rows=[];foot=[]
  for ln,l in enumerate(page.splitlines(),1):
   m=re.match(r'^\s*('+'|'.join(c.upper() for c in COUNTIES)+r')\s+.*?\s+([\d,]+)\s*$',l)
   if m:rows.append({'county':m[1].title(),'votes':integer(m[2]),'page':pn,'line':ln,'raw':l})
   m=re.match(r'^\s*Total\s+([\d,]+)\s*$',l)
   if m:foot.append({'votes':integer(m[1]),'page':pn,'line':ln,'raw':l})
  if not rows:continue
  assert len(rows)==21 and len(foot)==1 and sum(r['votes'] for r in rows)==foot[0]['votes'],sid
  header=[{'line':i,'raw':l} for i,l in enumerate(page.splitlines(),1) if l.strip() and i<min(r['line'] for r in rows)]
  out.append({'source_id':sid,'scope':scope,'page':pn,'header':header,'counties':rows,'footer':foot[0]})
 return out

def ballots(sid,year,county):
 t=textof(sid);out=[];foot=[];headers=[]
 for pn,page in enumerate(t.split('\f'),1):
  lines=page.splitlines();anchors=[]
  for ln,line in enumerate(lines,1):
   toks=list(re.finditer(r'[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?%?',line))
   pct=next((i for i,m in enumerate(toks) if m.group().endswith('%')),None)
   if pct==2 and len(toks)>=5:anchors.append((ln,[m.end() for m in toks if not m.group().endswith('%')]))
  for ln,line in enumerate(lines,1):
   if not line.strip():continue
   m=re.search(r'\s{2,}(?=[\d,]+(?:\s|$))',line)
   if not m:headers.append({'source_id':sid,'page':pn,'line':ln,'raw':line});continue
   label=line[:m.start()].strip();toks=list(re.finditer(r'[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?%?',line[m.end():]));tokens=[m.group() for m in toks]
   if not tokens or not re.search('[a-zA-Z]',label) or any(x in label for x in ['NJDOE','Page','November']):continue
   if any(x in label for x in ['Number of','MUNICIPALITIES']):continue
   assert anchors,(sid,'no column anchors')
   row={'key':f'{sid}:p{pn:04}:l{ln:04}','source_id':sid,'year':year,'county':county,'label':label,'page':pn,'line':ln,'raw':line,'tokens':tokens,'cells':[]}
   names=['registered_voters','ballots_cast','mail_ballots','election_day_provisional','early_voting_provisional'] if county=='Monmouth' and year==2024 else ['registered_voters','ballots_cast','mail_ballots','provisional_ballots']
   row.update({k:None for k in ['registered_voters','ballots_cast','mail_ballots','provisional_ballots','election_day_provisional','early_voting_provisional','published_percent']})
   ends=min(anchors,key=lambda x:abs(x[0]-ln))[1]
   numeric=[z for z in toks if not z.group().endswith('%')]
   for z in toks:
    if z.group().endswith('%'):row['published_percent']=z.group();continue
    end=m.end()+z.end();j=numeric.index(z) if len(numeric)==len(names) else min(range(len(ends)),key=lambda j:abs(end-ends[j]))
    assert j<len(names) and row[names[j]] is None,(sid,line)
    row[names[j]]=integer(z.group());row['cells'].append({'field':names[j],'literal':z.group(),'start':m.end()+z.start(),'end':end})
   (foot if label.lower() in ['total','county total'] else out).append(row)
 return {'source_id':sid,'year':year,'county':county,'rows':out,'footers':foot,'headers':headers}
def main():
 native={s:[] for s in CANDIDATES};controls={};ball=[]
 for scope in CANDIDATES:
  for county,slug in zip(COUNTIES,SLUGS):native[scope].append(native_contest(contest_id(scope,slug),scope,county))
  year,kind=scope.split('-');sid=f'sos-{year}-'+('senate-county' if kind=='senate' else 'president-county');controls[scope]=county_controls(sid,scope)
 save(E/'native-contests.json',native);save(E/'county-candidate-controls.json',controls)
 for year in [2024,2020,2022]:
  for county,slug in zip(COUNTIES,SLUGS):
   sid=f'{year}-official-general-result-ballotscast-{slug}'
   if sid not in BY:sid=f'{year}-official-general-results-ballotscast-{slug}'
   assert sid in BY,(year,slug)
   ball.append(ballots(sid,year,county))
 save(E/'ballot-records.json',ball)
 tc={}
 for sid in ['sos-2024-turnout','sos-2022-turnout','2020-official-general-voter-turnout']:
  t=textof(sid);rows=[]
  for pn,p in enumerate(t.split('\f'),1):
   for ln,l in enumerate(p.splitlines(),1):
    if any(re.match(r'^\s*'+re.escape(c)+r'\s',l,re.I) for c in COUNTIES) or re.match(r'^\s*(Total|State Total)\s',l,re.I):rows.append({'source_id':sid,'page':pn,'line':ln,'raw':l,'tokens':re.findall(r'\d[\d,]*(?:\.\d+)?%?',l)})
  tc[sid]={'rows':rows,'full_text':str((E/(sid+'.layout.txt.gz')).relative_to(D))}
 save(E/'turnout-controls.json',tc)
 t=textof('clerk-2020');section=t.split('NEW JERSEY',1)[1].split('FOR UNITED STATES REPRESENTATIVE',1)[0];save(E/'clerk-2020-section.json',{'literal_section':section,'Booker':integer(re.search(r'Cory A\. Booker[^\n]+?([0-9][0-9,]*)\s*$',section,re.M)[1]),'Mehta':integer(re.search(r'Rikin[^\n]+?Mehta[^\n]+?([0-9][0-9,]*)\s*$',section,re.M)[1])})
 print(json.dumps({s:{'rows':sum(len(c['rows']) for c in v),'numeric_totals':[sum(r['votes'][i] or 0 for c in v for r in c['rows']) for i in range(len(CANDIDATES[s]))]} for s,v in native.items()}))
if __name__=='__main__':main()
