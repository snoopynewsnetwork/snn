#!/usr/bin/env python3
"""Independent Florida primary parsing; no peer-extracted counts are inputs."""
import csv,gzip,hashlib,io,json,re,subprocess,zipfile
from collections import Counter,defaultdict
from html.parser import HTMLParser
from pathlib import Path
D=Path(__file__).resolve().parent
FIELDS=['county_code','county_name','election_number','election_date','election_name','precinct_id','polling_location','registered_total','registered_rep','registered_dem','registered_other','contest_name','district','contest_code','candidate_name','candidate_party','candidate_fvrs_id','candidate_doe_id','votes']
def sha(b):return hashlib.sha256(b).hexdigest()
def writejson(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def csvwrite(p,rows,fields=None):
 rows=list(rows);fields=fields or list(rows[0]);op=io.TextIOWrapper(gzip.GzipFile(filename=str(p),mode='wb',mtime=0),encoding='utf-8',newline='') if p.suffix=='.gz' else p.open('w',encoding='utf-8',newline='')
 with op as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
class Tables(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.rows=[];self.row=None;self.cell=None;self.links=[]
 def handle_starttag(self,t,a):
  if t.lower()=='tr':self.row=[]
  if t.lower() in ('td','th') and self.row is not None:self.cell=[]
  if t.lower()=='br' and self.cell is not None:self.cell.append(' ')
  if t.lower()=='a':self.links.append(dict(a))
 def handle_data(self,s):
  if self.cell is not None:self.cell.append(s)
 def handle_endtag(self,t):
  if t.lower() in ('td','th') and self.cell is not None:
   self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
  if t.lower()=='tr' and self.row is not None:self.rows.append(self.row);self.row=None

def official_tables():
 result=[];inventory=[]
 for year,office in [(2024,'senate'),(2022,'senate'),(2024,'president'),(2020,'president')]:
  sid=f'dos-{office}-{year}';raw=gzip.decompress((D/'source'/f'{sid}.body.gz').read_bytes());receipt=json.loads((D/'source'/f'{sid}.receipt.json').read_text());assert receipt['status']==200 and sha(raw)==receipt['raw_sha256']
  parser=Tables();parser.feed(raw.decode('cp1252'));header=next(x for x in parser.rows if x and x[0]=='County');counties=[]
  for i,row in enumerate(parser.rows,1):
   if not row or row[0] in ['County','Total','% Votes'] or len(row)!=len(header):continue
   if not all(re.fullmatch(r'[\d,]+',s) for s in row[1:]):continue
   counties.append(row[0])
   for pos,(h,n) in enumerate(zip(header[1:],row[1:]),1):
    match=re.fullmatch(r'(.*?)\s*\(([^)]+)\)',h);assert match,h
    result.append({'year':year,'contest':office,'stage':'general','county':row[0],'candidate_position':pos,'candidate_name':match[1].strip(),'party':match[2],'votes':int(n.replace(',','')),'source_id':sid,'source_tr_1based':i,'source_column_1based':pos+1,'raw_sha256':sha(raw)})
  assert len(counties)==67 and len(set(counties))==67,(sid,len(counties))
  totals=next(x for x in parser.rows if x and x[0]=='Total'); controls=[]
  for pos,h in enumerate(header[1:],1):
   n=sum(a['votes'] for a in result if a['source_id']==sid and a['candidate_position']==pos);assert n==int(totals[pos].replace(',',''));controls.append({'header':h,'votes':n})
  inventory.append({'source_id':sid,'raw_sha256':sha(raw),'tr_count':len(parser.rows),'county_count':len(counties),'header':header,'controls':controls})
 csvwrite(D/'official-county-candidates.csv',result);writejson(D/'source/county-html-parse.json',inventory);return result

def native():
 refs=json.loads((D/'source/external-source-references.json').read_text());native_rows=[];candidate_counties=Counter();candidate_states=Counter();members=[];units={}; all_inventory=[]
 source_ids={2024:'dos-2024-precinct-official-storage-alias',2022:'dos-2022-precinct-official-storage-alias',2020:'dos-2020-precinct-zip'}
 for year,sid in source_ids.items():
  ref=next(x for x in refs if x['id']==sid);p=D/ref['asset'];raw=gzip.decompress(p.read_bytes());assert sha(raw)==ref['raw_sha256'];zf=zipfile.ZipFile(io.BytesIO(raw));assert zf.testzip() is None
  for info in zf.infolist():
   body=zf.read(info);encoding='utf-8-sig'
   try:s=body.decode(encoding)
   except UnicodeDecodeError:encoding='cp1252';s=body.decode(encoding)
   recount='recount' in info.filename.lower();allc=Counter();selected=0;cc=set();geos=set(); colvals=[set() for _ in FIELDS]
   for rownum,line in enumerate(s.splitlines(),1):
    row=line.split('\t');assert len(row)==19,(info.filename,rownum,len(row));cc.add((row[0],row[1]));allc[(row[11],row[12],row[13])]+=1;geos.add(tuple(row[:7]))
    for j,v in enumerate(row):colvals[j].add(v)
    contest='senate' if row[13]=='120000' else 'president' if row[13]=='100000' else None
    if not contest or (year==2022 and contest!='senate') or (year==2020 and contest!='president'):continue
    selected+=1
    uid=json.dumps([str(year),contest,row[0],row[2],row[5],row[6]],separators=(',',':'),ensure_ascii=False);key=tuple(row[14:18]);n=int(row[18]);category={'900':'generic_writein_marks','901':'overvotes','902':'undervotes'}.get(row[17],'named_candidate')
    record={'source_id':sid,'source_member':info.filename,'source_row_1based':rownum,'base_selected':not recount,'native_key':uid,**dict(zip(FIELDS,row)),'category':category}
    native_rows.append(record)
    if recount:continue
    candidate_counties[(year,contest,row[0],row[1],*key,category)]+=n;candidate_states[(year,contest,*key,category)]+=n
    if uid not in units:units[uid]={'year':year,'contest':contest,'county_code':row[0],'county':row[1],'election_number':row[2],'precinct_id':row[5],'polling_location':row[6],'native_key':uid,'A':0,'B':0,'other_printed_candidates':0,'generic_writein_marks':0,'overvotes':0,'undervotes':0,'candidate_keys':set(),'registration_contexts':set(),'source_positions':[],'method':'not_provided_in_19field_schema','native_label_method_hint':bool(re.search(r'absent|early|mail|provis|central|EV\b|VBM\b',row[5]+' '+row[6],re.I))}
    u=units[uid];u['source_positions'].append([info.filename,rownum]);u['registration_contexts'].add(tuple(row[7:11]));u['candidate_keys'].add(key)
    if category!='named_candidate':u[category]+=n
    elif row[15]=='DEM':u['A']+=n
    elif row[15]=='REP':u['B']+=n
    else:u['other_printed_candidates']+=n
   members.append({'year':year,'source_id':sid,'source_member':info.filename,'source_zip_sha256':sha(raw),'member_sha256':sha(body),'member_bytes':len(body),'member_crc32':f'{info.CRC:08x}','encoding':encoding,'recount_excluded':recount,'source_rows':sum(allc.values()),'county_identities':sorted(cc),'all_office_native_contexts':len(geos),'selected_rows':selected,'all_contest_inventory':[{'contest_name':k[0],'district':k[1],'contest_code':k[2],'rows':n} for k,n in sorted(allc.items())],'distinct_field_counts':dict(zip(FIELDS,map(len,colvals)))})
 for u in units.values():
  for k in ['candidate_keys','registration_contexts']:u[k]=json.dumps(sorted(u[k]),ensure_ascii=False,separators=(',',':'))
  u['source_positions']=json.dumps(u['source_positions'],separators=(',',':'));u['pair_total']=u['A']+u['B'];u['raw_mark_total']=u['pair_total']+u['other_printed_candidates']+u['generic_writein_marks'];u['registration_context_count']=len(json.loads(u['registration_contexts']))
 csvwrite(D/'native-source-rows.csv.gz',native_rows)
 csvwrite(D/'native-units.csv.gz',sorted(units.values(),key=lambda x:x['native_key']))
 names=['year','contest','county_code','county','candidate_name','party','candidate_fvrs_id','candidate_doe_id','category']
 csvwrite(D/'compiled-county-candidates.csv',[dict(zip(names,k),votes=n) for k,n in sorted(candidate_counties.items())])
 names=['year','contest','candidate_name','party','candidate_fvrs_id','candidate_doe_id','category']
 csvwrite(D/'compiled-state-candidates.csv',[dict(zip(names,k),votes=n) for k,n in sorted(candidate_states.items())])
 writejson(D/'source/zip-member-inventory.json',members)
 summary=[]
 for year,contest in [(2024,'senate'),(2024,'president'),(2022,'senate'),(2020,'president')]:
  us=[u for u in units.values() if u['year']==year and u['contest']==contest];summary.append({'year':year,'contest':contest,'counties':len({u['county_code'] for u in us}),'native_units':len(us),'method_not_provided':len(us),'label_hints_only':sum(u['native_label_method_hint'] for u in us),'A':sum(u['A'] for u in us),'B':sum(u['B'] for u in us),'other_printed_candidates':sum(u['other_printed_candidates'] for u in us),'generic_writein_marks':sum(u['generic_writein_marks'] for u in us),'overvotes':sum(u['overvotes'] for u in us),'undervotes':sum(u['undervotes'] for u in us),'multiple_registration_contexts':sum(u['registration_context_count']!=1 for u in us)})
 writejson(D/'native-coverage.json',summary);print(json.dumps(summary,indent=2));return units
if __name__=='__main__':
 official_tables();native()
