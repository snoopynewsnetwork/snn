#!/usr/bin/env python3
"""Archived original BIFF preflight; requires external xlrd 2.0.2, no dispatch approval."""
from pathlib import Path
import datetime, gzip, hashlib, json
import xlrd
ROOT=Path(__file__).resolve().parent;NEWS=ROOT/'news'
m=next(x for x in json.loads((NEWS/'manifest.json').read_text())if x['id']=='sos-2024-president-archived-original')
stored=(NEWS/m['asset']).read_bytes();body=gzip.decompress(stored)
assert hashlib.sha256(stored).hexdigest()==m['stored_sha256']
assert len(body)==m['bytes'] and hashlib.sha256(body).hexdigest()==m['raw_sha256']
assert body.startswith(bytes.fromhex('d0cf11e0a1b11ae1'))
book=xlrd.open_workbook(file_contents=body,formatting_info=True)
assert len(book.sheets())==11
native=[];rawrows=[];footers=[];county_controls={};blanks=[]
for si,s in enumerate(book.sheets()):
    for ri in range(s.nrows):
        values=s.row_values(ri);types=list(s.row_types(ri))
        rawrows.append({'sheet':s.name,'source_row':ri+1,'values':values,'BIFF_cell_types':types})
        if si==0:
            if 3<=ri<=12:county_controls[values[0].strip()]=values[1:8]
            if values[0]=='TOTALS':state=values[1:8]
            continue
        if ri<3 or not str(values[0]).strip():continue
        if values[0]=='TOTALS':
            footers.append({'sheet':s.name,'source_row':ri+1,'county_label':s.cell_value(2,0),'values':values[1:8]})
            continue
        native.append({'sheet':s.name,'source_row':ri+1,'county_label':s.cell_value(2,0),'native_label':values[0],
                       'values':values[1:8],'BIFF_cell_types':types[1:8]})
        if any(t in (xlrd.XL_CELL_EMPTY,xlrd.XL_CELL_BLANK) for t in types[1:8]):blanks.append({'sheet':s.name,'source_row':ri+1,'native_label':values[0],'blank_columns':[i+2 for i,t in enumerate(types[1:8])if t in (xlrd.XL_CELL_EMPTY,xlrd.XL_CELL_BLANK)]})
assert len(native)==320 and len(footers)==10 and len(county_controls)==10
for f in footers:
    subset=[r for r in native if r['sheet']==f['sheet']]
    numeric=[sum(r['values'][col]for r in subset if isinstance(r['values'][col],(int,float)))for col in range(7)]
    assert numeric==f['values']==county_controls[f['county_label'].removesuffix(' County')]
assert [sum(f['values'][col]for f in footers)for col in range(7)]==state==[418488,395523,4425,3680,4482,362,4073]
candidate_marks=int(sum(state[:4])+state[6]);contest_with_under_over=int(sum(state))
assert candidate_marks==826189 and contest_with_under_over==831033
clerk=(ROOT.parent.parent/'ohio/data/baselines/house-2024.txt').read_text().split('NEW HAMPSHIRE',1)[1].split('FOR UNITED STATES REPRESENTATIVE',1)[0]
import re
for label,value in [('Democratic',418488),('Republican',395523),('Libertarian',4425),('Green',3680),('Write-in',4073),('Under Votes',4482),('Over Votes',362)]:
    match=re.search(re.escape(label)+r'\s*\.+\s*([\d,]+)',clerk);assert match and int(match[1].replace(',',''))==value
(ROOT/'coordinator-2024-native-rows.json.gz').write_bytes(gzip.compress(json.dumps(native,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
(ROOT/'coordinator-2024-raw-rows.jsonl.gz').write_bytes(gzip.compress(b''.join((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode()for r in rawrows),mtime=0))
result={'status':'pass_primary_preflight_only','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':'Original archived SOS2024BIFF/statecounty/native positions only; no accepted priority/FIPS/current geographic crosswalk.',
        'source_id':m['id'],'original_sha256':m['raw_sha256'],'original_bytes':len(body),
        'archive_capture':'20241219142947','current_original_route':'403 retained separately',
        'worksheets':book.sheet_names(),'native_labeled_rows':len(native),'county_footer_controls':len(footers),
        'state_columns':['Harris/Walz','Trump/Vance','Oliver/terMaat','Stein/Ware','Undervotes','Overvotes','Write-Ins'],
        'state_controls':state,'named_plus_generic_marks':candidate_marks,'including_under_over':contest_with_under_over,
        'House_Clerk_control_fields_equal':7,'blank_cells_retained_by_row':blanks,
        'limits':['Blank BIFFcells remain literal unavailable/blank; numeric-sum reconciliation does not silently recode each one to zero.','Summarycountyrows and countyfooters overlap native town/cityward/territory rows; do not add them.','Generic4073is not a demonstrated valid-named write-in allocation.','Archivecapture/electionserialdate/retrieval and certificate date are different clocks.','All320native labels remain literal; no county replacement or approved physical current equivalence.']}
out=ROOT/'coordinator-primary-preflight.json'
if out.exists():
    previous=json.loads(out.read_text())
    if {k:v for k,v in previous.items()if k!='checked_utc'}=={k:v for k,v in result.items()if k!='checked_utc'}:result['checked_utc']=previous['checked_utc']
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='blank_cells_retained_by_row'},indent=2))
