"""Independent physical-rule repair and two-engine cell comparison.

No vote is chosen to fit county controls. Conflicting numeric readings remain
unresolved; single-engine readings are explicitly qualified. Original row/header
boxes and all raw alternatives remain available for visual/peer review.
"""
import concurrent.futures,csv,gzip,json,re
from collections import defaultdict
import numpy as np
from PIL import Image
from sources import *
from extract_native import groups,ocr
from compile_vision_grid import pixels,PAT

def read(key):
 dest=OUT/'extracts/repaired-grid'/f'{key}.json.gz';dest.parent.mkdir(exist_ok=True)
 if dest.exists():return json.loads(gzip.decompress(dest.read_bytes()))
 directory=OUT/'extracts/vision-pages'/key;pages=[]
 for path in sorted(directory.glob('*.json.gz')):
  v=json.loads(gzip.decompress(path.read_bytes()));x=json.loads(gzip.decompress((OUT/'extracts/native-v4'/key/path.name).read_bytes()));w,h=v['render_size'];im=Image.open(BASE/v['raster_path']);a=np.array(im);cols=x.get('columns',[]);ys=x.get('grid_y',[])
  if cols:top,bottom=cols[0]['bounds'][1::2]
  else:
   bottom=next((y for y in ys if .25*h<y<.42*h),round(.3*h));top=next((y for y in reversed(ys) if y<bottom-70 and y>.08*h),round(.15*h))
  mask=a[top+5:bottom-5]<220
  if mask.shape[0]<30:continue
  mask=mask|np.roll(mask,1,axis=1)|np.roll(mask,-1,axis=1);runs=np.zeros(w,dtype=int);maxruns=runs.copy()
  for row in mask:runs=np.where(row,runs+1,0);maxruns=np.maximum(maxruns,runs)
  xs=groups(np.flatnonzero(maxruns>.60*len(mask)),5)
  if len(xs)<7:continue
  possibilities=[(xs[i]-xs[i-1],i) for i in range(1,len(xs)-5) if .20*w<xs[i]<.68*w]
  if not possibilities:continue
  gap,start=max(possibilities);bounds=xs[start:]
  if gap<2*np.median(np.diff(bounds)):continue
  anchors={}
  for name in ['Ty Pinkins','Roger F. Wicker']:
   hits=[]
   for z in v['observations']:
    box=pixels(z,w,h)
    if box[0]<bounds[0] and re.search(PAT[name],z['text'],re.I):hits.append((box,z['text']))
   if len(hits)==1:anchors[name]=hits[0]
  if len(anchors)!=2:continue
  columns=[]
  for ordinal,(l,r) in enumerate(zip(bounds,bounds[1:]),1):
   prior=next((c for c in cols if abs(c['bounds'][0]-l)<5 and abs(c['bounds'][2]-r)<5),None)
   header=prior['ocr_label'] if prior else ocr(im.crop((l,top,r,bottom)).rotate(270,expand=True),6).strip()
   typ='summary_TOTAL' if re.search(r'\btotal\b',header,re.I) else 'blank_or_unresolved_label' if not re.search('[A-Za-z0-9]',header) else 'source_native_label_OCR_pending_review';fields={}
   for name,(anchor,labeltext) in anchors.items():
    cy=(anchor[1]+anchor[3])/2;tokens=[]
    for z in v['words']:
     box=pixels(z,w,h);cx=(box[0]+box[2])/2;y=(box[1]+box[3])/2
     if l<cx<r and abs(y-cy)<max(16,.013*h):tokens.append(dict(text=z['text'],box=box,confidence=z['confidence']))
    literal=' '.join(z['text'] for z in sorted(tokens,key=lambda z:z['box'][0]));s=literal.replace(',','').strip();vv=int(s) if re.fullmatch(r'\d+',s) else None;old=[]
    for f in x['fields']:
     if f['field']!=name or abs((f['row_bounds'][1]+f['row_bounds'][3])/2-cy)>35:continue
     for c in f['cells']:
      if abs(c['bounds'][0]-l)<5 and abs(c['bounds'][2]-r)<5:old.append(c)
    tv=old[0]['value'] if len(old)==1 else None
    conflict=vv is not None and tv is not None and vv!=tv;value=None if conflict else vv if vv is not None else tv
    fields[name]=dict(value=value,status='conflicting_original_OCR_readings' if conflict else 'two_engine_agreement_pending_source_identity_review' if vv is not None and tv is not None else 'single_engine_pending_visual_review' if value is not None else 'unresolved',vision_value=vv,vision_literal=literal,vision_tokens=tokens,tesseract_readings=old,source_field_label=labeltext,field_label_box=anchor,cell_box=[l,cy-30,r,cy+30])
   columns.append(dict(source_column=ordinal,x_bounds=[l,r],header_box=[l,top,r,bottom],native_label_ocr=header,unit_type=typ,fields=fields))
  pages.append(dict(page=x['page'],render_size=[w,h],rotation_ccw=x['rotation_ccw'],deskew_angle_ccw=x['deskew_angle_ccw'],header_rule_x=xs,selected_split=bounds[0],split_basis='Boundary after widest observed header-rule gap with at least five further columns; physical-rule aid, not assumed eleven or name-based join.',columns=columns))
 result=dict(source_id=key,raw_sha256=sha(original(key)),pages=pages,qualification='Original physical geometry plus independent engine readings. No peer numeric import or control-fitted values. Not complete native acceptance.')
 dest.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False).encode(),mtime=0));return result

def main():
 keys=[p.name for p in (OUT/'extracts/vision-pages').iterdir() if p.name.startswith('sos-2024-')];county={r['county'].lower():r for r in csv.DictReader((BASE/'data/county-baselines.csv').open())};checks=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for x in pool.map(read,keys):
   key=x['source_id'];sums=defaultdict(int);miss=defaultdict(int);conf=defaultdict(int);n=0;statuses=defaultdict(int)
   for p in x['pages']:
    for c in p['columns']:
     if c['unit_type'] in ['summary_TOTAL','blank_or_unresolved_label']:continue
     n+=1
     for name,f in c['fields'].items():
      statuses[f['status']]+=1
      if f['value'] is None:miss[name]+=1
      else:sums[name]+=f['value']
      if f['status'].startswith('conflicting'):conf[name]+=1
   label=key.removeprefix('sos-2024-county-').removesuffix('-updated').replace('-',' ');r=county.get(label)
   if not r:continue
   ex={n:int(r['2024-senate_'+role]) for n,role in [('Ty Pinkins','A'),('Roger F. Wicker','B')]}
   if key=='sos-2024-county-pike':ex={'Ty Pinkins':5898,'Roger F. Wicker':6719}
   rec=dict(source_id=key,native_labeled_positions=n,numeric_sums=dict(sums),unresolved=dict(miss),conflicts=dict(conf),differences={n:sums[n]-ex[n] for n in ex},statuses=dict(statuses));checks.append(rec);print(key,n,rec['differences'],rec['unresolved'],flush=True)
 save(OUT/'repaired-grid-checks.json',checks)
if __name__=='__main__':main()
