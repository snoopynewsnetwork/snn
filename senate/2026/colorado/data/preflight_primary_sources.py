#!/usr/bin/env python3
"""Stream original OOXML, preserving million-row cached-error tail without fake units."""
from pathlib import Path
import collections,gzip,hashlib,io,json,zipfile,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;N=D/'news';NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def main():
 mf={a['id']:a for a in json.loads((N/'manifest.json').read_text())};a=mf['sos-2024-native-turnout'];stored=(N/a['asset']).read_bytes();raw=gzip.decompress(stored);assert hashlib.sha256(raw).hexdigest()==a['raw_sha256'] and hashlib.sha256(stored).hexdigest()==a['stored_sha256'];z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None;ss=[''.join(v.itertext()) for v in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)];records=[];other=[];tail=collections.Counter();tail_start=tail_end=None;county=collections.defaultdict(collections.Counter);missing=collections.defaultdict(collections.Counter);exceptions=[];imbalances=[]
 with z.open('xl/worksheets/sheet1.xml') as f:
  for event,row in E.iterparse(f,events=['end']):
   if row.tag!='{'+NS['s']+'}row':continue
   cells={}
   for c in row:
    v=c.find('s:v',NS);v=v.text if v is not None else None
    if v is not None:cells[''.join(v for v in c.attrib['r'] if v.isalpha())]={'type':c.get('t'),'value':ss[int(v)] if c.get('t')=='s' else v}
   number=int(row.attrib['r']);row.clear()
   if not cells:continue
   plain={k:v['value'] for k,v in cells.items()}
   if number==1:other.append({'row':number,'cells':cells});continue
   if 'A' in plain and 'B' in plain and plain['B'].isdigit():
    vals={k:int(plain[k]) if k in plain and plain[k].lstrip('-').isdigit() else None for k in 'CDEF'}
    for k,v in vals.items():
     if v is None:missing[plain['A']][k]+=1
     else:county[plain['A']][k]+=v
    if all(vals[k] is not None for k in 'CDE') and vals['C']+vals['D']!=vals['E']:imbalances.append({'row':number,'cells':cells})
    rec={'source_row':number,'county_literal':plain['A'],'precinct_literal':plain['B'],'cells':cells};records.append(rec)
    if vals['F'] is not None and vals['E'] is not None and vals['F']>vals['E']:exceptions.append(rec)
   elif set(plain)=={'G'}:
    tail[json.dumps(cells,sort_keys=True)]+=1;tail_start=number if tail_start is None else min(tail_start,number);tail_end=number if tail_end is None else max(tail_end,number)
   else:other.append({'row':number,'cells':cells})
 assert len(county)==64 and len(records)==3183
 result={'status':'original_turnout_preflight_priority_unaccepted','source':a,'native_records':len(records),'counties':len(county),'county_sums':county,'missing_numeric_fields_by_county':missing,'active_inactive_total_source_imbalances':imbalances,'state_known_numeric_sums':{k:sum(v[k] for v in county.values()) for k in 'CDEF'},'all_native_source_rows':records,'other_source_rows':other,'cached_tail':{'rows':sum(tail.values()),'minimum_row':tail_start,'maximum_row':tail_end,'raw_cell_patterns':dict(tail)},'ballots_above_total_registration':exceptions,'scope':['Precinct IDs are source strings, not FIPS/current reporting approval.','Original XLSX retains whole cached-error tail; only county+precinct rows are actual turnout records, no deletion of originalbytes.','Blank/missing numeric cells are unknown, not zeros; known sums do not certify fullstatecontrols.','Printed Montezuma relocation footnote is source evidence, not authority to reallocate votes or repair unit denominators.','2024 president,2020 same-ClassII Hickenlooper-Gardner,2022 other-ClassIII Bennet-ODea/midterm remain separate.','Need independently recovered candidate/native controls and exact priority; turnout numbers are not valid candidate votes.']};(D/'coordinator-primary-preflight.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['source','all_native_source_rows','county_sums','ballots_above_total_registration']},indent=2));print('ballots_above_registration_count',len(exceptions))
if __name__=='__main__':main()
