"""Independent physical-grid reading aid, retaining every position and ambiguity.

Uses exchanged original-page geometry, never exchanged numeric transcription.
Restores missing rules only as explicitly marked geometry hypotheses. Candidate
rows interpolated only when at least two ordered anchors have identical grid
offsets. All readings remain unaccepted until source/county/native QA closes.
"""
import argparse, concurrent.futures, csv, gzip, io, json, statistics
import fitz
import numpy as np
from PIL import Image,ImageOps
from acquire_sources import BASE, OUT, receipts, sha
from read_native_positions import montage,ocr

PEER=BASE/'data/baselines/extracts/native-v4'
SEN24=['Ty Pinkins','Roger F. Wicker']
PRES24=['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump','Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski']
SPECIAL=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel']

def original_size_numbers(crops):
 # Preserve complete cell interiors and native digit size. No cell-edge crop,
 # resampling, bounding-box shrink or number-dependent preprocessing.
 tiles=[]
 for crop in crops:
  a=np.array(crop).copy();dark=a<230
  a[:,dark.sum(axis=0)>a.shape[0]*.8]=255
  a[dark.sum(axis=1)>a.shape[1]*.8,:]=255
  tiles.append(ImageOps.expand(Image.fromarray(a),border=16,fill=255))
 step=max(t.height for t in tiles)+28;width=max(t.width for t in tiles)+32
 canvas=Image.new('L',(width,step*len(tiles)),255)
 for i,t in enumerate(tiles):canvas.paste(t,(16,i*step+14))
 t,tt=ocr(canvas,6,True);rows=[]
 for i in range(len(tiles)):
  toks=[x for x in tt if i*step<=int(x['top'])+int(x['height'])/2<(i+1)*step]
  literal=' '.join(x['text'] for x in sorted(toks,key=lambda x:int(x['left'])));s=literal.replace(' ','').replace(',','')
  rows.append(dict(value=int(s) if s.isdigit() else None,raw_ocr=literal,tokens=toks))
 return rows,t,canvas

def groups(sid):
 if '2024' in sid:return [PRES24,SEN24]
 if '2018-runoff' in sid:return [['Mike Espy','Cindy Hyde-Smith']]
 if '2018-county' in sid:return [SPECIAL]
 return [['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']]

def physical_x(g):
 # Retain the detected physical rule coordinates; correct omissions as marked
 # hypotheses rather than silently shifting source-column ordinals.
 w=g['render_size'][0];xs=g['grid_x'];near=[x for x in xs if .285*w<x<.98*w]
 gaps=[b-a for a,b in zip(near,near[1:]) if .04*w<b-a<.075*w]
 if not gaps:return None,[]
 step=statistics.median(gaps);first=min(near);last=max(near)
 while first>.345*w:first-=step
 rules=[];inferred=[]
 for i in range(round((last-first)/step)+1):
  predicted=first+i*step;real=min(near,key=lambda x:abs(x-predicted))
  if abs(real-predicted)<step*.22:x=real
  else:x=round(predicted);inferred.append(x)
  if not rules or x>rules[-1]:rules.append(x)
 return rules,inferred

def run(sid):
 target=OUT/'extracts/physical-native-v3'/f'{sid}.json.gz';target.parent.mkdir(exist_ok=True)
 if target.exists():return sid,'cached'
 r=next(x for x in receipts if x['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');pages=[]
 oldpath=OUT/'extracts/independent-position-cells-v2'/f'{sid}.json.gz';old=json.loads(gzip.decompress(oldpath.read_bytes())) if oldpath.exists() else {'pages':[]}
 oldpages={p['page']:p for p in old['pages']}
 for path in sorted((PEER/sid).glob('p*.json.gz')):
  gb=path.read_bytes();g=json.loads(gzip.decompress(gb));hints={f['field']:f for f in g['fields']};wanted=[n for group in groups(sid) for n in group]
  if not any(n in hints for n in wanted):continue
  assert g['raw_sha256']==r['raw_sha256'];rules,inferred=physical_x(g)
  if not rules or len(rules)<2:continue
  op=oldpages.get(g['page'],{});oldfields={f['source_row']:f for f in op.get('fields',[])};cache={}
  for hf in g['fields']:
   of=oldfields.get(hf['source_row'],{})
   for c in of.get('cells',[]):cache[tuple(c['bounds'])]=c
  fields=[];reconstructed=[];missing=[]
  for group in groups(sid):
   anchors=[]
   for i,name in enumerate(group):
    if name in hints and hints[name]['row_bounds'][1] in g['grid_y']:anchors.append(g['grid_y'].index(hints[name]['row_bounds'][1])-i)
   offset=anchors[0] if len(anchors)>=2 and len(set(anchors))==1 else None
   for i,name in enumerate(group):
    if name in hints:bounds=hints[name]['row_bounds'];hint=hints[name]
    elif offset is not None and 0<=offset+i<len(g['grid_y'])-1:
     bounds=[0,g['grid_y'][offset+i],g['render_size'][0],g['grid_y'][offset+i+1]];hint=None;reconstructed.append(name)
    else:missing.append(name);continue
    fields.append(dict(candidate_position_hint=name,row_bounds=bounds,source_row=hint['source_row'] if hint else None,row_geometry_basis='detected_anchor' if hint else 'consecutive_grid_offset_hypothesis',cells=[]))
  p=doc[g['page']-1];im=Image.open(io.BytesIO(p.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(g['rotation_ccw'],expand=True).rotate(g.get('deskew_angle_ccw',0),fillcolor=255)
  assert list(im.size)==g['render_size']
  cols=[];headers=[];labelcrops=[]
  hy=g['columns'][0]['bounds'][1::2] if g['columns'] else [int(im.height*.15),int(im.height*.3)]
  for j,(x0,x1) in enumerate(zip(rules,rules[1:]),1):
   box=[x0,hy[0],x1,hy[1]];cols.append(dict(source_column=j,bounds=box));headers.append(im.crop(box).rotate(-90,expand=True))
  for f in fields:labelcrops.append(im.crop((0,f['row_bounds'][1],rules[0],f['row_bounds'][3])))
  labs,ltsv,_=montage(labelcrops,False);hdr,htsv,_=montage(headers,False)
  for f,v in zip(fields,labs):f['independent_label_party_ocr']=v['raw_ocr']
  for c,v in zip(cols,hdr):c['independent_label_ocr']=v['raw_ocr']
  crops=[];positions=[]
  for i,f in enumerate(fields):
   for j,(x0,x1) in enumerate(zip(rules,rules[1:]),1):
    box=[x0,f['row_bounds'][1],x1,f['row_bounds'][3]];prior=cache.get(tuple(box));cell=dict(source_column=j,bounds=box)
    positions.append((i,len(f['cells'])));crops.append(im.crop(box))
    f['cells'].append(cell)
  tsv=[]
  for start in range(0,len(crops),22):
   vals,t,_=original_size_numbers(crops[start:start+22]);tsv.append(t)
   for (i,j),v in zip(positions[start:start+22],vals):fields[i]['cells'][j].update(v,reading_basis='independent_original_new_physical_bounds')
  pages.append(dict(page=g['page'],source_rect=list(p.rect),source_pdf_rotation=p.rotation,rotation_ccw=g['rotation_ccw'],deskew_angle_ccw=g.get('deskew_angle_ccw',0),render_size=list(im.size),geometry_reference_path=str(path.relative_to(BASE)),geometry_stored_sha256=sha(gb),physical_numeric_grid_x=rules,inferred_numeric_rules=inferred,geometry_qualification='Inferred rules and reconstructed rows are explicit hypotheses requiring original review; no native ID/boundary inference.',missing_candidate_row_positions=missing,reconstructed_candidate_row_positions=reconstructed,columns=cols,fields=fields,own_new_numeric_ocr_tsv=tsv,own_label_ocr_tsv=ltsv,own_header_ocr_tsv=htsv))
 target.write_bytes(gzip.compress(json.dumps(dict(source_id=sid,raw_sha256=r['raw_sha256'],parser='turnout-physical-native-3',qualification='Independent original readings; exchanged geometry only. No peer numeric or label transcription. No counts fitted to controls. Native coverage and roles require separate review.',pages=pages),ensure_ascii=False).encode(),mtime=0))
 return sid,len(pages),sum(len(f['cells']) for p in pages for f in p['fields'])

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prefix',default='sos-2024-county-');ap.add_argument('--only');ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args()
 ids=[r['id'] for r in receipts if r['id'].startswith(a.prefix) and (PEER/r['id']).exists() and (not a.only or r['id'].endswith(a.only))]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
  for x in pool.map(run,ids):print(*x,flush=True)
