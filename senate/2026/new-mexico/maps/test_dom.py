"""Actual generated offline DOM, static filter/order/full-object and hostile escaping tests."""
from common import *
from build import entry_html
import copy,os

def objects(doc,cls):return [json.loads(n['text'])for n in doc.nodes if n['tag']=='pre'and n['attrs'].get('class')==cls]
def run():
 rows=[json.loads(line)for line in gzip.decompress((M/'inventory.jsonl.gz').read_bytes()).splitlines()];count=0;checks=[]
 groups=[('inventory.html',rows),('administrative.html',[r for r in rows if r['complete_constituent']['administrative']]),('masked.html',[r for r in rows if any(v is None for v in r['complete_constituent']['candidate_values'])]),('nonadministrative.html',[r for r in rows if not r['complete_constituent']['administrative']])]
 for name,wanted in groups:
  d=Document((M/name).read_bytes());articles=[n for n in d.nodes if n['tag']=='article'and n['attrs'].get('class')=='observation'];full=objects(d,'full-object')
  assert [a['attrs']['data-key']for a in articles]==[r['complete_constituent']['key']for r in wanted]
  assert [int(a['attrs']['data-sequence'])for a in articles]==[r['coverage_sequence']for r in wanted];assert full==wanted
  assert not any(n['tag']=='script'for n in d.nodes)
  checks.append({'page':name,'records':len(full),'full_objects_equal':True,'exact_filter_membership_and_order':True});count+=4
 parents=json.loads((M/'parents-index.json').read_bytes());index=Document((M/'index.html').read_bytes());assert [n['attrs']['data-parent']for n in index.nodes if n['tag']=='article'and 'data-parent'in n['attrs']]==[p['key']for p in parents];count+=1
 for p in parents:
  f=p['key'].split(':')[-1];fullparent=json.loads((M/'parents'/(f+'.json')).read_bytes());d=Document((M/'atlas'/(f+'.html')).read_bytes());assert objects(d,'parent-object')==[fullparent]
  want=[r for r in rows if r['complete_constituent']['parent_key']==p['key']];assert objects(d,'full-object')==want;count+=2
 # Generated hostile labels/URLs/nulls must remain text and a complete JSON object.
 r=copy.deepcopy(rows[0]);evil='</pre><script>globalThis.INJECTED=true</script><img src=x onerror=alert(1)> & " \' Ω'
 r['complete_constituent']['native_id_literal']=evil;r['source_specific_gaps'].append(evil);r['complete_original_source_observation']['raw_row'].append(evil);frag=entry_html(r);d=Document(frag.encode());assert objects(d,'full-object')==[r]
 assert not any(n['tag']in ['script','img']for n in d.nodes);assert '&lt;script&gt;'in frag and '&amp;'in frag and '&quot;'in frag;count+=3
 # Link existence is checked from actual emitted DOM, not from an assumed template.
 links_checked=0;allpages=list(M.glob('*.html'))+list((M/'atlas').glob('*.html'))
 for p in allpages:
  d=Document(p.read_bytes());ids=[n['attrs']['id']for n in d.nodes if 'id'in n['attrs']];assert len(ids)==len(set(ids));count+=1
  for n in d.nodes:
   for attr in ['href','src']:
    if attr not in n['attrs']:continue
    url=n['attrs'][attr];split=urllib.parse.urlsplit(url);assert not split.scheme and not split.netloc,(p,url)
    target=(p.parent/urllib.parse.unquote(split.path)).resolve();assert target.is_file()and target.is_relative_to(S),(p,url);links_checked+=1
    assert not url.lower().startswith(('javascript:','data:'))
 out={'status':'pass','DOM_parser':'stdlib HTMLParser full ordered node tree of actual emitted HTML; not a browser engine','javascript_shipped':False,'filter_mechanism':'complete static category pages/local links; no JavaScript runtime needed','checks':count,'filtered_pages':checks,'county_pages':33,'relative_links_checked':links_checked,'hostile_escaping_roundtrip':True,'browser_render_claim':False}
 write(M/'dom-tests.json',out);print(out)
if __name__=='__main__':run()
