"""Freeze bounded original-native2018 stages without modifying earlier witnesses."""
import argparse,gzip,json,re
from sources import OUT,BASE,sha,save

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',required=True);a=ap.parse_args();folder=OUT/'source'/('native-2018-'+a.version);sp=folder/'snapshot.json'
    files=['native-2018-original-readings.json','native-2018-original-candidate-votes.csv','native-2018-validation.json'];match=re.fullmatch(r'([0-9]+)views-v[0-9]+',a.version);assert match,'Explicit numeric source-view version required';expected=int(match.group(1));counts=json.loads((OUT/files[0]).read_text())['counts'];validation=json.loads((OUT/files[2]).read_text());assert counts['source_views']==expected and validation['counts']==counts,'Builder/validator scope must match requested witness name before freezing'
    if sp.exists():
        existing=json.loads(sp.read_text());assert existing['counts']['source_views']==expected,'Rejected stale-scope witness cannot be accepted or overwritten; use a new version'
        for pin in existing['pins']:
            stored=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(stored);assert len(stored)==pin['stored_bytes'] and sha(stored)==pin['stored_sha256'] and len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256']
        print('Existing2018 witness verified',a.version);return
    folder.mkdir(parents=True,exist_ok=True);pins=[]
    for f in files:
        p=OUT/f;raw=p.read_bytes();stored=gzip.compress(raw,mtime=0);q=folder/(f+'.gz');assert len(stored)<40000000;q.write_bytes(stored);pins.append(dict(original_path=str(p.relative_to(BASE)),original_bytes=len(raw),original_sha256=sha(raw),stored_path=str(q.relative_to(BASE)),stored_bytes=len(stored),stored_sha256=sha(stored)))
    counts=json.loads((OUT/files[0]).read_text())['counts'];save(sp,dict(version=a.version,counts=counts,pins=pins,qualification='Distinct actual2018Nov6 four-candidate special andNov27 two-candidate runoff source-native scopes, never merged electorates or current geographic IDs; original source hashes/physical positions retained.'))
    print('Frozen2018 native',a.version,counts)
if __name__=='__main__':main()
