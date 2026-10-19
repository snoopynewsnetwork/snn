"""Freeze exact historical native publication ledgers without replacing witnesses."""
import argparse,gzip,json
from sources import OUT,BASE,sha,save
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',required=True);a=ap.parse_args();assert a.version.replace('-','').isalnum();folder=OUT/'source'/('native-2020-'+a.version);sp=folder/'snapshot.json'
    if sp.exists():
        x=json.loads(sp.read_text())
        for p in x['pins']:
            raw=gzip.decompress((BASE/p['stored_path']).read_bytes());assert len(raw)==p['original_bytes'] and sha(raw)==p['original_sha256'] and sha((BASE/p['stored_path']).read_bytes())==p['stored_sha256']
        print('Verified immutable2020native',a.version);return
    coverage=OUT/'native-2020-coverage.json';c=json.loads(coverage.read_text());assert a.version.startswith(str(c['counts']['reviewed_source_publications'])+'views');folder.mkdir(exist_ok=True);pins=[]
    for path in [BASE/p['path'] for p in c['inputs']]+[coverage,OUT/'native-2020-additional-candidate-votes.csv']:
        raw=path.read_bytes();stored=gzip.compress(raw,mtime=0);q=folder/(path.name+'.gz');assert len(stored)<40000000;q.write_bytes(stored);pins.append(dict(original_path=str(path.relative_to(BASE)),original_bytes=len(raw),original_sha256=sha(raw),stored_path=str(q.relative_to(BASE)),stored_bytes=len(stored),stored_sha256=sha(stored),reconstruction='gzip.decompress equals exact complete original derivative bytes; source-original PDF hashes retained in each reading'))
    save(sp,dict(version=a.version,counts=c['counts'],complete_all104_native_Senate_three_candidates=c.get('complete_all104_native_Senate_three_candidates',False),complete_selected82_native_Senate_three_candidates=c.get('complete_selected82_native_Senate_three_candidates',False),pins=pins,qualification='Bounded original-native2020threeSenatecandidate publication scopes, no common-vintage or cross-year/native/current identity inference. Unreviewed counts unknown; vendor/method/fullhistorical gatesOPEN.',complete2020_native=False,current2026_geography_approved=False));print('Frozen2020native',a.version,c['counts'])
if __name__=='__main__':main()
