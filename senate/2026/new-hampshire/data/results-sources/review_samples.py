#!/usr/bin/env python3
"""Reconcile representative local publications to their actual field universes."""
import gzip,json,re,subprocess
from acquire import ROOT,dump,sha
from inspect_html import decode_body
def text(sid):return gzip.decompress((ROOT/'derived'/(sid+'.txt.gz')).read_bytes()).decode()
native=[json.loads(l) for l in gzip.open(ROOT/'historical-native-records.jsonl.gz','rt') if l.strip()]
pres=[r for r in native if r['source_id']=='sos-2024-president-archived-original']
audits=[]
sid='sample-portsmouth-november-5-2024-state-general';t=text(sid);part=t.split('Governor')[0]
cols={'Trump, Donald':'trump_vance','Oliver, Chase':'oliver_ter_maat','Stein, Jill':'stein_ware','Harris, Kamala':'harris_walz'};matrix={};positions=[]
for line_no,line in enumerate(part.splitlines(),1):
    for prefix,key in cols.items():
        if line.startswith(prefix):
            vals=[int(n.replace(',','')) for n in re.findall(r'(?<!\w)\d[\d,]*(?!\w)',line)]
            assert len(vals)==6 and sum(vals[:5])==vals[-1]
            for ward in range(1,6):
                p=next(r for r in pres if r['county']=='Rockingham' and r['native_label'].strip()==f'Portsmouth Ward {ward}')
                assert vals[ward-1]==p['fields'][key],(ward,key,vals,p['fields'])
            matrix[key]=vals;positions.append({'page':1,'line':line_no,'text':line})
assert len(matrix)==4
audits.append({'source_id':sid,'election':'2024-11-05 general President','scope':'Four printed tickets, five wards and overlapping city TOTAL. Write-ins/under/over not supplied in this local matrix; never infer zero.','fields':matrix,'raw_positions':positions,'checks':'all 20 ward/candidate cells equal primary SOS; each city total equals five wards','candidate_field_checks':20,'method_split':None,'source_numeric_unit_ids':None})
sid='municipal-londonderry-documents1';t=text(sid)
expected={'harris_walz':7655,'trump_vance':8435,'oliver_ter_maat':54,'stein_ware':44,'generic_write_ins':86,'undervotes':66,'overvotes':9}
row=next(r for r in pres if r['native_label'].strip()=='Londonderry');assert row['fields']==expected
for val in ['16,050','299','16,349','8,435','7,655','54','44','86','66']:
    assert val in t,val
assert sum(expected[k] for k in expected)==16349
audits.append({'source_id':sid,'election':'2024-11-05 general President','scope':'Presidential panel only, manually visually reviewed page1. Adjacent offices use different manual/ballot totals.','source_clock':'Wednesday, November 6, 2024, 2:01:48 PM EST','candidate_fields':expected,'presidential_ballots_cast':16349,'scanned_ballots':16050,'manual_ballots':299,'checks':'seven fields agree with primary SOS; candidate/generic+under+over=16349','caution':'scanned/manual are counting modes, not proven absentee/ElectionDay voting methods. Neighboring offices list manual265/ballots16315. No rescaling or statewide extrapolation.'})
sid='municipal-salem-documents1';t=text(sid);start=t.index('Senator - US - Republican');part=t[start:t.index('Representative - Congress',start)]
rows=[]
for ln,line in enumerate(part.splitlines(),1):
    if 'Total Per Race' in line:continue
    m=re.match(r'^\s*(.*?)\s{2,}([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)(?:\s+X)?\s*$',line)
    if m:
        vals=[int(v.replace(',','')) for v in m.groups()[1:]];assert sum(vals[:5])==vals[5];rows.append({'label':m[1],'values':vals,'panel_line':ln,'literal_line':line})
assert len(rows)==11,len(rows)
assert [sum(r['values'][i] for r in rows) for i in range(5)]==[456,557,759,520,518]
assert sum(r['values'][-1] for r in rows)==2810
audits.append({'source_id':sid,'election':'2026-09-08 Republican primary Senate; NOT November general','scope':'five polling-site columns Woodbury1/Woodbury2/NorthSalem/Fisk/Barron plus overlapping total','rows':rows,'polling_site_ballots':[456,557,759,520,518],'total_per_race':2810,'checks':'11 candidate/write-in/under/over rows each sum across five sites; complete panel sums2810','current_general_election_id':None,'current_general_candidate_ids':None,'reporting_completion':None})
sid='sample-londonderry-2024-general-election-write';t=text(sid)
assert '86 total write-ins / 0 not adjudicated' in t
audits.append({'source_id':sid,'election':'2024-11-05 general President','scope':'Local Write-In Adjudication Report, presidential panel reports86 total/0 not adjudicated. Literal names include noncandidate/slogan entries; no statewide valid named write-in allocation inferred.','source_clock':'Wednesday, November 6, 2024, 2:18:07 PM EST','relationship':'Overlaps the86 generic Write-In cell in tally report; do not add the two files.'})
dump(ROOT/'sample-audits.json',audits)
# Deterministic visual QA previews, originals never modified.
for sid,page in [('municipal-londonderry-documents1',1),('sample-portsmouth-november-5-2024-state-general',1),('municipal-salem-documents1',1),('sample-moultonborough-polls',1),('court-oct2-order',50)]:
    m=json.load(open(ROOT/'source'/(sid+'.json')));body=decode_body(m)
    import tempfile,pathlib
    with tempfile.TemporaryDirectory(prefix='nh-official-pdf-') as td:
        pdf=pathlib.Path(td)/'source.pdf';pdf.write_bytes(body)
        subprocess.run(['pdftoppm','-f',str(page),'-singlefile','-scale-to','1600','-png',str(pdf),str(ROOT/'qa'/(sid+'-page'+str(page)))],check=True,capture_output=True)
print('PASS: Portsmouth20 cells; Londonderry7 fields+ballot balance; Salem5-site primary panel; distinct write-in scope')
