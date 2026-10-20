"""Coordinator independent complete baseline original-position/source audit.
Reads fixed individual source pins; never imports producer parsers or counts.
"""
from pathlib import Path
import csv,gzip,hashlib,io,json,sys,xml.etree.ElementTree as ET,zipfile
S=Path(__file__).resolve().parents[1];B=S/'data/baselines';N=0

def ck(v,msg):
 global N
 N+=1
 if not v:raise AssertionError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def same(a,b,msg):ck(canon(a)==canon(b),msg)
def pointer(v,pos):
 for p in pos.split('/')[1:]:
  p=p.replace('~1','/').replace('~0','~');v=v[int(p)]if isinstance(v,list)else v[p]
 return v
mf=read(B/'asset-manifest.json');ck(sha((B/'asset-manifest.json').read_bytes())=='6d320e1b8b87fbea6788a7343544e39fab21dc81019c6f3e63251ba81baee8c4','actual final sealed package')
actual={str(p.relative_to(S))for p in B.rglob('*')if p.is_file()and p!=B/'asset-manifest.json'}|{'county-partisanship.md','data/county-baselines.csv'}
ck(actual=={r['path']for r in mf['assets']}and len(actual)==313,'complete original baseline membership')
for r in mf['assets']:
 p=S/r['path'];body=p.read_bytes();ck(len(body)==r['bytes']<40000000 and sha(body)==r['sha256'],'every exact sealed body')
raw={};receipts={};originals=read(B/'source/original-pins.json')
for r in originals:
 receipt=Path(r['receipt_path']).read_bytes();stored=Path(r['path']).read_bytes();entity=gzip.decompress(stored)
 ck(sha(receipt)==r['receipt_sha256']and json.loads(receipt)==r['receipt'],'complete exact individual original receipt')
 ck(sha(stored)==r['stored_sha256']and len(stored)==r['stored_bytes']and sha(entity)==r['raw_sha256']and len(entity)==r['raw_bytes'],'complete original response bytes')
 sid=r['receipt']['id'];ck(sid not in raw,'distinct source receipt identities');raw[sid]=entity;receipts[sid]=r['receipt']
# Whole original OOXML precise cell dictionary, no dataframe or derived input.
xbytes=raw['2024-xlsx-current'];ck(sha(xbytes)=='6509c03c4e32717d41e7ad561f813bcc702cf72b2a0b80c12e74cdee6b7dee94','primary XLSX source')
z=zipfile.ZipFile(io.BytesIO(xbytes));ck(z.testzip()is None,'all complete OOXML ZIP CRCs');ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
strings=[''.join(t.text or''for t in si.iter('{'+ns['m']+'}t'))for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
worksheet={};selected={};header=None
for rr in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('m:sheetData/m:row',ns):
 cells=[]
 for c in rr.findall('m:c',ns):
  v=c.find('m:v',ns);rv=v.text if v is not None else None;value=strings[int(rv)]if c.get('t')=='s'else rv
  cell={'position':c.get('r'),'type':c.get('t'),'value':value,'raw_value':rv};worksheet[c.get('r')]=cell;cells.append(cell)
 values=[c['value']for c in cells]
 if header is None:header=values;continue
 if values[2]=='U.S. President':selected[int(rr.get('r'))]=cells
savedrows=[json.loads(line)for line in gzip.decompress((B/'source/xlsx-president-rows.jsonl.gz').read_bytes()).splitlines()]
ck(len(savedrows)==len(selected)==19887,'every presidential OOXML source row')
for r in savedrows:same(r['cells'],selected[r['row']],'all raw original cells/type/shared-string/raw-v/address')
# Parse only exact complete originals needed by selected source records.
objects={}
def obj(sid):
 if sid not in objects:objects[sid]=json.loads(raw[sid])
 return objects[sid]
metadata={}
for y in [2020,2022,2024]:
 info=obj(f'{y}-info')['response'];meta=obj(f'{y}-metadata')['response']['contests'];metadata[y]=(info,meta)
# Source candidate/party/method/source-position fields at EVERY selected record.
records=0;bylane={};native_pos={};info_names={v['locationName']:k for k,v in metadata[2024][0]['locations'].items()}
with gzip.open(B/'candidate-records.csv.gz','rt')as f:
 for r in csv.DictReader(f):
  records+=1;yr=int(r['year']);position=r['position'];sid=r['source_id'];lane=r['lane'];bylane[lane]=bylane.get(lane,0)+1
  if lane=='2024-xlsx':
   addr=position.rsplit('/',1)[1];cell=worksheet[addr];cells=selected[int(''.join(c for c in addr if c.isdigit()))];values=[c['value']for c in cells]
   ck(int(r['votes'])==int(cell['value'])and r['candidate']==values[3]and r['party_literal']==values[4]and r['contest']==values[2]and r['county']==values[0]and r['native_name']==values[1]and r['county_id']==info_names[values[0]],'every original XLSX candidate/method/source identity')
   col=''.join(c for c in addr if c.isalpha());ck(r['method']==header[ord(col)-ord('A')],'literal method header at cell')
  else:
   v=pointer(obj(sid),position)
   if lane.endswith('-api'):
    cid=position.split('/')[3];info,meta=metadata[yr];desc=meta[cid];choice=desc['choices'][v['choiceID']];party=info['parties'].get(v['partyID'],{})
    ck(int(r['votes'])==v['totalVotes']and r['candidate_id']==v['choiceID']and r['party_id']==v['partyID']and r['candidate']==choice['name']and r['party_literal']==(party.get('partyName')or'')and r['contest']==desc['contestName']and r['method']=='All','every raw API candidate/ID/party/method value')
    if r['county_id']:
     loc=info['locations'][r['county_id']];ck(r['county']==loc['locationName'],'original API parent literal')
     if r['native_id']:ck(r['native_name']==loc['locations'][r['native_id']]['locationName'],'original API child literal')
   else:
    root=obj(sid);parts=position.split('/');contest=root['ContestData'][int(parts[2])]
    ck(int(r['votes'])==v['TotalVotes']and r['candidate']==v['Name']and r['party_literal']==(v.get('PartyName')or'')and r['contest']==contest['ContestName']and r['method']=='All','every raw FullData candidate/party/method value')
    if 'Counties'in parts:
     wrapper=contest['Counties'][int(parts[parts.index('Counties')+1])];ck(r['county']==wrapper['CountyName'],'every original repeated wrapper literal')
     if 'Precincts'in parts:
      precinct=wrapper['Precincts'][int(parts[parts.index('Precincts')+1])];ck(r['native_name']==precinct['PrecinctName'],'original FullData leaf literal')
  ck(r['source_id']in raw,'every source exists in fixed original inventory')
ck(records==300887,'all positional selected source records, not a sample')
# All full source-node fields retained except separately represented child arrays.
controls=read(B/'source/contest-controls.json.gz')
for r in controls:
 original=pointer(obj(r['source_id']),r['position']);projected={k:v for k,v in original.items()if k not in ['locations','Counties','Precincts']}
 same(r['raw'],projected,'every whole original control node field/null/ID/status')
 field='choices'if r['lane'].endswith('-api')else'Candidates';countfield='totalVotes'if field=='choices'else'TotalVotes';vals=original[field]
 ck(sum(v[countfield]for v in vals)==r['total']==r['sum_choices'],'whole original native/parent/state candidate balance')
for r in read(B/'source/native-inventory.json'):
 original=pointer(obj(f'{r["year"]}-info'),r['info_position']);same(r['raw'],original,'every complete original native descriptor')
for r in read(B/'source/candidate-metadata.json'):
 info,meta=metadata[int(r['year'])];same(r['metadata'],meta[r['contest_id']],'complete selected candidate metadata');same(r['parties'],info['parties'],'all literal party definitions');same(r['vote_types'],info['voteTypes'],'all vote type definitions')
for r in read(B/'source/turnout-controls.json'):
 original=obj(r['source_id']);same(r['response'],original['response'],'all225 whole county turnout responses');same(r['publication'],{k:v for k,v in original.items()if k!='response'},'all225 complete publication/clocks/status/nulls');ck(original['response']['locations']=={},'native turnout unknown not0')
# Native baselines must come from exact original per-choice observations.
units=read(B/'native-baselines.json.gz');ck(len(units)==23749 and len({(r['lane'],r['contest'],r['key'])for r in units})==len(units),'all source-native contest identities')
for u in units:
 counts={};method_counts={}
 for p in u['source_positions']:
  sid=p['source_id'];pos=p['position']
  if u['lane']=='2024-xlsx':
   addr=pos.rsplit('/',1)[1];rr=int(''.join(c for c in addr if c.isdigit()));v=selected[rr];name=v[3]['value'];counts[name]=int(worksheet[addr]['value'])
   for i,m in enumerate(header[5:9],5):method_counts.setdefault(m,{})[name]=int(v[i]['value'])
  else:
   v=pointer(obj(sid),pos)
   if u['lane'].endswith('-api'):
    cid=pos.split('/')[3];name=metadata[int(u['year'])][1][cid]['choices'][v['choiceID']]['name'];counts[name]=v['totalVotes']
   else:counts[v['Name']]=v['TotalVotes']
 same(u['candidates'],counts,'complete native candidate vector from independent original positions');ck(sum(counts.values())==u['votes'],'native reported total')
 if u['lane']=='2024-xlsx':same(u['methods'],method_counts,'complete native candidate/method vector')
for row in csv.DictReader((S/'data/county-baselines.csv').open(newline='')):
 ck(sum(json.loads(row['candidates_json']).values())==int(row['all_candidate_votes']),'all675 county full-candidate balances')
ck(len(controls)==31970,'complete selected node coverage')
# Independent complete orders from producer-own counts already original-checked above.
orders=read(B/'independent-complete-orders.json');ck(len(orders)==20,'all shared full orders')
for scope,rows in orders.items():
 sortedrows=sorted(rows,key=lambda r:(-r['votes'],r['key']));ck([r['key']for r in sortedrows]==[r['key']for r in rows],'full descending source order');den=sum(r['votes']for r in rows);cum=0
 for i,r in enumerate(rows,1):cum+=r['votes'];ck(r['rank']==i and r['cumulative_votes']==cum and r['share_denominator']==den,'every complete source-order cumulative record')
peer=read(B/'peer-reconciliation.json');ck(peer['checks']==peer['passing']==162714 and peer['errors']==[],'final expanded actual frozen-peer raw coverage proof')
# No source flags are replaced by inferred eligible/current/geographic assumptions.
out={'status':'pass_independent_complete_original_baseline_source_review','checks':N,'actual_fixed_original_receipts':len(originals),'selected_OOXML_rows':len(selected),'raw_positional_candidate_method_records':records,'records_by_lane':bylane,'complete_source_nodes':len(controls),'native_source_contest_rows':len(units),'whole_native_descriptors':len(read(B/'source/native-inventory.json')),'county_source_contest_rows':675,'all225_complete_turnout_publication_responses':True,'full_shared_orders':20,'final_peer_proof_checks':162714,'producer_import_or_write':False,'no_current_geographic_legal_or_eligible_writein_approval':True}
body=(json.dumps(out,indent=2)+'\n').encode();p=S/'data/coordinator-baseline-original-review.json'
if '--check'in sys.argv:ck(p.read_bytes()==body,'frozen review exact replay')
else:p.write_bytes(body)
print(json.dumps(out))
