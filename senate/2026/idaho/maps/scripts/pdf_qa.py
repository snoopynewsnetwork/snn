#!/usr/bin/env python3
"""Read-only original PDF inspection; complete automated rendering, no PDF edits."""
import collections,hashlib,json
from pathlib import Path
import fitz
from evidence import original,own_receipts
from PIL import Image,ImageDraw,ImageFont
MAPS=Path(__file__).resolve().parents[1];ROOT=MAPS.parent

def main():
 rs=own_receipts();by=collections.defaultdict(list)
 for r in rs:
  if r.get('stored_path','').endswith('.pdf') or 'stored_parts' in r:by[r.get('stored_path',r['id'])].append(r)
 out=[];cards=[];directory=MAPS/'previews/pdf';directory.mkdir(exist_ok=True)
 for path,rr in sorted(by.items()):
  b=original(rr[0]);h=hashlib.sha256(b).hexdigest();doc=fitz.open(stream=b,filetype='pdf');texts=[];pages=[]
  for i,page in enumerate(doc):
   texts.append(page.get_text());scale=min(1.5,1300/max(page.rect.width,page.rect.height));pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False);image=directory/f'{h[:16]}-p{i+1}.png';pix.save(image)
   pages.append(dict(page=i+1,width_points=page.rect.width,height_points=page.rect.height,png=str(image.relative_to(MAPS)),render_pixels=[pix.width,pix.height]))
  text='\n\f\n'.join(texts);tp=MAPS/'qa'/f'pdf-{h[:16]}.txt';tp.write_text(text)
  out.append(dict(original=path,sha256=h,request_ids=[r['id'] for r in rr],requested_urls=[r['requested_url'] for r in rr],metadata=doc.metadata,complete_pages=len(doc),all_pages_rendered=True,pages=pages,complete_text_path=str(tp.relative_to(MAPS)),first_text=text[:1200]))
  # One contact card for every original; complete pages remain separately inspectable.
  im=Image.open(MAPS/pages[0]['png']);im.thumbnail((290,230));card=Image.new('RGB',(300,275),'white');card.paste(im,((300-im.width)//2,0));d=ImageDraw.Draw(card);d.text((5,234),rr[0]['id'][:42],fill='black');d.text((5,250),f'{h[:16]} | {len(doc)} pages',fill='black');cards.append(card)
 for start in range(0,len(cards),25):
  group=cards[start:start+25];sheet=Image.new('RGB',(1500,((len(group)+4)//5)*275),'#e1e6ea')
  for i,card in enumerate(group):sheet.paste(card,((i%5)*300,(i//5)*275))
  sheet.save(directory/f'contact-{start//25+1:02}.png')
 warnings=fitz.TOOLS.mupdf_warnings();(MAPS/'qa/pdf-engine-warnings.txt').write_text(warnings+'\n')
 result=dict(status='automated_complete_original_PDF_render',originals=len(out),pages=sum(x['complete_pages'] for x in out),viewed_scope='Automated full render only; actual viewed pages separately recorded in qa/visual-review.json',pdfs=out)
 (MAPS/'qa/pdf-render.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(dict(originals=len(out),pages=result['pages'])))
if __name__=='__main__':main()
