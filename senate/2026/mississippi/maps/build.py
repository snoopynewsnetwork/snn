#!/usr/bin/env python3
"""Offline index/build. Complete contract remains a pinned canonical reference."""
import html,json,pathlib,re
from acquire import ROOT,STATE,sha,savejson
from compatibility import CONTRACT,canonical,contract,pin

EXTRA={
 '28033':dict(refs=['desoto-native','desoto-voting-map-pdf'],attempts=['desoto-election-maps-network','desoto-layer-pre','desoto-app-data','desoto-webmap'],gap='County-linked service has154 split features, with PRECINCT_ID_SPLIT and2 native curveRings; these do not establish a SEMS source-column join. Original county precinct PDF prints3/7/2025; current adoption/effective/November approval dates unknown.'),
 '28047':dict(refs=['harrison-native'],attempts=['harrison-layer-pre','harrison-gis-parent','harrison-home','harrison-portal-item'],gap='County-hosted service credits Board of Supervisors/Circuit Clerk/GIS, but description ties adjustments to2010Census. No current adoption/effective/November approval evidence;49features are not approved SEMS identities.'),
 '28073':dict(refs=['lamar-webmap-collection','lamar-precinct-pdf'],attempts=['lamar-home-network','lamar-home-retry','lamar-app-data','lamar-webmap'],gap='County-linked webmap embeds25features, one empty (attributes retained); underlying original shapefile/native precision and independent source count/edit clock unavailable. PDF prints08/09/2022. Neither establishes November approval or a source-column join.'),
 '28071':dict(refs=['lafayette-locations'],attempts=['lafayette-voting-network'],gap='County-linked2026/05-path PDF supplies18precinct location entries, no polygons. Filename path is not an adoption/effective date; no match of Oxford/source-label variants is approved.'),
 '28089':dict(refs=[],attempts=['madison-maps-network','madison-app-data','madison-app-arcgis-data'],gap='Official county maps page links CMPDD app5228a85a04324e79986d8c8b36237d4b. Portal request connection failure; ArcGIS public sharing request returns HTTP200item-not-found/not-accessible error. Finer native/current geometry not acquired.'),
 '28059':dict(refs=[],attempts=['jackson-county-maps-network','jackson-webmapping-network','jackson-app-data'],gap='Official county pages link Experience Builder appd41c10058cab4eaea47763fde92eabe6. Portal data request HTTP403; complete native layers/current boundaries not acquired. HTML pages alone are not geometry.'),
 '28045':dict(refs=[],attempts=['hancock-map-network','hancock-map-alt'],gap='Official county precinct PDF615 returns HTTP403 via two bounded request forms; map body not acquired. Challenge HTML is retained as error evidence, not a map.'),
 '28049':dict(refs=[],attempts=['hinds-approved-supervisor-map','hinds-election-commission','hinds-jackson-ward-map-page-network'],gap='County approved-supervisor PDF request connection failure; election commission HTTP500 and Jackson municipal map page HTTP404. Supervisor/municipal maps would still require precinct-vintage and finer reporting-unit review; no geometry substituted.')}

EXTRA['28109']=dict(refs=['pearl-river-locations'],attempts=['pearl-river-links','pearl-river-app-data','pearl-river-locations'],gap='No Pearl River archive link in MARIS active/disabled county list. County quicklinks provide a2page DP-009polling-place PDF dated09/08/2026 and Find My Polling Place app3dd6368364194c329d59278fec109a39. Complete app configuration acquired; it names webmap8bd14551937245989f448cc4c16bd511 and explicitly asks users to verify with Circuit Clerk. That downstream webmap/native layer was not acquired in this bounded investigation; polling PDF is not polygons or a certified reporting dictionary.')
EXTRA['28121']=dict(refs=[],attempts=['rankin-documents','rankin-app-data'],gap='Official county document index links CMPDD viewer2a84c1decebc4733b91fb86c928b402a. Actual portal data request connection failure; no complete native/current geometry acquired. A viewer link is not geometry or current approval.')

def build():
    c=contract();comp=json.loads((ROOT/'compatibility.json').read_text());geo=json.loads((ROOT/'geometry-audit.json').read_text());shared=json.loads((ROOT/'shared-map-references.json').read_text())['sources'];receipts=[json.loads(p.read_text()) for p in sorted((ROOT/'source').glob('*.receipt.json'))];sources=shared+receipts;byid={s['id']:s for s in sources};native={x['key']:(i,x) for i,x in enumerate(c['source_native_constituents'])};parents=[]
    names={x['parent_county_fips']:x['parent_county'] for x in c['source_native_constituents']};byname={v.lower().replace(' ',''):k for k,v in names.items()};byname['jeffdavis']='28065'
    maris={}
    for s in shared:
        if s['id'].startswith('maris-2023-precinct-') and s['status']==200:
            slug=s['requested_url'].rsplit('/',1)[1].split('_')[0].lower();maris[byname[slug]]=s['id']
    comment={}
    for s in receipts:
        if s['id'].startswith('maris-comment-'):
            slug=s['requested_url'].rsplit('/',1)[1].split('_')[0].lower()
            if slug in byname:comment[byname[slug]]=s['id']
    for fips,pk in c['native_priority_by_parent'].items():
        full=[x['key'] for x in c['all_unit_order'] if x['parent_county_fips']==fips];refs=['maris-2020-precinct-zip'];attempts=['maris-updated-precinct-parent','maris-2020-precinct-parent'];gap=[]
        if fips in maris:refs.append(maris[fips]);attempts.append(maris[fips]);gap.append('Actual MARIS2023-labeled ZIP acquired; publication label and March2023HTTPfile modification are separate from unknown adoption/effective/November approval dates.')
        elif fips in comment:
            attempts.append(comment[fips]);s=byid[comment[fips]];gap.append(f"No actively advertised MARIS2023 ZIP for this parent; exact disabled/commented primary URL attempt {s['status']}"+(' '+s.get('error_type','') if not s['status'] else '')+'.')
        else:gap.append('No active MARIS2023 archive for this parent; not present in extracted disabled-link attempts.')
        if fips in EXTRA:refs+=EXTRA[fips]['refs'];attempts+=EXTRA[fips]['attempts'];gap.append(EXTRA[fips]['gap'])
        gap.append('2020Census VTDs are a shared parent reference, not certified current precincts. Native-column polygons, source-ID crosswalk, splits/mergers and central/absentee/administrative coverage remain unknown. No geometry intersection, fuzzy label, ordinal or printed code is used to resolve them.')
        parents.append(dict(parent_county_fips=fips,parent_county=names[fips],priority_child_keys=pk,full_child_keys=full,remainder_child_keys=[k for k in full if k not in pk],priority_count=len(pk),full_count=len(full),map_reference_ids=refs,
          fallback_feature_count=geo['county_fallback_feature_counts'][fips],fallback_preview=geo['previews'][f'vtd2020-{fips}'],primary_attempt_ids=attempts,
          discovery_depth='State MARIS active/disabled exact links plus complete2020fallback; bounded specific county followup' if fips in EXTRA else ('State MARIS active/disabled exact links plus complete2020fallback; no separate county-site exhaustive audit' if pk else 'Remainder-only parent: statewide MARIS/Census discovery and disabled archive attempt only'),
          gap=' '.join(gap),current_approval=False,native_geometry_match_status='unknown_unallocated'))
    parentmap={p['parent_county_fips']:p for p in parents};entries=[]
    for row in c['all_unit_order']:
        i,obj=native[row['key']];fips=row['parent_county_fips'];p=parentmap[fips]
        entries.append(dict(rank=row['rank'],key=row['key'],parent_county_fips=fips,label_literal=obj['label_literal'],printed_native_id=obj['printed_native_id'],printed_native_id_role='source-only printed code; null preserved; no approved geometry identity',source_id=obj['source_id'],source_page=obj['source_page'],physical_column=obj['source_column'],source_raw_sha256=obj['source_raw_sha256'],source_role=obj['role'],complete_native_object_reference=dict(contract_path=CONTRACT['path'],json_pointer=f'/source_native_constituents/{i}',canonical_object_sha256=sha(canonical(obj))),
          rank_record_json_pointer=f"/all_unit_order/{row['rank']-1}",priority=row['key'] in c['ordered_priority_keys'],map_reference_ids=p['map_reference_ids'],map_reference_role='shared parent/map reference; no entry-specific polygon or vote assignment',geometry_feature_ids=None,approved_current_crosswalk=None,
          gap=f"{row['key']}: boundary/reporting identity for literal label {obj['label_literal']!r} at original PDF{obj['source_page']}/physical column{obj['source_column']} is unverified. See parent{fips} attempted primary alternatives and vintage/access/finer-geography gaps."))
    index=dict(schema='ms-source-native-map-index-v1',primary_scope='Exactly887ordered2024SEMSsource-native observations beneath77county parents; no legal/current polygon identity implied',complete_compatibility_reference=dict(path='maps/compatibility.json',**{k:v for k,v in pin('maps/compatibility.json').items() if k!='path'}),complete_contract=CONTRACT,ordered_priority_keys=c['ordered_priority_keys'],priority_entries=entries[:887],full_preferred_native_entries=entries,all82parents=parents,
       full_source_admin_null_alternative_inventory=dict(contract_path=CONTRACT['path'],json_pointer='',preservation='Complete canonical root object;2321source columns/84source views, all global/source/candidate/method/admin/null/alternative objects and recursively resolved historical/full field bodies survive. Not restricted to1736preferred. See compatibility canonical_resolution.'),
       priority_count=887,priority_parent_count=77,full_count=1736,remainder_count=849,current_2026_geographic_approval=False)
    savejson(ROOT/'index.json',index)
    savejson(ROOT/'acquisition.json',dict(schema='ms-map-acquisition-v1',sources=sources,source_body_storage='Exact existing originals reused read-only; all new complete response/error bytes gzip or segments. No duplicate bodies. HTTP200is not success without payload inspection.',source_qualifications=EXTRA))
    def esc(s):return html.escape(str(s))
    def link(path,label):return f'<a href="{esc(path)}">{esc(label)}</a>'
    def start(title):return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'+title+'</title><style>body{font:16px system-ui;color:#233d43;background:#f5f3ec;margin:32px;max-width:1500px}h1{font-size:30px}a{color:#126073}table{border-collapse:collapse;width:100%;background:#fff}th,td{padding:9px;border:1px solid #ccd5d5;text-align:left;vertical-align:top}th{background:#dce8e5;position:sticky;top:0}pre{white-space:pre-wrap;margin:0}small{display:block;color:#4a5c62}details{margin:16px 0}img{max-width:100%;height:auto}p{max-width:1000px}</style><body><h1>'+title+'</h1>'
    out=[start('Mississippi | 887 historical source observations'),'<p>Offline research index. Exactly 887 priority entries; all 1,736 preferred units and 82 parents remain in the inventory. Shared map references do not resolve source columns to legal precincts or approved November units. No votes are assigned to geometry.</p>',
       '<p>'+link('inventory.html','Full1,736 /82-parent inventory')+' · '+link('index.json','Machine index')+' · '+link('compatibility.json','Complete canonical compatibility')+' · '+link('geometry-audit.json','Native geometry audit')+' · '+link('acquisition.json','Full acquisition receipts')+' · '+link('../precinct-maps.md','Report')+'</p>',
       '<details><summary>Representative original PDF renders and map previews</summary>']
    for k in ['desoto-voting-map-pdf-p1','lamar-precinct-pdf-p1','lafayette-locations-p1','lauderdale-original-p9']:
        out.append('<p>'+link('previews/'+k+'.png',k)+'</p>')
    out+=['</details><table><thead><tr><th>Rank / key</th><th>Literal source label / physical locator</th><th>Shared parent map references</th><th>Unresolved entry gap</th></tr></thead><tbody>']
    for e in entries[:887]:
        p=parentmap[e['parent_county_fips']];s=next(x for x in c['source_native_inventory'] if x['source_id']==e['source_id'])
        refs=[link(p['fallback_preview'].removeprefix('maps/'),'2020VTD parent preview')]
        for k in p['map_reference_ids'][1:]:
            if k in geo['previews']:refs.append(link(geo['previews'][k].removeprefix('maps/'),k+' preview'))
            elif k in byid and 'path' in byid[k]:refs.append(link('../'+byid[k]['path'],k+' original gzip'))
        out.append(f'<tr data-priority-rank="{e["rank"]}" id="unit-{e["rank"]}"><td>{e["rank"]}<small>{esc(e["key"])}</small></td><td><pre>{esc(e["label_literal"])}</pre><small>{esc(names[e["parent_county_fips"]])} · PDF{e["source_page"]}, physical c{e["physical_column"]} · printed code {esc(e["printed_native_id"])}</small>'+link('../'+s['original_path'],'Complete original gzip')+f'<small>rawSHA256 {e["source_raw_sha256"]}</small></td><td>'+ '<br>'.join(refs)+'</td><td>'+esc(e['gap'])+' '+link('inventory.html#parent-'+p['parent_county_fips'],'Specific parent access/vintage gap')+'</td></tr>')
    out+=['</tbody></table></body></html>'];(ROOT/'index.html').write_text('\n'.join(out)+'\n')
    out=[start('Mississippi | full preferred inventory and parent gaps'),'<p>'+link('index.html','887priority source observations')+' · '+link('index.json','Full machine inventory')+'</p>','<h2>All82parent references</h2><table><tr><th>County /FIPS</th><th>Priority /full /2020VTD features</th><th>Attempted primary sources and specific gaps</th></tr>']
    for p in parents:
        refs=[]
        for k in p['primary_attempt_ids']:
            s=byid[k];refs.append(link(s['requested_url'],k)+f" [HTTP{s['status']}]"+((' '+link('../'+s['path'],'retained complete response gzip')) if s.get('path') else ' '+esc(s.get('error_type',''))))
        out.append(f'<tr id="parent-{p["parent_county_fips"]}"><td>{esc(p["parent_county"])} {p["parent_county_fips"]}</td><td>{p["priority_count"]}/{p["full_count"]}/{p["fallback_feature_count"]}<br>'+link(p['fallback_preview'].removeprefix('maps/'),'Shared 2020preview')+'</td><td>'+esc(p['gap'])+'<details><summary>Actual attempts /discovery depth</summary>'+esc(p['discovery_depth'])+'<p>'+'<br>'.join(refs)+'</p></details></td></tr>')
    out+=['</table><h2>All1,736preferred observations in full contract rank order</h2><table><tr><th>Rank/key</th><th>Literal label/source location</th><th>Scope</th></tr>']
    for e in entries:out.append(f'<tr data-full-rank="{e["rank"]}"><td>{e["rank"]} {esc(e["key"])}</td><td><pre>{esc(e["label_literal"])}</pre>PDF{e["source_page"]}/physical c{e["physical_column"]} · code {esc(e["printed_native_id"])}</td><td>'+('priority' if e['priority'] else 'remainder')+' · '+link('#parent-'+e['parent_county_fips'],'Shared parent reference /gap')+'</td></tr>')
    out+=['</table></body></html>'];(ROOT/'inventory.html').write_text('\n'.join(out)+'\n');print('offline index887 /1736 /82 complete')

if __name__=='__main__':build()
