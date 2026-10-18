#!/usr/bin/env python3
"""Independent county/priority review; finer native contract acceptance is separate."""
from pathlib import Path
from collections import Counter, defaultdict
import csv, datetime, gzip, hashlib, io, json, re, runpy, subprocess, zipfile
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read_csv(p):
    with p.open() as f: return list(csv.DictReader(f))
ns = runpy.run_path(str(DATA / 'preflight_primary_sources.py'))
raw, sheet = ns['raw'], ns['sheet']
alias = {'Comanche ': 'Comanche'}
primary = defaultdict(Counter)
candidate_map = {'Kamala D. Harris / Tim Walz':'harris', 'Donald J. Trump / JD Vance':'trump',
                 'Chase Oliver / Mike ter Maat':'oliver', 'Robert F. Kennedy Jr./ Nicole Shanahan':'kennedy'}
with zipfile.ZipFile(io.BytesIO(raw('sos-2024-president-county'))) as z:
    for row, cells in sheet(z, 1):
        if row == 1: continue
        assert cells['G'] == 'President / Vice President' and cells['J'].isdigit()
        primary[alias.get(cells['E'],cells['E'])][candidate_map[cells['H']]] += int(cells['J'])
assert len(primary) == 105
turnout = read_csv(DATA / 'county-turnout.csv')
baseline = read_csv(DATA / 'county-baselines.csv')
assert len(turnout) == len(baseline) == 105
t = {r['county']:r for r in turnout}; b = {r['county']:r for r in baseline}
assert set(t) == set(b) == set(primary)
acq = json.loads((DATA / 'turnout/source/acquisition.json').read_text())
census = next(a for a in acq if a['id']=='county-codes-2020')
stored = (DATA / 'turnout' / census['path']).read_bytes()
assert hashlib.sha256(stored).hexdigest()==census['stored_sha256']
body = gzip.decompress(stored)
assert hashlib.sha256(body).hexdigest()==census['raw_sha256'] and len(body)==census['raw_bytes']
fips = {r['COUNTYNAME'].removesuffix(' County'):'20'+r['COUNTYFP']
        for r in csv.DictReader(io.StringIO(body.decode()),delimiter='|') if r['STATEFP']=='20'}
assert len(fips)==105 and set(fips)==set(t)
comparisons=0
for county in t:
    assert t[county]['county_fips']==b[county]['county_fips']==fips[county]
    assert t[county]['county_key']==b[county]['county_key']=='US-KS-'+fips[county]
    for candidate,votes in primary[county].items():
        assert int(t[county]['president_2024_'+candidate])==int(b[county]['president_2024_'+candidate+'_votes'])==votes
        comparisons+=2
    for year, candidates in [(2022,['holland','moran','graham']), (2020,['bollier','marshall','buckley'])]:
        for candidate in candidates:
            assert int(t[county][f'senate_{year}_{candidate}'])==int(b[county][f'senate_{year}_{candidate}_votes'])
            comparisons+=1
    for field, source in [('ballots_cast_2024_broad','ballots_cast'),('registered_voters_2024_broad','registered_voters')]:
        assert int(t[county][field])==ns['county_turnout'][county][source]
        comparisons+=1
controls=read_csv(DATA/'baselines/candidate-controls.csv')
for control in controls:
    source = ('sos-2024-general-canvass' if control['baseline']=='president_2024' else
              'sos-2026-primary-canvass' if control['baseline']=='senate_primary_2026' else
              'sos-'+control['baseline'][-4:]+'-general-canvass')
    text = subprocess.run(['pdftotext','-layout','-','-'],input=raw(source),capture_output=True,check=True).stdout.decode()
    title = 'President / Vice President' if control['baseline']=='president_2024' else 'United States Senate'
    section=text.split(title,1)[1].split('United States House of Representatives 1',1)[0]
    match=re.search(re.escape(control['candidate_name'])+r'\s+([\d,]+)\s+[\d.]+%',section)
    assert match, control['candidate_name']
    votes=int(match[1].replace(',',''))
    assert votes==int(control['county_sum'])==int(control['statewide_control'])
    key=control['baseline']+'_'+control['candidate']
    assert sum(int(row[key]) for row in turnout)==votes
ranked=sorted(t,key=lambda c:(-sum(primary[c].values()),c))
assert [r['county'] for r in turnout]==ranked
assert [r['county'] for r in sorted(baseline,key=lambda r:int(r['president_2024_rank']))]==ranked
den=sum(sum(v.values()) for v in primary.values());running=0;priority=[]
for county in ranked:
    if running*5>=den*4:break
    priority.append(county);running+=sum(primary[county].values())
assert (den,len(priority),running)==(1327591,23,1067659)
assert running-sum(primary[priority[-1]].values())==1057110
contract=json.loads((DATA/'turnout/priority-set.json').read_text())
assert contract['ordered_priority_names']==priority
assert contract['ordered_priority_keys']==['US-KS-'+fips[c] for c in priority]
assert contract['full_all_unit_order']==['US-KS-'+fips[c] for c in ranked]
peer=json.loads((DATA/'baselines/peer-reconciliation.json').read_text())
assert peer['status']=='pass' and not peer['county_differences'] and not peer['native_field_differences'] and not peer['candidate_field_differences']
keybytes=('\n'.join('US-KS-'+fips[c] for c in priority)+'\n').encode()
(DATA/'coordinator-priority-keys.txt').write_bytes(keybytes)
result=dict(status='pass',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            scope='County arithmetic and exact research priority accepted; finer native contract and final worker metadata review remain separate. No current geography or outcome-model approval.',
            counties=105,primary_2024_county_candidate_cells=420,county_peer_and_administration_comparisons=comparisons,
            primary_candidate_controls=len(controls),denominator=den,top15=sum(sum(primary[c].values()) for c in ranked[:15]),
            priority_count=len(priority),priority_votes=running,preceding_votes=1057110,
            crossing={'county':'Sumner','fips':'20191','votes':10549},remainder_count=82,remainder_votes=den-running,
            ordered_keys_sha256=hashlib.sha256(keybytes).hexdigest(),
            source_candidate_universe='Four reported named presidential tickets; statewide generic/valid write-ins and under/over unavailable, not zero.',
            county_CSV_hashes={str(p.relative_to(ROOT)):digest(p) for p in [DATA/'county-turnout.csv',DATA/'county-baselines.csv']},
            peer_checks={'county_fields':peer['county_field_comparisons'],'native_units':peer['native_units_compared'],'candidate_source_cells':peer['source_cell_candidate_comparisons']},
            retained_gaps=['2022turnout ballot/registration county anomalies; excluded from clean weights.','2024workbook vs certification-release ballot/registration vintage differences.','Missing or suppressed detail counts and residuals remain unallocated.','Current grace-period court status must be verified from primary orders.'])
out=DATA/'coordinator-county-reconciliation.json'
if out.exists():
    previous=json.loads(out.read_text())
    if {k:v for k,v in previous.items() if k!='checked_utc'}=={k:v for k,v in result.items() if k!='checked_utc'}:result['checked_utc']=previous['checked_utc']
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
