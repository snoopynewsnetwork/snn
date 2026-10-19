"""Independent whole-raster Vision at shared positions only; no peer votes/labels.

Source boxes are a targeting aid. Preserve geometry/version disagreements and
never assume the same ordinal identifies the same printed column.
"""
import concurrent.futures,gzip,io,json,subprocess
import fitz
from PIL import Image
from sources import *
def hints():
 dest=OUT/'source/native-2024-layout-hints-v2.json.gz'
 if dest.exists():return json.loads(gzip.decompress(dest.read_bytes()))
 result=[]
 for path in sorted((BASE/'data/turnout/extracts').glob('*-native-grid-v5.json.gz')):
  raw=path.read_bytes();x=json.loads(gzip.decompress(raw));pages=[]
  for p in x['pages']:
   pages.append(dict(page=p['page'],render_size=p.get('render_size'),rotation_ccw=p.get('rotation_ccw'),deskew_angle_ccw=p.get('deskew_angle_ccw'),columns=[dict(source_column=c['source_column'],header_box=c.get('header_box'),candidate_boxes={n:z.get('box') for n,z in c.get('votes',{}).items()}) for c in p.get('columns',[])]))
  result.append(dict(source_id=x['source_id'],raw_sha256=x['raw_sha256'],layout_reference=str(path.relative_to(BASE)),layout_reference_stored_sha256=sha(raw),pages=pages,qualification='Only source ID/hash/page/transform/bounds imported. No peer labels/numbers/OCR imported.'))
 dest.write_bytes(gzip.compress(json.dumps(result).encode(),mtime=0));return result

def read(r):
 dest=OUT/'extracts/vision-layout'/r['source_id'];dest.mkdir(parents=True,exist_ok=True);doc=fitz.open(stream=original(r['source_id']),filetype='pdf');pages=[]
 for p in r['pages']:
  if not p['columns']:continue
  out=dest/f'p{p["page"]:04d}.json.gz'
  if out.exists():continue
  rw,rh=p['render_size'];rot=p['rotation_ccw'];page=doc[p['page']-1];scale=(rh if rot in [90,-90,270] else rw)/page.rect.width
  im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png'))).rotate(rot,expand=True).rotate(p['deskew_angle_ccw'],fillcolor=255)
  assert abs(im.width-rw)<=1 and abs(im.height-rh)<=1
  png=dest/f'p{p["page"]:04d}.png';im.save(str(png));result=subprocess.run([str(OUT/'qa/vision-ocr'),str(png)],capture_output=True,check=True,text=True);v=json.loads(result.stdout)
  v.update(source_id=r['source_id'],raw_sha256=r['raw_sha256'],page=p['page'],render_size=list(im.size),rotation_ccw=rot,deskew_angle_ccw=p['deskew_angle_ccw'],layout_reference=r['layout_reference'],layout_reference_stored_sha256=r['layout_reference_stored_sha256'],source_position_columns=p['columns'],raster_path=str(png.relative_to(BASE)),raster_sha256=sha(png.read_bytes()),qualification='Independent whole original raster OCR. Shared boxes only; source raw hash verified. No peer values imported, unresolved not zero.')
  out.write_bytes(gzip.compress(json.dumps(v,ensure_ascii=False).encode(),mtime=0));print(r['source_id'],p['page'],len(v['words']),flush=True)
 return r['source_id']
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for x in pool.map(read,hints()):print(x,flush=True)
