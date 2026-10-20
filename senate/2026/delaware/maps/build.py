"""Deterministic offline atlas/index. No network, source allocation or leaf join."""
from common import *
import collections,csv,html,io,math,re,struct,zipfile
E=html.escape

def textfile(p,s):
 b=s.encode();assert len(b)<LIMIT;(M/p).parent.mkdir(parents=True,exist_ok=True);(M/p).write_bytes(b)
def linkpath(p):return str(Path(p).relative_to('maps')) if str(p).startswith('maps/') else '../'+str(p)
def reference(path,pointer=''):
 return dict(file=path,pointer=pointer,whole_body_required=True)
def svg(name,features,title):
 points=[p for f in features for r in (f.get('geometry') or {}).get('rings',[]) for p in r]
 lo=[min(p[i] for p in points) for i in [0,1]];hi=[max(p[i] for p in points) for i in [0,1]]
 scale=min(1150/(hi[0]-lo[0]),1550/(hi[1]-lo[1]));height=(hi[1]-lo[1])*scale+100;width=(hi[0]-lo[0])*scale+80
 paths=[];ringn=0;positionn=0
 for f in features:
  paths.append('<g><title>'+E(str(f['attributes']))+'</title>')
  for ring in (f.get('geometry') or {}).get('rings',[]):
   # repr(float) preserves full derived display values. Never drop/close/simplify.
   xy=' '.join(repr((p[0]-lo[0])*scale+40)+','+repr((hi[1]-p[1])*scale+60) for p in ring)
   paths.append('<polyline points="'+xy+'"/>');ringn+=1;positionn+=len(ring)
  paths.append('</g>')
 textfile(name,f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width!r} {height!r}"><rect width="100%" height="100%" fill="#fff"/><text x="20" y="25" font-family="sans-serif" font-size="16">{E(title)}</text><g fill="none" stroke="#174b6b" stroke-width="0.55">'+''.join(paths)+'</g></svg>')
 return dict(path='maps/'+name,source_positions=positionn,source_rings=ringn,affine=dict(x_scale=scale,y_scale=-scale,x_translation=40-lo[0]*scale,y_translation=60+hi[1]*scale),simplified=False,ring_reordered=False,source_crs_changed=False,coordinate_rounding=False,source_bounds=[lo,hi])

def census_features(r):
 z=zipfile.ZipFile(io.BytesIO(body(r)));shp=z.read(next(n for n in z.namelist() if n.endswith('.shp')));audit=read(M/('qa/'+r['id']+'-audit.json.gz'));fs=[]
 for rec in audit['records']:
  off=rec['shp_record_byte_offset']+8;points=[struct.unpack_from('<2d',shp,off+rec['xy_byte_offset_in_content']+16*j) for j in range(rec['positions'])];parts=rec['parts']
  fs.append(dict(attributes={f['name']:f['value'] for f in rec['fields']},geometry=dict(rings=[points[a:b] for a,b in zip(parts,parts[1:]+[len(points)])])))
 return fs

def main():
 refs=read(M/'source/frozen-references.json.gz');verify(refs['contract']);contract=read(S/refs['contract']['path'])
 receipts=[read(p) for p in sorted((M/'source').glob('*.receipt.json'))]
 native=read(M/'native-features.json.gz');source_inventory=[]
 for r in receipts:
  raw=body(r);is_pdf=raw.startswith(b'%PDF');is_zip=raw.startswith(b'PK')
  source_inventory.append(dict(id=r['id'],receipt=pin(M/'source'/f"{r['id']}.receipt.json"),url=r['url'],final_url=r['final_url'],parent_id=r.get('parent_id'),literal_href=r.get('literal_href'),status=r['status'],retrieval_utc=r['completed_utc'],source_date=r['headers'].get('Date'),last_modified=r['headers'].get('Last-Modified'),entity_bytes=r['raw_bytes'],entity_sha256=r['raw_sha256'],original=pin(S/r['asset_path']),format='PDF' if is_pdf else 'ZIP' if is_zip else r['headers'].get('Content-Type','unavailable'),access='complete original acquired' if r['status']==200 else 'request failed; preserved response/attempt',leaf_match_approved=False))
 write('source-inventory.json',source_inventory)
 outcsv=io.StringIO();cw=csv.DictWriter(outcsv,fieldnames=['id','url','retrieval_utc','format','CRS','native_feature_count','original_path','raw_bytes','raw_sha256','stored_bytes','stored_sha256','scope']);cw.writeheader()
 for r in source_inventory:
  is_native=r['id'].startswith('native-');is_census=r['id'].startswith('census-vtd-100');count=531 if r['id'] in ['native-pre-count','native-post-count'] else ''
  if r['id'].startswith('native-batch-'):count=len(read(M/('source/'+r['id']+'.receipt.json'))['requested_object_ids'])
  if is_census:count=read(M/('qa/'+r['id']+'-audit.json.gz'))['native_records']
  cw.writerow(dict(id=r['id'],url=r['url'],retrieval_utc=r['retrieval_utc'],format=r['format'],CRS='EPSG3857' if is_native else 'EPSG4269' if is_census else 'not established / non-geographic companion',native_feature_count=count,original_path=r['original']['path'],raw_bytes=r['entity_bytes'],raw_sha256=r['entity_sha256'],stored_bytes=r['original']['bytes'],stored_sha256=r['original']['sha256'],scope='Native source/reference only; no leaf or current legal identity approved'))
 textfile('manifest.csv',outcsv.getvalue())
 previews=[svg('previews/firstmap-native.svg',native['features'],'FirstMap native election districts - 531 unjoined features')]
 for r in receipts:
  if r['id'].startswith('census-vtd-100'):
   fs=census_features(r);previews.append(svg('previews/'+r['id']+'.svg',fs,r['id']+' - 2020 Census VTD, historical fallback'))
 write('previews/affine-transforms.json',previews)
 parent_names={'KENT':('kent','10001','11'),'NEW CASTLE':('newcastle','10003','01'),'SUSSEX':('sussex','10005','04')};parents=[]
 ed=next(r for r in receipts if r['id'].startswith('parent-') and '/maps/ed/'in r['url'])
 for county,(slug,fips,rd) in parent_names.items():
  anchor={'kent':'2022kc','newcastle':'2022nc','sussex':'2022sc'}[slug]
  actual=next(r for r in receipts if r['id'].startswith('parent-') and r['url'].endswith('#'+anchor))
  overview=next(r for r in receipts if r['id']=='county-'+slug+'-overview')
  parents.append(dict(county=county,fips=fips,publication_authority='Delaware Department of Elections; corresponding county Department office. County Superior Court canvass is a different role.',county_office_directory=reference('maps/source/parent-'+sha('https://elections.delaware.gov/locations.html'.encode())[:12]+'.receipt.json'),source_chain=[actual['id'],overview['id'],'firstmap-hub','firstmap-dataset','firstmap-service','native-pre-metadata','native-pre-count','native-pre-ids']+[f'native-batch-{j:02}'for j in range(1,12)]+['native-post-metadata','native-post-count','native-post-ids','census-vtd-'+fips],literal_county_directory_maps=[l for l in ed['literal_links'] if '/'+slug+'/'in l['url']],complete_contract_hierarchy=reference(refs['contract']['path'],'/county_native_hierarchy/'+county),priority_keys=[k for k in contract['ordered_priority_keys'] if k in contract['county_native_hierarchy'][county]['ordered_senate_native_keys']],full_native_keys=contract['county_native_hierarchy'][county]['ordered_senate_native_keys'],shared_state_geometry=dict(features=531,CRS='EPSG3857',native_has_county_attribute=False,vintage='template 2022; service says November 2023 update; stale Hub description refers to 2010',leaf_matches=0),downloaded_parent_PDF=dict(source_id=overview['id'],vintage='2023 directory; no printed effective date observed on the RD overview; March 8, 2023 is printed on the two separate ED examples',scope='Representative-district overview example, not whole county',georeferencing='PDF graphic; no reliable machine CRS asserted',gap='County/RD scope may cross county; District 11 header explicitly New Castle & Kent'),historical_census=dict(source_id='census-vtd-'+fips,vintage='2020 Census January 1 geography, county-based TIGER2020PL VTD20',CRS='EPSG4269 NAD83 geographic degrees',scope='all native county VTD records; finer current ED and reporting-unit match unavailable'),gaps=['Current signed November 2026 legal geometry and reporting identity dictionary not established','Shared whole-state geometry and historical Census are research references only','Administrative/statutory EDs need no physical polygon; no fabricated poll-site or board mapping']))
 write('parent-inventory.json',parents)
 parentbykey={k:p for p in parents for k in p['full_native_keys']};structure=read(S/'data/turnout/extracts/structure-2024.json');sample=read(S/'data/turnout/extracts/sample-ballot-identities.json')
 candidate_rows=read(S/'data/turnout/extracts/candidate-rows.jsonl.gz');candidate_refs=collections.defaultdict(list)
 for i,r in enumerate(candidate_rows):
  if r['year']==2024 and r['office_key']=='USSenator':candidate_refs[r['native_key']].append(dict(file='data/turnout/extracts/candidate-rows.jsonl.gz',JSONL_record=i+1,complete_body_required=True))
 rows=[]
 for i,rawrow in enumerate(contract['full_order']):
  k=rawrow['native_key'];p=parentbykey[k];adm=structure.get(k,{}).get('kind')=='statutory administrative district'
  rows.append(dict(**rawrow,observation_identity='DE|2024-11-05|USSenator|'+k,priority=i<311,county=p['county'],county_fips=p['fips'],source_contract_row=reference(refs['contract']['path'],f'/full_order/{i}'),complete_candidate_objects=candidate_refs[k],full_hierarchy=reference(refs['contract']['path'],'/county_native_hierarchy/'+p['county']),structure=reference('data/turnout/extracts/structure-2024.json','/'+k) if k in structure else None,shared_parent_research='parent-inventory.json#'+p['county'],available_geographic_references=['native-features.json.gz','source/county-'+parent_names[p['county']][0]+'-overview.receipt.json','source/census-vtd-'+p['fips']+'.receipt.json'],reference_scope='shared state/parent and historical fallback; no individual leaf match',administrative=adm,leaf_feature_ids=None,current_geography_approved=False,physical_polling_site=None,ballot_style=None,central_counting_board=None,gap='Statutory administrative ED: no physical polygon presumed' if adm else 'Finer source/current/legal identity unverified; no feature assigned'))
 assert len(rows)==530 and [r['native_key'] for r in rows[:311]]==contract['ordered_priority_keys'] and [r['native_key']for r in rows[311:]]==contract['ordered_remainder_keys']
 index=dict(schema='DE-maps-full-reference-index-v1',priority=rows[:311],all_senate=rows,remainder=rows[311:],full_parent_hierarchies=contract['county_native_hierarchy'],all_available_source_cases=reference(refs['contract']['path'],'/all_available_source_constituents'),all_available_source_cases_count=1495,administrative_cases=contract['administrative_cases'],unavailable_administrative_cases=contract['unavailable_administrative_cases'],structure_rows=reference('data/turnout/extracts/structure-2024.json'),structure_row_count=len(structure),historical_sample_identities=reference('data/turnout/extracts/sample-ballot-identities.json'),historical_sample_identities_count=len(sample),frozen_complete_references='source/frozen-references.json.gz',current_geography_approved=False,current_reporting_IDs_approved=False,collector_approved=False,probability_approved=False)
 write('index.json',index)
 out=io.StringIO();w=csv.DictWriter(out,fieldnames=['rank','native_key','votes','county','county_fips','priority','administrative','reference_scope','gap']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in rows);textfile('map-index.csv',out.getvalue())
 def table(name,rs):
  h=f'<section id="{name}"><h2>{E(name)} ({len(rs)})</h2><table><thead><tr><th>Rank</th><th>Literal source observation</th><th>County parent</th><th>Source candidate votes</th><th>Research coverage and qualification</th></tr></thead><tbody>'
  for r in rs:
   slug=parent_names[r['county']][0];h+=f'<tr><td>{r["rank"]}</td><td>{E(r["native_key"])}</td><td><a href="#{slug}">{E(r["county"])}</a></td><td>{r["votes"]}</td><td>Shared state/parent + 2020 Census fallback; {E(r["gap"])}</td></tr>'
  return h+'</tbody></table></section>'
 h='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Delaware precinct map research atlas</title><style>body{font:16px system-ui,sans-serif;max-width:1400px;margin:auto;padding:24px;color:#142b3c;background:#f5f8fa}a{color:#135e86}table{border-collapse:collapse;width:100%;background:white;font-size:14px}td,th{padding:8px;border:1px solid #cbd7df;text-align:left}th{background:#e4edf2}img{max-width:100%;max-height:1100px}section{margin:36px 0}.notice{padding:18px;background:#fff0cf;border-left:5px solid #bf7d12}nav a{margin-right:18px}</style><h1>Delaware precinct map research atlas</h1><p>Historical dispatch: 2024 Senate, all three reported candidates. Offline source evidence; current legal/reporting crosswalk remains unapproved.</p><div class="notice">311 priority observations / all 530 / 219 remainder. 531 FirstMap features, 537 structural rows, 533 historical sample-index identities and 412 Census VTDs are separate scopes. No result leaf has been assigned a polygon. No votes are spatially allocated.</div><nav><a href="#priority">311 priority</a><a href="#all-senate">All 530</a><a href="#remainder">219 remainder</a><a href="#sources">Sources</a><a href="index.json">Complete index JSON</a><a href="README.md">README</a></nav><section><h2>Whole-state native atlas</h2><p>All 169,245 source coordinate positions, 533 original rings; affine display only, no simplification or ring reordering. EPSG3857 coordinates remain in the original.</p><a href="native-features.json.gz">Complete native features</a><br><img src="previews/firstmap-native.svg" alt="All 531 unjoined native district boundaries"></section>'
 for p in parents:
  slug,fips,rd=parent_names[p['county']];h+=f'<section id="{slug}"><h2>{E(p["county"])}</h2><p>{len(p["priority_keys"])} priority and {len(p["full_native_keys"])} full Senate observations. Actual Department county map chain and RD{rd} overview acquired; whole-state FirstMap and entire county Census fallback acquired. Shared research reference; no finer/current match.</p><p><a href="source/county-{slug}-overview.receipt.json">Original PDF receipt</a> · <a href="parent-inventory.json">Full parent hierarchy and chain</a> · <a href="previews/census-vtd-{fips}.svg">2020 Census VTD preview</a></p></section>'
 h+=table('priority',rows[:311])+table('all-senate',rows)+table('remainder',rows[311:])
 h+='<section id="structural"><h2>All 537 structural rows (historical administrative evidence)</h2><table><tr><th>Literal key</th><th>Printed county</th><th>Kind</th><th>Raw original line / footnote</th></tr>'
 for k,r in structure.items():h+=f'<tr><td>{E(k)}</td><td>{E(r["county"])}</td><td>{E(r["kind"])}</td><td>{E(r["raw_line"])}; {E(str(r.get("statutory_reference")))}</td></tr>'
 h+='</table></section><section id="sample-identities"><h2>533 historical sample-index identities</h2><p>Index links only; individual ballot PDFs not acquired by this map worker. Not a current geometry roster.</p><table><tr><th>Source key</th><th>Printed county/RD/ED</th><th>Literal historical links</th></tr>'
 for r in sample:h+=f'<tr><td>{E(r["native_key"])}</td><td>{E(r["county_literal"])} / {E(r["rd_literal"])} / {E(r["ed_literal"])}</td><td>{E(str(r["hrefs"]))}</td></tr>'
 h+='</table></section><section id="administrative"><h2>All administrative and unavailable cases</h2><pre>'+E(__import__('json').dumps(dict(administrative=index['administrative_cases'],unavailable=index['unavailable_administrative_cases']),ensure_ascii=False,indent=2))+'</pre></section><section id="native-attributes"><h2>All 531 native feature attributes (unjoined)</h2><table><tr><th>OBJECTID</th><th>Complete native attributes</th></tr>'
 for f in native['features']:h+=f'<tr><td>{f["attributes"]["OBJECTID"]}</td><td>{E(str(f["attributes"]))}</td></tr>'
 h+='</table></section><section id="sources"><h2>Every actual request</h2><p>Full entities and redirects are pinned in receipts; compressed originals can be reconstructed using reconstruct.py.</p><table><tr><th>Request</th><th>Status / bytes</th><th>Original URL</th><th>Receipt</th></tr>'
 for r in source_inventory:h+=f'<tr><td>{E(r["id"])}</td><td>{r["status"]} / {r["entity_bytes"]}</td><td><a href="{E(r["url"],quote=True)}">{E(r["url"])}</a></td><td><a href="{E(linkpath(r["receipt"]["path"]))}">complete evidence</a></td></tr>'
 h+='</table></section><section id="pdf-atlas"><h2>All downloaded PDF renderings</h2><p>Every PDF page was rendered automatically; only the selected pages listed in qa/visual-review.json were manually inspected.</p><ul>'
 for pdf in read(M/'qa/pdf-rendering.json')['outputs']:
  h+='<li>'+E(', '.join(pdf['source_ids']))+': '+ ' '.join('<a href="'+E(linkpath(p['path']))+'">page '+str(j+1)+'</a>' for j,p in enumerate(pdf['images']))+'</li>'
 h+='</ul></section><p>All current geography, live reporting IDs, cadence, remaining pool, collector and forecast approvals remain false.</p></html>'
 textfile('index.html',h)
 # Official literal map inventory, not guessed filename enumeration.
 write('source/official-map-link-inventory.json',[dict(parent_id=r['id'],parent_url=r['url'],links=r['literal_links']) for r in receipts if r.get('literal_links') and r['id'].startswith('parent-')])
 write('qa/build-summary.json',dict(priority=311,all_senate=530,remainder=219,parents=3,priority_votes=sum(r['votes']for r in rows[:311]),remainder_votes=sum(r['votes']for r in rows[311:]),all_votes=sum(r['votes']for r in rows),structure_rows=537,sample_index_ids=533,native_features=531,census_VTDs=412,leaf_matches_approved=0,source_requests=len(receipts)))
 print('Built offline index/atlas',len(rows),len(receipts),'requests')
if __name__=='__main__':main()
