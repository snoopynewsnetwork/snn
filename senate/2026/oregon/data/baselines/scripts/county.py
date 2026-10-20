"""Independent extraction of literal abstract/participation county tables."""
import csv,gzip,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
COUNTIES='Baker,Benton,Clackamas,Clatsop,Columbia,Coos,Crook,Curry,Deschutes,Douglas,Gilliam,Grant,Harney,Hood River,Jackson,Jefferson,Josephine,Klamath,Lake,Lane,Lincoln,Linn,Malheur,Marion,Morrow,Multnomah,Polk,Sherman,Tillamook,Umatilla,Union,Wallowa,Wasco,Washington,Wheeler,Yamhill'.split(',')
FIPS={c:f'41{2*i+1:03}' for i,c in enumerate(COUNTIES)}
# Tuple order is literal source column order. Generic Misc. is not a named candidate.
SPECS={
 '2024-president':('2024-abstract',1,[('Robert F Kennedy Jr','WTP'),('Cornel West','P'),('Chase Oliver','L'),('Randall Terry','C'),('Donald J Trump','R'),('Jill Stein','PG'),('Kamala D Harris','D'),('Misc.','')],6,4),
 '2020-senate':('2020-abstract',2,[('Jo Rae Perkins','R'),('Jeff Merkley','D'),('Ibrahim A Taher','PG'),('Gary Dye','L'),('Misc.','')],1,0),
 '2022-senate':('2022-abstract',1,[('Jo Rae Perkins','R'),('Dan Pulju','PG'),('Ron Wyden','D'),('Chris Henry','P'),('Misc.','')],2,0),
 '2022-governor':('2022-abstract',4,[('Tina Kotek','D'),('Donice Noelle Smith','C'),('R Leon Noble','L'),('Betsy Johnson','NAV'),('Christine Drazan','R'),('Misc.','')],0,4)}
def text(k):return gzip.decompress((R/'source/text'/f'{k}.txt.gz').read_bytes()).decode(errors='replace')
def js(n,x):(R/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def csvout(p,rs):
 with (R/p).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def parse_table(k,p,n):
 page=text(k).split('\f')[p-1];rows={};foot=None
 for i,line in enumerate(page.splitlines(),1):
  m=re.match(r'^\s*('+ '|'.join(COUNTIES)+r'|Total|TOTAL)\s+(.+)$',line)
  if not m:continue
  vals=m.group(2).split()
  if len(vals)!=n or not all(re.fullmatch(r'\d[\d,]*',v) for v in vals):continue
  rec={'values':[int(v.replace(',','')) for v in vals],'page':p,'line':i,'raw_line':line}
  if m[1].lower()=='total':foot=rec
  else:assert m[1] not in rows;rows[m[1]]=rec
 assert set(rows)==set(COUNTIES) and foot is not None,(k,p,len(rows))
 assert [sum(v['values'][j] for v in rows.values()) for j in range(n)]==foot['values']
 return rows,foot,page

def main():
 long=[];wide=[];controls={};headers={}
 for contest,(k,p,choices,a,b) in SPECS.items():
  rows,foot,page=parse_table(k,p,len(choices));controls[contest]=foot;headers[contest]={'source_key':k,'page':p,'full_page':page,'candidates':choices,'A':choices[a][0],'B':choices[b][0],'status':'General Election Abstract of Votes; ** Elected as printed','generic_scope':'Misc. not independently proved valid named write-ins'}
  for c in COUNTIES:
   rec=rows[c];v=rec['values'];total=sum(v);pair=v[a]+v[b]
   wide.append({'contest':contest,'county':c,'fips':FIPS[c],'A':choices[a][0],'B':choices[b][0],'A_votes':v[a],'B_votes':v[b],'other_reported_votes':total-pair,'named_candidate_votes':total-v[-1],'generic_Misc_votes':v[-1],'reported_all_choice_votes':total,'pair_votes':pair,'pair_participation_in_reported_all_choice':pair/total,'A_pair_share':v[a]/pair,'A_minus_B_pair_margin':(v[a]-v[b])/pair,'A_minus_B_net_votes':v[a]-v[b],'A_all_choice_share':v[a]/total,'B_all_choice_share':v[b]/total,'source_key':k,'source_page':p,'source_line':rec['line']})
   for j,(label,party) in enumerate(choices):long.append({'contest':contest,'county':c,'fips':FIPS[c],'source_candidate_column':j+1,'candidate':label,'party_source':party,'votes':v[j],'scope':'reported generic Misc.' if label=='Misc.' else 'named candidate','source_key':k,'page':p,'line':rec['line'],'raw_line':rec['raw_line']})
 csvout('county-candidates.csv',long);csvout('../county-baselines.csv',wide);js('state-controls.json',controls);js('source/abstract-evidence.json',headers)
 # Nonadditive vice-president presentation: preserve all six literal columns, no missing slate expansion.
 rows,foot,page=parse_table('2024-abstract',2,6)
 vp=[]
 for c,r in rows.items():
  for j,(label,party) in enumerate([('Nicole Shanahan','WTP'),('Mike ter Maat','L'),('JD Vance','R'),('Rudolph Ware','PG'),('Tim Walz','D'),('Misc.','')]):vp.append({'county':c,'candidate':label,'party_source':party,'votes':r['values'][j],'source_page':2,'source_line':r['line'],'additive':False,'raw_line':r['raw_line']})
 csvout('nonadditive-vice-president.csv',vp)
 participation=[];monthly=[];pfoot={}
 for y in [2020,2022,2024]:
  k=f'sos-{y}-participation-archived'+('-20241227' if y==2024 else '')
  pages=text(k).split('\f');state={}
  for p,page in enumerate(pages,1):
   if 'PARTICIPATION BY COUNTY' not in page:continue
   header=next(l for l in page.splitlines() if re.search('Republican|Independent|Pacific Green|We The People|Other|^\s+Total\s*$',l))
   groups=re.split(r'\s{2,}',header.strip());assert 1<=len(groups)<=3,(k,p,groups)
   totals=None;cr={}
   for i,line in enumerate(page.splitlines(),1):
    m=re.match(r'^\s*('+ '|'.join(COUNTIES)+r'|Total)\s+(.+)$',line)
    if not m:continue
    toks=m[2].split()
    if len(toks)!=3*len(groups):continue
    if not all(re.fullmatch(r'\d[\d,]*',toks[j]) for j in range(0,len(toks),3)):continue
    for j,g in enumerate(groups):
     a,b,pc=toks[3*j:3*j+3];r={'year':y,'county':m[1],'group_source':g,'Number Eligible':int(a.replace(',','')),'Ballots Returned':int(b.replace(',','')),'Percent Voting_source':pc,'source_key':k,'page':p,'line':i,'raw_line':line}
     participation.append(r)
     if m[1]=='Total':state[g]=r
     else:cr[(m[1],g)]=r
   for g in groups:
    for field in ['Number Eligible','Ballots Returned']:
     assert sum(cr[c,g][field] for c in COUNTIES)==state[g][field],(y,g,field)
  pfoot[y]=state
  # Monthly stock comparison is a separate publication/as-of definition.
  page=text(f'{y}-registration').split('\f')[0]
  for i,line in enumerate(page.splitlines(),1):
   m=re.match(r'^\s*('+ '|'.join(COUNTIES)+r'|Total)\s+(.+)$',line)
   if not m:continue
   vals=m[2].split()
   if len(vals)<5:continue
   monthly.append({'year':y,'county':m[1],'this_month':int(vals[0].replace(',','')),'last_month':int(vals[1].replace(',','')),'prior_year_month':int(vals[3].replace(',','')),'source_key':f'{y}-registration','page':1,'line':i,'raw_line':line})
 csvout('participation-controls.csv',participation);csvout('monthly-registration.csv',monthly);js('participation-state-controls.json',pfoot)
 print(json.dumps({'county_rows':len(wide),'candidate_rows':len(long),'participation_rows':len(participation),'all_candidate_columns_balance':True}))
if __name__=='__main__':main()
