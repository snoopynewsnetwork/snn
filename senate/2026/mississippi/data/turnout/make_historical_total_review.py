"""Render original historical source TOTAL columns as bounded human reading aids."""
import argparse,gzip,io,json,re
from pathlib import Path
import fitz
from PIL import Image,ImageOps,ImageDraw
from acquire_sources import BASE,OUT,receipts,sha,savejson

def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def run(sid):
 batchpath=OUT/'extracts/independent-position-cells-v2'/f'{sid}.json.gz'
 if not batchpath.exists():return None
 b=read(batchpath);names=['Mike Espy','Cindy Hyde-Smith'] if 'runoff' in sid else ['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'] if '2018' in sid else ['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards'];candidates=[]
 for p in b['pages']:
  g=read(BASE/p['geometry_reference_path']);fields=[f for f in g.get('fields',[]) if f['field'] in names and f['office_context_ocr'] in ['senate','senate-special']]
  if len(fields)>=1:candidates.append((p,g,fields))
 if not candidates:return None
 p,g,fields=max(candidates,key=lambda v:v[0]['page']);cols=p['columns'];tot=[c for c in cols if re.search('total|toral|tota[l1i]|t0tal',c['own_label_ocr'],re.I)];strategy='own_header_TOTAL_ocr_requires_visual_verification'
 if not tot:
  scores=[]
  for c in cols:
   vv=[next((x['value'] for x in f['cells'] if x['source_column']==c['source_column']),None) for f in p['fields'] if f['source_row'] in [x['source_row'] for x in fields]];vs=sorted(v for v in vv if v is not None and 0<=v<200000)
   if vs:scores.append((sum(vs),c))
  if not scores:return None
  tot=[max(scores,key=lambda x:x[0])[1]];strategy='largest_candidate_column_discovery_only_not_TOTAL_acceptance'
 c=tot[-1]
 if len(fields)<len(names) and len(fields)>=2:
  ys=g.get('grid_y',[]);bases=[]
  for f in fields:
   if f['row_bounds'][1] in ys:bases.append(ys.index(f['row_bounds'][1])-names.index(f['field']))
  if bases and len(set(bases))==1:
   base=bases[0]
   for i,name in enumerate(names):
    if any(f['field']==name for f in fields) or not 0<=base+i<len(ys)-1:continue
    lo,hi=ys[base+i:base+i+2];fields.append(dict(field=name,row_bounds=[0,lo,g['render_size'][0],hi],source_row=base+i+1,cells=[dict(source_column=x['source_column'],bounds=[x['bounds'][0],lo,x['bounds'][2],hi]) for x in cols],position_basis='Missing row position reconstructed from consecutive printed candidate rows/grid; original label and number require visual reading.'))
 r=next(r for r in receipts if r['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');pg=doc[p['page']-1];im=Image.open(io.BytesIO(pg.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(g['rotation_ccw'],expand=True).rotate(g.get('deskew_angle_ccw',0),fillcolor=255)
 height=110+len(names)*95;canvas=Image.new('RGB',(1000,height),'white');dr=ImageDraw.Draw(canvas);dr.text((5,5),f'{sid} ORIGINAL p{p["page"]} col{c["source_column"]}',fill='black');dr.text((5,22),strategy,fill='black');head=im.crop(tuple(c['bounds'])).rotate(-90,expand=True);head.thumbnail((450,55));canvas.paste(head,(530,42));pointers=[]
 for i,name in enumerate(names):
  f=next((f for f in fields if f['field']==name),None);y=105+i*95;dr.text((5,y),name,fill='black')
  if f is None:dr.text((5,y+28),'ROW POSITION MISSING; direct full-page review needed',fill='red');continue
  row=f['row_bounds'];left=min(x['bounds'][0] for x in f['cells']);label=im.crop((0,row[1],left,row[3]));label.thumbnail((560,65));canvas.paste(label,(5,y+20));cell=next((x for x in f['cells'] if x['source_column']==c['source_column']),None)
  if cell:
   box=cell['bounds'];crop=im.crop((max(0,box[0]-5),box[1],min(im.width,box[2]+6),box[3]));crop.thumbnail((300,80));canvas.paste(crop,(650,y));pointers.append(dict(candidate=name,row_bounds=row,cell_bounds=box))
 target=OUT/'qa/historical-total-review';target.mkdir(exist_ok=True);q=target/(sid+'.png');canvas.save(q);full=im.copy();full.thumbnail((2000,2000));full.save(target/(sid+'-full-original.jpg'),quality=90)
 return dict(source_id=sid,raw_sha256=r['raw_sha256'],source_page=p['page'],proposed_source_column=c['source_column'],selection_strategy=strategy,render_size=list(im.size),rotation_ccw=g['rotation_ccw'],deskew_angle_ccw=g.get('deskew_angle_ccw',0),header_bounds=c['bounds'],candidate_positions=pointers,review_png=str(q.relative_to(BASE)),full_original_preview=str((target/(sid+'-full-original.jpg')).relative_to(BASE)))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prefix',default='sos-2018-runoff-county-');ap.add_argument('--only');a=ap.parse_args();records=[]
 for r in receipts:
  if r['id'].startswith(a.prefix) and 'pdf' in str(r.get('headers',{})).lower() and (not a.only or r['id'].endswith(a.only)):
   x=run(r['id'])
   if x:records.append(x)
 savejson(OUT/'source'/('historical-total-positions-'+a.prefix.rstrip('-')+('-'+a.only if a.only else '')+'.json'),records);print(len(records))
