"""Verify preserved Perry pre-peer folded-header bytes and literal correction."""
import csv
import gzip
import json
from acquire_sources import OUT, sha, savejson

ARCHIVE=OUT/'source/2018-perry-initial-folded-header-archive/archive-manifest.json'


def main():
    manifest=json.loads(ARCHIVE.read_text())
    originals={}
    for pin in manifest['pins']:
        stored=(OUT/pin['archive_path']).read_bytes();raw=gzip.decompress(stored)
        assert len(stored)==pin['stored_bytes'] and sha(stored)==pin['stored_sha256']
        assert len(raw)==pin['raw_bytes'] and sha(raw)==pin['raw_sha256']
        originals[pin['initial_path']]=raw
    prior=json.loads(originals['2018-perry-two-stage-native-original-readings.json'])
    current_raw=(OUT/'2018-perry-two-stage-native-original-readings.json').read_bytes()
    current=json.loads(current_raw)
    assert len(prior['sources'])==len(current['sources'])==2
    changes=[]
    for old,new in zip(prior['sources'],current['sources']):
        assert old.keys()==new.keys() and old['source_id']==new['source_id']
        assert {k:v for k,v in old.items() if k!='rows'}=={k:v for k,v in new.items() if k!='rows'}
        assert len(old['rows'])==len(new['rows'])
        for before,after in zip(old['rows'],new['rows']):
            assert {k:v for k,v in before.items() if k!='literal_source_header'}=={
                k:v for k,v in after.items() if k!='literal_source_header'}
            if before['literal_source_header']!=after['literal_source_header']:
                assert before['literal_source_header']==' '.join(after['literal_source_header'].split())
                assert '\n' in after['literal_source_header']
                changes.append(dict(source_id=old['source_id'],
                                    page=before['source_pdf_page'],
                                    physical_column=before['physical_source_column'],
                                    candidate=before['candidate'],
                                    initial_folded=before['literal_source_header'],
                                    direct_original_wrap=after['literal_source_header']))
    assert len(changes)==36 and len({(x['source_id'],x['page'],x['physical_column']) for x in changes})==12
    with (OUT/'2018-perry-two-stage-native-original-cells.csv').open(newline='') as f:
        now_csv=list(csv.DictReader(f))
    old_csv=list(csv.DictReader(originals['2018-perry-two-stage-native-original-cells.csv'].decode().splitlines(keepends=True)))
    assert len(old_csv)==len(now_csv)==132
    for old,new in zip(old_csv,now_csv):
        assert {k:v for k,v in old.items() if k!='literal_source_header'}=={
            k:v for k,v in new.items() if k!='literal_source_header'}
        assert old['literal_source_header']==' '.join(new['literal_source_header'].split())
    result=dict(scope='Initial Perry original vote cells preceded independent peer read. Only six source-visible line-wrap headers in each distinct stage were repaired. Exact initial JSON/CSV stored gzip bytes remain unchanged; no votes/roles/source positions altered.',
                archive_manifest_path=str(ARCHIVE.relative_to(OUT)),
                archive_manifest_sha256=sha(ARCHIVE.read_bytes()),
                initial_byte_pins=manifest['pins'],
                current_reading_sha256=sha(current_raw),
                source_views=2,candidate_positions=132,
                changed_candidate_label_positions=len(changes),
                changed_physical_header_positions=12,
                changes=changes)
    savejson(OUT/'2018-perry-header-wrap-correction-history.json',result)
    print('Perry original header wrap history:',len(changes),'label-only fields')


if __name__=='__main__':main()
