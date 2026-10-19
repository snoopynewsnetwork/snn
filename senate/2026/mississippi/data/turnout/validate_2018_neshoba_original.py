"""Offline source and correction-history validation for Neshoba's two stages."""
import csv
import gzip
import json
from collections import Counter
from acquire_sources import BASE,OUT,receipts,savejson,sha,source


def main():
    path=OUT/'2018-neshoba-two-stage-native-original-readings.json'
    reading=json.loads(path.read_text())
    peer=json.loads((OUT/'2018-neshoba-native-peer-reconciliation.json').read_text())
    history=json.loads((OUT/'source/2018-neshoba-original-header-correction-v1/correction-history.json').read_text())
    old={}
    for label,pin in history['pins'].items():
        if 'stored_path' in pin:
            stored=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(stored)
            assert len(stored)==pin['stored_bytes'] and sha(stored)==pin['stored_sha256']
            assert len(raw)==pin['raw_bytes'] and sha(raw)==pin['raw_sha256']
            old[label]=raw
        else:
            blob=(BASE/pin['path']).read_bytes()
            assert len(blob)==pin['raw_bytes'] and sha(blob)==pin['raw_sha256']
    first=json.loads(old['initial_reading'])
    assert first['total_candidate_positions']==reading['total_candidate_positions']==198
    assert reading['native_constituents_per_stage']==first['native_constituents_per_stage']==27
    initial=[r for s in first['sources'] for r in s['rows']]
    current=[r for s in reading['sources'] for r in s['rows']]
    assert len(initial)==len(current)==198
    changed=[]
    for a,b in zip(initial,current):
        assert {k:v for k,v in a.items() if k!='literal_source_header'}=={k:v for k,v in b.items() if k!='literal_source_header'}
        if a['literal_source_header']!=b['literal_source_header']:
            changed.append((a['source_id'],a['source_pdf_page'],a['physical_source_column'],a['literal_source_header'],b['literal_source_header']))
    assert len(changed)==36
    assert Counter((s,p,c) for s,p,c,_,_ in changed)==Counter({(s,p,c):n for s,n in [('sos-2018-county-neshoba',4),('sos-2018-runoff-county-neshoba',2)] for p,c in [(2,1),(3,9),(3,10),(4,1),(4,2),(4,4)]})
    assert all(x[3:] == ('Arrington','Arlington') for x in changed if x[1:3]==(2,1))
    for s in reading['sources']:
        sid=s['source_id']
        assert sha(source(sid))==s['source_raw_sha256']==next(r['raw_sha256'] for r in receipts if r['id']==sid)
        assert s['native_constituents']==27 and s['physical_TOTAL_page']==4 and s['physical_TOTAL_column']==6
        assert len(s['pages'])==3 and all(x['passes'] for x in s['candidate_checks'].values())
        for p in s['pages']:
            blob=(BASE/p['original_raster']).read_bytes()
            assert sha(blob)==p['raster_sha256']
        assert set(r['role'] for r in s['rows'])=={'source_native_reporting_constituent','source_TOTAL','unused_template_column'}
        assert all(r['literal_source_header']=='Arlington' for r in s['rows'] if r['source_pdf_page']==2 and r['physical_source_column']==1)
    assert peer['source_position_count']==198 and not peer['disagreements'] and peer['own_sha256']==sha(path.read_bytes())
    flat=list(csv.DictReader((OUT/'2018-neshoba-two-stage-native-original-cells.csv').open()))
    assert len(flat)==198
    assert Counter(r['role'] for r in current)==Counter({'source_native_reporting_constituent':162,'source_TOTAL':6,'unused_template_column':30})
    assert sum(r['votes'] is not None for r in current)==168
    savejson(OUT/'2018-neshoba-original-validation.json',{
        'status':'pass_bounded_complete_original_two_stages',
        'source_ids':[s['source_id'] for s in reading['sources']],
        'source_position_count':198,'native_constituents_per_stage':27,
        'numeric_positions':168,'unprinted_null_positions':30,
        'initial_header_difference_count':36,
        'glyph_correction':'Arrington to Arlington on both separate original PDFpage2 physical column1 headers',
        'other_header_differences':'five per stage are literal line-break representation only',
        'initial_reading_sha256':history['pins']['initial_reading']['raw_sha256'],
        'current_reading_sha256':sha(path.read_bytes()),
        'reciprocal_peer_source_positions':198,'reciprocal_differences':0,
        'limits':'No current precinct identity or cross-stage geography join, no party union, no numeric-crop polygon accepted.'})
    print('Neshoba original two-stage source/old-history/peer validation: 198 positions PASS')


if __name__=='__main__':main()
