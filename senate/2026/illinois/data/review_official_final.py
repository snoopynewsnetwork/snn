"""Coordinator full-original audit. No producer imports, writes or network."""
from pathlib import Path
from html.parser import HTMLParser
import collections,csv,gzip,hashlib,io,json,zipfile
import xml.etree.ElementTree as ET

S=Path(__file__).resolve().parents[1]
H=S/'data/results-sources'
N=0
def ck(v,note=''):
 global N
 assert v,note
 N+=1
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def raw(p):return (S/p).read_bytes()
def verify(r):
 b=raw(r['path']);ck(len(b)==r['bytes']<40000000,r['path']);ck(sha(b)==r['sha256'],r['path']);return b
def read(p):
 b=raw(p);b=gzip.decompress(b)if str(p).endswith('.gz')else b
 if '.jsonl' in str(p):return [json.loads(l)for l in b.splitlines()if l.strip()]
 if '.csv' in str(p):return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 return json.loads(b)
def ptr(v,p):
 for k in p.split('/')[1:]:
  k=k.replace('~1','/').replace('~0','~');v=v[int(k)]if isinstance(v,list)else v[k]
 return v
class Page(HTMLParser):
 def __init__(self,b):
  super().__init__(convert_charrefs=True);self.rows=[];self.row=None;self.cell=None;self.text=[];self.links=[];self.feed(b.decode('utf-8-sig',errors='replace'))
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t in ('a','iframe'):self.links.append((t,d))
  if t=='tr':self.row=[];self.rows.append(self.row)
  if t in ('th','td')and self.row is not None:self.cell=[];self.row.append(self.cell)
 def handle_endtag(self,t):
  if t in ('th','td'):self.cell=None
  if t=='tr':self.row=None
 def handle_data(self,d):
  self.text.append(d)
  if self.cell is not None:self.cell.append(d)
 def cells(self):return [[''.join(c)for c in r]for r in self.rows]
def fields_equal(a,b):
 ck(type(a)is type(b))
 if isinstance(a,dict):
  ck(list(a)==list(b)or set(a)==set(b))
  for k in a:fields_equal(a[k],b[k])
 elif isinstance(a,list):
  ck(len(a)==len(b))
  for x,y in zip(a,b):fields_equal(x,y)
 else:ck(a==b)

def main():
 mf=read('data/results-sources/asset-manifest.json')
 actual={str(p.relative_to(S))for p in H.rglob('*')if p.is_file()and p.name!='asset-manifest.json'}|{'official-results.md','data/official-results-sources.csv'}
 ck(actual=={r['path']for r in mf['owned_assets']});ck(len(actual)==3047)
 for r in mf['owned_assets']:verify(r)
 ck(not list(H.rglob('__pycache__')))
 a=read('data/coordinator-priority-acceptance.json');c=json.loads(verify(a['frozen_contract']));ck(len(c)==31)
 for r in a['complete_root_field_semantics']:ck(sha(canon(ptr(c,r['pointer'])))==r['full_recursive_semantic_sha256'])
 for r in a['complete_source_companion_files']:
  b=verify(r)
  if r['path'].endswith('.gz'):
   b=gzip.decompress(b);ck(len(b)==r['complete_reconstructed_bytes']);ck(sha(b)==r['complete_reconstructed_sha256'])
  if 'full_semantic_sha256'in r:ck(sha(canon(read(r['path'])))==r['full_semantic_sha256'])
 objects=0
 for r in a['complete_source_object_reference_bodies']:
  verify(r);digest=hashlib.sha256();size=0;file=None;value=None;seen=collections.Counter()
  with gzip.open(S/r['path'],'rb')as f:
   for line in f:
    size+=len(line);digest.update(line);v=json.loads(line)
    if v['file']!=file:file=v['file'];value=read(file)
    obj=ptr(value,v['pointer'])if 'pointer'in v else value[v['JSONL_record_1based']-1]if 'JSONL_record_1based'in v else value[v['CSV_row_1based_including_header']-1]
    ck(sha(canon(obj))==v['full_recursive_semantic_sha256']);objects+=1;seen[file]+=1
  ck(size==r['complete_reconstructed_bytes']);ck(digest.hexdigest()==r['complete_reconstructed_sha256']);ck(dict(seen)==r['source_objects_by_file'])
 ck(objects==554096)
 refs=read('data/results-sources/original-asset-references.json')['assets'];ck(len(refs)==1209)
 for r in refs:verify(r)
 by={r['key']:r for r in c['native_constituents']};rows=read('data/results-sources/investigations-priority.jsonl.gz')+read('data/results-sources/investigations-remainder.jsonl.gz');ck(len(rows)==10062)
 ck([r['key']for r in rows]==a['ordered_full_keys'])
 for i,r in enumerate(rows,1):
  ck(r['historical_rank']==i);fields_equal(r['complete_historical_native_source_object'],by[r['key']]);ck(r['historical_parent_key']==c['native_to_authority_parent_map'][r['key']]);ck(r['november_returns_admitted']is False);ck(r['current_geography_join']is r['unknown_remaining_ballots']is r['current_navigation_election_contest_choice_unit_mapping']is None)
 vals=[by[k]['printed_known_recorded_sum']for k in a['ordered_full_keys']];ck(sum(vals)==5592368);ck(sum(vals[:15])==29572);ck(sum(vals[:5539])==4473789);ck(vals[5539]==523);ck(sum(vals[:5540])==4474312);ck(sum(vals[5540:])==1118056)
 directory=read('data/results-sources/current-authority-directory.json');ck(len(directory)==108)
 receipts={};bodies={};aliases=[];complete=redirects=0
 for p in sorted((H/'receipts').glob('*.json')):
  r=read(str(p.relative_to(S)));receipts[r['id']]=r
  if p.stem!=r['id']:aliases.append(str(p.relative_to(S)))
  ck(r['method']in ['GET','POST']);ck(bool(r['retrieved_at_utc']and r['finished_at_utc']))
  if not r['complete']:ck(bool(r.get('error')));continue
  b=raw(r['path']);ck(len(b)==r['stored_bytes']);ck(sha(b)==r['stored_sha256']);b=gzip.decompress(b);ck(len(b)==r['raw_bytes']);ck(sha(b)==r['raw_sha256']);bodies[r['id']]=b;complete+=1
  ck('headers'in r or 'raw_headers_latin1'in r)
  for redir in r.get('redirects',[]):
   ck(all(k in redir for k in ['url','status','headers','body_hex']));bytes.fromhex(redir['body_hex']);redirects+=1
 ck(len(receipts)==898 and complete==881 and redirects==188 and len(aliases)==4)
 dp=Page(bodies['state-directory-all']);dr=[r for r in dp.cells()if len(r)==7 and r[0]not in ['Jurisdiction','']]
 ck(dr==[[cell['text']for cell in r['complete_directory_row']['cells']]for r in directory])
 parents=read('data/results-sources/historical-parent-hierarchy.json.gz');ck(len(parents)==108);locals_count=0;prior_count=0
 for old,h in zip(c['authority_inventory'],parents):
  d=read(f"data/results-sources/parents/{old['authority_id']}.json");fields_equal(d['complete_historical_parent_object'],old);fields_equal(h['complete_historical_parent_object'],old)
  keys=[k for k in a['ordered_full_keys']if c['native_to_authority_parent_map'][k]==old['key']];ck(d['historical_child_keys_ordered']==keys);ck(d['priority_child_keys_ordered']==[k for k in keys if k in set(a['ordered_priority_keys'])]);ck(d['remainder_child_keys_ordered']==[k for k in keys if k in set(a['ordered_remainder_keys'])]);locals_count+=bool(d['local_requests']);prior_count+=bool(d['priority_child_keys_ordered']);ck(d['admitted_november_returns']is False);ck(d['current_leaf_matches']is d['measured_cadence']is d['exact_outstanding_eligible_ballots']is None)
 ck(locals_count==103 and prior_count==97)
 schema=read('data/results-sources/source-schema-inventory.json');ck(len(schema)==77);kinds=collections.Counter();html_samples=0;json_samples=0
 for r in schema:
  sid=r['receipt_id'];b=bodies[sid];v=read(r['sample_path']);kinds[r['format']]+=1
  if r['format']=='complete JSON':fields_equal(v,json.loads(b));json_samples+=1
  elif sid in ['state-candidate-file-tsv','hancock-primary-csv','macoupin-primary-csv']:
   expected=list(csv.reader(io.StringIO(b.decode('utf-8-sig')),delimiter='\t'if sid.endswith('tsv')else ','));ck(v['complete_header_in_order']==expected[0]);fields_equal(v['complete_rows'],expected[1:])
  elif sid=='state-candidate-file-xml':
   root=ET.fromstring(b);ck(v['root_tag']==root.tag);ck(len(v['complete_rows'])==len(root))
   for saved,node in zip(v['complete_rows'],root):ck(saved['tag']==node.tag);ck(saved['attributes_in_source_order']==[list(t)for t in node.attrib.items()]);ck(saved['text']==node.text)
  elif sid=='logan-elected-register-xlsx':
   z=zipfile.ZipFile(io.BytesIO(b));ck(z.testzip()is None);ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};ss=[''.join(n.itertext())for n in ET.fromstring(z.read('xl/sharedStrings.xml'))]
   for sh in v['complete_sheets']:
    rb=z.read(sh['member']);ck(sha(rb)==sh['complete_xml_sha256']);nodes=ET.fromstring(rb).findall('.//x:sheetData/x:row',ns);ck(len(nodes)==len(sh['rows']))
    for node,saved in zip(nodes,sh['rows']):
     ck(node.attrib==saved['attributes']);cells=node.findall('x:c',ns);ck(len(cells)==len(saved['cells']))
     for cell,sc in zip(cells,saved['cells']):
      val=cell.find('x:v',ns);fv=cell.find('x:f',ns);x=val.text if val is not None else None
      if cell.get('t')=='s'and x is not None:x=ss[int(x)]
      ck(sc['attributes']==cell.attrib);ck(sc['source_value']==x);ck(sc['formula']==(fv.text if fv is not None else None));ck(sc['complete_xml']==ET.tostring(cell,encoding='unicode'))
  else:
   h=Page(b);ck([[c['text']for c in row['cells']]for row in v['rows']]==h.cells());ck(v['text']==' '.join(h.text));ck([(r['tag'],r['attrs'])for r in v['links']]==h.links);html_samples+=1
 tsv=list(csv.DictReader(io.StringIO(bodies['state-candidate-file-tsv'].decode('utf-8-sig')),delimiter='\t'));ck(len(tsv)==528);senate=[r for r in tsv if r['OfficeName']=='UNITED STATES SENATOR'];ck(len(senate)==4);ck(collections.Counter(r['CandidateStatus']for r in senate)=={'Active':3,'Removed':1});ck({r['CandidateID']for r in senate}=={'35626','35627','35910','35913'})
 ss=read('data/results-sources/operative-statutes-complete.json');ck(len(ss)==32)
 for r in ss:
  b=bodies[r['receipt_id']];text=' '.join(Page(b).text);ck(text==r['complete_text']);ck(r['section']in text)
 out=dict(status='pass_independent_full_official_original_graph_source_and_seal_review',checks=N,producer_manifest=pin(H/'asset-manifest.json'),owned_entries=3047,complete_root_fields=31,complete_companions=116,complete_recursive_objects=objects,immutable_original_asset_refs=len(refs),all_complete_native_objects=10062,priority=5540,remainder=4522,all_authorities=108,priority_parents=97,current_local_request_parents=locals_count,receipt_files=902,complete_entities=complete,redirect_observations=redirects,complete_schemas=77,JSON_full_objects=json_samples,HTML_fulltext_table_link_replays=html_samples,sample_format_counts=dict(kinds),current_all_status_candidate_rows=528,Senate_status_rows=4,active_Senate_rows=3,operative_section_raw_text_replays=32,november_returns_admitted=0,current_leaf_joins_approved=False,no_producer_import_or_write=True,qualification='Current authority associations and primary/November zero templates only; all source scopes, unknowns, writein limitations, five local publisher gaps and precise legal/docket qualifications remain. No live readiness or legally exhaustive allocation approval.')
 p=S/'data/coordinator-official-final-review.json';p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(dict(status=out['status'],checks=N,proof=pin(p)))
if __name__=='__main__':main()
