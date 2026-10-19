"""Deterministic offline map atlas/index; --check compares bytes without writing."""
import collections,gzip,html,io,json,pathlib,re,sys,zipfile
import fitz
from acquire import ROOT,body,sha
from geometry import zip_shapes,audit_shp
from service_audit import run as services
from conservation import run as conservation
CHECK='--check'in sys.argv
OUTPUTS=[]
def put(path,b):
 p=ROOT/path;b=b.encode() if isinstance(b,str) else b
 assert len(b)<40000000,(path,len(b));OUTPUTS.append(path)
 if CHECK:assert p.read_bytes()==b,('replay differs',path)
 else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def js(v):return json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def esc(s):return html.escape(str(s),quote=True)
def slug(s):return s.lower().replace(' ','-')
def preview(name,title,features,subtitle):
 points=[p for s,a in features for p in s.points]
 if not points:return None
 xmin=min(p[0] for p in points);xmax=max(p[0] for p in points);ymin=min(p[1] for p in points);ymax=max(p[1] for p in points)
 scale=min(1000/(xmax-xmin),660/(ymax-ymin));tx=50+(1000-(xmax-xmin)*scale)/2-xmin*scale;ty=110+(660-(ymax-ymin)*scale)/2+ymax*scale
 paths=[]
 for s,a in features:
  pathsrc=[]
  for left,right in zip(list(s.parts),list(s.parts)[1:]+[len(s.points)]):
   ring=s.points[left:right]
   if ring:pathsrc.append('M'+' L'.join(repr(float(p[0]))+','+repr(float(p[1])) for p in ring))
  label=next((str(a[k]) for k in ['NAME20','Precinct','PRECINCT','PRECINCTID','PRECINCT_ID','NAME','precinctid'] if k in a),str(a))
  paths.append('<path d="'+esc(' '.join(pathsrc))+'"><title>'+esc(label)+'</title></path>')
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="850" viewBox="0 0 1100 850"><rect width="1100" height="850" fill="#faf9f5"/><g font-family="Arial" fill="#172d3a"><text x="40" y="42" font-size="26">'+esc(title)+'</text><text x="40" y="70" font-size="15">'+esc(subtitle)+'</text><text x="40" y="810" font-size="14">'+esc(str(len(features))+' features | native coordinates; preview only | no reporting-row/current/legal crosswalk')+'</text></g><g transform="translate('+repr(tx)+' '+repr(ty)+') scale('+repr(scale)+' '+repr(-scale)+')" fill="#cadde1" fill-rule="evenodd" stroke="#254c5e" stroke-width="'+repr(0.7/scale)+'">'+''.join(paths)+'</g></svg>'
 put('previews/'+name+'.svg',svg)
 doc=fitz.open(stream=svg.encode(),filetype='svg');png=doc[0].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).tobytes('png');put('previews/'+name+'.png',png)
 return dict(svg='previews/'+name+'.svg',png='previews/'+name+'.png',features=len(features),bbox=[xmin,ymin,xmax,ymax],native_source_point_count=len(points),precision_policy='every source XY position retained in SVG path in source parts/order; affine preview transform only; source geometry unchanged; no line auto-close constructor')

def run():
 con,c=conservation();auth=json.loads((ROOT/'authorities.json').read_text());bycounty={a['county']:a for a in auth};receipts={f.name.removesuffix('.receipt.json'):json.loads(f.read_text()) for f in sorted((ROOT/'raw').glob('*.receipt.json'))}
 def countyof(k):
  if k.startswith('county-'):
   for a in sorted(auth,key=lambda x:-len(slug(x['county']))):
    if k.startswith('county-'+slug(a['county'])):return a['county']
  for n in ['adams','arapahoe','archuleta','boulder','broomfield','douglas','eagle','el-paso','fremont','garfield','jefferson','larimer','weld']:
   if k.startswith(n+'-'):return next((a['county'] for a in auth if slug(a['county'])==n),None)
  p=receipts.get(k,{}).get('parent');return countyof(p) if p in receipts and p!=k else None
 maps=[];rendercoverage=[];contacttext=''
 for k,r in receipts.items():
  if r['status']!=200:continue
  raw=body(k);candidates=[]
  if raw.startswith(b'%PDF'):candidates=[(k,raw,None)]
  elif raw.startswith(b'PK'):
   z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
   candidates=[(k+'-'+str(i),z.read(n),n) for i,n in enumerate(z.namelist()) if n.lower().endswith('.pdf')]
  for assetid,b,member in candidates:
   assert len(b)<40000000
   doc=fitz.open(stream=b,filetype='pdf');texts=[p.get_text() for p in doc];text='\n\n'.join(texts)
   put('assets/'+assetid+'.pdf',b);put('assets/'+assetid+'.txt.gz',gzip.compress(text.encode(),mtime=0))
   records=[]
   for i,p in enumerate(doc):
    # Automatic whole-page render of every acquired PDF page; visual inspection scope recorded separately.
    scale=min(900/p.rect.width,900/p.rect.height);pix=p.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False);path='previews/'+assetid+'-page-'+str(i+1).zfill(3)+'.png';put(path,pix.tobytes('png'));records.append(path)
   item=dict(id=assetid,county=countyof(k),source=k,zip_member=member,path='assets/'+assetid+'.pdf',bytes=len(b),sha256=sha(b),pages=len(doc),pdf_metadata=doc.metadata,page_sizes_points=[[p.rect.width,p.rect.height] for p in doc],source_text='assets/'+assetid+'.txt.gz',page_previews=records,crs='not asserted from PDF; printed grid/map metadata retained in original',finer_ID_match=False,current_legal_match=False,purpose='shared county cartographic research reference; no leaf allocation',vintage_qualification='printed text and PDF metadata retained; creation/download dates do not establish November2026 legal boundary vintage')
   if k=='sos-clerk-roster':item['purpose']='all64 county election contact roster';contacttext=text
   item['county_source_qualification']=json.loads((ROOT/'source-qualifications.json').read_text()).get(item['county'],'See source text; vintage unresolved')
   item['renderer_warnings']=fitz.TOOLS.mupdf_warnings()
   maps.append(item);rendercoverage.append(dict(source=k,member=member,pages=len(doc),rendered_whole_pages=len(records),human_visual_review='see qa/visual-review.json; automatic render is not human inspection'))
 put('pdf-assets.json',js(maps));put('qa/pdf-render-coverage.json',js(rendercoverage));put('contacts.txt',contacttext)
 # One original Census ZIP; county previews are derivatives, not duplicate statewide assets.
 census=[]
 for name,f in zip_shapes('census-co-vtd'):
  audit,census=audit_shp('census-co-vtd',name,f)
 grouped=collections.defaultdict(list)
 for s,a in census:grouped[a['COUNTYFP20']].append((s,a))
 previews={};parents=[];qualifications=json.loads((ROOT/'source-qualifications.json').read_text())
 for a,h,par in zip(auth,c['county_native_hierarchy'],c['county_parents']):
  assert a['county']==h['county']==par['county_literal'];n=a['county'];fips=a['county_fips'];features=grouped[fips[2:]]
  previews[n]=preview('census-'+slug(n),n+' | Census 2020 VTD',features,'Historical Census reference; complete parent subset; no 2024/2026 precinct match')
  r=receipts.get(a['acquisition_id']);pdfs=[m['id'] for m in maps if m['county']==n]
  parents.append(dict(**a,full_source_parent_ref=dict(path='../data/turnout/priority-set.json',pointer='/county_parents/'+str(len(parents))),full_source_hierarchy_ref=dict(path='../data/turnout/priority-set.json',pointer='/county_native_hierarchy/'+str(len(parents))),source_all_native_keys=h['all_native_keys'],source_priority_native_keys=[k for k in c['ordered_priority_keys'] if k in set(h['all_native_keys'])],derived_remainder_native_keys=[k for k in h['all_native_keys'] if k in set(c['ordered_remainder_keys'])],remainder_provenance='derived from complete source full child/global remainder keys; original hierarchy did not contain remainder field',authority_http_status=r['status'] if r else 'not requested; nonpriority authority directory retained',county_pdf_assets=pdfs,county_source_qualification=qualifications.get(n,'Bounded authority request retained; acquired county precinct geometry unresolved. Historical Census parent reference available.'),census_reference=dict(source='census-co-vtd',vintage='2020 Census TIGER2020PL VTD20; published archive2021',county_field='COUNTYFP20',county_value=fips[2:],feature_count=len(features),crs_wkt=audit['crs_wkt'],preview=previews[n],source_receipt='raw/census-co-vtd.receipt.json',purpose='shared-parent historical geographic reference only; FIPS selects Census county context, never a reporting-leaf polygon join',finer_ID_match=False,current_physical_match=False,legal_match=False),gaps='No verified source-native2024 or current2026 leaf-to-boundary crosswalk; no central/administrative ballot spatial allocation; county assets can have different vintage/ID/coverage. Census-only where acquired county assets absent.'))
 sa,st,natives=services();native_previews={}
 for k,v in natives.items():native_previews[k]=preview(k,k+' | source-native precinct layer',v,'Linear preview only; '+str(len(next(x for x in sa if x['source']==k)['true_curve_features']))+' curve features excluded; all originals retained')
 for p in parents:p['native_layer_references']=[dict(source=x['source'],features=x['feature_count'],crs=x['source_crs'],preview=native_previews[x['source']],purpose='qualified shared county native layer; source IDs preserved; no leaf/legal/current equivalence',finer_ID_match=False) for x in sa if x['county']==p['county']]
 inv=[]
 for i,row in enumerate(c['full_order']):
  p=next(p for p in parents if p['county']==row['county_literal'])
  inv.append(dict(rank=i+1,key=row['key'],county=row['county_literal'],native_id_literal=row['native_id_literal'],candidate_votes=row['candidate_votes'],priority=i<1992,full_source_object_ref=dict(path='../data/turnout/priority-set.json',pointer='/full_order/'+str(i)),qualified_parent_reference='parents.html#'+slug(p['county']),county_pdf_assets=p['county_pdf_assets'],native_shared_parent_assets=[x['source'] for x in p['native_layer_references']],historical_fallback='census-co-vtd',fallback_county_field='COUNTYFP20',fallback_county_value=p['census_reference']['county_value'],fallback_feature_count=p['census_reference']['feature_count'],fallback_crs=audit['crs_wkt'],map_reference_scope='shared-parent research reference; no leaf/map/current/legal join',leaf_geometry_match=False,current_legal_match=False))
 put('parent-inventory.json',js(parents));put('inventory.json',js(dict(acceptance_path='../data/coordinator-priority-acceptance.json',contract_reference='../data/turnout/priority-set.json',ordered_priority_keys=c['ordered_priority_keys'],ordered_remainder_keys=c['ordered_remainder_keys'],all3199=inv)))
 put('native-previews.json',js(native_previews));put('qa/render-environment.json',js(dict(fitz=fitz.VersionBind,svg_crs='native affine transform only',automatically_rendered_census_counties=64,automatically_rendered_native_layers=4,visual_review='separate selected images; browser not used')))
 css='body{font:16px system-ui;margin:30px auto;max-width:1450px;padding:0 20px;color:#172d3a;background:#faf9f5}a{color:#14516c}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:8px;border-bottom:1px solid #bdcbd0;text-align:left;vertical-align:top}th{background:#e2edf0;position:sticky;top:0}button,input{padding:9px;margin:5px}img{max-width:100%}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:22px}.note{background:#e2edf0;padding:18px}details{margin:12px 0}code{font-size:12px}'
 def header(title):return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+title+'</title><style>'+css+'</style><body><h1>'+title+'</h1>'
 overview='<p class="note">Historical research references only. 2024 president: 3,192,745 named-ticket votes, 3,199 native observations, 64 parents. Exact 80% prefix: 1,992 / 2,554,233; remainder: 1,207 / 638,512. No current legal boundary or reporting-leaf polygon crosswalk is approved. County and Census IDs are kept separate from historical source keys.</p>'
 nav='<p><a href="atlas.html">64-county Census atlas</a> · <a href="native.html">Native county GIS</a> · <a href="pdfs.html">Acquired PDF maps</a> · <a href="parents.html">All64 authorities and hierarchy</a> · <a href="contacts.txt">Offline county contacts</a> · <a href="README.md">Methods and gaps</a></p>'
 rows=[]
 for v in inv:
  n=v['county'];p=next(x for x in parents if x['county']==n);refs='<a href="previews/census-'+slug(n)+'.svg">Census2020 parent ('+str(v['fallback_feature_count'])+' VTDs)</a>'
  refs+=''.join(' · <a href="assets/'+x+'.pdf">county PDF</a>' for x in v['county_pdf_assets'])
  refs+=''.join(' · <a href="previews/'+x+'.svg">native county GIS</a>' for x in v['native_shared_parent_assets'])
  rows.append('<tr data-priority="'+str(v['priority']).lower()+'"><td>'+str(v['rank'])+'</td><td><code>'+esc(v['key'])+'</code></td><td>'+str(v['candidate_votes'])+'</td><td>'+('priority' if v['priority'] else 'remainder')+'</td><td>'+refs+'<br>Shared parent only; leaf/current/legal match unresolved.</td><td><a href="../data/turnout/priority-set.json">full source object /full_order/'+str(v['rank']-1)+'</a></td></tr>')
 script="""<script>const rows=[...document.querySelectorAll('tbody tr')];let mode='all';function filter(){let q=document.getElementById('search').value.toLowerCase(),n=0;for(let r of rows){let ok=(mode==='all'||(mode==='priority')===(r.dataset.priority==='true'))&&r.textContent.toLowerCase().includes(q);r.hidden=!ok;n+=ok}document.getElementById('shown').textContent=n+' observations shown'}function select(m){mode=m;filter()}document.getElementById('search').addEventListener('input',filter);filter()</script>"""
 index=header('Colorado precinct-map research index')+overview+nav+'<p><button onclick="select(\'all\')">All 3,199</button><button onclick="select(\'priority\')">Exact 1,992 priority</button><button onclick="select(\'remainder\')">All 1,207 remainder</button><label>Filter <input id="search" placeholder="County or literal native ID"></label><span id="shown"></span></p><table><thead><tr><th>Rank</th><th>Full literal source key</th><th>Candidate votes</th><th>Set</th><th>Acquired qualified references</th><th>Complete source fields</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>'+script+'</body></html>'
 put('index.html',index)
 atlas=header('Colorado | Census 2020 historical VTD atlas')+overview+nav+'<p>Complete county subsets from one unmodified statewide original. These 3,108 Census VTDs are independent of the 3,199 reporting observations. Native NAD83 geographic coordinates are displayed with an affine preview transform. No candidate votes are allocated to these polygons.</p><div class="grid">'
 for p in parents:
  v=previews[p['county']];atlas+='<article><h2>'+esc(p['county'])+'</h2><a href="'+v['svg']+'"><img loading="lazy" src="'+v['png']+'" alt="'+esc(p['county'])+' Census2020 VTD preview"></a><p>'+str(v['features'])+' historical VTDs · <a href="'+v['svg']+'">full SVG</a></p></article>'
 put('atlas.html',atlas+'</div></body></html>')
 native=header('Colorado | acquired native county GIS')+overview+nav
 for a in sa:
  v=native_previews[a['source']];native+='<h2>'+esc(a['county'])+' | '+str(a['feature_count'])+' source features</h2><a href="'+v['svg']+'"><img src="'+v['png']+'" alt="Native '+esc(a['county'])+' precinct map"></a><p>All native fields, coordinates, ring parts, IDs, CRS and source order retained in complete raw pages. <a href="raw/'+a['source']+'.service.json">Capture / pages</a> · <a href="'+v['svg']+'">SVG</a>. Shared-parent reference; no historical/current leaf match. True-curve features excluded from this linear preview: '+str(len(a['true_curve_features']))+'.</p>'
 put('native.html',native+'</body></html>')
 pdfhtml=header('Colorado | downloaded county map originals')+overview+nav
 for m in maps:
  pdfhtml+='<details><summary>'+esc(m['county'] or 'Statewide contacts')+' | '+esc(m['id'])+' | '+str(m['pages'])+' pages</summary><p><a href="'+m['path']+'">Complete original PDF</a> · '+str(m['bytes'])+' bytes · SHA256 <code>'+m['sha256']+'</code></p><p>'+esc(m['county_source_qualification']+' '+m['vintage_qualification'])+'</p>'
  for v in m['page_previews']:pdfhtml+='<a href="'+v+'"><img loading="lazy" width="360" src="'+v+'" alt="Automatic whole-page preview '+esc(v)+'"></a>'
  pdfhtml+='</details>'
 put('pdfs.html',pdfhtml+'</body></html>')
 parenthtml=header('Colorado | all64 authority and source-parent inventory')+overview+nav
 for p in parents:
  parenthtml+='<details id="'+slug(p['county'])+'"><summary>'+esc(p['county'])+' | '+str(len(p['source_all_native_keys']))+' full / '+str(len(p['source_priority_native_keys']))+' priority / '+str(len(p['derived_remainder_native_keys']))+' remainder</summary><p><a href="'+esc(p['authority_url'])+'">Official authority</a> · observed HTTP '+esc(p['authority_http_status'])+' · <a href="assets/sos-clerk-roster.pdf">downloaded statewide contact roster</a></p><p>'+esc(p['gaps'])+'</p><p>Full parent and hierarchy retained in <a href="../data/turnout/priority-set.json">complete frozen contract</a>; derived remainder arrays in <a href="parent-inventory.json">parent inventory</a>.</p><pre>'+esc(js(p))+'</pre></details>'
 put('parents.html',parenthtml+'</body></html>')
 return dict(outputs=OUTPUTS,pdf_originals=len(maps),pdf_pages=sum(m['pages'] for m in maps),county_pdf_parents=len(set(m['county'] for m in maps if m['county'])),native_service_features=sum(x['feature_count'] for x in sa),census_features=len(census),observations=len(inv),priority_observations=1992,remainder_observations=1207,parents=64)
if __name__=='__main__':
 result=run();put('qa/build-summary.json',js(result));print(json.dumps({k:v for k,v in result.items() if k!='outputs'}))
