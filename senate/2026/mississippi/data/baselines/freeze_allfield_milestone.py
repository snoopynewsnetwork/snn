"""Immutable bounded original all11 snapshot; never mutates an existing version."""
import argparse,gzip,json
from sources import OUT,BASE,save,sha
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',required=True);a=ap.parse_args();assert a.version.replace('-','').isalnum();folder=OUT/'source'/f'native-allfield-{a.version}';snapshot=folder/'snapshot.json'
    if snapshot.exists():
        x=json.loads(snapshot.read_text())
        for p in x['pins']:
            stored=(BASE/p['frozen_path']).read_bytes();raw=gzip.decompress(stored);assert len(stored)==p['stored_bytes'] and sha(stored)==p['stored_sha256'] and len(raw)==p['original_bytes'] and sha(raw)==p['original_sha256']
        print('Verified immutable original all11 snapshot',a.version);return
    coveragepath=OUT/'native-allfield-coverage.json';coverage=json.loads(coveragepath.read_text());assert a.version==str(coverage['counts']['source_views'])+'views';folder.mkdir();paths=[BASE/p['path'] for p in coverage['inputs']]+[coveragepath,OUT/'native-allfield-additional-candidate-votes.csv',OUT/'winston-native-allfield-candidate-votes.csv'];pins=[]
    for p in paths:
        raw=p.read_bytes();stored=gzip.compress(raw,mtime=0);dest=folder/(p.name+'.gz');assert len(stored)<40000000 and not dest.exists();dest.write_bytes(stored);pins.append(dict(original_path=str(p.relative_to(BASE)),original_bytes=len(raw),original_sha256=sha(raw),frozen_path=str(dest.relative_to(BASE)),stored_bytes=len(stored),stored_sha256=sha(stored),reconstruction='gzip.decompress stored bytes equals exact complete original file bytes'))
    save(snapshot,dict(version=a.version,qualification='Bounded independently original-read11candidate source-view milestone. These owned ledgers/flatfields/coverage bytes are immutable and may differ from later mutable working aggregates. Source originals reused by exact raw hashes in the ledgers. No whole-state allfield/history/method/current-geometry or external priority acceptance.',counts=coverage['counts'],pins=pins,complete_statewide_presidential=False,historical_native_complete=False,current2026_geography_approved=False));print('Frozen',a.version,coverage['counts'],len(pins),'complete byte pins')
if __name__=='__main__':main()
