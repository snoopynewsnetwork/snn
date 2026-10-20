"""Acyclic whole-owned inventory. Only manifest itself is excluded."""
from acquire import *
from replay import pin
from validate import owned
import platform,subprocess,zlib
PROOFS=['replay-validation.json','sample-validation.json','historical-validation.json','negative-fixtures.json','validation.json','coverage.json','legal-calculations.json','visual-scope.json','access-qualifications.json']
def seal():
    dump(HERE/'final-seal.json',dict(status='bounded research complete; awaiting coordinator review',authority_path='data/coordinator-source-research-acceptance.json',proofs=[pin('data/results-sources/'+p) for p in PROOFS],environment=dict(Python=platform.python_version(),zlib=zlib.ZLIB_VERSION,Poppler=subprocess.run(['pdftotext','-v'],capture_output=True,text=True,check=True).stderr.strip()),source_observations=2201,county_parents=33,shared_parent_not_discovered_live_feeds=True,canonical_certified_native_priority=None,ordered_priority_keys=[],current_count_admitted=False,current_change_admitted=False,current_join_admitted=False,coordinator_accepted=False,manifest_reverse_pin=False))
    files=[pin(str(p.relative_to(STATE))) for p in owned()]
    dump(HERE/'manifest.json',dict(schema='complete-owned-assets-v1',excluded_only='data/results-sources/manifest.json',owned_files=files,owned_count=len(files),owned_bytes=sum(r['bytes'] for r in files),maximum_owned_file_bytes=max(r['bytes'] for r in files),strict_each_file_bytes_less_than=40000000,external_immutable_references='data/results-sources/immutable-inputs.json',authority_path='data/coordinator-source-research-acceptance.json',current_count_admitted=False,current_change_admitted=False,coordinator_accepted=False))
    return audit()
def audit():
    m=json.loads((HERE/'manifest.json').read_bytes());expected=[pin(str(p.relative_to(STATE))) for p in owned()]
    assert expected==m['owned_files'],'exact complete owned inventory/size/hash'
    assert len(expected)==m['owned_count'] and sum(x['bytes'] for x in expected)==m['owned_bytes']
    assert max(x['bytes'] for x in expected)==m['maximum_owned_file_bytes']<40000000
    assert (HERE/'manifest.json').stat().st_size<40000000
    s=json.loads((HERE/'final-seal.json').read_bytes())
    assert not s['manifest_reverse_pin'] and not s['coordinator_accepted']
    for r in s['proofs']:assert pin(r['path'])==r
    return dict(status='pass',owned_files=len(expected),owned_bytes=m['owned_bytes'],maximum_file_bytes=m['maximum_owned_file_bytes'],manifest_excludes_only_itself=True,read_only=True)
if __name__=='__main__':print(audit() if '--audit' in sys.argv else seal())
