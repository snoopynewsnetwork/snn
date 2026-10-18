#!/usr/bin/env python3
"""Offline deterministic native extraction, PDF audit, compatibility and index builder.
Requirements: Python3, PyMuPDF, Shapely, Pillow. Writes ONLY owned maps outputs.
No GIS clipping, repairing, rounding, generalization or projection is used on source data.
"""
import sys
sys.dont_write_bytecode=True
import json,gzip,hashlib,sqlite3,struct,io,zipfile,re,html,collections,math
from pathlib import Path
import fitz
from shapely import from_wkb, get_num_coordinates
from shapely.validation import explain_validity
from shapely.strtree import STRtree
from acquire import ROOT,read,sha
STATE=ROOT.parent
PIN='b60b0bc4fed0c0b8618b6f851cc8f25d3c963bbd3ea12debecc5995dff54ceb1'
def dump(p,d):
 b=(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def meta(k):return json.loads((ROOT/'evidence'/f'{k}.request.json').read_text())
def raw(k):return read(meta(k))
def q(s):return '"'+s.replace('"','""')+'"'
def connect(k):
 c=sqlite3.connect(':memory:');c.deserialize(raw(k+'-gpkg'));return c

from native import wkb_blob,scan_wkb

def subset(c,t,rows,bounds):
 out=sqlite3.connect(':memory:');out.execute('PRAGMA application_id=1196444487');out.execute('PRAGMA user_version=10200')
 for name in ['gpkg_spatial_ref_sys','gpkg_contents','gpkg_geometry_columns',t]:
  sql=c.execute("select sql from sqlite_master where type='table' and name=?",(name,)).fetchone()[0];out.execute(sql)
  rr=rows if name==t else c.execute('select * from '+q(name)).fetchall()
  if name in ('gpkg_contents','gpkg_geometry_columns'):rr=[r for r in rr if r[0]==t]
  if name=='gpkg_contents':
   rr=[tuple(list(r[:5])+[bounds[0],bounds[1],bounds[2],bounds[3]]+list(r[9:])) for r in rr]
  if rr:out.executemany('insert into '+q(name)+' values('+','.join('?' for _ in rr[0])+')',rr)
 out.commit();assert out.execute('pragma integrity_check').fetchone()[0]=='ok'
 assert out.execute('select * from '+q(t)+' order by OBJECTID').fetchall()==rows
 return out.serialize()

def svg(paths,p,title):
 gs=[g for g in paths if g is not None and not g.is_empty]
 if not gs:return
 xmin=min(g.bounds[0] for g in gs);ymin=min(g.bounds[1] for g in gs);xmax=max(g.bounds[2] for g in gs);ymax=max(g.bounds[3] for g in gs)
 scale=min(700/(xmax-xmin),500/(ymax-ymin));ox=(760-(xmax-xmin)*scale)/2;oy=(560-(ymax-ymin)*scale)/2
 out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 600"><rect width="760" height="600" fill="#f3f5f7"/>',f'<title>{html.escape(title)}</title>']
 for g in gs:
  pp=g.geoms if g.geom_type=='MultiPolygon' else [g];d=[]
  for poly in pp:
   if poly.geom_type!='Polygon':continue
   for ring in [poly.exterior,*poly.interiors]:
    xy=[f'{(x-xmin)*scale+ox:.2f},{(ymax-y)*scale+oy:.2f}' for x,y,*_ in ring.coords]
    d.append('M'+'L'.join(xy)+'Z')
  out.append('<path d="'+''.join(d)+'" fill="#dce8ef" fill-rule="evenodd" stroke="#245470" stroke-width="0.7"/>')
 out.append(f'<text x="22" y="584" font-family="sans-serif" font-size="15">{html.escape(title)} · preview only</text></svg>');p.parent.mkdir(exist_ok=True,parents=True);p.write_text(''.join(out))

contract_bytes=(STATE/'data/turnout/priority-set.json').read_bytes();assert sha(contract_bytes)==PIN
contract=json.loads(contract_bytes);accept=json.loads((STATE/'data/coordinator-priority-acceptance.json').read_text());assert accept['contract_sha256']==PIN
counties=contract['county_order'];assert len(counties)==87 and [c['key'] for c in counties[:24]]==accept['ordered_priority_keys']
assert sum(len(v) for c in counties for v in c['native_constituents'].values())==12316
# Pin only immutable finished inputs; full objects retained without depending on peer aggregates.
pinpaths=['data/turnout/priority-set.json','data/coordinator-priority-acceptance.json','data/coordinator-native-contract-review.json','data/baselines/asset-manifest.json','data/baselines/validation.json','data/baselines/source/current-ballot.json','data/coordinator-current-ballot-visual-review.json']
dump('input-pins.json',{'authority':'acceptance path; no reverse contract hash dependency','inputs':[{'path':p,'bytes':len((STATE/p).read_bytes()),'sha256':sha((STATE/p).read_bytes())} for p in pinpaths]})
layers={};geometry_diagnostics={};schemas={};allg={}
for vintage,k,t in [('2024','results','general_election_results_by_precinct_2024'),('2022','results','general_election_results_by_precinct_2022'),('current','current','bdry_votingdistricts')]:
 c=connect(k);fields=[r[1] for r in c.execute('pragma table_info('+q(t)+')')];rows=c.execute('select * from '+q(t)+' order by OBJECTID').fetchall();geomcol=fields.index('Shape');by=collections.defaultdict(list);geoms=[];recorddiag=[];byid={};headers=collections.Counter();types=collections.Counter();dims=collections.Counter();coords=0
 schema={'table':t,'source_original':k+'-gpkg','columns':c.execute('pragma table_info('+q(t)+')').fetchall(),'create_sql':c.execute("select sql from sqlite_master where name=?",(t,)).fetchone()[0],'gpkg_geometry_columns':c.execute('select * from gpkg_geometry_columns where table_name=?',(t,)).fetchall(),'gpkg_spatial_ref_sys':c.execute('select * from gpkg_spatial_ref_sys').fetchall(),'gpkg_contents':c.execute('select * from gpkg_contents where table_name=?',(t,)).fetchall(),'field_value_states':{}}
 for fi,f in enumerate(fields):
  if f=='Shape':continue
  states=collections.Counter('null' if r[fi] is None else 'blank' if r[fi]=='' else 'whitespace' if isinstance(r[fi],str) and r[fi].strip()=='' else 'zero' if r[fi]==0 else 'nonzero_or_text' for r in rows);schema['field_value_states'][f]=dict(states)
 for row in rows:
  d=dict(zip(fields,row));gid=d['VTDID'];fips='27'+d['COUNTYFIPS'];by[fips].append(row);assert gid not in byid;byid[gid]=d
  blob=row[geomcol];g=None;diag={'OBJECTID':d['OBJECTID'],'VTDID':gid,'county_fips':fips,'raw_geometry_sha256':sha(blob) if blob else None}
  if blob:
   w,h=wkb_blob(blob);sc=scan_wkb(w);headers[json.dumps(h,sort_keys=True)]+=1;types.update(sc['types']);dims.update(sc['dimensions']);coords+=sc['coordinate_positions'];diag.update(sc)
   try:g=from_wkb(w);diag.update({'valid':bool(g.is_valid),'empty':bool(g.is_empty),'reason':explain_validity(g),'area_square_meters':g.area,'length_meters':g.length,'bounds_native_meters':g.bounds,'interior_ring_count':sum(len(p.interiors) for p in (g.geoms if g.geom_type=='MultiPolygon' else [g])), 'component_areas_square_meters':[p.area for p in (g.geoms if g.geom_type=='MultiPolygon' else [g])], 'hole_areas_square_meters':[__import__('shapely').geometry.Polygon(r).area for p in (g.geoms if g.geom_type=='MultiPolygon' else [g]) for r in p.interiors]})
   except Exception as e:diag['geometry_parser_error']=str(e)
  else:diag['missing_geometry']=True
  recorddiag.append(diag);geoms.append(g)
 assert set(by)=={x['county_fips'] for x in counties}
 # Pair intersections retain every positive area including floating point slivers. Invalids remain unmodified.
 validix=[i for i,g in enumerate(geoms) if g is not None and g.is_valid and not g.is_empty];vg=[geoms[i] for i in validix];tree=STRtree(vg);overlaps=[];errors=[]
 for a,ga in enumerate(vg):
  for b in tree.query(ga):
   b=int(b)
   if b<=a:continue
   ia,ib=validix[a],validix[b]
   try:
    inter=ga.intersection(vg[b]);area=inter.area
    if area>0:overlaps.append({'a':recorddiag[ia]['VTDID'],'b':recorddiag[ib]['VTDID'],'area_square_meters':area,'bounds_native_meters':inter.bounds,'under_1m2_diagnostic':area<1})
   except Exception as e:errors.append({'a':recorddiag[ia]['VTDID'],'b':recorddiag[ib]['VTDID'],'error':str(e)})
 gd={'scope':'Native EPSG26915 meters. No repairs/snap/union/clipping; every positive intersection area retained, no tolerance filter. Invalid-pair overlaps unassessed. Gaps versus legal county topology unknown; county boundary is not inferred. Interior holes recorded per feature; their legal/water significance unknown. Under1m2 is diagnostic only.','records':recorddiag,'positive_area_overlaps':overlaps,'pair_errors':errors,'headers':dict(headers),'wkb_types':dict(types),'wkb_dimensions':dict(dims),'coordinate_positions':coords,'missing_geometry':sum(g is None for g in geoms),'invalid':sum(g is not None and not g.is_valid for g in geoms),'sub_1m2_features':[d for d in recorddiag if d.get('area_square_meters',2)>=0 and d.get('area_square_meters',2)<1]}
 dump(f'diagnostics/{vintage}-geometry.json.gz',gd);geometry_diagnostics[vintage]={x:gd[x] for x in ['wkb_types','wkb_dimensions','coordinate_positions','missing_geometry','invalid']};geometry_diagnostics[vintage]['positive_area_overlaps']=len(overlaps)
 schemas[vintage]=schema;layers[vintage]={'fields':fields,'rows':rows,'bycounty':by,'byid':byid};allg[vintage]=dict((r['VTDID'],g) for r,g in zip(recorddiag,geoms))
 for county in counties[:24]:
  fips=county['county_fips'];rr=by[fips];gg=[allg[vintage][r[fields.index('VTDID')]] for r in rr];bounds=(min(g.bounds[0] for g in gg if g is not None),min(g.bounds[1] for g in gg if g is not None),max(g.bounds[2] for g in gg if g is not None),max(g.bounds[3] for g in gg if g is not None))
  bb=subset(c,t,rr,bounds);p=ROOT/'counties'/fips/f'{vintage}.gpkg.gz';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gzip.compress(bb,mtime=0));svg(gg,p.parent/f'{vintage}.svg',county['name']+' / '+vintage)
 print('native',vintage,len(rows),'coords',coords,'invalid',gd['invalid'],'overlaps',len(overlaps),flush=True)
dump('schema.json',schemas)
# Every PDF within each actual ZIP: validate header/parse/pagecount/text/member identity. Preview first source-ordered PDF per county.
papers={}
for county in counties[:24]:
 fips=county['county_fips'];key='lcc2025-'+fips;m=meta(key);b=read(m);pd={'key':key,'geography':county['name'],'publisher':'Minnesota Legislative Coordinating Commission GIS; boundaries credited to SOS Elections Division','vintage':'2025 precinct map publication; NOT November2026 approval','request':f'evidence/{key}.request.json','status':m['status'],'actual_zip':b.startswith(b'PK'),'members':[],'errors':[]}
 if pd['actual_zip']:
  z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None
  for zi in z.infolist():
   bb=z.read(zi);mi={'member_path':zi.filename,'CRC':zi.CRC,'compression_type':zi.compress_type,'compressed_bytes':zi.compress_size,'original_bytes':len(bb),'sha256':sha(bb),'zip_member_datetime_unspecified_timezone':zi.date_time}
   if bb.startswith(b'%PDF-'):
    try:
     doc=fitz.open(stream=bb,filetype='pdf');mi['pages']=len(doc);mi['pdf_metadata']=doc.metadata;mi['page_dimensions_points']=[list(p.rect) for p in doc];mi['full_page_text']=[p.get_text() for p in doc];mi['pdf_version_magic']=bb[:12].decode(errors='replace');mi['native_geospatial_crs']='unknown unless declared in original; paper map not assumed EPSG26915'
     if not any(x.get('preview') for x in pd['members']):
      p=ROOT/'counties'/fips/'paper2025-page1.png';page=doc[0];pix=page.get_pixmap(matrix=fitz.Matrix(1400/page.rect.width,1400/page.rect.width),alpha=False);pix.save(str(p));mi['preview']=str(p.relative_to(ROOT));mi['preview_transform']='PyMuPDF page1 at1400pixel width, aspect preserved; no map geometry extracted'
    except Exception as e:mi['error']=str(e);pd['errors'].append({'member':zi.filename,'error':str(e)})
   else:mi['not_pdf']=True
   pd['members'].append(mi)
 pd['pdf_count']=sum('pages' in x for x in pd['members']);pd['page_count']=sum(x.get('pages',0) for x in pd['members']);papers[fips]=pd
 print('paper',county['name'],pd['pdf_count'],pd['page_count'],flush=True)
dump('paper-audit.json.gz',papers)
# Complete objects/fields, not just a reduced list or priorities. Equality validated independently.
compat={'scope':'ID coincidence only. No legal physical/reporting/method/crossyear/results approval, no vote allocation.2020 geometry not acquired; every2020 object preserved unmodified. Counties disjoint primary aggregates. All central/no-data cases remain source context.','complete_frozen_contract':contract,'counties':[]}
inventory=[]
for co in counties:
 f=co['county_fips'];d={'key':co['key'],'county':co['name'],'county_fips':f,'rank':co['rank'],'historical_votes':co['votes'],'in_priority':co['in_priority'],'historical_native':{},'geometry':{},'id_diagnostics':{}}
 for vintage,l in layers.items():
  rr=l['bycounty'][f];fld=l['fields'];records=[dict(zip(fld,r)) for r in rr];ids=[r['VTDID'] for r in records];d['geometry'][vintage]={'count':len(rr),'object_ids':[r['OBJECTID'] for r in records],'VTDIDs':ids,'municipalities':dict(collections.Counter(r['MCDNAME'] for r in records)),'wards':dict(collections.Counter(str(r['WARD']) for r in records)),'CTU_TYPE':dict(collections.Counter(str(r['CTU_TYPE']) for r in records))}
 for year,rr in co['native_constituents'].items():
  ids=[r['VTDID'] for r in rr];d['historical_native'][year]=len(rr);l=layers.get(year);gids=set(d['geometry'].get(year,{}).get('VTDIDs',[]))
  d['id_diagnostics'][year]={'scope':'exact source string IDs, NOT boundary/result/method approval','geometry_vintage_available':l is not None,'same_vintage_id_present':sorted(set(ids)&gids),'native_id_without_same_vintage_polygon':sorted(set(ids)-gids),'polygon_without_native_record':sorted(gids-set(ids))}
 ids24=set(d['geometry']['2024']['VTDIDs']);idsc=set(d['geometry']['current']['VTDIDs']);common=ids24&idsc
 d['current_vs_2024']={'common_ids':sorted(common),'removed_ids':sorted(ids24-idsc),'added_ids':sorted(idsc-ids24),'identical_raw_geometry_blobs':[i for i in sorted(common) if layers['2024']['byid'][i]['Shape']==layers['current']['byid'][i]['Shape']],'changed_raw_geometry_blobs':[i for i in sorted(common) if layers['2024']['byid'][i]['Shape']!=layers['current']['byid'][i]['Shape']],'name_changes':[{'VTDID':i,'2024':layers['2024']['byid'][i]['PCTNAME'],'current':layers['current']['byid'][i]['PCTNAME']} for i in sorted(common) if layers['2024']['byid'][i]['PCTNAME']!=layers['current']['byid'][i]['PCTNAME']],'scope':'Same CRS/raw blob comparison within acquired publications. Shared IDs or identical bytes do not certify legal currency or November joins.'}
 if f in papers:d['paper']={x:papers[f][x] for x in ['pdf_count','page_count','vintage','request','actual_zip','status']}
 compat['counties'].append(d);inventory.append(d)
dump('compatibility.json.gz',compat);dump('county-inventory.json',inventory)
dump('coverage.json',{'geometry':geometry_diagnostics,'counts':{v:len(l['rows']) for v,l in layers.items()},'per_county_counts':{v:{co['county_fips']:len(l['bycounty'][co['county_fips']]) for co in counties} for v,l in layers.items()},'priority_counts':{v:sum(len(l['bycounty'][co['county_fips']]) for co in counties[:24]) for v,l in layers.items()},'metadata_advertised_current':4120,'actual_current':4105,'advertised_minus_actual':15,'scope':'4120 metadata is not acquisition count. GPKG/service acquired4105; no missing features fabricated.2024/2022 all87each4103. Full2022 retained within same original once.2020 all4110 contract records retained but no2020 geometry original acquired.'})
print('BUILD CORE COMPLETE',flush=True)
