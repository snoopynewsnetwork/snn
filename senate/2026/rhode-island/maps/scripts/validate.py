from acquire import *
from build import detail
from audit_native import load,geometry,differences
from html.parser import HTMLParser
from collections import Counter
import re,copy,math,urllib.parse
class DOM(HTMLParser):
 def __init__(self,b):
  super().__init__(convert_charrefs=True);self.frames=[];self.pre=False;self.text='';self.objects=[];self.tags=[];self.links=[];self.keys=[];self.parents=[];self.feed(b)
 def handle_starttag(self,t,a):
  a=dict(a);self.tags.append(t)
  if t=='details':self.frames.append(a)
  if t=='pre':self.pre=True;self.text=''
  if t=='li' and 'data-key' in a:self.keys.append(a['data-key'])
  if t=='li' and 'data-parent' in a:self.parents.append(a['data-parent'])
  if t in ['a','img']:
   u=a.get('href') if t=='a' else a.get('src')
   if u:self.links.append(u)
 def handle_data(self,s):
  if self.pre:self.text+=s
 def handle_endtag(self,t):
  if t=='pre':
   self.pre=False
   if self.frames:self.objects.append((self.frames[-1].get('class'),self.frames[-1].get('data-key'),json.loads(self.text)))
  if t=='details':self.frames.pop()
def invariants(c,o):
 full=c['complete_descending_order'];priority=c['ordered_priority_keys'];inv=c['all_source_native_constituents'];parents=c['municipal_and_administrative_parent_sensitivity']['full_inventory']
 assert len(full)==458 and len(inv)==497 and len(parents)==43
 assert len(priority)==242 and [x['key'] for x in full[:242]]==priority
 assert sum(x['votes'] for x in full)==491948 and sum(x['votes'] for x in full[:241])==393066 and sum(x['votes'] for x in full[:242])==394072
 assert len({x['key'] for x in full})==458 and full==sorted(full,key=lambda x:(-x['votes'],x['source_anchor']['byte_offset']))
 assert sum(x['votes']==0 for x in full)==15 and sum(x['contests']['Senator in Congress']['total'] is None for x in inv)==39
 assert o['ordered_full_keys']==[x['key'] for x in full] and o['ordered_priority_keys']==priority and o['ordered_remainder_keys']==[x['key'] for x in full[242:]]
 assert all(v is False for v in o['approvals'].values())
 assert len(o['all_497_inventory_observations'])==497 and len(o['ordered_full_observations'])==458
 for x,r in zip(o['ordered_full_observations'],full,strict=True):
  assert x['source_key']==r['key'] and x['source_anchor']==r['source_anchor'] and x['source_inventory_key']==r['native_key'] and x['parent_key']==r['parent_key']
  assert all(k in x['gaps'] for k in ['access','vintage','crs','finer','current','legal','physical','ballotstyle'])
 for r,p in zip(o['complete_parent_resource_records'],parents,strict=True):
  assert r['complete_parent']==p
  if p['geography_type']!='municipality':assert r['shared_native_resources']=={} and r['physical_geometry_available'] is False
  else:
   assert set(r['shared_native_resources'])=={'rigis','sos'}
   for v in r['shared_native_resources'].values():assert v['current_approval'] is False and v['legal_approval'] is False
  rows=[x for x in full if x['parent_key']==p['key']]
  assert r['child_arrays']==o['parent_child_arrays'][p['key']]==dict(original_ordered_native_inventory_keys=p['native_keys'],full_source_rank_ordered_children=[x['key'] for x in rows],ordered_priority_children=[x['key'] for x in rows if x['key'] in priority],ordered_remainder_children=[x['key'] for x in rows if x['key'] not in priority])

def negatives(c,o):
 names=[]
 cases=[('priority-order',lambda x:x['ordered_priority_keys'].reverse()),('remainder-omission',lambda x:x['ordered_remainder_keys'].pop()),('full-observation-omission',lambda x:x['ordered_full_observations'].pop()),('null-source-anchor',lambda x:x['ordered_full_observations'][0].update(source_anchor=None)),('source-key-substitution',lambda x:x['ordered_full_observations'][0].update(source_key='0707')),('current-approval',lambda x:x['approvals'].update(current_geography=True)),('parent-missing-child',lambda x:next(iter(x['parent_child_arrays'].values()))['original_ordered_native_inventory_keys'].pop()),('admin-polygon',lambda x:next(r for r in x['complete_parent_resource_records'] if not r['shared_native_resources'])['shared_native_resources'].update(rigis={'polygon':'fake'})),('legal-resource-approval',lambda x:x['complete_parent_resource_records'][0]['shared_native_resources']['rigis'].update(legal_approval=True)),('source-position-replacement',lambda x:x['ordered_full_observations'][0]['source_anchor'].update(byte_offset=0)),('missing-physical-gap',lambda x:x['ordered_full_observations'][0]['gaps'].pop('physical'))]
 for name,mutate in cases:
  v=copy.deepcopy(o);mutate(v)
  try:invariants(c,v)
  except (AssertionError,KeyError):names.append(name)
  else:raise AssertionError('accepted corruption '+name)
 fixture={'tag':'</pre><script>alert("x")</script> & < > " \'','nested':[None,{'party':'DEM ','method':[0]*14}],'raw':'row\r\n'}
 dom=DOM(detail('Untrusted </summary>',fixture,key='\" onmouseover=\"bad'))
 assert 'script' not in dom.tags and dom.objects[0][2]==fixture and dom.objects[0][1]=='\" onmouseover=\"bad';names.append('full-object-html-escaping')
 tests=[None,{'rings':[]},{'rings':[[]]},{'rings':[[[0,0],[1,0],[1,1]]]},{'rings':[[[0,0],[1,1],[0,0]]]},{'curveRings':[[[0,0],{'c':[[1,1],[2,2]]}]]},{'rings':[[[0,0],[1,0],[1,0],[1,1],[0,0]]]},{'rings':[[[-0.0,0.0],[1.0,0.0],[1.0,1.0],[-0.0,0.0]]]}]
 for i,g in enumerate(tests):
  before=canon(g);d,s=geometry(g);assert canon(g)==before
  if i in [0,1,2,5]:assert s is None
  if i==3:assert d['counts']['open_rings']==1 and len(g['rings'][0])==3 and s is None
  if i==4:assert d['counts']['short_rings']==1 and s is None
  if i==5:assert d['status']=='curved' and d['preview'] is False
  if i==6:assert d['positions']==5 and len(g['rings'][0])==5
  names.append('native-geometry-preservation-'+str(i))
 a={'extent':{'xmin':0},'fields':[{'x':None}]};b=copy.deepcopy(a);b['extent']['xmin']=1
 assert differences(a,b)==[{'pointer':'/extent/xmin','pre':0,'post':1}];names.append('extent-only-prepost-difference')
 return names

def run(final=False):
 c=parsed(S/'data/turnout/priority-set.json');o=parsed(M/'derived/context-observations.json');invariants(c,o);n=Counter();n['negative_fixtures']=len(negatives(c,o))
 for name in ['sos-maps-hub','rigis-precinct-page']:
  html=read(parsed(M/f'requests/{name}.json')).decode();match=re.search(r'window\.__SITE=(".*?")\s*\n',html)
  assert match and json.loads(urllib.parse.unquote(json.loads(match[1])))==parsed(M/f'source/{name}-embedded.json');n['whole_embedded_source_configs']+=1
 assert gzip.decompress((M/'derived/full-source-contract.json.gz').read_bytes())==(S/'data/turnout/priority-set.json').read_bytes()
 full=c['complete_descending_order'];inv=c['all_source_native_constituents'];parents=c['municipal_and_administrative_parent_sensitivity']['full_inventory'];doms={}
 for file in sorted(M.rglob('*.html')):
  d=DOM(file.read_text());assert 'script' not in d.tags and 'iframe' not in d.tags;doms[file]=d;n['html_documents']+=1
  for u in d.links:
   if urllib.parse.urlparse(u).scheme or u.startswith('//'):continue
   target=(file.parent/urllib.parse.unquote(u.split('#',1)[0])).resolve()
   assert target.is_file(),(file,u);n['local_html_links']+=1
 for mode,rows in [('priority',full[:242]),('full',full),('remainder',full[242:])]:
  d=doms[M/f'{mode}.html'];assert d.keys==[r['key'] for r in rows]
  assert [v for cl,k,v in d.objects if cl=='ranked-object']==rows
  expected={r['source_key']:r for r in o['ordered_full_observations']}
  assert [v for cl,k,v in d.objects if cl=='qualification']==[expected[r['key']] for r in rows]
  n['full_ranked_DOM_objects']+=len(rows)
 for p in parents:
  d=doms[M/f"parents/{p['key'].split(':')[-1]}.html"]
  assert [v for cl,k,v in d.objects if cl=='constituent']==[x for x in inv if x['key'] in p['native_keys']]
  assert [v for cl,k,v in d.objects if cl=='ranked-object']==[x for x in full if x['native_key'] in p['native_keys']]
  rec=next(x for x in o['complete_parent_resource_records'] if x['parent_key']==p['key']);assert [v for cl,k,v in d.objects if cl=='parent-object']==[rec]
  n['full_constituent_DOM_objects']+=len(p['native_keys']);n['parent_DOM_objects']+=1
 assert doms[M/'index.html'].parents==parsed(M/'source/directory-observation.json')['priority_order']
 seenparts=set();all_requests=[parsed(f) for f in sorted((M/'requests').glob('*.json'))]
 for r in all_requests:
  assert r['request_method']=='GET' and r['request_body'] is None
  for h in r['hops']:
   if 'parts' not in h:continue
   chunks=[]
   for i,p in enumerate(h['parts']):
    b=(M/p['path']).read_bytes();assert len(b)==p['stored_bytes']<40000000 and sha(b)==p['stored_sha256'];raw=gzip.decompress(b)
    assert p['part']==i and len(raw)==p['raw_bytes'] and sha(raw)==p['raw_sha256'];chunks.append(raw);seenparts.add(p['path']);n['original_part_references']+=1
   body=b''.join(chunks);assert len(body)==h['raw_bytes'] and sha(body)==h['raw_sha256'];n['whole_response_entities']+=1
  n['full_requests']+=1
 assert {str(p.relative_to(M)) for p in (M/'originals').glob('*')}==seenparts
 for pre in ['rigis','sos']:
  fs,index=load(pre);assert fs==parsed(M/f'derived/{pre}-native-features.json.gz');n['native_features']+=len(fs)
  qa=parsed(M/'qa/native-audit.json')[pre]
  for f,row in zip(fs,qa['features'],strict=True):
   d,_=geometry(f.get('geometry'));assert d==row['geometry_audit'] and f['attributes']==row['attributes'];n['native_full_attribute_geometry_rechecks']+=1
  assert len(index['batches'])==9
 pdfs=parsed(M/'qa/pdf-rendering.json');pdfrequests={r['id'] for r in all_requests if last(r).get('status')==200 and read(r).startswith(b'%PDF')}
 assert {r['request'] for r in pdfs['publications']}==pdfrequests
 for r in pdfs['publications']:
  if 'pages' not in r:continue
  assert len(r['rendered_all_pages'])==r['pages']
  for p in r['rendered_all_pages']:assert (M/p).read_bytes()[:8]==b'\x89PNG\r\n\x1a\n';n['PDF_pages']+=1
 manual=parsed(M/'qa/manual-visual-review.json');assert len(manual['manual_images'])==manual['count']==15
 for f in list(M.rglob('*'))+[S/'precinct-maps.md']:
  if f.is_dir():assert f.name not in ['__pycache__','node_modules','.venv','venv'];continue
  assert f.stat().st_size<40000000;n['owned_bodies_under_limit']+=1
  if f.suffix=='.md':
   for u in re.findall(r'(?<!!)\[[^\]]*\]\(([^\s)]+)\)',f.read_text()):
    if urllib.parse.urlparse(u).scheme or u.startswith('#'):continue
    target=(f.parent/u.split('#')[0]).resolve()
    if not final and target in [M/'manifest.json',M/'final-seal.json',M/'qa/reproduction.json',M/'qa/validation.json']:continue
    assert target.is_file(),(f,u);n['local_markdown_links']+=1
 return dict(status='pass',counts=dict(n),negative_fixtures=negatives(c,o),authority_path=AUTHORITY,no_javascript=True,no_spatial_allocation=True,scope='Full static DOM/object/order/escaping, local links, complete requests/entities, native coordinates/attributes, PDF every-page coverage, null/admin/source scope and no-cache/bounds checks; no legal/current admission.')
if __name__=='__main__':
 import sys
 r=run('--final' in sys.argv)
 if '--write' in sys.argv:dump(M/'qa/validation.json',r)
 print(json.dumps(r))
