from acquire import *
import fitz,concurrent.futures,subprocess,tempfile,shutil,re
VIEWED={(v["raw_sha256"],v["page_1based"])for v in json.loads((M/"visual-review.json").read_bytes())["PDF_pages_actually_viewed"]}if (M/"visual-review.json").exists()else set()

def render(item):
 key,r=item;b=body(r)
 if not b.startswith(b'%PDF-'):return None
 folder=M/'pdf-review'/r['raw_sha256'];folder.mkdir(parents=True,exist_ok=True);doc=fitz.open(stream=b,filetype='pdf');txt=[];pages=[]
 # Original is reconstructed only in an ephemeral file for Poppler, never retained twice.
 with tempfile.TemporaryDirectory(prefix='ma-maps-',dir='/private/tmp')as tmp:
  src=Path(tmp)/'original.pdf';src.write_bytes(b)
  for n,page in enumerate(doc):
   text=page.get_text(sort=True);txt.append(text)
   if len(doc)>200 and n not in [0,1,len(doc)-1]and not (folder/('page-%03d.png'%(n+1))).exists():
    pages.append(dict(page_1based=n+1,render=None,text_characters=len(text),automatically_rendered=False,visually_inspected=(r["raw_sha256"],n+1)in VIEWED,render_gap='Long roster >200 pages: first2,last and prior completed pages only; complete text/original retained'));continue
   prefix=folder/('page-%03d'%(n+1));png=prefix.with_suffix('.png')
   if not png.exists():subprocess.run(['pdftoppm','-f',str(n+1),'-l',str(n+1),'-singlefile','-scale-to','1400','-png',str(src),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   pages.append(dict(page_1based=n+1,render=str(png.relative_to(M)),text_characters=len(text),printed_dates=re.findall(r'\b(?:19|20)\d{2}\b',text),automatically_rendered=True,visually_inspected=(r["raw_sha256"],n+1)in VIEWED))
 (folder/'text.txt').write_text('\n\f\n'.join(txt));out=dict(raw_sha256=r['raw_sha256'],receipt=key,original_parts=r['parts'],pages=pages,page_count=len(doc),metadata=doc.metadata,pdf_format=doc.metadata.get('format'),render_scope='All pages for <=200-page documents; first2,last and earlier completed pages for longer rosters',render_engine='Poppler pdftoppm -scale-to 1400; full pages',text_engine='PyMuPDF '+fitz.VersionBind,visual_scope='automatic render only unless listed in visual-review.json')
 dump(folder/'document.json',out);return out

def main():
 unique={}
 for p in sorted((M/'receipts').glob('*.json')):
  r=json.loads(p.read_bytes())
  if 'parts'in r and r.get('status')==200:
   with gzip.open(M/r['parts'][0]['path'],'rb')as z:prefix=z.read(5)
   if prefix==b'%PDF-':unique.setdefault(r['raw_sha256'],(str(p.relative_to(M)),r))
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as ex:out=list(ex.map(render,unique.values()))
 dump(M/'pdf-index.json',out);print('PDFs',len(out),'pages',sum(x['page_count']for x in out))
if __name__=='__main__':main()
