"""Bounded-repair seal: preserve historical bodies, fixed seal, manifest LAST."""
import io,tarfile,json,gzip
from common import *
from repair_validation import historical
def owned():return sorted([STATE/'turnout.md',STATE/'data/county-turnout.csv']+[p for p in ROOT.rglob('*')if p.is_file()])
def run():
    assert not (ROOT/'qa/repaired-body-witness.json').exists(),'Repaired witness already sealed'
    old=historical();validation=json.loads((ROOT/'validation.json').read_text());assert validation['status']=='passed'
    comparison=json.loads((ROOT/'reciprocal/source-core-comparison.json').read_text());assert comparison['status']=='passed'
    capture=json.loads((ROOT/'history/pre-repair-v1/capture.json').read_text());refs={x['path']:x for x in capture['immutable_original_refs']}
    excluded={ROOT/x for x in ['asset-manifest.json','final-seal.json','qa/repaired-body-witness.json','qa/repaired-body-changes.tar.gz']};bodies=[];changed={}
    for path in owned():
        if path in excluded:continue
        b=path.read_bytes();name=str(path.relative_to(STATE));item=dict(path=name,sha256=sha(b),bytes=len(b))
        if name in old and old[name]==b:item['storage']=dict(kind='immutable_original_reference',path=name)if name in refs else dict(kind='historical_tar',archive='history/pre-repair-v1/bodies.tar.gz',member=name)
        elif path.suffix=='.gz'or '.part'in path.name:item['storage']=dict(kind='immutable_evidence_reference',path=name)
        else:changed[name]=b;item['storage']=dict(kind='changed_tar',archive='qa/repaired-body-changes.tar.gz',member=name)
        bodies.append(item)
    buf=io.BytesIO()
    with tarfile.open(fileobj=buf,mode='w',format=tarfile.PAX_FORMAT)as t:
        for name,b in sorted(changed.items()):
            e=tarfile.TarInfo(name);e.size=len(b);e.mtime=0;e.mode=420;t.addfile(e,io.BytesIO(b))
    packed=gzip.compress(buf.getvalue(),mtime=0);assert len(packed)<40000000;(ROOT/'qa/repaired-body-changes.tar.gz').write_bytes(packed)
    dump(ROOT/'qa/repaired-body-witness.json',dict(schema='ri-complete-repaired-body-witness-v1',bodies=bodies,changed_archive=dict(path='qa/repaired-body-changes.tar.gz',sha256=sha(packed),bytes=len(packed),tar_sha256=sha(buf.getvalue())),historical_capture=dict(path='history/pre-repair-v1/capture.json',sha256=sha((ROOT/'history/pre-repair-v1/capture.json').read_bytes())),original_first_witness=dict(path='qa/pre-peer-body-witness.json',sha256=sha((ROOT/'qa/pre-peer-body-witness.json').read_bytes())),terminal_exclusions=[str(p.relative_to(STATE))for p in sorted(excluded)],reconstruction='Each complete body is its historical tar member, unchanged immutable original/evidence file, or current changed-body tar member. Original ZIP/PDF/XLSX bodies are not duplicated. Manifest pins witness/terminal files; fixed seal never pins current manifest.'))
    pins={}
    for name in ['priority-set.json','validation.json','qa/repair-validation.json','reciprocal/source-core-comparison.json','reciprocal/peer-finished-capture/capture.json','qa/pre-peer-body-witness.json','qa/repaired-body-witness.json','qa/repaired-body-changes.tar.gz']:
        b=(ROOT/name).read_bytes();pins[name]=dict(sha256=sha(b),bytes=len(b))
    dump(ROOT/'final-seal.json',dict(schema='ri-turnout-bounded-repair-final-seal-v2',phase='Original-first row5 detail correction and captured-finished-peer source-core review complete; coordinator acceptance pending',pins=pins,peer_id='5d9f9b63-0cf2-4b55-b52b-579cbc1d76d1',peer_manifest_sha256='f3b33d30631cec93796c4aab2becec82a49982da39878421f11c22ea5e1a8620',source_core_agreement='passed; bounded captured source objects and independent order arithmetic only',peer_model_scenario_outcome_equality_claimed=False,original_first_witness_unchanged=True,prior362_historical_bodies_preserved=True,primary_native_csv_source_order_unchanged=True,coordinator_acceptance=False,current_geometry_approval=False,eligible_writein_universe=None,no_manifest_reverse_pin=True,final_read_only_audit_required=True,final_audit_command='python3 -B senate/2026/rhode-island/data/turnout/validate_turnout.py'))
    assets=[]
    for path in owned():
        if path==ROOT/'asset-manifest.json':continue
        b=path.read_bytes();assert len(b)<40000000;assets.append(dict(path=str(path.relative_to(STATE)),sha256=sha(b),bytes=len(b)))
    # LAST OWNED WRITE. Final audit is read-only.
    dump(ROOT/'asset-manifest.json',dict(schema='ri-turnout-owned-assets-repair-v2',excludes_only_itself=True,owned_assets=assets,external_original_references=json.loads(old['data/turnout/asset-manifest.json'])['external_original_references'],source_core_agreement='passed within captured finished-peer source-core scope',coordinator_acceptance=False))
    print(json.dumps(dict(owned_targets=len(assets),witness_bodies=len(bodies),changed_bodies=len(changed),changed_archive_bytes=len(packed),manifest_sha256=sha((ROOT/'asset-manifest.json').read_bytes()),seal_sha256=sha((ROOT/'final-seal.json').read_bytes()),witness_sha256=sha((ROOT/'qa/repaired-body-witness.json').read_bytes()),comparison_sha256=sha((ROOT/'reciprocal/source-core-comparison.json').read_bytes()))))
if __name__=='__main__':run()
