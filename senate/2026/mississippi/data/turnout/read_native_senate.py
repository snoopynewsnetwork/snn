"""Independent per-cell original Senate reads at shared pixel bounds.

This reader uses source positions only. Re-extracted values are never fitted to
county totals. Row labels and full-source originals remain separate evidence.
"""
import argparse,concurrent.futures,gzip,io,json,re
from pathlib import Path
import fitz
from PIL import Image
from acquire_sources import BASE,OUT,receipts,sha
from extract_grid import cellnumber
PEER=BASE/'data/baselines/extracts/native-v4'
def allowed(sid,f):
 name=f.get('field','')
 if '2024' in sid:return name in ['Ty Pinkins','Roger F. Wicker']
 if '2018-runoff' in sid:return name in ['Mike Espy','Cindy Hyde-Smith']
 if '2018-county' in sid:return name in ['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel']
 return name in ['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
def run(sid):
 target=OUT/'extracts/independent-senate-cells'/f'{sid}.json.gz';target.parent.mkdir(exist_ok=True)
 if target.exists():return sid,'cached'
 r=next(r for r in receipts if r['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];d=fitz.open(stream=raw,filetype='pdf');pages=[]
 for path in sorted((PEER/sid).glob('p*.json.gz')):
  gb=path.read_bytes();g=json.loads(gzip.decompress(gb));selected=[f for f in g.get('fields',[]) if allowed(sid,f)]
  if not selected:continue
  assert g['raw_sha256']==r['raw_sha256'];page=d[g['page']-1]
  im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(g['rotation_ccw'],expand=True).rotate(g.get('deskew_angle_ccw',0),fillcolor=255)
  assert list(im.size)==g['render_size']
  fields=[]
  for f in selected:
   cells=[]
   for c in f['cells']:
    x0,y0,x1,y1=c['bounds'];box=[max(0,x0-2),max(0,y0),min(im.width,x1+4),min(im.height,y1+1)]
    v=cellnumber(im.crop(box));cells.append(dict(source_column=c['source_column'],reference_bounds=c['bounds'],read_bounds=box,**v))
   fields.append(dict(source_row=f['source_row'],field_position_hint=f['field'],office_context_position_hint=f['office_context_ocr'],row_bounds=f['row_bounds'],cells=cells))
  pages.append(dict(page=g['page'],source_rect=list(page.rect),rotation_ccw=g['rotation_ccw'],deskew_angle_ccw=g.get('deskew_angle_ccw',0),render_size=list(im.size),geometry_reference_path=str(path.relative_to(BASE)),geometry_stored_sha256=sha(gb),fields=fields))
 target.write_bytes(gzip.compress(json.dumps(dict(source_id=sid,raw_sha256=r['raw_sha256'],parser='turnout-individual-original-cell-1',qualification='Independent original-cell OCR reading aid using exchanged geometry only; named/office hints require original-row validation. No peer numeric values or labels copied; no fitting to totals.',pages=pages),ensure_ascii=False).encode(),mtime=0))
 return sid,len(pages),sum(len(f['cells']) for p in pages for f in p['fields'])
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prefix',default='sos-2024-county-');ap.add_argument('--only');ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args()
 ids=[r['id'] for r in receipts if r['id'].startswith(a.prefix) and (PEER/r['id']).exists() and (not a.only or r['id'].endswith(a.only))]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
  for x in pool.map(run,ids):print(*x,flush=True)
