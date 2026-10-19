"""Seal exact owned membership; no producer/acceptance mutation or hash cycle."""
import json,sys
from acquire import ROOT,sha
if '--prepare'in sys.argv:
 p=ROOT/'asset-manifest.json'
 assert not p.exists(),'do not overwrite a seal during preparation'
 p.write_text('{"status":"unsealed preparation; local link target only"}\n')
else:
 files=[ROOT.parent/'precinct-maps.md']+sorted(p for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'asset-manifest.json')
 entries=[]
 for p in files:
  b=p.read_bytes();assert len(b)<40000000;assert '__pycache__'not in p.parts
  entries.append(dict(path=str(p.relative_to(ROOT.parent)),bytes=len(b),sha256=sha(b)))
 con=json.loads((ROOT/'historical-conservation.json').read_text());deps={r['path']:dict(path=r['path'],bytes=r['bytes'],sha256=r['sha256']) for r in con['read_only_complete_dependencies']+con['individual_original_references']}
 for r in deps.values():
  b=(ROOT.parent/r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256']
 out=dict(schema='CO-map-research-exact-seal-v1',status='worker research seal only; external coordinator review/publication separate',acceptance_path='../data/coordinator-priority-acceptance.json',self_excluded_only='maps/asset-manifest.json',owned_files=entries,read_only_dependencies=sorted(deps.values(),key=lambda r:r['path']),strict_stored_size_limit_exclusive=40000000,source_originals_changed=False,current_legal_crosswalk_approved=False)
 (ROOT/'asset-manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(len(entries),'owned files;',len(deps),'individual immutable read-only dependencies')
