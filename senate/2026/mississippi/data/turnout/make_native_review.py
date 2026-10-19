"""Original-byte native header/Senate mosaics for human review, never new data."""
import argparse,gzip,json,io
from pathlib import Path
import fitz,numpy as np
from PIL import Image,ImageOps,ImageDraw
from acquire_sources import BASE,OUT,receipts,sha

def tidy(crop,target):
 im=ImageOps.autocontrast(crop);a=np.array(im);ys,xs=np.nonzero(a<140)
 if len(xs):im=im.crop((max(0,int(xs.min())-2),max(0,int(ys.min())-2),min(im.width,int(xs.max())+3),min(im.height,int(ys.max())+3)))
 im.thumbnail(target);return im

def run(sid):
 p=OUT/'extracts'/f'{sid}-native-grid-v5.json.gz'
 if not p.exists():return
 d=json.loads(gzip.decompress(p.read_bytes()));r=next(x for x in receipts if x['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');out=[]
 for pg in d['pages']:
  if not pg.get('columns'):continue
  src=doc[pg['page']-1];scale=min(2.5,3300/max(src.rect.width,src.rect.height));im=Image.open(io.BytesIO(src.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png'))).rotate(pg['rotation_ccw'],expand=True).rotate(pg.get('deskew_angle_ccw') or 0,fillcolor=255)
  canvas=Image.new('RGB',(1100,44+len(pg['columns'])*58),'white');dr=ImageDraw.Draw(canvas);dr.text((8,5),f'{sid} ORIGINAL p{pg["page"]}; source column / header / Pinkins / Wicker',fill='black')
  for i,c in enumerate(pg['columns']):
   y=40+i*58;dr.text((5,y+10),str(c['source_column']),fill='black');box=c['header_box'];lab=im.crop(box).rotate(-90,expand=True);lab=tidy(lab,(620,50));canvas.paste(lab,(45,y))
   for j,name in enumerate(['Ty Pinkins','Roger F. Wicker']):
    cell=c['votes'].get(name)
    if cell and cell.get('box'):
     box=cell['box'];v=im.crop(box);v=tidy(v,(170,50));canvas.paste(v,(710+j*190,y))
  q=OUT/'qa/native-review'/f'{sid}-p{pg["page"]:02d}.png';q.parent.mkdir(exist_ok=True);canvas.save(q);out.append(str(q.relative_to(BASE)))
 return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('counties',nargs='+');a=ap.parse_args()
 for county in a.counties:print(county,run('sos-2024-county-'+county))
