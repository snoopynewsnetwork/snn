"""Reconstruct source-only boxes on original own v5 render after full-page review."""
import io,gzip,json
import fitz,numpy as np
from PIL import Image,ImageDraw
from acquire_sources import BASE,OUT,receipts,sha
from make_native_review import tidy

def geometry(county,pg,left,right,hy,rows,rotation_override=None,candidate_header_grid=False):
 sid='sos-2024-county-'+county;src=json.loads(gzip.decompress((OUT/'extracts'/f'{sid}-native-grid-v5.json.gz').read_bytes()));old=next(p for p in src['pages'] if p['page']==pg)
 if rotation_override is not None:old={**old,'rotation_ccw':rotation_override,'deskew_angle_ccw':0}
 r=next(r for r in receipts if r['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==src['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');page=doc[pg-1];scale=min(2.5,3300/max(page.rect.width,page.rect.height));im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png'))).rotate(old['rotation_ccw'],expand=True).rotate(old.get('deskew_angle_ccw') or 0,fillcolor=255);
 if rotation_override is not None:old['render_size']=list(im.size)
 else:assert list(im.size)==old['render_size']
 im.save(OUT/'qa'/f'{sid}-independent-own-grid-original-p{pg}.png');a=np.array(im)
 def rules(y0,y1):
  score=(a[y0+5:y1-3]<180).sum(axis=0);out=[]
  for x in np.linspace(left,right,12):
   lo,hi=max(0,round(x)-18),min(im.width,round(x)+19);out.append(int(np.argmax(score[lo:hi]))+lo)
  assert all(75<b-a<150 for a,b in zip(out,out[1:]));return out
 hx=rules(*hy);xx={name:(hx if candidate_header_grid else rules(*yy)) for name,yy in rows.items()};cols=[]
 for i in range(11):cols.append(dict(source_column=i+1,header_box=[hx[i]+1,hy[0],hx[i+1]+1,hy[1]],votes={name:dict(box=[xx[name][i]+1,yy[0],xx[name][i+1]+1,yy[1]]) for name,yy in rows.items()}))
 canvas=Image.new('RGB',(1300,880),'white');draw=ImageDraw.Draw(canvas);draw.text((5,5),f'{sid} ORIGINAL p{pg}: own source-specific grid; header / Pinkins / Wicker',fill='black')
 for i,c in enumerate(cols):
  y=40+i*75;draw.text((5,y+10),str(i+1),fill='black');canvas.paste(tidy(im.crop(c['header_box']).rotate(-90,expand=True),(780,65)),(45,y))
  for j,name in enumerate(rows):canvas.paste(tidy(im.crop(c['votes'][name]['box']),(180,65)),(850+j*210,y))
 dest=OUT/'qa/native-review'/f'{sid}-p{pg:02d}-own-geometry.png';canvas.save(dest)
 out=dict(page=pg,render_size=old['render_size'],rotation_ccw=old['rotation_ccw'],deskew_angle_ccw=old.get('deskew_angle_ccw'),columns=cols)
 log=dict(raw_sha256=src['raw_sha256'],page=pg,manual_full_original_grid_anchors=[left,right],header_y=hy,candidate_y=rows,candidate_header_grid=candidate_header_grid,detected_header_rules=hx,detected_candidate_rules=xx,source_render_size=old['render_size'],rotation_ccw=old['rotation_ccw'],deskew_angle_ccw=old.get('deskew_angle_ccw'),method='Source-only vertical strokes within 18 pixels of evenly spaced anchors after full original visual review; no candidate numbers or labels used to choose bounds.',evidence=str(dest.relative_to(BASE)))
 (OUT/'extracts'/f'{sid}-own-geometry-p{pg}.json').write_text(json.dumps(log,indent=2)+'\n');return out

def evidence(county,pages):
 f=OUT/'native-reviewed-2024.json';d=json.loads(f.read_text());s=d['sources']['sos-2024-county-'+county]
 for p in s['pages']:
  if p['page'] in pages:
   p['previous_template_evidence']=p['evidence'];p['evidence']=f'data/turnout/qa/native-review/sos-2024-county-{county}-p{p["page"]:02d}-own-geometry.png';p['geometry_review_record']=f'data/turnout/extracts/sos-2024-county-{county}-own-geometry-p{p["page"]}.json';p['coordinate_system']='Own original v5 render transform; source-specific header and candidate row physical rule targeting. No ordinal join or candidate values used for geometry.'
 f.write_text(json.dumps(d,indent=2)+'\n')
