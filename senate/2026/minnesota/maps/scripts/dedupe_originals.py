#!/usr/bin/env python3
"""Content-identical response entities share exact stored parts. Request observations
remain distinct, including time, URL, redirects, status and headers. No originals
are recoded or dropped; only unreferenced duplicate stored bytes are removed.
"""
import sys
sys.dont_write_bytecode=True
import json,collections
from acquire import ROOT,read,sha
files=list((ROOT/'evidence').glob('*.request.json'));groups=collections.defaultdict(list)
for p in files:
 m=json.loads(p.read_text());groups[m['original_entity_sha256']].append((p,m))
for digest,group in groups.items():
 if len(group)<2:continue
 group.sort(key=lambda x:(x[1]['retrieved_utc'],x[1]['key']));cp,canonical=group[0];entity=read(canonical);assert sha(entity)==digest
 for p,m in group[1:]:
  assert read(m)==entity
  m['ordered_parts']=canonical['ordered_parts'];m['identical_entity_reused_from']={'key':canonical['key'],'sha256':digest,'scope':'Identical response entity only; this request/time/status remains a separate observation.'};p.write_text(json.dumps(m,indent=2)+'\n')
refs={part['path'] for p in files for part in json.loads(p.read_text())['ordered_parts']}
for p in (ROOT/'originals').glob('*.gz'):
 if str(p.relative_to(ROOT)) not in refs:p.unlink()
print('Unique original entities',len(groups),'stored parts',len(refs))
