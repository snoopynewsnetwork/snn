"""Audit actual published Colorado CSVs by source hierarchy and independent controls."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json,re,subprocess,tempfile
from html.parser import HTMLParser
D=Path(__file__).resolve().parent;N=D/'news';X=N/'extracts'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(D)),bytes=len(b),sha256=sha(b))
class Next(HTMLParser):
 def __init__(self):super().__init__();self.on=False;self.parts=[]
 def handle_starttag(self,t,a):
  if t=='script'and dict(a).get('id')=='__NEXT_DATA__':self.on=True
 def handle_data(self,v):
  if self.on:self.parts.append(v)
 def handle_endtag(self,t):
  if t=='script':self.on=False
def main():
 X.mkdir(exist_ok=True);manifest={r['id']:r for r in json.loads((N/'manifest.json').read_bytes())};pins=[]
 def raw(sid):
  a=manifest[sid];b=(N/a['asset']).read_bytes();assert sha(b)==a['stored_sha256'];b=gzip.decompress(b);assert len(b)==a['bytes']and sha(b)==a['raw_sha256'];pins.append(a);return b
 original_controls=json.loads((D/'coordinator-historical-controls-preflight.json').read_bytes());result=[];positions=[];byyear={}
 for year,kind in [(2024,'president'),(2022,'senate'),(2020,'senate')]:
  sid=f'sos-history-observed-{year}-{kind}-table-csv';pageid=f'sos-history-observed-{year}-{kind}-contest';h=Next();h.feed(raw(pageid).decode());page=json.loads(''.join(h.parts))['props']['pageProps'];contest=page['contest'];rr=list(csv.reader(io.StringIO(raw(sid).decode('utf-8-sig'))));header,parties=rr[:2];n=len(header)-4;assert len(set(header[2:-2]))==n and header[-2:]==['Total Votes Cast','Total Ballots Cast'];county={};children=collections.defaultdict(list);parent=None;state=None;rowchecks=0;candidate_checks=0
  for ordinal,r in enumerate(rr[2:],3):
   assert len(r)==len(header);assert r[0]in ['State','County','Precinct'];values=[int(v)for v in r[2:]];assert all(v>=0 for v in values);assert sum(values[:n])==values[n];assert values[n]==values[n+1]
   if r[0]=='State':assert state is None;state=dict(row=r,record_ordinal=ordinal)
   elif r[0]=='County':assert r[1]not in county;parent=r[1];county[parent]=dict(row=r,record_ordinal=ordinal)
   else:assert parent is not None;children[parent].append(dict(row=r,record_ordinal=ordinal))
   for j,v in enumerate(values,2):positions.append(dict(source_id=sid,record_ordinal=ordinal,column_ordinal=j+1,raw_field_literal=r[j],field_role='named_candidate'if j<len(header)-2 else'source_total_pseudocandidate',header_literal=header[j],party_header_literal=parties[j],level_literal=r[0],unit_literal=r[1],parent_county_literal=parent if r[0]=='Precinct'else None,value=v))
   rowchecks+=1
  assert len(county)==len(children)==64 and state is not None
  for c,rs in children.items():
   sums=[sum(int(r['row'][j])for r in rs)for j in range(2,len(header))];assert sums==[int(v)for v in county[c]['row'][2:]];candidate_checks+=n
  assert [sum(int(r['row'][j])for r in county.values())for j in range(2,len(header))]==[int(v)for v in state['row'][2:]]
  nativekeys=[(c,r['row'][1])for c,rs in children.items()for r in rs];dupes=[dict(county=c,precinct_literal=k,rows=count)for(c,k),count in collections.Counter(nativekeys).items()if count>1]
  flags=[dict(source_CandidateInContest_id=c['id'],source_candidate_id=c['candidate']['id'],name=c['displayName'],pseudocandidate_literal=c['candidate']['pseudocandidate'],isWriteIn=c['isWriteIn'],isMasked=c['isMasked'],nVotes=c['nVotes'])for c in contest['candidates']]
  for c in flags:assert c['name']in header and int(state['row'][header.index(c['name'])])==c['nVotes']
  official_compares=[];ballots=[]
  if year==2020:
   signed={(r['county_literal'],r['candidate_literal']):r for r in original_controls['signed2020']['candidate_rows']}
   left=original_controls['booklet2020']['PDF_page106']
   for c,r in county.items():
    for name in header[2:-2]:
     v=int(r['row'][header.index(name)]);original=signed[(c.upper(),name)];assert v==original['votes'];official_compares.append(dict(county=c,candidate=name,votes=v,original_PDFpage=original['page'],original_line=original['line']))
    actual=left[c]['values'][1];ballots.append(dict(county=c,public_CSV_Total_Ballots_Cast=int(r['row'][-1]),booklet_administrative_ballots=actual,CSV_minus_booklet=int(r['row'][-1])-actual))
  if year==2022:
   old=original_controls['HTML2022']['sos-2022-senate-abstract'];oldnames=[s.split(' (',1)[0]for s in old['header_literal'][3:-2]];assert len(oldnames)==n
   for oldrow in old['records']:
    c=oldrow['county_literal'];r=county[c]
    for name,v in zip(oldnames,oldrow['candidate_values']):assert int(r['row'][header.index(name)])==v;official_compares.append(dict(county=c,candidate=name,votes=v,original_HTML_table_row=oldrow['source_table_row']))
    ballots.append(dict(county=c,public_CSV_Total_Ballots_Cast=int(r['row'][-1]),official_HTML_administrative_ballots=oldrow['ballots_cast'],CSV_minus_official_HTML=int(r['row'][-1])-oldrow['ballots_cast']))
  info=dict(year=year,contest_id=contest['id'],event=contest['event'],office=contest['office'],verifiedAt_literal=contest['verifiedAt'],hasNestedPrecincts=page['hasNestedPrecincts'],hasBallots_page=page['hasBallots'],hasBallots_event=contest['event']['hasBallots'],hasVoteChannels=contest['hasVoteChannels'],full_CSV_records=len(rr),county_records=64,native_source_records=len(nativekeys),candidate_headers=header[2:-2],party_headers=parties[2:-2],source_state_vector=[int(v)for v in state['row'][2:-2]],candidate_total=int(state['row'][-2]),all_native_candidate_and_two_total_fields_close_county=True,county_candidate_field_comparisons=candidate_checks,duplicate_county_native_literal_keys=dupes,native_row_counts={c:len(rs)for c,rs in children.items()},source_candidate_and_pseudocandidate_objects=flags,independent_prior_official_candidate_comparisons=official_compares,administrative_ballot_scope_comparisons=ballots,
    qualifications=['EveryCSV Total Ballots Cast field literally duplicates candidateTotalVotesCast; page/event hasBallots=false. These fields are not adopted as administrative ballots, remaining votes or blank/under/over controls.','Historical app verifiedAt is a retained verification field, not an election-night upload/cadence clock.','Native literal numeric precinct strings and parent hierarchy are source navigation, not cross-year/November physical or reporting approval.','App isWriteIn/isMasked flags remain literal. Names in official source write-in columns are not reclassified from an appflag.'])
  result.append(info);byyear[year]=dict(county=county,children=children,header=header)
 # Independent2024 abstract source has presidential columns over five actualPDF
 # pages106--110 (printed103--107), not a presumed two-page table.
 pdf=raw('sos-2024-abstract')
 with tempfile.NamedTemporaryFile(suffix='.pdf')as p:
  p.write(pdf);p.flush();texts=subprocess.check_output(['pdftotext','-f','106','-l','110','-layout',p.name,'-']).decode().split('\f')
 counties=set(byyear[2024]['county']);blocks=[]
 (X/'2024-abstract-president-complete-PDFpages106-110.txt.gz').write_bytes(gzip.compress('\f'.join(texts).encode(),mtime=0))
 for k in [0,1,3]:
  block={}
  for line,text in enumerate(texts[k].splitlines(),1):
   a=re.split(r'\s{2,}',text.strip())
   if a[0]in counties:
    values=a[1:-1]if k==3 else a[1:];block[a[0]]=dict(actual_PDFpage=106+k,line=line,raw_line=text,values=[int(v.replace(',',''))for v in values])
  assert set(block)==counties;blocks.append(block)
 # Exact source-column correspondence, explicitly retained rather than fuzzy
 # national party/name normalization. Header spelling differences stay in text.
 h=byyear[2024]['header'];mapping=[[h.index(x)for x in [h[2],h[3],h[9],h[5],h[6]]],[h.index(x)for x in [h[8],h[7],h[4],h[12],h[11],h[13],h[10]]],[h.index(h[14]),h.index(h[15])]]
 checks=[];administrative=[]
 for c in sorted(counties):
  r=byyear[2024]['county'][c]['row'];count=0
  for k,(block,cols)in enumerate(zip(blocks,mapping)):
   values=block[c]['values'];vs=values[2:]if k==0 else values[:-1]if k==2 else values;assert len(vs)==len(cols)
   for col,v in zip(cols,vs):assert int(r[col])==v;checks.append(dict(county=c,CSV_header=h[col],votes=v,source_PDFpage=block[c]['actual_PDFpage'],source_line=block[c]['line']))
  assert int(r[-2])==blocks[2][c]['values'][-1]
  ballots=blocks[0][c]['values'][1];administrative.append(dict(county=c,CSV_Total_Ballots_Cast=int(r[-1]),abstract_administrative_ballots=ballots,CSV_minus_abstract=int(r[-1])-ballots))
 result[0]['independent_2024_abstract_candidate_comparisons']=checks;result[0]['administrative_ballot_scope_comparisons']=administrative;result[0]['abstract_source_row_blocks']=blocks;result[0]['explicit_CSV_header_correspondence_per_PDF_column_block']=[[h[i]for i in cols]for cols in mapping]
 # Prior raw-turnout preflight is explicitly a different source. Literal-key
 # diagnostics keep the one recorded Weld trailing-space alias separate.
 stats=json.loads((D/'coordinator-primary-preflight.json').read_bytes());lookup={};csvkeys={};aliases=[]
 for r in stats['all_native_source_rows']:
  c=r['county_literal'];alias=c.strip()if c=='Weld 'else c
  if alias!=c:aliases.append(dict(source_row=r['source_row'],literal=c,comparison_only_alias=alias))
  key=(alias,r['precinct_literal']);assert key not in lookup;lookup[key]=r
 for c,rs in byyear[2024]['children'].items():
  for r in rs:
   key=(c,r['row'][1]);assert key not in csvkeys;csvkeys[key]=r
 onlyCSV=[dict(county=c,native_literal=k,CSV_record=csvkeys[(c,k)]['record_ordinal'],candidate_votes=int(csvkeys[(c,k)]['row'][-2]))for c,k in sorted(csvkeys.keys()-lookup.keys())]
 onlyStats=[dict(county=c,native_literal=k,stats_source_row=lookup[(c,k)]['source_row'])for c,k in sorted(lookup.keys()-csvkeys.keys())]
 cross=dict(stats_original_sha256=stats['source']['raw_sha256'],stats_records=len(lookup),candidate_records=len(csvkeys),literal_pairs=len(lookup.keys()&csvkeys.keys()),source_county_trailing_space_aliases=aliases,CSV_only_literal_keys=onlyCSV,stats_only_literal_keys=onlyStats,qualification='Literal same-year key diagnostics only; sourceId/current reporting/physical scope equivalence not approved. No extra row gets invented count/registration/method values or allocated votes.')
 rawpos=b''.join((json.dumps(p,separators=(',',':'))+'\n').encode()for p in positions);xp=X/'public-historical-CSV-original-positions.jsonl.gz';xp.write_bytes(gzip.compress(rawpos,mtime=0));assert xp.stat().st_size<40000000
 out=dict(status='pass_bounded_published_historical_CSV_source_controls_only',source_pins=pins,contests=result,all_selected_numeric_source_positions=len(positions),native_candidate_positions=sum(r['native_source_records']*len(r['candidate_headers'])for r in result),independent2020_signed_candidate_cells=512,independent2022_HTML_candidate_cells=576,independent2024_PDF_candidate_cells=len(checks),separate2024_statistics_literal_key_diagnostics=cross,position_derivative_pin=pin(xp),current_feed_admitted=False,priority_accepted=False,current_geography_approved=False,
 qualification='The official archive/publichistoricalclient leads to actualSSRdownloadanchors with returned date/contest/candidate identities verified. Complete nativeCSVsourcepositions/hierarchy/flags/originalheaders remain retained and reconcile candidate controls. No hiddenAPIguessing, missingzero fill, method allocation, trueadministrativeballot adoption, exactremaining estimate, measuredlivecadence or November identity approval follows. Queued primary-source preparation does not complete either independent question or dispatch review.')
 p=D/'coordinator-public-native-export-preflight.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(report_pin=pin(p),source_positions=len(positions),native_candidate_positions=out['native_candidate_positions'],native_counts={r['year']:r['native_source_records']for r in result},independent_candidate_cells=512+576+len(checks),literal_stats_pairs=cross['literal_pairs'],CSV_only=len(onlyCSV),stats_only=len(onlyStats))))
if __name__=='__main__':main()
