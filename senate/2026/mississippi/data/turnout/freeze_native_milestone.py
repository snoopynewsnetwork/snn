"""Freeze exact immutable reviewed-scope bytes; no acceptance or new extraction."""
import json,shutil,hashlib,collections
from acquire_sources import OUT,BASE

def main():
 files=['native-reviewed-2024.json','native-reviewed-controls.json','native-candidate-votes-reviewed.csv','native-constituents-reviewed.json.gz'];d=json.loads((OUT/files[0]).read_text());n=len(d['sources']);dest=OUT/f'qa/milestones/native-2024-{n}views';dest.mkdir(exist_ok=False);pins=[]
 for name in files:
  data=(OUT/name).read_bytes();(dest/name).write_bytes(data);pins.append(dict(path=str((dest/name).relative_to(BASE)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 cols=[c for s in d['sources'].values() for p in s['pages'] for c in p['columns']];counts=dict(collections.Counter(c['role'] for c in cols))
 snapshot=dict(scope='All independently direct-original reviewed literal headers and both named Senate fields in this frozen ledger only. Whole-state native, presidential and historical gates remain open.',source_views=n,counts=counts,pins=pins)
 (dest/'snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n');print(json.dumps(snapshot))
if __name__=='__main__':main()
