"""Read-only peer replay AFTER complete own preferred original transcriptions.

Freeze peer accepted batches, retaining exact bytes and source-page/label checks.
These comparisons do not establish identical rasters or accepted numeric polygons.
"""
import argparse,csv,gzip,io,json
from collections import Counter
from sources import OUT,BASE,save,sha,original
from extract_replay_president import NAMES
def role(r):
    if r in ['summary_TOTAL','source_TOTAL','TOTAL']:return 'TOTAL'
    if r in ['unused','unused_template_column']:return 'unused'
    if r=='parallel_native_observation':return 'parallel'
    return 'native'
def fold(x):return ' '.join((x or '').split())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--capture',action='store_true');ap.add_argument('--version',default='through-batch33-v4');ap.add_argument('--through-batch',type=int,default=33);a=ap.parse_args();assert 11<=a.through_batch<=33;folder=OUT/'source'/('presidential-peer-'+a.version);snap=folder/'snapshot.json';stems=['tunica','perry','hinds','small']+[f'batch{n}' for n in range(2,a.through_batch+1)]
    if a.capture and not snap.exists():
        folder.mkdir(exist_ok=True);pins=[]
        names=[f'{stem}-presidential-original-{suffix}' for stem in stems for suffix in ['cells.csv','readings.json']]+['winston-allfield-original-cells.csv','winston-allfield-original-readings.json']
        for filename in names:
            p=BASE/'data/turnout'/filename;raw=p.read_bytes();stored=gzip.compress(raw,mtime=0);q=folder/(p.name+'.gz');assert len(stored)<40000000;q.write_bytes(stored);pins.append(dict(original_path=str(p.relative_to(BASE)),original_bytes=len(raw),original_sha256=sha(raw),stored_path=str(q.relative_to(BASE)),stored_bytes=len(stored),stored_sha256=sha(stored)))
        save(snap,dict(qualification='Exact accepted peer original-reading ledgers and flat source cells, captured read-only only after own82preferred original9Pres transcription. No peer votes imported to own readings.',through_batch=a.through_batch,pins=pins))
    sx=json.loads(snap.read_text());peerfiles={}
    for pin in sx['pins']:
        stored=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(stored);assert len(stored)==pin['stored_bytes'] and sha(stored)==pin['stored_sha256'] and len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256'];peerfiles[pin['original_path']]=raw
    coverage=json.loads((OUT/'native-allfield-coverage.json').read_text());assert coverage['complete_statewide_nine_presidential_native'];ours={};ownpins=[];native_index={(s['source_id'],p['page']):p for s in json.loads((OUT/'native-2024-senate-reviewed-84views.json').read_text())['sources'] for p in s['pages']}
    for pin in coverage['inputs']:
        p=BASE/pin['path'];assert sha(p.read_bytes())==pin['sha256'];x=json.loads(p.read_text());ss=x['sources'] if 'sources' in x else [x];ownpins.append(pin)
        for s in ss:
            for pg in s['pages']:
                if 'columns' in pg:cols=pg['columns'];roles=[role(c['unit_type']) for c in cols]
                else:
                    roles=[role(r) for r in pg['roles']];cols=pg.get('headers')
                    if cols is None:
                        original_cols=native_index[s['source_id'],pg['page']]['columns'];assert len(original_cols)==len(roles)
                        cols=[dict(source_column=c['source_column'],label_literal=pg['labels_literal'][i] if i<len(pg['labels_literal']) else '') for i,c in enumerate(original_cols)]
                for f in pg['fields']:
                    name=f.get('candidate',f.get('field'))
                    if name not in NAMES:continue
                    for c,r,v in zip(cols,roles,f['values']):
                        k=(s['source_id'],pg['page'],c['source_column'],name);assert k not in ours;ours[k]=dict(value=v,role=r,label=c.get('label_literal',c.get('native_label_literal','')),raw_sha256=s['raw_sha256'])
    diffs=[];labels=[];label_aliases=[];role_diffs=[];counts=Counter();sourcecounts={};seen=set();rawchecks=set();missing=[]
    for path,raw in peerfiles.items():
        if not path.endswith('.csv'):continue
        for r in csv.DictReader(io.StringIO(raw.decode())):
            if r['candidate'] not in NAMES:continue
            k=(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']);assert k not in seen;seen.add(k);o=ours.get(k)
            if o is None:missing.append(k);continue
            assert o['raw_sha256']==r['source_raw_sha256'];rawchecks.add((r['source_id'],o['raw_sha256']));val=r.get('direct_original_value',r.get('direct_original_visual_value'));v=None if val in ['',None] else int(val);pr=role(r['role']);counts[pr]+=1;sourcecounts.setdefault(r['source_id'],Counter())[pr]+=1
            if o['value']!=v:diffs.append(dict(key=k,own=o['value'],peer=v))
            if o['role']!=pr:role_diffs.append(dict(key=k,own=o['role'],peer=pr))
            if fold(o['label'])!=fold(r['label_literal']):
                q=dict(key=k,own=o['label'],peer=r['label_literal'])
                known_wrap=a.through_batch>=27 and k[0]=='sos-2024-county-holmes' and k[1:3] in [(3,1),(3,4)] and (o['label'],r['label_literal']) in [('Beat 4 Thornton (A-\nZ)','Beat 4 Thornton (A-Z)'),('Beat 5 Lexington (A-\nZ)','Beat 5 Lexington (A-Z)')]
                if known_wrap:label_aliases.append(dict(**q,qualification='Exact two source-header hyphen-wrap representations retained separately; unequal under whitespace-only folding. No source label or frozen prior witness is rewritten.'))
                else:labels.append(q)
    for sid,h in rawchecks:assert sha(original(sid))==h
    result=dict(status='pass_bounded_post_original_peer_replay' if not(diffs or labels or role_diffs or missing) else 'differences_require_original_review',peer_snapshot=dict(path=str(snap.relative_to(BASE)),bytes=snap.stat().st_size,sha256=sha(snap.read_bytes())),own_original_reading_inputs=ownpins,compared_positions=len(seen),source_views=len(sourcecounts),candidate_positions_by_role=dict(counts),source_counts={k:dict(v) for k,v in sourcecounts.items()},value_differences=diffs,label_differences_after_whitespace_only=labels,role_differences=role_diffs,missing_own_positions=missing,source_raw_hashes_verified=len(rawchecks),qualification='Actual peer accepted9Pres fields only, after own original typed all82preferred. Source raw hash/PDFpage/physical column ordinal and literal original header are jointly checked; no cross-year or name-only join, no raster/numeric-polygon equality or printed-ID agreement inferred. Prior Alcorn/Coahoma all11 independent comparison remains separately pinned. Complete remaining peer/native-method/history/currentgeo gates are not implied.')
    separate=OUT/'native-allfield-peer-reconciliation.json';two=json.loads(separate.read_text());assert two['compared_positions']==484 and two['numeric_positions_including_TOTAL']==407 and two['unused_null_positions']==77
    separate_ids={s['source_id'] for s in two['sources']};assert not(separate_ids & set(sourcecounts))
    assert all(c.get('native',0)%9==0 for c in sourcecounts.values())
    native_count=counts['native']//9+35;source_count=len(sourcecounts)+2
    result.update(through_batch=sx.get('through_batch'),separate_original_all11_peer_proof=dict(path=str(separate.relative_to(BASE)),bytes=separate.stat().st_size,sha256=sha(separate.read_bytes()),source_ids=sorted(separate_ids),native_constituents=35),bounded_preferred_source_views_including_separate_two=source_count,bounded_preferred_native_constituents_including_separate_two=native_count,remaining_preferred_source_views=82-source_count,remaining_preferred_native_constituents=1736-native_count,complete_preferred82_named_presidential_peer_scope=source_count==82 and native_count==1736,current2026_geography_approved=False,complete_historical_methods=False)
    if a.through_batch>=27:
        outside=[dict(key=k,**o) for k,o in sorted(ours.items()) if k[0] in sourcecounts and k not in seen]
        assert all(o['role']=='unused' and o['value'] is None for o in outside),'Uncompared numeric/native/TOTAL/parallel positions require original-scope review'
        result.update(own_positions_outside_peer_flat_scope=outside,own_positions_outside_peer_flat_scope_count=len(outside),blank_scope_qualification='Older direct Perry/Tunica peer CSVs omit unprinted template positions. Their omission is preserved; no peer nulls are imputed and no same full blank-position scope is claimed. Own original blank readings remain separate.',complete_all_blank_position_peer_scope=not outside,label_representation_aliases_after_whitespace_only=label_aliases,label_representation_alias_count=len(label_aliases),all_labels_identical_after_whitespace_only=not label_aliases and not labels)
    save(OUT/'native-presidential-peer-batches-reconciliation.json',result);print(result['status'],result['source_views'],result['compared_positions'],dict(counts),'value/label/role/missing',len(diffs),len(labels),len(role_diffs),len(missing));assert not(diffs or labels or role_diffs or missing)
    frozen=folder/'reconciliation.json';body=(OUT/'native-presidential-peer-batches-reconciliation.json').read_bytes()
    if frozen.exists():assert frozen.read_bytes()==body,'New input/metadata version requires a new immutable peer replay version'
    else:frozen.write_bytes(body)
if __name__=='__main__':main()
