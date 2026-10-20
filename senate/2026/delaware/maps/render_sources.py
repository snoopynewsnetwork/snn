"""Full-page automated rendering of EVERY distinct acquired PDF, no crop.
Visual-review.json separately records actually viewed selected images.
"""
from common import *
import subprocess,tempfile,re,collections

def main():
 receipts=[read(p) for p in sorted((M/'source').glob('*.receipt.json'))];pdfs={}
 for r in receipts:
  raw=body(r)
  if raw.startswith(b'%PDF'):pdfs.setdefault(r['raw_sha256'],[]).append(r)
 outputs=[]
 for h,rs in pdfs.items():
  r=rs[0];out=M/'previews/pdf'/r['id'];out.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'original.pdf';p.write_bytes(body(r));info=subprocess.check_output(['pdfinfo',str(p)]).decode();pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1])
   subprocess.run(['pdftotext','-layout',str(p),str(out/'full-text.txt')],check=True)
   subprocess.run(['pdftoppm','-scale-to','1800','-png',str(p),str(out/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  imgs=sorted(out.glob('page-*.png'));assert len(imgs)==pages
  text=(out/'full-text.txt').read_text(errors='replace')
  outputs.append(dict(source_ids=[v['id'] for v in rs],source_raw_sha256=h,pages=pages,pdfinfo=info,command=['pdftoppm','-scale-to','1800','-png','EXACT_ORIGINAL','OUTPUT'],scope='all pages, full media page scaled to <=1800px longest side; automated render only, not universal manual inspection',images=[pin(p) for p in imgs],text=pin(out/'full-text.txt'),date_line_candidates=[line for line in text.splitlines() if re.search('updated|March|2023|2024|2022|2012|2002',line,re.I)][:25]))
  print(r['id'],pages,flush=True)
 write('qa/pdf-rendering.json',dict(distinct_original_pdfs=len(pdfs),total_pages=sum(v['pages'] for v in outputs),renderer_version=subprocess.check_output(['pdftoppm','-v'],stderr=subprocess.STDOUT).decode(),outputs=outputs,manual_visual_inspection='See visual-review.json; automatic rendering does not imply visual inspection'))
if __name__=='__main__':main()
