#!/usr/bin/env python3
"""Complete archived original presidential abstract; reject misleading routes."""
from pathlib import Path
import gzip
import hashlib
import json
import re
import subprocess

D = Path(__file__).resolve().parent
N = D/'news'
mf = {r['id']:r for r in json.loads((N/'manifest.json').read_text())}
sha = lambda b:hashlib.sha256(b).hexdigest()
def body(id):
    m=mf[id];z=(N/m['asset']).read_bytes();raw=gzip.decompress(z)
    assert sha(z)==m['stored_sha256'] and sha(raw)==m['raw_sha256']
    return raw
complete=body('sos-2024-results-archived-20241212')
partial=body('sos-2024-results-archived-20250118')
assert b'%%EOF' in complete[-100:] and len(complete)==1185360
assert len(partial)==1048576 and b'%%EOF' not in partial[-100:]
assert complete[:len(partial)]==partial
text=subprocess.run(['pdftotext','-layout','-','-'],input=complete,capture_output=True,check=True).stdout.decode()
page=text.split('\f')[0]
assert 'US President' in page and 'November 5, 2024' in page
pattern=re.compile(r'^\s*(.+?)\s+('+r'\d[\d,]*\s+'*7+r'\d[\d,]*)\s*$')
rows=[];total=None
for i,line in enumerate(page.splitlines()):
    m=pattern.match(line)
    if not m:continue
    name=m[1].strip();values=[int(v.replace(',',''))for v in m[2].split()]
    record={'county_literal':name,'PDF_page':1,'line_ordinal_zero_based':i,'raw_line':line,'values':values}
    if name=='Total':total=record
    else:rows.append(record)
assert len(rows)==len({r['county_literal']for r in rows})==36
sums=[sum(r['values'][i]for r in rows)for i in range(8)]
assert sums==total['values']==[33733,5644,9061,1850,919480,19099,1240600,15026]
rejected=[]
for id in ['sos-2024-abstract-original','sos-2022-abstract-original','sos-2020-abstract-original']:
    b=body(id);t=subprocess.run(['pdftotext','-layout','-','-'],input=b,capture_output=True,check=True).stdout.decode()
    assert 'Voter Registration Comparison by County' in t
    rejected.append({'capture_id':id,'raw_sha256':sha(b),'actual_content':'Voter Registration Comparison by County, not candidate results. Capture ID is not a content classification.'})
out={'status':'primary_presidential_abstract_reconciles_priority_unaccepted',
     'source':{'capture_id':'sos-2024-results-archived-20241212','actual_original_url':mf['sos-2024-results-archived-20241212']['url'],'raw_sha256':sha(complete),'raw_bytes':len(complete),'complete_EOF':True},
     'columns':['Robert F Kennedy Jr (WTP)','Cornel West (P)','Chase Oliver (L)','Randall Terry (C)','Donald J Trump (R)','Jill Stein (PG)','Kamala D Harris (D)','Misc.'],
     'county_rows':rows,'state_controls':sums,'reported_named_plus_Misc_total':sum(sums),
     'truncated_archive_observation':{'capture_id':'sos-2024-results-archived-20250118','raw_bytes':len(partial),'raw_sha256':sha(partial),'exact_prefix_of_complete_original':True,'classification':'Truncated archive capture, not an established different candidate vintage.'},
     'rejected_candidate_abstract_classifications':rejected,
     'limits':['Current original candidate PDF route404; complete actual official archive recovery retained with headers/source chain.',
               'Public history webpart GET shell200 but observed anonymous read-only Lists SOAP route401; no credentials requested or source absence inferred.',
               'Current precinct record search returns0; complete precinct originals not recovered by this preflight.',
               'Presidential and vice-presidential tables overlap; do not add repeated elector/slate counts. Misc. scope is not a demonstrated valid/named write-in allocation.',
               '2020 same-ClassII Merkley and2022 other-ClassIII Wyden baselines/native source recovery remain worker tasks. No2024Senate invented.',
               '36county controls do not imply native completeness/current approval or accepted priority.']}
(D/'coordinator-primary-preflight.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'county_controls':len(rows),'state_controls':sums,'reported_total':sum(sums),'truncated_capture_exact_prefix':True}))
