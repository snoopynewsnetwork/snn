"""Independent complete HTML/XLSX selected publication object and source-position replay."""
from common import *
from html.parser import HTMLParser
from collections import Counter,defaultdict
import xml.etree.ElementTree as ET,zipfile,re,urllib.parse
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
class Node:
 def __init__(self,tag='',attrs=()):self.tag=tag;self.attrs=dict(attrs);self.children=[]
 def text(self):return ''.join(c.text() if isinstance(c,Node) else c for c in self.children)
 def all(self,tag):
  for c in self.children:
   if isinstance(c,Node):
    if c.tag==tag:yield c
    yield from c.all(tag)
 def has(self,cls):return cls in self.attrs.get('class','').split()
class Tree(HTMLParser):
 def __init__(self,b):super().__init__();self.root=Node();self.stack=[self.root];self.feed(b.decode('utf-8'));self.close()
 def handle_starttag(self,t,a):
  node=Node(t,a);self.stack[-1].children.append(node)
  if t not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):self.stack.append(node)
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==t:self.stack=self.stack[:i];break
 def handle_data(self,s):self.stack[-1].children.append(s)
def clean(s):return ' '.join(s.split())
def run():
 refs={r['raw_sha256']:r for name in ['data/turnout/asset-manifest.json','data/baselines/asset-manifest.json'] for r in parsed(S/name)['external_original_references']};cache={};n=Counter()
 def raw(digest):
  if digest not in cache:
   r=refs[digest];b=(S/r['path']).read_bytes();assert sha(b)==r['stored_sha256'] and len(b)==r['stored_bytes'];v=gzip.decompress(b) if r.get('compression')=='gzip' else b
   assert len(v)==r['raw_bytes'] and sha(v)==digest;cache[digest]=v
  return cache[digest]
 groups=defaultdict(list)
 for r in parsed(S/'data/turnout/extracts/html-controls.json'):groups[(r['source_id'],r['source_raw_sha256'])].append(r)
 trees={}
 for (source,digest),rows in groups.items():
  tree=Tree(raw(digest)).root;trees[digest]=tree;own=[]
  for ti,table in enumerate(tree.all('table'),1):
   contest=table.attrs.get('summary','')
   if contest not in ['Presidential Electors For:','Senator in Congress','Governor']:continue
   for ri,tr in enumerate(table.all('tr'),1):
    cand=next((c for c in tr.all('td') if c.has('candidate')),None);total=next((c for c in tr.all('td') if c.has('total') and c.has('votes')),None)
    if cand is None or total is None:continue
    own.append(dict(source_id=source,source_raw_sha256=digest,position=dict(table_ordinal=ti,row_ordinal=ri),contest=contest,candidate=clean(cand.text()),party_text=[clean(t.text()) for t in cand.all('span')],total=int(clean(total.text()).replace(',','')),methods=[dict(label=clean(t.text()).rsplit(':',1)[0],votes=int(clean(t.text()).rsplit(':',1)[1])) for t in tr.all('li')]))
  assert own==rows,(source,'full HTML control objects');n['full_HTML_candidate_control_objects']+=len(rows);n['full_HTML_entities']+=1
 parents=parsed(S/'data/turnout/extracts/municipal-hierarchy.json')
 for p in parents:
  digest=p['raw_sha256'];tree=trees[digest] if digest in trees else Tree(raw(digest)).root
  children=[]
  for a in tree.all('a'):
   if 'href' not in a.attrs:continue
   url=urllib.parse.urljoin(p['url'],a.attrs['href'])
   if url.startswith(p['url']) and re.fullmatch(r'\d{4}/',url[len(p['url']):]):children.append(dict(code=url[len(p['url']):].strip('/'),label=clean(a.text()),url=url))
  heading=next(clean(x.text()) for x in tree.all('h2') if x.attrs.get('id')=='contest-title')
  assert heading=='Votes by municipality: '+p['name'] and children==p['children'];n['municipal_original_parents']+=1;n['municipal_original_child_links']+=len(children)
 rows=parsed(S/'data/turnout/extracts/workbook-selected-rows.jsonl.gz');workbooks={}
 for digest in dict.fromkeys(r['source_raw_sha256'] for r in rows):
  z=zipfile.ZipFile(io.BytesIO(raw(digest)));assert z.testzip() is None
  strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)] if 'xl/sharedStrings.xml' in z.namelist() else []
  names=[s.attrib for s in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',NS)]
  sheets={}
  for member in z.namelist():
   if not re.fullmatch(r'xl/worksheets/sheet\d+\.xml',member):continue
   out={}
   for row in ET.fromstring(z.read(member)).findall('.//m:row',NS):
    cells={}
    for cell in row:
     v=cell.find('m:v',NS);s=v.text if v is not None else ''.join(cell.itertext());value=strings[int(s)] if cell.attrib.get('t')=='s' else s
     cells[cell.attrib['r']]=dict(value=value,xml_type=cell.attrib.get('t'),raw_v=None if v is None else v.text)
    out[int(row.attrib['r'])]=cells
   sheets[member]=out
  workbooks[digest]=(names,sheets);n['complete_Board_workbooks']+=1
 for r in rows:
  names,sheets=workbooks[r['source_raw_sha256']];cells=sheets[r['member']][r['row']]
  assert r['cells']==cells and r['columns']=={re.sub(r'\d+$','',k):v['value'] for k,v in cells.items()}
  assert r['header']==dict(cells=sheets[r['member']][1],sheetnames=names)
  assert r['key']==r['source_raw_sha256']+':'+r['member']+':row'+str(r['row']);n['whole_workbook_selected_rows']+=1;n['whole_workbook_selected_cells']+=len(cells)
 proof=parsed(S/'data/baselines/extracts/writein-row5-source-proof.json');z=zipfile.ZipFile(io.BytesIO(raw(proof['source_raw_sha256'])));b=z.read(proof['member']);assert sha(b)==proof['member_sha256']
 strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)];cells={c.attrib['r']:c for c in ET.fromstring(b).findall('.//m:c',NS)}
 for row in proof['rows']:
  for c in row['cells']:
   assert b[c['xml_byte_start']:c['xml_byte_end']].decode()==c['original_cell_xml']
   cell=cells[c['cell']];v=cell.find('m:v',NS);literal=strings[int(v.text)] if cell.attrib.get('t')=='s' else (v.text if v is not None else None)
   assert literal==c['literal'];n['writein_exact_XML_positions']+=1
 assert strings[int(cells['D5'].find('m:v',NS).text)]=='Mario Frioli ' and cells['E5'].find('m:v',NS).text=='1'
 n['unique_complete_original_entities_read']=len(cache)
 return dict(status='pass',counts=dict(n),scope='Full original HTML candidate/method controls and117 municipal child inventories; every selected Board workbook cell/header/type/raw scalar; every captured Cranston write-in XML position and literal trailing-space D5/E5. Complete bodies, no sampled originals or producer import/writer.')
if __name__=='__main__':
 import sys
 r=run()
 if '--write' in sys.argv:dump(M/'qa/publication-reconstruction.json',r)
 print(json.dumps(r))
