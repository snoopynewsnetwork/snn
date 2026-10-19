"""Read exact public OOXML exports; preserve contradictory publisher labels."""
from pathlib import Path
import collections,gzip,hashlib,io,json,posixpath,re,zipfile
import xml.etree.ElementTree as E

DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
HEADERS=['Kamala D. Harris and Tim Walz ','Chase Oliver and Mike ter Maat ',
         'Donald J. Trump and JD Vance ','Robert F. Kennedy, Jr. and Nicole Shanahan ']
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(DATA.parent)),'bytes':len(b),'sha256':sha(b)}
def book(source):
 b=(NEWS/source['asset']).read_bytes();raw=gzip.decompress(b)
 assert sha(b)==source['stored_sha256']and sha(raw)==source['raw_sha256']and raw.startswith(b'PK')
 z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip()is None
 strings=[''.join(si.itertext())for si in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
 relationships={r.get('Id'):r.get('Target')for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
 output=[]
 for s in E.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',NS):
  target=relationships[s.get(RID)];target=target.lstrip('/')if target.startswith('/')else posixpath.normpath('xl/'+target)
  root=E.fromstring(z.read(target));rows=[]
  for r in root.findall('m:sheetData/m:row',NS):
   cells=[]
   for c in r.findall('m:c',NS):
    v=c.find('m:v',NS);rawvalue=v.text if v is not None else None;value=rawvalue
    if c.get('t')=='s':value=strings[int(rawvalue)]
    elif c.get('t')=='inlineStr':value=''.join(c.find('m:is',NS).itertext())
    cells.append({'address':c.get('r'),'type':c.get('t'),'style':c.get('s'),
      'raw_v':rawvalue,'resolved_value':value,'complete_cell_XML':E.tostring(c,encoding='unicode')})
   rows.append({'source_row':int(r.get('r')),'attributes':r.attrib,'cells':cells})
  output.append({'name':s.get('name'),'sheet_attributes':s.attrib,'target_member':target,'rows':rows})
 return {'source_pin':source,'ZIP_members':[{'name':i.filename,'bytes':i.file_size,'CRC32':f'{i.CRC:08x}','sha256':sha(z.read(i.filename))}for i in z.infolist()],
         'sheets':output,'shared_strings':strings}
def vals(row):return {re.sub(r'\d+$','',c['address']):c['resolved_value']for c in row['cells']}
def main():
 m=json.loads((NEWS/'manifest.json').read_bytes());keys=['sos-2024-public-presidential-precinct-export-684','sos-2024-public-statewide-export-postback-684','sos-2024-public-aurora-export-postback-684']
 books={k:book(next(r for r in m if r['id']==k))for k in keys}
 nativebook=books[keys[0]];assert len(nativebook['sheets'])==66
 certified=json.loads((DATA/'coordinator-primary-preflight.json').read_bytes())['tables']['2024_President']
 expected=certified['rows'];county=[];units=[];columns=['C','D','E','F']
 for sheet in nativebook['sheets']:
  name=sheet['name'];assert name in expected
  rows={r['source_row']:r for r in sheet['rows']};header=vals(rows[7])
  assert vals(rows[1])['A']=='2024 Unofficial General Election Results'
  assert vals(rows[3])['A']=='Precincts 691 of 691 Reporting (Precincts Partially Reported: 0/691)'
  assert vals(rows[4])['A'].startswith('Downloaded at ')
  assert [header[c]for c in columns]==HEADERS and header['B']=='Precinct'
  totalrows=[r for r in sheet['rows']if vals(r).get('B')=='TOTALS'];assert len(totalrows)==1
  totalrow=totalrows[0];first=7;last=totalrow['source_row'];native=[r for r in sheet['rows']if first<r['source_row']<last]
  for r in native:
   v=vals(r);counts=[int(v[c])for c in columns]
   assert v['B']and all(c['type']=='n'for c in r['cells']if re.sub(r'\d+$','',c['address'])in columns)
   units.append({'source_id':keys[0],'raw_source_sha256':nativebook['source_pin']['raw_sha256'],
    'county_sheet_literal':name,'literal_native_label':v['B'],'sheet_member':sheet['target_member'],
    'source_row':r['source_row'],'candidate_column_addresses':[c+str(r['source_row'])for c in columns],
    'candidate_header_literals':HEADERS,'source_candidate_counts':counts,
    'native_numeric_ID':None,'candidate_method_ballot_registration_fields':None})
  footer=[int(vals(totalrow)[c])for c in columns]
  assert [sum(int(vals(r)[c])for r in native)for c in columns]==footer
  official=expected[name]['votes'];county.append({'county_sheet_literal':name,'source_native_rows':len(native),
   'source_TOTAL_row':totalrow['source_row'],'source_candidate_footer':footer,
   'certified_original_canvass_candidate_counts':official,'public_export_minus_certified':[a-b for a,b in zip(footer,official)],
   'literal_source_headings':[vals(r)for n,r in rows.items()if n<=7]})
 assert len({r['county_sheet_literal']for r in county})==66
 totals=[sum(c['source_candidate_footer'][j]for c in county)for j in range(4)]
 assert totals==[146811,2777,271938,7202]and sum(totals)==428728
 differences=[c for c in county if any(c['public_export_minus_certified'])]
 assert [sum(c['public_export_minus_certified'][j]for c in county)for j in range(4)]==[-48,-1,-143,-2]
 nativepath=NEWS/'extracts/2024-public-presidential-native-original-positions.jsonl.gz'
 nativepath.write_bytes(gzip.compress(b''.join((json.dumps(u,separators=(',',':'))+'\n').encode()for u in units),mtime=0))
 allpath=NEWS/'extracts/2024-public-exports-complete-OOXML-rows.json.gz'
 allpath.write_bytes(gzip.compress(json.dumps(books,separators=(',',':')).encode(),mtime=0))
 misleading=[]
 for key in keys[1:]:
  s=next(s for s in books[key]['sheets']if s['name'].startswith('12665'))
  h=vals(next(r for r in s['rows']if r['source_row']==7))
  if [h[c]for c in columns]==HEADERS:continue
  assert h['C']==HEADERS[0]and h['D']==HEADERS[2]and h['E']=='Donald J. Trump and JD Vance 1'and h['F']==HEADERS[3]
  misleading.append({'source_id':key,'worksheet_name':s['name'],'source_header_row':7,
    'literal_header_cells':h,'candidate_header_conflict':'D7 literally namesTrump and E7Trump1, omittingOliver; correct native export namesOliver atD7 andTrump atE7. No silent relabel or candidate mapping from numeric resemblance.',
    'complete_header_XML':[c['complete_cell_XML']for c in next(r for r in s['rows']if r['source_row']==7)['cells']]})
 output={'status':'pass_original_public_native_export_arithmetic_with_retained_canvass_and_header_conflicts',
  'native_source':nativebook['source_pin'],'workbook_county_sheets':66,'retained_source_native_rows':len(units),
  'presidential_candidate_header_literals':HEADERS,'public_source_candidate_totals':totals,'public_source_named_total':sum(totals),
  'source_status_label_literal':'2024 Unofficial General Election Results',
  'source_counter_literal':'Precincts 691 of 691 Reporting (Precincts Partially Reported: 0/691)',
  'download_generation_clock_is_source_update_clock':False,
  'certified_candidate_controls':certified['controls'],'certified_named_total':428922,
  'public_minus_certified':[-48,-1,-143,-2],'public_named_difference':-194,
  'county_source_controls':county,'counties_with_actual_source_differences':differences,
  'separate_workbook_header_conflicts':misleading,'complete_original_OOXML_derivative':pin(allpath),
  'native_original_positions':pin(nativepath),
  'qualification':'Exact observed public PrecinctLevel export for historical election684 supplies66 correctly named county sheets and691 displayed-reporting native rows. All native candidate sums close their source county TOTALs.691/691 reporting and newly generated download clock do not mean certified final votes: totals are194 below retained signed canvass, with source/county candidate differences preserved unallocated. Separate all-race exports retain each literal candidate header; the statewide export has a documented conflict, while Aurora headers agree the correctly labelled native view. No automatic repair or mapping from values is adopted. Original files, complete OOXML/cell types/addresses/XML, ZIP CRCs/member hashes and request/form chains remain. Labels, counts and source rows do not approve physical precincts, voting-method IDs, historical/current joins or exact priority. This is coordinator preparation, not independent question-worker extraction or accepted dispatch.',
  'formal_dispatch_accepted':False,'current_geography_approved':False}
 assert len(units)==691
 target=DATA/'coordinator-2024-public-native-export-preflight.json';target.write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'status':output['status'],'counties':66,'native_rows':len(units),'source_votes':totals,'source_difference':-194,
  'county_differences':[(c['county_sheet_literal'],c['public_export_minus_certified'])for c in differences],'output_pin':pin(target)}))
if __name__=='__main__':main()
