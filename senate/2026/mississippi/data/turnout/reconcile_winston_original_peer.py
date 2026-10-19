"""Post-transcription reciprocal Winston original/peer/county control audit."""
import csv,json
from acquire_sources import BASE,OUT,sha,savejson
from read_physical_native import PRES24

NAMES=PRES24+['Ty Pinkins','Roger F. Wicker']

def main():
    ownfile=OUT/'winston-allfield-original-readings.json';own=json.loads(ownfile.read_text())
    peerfile=BASE/'data/baselines/winston-native-allfield-readings.json';peer=json.loads(peerfile.read_text())
    assert own['source_raw_sha256']==peer['raw_sha256']
    position_checks=[]
    for op,pp in zip(own['pages'],peer['pages']):
        assert op['page']==pp['page'] and op['labels_literal']==pp['labels_literal']
        pf={x['candidate']:x['values'] for x in pp['fields']}
        for name in NAMES:
            own_values=op['candidate_values'][name]+([None]*9 if op['page']==3 else [])
            assert own_values==pf[name]
            for col,v in enumerate(own_values,1):
                position_checks.append(dict(page=op['page'],source_column=col,candidate=name,role='unused_template_column' if op['page']==3 and col>2 else 'source_TOTAL' if op['page']==3 and col==2 else 'native_reporting_constituent',direct_original_visual_value=v,peer_original_visual_value=pf[name][col-1]))
    assert len(position_checks)==242 and sum(x['direct_original_visual_value'] is None for x in position_checks)==99
    with (OUT/'candidate-votes.csv').open(newline='') as f:county=list(csv.DictReader(f))
    control=[]
    for name in NAMES:
        office='United States-President' if name in PRES24 else 'United States-Senate'
        matches=[x for x in county if x['county']=='Winston' and x['election_date']=='2024-11-05' and x['office_literal']==office and name in x['candidate_literal']]
        assert len(matches)==1,(name,matches)
        v=int(matches[0]['votes']);c=own['candidate_checks'][name]
        assert c['native_sum']==c['printed_TOTAL']==v
        control.append(dict(candidate=name,source_native_sum=c['native_sum'],source_printed_TOTAL=c['printed_TOTAL'],SOS_county_CSV=v))
    savejson(OUT/'winston-original-peer-reconciliation.json',dict(scope='Independent complete original visual review of Winston PDF2/3, compared after extraction to separate peer original visual ledger and SOS county CSV. Does not imply full-state native acceptance.',source_raw_sha256=own['source_raw_sha256'],own_original_ledger_sha256=sha(ownfile.read_bytes()),independent_peer_original_ledger_sha256=sha(peerfile.read_bytes()),position_count=len(position_checks),numeric_positions=143,unused_null_positions=99,all_position_values_and_labels_match=True,county_candidate_controls=control,position_checks=position_checks))
    print('Winston 242/242 original candidate positions and all11 county controls agree peer')

if __name__=='__main__':main()
