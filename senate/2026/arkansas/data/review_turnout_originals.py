"""Independent coordinator review of complete Arkansas original turnout scopes.
No producer parser/module imports and no producer output writes.
"""
from pathlib import Path
from collections import Counter,defaultdict
from urllib.parse import quote
import csv,gzip,hashlib,io,json,re,subprocess,sys,tempfile,xml.etree.ElementTree as ET,zipfile
S=Path(__file__).resolve().parents[1];T=S/'data/turnout';N=0;receipts={};raws={}
def ck(v,msg):
 global N
 N+=1
 if not v:raise AssertionError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def pin(p):
 b=p.read_bytes();return {'path':str(p.resolve().relative_to(S.resolve())),'bytes':len(b),'sha256':sha(b)}
def same(a,b,msg):ck(json.dumps(a,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':'))==json.dumps(b,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':')),msg)
def original(name):return raws[name]
def obj(name):return json.loads(original(name))
def sourcekey(lane,parent,label):return 'AR:'+lane+':'+parent+':'+quote(label,safe='')
def votes(choices,name='Name',field='TotalVotes'):
 ck(len({r[name]for r in choices})==len(choices),'distinct original candidate identities')
 return{r[name]:r[field]for r in choices}
manifest=read(T/'asset-manifest.json');ck(sha((T/'asset-manifest.json').read_bytes())=='d1558ec667c3e91f3727e24b5e1898b35d9c19208f3e55056517f310fbcb5693','frozen original turnout seal')
actual={str(p.relative_to(S))for p in T.rglob('*')if p.is_file()and p!=T/'asset-manifest.json'}|{'turnout.md','data/county-turnout.csv'}
ck(actual=={r['path']for r in manifest['assets']}and len(actual)==1027,'exact complete manifest scope')
for r in manifest['assets']:ck(pin(S/r['path'])==r and r['bytes']<40000000,'every owned complete body')
for p in sorted((T/'source').rglob('*.receipt.json')):
 r=read(p)
 if r.get('shared_original_path'):path=Path(r['shared_original_path'])
 else:path=p.parent/r['asset']
 stored=path.read_bytes();raw=gzip.decompress(stored)
 ck(sha(stored)==r['stored_sha256']and len(stored)==r.get('stored_bytes',len(stored)),'stored complete original')
 ck(sha(raw)==r['raw_sha256']and len(raw)==r.get('raw_bytes',r.get('bytes')),'raw complete original')
 if r['id']in raws:ck(raws[r['id']]==raw,'duplicate logical receipt bytes remain same')
 raws[r['id']]=raw;receipts[r['id']]=r
for r in read(T/'source/original-pins.json'):
 same(receipts[r['id']],r,'copied immutable individual shared receipt')
failures=[]
for p in sorted((T/'history/acquisition-timeout').glob('*.receipt.json')):
 r=read(p);b=gzip.decompress((p.parent/r['asset']).read_bytes());ck(sha(b)==r['raw_sha256']and len(b)==r['raw_bytes'],'complete separate initial transport failure body');failures.append({'path':str(p.relative_to(S)),'raw_sha256':sha(b),'raw_bytes':len(b)})
# Parse original OOXML by exact cell addresses/types, independent of producer parser.
raw=original('sos-2024-general-precinct-original');ck(sha(raw)=='6509c03c4e32717d41e7ad561f813bcc702cf72b2a0b80c12e74cdee6b7dee94','original workbook raw pin')
z=zipfile.ZipFile(io.BytesIO(raw));ck(z.testzip()is None,'every original OOXML member CRC')
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};strings=[]
for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns):strings.append(''.join(n.text or''for n in si.iter('{'+ns['m']+'}t')))
source_rows=[];inventory=Counter();headers=None;allrows=0;rawcellchecks=0
saved=read(T/'extracted/2024-xlsx-president-raw-rows.json.gz');savedrows={r['source_row']:r for r in saved['rows']}
for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('m:sheetData/m:row',ns):
 cellvalues=[];cellobjects=[]
 for c in row.findall('m:c',ns):
  v=c.find('m:v',ns);text=v.text if v is not None else None;value=strings[int(text)]if c.get('t')=='s'else text
  cellvalues.append(value);cellobjects.append({'ref':c.get('r'),'type':c.get('t'),'v':text,'value':value})
 if headers is None:headers=cellvalues;continue
 allrows+=1;ck(len(cellvalues)==len(headers)==10,'original complete ten-column row')
 d=dict(zip(headers,cellvalues));inventory[d['contest']]+=1
 if d['contest']=='U.S. President':
  rr=int(row.get('r'));sd=savedrows[rr]
  for k,v in d.items():ck(sd[k]==v,'every exact original field/token')
  same(sd['source_cells'],cellobjects,'whole raw typed cell objects/address/shared-string/raw-v');rawcellchecks+=len(cellobjects)
  d['row']=rr;source_rows.append(d)
ck(len(source_rows)==len(savedrows)==19887 and inventory==saved['all_contests_inventory']and headers==saved['headers'],'whole selected workbook scope and all contest inventory')
universes=read(T/'extracted/source-native-universes.json.gz');original_native={};countycontrols={};orders={};yearproof={};countybodies=nativeobjects=0;diffs=[]
for year in [2024,2022,2020]:
 info=obj(f'{year}-info');meta=obj(f'{year}-metadata');state=obj(f'{year}-federal-state');full=obj(f'{year}-full');title='U.S. President'if year==2024 else'U.S. Senate'
 matches=[(k,v)for k,v in meta['response']['contests'].items()if v['contestName']==title];ck(len(matches)==1,'actual returned unique selected contest constructor')
 cid,desc=matches[0];sc=state['response']['contests'][cid];locs=info['response']['locations'];ck(len(locs)==75,'all actual returned county identities')
 saved=read(T/f'extracted/{year}-api-original-relevant-records.json.gz');same(saved['state'],state,'whole state original response');same(saved['metadata'],desc,'whole raw selected contest metadata')
 sid={c['choiceID']:desc['choices'][c['choiceID']]['name']for c in sc['choices']};statevotes={sid[c['choiceID']]:c['totalVotes']for c in sc['choices']};api=[];parent={};reverse={v['locationName'].upper():k for k,v in locs.items()};ck(len(reverse)==75,'explicit distinct administrative parents')
 originalinventory=[];savednative={(r['county_fips'],r['native_id']):r for r in saved['native_records']};savedcounty={r['county_fips']:r for r in saved['counties']};summed=Counter()
 for fips,l in locs.items():
  cr=obj(f'{year}-federal-{fips}')['response']['contests'][cid];same(savedcounty[fips]['raw_contest'],cr,'whole county native response, not projected votes');countybodies+=1
  cv={sid[c['choiceID']]:c['totalVotes']for c in cr['choices']};ck(sum(cv.values())==cr['totalVotes']==sc['locations'][fips]['totalVotes'],'all county original control totals')
  nativecounter=Counter()
  for nid,nloc in l['locations'].items():originalinventory.append({'county_fips':fips,'native_id':nid,'raw_location':nloc,'source_pointer':f'/response/locations/{fips}/locations/{nid}'})
  for nid,r in cr['locations'].items():
   sr=savednative[fips,nid];same(sr['raw_result'],r,'whole raw source native result');same(sr['raw_location'],l['locations'][nid],'whole raw source native descriptor')
   ck(sr['source_id']==f'{year}-federal-{fips}'and sr['source_pointer']==f'/response/contests/{cid}/locations/{nid}','exact original source pointer')
   vv={sid[c['choiceID']]:c['totalVotes']for c in r['choices']};ck(len(vv)==len(r['choices'])and sum(vv.values())==r['totalVotes'],'native complete source candidate vector')
   nativecounter.update(vv);api.append({'key':sourcekey(f'{year}-api',fips,nid),'county_fips':fips,'native_id':nid,'native_name':l['locations'][nid]['locationName'],'votes':r['totalVotes'],'candidates':vv});nativeobjects+=1
  ck(dict(nativecounter)==cv,'each parent complete native candidate closure');summed.update(cv);parent[fips]={'candidates':cv,'votes':cr['totalVotes'],'name':l['locationName']}
 same(saved['native_inventory'],originalinventory,'every whole returned native descriptor inventory')
 ck(dict(summed)==statevotes and sum(statevotes.values())==sc['totalVotes'],'all75 controls close original statewide candidate vector')
 original_native[f'{year}-api']=api;countycontrols[year]=parent
 # FullData lane: every complete raw wrapper is independently reconstructed.
 chosen=[(i,v)for i,v in enumerate(full['ContestData'])if v['ContestName']==title];ck(len(chosen)==1,'actual FullData selected contest')
 ci,fc=chosen[0];fsaved=read(T/f'extracted/{year}-full-original-relevant-records.json.gz');same(fsaved['state'],{k:v for k,v in fc.items()if k!='Counties'},'whole FullData original state fields');same(fsaved['turnout'],full['Turnout'],'whole FullData turnout fields');same(fsaved['election_info'],full['ElectionInfo'],'whole FullData election metadata')
 leaves=[];fullparents=defaultdict(Counter);fullsum=Counter()
 ck(len(fsaved['wrappers'])==len(fc['Counties']),'all original FullData wrappers preserved')
 for wi,(w,sr)in enumerate(zip(fc['Counties'],fsaved['wrappers'])):
  same(sr['raw'],w,'every full original wrapper with complete native/candidate fields');fips=reverse[w['CountyName'].upper()];wsum=Counter()
  for pi,p in enumerate(w['Precincts']):
   vv=votes(p['Candidates']);ck(sum(vv.values())==p['TotalVotes'],'FullData native original candidate sum');wsum.update(vv)
   leaves.append({'key':sourcekey(f'{year}-full',fips,f'{wi}/{pi}'),'county_fips':fips,'native_id':None,'native_name':p['PrecinctName'],'votes':p['TotalVotes'],'candidates':vv})
  ck(dict(wsum)==votes(w['Candidates'])and sum(wsum.values())==w['TotalVotes'],'whole wrapper totals are not extra counties');fullparents[fips].update(wsum);fullsum.update(wsum)
 ck(dict(fullsum)==votes(fc['Candidates'])and sum(fullsum.values())==fc['TotalVotes'],'full original native/state FullData closure')
 original_native[f'{year}-full']=leaves
 for fips,vv in fullparents.items():
  for name,value in vv.items():
   if value!=parent[fips]['candidates'][name]:diffs.append({'year':year,'county_fips':fips,'candidate':name,'api':parent[fips]['candidates'][name],'full':value,'full_minus_api':value-parent[fips]['candidates'][name]})
 # Entire raw county turnout/state source envelopes remain exact, with empty native locations.
 ts=obj(f'{year}-turnout-state');tsaved=read(T/f'extracted/{year}-turnout-original-records.json.gz');same(tsaved['state'],ts,'complete original state turnout response')
 for fips in locs:
  r=obj(f'{year}-turnout-{fips}');same(tsaved['counties'][fips],r,'whole original county turnout response/clocks/nulls');ck(r['response']['locations']=={},'empty native turnout publication is not zero')
  ctrl=ts['response']['locations'][fips];ck(r['response']['registeredVoters']==ctrl['registeredVoters']and r['response']['totalBallotsCast']==ctrl['totalBallotsCast'],'all county/state turnout controls');same(r['response']['ballotsCast'],ctrl['ballotsCast'],'whole literal All method ballot fields')
 ck(sum(v['registeredVoters']for v in ts['response']['locations'].values())==ts['response']['registeredVoters']and sum(v['totalBallotsCast']for v in ts['response']['locations'].values())==ts['response']['totalBallotsCast'],'whole turnout statewide balance')
 for field in ['VotesCast','RegisteredVoters']:
  orders[f'{year}-county-{field}']=[{'key':sourcekey(f'{year}-full-{field}',reverse[r['CountyName'].upper()],r['CountyName']),'votes':r[field]}for r in full['Turnout']['CountyTurnout']]
 orders[f'{year}-county-contest']=[{'key':sourcekey(f'{year}-api-county',k,v['name']),'votes':v['votes']}for k,v in parent.items()]
 yearproof[str(year)]={'contest_id':cid,'all_counties':75,'API_native':len(api),'Full_native':len(leaves),'API_candidate_vector':statevotes,'API_total':sc['totalVotes'],'Full_candidate_vector':dict(fullsum),'Full_total':fc['TotalVotes'],'ballots':ts['response']['totalBallotsCast'],'registration':ts['response']['registeredVoters']}
for lane,expected in original_native.items():
 actual={r['key']:r for r in universes[lane]};ck(len(actual)==len(expected),'full universe unique source keys')
 for e in expected:
  a=actual[e['key']]
  for k,v in e.items():same(a[k],v,'entire original-count native field '+k)
  for k in ['ballots_cast','registered_voters','blank','undervotes','overvotes']:ck(a[k]is None,'unavailable native field not invented0')
 orders[lane]=expected
same(diffs,read(T/'extracted/full-vs-api-county-candidate-differences.json'),'all19 FullData/API county candidate differences stay exact')
# Build full original seven-candidate/method native vectors solely from original OOXML.
byparent={v['name'].upper():k for k,v in countycontrols[2024].items()};grouped=defaultdict(list)
for r in source_rows:grouped[r['county'],r['precinct']].append(r)
primary=[];bycounty=defaultdict(Counter)
for(county,native),rows in grouped.items():
 fips=byparent[county];ck(len(rows)==len({r['choice']for r in rows})==7,'all seven source candidate rows per native')
 vv={r['choice']:int(r['total votes'])for r in rows};mm={m:sum(int(r[m])for r in rows)for m in headers[5:9]}
 for r in rows:ck(sum(int(r[m])for m in headers[5:9])==int(r['total votes']),'every raw candidate method partition')
 bycounty[fips].update(vv);primary.append({'key':sourcekey('2024-xlsx',fips,native),'county_fips':fips,'native_name':native,'votes':sum(vv.values()),'candidates':vv,'methods':mm,'source_rows':[r['row']for r in rows],'party_literals':{r['choice']:r['party']for r in rows}})
ck(len(primary)==2841,'all original literal native units')
for fips,vv in bycounty.items():same(dict(vv),countycontrols[2024][fips]['candidates'],'every original county/candidate workbook/API balance')
primarysaved={r['key']:r for r in universes['2024-xlsx']}
for e in primary:
 for k,v in e.items():same(primarysaved[e['key']][k],v,'every original primary field '+k)
orders['2024-xlsx']=primary
for method in headers[5:9]:orders['2024-xlsx-'+method.lower().replace(' ','-')]=[{'key':r['key'],'votes':r['methods'][method]}for r in primary]
statistics=read(T/'orders/statistics.json');ck(set(orders)==set(statistics)and len(orders)==20,'all20 complete source scoped orders')
rankproof={}
for lane,rows in orders.items():
 ordered=sorted(rows,key=lambda r:(-r['votes'],r['key']));den=sum(r['votes']for r in rows);saved=list(csv.DictReader((T/'orders'/(lane+'.csv')).open(newline='')));cum=0;cross=None
 ck(len(saved)==len(rows),'complete whole order rows')
 for i,(r,sr)in enumerate(zip(ordered,saved),1):
  cum+=r['votes'];ck(sr['key']==r['key']and int(sr['votes'])==r['votes']and int(sr['rank'])==i and int(sr['cumulative_votes'])==cum,'every original-count descending/cumulative row')
  if cross is None and 5*cum>=4*den:cross=i;before=cum-r['votes'];prefix=cum
 st=statistics[lane];ck((den,cross,before,prefix)==(st['denominator'],st['minimum80_count'],st['preceding_votes'],st['minimum80_votes']),'whole original integer80 crossing')
 ck(sum(r['votes']for r in ordered[:15])==st['top15_votes']and den-prefix==st['remainder_votes'],'full top15 and remainder')
 rankproof[lane]={'count':len(rows),'denominator':den,'minimum80':cross,'prefix':prefix,'preceding':before}
c=read(T/'priority-set.json');ordered=sorted(primary,key=lambda r:(-r['votes'],r['key']));ck([r['key']for r in c['full_order']]==[r['key']for r in ordered]and c['ordered_priority_keys']==[r['key']for r in ordered[:1056]]and c['remainder_keys']==[r['key']for r in ordered[1056:]],'full complete primary dispatch arrays')
ck(len(c['all75parents'])==75 and len(c['priority_parent_fips'])==68,'whole75 and68priorityparent distinction')
for p in c['all75parents']:
 for lane,children in p['source_native_constituents'].items():
  expected=[r for r in(primary if lane=='2024-xlsx'else original_native[lane])if r['county_fips']==p['county_fips']]
  ck([r['key']for r in children]==[r['key']for r in expected],'whole native ordered parent constituent arrays')
# Independent original PDF extraction, full candidate headers and all525 county fields.
with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
 f.write(original('sos-2024-general-state-original'));f.flush();text=subprocess.run(['pdftotext','-layout',f.name,'-'],capture_output=True,check=True).stdout.decode()
section=text.split('U.S. President',1)[1].split('U.S. Congress District 01',1)[0];pdf=read(T/'extracted/2024-pdf-controls.json');same(re.findall(r'#\d-([^\n]+) \(([^)]+)\)',section),[tuple(v)for v in pdf['candidates']],'whole original printed candidate/ticket/party headers')
for row in pdf['rows']:
 line=section.splitlines()[row['section_line']-1];ck(line==row['raw_line'],'every PDF exact line/source position');tokens=[int(v)for v in re.findall(r'\d+',line)];ck(tokens==row['values'],'every source county integer token')
 if row['county']!='Totals':
  ck(len(row['values'])==8 and sum(row['values'][:-1])==row['values'][-1],'all source county footer balances')
  # PDF capitalization/spacing is a separate literal administrative representation.
  norm=lambda s:re.sub('[^A-Z]','',s.upper());fips=next(k for k,v in countycontrols[2024].items()if norm(v['name'])==norm(row['county']))
  for name,value in zip([v[0]for v in pdf['candidates']],row['values'][:-1]):ck(bycounty[fips][name]==value,'all525 original county candidate cells')
out={'status':'pass_independent_full_turnout_original_source_and_scope_review','checks':N,'producer_manifest':pin(T/'asset-manifest.json'),'whole_source_receipts':len(receipts),'retained_failure_bodies':failures,'whole_workbook_data_rows':allrows,'selected_workbook_rows':len(source_rows),'selected_raw_typed_cells':rawcellchecks,'complete_county_result_bodies':countybodies,'whole_native_result_objects':nativeobjects,'all225_county_turnout_envelopes':True,'all20_original_count_orders':rankproof,'source_controls':yearproof,'preserved_FullData_API_county_candidate_differences':len(diffs),'native2024':2841,'priority':1056,'remainder':1785,'all_parents':75,'priority_parents':68,'producer_import_or_write':False,'no_geometric_or_current_ID_approval':True,'no_manual_PDF_scope_claim':'Full original text/header/cell replay only in this checker'}
body=(json.dumps(out,indent=2)+'\n').encode();p=S/'data/coordinator-turnout-original-review.json'
if '--check'in sys.argv:ck(p.read_bytes()==body,'frozen exact review replay')
else:p.write_bytes(body)
print(json.dumps({k:v for k,v in out.items()if k not in ['all20_original_count_orders','source_controls','retained_failure_bodies']}))
