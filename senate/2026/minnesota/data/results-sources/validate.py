#!/usr/bin/env python3
"""Network-free QA against complete retained primary bytes and frozen PATH authority."""
import pathlib,json,gzip,hashlib,csv,collections,re,io,zipfile,xml.etree.ElementTree as E,sys
ROOT=pathlib.Path(__file__).resolve().parent;STATE=ROOT.parent.parent;checks={}
def ok(k,v):
 assert v,k
 checks[k]='pass'
def j(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
a=j(STATE/'data/coordinator-priority-acceptance.json');cb=(STATE/'data/turnout/priority-set.json').read_bytes();contract=json.loads(cb)
ok('frozen_contract_path_authority',sha(cb)==a['contract_sha256']=='b60b0bc4fed0c0b8618b6f851cc8f25d3c963bbd3ea12debecc5995dff54ceb1' and len(cb)==9885383)
for ref in j(ROOT/'input-pins.json'):
 p=STATE/ref['path'];b=p.read_bytes();ok('input:'+ref['path'],len(b)==ref['stored_bytes'] and sha(b)==ref['stored_sha256'])
 if 'raw_sha256' in ref:ok('decompressed:'+ref['path'],sha(gzip.decompress(b))==ref['raw_sha256'])
ctx=[json.loads(x) for x in gzip.decompress((ROOT/'county-native-contexts.jsonl.gz').read_bytes()).decode().splitlines()]
ok('every_complete_county_object_equal',ctx==contract['county_order'] and len(ctx)==87)
ok('all_native_constituents_12316',sum(len(c['native_constituents'][y]) for c in ctx for y in ['2024','2022','2020'])==12316)
ok('all24_ordered_priorities', [c['key'] for c in ctx if c['in_priority']]==a['ordered_priority_keys'] and sum(len(c['native_constituents']['2024']) for c in ctx if c['in_priority'])==2067)
ok('historical_vote_controls',sum(c['votes'] for c in ctx)==3189323 and sum(c['votes'] for c in ctx[:15])==2308744 and sum(c['votes'] for c in ctx[:23])==2543408 and sum(c['votes'] for c in ctx[:24])==2567977 and ctx[23]['name']=='Beltrami' and ctx[23]['votes']==24569 and sum(c['votes'] for c in ctx[24:])==621346)
# Independently compare every retained OOXML cell to original sheet rows; no extraction module imported.
N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};candidatepositions=0;primary_native={}
for year,expected in [(2024,4103),(2022,4103),(2020,4110)]:
 z=zipfile.ZipFile(io.BytesIO(gzip.decompress((STATE/f'data/news/sos-{year}-precinct-original.html.gz').read_bytes())));ss=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',N)];original=E.fromstring(z.read('xl/worksheets/sheet2.xml'));source_rows={x.attrib['r']:x for x in original.findall('.//s:sheetData/s:row',N)}
 rows=[json.loads(x) for x in gzip.decompress((ROOT/f'native-{year}.jsonl.gz').read_bytes()).decode().splitlines()];ok(f'all_native_rows_{year}',len(rows)==expected)
 primary_native[year]={}
 for row in rows:
  orig=list(source_rows[row['row']]);out=row['all_cells'];assert len(orig)==len(out)
  for cell,kept in zip(orig,out):
   v=cell.find('s:v',N);raw=v.text if v is not None else None;val=ss[int(raw)] if cell.attrib.get('t')=='s' and raw is not None else ''.join(cell.find('s:is',N).itertext()) if cell.attrib.get('t')=='inlineStr' else raw
   assert kept['address']==cell.attrib['r'] and kept['attributes']==dict(cell.attrib) and kept['raw_value']==raw and kept['value']==val
  values={row['headers_by_column'][re.sub(r'\d','',c.attrib['r'])]: ss[int(c.find('s:v',N).text)] if c.attrib.get('t')=='s' else c.find('s:v',N).text if c.find('s:v',N) is not None else None for c in orig if row['headers_by_column'][re.sub(r'\d','',c.attrib['r'])]!='TABMODEL'}
  key=(int(values['COUNTYCODE']),values['PCTCODE']);assert key not in primary_native[year];primary_native[year][key]=values
  candidatepositions+=sum(1 for col,name in row['headers_by_column'].items() if name.startswith('MNGOV' if year==2022 else 'USSEN') and not name.endswith('TOTAL'))
 ok(f'every_original_cell_{year}',True)
 if year==2020:ok('duplicate2020TABMODEL_G_R_survive',rows[0]['headers_by_column']['G']=='TABMODEL' and rows[0]['headers_by_column']['R']=='TABMODEL' and any(x['address'].startswith('R') and x['value'] is None for x in rows[0]['all_cells']))
ok('native_candidate_positions_69786',candidatepositions==69786)
# Retained raw source bodies, redirects and original byte lengths.
metas=j(ROOT/'acquisition.json');ok('acquisition_ledger_exact',len(metas)==len(list((ROOT/'raw').glob('*.meta.json'))))
for rec in metas:
 if 'body' not in rec:assert 'error'in rec;continue
 packed=(ROOT/rec['body']).read_bytes();b=gzip.decompress(packed);assert len(b)==rec['raw_bytes'] and sha(b)==rec['raw_sha256'];assert len(packed)==rec['stored_bytes'] and sha(packed)==rec['stored_sha256'];assert rec['requested_url'] and rec['retrieved_utc'] and 'redirects'in rec
ok('all_acquired_complete_entity_hashes',True)
for p in ROOT.glob('export-*.rows.jsonl.gz'):
 id=p.name.removesuffix('.rows.jsonl.gz');source=gzip.decompress((ROOT/'raw'/f'{id}.body.gz').read_bytes());kept=[json.loads(x) for x in gzip.decompress(p.read_bytes()).decode().splitlines()];lines=source.splitlines(keepends=True);assert len(lines)==len(kept);off=0
 for i,(b,row) in enumerate(zip(lines,kept),1):assert row['line']==i and row['byte_start']==off and row['byte_end']==off+len(b) and row['fields']==b.rstrip(b'\r\n').decode('cp1252').split(';');off+=len(b)
ok('every_export_line_byte_field_position',True)
# Recompute native/county/state controls directly from complete original entities,
# independent of saved reconciliation verdicts and without importing build code.
def original_export(year,kind):
 return [b.rstrip(b'\r\n').decode('cp1252').split(';') for b in gzip.decompress((ROOT/'raw'/f'export-{year}-{kind}.body.gz').read_bytes()).splitlines(keepends=True)]
independent_positions=0;independent_method_differences=[]
for year in [2024,2022,2020]:
 source=primary_native[year];state=original_export(year,'state');pct=original_export(year,'precinct');prefix='MNGOV'if year==2022 else 'USSEN'
 mapping={x[7]:prefix+x[10]for x in state};by_county=collections.Counter();by_state=collections.Counter()
 for x in pct:
  key=(int(x[1]),x[2]);field=mapping[x[7]];vote=int(x[13]);assert vote==int(source[key][field]),(year,key,x[7]);by_county[(key[0],x[7])]+=vote;by_state[x[7]]+=vote;independent_positions+=1
 assert len(pct)==len(source)*len(state)
 for county in {x[0]for x in source}:
  for name,field in mapping.items():assert by_county[(county,name)]==sum(int(v[field])for k,v in source.items()if k[0]==county)
 for x in state:assert int(x[13])==by_state[x[7]]==sum(int(v[mapping[x[7]]])for v in source.values())
 if year!=2022:
  county=original_export(year,'county');assert len(county)==87*len(state)
  for x in county:assert int(x[13])==by_county[(int(x[1]),x[7])]
 for line,x in enumerate(original_export(year,'statistics'),1):
  key=(int(x[1]),x[2])
  for fieldindex,field in [(5,'REG7AM'),(6,'EDR'),(7,'SIGNATURES'),(8,'AB_MB'),(9,'FEDONLYAB'),(10,'PRESONLYAB'),(11,'TOTVOTING')]:
   if year==2022 and field=='PRESONLYAB':assert field not in source[key];continue
   if source[key][field]!=x[fieldindex]:independent_method_differences.append((year,line,key,fieldindex,field,x[fieldindex],source[key][field]))
 ok(f'independent_raw_native_county_state_methods_{year}',True)
ok('independently_recomputed69786_positions',independent_positions==69786)
r=j(ROOT/'export-reconciliation.json');ok('2024_all5candidate_controls',all(x['equal']for x in r['candidate_county_state']) and r['native_candidate_comparisons']==20515)
ok('independent_all56_method_difference_positions',independent_method_differences==[(2024,x['line'],tuple(x['key']),x['field_index'],x['field'],x['text'],x['workbook'])for x in r['differences']])
ok('Kittson56exact_unallocated_differences',len(r['differences'])==56 and set(x['key'][0]for x in r['differences'])=={35} and collections.Counter(x['field']for x in r['differences'])=={'AB_MB':27,'TOTVOTING':27,'SIGNATURES':2} and sum(int(x['text'])-int(x['workbook'])for x in r['differences']if x['field']=='TOTVOTING')==-172)
h=j(ROOT/'additional-historical-reconciliation.json');ok('2020_2022_all_candidate_and_method_controls',all(not x['differences'] and not x['method_differences'] and all(c['equal']for c in x['candidate_state_controls'])for x in h.values()) and h['2022']['native_candidate_positions']==28721 and h['2020']['native_candidate_positions']==20550)
p=j(ROOT/'canvass-2020-positions.json');ok('2020main435_named522_32nonadditive',sum(x['scope']=='main_report'for x in p)==435 and sum(x['scope']=='separate_named_writein_appendix'for x in p)==522 and sum(x['votes']for x in p if x['scope']=='separate_named_writein_appendix')==32 and all(x['equal_to_workbook']for x in p if x['scope']=='main_report'))
text=(ROOT/'pdf-text/canvass-2020.txt').read_text()
for x in p:assert int(text[x['global_text_character_start']:x['global_text_character_end']].replace(',',''))==x['votes']
ok('every_pdf_numeric_position',True)
hrs=j(ROOT/'hours-exceptions.json');ok('current_hours286_268general_18primaryonly',len(hrs)==286 and sum(x['general_opening_local']is not None for x in hrs)==268 and sum(x['scope']=='primary_only'for x in hrs)==18 and all(x['general_opening_local']is None for x in hrs if x['scope']=='primary_only'))
setup=j(ROOT/'general201-setup-inspection.json');parent=gzip.decompress((STATE/'data/news/sos-november-observed201.html.gz').read_bytes()).decode();ok('201explicit_TEST_rejected_despite_arithmetic',not setup['admitted_to_current_counts'] and not setup['expected_actual_november_universe_approved'] and 'TEST RESULTS'in parent and setup['rows']['precincts']==4105 and setup['rows']['county']==435 and setup['rows']['precinct']==20525 and all(x['state']==x['county_sum']==x['precinct_sum']for x in setup['reconciliation']))
ok('201four_identity_sample_agreement',[(x['fields'][0],x['fields'][1],x['fields'][6])for x in setup['candidate_identity_rows']]==[('01021001','Marisa Simonetti','IND'),('01021102','Rebecca Whiting','LIB'),('01020403','Peggy Flanagan','DFL'),('01020304','Michele Tafoya','R')])
inv=j(ROOT/'authority-inventory.json');pri=j(ROOT/'priority-investigations.json');csvrows=list(csv.DictReader((STATE/'data/official-results-sources.csv').open()));ok('inventory87_csv87_individual24',len(inv)==87 and len(csvrows)==87 and len(pri)==24 and [x['key']for x in pri]==a['ordered_priority_keys'] and [x['county_fips']for x in inv]==[x['county_fips']for x in csvrows])
ok('all87individual_root_requests_and_directory_spans',all(any(e['id'].endswith('-root')for e in x['evidence'])and x['directory']['directory_context'] for x in inv))
for x in pri:assert x['finding'] and x['gap'] and x['source_records'] and len(x['historical_2024_export_positions']['lines'])==5*x['native_counts']['2024']
ok('24substantive_records_native_controls',True)
# Current legal claims are anchored in complete captured body, not remembered old rule.
law=(ROOT/'raw/law-204C.33.text.txt').read_text();ok('operative_state16thday_county3to8', 'on the 16th day following' in law and 'third and eighth days' in law)
ok('operative_writein19thday', '19th day before the general election'in (ROOT/'raw/law-204B.09.text.txt').read_text())
ok('USPS_full_primary_chain',all((ROOT/'raw'/f'{x}.meta.json').exists()for x in ['scotus-docket','scotus-primary-orders-appendix','scotus-linked-50','ag-usps-original-95']) and 'Document 285' in (ROOT/'pdf-text/scotus-primary-orders-appendix.txt').read_text() and 'September 14, 2026' in (ROOT/'pdf-text/ag-usps-original-95.txt').read_text())
report=(STATE/'official-results.md').read_text();ok('report_exact24_headings',len(re.findall(r'^### \d+\.',report,re.M))==24)
for target in re.findall(r'\]\(([^)]+)\)',report):
 if re.match(r'https?://',target):continue
 assert (STATE/target.split('#')[0]).exists(),target
ok('report_relative_links',True)
from urllib.parse import unquote,urlsplit
for markdown in ROOT.rglob('*.md'):
 for target in re.findall(r'\]\(([^)]+)\)',markdown.read_text()):
  u=urlsplit(target)
  if not u.scheme and u.path:assert (markdown.parent/unquote(u.path)).exists(),(str(markdown.relative_to(ROOT)),target)
ok('nested_markdown_relative_links',True)
# All stored owned objects; manifest may not yet exist during --record first freeze.
owned=[STATE/'official-results.md',STATE/'data/official-results-sources.csv']+[p for p in ROOT.rglob('*')if p.is_file() and p.name!='asset-manifest.json']
ok('all_objects_strictly_under40million',all(p.stat().st_size<40000000 for p in owned))
ok('no_caches_dependencytrees',not any('__pycache__'in p.parts or 'node_modules'in p.parts or '.cache'in p.parts for p in owned))
if '--record'in sys.argv:
 (ROOT/'validation.json').write_text(json.dumps({'status':'pass','mode':'deterministic offline; no network; generated before manifest','checks':checks,'check_count':len(checks),'native_candidate_positions':69786,'county_count':87,'priority_count':24,'native_constituents':12316},indent=2)+'\n')
else:
 mf=j(ROOT/'asset-manifest.json');expected={str(p.relative_to(STATE))for p in owned};actual={x['path']for x in mf['assets']};ok('manifest_self_exclusion_only',expected==actual and mf['excluded_paths']==['data/results-sources/asset-manifest.json'])
 for x in mf['assets']:
  b=(STATE/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
 ok('every_owned_manifest_hash',True)
print(json.dumps({'status':'pass','checks':len(checks),'native_candidate_positions':69786,'native_constituents':12316,'authorities':87,'individual_priorities':24,'manifest_verified':'--record'not in sys.argv},sort_keys=True))
