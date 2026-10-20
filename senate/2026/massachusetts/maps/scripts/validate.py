"""Offline whole-owned evidence, exact service batching, and semantic QA."""
from acquire import *
import json,collections,subprocess,copy,io,re,zipfile

def partition(r):
 # Streaming ordered split concatenation; no temporary whole oversized archive.
 class Reader:
  def __init__(self):self.i=0;self.f=None
  def read(self,n=-1):
   out=[];remaining=n
   while remaining:
    if self.f is None:
     if self.i==len(r['parts']):break
     self.f=(M/r['parts'][self.i]['path']).open('rb');self.i+=1
    b=self.f.read(remaining);out.append(b)
    if remaining>0:remaining-=len(b)
    if not b:self.f.close();self.f=None
   return b''.join(out)
 return Reader()

def verify_digest(r,size,digest):assert size==r['raw_bytes']and digest==r['raw_sha256']
def check_ids(want,got,count):assert len(want)==len(set(want))==count and len(got)==len(set(got))==count and set(want)==set(got)
def check_query(q):assert not any(k.lower()in ['outsr','outputcrs','geometryprecision','quantizationparameters','maxallowableoffset']for k in q);assert q['outFields']=='*'and q['returnZ']=='true'and q['returnM']=='true'and q['returnTrueCurves']=='true'
def inventory_check(o):
 units=o['units'];assert len(units)==2394 and len(o['parents'])==351 and len(o['priority'])==1470 and len(o['remainder'])==924
 keys=[u['full_source_object']['native_key']for u in units];assert keys==o['rank_order']==o['priority']+o['remainder']and len(set(keys))==2394
 for u in units:
  s=u['full_source_object']['source_record'];assert all(k in s and s[k]is None for k in ['numeric_native_id','method','administrative_identity']);assert u['geometry_match']is None and u['current_approved']is False
 assert sum(u['full_source_object']['votes']for u in units)==3407108;assert sum(u['full_source_object']['votes']for u in units[:1470])==2726450;assert units[1469]['full_source_object']['native_key']=='["Northampton","3","B"]'
 for p in o['parents']:
  rr=[u['full_source_object']for u in units if u['parent_literal']==p['parent_literal']];assert [x['native_key']for x in rr]==p['canonical_rank_ordered_children'];assert [x['native_key']for x in sorted(rr,key=lambda x:x['csv_record_ordinal'])]==p['original_source_ordered_children']
 assert sum(p['in_priority']for p in o['parents'])==287;assert all(p['municipal_chain']for p in o['parents']if p['in_priority'])

def negatives(inv):
 cases=[]
 def reject(name,fn):
  try:fn()
  except (AssertionError,KeyError,ValueError):cases.append(dict(name=name,status='rejected'));return
  raise AssertionError('negative accepted '+name)
 reject('corrupted equal-length complete raw-byte hash',lambda:verify_digest(dict(raw_bytes=8,raw_sha256=sha(b'original')),8,sha(b'tampered')))
 reject('ID omitted',lambda:check_ids([1,2],[1],2));reject('duplicate returned ID with matching count',lambda:check_ids([1,2],[1,1],2));reject('extra substituted ID',lambda:check_ids([1,2],[1,3],2))
 q={'outFields':'*','returnZ':'true','returnM':'true','returnTrueCurves':'true'}
 for k in ['outSR','geometryPrecision','quantizationParameters','maxAllowableOffset']:reject('forbidden '+k,lambda k=k:check_query(q|{k:1}))
 def mutate_drop():v=copy.deepcopy(inv);v['units'].pop();inventory_check(v)
 reject('dropped remainder source object',mutate_drop)
 def mutate_null():v=copy.deepcopy(inv);del v['units'][0]['full_source_object']['source_record']['method'];inventory_check(v)
 reject('missing source null',mutate_null)
 def mutate_geometry():v=copy.deepcopy(inv);v['units'][0]['geometry_match']=1;inventory_check(v)
 reject('invented numeric polygon match',mutate_geometry)
 def mutate_tuple():v=copy.deepcopy(inv);v['units'][0]['full_source_object']['native_key']='["Nantucket","0","1"]';inventory_check(v)
 reject('literal dash normalized into invented zero',mutate_tuple)
 from audit_native import diagnose
 f={'attributes':{'OBJECTID':999},'geometry':{'rings':[[[0.,0.],[0.,1.],[1.,1.],[1.,0.]]]}}
 x=diagnose([f]);assert x['features'][0]['diagnostic_status']=='invalid_or_unclosed_ring_no_repair';cases.append(dict(name='unclosed native ring remains unrepaired',status='preserved_unknown'))
 f['geometry']={'curveRings':[[[0.,0.],{'c':[[1.,1.],[.5,.5]]}]]};x=diagnose([f]);assert x['features'][0]['diagnostic_status']=='truecurves_preserved_not_linearized';cases.append(dict(name='truecurve not flattened',status='preserved_curve'))
 dump(M/'negative-fixtures.json',dict(status='pass',cases=cases))
 return cases

def main():
 owned=[p for p in M.rglob('*')if p.is_file()];assert all(p.stat().st_size<40000000 for p in owned);assert not any('__pycache__'in p.parts or p.suffix=='.pyc'for p in owned)
 observed={};http=collections.Counter();redirects=0
 for p in sorted((M/'receipts').glob('*.json')):
  r=json.loads(p.read_bytes());http[str(r.get('status'))]+=1
  for x in r.get('exchanges',[]):
   redirects+=x['status']in range(300,400)
   h=x['raw_sha256']
   if h in observed:continue
   for part in x['parts']:
    path=M/part['path'];assert path.stat().st_size==part['bytes']<40000000;d=hashlib.sha256()
    with path.open('rb')as f:
     for b in iter(lambda:f.read(1048576),b''):d.update(b)
    assert d.hexdigest()==part['sha256']
   z=gzip.GzipFile(fileobj=partition(x));d=hashlib.sha256();size=0
   for b in iter(lambda:z.read(1048576),b''):d.update(b);size+=len(b)
   verify_digest(x,size,d.hexdigest());observed[h]=size
 inv=json.loads((M/'inventory.json').read_bytes());inventory_check(inv);cases=negatives(inv)
 for prefix in ['wards','subprecinct']:
  a=json.loads((M/(prefix+'-layer0-acquisition.json')).read_bytes());seen=[];assert len(a['ids'])==a['count']
  for x in a['batches']:
   r=json.loads((M/x['receipt']).read_bytes());check_query(r['query']);assert len(x['requested_ids'])<=50
   o=json.loads(body(r));got=[f['attributes'][a['object_id_field']]for f in o['features']];check_ids(x['requested_ids'],got,x['requested_count']);assert got==x['returned_ids'];seen+=got
  check_ids(a['ids'],seen,a['count'])
  meta_pre=json.loads(load(M/('receipts/'+prefix+'-layer0-pre.json'))[0]);meta_post=json.loads(load(M/('receipts/'+prefix+'-layer0-post.json'))[0]);assert meta_pre==meta_post
  for suffix in ['pre','post']:
   assert json.loads(load(M/('receipts/'+prefix+'-layer0-count-'+suffix+'.json'))[0])['count']==a['count']
   ids=json.loads(load(M/('receipts/'+prefix+'-layer0-ids-'+suffix+'.json'))[0])['objectIds'];check_ids(a['ids'],ids,a['count'])
  assert a['pre_post_layer_metadata_equal']and a['pre_post_ids_equal']and a['pre_post_count_equal']
 pdf=json.loads((M/'pdf-index.json').read_bytes());assert all(x['page_count']==len(x['pages'])for x in pdf)
 for x in pdf:
  for page in x['pages']:
   if page.get('render'):assert (M/page['render']).is_file()
   else:assert page['automatically_rendered']is False and page['render_gap']
 node=subprocess.run(['node',str(M/'test_atlas.cjs')],check=True,capture_output=True,text=True);atlas=json.loads(node.stdout)
 out=dict(status='pass',inventory=[2394,1470,924,351,287],exact_shared_historical_reconstruction=json.loads((M/'reconstruction.json').read_bytes())['status'],unique_retained_HTTP_entities=len(observed),complete_raw_entity_bytes=sum(observed.values()),HTTP_status_counts=dict(http),redirect_exchanges=redirects,PDF_originals=len(pdf),PDF_pages=sum(x['page_count']for x in pdf),PDF_pages_automatically_rendered=sum(sum(bool(p.get('render'))for p in x['pages'])for x in pdf),negative_fixtures=len(cases),atlas=atlas,all_stored_artifacts_strictly_below_40000000=True,approvals=dict(current_geometry=False,current_numeric_ID=False,legal_native80=False,live_returns=False,collector=False,probability=False))
 dump(M/'validation.json',out);print(out)
if __name__=='__main__':main()
