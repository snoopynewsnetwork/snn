"""Read-only index verification for one explicit reviewed map transfer batch."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

S = Path(__file__).resolve().parents[1]
ROOT = S.parents[2]
plan = json.loads((S / 'data/coordinator-map-publication-plan.json').read_bytes())
batch = plan['batches'][int(sys.argv[1])]
prefix = str(S.relative_to(ROOT))
want = {prefix + '/' + r['path']: r for r in batch['entries']}
actual = {s.decode() for s in subprocess.check_output(
    ['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT).split(b'\0') if s}
assert actual == set(want), (actual - set(want), set(want) - actual)
proc = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE)
for name, r in want.items():
    proc.stdin.write((':' + name + '\n').encode())
    proc.stdin.flush()
    header = proc.stdout.readline().decode().split()
    assert header[1] == 'blob'
    size = int(header[2])
    assert size == r['bytes'] < 40000000
    h = hashlib.sha256()
    left = size
    while left:
        b = proc.stdout.read(min(1048576, left))
        assert b
        h.update(b)
        left -= len(b)
    assert proc.stdout.read(1) == b'\n'
    assert h.hexdigest() == r['sha256'], name
proc.stdin.close()
assert proc.wait() == 0
print(json.dumps(dict(status='pass_exact_reviewed_index_blobs', batch=int(sys.argv[1])+1,
                      files=len(want), bytes=batch['bytes'])))
