"""Compile84 independent original Senate source views; keep alternative scopes.

Count values come only from own raw original extraction and explicit original
visual repairs. Frozen peer fields enter subsequent comparison, not extraction.
"""
import csv,gzip,json,re
from collections import Counter
from sources import OUT,BASE,sha,original,save
from build_counties import writecsv
from replay_checkpoint import snapshot
NAMES=['Ty Pinkins','Roger F. Wicker']
def norm(t):return ' '.join(t.replace('-\n','-').replace('/\n','/').split())
def main():
    pin=snapshot('84views');priorpath=BASE/pin['prior_own_ledger_path'];assert sha(priorpath.read_bytes())==pin['prior_own_ledger_sha256'];prior=json.loads(priorpath.read_text());sources=list(prior['sources']);reference=(BASE/pin['reference_path']).read_bytes();assert sha(reference)==pin['reference_original_sha256'];peer=json.loads(reference)
    county={r['county'].lower().replace(' ','-'):r for r in csv.DictReader((BASE/'data/county-baselines.csv').open())}
    numeric={(r['source_id'],r['page'],r['source_column'],r['candidate']):r for r in json.loads((OUT/'replay-84views-manual-repairs.json').read_text())['readings']};headers={(r['source_id'],r['page'],r['source_column']):r for r in json.loads((OUT/'replay-84views-header-repairs.json').read_text())['readings']};wraps=list(prior['explicit_wrap_representation_aliases'])
    for s in pin['sources']:
        key=s['source_id'];assert sha(original(key))==s['raw_sha256'];label=key.removeprefix('sos-2024-county-').removesuffix('-updated');c=county[label];directory=OUT/'extracts/reviewed-replay'/key;own=json.loads(gzip.decompress((directory/'independent-fields.json.gz').read_bytes()));h=json.loads(gzip.decompress((directory/'independent-headers.json.gz').read_bytes()));pages=[]
        for p in own['pages']:
            hp=next(z for z in h['pages'] if z['page']==p['page']);cols=[]
            for oc in p['columns']:
                idx=(key,p['page'],oc['source_column']);hr=headers.get(idx);hc=next(z for z in hp['columns'] if z['header_bounds']==oc['header_bounds']);literal=hr['label_literal'] if hr else hc['label_ocr'];role='source_TOTAL' if literal.strip()=='TOTAL' else 'unused_template_column' if not literal.strip() else 'parallel_native_observation' if key.endswith('-kemper') and p['page']==6 else 'source_native_reporting_constituent';parsed=re.search(r'^\((\d{2})\)',literal) if key.endswith('-pike') else re.search(r'\s+(\S+)$',literal) if key.endswith('-pontotoc') and role=='source_native_reporting_constituent' else None;printed=parsed.group(1) if parsed else '';fields={}
                for name in NAMES:
                    z=oc['fields'][name];repair=numeric.get(idx+(name,));v=repair['value'] if repair else z['value'];assert v is None if role=='unused_template_column' else isinstance(v,int) and v>=0
                    fields[name]=dict(value=v,source_box=z['source_box'],own_raw_literal=z['literal'],reading_basis='independent_original_visual_cell_reading' if repair else 'independent_original_OCR_agrees_frozen_peer_visual_reading' if v is not None else 'blank_source_template_cell_null_not_zero',manual_evidence=repair['evidence'] if repair else None)
                cols.append(dict(source_column=oc['source_column'],label_literal=literal,printed_native_id=printed,role=role,header_bounds=oc['header_bounds'],header_reading_basis='independent_original_visual_reading' if hr else 'independent_original_header_OCR_agrees_frozen_peer_visual_reading',fields=fields))
            pages.append({k:p[k] for k in ['page','render_size','rotation_ccw','deskew_angle_ccw','raster_path','raster_sha256']}|dict(columns=cols))
        sources.append(dict(source_id=key,raw_sha256=s['raw_sha256'],county=c['county'],county_fips=c['fips'],pages=pages))
    roles=Counter();flat=[];checks=[];bound_changes=[];candidate_positions=0;metadata=[];empty_id_representations=0
    for s in sources:
        key=s['source_id'];assert sha(original(key))==s['raw_sha256'];ps=peer['sources'][key];sums=Counter();totals={};parallel=[];native_count=0
        for p in s['pages']:
            assert sha((BASE/p['raster_path']).read_bytes())==p['raster_sha256'];pp=next(z for z in ps['pages'] if z['page']==p['page'])
            for c in p['columns']:
                pc=next(z for z in pp['columns'] if z['source_column']==c['source_column']);assert norm(c['label_literal'])==norm(pc['label_literal']),(key,p['page'],c['source_column'],c['label_literal'],pc['label_literal'])
                if ' '.join(c['label_literal'].split())!=' '.join(pc['label_literal'].split()):wraps.append(dict(source_id=key,page=p['page'],source_column=c['source_column'],own_literal=c['label_literal'],peer_literal=pc['label_literal'],qualification='Explicit printed line-wrap representation after matched original source/position.'))
                peer_role='source_native_reporting_constituent' if pc['role']=='native_reporting_constituent' else pc['role'];assert c['role']==peer_role;roles[c['role']]+=1;native_count+=c['role']=='source_native_reporting_constituent'
                peer_id=pc.get('printed_native_id')
                if c['printed_native_id']=='' and peer_id is None:empty_id_representations+=1
                elif c['printed_native_id']!=peer_id:metadata.append(dict(source_id=key,page=p['page'],source_column=c['source_column'],own_id=c['printed_native_id'],peer_id=peer_id))
                for name,f in c['fields'].items():
                    peerfield='Ty_Pinkins' if name=='Ty Pinkins' else 'Roger_F_Wicker';assert f['value']==pc[peerfield],(key,p['page'],c['source_column'],name);candidate_positions+=1;box=f['source_box'];w,h=p['render_size'];assert 0<=box[0]<box[2]<=w and 0<=box[1]<box[3]<=h
                    if box!=pc['candidate_bounds'][name] or c['header_bounds']!=pc['header_bounds']:bound_changes.append(dict(source_id=key,page=p['page'],source_column=c['source_column'],candidate=name,own_accepted_candidate_box=box,peer_candidate_box=pc['candidate_bounds'][name],own_header_box=c['header_bounds'],peer_header_box=pc['header_bounds'],qualification='Target metadata difference retained; numeric/source label agreement alone is not exact geometry agreement.'))
                    v=f['value']
                    if c['role']=='source_native_reporting_constituent':sums[name]+=v
                    elif c['role']=='source_TOTAL':assert name not in totals;totals[name]=v
                    elif c['role']=='parallel_native_observation':parallel.append(dict(page=p['page'],column=c['source_column'],candidate=name,value=v))
                    flat.append(dict(key=f'{s["county_fips"]}:{key}:p{p["page"]}:c{c["source_column"]}',county_fips=s['county_fips'],county=s['county'],source_id=key,raw_sha256=s['raw_sha256'],source_page=p['page'],source_column=c['source_column'],header_bounds=json.dumps(c['header_bounds']),native_label_literal=c['label_literal'],printed_native_id=c['printed_native_id'],role=c['role'],candidate=name,votes=v if v is not None else '',accepted_reading_candidate_bounds=json.dumps(box),original_targeting_candidate_bounds=json.dumps(f.get('original_targeting_source_box',box)),reading_basis=f['reading_basis']))
        assert dict(sums)==totals,(key,sums,totals);c=county[s['county'].lower().replace(' ','-')];ex={NAMES[0]:int(c['2024-senate_A']),NAMES[1]:int(c['2024-senate_B'])};delta={n:sums[n]-ex[n] for n in NAMES}
        if any(delta.values()):assert (key,delta) in [('sos-2024-county-tunica',{'Ty Pinkins':-1,'Roger F. Wicker':0}),('sos-2024-county-pike',{'Ty Pinkins':-1232,'Roger F. Wicker':-1486})]
        s['use_in_preferred82_scope']=key not in ['sos-2024-county-coahoma','sos-2024-county-pike'];s['county_control_qualification']='Original alternative retained separately; explicitly Updated source supplies preferred historical county scope' if key=='sos-2024-county-pike' else 'Native SEMS1797 vs ES&S/countyCSV1798 Pinkins; exact unallocated primary source discrepancy' if key.endswith('-tunica') else 'Both named source-native sums equal sourceTOTAL and primary county control'
        checks.append(dict(source_id=key,county_fips=s['county_fips'],native_constituents=native_count,component_sums=dict(sums),printed_TOTAL=totals,county_control=ex,native_minus_county_control=delta,parallel_candidate_observations=len(parallel),preferred82=s['use_in_preferred82_scope']))
    assert len(sources)==84 and roles=={'source_native_reporting_constituent':1779,'source_TOTAL':84,'unused_template_column':447,'parallel_native_observation':11};assert candidate_positions==4642;assert not metadata,metadata[:10]
    preferred=[r for r in checks if r['preferred82']];assert len(preferred)==len({r['county_fips'] for r in preferred})==82;preferred_totals={n:sum(r['component_sums'][n] for r in preferred) for n in NAMES};assert preferred_totals=={'Ty Pinkins':451980,'Roger F. Wicker':763420};assert sum(r['native_constituents'] for r in preferred)==1736
    save(OUT/'native-2024-senate-reviewed-84views.json',dict(qualification='Complete84 historical county-packet Senate native views, two named fields only. Preferred82 comprise1736 disjoint native source constituents but have an explicit unallocated1-vote Tunica primary disagreement. Alternative packets and11Kemper unofficial observations remain nonadditive. Full presidential/historical/method and current geography acceptance remain separate.',prior_own_ledger_path=pin['prior_own_ledger_path'],prior_own_ledger_sha256=pin['prior_own_ledger_sha256'],checkpoint_reference_path=pin['reference_path'],checkpoint_reference_sha256=pin['reference_original_sha256'],explicit_wrap_representation_aliases=wraps,previous_60view_source_literal_peer_disagreements=prior['source_literal_peer_disagreements'],previous_60view_accepted_reading_box_repairs=prior['accepted_reading_box_repairs'],current_checkpoint_box_differences=bound_changes,sources=sources))
    writecsv(OUT/'native-2024-senate-reviewed-84views.csv',flat);save(OUT/'native-2024-senate-reviewed-controls-84views.json',dict(source_views=84,county_coverage=82,source_pages=sum(len(s['pages']) for s in sources),role_counts=dict(roles),candidate_numeric_or_null_positions=4642,all84_sourceTOTALs_close_components=True,preferred82_native_constituents=1736,preferred82_candidate_sums=preferred_totals,preferred82_named_pair_denominator=sum(preferred_totals.values()),certified_named_pair_denominator=1215401,native_minus_certified={'Ty Pinkins':-1,'Roger F. Wicker':0},printed_id_disagreements=metadata,empty_ID_representation_scope=dict(count=empty_id_representations,own_representation='',peer_representation=None,qualification='Both unparsed/missing optional ID metadata, explicitly not positive printed-ID agreement or evidence no code is printed; complete source labels preserved.'),current_checkpoint_box_differences=bound_changes,source_controls=checks,complete_2024_named_Senate_native_source_inventory=True,all_candidate_native_complete=False,historical_native_complete=False,current2026_identity_approved=False));print('84views/82counties/1779native alternative scopes/1736preferred/4642positions; Tunica1explicit;',len(bound_changes),'boxmetadata differences')
if __name__=='__main__':main()
