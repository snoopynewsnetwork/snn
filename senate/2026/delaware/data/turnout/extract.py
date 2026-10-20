#!/usr/bin/env python3
"""Independent stdlib extraction from complete original entities, not prep derivatives."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import re,json,gzip,csv,io,hashlib,collections
D=Path(__file__).resolve().parent; N=D.parent/'news'; X=D/'extracts'; X.mkdir(exist_ok=True)
MF={a['id']:a for a in json.loads((D/'source/original-inputs.json').read_text())}
SOURCES={2024:('sos-2024-general-report','sos-2024-csv'),2022:('official-2022-report','sos-observed-2022-state-csv'),2020:('sos-observed-2020-general-report','sos-observed-2020-state-csv')}
TARGETS={2024:['PresidentandVicePresident','USSenator'],2022:['RepresentativeinCongress'],2020:['PresidentandVicePresident','USSenator']}
METHODS={'Machine Votes':'machinevotessum','Absentee Votes':'absenteevotessum','Early Voting Votes':'earlyvotessum','Total Votes':'totalvotessum'}
def raw(sid):
 a=MF[sid];z=(N/a['asset']).read_bytes();b=gzip.decompress(z)
 assert hashlib.sha256(z).hexdigest()==a['stored_sha256']
 assert hashlib.sha256(b).hexdigest()==a['raw_sha256']
 return b
def clean(s):
 import html
 return html.unescape(re.sub('<[^>]*>','',s)).strip()
def num(v):return int(v.replace(',','')) if v is not None and re.fullmatch(r'[\d,]+',v) else None
def dump(name,obj): (X/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def zipped(name,rows):
 b=''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows).encode();(X/name).write_bytes(gzip.compress(b,mtime=0))
def extract():
 allrows=[]; controls=[];tables=[];inventories=[];checks=[];source_refs=[]
 for year,(hsid,csid) in SOURCES.items():
  text=raw(hsid).decode('utf-8-sig'); state=list(csv.DictReader(io.StringIO(raw(csid).decode('utf-8-sig'))))
  for sid in [hsid,csid]:source_refs.append({'id':sid,'path':'../../news/'+MF[sid]['asset'],'receipt':MF[sid],'redirect_qualification':'retained acquisition has final URL and HTTP headers but intermediate redirects were not retained'})
  sections=sorted([(m.start(),m[1]) for m in re.finditer(r'<div\b[^>]*\bid="(statewide|byrepdist|byelectiondist|bycounty|bycountyw)"',text)])
  assert len(sections)==5,(year,sections)
  headings=list(re.finditer(r'<h([34])\b[^>]*\bclass="([^"]+)"[^>]*>(.*?)</h\1>',text,re.S))
  eds={};rds={};yearrows=[]
  for i,h in enumerate(headings):
   classes=h[2].split(); typ=classes[0]
   if typ not in ['contest-title','repdistrict-title','electiondistrict-title']:continue
   officekey=classes[1];section=[sec for pos,sec in sections if pos<h.start()][-1]
   stop=headings[i+1].start() if i+1<len(headings) else len(text)
   match=re.search(r'<table\b[^>]*>(.*?)</table>',text[h.end():stop],re.S)
   if typ in ['electiondistrict-title','repdistrict-title']:
    native=classes[2];inventory=eds if typ=='electiondistrict-title' else rds
    ent=inventory.setdefault(native,{'year':year,'native_key':native,'native_name':clean(h[3]),'offices':[],'source_id':hsid,'source_heading_positions':[]})
    ent['offices'].append(officekey);ent['source_heading_positions'].append(h.start())
   else:native='State' if section=='statewide' else section
   if not match or officekey not in TARGETS[year]:continue
   ts=h.end()+match.start();te=h.end()+match.end();headers=[clean(v) for v in re.findall(r'<th\b[^>]*>(.*?)</th>',match[1],re.S)]
   tt={'year':year,'source_id':hsid,'view':section,'office_key':officekey,'heading_type':typ,'native_key':native,'native_name':clean(h[3]),'heading_start':h.start(),'table_start':ts,'table_end':te,'headers':headers,'rows':0}
   for rowno,rm in enumerate(re.finditer(r'<tr\b[^>]*>(.*?)</tr>',match[1],re.S)):
    cells=list(re.finditer(r'<td\b([^>]*)>(.*?)</td>',rm[1],re.S))
    if not cells:continue
    assert len(cells)==len(headers),(year,section,officekey,len(cells),headers)
    fields={};cellinfo=[]
    for j,c in enumerate(cells):
     label=re.search(r'data-label="([^"]+)"',c[1]);key=clean(label[1]) if label else headers[j]
     assert key not in fields
     fields[key]=clean(c[2]);cellinfo.append({'column':j,'key':key,'raw_cell_html':c[0],'text':clean(c[2])})
    assert 'Candidate' in fields or 'Candidate Name' in fields,(year,section,officekey,headers,fields)
    rs=ts+match[0].find(match[1])+rm.start();re_=ts+match[0].find(match[1])+rm.end()
    out={k:tt[k] for k in ['year','source_id','view','office_key','native_key','native_name','heading_start','table_start','table_end']}
    out.update({'row_index':rowno,'row_start':rs,'row_end':re_,'candidate':fields.get('Candidate',fields.get('Candidate Name')),'party':fields.get('Party',fields.get('Party Name')),'raw_fields':fields,'cells':cellinfo,'numeric':{k:num(fields.get(k)) for k in METHODS}})
    if section in ['statewide','byrepdist','byelectiondist']:
     vals=out['numeric'];assert vals['Machine Votes']+vals['Absentee Votes']+(vals['Early Voting Votes'] or 0)==vals['Total Votes']
     if year!=2020:assert vals['Early Voting Votes'] is not None
    allrows.append(out);yearrows.append(out);tt['rows']+=1
   tables.append(tt)
  # Derive county membership only from explicit county-office titles, never ranges.
  county_offices={}
  for h in headings:
   cl=h[2].split()
   if cl[0]=='contest-title':
    label=clean(h[3]);office=cl[1]
    for county,prefixes in {'New Castle':['New Castle County','NCC '],'Kent':['Kent County','KC '],'Sussex':['Sussex County','SC ']}.items():
     if any(label.startswith(p) for p in prefixes):county_offices[office]=county
  for ed in eds.values():
   evidence=[{'office_key':o,'county':county_offices[o],'heading_position':ed['source_heading_positions'][j]} for j,o in enumerate(ed['offices']) if o in county_offices]
   parents=sorted(set(e['county'] for e in evidence));assert len(parents)<=1,(year,ed,parents)
   ed['county']=parents[0] if parents else None;ed['county_evidence']=evidence;ed['county_fips']={'New Castle':'10003','Kent':'10001','Sussex':'10005'}.get(ed['county'])
   ed['county_scope']='explicit county-office ED membership' if parents else 'unavailable: no county-office table establishes parent'
  inventories.append({'year':year,'source_id':hsid,'source_sha256':MF[hsid]['raw_sha256'],'election_districts':eds,'representative_districts':rds,'county_office_titles':county_offices,'headline':re.findall(r'\d+ of \d+ Precincts Reporting',text),'turnout_literal':re.findall(r'[\d,]+\s+of\s+[\d,]+\s+Registered Votes',text),'source_clock':re.findall(r'Data as of[^<]+',text),'status':'OFFICIAL RESULTS' if 'OFFICIAL RESULTS' in text else None})
  for office in TARGETS[year]:
   sr=[r for r in yearrows if r['view']=='statewide' and r['office_key']==office];assert sr
   names=[r['candidate'] for r in sr];assert len(names)==len(set(names))
   for r in sr:
    cr=[(i,c) for i,c in enumerate(state,2) if c['candidatename']==r['candidate'] and c['partyname']==r['party'] and int(c['totalvotessum'])==r['numeric']['Total Votes']];assert len(cr)==1,(year,r['candidate'],cr)
    line,c=cr[0];controls.append({'year':year,'office_key':office,'source_id':csid,'csv_row_number':line,'raw_fields':c})
    for field,csvfield in METHODS.items():
     for view in ['byelectiondist','byrepdist']:
      rr=[a for a in yearrows if a['office_key']==office and a['view']==view and a['candidate']==r['candidate']]
      assert rr and len({a['native_key'] for a in rr})==len(rr)
      vals=[a['numeric'][field] for a in rr]
      if field=='Early Voting Votes' and year==2020:assert all(v is None for v in vals);total=None
      else:assert all(v is not None for v in vals);total=sum(vals);assert total==int(c[csvfield]),(year,office,view,r['candidate'],field,total,c[csvfield])
      checks.append({'year':year,'office_key':office,'view':view,'candidate':r['candidate'],'field':field,'native_sum':total,'csv_control':int(c[csvfield]),'null_positions':sum(v is None for v in vals),'pass':True})
    # Disjoint county controls plus alternative Wilmington partition.
    for view,cols in [('bycounty',['New Castle','Kent','Sussex']),('bycountyw',['Wilmington','Rest of New Castle','Kent','Sussex'])]:
     rr=[a for a in yearrows if a['office_key']==office and a['view']==view and a['candidate']==r['candidate']];assert len(rr)==1
     f=rr[0]['raw_fields'];assert sum(num(f[k]) for k in cols)==int(c['totalvotessum'])
     if view=='bycounty':
      for county in cols:
       edrows=[a for a in yearrows if a['office_key']==office and a['view']=='byelectiondist' and eds[a['native_key']]['county']==county]
       unknown=[a for a in yearrows if a['office_key']==office and a['view']=='byelectiondist' and eds[a['native_key']]['county'] is None]
       if not unknown:assert sum(a['numeric']['Total Votes'] for a in edrows if a['candidate']==r['candidate'])==num(f[county]),(year,office,county)
   checks.append({'year':year,'office_key':office,'native_count':len({a['native_key'] for a in yearrows if a['view']=='byelectiondist' and a['office_key']==office}),'named_votes':sum(r['numeric']['Total Votes'] for r in sr),'county_parent_unknown_ed_count':sum(e['county'] is None for e in eds.values()),'pass':True})
 zipped('candidate-rows.jsonl.gz',allrows);dump('tables.json',tables);dump('state-controls.json',controls);dump('native-inventory.json',inventories);dump('reconciliation.json',checks);dump('source-references.json',source_refs)
 print(json.dumps([r for r in checks if 'native_count' in r],indent=2))
if __name__=='__main__':extract()
