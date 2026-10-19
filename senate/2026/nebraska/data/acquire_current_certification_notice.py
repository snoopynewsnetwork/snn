"""Acquire the observed primary certification notice without replacing captures."""
from pathlib import Path
from html.parser import HTMLParser
import gzip,hashlib,importlib.util,json,urllib.parse
DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.hrefs=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a'and'href'in dict(attrs):self.hrefs.append(dict(attrs)['href'])
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 spec=importlib.util.spec_from_file_location('ne_capture',NEWS/'fetch_evidence.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 manifest=NEWS/'manifest.json';before=manifest.read_bytes();rows=json.loads(before);original=list(rows);byid={r['id']:r for r in rows}
 def acquire(key,url,parent=None):
  if key in byid:assert byid[key]['url']==url;return byid[key]
  assert not(NEWS/(key+'.html.gz')).exists();r=m.fetch((key,url));r['parent_source_id']=parent
  if r.get('raw_sha256'):
   same=next((x for x in rows if x.get('raw_sha256')==r['raw_sha256']and x.get('asset')),None)
   if same:
    fresh=NEWS/r['asset'];existing=NEWS/same['asset'];assert gzip.decompress(fresh.read_bytes())==gzip.decompress(existing.read_bytes());fresh.unlink();r['asset']=same['asset'];r['stored_sha256']=sha(existing.read_bytes());r['shared_identical_entity_id']=same['id']
  rows.append(r);byid[key]=r;return r
 parent=acquire('sos-2026-general-certification-notice-parent','https://sos.nebraska.gov/secretary-state-certifies-ballot-2026-general-election');assert parent['status']==200
 parser=Links();parser.feed(gzip.decompress((NEWS/parent['asset']).read_bytes()).decode());hrefs=[h for h in parser.hrefs if urllib.parse.urlparse(h).path.lower().endswith('.pdf')and'certifies' in urllib.parse.unquote(h).lower()];assert len(hrefs)==1
 url=urllib.parse.urljoin(parent['final_url'],hrefs[0]);doc=acquire('sos-2026-general-certification-notice-pdf',url,parent['id']);assert doc['status']==200 and gzip.decompress((NEWS/doc['asset']).read_bytes()).startswith(b'%PDF-')
 assert rows[:len(original)]==original and manifest.read_bytes()==before
 target=manifest.with_suffix('.new.json');target.write_text(json.dumps(rows,indent=2)+'\n');target.replace(manifest)
 out=dict(status='actual_primary_parent_linked_certification_notice_acquired_not_new_worker',parent_id=parent['id'],literal_PDF_href=hrefs[0],resolved_PDF_URL=url,PDF_id=doc['id'],existing_final_candidate_list_id='sos-final-general-candidate-pdf',new_observations=len(rows)-len(original),qualification='Retained current primary certification announcement is distinct from the finalcandidate listing, sampleballot, currentfeedIDs, namedwritein universe and later withdrawal/court scope. No worker launch or accepted priority follows.')
 p=DATA/'coordinator-current-certification-acquisition.json'
 if p.exists():
  prior=json.loads(p.read_bytes());assert{k:v for k,v in prior.items()if k!='new_observations'}=={k:v for k,v in out.items()if k!='new_observations'}
 else:p.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(dict(new_observations=out['new_observations'],captures=[dict(id=r['id'],status=r.get('status'),bytes=r.get('bytes'),raw_sha256=r.get('raw_sha256'))for r in[parent,doc]])))
if __name__=='__main__':main()
