#!/usr/bin/env python3
"""Original-first Colorado extraction. Standard-library code; pdftotext controls replays separate."""
from pathlib import Path
from collections import Counter,defaultdict
from html.parser import HTMLParser
import csv,io,gzip,json,hashlib,re,zipfile,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent; N=D.parent/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def gzjson(p,x):p.write_bytes(gzip.compress(('\n'.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))for r in x)+'\n').encode(),mtime=0))
def csvout(p,rows):
 rows=list(rows);s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);b=s.getvalue().encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None;self.struck=False;self.links=[]
 def handle_starttag(self,t,a):
  if t=='a':self.links.append(dict(a))
  if t=='tr':self.row=[];self.struck=False
  if t in ('td','th'):self.cell=[]
  if t in ('s','strike','del')or 'line-through'in dict(a).get('style',''):self.struck=True
 def handle_endtag(self,t):
  if t in ('td','th')and self.cell is not None:
   if self.row is not None:self.row.append(' '.join(''.join(self.cell).split()))
   self.cell=None
  if t=='tr'and self.row is not None:self.rows.append(dict(cells=self.row,struck=self.struck));self.row=None
 def handle_data(self,s):
  if self.cell is not None:self.cell.append(s)
def main():
 mf={r['id']:r for r in json.loads((N/'manifest.json').read_bytes())};pins=[]
 def raw(sid):
  a=mf[sid];b=(N/a['asset']).read_bytes();assert sha(b)==a['stored_sha256'];v=gzip.decompress(b);assert sha(v)==a['raw_sha256']and len(v)==a['bytes'];pins.append(dict(a,path='../news/'+a['asset']));return v
 # Every published county+native candidate cell and hierarchy retained; source totals stay separate.
 allrows=[];long=[];contexts=[];state=[];pages={};summaries=[]
 for year,kind,cid in [(2024,'president','26499'),(2022,'senate','25990'),(2020,'senate','3602')]:
  sid=f'sos-history-observed-{year}-{kind}-table-csv';rows=list(csv.reader(io.StringIO(raw(sid).decode('utf-8-sig'))));header,parties=rows[:2];n=len(header)-4
  page=raw(f'sos-history-observed-{year}-{kind}-contest').decode();page=json.loads(re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',page,re.S)[1])['props']['pageProps'];pages[str(year)]=page
  assert page['contest']['id']==cid and not page['contest']['isRunoff'];candidate_objects=page['contest']['candidates'];assert len({c['id']for c in candidate_objects})==len(candidate_objects)
  parent=None;bycounty={};native=defaultdict(list);state_row=None
  for pos,r in enumerate(rows[2:],3):
   assert len(r)==len(header);level,label=r[:2];vals=list(map(int,r[2:]));assert min(vals)>=0 and sum(vals[:n])==vals[n]==vals[n+1]
   if level=='County':parent=label;assert label not in bycounty
   county=parent if level=='Precinct'else label if level=='County'else''
   nativeid=label if level=='Precinct'else'';key=f'CO|{year}|{cid}|{county}|{nativeid}'
   obj=dict(year=year,contest_id=cid,source_id=sid,record_ordinal=pos,level_literal=level,county_literal=county,native_id_literal=nativeid,key=key,unit_literal=label,raw_fields=r,header_fields=header,party_fields=parties)
   allrows.append(obj)
   a,b=vals[:2];total=vals[n];pair=a+b
   rec=dict(year=year,contest_id=cid,source_id=sid,source_record=pos,key=key,level=level,county_literal=county,native_id_literal=nativeid,A_name=header[2],B_name=header[3],A=a,B=b,other=total-pair,pair_votes=pair,candidate_votes=total,pair_participation=pair/total if total else None,A_pair_share=a/pair if pair else None,A_minus_B_net=a-b,pair_margin_pp=100*(a-b)/pair if pair else None,all_candidate_margin_pp=100*(a-b)/total if total else None,source_Total_Votes_Cast=vals[n],source_Total_Ballots_Cast=vals[n+1],administrative_ballots=None,registered_voters=None,active_voters=None,inactive_voters=None,undervotes=None,overvotes=None,blank_votes=None,method=None,method_status='not supplied; source hasVoteChannels='+str(page['contest']['hasVoteChannels']),candidate_vector_json=json.dumps(dict(zip(header[2:-2],vals[:n])),ensure_ascii=False,separators=(',',':')))
   if level=='County':bycounty[label]=rec
   elif level=='Precinct':native[parent].append(rec);contexts.append(rec)
   elif level=='State':assert state_row is None;state_row=rec;state.append(rec)
   else:raise AssertionError(level)
   for col,v in enumerate(vals[:n],3):
    name=header[col-1];cs=[c for c in candidate_objects if c['displayName']==name];assert len(cs)==1;c=cs[0]
    long.append(dict(year=year,contest_id=cid,level=level,key=key,source_id=sid,source_record=pos,source_column=col,candidate_literal=name,party_literal=parties[col-1],candidate_in_contest_id=c['id'],candidate_id=c['candidate']['id'],isWriteIn_literal=c['isWriteIn'],isMasked_literal=c['isMasked'],pseudocandidate_literal=c['candidate']['pseudocandidate'],votes=v))
  assert len(bycounty)==len(native)==64
  for c,rs in native.items():
   assert len({r['key']for r in rs})==len(rs)
   for f in ['A','B','other','candidate_votes','source_Total_Votes_Cast','source_Total_Ballots_Cast']:assert sum(r[f]for r in rs)==bycounty[c][f]
  for f in ['A','B','other','candidate_votes']:assert sum(r[f]for r in bycounty.values())==state_row[f]
  summaries.append(dict(year=year,contest_id=cid,native=len([r for r in contexts if r['year']==year]),counties=64,candidate_columns=header[2:-2],party_columns=parties[2:-2],state=state_row,hasVoteChannels=page['contest']['hasVoteChannels'],hasBallots=page['hasBallots'],verifiedAt=page['contest']['verifiedAt']))
 # Original OOXML raw-cell lanes; literal shared-string indices, annotations and million-row tail.
 z=zipfile.ZipFile(io.BytesIO(raw('sos-2024-native-turnout')));ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};ss=[''.join(si.itertext())for si in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)];stats=[];explanatory=[];tail=Counter();numeric=Counter();inclusive=Counter();missing=Counter()
 with z.open('xl/worksheets/sheet1.xml')as f:
  for _,row in E.iterparse(f,events=['end']):
   if row.tag!='{'+ns['m']+'}row':continue
   number=int(row.attrib['r']);cells={}
   for c in row:
    v=c.find('m:v',ns);formula=c.find('m:f',ns);v=v.text if v is not None else None
    cells[re.sub(r'\d','',c.attrib['r'])]=dict(attributes=dict(c.attrib),raw_v=v,text=ss[int(v)]if c.get('t')=='s'and v is not None else v,formula=formula.text if formula is not None else None)
   row.clear();texts={k:v['text']for k,v in cells.items()if v['text']is not None}
   if texts.get('B','').isdigit()and 'A'in texts:
    values={};plain={}
    for col in 'CDEF':
     text=texts.get(col,'');plain[col]=int(text)if text.isdigit()else None;m=re.fullmatch(r'(\d+)\*',text);values[col]=int(m[1])if m else plain[col]
     if plain[col]is not None:numeric[col]+=plain[col]
     if values[col]is not None:inclusive[col]+=values[col]
     else:missing[col]+=1
    stats.append(dict(source_row=number,county_literal=texts['A'],native_id_literal=texts['B'],comparison_county_alias='Weld'if texts['A']=='Weld 'else texts['A'],raw_cells=cells,plain_numeric=plain,annotated_inclusive=values))
   elif set(texts)=={'G'}and texts['G']=='#VALUE!':tail[json.dumps(dict(type=cells['G']['attributes'].get('t'),text=texts['G']),sort_keys=True)]+=1
   elif cells:explanatory.append(dict(source_row=number,cells=cells))
 assert len(stats)==3183 and sum(tail.values())==1043548
 assert inclusive==Counter(C=4074612,D=508668,E=4583280,F=3241155)
 gzjson(D/'extracts/turnout-original-cells.jsonl.gz',stats);dump(D/'extracts/turnout-lanes.json',dict(plain_numeric_known=dict(numeric),annotated_inclusive_known=dict(inclusive),remaining_unprinted_fields=dict(missing),tail_counts=dict(tail),explanatory=explanatory))
 # Independent controls (original-byte extraction replay above), never peer data.
 controls=json.loads((D/'coordinator-historical-controls-preflight.json').read_bytes());verified=json.loads((D/'coordinator-public-native-export-preflight.json').read_bytes());countyrows=[r for r in allrows if r['level_literal']=='County'];records=[]
 for r in countyrows:
  year=r['year'];c=r['county_literal'];v=next(x for x in summaries if x['year']==year)
  vals=list(map(int,r['raw_fields'][2:]));a,b=vals[:2];total=vals[-2];pair=a+b
  if year==2024:
   vi=verified['contests'][0];block=vi['abstract_source_row_blocks'][0][c];reg,ballots=block['values'][:2];control_source='sos-2024-abstract';position=f"PDFpage{block['actual_PDFpage']}:line{block['line']}"
  elif year==2022:
   co=next(x for x in controls['HTML2022']['sos-2022-senate-abstract']['records']if x['county_literal']==c);reg,ballots=co['registered_voters'],co['ballots_cast'];control_source='sos-2022-senate-abstract';position='HTMLtable-row'+str(co['source_table_row'])
  else:
   co=controls['booklet2020']['PDF_page106'][c];reg,ballots=co['values'][:2];control_source='sos-2020-booklet-archive';position='PDFpage106:line'+str(co['line'])
  records.append(dict(year=year,contest_id=r['contest_id'],county_literal=c,key=r['key'],source_id=r['source_id'],source_record=r['record_ordinal'],A_name=r['header_fields'][2],B_name=r['header_fields'][3],A=a,B=b,other=total-pair,candidate_votes=total,pair_votes=pair,pair_participation=pair/total,A_pair_share=a/pair,pair_margin_pp=100*(a-b)/pair,all_candidate_margin_pp=100*(a-b)/total,A_minus_B_net=a-b,administrative_ballots=ballots,registered_voters=reg,ballot_minus_candidate_gap=ballots-total,blank_votes=None,undervotes=None,overvotes=None,control_source=control_source,control_position=position,candidate_vector_json=json.dumps(dict(zip(r['header_fields'][2:-2],vals[:-2])),ensure_ascii=False,separators=(',',':'))))
 for s in summaries:
  y=s['year'];rs=[r for r in records if r['year']==y];s['administrative_ballots']=sum(r['administrative_ballots']for r in rs);s['registered_voters']=sum(r['registered_voters']for r in rs)
  assert sum(r['candidate_votes']for r in rs)==s['state']['candidate_votes']
 # Current official roster, literal table positions and strike-through semantics.
 current=gzip.decompress((D/'source/current-candidates.gz').read_bytes()).decode();tp=Tables();tp.feed(current);roster=[dict(source_table_row=i+1,fields=x['cells'],struck=x['struck'])for i,x in enumerate(tp.rows)if len(x['cells'])>1 and x['cells'][1]=='US Senate'];assert len(roster)==9
 dump(D/'source/current-senate-roster.json',dict(source='current-candidates',source_updated_literal=re.findall(r'Last updated[^<]+',current),rows=roster,qualification='Final official list, not historical IDs; no live vendor ID mapping inferred.'))
 gzjson(D/'extracts/original-csv-records.jsonl.gz',allrows);csvout(D/'extracts/all-candidate-votes.csv.gz',long);csvout(D/'native-baselines.csv.gz',contexts);csvout(D.parent/'county-baselines.csv',records);dump(D/'source/historical-page-props.json',pages);dump(D/'source/reused-originals.json',pins);dump(D/'baseline-summary.json',summaries)
 # Complete descending order and exact integer threshold, never subset the state denominator.
 rs=sorted([r for r in contexts if r['year']==2024],key=lambda r:(-r['candidate_votes'],r['key']));den=sum(r['candidate_votes']for r in rs);cum=0;cross=None;ordered=[]
 for rank,r in enumerate(rs,1):
  prev=cum;cum+=r['candidate_votes'];row=dict(rank=rank,key=r['key'],county_literal=r['county_literal'],native_id_literal=r['native_id_literal'],candidate_votes=r['candidate_votes'],cumulative_votes=cum,minimum80_member=10*prev<8*den,source_record=r['source_record']);ordered.append(row)
  if cross is None and 10*cum>=8*den:cross=dict(rank=rank,key=r['key'],votes=r['candidate_votes'],cumulative=cum,previous=prev)
 csvout(D/'native-order.csv',ordered);dump(D/'priority-contract.json',dict(status='independent_provisional_pending_coordinator_acceptance',canonical_key='CO|year|contest_id|county_literal|native_id_literal',sort='candidate_votes descending; literal key ascending',denominator=den,native_count=len(rs),county_count=len({r['county_literal']for r in rs}),top15=sum(r['candidate_votes']for r in rs[:15]),crossing=cross,ordered_keys=[r['key']for r in rs],priority_keys=[r['key']for r in ordered if r['minimum80_member']],nonpriority_count=len(rs)-cross['rank'],nonpriority_votes=den-cross['cumulative']))
 print(json.dumps(dict(original_first=True,native={s['year']:s['native']for s in summaries},priority=cross,source_denominator=den)))
if __name__=='__main__':main()
