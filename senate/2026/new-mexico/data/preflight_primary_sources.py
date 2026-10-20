#!/usr/bin/env python3
"""Primary route observations, source-scoped controls and privacy residuals."""
from pathlib import Path
import collections
import csv
import gzip
import hashlib
import io
import json

D=Path(__file__).resolve().parent
N=D/'news'
mf={x['id']:x for x in json.loads((N/'manifest.json').read_text())}
sha=lambda b:hashlib.sha256(b).hexdigest()
def body(id):
    m=mf[id];stored=(N/m['asset']).read_bytes();b=gzip.decompress(stored)
    assert sha(stored)==m['stored_sha256'] and sha(b)==m['raw_sha256']
    return b
controls={}
for id in ['sos-2024-federal-csv','sos-2020-federal-csv','sos-2022-statewide-csv']:
    raw=body(id);rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    selected=[x for x in rows if 'Senat' in x['RaceName'] or 'Governor' in x['RaceName']]
    for x in selected:
        assert int(x['CandidateVotes'])==sum(int(x[k])for k in ['CandidateAbsenteeVotes','CandidateElectionDayVotes','CandidateEarlyVotes'])
    controls[id]={'url':mf[id]['url'],'original_sha256':sha(raw),'rows':len(rows),
                  'selected_state_candidate_method_controls':selected,
                  'native_county_allocation':False,'header_only_is_unavailable_not_zero':not rows}

id='elstats-2024-senate-linked-csv';rows=list(csv.reader(io.StringIO(body(id).decode())))
assert rows[0]==['','','Martin Heinrich','Nella Louise Domenici','Total Votes Cast','Total Ballots Cast']
assert rows[2]==['State','New Mexico','497333','405978','903311','903311']
counties=[];native=[];now=None
for i,row in enumerate(rows[2:],3):
    assert len(row)==6
    if row[0]=='County':
        now={'county_literal':row[1],'source_row':i,'raw_row':row,'controls':list(map(int,row[2:])),'native_rows':[]}
        counties.append(now)
    elif row[0]=='Precinct':
        assert now is not None
        r={'county_literal':now['county_literal'],'native_label':row[1],'source_row':i,'raw_row':row,
           'numeric_fields':[int(x)if x.isdigit()else None for x in row[2:]],
           'missing_literals':[x for x in row[2:]if not x.isdigit()],
           'administrative_source_label':row[1]=='Voter Privacy'}
        native.append(r);now['native_rows'].append(r)
    else:assert row[0]=='State'
assert len(counties)==33 and len(native)==2201
assert [sum(c['controls'][j]for c in counties)for j in range(4)]==[497333,405978,903311,903311]
assert sum(r['administrative_source_label']for r in native)==33
assert sum(v is None for r in native for v in r['numeric_fields'])==36
assert len({(r['county_literal'],r['native_label'])for r in native})==2201
for c in counties:
    c['known_native_sums']=[sum(r['numeric_fields'][j]for r in c['native_rows']if r['numeric_fields'][j]is not None)for j in range(4)]
    c['unallocated_residuals']=[a-b for a,b in zip(c['controls'],c['known_native_sums'])]
    c['native_row_count']=len(c['native_rows'])
    del c['native_rows']
out={'status':'primary_route_preflight_only_no_priority_acceptance','legacy_export_controls':controls,
     'new_2024_official_database':{'source_url':mf[id]['url'],'original_sha256':mf[id]['raw_sha256'],
                                  'header':rows[0],'state_controls':rows[2],'counties':counties,
                                  'native_rows':native,'masked_numeric_cells':36,'masked_candidate_cells':30,
                                  'administrative_privacy_rows':33,'original_state_canvass_link':'https://nm.elstats2.civera.com/eng/files/serve/799',
                                  'original_state_canvass_fetch_status':mf['elstats-2024-state-canvass-original']['status']},
     'limitations':['Actual legacy2024official archiveEID2882 federalHTML/export currently has no candidates despite200; header-only is notzero. New official database restores candidate/county/native observations.',
                    'All33new2024county vectors reconcile statewide497333/405978;2201source rows include33VoterPrivacy aggregates, not2201proved physical precincts.',
                    '30candidate and6total/ballot cells are masked; seven county residual vectors remain unallocated. A sourcePrivacy aggregate or zero residual doesnot make every missing cell knownzero.',
                    'TotalBallotsCast equalscandidate scope atstate/county level in this export; actual registration/wholeballot/under-over semantics require independent primary controls, notautomatic turnout admission.',
                    'Published current document799 explicitly links original statecanvass, directsourcefile403 retained; original summary/native-provenance recovery remainsworker task.',
                    '2020/2022statecandidate-methodcontrols available, blankAreaNum isnotcountyallocation; CSVtrailingemptyfields retained in originals.',
                    '2026ClassII Lujan same2020seat;2024Heinrich otherClassI;2022Governor actualmidterm. No liveNovemberID/cadence/currentgeographic approval or acceptedpriority.']}
(D/'coordinator-primary-preflight.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'state_candidate_controls_2024':[497333,405978],'county_count':33,'native_rows':2201,'masked_cells':36,'residual_counties':[c['county_literal']for c in counties if any(c['unallocated_residuals'])]}))
