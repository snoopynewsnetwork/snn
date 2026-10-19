"""Read only exact linked Douglas BIFF originals and compare source controls.

Requires external xlrd2.0.2; no workbook changes, normalization or allocation.
"""
from pathlib import Path
import gzip,hashlib,io,json,re,subprocess,sys,tempfile
sys.dont_write_bytecode=True
if Path('/tmp/snn-xls-reading-libs').exists():sys.path.insert(0,'/tmp/snn-xls-reading-libs')
import xlrd

DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
CONFIG=[
 (2024,'U.S. Senator - 2-Yr Term','2024_Senate_ClassII_two_year','For United States Senator Two-Year Term',
  ['Pete Ricketts','Preston Love Jr.','Write-ins'],['Pete Ricketts','Preston Love Jr.','Write-In Totals']),
 (2024,'U.S. Senator','2024_Senate_ClassI_six_year','For United States Senator',
  ['Deb Fischer','Dan Osborn','Write-ins'],['Deb Fischer','Dan Osborn','Write-In Totals']),
 (2024,'U.S. President',None,'For President And Vice President Of The United States',
  ['Donald J. Trump','Kamala D. Harris','Chase Oliver','Cornel West','Jill Stein','Write-ins'],
  ['Donald J. Trump','Kamala D. Harris','Chase Oliver','Cornel West','Jill Stein','Write-In Totals']),
 (2022,'Governor',None,'For Governor',
  ['Jim Pillen','Carol Blood','Scott Zimmerman','Write-Ins'],['Jim Pillen','Carol Blood','Scott Zimmerman','Write-In Totals']),
 (2020,'U.S. Senator','2020_Senate_ClassII_six_year','For United States Senator',
  ['Ben Sasse','Chris Janicek','Gene Siadek','Preston Love, Jr.','Other Write-Ins'],
  ['Ben Sasse','Chris Janicek','Gene Siadek','Preston Love, Jr.','Not Assigned'])]

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(DATA.parent)),'bytes':len(b),'sha256':sha(b)}
def original(row):
 p=NEWS/row['asset'];stored=p.read_bytes();raw=gzip.decompress(stored)
 assert sha(stored)==row['stored_sha256'] and sha(raw)==row['raw_sha256'] and len(raw)==row['bytes']
 assert row['status']==200
 return raw
def section(text,name):
 pattern=r'^\s*'+re.escape(name)+r'\s*$'
 m=re.search(pattern,text,re.M);assert m,name
 tail=text[m.end():]
 next_m=re.search(r'^\s*For (?:United|U\.|President|Governor|Secretary|State|Attorney|Auditor|Douglas|Public)',tail,re.M)
 return tail[:next_m.start()] if next_m else tail
def literal_value(block,name):
 lines=[l for l in block.splitlines() if re.match(r'^\s*'+re.escape(name)+r'(?:\s|\()',l)]
 assert len(lines)==1,(name,lines)
 m=re.search(r'(\d[\d,]*)\s*$',lines[0]);assert m,(name,lines)
 return int(m[1].replace(',','')),lines[0]

def main():
 manifest=json.loads((NEWS/'manifest.json').read_bytes());m={r['id']:r for r in manifest}
 preflight=json.loads((DATA/'coordinator-primary-preflight.json').read_bytes())
 books={};texts={};inputs=[];topology=[];raw_rows=[]
 for year in [2024,2022,2020]:
  source=m[f'county-douglas-{year}-native-xls'];raw=original(source)
  book=xlrd.open_workbook(file_contents=raw,formatting_info=True);books[year]=book
  inputs.append(source)
  topology.append({'year':year,'datemode':book.datemode,'sheets':[
    {'name':s.name,'rows':s.nrows,'columns':s.ncols}for s in book.sheets()],
    'instructions':[{'source_row':i+1,'values':book.sheet_by_name('Instructions').row_values(i),
                      'cell_types':list(book.sheet_by_name('Instructions').row_types(i))}
                     for i in range(book.sheet_by_name('Instructions').nrows)]})
  summary=m[f'county-douglas-{year}-summary-pdf'];pdf=original(summary);inputs.append(summary)
  with tempfile.NamedTemporaryFile(suffix='.pdf')as tmp:
   tmp.write(pdf);tmp.flush();texts[year]=subprocess.run(['pdftotext','-layout',tmp.name,'-'],check=True,capture_output=True).stdout.decode()
  (NEWS/'extracts'/f'county-douglas-{year}-summary.txt.gz').write_bytes(gzip.compress(texts[year].encode(),mtime=0))
 results=[];all_labels={};candidate_checks=[];numeric_footer_fields=0
 for year,name,state_key,pdf_section,fields,source_labels in CONFIG:
  s=books[year].sheet_by_name(name);header=s.row_values(1);types=list(s.row_types(1))
  footer_rows=[i for i in range(s.nrows)if s.cell_value(i,0)in['Totals','Total']]
  assert len(footer_rows)==1
  footer_row=footer_rows[0]
  assert all(all(v==''for v in s.row_values(i))for i in range(footer_row+1,s.nrows))
  native=list(range(2,footer_row));labels=[s.cell_value(i,0)for i in native]
  assert all(isinstance(x,str)and x for x in labels)and len(set(labels))==len(labels)
  all_labels[year,name]=labels
  footer=s.row_values(footer_row)
  countcols=[j for j,h in enumerate(header)if h and h not in ['Ward-Precinct','Ward - Precinct','% of Vote']]
  for col in countcols:
   assert all(s.cell_type(i,col)==xlrd.XL_CELL_NUMBER and int(s.cell_value(i,col))==s.cell_value(i,col)for i in native)
   assert sum(s.cell_value(i,col)for i in native)==footer[col],(year,name,header[col])
   numeric_footer_fields+=1
  cols=[]
  for field in fields:
   found=[j for j,h in enumerate(header)if h.startswith(field)]
   assert len(found)==1,(field,header);cols+=found
  total_col=header.index('Total Votes');over_col=header.index('Over Votes');under_col=header.index('Under Votes')
  for i in native:assert sum(s.cell_value(i,j)for j in cols)==s.cell_value(i,total_col),(year,name,i+1)
  block=section(texts[year],pdf_section)
  for col,label in zip(cols,source_labels):
   value,line=literal_value(block,label);assert value==footer[col]
   candidate_checks.append({'year':year,'sheet':name,'column':col+1,'workbook_literal_header':header[col],
                            'workbook_footer_value':int(footer[col]),'original_summary_line':line,'summary_value':value})
  state_comparison=None
  if state_key:
   expected=preflight['tables'][state_key]['county_rows']['Douglas']['votes']
   actual=[int(footer[j])for j in cols[:len(expected)]]
   assert actual==expected
   state_comparison={'table':state_key,'candidate_controls':actual,'named_or_writein_scope':preflight['tables'][state_key]['candidate_columns']}
  casts={labels[k]:int(sum(s.cell_value(i,j)for j in [total_col,over_col,under_col])) for k,i in enumerate(native)}
  ballot,line=literal_value(texts[year].split('\f')[0],'Ballots Cast - Total')
  reconstructed=sum(casts.values())
  results.append({'year':year,'sheet':name,'header':header,'header_cell_types':types,
   'native_rows':len(native),'full_literal_native_order':labels,'footer_source_row':footer_row+1,'footer':footer,
   'trailing_blank_formatted_rows':list(range(footer_row+2,s.nrows+1)),
   'candidate_column_ordinals':[j+1 for j in cols],'count_column_ordinals':[j+1 for j in countcols],
   'source_summary_count_fields':len(cols),'statewide_canvass_county_control_comparison':state_comparison,
   'sum_TotalVotes_plus_OverVotes_plus_UnderVotes':reconstructed,'separate_county_summary_ballots':ballot,
   'county_summary_ballot_literal':line,'arithmetic_difference_vs_summary_ballots':reconstructed-ballot,
   'native_reconstructed_contest_volume':casts})
  for i in range(s.nrows):raw_rows.append({'source_id':f'county-douglas-{year}-native-xls',
   'raw_source_sha256':m[f'county-douglas-{year}-native-xls']['raw_sha256'],'sheet':name,
   'source_row':i+1,'values':s.row_values(i),'cell_types':list(s.row_types(i))})
 assert all_labels[2024,'U.S. President']==all_labels[2024,'U.S. Senator']==all_labels[2024,'U.S. Senator - 2-Yr Term']
 casts={r['sheet']:r['native_reconstructed_contest_volume']for r in results if r['year']==2024}
 contrasts=[]
 for label in all_labels[2024,'U.S. President']:
  values={name:units[label]for name,units in casts.items()}
  if len(set(values.values()))>1:contrasts.append({'literal_native_label':label,'per_contest_source_arithmetic':values})
 assert len(contrasts)==1 and contrasts[0]['literal_native_label']=='03-02'
 derivative=DATA/'news/extracts/douglas-selected-native-original-rows.jsonl.gz'
 derivative.write_bytes(gzip.compress(b''.join((json.dumps(r,separators=(',',':'))+'\n').encode()for r in raw_rows),mtime=0))
 output={'status':'pass_bounded_Douglas_original_native_and_candidate_controls_with_source_volume_differences',
  'sources':inputs,'workbook_topology':topology,'selected_tables':results,'selected_raw_rows':pin(derivative),
  'native_contest_context_rows':sum(r['native_rows']for r in results),
  'distinct_source_native_labels_by_year':{'2024':len(all_labels[2024,'U.S. Senator - 2-Yr Term']),
    '2022':len(all_labels[2022,'Governor']),'2020':len(all_labels[2020,'U.S. Senator'])},
  'exact_numeric_native_to_footer_field_controls':numeric_footer_fields,
  'original_summary_candidate_field_comparisons':candidate_checks,'state_canvass_county_candidate_cells':10,
  'within2024_source_contest_volume_contrasts':contrasts,
  'qualification':'Coordinator preparation only; no state worker launched, exact statewide native coverage/order/80 scope accepted or current boundary identity approved. Selected full source rows/types remain intact, header/footer dates are source cells rather than inferred clocks. Douglas instructions explicitly combine early-voting and polling-place votes, so no candidate-by-method allocation is recovered from these sheets. Named versus other write-ins stay separate;2020 PDF parent Write-In Totals includes its named Love subset and is not additive with it. Computed candidate+generic+over+under differs from separate county ballot totals in Senate2024(-1),Governor2022(-4),Senate2020(-10), with2024 difference located at literal03-02. Cause/vintage/correction sequence remains unknown; no rescale or residual allocation.'}
 (DATA/'coordinator-douglas-native-preflight.json').write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'status':output['status'],'native_contexts':output['native_contest_context_rows'],
   'distinct_year_counts':output['distinct_source_native_labels_by_year'],'native_footer_controls':numeric_footer_fields,
   'local_PDF_candidate_controls':len(candidate_checks),'state_canvass_controls':10,
   'volume_differences':[(r['year'],r['sheet'],r['arithmetic_difference_vs_summary_ballots'])for r in results]},indent=2))
if __name__=='__main__':main()
