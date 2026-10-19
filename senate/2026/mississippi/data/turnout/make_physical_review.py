"""Original-only visual mosaics at detected physical grid positions, no values."""
import argparse,gzip,io,json
import fitz
from PIL import Image,ImageDraw
from acquire_sources import BASE,OUT,receipts,sha
from make_native_review import tidy
def run(sid,pg):
 ref=BASE/f'data/baselines/extracts/native-v4/{sid}/p{pg:04d}.json.gz';g=json.loads(gzip.decompress(ref.read_bytes()));xs=g['grid_x'][1:]
 ledger=OUT/'native-reviewed-2024.json'
 if ledger.exists():
  s=json.loads(ledger.read_text())['sources'].get(sid,{})
  p=next((x for x in s.get('pages',[]) if x['page']==pg),{})
  xs=p.get('explicit_numeric_grid_x',xs)
 if len(xs)!=12 and len(g['grid_x'])==12 and g['grid_x'][0]>.25*g['render_size'][0]:xs=g['grid_x']
 assert len(xs)==12
 r=next(x for x in receipts if x['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==g['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');im=Image.open(io.BytesIO(doc[pg-1].get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(g['rotation_ccw'],expand=True).rotate(g.get('deskew_angle_ccw',0),fillcolor=255);ff={f['field']:f for f in g['fields']};hy=g['columns'][0]['bounds'][1::2]
 canvas=Image.new('RGB',(1300,880),'white');dr=ImageDraw.Draw(canvas);dr.text((8,5),f'{sid} ORIGINAL p{pg}; physical source column / header / Pinkins / Wicker',fill='black')
 for i,(a,b) in enumerate(zip(xs,xs[1:]),1):
  y=40+(i-1)*75;dr.text((5,y+10),str(i),fill='black');lab=tidy(im.crop((a,hy[0],b,hy[1])).rotate(-90,expand=True),(780,65));canvas.paste(lab,(45,y))
  for j,name in enumerate(['Ty Pinkins','Roger F. Wicker']):
   f=ff[name];crop=tidy(im.crop((a,f['row_bounds'][1],b,f['row_bounds'][3])),(180,65));canvas.paste(crop,(850+j*210,y))
 dest=OUT/'qa/native-review'/f'{sid}-p{pg:02d}-physical.png';canvas.save(dest);print(dest)
 im.save(OUT/'qa'/f'{sid}-verified-physical-p{pg}.png')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('county');ap.add_argument('pages',type=int,nargs='+');a=ap.parse_args()
 for pg in a.pages:run('sos-2024-county-'+a.county,pg)
