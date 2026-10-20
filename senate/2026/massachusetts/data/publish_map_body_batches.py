"""Coordinator-only bounded transfer of already-reviewed, exactly pinned blobs.

This is Git publication, not acquisition or a worker task. Stops on any failure.
Explicit batch indices are zero-based; final metadata/state publication is separate.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys

S = Path(__file__).resolve().parents[1]
ROOT = S.parents[2]
plan_path = S / 'data/coordinator-map-publication-plan.json'
plan = json.loads(plan_path.read_bytes())
journal = S / 'data/coordinator-map-transfer-journal.json'


def run(args, capture=False):
    r = subprocess.run(args, cwd=ROOT, check=True,
                       capture_output=capture, text=capture)
    return r.stdout.strip() if capture else None


for number in map(int, sys.argv[1:]):
    assert 4 <= number <= 7, 'This bounded helper transfers only body batches5–8.'
    assert not run(['git', 'diff', '--cached', '--name-only'], True)
    batch = plan['batches'][number]
    assert batch['bytes'] <= 350000000
    prefix = str(S.relative_to(ROOT))
    paths = Path('/tmp/snn-ma-exact-map-transfer-%02d.paths' % number)
    paths.write_bytes(b'\0'.join((prefix + '/' + r['path']).encode()
                               for r in batch['entries']) + b'\0')
    run(['git', 'add', '--pathspec-from-file=' + str(paths), '--pathspec-file-nul'])
    run([sys.executable, '-B', '-S', str(S / 'data/verify_staged_map_batch.py'), str(number)])
    run(['git', '-c', 'core.whitespace=blank-at-eol,space-before-tab,cr-at-eol,-blank-at-eof',
         'diff', '--cached', '--check', '--', '*.md', '*.py', '*.json', '*.html', '*.svg'])
    run(['git', 'commit', '-qm', 'Retain reviewed Massachusetts map originals and page renders, batch %d of 9' % (number+1)])
    commit = run(['git', 'rev-parse', 'HEAD'], True)
    run(['git', 'push', 'origin', 'main'])
    remote = run(['git', 'ls-remote', 'origin', 'refs/heads/main'], True).split()[0]
    assert commit == remote
    rows = json.loads(journal.read_bytes()) if journal.exists() else []
    rows.append(dict(batch=number+1, commit=commit, push_exit=0,
                     remote_head_exact_verified=True, listed_bytes=batch['bytes'],
                     listed_files=len(batch['entries']), verified_at_utc=datetime.now(timezone.utc).isoformat(),
                     plan_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest()))
    journal.write_text(json.dumps(rows, indent=2)+'\n')
    print(json.dumps(rows[-1]), flush=True)
