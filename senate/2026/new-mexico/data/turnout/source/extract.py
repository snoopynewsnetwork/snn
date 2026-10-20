#!/usr/bin/env python3
"""Independent original-first extraction, with all CSV positions and literal values."""
from common import *
SPECS=[('2024-senate','14873','elstats-2024-senate','elstats-2024-senate-linked-csv'),('2020-senate','13251','elstats-observed-2020-senate-view','elstats-observed-2020-senate-native-csv'),('2022-governor','11090','elstats-observed-2022-governor-view','elstats-observed-2022-governor-native-csv'),('2024-president','14877','elstats-observed-2024-president-view','elstats-observed-2024-president-native-csv')]
num=lambda x:int(x.replace(',',''))if re.fullmatch(r'-?[0-9,]+',x)else None

def main():
 out={}
 for tag,cid,view,export in SPECS:
  raw=body(export);rr=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))));meta=Page(body(view)).next()['props']['pageProps'];n=len(rr[0])-4
  assert rr[0][-2:]==['Total Votes Cast','Total Ballots Cast'];assert rr[2][0]=='State'
  county=None;rows=[]
  for pos,r in enumerate(rr,1):
   assert len(r)==len(rr[0])
   if pos<3:continue
   level,label=r[:2]
   if level=='County':county=label
   assert level in ['State','County','Precinct']
   fields=[{'column_1based':j+1,'label':rr[0][j],'party_literal':rr[1][j],'literal':v,'value':num(v),'kind':'candidate'if j<2+n else 'printed_contest_total'if j==2+n else 'printed_ballot_total'}for j,v in enumerate(r)if j>=2]
   rows.append(dict(source_id=export,source_row_1based=pos,raw_row=r,level=level,county_literal=county if level!='State'else None,native_label=label,native_numeric_id=None,administrative=level=='Precinct'and label=='Voter Privacy',key=f'nm:elstats:{cid}:{county}:{label}'if level=='Precinct'else f'nm:elstats:{cid}:{level}:{label}',fields=fields,candidate_votes=sum(x['value']for x in fields[:n])if all(x['value']is not None for x in fields[:n])else None,known_candidate_sum=sum(x['value']for x in fields[:n]if x['value']is not None),method=None,registration=None,blank=None,undervotes=None,overvotes=None,write_in=None))
  assert len({x['key']for x in rows})==len(rows)
  counties=[r for r in rows if r['level']=='County'];native=[r for r in rows if r['level']=='Precinct'];state=rows[0];assert len(counties)==33
  for j in range(n+2):assert sum(c['fields'][j]['value']for c in counties)==state['fields'][j]['value']
  residuals=[]
  for c in counties:
   kids=[r for r in native if r['county_literal']==c['native_label']];known=[sum(r['fields'][j]['value']for r in kids if r['fields'][j]['value']is not None)for j in range(n+2)]
   residuals.append(dict(county=c['native_label'],source_row=c['source_row_1based'],native_row_count=len(kids),known_sums=known,county_minus_known=[x['value']-v for x,v in zip(c['fields'],known)],masked_cells=sum(f['value']is None for r in kids for f in r['fields']),masked_candidate_cells=sum(f['value']is None for r in kids for f in r['fields'][:n])))
  out[tag]=dict(contest_id=cid,source_id=export,raw_sha256=sha(raw),header_rows=rr[:2],candidate_count=n,metadata=meta,rows=rows,reconciliation=residuals)
 dump(D/'original-extract.json',out)
 methods={}
 for id in ['sos-2020-federal-csv','sos-2022-statewide-csv','sos-2024-federal-csv']:
  rr=list(csv.reader(io.StringIO(body(id).decode('utf-8-sig'))));header=rr[0];selected=[]
  for pos,row in enumerate(rr[1:],2):
   if len(row)<2:continue
   if row[1]not in ['United States Senator','Governor and Lieutenant Governor']:continue
   r=dict(zip(header,row));assert int(r['CandidateVotes'])==sum(int(r[x])for x in ['CandidateAbsenteeVotes','CandidateElectionDayVotes','CandidateEarlyVotes']);selected.append(dict(source_row_1based=pos,raw_row=row,fields=r))
  methods[id]=dict(source_id=id,header=header,all_source_rows=len(rr)-1,required_rows=selected,unavailable_not_zero=len(rr)==1)
 dump(D/'legacy-methods.json',methods)
 turnout={}
 for year in [2020,2022,2024]:
  id=f'turnout-{year}';b=body(id);s=b.decode();p=Page(b);text=p.plain();state=re.search(r'Ballots Cast ([\d,]+) Eligible Voters ([\d,]+)',text);assert state
  chunks=list(re.finditer(r'<div class="wrapper-inside">\s*<div class="provisional-results-wrapper">',s));counties=[];natives=[]
  for z,start in enumerate(chunks):
   end=chunks[z+1].start()if z+1<len(chunks)else len(s);part=s[start.start():end]
   if not re.search(r'countyid="([^"]+)"',part):continue
   name=re.search(r'<h1>(.*?)</h1>',part,re.S)[1];name=html.unescape(name);countyid=re.search(r'countyid="([^"]+)"',part)[1];native=[]
   pattern=r'<div class="(odd|even)">\s*<div class="county-precinct">(.*?)</div>\s*<div class="county-cast">\s*<span>(.*?)</span>\s*</div>\s*<div class="county-counted">\s*<span>(.*?)</span>\s*</div>\s*</div>'
   for k,m in enumerate(re.finditer(pattern,part,re.S),1):
    label,ballots,eligible=[html.unescape(x.strip())for x in m.group(2,3,4)];a=start.start()+m.start();e=start.start()+m.end();r=dict(key=f'nm:legacy:{year}:cty={countyid}:{label}',source_id=id,county_literal=name,county_id_literal=countyid,native_label=label,source_row_within_county=k,source_char_start=a,source_char_end=e,source_byte_start=len(s[:a].encode()),source_byte_end=len(s[:e].encode()),ballots_cast_literal=ballots,ballots_cast=num(ballots),eligible_voters_literal=eligible,eligible_voters=num(eligible),registration_status=None,registration_asof=None,method=None);native.append(r);natives.append(r)
   assert native
   counties.append(dict(county_literal=name,county_id_literal=countyid,source_char_start=start.start(),source_char_end=end,ballots_cast_native_sum=sum(r['ballots_cast']for r in native if r['ballots_cast']is not None),eligible_voters_native_sum=sum(r['eligible_voters']for r in native if r['eligible_voters']is not None),native_rows=len(native)))
  assert len(counties)==33
  turnout[str(year)]=dict(source_id=id,source_clock=re.search(r'Results last updated:(.*?) Statewide',text)[1],clock_timezone_literal='MT',state_ballots_cast=num(state[1]),state_eligible_voters=num(state[2]),native_ballots_sum=sum(r['ballots_cast']for r in natives if r['ballots_cast']is not None),native_eligible_voters_sum=sum(r['eligible_voters']for r in natives if r['eligible_voters']is not None),counties=counties,native_rows=natives)
 dump(D/'ballot-registration-extract.json',turnout)
 witness=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),basis='Turnout worker independently extracted retained original HTML/CSV entities, without running coordinator extractors or reading peer derivatives. Prompt/preflight figures were known but no private fields reconstructed.',peer_agent_id=None,peer_derivatives_read=False,files={p.name:dict(sha256=sha(p.read_bytes()),bytes=p.stat().st_size)for p in [D/'original-extract.json',D/'legacy-methods.json',D/'ballot-registration-extract.json']})
 if not(D/'original-first-witness.json').exists():dump(D/'original-first-witness.json',witness)
 print(json.dumps({k:dict(counties=len(v['counties']),native=len(v['native_rows']),state_ballots=v['state_ballots_cast'],native_ballots=v['native_ballots_sum'],state_eligible=v['state_eligible_voters'],native_eligible=v['native_eligible_voters_sum'])for k,v in turnout.items()}))
if __name__=='__main__':main()
