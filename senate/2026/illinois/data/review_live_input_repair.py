"""Replay the seven actual coordinator failures against a frozen fixed CLI."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
import argparse

D = Path(__file__).resolve().parent
O = D / 'coordinator-live-input-review-v1'
NAMES = ['NaN', 'positiveInfinity', 'negativeInfinity', 'null', 'text',
         'tooLarge', 'duplicate_pool_unit']


def reject_constant(value):
    raise ValueError('Nonfinite JSON output: '+value)


def main(final=False):
    pin_path = O/('final-calculator-input-pin.json' if final else 'repaired-calculator-input-pin.json')
    snapshot = O/('final-calculator.py.gz' if final else 'repaired-calculator.py.gz')
    if final and not snapshot.exists():
        raw=(D/'baselines/calculator.py').read_bytes()
        assert hashlib.sha256(raw).hexdigest()=='a840be4328b72a2fa3ff4d9408f860263578f1b4aa3ce6ad9e7956158e32003b'
        snapshot.write_bytes(gzip.compress(raw,mtime=0))
    stored = snapshot.read_bytes()
    raw = gzip.decompress(stored)
    actual = dict(path=str(snapshot.relative_to(D.parent)),
                  stored_bytes=len(stored), stored_sha256=hashlib.sha256(stored).hexdigest(),
                  raw_bytes=len(raw), raw_sha256=hashlib.sha256(raw).hexdigest())
    if pin_path.exists():
        assert json.loads(pin_path.read_bytes()) == actual
    else:
        pin_path.write_text(json.dumps(actual,indent=2)+'\n')
    results = []
    with tempfile.TemporaryDirectory() as temporary:
        script = Path(temporary)/'calculator.py'
        script.write_bytes(raw)
        for name in NAMES:
            path = O/(name+'.json')
            run = subprocess.run([sys.executable,'-B','-S',str(script),str(path)],
                                 capture_output=True,text=True)
            assert run.returncode==0 and not run.stderr,(name,run.returncode,run.stderr)
            value = json.loads(run.stdout,parse_constant=reject_constant)
            assert value['status'].startswith('invalid') or value['status']=='duplicate_remaining_unit_key'
            results.append(dict(input=path.name,
                                input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                exit_code=run.returncode, strict_JSON=value, stderr=run.stderr))
    output = dict(status='pass_actual_seven_input_repairs',frozen_repaired_CLI=actual,
                  cases=results,scope='Actual seven coordinator failures repeated against the complete frozen repaired CLI. No producer writer or solver import.')
    p = O/('final-repair-review.json' if final else 'repair-review.json')
    b = json.dumps(output,indent=2,allow_nan=False).encode()+b'\n'
    p.write_bytes(b)
    print(json.dumps(dict(path=str(p.relative_to(D.parent)),bytes=len(b),
                          sha256=hashlib.sha256(b).hexdigest(),actual_cases=len(results))))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--final',action='store_true')
    main(parser.parse_args().final)
