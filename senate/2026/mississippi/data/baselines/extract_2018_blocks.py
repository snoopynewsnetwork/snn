"""Original-source 2018 candidate blocks and printed TOTAL reading aids.

Recover missing label detections by adjacent *physical row* candidates, with
fresh original-label OCR retained for review. No vote residual allocation.
"""
import argparse,concurrent.futures,gzip,io,json,re
from collections import Counter
import fitz,numpy as np
from PIL import Image,ImageDraw,ImageOps
from sources import *
from extract_native import ocr
NAMES={'special':['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],'runoff':['Mike Espy','Cindy Hyde-Smith']}
def read(r):
 key=r['id'];stage='runoff' if '-runoff-' in key else 'special';names=NAMES[stage];dest=OUT/'extracts/2018-blocks'/f'{key}.json.gz';dest.parent.mkdir(exist_ok=True)
 if dest.exists():return key,'cached'
 doc=fitz.open(stream=original(key),filetype='pdf');pages=[]
 for path in sorted((OUT/'extracts/native-v4'/key).glob('*.gz')):
  x=json.loads(gzip.decompress(path.read_bytes()));ff=[f for f in x.get('fields',[]) if f['field'] in names and (f['field']!='Chris McDaniel' or 'chris' in f['label_ocr'].lower())]
  if not ff or not x.get('columns'):continue
  offsets=Counter(f['source_row']-1-names.index(f['field']) for f in ff);start=offsets.most_common(1)[0][0];ys=x['grid_y'];w,h=x['render_size']
  if start+len(names)>=len(ys):continue
  page=doc[x['page']-1];im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(x['rotation_ccw'],expand=True).rotate(x['deskew_angle_ccw'],fillcolor=255)
  xs=x['grid_x'];candidates=[z for i,z in enumerate(xs) if i and .23*w<z<.42*w and z-xs[i-1]>250];split=candidates[0] if candidates else x['columns'][0]['bounds'][0]
  cols=[z for z in xs if z>=split-3];header=x['columns'][0]['bounds'][1::2];columns=[]
  for c,(l,rgt) in enumerate(zip(cols,cols[1:]),1):
   box=[l,header[0],rgt,header[1]];lab=ocr(im.crop(tuple(box)).rotate(270,expand=True),6).strip()
   columns.append(dict(source_column=c,header_box=box,native_label_ocr=lab,unit_type='summary_TOTAL' if re.search(r'\btotal\b',lab,re.I) else 'unreviewed_source_column'))
  fields=[]
  for j,name in enumerate(names):
   top,bottom=ys[start+j:start+j+2];labelbox=[0,top,split,bottom];label=ocr(im.crop(tuple(labelbox)),6).strip();tiles=[]
   for l,rgt in zip(cols,cols[1:]):
    a=np.array(im.crop((l,top,rgt,bottom)));dark=a<220;a[:,dark.sum(axis=0)>.82*a.shape[0]]=255;a[dark.sum(axis=1)>.82*a.shape[1],:]=255
    tiles.append(ImageOps.expand(Image.fromarray(a),12,255))
   tw=max(t.width for t in tiles)+20;th=max(t.height for t in tiles)+20;montage=Image.new('L',(tw,th*len(tiles)),255)
   for k,t in enumerate(tiles):montage.paste(t,(10,k*th+10))
   from extract_native import words
   ww=words(ocr(montage,6,True,True));cells=[]
   for k,(l,rgt) in enumerate(zip(cols,cols[1:]),1):
    literal=' '.join(z['text'] for z in ww if (k-1)*th<=int(z['top'])+int(z['height'])/2<k*th);num=literal.replace(' ','').replace(',','');value=int(num) if re.fullmatch(r'\d+',num) else None
    cells.append(dict(source_column=k,box=[l,top,rgt,bottom],raw_ocr=literal,value=value))
   fields.append(dict(candidate=name,row_source_ordinal=start+j+1,label_box=labelbox,label_ocr=label,cells=cells))
  pages.append(dict(page=x['page'],render_size=x['render_size'],rotation_ccw=x['rotation_ccw'],deskew_angle_ccw=x['deskew_angle_ccw'],columns=columns,fields=fields,block_position_basis=dict(candidate_offsets=dict(offsets),selected_physical_start=start),qualification='Original numeric OCR plus adjacent-row position aids; fresh literal row-label OCR preserved; not yet accepted transcription.'))
 dest.write_bytes(gzip.compress(json.dumps(dict(source_id=key,raw_sha256=r['raw_sha256'],stage=stage,pages=pages),ensure_ascii=False).encode(),mtime=0));return key,len(pages)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--only');ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args();rr=[r for r in references().values() if re.match('sos-2018-(runoff-)?county-',r['id']) and 'pdf' in str(r.get('headers',{})).lower() and (not a.only or r['id']==a.only)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
  for result in pool.map(read,rr):print(*result,flush=True)
