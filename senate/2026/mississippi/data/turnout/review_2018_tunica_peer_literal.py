"""Preserve the literal Tunica Mhoon/Moon difference after original reading."""
import gzip,io,json
from PIL import Image
from acquire_sources import BASE,OUT,receipts,sha,savejson

IDS=('sos-2018-county-tunica','sos-2018-runoff-county-tunica')
SNAP='data/baselines/source/native-2018-78views-v1/snapshot.json'
SNAP_SHA='4df50caded4d9a1cdfd46081422e36002439b10aea28cfab1fb6dcf00f34621c'
ARCH=OUT/'source/2018-tunica-initial-peer-disagreement-v1.json.gz'

def main():
    ownpath=OUT/'2018-tunica-two-stage-native-original-readings.json'
    ownraw=ownpath.read_bytes();own=json.loads(ownraw)
    assert len(own['sources'])==2 and {s['source_id'] for s in own['sources']}==set(IDS)
    source_positions=[r for s in own['sources'] for r in s['rows']]
    assert len(source_positions)==132
    firstpath=OUT/'2018-tunica-native-peer-reconciliation.json'
    if ARCH.exists():
        firststored=ARCH.read_bytes();first=gzip.decompress(firststored)
    else:
        first=firstpath.read_bytes();firststored=gzip.compress(first,mtime=0)
        ARCH.parent.mkdir(parents=True,exist_ok=True);ARCH.write_bytes(firststored)
    initial=json.loads(first)
    assert initial['own_sha256']==sha(ownraw)
    assert initial['peer_snapshot_path']==SNAP and initial['peer_snapshot_sha256']==SNAP_SHA
    assert sha((BASE/SNAP).read_bytes())==SNAP_SHA
    assert initial['source_position_count']==132 and len(initial['disagreements'])==6
    accepted=[]
    for d in initial['disagreements']:
        assert set(d['checks'])=={'votes','role','literal_header','original_hash','county_fips'}
        assert d['checks']==dict(votes=True,role=True,literal_header=False,original_hash=True,county_fips=True)
        sid,page,column,candidate=d['position']
        assert sid in IDS and page==2 and column==2
        assert d['own_literal']=='Mhoon Landing' and d['peer_literal']=='Moon Landing'
        accepted.append(dict(source_id=sid,source_pdf_page=page,physical_source_column=column,
                             candidate=candidate,original_literal=d['own_literal'],
                             peer_derivative_literal=d['peer_literal'],votes=d['own_value']))
    assert len({(x['source_id'],x['candidate']) for x in accepted})==6
    evidence=[]
    for sid in IDS:
        r=next(x for x in receipts if x['id']==sid)
        full=OUT/f'qa/2018-frozen78-original-pixels/{sid}/p0002-original.png'
        crop=OUT/f'qa/2018-tunica-header-original/{sid}-p2-c2-original-pixels.png'
        assert full.exists() and crop.exists()
        im=Image.open(full);im=im.crop((806,270,945,510)).rotate(270,expand=True)
        buf=io.BytesIO();im.save(buf,format='PNG')
        assert sha(buf.getvalue())==sha(crop.read_bytes())
        evidence.append(dict(source_id=sid,raw_pdf_sha256=r['raw_sha256'],source_pdf_page=2,
                             original_full_raster=str(full.relative_to(BASE)),
                             original_full_raster_sha256=sha(full.read_bytes()),
                             original_pixel_crop_box=[806,270,945,510],rotation_clockwise_degrees=90,
                             exact_original_pixel_crop=str(crop.relative_to(BASE)),
                             crop_sha256=sha(crop.read_bytes()),direct_original_visual_read='Mhoon Landing'))
    result=dict(scope='Own direct original Tunica2018 special/runoff full-grid readings. All132 numeric/null votes, roles, raw PDF hashes and county FIPS match the immutable independent frozen78 witness. Six p2c2 peer derivative labels say Moon Landing, while both actual original page crops print Mhoon Landing. Both literal source representations remain distinct; no name normalization, cross-stage/current precinct join, exact numeric crop polygon or coordinator acceptance.',
                county='Tunica',own_path=str(ownpath.relative_to(BASE)),own_sha256=sha(ownraw),
                peer_snapshot_path=SNAP,peer_snapshot_sha256=SNAP_SHA,
                peer_flat_original_sha256=initial['peer_flat_original_sha256'],
                source_ids=list(IDS),source_position_count=132,native_per_stage=12,
                disagreements=[],accepted_literal_differences=accepted,
                original_crop_evidence=evidence,
                initial_disagreement_archive=dict(path=str(ARCH.relative_to(BASE)),
                    raw_sha256=sha(first),stored_sha256=sha(firststored),
                    raw_bytes=len(first),stored_bytes=len(firststored)))
    savejson(firstpath,result)
    print('Tunica2018:132 positions, six explicit Mhoon/Moon peer-label differences only')

if __name__=='__main__':main()
