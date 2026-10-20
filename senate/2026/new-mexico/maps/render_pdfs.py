"""Render every page of every complete acquired PDF; no modification to originals."""
from common import *
import subprocess,concurrent.futures,tempfile

def one(p):
 r=json.loads(p.read_bytes());ref=r.get('body',{});b=body(ref)if ref else b''
 if not b.startswith(b'%PDF-'):return None
 h=sha(b);dest=M/'renders'/h;dest.mkdir(parents=True,exist_ok=True)
 target=S/ref['path']if ref.get('encoding')=='identity'else None
 with tempfile.TemporaryDirectory()as td:
  if target is None:target=Path(td)/'original.pdf';target.write_bytes(b)
  info=subprocess.run(['pdfinfo',str(target)],capture_output=True,text=True,check=True).stdout
  (dest/'pdfinfo.txt').write_text(info)
  textfile=dest/'complete.txt';subprocess.run(['pdftotext','-layout',str(target),str(textfile)],check=True,capture_output=True)
  if not (dest/'page-1.png').exists()and not list(dest.glob('page-*.png')):
   cp=subprocess.run(['pdftoppm','-scale-to','1800','-png',str(target),str(dest/'page')],capture_output=True,timeout=240)
   if cp.returncode:raise RuntimeError(cp.stderr.decode())
  pages=int(next(l.split(':')[1]for l in info.splitlines()if l.startswith('Pages:')))
  imgs=sorted(dest.glob('page-*.png'));assert len(imgs)==pages,(p,pages,imgs)
 return {'receipt':pin(p),'original':ref,'pages':pages,'full_page_automatic_renders':[pin(x)for x in imgs],'pdfinfo':pin(dest/'pdfinfo.txt'),'whole_text':pin(textfile),'manual_visual_review':False,'render_scale_to_pixels':1800}
def run():
 seen=set();ps=[]
 for p in sorted((M/'receipts').glob('*.json')):
  r=json.loads(p.read_bytes());h=r.get('body',{}).get('raw_sha256')
  if h and h not in seen:ps.append(p);seen.add(h)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=[r for r in pool.map(one,ps)if r]
 write(M/'pdf-render-inventory.json',rows);print('Complete PDF render count',len(rows),'pages',sum(r['pages']for r in rows))
if __name__=='__main__':run()
