"""Post-original reciprocal all11 comparison to explicitly pinned peer2024body.
Older through33v4 omission/alias witnesses remain unchanged. No peer values
are imported into source readings or priority contracts.
"""
import csv,gzip,io,json
from collections import Counter
from sources import OUT,BASE,sha,save

def role(r):
    if r in ['summary_TOTAL','source_TOTAL','TOTAL']:return 'TOTAL'
    if r in ['unused','unused_template_column']:return 'unused'
    if r=='parallel_native_observation':return 'parallel'
    return 'native'
def fold(v):return ' '.join((v or '').split())
def main():
    ownsp=OUT/'source/native-allfield-82views/snapshot.json';ownsnap=json.loads(ownsp.read_text());docs={}
    for pin in ownsnap['pins']:
        z=(BASE/pin['frozen_path']).read_bytes();r=gzip.decompress(z);assert len(z)==pin['stored_bytes'] and sha(z)==pin['stored_sha256'] and len(r)==pin['original_bytes'] and sha(r)==pin['original_sha256'];docs[pin['original_path'].split('/')[-1]]=json.loads(r) if pin['original_path'].endswith('.json') else r
    own={};fips={}
    def put(key,value,rr,label,h,f=None):
        item=dict(value=value,role=role(rr),label=label,hash=h)
        if key in own:assert own[key]==item,(key,own[key],item)
        own[key]=item
        if f:
            if key[0] in fips:assert fips[key[0]]==f
            fips[key[0]]=f
    for name in ['native-allfield-additional-candidate-votes.csv','winston-native-allfield-candidate-votes.csv']:
        for r in csv.DictReader(io.StringIO(docs[name].decode())):
            put((r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']),None if r['value']=='' else int(r['value']),r['role'],r.get('literal_native_label',r.get('label_literal')),r['raw_sha256'],r['county_fips'])
    for name in ['alcorn-readings.json','coahoma-updated-readings.json','native-source-exception-readings.json']:
        doc=docs[name];ss=doc.get('sources',[doc])
        for s in ss:
            for pg in s['pages']:
                cols=pg.get('columns');roles=pg.get('roles');labels=pg.get('labels_literal')
                for field in pg['fields']:
                    name=field.get('candidate',field.get('field'))
                    for i,v in enumerate(field['values']):
                        c=cols[i] if cols is not None else {};put((s['source_id'],pg['page'],c.get('source_column',i+1),name),v,c.get('unit_type',roles[i] if roles else None),c.get('label_literal',c.get('native_label_literal',labels[i] if labels and i<len(labels) else '')),s['raw_sha256'],s.get('fips',s.get('county_fips')))
    # Each source has11fields/column and only82preferred source publications.
    assert len(own)==24926 and len({k[0] for k in own})==82
    peerpath=BASE/'data/turnout/source/2024-preferred-all11-source-fields-v1.json.gz';z=peerpath.read_bytes();r=gzip.decompress(z);assert len(z)==96203 and sha(z)=='d066e45bebca7ba66163989165a430164f5b84cef61d9e2cda7e4bc4e1d23b6b' and len(r)==2048366 and sha(r)=='b2a7e234eeb226bd13f35d3a4c32c867f88f7d59a680ec059a7378c036f1fbae';peer=json.loads(r);assert peer['source_views']==82 and peer['native_constituents']==1736 and peer['source_columns']==2266
    compared=set();counts=Counter();labelaliases=[];diffs=[];seenunit=set()
    for col in peer['columns']:
        uk=(col['source_id'],col['source_page'],col['source_column']);assert uk not in seenunit;seenunit.add(uk);vv=col['Senate_candidate_votes']|col['president_candidate_votes'];assert len(vv)==11
        if col['source_id'] in fips:assert fips[col['source_id']]==col['parent_county_fips']
        for name,v in vv.items():
            k=uk+(name,);assert k in own and k not in compared;compared.add(k);o=own[k];assert o['hash']==col['source_raw_sha256'];pr=role(col['role']);counts[pr]+=1
            if o['value']!=v or o['role']!=pr:diffs.append(dict(key=k,own=o,peer_value=v,peer_role=pr))
            if fold(o['label'])!=fold(col['label_literal']):
                alias=col['source_id']=='sos-2024-county-holmes' and col['source_page']==3 and col['source_column'] in [1,4] and (o['label'],col['label_literal']) in [('Beat 4 Thornton (A-\nZ)','Beat 4 Thornton (A-Z)'),('Beat 5 Lexington (A-\nZ)','Beat 5 Lexington (A-Z)')]
                if alias:labelaliases.append(dict(key=k,own=o['label'],peer=col['label_literal'],qualification='Exact hyphen-wrap representations unequal under whitespace fold; both retained, no source/current geography normalization'))
                else:diffs.append(dict(key=k,own_label=o['label'],peer_label=col['label_literal']))
    assert compared==set(own) and not diffs,(len(compared),diffs[:8]);assert counts==Counter(dict(native=19096,TOTAL=902,unused=4807,parallel=121))
    old=json.loads((OUT/'native-presidential-peer-batches-reconciliation.json').read_text());assert old['own_positions_outside_peer_flat_scope_count']==126
    newly_in_scope=old['own_positions_outside_peer_flat_scope'];assert len(newly_in_scope)==126
    for q in newly_in_scope:
        k=tuple(q['key']);assert k in compared and own[k]['value'] is None and own[k]['role']=='unused'
    folder=OUT/'source/2024-all11-complete-peer-v1';folder.mkdir(exist_ok=True);snapshot=dict(own_snapshot=dict(path=str(ownsp.relative_to(BASE)),bytes=ownsp.stat().st_size,sha256=sha(ownsp.read_bytes())),peer_body=dict(path=str(peerpath.relative_to(BASE)),stored_bytes=len(z),stored_sha256=sha(z),original_bytes=len(r),original_sha256=sha(r),reuse='Exact read-only peer immutable gzip; original reading provenance is embedded in this complete body; no duplicated source originals'),qualification='New complete24926-position named-field/null source scope after own82preferred original transcription. Does not replace older through33v4 which had126unlisted peer unused positions. No exact raster/header/numeric window/printed-ID/current identity equivalence.')
    sp=folder/'snapshot.json'
    if sp.exists():assert json.loads(sp.read_text())==snapshot
    else:save(sp,snapshot)
    result=dict(status='pass_post_original_complete_preferred82_all11_source_position_replay',input_snapshot=dict(path=str(sp.relative_to(BASE)),bytes=sp.stat().st_size,sha256=sha(sp.read_bytes())),source_views=82,source_columns=2266,native_units=1736,positions=len(compared),positions_by_role=dict(counts),named_source_presidential_total=peer['presidential_native_named_vote_sum'],signed_presidential_total=peer['signed_presidential_named_vote_sum'],Tunica_Harris_source_minus_signed=peer['Tunica_Harris_source_minus_signed'],new_explicit_peer_unused_positions=126,older_v4_body_unchanged=dict(path='data/baselines/native-presidential-peer-batches-reconciliation.json',bytes=(OUT/'native-presidential-peer-batches-reconciliation.json').stat().st_size,sha256=sha((OUT/'native-presidential-peer-batches-reconciliation.json').read_bytes())),value_role_differences=diffs,literal_label_representation_aliases=labelaliases,all_labels_equal_under_whitespace_only=not labelaliases,qualification='Source hash/page/physical column/named candidate cells and roles agree, with explicit source wrap representations. 126previously unlisted peer template blanks now explicitnull, never numericzero. Raw source vintage alternatives nonadditive. Complete named-field comparison is not method/ballot/registration/current2026geo or887acceptance.')
    save(OUT/'native-2024-all11-complete-peer-reconciliation.json',result);fp=folder/'reconciliation.json';body=(OUT/'native-2024-all11-complete-peer-reconciliation.json').read_bytes()
    if fp.exists():assert fp.read_bytes()==body
    else:fp.write_bytes(body)
    print('PASS2024all11',len(compared),dict(counts),'aliases',len(labelaliases),'newpeerblank126')
if __name__=='__main__':main()
