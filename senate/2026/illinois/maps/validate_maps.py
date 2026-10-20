"""Offline whole-package, negative and deterministic QA. --seal writes owned manifest only."""
from common import *
from acquire import body
from audit_gis import audit_zip,require,bits,bitseq
import argparse,copy,struct,io,zipfile,subprocess,sys
from collections import defaultdict

def indices(rows,p):
 require(len(rows)==10062,'complete inventory')
 require([r['key'] for r in rows]==p['full_order'],'exact full/priority/remainder order')
 units={u['key']:u for u in p['native_constituents']}
 for rank,r in enumerate(rows,1):
  require(r['rank_full']==rank and r['priority']==(rank<=5540),'rank/membership')
  require(r['source_observation']==units[r['key']],'complete recursive source observation including nulls/schema/category/positions')
  require(r['matched_geometry'] is None and r['physical_polygon'] is None and r['source_method'] is None,'no polygon/method inference')
  require(r['authority_key']==p['native_to_authority_parent_map'][r['key']],'reporting parent preserved')
  require(bool(r['gaps']),'specific gaps')
 require(sum(r['source_observation']['printed_known_recorded_sum'] for r in rows)==5592368,'denominator')
 require(sum(r['source_observation']['printed_known_recorded_sum'] for r in rows[:5539])==4473789,'preceding threshold')
 require(sum(r['source_observation']['printed_known_recorded_sum'] for r in rows[:5540])==4474312,'crossing threshold')
 require(rows[5539]['source_observation']['authority_id']=='88' and rows[5539]['source_observation']['precinct_name_literal']=='O FALLON 3','exact crossing')
 require(sum(r['source_observation']['printed_known_recorded_sum'] for r in rows[5540:])==1118056,'remainder')
 require(sum(r['source_observation']['administrative_only'] for r in rows)==4,'four unavailable pools')
 require(sum(bool(r['source_observation']['missing_printed_candidate_rows']) and not r['source_observation']['administrative_only'] for r in rows)==15,'15 absent Kennedy cells')

def exact_slices():
 r=load(M/'source/census-illinois-vtd2020.receipt.json');z=zipfile.ZipFile(io.BytesIO(body(r)))
 shp=z.read(next(n for n in z.namelist() if n.endswith('.shp')));dbf=z.read(next(n for n in z.namelist() if n.endswith('.dbf')))
 n,hlen,rlen=struct.unpack('<IHH',dbf[4:12]);seen=[];points=0
 for path in sorted((M/'derived/counties').glob('*.json.gz')):
  d=load(path);require(d['native_coordinate_unit']=='degree','native units')
  for x in d['records']:
   i=x['source_record_1based'];seen.append(i);off=x['source_shp_byte_offset'];length=x['source_content_bytes'];content=shp[off+8:off+8+length]
   require(sha(content)==x['source_content_sha256'],'full native record reference')
   require(bytes.fromhex(x['dbf_row_hex'])==dbf[hlen+(i-1)*rlen:hlen+i*rlen],'literal DBF row')
   require(x['attributes']['STATEFP20']+x['attributes']['COUNTYFP20']==d['source_county_fips'],'geographic county slice')
   if x['shapeType']==5:
    np,npt=struct.unpack('<ii',content[36:44]);require(struct.pack('<'+'i'*np,*x['parts'])==content[44:44+np*4],'persisted parts')
    require(bitseq(v for pt in x['points'] for v in pt)==content[44+np*4:],'persisted every XY bit')
    require(bitseq(x['bbox'])==content[4:36],'persisted bbox bits');points+=npt
   require(x['z'] is None and x['m'] is None and x['truecurves'] is None,'2D SHP has no fabricated Z/M/curve')
 require(sorted(seen)==list(range(1,n+1)),'all statewide records exactly once across102 slices')
 return points

def checks():
 a=load(S/ACCEPTANCE);p=json.loads(exact(a['frozen_contract']));rows=load(M/'derived/full-inventory.json.gz');indices(rows,p)
 require(load(M/'derived/priority-index.json.gz')==rows[:5540],'priority full objects')
 require(load(M/'derived/remainder-index.json.gz')==rows[5540:],'remainder full objects')
 parents=load(M/'derived/parents.json.gz');require(len(parents)==108,'108 parents')
 for x,expected in zip(parents,p['authority_inventory']):
  require(x['source_parent']==expected,'complete source authority')
  id=expected['authority_id'];allkeys=[r['key'] for r in rows if r['source_observation']['authority_id']==id]
  require(x['all_children_source_order']==expected['native_constituent_keys'],'original complete child arrays')
  require(x['all_children_rank_order']==allkeys,'ordered complete child arrays')
  require(x['ordered_priority_children']==[k for k in allkeys if k in set(p['ordered_priority_keys'])],'priority child arrays')
  require(x['ordered_remainder_children']==[k for k in allkeys if k not in set(p['ordered_priority_keys'])],'remainder child arrays')
 investigations=load(M/'derived/authority-investigations.json');require(len(investigations)==108 and sum(x['priority'] for x in investigations)==97,'complete actual chain inventory')
 for x in investigations:
  ar=load(S/x['archive_receipt']);require(ar['status'] is not None and bool(body(ar)),'actual archive content')
  require(x.get('leaf_access_receipts') or not x['archive_files'],'actual leaf request or observed empty archive')
 source_count=0
 for path in sorted((M/'source').glob('*.receipt.json')):
  r=load(path);source_count+=1
  for pin in r.get('stored_parts',[]):exact(pin)
  if r.get('stored_parts'):body(r)
  require(r['method'] in ('GET','HEAD') and r['request_body'] is None,'public read-only request')
  if r.get('parent'):require((M/'source'/f"{r['parent']}.receipt.json").exists(),'actual observed parent')
 require(p['coordinator_acceptance'] is False and p['current_geometry_approved'] is False,'producer false flags unchanged')
 pts=exact_slices();audit=audit_zip(body(load(M/'source/census-illinois-vtd2020.receipt.json')),write=False)
 require(audit==load(M/'qa/census-binary-audit.json'),'replayed complete binary audit')
 return dict(status='pass',source_receipts=source_count,source_observations=10062,priority_observations=5540,remainder_observations=4522,source_parents=108,priority_source_parents=97,complete_county_slices=102,all_persisted_XY_points_verified=pts,geometry_matches=0,external_authority_path=ACCEPTANCE)

def negatives():
 a=load(S/ACCEPTANCE);p=json.loads(exact(a['frozen_contract']));rows=load(M/'derived/full-inventory.json.gz');results=[]
 def reject(name,operation,fn):
  try:fn()
  except (AssertionError,ValueError,KeyError,zipfile.BadZipFile,struct.error) as e:results.append(dict(fixture=name,operation=operation,result='rejected',error=str(e)[:300]));return
  raise AssertionError('negative accepted: '+name)
 for name,operation in [('swapped-priority-order','swap ranks1and2'),('invented-polygon','set physical_polygon'),('dropped-source-field','remove method_status'),('absent-candidate-zero','replace absent Kennedy null with0'),('county-parent-replacement','replace city reporting parent with county'),('lost-remainder','delete final row')]:
  changed=copy.deepcopy(rows)
  if name=='swapped-priority-order':changed[0],changed[1]=changed[1],changed[0]
  elif name=='invented-polygon':changed[0]['physical_polygon']='invented'
  elif name=='dropped-source-field':del changed[0]['source_observation']['method_status']
  elif name=='absent-candidate-zero':
   target=next(r for r in changed if r['source_observation']['missing_printed_candidate_rows'] and not r['source_observation']['administrative_only']);target['source_observation']['printed_candidate_votes']['Robert F. Kennedy Jr.']=0
  elif name=='county-parent-replacement':next(r for r in changed if r['source_observation']['authority_id']=='105')['authority_key']='il:authority:16'
  else:changed.pop()
  reject(name,operation,lambda:indices(changed,p))
 raw=body(load(M/'source/census-illinois-vtd2020.receipt.json'));z=zipfile.ZipFile(io.BytesIO(raw));source={n:z.read(n) for n in z.namelist()}
 for name,ext,offset,change in [('bad-shx-index','.shx',103,1),('bad-dbf-field-width','.dbf',48,1),('bad-shp-feature-bbox','.shp',112,1),('bad-shp-part-index','.shp',152,1)]:
  blobs=dict(source);key=next(n for n in blobs if n.endswith(ext));b=bytearray(blobs[key]);b[offset]^=change;blobs[key]=bytes(b);out=io.BytesIO()
  with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as w:
   for n,b in blobs.items():w.writestr(n,b)
  reject(name,dict(member=key,byte_offset=offset,xor=change),lambda:audit_zip(out.getvalue(),write=False))
 dump('qa/negative-fixtures.json',dict(status='pass',source='mutations of actual accepted rows and actual acquired Census binary; no synthetic success fixture',cases=results))
 return len(results)

def deterministic():
 def snap():return {str(p.relative_to(M)):sha(p.read_bytes()) for p in M.rglob('*') if p.is_file() and (p.is_relative_to(M/'derived') or p.name=='atlas.html' or p.name=='build-summary.json' or p.suffix=='.png')}
 before=snap();subprocess.run([sys.executable,str(M/'audit_gis.py')],check=True);subprocess.run([sys.executable,str(M/'build_atlas.py')],check=True);subprocess.run(['node',str(M/'test_atlas.cjs')],check=True);after=snap();require(before==after,'deterministic replay exact bytes and membership')
 dump('qa/deterministic-replay.json',dict(status='pass',exact_rebuilt_assets=len(after),network_used=False,producer_writes=False))

def owned():return sorted([S/'precinct-maps.md']+[p for p in M.rglob('*') if p.is_file() and p!=M/'asset-manifest.json'])
def seal():
 paths=owned();assets=[]
 for p in paths:
  b=p.read_bytes();require(len(b)<40000000,'strict stored file bound');assets.append(dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b)))
 dump('asset-manifest.json',dict(schema='illinois-maps-owned-membership-v1',external_authority_path=ACCEPTANCE,excluded=['maps/asset-manifest.json itself only'],assets=assets))
def verify_seal():
 m=load(M/'asset-manifest.json');require([str(p.relative_to(S)) for p in owned()]==[x['path'] for x in m['assets']],'exact owned membership excluding ONLY manifest')
 for x in m['assets']:exact(x)
 return len(m['assets'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seal',action='store_true');ap.add_argument('--full',action='store_true');args=ap.parse_args()
 out=checks()
 if args.full:out['negative_cases']=negatives();deterministic()
 if args.seal:dump('qa/validation.json',out);seal()
 out['sealed_owned_assets']=verify_seal();print(json.dumps(out))
if __name__=='__main__':main()
