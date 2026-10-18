#!/usr/bin/env python3
"""Freeze exact read-only input references; no originals copied and no reverse acceptance digest."""
import hashlib,json,pathlib
from acquire import ROOT
BASE=ROOT.parent
EXPECTED={
'data/turnout/priority-set.json':'dcdc1457a5b08851ef76b5372435d56788f647708da5ff9a6ef35435f92fa6a7',
'data/county-turnout.csv':'44ff0242c75a5c310a15ff705138cd93a86365bcc622301fc49c05c9133a8993',
'data/turnout/asset-manifest.json':'ffa25d2d8e1f9d7f8463cf60e007c580c51ac052b4653171d764be11aa679290',
'data/baselines/asset-manifest.json':'bcc5001940d883216e474af42044f1503dccf658cdd2ecdde1ef84bd725ef1e6',
'data/county-baselines.csv':'5f6c140c8f418b598eacd49576c2e6fa77f92dda186cc46bc941710b802f24ab',
'county-partisanship.md':'cfe5fb7ed21ff7238d8ac424e02106afc97506be41d5e8f4115412fd89ac1854'}
paths=set(EXPECTED)|{'data/coordinator-first-wave-checks.json','data/coordinator-target-review.json','data/coordinator-native-contract-checks.json','data/coordinator-county-reconciliation.json','data/coordinator-priority-keys.txt','data/results-sources/native-source-scopes.json','data/results-sources/county-inventory.json','data/results-sources/vendor-extracts.json','data/turnout/source/shared-references.json','data/baselines/source/references.json'}
for name,field in [('data/turnout/asset-manifest.json','assets'),('data/baselines/asset-manifest.json','owned_assets')]:
 j=json.loads((BASE/name).read_text())
 for x in j[field]:
  p=BASE/x['path'];b=p.read_bytes();assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],x['path'];paths.add(x['path'])
refs=[]
for p in sorted(paths):
 b=(BASE/p).read_bytes();h=hashlib.sha256(b).hexdigest()
 if p in EXPECTED:assert h==EXPECTED[p],(p,h)
 refs.append({'path':'../'+p,'bytes':len(b),'sha256':h,'use':'read-only exact shared input; not copied or edited'})
# Traverse existing first-wave reference ledgers using their documented base, preserving original metadata.
shared=[]
for name,root in [('data/turnout/source/shared-references.json',BASE/'data/turnout'),('data/baselines/source/references.json',BASE/'data/baselines')]:
 for r in json.loads((BASE/name).read_text()):
  # The ledger paths and base semantics stay in the unchanged source; pin entire ledger+owned parser.
  shared.append({'ledger':'../'+name,'source_object':r})
out={'schema':'ks-maps-readonly-pins-v1','authoritative_acceptance_path':'../data/coordinator-priority-acceptance.json','acceptance_policy':'Read accepted flag and contract hash at validation; do not hash acceptance back into a worker contract','immutable_launch_pins':EXPECTED,'files':refs,'full_shared_source_metadata':shared,'no_current_geography_approval':True}
(ROOT/'readonly-pins.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print('Pinned',len(refs),'read-only files;',len(shared),'complete shared source objects; all immutable launch pins match')
