"""Complete-original page layout inventory cards, not numeric transcription aids."""
import io,json,math
import fitz
from PIL import Image,ImageOps,ImageDraw
from sources import OUT,BASE,sha,save,original
CW,CH,COLS,ROWS=210,174,10,8
def main():
 inv=json.loads((OUT/'printed-control-page-inventory.json').read_text());folder=OUT/'qa/source-page-scope';folder.mkdir(exist_ok=True);records=[]
 for year in ['2018','2020','2024']:
  slots=[];batch=0
  def flush():
   nonlocal slots,batch
   if not slots:return
   batch+=1;canvas=Image.new('RGB',(CW*COLS,CH*ROWS),'white');draw=ImageDraw.Draw(canvas);pages=[]
   for i,(im,q) in enumerate(slots):
    x=(i%COLS)*CW;y=(i//COLS)*CH;canvas.paste(im,(x+(CW-im.width)//2,y+20));draw.text((x+3,y+2),q['short_label'],fill='black');q['atlas_slot']=i+1;q['atlas_pixel_bounds']=[x,y,x+CW,y+CH];pages.append(q)
   p=folder/f'{year}-{batch:02d}.png';canvas.save(p);records.append(dict(path=str(p.relative_to(BASE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()),pages=pages));print(year,batch,len(pages),flush=True);slots=[]
  for s in inv['sources']:
   if s['source_id'].split('-')[1]!=year:continue
   raw=original(s['source_id']);h=sha(raw);doc=fitz.open(stream=raw,filetype='pdf');assert len(doc)==s['page_count']
   for q in s['pages']:
    assert q['source_raw_sha256']==h;p=doc[q['PDFpage']-1];pm=p.get_pixmap(matrix=fitz.Matrix(.45,.45),colorspace=fitz.csGRAY);im=Image.frombytes('L',[pm.width,pm.height],pm.samples)
    rot=q.get('rotation_ccw') or 0
    if rot:im=im.rotate(rot,expand=True,fillcolor='white')
    im.thumbnail((CW-6,CH-24));label=s['source_id'].replace('sos-','').replace('-county-','-').replace('-runoff-','-R-')
    slots.append((im,dict(source_id=s['source_id'],source_raw_sha256=h,PDFpage=q['PDFpage'],short_label=label+':'+str(q['PDFpage']),display_rotation_ccw=rot,locator_path=q['locator_path'],qualification='Complete unchanged source raster downsampled/rotated for packet-layout inventory only; source glyph values require full originals.')))
    if len(slots)==COLS*ROWS:flush()
   doc.close()
  flush()
 save(OUT/'source/original-page-scope-overviews.json',dict(page_count=sum(len(r['pages']) for r in records),source_count=inv['source_documents'],atlases=records,qualification='All3238 actual retained county PDF pages independently rasterized from hashchecked original bytes. Downsampled layout overview complements complete-original candidate/control readings and machine locators; no additional office or demographic values transcribed, no missing fields invented.'))
if __name__=='__main__':main()
