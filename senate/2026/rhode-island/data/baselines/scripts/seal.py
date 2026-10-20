"""Final authoring operation: seal first, full manifest last. Refuses replacement."""
import datetime,json
from common import *
def main():
    if (BASE/'final-seal.json').exists() or (BASE/'asset-manifest.json').exists():raise SystemExit('Already sealed; no replacement')
    validation=json.loads((BASE/'validation.json').read_text());require=validation['all_passed']
    if not require:raise SystemExit('Validation failed')
    owned=lambda: sorted([p for p in BASE.rglob('*') if p.is_file()]+[STATE/'county-partisanship.md',STATE/'data/county-baselines.csv'])
    before=owned()
    seal={'schema':'ri-baseline-final-seal-v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'validation_sha256':sha((BASE/'validation.json').read_bytes()),'validation_checks':validation['check_count'],
        'source_scope':'five original historical candidate universes, complete native/municipal/admin/statistic scopes',
        'bodies_before_seal':[{'path':str(p.relative_to(STATE)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in before],
        'coordinator_acceptance':False,'current_geography_approved':False,'current_final_ballot_mapping':None,
        'writein_scope_qualification':'Full source1227/8discrepancies; peer row6-onward1226/9discrepancies; Cranston actual row5 retained',
        'probability_calibrated':False,'reverse_current_manifest_digest':None,
        'next_and_last_owned_write':'asset-manifest.json; then read-only audit only'}
    write_json('final-seal.json',seal)
    references=[]
    for r in inputs().values():
        references.append({'id':r['id'],'path':r['body_path'],'compression':'gzip','raw_sha256':r['raw_sha256'],
            'raw_bytes':r['raw_bytes'],'stored_sha256':r['stored_sha256'],'stored_bytes':r['stored_bytes'],'ownership':'shared original read-only reference'})
    manifest={'schema':'ri-baseline-owned-assets-v1','excludes_only_itself':True,
        'owned_assets':[{'path':str(p.relative_to(STATE)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in owned()],
        'external_original_references':references,'coordinator_acceptance':False,
        'peer_scope':'fixed captured final bodies only; source/key equality scoped,11 whitespace and1writein scan-start differences preserved'}
    write_json('asset-manifest.json',manifest)
    print(json.dumps({'manifest_sha256':sha((BASE/'asset-manifest.json').read_bytes()),'seal_sha256':sha((BASE/'final-seal.json').read_bytes()),
        'owned_targets':len(manifest['owned_assets']),'original_references':len(references),'total_owned_bytes':sum(x['bytes'] for x in manifest['owned_assets'])},indent=2))
if __name__=='__main__':main()
