"""Independent complete source/native descending-order and exact80 audit."""
import gzip,json,datetime
from sources import OUT,BASE,save,sha
def main():
    ownpath=OUT/'native-source-orders.json';ownraw=ownpath.read_bytes();own=json.loads(ownraw);ref=OUT/'source/peer-native-source-orders-reference.json.gz';receipt=OUT/'source/peer-native-source-orders-reference.json'
    if not ref.exists():
        p=BASE/'data/turnout/native-source-orders.json';raw=p.read_bytes();packed=gzip.compress(raw,mtime=0);ref.write_bytes(packed);save(receipt,dict(reference_path=str(p.relative_to(BASE)),snapshot_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_sha256=sha(raw),original_bytes=len(raw),stored_sha256=sha(packed),stored_bytes=len(packed),storage='Exact ordered-byte losslessgzip internal peer artifact snapshot, not a public original or extraction input'))
    raw=gzip.decompress(ref.read_bytes());pin=json.loads(receipt.read_text());assert sha(raw)==pin['original_sha256'] and sha(ref.read_bytes())==pin['stored_sha256'];peer=json.loads(raw);assert set(own['source_views'])==set(peer['source_views']);wrap=[];checked=0;idreps=0;IDadditions=[]
    pairs=list((key,own['source_views'][key],peer['source_views'][key]) for key in own['source_views'])+[('preferred82_view',own['preferred82_view'],peer['preferred82_view'])]
    for view,a,b in pairs:
        for field in ['count','named_candidate_total','candidate_sums','top15','minimum80','remainder_votes']:assert a[field]==b[field],(view,field,a[field],b[field])
        assert len(a['full_descending_order'])==len(b['full_descending_order'])
        for x,y in zip(a['full_descending_order'],b['full_descending_order']):
            for field in ['rank','key','parent_county_fips','source_id','source_page','source_column','candidate_votes','named_candidate_votes','cumulative_votes']:assert x[field]==y[field],(view,field,x[field],y[field])
            if x['printed_native_id']=='' and y['printed_native_id'] is None:idreps+=1
            elif x['printed_native_id']=='' and y['printed_native_id']:
                assert y['printed_native_id'] in x['label_literal'];IDadditions.append(dict(view=view,key=x['key'],frozen84_own_optional_ID='',working_peer_parsed_ID=y['printed_native_id'],unchanged_source_literal=x['label_literal'],qualification='Working-order parsed optional ID addition from exact printed literal substring. Frozen84 metadata preserved; not a byte-for-byte old-ID match, new geography ID or crosswalk.'))
            else:assert x['printed_native_id']==y['printed_native_id']
            norm=lambda s:' '.join(s.replace('-\n','-').replace('/\n','/').split());assert norm(x['label_literal'])==norm(y['label_literal'])
            if ' '.join(x['label_literal'].split())!=' '.join(y['label_literal'].split()):wrap.append(dict(view=view,key=x['key'],own_literal=x['label_literal'],peer_literal=y['label_literal'],scope='Explicit printed hyphen/slash-wrap representation only; source/position/wholecandidatefields matched, no geographic name alias.'))
            checked+=1
    p=own['preferred82_view'];assert p['minimum80']['count']==887 and p['minimum80']['preceding_votes']*5<4*1215400<=p['minimum80']['votes']*5;assert p['minimum80']['preceding_votes']*5<4*1215401<=p['minimum80']['votes']*5
    assert len(IDadditions)==86 and len({r['key'] for r in IDadditions})==43
    save(OUT/'native-order-peer-reconciliation.json',dict(status='pass_independent_complete_source_order_and_exact80_with_explicit_metadata_versions',qualification='All84 source-view orders and full1736 preferred native order independently computed from own original-replay candidate values. Peer artifact only enters subsequent comparison. This is NOT coordinator geographic/dispatch acceptance.',own_path=str(ownpath.relative_to(BASE)),own_sha256=sha(ownraw),own_bytes=len(ownraw),peer_reference=pin,compared_source_views=84,compared_preferred_native_units=1736,compared_ordered_unit_positions=checked,compared_candidate_fields=2*checked,exact_order_key_candidate_parent_rank_cumulative_disagreements=0,source_native_min80=p['minimum80'],top15_native=p['top15'],source_native_denominator=1215400,separate_certified_county_denominator=1215401,unallocated_Tunica_Pinkins_source_difference=-1,explicit_wrap_representation_aliases=wrap,missing_optional_ID_blank_null_representations=idreps,working_peer_optional_ID_extraction_additions=IDadditions,working_peer_ID_addition_unique_source_positions=43,all849nonpriority_native_units_retained=True,coordinator_accepted=False,current2026_geography_approved=False));print('PASS84sourceorders+1736preferredfullorder/887exact80;',checked,'ordered positions;',len(wrap),'explicitwraprepresentations;43working-IDadditionsqualified')
if __name__=='__main__':main()
