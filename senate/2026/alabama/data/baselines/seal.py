#!/usr/bin/env python3
"""Seal validated owned artifacts, manifest LAST. Run validate.py --audit next."""
import datetime,hashlib,json,pathlib
BASE=pathlib.Path(__file__).resolve().parent;STATE=BASE.parent.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    validation=json.loads((BASE/'validation.json').read_text());assert validation['status']=='pass'
    cli=json.loads((BASE/'cli-validation.json').read_text());assert cli['passed']==cli['actual_cli_cases']
    seal={'schema':'AL-partisanship-seal-v1','sealed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owned_scope':['county-partisanship.md','data/county-baselines.csv','data/baselines/**'],'validation_sha256':sha((BASE/'validation.json').read_bytes()),'historical_coverage':{'county_rows':201,'native_rows':6270,'raw_members':201,'native2024':2085,'native2024_priority':887,'native2024_remainder':1198},'original_first_evidence_preserved':True,'peer':'frozen actual turnout worker; source-only reciprocal; no peer input to calculations','qualifications':validation['external_qualifications'],'manifest_excludes_only_itself':True,'manifest_hash_in_seal':None,'instruction':'manifest written last; follow only with read-only exact audit; no owned writes after final manifest'}
    (BASE/'final-seal.json').write_text(json.dumps(seal,indent=2,allow_nan=False)+'\n')
    paths=sorted([STATE/'county-partisanship.md',STATE/'data/county-baselines.csv']+[p for p in BASE.rglob('*') if p.is_file() and p!=BASE/'asset-manifest.json'])
    assets=[]
    for p in paths:
        assert p.stat().st_size<40000000
        assert '__pycache__' not in p.parts and 'node_modules' not in p.parts
        assets.append({'path':str(p.relative_to(STATE)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())})
    manifest={'schema':'AL-partisanship-assets-v1','scope':'Exact owned report, county CSV, every baseline script/source/receipt/history/proof/fixture/validation/seal. Excludes ONLY itself. Shared original bodies pinned individually in source references, not copied.','assets':assets}
    (BASE/'asset-manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'assets':len(assets),'manifest_sha256':sha((BASE/'asset-manifest.json').read_bytes())}))
if __name__=='__main__':main()
