#!/usr/bin/env python3
"""Build historical Alabama reporting-unit volume from complete original source extracts."""
import pathlib,json,gzip,re,csv,io,hashlib,collections,urllib.parse
from fractions import Fraction
from freeze import write
R=pathlib.Path(__file__).resolve().parents[1];S=R.parents[1]
def js(p,o):write(R/p,json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def load(p):return json.loads((R/p).read_text())
def csvout(p,rows):
 b=io.StringIO();w=csv.DictWriter(b,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);write(p,b.getvalue())
def body(prefix):return gzip.decompress(next((R/'source/http').glob(prefix+'*.gz')).read_bytes())
fips={}
for line in body('9f6e5f').decode().splitlines():
 a=line.split('|')
 if a[0]=='AL':fips[a[4].removesuffix(' County')]=a[1]+a[2]
assert len(fips)==67
names=sorted(fips,key=lambda n:fips[n]);js('source/county-fips.json',{'source_sha256':hashlib.sha256(body('9f6e5f')).hexdigest(),'scope':'2020 Census county code reference; no native precinct equivalence','mapping':fips})
alias={'Nale':'Hale','Uefferson':'Jefferson','ilalladega':'Talladega','!Tallapoosa':'Tallapoosa','il uscaloosa':'Tuscaloosa','1walker':'Walker','1wilcox':'Wilcox','1wmston':'Winston','St_ Clair':'St. Clair'}
contest_names={2024:['Kamala D. Harris','Donald J. Trump','Robert F. Kennedy Jr.','Jill Stein','Chase Oliver','Write-In'],2022:['Will Boyd','Katie Britt','John Sophocleus','Write-In'],2020:['Doug Jones','Tommy Tuberville','Write-In']}
configs={2024:[(5,25,[44,65,91,110,127,136]),(6,40,[61,81,109,126,144,153])],2022:[(4,20,[38,59,68,82,96,118,127]),(5,20,[31,52,60,74,90,111,120])],2020:[(3,20,[37,59,77,84,97,122,133]),(4,20,[37,59,77,84,97,121,133])]}
canvass={};controls={};evidence=[]
for y,conf in configs.items():
 pages=(R/f'source/sos-{y}-canvass-original.txt').read_text().split('\f');rows={}
 for page,labelend,ends in conf:
  ls=pages[page-1].splitlines()
  for ln,line in enumerate(ls,1):
   rawlabel=line[:labelend].strip();label=alias.get(rawlabel,rawlabel)
   if y==2022 and page==5 and rawlabel=='Total':label='Henry'
   if label not in names and rawlabel not in ['Total','!Total']:continue
   if label=='Henry' and not re.search(r'\d',line):continue
   vals=[];cells=[]
   for j,end in enumerate(ends):
    matches=[m for m in re.finditer(r'(?<!\S)[0-9][0-9,]*(?!\S)',line) if m.start()>=labelend and abs(m.end()-end)<=2]
    assert len(matches)<=1,(y,page,line,end,matches)
    m=matches[0] if matches else None
    dash=bool(re.search('[‐–—-]',line[max(labelend,end-8):end+2])) if not m else False
    v=int(m.group().replace(',','')) if m else None
    vals.append(v);cells.append({'column_1based':j+1,'value':v,'literal':m.group() if m else ('‐' if dash else ''),'cell_type':'number' if m else ('dash' if dash else 'blank'),'character_span_0based': [m.start(),m.end()] if m else None})
   repair=None
   if y==2024 and label in ['Hale','Winston']:
    vals={'Hale':[3868,3369,30,10,13,15],'Winston':[884,10191,36,8,10,20]}[label]
    repair={'kind':'explicit_visual_transcription','image':f'source/visual/canvass-2024-p{page}.png','region':'bottom county row across six presidential columns','values_in_printed_order':vals,'raw_line_continuation':ls[ln] if label=='Hale' else None}
    for c,v in zip(cells,vals):c['value']=v;c['visual_transcription']=True;c['ocr_extraction_cell_type']=c['cell_type'];c['cell_type']='number_visual_transcription';c['printed_literal']=format(v,',')
   vals=vals[-len(contest_names[y]):];cells=cells[-len(vals):]
   entry={'county':label if label in names else None,'county_fips':fips.get(label),'pdf_page_1based':page,'extracted_line_1based':ln,'raw_label':rawlabel,'raw_line':line,'target_contest_numeric_values':vals,'candidate_names_in_order':contest_names[y],'cells':cells,'visual_evidence':repair,'source':f'sos-{y}-canvass-original','certified_date':{2024:'2024-11-26',2022:'2022-11-28',2020:'2020-11-23'}[y]}
   evidence.append(entry)
   if label in names:assert label not in rows;rows[label]=entry
   else:assert y not in controls;controls[y]=dict(zip(contest_names[y],vals))
 assert set(rows)==set(names),(y,set(names)-set(rows))
 for j,n in enumerate(contest_names[y]):assert sum(r['cells'][j]['value'] or 0 for r in rows.values())==controls[y][n],(y,n)
 canvass[y]=rows
js('canvass-cells.json',evidence)
js('statewide-controls.json',{str(y):v for y,v in controls.items()})
# Separate official ballot-report rows, not presidential or Senate votes.
ballots={};ballotcontrols={}
for y,filename in [(2024,next(p for p in (R/'source').glob('f1cfb4*.txt') if 'warnings' not in p.name)),(2022,next(p for p in (R/'source').glob('823fe8*.txt') if 'warnings' not in p.name)),(2020,R/'source/sos-2020-ballots-original.txt')]:
 data={};page=1
 for li,line in enumerate(filename.read_text().splitlines(),1):
  parts=re.split(r'\s{2,}',line.strip());name=parts[0] if parts else ''
  if name not in names+['Total']:continue
  tokens=re.findall(r'[\d,]+(?:\.\d+)?%?',line[len(name):]);assert len(tokens)==7,(y,line,tokens)
  ints=[int(v.replace(',','')) for v in tokens[:5]]
  row={'year':y,'county':name,'county_fips':fips.get(name),'registered_voters':ints[0],'ballots_cast':ints[1],'democrat_ballots':ints[2],'republican_ballots':ints[3],'absentee_ballots':ints[4],'printed_turnout_pct':tokens[5],'printed_absentee_pct':tokens[6],'source_text':str(filename.relative_to(R)),'source_line_1based':li,'raw_line':line,'registration_status_scope':'Registered Voters as printed; active/inactive split and extract/as-of date not specified in this report','party_ballot_scope':'Straight-party in 2020/2022 headers; 2024 header says Democrat Ballots / Republican Ballots, not all votes for party candidates'}
  if name=='Total':ballotcontrols[y]=row
  else:data[name]=row
 assert len(data)==67,(y,len(data))
 for field in ['registered_voters','ballots_cast','democrat_ballots','republican_ballots','absentee_ballots']:
  assert sum(r[field] for r in data.values())==ballotcontrols[y][field],(y,field)
 ballots[y]=data
js('ballot-registration-controls.json',{'county_rows':[v for data in ballots.values() for v in data.values()],'statewide':list(ballotcontrols.values())})
allunits={};summaries={};recon=[];coverage=[];candidateuniverses=[]
def rank(rows,value):
 order=sorted(rows,key=lambda r:(-r[value],r['key']));den=sum(r[value] for r in order);cum=0
 for i,r in enumerate(order,1):cum+=r[value];r['rank']=i;r['cumulative_votes']=cum;r['weight_exact']=str(Fraction(r[value],den));r['cumulative_share_exact']=str(Fraction(cum,den))
 k=next(i for i,r in enumerate(order,1) if 5*r['cumulative_votes']>=4*den)
 top=sum(r[value] for r in order[:15]);pre=sum(r[value] for r in order[:k-1]);cross=order[k-1]
 return order,{'denominator':den,'unit_count':len(order),'top15_votes':top,'top15_share_exact':str(Fraction(top,den)),'top15_share_pct':100*top/den,'minimum80_count':k,'minimum80_votes':cross['cumulative_votes'],'minimum80_share_exact':str(Fraction(cross['cumulative_votes'],den)),'minimum80_share_pct':100*cross['cumulative_votes']/den,'preceding_count':k-1,'preceding_votes':pre,'preceding_share_exact':str(Fraction(pre,den)),'crossing_key':cross['key'],'crossing_label':cross.get('native_label',cross.get('county')),'crossing_county':cross['county'],'crossing_votes':cross[value],'priority_keys':[r['key'] for r in order[:max(k,15)]],'full_order':[r['key'] for r in order],'remainder_keys':[r['key'] for r in order[max(k,15):]],'remainder_votes':den-sum(r[value] for r in order[:max(k,15)])}
for y in [2024,2022,2020]:
 workbooks=json.loads(gzip.decompress((R/f'source/workbooks-{y}.json.gz').read_bytes()));units=[]
 for w in workbooks:
  county=w['member']['name'].split('-General-')[1].removesuffix('.xls');county={'StClair':'St. Clair'}.get(county,county);f=fips[county];sheet=w['sheets'][0];head=sheet['rows'][0]['values'];cols=[i for i in range(3,len(head)) if str(head[i]).strip()]
  assert len(set(head[c] for c in cols))==len(cols)
  contest='PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES' if y==2024 else 'UNITED STATES SENATOR'
  rs=[r for r in sheet['rows'][1:] if r['values'][0].strip()==contest];candidates=[r for r in rs if r['values'][2].strip() not in ['Under Votes','Over Votes']]
  assert sorted(r['values'][2].strip() for r in candidates)==sorted(contest_names[y]),(county,y)
  meta=[r for r in sheet['rows'][1:] if r['values'][0].strip().startswith(('REGISTERED VOTERS','BALLOTS CAST')) or r['values'][0].strip()=='STRAIGHT PARTY']
  canduniv=[{'row_1based':r['row_1based'],'contest_literal':r['values'][0],'party_literal':r['values'][1],'candidate_literal':r['values'][2]} for r in rs]
  candidateuniverses.append({'year':y,'county':county,'member':w['member'],'sheet':sheet['name'],'source_rows':canduniv})
  for c in cols:
   label=head[c];key=f'AL:{y}:general:{f}:col{c+1:03}:'+urllib.parse.quote(label,safe='')
   def cell(r):
    v=r['values'][c];numeric=isinstance(v,(int,float));assert not numeric or int(v)==v
    return {'row_1based':r['row_1based'],'column_1based':c+1,'contest_literal':r['values'][0],'party_literal':r['values'][1],'candidate_literal':r['values'][2],'value':int(v) if numeric else None,'raw_value':v,'xls_type':r['types'][c]}
   cv=[cell(r) for r in candidates];other=[cell(r) for r in rs if r not in candidates];admin=[cell(r) for r in meta]
   get=lambda n:next((v['value'] for v in admin if v['candidate_literal'].strip()==n),None)
   method='provisional_absentee' if 'ABSENTEE' in label and ('PROVISIONAL' in label or 'PROVSIONAL' in label) else 'absentee' if 'ABSENTEE' in label else 'provisional' if 'PROVISIONAL' in label or 'PROVSIONAL' in label else 'unspecified_native_precinct_or_site'
   u={'key':key,'year':y,'county':county,'county_fips':f,'native_label':label,'native_id':label,'standalone_native_numeric_id':None,'native_identity_scope':'literal workbook header; election/county/sheet/column scoped; no invented precinct code','method_context':method,'geometry_status':'administrative_no_polygon_assumed' if method!='unspecified_native_precinct_or_site' else 'historical_reporting_column_polygon_unverified','source_member':w['member']['name'],'member_sha256':w['member']['sha256'],'source_sheet':sheet['name'],'column_1based':c+1,'contest':contest,'candidate_votes':cv,'contest_other_fields':other,'administrative_fields':admin,'reported_candidate_votes':sum(a['value'] for a in cv),'ballots_cast_source':get('Ballots Cast - Total'),'blank_ballots_source':get('Ballots Cast - Blank'),'registration_source':get('Registered Voters - Total'),'under_votes_source':next((v['value'] for v in other if v['candidate_literal'].strip()=='Under Votes'),None),'over_votes_source':next((v['value'] for v in other if v['candidate_literal'].strip()=='Over Votes'),None),'named_valid_writein_allocation':None,'current_2026_crosswalk':None}
   units.append(u)
  group=[u for u in units if u['county']==county];row=canvass[y][county]
  for j,n in enumerate(contest_names[y]):
   native=sum(next(v['value'] for v in u['candidate_votes'] if v['candidate_literal'].strip()==n) for u in group);pdf=row['cells'][j]['value']
   assert pdf is None or native==pdf,(y,county,n,native,pdf)
   recon.append({'year':y,'county_fips':f,'county':county,'candidate':n,'native_sum':native,'canvass_value':pdf,'canvass_cell_type':row['cells'][j]['cell_type'],'difference_when_comparable':None if pdf is None else native-pdf,'source_scope_resolution':'numeric native cells independently observed; PDF null preserved' if pdf is None else 'exact agreement'})
  coverage.append({'year':y,'county':county,'county_fips':f,'parent_key':f'AL:{y}:general:{f}','native_count':len(group),'constituent_keys':[u['key'] for u in group],'native_coverage':'all labeled source columns; no missing labeled candidate cells','unavailable_cases':{'standalone_numeric_precinct_ids':'not a separate field in this workbook','2026_legal_boundaries':'not established','eligible_named_writein_breakdown':'not published in generic write-in rows'},'source_member':w['member'],'unlabeled_populated_cells':sum(1 for r in sheet['rows'][1:] for c,v in enumerate(r['values'][3:],3) if v!='' and c not in cols)})
  assert coverage[-1]['unlabeled_populated_cells']==0
 order,summary=rank(units,'reported_candidate_votes');allunits[y]=order;summaries[str(y)]=summary
 for n,v in controls[y].items():assert sum(next(c['value'] for c in u['candidate_votes'] if c['candidate_literal'].strip()==n) for u in units)==v
 js(f'native-units-{y}.json',order)
 csvout(R/f'native-order-{y}.csv',[{k:u[k] for k in ['rank','key','county_fips','county','native_label','method_context','source_member','source_sheet','column_1based','reported_candidate_votes','cumulative_votes','weight_exact','cumulative_share_exact','ballots_cast_source','blank_ballots_source','registration_source','under_votes_source','over_votes_source']} for u in order])
js('candidate-universe.json',candidateuniverses);js('candidate-reconciliation.json',recon);js('native-coverage.json',coverage);js('native-rank-summary.json',summaries)
# All 67 counties are separate overlapping parents, never added to native totals.
countyrows=[];county_sensitivity={};sensitivities={}
for y in [2024,2022,2020]:
 rows=[]
 for n in names:
  us=[u for u in allunits[y] if u['county']==n];br=ballots[y][n]
  rows.append({'key':f'AL:{y}:general:{fips[n]}','county':n,'county_fips':fips[n],'reported_candidate_votes':sum(u['reported_candidate_votes'] for u in us),'ballots_cast_report':br['ballots_cast'],'registered_voters_report':br['registered_voters'],'absentee_ballots_report':br['absentee_ballots']})
 o,summary=rank(rows,'reported_candidate_votes');county_sensitivity[str(y)]=summary
 for metric in ['ballots_cast_report','registered_voters_report','absentee_ballots_report']:
  oo,sm=rank([dict(r) for r in rows],metric);sensitivities[f'{y}_{metric}']={'summary':sm,'ordered_rows':oo}
 for r in o:
  n=r['county'];us=[u for u in allunits[y] if u['county']==n];br=ballots[y][n]
  row={'year':y,'county_fips':r['county_fips'],'county':n,'rank_candidate_volume':r['rank'],'candidate_votes':r['reported_candidate_votes'],'candidate_cumulative_votes':r['cumulative_votes'],'candidate_weight_exact':r['weight_exact'],'native_unit_count':len(us),'ballots_cast_report':br['ballots_cast'],'registered_voters_report':br['registered_voters'],'absentee_ballots_report':br['absentee_ballots'],'democrat_ballots_report':br['democrat_ballots'],'republican_ballots_report':br['republican_ballots'],'ballots_cast_native_sum':sum(u['ballots_cast_source'] for u in us if u['ballots_cast_source'] is not None),'blank_ballots_native_sum':sum(u['blank_ballots_source'] for u in us if u['blank_ballots_source'] is not None),'registration_native_sum':sum(u['registration_source'] for u in us if u['registration_source'] is not None),'under_votes_native_known_sum':sum(u['under_votes_source'] for u in us if u['under_votes_source'] is not None),'over_votes_native_known_sum':sum(u['over_votes_source'] for u in us if u['over_votes_source'] is not None),'under_over_missing_native_units':sum(u['under_votes_source'] is None or u['over_votes_source'] is None for u in us),'ballots_native_minus_report':sum(u['ballots_cast_source'] for u in us if u['ballots_cast_source'] is not None)-br['ballots_cast'],'registration_native_minus_report':sum(u['registration_source'] for u in us if u['registration_source'] is not None)-br['registered_voters'],'ballot_report_minus_contest_votes':br['ballots_cast']-r['reported_candidate_votes']}
  for j in range(6):
   cand=contest_names[y][j] if j<len(contest_names[y]) else ''
   row[f'candidate_{j+1}_name']=cand;row[f'candidate_{j+1}_votes']=sum(next(c['value'] for c in u['candidate_votes'] if c['candidate_literal'].strip()==cand) for u in us) if cand else None
  countyrows.append(row)
csvout(S/'data/county-turnout.csv',countyrows);js('county-rank-sensitivity.json',county_sensitivity);js('ballot-registration-sensitivity.json',sensitivities)
# Native ballot and registration rankings retain raw source scope and discrepancies.
native_sensitivity={}
for y,us in allunits.items():
 for metric in ['ballots_cast_source','registration_source']:
  if all(u[metric] is not None for u in us):
   rows=[{'key':u['key'],'county':u['county'],'native_label':u['native_label'],metric:u[metric]} for u in us]
   o,sm=rank(rows,metric);native_sensitivity[f'{y}_{metric}']={'summary':sm,'ordered_rows':o}
js('native-ballot-registration-sensitivity.json',native_sensitivity)
primary=summaries['2024'];keys=set(primary['priority_keys']);parents=[]
for c in coverage:
 if c['year']==2024:parents.append(dict(c,priority_constituent_keys=[k for k in c['constituent_keys'] if k in keys],remainder_constituent_keys=[k for k in c['constituent_keys'] if k not in keys]))
contract={'schema_version':'AL-turnout-native-v1','order_sort':['reported_candidate_votes descending','complete source-scoped key ascending'],'native_source_status':'Official SOS historical precinct archive; explicit certification stamp not supplied on XLS. Candidate aggregates independently match certified county and statewide canvass.','source_chain':{'authority_url':'https://www.sos.alabama.gov/alabama-votes/voter/election-data','archive_receipt':next(str(p.relative_to(R)) for p in (R/'source/http').glob('*.receipt.json') if json.loads(p.read_text())['original_sha256'].startswith('4ecca55')),'canvass_receipt':'source/original-receipts.json','original_first_witness':'source/original-first-witness.json'},'state':'AL','priority_contest':'2024-11-05 President And Vice President Of The United States','denominator_scope':'reported votes for five named presidential choices plus generic Write-In; native archive numeric cells independently reconcile to certified canvass','historical_native_coverage_complete':True,'historical_candidate_reconciliation_complete':True,'peer_agent_id':None,'independent_peer_agreement':False,'coordinator_acceptance':False,'legal_geographic_approval_2026':False,'current_2026_crosswalk_complete':False,'dispatch_status':'historical native priority measured; coordinator acceptance and independent reciprocal pending','certified_statewide_native_order':primary['full_order'],'ordered_priority_keys':primary['priority_keys'],'priority_keys':primary['priority_keys'],'full_order':primary['full_order'],'remainder_keys':primary['remainder_keys'],'coverage':primary,'parents':parents,'units':allunits[2024],'top15_keys':primary['full_order'][:15],'administrative_contexts':[u['key'] for u in allunits[2024] if u['method_context']!='unspecified_native_precinct_or_site'],'unavailable_cases':{'current_2026_native_ids_and_legal_geometry':'not established by historical XLS header','named_or_valid_eligible_writein_allocation':'generic published marks only','polling_method_splits_within_ordinary_columns':'not present; do not infer election-day exclusivity','peer':'not launched at assignment; pending same-ID independent reciprocal'},'county_sensitivity_reference':'county-rank-sensitivity.json','all_other_geographies_retained':True}
js('priority-set.json',contract)
# Source-scoped differences, never repaired or allocated.
qc=[]
for row in countyrows:
 if row['ballots_native_minus_report'] or row['registration_native_minus_report'] or row['under_over_missing_native_units']:
  qc.append({k:row[k] for k in ['year','county','county_fips','ballots_native_minus_report','registration_native_minus_report','under_over_missing_native_units']})
js('source-discrepancies.json',{'county_differences_or_missing_controls':qc,'statewide_native':{str(y):{'candidate_votes':sum(u['reported_candidate_votes'] for u in us),'ballots_cast_known_sum':sum(u['ballots_cast_source'] for u in us if u['ballots_cast_source'] is not None),'blank_ballots_known_sum':sum(u['blank_ballots_source'] for u in us if u['blank_ballots_source'] is not None),'registration_known_sum':sum(u['registration_source'] for u in us if u['registration_source'] is not None),'under_votes_known_sum':sum(u['under_votes_source'] for u in us if u['under_votes_source'] is not None),'over_votes_known_sum':sum(u['over_votes_source'] for u in us if u['over_votes_source'] is not None),'missing_under_over_units':sum(u['under_votes_source'] is None or u['over_votes_source'] is None for u in us)} for y,us in allunits.items()}})
print(json.dumps({y:{k:v for k,v in s.items() if k not in ['priority_keys','full_order','remainder_keys']} for y,s in summaries.items()},indent=2))
