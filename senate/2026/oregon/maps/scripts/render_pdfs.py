"""Render every complete acquired map/legal PDF page, including all PDFs inside ZIPs."""
from common import *
from acquire import body_of
import tempfile,subprocess,zipfile,concurrent.futures,fitz,sys

def pdfs():
 seen=set()
 for p in sorted((M/'requests').glob('*.json')):
  r=load(str(p.relative_to(S)));b=body_of(r)
  if b.startswith(b'%PDF'):candidates=[(None,b)]
  elif b.startswith(b'PK\x03\x04'):
   with zipfile.ZipFile(io.BytesIO(b)) as z:candidates=[(n,z.read(n)) for n in z.namelist() if n.lower().endswith('.pdf')]
  else:continue
  for member,raw in candidates:
   digest=sha(raw)
   if digest in seen:continue
   seen.add(digest);yield {'request':str(p.relative_to(S)),'member':member,'source_pdf_sha256':digest,'source_pdf_bytes':len(raw)},raw

def render(job):
 locator,raw=job;digest=locator['source_pdf_sha256'];outdir=M/'renders'/digest;outdir.mkdir(parents=True,exist_ok=True)
 with fitz.open(stream=raw,filetype='pdf') as doc:
  metadata=doc.metadata;pages=[{'page':i+1,'width_points':p.rect.width,'height_points':p.rect.height} for i,p in enumerate(doc)];text='\n\f\n'.join(p.get_text() for p in doc).encode()
 textpath='maps/renders/'+digest+'/complete-text.txt.gz';(S/textpath).write_bytes(gzip.compress(text,mtime=0))
 with tempfile.TemporaryDirectory(prefix='or-map-pdf-') as d:
  source=Path(d)/'original.pdf';source.write_bytes(raw)
  command=['pdftoppm','-scale-to','1600','-png',str(source),str(outdir/'page')]
  if not all(outdir.glob('page-*.png')) or len(list(outdir.glob('page-*.png')))!=len(pages):
   p=subprocess.run(command,capture_output=True,check=True);stderr=p.stderr.decode('utf-8','replace')
  else:stderr='previous complete rendering retained'
 images=sorted(outdir.glob('page-*.png'),key=lambda p:int(p.stem.split('-')[-1]));assert len(images)==len(pages)
 for page,p in zip(pages,images):page['render']=ref(str(p.relative_to(S)))
 out={**locator,'metadata':metadata,'page_count':len(pages),'pages':pages,'text':ref(textpath),'complete_render':True,'renderer':'pdftoppm -scale-to 1600 -png; all pages, no clipping','render_stderr':stderr}
 print(json.dumps({'request':locator['request'],'member':locator['member'],'pages':len(pages)}),flush=True);return out
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:out=list(pool.map(render,pdfs()))
 save('maps/renders/index.json',out);print(json.dumps({'whole_pdfs':len(out),'complete_pages':sum(x['page_count'] for x in out)}))
