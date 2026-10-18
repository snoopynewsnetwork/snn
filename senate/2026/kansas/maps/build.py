#!/usr/bin/env python3
"""Offline rebuild of native context exports, diagnostics, original-PDF renders and map index.
Never modifies acquired bytes or read-only peer/first-wave data. PYTHONDONTWRITEBYTECODE=1 recommended.
"""
import collections,datetime,gzip,hashlib,html,io,json,math,pathlib,re,sys
import fitz
from PIL import Image,ImageDraw
from acquire import ROOT,MAN,read,links
from geometry import load_records,diagnostic,as_crs

def dump(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def gz(path,obj):path.write_bytes(gzip.compress((json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode(),mtime=0))
def esc(x):return html.escape(str(x),quote=True)
def preview(key,features,title):
 rings=[];total=0;curve=[]
 for f in features:
  g=f.get('geometry')
  if not g:continue
  if 'curveRings'in g:curve.append(f);continue
  for r in g.get('rings',[]):
   if r:rings.append((r,f['attributes']));total+=len(r)
 if not rings:return None
 xs=[p[0] for r,a in rings for p in r];ys=[p[1] for r,a in rings for p in r]
 x0,y0,x1,y1=min(xs),min(ys),max(xs),max(ys);scale=min(940/(x1-x0),650/(y1-y0));xo=(1000-(x1-x0)*scale)/2;yo=(730-(y1-y0)*scale)/2
 paths=[]
 # Every source vertex/part is traversed, preview XY rounded to 0.01 display pixels only.
 byfeature=collections.defaultdict(list);attrs={}
 for r,a in rings:
  label=json.dumps(a,ensure_ascii=False,sort_keys=True);attrs[label]=a
  path='M'+'L'.join(f'{xo+(p[0]-x0)*scale:.2f},{yo+(y1-p[1])*scale:.2f}' for p in r)+'Z';byfeature[label].append(path)
 for n,(label,ps) in enumerate(byfeature.items()):
  paths.append(f'<path d="{" ".join(ps)}" fill="hsl({(n*137.5)%360:.1f},42%,83%)" fill-rule="evenodd" stroke="#294451" stroke-width="0.65"><title>{esc(label)}</title></path>')
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 780" role="img"><title>{esc(title)}</title><rect width="1000" height="780" fill="#f7fafb"/>'+''.join(paths)+f'<text x="20" y="758" font-family="sans-serif" font-size="15">{esc(title)}</text></svg>'
 (ROOT/'previews'/f'{key}.svg').write_text(svg)
 return {'path':f'previews/{key}.svg','source_vertices':total,'source_rings':len(rings),'display_extent':[x0,y0,x1,y1],'curve_omissions':len(curve),'precision':'0.01 preview pixel; originals unmodified'}

def run():
 for d in ['native','previews','extracts']:(ROOT/d).mkdir(exist_ok=True)
 contractpath=ROOT.parent/'data/turnout/priority-set.json';contract=json.loads(contractpath.read_text())
 assert hashlib.sha256(contractpath.read_bytes()).hexdigest()=='dcdc1457a5b08851ef76b5372435d56788f647708da5ff9a6ef35435f92fa6a7'
 accepted=json.loads((ROOT.parent/'data/coordinator-priority-acceptance.json').read_text());assert accepted['accepted'] and accepted['contract_sha256']==hashlib.sha256(contractpath.read_bytes()).hexdigest()
 records={x['id']:x for x in json.loads(MAN.read_text())};services=json.load(open(ROOT/'services.json'));notes=json.load(open(ROOT/'county-notes.json'))
 data,archives=load_records(records,services);dump(ROOT/'extracts/archive-checks.json',archives)
 geom={};previews={};features=[]
 for key,value in data.items():
  d=diagnostic(value)
  extent_id=key+'-extent'
  if extent_id in records:d['advertised_query_extent']=json.loads(read(records[extent_id])).get('extent')
  gz(ROOT/'extracts'/f'{key}-geometry.json.gz',d);geom[key]=d
  draw=value['features']
  if key=='shawnee':
   linear=json.loads(read(records['shawnee-curve-linearized-preview']))['features'];ids=[x['attributes']['OBJECTID'] for x in linear];assert sorted(ids)==[2120,2176,2199,2211]
   draw=[x for x in draw if 'curveRings' not in (x.get('geometry') or {})]+linear
  if key!='klrd-2022':
   p=preview(key,draw,f'{key}: publication reference; no vote allocation')
   if p:
    if key=='shawnee':p['curve_preview_capture']='shawnee-curve-linearized-preview';p['native_curve_ids']=[2120,2176,2199,2211];p['curve_policy']='Four native true-curve objects preserved in originals; separate server-linearized geometry used only for preview.'
    previews[key]=p
  for index,f in enumerate(value['features']):
   features.append({'source_id':key,'row':index,'attributes':f['attributes'],'geometry_availability':'present' if f.get('geometry') else 'unavailable','historical_result_crosswalk':'unreviewed; no votes assigned'})
 state=data['klrd-2022']['features'];bycounty=collections.defaultdict(list)
 for f in state:bycounty[str(f['attributes']['CO_CODE'])].append(f)
 assert len(bycounty)==105 and sum(map(len,bycounty.values()))==4749
 counties=[];native_total=0;family_counts=collections.Counter();unknown=collections.Counter()
 for c in contract['all_geography_coverage']:
  fips=c['county_fips'];key=c['county_key'];name=c['county'];families=c['source_native_families'];native_total+=sum(len(f['constituents']) for f in families)
  for f in families:
   family_counts[f['source_id']]+=len(f['constituents']);unknown[f['source_id']]+=sum(x['named_candidate_total'] is None for x in f['constituents'])
  gz(ROOT/'native'/f'{fips}.json.gz',c) # full unchanged source-native objects, not a county-only replacement
  pp=preview('klrd2022-'+fips,bycounty[fips],f'{name}: KLRD2022 post-redistricting reference; current approval unavailable');previews['klrd2022-'+fips]=pp
  n=notes.get(name,{'assets':[],'scope':'Outside exact23 deep-research priority; all historical source objects retained; actual complete official2022 reference geometry downloaded.','vintage':'2022 state reference only.','gaps':'Current county/November2026 map and result crosswalk not investigated in this bounded priority assignment.'})
  counties.append({'county':name,'county_key':key,'county_fips':fips,'rank':c['rank'],'priority':c['priority80'],'native_context':f'native/{fips}.json.gz','native_families':[{'source_id':f['source_id'],'count':len(f['constituents']),'unknown_count':sum(x['named_candidate_total'] is None for x in f['constituents'])} for f in families],'native_crosswalk_status':'All source-native objects remain unmatched/unapproved; lexical identity alone never allocates votes.','state_2022_feature_count':len(bycounty[fips]),'state_2022_feature_ids':[x['attributes']['FID'] for x in bycounty[fips]],'state_2022_preview':pp['path'],'local':n,'november_2026_boundary_approval':False})
 assert native_total==22031 and set(notes)==set(contract['ordered_priority_names'])
 gz(ROOT/'extracts/map-feature-attributes.json.gz',features)
 dump(ROOT/'inventory.json',{'source_contract':'../data/turnout/priority-set.json','contract_sha256':hashlib.sha256(contractpath.read_bytes()).hexdigest(),'authoritative_acceptance_path':'../data/coordinator-priority-acceptance.json','acceptance_scope':'Historical research scope only; no reverse acceptance hash','ordered_priority_keys':contract['ordered_priority_keys'],'counties':counties,'native_count':native_total,'source_family_counts':dict(family_counts),'unknown_count_units':dict(unknown),'state_reference_count':len(state),'map_crosswalk_approved':False})
 dump(ROOT/'preview-manifest.json',previews)
 # Real PDF pages. All pages rendered into contact sheets; original PDF bytes retained.
 items=[];pdfs={}
 for key,r in records.items():
  if not r.get('storage'):continue
  b=read(r)
  if not b.startswith(b'%PDF-'):continue
  doc=fitz.open(stream=b,filetype='pdf');text='\n'.join(p.get_text() for p in doc);(ROOT/'extracts'/f'{key}.txt').write_text(text)
  pdfs[key]={'pages':len(doc),'metadata':doc.metadata,'page_sizes_points':[list(p.rect) for p in doc],'text_chars':len(text),'preview':f'previews/{key}.png','type':'original PDF; preview raster only','status':'scope manually reviewed in visual-review.md'}
  for n,page in enumerate(doc):
   z=500/max(page.rect.width,page.rect.height);pix=page.get_pixmap(matrix=fitz.Matrix(z,z),alpha=False);im=Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB');canvas=Image.new('RGB',(520,550),'white');canvas.paste(im,((520-im.width)//2,25));ImageDraw.Draw(canvas).text((12,525),f'{key} page {n+1}/{len(doc)}',fill='black');items.append(canvas)
   if n==0:
    z=1400/max(page.rect.width,page.rect.height);page.get_pixmap(matrix=fitz.Matrix(z,z),alpha=False).save(ROOT/'previews'/f'{key}.png')
 for n in range(0,len(items),9):
  canvas=Image.new('RGB',(1560,1650),'#ddd')
  for m,im in enumerate(items[n:n+9]):canvas.paste(im,((m%3)*520,(m//3)*550))
  canvas.save(ROOT/'previews'/f'pdf-contact-{n//9:02}.jpg',quality=88)
 dump(ROOT/'extracts/pdf-metadata.json',pdfs)
 # Derived source-status inventory preserves failures and wrong-scope successful bodies.
 statuses=[]
 for key,r in records.items():
  s={'capture_id':key,'requested_url':r['requested_url'],'final_url':r.get('final_url'),'http_status':r.get('status'),'parent_capture_id':r.get('parent_capture_id'),'retrieved_utc':r['retrieved_utc'],'purpose':r['purpose'],'source_clock_and_status':'HTTP clocks in acquisition; election effective/approval status not inferred','source_status':'retrieved reference evidence' if r.get('status')==200 else 'failed original; retained separately'}
  if key in ['pott-legislative-pdf','sumner-diff-service','shawnee-curve-preview']:s['source_status']='Excluded as qualified precinct geometry: legislative map / point-only differences / provisional preview query respectively'
  if key.startswith('wyandotte-features'):s['source_status']='Attributes-only service response; no returned geometry; not a geometry asset'
  if r.get('storage'):
   try:
    body=json.loads(read(r))
    if isinstance(body,dict) and 'error' in body:s['source_status']='HTTP200 API error body; excluded as data'
   except (ValueError,UnicodeDecodeError):pass
  if key in ['ellis-city-pdf','ellis-victoria-pdf','barton-hoisington-pdf','barton-county-pdf']:s['source_status']='Limited city/ward/polling-area context; not proof of complete precinct equivalence'
  statuses.append(s)
 dump(ROOT/'source-status.json',statuses)
 # Offline index uses only relative local assets, no online basemap/library.
 def download_links(asset):
  if asset in data:
   ss=next((s for s in services if s['id']==asset),None)
   if ss:return '<details><summary>Native original response downloads</summary>'+''.join(download_links(p) for p in ss['pages'])+'</details>'
  r=records.get(asset)
  if not r or not r.get('storage'):return ''
  out=[]
  for part in r['storage']['ordered_parts']:
   out.append(f'<a download href="{esc(part["path"])}">{esc(asset)} ({esc(r["storage"]["encoding"])}, {part["bytes"]:,} bytes)</a>')
  return '<p>'+ '<br>'.join(out)+'</p>'
 cards=[]
 for c in counties[:23]:
  n=c['local'];assets=n['assets'];main=next((pdfs[a]['preview'] for a in assets if a in pdfs),None) or next((previews[a]['path'] for a in assets if a in previews),None) or c['state_2022_preview']
  source='County/reference asset' if assets else '2022 state reference; current county gap'
  if c['county']=='Barton':source='Great Bend city map; county current scope gap'
  if c['county']=='Cowley':source='Archived county-produced PDF; historical reference'
  cards.append(f'<article class="card" id="{c["county_fips"]}" data-county-key="{c["county_key"]}" data-search="{esc(c["county"].lower())}"><h2>{c["rank"]}. {esc(c["county"])} <small>{c["county_fips"]}</small></h2><span class="badge">Reference; November approval unavailable</span><a href="{main}"><img loading="lazy" src="{main}" alt="{esc(c["county"])} actual map preview"/></a><p class="caption">{source}. Open preview for detail.</p><p>{esc(n["scope"])}</p><p><b>Vintage:</b> {esc(n["vintage"])}</p><p class="gap"><b>Gap:</b> {esc(n["gaps"])}</p>'+''.join(download_links(a) for a in assets)+f'<details><summary>Complete official KLRD2022 county reference: {c["state_2022_feature_count"]} source polygons</summary><a href="{c["state_2022_preview"]}"><img loading="lazy" src="{c["state_2022_preview"]}" alt="2022 reference for {esc(c["county"])}"/></a><p>Original native state pages stored once; full county FID list in inventory.json. No current equivalence assumed.</p><a href="#state-downloads">Original state downloads</a></details><p><a download href="{c["native_context"]}">Full five historical native source families</a> · <a href="extracts/map-feature-attributes.json.gz">All map attributes</a></p></article>')
 rows=[]
 for c in counties:
  counts=' / '.join(str(x['count']) for x in c['native_families']);unknowns=' / '.join(str(x['unknown_count']) for x in c['native_families'])
  rows.append(f'<tr data-search="{esc(c["county"].lower())}"><td>{c["rank"]}</td><th>{esc(c["county"])}</th><td>{c["county_fips"]}</td><td>{"priority" if c["priority"] else "state reference"}</td><td><a href="{c["native_context"]}" download>{counts}</a></td><td>{unknowns}</td><td><a href="{c["state_2022_preview"]}">{c["state_2022_feature_count"]}</a></td><td>{esc(c["local"]["gaps"])}</td></tr>')
 styles='body{font:16px/1.55 system-ui,sans-serif;color:#193244;background:#eff4f6;margin:0}main{max-width:1450px;margin:auto;padding:30px}h1{font-size:36px;line-height:1.12}a{color:#145e92}p{max-width:110ch}input{padding:12px;font:inherit;width:min(90%,500px)}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:22px}.card{background:white;border:1px solid #c5d1d8;border-radius:10px;padding:20px}.card h2{margin:0 0 8px}.card img{width:100%;height:330px;object-fit:contain;background:#f7fafb;margin-top:15px}.card small{font-size:14px;color:#526774}.badge{background:#e6eef7;color:#244d70;padding:5px 9px;font-size:12px;border-radius:4px}.gap{border-left:3px solid #ad7042;padding-left:12px}.caption{font-size:13px;color:#526774}table{border-collapse:collapse;min-width:1100px;font-size:13px;background:white}td,th{border:1px solid #b8c8d1;padding:9px;text-align:left;vertical-align:top}section{margin:35px 0}.scroll{overflow:auto}details{padding:10px 0}summary{cursor:pointer}code{font-size:13px}header{background:#173d52;color:white;padding:25px}header a{color:#d8efff}'
 content='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kansas precinct map reference library</title><style>'+styles+'</style><header><main><h1>Kansas precinct map reference library</h1><p>Exact ordered 23-county research priority · all 105 counties · 22,031 historical source identities retained.</p><p>Downloaded full native geometry and original PDFs. Reference vintages stay separate from November 3, 2026 approval. No votes are assigned to polygons.</p></main></header><main><p>The 23 research counties account for 1,067,659 of 1,327,591 four-ticket 2024 presidential votes (80.4207771821%). This measures historical volume, not geographic approval. The 2022 state layer is a full native reference covering all 105 counties, with 4,749 source polygons. County map units and five historical result families overlap and are never summed.</p><p><a href="../precinct-maps.md">Research report</a> · <a href="SCHEMA.md">Schema/reproduction</a> · <a href="inventory.json">Exact scope and gaps</a> · <a href="acquisition.json">Original acquisition metadata</a> · <a href="visual-review.md">Visual inspection</a></p><label>Filter county <input id="filter" placeholder="County name" type="search"></label><section class="cards" id="priority-cards">'+''.join(cards)+'</section><section id="state-downloads"><h2>Complete state original downloads</h2><p>KLRD explicitly describes 2022 post-redistricting precincts; counties can subsequently rename/recombine/change them. Native coordinates, VTD fields and source objects are retained. These polygons do not establish 2024 or 2026 physical equivalence.</p>'+download_links('klrd-2022')+'</section><section><h2>All 105 county inventory</h2><p>Historical family order: broader2024 / alternative2024 precinct / Senate2022 / Senate2020 / Senate primary2026. These are overlapping historical publication families. Unknown-count units are retained, not zero. Every linked county native file contains the complete unchanged source contract object and all constituents.</p><div class="scroll"><table id="inventory"><thead><tr><th>Rank</th><th>County</th><th>FIPS</th><th>Scope</th><th>Native family counts</th><th>Unknown-count units</th><th>2022 map polygons</th><th>Current/local gaps</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div></section><p>Offline only. PNG/SVG images are display derivatives. Original PDF, ZIP and Esri JSON response bytes are authoritative. Reconstruct gzip/ordered parts with reconstruct.py; see SCHEMA.md. No external basemap, geocoding or network requests are used by this index.</p></main><script>document.getElementById("filter").addEventListener("input",e=>{const q=e.target.value.toLowerCase();document.querySelectorAll("[data-search]").forEach(x=>x.hidden=!x.dataset.search.includes(q))});</script></html>'
 (ROOT/'index.html').write_text(content)
 dump(ROOT/'build-summary.json',{'counties':105,'ordered_priority_count':23,'native_identities':native_total,'historical_families':dict(family_counts),'unknown_count_units':dict(unknown),'state_reference_polygons':4749,'state_reference_vertices':geom['klrd-2022']['vertices'],'state_reference_invalid':len(geom['klrd-2022']['invalid']),'county_geometry_sources':{k:{'features':d['features'],'null_geometry':len(d['null_geometry']),'invalid_XY':len(d['invalid']),'true_curve_features':len(d['curve_geometry']),'overlap_pairs_valid_XY':len(d['valid_pair_overlap']),'area_units':d['area_units']} for k,d in geom.items() if k!='klrd-2022'},'pdf_assets':len(pdfs),'pdf_pages_rendered':len(items),'contact_sheets':(len(items)+8)//9,'native_crosswalk_approved':False,'november_boundary_approval':False,'unrepaired_originals':True})
 print('Built',len(counties),'counties;',native_total,'native contexts;',len(pdfs),'PDFs',len(items),'pages; state4749 native polygons')
if __name__=='__main__':run()
