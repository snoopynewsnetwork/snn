"""Read-only reciprocal comparison after complete Clay2018 originals were typed."""
import csv
import gzip
import io
import json
from acquire_sources import BASE,OUT,sha,savejson

SNAPSHOT='data/baselines/source/native-2018-28views-v1/snapshot.json'
SNAPSHOT_SHA='cf079fd6e7c7ac29525c82e8b57549b63b3f91c1657829e32a4f726df9c0dfcf'
ROLES={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL',
       'unused_template_column':'unused'}

def main():
    ourpath=OUT/'2018-clay-two-stage-native-original-readings.json'
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
    assert not differences,differences[:10]
    savejson(OUT/'2018-clay-native-peer-reconciliation.json',
             dict(scope='After independent complete original Nov6 and Nov27 Clay reading, compare every printed numeric and unprinted template candidate position to immutable independent28-view source CSV. Same source/page/physical-column/candidate positions; key-string wrapper, raster pixels, candidate crop polygons, unprinted party and parsed-ID representation equivalence are not asserted. Prior county TOTAL locator3 for runoff is unaccepted; actual source page3 physical4.',
                  own_path=str(ourpath.relative_to(BASE)),own_sha256=sha(ourpath.read_bytes()),
                  peer_snapshot_path=SNAPSHOT,peer_snapshot_sha256=SNAPSHOT_SHA,
                  peer_flat_original_sha256=sha(raw),
                  source_ids=sorted(ids),source_position_count=len(ours),
                  native_per_stage=14,disagreements=differences,
                  original_source_hashes={s['source_id']:s['source_raw_sha256'] for s in our['sources']}))
    print('Clay2018 reciprocal native',len(ours),'positions; zero source/role/value/literal differences')

if __name__=='__main__':main()
