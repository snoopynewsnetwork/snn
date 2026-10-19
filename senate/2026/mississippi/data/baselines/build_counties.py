"""Independently extract original state CSVs/EAC, preserving literal identities/rows."""
import csv,gzip,io,json,re,zipfile,xml.etree.ElementTree as ET
from collections import defaultdict
from sources import *
def writecsv(p,rows):
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def rawcsv(key):
    raw=original(key);rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    (OUT/'extracts'/(key+'-all-rows.jsonl.gz')).write_bytes(gzip.compress(('\n'.join(json.dumps(dict(source_id=key,source_row=i+2,fields=r),ensure_ascii=False) for i,r in enumerate(rows))+'\n').encode(),mtime=0))
    return rows
def eac():
    result={};code=[]
    for year in [2022,2024]:
        key=next(k for k in references() if k.startswith(f'eac-{year}-csv-') and not k.endswith('parent'))
        z=zipfile.ZipFile(io.BytesIO(original(key)));member=next(n for n in z.namelist() if n.endswith('.csv'))
        rr=list(csv.DictReader(io.StringIO(z.read(member).decode('utf-8-sig'))))
        ms=[dict(source_id=key,zip_member=member,source_row=i+2,**r) for i,r in enumerate(rr) if r['State_Abbr']=='MS']
        assert len(ms)==82
        (OUT/'extracts'/f'eac-{year}-MS-all-fields.jsonl.gz').write_bytes(gzip.compress(('\n'.join(json.dumps(r) for r in ms)+'\n').encode(),mtime=0))
        result[year]={r['FIPSCode'][:5]:r for r in ms}
        key=next(k for k in references() if k.startswith(f'eac-{year}-codebook-') and not k.endswith('parent'))
        z=zipfile.ZipFile(io.BytesIO(original(key)));ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        strings=[''.join(s.itertext()) for s in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
        for member in z.namelist():
            if member.startswith('xl/worksheets/sheet') and member.endswith('.xml'):
                for row in ET.fromstring(z.read(member)).findall('.//m:row',ns):
                    vals=[]
                    for c in row:
                        v=c.find('m:v',ns);s=v.text if v is not None else '';vals.append(strings[int(s)] if c.attrib.get('t')=='s' else s)
                    if vals and (vals[0].startswith(('A1','F1')) or any('missing' in s.lower() for s in vals)):
                        code.append(dict(year=year,source_id=key,member=member,row=row.attrib['r'],values=vals))
    save(OUT/'extracts/eac-codebook-fields.json',code)
    return result
def main():
    surveys=eac();fips={r['Jurisdiction_Name'].removesuffix(' COUNTY').title():k for k,r in surveys[2024].items()}
    # Explicit source alias, not alphabetical synthetic FIPS assignment.
    fips['Jeff Davis']=fips['Jefferson Davis'];fips['DeSoto']=fips['Desoto']
    candidates=[];county={};controls=[]
    pike=[7402,20,17,13,7943,10,9,58,13]
    for year in [2024,2020]:
        rr=rawcsv(f'sos-{year}-recap-csv');presnames=list(dict.fromkeys(r['Candidate'] for r in rr if r['Office'].strip()=='United States-President'))
        for pos,r in enumerate(rr,2):
            if r['Office'].strip() not in ['United States-Senate','United States-President']:continue
            if year==2020 and r['Office'].strip()!='United States-Senate':continue
            c=r['County'];fid=fips[c];contest=f'{year}-'+('senate' if r['Office'].strip().endswith('Senate') else 'president');v=int(r['County Total']);old=v;sid=f'sos-{year}-recap-csv';pointer=f'CSV record {pos}'
            if year==2024 and c=='Pike':
                v=({'Ty Pinkins':7130,'Roger F. Wicker':8205}[r['Candidate']] if contest.endswith('senate') else pike[presnames.index(r['Candidate'])])
                sid='sos-2024-county-pike-updated';pointer='PDF page 4 TOTAL column; independently visually read'
            candidates.append(dict(contest=contest,election_date='2024-11-05' if year==2024 else '2020-11-03',county=c,fips=fid,
               office_literal=r['Office'],candidate_literal=r['Candidate'],party_literal=r['Party'],votes=v,source_id=sid,source_position=pointer,
               original_csv_votes=old,original_csv_state_total=int(r['State Total']),original_csv_row=pos,original_csv_source_id=f'sos-{year}-recap-csv'))
            dest=county.setdefault(fid,dict(county=c,fips=fid,geography_type='county'))
            role='A' if r['Party']=='Democrat' else 'B' if r['Party']=='Republican' else 'other'
            dest[contest+'_'+role]=dest.get(contest+'_'+role,0)+v
        for name in list(dict.fromkeys((r['Office'],r['Candidate'],r['Party']) for r in rr if r['Office'].strip() in ['United States-Senate','United States-President'])):
            selected=[r for r in rr if (r['Office'],r['Candidate'],r['Party'])==name]
            controls.append(dict(year=year,office_literal=name[0],candidate_literal=name[1],party_literal=name[2],county_rows=len(selected),county_sum=sum(int(r['County Total']) for r in selected),state_column_values=sorted({int(r['State Total']) for r in selected})))
    historical=OUT/'county-2018-readings.json'
    if historical.exists():
        ledger=json.loads(historical.read_text())
        for obs in ledger['readings']:
            contest='2018-'+obs['stage'];key=obs['source_id'];label=key.split('county-',1)[1]
            aliases={'jefferson-davis':'Jeff Davis','desoto':'DeSoto','jackon':'Jackson'}
            county_name=aliases.get(label,label.replace('-',' ').title());fid=fips[county_name];dest=county[fid]
            for name,v in obs['candidate_values'].items():
                role='A' if name=='Mike Espy' else 'B' if name=='Cindy Hyde-Smith' else 'other'
                dest[contest+'_'+role]=dest.get(contest+'_'+role,0)+v
                if role=='other':dest[contest+'_'+('Bartee' if name=='Tobey Bernard Bartee' else 'McDaniel')]=v
                candidates.append(dict(contest=contest,election_date='2018-11-27' if obs['stage']=='runoff' else '2018-11-06',county=county_name,fips=fid,office_literal='United States-Senate Unexpired Term' if obs['stage']=='runoff' else 'United States-Senate Special',candidate_literal=name,party_literal='',votes=v,source_id=key,source_position=json.dumps(obs['source_positions'],ensure_ascii=False),party_scope='Blank source party cell retained; named Espy/Hyde-Smith pair, no party pool. House Clerk supplementary affiliations are separate evidence.',source_vintage='Original county packet; statewide candidate reconciliation tracked separately.'))
    contests=['2024-senate','2024-president','2020-senate']+(['2018-special','2018-runoff'] if historical.exists() else [])
    for fid,r in county.items():
        for contest in contests:
            a=r[contest+'_A'];b=r[contest+'_B'];o=r.get(contest+'_other',0);n=a+b
            r.update({contest+'_other':o,contest+'_pair_votes':n,contest+'_named_candidate_votes':n+o,contest+'_A_pair_share':a/n,
              contest+'_pair_margin_pp':100*(a-b)/n,contest+'_all_candidate_margin_pp':100*(a-b)/(n+o),contest+'_net_A_minus_B':a-b,
              contest+'_historical_winner': 'A' if a>b else 'B' if b>a else 'tie'})
        for year in [2022,2024]:
            s=surveys[year][fid]
            for field in [k for k in s if re.fullmatch(r'(A1|F1)([a-z](_Other)?|Comments)',k) or k.startswith('F2_') or k=='F2Comments']:
                r[f'eac_{year}_{field}']=s.get(field,'')
            assert int(s['A1a'])==int(s['A1b'])+int(s['A1c'])
    ordered=sorted(county.values(),key=lambda r:(-r['2024-senate_named_candidate_votes'],r['fips']))
    total=sum(r['2024-senate_named_candidate_votes'] for r in ordered);cum=0;cross=None
    for rank,r in enumerate(ordered,1):
        cum+=r['2024-senate_named_candidate_votes'];r.update(rank=rank,cumulative_named_votes=cum,priority=False,priority_denominator=total,priority_scope='county_parent_80_sensitivity_only_not_native_dispatch',primary_native_priority_contract_path='data/baselines/native-priority-contract.json')
        if cross is None and 5*cum>=4*total:cross=rank
    for r in ordered:r['priority']=r['rank']<=max(15,cross)
    writecsv(BASE/'data/county-baselines.csv',ordered);writecsv(OUT/'candidate-votes.csv',candidates)
    save(OUT/'state-csv-controls.json',controls)
    totals={con:{name:sum(r['votes'] for r in candidates if r['contest']==con and r['candidate_literal']==name) for name in dict.fromkeys(r['candidate_literal'] for r in candidates if r['contest']==con)} for con in contests}
    assert totals['2024-senate']=={'Ty Pinkins':451981,'Roger F. Wicker':763420}
    assert totals['2020-senate']=={'Mike Espy':578691,'Cindy Hyde-Smith':709511,'Jimmy L. Edwards':23152}
    if historical.exists():
        primary=json.loads((OUT/'source/primary-state-readings.json').read_text())
        save(OUT/'historical-county-controls.json',[dict(contest=c,county_rows=len({r['fips'] for r in candidates if r['contest']==c}),county_candidate_sums=totals[c],primary_state_candidate_controls=primary[c]['candidates'],candidate_differences={n:v-primary[c]['candidates'][n] for n,v in totals[c].items()},qualification='No scaling or allocation of differences; original-county and statewide source scopes/vintages retained.') for c in ['2018-special','2018-runoff']])
    save(OUT/'county-contract.json',dict(schema_version='ms-baselines-1',status='independent_county_check_native_pending_not_accepted',basis='2024 Senate State SEMS/certified two named candidates; generic write-in marks outside scope',state_total=total,candidate_totals=totals,top15_votes=sum(r['2024-senate_named_candidate_votes'] for r in ordered[:15]),minimum80_count=cross,preceding_votes=ordered[cross-2]['cumulative_named_votes'],crossing_votes=ordered[cross-1]['cumulative_named_votes'],crossing_county=ordered[cross-1]['county'],ordered_keys=[r['fips'] for r in ordered],ordered_priority_keys=[r['fips'] for r in ordered[:max(15,cross)]],county_csv_sha256=sha((BASE/'data/county-baselines.csv').read_bytes()),candidate_csv_sha256=sha((OUT/'candidate-votes.csv').read_bytes()),fips_authority='EAC 2024 v2 FIPSCode prefix; Jeff Davis -> Jefferson Davis; DeSoto -> DESOTO COUNTY',native_coverage='pending independent source extraction',current_geography_approval=False))
    print(json.dumps(totals));print('min80',cross,total,ordered[cross-1]['county'])
if __name__=='__main__':main()
