"""Reproduce all-county historical vectors and exact integer priority calculation.

County-native checks are separately source-scoped; this never allocates ballots
or assumes cross-year precinct equivalence. CSV literal fields remain in extracts.
"""
import csv,gzip,io,json
from decimal import Decimal
from acquire_sources import BASE,OUT,source,receipts,savejson,sha

def csvrows(key):
    raw=source(key);rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    data=[dict(source_id=key,source_row=i+2,raw_fields=r) for i,r in enumerate(rows)]
    (OUT/'extracts'/(key+'-rows.jsonl.gz')).write_bytes(gzip.compress(('\n'.join(json.dumps(x,ensure_ascii=False) for x in data)+'\n').encode(),mtime=0))
    return rows
def percent(a,b):return str(Decimal(a)*100/Decimal(b))

def main():
    rows=csvrows('sos-2024-recap-csv');old=csvrows('sos-2020-recap-csv')
    counties=sorted({r['County'] for r in rows});assert len(counties)==82
    counties_for_fips=sorted('Jefferson Davis' if c=='Jeff Davis' else c for c in counties)
    fips={c:f'28{2*i+1:03d}' for i,c in enumerate(counties_for_fips)}
    # Explicit published replacement: independently visually reviewed updated Pike p4.
    pike={'Ty Pinkins':7130,'Roger F. Wicker':8205}
    pike_pres={'Kamala D. Harris':7402,'Chase Oliver':20,'Jill Stein':17,'Randall Terry':13,
               'Donald J. Trump':7943,'Shiva Ayyadurai':10,'Claudia De la Cruz':9,'Robert F. Kennedy Jr.':58,'Peter Sonski':13}
    control={'Ty Pinkins':451981,'Roger F. Wicker':763420}
    candidates=[];county=[]
    for c in counties:
        dest={'county':c,'fips':fips.get(c if c!='Jeff Davis' else 'Jefferson Davis'),'geography_type':'county','election_date':'2024-11-05'}
        for year,rr in [('2024',rows),('2020',old)]:
            for office,abbr in [('United States-Senate','senate'),('United States-President','president')]:
                selected=[(i+2,r) for i,r in enumerate(rr) if r['County']==c and r['Office'].strip()==office]
                total=0
                for pos,r in selected:
                    v=int(r['County Total']);sid=f'sos-{year}-recap-csv';pointer=f'CSV row {pos}'
                    if year=='2024' and c=='Pike':
                        if abbr=='senate':v=pike[r['Candidate']]
                        else:v=next(n for name,n in pike_pres.items() if r['Candidate'].startswith('Presidential Electors for '+name))
                        sid='sos-2024-county-pike-updated';pointer='PDF page 4, TOTAL column'
                    candidates.append(dict(county=c,fips=dest['fips'],election_date='2024-11-05' if year=='2024' else '2020-11-03',office_literal=r['Office'],candidate_literal=r['Candidate'],party_literal=r['Party'],votes=v,source_id=sid,source_position=pointer,prior_csv_votes=int(r['County Total']),prior_csv_source_row=pos))
                    total+=v
                    if abbr=='senate':dest[year+'_senate_'+('pinkins' if r['Candidate']=='Ty Pinkins' else 'wicker' if r['Candidate']=='Roger F. Wicker' else 'espy' if r['Candidate']=='Mike Espy' else 'hyde_smith' if r['Candidate']=='Cindy Hyde-Smith' else 'edwards')]=v
                dest[year+'_'+abbr+'_candidate_votes']=total
        for k in ['2024_ballots_cast','2024_registered_voters','2024_blank','2024_under','2024_over','2024_generic_write_in_votes']:
            dest[k]=None
        county.append(dest)
    for name,num in control.items():assert sum(r['votes'] for r in candidates if r['election_date']=='2024-11-05' and r['office_literal']=='United States-Senate' and r['candidate_literal']==name)==num
    county.sort(key=lambda x:(-x['2024_senate_candidate_votes'],x['fips']))
    total=sum(x['2024_senate_candidate_votes'] for x in county);assert total==1215401
    cum=0;cross=None
    for i,r in enumerate(county,1):
        cum+=r['2024_senate_candidate_votes'];r.update(rank=i,cumulative_votes=cum,share=percent(r['2024_senate_candidate_votes'],total),cumulative_share=percent(cum,total),priority=False)
        if cross is None and 5*cum>=4*total:cross=i
    count=max(15,cross)
    for r in county:r['priority']=r['rank']<=count
    with (BASE/'data/county-turnout.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(county[0]));w.writeheader();w.writerows(county)
    with (OUT/'candidate-votes.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(candidates[0]));w.writeheader();w.writerows(candidates)
    contract=dict(schema_version='ms-turnout-1',status='in_progress_not_coordinator_accepted',basis_election='2024-11-05',basis_contest='United States-Senate',denominator='reported named candidate votes; write-in availability separately unresolved at native level',state_candidate_votes=total,
        candidate_controls=control,coverage=dict(expected_counties=82,included_counties=len(county),complete_county_order=True,native_unit_extraction='in_progress'),
        top15=dict(count=15,votes=sum(r['2024_senate_candidate_votes'] for r in county[:15]),share_percent=percent(sum(r['2024_senate_candidate_votes'] for r in county[:15]),total)),
        minimum80=dict(count=cross,votes=county[cross-1]['cumulative_votes'],share_percent=county[cross-1]['cumulative_share'],preceding_count=cross-1,preceding_votes=county[cross-2]['cumulative_votes'],crossing_key=county[cross-1]['fips'],crossing_county=county[cross-1]['county']),
        ordered_priority_keys=[r['fips'] for r in county[:count]],priority_count=count,all_unit_order=county,
        remainder=dict(count=82-count,votes=total-county[count-1]['cumulative_votes'],ordered_keys=[r['fips'] for r in county[count:]]),
        source_native_constituents=[],peer_agreement=None,current_2026_geographic_approval=False)
    savejson(OUT/'priority-set.json',contract)
    print(json.dumps({k:v for k,v in contract.items() if k in ['coverage','top15','minimum80','remainder']}))

if __name__=='__main__':main()
