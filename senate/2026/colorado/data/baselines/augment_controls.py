#!/usr/bin/env python3
"""Independently read supplemental original turnout tables and retain exact comparison witnesses."""
from pathlib import Path
from collections import defaultdict
import gzip,json,hashlib,re,subprocess,tempfile,io,csv
from extract import D,Tables,dump,gzjson,csvout

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 N=D.parent/'news';manifest={x['id']:x for x in json.loads((N/'manifest.json').read_text())};pins=json.loads((D/'source/reused-originals.json').read_text());sources={}
 for y,sid in [(2024,'sos-2024-abstract'),(2020,'sos-2020-booklet-archive')]:
  a=manifest[sid];stored=(N/a['asset']).read_bytes();raw=gzip.decompress(stored);assert sha(stored)==a['stored_sha256']and sha(raw)==a['raw_sha256'];pins.append(dict(a,path='../news/'+a['asset']))
  with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
   f.write(raw);f.flush();text=subprocess.check_output(['pdftotext','-layout',f.name,'-']).decode()
  (D/f'extracts/{sid}-full-text.txt.gz').write_bytes(gzip.compress(text.encode(),mtime=0));sources[y]=text.split('\f')
 # New original source was acquired by turnout peer. Reuse immutable original bytes, never its derivative values.
 pm=D.parent/'turnout/source/acquisition.json';frozen=D/'source/supplemental-originals.json'
 if not frozen.exists():dump(frozen,[x for x in json.loads(pm.read_text())if x['id']in ['turnout-2022','census-colorado-codes']])
 original_acquisition=json.loads(frozen.read_text());a=next(x for x in original_acquisition if x['id']=='turnout-2022');sp=pm.parent/a['asset'];stored=sp.read_bytes();raw=gzip.decompress(stored);assert sha(stored)==a['stored_sha256']and sha(raw)==a['raw_sha256']and len(raw)==a['raw_bytes'];pins.append(dict(a,path='../turnout/source/'+a['asset']));tp=Tables();tp.feed(raw.decode())
 a=next(x for x in original_acquisition if x['id']=='census-colorado-codes');sp=pm.parent/a['asset'];stored=sp.read_bytes();raw=gzip.decompress(stored);assert sha(stored)==a['stored_sha256']and sha(raw)==a['raw_sha256'];pins.append(dict(a,path='../turnout/source/'+a['asset']));cp=Tables();cp.feed(raw.decode());head=cp.rows[0]['cells'];fips={r['cells'][head.index('BASENAME')]:r['cells'][head.index('GEOID')]for r in cp.rows[1:]};assert len(fips)==64

 rows=list(csv.DictReader((D.parent/'county-baselines.csv').open()));counties={x['county_literal']for x in rows};turnout={y:defaultdict(dict)for y in [2024,2022,2020]};positions=[]
 for y,pp in [(2024,[(181,'active'),(182,'registered')]),(2020,[(165,'active'),(166,'registered')])]:
  for page,role in pp:
   found={}
   for line,text in enumerate(sources[y][page-1].splitlines(),1):
    fields=re.split(r'\s{2,}',text.strip())
    if fields[0]not in counties|{'Total'}:continue
    assert len(fields)==4;v=[int(t.replace(',',''))for t in fields[1:3]];found[fields[0]]=v
    positions.append(dict(year=y,county_literal=fields[0],role=role,page=page,line=line,raw_line=text,raw_fields=fields,values=v))
    if fields[0]!='Total':turnout[y][fields[0]][role]=v[0];turnout[y][fields[0]]['ballots']=v[1]
   assert set(found)==counties|{'Total'}
   for k in [0,1]:assert sum(v[k]for c,v in found.items()if c!='Total')==found['Total'][k]
 # two consecutive full2022 tables with their own headers/footer positions.
 header=None;role=None;footers=[]
 for pos,row in enumerate(tp.rows,1):
  f=row['cells']
  if f and any('Active'in c for c in f):header=f;role='active';continue
  if f and any('Registered'in c for c in f):header=f;role='registered';continue
  if not f or f[0]not in counties|{'Total'}:continue
  assert role and len(f)==4;v=[int(t.replace(',',''))for t in f[1:3]];positions.append(dict(year=2022,county_literal=f[0],role=role,source='turnout-2022',source_table_row=pos,raw_fields=f,values=v))
  if f[0]=='Total':footers.append((role,v));continue
  turnout[2022][f[0]][role]=v[0]
  if 'ballots'in turnout[2022][f[0]]:assert turnout[2022][f[0]]['ballots']==v[1]
  turnout[2022][f[0]]['ballots']=v[1]
 assert len(footers)==2
 for role,v in footers:
  assert sum(r[role]for r in turnout[2022].values())==v[0];assert sum(r['ballots']for r in turnout[2022].values())==v[1]
 disagreements=[]
 for r in rows:
  y=int(r['year']);t=turnout[y][r['county_literal']];assert set(t)=={'active','registered','ballots'}
  for field,cf in [('registered','registered_voters'),('ballots','administrative_ballots')]:
   if t[field]!=int(r[cf]):disagreements.append(dict(year=y,county=r['county_literal'],field=field,turnout_table=t[field],contest_abstract=int(r[cf]),difference=t[field]-int(r[cf]),qualification='different original publication controls; retained without allocation or rescaling'))
  r.update(county_fips=fips[r['county_literal']],active_voters=t['active'],turnout_registered_voters=t['registered'],turnout_table_ballots=t['ballots'],registration_date='unknown beyond historical election/publication vintage',registration_definition='contest abstract eligible registered; turnout table active/registered retained separately')
 csvout(D.parent/'county-baselines.csv',rows);dump(D/'source/reused-originals.json',list({(a['id'],a['path']):a for a in pins}.values()));dump(D/'extracts/county-turnout-registration.json',turnout);gzjson(D/'extracts/turnout-control-positions.jsonl.gz',positions);dump(D/'extracts/administrative-source-disagreements.json',disagreements)
 # All historical orders and source-native county maps; zero rows survive. No crossyear native join.
 native=[]
 with gzip.open(D/'native-baselines.csv.gz','rt')as f:native=list(csv.DictReader(f))
 maps={};orders={}
 for y in [2024,2022,2020]:
  rs=[r for r in native if int(r['year'])==y];ordered=sorted(rs,key=lambda r:(-int(r['candidate_votes']),r['key']));bycounty=defaultdict(list)
  for r in rs:bycounty[r['county_literal']].append(r['key'])
  maps[y]=dict(bycounty);cum=0;out=[]
  for i,r in enumerate(ordered,1):cum+=int(r['candidate_votes']);out.append(dict(rank=i+0,key=r['key'],candidate_votes=int(r['candidate_votes']),source_record=int(r['source_record']),cumulative_votes=cum))
  orders[y]=out
 dump(D/'native-hierarchy.json',maps);dump(D/'historical-orders.json',orders)
 # Candidate rows must reconcile individually at every aggregation, not just A/B/other.
 rawrows=[json.loads(x)for x in gzip.decompress((D/'extracts/original-csv-records.jsonl.gz').read_bytes()).splitlines()];checks=0
 for y in [2024,2022,2020]:
  rs=[r for r in rawrows if r['year']==y];sr=next(r for r in rs if r['level_literal']=='State');cr=[r for r in rs if r['level_literal']=='County'];nr=[r for r in rs if r['level_literal']=='Precinct'];n=len(sr['header_fields'])-2
  for col in range(2,n+2):
   assert sum(int(r['raw_fields'][col])for r in cr)==int(sr['raw_fields'][col]);checks+=1
   for r in cr:
    assert sum(int(v['raw_fields'][col])for v in nr if v['county_literal']==r['county_literal'])==int(r['raw_fields'][col]);checks+=1
 dump(D/'extracts/all-column-reconciliation.json',dict(checks=checks,all_candidate_and_both_pseudocandidate_columns=True,source_disagreements=disagreements));print(json.dumps(dict(turnout_positions=len(positions),administrative_disagreements=len(disagreements),all_column_checks=checks)))
if __name__=='__main__':main()
