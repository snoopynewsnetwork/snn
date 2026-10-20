#!/usr/bin/env python3
"""Verify immutable prior handoff, exact original references and unchanged historical core."""
import gzip,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;STATE=D.parents[1];H=D/'repair-history/pre-input-validation-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    cap=json.loads((H/'freeze.json').read_text());assert sha((H/'freeze.json').read_bytes())=='b0291453d6b01926e9ea05a6276c863c2fcf59d226890456e4660d377f97af48'
    allowed={'county-partisanship.md',*[f'data/baselines/{p}'for p in ['calculator.py','render_report.py','run_offline.py','validate.py','seal.py','source/SCHEMA.md','validation.json','live-synthetic-scenarios.json']]}
    changed=[];unchanged=[];errors=[]
    for r in cap['files']:
        z=(STATE/r['stored_path']).read_bytes();b=gzip.decompress(z)
        assert sha(z)==r['stored_sha256']and len(z)==r['stored_bytes']and sha(b)==r['raw_sha256']and len(b)==r['raw_bytes']
        if r['scope']!='prior-owned':continue
        p=STATE/r['original_path'];same=sha(p.read_bytes())==r['raw_sha256']
        (unchanged if same else changed).append(r['original_path'])
        if not same and r['original_path']not in allowed:errors.append(r['original_path'])
        if r['original_path']=='data/baselines/live-synthetic-scenarios.json':
            old=json.loads(b);new=json.loads(p.read_text())
            assert set(old)==set(new)
            for k,v in old.items():
                if not v['status'].startswith('invalid'):assert new[k]==v,('valid synthetic meaning changed',k)
    for r in cap['external_original_assets']:
        z=(STATE/r['path']).read_bytes();assert sha(z)==r['sha256']and len(z)==r['bytes'];b=gzip.decompress(z);assert sha(b)==r['raw_sha256']and len(b)==r['raw_bytes']
    # Re-derive key invariant counts from current original objects, without producer imports.
    ext=json.loads((D/'original-extract.json').read_text());native={k:sum(r['scope']=='Precinct'for r in v['rows'])for k,v in ext.items()}
    assert native=={'2024-senate':2201,'2020-senate':1959,'2022-governor':2196,'2024-president':2202}
    for v in json.loads((D/'priority-contract.json').read_text()).values():assert v['canonical_dispatch_keys']==[]and v['certified_native_minimum80']is None and v['certified_native_order']is None
    assert sha((D/'source/independent-first-pin.json').read_bytes())==cap['original_first_pin_sha256']=='6770ae96313d9f9d2e0964da2470fd903d1f72122e260eece7635370aca014b7'
    out={'status':'pass'if not errors else 'fail','freeze_sha256':sha((H/'freeze.json').read_bytes()),'prior_manifest_sha256':cap['prior_manifest_sha256'],'prior_bodies_verified':len(cap['files']),'prior_owned_verified':cap['prior_owned_count'],'external_original_references_verified':len(cap['external_original_assets']),'original_first_pin_sha256':cap['original_first_pin_sha256'],'byte_unchanged_prior_owned':unchanged,'allowed_repair_changed_prior_owned':changed,'unexpected_changes':errors,'all_valid_prior_live_cases_equal':True,'native_rows':native,'certified_native_priority':None,'canonical_dispatch_keys':[],'scope':'Byte invariance to pre-repair archive; source/count/mask/native/target and historical scenario artifacts unchanged. Calculator and documented repair metadata are outside any reciprocal source-core equality claim.'}
    (D/'repair-regressions/historical-invariance.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'unchanged_prior_owned':len(unchanged),'changed_allowed':len(changed),'external_originals':64}));assert not errors,errors
if __name__=='__main__':main()
