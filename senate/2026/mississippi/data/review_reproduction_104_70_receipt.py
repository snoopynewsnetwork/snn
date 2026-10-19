"""Verify the retained worker run receipt without executing a mutable worker build."""
from pathlib import Path
import gzip, hashlib, json

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
QA = DATA / 'coordinator-qa/reproduction-104-70'

def sha(b): return hashlib.sha256(b).hexdigest()
def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(ROOT)), bytes=len(b), sha256=sha(b))
def checked(p):
    b = (ROOT / p['path']).read_bytes()
    assert len(b) == p['bytes'] and sha(b) == p['sha256']
    return b
def freeze(path, b):
    QA.mkdir(parents=True, exist_ok=True)
    p = QA / (path.name + '.gz')
    if p.exists(): assert gzip.decompress(p.read_bytes()) == b
    else: p.write_bytes(gzip.compress(b, mtime=0))
    return dict(original=dict(path=str(path.relative_to(ROOT)), bytes=len(b), sha256=sha(b)), lossless_copy=pin(p))

def main():
    p = DATA / 'baselines/source/reproduction-1042020-70stage2018.json'
    b = p.read_bytes()
    assert sha(b) == '26341d217b6e080c6ccd096b3ce39f4f6c93e01a3dc2037177c5dfc2372dc74f'
    r = json.loads(b)
    assert r['exit_code'] == 0
    log = checked(r['log'])
    final = json.loads(log.decode()[log.decode().rfind('\n{\n  "status":')+1:])
    assert final['status'] == 'pass_county_and_calculator_checks_native_review_in_progress'
    assert len(final['checks']) == r['main_checks'] == 26
    script = checked(r['stored_execution_reproducer'])
    assert len(script) == r['reproducer']['bytes'] and sha(script) == r['reproducer']['sha256']
    current_path = ROOT / r['reproducer']['path']
    saved_current = QA / (current_path.name + '.gz')
    current = gzip.decompress(saved_current.read_bytes()) if saved_current.exists() else current_path.read_bytes()
    added = b"'reconcile_2018_native_peer_v2.py',"
    later_header = b" run('record_2018_header_evidence.py')\n"
    assert current.count(added) == 1 and current.count(later_header) == 1
    assert current.replace(added, b'').replace(later_header, b'') == script
    initial = checked(r['initial_receipt'])
    old = json.loads(initial)
    assert {k: v for k, v in r.items() if k not in ['stored_execution_reproducer', 'execution_reproducer_recovery', 'initial_receipt']} == old
    inputs = r['original_native_input_witnesses'] + r['bounded_peer_witnesses'] + list(r['native2020_arithmetic'].values())
    for item in inputs: checked(item)
    out = dict(status='pass_bounded_worker_reproduction_receipt_and_exact_execution_script_accounting', receipt=freeze(p,b), worker_log=freeze(ROOT/r['log']['path'],log), exact_execution_reproducer=freeze(ROOT/r['stored_execution_reproducer']['path'],script), later_observed_reproducer=freeze(current_path,current), initial_receipt=freeze(ROOT/r['initial_receipt']['path'],initial), checked_input_pins=inputs, recorded_final_bounded_checks=len(final['checks']), recorded_final_asset_count=final['assets'], reported_worker_exit_code=0, later_observed_reproducer_difference='One later reconcile_2018_native_peer_v2.py list member and one record_2018_header_evidence.py call. Removing these two exact additions reproduces pinned execution bytes. This observed later script is frozen separately; mutable working-script identity is not asserted.', qualification='The coordinator verifies the complete retained log, receipt, source witnesses, arithmetic input pins and exact archived execution script. This does not independently execute the mutating worker build, establish completeness beyond104 original2020 and70 distinct2018 native stages, or approve current geography/methods/native887 dispatch. Later78-stage and12-stage reciprocal witnesses remain distinct from this earlier run.', coordinator_executed_worker_reproduction=False, formal_native887_dispatch_accepted=False)
    target = DATA/'coordinator-reproduction-1042020-70stage2018-review.json'
    output=(json.dumps(out,indent=2)+'\n').encode()
    if target.exists(): assert target.read_bytes()==output
    else: target.write_bytes(output)
    print(json.dumps(pin(target)))

if __name__=='__main__': main()
