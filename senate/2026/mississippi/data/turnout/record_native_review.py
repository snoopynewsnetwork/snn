"""Write primary visual-read ledger entries, preserving original source bounds."""
import gzip,json,io
import fitz
from PIL import Image
from acquire_sources import BASE,OUT,receipts,sha

def verified_physical_geometry(sid,pg):
 """Replace inaccurate own template bounds after direct original physical review.
 Uses reference geometry only, never source candidate numeric values or labels.
 """
 f=OUT/'native-reviewed-2024.json';d=json.loads(f.read_text());s=d['sources'][sid];p=next(p for p in s['pages'] if p['page']==pg)
 ref=BASE/f'data/baselines/extracts/native-v4/{sid}/p{pg:04d}.json.gz';gb=ref.read_bytes();g=json.loads(gzip.decompress(gb));assert s['raw_sha256']==g['raw_sha256'];xs=g['grid_x'][1:];assert len(xs)==12
 yy=g['columns'][0]['bounds'][1::2];ff={x['field']:x for x in g['fields']}
 for c,(x0,x1) in zip(p['columns'],zip(xs,xs[1:])):
  c['previous_template_bounds']=dict(header=c['header_bounds'],candidates=c['candidate_bounds'])
  c['header_bounds']=[x0,yy[0],x1,yy[1]]
  c['candidate_bounds']={name:[x0,ff[name]['row_bounds'][1],x1,ff[name]['row_bounds'][3]] for name in ['Ty Pinkins','Roger F. Wicker']}
 p.update(render_size=g['render_size'],rotation_ccw=g['rotation_ccw'],deskew_angle_ccw=g['deskew_angle_ccw'],coordinate_system='Verified original fitz2.7 gray/PIL rotate/deskew pixels; physical detected grid lines, not sameordinal template join.',geometry_reference=str(ref.relative_to(BASE)),geometry_reference_sha256=sha(gb),geometry_review_basis='All physical columns counted and full original headers/rows directly visually read. No reference numeric/label values copied.')
 physical=OUT/'qa/native-review'/f'{sid}-p{pg:02d}-physical.png'
 if physical.exists():p['previous_template_evidence']=p['evidence'];p['evidence']=str(physical.relative_to(BASE))
 r=next(x for x in receipts if x['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==s['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');im=Image.open(io.BytesIO(doc[pg-1].get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(g['rotation_ccw'],expand=True).rotate(g['deskew_angle_ccw'],fillcolor=255);dest=OUT/'qa'/f'{sid}-verified-physical-p{pg}.png';im.save(dest);p['physical_original_preview']=str(dest.relative_to(BASE));f.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')

def record(county,pages,physical_pages=(),physical_x_overrides=None,page_overrides=None):
 f=OUT/'native-reviewed-2024.json';d=json.loads(f.read_text());sid='sos-2024-county-'+county;src=json.loads(gzip.decompress((OUT/'extracts'/f'{sid}-native-grid-v5.json.gz').read_bytes()));pp=[]
 for pg,labels,a,b,total in pages:
  page=next((x for x in src['pages'] if x['page']==pg),None)
  physical=False
  if pg in (page_overrides or {}):
   page=page_overrides[pg]
  elif pg in physical_pages or pg in (physical_x_overrides or {}) or page is None or not page.get('columns'):
   physical=True;refpath=BASE/f'data/baselines/extracts/native-v4/{sid}/p{pg:04d}.json.gz';gb=refpath.read_bytes();g=json.loads(gzip.decompress(gb));xs=(physical_x_overrides or {}).get(pg,g['grid_x'][1:]);assert len(xs)==12;assert g['raw_sha256']==src['raw_sha256'];hy=g['columns'][0]['bounds'][1::2];ff={f['field']:f for f in g['fields']}
   page=dict(page=pg,render_size=g['render_size'],rotation_ccw=g['rotation_ccw'],deskew_angle_ccw=g['deskew_angle_ccw'],columns=[dict(header_box=[x0,hy[0],x1,hy[1]],votes={n:dict(box=[x0,ff[n]['row_bounds'][1],x1,ff[n]['row_bounds'][3]]) for n in ['Ty Pinkins','Roger F. Wicker']}) for x0,x1 in zip(xs,xs[1:])])
  assert len(labels)==len(a)==len(b)
  cols=[]
  for i,(label,x,y) in enumerate(zip(labels,a,b),1):
   ref=page['columns'][i-1];role='source_TOTAL' if i==total else 'unused_template_column' if total is not None and i>total else 'native_reporting_constituent'
   assert role=='unused_template_column' or x is not None and y is not None
   cols.append(dict(source_column=i,label_literal=label,printed_native_id=None,role=role,Ty_Pinkins=x,Roger_F_Wicker=y,header_bounds=ref['header_box'],candidate_bounds={k:v['box'] for k,v in ref['votes'].items()}))
  pp.append(dict(page=pg,evidence=f'data/turnout/qa/native-review/{sid}-p{pg:02d}'+('-physical.png' if physical else '.png'),coordinate_system='Original fitz2.7 gray/PIL rotate and deskew pixels; exchanged geometry only, numeric and labels independently original-read' if physical else 'own v5 render pixels',render_size=page['render_size'],rotation_ccw=page['rotation_ccw'],deskew_angle_ccw=page.get('deskew_angle_ccw'),columns=cols))
  if physical:pp[-1].update(geometry_reference=str(refpath.relative_to(BASE)),geometry_reference_sha256=sha(gb))
  if pg in (physical_x_overrides or {}):pp[-1].update(explicit_numeric_grid_x=xs,geometry_qualification='Explicit physical-column geometry after complete-original visual review; the reference machine grid had missing rules. No reference values copied. Native identities follow independently read printed headers; no current boundary claim.')
 prior=d['sources'].get(sid,{});history=prior.get('correction_history',[])
 before={(p['page'],c['source_column']):c for p in prior.get('pages',[]) for c in p['columns']}
 for p in pp:
  for c in p['columns']:
   old=before.get((p['page'],c['source_column']))
   if old:
    for field in ['label_literal','Ty_Pinkins','Roger_F_Wicker','role']:
     if old.get(field)!=c.get(field):history.append(dict(page=p['page'],source_column=c['source_column'],field=field,previous=old.get(field),corrected=c.get(field),basis='Independent original image re-read; no residual allocation. See original and retained review evidence.'))
 d['sources'][sid]=dict(raw_sha256=src['raw_sha256'],pages=pp,review_scope='All native source-column labels and both named Senate candidates on listed original pages directly visually read, including TOTAL and unused template columns. Other contest/summary fields are separate source scopes.',correction_history=history)
 u=[c for p in pp for c in p['columns'] if c['role']=='native_reporting_constituent'];print(sid,len(u),sum(c['Ty_Pinkins'] for c in u),sum(c['Roger_F_Wicker'] for c in u))
 f.write_text(json.dumps(d,indent=2)+'\n')
