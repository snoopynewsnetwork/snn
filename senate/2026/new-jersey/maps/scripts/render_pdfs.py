"""Render every page of bounded acquired map/companion PDFs, retain full text."""
from acquire import *
import fitz,concurrent.futures,collections

def one(id):
 try:b=content(id)
 except Exception:return None
 if not b.startswith(b'%PDF'):return None
 rec=json.loads((BASE/'receipts'/f'{id}.json').read_bytes());h=sha(b);out=BASE/'derived/pdf'/h;out.mkdir(parents=True,exist_ok=True);doc=fitz.open(stream=b,filetype='pdf');pages=[];text=[]
 for i,p in enumerate(doc):
  # Preview only: complete page, longest side1600px. Originals unchanged.
  scale=min(1600/p.rect.width,1600/p.rect.height);path=out/f'p{i+1:04d}.png'
  if not path.exists():p.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False).save(path)
  t=p.get_text('text');text.append({'page':i+1,'text':t,'width_points':p.rect.width,'height_points':p.rect.height,'rotation':p.rotation});pages.append({'page':i+1,'preview':str(path.relative_to(BASE)),'preview_sha256':sha(path.read_bytes()),'automatic_render_only':True})
 (out/'all-pages-text.json.gz').write_bytes(gzip.compress(json.dumps(text,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
 return {'receipt_id':id,'original_raw_sha256':h,'page_count':len(doc),'metadata':doc.metadata,'pages':pages,'text_asset':str((out/'all-pages-text.json.gz').relative_to(BASE)),'actual_viewing':'see qa/visual-review.json; automatic rendering is not human/agent viewing'}

def main():
 ids=[x['id'] for x in json.loads((BASE/'map-original-catalog.json').read_bytes())]+[p.stem for p in (BASE/'receipts').glob('state-companion-*.json')]+['county-map-02','county-map-01']+[x['id'] for f in ['derived/bounded-followup-sources.json','derived/final-linked-sources.json'] for x in json.loads((BASE/f).read_bytes())]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:out=[r for r in e.map(one,ids) if r]
 write(BASE/'pdf-inventory.json',out);print({'PDFs':len(out),'pages_automatically_rendered':sum(r['page_count'] for r in out)})
if __name__=='__main__':main()
