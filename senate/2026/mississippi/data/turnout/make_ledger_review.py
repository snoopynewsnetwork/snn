"""Render independently retained original bytes at exact accepted ledger transforms."""
import argparse,io,gzip,json
import fitz
from PIL import Image,ImageDraw
from acquire_sources import OUT,BASE,receipts,sha
from make_native_review import tidy

def run(sid,pg):
 d=json.loads((OUT/'native-reviewed-2024.json').read_text());s=d['sources'][sid];p=next(p for p in s['pages'] if p['page']==pg);r=next(r for r in receipts if r['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==s['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');page=doc[pg-1]
 for scale in [min(2.5,3300/max(page.rect.width,page.rect.height)),2.7]:
  im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png'))).rotate(p['rotation_ccw'],expand=True).rotate(p['deskew_angle_ccw'] or 0,fillcolor=255)
  if list(im.size)==p['render_size']:break
 assert list(im.size)==p['render_size']
 canvas=Image.new('RGB',(1300,880),'white');dr=ImageDraw.Draw(canvas);dr.text((5,5),f'{sid} independently rendered ORIGINAL p{pg}; current accepted source boxes',fill='black')
 for i,c in enumerate(p['columns']):
  y=40+i*75;dr.text((5,y+10),str(c['source_column']),fill='black');canvas.paste(tidy(im.crop(c['header_bounds']).rotate(-90,expand=True),(780,65)),(45,y))
  for j,n in enumerate(['Ty Pinkins','Roger F. Wicker']):canvas.paste(tidy(im.crop(c['candidate_bounds'][n]),(180,65)),(850+j*210,y))
 path=OUT/'qa/native-review'/f'{sid}-p{pg:02d}-accepted-boxes.png';canvas.save(path);print(path)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('county');ap.add_argument('pages',nargs='+',type=int);a=ap.parse_args()
 for p in a.pages:run('sos-2024-county-'+a.county,p)
