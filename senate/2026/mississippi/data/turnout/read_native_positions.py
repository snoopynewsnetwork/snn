"""Independently read original PDF bytes at exchanged source-position bounds.

The peer file supplies geometry only, never numeric/label transcription. Preserve
its exact hash, source bounds and our independently OCR'd labels and cells. These
are reading aids until primary controls and direct page review close the scope.
"""
import argparse,concurrent.futures,csv,gzip,io,json,re,subprocess,tempfile
from pathlib import Path
import fitz,numpy as np
from PIL import Image,ImageOps,ImageDraw
from acquire_sources import BASE,OUT,receipts,sha
PEER=BASE/'data/baselines/extracts/native-v4'
def ocr(im,psm=6,numeric=False):
 with tempfile.TemporaryDirectory(prefix='ms-turnout-') as td:
  p=Path(td)/'crop.png';im.save(p)
  args=['tesseract',str(p),'stdout','--psm',str(psm)]
  if numeric:args+=['-c','tessedit_char_whitelist=0123456789,']
  args+=['tsv'];r=subprocess.run(args,capture_output=True,check=True)
  t=r.stdout.decode();tokens=[x for x in csv.DictReader(io.StringIO(t),delimiter='\t',quoting=csv.QUOTE_NONE) if x.get('text','').strip()]
  return t,tokens
def clean(im):
 a=np.array(im).copy();b=a<150
 # Only nearly continuous rules, no candidate-based correction or residuals.
 a[np.flatnonzero(b.sum(axis=1)>a.shape[1]*.72),:]=255
 a[:,np.flatnonzero(b.sum(axis=0)>a.shape[0]*.72)]=255
 return ImageOps.autocontrast(Image.fromarray(a))
def montage(crops,numeric):
 step=90 if numeric else 110;width=420 if numeric else 760
 canvas=Image.new('L',(width,step*len(crops)),255)
 for i,crop in enumerate(crops):
  im=clean(crop)
  if numeric:
   im=im.crop((3,3,max(4,im.width-3),max(4,im.height-3)))
   a=np.array(im);ys,xs=np.nonzero(a<145)
   if len(xs):im=im.crop((max(0,int(xs.min())-2),max(0,int(ys.min())-2),min(im.width,int(xs.max())+3),min(im.height,int(ys.max())+3)))
  im.thumbnail((width-40,step-24))
  if im.width<width-40 and im.height<step-24:
   scale=min((width-40)/im.width,(step-24)/im.height)
   im=im.resize((round(im.width*scale),round(im.height*scale)))
  canvas.paste(im,(20,i*step+12))
 t,tt=ocr(canvas,6,numeric);rows=[]
 for i in range(len(crops)):
  a=[x for x in tt if i*step<=int(x['top'])+int(x['height'])/2<(i+1)*step]
  s=' '.join(x['text'] for x in sorted(a,key=lambda x:int(x['left'])));v=s.replace(',','').replace(' ','')
  rows.append(dict(raw_ocr=s,value=int(v) if numeric and v.isdigit() else None,tokens=a))
 return rows,t,canvas

def run(sid):
 target=OUT/'extracts/independent-position-cells-v2'/f'{sid}.json.gz';target.parent.mkdir(exist_ok=True)
 if target.exists():return sid,'cached'
 r=next(r for r in receipts if r['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];d=fitz.open(stream=raw,filetype='pdf');pages=[]
 for path in sorted((PEER/sid).glob('p*.json.gz')):
  geometrybytes=path.read_bytes();g=json.loads(gzip.decompress(geometrybytes))
  if not g.get('fields'):continue
  assert g['raw_sha256']==r['raw_sha256']
  p=d[g['page']-1];im=Image.open(io.BytesIO(p.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png')))
  im=im.rotate(g['rotation_ccw'],expand=True).rotate(g.get('deskew_angle_ccw',0),fillcolor=255)
  assert list(im.size)==g['render_size'],(sid,g['page'],im.size,g['render_size'])
  fields=[];crops=[];positions=[];labelcrops=[]
  for j,f in enumerate(g['fields']):
   rowbox=f['row_bounds'];left=min(c['bounds'][0] for c in f['cells']) if f['cells'] else im.width
   labelcrops.append(im.crop((max(0,rowbox[0]),rowbox[1],left,rowbox[3])))
   fields.append(dict(source_row=f['source_row'],row_bounds=rowbox,cells=[]))
   for c in f['cells']:
    crops.append(im.crop(tuple(c['bounds'])));positions.append((j,c['source_column'],c['bounds']))
  vals=[];tsvs=[]
  for start in range(0,len(crops),22):
   vv,tt,canvas=montage(crops[start:start+22],True);vals.extend(vv);tsvs.append(tt)
  tsv=tsvs;labels,ltsv,lcanvas=montage(labelcrops,False)
  for f,label in zip(fields,labels):f['source_row_label_ocr']=label['raw_ocr']
  for (j,col,box),v in zip(positions,vals):fields[j]['cells'].append(dict(source_column=col,bounds=box,**v))
  hcrops=[im.crop(tuple(c['bounds'])).rotate(-90,expand=True) for c in g['columns']]
  if hcrops:
   hdr,htsv,hcanvas=montage(hcrops,False)
   cols=[dict(source_column=c['source_column'],bounds=c['bounds'],own_label_ocr=v['raw_ocr']) for c,v in zip(g['columns'],hdr)]
  else:cols=[];htsv=''
  pages.append(dict(page=g['page'],source_rect=list(p.rect),source_pdf_rotation=p.rotation,rotation_ccw=g['rotation_ccw'],deskew_angle_ccw=g.get('deskew_angle_ccw',0),render_size=list(im.size),geometry_reference_path=str(path.relative_to(BASE)),geometry_stored_sha256=sha(geometrybytes),columns=cols,fields=fields,numeric_ocr_tsv=tsv,row_label_ocr_tsv=ltsv,header_ocr_tsv=htsv))
 target.write_bytes(gzip.compress(json.dumps(dict(source_id=sid,raw_sha256=r['raw_sha256'],parser='independent-turnout-position-reader-1',qualification='Peer geometry only; labels and numeric cells independently read from original bytes. Unreviewed OCR is not accepted transcription.',pages=pages),ensure_ascii=False).encode(),mtime=0))
 return sid,len(pages),sum(len(f['cells']) for p in pages for f in p['fields'])
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prefix',default='sos-2024-county-');ap.add_argument('--only');ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args()
 ids=[r['id'] for r in receipts if r['id'].startswith(a.prefix) and (PEER/r['id']).exists() and (not a.only or r['id'].endswith(a.only))]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
  for x in pool.map(run,ids):print(*x,flush=True)
