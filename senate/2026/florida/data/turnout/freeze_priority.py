#!/usr/bin/env python3
"""Pin final worker contract bytes; external acceptance remains coordinator-owned."""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;p=D/'priority-set.json';b=p.read_bytes();c=json.loads(b)
assert not c['coordinator_accepted'];assert c['coordinator_acceptance_path']=='data/coordinator-priority-acceptance.json'
assert len(c['all_unit_order'])==67 and len(c['ordered_priority_keys'])==22
assert sum(x['constituent_count'] for x in c['native_constituents'])==5710
assert json.loads((D/'peer-agreement.json').read_text())['status']=='pass'
pin=dict(path='data/turnout/priority-set.json',sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),coordinator_acceptance_path=c['coordinator_acceptance_path'],coordinator_accepted=False,policy='Frozen worker bytes; build must reproduce exactly or refuse drift; no reverse acceptance hash')
repair=D/'priority-freeze-repair.json'
if repair.exists():
    r=json.loads(repair.read_text());assert pin['sha256']==r['expected_repaired_sha256'] and pin['bytes']==r['expected_repaired_bytes'];assert r['historical_counts_order_native_source_objects_unchanged']
f=D/'priority-freeze.json'
if f.exists():assert json.loads(f.read_text())==pin
else:f.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps(pin,indent=2))
