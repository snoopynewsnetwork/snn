#!/usr/bin/env python3
"""Read-only render of complete saved official PDF entities; no PDF authoring."""
import sys
sys.dont_write_bytecode=True
import collections,hashlib,json,pathlib
import fitz
from PIL import Image,ImageDraw,ImageChops,ImageStat
from acquire import ROOT,body

def main():
 out=ROOT/'previews/pdfs';out.mkdir(parents=True,exist_ok=True);records=[];contacts=[]
 for p in sorted((ROOT/'raw').glob('*.receipt.json')):
  r=json.loads(p.read_text());
  if r.get('status')!=200:continue
  b=body(r['source_id'])
  if not b.startswith(b'%PDF'):continue
  doc=fitz.open(stream=b,filetype='pdf');key=r['source_id'];pages=[];text=[]
  for i,page in enumerate(doc):
   text.append(f'--- PAGE {i+1} ---\n'+page.get_text())
   fitz.TOOLS.mupdf_warnings(reset=True)
   scale=(2000 if key=='duval-archived-countywide-pdf' else 1200)/max(page.rect.width,page.rect.height) if len(doc)<4 else 850/max(page.rect.width,page.rect.height)
   pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False);warnings=fitz.TOOLS.mupdf_warnings(reset=True);path=out/f'{key}-p{i+1:03d}.png';pix.save(path)
   im=Image.open(path).convert('RGB');diff=ImageChops.difference(im,Image.new('RGB',im.size,'white'));box=diff.getbbox();assert box is not None,(key,i)
   pages.append({'page_1based':i+1,'source_render_warnings':warnings,'source_page_points':[page.rect.width,page.rect.height],'text_characters':len(page.get_text()),'embedded_image_count':len(page.get_images()),'preview_path':str(path.relative_to(ROOT)),'preview_pixels':list(im.size),'nonwhite_bbox':box,'PNG_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
   thumb=Image.new('RGB',(260,230),'white');im.thumbnail((250,195));thumb.paste(im,((260-im.width)//2,25));ImageDraw.Draw(thumb).text((5,5),f'{key} p{i+1}',fill='black');contacts.append(thumb)
  (out/f'{key}.txt').write_text('\n'.join(text));records.append({'source_id':key,'original_sha256':r['original_sha256'],'page_count':len(doc),'metadata':doc.metadata,'pages':pages,'text_extract':str((out/f'{key}.txt').relative_to(ROOT))})
  print(key,len(doc),flush=True)
 for n in range(0,len(contacts),36):
  subset=contacts[n:n+36];canvas=Image.new('RGB',(6*260,((len(subset)+5)//6)*230),'#d9dfe7')
  for j,im in enumerate(subset):canvas.paste(im,((j%6)*260,(j//6)*230))
  canvas.save(out/f'contact-{n//36+1:02d}.png')
 (ROOT/'pdf-render-validation.json').write_text(json.dumps({'engine':'PyMuPDF '+fitz.VersionBind,'source_PDF_count':len(records),'all_pages_rendered':sum(r['page_count'] for r in records),'contact_sheets':list(str(p.relative_to(ROOT)) for p in sorted(out.glob('contact-*.png'))),'PDFs':records},indent=2)+'\n')
if __name__=='__main__':main()
