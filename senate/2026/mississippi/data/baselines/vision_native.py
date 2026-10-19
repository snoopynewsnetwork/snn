"""Second offline OCR engine on original PDF rasters, preserving every position.

Vision and Tesseract readings are independent; neither replaces the primary
original or candidate/geography/denominator reconciliation.
"""
import argparse,concurrent.futures,gzip,io,json,re,subprocess
import fitz
from PIL import Image
from sources import *
def read(r):
 key=r['id'];dest=OUT/'extracts/vision-pages'/key;dest.mkdir(parents=True,exist_ok=True);pages=[]
 for path in sorted((OUT/'extracts/native-v4'/key).glob('*.gz')):
  x=json.loads(gzip.decompress(path.read_bytes()));names=['Ty Pinkins','Roger F. Wicker'] if '-2024-' in key else ['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards'] if '-2020-' in key else ['Mike Espy','Cindy Hyde-Smith','Tobey Bernard Bartee','Chris McDaniel']
  located=any(f['field'] in names and (f['field']!='Chris McDaniel' or 'chris' in f['label_ocr'].lower()) for f in x.get('fields',[]))
  # A failed grid/row parser does not imply the requested contest is absent.
  # Inspect independent whole-page keyword evidence too, retaining a following
  # page for a garbled tail. No unrelated-office numeric table is extracted.
  rawtext=x.get('probe_text','')+' '+x.get('full_ocr_tsv','')+' '+x.get('pdf_text','')
  pattern=r'espy|hyde.?smith|jimmy' if '-2020-' in key or '-2018-' in key else r'pinkins|wicker'
  if located or re.search(pattern,rawtext,re.I):pages.append(x['page'])
 if not pages:pages=[2,3]
 # All preceding pages and one following page repair failed label/grid detection.
 end=max(pages)+1;doc=fitz.open(stream=original(key),filetype='pdf');end=min(len(doc),end)
 for pg in range(1 if 1 in pages else 2,end+1):
  out=dest/f'p{pg:04d}.json.gz'
  if out.exists():continue
  x=json.loads(gzip.decompress((OUT/'extracts/native-v4'/key/f'p{pg:04d}.json.gz').read_bytes()));page=doc[pg-1];im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(x['rotation_ccw'],expand=True).rotate(x['deskew_angle_ccw'],fillcolor=255)
  png=dest/f'p{pg:04d}.png';im.save(str(png));raw=png.read_bytes()
  result=subprocess.run([str(OUT/'qa/vision-ocr'),str(png)],capture_output=True,check=True,text=True);z=json.loads(result.stdout)
  z.update(source_id=key,source_raw_sha256=r['raw_sha256'],page=pg,render_size=list(im.size),rotation_ccw=x['rotation_ccw'],deskew_angle_ccw=x['deskew_angle_ccw'],raster_path=str(png.relative_to(BASE)),raster_sha256=sha(raw),raster_bytes=len(raw),engine='Apple Vision accurate en-US; usesLanguageCorrection=false',script_sha256=sha((OUT/'vision_ocr.swift').read_bytes()),qualification='Independent OCR aid, not accepted candidate/native transcription; unresolved never zero.')
  out.write_bytes(gzip.compress(json.dumps(z,ensure_ascii=False).encode(),mtime=0));print(key,pg,len(z['words']),flush=True)
 return key,end
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prefix',default='sos-2024-');ap.add_argument('--only');ap.add_argument('--jobs',type=int,default=2);a=ap.parse_args();rr=[r for r in references().values() if r['id'].startswith(a.prefix) and re.match(r'sos-(2018|2020|2024)-(runoff-)?county-',r['id']) and 'pdf' in str(r.get('headers',{})).lower() and (not a.only or r['id']==a.only)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
  for x in pool.map(read,rr):print(x,flush=True)
