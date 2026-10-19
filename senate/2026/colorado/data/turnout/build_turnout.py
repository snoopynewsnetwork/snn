#!/usr/bin/env python3
"""Independent raw-source Colorado extraction. Python stdlib + pdftotext; no coordinator values imported."""
from pathlib import Path
from html.parser import HTMLParser
import json,gzip,csv,io,hashlib,re,collections,subprocess,zipfile,xml.etree.ElementTree as ET
O=Path(__file__).resolve().parent;S=O/'source';X=O/'extracts';N=O.parent/'news';ROOT=O.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def gz(path,obj):path.write_bytes(gzip.compress(('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))for x in obj)+'\n').encode(),mtime=0))
M={a['id']:a for a in json.loads((N/'manifest.json').read_text())}
def raw(sid):
 a=M[sid];z=(N/a['asset']).read_bytes();b=gzip.decompress(z);assert sha(z)==a['stored_sha256'] and sha(b)==a['raw_sha256'];return b
def acquired(sid):return gzip.decompress((S/(sid+'.body.gz')).read_bytes())
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.tables=[];self.table=None;self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t=='table':self.table=[]
  if t=='tr'and self.table is not None:self.row=[]
  if t in ['td','th']and self.row is not None:self.cell=[]
 def handle_data(self,d):
  if self.cell is not None:self.cell.append(d)
 def handle_endtag(self,t):
  if t in ['td','th']and self.cell is not None:self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
  if t=='tr'and self.row is not None:self.table.append(self.row);self.row=None
  if t=='table'and self.table is not None:self.tables.append(self.table);self.table=None
def tables(b):p=Tables();p.feed(b.decode());return p.tables
def pdf(sid):
 t=subprocess.check_output(['pdftotext','-layout','-','-'],input=raw(sid)).decode();(X/(sid+'.txt.gz')).write_bytes(gzip.compress(t.encode(),mtime=0));return t.split('\f')
def numeric(v):return int(v.replace(',',''))
def percent(n,d):return f'{n*100/d:.8f}'
def rank(rows,field):
 a=sorted(rows,key=lambda r:(-r[field],r['key']));total=sum(r[field]for r in a);cum=0
 for i,r in enumerate(a,1):
  r=dict(r);cum+=r[field];a[i-1]=dict(r,rank=i,cumulative_votes=cum,share_numerator=r[field],share_denominator=total)
 k=next(i for i,r in enumerate(a,1)if 5*r['cumulative_votes']>=4*total)
 return dict(total=total,unit_count=len(a),top15_votes=sum(r[field]for r in a[:15]),top15_share_fraction=[sum(r[field]for r in a[:15]),total],minimum80_count=k,preceding_count=k-1,preceding_votes=a[k-2]['cumulative_votes']if k>1 else 0,crossing_key=a[k-1]['key'],crossing_votes=a[k-1][field],priority_votes=a[k-1]['cumulative_votes'],remainder_count=len(a)-k,remainder_votes=total-a[k-1]['cumulative_votes'],full_order=a)
def main():
 X.mkdir(exist_ok=True);years={};allrows=[];catalog={};checks=[]
 for y,kind in [(2024,'president'),(2022,'senate'),(2020,'senate')]:
  sid=f'sos-history-observed-{y}-{kind}-table-csv';page=f'sos-history-observed-{y}-{kind}-contest';b=raw(sid);rr=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))));head,party=rr[:2];n=len(head)-4
  p=json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',raw(page).decode()).group(1))['props']['pageProps'];c=p['contest'];catalog[y]=dict(source_page=page,source_csv=sid,page_properties=p,header=head,party_header=party)
  assert c['event']['startDate'][:10]=={2024:'2024-11-05',2022:'2022-11-08',2020:'2020-11-03'}[y]
  assert not c['hasVoteChannels'] and not p['hasBallots']
  county=None;rs=[]
  for ordinal,r in enumerate(rr[2:],3):
   assert len(r)==len(head);vs=[int(x)for x in r[2:]];assert sum(vs[:n])==vs[-2]==vs[-1]
   if r[0]=='County':county=r[1]
   level=r[0];key=f'CO|{y}|{c["id"]}|'+ ('State'if level=='State'else r[1]if level=='County'else county+'|'+r[1])
   z=dict(year=y,contest_id=c['id'],source_id=sid,source_record=ordinal,key=key,level_literal=level,county_literal=county if level=='Precinct'else r[1]if level=='County'else None,native_id_literal=r[1]if level=='Precinct'else None,raw_fields=r,candidate_values=vs[:n],candidate_votes=sum(vs[:n]),source_TOTAL_VOTES=vs[-2],source_TOTAL_BALLOTS=vs[-1],method=None,method_scope='all methods combined; no source vote channels',blank=None,undervote=None,overvote=None,administrative_ballots=None,registration=None)
   rs.append(z);allrows.append(z)
  state=[r for r in rs if r['level_literal']=='State'];parents=[r for r in rs if r['level_literal']=='County'];native=[r for r in rs if r['level_literal']=='Precinct'];assert len(state)==1 and len(parents)==64 and len({r['key']for r in native})==len(native)
  for par in parents:
   children=[r for r in native if r['county_literal']==par['county_literal']];assert children
   assert [sum(r['candidate_values'][i]for r in children)for i in range(n)]==par['candidate_values']
  assert [sum(r['candidate_values'][i]for r in parents)for i in range(n)]==state[0]['candidate_values']
  for obj in c['candidates']:
   j=head.index(obj['displayName'])-2;assert state[0]['raw_fields'][j+2]==str(obj['nVotes'])
  years[y]=dict(rows=rs,counties=parents,native=native,state=state[0],headers=head,parties=party)
  # Current re-download must reproduce complete historical original byte hashes.
  assert sha(acquired(f'current-{y}-{kind}-csv'))==sha(b)
  checks.append(dict(year=y,native=len(native),counties=64,candidate_total=state[0]['candidate_votes'],candidate_columns=n,all_native_candidate_cells_balanced=True,current_download_identical=True))
 dump(X/'candidate-universes.json',catalog)
 candidate_rows=[]
 for y,cat in catalog.items():
  named_wi={2024:{'Peter Sonski and Lauren Onak','Claudia De la Cruz and Karina Garcia','Chris Garrity and Cody Ballard','Shiva Ayyadurai and Crystal Ellis','Bill Frankel and Steve Jenkins','Brian Anthony Perry and Mark Sbani'},2022:{'Tom Harvey','Joanne Rock','John Carleton Rutledge'},2020:{'Bruce Lohmiller','Danny Skelly','Michael Sanchez'}}[y]
  for obj in cat['page_properties']['contest']['candidates']:
   name=obj['displayName'];j=cat['header'].index(name);candidate_rows.append(dict(year=y,contest_id=cat['page_properties']['contest']['id'],candidate_in_contest_id=obj['id'],candidate_id=obj['candidate']['id'],display_name=name,csv_column_ordinal=j+1,party_header=cat['party_header'][j],party_object_name=(obj['party']or{}).get('name'),pseudocandidate=obj['candidate']['pseudocandidate'],app_isWriteIn=obj['isWriteIn'],app_isMasked=obj['isMasked'],printed_write_in_label=name in named_wi,printed_scope='explicit named Write-In abstract column'if name in named_wi else 'no printed Write-In marker; not a legal-status inference',state_votes=obj['nVotes']))
 with (X/'candidate-universe.csv').open('w')as f:
  w=csv.DictWriter(f,fieldnames=list(candidate_rows[0]));w.writeheader();w.writerows(candidate_rows)
 gz(X/'historical-source-rows.jsonl.gz',allrows)
 # County authority PDF/HTML controls, extracted from original bytes independently.
 counties={r['county_literal']for r in years[2024]['counties']};ct=tables(acquired('census-colorado-codes'))[0];fips={r[6]:r[2]for r in ct[1:]};assert set(fips)==counties and len(set(fips.values()))==64;dump(X/'county-fips.json',dict(source='census-colorado-codes',vintage='2020 Census table; county identifiers only',mapping=fips));
 for yr in years.values():
  for rr in yr['rows']:rr['county_fips']=fips.get(rr['county_literal'])
 controls={y:{}for y in years};proof=[]
 p24=pdf('sos-2024-abstract');p20=pdf('sos-2020-booklet-archive');signed=pdf('sos-2020-signed-archive')
 def pdfrows(pages,page,width,percent_column=False,require_total=True):
  out={}
  for line,t in enumerate(pages[page-1].splitlines(),1):
   a=re.split(r'\s{2,}',t.strip())
   if a[0]not in counties|{'Total'}:continue
   v=a[1:-1]if percent_column else a[1:];assert len(v)==width,(page,a)
   out[a[0]]=dict(page=page,line=line,raw_line=t,values=[numeric(x)for x in v],raw_fields=a)
  assert set(out)==(counties|{'Total'} if require_total else counties),(page,len(out));return out
 h=years[2024]['headers'];blocks=[pdfrows(p24,106,7),pdfrows(p24,107,7,require_total=False),pdfrows(p24,109,3,True,False)];mapping=[[2,3,9,5,6],[8,7,4,12,11,13,10],[14,15]]
 for par in years[2024]['counties']:
  c=par['county_literal'];vals=[]
  for bi,(block,cols)in enumerate(zip(blocks,mapping)):
   vv=block[c]['values'];vv=vv[2:]if bi==0 else vv[:-1]if bi==2 else vv
   for col,v in zip(cols,vv):assert v==int(par['raw_fields'][col]);proof.append(dict(year=2024,county=c,header=h[col],votes=v,source='sos-2024-abstract',page=block[c]['page'],line=block[c]['line']))
  assert blocks[2][c]['values'][-1]==par['candidate_votes'];controls[2024][c]=dict(registered=blocks[0][c]['values'][0],ballots=blocks[0][c]['values'][1],source='sos-2024-abstract',page=106,line=blocks[0][c]['line'])
 # All 2024 candidate footers include continuation-only pages108/110.
 for bi,pg in [(1,108),(2,110)]:
  line=next(t for t in p24[pg-1].splitlines()if t.startswith('Total'));v=re.split(r'\s{2,}',line.strip())[1:];v=v[:-1]if bi==2 else v
  vv=[numeric(x)for x in v];expected=[sum(blocks[bi][c]['values'][j]for c in counties)for j in range(len(vv))];assert vv==expected
 # Original HTML2022 whole tables and governor comparator retained, no unrelated office derivatives.
 html22={}
 for name in ['senate','governor']:
  sid='sos-2022-'+name+'-abstract';t=tables(raw(sid))[0];head=t[0];rows=t[1:-1];footer=t[-1];assert len(rows)==64 and footer[0]=='Total';html22[name]=dict(header=head,rows=rows,footer=footer)
  for j in range(1,len(head)-1):assert sum(numeric(r[j])for r in rows)==numeric(footer[j])
  for rownum,r in enumerate(rows,2):
   assert sum(numeric(x)for x in r[3:-2])==numeric(r[-2])
   if name=='senate':
    c=r[0];par=next(x for x in years[2022]['counties']if x['county_literal']==c);controls[2022][c]=dict(registered=numeric(r[1]),ballots=numeric(r[2]),source=sid,table_row=rownum)
    for label,v in zip(head[3:-2],r[3:-2]):
     name2=label.split(' (',1)[0];assert numeric(v)==int(par['raw_fields'][years[2022]['headers'].index(name2)]);proof.append(dict(year=2022,county=c,header=name2,votes=numeric(v),source=sid,table_row=rownum))
 dump(X/'2022-HTML-controls.json',html22)
 signed_lookup={}
 for page,t in enumerate(signed,1):
  for line,txt in enumerate(t.splitlines(),1):
   if not txt.startswith('United States Senator'):continue
   a=re.split(r'\s{2,}',txt.strip())
   if len(a)==5 and a[2]in{c.upper()for c in counties}:signed_lookup[(a[2],a[3])]=dict(page=page,line=line,raw_line=txt,votes=numeric(a[4]))
 assert len(signed_lookup)==512
 b20=[pdfrows(p20,106,7),pdfrows(p20,107,4,True)];names=['John W. Hickenlooper','Cory Gardner','Daniel Doyle','Stephan "Seku" Evans','Raymon Anthony Doane','Danny Skelly','Bruce Lohmiller','Michael Sanchez']
 for par in years[2020]['counties']:
  c=par['county_literal'];controls[2020][c]=dict(registered=b20[0][c]['values'][0],ballots=b20[0][c]['values'][1],source='sos-2020-booklet-archive',page=106,line=b20[0][c]['line'])
  for name,v in zip(names,b20[0][c]['values'][2:]+b20[1][c]['values'][:3]):
   assert v==int(par['raw_fields'][years[2020]['headers'].index(name)])==signed_lookup[(c.upper(),name)]['votes'];proof.append(dict(year=2020,county=c,header=name,votes=v,source='sos-2020-signed-archive',**{k:x for k,x in signed_lookup[(c.upper(),name)].items()if k!='votes'}))
 gz(X/'independent-candidate-controls.jsonl.gz',proof);gz(X/'historical-source-rows.jsonl.gz',allrows)
 # State totals/control footer verification includes registered and ballot fields.
 for y,bs in [(2024,blocks),(2020,b20)]:
  for j,f in [(0,'registered'),(1,'ballots')]:assert sum(r[f]for r in controls[y].values())==bs[0]['Total']['values'][j]
 # Separate active/registered county turnout pages; preserve exact denominators and footer.
 turnout={};turnout_positions=[]
 for y,pages,pgs in [(2024,p24,[181,182]),(2020,p20,[165,166])]:
  turnout[y]={}
  for pg,role in zip(pgs,['active','registered']):
   rows=pdfrows(pages,pg,2,True)
   for c in counties:
    v=rows[c];turnout[y].setdefault(c,{})[role]=v['values'][0];turnout[y][c]['ballots']=v['values'][1];turnout_positions.append(dict(year=y,county=c,role=role,**v))
   for j in range(2):assert sum(rows[c]['values'][j]for c in counties)==rows['Total']['values'][j]
  for c in counties:assert turnout[y][c]['registered']==controls[y][c]['registered']and turnout[y][c]['ballots']==controls[y][c]['ballots']
 for y in [2022,2020]:
  ts=tables(acquired(f'turnout-{y}'));assert len(ts)==2
  for tab,role in zip(ts,['active','registered']):
   assert len(tab)==66
   for j in [1,2]:assert sum(numeric(r[j])for r in tab[1:-1])==numeric(tab[-1][j])
   for pos,r in enumerate(tab[1:-1],2):
    c=r[0];turnout.setdefault(y,{}).setdefault(c,{})[role]=numeric(r[1]);turnout[y][c]['ballots']=numeric(r[2]);assert numeric(r[2])==controls[y][c]['ballots'];assert role!='registered'or numeric(r[1])==controls[y][c]['registered'];turnout_positions.append(dict(year=y,county=c,role=role,source=f'turnout-{y}',table_row=pos,raw_fields=r))
 gz(X/'turnout-control-positions.jsonl.gz',turnout_positions);dump(X/'county-administrative-controls.json',controls);dump(X/'county-turnout-registration.json',turnout)
 # All available native workbook records; sparse cell addresses/types/formulas retained.
 ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};z=zipfile.ZipFile(io.BytesIO(raw('sos-2024-native-turnout')));ss=[''.join(x.itertext())for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)];stats=[];other=[];tail=collections.Counter()
 for _,r in ET.iterparse(z.open('xl/worksheets/sheet1.xml'),events=['end']):
  if r.tag!='{'+ns['s']+'}row':continue
  cells={}
  for cell in r:
   v=cell.find('s:v',ns);f=cell.find('s:f',ns)
   if v is not None:cells[cell.attrib['r']]=dict(attributes=cell.attrib,value=v.text,decoded=ss[int(v.text)]if cell.get('t')=='s'else v.text,formula=f.text if f is not None else None)
  row=int(r.attrib['r']);r.clear();plain={re.sub(r'\d','',a):v['decoded']for a,v in cells.items()}
  if 'A'in plain and 'B'in plain and plain['B'].isdigit():
   c=plain['A'];alias='Weld'if c=='Weld 'else c;vals={k:int(plain[k])if k in plain and plain[k].lstrip('-').isdigit()else None for k in 'CDEF'};stats.append(dict(source_row=row,county_literal=c,comparison_county=alias,native_id_literal=plain['B'],cells=cells,active=vals['C'],inactive=vals['D'],total=vals['E'],ballots=vals['F'],turnout_literal=plain.get('G')))
  elif set(plain)=={'G'}:tail[str((next(iter(cells.values()))['attributes'].get('t'),plain['G']))]+=1
  elif cells:other.append(dict(source_row=row,cells=cells))
 assert len(stats)==3183 and sum(tail.values())==1043548
 for sr in stats:
  sr['annotated_counts']={}
  for fld,col in [('active','C'),('inactive','D'),('total','E'),('ballots','F')]:
   cell=sr['cells'].get(col+str(sr['source_row']));literal=cell['decoded']if cell else None;match=re.fullmatch(r'([0-9]+)(\*)',literal or '')
   if match:sr['annotated_counts'][fld]=dict(literal=literal,parsed_count=int(match[1]),annotation=match[2],cell_address=col+str(sr['source_row']),source_type=cell['attributes'].get('t'),raw_v=cell['value'])
   sr['published_'+fld]=sr[fld]if sr[fld]is not None else int(match[1])if match else None
  sr['published_count_scope']='explicit decimal source values plus separately parsed literal star-annotated strings; no imputation or residual allocation'
 assert [r['source_row']for r in stats if r['annotated_counts']]==[2632,2633]
 assert sum(r['published_ballots']for r in stats)==3241155
 assert sum(r['published_active']for r in stats)==4074612
 assert sum(r['published_total']for r in stats)==4583280
 gz(X/'2024-native-statistics.jsonl.gz',stats);dump(X/'2024-workbook-footnotes-tail.json',dict(other_rows=other,cached_error_only_tail=tail,whole_original_unchanged=True))
 lookup={(r['comparison_county'],r['native_id_literal']):r for r in stats};assert len(lookup)==len(stats)
 keys={(r['county_literal'],r['native_id_literal'])for r in years[2024]['native']};assert set(lookup)<=keys
 native=years[2024]['native'];csvonly=[]
 for r in native:
  k=(r['county_literal'],r['native_id_literal']);s=lookup.get(k);r['statistics_source_row']=s['source_row']if s else None;r['statistics_available']=s is not None
  r['stats_county_literal']=s['county_literal']if s else None
  for fld in ['active','inactive','total','ballots']:
   r['stats_'+fld]=s[fld]if s else None
   r['stats_published_'+fld]=s['published_'+fld]if s else None
  r['stats_annotations']=s['annotated_counts']if s else None
  r['statistics_join_scope']='same-year literal pair diagnostic; explicit Weld trailing-space alias only; no current or cross-year equivalence'
  if s is None:assert r['candidate_votes']==0;csvonly.append(dict(key=r['key'],source_record=r['source_record'],county=k[0],native_literal=k[1]))
 assert len(csvonly)==16
 dump(X/'native-coverage.json',dict(csv_only_2024=csvonly,statistics_annotated_count_records=[r for r in stats if r['annotated_counts']],statistics_missing_printed_count_fields=[dict(source_row=r['source_row'],county=r['county_literal'],native_id=r['native_id_literal'],field=f)for r in stats for f in ['active','inactive','total','ballots']if r['published_'+f]is None],literal_alias='Weld (CSV) compares with Weld + trailing space (workbook); both originals retained',native_method_split='unavailable in statewide CSVs: hasVoteChannels=false; precinct rows combine methods',native_unit_type='source literal Precinct; physical precinct, ballot style, central processing, and vote-center equivalence not inferred'))
 priorities={str(y):rank(v['native'],'candidate_votes')for y,v in years.items()};county_ranks={str(y):rank(v['counties'],'candidate_votes')for y,v in years.items()};dump(X/'native-rankings.json',priorities);dump(X/'county-candidate-rankings.json',county_ranks)
 gz(X/'2024-native-ranked.jsonl.gz',priorities['2024']['full_order'])
 fields=['rank','key','county_literal','county_fips','native_id_literal','candidate_votes','cumulative_votes','share_numerator','share_denominator','source_id','source_record','method','blank','undervote','overvote','stats_county_literal','statistics_source_row','stats_active','stats_inactive','stats_total','stats_ballots','stats_published_active','stats_published_inactive','stats_published_total','stats_published_ballots','stats_annotations']
 with (O/'native-unit-order.csv').open('w')as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(priorities['2024']['full_order'])
 with (O/'county-order.csv').open('w')as f:
  fields2=['rank','key','county_literal','county_fips','candidate_votes','cumulative_votes','share_numerator','share_denominator','source_id','source_record'];w=csv.DictWriter(f,fieldnames=fields2,extrasaction='ignore');w.writeheader();w.writerows(county_ranks['2024']['full_order'])
 # No missing native values are filled from county differences.
 diag=[]
 for c in sorted(counties):
  rs=[v for v in stats if v['comparison_county']==c];d=dict(county=c,county_fips=fips[c],statistics_rows=len(rs),source='sos-2024-native-turnout',unknown_fields={},known_sums={},published_count_sums={},missing_published_fields={},abstract_controls=turnout[2024][c],known_minus_abstract={},published_minus_abstract={})
  for fld in ['active','inactive','total','ballots']:
   d['known_sums'][fld]=sum(v[fld]for v in rs if v[fld]is not None);d['unknown_fields'][fld]=sum(v[fld]is None for v in rs);d['published_count_sums'][fld]=sum(v['published_'+fld]for v in rs if v['published_'+fld]is not None);d['missing_published_fields'][fld]=sum(v['published_'+fld]is None for v in rs)
   if fld!='inactive':d['published_minus_abstract'][fld]=d['published_count_sums'][fld]-turnout[2024][c]['registered'if fld=='total'else fld]
   if fld!='inactive':d['known_minus_abstract'][fld]=d['known_sums'][fld]-turnout[2024][c]['registered'if fld=='total'else fld]
  diag.append(d)
 dump(X/'2024-statistics-county-reconciliation.json',diag)
 assert all(not any(r['published_minus_abstract'].values())for r in diag)
 dump(S/'montezuma-annotated-count-correction.json',dict(source_id='sos-2024-native-turnout',raw_original_sha256=M['sos-2024-native-turnout']['raw_sha256'],source_rows=[r for r in stats if r['annotated_counts']],footnote_rows=other[1:],plain_decimal_known_totals={f:sum(r[f]for r in stats if r[f]is not None)for f in ['active','inactive','total','ballots']},published_decimal_and_annotated_totals={f:sum(r['published_'+f]for r in stats if r['published_'+f]is not None)for f in ['active','inactive','total','ballots']},all64_published_active_total_ballot_controls_close=True,correction='Earlier preflight lexical-only count parser left star-annotated shared strings null; actual source counts are printed, not absent. Exact t=s/rawv/shared-string/asterisk retained. Added explicit parsed-annotation lane only; original/plain lane and dated preflight remain unchanged. No county residual fitting, reallocation or geography repair.'))
 # County sensitivities by true administrative ballots and both registration universes.
 sensitivities={}
 gov=html22['governor'];sensitivities['2022_governor_county_candidate_votes']=rank([dict(key='CO|2022|governor|'+r[0],county=r[0],value=numeric(r[-2]))for r in gov['rows']],'value')
 for y in [2024,2022,2020]:
  for field in ['ballots','active','registered']:
   rs=[dict(key=f'CO|{y}|county|{c}',county=c,value=v[field])for c,v in turnout[y].items()];sensitivities[f'{y}_{field}']=rank(rs,'value')
 sensitivities['2024_native_known_ballots']=rank([dict(key=f'CO|2024|statistics|{r["comparison_county"]}|{r["native_id_literal"]}',county=r['comparison_county'],native_id_literal=r['native_id_literal'],source_row=r['source_row'],value=r['ballots'])for r in stats if r['ballots']is not None],'value');sensitivities['2024_native_known_ballots']['scope']='3181 plain-decimal ballot rows only; two source-starred Montezuma rows excluded by this lexical lane, not absent source counts; sixteen CSV-only statistic contexts unavailable; incomplete denominator, see2024_native_published_ballots for annotated-source sensitivity'
 sensitivities['2024_native_published_ballots']=rank([dict(key=f'CO|2024|statistics|{r["comparison_county"]}|{r["native_id_literal"]}',county=r['comparison_county'],native_id_literal=r['native_id_literal'],source_row=r['source_row'],value=r['published_ballots'],annotations=r['annotated_counts'].get('ballots'))for r in stats],'value');sensitivities['2024_native_published_ballots']['scope']='all3183 worksheet source contexts, decimal values plus two explicit star-annotated counts retained separately; full administrative ballot total closes all64countyabstractcontrols; sixteen candidateCSV-onlystatisticcontexts remain unknown, not invented zeros; no legal/current crosswalk'
 dump(X/'sensitivities.json',sensitivities)
 # County CSV is explicit parent comparison, never substituted for native dispatch.
 rows=[]
 for r in county_ranks['2024']['full_order']:
  c=r['county_literal'];v=dict(county=c,county_fips=fips[c],rank_2024_president=r['rank'],votes_2024_president=r['candidate_votes'],cumulative_2024=r['cumulative_votes'],share_2024_numerator=r['candidate_votes'],share_2024_denominator=priorities['2024']['total'],native_2024_count=sum(t['county_literal']==c for t in native))
  for y in [2024,2022,2020]:
   par=next(x for x in years[y]['counties']if x['county_literal']==c)
   for name,vv in zip(years[y]['headers'][2:-2],par['candidate_values']):v[f'{y}_candidate::{name}']=vv
   v[f'{y}_contest_votes']=par['candidate_votes']
   for fld in ['active','registered','ballots']:v[f'{y}_{fld}']=turnout[y][c][fld]
   v[f'{y}_ballots_minus_candidate_votes_unclassified']=turnout[y][c]['ballots']-par['candidate_votes']
   v[f'{y}_blank']=None;v[f'{y}_undervote']=None;v[f'{y}_overvote']=None
  gr=next(x for x in html22['governor']['rows']if x[0]==c)
  for name,vv in zip(html22['governor']['header'][3:-2],gr[3:-2]):v['2022_governor_candidate::'+name]=numeric(vv)
  v['2022_governor_votes']=numeric(gr[-2]);v['2022_governor_ballots']=numeric(gr[2]);v['2022_governor_registered']=numeric(gr[1])
  rows.append(v)
 cols=list(rows[0]);f=io.StringIO();w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows);(O.parent/'county-turnout.csv').write_text(f.getvalue())
 contract=dict(schema_version='CO-turnout-priority-v1',state='CO',election_date='2024-11-05',contest='President',contest_id='26499',priority_basis='sum of 14 source named-ticket candidate columns, six printed write-in tickets included; pseudocandidates excluded',disjoint_level='source Precinct rows only; State/County rows controls not additive',key_schema='CO|year|contest_id|county_literal|native_id_literal',tie_break='descending integer candidate_votes, ascending literal composite key (Unicode)',status='independently_reconciled_pending_peer_and_coordinator_acceptance',current_geography_approved=False,complete_native_count=3199,county_count=64,**{k:v for k,v in priorities['2024'].items()if k!='full_order'},ordered_priority_keys=[r['key']for r in priorities['2024']['full_order'][:priorities['2024']['minimum80_count']]],ordered_top15_keys=[r['key']for r in priorities['2024']['full_order'][:15]],ordered_remainder_keys=[r['key']for r in priorities['2024']['full_order'][priorities['2024']['minimum80_count']:]],county_native_hierarchy=[dict(county=c,county_fips=fips[c],all_native_keys=[r['key']for r in priorities['2024']['full_order']if r['county_literal']==c],priority_native_keys=[r['key']for r in priorities['2024']['full_order'][:priorities['2024']['minimum80_count']]if r['county_literal']==c],all_count=len([r for r in native if r['county_literal']==c]))for c in sorted(counties)],full_order=priorities['2024']['full_order'],county_parents=years[2024]['counties'],all_available_source_constituents='full_order retains every native CSV row; 3,183 native stats records by source row and same-year literal diagnostic; candidate universe/objects in extracts/candidate-universes.json; historical contexts complete in extracts/historical-source-rows.jsonl.gz',unavailable_administrative_cases=dict(method_splits=None,ballot_styles=None,central_absentee_groups=None,vote_centers=None,source_numeric_division_ids=None,blank=None,undervote=None,overvote=None,current_crosswalk=None,explanation='no such disjoint detail is published in the selected full-state contest CSV; source type Precinct is retained without invented physical or method assignments; zero-only rows retained explicitly'),csv_only_statistics_unavailable=csvonly)
 if (O/'peer-agreement.json').exists():
  qa=json.loads((O/'peer-agreement.json').read_text())
  if qa['status']=='pass_bounded_reciprocal_original_source_QA':
   contract['status']='historical_source_reconciliation_and_bounded_peer_QA_passed_formal_acceptance_pending'
   contract['peer_agreement']=dict(path='peer-agreement.json',peer_id=qa['peer_id'],scope=qa['scope'],capture=qa['capture'],prior_frozen_witness=qa['frozen_own'])
 contract['formal_coordinator_acceptance']=False
 dump(O/'priority-set.json',contract)
 dump(O/'calculation-summary.json',dict(contests=checks,priority={k:{f:v for f,v in x.items()if f!='full_order'}for k,x in priorities.items()},county={k:{f:v for f,v in x.items()if f!='full_order'}for k,x in county_ranks.items()},administrative_state={str(y):{f:sum(r[f]for r in turnout[y].values())for f in ['ballots','registered','active']}for y in turnout},independent_primary_candidate_cells=len(proof),controls=checks))
 print(json.dumps({k:{f:v for f,v in x.items()if f!='full_order'}for k,x in priorities.items()},indent=2))
if __name__=='__main__':main()
