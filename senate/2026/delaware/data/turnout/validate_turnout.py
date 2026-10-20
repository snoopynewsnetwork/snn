#!/usr/bin/env python3
"""Offline checks of originals, positions, complete scopes, integer ranks and sealed assets.
--seal writes validation.json then a complete asset manifest; --check is read-only.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,gzip,hashlib,re,csv,io,collections,datetime
D=Path(__file__).resolve().parent;X=D/'extracts';ROOT=D.parent.parent;NEWS=D.parent/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(n):return json.loads((X/n).read_text())
def verify():
 checks=[]
 def ck(name,condition,detail=None):
  checks.append({'check':name,'pass':bool(condition),'detail':detail});assert condition,(name,detail)
 mf={r['id']:r for r in json.loads((D/'source/original-inputs.json').read_text())};raw={};texts={}
 for sid,a in mf.items():
  z=(NEWS/a['asset']).read_bytes();b=gzip.decompress(z);ck('original stored/raw hash '+sid,sha(z)==a['stored_sha256'] and sha(b)==a['raw_sha256'],{'stored_bytes':len(z),'raw_bytes':len(b)});ck('original declared entity byte length '+sid,len(b)==a['bytes'])
  raw[sid]=b
  if 'report' in sid or sid=='official-2022-report':texts[sid]=b.decode('utf-8-sig')
 receipts=list((D/'source').glob('*.receipt.json'))
 for p in receipts:
  a=json.loads(p.read_text());z=(p.parent/a['body_path']).resolve().read_bytes();b=gzip.decompress(z)
  ck('acquisition body hashes/lengths '+a['id'],sha(z)==a['stored_sha256'] and sha(b)==a['raw_sha256'] and len(z)==a['stored_bytes'] and len(b)==a['raw_bytes'])
  headers=(p.parent/a['headers_path']).read_text();ck('HTTP headers present or explicit network failure '+a['id'], bool(headers) if a['curl_exit']==0 else a['http'].get('http_code')==0)
  if a['curl_exit']==0:ck('successful source HTTP200 '+a['id'],a['http']['http_code']==200)
 rows=[json.loads(l) for l in gzip.decompress((X/'candidate-rows.jsonl.gz').read_bytes()).splitlines()]
 ck('complete required candidate rows',len(rows)==10699);keys=set()
 for r in rows:
  key=(r['source_id'],r['view'],r['office_key'],r['native_key'],r['candidate'],r['party']);ckname=None
  assert key not in keys;keys.add(key)
  t=texts[r['source_id']];s,e=r['row_start'],r['row_end'];assert t[s:e].startswith('<tr') and t[s:e].endswith('</tr>');assert t[r['table_start']:r['table_end']].startswith('<table')
  for c in r['cells']:assert c['raw_cell_html'] in t[s:e]
  for field,v in r['numeric'].items():
   if v is not None:assert v>=0 and int(r['raw_fields'][field].replace(',',''))==v
 ck('unique native candidate/party source identities and every raw table/row/cell position',True,{'candidate_rows':len(keys)})
 expected={(2024,'USSenator'):(530,500606),(2024,'PresidentandVicePresident'):(533,511697),(2022,'RepresentativeinCongress'):(516,321649),(2020,'USSenator'):(436,490935),(2020,'PresidentandVicePresident'):(439,504010)}
 source_csv={2024:'sos-2024-csv',2022:'sos-observed-2022-state-csv',2020:'sos-observed-2020-state-csv'};fields={'Machine Votes':'machinevotessum','Absentee Votes':'absenteevotessum','Early Voting Votes':'earlyvotessum','Total Votes':'totalvotessum'}
 hist=read('historical-rankings.json')
 for (year,office),(units,total) in expected.items():
  rr=[r for r in rows if r['year']==year and r['office_key']==office];sr=[r for r in rr if r['view']=='statewide'];allcsv=list(csv.DictReader(io.StringIO(raw[source_csv[year]].decode('utf-8-sig'))))
  ed=[r for r in rr if r['view']=='byelectiondist'];ck(f'native full coverage {year}/{office}',len(set(r['native_key'] for r in ed))==units and sum(r['numeric']['Total Votes'] for r in ed)==total)
  for r in sr:
   ctl=[c for c in allcsv if c['candidatename']==r['candidate'] and c['partyname']==r['party'] and int(c['totalvotessum'])==r['numeric']['Total Votes']];assert len(ctl)==1;c=ctl[0]
   for view in ['byelectiondist','byrepdist']:
    for f,cf in fields.items():
     vals=[a['numeric'][f] for a in rr if a['view']==view and a['candidate']==r['candidate']]
     assert vals
     if year==2020 and f=='Early Voting Votes':assert all(v is None for v in vals) and int(c[cf])==0
     else:assert all(v is not None for v in vals) and sum(vals)==int(c[cf])
  ck(f'all candidate/method ED/RD primary CSV controls {year}/{office}',True)
  for r in [r for r in rr if r['view']=='bycounty']:assert sum(int(r['raw_fields'][k].replace(',','')) for k in ['New Castle','Kent','Sussex'])==int(r['raw_fields']['State'].replace(',',''))
  for r in [r for r in rr if r['view']=='bycountyw']:
   f=r['raw_fields'];c=next(q for q in rr if q['view']=='bycounty' and q['candidate']==r['candidate'])['raw_fields'];assert int(f['Wilmington'].replace(',',''))+int(f['Rest of New Castle'].replace(',',''))==int(c['New Castle'].replace(',',''))
   for k in ['Kent','Sussex','State']:assert f[k]==c[k]
  ck(f'county disjoint and Wilmington partition controls {year}/{office}',True)
  a=next(a for a in hist if a['year']==year and a['office_key']==office);vol=collections.Counter()
  for r in ed:vol[r['native_key']]+=r['numeric']['Total Votes']
  order=sorted(vol,key=lambda k:(-vol[k],k));ck(f'full descending order {year}/{office}',[(r['native_key'],r['votes']) for r in a['full_order']]==[(k,vol[k]) for k in order]);cum=0
  for i,r in enumerate(a['full_order'],1):cum+=r['votes'];assert r['rank']==i and r['cumulative_votes']==cum and r['share_fraction']==[r['votes'],total]
  n=a['minimum80_count'];before=sum(vol[k] for k in order[:n-1]);at=sum(vol[k] for k in order[:n]);ck(f'integer minimum80+weights {year}/{office}',5*before<4*total<=5*at and sum(vol.values())==total and before==a['preceding_votes'] and at==a['priority_votes'])
 ck('2020 native early null positions',sum(r['numeric']['Early Voting Votes'] is None for r in rows if r['year']==2020 and r['view']=='byelectiondist')==3500)
 c=json.loads((D/'priority-set.json').read_text());ck('exact primary minimum crossing',c['unit_count']==530 and c['total']==500606 and c['top15_votes']==35875 and c['minimum80_count']==311 and c['preceding_votes']==399708 and c['crossing_key']=='ElectionDistrict0807' and c['crossing_votes']==831 and c['priority_votes']==400539 and c['remainder_count']==219 and c['remainder_votes']==100067)
 order=[r['native_key'] for r in c['full_order']];ck('complete disjoint priority/remainder/top15',c['ordered_priority_keys']==order[:311] and c['ordered_remainder_keys']==order[311:] and c['ordered_top15_keys']==order[:15] and set(order[:311]).isdisjoint(order[311:]) and len(set(order))==530)
 ck('not accepted or current geometry',c['formal_coordinator_acceptance'] is False and c['current_geography_approved'] is False)
 sample=read('sample-ballot-identities.json');sampletext=gzip.decompress((D/'source/sample-ballot-index-2024.body.gz').read_bytes()).decode('utf-8-sig')
 ck('sample ballot index complete source-native coverage',len(sample)==533 and {r['native_key'] for r in sample}=={r['native_key'] for r in c['all_available_source_constituents'] if r['year']==2024 and r['report_present']})
 for a in sample:
  source_row=sampletext[a['source_char_start']:a['source_char_end']];assert source_row.startswith('<tr') and source_row.endswith('</tr>')
  assert a['county_literal'].upper()==next(r['parent']['county'] for r in c['all_available_source_constituents'] if r['year']==2024 and r['native_key']==a['native_key'])
  assert c['additional_native_sources']['sample_ballot_index_2024']==sample
 ck('sample ballot original positions and explicit county parent agreement',True)
 censustext=gzip.decompress((D/'source/census-county-identifiers.body.gz').read_bytes()).decode('utf-8-sig')
 censusrows=re.findall(r'<tr[^>]*>(.*?)</tr>',censustext,re.S|re.I)
 ck('Census county identifier primary evidence',all(any(code in r and county in r for r in censusrows) for code,county in [('10001','Kent'),('10003','New Castle'),('10005','Sussex')]))
 cr=list(csv.DictReader((D.parent/'county-turnout.csv').open()));ck('main CSV complete native order',len(cr)==530 and [r['native_key'] for r in cr]==order)
 for r in cr:
  assert int(r['blunt_rochester'])+int(r['hansen'])+int(r['katz'])==int(r['senate_candidate_votes']);assert int(r['machine_candidate_votes'])+int(r['absentee_candidate_votes'])+int(r['early_candidate_votes'])==int(r['senate_candidate_votes'])
  assert r['ballots_cast']==r['generic_writein_votes']==r['blank_ballots']==r['undervotes']==r['overvotes']==''
  assert r['county_fips'] in ['10001','10003','10005']
 ck('all CSV candidate/method/null/FIPS fields',True)
 cov=read('native-coverage.json');ck('complete native union and source cases',len(cov)==1495 and len({(r['year'],r['native_key']) for r in cov})==1495)
 unknown=[r for r in cov if r['parent'] is None or r['parent']['county'] is None];ck('unparented exact scope',[r['native_key'] for r in unknown]==['ElectionDistrict0218','ElectionDistrict3117','ElectionDistrict4117'] and all(r['year']==2020 for r in unknown))
 st=read('structure-2024.json');ck('structure complete and administrative identities',len(st)==537 and len([r for r in st.values() if r['footnote']])==6 and len(c['administrative_cases'])==6)
 for v in st.values():assert (D/'source/district-structure.txt').read_text().splitlines()[v['source_line']-1]==v['raw_line']
 part=read('participation-totals.json');ck('full participation totals/ED scope',len(part)==1631 and sum(r['level']=='ed' for r in part)==1491)
 for y in [2024,2022,2020]:
  s=gzip.decompress((D/'source'/f'participation-{y}.body.gz').read_bytes()).decode('utf-8-sig');rr=[r for r in part if r['year']==y]
  for r in rr:assert s[r['source_char_start']:r['source_char_end']]==r['raw_line']
  for f in ['registered','voted']:
   total=next(r['values']['Total'][f] for r in rr if r['level']=='state')
   for lev in ['ed','rd','county']:assert sum(r['values']['Total'][f] for r in rr if r['level']==lev)==total
 ck('all participation original line positions and state/RD/ED/county balances',True)
 reg=read('registration-november.json');ck('all November RD native rows and sparse nulls',len(reg)==1477 and sum(r['registered'] is None for r in reg)==4)
 for r in reg:
  if r['year']==2020:
   s=gzip.decompress((D/'source/registration-2020-november.body.gz').read_bytes()).decode('utf-8-sig');assert s[r['source_char_start']:r['source_char_end']].startswith('<tr')
 w=read('writein-rows.json');ck('all separate WI row universes/totals',[(y,len([r for r in w if r['year']==y]),sum(r['values']['Grand Total'] for r in w if r['year']==y)) for y in [2024,2022,2020]]==[(2024,24,1215),(2022,2,18),(2020,17,336)])
 for r in w:
  assert r['values']['Provisional'] is None
  assert sum(v for k,v in r['values'].items() if k!='Grand Total' and v is not None)==r['values']['Grand Total']
 ck('WI method cells/pages/totals and blank provisional preserved',True)
 universe=read('candidate-universe.json');ck('independent declared Senate universe no rows',all(r['senate_declared_writein_rows']==0 for r in universe if r['list_type']=='w'))
 for rel in ['peer/reconciliation-v1.json','peer/rank-reconciliation.json','peer/supplement-reconciliation.json']:ck('independent peer agreement '+rel,json.loads((D/rel).read_text())['pass'])
 for frozen in [D/'source/stable-supplement-v1.json']:
  for r in json.loads(frozen.read_text()):assert sha((D/r['path']).read_bytes())==r['sha256'] and (D/r['path']).stat().st_size==r['bytes']
 ck('own stable supplemental files immutable',True)
 for cap in (D/'peer').rglob('capture-manifest.json'):
  for a in json.loads(cap.read_text()):assert sha((D/a['capture_path']).read_bytes())==a['sha256'] and (D/a['capture_path']).stat().st_size==a['bytes']
 ck('all immutable peer captures hashes/lengths',True)
 for a in json.loads((D/'source/visual-review.json').read_text())['reviews']:assert sha((D/a['path']).read_bytes())==a['sha256']
 ck('visually reviewed PDF raster hashes',True)
 for f in [ROOT/'turnout.md',D/'source/SCHEMA.md']:
  for target in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   if '://' in target or target.startswith('#'):continue
   target=target.split('#')[0];resolved=(f.parent/target).resolve();assert resolved.exists() or ('--seal' in sys.argv and resolved in [(D/'validation.json').resolve(),(D/'asset-manifest.json').resolve()]),(str(f),target)
 ck('all relative report/schema links resolve',True)
 files=[p for p in D.rglob('*') if p.is_file()]+[ROOT/'turnout.md',D.parent/'county-turnout.csv'];ck('strict individual artifact bounds',all(p.stat().st_size<40000000 for p in files),{'max_bytes':max(p.stat().st_size for p in files),'owned_files_before_seal':len(files)})
 ck('no dependency/cache directories',not any(p.name in ['__pycache__','node_modules','.venv','venv'] for p in D.rglob('*') if p.is_dir()))
 return {'status':'pass','scope':'complete historical source research; exact whole-state named contest/method/native reconciliation; no current geometry/collector/forecast approval','checks':checks,'primary_total':500606,'top15_votes':35875,'minimum80_count':311,'priority_votes':400539,'preceding_votes':399708,'native_senate_count':530,'all_year_native_union':1495,'known_material_limits':['cast-ballot/blank/under/over/generic write-in counts unavailable in retained whole-state products','2020 president-only native county parents unavailable for0218/3117/4117; one Biden vote unallocated to county','separate 2024/2020presidential and2022House named write-ins have no ED allocation','registration/participation definitions, dates and native universes differ; no cross-year or current boundary equivalence']}
def manifest():
 paths=sorted([p for p in D.rglob('*') if p.is_file() and p.name!='asset-manifest.json']+[ROOT/'turnout.md',D.parent/'county-turnout.csv']);owned=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in paths]
 mf=json.loads((D/'source/original-inputs.json').read_text());shared=[];seen=set()
 for a in mf:
  p=NEWS/a['asset'];key=str(p.relative_to(ROOT))
  if key not in seen:shared.append({'path':key,'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size,'raw_sha256':a['raw_sha256'],'original_source_id':a['id'],'ownership':'shared original read-only by exact hash'});seen.add(key)
 return {'schema_version':'DE-turnout-assets-v1','scope':'every owned file except this self-referential manifest; all referenced frozen primary input bodies','limit_bytes_exclusive':40000000,'owned':owned,'shared_originals':shared}
if __name__=='__main__':
 result=verify()
 if '--seal' in sys.argv:
  (D/'validation.json').write_text(json.dumps(result,indent=2)+'\n');(D/'asset-manifest.json').write_text(json.dumps(manifest(),indent=2)+'\n');print('SEALED',len(result['checks']),'checks; complete asset manifest written')
 else:
  saved=json.loads((D/'asset-manifest.json').read_text());now=manifest();assert saved==now,'asset manifest mismatch';prior=json.loads((D/'validation.json').read_text());assert prior['status']=='pass';print('PASS',len(result['checks']),'offline checks; all sealed hashes/bytes/coverage and relative links verified')
