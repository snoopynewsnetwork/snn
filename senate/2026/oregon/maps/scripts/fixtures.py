"""Meaningful corruption/scope fixtures against actual generated DOM and replay routines; memory only."""
from common import *
from audit import objects_dom,full_inventory,DOM,membership,all_owned
from build import outputs,pre
from resolve import resolve
from binary_audit import audit_zip
from acquire import body_of
from native import diff
import geography,copy,zipfile,struct,zlib,shapefile
from unittest.mock import patch

def run():
 inv=load('maps/inventory.json.gz');c=json.loads(exact(inv['frozen_contract']));pages=outputs(inv);results=[]
 def rejects(name,fn):
  try:fn()
  except (AssertionError,ValueError,KeyError,StopIteration,zipfile.BadZipFile,zlib.error,shapefile.ShapefileException) as e:results.append({'name':name,'status':'rejected','type':type(e).__name__});return
  raise AssertionError('corruption accepted: '+name)
 # Entire objects and nulls, not a scalar vote-only projection.
 mutant=copy.deepcopy(inv);mutant['canonical_priority']=[];rejects('null canonical priority replaced by empty dispatch',lambda:full_inventory(mutant,c))
 mutant=copy.deepcopy(inv);mutant['known_source_contexts']+=mutant['unavailable_native_parent_cases'];rejects('synthetic541 native inventory',lambda:full_inventory(mutant,c))
 mutant=copy.deepcopy(inv);mutant['parents']=mutant['parents'][:11];rejects('eleven-county sensitivity substituted for all36',lambda:full_inventory(mutant,c))
 mutant=copy.deepcopy(inv);mutant['known_source_contexts']=mutant['known_source_contexts'][:213];rejects('known-only213 substituted for full510',lambda:full_inventory(mutant,c))
 # Actual generated parent/context markup; remove one nonvote field, preserving scalar totals.
 parent=c['all_36_county_parents'][2];obj=parent['source_native_constituents'][0];path='maps/parents/clackamas.html';originalpre=pre(obj,'context',obj['key']);changed=copy.deepcopy(obj);changed['source_presentations']=[];mutant=pages.copy();mutant[path]=mutant[path].replace(originalpre.encode(),pre(changed,'context',obj['key']).encode(),1);rejects('full source methods/admin presentations omitted from DOM',lambda:objects_dom(mutant,c))
 mutant=pages.copy();mutant[path]=mutant[path].replace(originalpre.encode(),b'',1);rejects('missing complete context DOM node',lambda:objects_dom(mutant,c))
 mutant=pages.copy();mutant['maps/known.html']=mutant['maps/known.html'].replace(inv['known_source_contexts'][0]['key'].encode(),inv['known_source_contexts'][1]['key'].encode(),1);rejects('known source order/uniqueness changed in actual DOM',lambda:objects_dom(mutant,c))
 tricky={'source_label':'</pre><script>alert("x")</script><img src=x onerror=bad>& \\ \u2028','candidate_vector':[1,None,0],'headers':['<x>','&']};d=DOM(pre(tricky,'fixture','quote"<&').encode());assert not d.scripts and json.loads(d.pres[0][1])==tricky and len(d.links)==0;results.append({'name':'source escaping roundtrip and no executable markup','status':'pass'})
 # Exact historical path+hash resolves captured older body, not current replaced file.
 a=load(AUTH);historical=a['immutable_historical_snapshot_body_resolvers'][0]['complete_records'][0];b=resolve(historical['original_path'],historical['original_sha256']);assert sha(b)==historical['original_sha256'];assert b!=(S/historical['original_path']).read_bytes();results.append({'name':'actual older whole historical report restored instead of later current body','status':'pass'})
 rejects('unrecognized old expected hash cannot fall back to current file',lambda:resolve(historical['original_path'],'0'*64))
 pin=copy.deepcopy(inv['frozen_contract']);pin['sha256']='0'*64;rejects('whole original input byte corruption',lambda:exact(pin))
 # Exact native snapshot page and full pre/post service metadata mutations.
 snap=load('maps/native/clackamas-precinct.json');first=snap['pages'][0]['request'];entity=geography.entity
 def native_mutation(name,change,route=first):
  def overridden(path):
   x=copy.deepcopy(entity(path))
   if path==route:change(x)
   return x
  with patch.object(geography,'entity',overridden):rejects(name,lambda:geography.native_replay(snap))
 native_mutation('native page missing one requested ID',lambda x:x['features'].pop())
 native_mutation('native duplicate returned ID',lambda x:x['features'].append(copy.deepcopy(x['features'][0])))
 field=next(k for k in entity(first)['features'][0]['attributes'] if k!=snap['object_id_field'])
 native_mutation('native non-OID attribute omitted',lambda x:x['features'][0]['attributes'].pop(field))
 service=snap['post_service'];svc=entity(service);extent='fullExtent' if 'fullExtent'in svc else 'initialExtent';coord=next(k for k in svc[extent] if isinstance(svc[extent][k],(int,float)))
 native_mutation('service-extent-only pre/post change not hidden',lambda x:x[extent].__setitem__(coord,x[extent][coord]+1),service)
 sample={'fullExtent':{'xmin':1,'xmax':2},'layers':[{'id':7}]};other=copy.deepcopy(sample);other['fullExtent']['xmin']=0;assert diff(sample,other)==['/fullExtent/xmin'];results.append({'name':'full service extent-only comparison positive control','status':'pass'})
 load_original=geography.load
 def transformed(path):
  x=copy.deepcopy(load_original(path))
  if path==first:x['requested_url']+='&outSR=4326'
  return x
 with patch.object(geography,'load',transformed):rejects('forbidden outSR even with unchanged feature bodies',lambda:geography.native_replay(snap))
 points=[[0,0],[1,0],[0,1]];obj=shapefile.Shape(shapeType=5,points=points,parts=[0]);assert list(obj.points)==points and len(obj.points)==3;closed=shapefile.Shape(shapeType=5,lines=[points]);assert len(closed.points)==4;results.append({'name':'installedPyShp3.1.6 points/parts preserves raw open positions; lines auto-closes','status':'pass'})
 fs=[{'attributes':{'OID':1},'geometry':{'curveRings':[[[0,0],{'c':[[1,1],[0,1]]}]]}},{'attributes':{'OID':2},'geometry':None},{'attributes':{'OID':3},'geometry':{'rings':[points]}}];before=packed(fs);p=geography.preview('fixture',fs,'OID',write=False);assert p['counts']['curved_excluded_whole_feature']==1 and p['counts']['null_or_empty_excluded']==1 and p['full_ring_diagnostics'][2]['rings'][0]['simple_closed_ring'] is None and packed(fs)==before;results.append({'name':'curves/null/open/short preserved, excluded from unavailable topology without repair','status':'pass'})
 # Independently audited actual SHP ZIP, corrupt SHX offsets but recompute ZIP CRCs.
 raw=body_of(load('maps/requests/mapchain-032-net.json'))
 with zipfile.ZipFile(io.BytesIO(raw)) as z:members={n:z.read(n) for n in z.namelist()}
 shx=next(n for n in members if n.endswith('.shx'));bad=bytearray(members[shx]);offset=struct.unpack_from('>i',bad,100)[0];struct.pack_into('>i',bad,100,offset+1);members[shx]=bytes(bad);dest=io.BytesIO()
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for n,payload in members.items():z.writestr(n,payload)
 rejects('actual SHX record offset corruption despite valid ZIP CRCs',lambda:audit_zip('fixture',dest.getvalue()))
 bad=bytearray(raw)
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  info=z.infolist()[0];o=info.header_offset;namelen,extralen=struct.unpack_from('<HH',raw,o+26);bad[o+30+namelen+extralen+max(0,info.compress_size//2)]^=1
 rejects('actual ZIP member corruption CRC/deflate failure',lambda:audit_zip('fixture',bytes(bad)))
 actual=all_owned();entries=[ref(p) for p in actual if p!='maps/history/research-history.json'];rejects('manifest omits real history file',lambda:membership(entries,actual))
 save('maps/qa/fixtures.json',{'status':'pass','fixtures':results,'mutation_scope':'in memory only; shared originals and producer flags untouched','negative_fixture_count':sum(r['status']=='rejected' for r in results),'positive_controls':sum(r['status']=='pass' for r in results)})
 return results
if __name__=='__main__':print(json.dumps(run()))
