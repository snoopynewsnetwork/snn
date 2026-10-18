#!/usr/bin/env python3
"""Independently parse shared original EAC surveys and DOS registration workbooks."""
import csv,gzip,io,json,re,subprocess,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from parse_sources import D,sha,writejson,csvwrite,Tables
from build import norm,readcsv
P=D.parent/'turnout';NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def original(sid):
 r=json.loads((P/'source'/f'{sid}.receipt.json').read_text());path=P/r['stored_path'];stored=path.read_bytes();raw=gzip.decompress(stored);assert r['status']==200 and sha(raw)==r['raw_sha256'] and sha(stored)==r['stored_sha256'];return raw,{**r,'stored_path':str(path.relative_to(D.parent.parent)),'receipt_path':str((P/'source'/f'{sid}.receipt.json').relative_to(D.parent.parent))}
def workbook(raw):
 z=zipfile.ZipFile(io.BytesIO(raw));strings=[]
 if 'xl/sharedStrings.xml' in z.namelist():
  for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS):strings.append(''.join(t.text or '' for t in si.findall('.//s:t',NS)))
 out=[]
 for f in z.namelist():
  if not re.fullmatch(r'xl/worksheets/sheet\d+\.xml',f):continue
  for row in ET.fromstring(z.read(f)).findall('.//s:sheetData/s:row',NS):
   cells={}
   for c in row.findall('s:c',NS):
    v=c.find('s:v',NS);v=v.text if v is not None else ''
    if c.get('t')=='s':v=strings[int(v)] if v else ''
    elif c.get('t')=='inlineStr':v=''.join(t.text or '' for t in c.findall('.//s:t',NS))
    cells[c.get('r')]=v
   out.append({'sheet':f,'row':int(row.get('r')),'cells':cells})
 return out

def main():
 refs=[];eavs=[];book=[];codebook=[];b=readcsv(D.parent/'county-baselines.csv');fips={norm(r['county']):r['county_fips'] for r in b};native=readcsv(D/'native-units.csv.gz');summary=[]
 for y in [2024,2022]:
  sid=f'eavs-{y}';raw,ref=original(sid);refs.append(ref);z=zipfile.ZipFile(io.BytesIO(raw));member=z.namelist()[0];rdr=csv.DictReader(io.TextIOWrapper(z.open(member),encoding='utf-8-sig'));yearrows=[]
  for i,r in enumerate(rdr,2):
   if r['State_Abbr']!='FL':continue
   fp=r['FIPSCode'][:5];assert fp==fips[norm(r['Jurisdiction_Name'])];fields={k:v for k,v in r.items() if any(k.startswith(prefix) for prefix in ['A1','B18','C1','C8','E1','F1','F2'])}
   # This prefix set preserves all turnout/method/registration controls and their comments.
   a={'year':str(y),'county_fips':fp,'county':r['Jurisdiction_Name'],'source_id':sid,'source_member':member,'source_csv_row_1based':i,'fields':fields};eavs.append(a);yearrows.append(a)
  assert len(yearrows)==67
  for sid in [f'eavs-{y}-codebook']:
   raw,ref=original(sid);refs.append(ref)
   for row in workbook(raw):
    values=list(row['cells'].values())
    if any(re.fullmatch(r'(A1|B18|C1|C8|E1|F1|F2)[A-Za-z0-9_]*',v) for v in values):codebook.append({'source_id':sid,**row})
  sid=f'bookclosing-{y}';raw,ref=original(sid);refs.append(ref);ws=workbook(raw);header_rows=[r for r in ws if any(v.strip()=='County Name' for v in r['cells'].values())];assert len(header_rows)==1
  h=header_rows[0];labels={re.sub(r'\d','',c):v.strip() for c,v in h['cells'].items()};found=[]
  for row in ws:
   name=row['cells'].get(f"A{row['row']}",'');nm=norm(name)
   if nm not in fips:continue
   rec={'year':str(y),'county_fips':fips[nm],'source_id':sid,**row,'labels':{labels.get(re.sub(r'\d','',c),re.sub(r'\d','',c)):v for c,v in row['cells'].items()}};found.append(rec);book.append(rec)
  assert len(found)==67
  totals={k:sum(int(r['fields'][k]) for r in yearrows if re.fullmatch(r'\d+',r['fields'].get(k,''))) for k in ['A1a','A1b','A1c','F1a','F1b','F1c','F1d','F1e','F1f']}
  totals['F1a_counties_nonpositive_or_unknown']=sum(not re.fullmatch(r'\d+',r['fields'].get('F1a','')) for r in yearrows)
  summary.append({'year':y,'eavs_counties':len(yearrows),'bookclosing_counties':len(found),'eavs_survey_controls':totals,'bookclosing_total':sum(int(next(v for k,v in r['labels'].items() if k.lower()=='total')) for r in found),'bookclosing_status':'active registered by party, 29 days before general election; not EAVS election eligibility or current2026 registration'})
 for sid in ['eavs-2024-instrument','bookclosing-index','bookclosing-regular','dos-2024-zip-direct','dos-2022-zip-direct','provisional-law','canvass-law','gulf-election-day']:
  raw,ref=original(sid);refs.append(ref)
 for p in sorted((P/'source').glob('supervisor-*.receipt.json')):
  raw,ref=original(p.name.removesuffix('.receipt.json'));refs.append(ref)
  code=p.name.split('-')[1].split('.')[0];parser=Tables();parser.feed(raw.decode('utf-8',errors='strict'));links=[a['href'] for a in parser.links if a.get('href','').lower().startswith(('http://','https://'))]
  # Preserve all published links; no assumption that any is a result feed.
  writejson(D/'source'/f'authority-{code}-links.json',{'county_code':code,'source_receipt':ref['receipt_path'],'source_raw_sha256':ref['raw_sha256'],'links':links})
 writejson(D/'source/shared-original-references.json',refs);writejson(D/'source/eavs-codebook-controls.json',codebook);writejson(D/'eavs-controls.json',eavs);writejson(D/'bookclosing-controls.json',book);writejson(D/'turnout-registration-summary.json',summary)
 # County/native registration comparison: a diagnostic, never silently chosen denominator.
 comps=[]
 for r in b:
  if r['contest']!='senate':continue
  y=r['year'];fp=r['county_fips'];er=next(a for a in eavs if a['year']==y and a['county_fips']==fp);br=next(a for a in book if a['year']==y and a['county_fips']==fp);us=[u for u in native if u['year']==y and u['contest']=='senate' and u['county_code']==r['county_code']];contexts=[json.loads(u['registration_contexts']) for u in us];assert all(len(c)==1 for c in contexts);reg=sum(int(c[0][0]) for c in contexts);mark=sum(int(u['raw_mark_total'])+int(u['overvotes'])+int(u['undervotes']) for u in us)
  comps.append({'year':y,'county_fips':fp,'county':r['county'],'official_senate_valid_votes':r['all_candidate_votes'],'compiled_senate_all_marks_plus_under_over':mark,'EAVS_F1a_counted_participants':er['fields']['F1a'],'EAVS_registered_eligible_A1a':er['fields']['A1a'],'EAVS_active_A1b':er['fields']['A1b'],'EAVS_inactive_A1c':er['fields']['A1c'],'DOS_bookclosing_active_total':next(v for k,v in br['labels'].items() if k.lower()=='total'),'compiled_native_registration_sum_once_per_context':reg,'compiled_registration_minus_bookclosing':reg-int(next(v for k,v in br['labels'].items() if k.lower()=='total')),'compiled_marks_minus_EAVS_F1a':mark-int(er['fields']['F1a']),'scope_note':'EAVS F1a participants with counted ballot; DOS valid contest votes; compiled generic marks and under/over; registration universes/source dates differ'})
 csvwrite(D/'turnout-registration-controls.csv',comps);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
