"""Read-only reciprocal comparison after complete Smith 2018 originals were typed."""
import csv
import gzip
import io
import json
from acquire_sources import BASE,OUT,sha,savejson

SNAPSHOT='data/baselines/source/native-2018-40views-v1/snapshot.json'
SNAPSHOT_SHA='59d10972abc73a936ddf6c77d62258b6a9d7d62298cc46bd570ae6c1ad83895f'
ROLES={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL',
       'unused_template_column':'unused'}

def main():
    ourpath=OUT/'2018-smith-two-stage-native-original-readings.json'
    our=json.loads(ourpath.read_text())
    assert len(our['sources'])==2 and our['total_candidate_positions']==132
    path=BASE/SNAPSHOT;source=path.read_bytes()
    assert sha(source)==SNAPSHOT_SHA
    snap=json.loads(source)
    pin=next(x for x in snap['pins'] if x['original_path']=='data/baselines/native-2018-original-candidate-votes.csv')
    stored=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(stored)
    assert len(stored)==pin['stored_bytes'] and sha(stored)==pin['stored_sha256']
    assert len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256']
    ids={s['source_id'] for s in our['sources']}
    theirs={(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']):r
            for r in csv.DictReader(io.StringIO(raw.decode())) if r['source_id'] in ids}
    ours=[r for s in our['sources'] for r in s['rows']]
    assert len(ours)==len(theirs)==132
    differences=[]
    for r in ours:
        key=(r['source_id'],r['source_pdf_page'],r['physical_source_column'],r['candidate'])
        other=theirs.get(key)
        if not other:
            differences.append(dict(source_position=key,reason='peer_missing'))
            continue
        checks=dict(votes=('' if r['votes'] is None else str(r['votes']))==other['votes'],
                    role=ROLES[r['role']]==other['role'],
                    literal_header=r['literal_source_header']==other['literal_native_label'],
                    original_raw_hash=r['source_raw_sha256']==other['source_raw_sha256'],
                    county_fips=r['county_fips']==other['county_fips'])
        if not all(checks.values()):differences.append(dict(source_position=key,checks=checks,
                                             own_value=r['votes'],peer_value=other['votes'],
                                             own_literal=r['literal_source_header'],
                                             peer_literal=other['literal_native_label']))
    savejson(OUT/'2018-smith-native-peer-reconciliation.json',
             dict(scope='After independent complete original Smith Nov6 and Nov27 reading, compare every printed numeric and unprinted template candidate position to immutable independent40-view source CSV. Source/page/physical-column/candidate fields are compared; key-string wrapper, raster pixels, candidate crop polygons, party and parsed-ID representation equivalence are not asserted.',
                  own_path=str(ourpath.relative_to(BASE)),own_sha256=sha(ourpath.read_bytes()),
                  peer_snapshot_path=SNAPSHOT,peer_snapshot_sha256=SNAPSHOT_SHA,
                  peer_flat_original_sha256=sha(raw),source_ids=sorted(ids),
                  source_position_count=len(ours),native_per_stage=18,
                  disagreements=differences,
                  original_source_hashes={s['source_id']:s['source_raw_sha256'] for s in our['sources']}))
    print('Smith2018 reciprocal native',len(ours),'positions;',len(differences),'differences')
    if differences:print(differences[:10])

if __name__=='__main__':main()
