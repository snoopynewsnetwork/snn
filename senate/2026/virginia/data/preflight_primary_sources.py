#!/usr/bin/env python3
"""Actual official-linked CSV hierarchy; independent cities remain localities."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json

D=Path(__file__).resolve().parent
N=D/'news'
mf={x['id']:x for x in json.loads((N/'manifest.json').read_text())}
sha=lambda b:hashlib.sha256(b).hexdigest()
tables={}
for year in [2024,2020,2018]:
    id=f'elect-{year}-senate-linked-csv';m=mf[id]
    z=(N/m['asset']).read_bytes();b=gzip.decompress(z)
    assert sha(z)==m['stored_sha256'] and sha(b)==m['raw_sha256']
    rows=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
    names={2024:['Timothy M. Kaine','Hung Cao'],2020:['Mark Robert Warner','Daniel Mac Arthur Gade'],2018:['Timothy Michael Kaine','Corey Alan Stewart']}
    assert rows[0][2:4]==names[year]
    assert rows[2][0:2]==['State','Virginia']
    state=list(map(int,rows[2][2:]));localities=[];native=[];now=None
    for i,row in enumerate(rows[3:],4):
        assert len(row)==len(rows[0])
        if row[0]=='Locality':
            now={'literal_name':row[1],'source_row':i,'counts':list(map(int,row[2:])),'native':[]}
            localities.append(now)
        else:
            assert row[0]=='Precinct' and now is not None
            r={'source_row':i,'locality_literal':now['literal_name'],'native_literal':row[1],
               'counts':list(map(int,row[2:])),'raw_row':row}
            now['native'].append(r);native.append(r)
    assert len(localities)==len({r['literal_name']for r in localities})==133
    assert len(native)=={2024:2669,2020:2846,2018:2825}[year]
    assert len({(r['locality_literal'],r['native_literal'])for r in native})==len(native)
    mismatches=[]
    for c in localities:
        sums=[sum(r['counts'][j]for r in c['native'])for j in range(len(c['counts']))]
        residual=[a-b for a,b in zip(sums,c['counts'])]
        c['native_sums']=sums;c['native_minus_locality']=residual
        if any(residual):mismatches.append({'locality':c['literal_name'],'source_row':c['source_row'],'native_minus_locality':residual})
        c['native_count']=len(c['native']);del c['native']
    locality_sums=[sum(c['counts'][j]for c in localities)for j in range(len(state))]
    native_sums=[sum(r['counts'][j]for r in native)for j in range(len(state))]
    assert native_sums==state
    if year==2018:
        assert {r['locality']:r['native_minus_locality'] for r in mismatches}=={'Fairfax City':[0,0,0,1,1,0],'Richmond City':[0,0,0,10,10,0],'Roanoke County':[0,0,0,25,25,0]}
        assert [a-b for a,b in zip(locality_sums,state)]==[0,0,0,-36,-36,0]
    else:assert not mismatches and locality_sums==state
    total_index=rows[0][2:].index('Total Votes Cast')
    for r in native:
        assert sum(r['counts'][:total_index])==r['counts'][total_index]
    assert state=={2024:[2417115,2019911,8509,4445535],2020:[2466500,1934199,4388,4405087,0],2018:[1910370,1374313,61565,5509,3351757,0]}[year]
    tables[str(year)]={'source_url':m['url'],'original_sha256':sha(b),'header':rows[0],
                       'party_header':rows[1],'state_controls':state,'localities':localities,
                       'native_rows':native,'native_count':len(native),'locality_candidate_sums':locality_sums,'native_candidate_sums':native_sums,'locality_native_mismatches':mismatches,'locality_minus_state':[a-b for a,b in zip(locality_sums,state)]}
out={'status':'original_linked_hierarchy_preflight_only_priority_unaccepted','tables':tables,
     'limits':['133 localities include independent cities and counties; city totals are not assigned to surrounding counties or merged by name.',
               'Locality and precinct tables overlap; native labels/source row positions are source identities, not approved FIPS/cross-year geometry.',
               'All8340 source-native rows balance to their respective state controls.2024/2020 each133 locality vectors also balance.2018 locality footer Write-Ins sum5473 vs state/native5509: native-minus-locality differences FairfaxCity+1,RichmondCity+10,RoanokeCounty+25; totalvotes likewise+36. Named3candidate vectors match at all levels. All original levels preserved, no footer repair or cause inferred.',
               '2020 official historical page explicitly notes conflicting official/unofficial source totals; current compiled CSV reconciliation doesnot prove amendment cause or full primary-original chronology.',
               '2020/2018 UnderVotes columns are all literal0; no meaning as actual ballot undervote universe inferred without original evidence.2024 has no under/over/ballot/registration fields here.',
               'Generic Write-Ins remain unallocated among named/valid candidates. Election-specific provisional/admin labels remain literal, not new physical precincts.',
               '2026ClassII Warner same2020seat;2024Kaine otherClassI. No2022Senate/Gov; actual2018Senate midterm is independently retained from its actual official linkedCSV, separate2022House/administrative context still requires proper source scope.',
               'No approved2026sourceIDs/crosswalk/cadence/remainingvotes or live model.']}
(D/'coordinator-primary-preflight.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({year:{'localities':len(t['localities']),'native':t['native_count'],'state':t['state_controls']}for year,t in tables.items()}))
