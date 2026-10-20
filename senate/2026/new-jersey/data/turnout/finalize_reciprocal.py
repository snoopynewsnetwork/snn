#!/usr/bin/env python3
"""Write acyclic final review seal. Complete manifest independently pins this seal and QA."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;ST=D.parent.parent
paths=['pre-peer-witness.json','reciprocal-review/pre-reciprocal-capture.json','reciprocal-review/peer-capture.json','reciprocal-review/peer-return-capture.json','reciprocal-review/comparison.json','extract/native-rows.json','extract/municipal-footers.json','extract/ballot-rows.json','extract/ballot-footers.json','extract/state-candidate-controls.json','extract/turnout-controls.json','all-source-orders.json','native-coverage.json','discrepancy-ledger.json','reproducibility.json']
pins=[]
for rel in paths:
 p=D/rel;b=p.read_bytes();pins.append({'path':str(p.relative_to(ST)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
p=D.parent/'county-turnout.csv';b=p.read_bytes();pins.append({'path':str(p.relative_to(ST)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
review=json.loads((D/'reciprocal-review/comparison.json').read_text());assert not review['differences']
seal={'phase':'bounded-actual-peer-fixed-core-reciprocal-v1','worker_id':'04473229-3e65-45b1-b628-b2fe909eaeee','peer_id':'61054f9e-a14c-44fc-b6b2-7bbc4c84b449','own_comparison_checks':review['checks'],'peer_reverse_checks':40921,'scope':'completed immutable original-first core only; later/future peer report/scenario/finer/final artifacts outside equality','pins':pins,'validation_path':'data/turnout/validation.json','manifest_policy':'Complete manifest excludes only itself and independently pins validation and this final seal; no reverse manifest/validation digest stored here.','acceptance':{'coordinator':False,'current_or_legal_geography':False,'eligible_writein_universe':False,'november2026_returns':False}}
(D/'final-seal.json').write_text(json.dumps(seal,indent=2)+'\n');print('Final bounded reciprocal seal written without reverse manifest digest.')
