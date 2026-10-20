"""Deterministic offline atlas: full source observations, no geometry matches or votes allocation."""
from common import *
from acquire import body
from collections import defaultdict
import html,re,io,zipfile,fitz

def h(s):return html.escape(str(s),quote=True)
def svg_county(d):
 records=d['records'];boxes=[r['bbox'] for r in records if r['bbox']]
 xmin=min(b[0] for b in boxes);ymin=min(b[1] for b in boxes);xmax=max(b[2] for b in boxes);ymax=max(b[3] for b in boxes)
 w=xmax-xmin;he=ymax-ymin;pad=max(w,he)*.02
 out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{xmin-pad} {-ymax-pad} {w+2*pad} {he+2*pad}" width="900" height="900"><title>{d["source_county_fips"]}: historical 2020 Census VTDs; no source observation join</title><rect x="{xmin-pad}" y="{-ymax-pad}" width="{w+2*pad}" height="{he+2*pad}" fill="white"/><g transform="scale(1,-1)" stroke="#285468" stroke-width="{max(w,he)/1900}" fill="#e2edf0" fill-rule="evenodd">']
 for r in records:
  paths=[];pts=r['points'];parts=r['parts']
  for j,start in enumerate(parts):
   ring=pts[start:parts[j+1] if j+1<len(parts) else len(pts)]
   if ring:paths.append('M'+' L'.join(str(x)+','+str(y) for x,y in ring))
  out.append('<path d="'+' '.join(paths)+'"><title>'+h(r['attributes']['GEOID20']+' '+r['attributes']['NAME20'])+'</title></path>')
 out.append('</g></svg>');return ''.join(out)

def pdf_inventory():
 out=[]
 for p in sorted((M/'source').glob('authority-*.receipt.json')):
  r=load(p)
  if '-asset-' not in r['id'] and not r['id'].endswith('-supplement'):continue
  b=body(r);row=dict(receipt='maps/source/'+p.name,status=r['status'],literal_href=r['literal_href'],format=None,visual_inspection_record='maps/qa/visual-review.json; this automatic inventory makes no visual claim')
  if b.startswith(b'%PDF'):
   doc=fitz.open(stream=b,filetype='pdf');row.update(format='PDF',pages=len(doc),metadata=doc.metadata,page_boxes=[list(page.rect) for page in doc],full_original_pages_preserved=True)
   # Full text of every page is derivative evidence, never a visual inspection claim.
   texts=[dict(page_1based=i+1,text=page.get_text()) for i,page in enumerate(doc)]
   dump('derived/pdf-text/'+r['id']+'.json.gz',texts)
   found=[]
   for x in texts:
    for match in re.findall(r'(?i)(?:revised|updated|effective|prepared|date|election|copyright)[^\n]{0,100}|\b(?:19|20)\d{2}\b',x['text']):
     if match not in found:found.append(match)
   row['vintage_text_fragments_uninterpreted']=found
   if r['id'] in ['authority-1-asset-0','authority-16-asset-0','authority-88-asset-0','authority-105-asset-0','authority-110-asset-0','authority-16-supplement','authority-104-supplement','authority-110-supplement']:
    for index in sorted({0,len(doc)-1}):
     pix=doc[index].get_pixmap(matrix=fitz.Matrix(1,1));name='qa/'+r['id']+'-page-'+str(index+1)+'.png';pix.save(M/name)
    row['automatic_rendered_pages_1based']=sorted({1,len(doc)})
  elif b[:2]==b'PK':
   row['format']='ZIP';z=zipfile.ZipFile(io.BytesIO(b));row['members']=[dict(name=i.filename,bytes=i.file_size,crc32=f'{i.CRC:08x}',sha256=sha(z.read(i))) for i in z.infolist()]
  elif b:
   from PIL import Image
   try:
    im=Image.open(io.BytesIO(b));row.update(format=im.format,pixels=list(im.size),mode=im.mode,metadata={k:str(v) for k,v in im.info.items()})
   except Exception:row.update(format='other',first_32_bytes_hex=b[:32].hex())
  out.append(row)
 dump('derived/original-asset-inventory.json',out);return out

def main():
 a=load(S/ACCEPTANCE);p=json.loads(exact(a['frozen_contract']));invest=load(M/'derived/authority-investigations.json')
 by_auth={x['authority_id']:x for x in invest};assert len(by_auth)==108
 assets=pdf_inventory();assetby={x['receipt']:x for x in assets}
 units={x['key']:x for x in p['native_constituents']};assert len(units)==10062
 order=p['full_order'];assert len(order)==10062 and order[:5540]==p['ordered_priority_keys'] and order[5540:]==p['remainder_keys']
 selected=set(p['ordered_priority_keys']);children=defaultdict(list);prioritychildren=defaultdict(list);remainderchildren=defaultdict(list);index=[]
 for rank,key in enumerate(order,1):
  u=units[key];id=u['authority_id'];children[id].append(key)
  (prioritychildren if key in selected else remainderchildren)[id].append(key)
  auth=next(x for x in p['authority_inventory'] if x['authority_id']==id);research=by_auth[id]
  gaps=['Source observation is not a physical precinct identifier; no label/count/spatial crosswalk made.','2020 Census VTD vintage precedes 2024 source and 2026 election; finer and current identity unverified.','County FIPS is a geographic fallback locator, never a replacement for the county/city reporting authority.']
  if u['administrative_only']:gaps.append('Administrative-only pool: no physical polygon assigned; named pool remains null.')
  if re.search(r'STYLE|FED|CENTRAL|PRESIDENTIAL|ABSENT|EARLY',u['precinct_name_literal'],re.I):gaps.append('Special-looking literal label retained; no administrative/method classification or physical polygon inferred.')
  if research.get('original_access_gap'):gaps.append(research['original_access_gap'])
  if not research['archive_files']:gaps.append('Observed authority archive folder contains no linked map assets; historical Census county-context fallback only.')
  else:gaps.append('State archive assets have incomplete/unverified historical/current scope; selected PDF sample does not establish every child boundary.')
  if u['missing_printed_candidate_rows']:gaps.append('Absent printed candidate rows stay null: '+', '.join(u['missing_printed_candidate_rows']))
  originals=[]
  for rp in research['selected_asset_receipts']:
   receipt=load(S/rp);asset=assetby[rp]
   originals.append(dict(receipt=rp,literal_href=receipt['literal_href'],url=receipt['requested_url'],status=receipt['status'],complete_entity_acquired=True,publisher_http_clocks=receipt['publisher_clock'],vintage_text_fragments_uninterpreted=asset.get('vintage_text_fragments_uninterpreted',[]),pdf_metadata=asset.get('metadata'),pdf_pages=asset.get('pages'),asset_inventory_reference='maps/derived/original-asset-inventory.json'))
  row=dict(rank_full=rank,rank_priority=rank if rank<=5540 else None,key=key,priority=rank<=5540,source_observation=u,authority_key=auth['key'],county_fips_locator=auth['county_fips'],authority_archive_receipt=research['archive_receipt'],authority_map_asset_receipts=research['selected_asset_receipts'],authority_complete_original_assets=originals,authority_leaf_access_receipts=research.get('leaf_access_receipts',[]),authority_original_vintage='See complete map metadata, filename and uninterpreted text fragments; directory modification dates do not establish boundary vintage',fallback_slice='maps/derived/counties/'+auth['county_fips']+'.native.json.gz',fallback_preview='maps/derived/previews/'+auth['county_fips']+'.svg',map_support='shared historical geographic context only',matched_geometry=None,physical_polygon=None,source_method=None,gaps=gaps)
  index.append(row)
 dump('derived/full-inventory.json.gz',index);dump('derived/priority-index.json.gz',index[:5540]);dump('derived/remainder-index.json.gz',index[5540:])
 parents=[]
 for auth in p['authority_inventory']:
  id=auth['authority_id'];parents.append(dict(source_parent=auth,all_children_source_order=auth['native_constituent_keys'],all_children_rank_order=children[id],ordered_priority_children=prioritychildren[id],ordered_remainder_children=remainderchildren[id],investigation=by_auth[id],county_geographic_fallback_is_not_reporting_parent=True))
 dump('derived/parents.json.gz',parents)
 assert len(parents)==108 and sum(bool(x['ordered_priority_children']) for x in parents)==97
 county=[]
 for path in sorted((M/'derived/counties').glob('*.json.gz')):
  d=load(path);fips=d['source_county_fips'];svg=svg_county(d);pr=M/'derived/previews'/f'{fips}.svg';pr.parent.mkdir(exist_ok=True);pr.write_text(svg)
  county.append(dict(fips=fips,records=len(d['records']),slice='maps/'+str(path.relative_to(M)),preview='maps/'+str(pr.relative_to(M)),source_record_positions=[r['source_record_1based'] for r in d['records']],source='maps/source/census-illinois-vtd2020.receipt.json',vintage='2020',current_approved=False))
 dump('derived/county-fallback-index.json',county)
 for fips in ['17031','17019','17163','17197']:
  doc=fitz.open(stream=(M/'derived/previews'/f'{fips}.svg').read_bytes(),filetype='svg');doc[0].get_pixmap().save(M/'qa'/f'county-{fips}-affine.png')
 # Self-contained HTML with the entire exact 5540 priority order, all 10062 inventory,
 # all108 parents/children; no fetch/CDN/dependency needed, SVG previews use local links.
 compact=[]
 for r in index:
  u=r['source_observation'];compact.append(dict(source_observation=u,rank=r['rank_full'],key=r['key'],authority=u['authority_id'],name=u['authority_name'],label=u['precinct_name_literal'],votes=u['printed_observed_sum'],administrative_only=u['administrative_only'],missing=u['missing_printed_candidate_rows'],fips=r['county_fips_locator'],gaps=r['gaps']))
 data=json.dumps(compact,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
 parentdata=json.dumps(parents,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
 template='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Illinois historical source observation atlas</title><style>body{font:16px system-ui;margin:24px;color:#183741;max-width:1400px}a{color:#125b84}button,select,input{font:inherit;padding:6px}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ccd6d8;padding:5px;text-align:left}#preview{width:500px;height:500px;object-fit:contain;float:right}details{margin:12px 0}#scope{max-width:850px}.gap{color:#88421d}code{word-break:break-all}tbody tr:hover{background:#eaf1f3}</style><h1>Illinois historical source observation atlas</h1><p id="scope">Primary: 2024 president, printed-known records. 5,540 ordered observations / 4,474,312 votes of 5,592,368. All 10,062 observations and all 108 historical source authorities remain here. Maps supply shared historical geographic context. <b>No observation has an assigned polygon.</b> County VTD slices are 2020 Census geography; no current, legal or election-night crosswalk is approved.</p><p><a href="../precinct-maps.md">Research report</a> · <a href="SCHEMA.md">Schema</a> · <a href="derived/county-fallback-index.json">102-county fallback index</a></p><label>View <select id="mode"><option value="priority">5,540 priority — exact accepted order</option><option value="all">10,062 full inventory</option><option value="remainder">4,522 remainder</option></select></label> <label>Authority <select id="authority"><option value="">All108</option></select></label> <label>Literal label filter <input id="query"></label><p id="count"></p><img id="preview" alt="Selected county historical VTD affine preview"><div id="detail"><p>Select a row for the complete observation and map gaps.</p></div><table><thead><tr><th>Full rank</th><th>Source authority</th><th>Literal source label</th><th>Printed-known votes</th></tr></thead><tbody id="rows"></tbody></table><details><summary>All108 complete source parent/child arrays</summary><pre id="parents"></pre></details><script>const records=DATA;const parents=PARENTDATA;const el=id=>document.getElementById(id);const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));for(const p of parents){const a=p.source_parent;el('authority').add(new Option(a.authority_id+' '+a.name,a.authority_id));}el('parents').textContent=JSON.stringify(parents,null,2);function show(r){el('preview').src='derived/previews/'+r.fips+'.svg';const p=parents.find(p=>p.source_parent.authority_id===r.authority);el('detail').innerHTML='<h2>'+esc(r.name)+' — '+esc(r.label)+'</h2><p><code>'+esc(r.key)+'</code></p><p>Historical county-context locator '+r.fips+'; physical polygon: null.</p><p class="gap">'+r.gaps.map(esc).join('<br>')+'</p><p><a href="derived/counties/'+r.fips+'.native.json.gz">Exact native county VTD slice</a></p><p>Original archive receipts: '+p.investigation.selected_asset_receipts.map(x=>'<a href="'+esc(x.replace('maps/',''))+'">'+esc(x.split('/').pop())+'</a>').join(' · ')+'</p><details><summary>Complete original source observation object</summary><pre>'+esc(JSON.stringify(r.source_observation,null,2))+'</pre></details>';}function render(){const mode=el('mode').value,a=el('authority').value,q=el('query').value.toLowerCase();const rows=records.filter(r=>(mode==='all'||(mode==='priority'?r.rank<=5540:r.rank>5540))&&(!a||r.authority===a)&&r.label.toLowerCase().includes(q));el('count').textContent=rows.length+' observations shown in original full-order sequence';el('rows').innerHTML=rows.map(r=>'<tr data-rank="'+r.rank+'"><td>'+r.rank+'</td><td>'+esc(r.authority+' '+r.name)+'</td><td>'+esc(r.label)+'</td><td>'+(r.votes===null?'null':r.votes)+'</td></tr>').join('');for(const row of el('rows').children)row.onclick=()=>show(records[Number(row.dataset.rank)-1]);}for(const id of ['mode','authority','query'])el(id).oninput=render;render();show(records[0]);</script></html>'''
 atlas=template.replace('PARENTDATA',parentdata).replace('DATA',data)
 assert len(atlas.encode())<40000000
 (M/'atlas.html').write_text(atlas)
 dump('qa/build-summary.json',dict(full_inventory=len(index),priority=len(index[:5540]),remainder=len(index[5540:]),parents=108,priority_parents=97,county_slices=102,source_geometry_matches=0,pdf_originals=sum(x['format']=='PDF' for x in assets),pdf_pages=sum(x.get('pages',0) for x in assets),native_arcgis_layers_acquired=0,source_approval=False))
 print('built',len(index),len(parents),len(county))
if __name__=='__main__':main()
