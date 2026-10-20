"""Deterministic offline atlas from verified individual originals and full contract.

No votes, ballots or registration are assigned to geometry. Every historical
source object is emitted whole in a parent page, with complete original links.
"""
import collections,gzip,html,json,re
from pathlib import Path
from acquire import HERE,entity,sha

STATE=HERE.parent
WARN=('These are source map assets and historical source records. Current ELECT geometry, '
      '2020 Census VTDs and historical result units are separate inventories. No approved '
      'leaf join, legal adoption, crossyear equivalence or spatial allocation of votes, '
      'ballots or registration is asserted. Virtual/administrative records remain visible. '
      'ELECT warns that recently enacted local changes may take weeks to appear.')
STYLE='body{font:16px system-ui;max-width:1200px;margin:2rem auto;padding:0 1rem;color:#152f38;background:#f5f6f0}a{color:#075c88}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #c1c9c6;text-align:left;padding:.5rem}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:1rem}summary{padding:.6rem;cursor:pointer}img{max-width:100%;height:auto}details{border:1px solid #b3c1c1;margin:.5rem 0}aside{background:#ffedbc;padding:1rem}input,select{font:inherit;margin:.5rem;padding:.4rem}small{display:block}nav{margin:1rem 0}.maps{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1rem}.maps img{width:100%}'
def esc(v):return html.escape(str(v),quote=True)
def pretty(v):return esc(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False))
def page(title,body,prefix=''):
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'+esc(title)+'</title><style>'+STYLE+'</style><body><nav><a href="'+prefix+'index.html">Virginia atlas</a> · <a href="'+prefix+'sources.html">Complete source catalogue</a></nav><h1>'+esc(title)+'</h1><aside>'+esc(WARN)+'</aside>'+body+'</body></html>\n'
def original_link(rec,prefix=''):
    hop=rec['hops'][-1]
    return ' '.join('<a href="'+prefix+esc(p['path'])+'" download="'+esc(rec['key'])+('.pdf.gz' if '.pdf' in rec['final_url'].lower() else '.zip.gz' if '.zip' in rec['final_url'].lower() else '.entity.gz')+'">complete gzip original'+(' part '+str(i+1) if len(hop['parts'])>1 else '')+'</a>' for i,p in enumerate(hop['parts']))
def svg(features,title):
    points=[p for f in features for p in f['points']]
    if not points:return '<svg xmlns="http://www.w3.org/2000/svg"><text>No source coordinates</text></svg>'
    xmin=min(p[0] for p in points);xmax=max(p[0] for p in points);ymin=min(p[1] for p in points);ymax=max(p[1] for p in points)
    width=xmax-xmin;height=ymax-ymin;pad=max(width,height)*.02
    out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="'+f'{xmin-pad} {-ymax-pad} {width+2*pad} {height+2*pad}'+'"><title>'+esc(title)+'; raw native-coordinate part outlines, Y reflected for display only; no ring classification or fill</title><g transform="scale(1,-1)" fill="none" stroke="#23596b" stroke-width="1" vector-effect="non-scaling-stroke">']
    for feature in features:
        pts=feature['points'];parts=feature['parts'];d=[]
        for i,start in enumerate(parts):
            ring=pts[start:parts[i+1] if i+1<len(parts) else len(pts)]
            if ring:d.append('M'+' L'.join(repr(p[0])+','+repr(p[1]) for p in ring))
        out.append('<path vector-effect="non-scaling-stroke" d="'+' '.join(d)+'"><title>source record '+str(feature['source_record_index'])+'</title></path>')
    return ''.join(out)+'</g></svg>\n'

def build(output=HERE):
    for directory in ('parents','previews'): (output/directory).mkdir(exist_ok=True)
    contractpath=STATE/'data/turnout/priority-set.json';raw=contractpath.read_bytes()
    assert sha(raw)=='5a832915bfb054111f59759503a6024cfa8696588b6dacd62cbee54d15b74f0c'
    c=json.loads(raw);a=json.loads((STATE/'data/coordinator-priority-acceptance.json').read_bytes())
    priority=set(c['ordered_priority_keys']);plans=json.loads((HERE/'state-link-plan.json').read_bytes())['parents']
    local={p['fips']:p for p in json.loads((HERE/'local-navigation.json').read_bytes())['parents']};follow={p['fips']:p for p in json.loads((HERE/'local-map-navigation.json').read_bytes())['parents']}
    pdfaudit=json.loads((HERE/'pdf-audit.json').read_bytes());pdfs={p['request']:p for p in pdfaudit['documents']}
    census=json.loads(gzip.decompress((HERE/'decoded/census-vtd-2020.json.gz').read_bytes()))[0]
    bycounty=collections.defaultdict(list)
    for f in census['features']:bycounty[f['attributes']['STATEFP20']+f['attributes']['COUNTYFP20']].append(f)
    assert set(bycounty)=={p['fips'] for p in plans}
    parents=[];unitcoverage=[];table=[]
    for plan,parent in zip(plans,c['parent_inventory']):
        assert plan['parent_key']==parent['historical_parent_key']
        fips=plan['fips'];name=plan['parent_label'];key=plan['parent_key'];units=[u for u in c['ordered_units'] if u['parent_key']==key]
        native=json.loads(gzip.decompress((HERE/'decoded'/f'state-gis-{fips}.json.gz').read_bytes()))[0];features=native['features'];summary=native['dataset']
        ziprec=json.loads((HERE/'requests'/f'state-gis-{fips}.json').read_bytes());pdfrec=json.loads((HERE/'requests'/f'state-pdf-{fips}.json').read_bytes());pdf=pdfs[f'state-pdf-{fips}']
        counts=collections.Counter(f['attributes'].get('PrecinctFI') for f in features)
        # Numeric code comparison is retained only as a candidate-search aid.
        # These candidates never supply geometry IDs or data allocation.
        candidates=collections.defaultdict(list)
        for f in features:
            token=f['attributes'].get('PrecinctFI')
            if isinstance(token,str) and token.isdecimal():candidates[str(int(token))].append(f['source_record_index'])
        cover=[]
        for u in units:
            virtual=u['source_native_constituents']['enr_api']['full_native_object']['precinct']['isVirtual']
            code=u['literal_label_code'];indexes=candidates.get(str(int(code)),[]) if code and code.isdecimal() and not virtual else []
            status='virtual source; no physical polygon assertion' if virtual else 'current numeric-code candidates only; unapproved identity' if indexes else 'no current numeric-code candidate; finer identity unavailable'
            cover.append({'key':u['key'],'rank':u['rank'],'parent_key':key,'scope':'priority' if u['key'] in priority else 'remainder','source_record':u['source_record'],'historical_literal_label':u['label'],'source_virtual':virtual,'source_native_uuid':u['source_native_id'],'literal_code':code,'current_candidate_feature_positions':indexes,'candidate_basis':'same explicit parent, integer representation of full literal numeric code vs PrecinctFI only; neither label/UUID/current/legal equivalence nor approved join','geometry_status':status,'approved_leaf_join':False,'spatial_allocation':False})
        unitcoverage.extend(cover)
        created=collections.defaultdict(set)
        for f in features:
            for k,v in f['attributes'].items():
                if isinstance(v,dict) and v.get('type')=='date':created[k].add(v['iso'])
        vintage={'gis_url_filename':plan['gis_link']['href'].rsplit('/',1)[-1],'pdf_url_filename':plan['pdf_link']['href'].rsplit('/',1)[-1],'pdf_metadata':pdf['metadata'],'dbf_date_values':{k:sorted(v) for k,v in created.items()},'qualification':'filename/ZIP/DBF/editor/PDF creation dates are publication/edit evidence only; adopted/effective/legal November date unknown; full printed source text and complete ZIP XML retained','adopted_date':None,'legal_effective_date':None,'current_November_approval':False}
        row={'parent_key':key,'parent_label':name,'fips':fips,'priority_children':plan['priority_children'],'remainder_children':len(units)-plan['priority_children'],'full_native_children':len(units),'virtual_source_children':sum(r['source_virtual'] for r in cover),'state_geometry_features':len(features),'state_geometry_parts':summary['parts'],'state_geometry_positions':summary['positions'],'census2020_vtd_features':len(bycounty[fips]),'source_crs_wkt':summary['crs_wkt'],'physical_equivalence':'unavailable; map features and result source observations have different vintages and unit definitions','split_and_identifier_gaps':{'duplicate_literal_Precinct_1':summary['repeated_literal_Precinct_1'],'duplicate_full_PrecinctFI':{str(k):v for k,v in counts.items() if v>1},'historical_finer_crosswalk':'unavailable','source_uuid_to_polygon':'unavailable'},'vintage':vintage,'local_navigation':local.get(fips,{'scope':'remainder-only parent; local directory outside108bound; complete state ZIP/PDF and Census fallback acquired'}),'local_map_navigation':follow.get(fips),'state_zip_request':f'state-gis-{fips}','state_pdf_request':f'state-pdf-{fips}','current_geography_approved':False,'legal_admission':False,'spatial_allocation':False,'source_geometry_kind':'precinct polygons, not county outline','coverage_kind':'source assets and contextual candidates; no approved leaf match'}
        parents.append(row)
        (output/'previews'/f'{fips}-state.svg').write_text(svg(features,name+' ELECT current publication'))
        (output/'previews'/f'{fips}-census2020.svg').write_text(svg(bycounty[fips],name+' Census2020 VTD fallback'))
        body='<p>'+str(plan['priority_children'])+' priority / '+str(len(units)-plan['priority_children'])+' remainder historical records; '+str(len(features))+' current source polygon features; '+str(len(bycounty[fips]))+' Census2020 VTDs.</p>'
        body+='<div class="maps"><div><h2>ELECT publication</h2><img alt="ELECT native part outlines" src="../previews/'+fips+'-state.svg"></div><div><h2>Census2020 fallback</h2><img alt="Census native part outlines" src="../previews/'+fips+'-census2020.svg"></div></div><p>Previews draw every original position, with Y reflected for display. They contain no vote data or ring fill. Native CRS and original coordinates stay in the decoded objects.</p>'
        body+='<h2>Complete originals and proofs</h2><p>State ZIP: '+original_link(ziprec,'../')+' · <a href="../requests/state-gis-'+fips+'.json">request receipt</a> · <a href="../binary-proof/state-gis-'+fips+'.json">binary proof</a> · <a href="../decoded/state-gis-'+fips+'.json.gz">all decoded fields and original coordinate positions</a></p><p>State PDF: '+original_link(pdfrec,'../')+' · <a href="../pdf/state-pdf-'+fips+'-text.json.gz">complete extracted text</a></p>'
        for r in pdf['renders']:body+='<details><summary>State map full page '+str(r['page'])+' (automated render)</summary><a href="../'+r['png']+'"><img loading="lazy" alt="Complete original PDF page" src="../'+r['png']+'"></a></details>'
        body+='<details><summary>Full parent source object and native child order</summary><pre class="parent-object">'+pretty(parent)+'</pre></details><details><summary>Acquisition, vintage, CRS, identifiers and access gaps</summary><pre>'+pretty(row)+'</pre></details>'
        body+='<h2>Every historical source record, in full source rank order</h2><label>Search <input id="filter" aria-label="Search source records"></label><label>Scope <select id="scope"><option value="all">All records</option><option value="priority">Priority</option><option value="remainder">Remainder</option></select></label><p id="visible-count"></p>'
        for u,coverage in zip(units,cover):
            body+='<details class="source-unit" id="'+esc(u['key'])+'" data-scope="'+coverage['scope']+'" data-search="'+esc(u['key']+' '+u['label']+' '+u['administrative_case'])+'"><summary>Rank '+str(u['rank'])+' · '+coverage['scope']+' · '+esc(u['label'])+' · '+esc(coverage['geometry_status'])+'</summary><pre class="full-object">'+pretty(u)+'</pre><pre class="unit-coverage">'+pretty(coverage)+'</pre></details>'
        body+='<script src="../filter.js"></script>'
        (output/'parents'/f'{fips}.html').write_text(page(name,body,'../'))
        table.append('<tr data-search="'+esc(name+' '+fips)+'"><td><a href="parents/'+fips+'.html">'+esc(name)+'</a><small>'+fips+' · '+esc(key)+'</small></td><td>'+str(plan['priority_children'])+'</td><td>'+str(len(units)-plan['priority_children'])+'</td><td>'+str(len(features))+'</td><td>'+str(len(bycounty[fips]))+'</td></tr>')
    (output/'parent-coverage.json').write_text(json.dumps({'parents':parents,'all_parents':133,'priority_parents':108,'approved_leaf_joins':0,'spatial_allocations':0},ensure_ascii=False,indent=2)+'\n')
    (output/'unit-coverage.json').write_text(json.dumps({'units':unitcoverage,'priority':1538,'remainder':1131,'order':'complete authority native rank; parent pages preserve each parent subsequence','approved_leaf_joins':0},ensure_ascii=False,indent=2)+'\n')
    intro='<p>All 133 county-equivalent parents, 2,669 complete historical source objects, 1,538 priority records across 108 parents, and all 1,131 remainder records. Native1538 crossing = 3,557,034 of 4,445,535 reported 2024 Senate marks; the 44-parent sensitivity is separate.</p><p><a href="../precinct-maps.md">Research report</a> · <a href="parent-coverage.json">Full parent coverage</a> · <a href="unit-coverage.json">Every unit qualification</a> · <a href="pdf-pages.html">All PDF pages and full originals</a> · <a href="manual-review.json">Exact manual review scope</a></p><label>Find parent <input id="parent-filter"></label><table><thead><tr><th>Parent</th><th>Priority units</th><th>Remainder units</th><th>ELECT polygons</th><th>Census2020 VTDs</th></tr></thead><tbody>'+''.join(table)+'</tbody></table><script src="filter.js"></script>'
    (output/'index.html').write_text(page('Virginia source maps and historical scope',intro))
    sources='<h2>Whole verified companions</h2><p>External source authority is <a href="../data/coordinator-priority-acceptance.json">path only</a>. Every source field survives in its complete original; archives resolve historical path plus SHA, never a later current path.</p><table><tr><th>Exact path</th><th>Bytes</th><th>SHA256</th></tr>'
    for pin in a['frozen_file_pins']:
        sources+='<tr><td><a href="../'+esc(pin['path'])+'">'+esc(pin['path'])+'</a></td><td>'+str(pin['bytes'])+'</td><td>'+pin['sha256']+'</td></tr>'
    sources+='</table><h2>Exact historical bodies</h2><p>Use reconstruct.py --historical PATH SHA256 OUTPUT to extract the exact member below, independently checking its original bytes.</p><table><tr><th>Historical path and member</th><th>Exact immutable storage</th><th>Bytes / SHA256</th></tr>'
    for r in a['historical_full_body_resolvers']:
        st=r['storage'];storage=st.get('archive',st.get('file'));member=st.get('member','(complete individual original)')
        sources+='<tr><td>'+esc(r['path'])+'<small>member '+esc(member)+'</small></td><td><a href="../'+esc(storage['path'])+'">'+esc(storage['path'])+'</a></td><td>'+str(r['bytes'])+'<small>'+r['sha256']+'</small></td></tr>'
    sources+='</table><h2>Acquired public response receipts</h2><table>'
    for path in sorted((HERE/'requests').glob('*.json')):
        r=json.loads(path.read_bytes());h=r['hops'][-1]
        sources+='<tr><td><a href="requests/'+path.name+'">'+esc(r['key'])+'</a></td><td>'+esc(h['status'])+'</td><td>'+esc(r['final_url'])+'</td><td>'+original_link(r)+'</td></tr>'
    (output/'sources.html').write_text(page('Complete source and historical-body catalogue',sources+'</table>'))
    pages='<p>Every page is rendered automatically at up to 1,400 pixels. Only manual-review.json names actually viewed pages. Full source PDF warnings/text are retained. Gzip originals reconstruct losslessly with reconstruct.py.</p>'
    for doc in pdfaudit['documents']:
        key=doc['request'];r=json.loads((HERE/'requests'/f'{key}.json').read_bytes())
        pages+='<details><summary>'+esc(key)+' · '+str(doc.get('pages','duplicate'))+' pages</summary><p>'+original_link(r)+'</p><pre>'+pretty({k:v for k,v in doc.items() if k!='renders'})+'</pre>'
        for img in doc.get('renders',[]):pages+='<a href="'+img['png']+'">Page '+str(img['page'])+'</a> '
        pages+='</details>'
    (output/'pdf-pages.html').write_text(page('Complete PDF originals and every rendered page',pages))
    return parents,unitcoverage

if __name__=='__main__':build()
