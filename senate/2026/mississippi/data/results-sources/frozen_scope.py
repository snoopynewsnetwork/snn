"""Independent read-only full payload and original-byte verification.

External acceptance is path-only. Its entire final contract is dereferenced,
without copying it or promoting peer transcripts to independent originals.
No imports of producer builders/calculators/validators; no source mutations.
"""
from pathlib import Path
import csv, gzip, hashlib, io, json
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
ACCEPTANCE='data/coordinator-priority-acceptance.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return sha(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
def ordered_equal(a,b):
    assert type(a) is type(b),(type(a),type(b))
    if isinstance(a,dict):
        assert list(a)==list(b)
        for k in a:ordered_equal(a[k],b[k])
    elif isinstance(a,list):
        assert len(a)==len(b)
        for x,y in zip(a,b):ordered_equal(x,y)
    else: assert a==b,(a,b)
def scalar_stats(x):
    c=Counter()
    def walk(v):
        c[type(v).__name__]+=1
        if isinstance(v,dict):
            for vv in v.values():walk(vv)
        elif isinstance(v,list):
            for vv in v:walk(vv)
    walk(x);return dict(c)
def run():
    a=json.loads((ROOT/ACCEPTANCE).read_bytes());assert a['status']=='accepted_historical_dispatch_only' and a['accepted']
    checked={};originals={};components={}
    def read(path,expected=None,size=None):
        b=(ROOT/path).read_bytes()
        if expected: assert sha(b)==expected,path
        if size is not None: assert len(b)==size,path
        checked[path]=dict(path=path,bytes=len(b),sha256=sha(b));return b
    for k in ['contract','independent_reviews','frozen_first_pair_reports','frozen_first_pair_manifests','frozen_first_pair_validations','complete_source_dependencies']:
        for p in a[k] if isinstance(a[k],list) else [a[k]]:read(p['path'],p['sha256'],p['bytes'])
    cb=read(**dict(path=a['contract']['path'],expected=a['contract']['sha256'],size=a['contract']['bytes']))
    contract=json.loads(cb)
    # Resolve full body directly, then roundtrip with ordered recursive comparison.
    ordered_equal(contract,json.loads(json.dumps(contract,ensure_ascii=False)))
    assert contract['ordered_priority_keys']==a['ordered_priority_keys']
    allkeys=[x['key'] for x in contract['all_unit_order']]
    assert contract['source_native_preferred_ordered_keys']==allkeys
    assert allkeys[:887]==a['ordered_priority_keys']
    assert contract['remainder']['ordered_keys']==allkeys[887:]
    assert contract['native_priority_by_parent']==a['parent_priority_native_keys']
    def snapshot(path):
        s=json.loads(read(path))
        for p in s.get('pins',[]):
            sp=p.get('stored_path',p.get('frozen_path'))
            if not sp:continue
            b=read(sp,p['stored_sha256'],p['stored_bytes']);raw=gzip.decompress(b)
            assert sha(raw)==p['original_sha256'] and len(raw)==p['original_bytes']
            components[p['original_path']]=raw
        return s
    snapshot('data/baselines/source/native-priority-v2/snapshot.json')
    snapshot('data/baselines/source/native-priority-v2-field-evidence-v1/snapshot.json')
    v2=json.loads(components['data/baselines/native-priority-contract-v2.json'])
    assert v2['ordered_native_keys']==allkeys
    assert v2['ordered_priority_native_keys']==contract['ordered_priority_keys']
    assert v2['ordered_nonpriority_native_keys']==contract['remainder']['ordered_keys']
    assert v2['parent_priority_native_keys']==contract['native_priority_by_parent']
    assert len(v2['parent_all_native_keys'])==82
    dep=contract['preferred_2024_all11_source_fields_dependency']
    raw=gzip.decompress(read(dep['path'],dep['stored_sha256'],dep['stored_bytes']))
    assert sha(raw)==dep['raw_sha256'] and len(raw)==dep['raw_bytes']
    all11=json.loads(raw);cols=all11['columns'];assert len(cols)==2266
    roles=Counter(c['role'] for c in cols);counts=Counter()
    for c in cols:
        assert len(c['Senate_candidate_votes'])==2 and len(c['president_candidate_votes'])==9
        for v in list(c['Senate_candidate_votes'].values())+list(c['president_candidate_votes'].values()):
            assert v is None or (type(v) is int and v>=0)
            counts['null' if v is None else 'numeric']+=1
    assert counts=={'numeric':20119,'null':4807}
    by={x['key']:x for x in cols}; assert len(by)==len(cols)
    rolemap={'native':'native_reporting_constituent','unused':'unused_template_column','TOTAL':'source_TOTAL','parallel':'parallel_native_observation'}
    label_differences=[];paired_fields=0
    for vc in v2['all_preferred_source_columns']:
        c=by[vc['source_position_key']]
        assert vc['source_id']==c['source_id'] and vc['source_raw_sha256']==c['source_raw_sha256']
        assert vc['PDFpage']==c['source_page'] and vc['physical_source_column']==c['source_column']
        assert vc['county_fips']==c['parent_county_fips'] and rolemap[vc['role']]==c['role']
        both=dict(c['Senate_candidate_votes'],**c['president_candidate_votes'])
        assert vc['candidate_votes']==both;paired_fields+=len(both)
        if vc['label_literal']!=c['label_literal']:
            label_differences.append(dict(key=c['key'],v2_literal=vc['label_literal'],turnout_dependency_literal=c['label_literal'],scope='Distinct retained source-reading representations; no alias or current join inferred'))
    assert paired_fields==24926
    native=[by[k] for k in allkeys]
    assert len(native)==1736 and all(c['role']=='native_reporting_constituent' for c in native)
    sums={name:sum(c['Senate_candidate_votes'][name] for c in native) for name in ['Ty Pinkins','Roger F. Wicker']}
    assert sums=={'Ty Pinkins':451980,'Roger F. Wicker':763420}
    volumes=[sum(c['Senate_candidate_votes'].values()) for c in native]
    order=sorted(native,key=lambda c:(-sum(c['Senate_candidate_votes'].values()),c['key']))
    assert [c['key']for c in order]==allkeys
    for rank,c in enumerate(native,1):
        r=contract['all_unit_order'][rank-1]
        assert r['rank']==rank and r['candidate_votes']==c['Senate_candidate_votes']
        assert r['named_candidate_votes']==sum(c['Senate_candidate_votes'].values())
        assert r['cumulative_votes']==sum(sum(v['Senate_candidate_votes'].values())for v in native[:rank])
    assert (sum(volumes[:15]),sum(volumes[:886]),sum(volumes[:887]),sum(volumes[887:]))==(60019,972157,972656,242744)
    for p,keys in v2['parent_all_native_keys'].items():
        assert set(keys)=={c['key']for c in native if c['parent_county_fips']==p}
    # Verify exact original PDFs for all source views, never transcript as original.
    records={}
    for path in ['data/news/manifest.json','data/turnout/source/acquisition.json','data/baselines/source/references.json']:
        # Mutable aggregate ledgers are locator aids, never frozen build pins.
        for r in json.loads((ROOT/path).read_bytes()):
            if 'raw_sha256' in r: records.setdefault((r['id'],r['raw_sha256']),r)
    def original(sid,raw_hash,path=None,stored_hash=None,size=None):
        if path is None:
            r=records[(sid,raw_hash)];path=r.get('path') or 'data/news/'+r['asset'];stored_hash=r['stored_sha256']
        b=read(path,stored_hash,size);raw=gzip.decompress(b) if path.endswith('.gz') else b
        assert sha(raw)==raw_hash,sid
        originals[sid]=dict(path=path,stored_bytes=len(b),stored_sha256=sha(b),raw_bytes=len(raw),raw_sha256=raw_hash)
    for s in contract['source_native_inventory']:original(s['source_id'],s['raw_sha256'],s['original_path'],records[(s['source_id'],s['raw_sha256'])]['stored_sha256'])
    histref=contract['historical_source_native_dependencies']
    # The main contract's historical path is relative to data/turnout.
    histpath=str(Path(a['contract']['path']).parent/histref['path'])
    hist=json.loads(read(histpath,histref['sha256'],histref['bytes']))
    historical={}
    for year in ['2020','2018']:
        h=hist[year];read(h['canonical_snapshot_path'],h['canonical_snapshot_sha256'],h['canonical_snapshot_bytes'])
        snap=snapshot(h['canonical_snapshot_path'])
        for p in h['canonical_lossless_component_pins']:
            b=read(p['stored_path'],p['stored_sha256'],p['stored_bytes']);raw=gzip.decompress(b)
            assert len(raw)==p['original_bytes'] and sha(raw)==p['original_sha256']
            ordered_equal(json.loads(raw),json.loads(components[p['original_path']])) if p['original_path'].endswith('.json') else None
        if year=='2020':
            sources=json.loads(components['data/baselines/native-2020-additional-readings.json'])['sources']+json.loads(components['data/baselines/coahoma-2020-amendment-readings.json'])['sources']
            flat=list(csv.DictReader(io.StringIO(components['data/baselines/native-2020-additional-candidate-votes.csv'].decode())))
        else:
            sources=json.loads(components['data/baselines/native-2018-original-readings.json'])['sources']
            flat=list(csv.DictReader(io.StringIO(components['data/baselines/native-2018-original-candidate-votes.csv'].decode())))
        assert len(sources)==(104 if year=='2020' else 164)
        expected=h['complete_source_objects_in_ledger_order'];assert [s['source_id']for s in sources]==[s['source_id']for s in expected]
        for s,e in zip(sources,expected):
            assert canonical(s)==e['complete_source_object_sha256'] and s['raw_sha256']==e['source_raw_sha256']
            assert [p['page']for p in s['pages']]==e['pages']
            ordered_equal(s,json.loads(json.dumps(s,ensure_ascii=False)))
        flatmap={(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']):r for r in flat}
        assert len(flatmap)==len(flat)
        checks=0;marks=Counter();nativecount=0;rolecounts=Counter();fieldcounts=Counter()
        for s in sources:
            for page in s['pages']:
                for c in page['columns']:
                    if c['role'] in ['native','source_native_reporting_constituent']:nativecount+=1
                for f in page['fields']:
                    assert len(f['values'])==len(page['columns'])
                    for col,val in zip(page['columns'],f['values']):
                        rolecounts[col['role']]+=1;fieldcounts['null' if val is None else 'numeric']+=1
                        mark=f.get('source_marks',{}).get(str(col['source_column']),'')
                        if mark: marks[mark]+=1;assert val is None
                        k=(s['source_id'],page['page'],col['source_column'],f['candidate'])
                        if k in flatmap:
                            r=flatmap[k];assert r['votes']==('' if val is None else str(val))
                            assert r['role']==col['role'] and r['literal_native_label']==col['label_literal']
                            assert r['source_raw_sha256']==s['raw_sha256']
                            assert r.get('raw_source_mark','')==mark
                            assert r['party_literal']==(f.get('party_literal') or '')
                            checks+=1
        assert checks==len(flat)
        assert nativecount==h['native_observations_across_publications_or_stages']
        if year=='2018':assert marks=={'X':6}
        for r in h['original_pdf_receipts']:original(r['source_id'],r['raw_sha256'],r['stored_path'],r['stored_sha256'],r['stored_bytes'])
        historical[year]=dict(full_source_objects=len(sources),recursive_ordered_objects_pass=True,scalar_stats=scalar_stats(sources),flat_positions_checked=checks,native_observations=nativecount,roles=dict(rolecounts),numeric_null=dict(fieldcounts),literal_marks=dict(marks),new_independent_glyph_readings_from_reuse=0)
    return dict(status='pass_exact_full_payload_original_hashes_and_independent_arithmetic',external_acceptance_path_only=ACCEPTANCE,
                contract=checked[a['contract']['path']],full_contract_recursive_type_stats=scalar_stats(contract),
                preferred_all11_roles=dict(roles),preferred_all11_fields=dict(counts),preferred_v2_to_turnout_field_checks=paired_fields,retained_label_representation_differences=label_differences,historical=historical,
                originals=originals,dependencies=list(checked.values()),current_crosswalk_approved=False),contract,v2,all11,hist,components
if __name__=='__main__':
    r,*_=run();(OUT/'frozen-scope-validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(r['status'],len(r['originals']),len(r['dependencies']))
