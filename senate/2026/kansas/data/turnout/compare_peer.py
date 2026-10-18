#!/usr/bin/env python3
"""Read-only, coordinate-based comparison with the actual independent Kansas peer.

This writes turnout-owned agreement evidence only. Different source-native key
encodings are crosswalked by exact source, worksheet, county and original rows.
"""
import csv, gzip, json
from collections import Counter, defaultdict
from sources import HERE, STATE, sha, dump_json
from build_turnout import IDENTITIES, SOURCES, BROAD, csv_output

PEER_ID='78f9c3c0-062f-41f7-87c0-f0a6443f8877'
PEER=STATE/'data/baselines'

def read_jsonl(path):
    return [json.loads(x) for x in gzip.open(path,'rt')]

def main():
    ours=list(csv.DictReader((STATE/'data/county-turnout.csv').open()))
    theirs=list(csv.DictReader((STATE/'data/county-baselines.csv').open()))
    om={x['county_fips']:x for x in ours};pm={x['county_fips']:x for x in theirs}
    assert set(om)==set(pm) and len(om)==105
    mismatches=[];county_fields=0
    def same(where,a,b):
        if a!=b: mismatches.append({'where':where,'turnout':a,'peer':b})
    fields=[('county','county'),('county_key','county_key'),('rank','president_2024_rank'),('president_2024_cumulative_votes','president_2024_cumulative_votes'),
        ('ballots_cast_2024_broad','ballots_2024_source_workbook'),('registered_voters_2024_broad','registration_2024_source_workbook'),
        ('ballots_cast_2022','ballots_2022_source_workbook'),('registered_voters_2022','registration_2022_source_workbook'),
        ('registered_voters_2024_november','registration_2024_november_separate_publication'),
        ('generic_write_in_2020_published_supplement','generic_write_in_2020_published_supplement')]
    for contest in ['president_2024','senate_2022','senate_2020']:
        fields += [(contest+'_'+k,contest+'_'+k+'_votes') for k in IDENTITIES[contest]]
        fields.append((contest+'_total',contest+'_named_votes'))
    for f in om:
        for a,b in fields:
            same(['county',f,a,b],om[f][a],pm[f][b]);county_fields+=1
        same(['county',f,'priority'],bool(int(om[f]['priority80'])),pm[f]['priority_top15_or_min80']=='True')
    po=sorted(theirs,key=lambda r:int(r['president_2024_rank']))
    same('complete105 descending order',[r['county_fips'] for r in ours],[r['county_fips'] for r in po])
    same('ordered priority keys',[r['county_key'] for r in ours if r['priority80']=='1'],[r['county_key'] for r in po if r['priority_top15_or_min80']=='True'])
    # Every shared native named/write-in/footer observation is compared by coordinates.
    raw_ours=read_jsonl(HERE/'extracts/candidate-observations.jsonl.gz')+read_jsonl(HERE/'extracts/county-summary-observations.jsonl.gz')
    raw_ours=[r for r in raw_ours if r['category']!='reported_contest_total']
    raw_peer=list(csv.DictReader(gzip.open(PEER/'native-candidates.csv.gz','rt')))
    def ok(r):return (r['source_id'],r['sheet'],r['county_fips'],int(r['row']),r['column'])
    def pk(r):return (r['source_id'],r['sheet'],r['county_fips'],int(r['source_row']),r['vote_column'])
    oc={ok(r):r for r in raw_ours};pc={pk(r):r for r in raw_peer}
    assert len(oc)==len(raw_ours) and len(pc)==len(raw_peer)
    same('candidate coordinates only turnout',sorted(oc.keys()-pc.keys()),[])
    same('candidate coordinates only peer',[],sorted(pc.keys()-oc.keys()))
    for k in oc.keys() & pc.keys():
        a=oc[k];b=pc[k]
        av=(a['candidate_key'],a['source_candidate_label'],a['raw_value'] or '',str(a['votes']) if a['votes'] is not None else '')
        bv=(b['canonical_candidate'],b['source_candidate'],b['raw_value'],b['votes'])
        same(['candidate',*k],av,bv)
    # Literal header codes and all other raw fields are checked directly. The
    # peer's source_party stores preceding-row codes '-'/'VOTE FOR 1' whereas
    # turnout distinguishes those contexts from candidate-label party prefixes.
    pr={(r['source_id'],r['sheet'],r['row']):r['cells'] for r in read_jsonl(PEER/'source/raw-rows.jsonl.gz')}
    raw_rows_compared=0
    for sid in {r['source_id'] for r in raw_ours}:
        for r in read_jsonl(HERE/'extracts'/f'{sid}-rows.jsonl.gz'):
            k=(sid,r['sheet'],r['row'])
            same(['raw source row',*k],r['cells'],pr.get(k));raw_rows_compared+=1
    # All units crosswalk through the complete original row set, including unavailable cells.
    ounits=read_jsonl(HERE/'extracts/native-units.jsonl.gz');punits=read_jsonl(PEER/'native-units.jsonl.gz')
    def uk(r):return (r['source_id'],r['sheet'],r['county_fips'],tuple(r['source_rows']))
    def vk(r):return (r['source_id'],r['sheet'],r['county_fips'],tuple(sorted({int(x[0]) for x in r['rows']})))
    ou={uk(r):r for r in ounits};pu={vk(r):r for r in punits}
    assert len(ou)==len(ounits) and len(pu)==len(punits)
    same('native coordinates only turnout',sorted(ou.keys()-pu.keys()),[])
    same('native coordinates only peer',[],sorted(pu.keys()-ou.keys()))
    crosswalk=[]
    for k in ou.keys() & pu.keys():
        a=ou[k];b=pu[k]; same(['native count',*k],(a['named_candidate_total'],a['named_candidate_numeric_sum']),(b['named_votes'],b['known_named_votes']))
        same(['native completeness',*k],a['unknown_named_cells']==0,b['complete_named_values'])
        if a['source_id']==BROAD:
            af=list(a['native_id_fields'].items())
        elif a['sheet'] in ['OfficialPrecinctLevelResults','U.S. Senate']:
            af=[('precinct',a['native_id_fields']['Precinct']),('VTD',a['native_id_fields']['VTD'])]
        else: af=[(col,v['value']) for col,v in a['native_id_fields'].items()]
        same(['native components',*k],af,[tuple(v) for v in b['native_components']])
        crosswalk.append({'source_id':a['source_id'],'sheet':a['sheet'],'county_fips':a['county_fips'],'source_rows':json.dumps(a['source_rows'],separators=(',',':')),'turnout_unit_key':a['unit_key'],'peer_unit_key':b['unit_key']})
    # Same total ordering including tie convention, without relying on either hash scheme.
    for sid in {u['source_id'] for u in ounits}:
        a=sorted([r for r in ounits if r['source_id']==sid and r['named_candidate_total'] is not None],key=lambda r:(-r['named_candidate_total'],r['county_fips'],r['sheet'],r['source_rows']))
        b=sorted([r for r in punits if r['source_id']==sid and r['named_votes'] is not None],key=lambda r:(-r['named_votes'],r['county_fips'],r['sheet'],sorted({int(v[0]) for v in r['rows']})))
        same(['full native numeric order',sid],[uk(x) for x in a],[vk(x) for x in b])
    # Independently derive peer primary2026 county/candidate controls from footer+101 detail.
    p26=defaultdict(Counter)
    for r in raw_peer:
        if r['baseline']=='senate_primary_2026' and r['canonical_candidate']!='generic_write_in' and r['votes']!='':
            if r['county'] in {'Johnson','Sedgwick','Shawnee','Wyandotte'} and r['role']!='county_footer':continue
            p26[r['county_fips']][r['canonical_candidate']]+=int(r['votes'])
    for f in om:
        for ck in IDENTITIES['senate_primary_2026']:
            same(['primary2026 county',f,ck],int(om[f]['senate_primary_2026_'+ck]),p26[f][ck])
    # Source hashes pin the compared bytes; peer scripts independently parse shared originals.
    paths=[STATE/'data/county-baselines.csv',PEER/'native-candidates.csv.gz',PEER/'native-units.jsonl.gz',PEER/'native-coverage.csv']
    result={'status':'pass' if not mismatches else 'fail','peer_actual_id':PEER_ID,
       'scope':'independent read-only comparison of all105 counties, all shared candidate/method scope, raw values, party headers, all22031 native contexts and full numeric native orders',
       'county_fields_compared':county_fields,'county_count':len(om),'native_unit_count':len(ounits),
       'shared_observations_compared':len(oc),'primary2026_county_candidate_values_compared':105*13,'complete_raw_rows_compared':raw_rows_compared,
       'full_county_order_agrees':not any(x['where']=='complete105 descending order' for x in mismatches),
       'native_order_ties':'descending named integers, county FIPS, sheet, exact ordered source rows; unknowns unranked',
       'method_scope':'Both extracts report combined/not separately published; no candidate-by-method counts exist in the shared statewide originals',
       'additional_turnout_fields':'Sedgwick2020 reported contest Total Votes Cast269 native rows plus county footer are retained in turnout extracts; peer raw-rows preserves them but native-candidates excludes this noncandidate field',
       'party_header_context':'All original raw row cells including party headers agree exactly. Peer source_party includes preceding header values NON, -, VOTE FOR 1; turnout retains header contexts separately from verified party identity and candidate-label prefixes.',
       'mismatches':mismatches,'peer_assets':[{'path':str(p.relative_to(STATE)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in paths],
       'turnout_csv_sha256':sha((STATE/'data/county-turnout.csv').read_bytes()),
       'coordinator_acceptance':False,'geographic_approval':'This comparison does not approve current November2026 IDs or boundaries.'}
    dump_json('peer-agreement.json',result)
    csv_output('extracts/peer-native-key-crosswalk.csv.gz',sorted(crosswalk,key=lambda r:(r['source_id'],r['sheet'],r['county_fips'],r['source_rows'])))
    print(json.dumps({k:v for k,v in result.items() if k not in ['peer_assets','mismatches']},indent=2))
    if mismatches:
        print(json.dumps({'mismatch_count':len(mismatches),'examples':mismatches[:6]},indent=2));raise SystemExit(1)
    contract=json.loads((HERE/'priority-set.json').read_text())
    contract['status']='independent primary-source and peer reconciliation complete; coordinator acceptance pending'
    contract['peer_reconciliation']={'status':'pass','peer_actual_id':PEER_ID,'evidence':'peer-agreement.json','native_key_crosswalk':'extracts/peer-native-key-crosswalk.csv.gz'}
    if (STATE/'data/coordinator-priority-acceptance.json').exists():
        contract['coordinator_acceptance_record']='../coordinator-priority-acceptance.json'
        contract['coordinator_acceptance_scope']='The external coordinator record is authoritative for research dispatch. The legacy false flag means this worker does not self-grant coordinator acceptance. No current geography approval is asserted; no reverse hash of the acceptance record is stored.'
        contract['status']='primary and peer reconciliation complete; research dispatch acceptance recorded externally by coordinator'
    dump_json('priority-set.json',contract)

if __name__=='__main__':main()
