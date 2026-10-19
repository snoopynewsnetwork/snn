"""Compile only independently read, source-bound and peer-reconciled Senate views.

Peer candidate/label values are comparison controls; never used as a substitute
for an own original reading. Literal wrap differences stay in the owned ledger.
This bounded set is not the complete statewide native geography.
"""
import argparse,csv,gzip,json,re
from collections import defaultdict
from sources import BASE,OUT,sha,save
from replay_reviewed_native import hint_snapshot,PEER
from build_counties import writecsv

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--extension',action='store_true');args=ap.parse_args()
    numeric={(r['source_id'],r['page'],r['source_column'],r['candidate']):r for r in json.loads((OUT/'reviewed-replay-manual-repairs.json').read_text())['readings']}
    headers={(r['source_id'],r['page'],r['source_column']):r for r in json.loads((OUT/'reviewed-replay-header-repairs.json').read_text())['readings']}
    county={r['county'].lower().replace(' ','-'):r for r in csv.DictReader((BASE/'data/county-baselines.csv').open())}
    peer=json.loads(gzip.decompress(PEER.read_bytes()));hints=hint_snapshot()['sources'];suffix='';references=[dict(path=str(PEER.relative_to(BASE)),original_sha256=sha(gzip.decompress(PEER.read_bytes())))]
    if args.extension:
        from replay_extension import snapshot
        ext=snapshot();raw=gzip.decompress((BASE/ext['reference_path']).read_bytes());assert sha(raw)==ext['reference_original_sha256'];ep=json.loads(raw)
        for s in ext['sources']:peer['sources'][s['source_id']]=ep['sources'][s['source_id']]
        hints=hints+ext['sources'];suffix=f'-{len(hints)}views';references.append(dict(path=ext['reference_path'],original_sha256=ext['reference_original_sha256']))
        for r in json.loads((OUT/'replay-extension-manual-repairs.json').read_text())['readings']:numeric[(r['source_id'],r['page'],r['source_column'],r['candidate'])]=r
        for r in json.loads((OUT/'replay-extension-header-repairs.json').read_text())['readings']:headers[(r['source_id'],r['page'],r['source_column'])]=r
    sources=[];rows=[];checks=[];wrap_aliases=[]
    for s in hints:
        key=s['source_id'];o=json.loads(gzip.decompress((OUT/'extracts/reviewed-replay'/key/'independent-fields.json.gz').read_bytes()));h=json.loads(gzip.decompress((OUT/'extracts/reviewed-replay'/key/'independent-headers.json.gz').read_bytes()));c=county[key.removeprefix('sos-2024-county-').removesuffix('-updated')];pages=[];sums=defaultdict(int);totals={};n=0;unused=0
        for p in o['pages']:
            hp=next(a for a in h['pages'] if a['page']==p['page']);pp=next(a for a in peer['sources'][key]['pages'] if a['page']==p['page']);cols=[]
            for oc in p['columns']:
                idx=(key,p['page'],oc['source_column']);hr=headers.get(idx);hc=next(z for z in hp['columns'] if z['header_bounds']==oc['header_bounds']);label=hr['label_literal'] if hr else hc['label_ocr'];role='source_TOTAL' if label.strip()=='TOTAL' else 'unused_template_column' if not label.strip() else 'source_native_reporting_constituent';values={};pc=next(z for z in pp['columns'] if z['header_bounds']==oc['header_bounds'])
                # Ignore literal line wrapping only after physical boxes agree.
                norm=lambda t:' '.join(t.replace('-\n','-').replace('/\n','/').split())
                assert norm(label)==norm(pc['label_literal']),(key,p['page'],oc['source_column'],label,pc['label_literal'])
                if ' '.join(label.split())!=' '.join(pc['label_literal'].split()):wrap_aliases.append(dict(source_id=key,page=p['page'],source_column=oc['source_column'],own_literal=label,peer_literal=pc['label_literal'],qualification='Exact physical header agrees; explicit source line-wrap representation alias only, not a normalized geography join.'))
                assert (role=='source_TOTAL')==(pc['role']=='source_TOTAL')
                assert (role=='unused_template_column')==(pc['role']=='unused_template_column')
                printed=re.match(r'^\((\d+)\)',label);printed_id=printed.group(1) if printed else ''
                if args.extension and not printed_id:
                    pattern=r'^(\d+)-' if key.endswith('-sunflower') else r'(\d{4})$' if key.endswith('-wilkinson') else r'^Precinct (\d+)$' if key.endswith('-hinds') else r'^(\d+)\s+-\s+' if key.endswith('-lauderdale') else None
                    code=re.search(pattern,label) if pattern else None;printed_id=code.group(1) if code else ''
                for name,pfield in [('Ty Pinkins','Ty_Pinkins'),('Roger F. Wicker','Roger_F_Wicker')]:
                    z=oc['fields'][name];repair=numeric.get(idx+(name,));value=repair['value'] if repair else z['value'];assert value==pc[pfield],(idx,name,value,pc[pfield]);assert value is None or value>=0
                    if role=='unused_template_column':assert value is None
                    else:assert value is not None
                    if role=='source_native_reporting_constituent':sums[name]+=value
                    if role=='source_TOTAL':assert name not in totals;totals[name]=value
                    basis='independent_original_visual_cell_reading' if repair else 'independent_original_OCR_agrees_frozen_peer_visual_reading' if value is not None else 'blank_source_template_cell_null_not_zero'
                    values[name]=dict(value=value,source_box=z['source_box'],own_raw_literal=z['literal'],reading_basis=basis,manual_evidence=repair.get('evidence') if repair else None)
                    rows.append(dict(key=f'{c["fips"]}:{key}:p{p["page"]}:c{oc["source_column"]}',county_fips=c['fips'],county=c['county'],source_id=key,raw_sha256=s['raw_sha256'],source_page=p['page'],source_column=oc['source_column'],header_bounds=json.dumps(oc['header_bounds']),native_label_literal=label,printed_native_id=printed_id,role=role,candidate=name,votes=value if value is not None else '',candidate_bounds=json.dumps(z['source_box']),reading_basis=basis))
                n+=role=='source_native_reporting_constituent';unused+=role=='unused_template_column';cols.append(dict(source_column=oc['source_column'],label_literal=label,printed_native_id=printed_id,role=role,header_bounds=oc['header_bounds'],header_reading_basis='independent_original_visual_reading' if hr else 'independent_original_header_OCR_agrees_frozen_peer_visual_reading',fields=values))
            pages.append({k:p[k] for k in ['page','render_size','rotation_ccw','deskew_angle_ccw','raster_path','raster_sha256']}|dict(columns=cols))
        expected={'Ty Pinkins':int(c['2024-senate_A']),'Roger F. Wicker':int(c['2024-senate_B'])};assert dict(sums)==totals==expected,(key,sums,totals,expected)
        checks.append(dict(source_id=key,county_fips=c['fips'],native_constituents=n,unused_columns=unused,component_sums=dict(sums),printed_TOTAL=totals,county_control=expected,differences={name:0 for name in totals}))
        sources.append(dict(source_id=key,raw_sha256=s['raw_sha256'],county=c['county'],county_fips=c['fips'],pages=pages))
    ledger=dict(qualification=f'{len(sources)} frozen original source views, two named Senate candidates only. Independent source-byte extraction plus exact frozen peer comparison and explicit original visual repairs. Not statewide native coverage, not presidential coverage, no current2026 IDs or boundary equivalence. Generic write-ins/under/over/method fields remain separate source scopes.',peer_snapshot_path=str(PEER.relative_to(BASE)),peer_original_sha256=sha(gzip.decompress(PEER.read_bytes())),source_position_rounding='Own source rendering differs from targeting raster by at most1pixel on some pages; both sizes and exact owned raster hashes retained. Shared boxes are targeting hints, no ordinal-only cross-source join.',sources=sources)
    if args.extension:ledger.update(peer_references=references,explicit_wrap_representation_aliases=wrap_aliases,parsed_printed_id_scope='Pike parenthesized codes; Sunflower leading hyphen codes; Wilkinson trailing four-digit codes; Hinds Precinct numbers; Lauderdale leading hyphen-separated codes parsed from own literal headers. Source-scoped metadata, not2026/cross-year IDs. Blank IDs elsewhere are not evidence none printed.')
    save(OUT/f'native-2024-senate-reviewed{suffix}.json',ledger)
    writecsv(OUT/f'native-2024-senate-reviewed{suffix}.csv',rows)
    save(OUT/f'native-2024-senate-reviewed-controls{suffix}.json',dict(sources=checks,source_views=len(sources),pages=sum(len(s['pages']) for s in sources),native_constituents=sum(s['native_constituents'] for s in checks),native_candidate_cells=2*sum(s['native_constituents'] for s in checks),summary_TOTALs=len(checks),unused_columns=sum(s['unused_columns'] for s in checks),manual_numeric_repairs=len(numeric),manual_header_repairs=len(headers),all_named_county_controls_exact=True,statewide_native_complete=False))
    print('reviewed source views',len(sources),'native constituents',sum(s['native_constituents'] for s in checks),'all two-candidate controls exact')
if __name__=='__main__':main()
