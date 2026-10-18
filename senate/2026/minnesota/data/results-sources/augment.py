#!/usr/bin/env python3
"""Deterministic auxiliary extraction from pinned originals; no peer aggregates imported."""
import pathlib,json,gzip,sys,re,collections,decimal,subprocess,hashlib,datetime
from extract import ROOT,STATE,workbook,rowsmap,writejson,textfile,digest
RAW=ROOT/'raw'
# Current hours workbook, exact primary-only annotations retained.
w=workbook(gzip.decompress((RAW/'hours-exceptions.body.gz').read_bytes()));writejson(ROOT/'hours-exceptions-raw-cells.json',w)
cs=json.loads((ROOT/'directory.json').read_text());bycode={int(c['source_county_code']):c for c in cs};hours=[]
for sn,sh in w.items():
 for row,m in zip(sh['rows'][2:],rowsmap(sh)[2:]):
  if not m.get('D') or not m['D'].isdigit():continue
  c=bycode[int(m['D'])];v=m['C'];op=None;scope='general_and_primary'
  try:
   minute=round(decimal.Decimal(v)*1440);op=f'{minute//60:02}:{minute%60:02}'
  except decimal.InvalidOperation:
   if 'primary only' in v.lower():scope='primary_only';op=None
   else:
    mm=re.search(r'(\d{1,2}:\d\d)\s*\(general\)',v,re.I);assert mm,v;op=mm[1].zfill(5)
  hours.append({'source_sheet':sn,'source_row':row['row'],'county':m['A'],'county_fips':c['county_fips'],'county_code':m['D'],'precinct_name':m['B'],'precinct_code':m['E'],'opening_raw':v,'general_opening_local':op,'scope':scope,'timezone':'America/Chicago','general_close_local':'20:00' if op else None,'current_results_or_historic_vtdid_join':'not asserted'})
writejson(ROOT/'hours-exceptions.json',hours)
# Independent PDF text from original2020 primary, with all main + named positions.
pdf=STATE/'data/news/sos-2020-canvass-original.html.gz';b=gzip.decompress(pdf.read_bytes());tmp=ROOT/'pdf-text/canvass-2020.pdf';tmp.write_bytes(b);subprocess.run(['pdftotext','-layout',str(tmp),str(tmp.with_suffix('.txt'))],check=True);tmp.unlink();text=tmp.with_suffix('.txt').read_text();pages=text.split('\f')
norm=lambda s:re.sub('[^a-z]','',s.lower());county={norm(c['name']):c for c in cs};original2020=json.loads((ROOT/'historical-controls.json').read_text())['2020']['county_controls'];positions=[]
starts=[m.start() for m in re.finditer('U.S. Senator',text)];assert len(starts)==2
for which,start in enumerate(starts):
 nextoffice=re.search('U.S. Representative',text[start:]);end=start+nextoffice.start() if nextoffice else len(text);segment=text[start:end];offset=start
 for line in segment.splitlines(keepends=True):
  m=re.match(r'^\s*([A-Za-z .]+?)\s{2,}([0-9,\s]+)\s*$',line)
  if m and norm(m[1]) in county:
   c=county[norm(m[1])];nums=list(re.finditer(r'[\d,]+',m[2]));nn=len(nums)
   names=(['Kevin O\'Connor','Oliver Steinberg','Jason Lewis','Tina Smith'] if nn==4 else ['WRITE-IN']) if which==0 else (['Josh D. Ondich','John Berman','George A. Dennis Jr','Stephen W Carlson'] if nn==4 else ['Jason U. Shaver','Rob Barrett, Jr.'])
   assert nn==len(names),(line,names)
   fields=(['USSENLMN','USSENGLC','USSENR','USSENDFL'] if nn==4 else ['USSENWI']) if which==0 else [None]*nn
   pagenum=text[:offset].count('\f')+1;pagestart=text.rfind('\f',0,offset)+1;lineno=text[pagestart:offset].count('\n')+1
   for nm,f,n in zip(names,fields,nums):
    v=int(n[0].replace(',',''));check=original2020[c['county_fips']]['fields'][f] if f else None
    positions.append({'scope':'main_report' if which==0 else 'separate_named_writein_appendix','county':c['name'],'county_fips':c['county_fips'],'candidate':nm,'workbook_field':f,'votes':v,'pdf_page_1based':pagenum,'text_page_line_1based':lineno,'global_text_character_start':offset+m.start(2)+n.start(),'global_text_character_end':offset+m.start(2)+n.end(),'text_line':line.rstrip('\r\n'),'workbook_votes':check,'equal_to_workbook':v==check if f else None})
  offset+=len(line)
assert sum(x['scope']=='main_report' for x in positions)==435
assert sum(x['scope']=='separate_named_writein_appendix' for x in positions)==522
assert all(x['equal_to_workbook'] for x in positions if x['scope']=='main_report')
assert sum(x['votes'] for x in positions if x['scope']=='separate_named_writein_appendix')==32
writejson(ROOT/'canvass-2020-positions.json',positions)
writejson(ROOT/'canvass-2020-reconciliation.json',{'main_positions':435,'named_positions':522,'main_county_candidate_equal':True,'main_generic_writein':2261,'named_writein_appendix':32,'relationship':'separate overlapping scope; no addition, residual allocation or native join','source_raw_sha256':digest(b),'source_path':str(pdf.relative_to(STATE))})
# November201 setup exact raw text rows. No live feed configured.
ids=['state','county','precinct','statistics','parties','counties','precincts','municipalities','candidates'];data={}
for id in ids:
 key='export-general201-'+id;rows=textfile(key);data[id]=rows
 with gzip.GzipFile(filename='',mode='wb',fileobj=(ROOT/(key+'.rows.jsonl.gz')).open('wb'),mtime=0) as out:
  for row in rows:out.write((json.dumps(row,separators=(',',':'))+'\n').encode())
summary={'admitted_to_current_counts':False,'reason':'parent201 actual TEST RESULTS; pre-election mock data, not setup zeroes or measured votes','election_id_observed':'201','election_date_label':'2026-11-03','office_in_election_id_in_html_link':'38485','text_office_id':'0102','rows':{k:len(v) for k,v in data.items()},'reporting_universe_in_test_table':sum(int(x['fields'][2]) for x in data['counties']),'native_precinct_keys_unique':len(set((x['fields'][0],x['fields'][1]) for x in data['precincts'])),'candidate_identity_rows':[x for x in data['candidates'] if x['fields'][2]=='0102'],'test_state_rows':data['state'],'reconciliation':[],'timezone_of_file_http_last_modified':'GMT; filesystem/publication metadata, not election-local vote timestamp','expected_actual_november_universe_approved':False,'method_specific_candidate_fields':None,'full_eligible_named_writein_roster':None}
for s in data['state']:
 a=s['fields'];summary['reconciliation'].append({'candidate':a[7],'state':int(a[13]),'county_sum':sum(int(x['fields'][13]) for x in data['county'] if x['fields'][7]==a[7]),'precinct_sum':sum(int(x['fields'][13]) for x in data['precinct'] if x['fields'][7]==a[7])})
writejson(ROOT/'general201-setup-inspection.json',summary)
# Exactly ordered constituents preserved, plus county-level source positions in exports.
contract=json.loads((STATE/'data/turnout/priority-set.json').read_text());controls=json.loads((ROOT/'historical-controls.json').read_text());inventory=[]
for c in contract['county_order']:
 fips=c['county_fips'];directory=next(x for x in cs if x['county_fips']==fips);evidence=[]
 for f in sorted(RAW.glob('county-'+fips+'-*.meta.json')):
  m=json.loads(f.read_text());evidence.append({'id':m['id'],'metadata_path':str(f.relative_to(ROOT)),'requested_url':m['requested_url'],'final_url':m.get('final_url'),'status':m.get('status'),'entity_check':m.get('entity_check'),'retrieved_utc':m['retrieved_utc']})
 found=[]
 for e in evidence:
  lf=RAW/(e['id']+'.links.json')
  if lf.exists() and e['status']==200 and e['entity_check']!='challenge':
   for a in json.loads(lf.read_text()):
    if a['tag']=='a' and ('result' in a['text'].lower() or 'electionresults' in a['resolved_url']) and '/Search' not in a['resolved_url']:
     found.append({'parent':e['id'],'link_index':a['index'],'url':a['resolved_url'],'text':a['text'],'character_offset':a['character_offset']})
 inventory.append({'key':c['key'],'rank':c['rank'],'name':c['name'],'county_fips':fips,'source_county_code':c['source_county_code'],'in_priority':c['in_priority'],'historical_votes_2024':c['votes'],'native_context_object':{'path':'county-native-contexts.jsonl.gz','line_1based':c['rank'],'json_pointer_in_frozen_contract':'/county_order/'+str(c['rank']-1),'scope':'complete exact county object and every constituent, no field dropped'},'native_counts':{y:len(c['native_constituents'][y]) for y in ['2024','2022','2020']},'historical_method_controls':{y:controls[y]['county_controls'][fips] for y in ['2024','2022','2020']},'directory':directory,'evidence':evidence,'observed_results_links':found,'late_opening_rows':[x for x in hours if x['county_fips']==fips],'depth':'individual priority investigation with local public-channel attempts, statewide original/native and exported county/precinct controls; current gaps explicit' if c['in_priority'] else 'directory + actual root request; linked election/results landing inspected where found; no deep-feed claim','source_scope':'county aggregate; native municipality/precinct/ward/central contexts included, never added as extra county totals','current_2026_results_join':'unapproved','method_specific_candidate_split':'unavailable in historic workbook/stateflatresults','genuine_live_cadence':'not measured','exact_outstanding_senate_votes':None})
writejson(ROOT/'authority-inventory.json',inventory)
# Pair sameURL observations; intentionally does not imply live cadence.
pairs=[]
for f in sorted(RAW.glob('*-observation2.meta.json')):
 d=json.loads(f.read_text());old=json.loads((RAW/(d['id'].removesuffix('-observation2')+'.meta.json')).read_text());pairs.append({'first':old['id'],'second':d['id'],'first_retrieved_utc':old['retrieved_utc'],'second_retrieved_utc':d['retrieved_utc'],'first_raw_sha256':old.get('raw_sha256'),'second_raw_sha256':d.get('raw_sha256'),'same_body':old.get('raw_sha256')==d.get('raw_sha256'),'first_entity':old.get('entity_check'),'second_entity':d.get('entity_check'),'interpretation':'bounded dated accessibility/stability observation; not live publication cadence'})
writejson(ROOT/'bounded-observations.json',pairs)
print('PDFmain/named',435,522,'hours',len(hours),'Novemberexceptions',sum(x['general_opening_local']is not None for x in hours),'inventory',len(inventory),'setup',summary['rows'],'201controls',summary['reconciliation'])
