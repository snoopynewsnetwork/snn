"""Check two independently typed original SEMS views after transcription.

Peer and county CSV data are read only here, after the direct-original ledgers
have been built.  A successful match does not accept any other source view.
"""
import csv,json
from acquire_sources import BASE,OUT,sha,savejson
from read_physical_native import PRES24

def main():
    ledgers={county:json.loads((OUT/f'{county}-presidential-original-readings.json').read_text()) for county in ['tunica','perry']}
    county_csv=OUT/'candidate-votes.csv'
    with county_csv.open(newline='') as f:official=list(csv.DictReader(f))
    peerfile=BASE/'data/baselines/native-source-exception-readings.json'
    peer=json.loads(peerfile.read_text())
    tunica_peer=next(x for x in peer['sources'] if x['source_id']=='sos-2024-county-tunica')
    out=[]
    for county,d in ledgers.items():
        county_official=[x for x in official if x['county'].casefold()==county and x['election_date']=='2024-11-05' and x['office_literal']=='United States-President']
        assert len(county_official)==9
        checks=[]
        for name in PRES24:
            controls=[x for x in county_official if name in x['candidate_literal']]
            assert len(controls)==1,(county,name)
            original=d['candidate_checks'][name]['printed_TOTAL']
            checks.append(dict(candidate=name,original_native_sum=d['candidate_checks'][name]['native_sum'],original_printed_TOTAL=original,county_csv_control=int(controls[0]['votes']),source_to_CSV_difference=int(controls[0]['votes'])-original,original_native_matches_printed_TOTAL=d['candidate_checks'][name]['native_sum']==original))
        assert all(x['original_native_matches_printed_TOTAL'] for x in checks)
        expected_disagreements=[x for x in checks if x['source_to_CSV_difference']!=0]
        if county=='tunica':assert [(x['candidate'],x['source_to_CSV_difference']) for x in expected_disagreements]==[('Kamala D. Harris',1)]
        else:assert not expected_disagreements
        peer_positions=[]
        if county=='tunica':
            assert tunica_peer['raw_sha256']==d['source_raw_sha256']
            for op,pp in zip(d['pages'],tunica_peer['pages']):
                assert op['page']==pp['page']
                labels_match=op['labels_literal']==pp['labels_literal'][:len(op['labels_literal'])]
                assert labels_match
                other={f['candidate']:f['values'] for f in pp['fields']}
                for name in PRES24:
                    x=op['candidate_values'][name];y=other[name][:len(x)]
                    peer_positions.append(dict(page=op['page'],candidate=name,source_position_count=len(x),candidate_values_match=x==y,peer_unused_column_values=other[name][len(x):]))
                    assert x==y and all(z is None for z in other[name][len(x):])
            assert sum(x['source_position_count'] for x in peer_positions)==117
        out.append(dict(county=county,source_id=d['source_id'],source_raw_sha256=d['source_raw_sha256'],direct_original_ledger_sha256=sha((OUT/f'{county}-presidential-original-readings.json').read_bytes()),native_constituents=d['source_native_count'],candidate_positions=len(d['rows']),candidate_controls=checks,source_to_CSV_disagreements=expected_disagreements,independent_peer_full_original_position_checks=peer_positions,peer_position_count=sum(x['source_position_count'] for x in peer_positions),all_nine_native_sum_match_printed_TOTAL=True))
    savejson(OUT/'direct-presidential-two-source-reconciliation.json',dict(scope='Bounded source-original visual transcriptions only: Tunica and Perry. Peer comparison post-extraction. Tunica SEMS Harris 1836 versus CSV 1837 remains a source-scoped one-vote difference, not allocated. Does not accept statewide presidential native coverage.',county_candidate_csv_sha256=sha(county_csv.read_bytes()),peer_tunica_original_readings_sha256=sha(peerfile.read_bytes()),sources=out))
    print('Two direct original source views',sum(x['native_constituents'] for x in out),'native columns;',sum(x['candidate_positions'] for x in out),'candidate positions; nine source-to-CSV checks each; Tunica Harris source/CSV +1 unallocated; Tunica 117 post-extraction peer positions')

if __name__=='__main__':main()
