#!/usr/bin/env python3
"""Independent general-statistics HTML and original PDF control extraction."""
import collections,csv,gzip,hashlib,html,io,json,re,subprocess,tempfile
from pathlib import Path
from html.parser import HTMLParser
from extract import D,STATE,NEWS,save,sha
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.tables=[];self.table=None;self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t=='table':self.table=[]
  elif t=='thead'and self.table is not None:self.row=[]
  elif t=='tr'and self.table is not None:self.row=[]
  elif t in ['th','td']and self.row is not None:self.cell=[]
 def handle_data(self,d):
  if self.cell is not None:self.cell.append(d)
 def handle_endtag(self,t):
  if t in ['th','td']and self.cell is not None:self.row.append(''.join(self.cell).strip());self.cell=None
  elif t=='tr'and self.row is not None:self.table.append(self.row);self.row=None
  elif t=='thead'and self.row:self.table.append(self.row);self.row=None
  elif t=='table'and self.table is not None:self.tables.append(self.table);self.table=None
def num(s):return int(s.replace(',',''))if re.fullmatch('[0-9,]+',s or'')else None
def main():
 receipts=json.loads((D/'source/acquisition.json').read_text());a=next(a for a in receipts if a['id']=='stats-2022');p=Tables();p.feed(gzip.decompress((D/a['stored_path']).read_bytes()).decode());out=[]
 for ti,table in enumerate(p.tables):
  kind='registration'if any('Registered Voters at Cutoff'in c for row in table for c in row)else'method'if any('Absentee Ballots Cast'in c for row in table for c in row)else'other_retained_unassigned'
  for ri,row in enumerate(table):
   rec=dict(table_index=ti,row_index=ri,kind=kind,raw_cells=row)
   if kind=='registration'and len(row)==7 and num(row[1])is not None:rec.update(county=row[0],cutoff=num(row[1]),day=num(row[2]),registered=num(row[3]),ballots=num(row[4]),raw_turnout=row[5],raw_day_fraction=row[6])
   elif kind=='method'and len(row)==5 and num(row[1])is not None:rec.update(county=row[0],ballots=num(row[1]),absentee=num(row[2]),early=num(row[3]),raw_fraction=row[4])
   out.append(rec)
 save('source/2022-statistics-tables.json',out)
 # Reuse primary assets by exact hashes, not the peer's extracted quantities.
 peer=D.parent/'turnout';refs=[]
 requests=json.loads((peer/'source/requests.json').read_text())
 for a in requests:
  if a['id'] not in ['timezone-govinfo','classII','classIII']:continue
  path=peer/a['asset'];b=path.read_bytes();assert sha(b)==a['stored_sha256'];raw=gzip.decompress(b);assert sha(raw)==a['original_sha256'];refs.append(dict(a,relative_path='../turnout/'+a['asset'],raw_bytes=len(raw),raw_sha256=sha(raw)))
 # The Census code list is a raw shared reference, not any extracted election votes.
 path=peer/'source/fips2020.gz';b=path.read_bytes();raw=gzip.decompress(b);fipsrows=list(csv.DictReader(io.StringIO(raw.decode()),delimiter='|'));fips={r['COUNTYNAME']:r['STATEFP']+r['COUNTYFP']for r in fipsrows if r['STATE']=='ID'};assert len(fips)==44
 metadata=next(a for a in json.loads((D/'source/independent-reference-receipts.json').read_text())if a['id']=='Census-county-FIPS');assert metadata['raw_sha256']==sha(raw)
 refs.append(dict(id='Census-county-FIPS',relative_path='../turnout/source/fips2020.gz',stored_sha256=sha(b),stored_bytes=len(b),raw_sha256=sha(raw),raw_bytes=len(raw),original_receipt=metadata,source_url='https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt'))
 save('source/county-fips.json',fips)
 national=json.loads((peer/'source/reused-national-originals.json').read_text());national_texts={}
 for a in national:
  path=STATE.parent/a['original_asset_path'];b=path.read_bytes();raw=gzip.decompress(b);assert sha(b)==a['stored_sha256']and sha(raw)==a['original_sha256'];rel='../../../'+a['original_asset_path'];refs.append(dict(a,relative_path=rel,raw_sha256=sha(raw),raw_bytes=len(raw)))
  with tempfile.TemporaryDirectory(prefix='id-partisan-')as td:
   p=Path(td)/'source.pdf';p.write_bytes(raw);text=subprocess.check_output(['pdftotext','-layout',str(p),'-']).decode()
  save('source/'+a['id']+'-text.json.gz',dict(source_id=a['id'],raw_sha256=sha(raw),complete_text=text))
  national_texts[a['id']]=text
 fec_lines=[line for line in national_texts['fec-pres-2024'].splitlines()if re.match(r'\s*ID\s',line)];nums=[int(x.replace(',',''))for line in fec_lines[1:]for x in line.split()[1:]];assert nums[-1]==905057
 expected=[1577,274972,1230,2973,1026,12812,514,4462,605246,3,242];assert sorted(nums[:-1])==sorted(expected)
 ht=national_texts['house-clerk-2024'];start=ht.index('IDAHO');end=ht.index('FOR UNITED STATES REPRESENTATIVE',start);houseblock=ht[start:end];housevalues=[int(x.replace(',',''))for x in re.findall(r'\.{3,}\s+([\d,]+)',houseblock)];assert housevalues==[605246,274972,18555,11194,4462,1577,1215,245]and sum(housevalues)==917466
 save('source/national-control-reconciliation.json',dict(FEC_literal_ID_lines=fec_lines,FEC_named_counts=nums[:-1],FEC_valid_total=905057,HouseClerk_literal_Idaho_presidential_block=houseblock,HouseClerk_category_counts=housevalues,HouseClerk_total=917466,difference=12409,noncandidate_over=1215,noncandidate_under=11194,no_vote_rescaling=True))
 review=json.loads((NEWS/'coordinator-oct19-recheck/current-ballot-original-review.json').read_text());a=review['original_source'];path=STATE/a['asset_path'];b=path.read_bytes();raw=gzip.decompress(b);assert sha(b)==a['stored_sha256']and sha(raw)==a['raw_sha256']
 refs.append(dict(a,relative_path='../news/coordinator-oct19-recheck/'+path.name))
 with tempfile.TemporaryDirectory(prefix='id-ballot-')as td:
  p=Path(td)/'ballot.pdf';p.write_bytes(raw);text=subprocess.check_output(['pdftotext','-layout',str(p),'-']).decode();subprocess.check_call(['pdftoppm','-f','1','-singlefile','-scale-to','1600','-png',str(p),str(D/'source/ballot-page1')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 save('source/ballot-independent-review.json',dict(raw_sha256=sha(raw),complete_text=text,printed_choices=[['Todd Achilles','IND'],['Natalie M Fleming','IND'],['Matt Loesby','LIB'],['Jim Risch','REP']],scope='Twin Falls LD24 published sample, November3 2026; no statewide/signed/later/write-in completeness or result IDs established',parent_chain=review['exact_primary_web_reader_chain'],receipts_reference='../news/coordinator-oct19-recheck/acquisition-ballot-stage-v3.json',viewed_whole_page=True))
 save('source/additional-reused-originals.json',refs)
 a=next(a for a in json.loads((D/'source/independent-reference-receipts.json').read_text())if a['id']=='actual-2022-primary-governor-writeins');raw=gzip.decompress((D/a['relative_path']).read_bytes());assert sha(raw)==a['raw_sha256']
 with tempfile.TemporaryDirectory(prefix='id-primary-')as td:
  p=Path(td)/'primary.pdf';p.write_bytes(raw);text=subprocess.check_output(['pdftotext','-layout',str(p),'-']).decode()
 save('source/2022-writein-scope-disagreement.json',dict(general_workbook_candidate='Lisa Marie (W/I)',general_workbook_party='IND',general_workbook_votes=67,HTML_table_index=0,HTML_candidate='Lisa Marie',HTML_votes=46,HTML_scope='Unexplained publication/scope disagreement; generic page heading/links do not establish primary stage',HTML_original_receipt=next(a for a in receipts if a['id']=='stats-2022'),HTML_positions='2022-statistics-tables.json / table_index0 (original table order, zero based)',distinct_primary_PDF_receipt=a,distinct_primary_PDF_complete_text=text,primary_candidates={'Ryan Cole':22,'David Reilly':21,'Shelby Rognstad':6712},primary_not_merged=True))
 for a in receipts:
  if a['id'].startswith('law-'):
   t=gzip.decompress((D/a['stored_path']).read_bytes()).decode();i=t.find('34-'+a['id'].split('34-')[-1]+'.&nbsp;');part=t[i:t.find('History:',i)];save('source/'+a['id']+'-text.json',dict(source_id=a['id'],text=html.unescape(re.sub('<[^>]+>',' ',part)).strip()))
 # Canvass PDF independently checks all 985 vectors + statewide 13-category control.
 m={a['id']:a for a in json.loads((NEWS/'manifest.json').read_text())};a=m['sos-2024-canvass'];raw=gzip.decompress((NEWS/a['asset']).read_bytes())
 with tempfile.TemporaryDirectory(prefix='id-canvass-')as td:
  p=Path(td)/'source.pdf';p.write_bytes(raw);text=subprocess.check_output(['pdftotext','-layout',str(p),'-']).decode()
 (D/'source/2024-canvass-text.txt.gz').write_bytes(gzip.compress(text.encode(),mtime=0))
 records=[]
 for pi,page in enumerate(text.split('\f')[3:29],4):
  for li,line in enumerate(page.splitlines(),1):
   matches=list(re.finditer(r'(?<!\S)\d[\d,]*(?!\S)',line))
   if len(matches)<13:continue
   tail=matches[-13:]
   if re.sub(r'[\d,\s]','',line[tail[0].start():]):continue
   prefix=line[:tail[0].start()].strip();vals=[int(m.group().replace(',',''))for m in tail]
   if not prefix:continue
   records.append(dict(pdf_page=pi,text_line=li,prefix=prefix,values=vals,literal_line=line))
 units=json.loads(gzip.decompress((D/'source/native-units.json.gz').read_bytes()));u24=[u for u in units if u['contest']=='2024-president'];mapped=[];errors=[]
 for r in records:
  if r['prefix'].startswith('Race Total'):continue
  found=[u for u in u24 if r['prefix']==u['county'].removesuffix(' County')+' '+u['label']or re.sub(r'\s+',' ',r['prefix'])==u['county'].removesuffix(' County')+' '+u['label']]
  # PDF spacing differs; compare collapsed whitespace on both sides explicitly.
  if not found:found=[u for u in u24 if re.sub(r'\s+',' ',r['prefix'])==re.sub(r'\s+',' ',u['county'].removesuffix(' County')+' '+u['label'])]
  typography={('Bingham    MORGAN’S PASTURE 28',12):4045,('Cassia       121 Starrh’s Ferry',17):6463}
  if not found and (r['prefix'],r['pdf_page'])in typography:
   found=[u for u in u24 if u['row']==typography[r['prefix'],r['pdf_page']]]
   r['explicit_typographic_correspondence']={'pdf_prefix':r['prefix'],'xlsx_label':found[0]['label'],'xlsx_row':found[0]['row'],'reason':'curly apostrophe PDF versus ASCII apostrophe OOXML; original strings preserved'}
  if len(found)!=1:errors.append(r);continue
  u=found[0];byname={c['name']:c['votes']for c in u['candidates']+u['noncandidate']};order=['Joel Skousen','Kamala D. Harris','Claudia De la Cruz','Jill Stein','Randall Terry','Robert F Kennedy Jr.','Shiva Ayyadurai','Chase Oliver','Donald J. Trump','Overvotes','Undervotes','Brian Larry Kienitz (Write-In)','Peter Sonski (Write-In)'];expected=[byname[n]for n in order];assert r['values']==expected,(r,u);mapped.append(dict(r,unit_id=u['unit_id']))
 state=next(r for r in records if r['prefix'].startswith('Race Total'));expected=[sum(next(c['votes']for c in u['candidates']+u['noncandidate']if c['name']==name)for u in u24)for name in order];assert state['values']==expected
 save('source/2024-pdf-reconciliation.json',dict(records=mapped,unmatched_pdf_rows=errors,matched=len(mapped),expected=985,state=state,state_values_match=True,qualification='PDF label spacing collapse is explicit within same publication; no cross-year or current geometry join.'))
 print('PDF matched',len(mapped),'unmatched',len(errors))
if __name__=='__main__':main()
