"""Full read-only source/history/order/negative/offline audit; --audit never writes owned files."""
from pathlib import Path
import sys,json,gzip,hashlib,subprocess,copy,struct,re,io,contextlib
from urllib.parse import urlparse,parse_qs
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];S=ROOT.parent
sys.path.insert(0,'/private/tmp/al-turnout-deps')
import replay_authority,replay_xls,additional_negative,negative_fixtures,build
from html_tools import entity
from audit_shp import audit_zip
import fitz

def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.name.endswith('.gz') else b)
def owned():return {str(p.relative_to(S)):p for p in ROOT.rglob('*') if p.is_file()}|{'precinct-maps.md':S/'precinct-maps.md'}
def membership():
 mf=ROOT/'asset-manifest.json';m=load(mf);files=owned();files.pop('maps/asset-manifest.json');rows=m['assets'];assert len(rows)==len({r['path'] for r in rows}) and {r['path'] for r in rows}==set(files)
 for r in rows:
  b=files[r['path']].read_bytes();assert len(b)==r['bytes']<40000000 and sha(b)==r['sha256'],r['path']
 seal=load(ROOT/'final-seal.json');assert seal['validation_sha256']==sha((ROOT/'validation.json').read_bytes()) and 'manifest_sha256' not in seal
 return len(rows)
def negatives():
 c=replay_authority.loads((S/build.CONTRACT['path']).read_bytes());ref=c;counts=Counter()
 for p in sorted((ROOT/'negative-fixtures').glob('*.input.json*')):
  inp=load(p);name=p.name.split('.input.')[0];result=load(ROOT/'negative-fixtures'/(name+'.result.json'));assert result['status']=='REJECTED'
  rejected=False
  try:
   if 'base_complete_input' in inp:
    assert inp['base_complete_input']==build.CONTRACT
    if inp['operation']=='truncate_final_bytes':replay_authority.loads((S/build.CONTRACT['path']).read_bytes()[:-inp['bytes']])
    else:
     x=copy.deepcopy(c);negative_fixtures.patch(x,inp['path'],inp['value'],inp['operation']);negative_fixtures.check_contract(x,ref)
   elif 'base_complete_receipt' in inp:
    _,b=entity(inp['base_complete_receipt']);v=json.loads(b);x=copy.deepcopy(v);negative_fixtures.patch(x,inp['path'],inp['value'],inp['operation']);negative_fixtures.check_layer(x,v)
   elif 'page_receipt' in inp:
    a=inp['requested_ids'];b=inp['returned_ids'];n=inp['count'];negative_fixtures.reject('exact disjoint requested/returned IDs and count',len(b)==len(set(b))==len(a)==n and set(a)==set(b))
   elif 'raw_utf8' in inp:replay_authority.loads(inp['raw_utf8'])
   else:raise AssertionError('unknown fixture')
  except ValueError:rejected=True
  assert rejected,name;counts['rejected']+=1
 assert counts['rejected']==30
 assert additional_negative.run(False)==load(ROOT/'additional-negative-validation.json')
 return counts['rejected']+2

def run(audit=False):
 stats=Counter();files=owned()
 assert not any(any(part in ['__pycache__','node_modules','.cache','.venv','venv'] for part in p.parts) for p in files.values())
 for name,p in files.items():assert p.stat().st_size<40000000,name
 # Full independent source graph and every complete original workbook position.
 graph=replay_authority.run();assert graph==load(ROOT/'authority-validation.json')
 xls,refs=replay_xls.run();assert xls==load(ROOT/'xls-source-validation.json') and refs==load(ROOT/'original-references.json')
 # Every current acquisition original, including every redirect/error entity.
 originals={};pdfs={};receipts=[]
 for p in sorted((ROOT/'source').glob('*.receipt.json')):
  r=json.loads(p.read_bytes());receipts.append(str(p.relative_to(ROOT)));assert r['utc_start']<=r['utc_end'] and r['method']=='GET' and r['fields'] is None and r['request_body'] is None
  for hop in r['hops']:
   assert r['utc_start']<=hop['utc_start']<=hop['utc_end']<=r['utc_end'] and isinstance(hop['status'],int) and isinstance(hop['headers'],list)
   e=hop['entity'];parts=[]
   for part in e['parts']:
    b=(ROOT/part['path']).read_bytes();assert len(b)==part['bytes']<40000000 and sha(b)==part['sha256'];parts.append(b)
   b=gzip.decompress(b''.join(parts));assert len(b)==e['bytes'] and sha(b)==e['sha256'];stats['complete_hop_bodies']+=1
  if r['entity'] is None:assert r['status'] is None and 'error' in r
  else:
   rr,b=entity(str(p.relative_to(ROOT)));originals[r['entity']['sha256']]=b
   if r['status']==200 and b.startswith(b'%PDF'):pdfs[r['entity']['sha256']]=b
  stats['acquisition_receipts']+=1
 assert len(receipts)==975
 for r in load(ROOT/'original-catalogue.json'):assert r['receipt'] in receipts
 # Whole ZIP byte audit re-executed without any writer or adapter mutation.
 ziprecords=load(ROOT/'zip-audit-index.json');seen=set()
 for r in ziprecords:
  h=r['original_sha256']
  if h in seen:continue
  seen.add(h);computed=audit_zip(originals[h]);assert computed==load(ROOT/r['audit']);stats['complete_zip_audits']+=1
  for k,v in computed['checks'].items():stats[k]+=v
 assert len(seen)==46
 # All original PDF physical pages, full text/warnings, every whole-page PNG.
 index=load(ROOT/'pdf-index.json');seen=set()
 for r in index:
  h=r['original_sha256'];assert h in pdfs
  if h in seen:continue
  seen.add(h);m=load(ROOT/r['pages_metadata']);d=fitz.open(stream=pdfs[h],filetype='pdf');assert len(d)==len(m['pages']);text=gzip.decompress((ROOT/m['text_path']).read_bytes());assert m['pdftotext_exit']==0 and text.count(b'\x0c')==len(d)
  folder=(ROOT/r['pages_metadata']).parent;assert (folder/'pdftotext.warnings.txt').exists() and (folder/'render.warnings.txt').exists()
  for i,p in enumerate(m['pages']):
   b=(ROOT/p['render_path']).read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n' and list(struct.unpack('>II',b[16:24]))==[p['pixel_width'],p['pixel_height']] and p['page_1based']==i+1
   assert [d[i].rect.width,d[i].rect.height]==[p['width_points'],p['height_points']];stats['allpage_renders']+=1
  d.close();stats['complete_pdfs']+=1
 assert set(pdfs)==seen and len(seen)==242 and stats['allpage_renders']==2087
 manual=load(ROOT/'manual-visual-observations.json');assert len(manual)==3 and all(r['manual_whole_page_observed'] and (ROOT/r['selected_detail']).exists() and (ROOT/r['full_page_render']).exists() for r in manual)
 # Full native query scope and exact observed source attributes/IDs/CRS/vintage.
 for layer in load(ROOT/'native-service-captures.json'):
  lp=json.loads(entity(layer['pre']['layer'])[1]);lq=json.loads(entity(layer['post']['layer'])[1]);sp=json.loads(entity(layer['pre']['service'])[1]);sq=json.loads(entity(layer['post']['service'])[1]);ids=layer['pre']['ordered_ids'];allids=[]
  assert lp==lq and sp==sq and ids==layer['post']['ordered_ids']
  assert json.loads(entity(layer['pre']['count'])[1])['count']==json.loads(entity(layer['post']['count'])[1])['count']==len(ids)
  assert json.loads(entity(layer['pre']['all_ids'])[1])['objectIds']==json.loads(entity(layer['post']['all_ids'])[1])['objectIds']==ids
  for page in layer['pages']:
   rr,b=entity(page['receipt']);q=parse_qs(urlparse(rr['requested_url']).query);assert set(q)=={'f','objectIds','outFields','returnGeometry','returnZ','returnM','returnTrueCurves'}
   assert q['outFields']==['*'] and all(q[k]==['true'] for k in ['returnGeometry','returnZ','returnM','returnTrueCurves'])
   data=json.loads(b);received=[f['attributes'][layer['pre']['object_id_field']] for f in data['features']]
   assert len(page['requested_ids'])<=50 and received==page['returned_ids'] and set(received)==set(page['requested_ids']) and not(set(allids)&set(received)) and len(received)==page['count'];allids+=received
   assert data.get('spatialReference')==page['spatial_reference']==lp['extent']['spatialReference']
   for f in data['features']:assert set(f['attributes'])=={f['name'] for f in lp['fields']};stats['native_service_features']+=1
  assert set(allids)==set(ids) and len(allids)==layer['count'] and layer['current_geography_approved'] is False and layer['result_label_join'] is None
 # Complete old owned bodies and failure histories remain reconstructable.
 for p in (ROOT/'history').glob('*.origin.json'):
  r=load(p);b=gzip.decompress((p.parent/r['stored']).read_bytes());assert len(b)==r['bytes'] and sha(b)==r['sha256'];stats['old_whole_owned_bodies']+=1
 for p in (ROOT/'history').glob('*.gz'):gzip.decompress(p.read_bytes());stats['complete_history_streams']+=1
 for p in [S/'precinct-maps.md',ROOT/'SCHEMA.md']:
  for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if not link.startswith(('https://','http://','#')):assert (p.parent/link.split('#')[0]).exists(),(p,link)
 assert all(v is not True for k,v in load(ROOT/'admission.json').items() if k!='historical_source_only')
 stats['actual_negative_fixtures_rejected']=negatives()
 # Actual embedded JavaScript and exact deterministic outputs, stdout-only subprocesses.
 env=dict(__import__('os').environ,PYTHONDONTWRITEBYTECODE='1')
 for script,proof in [('test_dom.py','dom-validation.json'),('offline_rebuild.py','offline-validation.json')]:
  p=subprocess.run([sys.executable,str(ROOT/'scripts'/script)],capture_output=True,env=env);assert p.returncode==0,(script,p.stderr.decode());assert json.loads(p.stdout)==load(ROOT/proof),script;stats['exact_readonly_QA_replays']+=1
 if audit:stats['manifest_targets']=membership()
 return {'status':'PASS','mode':'final_readonly_sealed_audit' if audit else 'preseal_full_validation','checks':dict(stats),'source_graph_checks':graph['checks'],'original_xls_checks':xls['checks'],'full':2085,'priority':887,'remainder':1198,'all_parents':67,'priority_parents':63,'current_legal_live_approval':False,'authority_path':'data/coordinator-priority-acceptance.json','manifest_reverse_digest':None,'owned_writes_during_audit':False}
if __name__=='__main__':
 audit='--audit' in sys.argv;result=run(audit)
 if not audit:(ROOT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
