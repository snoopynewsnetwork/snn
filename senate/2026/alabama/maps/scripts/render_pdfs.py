"""Complete PDF originals, all-page text/warnings and automatic whole-page renders."""
from html_tools import ROOT,entity
from pathlib import Path
import json,gzip,hashlib,tempfile,subprocess,fitz

def sha(b):return hashlib.sha256(b).hexdigest()
index=[];seen={}
for receipt in sorted((ROOT/'source').glob('*.receipt.json')):
 path=str(receipt.relative_to(ROOT));r,b=entity(path)
 if r['status']!=200 or not b.startswith(b'%PDF'):continue
 h=sha(b)
 if (ROOT/'pdf'/h/'pages.json').exists():seen[h]=str((ROOT/'pdf'/h/'pages.json').relative_to(ROOT))
 if h not in seen:
  folder=ROOT/'pdf'/h;folder.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(prefix='al-maps-pdf-') as temp:
   p=Path(temp)/'original.pdf';p.write_bytes(b)
   result=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True);(folder/'all-pages.txt.gz').write_bytes(gzip.compress(result.stdout,mtime=0));(folder/'pdftotext.warnings.txt').write_bytes(result.stderr)
   fitz.TOOLS.reset_mupdf_warnings();doc=fitz.open(stream=b,filetype='pdf');pages=[]
   for i,page in enumerate(doc):
    scale=min(2,2000/max(page.rect.width,page.rect.height));pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False);target=folder/f'page-{i+1:04}.png';pix.save(target)
    pages.append({'page_1based':i+1,'width_points':page.rect.width,'height_points':page.rect.height,'render_path':str(target.relative_to(ROOT)),'pixel_width':pix.width,'pixel_height':pix.height,'manual_visual_review':False})
   (folder/'render.warnings.txt').write_text(fitz.TOOLS.mupdf_warnings())
   meta={'original_receipt':path,'original_sha256':h,'original_bytes':len(b),'pages':pages,'pdf_metadata':doc.metadata,'pdftotext_exit':result.returncode,'automatic_render_scope':'Every complete whole page; at most2000 pixels longest edge. Original vector/PDF bytes unchanged. Automatic rendering is not manual visual inspection.','text_path':str((folder/'all-pages.txt.gz').relative_to(ROOT))};doc.close()
   (folder/'pages.json').write_text(json.dumps(meta,indent=2)+'\n');seen[h]=str((folder/'pages.json').relative_to(ROOT));print(h[:12],len(pages),flush=True)
 index.append({'receipt':path,'original_sha256':h,'pages_metadata':seen[h]})
(ROOT/'pdf-index.json').write_text(json.dumps(index,indent=2)+'\n')
