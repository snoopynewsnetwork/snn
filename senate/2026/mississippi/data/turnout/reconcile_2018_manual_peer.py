"""Read-only source-position reconciliation after direct original transcription."""
import argparse
import csv
import gzip
import io
import json
from acquire_sources import BASE,OUT,sha,savejson

ROLES={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL',
       'unused_template_column':'unused'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--county',required=True)
    parser.add_argument('--snapshot',required=True)
    parser.add_argument('--snapshot-sha256',required=True)
    a=parser.parse_args()
    county=a.county.lower()
    ourpath=OUT/f'2018-{county}-two-stage-native-original-readings.json'
    our=json.loads(ourpath.read_text());assert len(our['sources'])==2
    snap_path=BASE/a.snapshot;snap_bytes=snap_path.read_bytes();assert sha(snap_bytes)==a.snapshot_sha256
    snap=json.loads(snap_bytes)
    pin=next(x for x in snap['pins'] if x['original_path']=='data/baselines/native-2018-original-candidate-votes.csv')
    stored=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(stored)
    assert len(stored)==pin['stored_bytes'] and sha(stored)==pin['stored_sha256']
    assert len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256']
    ids={s['source_id'] for s in our['sources']}
    peer={(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']):r
          for r in csv.DictReader(io.StringIO(raw.decode())) if r['source_id'] in ids}
    ours=[r for s in our['sources'] for r in s['rows']]
    assert len(ours)==len(peer)==our['total_candidate_positions']
    differences=[]
    for r in ours:
        key=(r['source_id'],r['source_pdf_page'],r['physical_source_column'],r['candidate'])
        other=peer.get(key)
        if not other:
            differences.append(dict(position=key,reason='peer_missing'))
            continue
        checks=dict(votes=('' if r['votes'] is None else str(r['votes']))==other['votes'],
                    role=ROLES[r['role']]==other['role'],
                    literal_header=r['literal_source_header']==other['literal_native_label'],
                    original_hash=r['source_raw_sha256']==other['source_raw_sha256'],
                    county_fips=r['county_fips']==other['county_fips'])
        if not all(checks.values()):differences.append(dict(position=key,checks=checks,
                                             own_value=r['votes'],peer_value=other['votes'],
                                             own_literal=r['literal_source_header'],peer_literal=other['literal_native_label']))
    output=dict(scope='Read-only reciprocal positions after own complete-original stage transcription. Equal numeric/null votes, roles, literal headers, original hashes and FIPS when differences empty. No shared source-key wrapper, raster, crop, party, cross-stage or current-geography equivalence claimed.',
                county=our['sources'][0]['rows'][0]['county'],
                own_path=str(ourpath.relative_to(BASE)),own_sha256=sha(ourpath.read_bytes()),
                peer_snapshot_path=a.snapshot,peer_snapshot_sha256=a.snapshot_sha256,
                peer_flat_original_sha256=sha(raw),source_ids=sorted(ids),
                source_position_count=len(ours),native_per_stage=our['native_constituents_per_stage'],
                disagreements=differences,
                original_source_hashes={s['source_id']:s['source_raw_sha256'] for s in our['sources']})
    savejson(OUT/f'2018-{county}-native-peer-reconciliation.json',output)
    assert not differences,differences[:10]
    print(county,'2018 reciprocal',len(ours),'positions; zero differences')

if __name__=='__main__':main()
