#!/usr/bin/env python3
"""Independently extract complete originals. Python stdlib + pdftotext only.
No coordinator derivative is an input to extraction; preflight compared afterward.
"""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json,posixpath,re,subprocess,tempfile,zipfile
import xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;DATA=D.parent;NEWS=DATA/'news';X=D/'extracts';X.mkdir(exist_ok=True)
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(name,obj): (D/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def gzjson(name,obj): (D/name).write_bytes(gzip.compress(json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
def csvout(name,rows):
 with (D/name).open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def shared(sid):
 a=next(x for x in json.loads((NEWS/'manifest.json').read_text())if x['id']==sid)
 if 'asset_parts'in a:
  parts=[]
  for p in a['asset_parts']:
   b=(NEWS/p['asset']).read_bytes();assert len(b)==p['bytes']<40000000 and sha(b)==p['sha256'];parts.append(b)
  z=b''.join(parts);assert len(z)==a['stored_bytes']
 else:z=(NEWS/a['asset']).read_bytes();assert len(z)<40000000
 assert sha(z)==a['stored_sha256'];raw=gzip.decompress(z);assert sha(raw)==a['raw_sha256'] and len(raw)==a['bytes'];return raw,a

def own(sid):
 a=json.loads((D/'source'/f'{sid}.receipt.json').read_text());z=(D/'source'/a['asset']).read_bytes();assert sha(z)==a['stored_sha256'];raw=gzip.decompress(z);assert sha(raw)==a['raw_sha256'] and len(raw)==a['raw_bytes'];return raw,a

def pdf(sid,own_source=False):
 b,a=(own if own_source else shared)(sid)
 with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
  f.write(b);f.flush();t=subprocess.run(['pdftotext','-layout',f.name,'-'],check=True,capture_output=True).stdout
 (X/(sid+'.txt.gz')).write_bytes(gzip.compress(t,mtime=0));return t.decode(),a

def county_tables(fips):
 out={}
 for year,sid,start,n,labels in [(2024,'sos-2024-general-canvass','Presidential Electors',4,['Harris DEM','Oliver LIB','Trump REP','Kennedy IND']),(2022,'sos-2022-general-canvass','United States Senator',3,['Bengs DEM','Lesnar LIB','Thune REP']),(2020,'sos-2020-general-canvass','United States Senator',2,['Rounds REP','Ahlers DEM'])]:
  t,a=pdf(sid);sec=t.split(start,1)[1].split('United States Representative',1)[0];rows={};footer=None
  for lineno,line in enumerate(sec.splitlines(),1):
   m=re.fullmatch(r'\s*([A-Za-z][A-Za-z .\'-]*?)\s+('+r'\s+'.join([r'[0-9][0-9,]*']*n)+r')\s*',line)
   if m:
    name=m[1].strip();counts=[int(v.replace(',',''))for v in m[2].split()]
    if name not in fips and name!='Total':continue
    if name=='Total':footer=counts
    else:
     assert name not in rows;position=t.find(line,t.index(start)+len(start));assert position>=0
     rows[name]={'candidate_votes':counts,'section_line_1based':lineno,'literal_line':line,'source_pdf_page':t[:position].count('\f')+1,'source_page_line_1based':t[:position].split('\f')[-1].count('\n')+1}
  assert len(rows)==66 and [sum(r['candidate_votes'][j]for r in rows.values())for j in range(n)]==footer
  out[str(year)]={'source_id':sid,'source_sha256':a['raw_sha256'],'candidate_order':labels,'candidate_controls':footer,'contest_votes':sum(footer),'counties':rows}
 dump('certified-controls.json',out);return out

def book(sid,own_source=False):
 b,a=(own if own_source else shared)(sid);z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip()is None
 ss=[''.join(si.itertext())for si in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
 rel={r.attrib['Id']:r.attrib['Target']for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
 sheets=[]
 for i,s in enumerate(E.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',NS),1):
  target=rel[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')];target=target.lstrip('/')if target.startswith('/')else posixpath.normpath('xl/'+target)
  rows=[]
  for r in E.fromstring(z.read(target)).findall('m:sheetData/m:row',NS):
   cells=[]
   for c in r.findall('m:c',NS):
    v=c.find('m:v',NS);rv=v.text if v is not None else None;val=ss[int(rv)]if c.get('t')=='s'else ''.join(c.find('m:is',NS).itertext())if c.get('t')=='inlineStr'else rv
    cells.append({'address':c.get('r'),'type':c.get('t'),'raw_v':rv,'resolved':val,'xml':E.tostring(c,encoding='unicode')})
   rows.append({'row':int(r.get('r')),'row_attributes':r.attrib,'cells':cells})
  sheets.append({'ordinal':i,'name':s.get('name'),'sheetId':s.get('sheetId'),'member':target,'rows':rows})
 return {'source_id':sid,'source_sha256':a['raw_sha256'],'zip_members':[{'name':i.filename,'bytes':i.file_size,'crc32':f'{i.CRC:08x}','sha256':sha(z.read(i.filename))}for i in z.infolist()],'shared_strings':ss,'sheets':sheets}
def values(r):return {re.sub(r'\d+$','',c['address']):c['resolved']for c in r['cells']}
def native2024(fips,controls):
 sid='sos-2024-public-presidential-precinct-export-684';b=book(sid);native=[];parents=[];headers=['Kamala D. Harris and Tim Walz ','Chase Oliver and Mike ter Maat ','Donald J. Trump and JD Vance ','Robert F. Kennedy, Jr. and Nicole Shanahan '];cols='CDEF'
 for s in b['sheets']:
  rows={r['row']:r for r in s['rows']};h=values(rows[7]);assert [h[c]for c in cols]==headers
  totals=[r for r in s['rows']if values(r).get('B')=='TOTALS'];assert len(totals)==1
  tr=totals[0];cnt=[]
  for r in s['rows']:
   if not 7<r['row']<tr['row']:continue
   v=values(r);county=s['name'];vv=[int(v[c])for c in cols];assert all(c['type']=='n'for c in r['cells']if re.sub(r'\d+$','',c['address'])in cols)
   label=v['B'];key=f"sd:2024:pres:{fips[county]}:sheet{s['ordinal']}:row{r['row']}"
   native.append({'key':key,'county':county,'county_fips':fips[county],'source_id':sid,'source_sha256':b['source_sha256'],'sheet_ordinal':s['ordinal'],'sheet_id':s['sheetId'],'sheet_member':s['member'],'source_row':r['row'],'native_label':label,'official_native_numeric_id':None,'unit_kind':'source_labeled_absentee_reporting_group'if label.strip()in ('Absentee','Absentee Precinct')else 'source_native_reporting_unit_type_unresolved','method_scope':'source_label_absentee_unsplit'if label.strip()in ('Absentee','Absentee Precinct')else 'unavailable_not_assumed_election_day','harris_dem':vv[0],'oliver_lib':vv[1],'trump_rep':vv[2],'kennedy_ind':vv[3],'contest_votes':sum(vv),'generic_writein_votes':None,'valid_named_writein_votes':None,'writein_scope':'not_countable_by_SDCL12-20-21.2; no writein column published','ballots_cast':None,'registered_voters':None,'blank_ballots':None,'undervotes':None,'overvotes':None,'null_reason':'fields not published in this native candidate workbook','status':'unofficial','current_geometry_join':'unapproved','source_cells':','.join(c+str(r['row'])for c in cols)})
   cnt.append(vv)
  footer=[int(values(tr)[c])for c in cols];assert [sum(v[j]for v in cnt)for j in range(4)]==footer
  parents.append({'county':s['name'],'county_fips':fips[s['name']],'sheet_ordinal':s['ordinal'],'source_native_rows':len(cnt),'footer_row':tr['row'],'candidate_footer':footer,'certified_candidate_counts':controls['2024']['counties'][s['name']]['candidate_votes'],'unofficial_minus_certified':[a-c for a,c in zip(footer,controls['2024']['counties'][s['name']]['candidate_votes'])],'source_heading_rows':[values(rows[i])for i in range(1,8)if i in rows]})
 assert len(native)==691 and len(parents)==66 and len({r['key']for r in native})==691
 gzjson('extracts/native2024-complete-OOXML.json.gz',b)
 native.sort(key=lambda r:(-r['contest_votes'],r['county_fips'],r['sheet_ordinal'],r['source_row']));c=0
 for i,r in enumerate(native,1):c+=r['contest_votes'];r['rank']=i;r['cumulative_votes']=c
 assert c==428728
 csvout('native-2024.csv',native);dump('native-2024-parent-reconciliation.json',parents)
 # Independently read contradictory all-race source; no inferred repair.
 conflicts=[]
 for sid in ['sos-2024-public-statewide-export-postback-684','sos-2024-public-aurora-export-postback-684']:
  wb=book(sid);gzjson('extracts/'+sid+'-OOXML.json.gz',wb)
  for s in wb['sheets']:
   if s['name'].startswith('12665'):
    hr=next(r for r in s['rows']if r['row']==7);conflicts.append({'source_id':sid,'source_sha256':wb['source_sha256'],'sheet':s['name'],'literal_header_cells':values(hr),'correct_native_headers':headers,'headers_agree':all(values(hr).get(c)==h for c,h in zip(cols,headers))})
 dump('candidate-header-presentation.json',conflicts);return native,parents

def native2022(controls,fips):
 text,a=pdf('sos-2022-precinct-canvass');raw,_=shared('sos-2022-precinct-canvass')
 with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
  f.write(raw);f.flush();bbox=subprocess.run(['pdftotext','-bbox-layout',f.name,'-'],check=True,capture_output=True).stdout
 ns={'h':'http://www.w3.org/1999/xhtml'};pages=E.fromstring(bbox).findall('.//h:page',ns)
 rows=[];footers={};inventory=[];retained=[]
 for page,p in enumerate(text.split('\f'),1):
  if not re.search(r'United\s+States\s+Senator',p):continue
  names=[n for n in fips if re.search(r'\b'+re.escape(n)+r' County\b',p)];assert len(names)==1,(page,names)
  county=names[0];el=pages[page-1];ws=[dict(w.attrib,text=w.text)for w in el.findall('.//h:word',ns)]
  hy=next(float(w['yMax'])for w in ws if w['text']=='Name')
  totalword=next((w for w in ws if w['text']=='Total'),None)
  ty=float(totalword['yMin'])if totalword else float(el.get('height'))-30
  groups={}
  for w in ws:
   if hy<float(w['yMin'])<=ty+1 and re.fullmatch(r'\d[\d,]*',w['text']):groups.setdefault(round(float(w['yMin']),1),[]).append(w)
  gr=sorted((sum(float(w['yMin'])for w in g)/len(g),sorted(g,key=lambda w:float(w['xMin']))[-3:])for _,g in groups.items()if len(g)>=3)
  cut=min(float(g[0]['xMin'])for y,g in gr)-2;records=[]
  for rowi,(y,g)in enumerate(gr,1):
   lw=[w for w in ws if hy<float(w['yMin'])<=min(ty+1,gr[-1][0]+15)and float(w['xMax'])<cut and min(gr,key=lambda z:abs(z[0]-float(w['yMin'])))[0]==y]
   lw.sort(key=lambda w:(float(w['yMin']),float(w['xMin'])));label=' '.join(w['text']for w in lw);vv=[int(w['text'].replace(',',''))for w in g]
   if label=='Total':footers[county]=vv;continue
   assert label,(page,rowi)
   records.append({'key':f"sd:2022:senate:{fips[county]}:page{page}:tablerow{rowi}",'county':county,'county_fips':fips[county],'native_label':label,'bengs_dem':vv[0],'lesnar_lib':vv[1],'thune_rep':vv[2],'contest_votes':sum(vv),'source_pdf_page':page,'source_table_row':rowi,'source_numeric_ymin':y,'method_scope':'source_label_absentee_unsplit'if label.strip()in ('Absentee','Absentee Precinct')else 'unavailable_not_assumed_election_day','official_native_numeric_id':None,'ballots_cast':None,'registered_voters':None,'blank_ballots':None,'undervotes':None,'overvotes':None,'source_id':'sos-2022-precinct-canvass','source_sha256':a['raw_sha256']})
  retained.append({'page':page,'county':county,'original_bbox_page_XML':E.tostring(el,encoding='unicode'),'label_assignment':'Left-column words assigned nearest candidate-row yMin; all counts reconciled to county footers. Split labels retain all original words.'})
  inventory.append({'page':page,'county':county,'rows':len(records)});rows+=records
 missing=sorted(set(fips)-set(footers));assert missing==['Yankton'],missing;diffs=[]
 for county in fips:
  if county in missing:continue
  rr=[r for r in rows if r['county']==county];s=[sum(r[k]for r in rr)for k in ['bengs_dem','lesnar_lib','thune_rep']];assert s==footers[county],(county,s,footers[county])
  cv=controls['2022']['counties'][county]['candidate_votes'];assert s==cv,(county,s,cv)
 assert len(rows)==679,len(rows)
 csvout('native-2022.csv',rows);gzjson('extracts/native2022-original-Senate-page-bboxes.json.gz',retained)
 dump('native-2022-reconciliation.json',{'source_pages':inventory,'rows':len(rows),'missing_native_counties':missing,'missing_native_candidate_controls':{n:controls['2022']['counties'][n]['candidate_votes']for n in missing},'candidate_sums':[sum(r[k]for r in rows)for k in ['bengs_dem','lesnar_lib','thune_rep']],'county_differences':diffs});return rows

def turnout_books(fips):
 tables={};reg={};prec={}
 for y,tp,rps,pp in [(2024,23,[20,21],22),(2022,25,[22,23],24),(2020,15,[13],14)]:
  t,a=pdf(f'returns-{y}-archive',True);pages=t.split('\f');p=pages[tp-1];rs={}
  # Independently locate literal county token then two integers + printed rate, with no join on position.
  # Oglala Lakota spans lines in2022/24 turnout table; last word is retained with explicit rule.
  for name in list(fips)+['TOTAL']:
   lit='Lakota'if name=='Oglala Lakota'and y!=2020 else name
   m=re.search(r'(?<![A-Za-z])'+re.escape(lit)+r'\s+(\d[\d,]*)\s+(\d[\d,]*)\s+([\d.]+)\s*%',p);assert m,(y,name)
   rs[name]={'registered_voters_turnout_table':int(m[1].replace(',','')),'votes_cast_source_label':int(m[2].replace(',','')),'percent_turnout_printed':m[3],'source_pdf_page':tp,'source_matched_text':m[0],'source_id':f'returns-{y}-archive','source_sha256':a['raw_sha256']}
  assert sum(rs[n]['votes_cast_source_label']for n in fips)==rs['TOTAL']['votes_cast_source_label']
  assert sum(rs[n]['registered_voters_turnout_table']for n in fips)==rs['TOTAL']['registered_voters_turnout_table']
  tables[str(y)]=rs;reg[str(y)]={}
  for page in rps:
   for line_no,line in enumerate(pages[page-1].splitlines(),1):
    m=re.match(r'\s*('+ '|'.join(re.escape(n)for n in sorted(fips,key=len,reverse=True))+r'|Total)\s+(.+)$',line)
    if not m:continue
    nums=re.findall(r'\d[\d,]*',m[2]);assert len(nums)>=4
    name=m[1];reg[str(y)][name]={'inactive':int(nums[-2].replace(',','')),'total_active':int(nums[-1].replace(',','')),'source_line_literal':line,'source_pdf_page':page,'source_line_1based':line_no,'party_fields':'preserved verbatim in original and source_line; omitted blank cells not invented zeros'}
  assert len(reg[str(y)])==67
  prec[str(y)]={'page':pp,'complete_page_text':pages[pp-1],'join_scope':'Literal historical table;2020 right-column alignment differs from other native sources. Not used to map identities by position.'}
 dump('turnout-registration-controls.json',{'turnout':tables,'registration_table':reg,'printed_precinct_tables':prec});return tables,reg

def main():
 raw,a=own('census-counties2020');fips={}
 for r in csv.DictReader(io.StringIO(raw.decode()),delimiter='|'):
  if r['STATE']=='SD':fips[r['COUNTYNAME'].removesuffix(' County')]=r['STATEFP']+r['COUNTYFP']
 assert len(fips)==66 and all(v.startswith('46')for v in fips.values());dump('county-fips.json',{'source_receipt':'source/census-counties2020.receipt.json','source_sha256':a['raw_sha256'],'counties':fips,'Oglala_Lakota_scope':'2020 Census code46102; historical Shannon code46113 is a separately named/vintaged identifier, never an extra county or assumed precinct crosswalk'})
 controls=county_tables(fips);native,parents=native2024(fips,controls);native22=native2022(controls,fips);tables,reg=turnout_books(fips)
 # Check coordinator preflights without running their shared-path writes.
 co=json.loads((DATA/'coordinator-primary-preflight.json').read_text())['tables'];co2=json.loads((DATA/'coordinator-2024-public-native-export-preflight.json').read_text())
 for y,k in [('2024','2024_President'),('2022','2022_Senate_other_ClassIII'),('2020','2020_Senate_same_ClassII')]:
  assert controls[y]['candidate_controls']==co[k]['controls']
  assert all(v['candidate_votes']==co[k]['rows'][n]['votes']for n,v in controls[y]['counties'].items())
 assert co2['public_source_candidate_totals']==[sum(r[k]for r in native)for k in ['harris_dem','oliver_lib','trump_rep','kennedy_ind']]
 dump('preflight-independent-check.json',{'status':'pass','original_extraction_not_coordinator_derivatives':True,'signed_county_vectors_checked':198,'native_county_vectors_checked':66,'preflight_primary_source_code_sha256':sha((DATA/'preflight_primary_sources.py').read_bytes()),'preflight_native_source_code_sha256':sha((DATA/'preflight_2024_public_native_export.py').read_bytes()),'notes':'Independently reproduced all computations from original bytes then compared preflight outputs read-only; supplied preflight main functions write outside ownership and were not invoked against shared paths.'})
 print(json.dumps({'native2024':len(native),'native2022':len(native22),'certified':{y:v['candidate_controls']for y,v in controls.items()},'status':'pass'}))
if __name__=='__main__':main()
