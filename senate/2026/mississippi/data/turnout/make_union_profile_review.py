"""Original-only profile reading cards; no OCR values drawn on source images."""
import gzip,io,json
import fitz
from PIL import Image,ImageDraw
from acquire_sources import BASE,OUT,receipts,sha,savejson

def main():
 sid='sos-2024-county-union';r=next(r for r in receipts if r['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf')
 dest=OUT/'qa/union-profiles';dest.mkdir(exist_ok=True);cards=[]
 for n in range(16,56,2):
  page=doc[n-1];im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(3.5,3.5),colorspace=fitz.csGRAY).tobytes('png')));full=dest/f'original-p{n}.png';im.save(full)
  box=[70,285,795,1900];crop=im.crop(box);canvas=Image.new('RGB',(725,1645),'white');canvas.paste(crop,(0,30));ImageDraw.Draw(canvas).text((5,5),f'UNALTERED ORIGINAL Union PDF p{n}; 3.5x',fill='black');cards.append(canvas)
  savejson(dest/f'original-p{n}-pointer.json',dict(source_id=sid,raw_sha256=r['raw_sha256'],source_page=n,render_scale=3.5,render_size=list(im.size),crop_bounds=box,original_render_path=str(full.relative_to(BASE)),render_sha256=sha(full.read_bytes())))
 for i in range(0,20,4):
  canvas=Image.new('RGB',(2900,1645),'white')
  for j,im in enumerate(cards[i:i+4]):canvas.paste(im,(725*j,0))
  canvas.save(dest/f'review-{i//4+1}.png')
 print('20 original profiles; five original-only review panels')
if __name__=='__main__':main()
