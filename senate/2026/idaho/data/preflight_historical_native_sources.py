"""Bounded Idaho original2020/2022 OOXML source preparation, not priority approval."""
from pathlib import Path
import collections,gzip,hashlib,io,json,posixpath,re,zipfile
import xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;N=D/'news';X=N/'extracts'
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';NS={'s':S}
def sha(b):return hashlib.sha256(b).hexdigest()
def serial(obj):return (json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n').encode()
def workbook(raw):
 z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip()is None
 ss=[''.join(t.text or ''for t in n.iter('{'+S+'}t'))for n in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]if'xl/sharedStrings.xml'in z.namelist()else[]
 rel={r.attrib['Id']:r.attrib['Target']for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
 sheets=[]
 for sh in E.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS):
  t=rel[sh.attrib['{'+R+'}id']];path=t.lstrip('/')if t.startswith('/')else posixpath.normpath(posixpath.join('xl',t));rows=[]
  for row in E.fromstring(z.read(path)).findall('s:sheetData/s:row',NS):
   cells={}
   for c in row:
    col=re.sub(r'\d','',c.attrib['r']);v=c.find('s:v',NS);value=None if v is None else v.text
    if c.get('t')=='s'and value is not None:value=ss[int(value)]
    elif c.get('t')=='inlineStr':value=''.join(t.text or ''for t in c.iter('{'+S+'}t'))
    cells[col]=dict(address=c.attrib['r'],type=c.get('t'),style=c.get('s'),raw_v=None if v is None else v.text,resolved=value,original_cell_XML=E.tostring(c,encoding='unicode'))
   rows.append(dict(source_row=int(row.attrib['r']),row_attributes=dict(row.attrib),cells=cells))
  sheets.append(dict(sheet_name=sh.attrib['name'],worksheet_member=path,rows=rows))
 return dict(raw_sha256=sha(raw),zip_member_pins=[dict(member=i.filename,bytes=i.file_size,CRC32=f'{i.CRC:08x}',sha256=sha(z.read(i)))for i in z.infolist()],sheets=sheets)
def val(row,col):return row['cells'].get(col,{}).get('resolved')
def main():
 X.mkdir(exist_ok=True);m={r['id']:r for r in json.loads((N/'manifest.json').read_bytes())};books={};originals=[]
 for year in [2020,2022]:
  sid=f'sos-{year}-general-canvass-zip';a=m[sid];stored=(N/a['asset']).read_bytes();raw=gzip.decompress(stored);assert sha(stored)==a['stored_sha256']and sha(raw)==a['raw_sha256'];z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip()is None
  originals.append(a)
  for member in z.namelist():
   if member.endswith('.xlsx')and('stwd'in member.lower()or'Statewide'in member):
    b=workbook(z.read(member));b.update(source_id=sid,archive_member=member);books[(year,'Precinct'if'_pct'in member or'Precinct'in member else'County')]=b
 assert len(books)==4
 specs=[dict(year=2020,contest='Senate_Class_II',sheet='Federal',columns=list('IJKL'),county_name_row=6,county_party_row=5,precinct_name_row=5,precinct_party_row=4),dict(year=2020,contest='President',sheet='Federal',columns=list('BCDEFGH'),county_name_row=6,county_party_row=5,precinct_name_row=5,precinct_party_row=4),dict(year=2022,contest='Senate_Class_III',sheet='US Sen',columns=list('BCDEF'),county_name_row=6,county_party_row=5,precinct_name_row=4,precinct_party_row=3),dict(year=2022,contest='Governor',sheet='Gov',columns=list('BCDEFG'),county_name_row=7,county_party_row=6,precinct_name_row=5,precinct_party_row=4)]
 findings=[];positions=[]
 for spec in specs:
  year=spec['year'];columns=spec['columns'];cb=books[(year,'County')];pb=books[(year,'Precinct')];cs=next(s for s in cb['sheets']if s['sheet_name']==spec['sheet']);ps=next(s for s in pb['sheets']if s['sheet_name']==spec['sheet']);cr={r['source_row']:r for r in cs['rows']};pr={r['source_row']:r for r in ps['rows']};names=[val(cr[spec['county_name_row']],c)for c in columns];parties=[val(cr[spec['county_party_row']],c)for c in columns]
  assert names==[val(pr[spec['precinct_name_row']],c).strip()for c in columns]
  assert parties==[val(pr[spec['precinct_party_row']],c)for c in columns]
  # The one trailing-space source candidate header is retained in the full raw
  # row derivative; whitespace-only label comparison is explicit here.
  controls={};state=None
  for r in cs['rows']:
   if r['source_row']<=spec['county_name_row']:continue
   label=val(r,'A')
   if label=='TOTAL':state=r;break
   if label is not None and all(re.fullmatch(r'\d+',str(val(r,c)))for c in columns):controls[label]=r
  assert len(controls)==44 and state is not None
  canonical={c.upper():c for c in controls};sums={c:[0]*len(columns)for c in controls};footers={};contexts=collections.Counter();roles=collections.Counter();parent=None;missing=[];native_keys=[];extra_controls=[]
  for r in ps['rows']:
   if r['source_row']<=spec['precinct_name_row']:continue
   label=val(r,'A');vv=[val(r,c)for c in columns]
   if label is None and all(v is None for v in vv):roles['blank_or_formatted_row']+=1;continue
   # Explicit within-document county-heading syntax only. No external label,
   # historical, method or physical-geography equivalence is claimed.
   heading=re.sub(r'(?: \(Continued\)|, cont\.)$','',label or '',flags=re.IGNORECASE)
   if heading in canonical and all(v is None for v in vv):parent=canonical[heading];roles['county_heading_or_continuation']+=1;continue
   if len(footers)==44:
    role='post_county_appendix_or_TOTAL_control';extra_controls.append(dict(source_row=r['source_row'],literal_label=label,contextual_last_county_heading=parent,values=vv))
    roles[role]+=1
    for j,c in enumerate(columns):positions.append(dict(year=year,contest=spec['contest'],source_id=pb['source_id'],archive_member=pb['archive_member'],workbook_sha256=pb['raw_sha256'],sheet_name=ps['sheet_name'],worksheet_member=ps['worksheet_member'],source_row=r['source_row'],cell_address=f'{c}{r["source_row"]}',parent_heading_literal=None,contextual_last_county_heading=parent,literal_unit_label=label,candidate=names[j],candidate_header_literal=val(pr[spec['precinct_name_row']],c),party=parties[j],party_header_literal=val(pr[spec['precinct_party_row']],c),raw_resolved_value=vv[j],role=role,original_cell=r['cells'].get(c)))
    continue
   if label=='TOTAL':roles['statewide_TOTAL_control']+=1;continue
   if label in ['Percentage','Plurality']:roles['noncount_control']+=1;continue
   if label=='CO. TOTAL':
    assert parent is not None
    assert all(re.fullmatch(r'\d+',str(v))for v in vv)
    if parent in footers:
     assert len(footers)==44
     role='additional_final_control_with_literal_CO_TOTAL_label';extra_controls.append(dict(source_row=r['source_row'],literal_label=label,contextual_last_county_heading=parent,values=vv))
    else:footers[parent]=r;role='overlapping_county_TOTAL_control'
   else:
    assert parent is not None and label is not None,(spec,r)
    role='source_native_precinct_or_central_literal_row';contexts[parent]+=1;native_keys.append([parent,label,r['source_row']])
    for j,v in enumerate(vv):
     if re.fullmatch(r'\d+',str(v)):sums[parent][j]+=int(v)
     else:assert v is None,(spec,r,v)
    if not all(re.fullmatch(r'\d+',str(v))for v in vv):missing.append(dict(parent=parent,source_row=r['source_row'],literal_label=label,raw_values=vv,missing_candidate_columns=[c for c,v in zip(columns,vv)if v is None]))
   roles[role]+=1
   for j,c in enumerate(columns):positions.append(dict(year=year,contest=spec['contest'],source_id=pb['source_id'],archive_member=pb['archive_member'],workbook_sha256=pb['raw_sha256'],sheet_name=ps['sheet_name'],worksheet_member=ps['worksheet_member'],source_row=r['source_row'],cell_address=f'{c}{r["source_row"]}',parent_heading_literal=parent,literal_unit_label=label,candidate=names[j],candidate_header_literal=val(pr[spec['precinct_name_row']],c),party=parties[j],party_header_literal=val(pr[spec['precinct_party_row']],c),raw_resolved_value=vv[j],role=role,original_cell=r['cells'].get(c)))
  assert len(footers)==len(contexts)==44
  differences=[]
  for county in controls:
   expected=[int(val(controls[county],c))for c in columns];footer=[int(val(footers[county],c))for c in columns]
   if sums[county]!=expected or footer!=expected:differences.append(dict(county=county,known_native_sums=sums[county],precinct_footer=footer,separate_county_control=expected,known_native_minus_county=[a-b for a,b in zip(sums[county],expected)]))
  statewide=[sum(int(val(r,c))for r in controls.values())for c in columns];printed=[int(val(state,c))for c in columns];assert statewide==printed
  for e in extra_controls:e['values_match_separate_statewide_controls']=[str(v)for v in statewide]==e['values']
  findings.append(dict(year=year,contest=spec['contest'],candidate_headers=names,party_headers=parties,statewide_candidate_counts=statewide,statewide_candidate_total=sum(statewide),county_count=44,native_source_rows=sum(contexts.values()),overlapping_county_footers=len(footers),role_counts=dict(roles),candidate_county_footer_comparisons=44*len(columns)*2,missing_native_count_rows=missing,missing_native_candidate_cells=sum(len(r['missing_candidate_columns'])for r in missing),known_sum_closure_does_not_fill_nulls=True,native_county_source_differences=differences,additional_final_literal_controls=extra_controls,native_context_counts=dict(contexts),native_source_positions=native_keys,qualification='Source-position contexts only; within-workbook literal county headings/continuations are parent scopes. OverlappingCO.TOTAL is a control, never another precinct. Blank/absent cells retain null; raw source candidate/party labels and trailing whitespace remain in original derivatives. Methods/native numericIDs/physical/current-year equivalence are not supplied or inferred.'))
 outpaths=[]
 for filename,body in [('historical-selected-workbooks-complete-OOXML-rows.json.gz',serial(list(books.values()))),('historical-selected-native-original-positions.jsonl.gz',b''.join(serial(p)for p in positions))]:
  p=X/filename;p.write_bytes(gzip.compress(body,mtime=0));outpaths.append(dict(path=str(p.relative_to(D)),raw_bytes=len(body),raw_sha256=sha(body),stored_bytes=p.stat().st_size,stored_sha256=sha(p.read_bytes())));assert p.stat().st_size<40000000
 report=dict(status='bounded_primary_original_historical_native_preparation_not_question_completion',source_originals=originals,workbook_count=4,selected_contests=findings,derivative_pins=outpaths,initial_unaccepted_parser_diagnostic='news/extracts/historical-native-parser-initial-unaccepted-diagnostic.json.gz',parser_scope_corrections=['2020 lowercase(continued) is a literal heading continuation, not a native row.','Rows after all44county footers are appendix/state controls with no county parent, including literal2022GovernorCO.TOTAL.','Known numeric cells sum independently; null candidate cells remain unknown rather than discarding the rest of their row or fillingzero.'],all_original_ZIP_CRCs_checked=True,current_geography_approved=False,priority_accepted=False,qualification='Preparation only, not an independently reconciled worker baseline or dispatch acceptance. Complete original ZIPs remain once in news assets. All four statewide workbooks retain complete worksheet rows/cells/types/styles/rawXML in a lossless derivative, including offices beyond the selected four. Selected source positions preserve native and overlapping footer roles. No allocation, missingzero fill, physical/name/cross-year join or2026 expected reporting universe is approved.')
 target=D/'coordinator-historical-native-preflight.json';target.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(report_path=str(target),report_sha256=sha(target.read_bytes()),derivatives=outpaths,contests=[{k:v for k,v in r.items()if k not in ['native_source_positions','native_context_counts']}for r in findings]),indent=2))
if __name__=='__main__':main()
