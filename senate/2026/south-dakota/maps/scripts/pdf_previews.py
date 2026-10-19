"""Read-only Poppler inspection; originals reconstructed only in temporary storage.
Full-document text and every-page thumbnail/contact sheet, with selected complete
pages rendered large for actual visual inspection. No PDF authoring or repair.
"""
from common import *
import subprocess,tempfile,math
from PIL import Image,ImageOps,ImageDraw
def main():
 es=load('source/reused-receipts.json')+[json.loads(p.read_bytes()) for p in sorted((MAPS/'raw').glob('*.receipt.json'))];seen=set();out=[]
 old=load('qa/PDF-inspection.json') if (MAPS/'qa/PDF-inspection.json').exists() else []
 for e in es:
  # Mapbook originals plus worker-owned map/doc PDFs. Shared historical canvasses
  # and unrelated sample ballots are available by reference, not rendered as maps.
  if not (e['id'] in ['minnehaha-county-PDF','minnehaha-city-PDF'] or not e['id'].startswith(('peer-','minnehaha-','pennington-','lincoln-','census-','rapid-'))):continue
  b=original(e)
  if not b.startswith(b'%PDF') or sha(b) in seen:continue
  seen.add(sha(b));ident=e['id']
  previous=next((x for x in old if x['id']==ident and x['original_raw_sha256']==sha(b)),None)
  if previous and all((STATE/x['path']).exists() for x in previous['large_complete_page_renders']):out.append(previous);continue
  with tempfile.TemporaryDirectory(prefix='sd-map-pdf-') as t:
   t=Path(t);pdf=t/'original.pdf';pdf.write_bytes(b)
   info=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,check=True).stdout.decode();pages=int(next(l.split(':')[1].strip() for l in info.splitlines() if l.startswith('Pages:')))
   tx=subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,check=True)
   (MAPS/f'previews/{ident}.txt.gz').write_bytes(gzip.compress(tx.stdout,mtime=0))
   subprocess.run(['pdftoppm','-scale-to','500','-png',str(pdf),str(t/'thumb')],capture_output=True,check=True)
   imgs=sorted(t.glob('thumb-*.png'));assert len(imgs)==pages
   cols=4;rows=math.ceil(pages/cols);sheet=Image.new('RGB',(cols*330,rows*360),'white');draw=ImageDraw.Draw(sheet)
   for i,p in enumerate(imgs):
    im=Image.open(p).convert('RGB');im.thumbnail((312,325));x=(i%cols)*330+(330-im.width)//2;y=(i//cols)*360+20;sheet.paste(im,(x,y));draw.text(((i%cols)*330+8,(i//cols)*360+3),f'Original page {i+1}',fill='black')
   sheetpath=f'previews/{ident}-all-pages.png';sheet.save(MAPS/sheetpath,optimize=True)
   selected=sorted(set([1,pages] + ([min(12,pages)] if pages>2 else [])));renders=[]
   for pg in selected:
    prefix=t/f'large-{pg}'
    subprocess.run(['pdftoppm','-f',str(pg),'-l',str(pg),'-singlefile','-scale-to','1800','-png',str(pdf),str(prefix)],capture_output=True,check=True)
    dest=MAPS/f'previews/{ident}-page{pg:03}.png';dest.write_bytes(prefix.with_suffix('.png').read_bytes());renders.append(dict(physical_page=pg,path=str(dest.relative_to(STATE))))
   out.append(dict(id=ident,original_raw_sha256=sha(b),original_raw_bytes=len(b),pages=pages,pdfinfo=info,complete_text_path=f'maps/previews/{ident}.txt.gz',all_pages_contact_sheet='maps/'+sheetpath,large_complete_page_renders=renders,rendering_errors=tx.stderr.decode()))
   print(ident,pages,flush=True)
 dump('qa/PDF-inspection.json',out)
if __name__=='__main__':main()
