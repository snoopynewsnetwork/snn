#!/usr/bin/env python3
"""Independent original-only extraction. No turnout derivative input."""
import csv,gzip,hashlib,io,json,zipfile,datetime,subprocess
import xml.etree.ElementTree as E
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[4]
SHARED=P.parent/'turnout/source'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,d):
 (P/name).parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
 if len(b)>=39000000:
  (P/(name+'.gz')).write_bytes(gzip.compress(b,mtime=0))
  if (P/name).exists():(P/name).unlink()
 else:(P/name).write_bytes(b)
def csvout(name,rows):
 if not rows:return
 with (P/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 if (P/name).stat().st_size>=39000000:
  (P/(name+'.gz')).write_bytes(gzip.compress((P/name).read_bytes(),mtime=0));(P/name).unlink()
def initialize():
 pins=[]
 for f in sorted(SHARED.rglob('*.receipt.json')):
  r=json.loads(f.read_text()); path=ROOT/r['shared_original_path'] if r.get('shared_original_path') else f.parent/(r.get('asset') or '__missing__')
  entry={'receipt_path':str(f.relative_to(ROOT)),'receipt_sha256':sha(f.read_bytes()),'receipt':r}
  if path.is_file():
   stored=path.read_bytes();raw=gzip.decompress(stored) if path.suffix=='.gz' else stored
   assert sha(raw)==r['raw_sha256'],f
   assert sha(stored)==r['stored_sha256'],f
   entry.update(path=str(path.relative_to(ROOT)),raw_sha256=sha(raw),stored_sha256=sha(stored),raw_bytes=len(raw),stored_bytes=len(stored))
  else:entry['unavailable']=True
  pins.append(entry)
 save('source/original-pins.json',pins)
def load(id):
 pins=json.loads((P/'source/original-pins.json').read_text())
 items=[r for r in pins if r['receipt']['id']==id and 'path' in r];assert items,id
 r=items[-1];p=ROOT/r['path'];b=p.read_bytes();assert sha(b)==r['stored_sha256'];return gzip.decompress(b) if p.suffix=='.gz' else b
def js(id):return json.loads(load(id))
def extract():
 records=[];controls=[];native=[];turnout=[];catalog=[]
 targets={2020:['560','673'],2022:['1123'],2024:['366']}
 infos={y:js(f'{y}-info')['response'] for y in targets}
 names={v['locationName']:k for k,v in infos[2024]['locations'].items()}
 # XLSX XML cells retain exact raw positions/types, not a dataframe normalization.
 z=zipfile.ZipFile(io.BytesIO(load('2024-xlsx-current')));ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 strings=[''.join(n.itertext()) for n in E.fromstring(z.read('xl/sharedStrings.xml'))]
 xrows=[]
 for row in E.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//m:row',ns):
  cells=[]
  for c in row:
   v=c.findtext('m:v',default=None,namespaces=ns);value=strings[int(v)] if c.get('t')=='s' else v
   cells.append({'position':c.get('r'),'type':c.get('t'),'value':value,'raw_value':v})
  if row.get('r')=='1':continue
  vals=[c['value'] for c in cells]
  if vals[2]=='U.S. President':
   xrows.append({'source_id':'2024-xlsx-current','row':int(row.get('r')),'cells':cells})
   for j,method in enumerate(['Election Day','Early Vote','Absentee','Provisional','total votes'],5):
    records.append(dict(lane='2024-xlsx',year=2024,contest='U.S. President',level='native',county=vals[0],county_id=names[vals[0]],native_id=None,native_name=vals[1],candidate_id=None,candidate=vals[3],party_id=None,party_literal=vals[4],method=method,votes=int(vals[j]),source_id='2024-xlsx-current',position=f"xl/worksheets/sheet1.xml/{cells[j]['position']}"))
 (P/'source/xlsx-president-rows.jsonl.gz').write_bytes(gzip.compress(('\n'.join(json.dumps(x,ensure_ascii=False) for x in xrows)+'\n').encode(),mtime=0))
 for y,ids in targets.items():
  info=infos[y];meta=js(f'{y}-metadata')['response']['contests'];state=js(f'{y}-federal-state')
  for cid in ids:
   m=meta[cid];catalog.append(dict(year=y,contest_id=cid,metadata=m,parties=info['parties'],vote_types=info['voteTypes']))
   for county_id,c in info['locations'].items():
    for ni,n in c['locations'].items():native.append(dict(year=y,contest_id=cid,county_id=county_id,county=c['locationName'],native_id=ni,native_name=n['locationName'],info_position=f'/response/locations/{county_id}/locations/{ni}',raw=n))
   def node(n,county_id,ni,level,source,pos):
    county=info['locations'][county_id]['locationName'] if county_id else None
    nn=info['locations'][county_id]['locations'].get(ni,{}).get('locationName') if ni else None
    controls.append(dict(lane=f'{y}-api',year=y,contest=m['contestName'],contest_id=cid,level=level,county_id=county_id,native_id=ni,total=n['totalVotes'],sum_choices=sum(c['totalVotes'] for c in n['choices']),source_id=source,position=pos,raw={k:v for k,v in n.items() if k not in ['locations']}))
    for i,ch in enumerate(n['choices']):
     cm=m['choices'][ch['choiceID']];party=info['parties'].get(ch['partyID'],{})
     records.append(dict(lane=f'{y}-api',year=y,contest=m['contestName'],level=level,county=county,county_id=county_id,native_id=ni,native_name=nn,candidate_id=ch['choiceID'],candidate=cm['name'],party_id=ch['partyID'],party_literal=party.get('partyName'),method='All',votes=ch['totalVotes'],source_id=source,position=f'{pos}/choices/{i}'))
   sc=state['response']['contests'][cid];node(sc,None,None,'state',f'{y}-federal-state',f'/response/contests/{cid}')
   for county_id,n in sc['locations'].items():node(n,county_id,None,'county',f'{y}-federal-state',f'/response/contests/{cid}/locations/{county_id}')
   for county_id,c in info['locations'].items():
    src=f'{y}-federal-{county_id}';co=js(src)['response']['contests'][cid]
    node(co,county_id,None,'county-native-response',src,f'/response/contests/{cid}')
    for ni,n in co['locations'].items():node(n,county_id,ni,'native',src,f'/response/contests/{cid}/locations/{ni}')
  for county_id,c in info['locations'].items():
   d=js(f'{y}-turnout-{county_id}')
   turnout.append(dict(year=y,county_id=county_id,county=c['locationName'],source_id=f'{y}-turnout-{county_id}',publication={k:v for k,v in d.items() if k!='response'},response=d['response']))
  full=js(f'{y}-full')
  for k,contest in enumerate(full['ContestData']):
   if not any(contest['ContestName']==meta[cid]['contestName'] for cid in ids):continue
   def fullnode(n,county,ni,nn,level,pos):
    controls.append(dict(lane=f'{y}-full',year=y,contest=contest['ContestName'],contest_id=None,level=level,county_id=names.get(county),native_id=ni,total=n['TotalVotes'],sum_choices=sum(c['TotalVotes'] for c in n['Candidates']),source_id=f'{y}-full',position=pos,raw={k:v for k,v in n.items() if k not in ['Counties','Precincts']}))
    for i,ch in enumerate(n['Candidates']):records.append(dict(lane=f'{y}-full',year=y,contest=contest['ContestName'],level=level,county=county,county_id=names.get(county),native_id=ni,native_name=nn,candidate_id=None,candidate=ch['Name'],party_id=None,party_literal=ch.get('PartyName'),method='All',votes=ch['TotalVotes'],source_id=f'{y}-full',position=f'{pos}/Candidates/{i}'))
   fullnode(contest,None,None,None,'state',f'/ContestData/{k}')
   for j,c in enumerate(contest['Counties']):
    pos=f'/ContestData/{k}/Counties/{j}';fullnode(c,c['CountyName'],str(j),None,'county-wrapper',pos)
    for l,n in enumerate(c['Precincts']):fullnode(n,c['CountyName'],f'{j}/{l}',n['PrecinctName'],'native',f'{pos}/Precincts/{l}')
 csvout('candidate-records.csv',records);save('source/contest-controls.json',controls);save('source/candidate-metadata.json',catalog);save('source/native-inventory.json',native);save('source/turnout-controls.json',turnout)
 # frozen complete order from independent XLSX and API lanes; exact integer crossing.
 ranks={}
 from collections import defaultdict
 for lane,level,contest in sorted(set((r['lane'],r['level'],r['contest']) for r in records if r['level'] in ['native','county'] and (r['method']=='All' or r['method']=='total votes'))):
  sums=defaultdict(int)
  for r in records:
   if (r['lane'],r['level'],r['contest'])==(lane,level,contest) and r['method'] in ['All','total votes']:
    key=(r['county_id'],r['native_name'] if lane.endswith('xlsx') else r['native_id']) if level=='native' else (r['county_id'],None);sums[key]+=r['votes']
  ranked=sorted(sums,key=lambda k:(-sums[k],k[0] or '',k[1] or ''));total=sum(sums.values());running=0;rows=[]
  for i,key in enumerate(ranked,1):
   before=running;running+=sums[key];rows.append(dict(rank=i,county_id=key[0],native_key=key[1],votes=sums[key],cumulative=running,priority=before*5<total*4))
  ranks[f'{lane}|{level}|{contest}']={'total':total,'order':rows}
 save('source/independent-rankings.json',ranks)
 save('source/extraction-controls.json',{'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_rows':len(records),'xlsx_rows':len(xrows),'native_inventory_rows':len(native),'turnout_responses':len(turnout),'source_controls':len(controls),'all_controls_balance':all(c['total']==c['sum_choices'] for c in controls),'no_peer_derivative_read':True})
if __name__=='__main__':
 import sys
 if '--initialize' in sys.argv:initialize()
 extract()
