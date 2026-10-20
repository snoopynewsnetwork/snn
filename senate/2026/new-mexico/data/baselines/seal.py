#!/usr/bin/env python3
"""Acyclic final owned inventory and exact shared original-body references."""
import gzip,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;STATE=D.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    from validate import owned
    assert json.loads((D/'validation.json').read_text())['status']=='pass'
    regression=json.loads((D/'repair-regressions/results.json').read_text());invariant=json.loads((D/'repair-regressions/historical-invariance.json').read_text());assert regression['status']==invariant['status']=='pass'
    attestation={'status':'pre_manifest_checks_passed','phase':'validation/regression/history verified before final manifest; final manifest is audited read-only afterward','calculator_sha256':sha((D/'calculator.py').read_bytes()),'validation_sha256':sha((D/'validation.json').read_bytes()),'regression_sha256':sha((D/'repair-regressions/results.json').read_bytes()),'historical_invariance_sha256':sha((D/'repair-regressions/historical-invariance.json').read_bytes()),'prior_manifest_sha256':invariant['prior_manifest_sha256'],'original_first_pin_sha256':invariant['original_first_pin_sha256'],'history_freeze_sha256':invariant['freeze_sha256'],'regression_cases':regression['case_count'],'all21suppliedcases_pass':True,'current_manifest_not_pinned_here':True,'approvals':{'current_results':False,'legal_operational':False,'geography':False,'feed':False,'forecast':False,'coordinator_publication':False},'reciprocal_scope':'Source-core pre-repair capture only; calculators/scenarios/report/final manifest and future bytes excluded.'}
    (D/'final-seal.json').write_text(json.dumps(attestation,indent=2)+'\n')
    def row(p):
        b=p.read_bytes();assert len(b)<40000000;return {'path':str(p.relative_to(STATE)),'bytes':len(b),'sha256':sha(b)}
    refs=json.loads((D/'source/original-references.json').read_text());external={}
    for r in refs:
        p=STATE/r['asset'];b=p.read_bytes();assert sha(b)==r['stored_sha256']and sha(gzip.decompress(b))==r['raw_sha256'];external[r['asset']]={**row(p),'raw_sha256':r['raw_sha256'],'raw_bytes':r['bytes'],'source_ids':[]}
    for r in refs:external[r['asset']]['source_ids'].append(r['id'])
    result={'schema':'nm-baselines-assets-1','self_excluded':True,'self_exclusion_reason':'No self hash or reciprocal manifest/validation hash cycle. Validation sealed first; --audit reads only.','owned':list(map(row,owned())),'external_original_assets':list(external.values()),'source_receipts':'data/baselines/source/original-references.json','fresh_receipts':'data/baselines/source/fresh-observations.json','superseded_supplemental_entities':'Some own supplemental HTML body variants precede final fresh receipt; header/retrieval receipt gap disclosed in source/SCHEMA.md. All retained bytes inventoried; no pinned historical provenance gap.'}
    (D/'asset-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'owned_assets':len(result['owned']),'external_original_assets':len(external),'all_stored_below_40000000':True}))
if __name__=='__main__':main()
