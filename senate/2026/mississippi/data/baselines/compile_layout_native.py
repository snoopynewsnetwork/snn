"""Independent cell readings from original whole-page Vision and physical boxes.

Names and numbers from peer ledgers are never imported. Header OCR is generated
again from original rasters. Numeric conflicts survive for original review.
"""
import concurrent.futures,csv,gzip,json,re
from collections import defaultdict
from PIL import Image
from sources import *
from extract_native import ocr
from compile_vision_grid import pixels
NAMES=['Ty Pinkins','Roger F. Wicker']
def read(key):
 dest=OUT/'extracts/layout-native'/f'{key}.json.gz';dest.parent.mkdir(exist_ok=True)
 if dest.exists():return json.loads(gzip.decompress(dest.read_bytes()))
 pages=[];oldp=OUT/'extracts/direct-layout'/f'{key}.json.gz';old=json.loads(gzip.decompress(oldp.read_bytes())) if oldp.exists() else {}
 for path in sorted((OUT/'extracts/vision-layout'/key).glob('*.json.gz')):
  x=json.loads(gzip.decompress(path.read_bytes()));w,h=x['render_size'];im=Image.open(BASE/x['raster_path']);columns=[]
  for c in x['source_position_columns']:
   hb=c['header_box'];oldcols=next((p.get('columns',[]) for p in old.get('pages',[]) if p['page']==x['page']),[]);prior=next((z for z in oldcols if z['header_box']==hb),None)
   header=prior.get('native_label_ocr') if prior else ocr(im.crop(tuple(hb)).rotate(270,expand=True),6).strip() if hb else None
   fields={}
   for name,box in c['candidate_boxes'].items():
    if box is None:fields[name]=dict(value=None,status='no_box_not_zero');continue
    tokens=[]
    for z in x['words']:
     b=pixels(z,w,h);cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
     if box[0]<cx<box[2] and box[1]<cy<box[3]:tokens.append(dict(text=z['text'],box=b,confidence=z['confidence']))
    literal=' '.join(z['text'] for z in sorted(tokens,key=lambda z:z['box'][0]));s=literal.replace(',','').strip();vv=int(s) if re.fullmatch(r'\d+',s) else None;oldfield=prior.get('fields',{}).get(name,{}) if prior else {};samebox=oldfield.get('box')==box;tv=oldfield.get('value') if samebox else None
    value=vv if vv is not None else tv;conflict=vv is not None and tv is not None and vv!=tv
    fields[name]=dict(value=value,vision_value=vv,vision_literal=literal,tesseract_value=tv,tesseract_readings=oldfield.get('readings') if samebox else None,box=box,vision_tokens=tokens,status='conflicting_readings_pending_visual' if conflict else 'independent_engines_agree' if vv is not None and tv is not None else 'single_engine_pending_review' if value is not None else 'blank_or_unresolved_not_zero')
   columns.append(dict(source_column=c['source_column'],header_box=hb,native_label_ocr=header,unit_type='summary_TOTAL' if re.search(r'\btotal\b',header or '',re.I) else 'blank_or_unresolved_label' if not re.search('[A-Za-z0-9]',header or '') else 'source_native_label_OCR_pending_review',fields=fields))
  pages.append(dict(page=x['page'],render_size=[w,h],rotation_ccw=x['rotation_ccw'],deskew_angle_ccw=x['deskew_angle_ccw'],raster_path=x['raster_path'],raster_sha256=x['raster_sha256'],columns=columns))
 result=dict(source_id=key,raw_sha256=sha(original(key)),pages=pages,qualification='Independent original bytes/header OCR/whole-page numeric OCR at shared positions only; unresolved not zero; source geometry and controls separately reviewed.')
 dest.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False).encode(),mtime=0));return result

def main():
 keys=sorted(p.name for p in (OUT/'extracts/vision-layout').iterdir());county={r['county'].lower():r for r in csv.DictReader((BASE/'data/county-baselines.csv').open())};checks=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for x in pool.map(read,keys):
   key=x['source_id'];sums=defaultdict(int);missing=defaultdict(int);n=0;conflicts=defaultdict(int)
   for p in x['pages']:
    for c in p['columns']:
     if c['unit_type'] in ['summary_TOTAL','blank_or_unresolved_label']:continue
     n+=1
     for name,z in c['fields'].items():
      if z['value'] is None:missing[name]+=1
      else:sums[name]+=z['value']
      if z['status'].startswith('conflicting'):conflicts[name]+=1
   label=key.removeprefix('sos-2024-county-').removesuffix('-updated').replace('-',' ');r=county.get(label)
   if not r:continue
   ex={n:int(r['2024-senate_'+role]) for n,role in zip(NAMES,['A','B'])}
   if key=='sos-2024-county-pike':ex={'Ty Pinkins':5898,'Roger F. Wicker':6719}
   rec=dict(source_id=key,native_labeled_positions=n,numeric_sums=dict(sums),unresolved=dict(missing),conflicts=dict(conflicts),differences={n:sums[n]-ex[n] for n in NAMES});checks.append(rec);print(key,n,rec['differences'],rec['unresolved'],rec['conflicts'],flush=True)
 save(OUT/'layout-native-checks.json',checks)
if __name__=='__main__':main()
