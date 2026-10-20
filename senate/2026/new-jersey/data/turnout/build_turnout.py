#!/usr/bin/env python3
"""Offline, original-first NJ extraction. Keys preserve PDF page/line source positions."""
from pathlib import Path
import gzip,json,csv,re,hashlib,itertools
D=Path(__file__).resolve().parent;E=D/'extract';S=D/'source'
COUNTIES=['Atlantic','Bergen','Burlington','Camden','Cape May','Cumberland','Essex','Gloucester','Hudson','Hunterdon','Mercer','Middlesex','Monmouth','Morris','Ocean','Passaic','Salem','Somerset','Sussex','Union','Warren']
FIPS={c:'34'+f'{2*i+1:03}' for i,c in enumerate(COUNTIES)}
SLUG={c:c.lower().replace(' ','') for c in COUNTIES}
CANDS={
'2024-senate':[('Andy Kim','Democratic'),('Curtis Bashaw','Republican'),('Christina Khalil','Green Party'),('Kenneth R. Kaplan','Libertarian Party'),('Patricia G. Mooneyham','Vote Better'),('Joanne Kuniansky','Socialist Workers Party')],
'2020-senate':[('Cory Booker','Democratic'),('Rikin "Rik" Mehta','Republican'),('Daniel Burke','LaRouche Was Right'),('Veronica Fernandez','Of, By, For!'),('Madelyn R. Hoffman','Green Party')],
'2018-senate':[('Robert Menendez','Democratic'),('Bob Hugin','Republican'),('Tricia Flanagan','New Day NJ'),('Madelyn R. Hoffman','Green Party'),('Kevin Kimple','Make It Simple'),('Natalie Lynn Rivera','For the People'),('Murray Sabrin','Libertarian Party'),('Hank Schroeder','Economic Growth')],
'2024-president':[('Kamala D. Harris','Democratic'),('Donald J. Trump','Republican'),('Jill Stein','Green Party'),('Robert F. Kennedy Jr.','Independent'),('Chase Oliver','Libertarian Party'),('Claudia De la Cruz','Socialism and Liberation'),('Randall A. Terry','U.S. Constitution Party'),('Joseph Kishore','Socialist Equality'),('Rachele Fruit','Socialist Workers Party')]}
def txt(sid):return gzip.decompress((E/(sid+'.txt.gz')).read_bytes()).decode()
def dump(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def writecsv(path,rows):
 with path.open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def poskey(sid,p,l):return f'{sid}:p{p:04d}:l{l:04d}'
def sourceid(yr,kind,county):
 slug=SLUG[county]
 return f'{yr}-general-election-results-us-senate-{slug}' if yr==2018 else f'{yr}-official-general-'+('result-ballotscast-' if kind=='ballots' else f'results-{kind}-')+slug
def parsemunicipal(sid,n,c):
 rows=[];foot=[];unparsed=[]
 for p,page in enumerate(txt(sid).split('\f'),1):
  for l,line in enumerate(page.splitlines(),1):
   m=re.match(r'^\s*(\S.*?)\s{2,}((?:[0-9][0-9,]*\s+){'+str(n-1)+r'}[0-9][0-9,]*)\s*$',line)
   if m:
    name=m[1].strip();v=[int(x.replace(',','')) for x in m[2].split()]
    r={'key':poskey(sid,p,l),'source_id':sid,'page':p,'line':l,'county':c,'county_fips':FIPS[c],'native_label':name,'unit_type':'administrative' if any(x in name.lower() for x in ['federal','overseas','provisional','absentee','hand counts']) else 'municipality','values':v,'source_line':line}
    if re.fullmatch(r'(?:COUNTY\s+)?TOTAL',name,re.I):r['unit_type']='county_summary';foot.append(r)
    else:rows.append(r)
   elif re.search(r'\d',line) and not any(x in line for x in ['November','NJDOE','General','United','2024','2020','2018']) and not re.fullmatch(r'\s*\d+\s*',line):
    # Sparse federal rows have genuinely blank cells, visually checked in original PDFs.
    sparse={
     '2024-official-general-results-us-senate-capemay':('Federal Oversees',[85,16,3,None,None,None]),
     '2024-official-general-results-president-capemay':('Federal Overseas',[93,15,None,1,None,None,None,None,None]),
     '2024-official-general-results-president-middlesex':('Federal Overseas',[837,283,12,None,None,2,None,None,None])}
    if sid in sparse and sparse[sid][0] in line:
     label,v=sparse[sid];assert [int(x.replace(',','')) for x in re.findall(r'\d[\d,]*',line)]==[x for x in v if x is not None]
     rows.append({'key':poskey(sid,p,l),'source_id':sid,'page':p,'line':l,'county':c,'county_fips':FIPS[c],'native_label':label,'unit_type':'administrative','values':v,'source_line':line,'sparse_cells':'Literal blank PDF cells retained null; numeric columns visually checked, not inferred zeros.'})
    else:unparsed.append({'page':p,'line':l,'source_line':line})
 return rows,foot,unparsed

def parseballots(sid,c):
 rows=[];foot=[];other=[]
 for p,page in enumerate(txt(sid).split('\f'),1):
  for l,line in enumerate(page.splitlines(),1):
   m=re.match(r'^\s*(\S.*?)\s{2,}([\d,][\d,\s%]*)\s*$',line)
   if not m:continue
   label=m[1].strip();tokens=m[2].split();record={'key':poskey(sid,p,l),'source_id':sid,'page':p,'line':l,'county':c,'county_fips':FIPS[c],'native_label':label,'source_line':line,'tokens':tokens}
   vals={k:None for k in ['registered_voters','ballots_cast','published_percent','vote_by_mail_ballots_cast','provisional_ballots_cast','election_day_provisional_ballots_cast','early_voting_provisional_ballots_cast']}
   if len(tokens)==5 and tokens[2].endswith('%'):
    for k,t in zip(list(vals)[:5],tokens):vals[k]=int(t.replace(',','').replace('%',''))
   elif len(tokens)==6 and tokens[2].endswith('%') and c=='Monmouth' and sid.startswith('2024-'):
    for k,t in zip(['registered_voters','ballots_cast','published_percent','vote_by_mail_ballots_cast','election_day_provisional_ballots_cast','early_voting_provisional_ballots_cast'],tokens):vals[k]=int(t.replace(',','').replace('%',''))
   elif len(tokens)==1 and any(x in label.lower() for x in ['federal','overseas']):vals['ballots_cast']=int(tokens[0].replace(',',''))
   elif len(tokens)==2 and any(x in label.lower() for x in ['federal','overseas']):
    vals['ballots_cast'],vals['vote_by_mail_ballots_cast']=[int(t.replace(',','')) for t in tokens]
   elif len(tokens)==4 and label=='Overseas' and sid=='2024-official-general-result-ballotscast-camden':
    for k,t in zip(['registered_voters','ballots_cast','vote_by_mail_ballots_cast','provisional_ballots_cast'],tokens):vals[k]=int(t.replace(',',''))
   else:other.append(record);continue
   record.update(vals)
   if re.fullmatch(r'(?:COUNTY\s+)?TOTAL',label,re.I):foot.append(record)
   else:rows.append(record)
 return rows,foot,other

def parsestate(sid):
 out=[]
 for p,page in enumerate(txt(sid).split('\f'),1):
  if 'Name' not in page or 'Tally' not in page:continue
  lines=page.splitlines();h=next(i for i,x in enumerate(lines) if 'Name' in x and 'Tally' in x)
  header=lines[h+1].strip();cells=[];total=None
  for l,line in enumerate(lines,1):
   for c in COUNTIES:
    m=re.match(r'^\s*'+re.escape(c.upper())+r'\s+.*?([\d][\d,]*)\s*$',line)
    if m:cells.append({'key':poskey(sid,p,l),'county':c,'county_fips':FIPS[c],'votes':int(m[1].replace(',','')),'source_line':line})
   m=re.fullmatch(r'\s*Total\s+([\d,]+)\s*',line)
   if m:total=int(m[1].replace(',',''))
  out.append({'source_id':sid,'page':p,'literal_header_line':header,'raw_page_text':page,'county_cells':cells,'published_total':total,'sum_counties':sum(x['votes'] for x in cells)})
 return out

def parseturnout(sid):
 rows=[]
 for p,page in enumerate(txt(sid).split('\f'),1):
  for l,line in enumerate(page.splitlines(),1):
   m=re.match(r'^\s*('+'|'.join(COUNTIES)+r'|TOTAL)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+(\d+)%\s+([\d,]+)\s*$',line)
   if m:rows.append({'source_id':sid,'key':poskey(sid,p,l),'county':m[1],'county_fips':FIPS.get(m[1]),**{k:int(v.replace(',','')) for k,v in zip(['registered_voters','ballots_cast','ballots_rejected','published_percent','election_districts'],m.groups()[1:])},'source_line':line})
 return rows

def rank(rows,field):
 rows=sorted(rows,key=lambda r:(-r[field],r['key']));total=sum(r[field] for r in rows);cum=0;out=[]
 for i,r in enumerate(rows,1):
  before=cum;cum+=r[field];out.append({**r,'rank':i,'cumulative_votes':cum,'previous_votes':before,'share_numerator':r[field],'share_denominator':total,'in_top15':i<=15,'in_minimum80':5*before<4*total})
 k=next(i+1 for i,r in enumerate(out) if 5*r['cumulative_votes']>=4*total)
 return out,{'unit_count':len(rows),'total':total,'top15_votes':sum(r[field] for r in out[:15]),'top15_keys':[r['key'] for r in out[:15]],'minimum80_count':k,'minimum80_votes':out[k-1]['cumulative_votes'],'preceding_count':k-1,'preceding_votes':out[k-1]['previous_votes'],'crossing_key':out[k-1]['key'],'crossing_label':out[k-1].get('native_label',out[k-1].get('county')),'remainder_count':len(out)-k,'remainder_votes':total-out[k-1]['cumulative_votes'],'ordered_keys':[r['key'] for r in out],'priority_keys':[r['key'] for r in out[:max(15,k)]],'remainder_keys':[r['key'] for r in out[max(15,k):]]}

def main():
 municipal={};footers={};unparsed={};balances=[]
 for scope in CANDS:
  year,office=scope.split('-');year=int(year);kind='us-senate' if office=='senate' else 'president'
  rows=[];feet=[]
  for c in COUNTIES:
   sid=sourceid(year,kind,c);rr,ff,uu=parsemunicipal(sid,len(CANDS[scope]),c);rows+=rr;feet+=ff
   if uu:unparsed[sid]=uu
   if len(ff)!=1: print('FOOTER',sid,len(ff))
   for j,(cand,party) in enumerate(CANDS[scope]):
    balances.append({'scope':scope,'county':c,'candidate':cand,'party_label':party,'municipal_sum':sum(r['values'][j] for r in rr if r['values'][j] is not None),'blank_source_cells':sum(r['values'][j] is None for r in rr),'published_municipal_footer':ff[0]['values'][j] if len(ff)==1 else None})
  municipal[scope]=rows;footers[scope]=feet
 ballots={};bfeet={}
 for year in [2024,2020,2022]:
  rows=[];feet=[]
  for c in COUNTIES:
   sid=sourceid(year,'ballots',c);rr,ff,uu=parseballots(sid,c);rows+=rr;feet+=ff
   if uu:unparsed[sid]=uu
  ballots[str(year)]=rows;bfeet[str(year)]=feet
 controls={scope:parsestate('shared-sos-'+scope.replace('-senate','-senate-county').replace('-president','-president-county')) for scope in CANDS}
 turnout={str(y):parseturnout('shared-sos-'+str(y)+'-turnout' if y!=2020 else '2020-official-general-voter-turnout') for y in [2024,2020,2022]}
 dump(D/'extract/native-rows.json',municipal);dump(D/'extract/municipal-footers.json',footers);dump(D/'extract/ballot-rows.json',ballots);dump(D/'extract/ballot-footers.json',bfeet);dump(D/'extract/state-candidate-controls.json',controls);dump(D/'extract/turnout-controls.json',turnout);dump(D/'extract/unparsed-numeric-lines.json',unparsed)
 for scope,cc in controls.items():
  # Primary statewide pages have different candidate order. Match by literal candidate name after punctuation/case folding only, never county allocations.
  def norm(x):return re.sub('[^a-z]','',x.lower())
  for row in [x for x in balances if x['scope']==scope]:
   cand=row['candidate'];matches=[x for x in cc if norm(cand) in norm(x['literal_header_line'])]
   if len(matches)!=1:print('CANDIDATE MATCH',scope,cand,[x['literal_header_line'] for x in cc]);continue
   cells=[x for x in matches[0]['county_cells'] if x['county']==row['county']];row['state_pdf_county_control']=cells[0]['votes'] if len(cells)==1 else None
   row['difference_from_state']=row['municipal_sum']-row['state_pdf_county_control'] if row['state_pdf_county_control'] is not None else None
 writecsv(D/'extract/candidate-reconciliation.csv',balances)
 ranked,summary=rank([{**r,'contest_votes':sum(x for x in r['values'] if x is not None)} for r in municipal['2024-senate']],'contest_votes')
 dump(D/'rank-summary.json',summary)
 # No inferred cross-year geography equivalence. Same-vintage exact label links are separately exposed.
 out=[]
 for r in ranked:
  b=[x for x in ballots['2024'] if x['county']==r['county'] and x['native_label']==r['native_label']]
  out.append({k:r[k] for k in ['rank','key','county','county_fips','native_label','unit_type','source_id','page','line','contest_votes','cumulative_votes','previous_votes','share_denominator','in_top15','in_minimum80']}|{re.sub('[^a-z]+','_',cand.lower()).strip('_')+'_votes':v for (cand,p),v in zip(CANDS['2024-senate'],r['values'])}|{'ballot_exact_label_key':b[0]['key'] if len(b)==1 else None,**{k:b[0][k] if len(b)==1 else None for k in ['registered_voters','ballots_cast','published_percent','vote_by_mail_ballots_cast','provisional_ballots_cast','election_day_provisional_ballots_cast','early_voting_provisional_ballots_cast']},'blank_votes':None,'undervotes':None,'overvotes':None,'generic_writein_votes':None,'named_writein_votes':None})
 writecsv(D.parent/'county-turnout.csv',out)
 dump(D/'preliminary-extraction-summary.json',{'municipal_counts':{k:len(v) for k,v in municipal.items()},'administrative':{k:[(r['county'],r['native_label'],r['values']) for r in v if r['unit_type']=='administrative'] for k,v in municipal.items()},'candidate_balances':{scope:{cand:sum(x['municipal_sum'] for x in balances if x['scope']==scope and x['candidate']==cand) for cand,p in CANDS[scope]} for scope in CANDS},'differences':[r for r in balances if r.get('difference_from_state')!=0],'unparsed_numeric_sources':len(unparsed),'ballot_counts':{y:len(r) for y,r in ballots.items()},'turnout_controls_counts':{y:len(r) for y,r in turnout.items()},'ballot_exact_label_unmatched':[(r['county'],r['native_label']) for r in out if not r['ballot_exact_label_key']]})
 print(json.dumps({'counts':{k:len(v) for k,v in municipal.items()},'rank_summary':{k:v for k,v in summary.items() if 'keys' not in k},'unparsed':len(unparsed),'differences':len([r for r in balances if r.get('difference_from_state')!=0])},indent=2))
if __name__=='__main__':main()
