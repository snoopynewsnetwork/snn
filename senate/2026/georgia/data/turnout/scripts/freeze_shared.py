#!/usr/bin/env python3
"""Pin/verify retained primary acquisition chain; shared originals stay read-only."""
import gzip,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];GA=R.parent.parent;out=R/'source/source-chain-references.json'
if out.exists():rs=json.loads(out.read_text())
else:
 rs=[]
 for m in json.loads((R.parent/'news/manifest.json').read_text()):
  if m['id'].startswith(('sos-','fec-2024','nara-2024')):rs.append({**m,'path':'data/news/'+m['asset'],'stored_bytes':(GA/'data/news'/m['asset']).stat().st_size,'entity_bytes':m['bytes'],'role':'primary discovery/control/original reference; read-only reuse'})
 out.write_text(json.dumps(rs,indent=2)+'\n')
for m in rs:
 b=(GA/m['path']).read_bytes();raw=gzip.decompress(b)
 assert hashlib.sha256(b).hexdigest()==m['stored_sha256']and hashlib.sha256(raw).hexdigest()==m['raw_sha256']and len(raw)==m['bytes']
print('Verified retained shared originals:',len(rs))
