#!/usr/bin/env python3
"""Meaningful offline validation against complete primary originals. No network/Git.
Default writes validation and final exact owned manifest. --check verifies manifest.
"""
import collections,csv,gzip,hashlib,io,json,pathlib,re,sys,zipfile
from urllib.parse import quote,unquote,urlsplit
from bs4 import BeautifulSoup
from pypdf import PdfReader
ROOT=pathlib.Path(__file__).resolve().parents[2];OUT=ROOT/'data/results-sources';SRC=OUT/'source';EX=OUT/'extracts';MF=OUT/'asset-manifest.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(p):return json.loads(p.read_text())
def gz(p):return json.loads(gzip.decompress(p.read_bytes()))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def owned():return sorted([ROOT/'official-results.md',ROOT/'data/official-results-sources.csv']+[p for p in OUT.rglob('*') if p.is_file() and p!=MF])
def check_manifest():
 m=js(MF);files=owned();assert {str(p.relative_to(ROOT)) for p in files}=={x['path'] for x in m['assets']}
 for x in m['assets']:
  p=ROOT/x['path'];assert p.stat().st_size==x['bytes'] and sha(p.read_bytes())==x['sha256'],x['path'];assert x['bytes']<40000000
 assert m['self_excluded']=='data/results-sources/asset-manifest.json';return len(files)
if '--check' in sys.argv:
 print(json.dumps({'manifest':'pass','exact_assets':check_manifest()}));sys.exit()
checks={};contract_path=ROOT/'data/turnout/priority-set.json';raw=contract_path.read_bytes();assert len(raw)==23823926 and sha(raw)=='0c056e0ebfdb393d4fcb59676805122d8442f444200b9edaf7f4c979c5e9a173';c=json.loads(raw);fc=gz(OUT/'frozen-context.json.gz');assert fc['frozen_contract']==c;assert c['coordinator_accepted'] is False;assert c['coordinator_acceptance_path']=='data/coordinator-priority-acceptance.json';a=js(ROOT/c['coordinator_acceptance_path']);assert a['accepted'] and a['contract']['sha256']==sha(raw);checks['full_frozen_semantic_equality']=True
# Final first-pair individual pins, never mutable aggregate assumptions.
for pin in js(OUT/'first-pair-pins.json'):
 b=(ROOT/pin['path']).read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256'],pin['path']
checks['final_first_pair_pins']=len(js(OUT/'first-pair-pins.json'))
parents=c['all_unit_order'];assert len(parents)==67 and len({p['key'] for p in parents})==67;assert sum(p['votes'] for p in parents)==10757428;assert [p['key'] for p in parents[:22]]==c['ordered_priority_keys']==a['ordered_priority_keys'];assert sum(p['votes'] for p in parents[:15])==7373225;assert sum(p['votes'] for p in parents[:21])==8572752;assert sum(p['votes'] for p in parents[:22])==8734473;assert sum(p['votes'] for p in parents[22:])==2022955;assert 5*8572752<4*10757428<=5*8734473;assert (4*10757428+4)//5==8605943
checks['arithmetic']={'parents':67,'ordered_priority':22,'remainder':45,'denominator':10757428,'top15':7373225,'first21':8572752,'threshold':8605943,'crossing':parents[21],'priority_votes':8734473,'remainder_votes':2022955}
# Every full parent/native/global/admin/unavailable object survives. Order reconstructed exactly.
records=[json.loads(line) for line in gzip.decompress((OUT/'county-investigations.jsonl.gz').read_bytes()).decode().splitlines()];assert [r['frozen_parent'] for r in records]==parents;assert [r['frozen_primary_constituent_object'] for r in records]==c['native_constituents'];copied=sorted([u for r in records for u in r['full_historical_native_contexts_in_source_order']],key=lambda u:u['global_source_position_1based']);assert [u['global_source_position_1based'] for u in copied]==list(range(1,23533))
native=[json.loads(line) for line in gzip.decompress((ROOT/'data/turnout/extracts/native-units.jsonl.gz').read_bytes()).decode().splitlines()];assert [u['full_native_object'] for u in copied]==native;assert len({u['native_key'] for u in native})==23532;counts=collections.Counter(u['context'] for u in native);assert dict(counts)=={'2024_president':5712,'2024_senate':5710,'2022_senate':6013,'2020_president':6097};checks['full_native_semantic_equality']={'all_native_objects':23532,'context_counts':dict(counts),'primary_frozen_constituents':sum(r['frozen_primary_constituent_object']['constituent_count'] for r in records),'blank_ids':sum(not u['precinct_id_available'] for u in native),'label_method_hints_only':sum(u['source_label_method_hint_only'] for u in native)}
# Complete originals by immutable hash, ZIP CRCs and original19 width; selected raw positions/bytes/fields compared independently.
shared=js(ROOT/'data/turnout/source/shared-source-references.json');zips={};members={};allsource_rows=0;zipcontrols=[]
for sid,r in shared.items():
 if 'precinct' not in sid or 'schema' in sid:continue
 p=(ROOT/'data/turnout/source'/r['relative_path']).resolve();stored=p.read_bytes();assert sha(stored)==r['stored_sha256'];b=gzip.decompress(stored);assert sha(b)==r['raw_sha256'] and len(b)==r['original_bytes'];z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None;zips[sid]=z
 for m in z.infolist():
  mb=z.read(m);lines=mb.splitlines(keepends=True);members[(sid,m.filename)]=(mb,lines)
  for line in lines:assert len(line.decode('utf-8-sig').rstrip('\r\n').split('\t'))==19,(sid,m.filename)
  allsource_rows+=len(lines)
 zipcontrols.append({'source_id':sid,'raw_bytes':len(b),'raw_sha256':sha(b),'members':len(z.infolist()),'all_member_CRCs_pass':True})
rawrows={};fieldcomp=0;selected=0
for year in [2024,2022,2020]:
 with gzip.open(ROOT/f'data/turnout/extracts/native-source-rows-{year}.jsonl.gz','rt') as f:
  for line in f:
   r=json.loads(line);mb,lines=members[(r['source_id'],r['source_member'])];orig=lines[r['source_row_1based']-1];assert mb[r['source_byte_offset']:r['source_byte_offset']+r['source_line_bytes']]==orig;assert sha(orig)==r['source_line_sha256'];fields=orig.decode(r['source_encoding']).rstrip('\r\n').split('\t');assert fields==r['fields'];assert not r['recount_overlap_excluded'];nk='/'.join([r['context'],fields[0],fields[2],quote(fields[5],safe=''),quote(fields[6],safe='')]);assert nk==r['native_key'];key=(r['source_id'],r['source_member'],r['source_row_1based']);assert key not in rawrows;rawrows[key]=fields;fieldcomp+=19;selected+=1
assert allsource_rows==1707538 and selected==211874 and fieldcomp==4025606
for u in native:
 for row in u['candidate_category_rows']:
  f=rawrows[(u['source_id'],u['source_member'],row['source_row_1based'])];assert [row[k] for k in ['candidate_label','party','fvrs_id','doe_candidate_id']]==[f[14],f[15],f[16],f[17]];assert row['votes']==int(f[18]);assert [u[k] for k in ['county_code','election_number','precinct_id','polling_location','contest_code']]==[f[0],f[2],f[5],f[6],f[13]]
ni={u['native_key']:u for u in native}
for rec in records:
 for u in rec['frozen_primary_constituent_object']['units']:
  n=ni[u['native_key']]
  for key in ['source_id','source_member','election_number','precinct_id','polling_location','contest_code','method_scope','native_type','precinct_id_available','source_label_method_hint_only','administrative_case']:assert u[key]==n[key]
  assert u['source_rows_1based']==[r['source_row_1based'] for r in n['candidate_category_rows']]
checks['original_native_validation']={'ZIPs':zipcontrols,'all_source_rows_original19':allsource_rows,'selected_original_positions':selected,'original_field_comparisons':fieldcomp,'native_candidate_vectors_checked':23532}
# All four legal valid/named county tables parsed from raw original HTML, not a derivative.
original_tables={};cells=0
for ctx,co in c['source_objects']['primary_county_tables'].items():
 r=js(ROOT/'data/turnout'/co['receipt']);b=gzip.decompress((ROOT/'data/turnout'/r['stored_path']).read_bytes());assert sha(b)==co['raw_sha256'];sp=BeautifulSoup(b,'html.parser');table=sp.find('td',class_='County').find_parent('table');trs=table.find_all('tr');candidate_headers=[];county={};totals=None
 for i,tr in enumerate(trs):
  arr=[td.get_text(' ',strip=True) for td in tr.find_all(['th','td'],recursive=False)]
  if arr and arr[0]=='County':
   candidate_headers=[' '.join(v.split()) for v in arr[1:]];assert candidate_headers==co['candidate_universe'];continue
  if not arr:continue
  name=arr[0];vals=arr[1:]
  if name.casefold() in {p['name'].casefold() for p in parents}:
   assert len(vals)==len(co['candidate_universe']);county[name]={cand:int(v.replace(',','')) for cand,v in zip(co['candidate_universe'],vals)};cells+=len(vals)
  elif 'total' in name.casefold() and vals and all(re.fullmatch(r'[\d,]+',v) for v in vals):totals=list(map(lambda v:int(v.replace(',','')),vals))
 assert len(county)==67,(ctx,len(county));sums={cand:sum(v[cand] for v in county.values()) for cand in co['candidate_universe']};assert sums==co['statewide_controls'];assert totals==list(sums.values());original_tables[ctx]=county
assert cells==2479
for p in parents:
 vals=next(v for k,v in original_tables['2024_senate'].items() if k.casefold()==p['name'].casefold());assert sum(vals.values())==p['votes']
checks['primary_original_HTML']={'contexts':4,'county_vectors':268,'candidate_cells':cells,'all_candidate_statewide_controls_match':True}
# Every owned response entity and error retained and hash-checked. No success inferred from HTTP status alone.
receipts=[js(p) for p in sorted(SRC.glob('*.receipt.json'))];seen=set()
for r in receipts:
 assert r['id'] not in seen;seen.add(r['id'])
 if r.get('raw_sha256'):
  p=ROOT/r['body_path'];sb=p.read_bytes();b=gzip.decompress(sb) if p.suffix=='.gz' else sb;assert sha(sb)==r['stored_sha256'];assert sha(b)==r['raw_sha256'] and len(b)==r['raw_bytes'];assert r['complete']
checks['response_hashes']={'complete_entity_receipts':sum(bool(r.get('raw_sha256')) for r in receipts),'transport_error_receipts':sum(not r.get('raw_sha256') for r in receipts),'status_counts':dict(collections.Counter(str(r.get('status')) for r in receipts))}
# Independent county vendor controls, all choices preserved; compare ONLY compatible named choices.
vr=gz(EX/'vr-complete-tables.json.gz');vendor_controls=[];method_checks=0
for v in vr:
 if '11/5/2024' not in (v['date_heading'] or ''):continue
 match=re.search(r'/(DAD|PAL|HIL|ORA|DUV|BRE|POL|PAS|SAR|MAN|CLL|MRN|STJ|STL|ESC)/',v['url'],re.I)
 if not match:continue
 code=match.group(1).upper();parent=next(p for p in parents if p['source_county_code']==code);base=next(t for k,t in original_tables['2024_senate'].items() if k.casefold()==parent['name'].casefold())
 for t in v['all_contest_tables']:
  if t['contest_label']!='United States Senator':continue
  named=[];generic=[];header=[x['text'] for x in t['rows'][0]['cells']];ti=header.index('Total Votes')
  for row in t['rows'][1:]:
   cols=row['cells']
   if len(cols)!=len(header):continue
   label=' '.join(cols[0]['text'].split());value=cols[ti]['text'];assert re.fullmatch(r'[\d,]+',value);num=int(value.replace(',',''))
   alias={'Tuan TQ Nguyen (NPA) (NON)':'Tuan TQ Nguyen (NPA)','Ben Everidge (NPA) (NON)':'Ben Everidge (NPA)','REP Rick Scott (REP)':'Rick Scott (REP)','DEM Debbie Mucarsel-Powell (DEM)':'Debbie Mucarsel-Powell (DEM)','LPF Feena Bonoan (LPF)':'Feena Bonoan (LPF)','NPA Tuan TQ Nguyen (NPA)':'Tuan TQ Nguyen (NPA)','NPA Ben Everidge (NPA)':'Ben Everidge (NPA)'}
   if code=='ORA':alias['TQ Nguyen (NPA)']='Tuan TQ Nguyen (NPA)'
   canonical=alias.get(label,label)
   if canonical in base:
    delta=num-base[canonical]
    if code!='POL':assert delta==0,(v['source_id'],label,num,base[canonical])
    named.append({'source_label':label,'legal_control_label':canonical,'alias_explicit':canonical!=label,'votes':num,'legal_control_votes':base[canonical],'source_minus_legal':delta,'source_table_position':t['table_position_0based'],'source_row_position':row['row_position_0based']})
   else:generic.append({'source_label':label,'votes':num,'scope':'generic marks or other source label; never allocated to named valid-writein'})
   methods=[x['text'] for x in cols[1:ti]]
   if all(re.fullmatch(r'[\d,]+',x) for x in methods):assert sum(int(x.replace(',','')) for x in methods)==num;method_checks+=1
  assert len(named)==5,(v['source_id'],named)
  vendor_controls.append({'county':parent['name'],'county_code':code,'source_id':v['source_id'],'named_choices_checked':named,'other_source_rows':generic,'legal_named_writein':{k:v for k,v in base.items() if '(WRI)' in k}})
# Complete XML rows and attributes remain present; separate source universe.
br=gz(EX/'broward-complete-xml.json.gz');b2024=next(x for x in br if x['source_id']=='broward-summary-236');bv={k:{x['tag']:x['text'] for x in row['fields']} for k,row in enumerate(b2024['all_rows'])};bbase=original_tables['2024_senate']['Broward'];bn=[]
for x in bv.values():
 if x.get('RaceName')!='United States Senator':continue
 label=x['ContestantName']+' ('+x['Party']+')'
 if label in bbase:assert int(x['TotalVotes'])==bbase[label];bn.append(label)
assert len(bn)==5
# Protected Pinellas details intentionally cannot numerically reconcile.
pi=gz(EX/'pinellas-complete-json.json.gz');sen=next(x for x in pi['summary'] if x['C']=='United States Senator');detail=next(x for x in pi['details']['Contests'] if x['K']==sen['K']);assert sen['K']=='0004' and sen['PR']==sen['TP']==286 and sum(sen['V'])==sen['T']==511942;assert len(detail['P'])==len(detail['V'])==286 and detail['T'] is None and detail['Eid']==detail['Cid']==[];protected=sum(x=='protected' for row in detail['V'] for x in row);assert protected==1716;assert sen['V'][:5]==[original_tables['2024_senate']['Pinellas'][k] for k in c['source_objects']['primary_county_tables']['2024_senate']['candidate_universe'][:5]]
# Complete PDF controls from source lines in native column order.
pdfcontrols=[]
for sid,county,totalposition in [('alt-LEE-2','Lee','first'),('results-SEM-02-follow-01-asset-134','Seminole','last')]:
 r=next(r for r in receipts if r['id']==sid);b=gzip.decompress((ROOT/r['body_path']).read_bytes());page=PdfReader(io.BytesIO(b)).pages[0];text=page.extract_text(extraction_mode='layout');start=text.find('United States Senator');assert start>=0;fragment=text[start:];fragment=fragment.split('Representative in Congress')[0];base=original_tables['2024_senate'][county];observ=[]
 for cand,val in list(base.items())[:5]:
  plain=cand.rsplit(' (',1)[0];line=next(ln for ln in fragment.splitlines() if plain in ln);tail=line.split(plain,1)[1];nums=re.findall(r'(?<![\w.])[\d,]+(?:\.\d+)?%?',tail);got=int((nums[0] if totalposition=='first' else nums[-1]).replace(',',''));assert got==val,(sid,cand,got,val,line);observ.append({'candidate':cand,'votes':got,'source_layout_line':line})
 pdfcontrols.append({'source_id':sid,'county':county,'compatible_named_choices':observ,'complete_original_retained':True})
assert len({x['county'] for x in vendor_controls})==15
checks['local_2024_controls']={'HTML_counties':15,'named_HTML_cells':sum(len(x['named_choices_checked']) for x in vendor_controls),'XML_counties':1,'JSON_counties':1,'PDF_counties':2,'distinct_counties':19,'named_HTML_disagreements':[{'county':x['county'],'source_id':x['source_id'],'candidate_comparisons':x['named_choices_checked']} for x in vendor_controls if any(r['source_minus_legal'] for r in x['named_choices_checked'])],'numeric_method_row_sums_checked':method_checks,'Pinellas_protected_cells_retained':protected}
dump(EX/'independent-county-controls.json',{'HTML_controls':vendor_controls,'PDF_controls':pdfcontrols,'Broward_compatible_named_choices':bn,'Pinellas_compatible_summary':sen,'Pinellas_detail_gap':'All1716cells protected; Tnull, emptyEidCid. No numeric nativecandidate reconciliation from this source.','source_scope':'Other/generic marks retained separately, no rescaling. Compiled-vs-legal discrepancies unchanged.'})
# Alternate public Polk CSVs preserve the HTML conflict and give independent numeric controls.
polk_full={};psums={};pcounts={};pmasks=0
for sid in ['polk2024-report-16','polk2024-report-18']:
 r=next(r for r in receipts if r['id']==sid);b=gzip.decompress((ROOT/r['body_path']).read_bytes());rows=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))));senrows=[r for r in rows if r['Contest']=='United States Senator'];assert len(senrows)==(6 if sid.endswith('16') else 1032)
 sums=collections.Counter();keys=set()
 for row in senrows:
  key=(row['Candidate Issue'],row['Party'],row.get('Precinct Name'));assert key not in keys;keys.add(key);sums[(row['Candidate Issue'],row['Party'])]+=int(row['Total Votes']);pmasks+=sum(row[k]=='-' for k in ['Mail Votes','Early Votes','Election Day Votes'])
 if sid.endswith('18'):assert len({r['Precinct Name'] for r in senrows})==172
 psums[sid]=sums;pcounts[sid]=len(rows);polk_full[sid]={'source_receipt':'data/results-sources/source/'+sid+'.receipt.json','all_rows':[{'source_csv_record_position_1based':i+2,'full_row':row} for i,row in enumerate(rows)]}
assert psums['polk2024-report-16']==psums['polk2024-report-18']
for label,val in original_tables['2024_senate']['Polk'].items():
 if '(WRI)' not in label:
  plain,party=label.rsplit(' (',1);assert psums['polk2024-report-16'][(plain,party[:-1])]==val
assert psums['polk2024-report-16'][('WRITE-IN','')]==383
(EX/'polk-complete-csv.json.gz').write_bytes(gzip.compress(json.dumps(polk_full,ensure_ascii=False).encode(),mtime=0));checks['Polk_alternate_primary_CSV']={'complete_summary_records':pcounts['polk2024-report-16'],'complete_precinct_records':pcounts['polk2024-report-18'],'Senate_unit_rows':1032,'Senate_units':172,'summary_and_precinct_totals_equal':True,'five_printed_choices_match_DOS':True,'generic_writein_marks_separate':383,'masked_method_cells_retained':pmasks,'HTML_five_printed_choices_source_minus_DOS':-431,'cause_or_change_time_established':False}
# Exact public candidate all-status form; repeated anchors are HTML presentation, not more candidates.
r=next(r for r in receipts if r['id']=='current-candidate-all-status');sp=BeautifulSoup(gzip.decompress((ROOT/r['body_path']).read_bytes()),'html.parser');candidate_records={}
for pos,anchor in enumerate(sp.find_all('a',href=True)):
 if 'CanDetail.asp?account=' not in anchor['href']:continue
 key=anchor['href'];tr=anchor.find_parent('tr');cells=[td.get_text(' ',strip=True) for td in tr.find_all('td',recursive=False)];assert len(cells)==4
 if key not in candidate_records:candidate_records[key]={'source_anchor_positions_0based':[],'full_source_row_HTML':str(tr),'cells':cells}
 candidate_records[key]['source_anchor_positions_0based'].append(pos)
assert len(candidate_records)==14;qualified=[v for v in candidate_records.values() if v['cells'][1]=='Qualified'];assert len(qualified)==3;assert sorted(v['cells'][0].split(',')[0].strip() for v in qualified)==['Gillespie','Moody','Nixon'];writein=[v for v in candidate_records.values() if '(WRI)' in v['cells'][0]];assert len(writein)==1 and writein[0]['cells'][1]=='Did Not Qualify'
dump(EX/'current-candidate-record-controls.json',{'source_receipt':'data/results-sources/source/current-candidate-all-status.receipt.json','form_status':'ALL','full_unique_filing_rows':candidate_records,'ENR_choice_IDs':None});checks['current_candidate_status_query']={'unique_filing_records':14,'qualified':3,'writein_filings':1,'qualified_writein_filings':0,'full_DNQ_withdrawn_defeated_rows_preserved':True,'November_ENR_choice_keys_admitted':False}
# Operative statutory clock, explicit effective-date source, and standard-time conversions.
from zoneinfo import ZoneInfo
import datetime
for zone,expected in [('America/New_York','2026-11-04T00:00:00+00:00'),('America/Chicago','2026-11-04T01:00:00+00:00')]:assert datetime.datetime(2026,11,3,19,tzinfo=ZoneInfo(zone)).astimezone(datetime.timezone.utc).isoformat()==expected
assert datetime.datetime(2026,11,3,19,tzinfo=ZoneInfo('America/New_York'))==datetime.datetime(2026,11,3,18,tzinfo=ZoneInfo('America/Chicago'))
r=next(r for r in receipts if r['id']=='operative2025-102.111');lawtext=' '.join(BeautifulSoup(gzip.decompress((ROOT/r['body_path']).read_bytes()),'html.parser').get_text(' ',strip=True).split());assert 'shall meet at 8 a.m.' in lawtext
session=gz(EX/'hb991-primary-pdf.pages.json.gz');assert 'January 1, 2027' in session['pages'][-1]['text'];checks['operative_clock']={'chapter2026_26_default_effective':'2027-01-01','operative2025_commission_hour':'08:00','Gulf_published_19ET_equals_18CT':True,'Gulf_frozen_fields_still_null':all(p['ordinary_poll_close_2026_utc'] is None and p['ordinary_election_admin_clock'] is None for p in parents if p['name']=='Gulf'),'deadlines_not_vendor_clocks':True}

# Current Lake setup: complete CSV rows including all source ordering and92Senate units, zero counts retained as setup only.
lake={}
for sid in ['lake-csv-15','lake-csv-17']:
 r=next(r for r in receipts if r['id']==sid);b=gzip.decompress((ROOT/r['body_path']).read_bytes());rows=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))));senrows=[x for x in rows if x['Contest']=='United States Senator'];assert len(senrows)==(3 if sid.endswith('15') else 276);assert {x['Candidate Issue'] for x in senrows}=={'Ashley Moody','Angie Nixon','Neil J. Gillespie'}
 for row in rows:
  assert all(row[k]=='0' for k in ['Mail Votes','Early Votes','Election Day Votes','Total Votes'])
 if sid.endswith('17'):assert len({x['Precinct Name'] for x in senrows})==92
 lake[sid]={'source_receipt':'data/results-sources/source/'+sid+'.receipt.json','all_rows':[{'source_csv_record_position_1based':i+2,'full_row':r} for i,r in enumerate(rows)],'senate_rows':len(senrows),'setup_only':True}
( EX/'lake-complete-csv.json.gz').write_bytes(gzip.compress(json.dumps(lake,ensure_ascii=False).encode(),mtime=0));checks['Lake_current_setup']={'election_id':'4079','contest_DOM_id':'61160','choice_IDs':None,'candidate_choices':3,'Senate_precinct_labels':92,'Senate_candidate_unit_rows':276,'all_csv_votes_zero':True,'genuine_returns_admitted':False}
sc=js(EX/'state-primary-controls.json');assert sc['county_units']==67 and sc['joins_checked']==2979;checks['state_selected_primary']={'county_units':67,'pipe_vote_rows':2979,'cross_format_compared':sc['cross_format_comparisons'],'cross_format_disagreements':len(sc['cross_format_mismatches']),'current_November_admitted':False}
# Source metadata, inventory and legal/calendar exclusions are structural offline checks, not a forecast.
csvrows=list(csv.DictReader((ROOT/'data/official-results-sources.csv').open()));assert len(csvrows)==68;assert [r['jurisdiction_key'] for r in csvrows[1:]]==[p['key'] for p in parents];assert sum(bool(r['priority_rank']) for r in csvrows[1:])==22;assert all(r['november_counts_admitted']=='false' for r in csvrows);checks['inventory_rows']=68
assert len([r for r in records if r['frozen_parent']['priority']])==22;assert all(r['current_november']['exact_outstanding_candidate_votes'] is None for r in records)
# All shared ledgers reference exact immutable originals and individual source receipts.
shared=js(OUT/'shared-evidence.json')
for r in shared['receipts']:
 p=ROOT/r['receipt_path'];assert p.stat().st_size==r['receipt_bytes'] and sha(p.read_bytes())==r['receipt_sha256'];assert js(p)==r['complete_receipt']
checks['shared_full_receipts']=len(shared['receipts'])
# Internal Markdown targets checked without network; external primary links remain observation-scoped.
linkcount=0
for p in [ROOT/'official-results.md']+list(OUT.glob('*.md')):
 text=p.read_text()
 for target in re.findall(r'\]\(([^)]+)\)',text):
  if target.startswith(('https:','http:','#','mailto:')):continue
  q=(p.parent/unquote(target.split('#')[0])).resolve();assert q.exists() or q in [MF,OUT/'validation.json'],(p,target);linkcount+=1
checks['relative_markdown_links']=linkcount
# Individual coordinator-reviewed sources stay byte-identical; review JSON itself not a dependency pin.
review=js(ROOT/'data/coordinator-current-source-review.json');review_pins=0
for pin in review['source_pins']:
 p=ROOT/pin['receipt'];assert sha(p.read_bytes())==pin['receipt_sha256'],pin['receipt'];review_pins+=1
checks['coordinator_reviewed_immutable_source_receipts']=review_pins
checks['byte_bounds']={'strict_max_exclusive':40000000,'all_owned_files_below_bound':all(p.stat().st_size<40000000 for p in owned())}
assert checks['byte_bounds']['all_owned_files_below_bound']
checks['limitations']=['No genuineNovembercounts/update sequence','No calibratedprobability/runningcollector/measuredcadence','No currentcrosswalk or method allocation','Volusia/Lake/Osceola no independenthistorical localcontrol in acquiredentities; completeDOSfour original scopes available','Pinellas detail cellsprotected; methodsuppressiondash unavailable','Future election-specific extensions/newcourtorders notcertifiedabsent; laterrecheck required']
checks['asset_manifest']={'exact_pathset_verified':True,'self_exclusion_only':'data/results-sources/asset-manifest.json'}
validation={'status':'pass_with_explicit_source_scope_and_access_gaps','offline':True,'checks':checks};dump(OUT/'validation.json',validation)
assets=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in owned()];dump(MF,{'schema_version':1,'root':'senate/2026/florida','self_excluded':'data/results-sources/asset-manifest.json','assets':assets,'source_reconstruction':'Complete entities stored losslessly as gzip or exact immutable shared body references. Extracts retain full source positions/attrs/nulls/flags; manifest excludes only itself. No dependency/caches.'});assert check_manifest()==len(assets)
print(json.dumps({'validation':validation['status'],'assets':len(assets),'validation_sha256':sha((OUT/'validation.json').read_bytes()),'manifest_sha256':sha(MF.read_bytes()),'checks':{k:v for k,v in checks.items() if k in ['primary_original_HTML','original_native_validation','local_2024_controls','Lake_current_setup']}}))
