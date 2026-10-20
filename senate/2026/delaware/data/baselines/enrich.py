#!/usr/bin/env python3
"""Source-scoped PDF/participation and published candidate-list evidence."""
from pathlib import Path
import gzip,hashlib,json,re,collections,csv,fitz,html
from extract import writecsv,writejson,COUNTIES,raw,clean
P=Path(__file__).resolve().parent

def pdf_writeins():
 out=[];evidence=[]
 specs=[(2024,'sos-2024-valid-writeins'),(2022,'sos-observed-2022-writeins'),(2020,'sos-observed-2020-writeins')]
 for year,sid in specs:
  b=raw(sid);d=fitz.open(stream=b,filetype='pdf')
  for pi,pg in enumerate(d):
   words=pg.get_text('words');evidence.append(dict(year=year,source_id=sid,source_sha256=hashlib.sha256(b).hexdigest(),page=pi+1,words=words))
   # Each source's target sections visually reviewed in complete raster pages.
   if year==2020 and pi>0:continue
   if year==2020:regions=[('State',160,425,'PresidentandVicePresident')];cols={'absentee':387.2,'machine':468.5,'total':532.2};cut=350
   elif year==2022:regions=[('State',210,244,'RepresentativeinCongress')];cols={'absentee':314.7,'early':380.8,'machine':444.1,'provisional':508,'total':567.3};cut=280
   elif pi==0:regions=[('New Castle',210,364,'PresidentandVicePresident'),('Kent',565,700,'PresidentandVicePresident')];cols={'absentee':314.4,'early':380.4,'machine':443.5,'provisional':508,'total':566.7};cut=280
   else:regions=[('Sussex',270,380,'PresidentandVicePresident')];cols={'absentee':314.4,'early':380.4,'machine':443.5,'provisional':508,'total':566.7};cut=280
   lines=[]
   for w in sorted(words,key=lambda w:(w[1],w[0])):
    match=next((line for line in lines if abs(line[0]-w[1])<1.0),None)
    if match:match[1].append(w)
    else:lines.append([w[1],[w]])
   for county,lo,hi,office in regions:
    for y,ws in lines:
     if not lo<=y<=hi:continue
     numbers=[w for w in ws if w[0]>cut and re.fullmatch(r'[\d,]+',w[4])]
     if not any(abs(w[2]-cols['total'])<2 for w in numbers):continue
     name=' '.join(w[4] for w in sorted(ws,key=lambda w:w[0]) if w[0]<cut)
     vals={k:None for k in ['machine','absentee','early','provisional','total']}
     for w in numbers:
      col=min(cols,key=lambda k:abs(cols[k]-w[2]));assert abs(cols[col]-w[2])<2,(year,w,cols);assert vals[col] is None;vals[col]=int(w[4].replace(',',''))
     assert sum(v for k,v in vals.items() if k!='total' and v is not None)==vals['total']
     out.append(dict(year=year,office_key=office,geo_key=county,scope='county' if county!='State' else 'statewide',candidate=name,party=None,ballot_identity='separate named official write-in tally; party unprinted',**vals,source_id=sid,page=pi+1,y_min=y,blank_cells='null, not inferred zero',source_sha256=hashlib.sha256(b).hexdigest()))
 writecsv(P/'extracted/writeins.csv',out);writejson(P/'source/pdf-words.json',evidence)
 print('writeins',collections.Counter((r['year'],r['geo_key']) for r in out),{y:sum(r['total'] for r in out if r['year']==y) for y in [2020,2022,2024]})

def participation():
 rows=[];hier=[]
 for year in [2020,2022,2024]:
  b=gzip.decompress((P/f'source/current/participation-{year}.gz').read_bytes());t=b.decode();county=rd=ed=None;pos=0
  for li,line in enumerate(t.splitlines(keepends=True),1):
   s=line.strip();cm=re.fullmatch(r'(KENT|NEW CASTLE|SUSSEX) COUNTY',s,re.I)
   if cm:county=cm[1].title();rd=ed=None
   if s=='STATEWIDE':county=rd=ed=None
   rm=re.fullmatch(r'Representative District (\d+)',s)
   if rm:rd=rm[1];ed=None
   em=re.fullmatch(r'Election District (\d+)-(\d+)',s)
   if em:ed='ElectionDistrict'+em[1].zfill(2)+em[2].zfill(2)
   if re.match(r'i\. Total\s',s):
    vals=s.split()[2:];assert len(vals)==12,(year,li,vals)
    d={}
    for j,party in enumerate(['democrat_registration','republican_registration','all_other_registration','total']):
     d[party+'_registered']=int(vals[j*3].replace(',',''));d[party+'_voted']=int(vals[j*3+1].replace(',',''));d[party+'_percentage_raw']=vals[j*3+2]
    assert sum(d[k+'_registered'] for k in ['democrat_registration','republican_registration','all_other_registration'])==d['total_registered']
    assert sum(d[k+'_voted'] for k in ['democrat_registration','republican_registration','all_other_registration'])==d['total_voted']
    scope='election_district' if ed else ('representative_district' if rd else ('county' if county else 'statewide'))
    row=dict(year=year,scope=scope,county=county,fips=COUNTIES.get(county),rd=rd,geo_key=ed or ('RepresentativeDistrict'+rd.zfill(2) if rd else county or 'State'),source_id=f'participation-{year}',source_line=li,source_char_start=pos,source_char_end=pos+len(line),raw_line=line.rstrip('\r\n'),**d)
    rows.append(row)
    if ed:hier.append(dict(year=year,geo_key=ed,county=county,fips=COUNTIES[county],representative_district=rd,source_id=f'participation-{year}',source_line=li,basis='Explicit county/Representative District/Election District nesting in original Registered/Voted report'))
   pos+=len(line)
  for field in ['total_registered','total_voted']:
   state=next(r[field] for r in rows if r['year']==year and r['scope']=='statewide')
   for scope in ['election_district','representative_district','county']:
    assert sum(r[field] for r in rows if r['year']==year and r['scope']==scope)==state,(year,field,scope)
 writecsv(P/'extracted/participation-totals.csv',rows);writejson(P/'extracted/participation-hierarchy.json',hier)
 # Source structure table is an additional historical administrative identity, not a geometry crosswalk.
 b=gzip.decompress((P/'source/current/registration-2022.gz').read_bytes());d=fitz.open(stream=b,filetype='pdf');out=[]
 for pi,pg in enumerate(d):
  tx=pg.get_text(sort=True)
  for li,line in enumerate(tx.splitlines(),1):
   m=re.match(r'\s*(KENT|NEW CASTLE|SUSSEX)\s+(\d{2})-(\d{2})([12]?)\s+(\d{2})(.*)',line)
   if m:out.append(dict(county=m[1].title(),geo_key='ElectionDistrict'+m[2]+m[3],footnote=m[4] or None,representative_district=m[5],remaining_source_fields=m[6].strip(),source_page=pi+1,source_line=li,raw_line=line,source_id='registration-2022',source_sha256=hashlib.sha256(b).hexdigest()))
 writejson(P/'extracted/district-structure.json',out)
 print('participation',collections.Counter((r['year'],r['scope']) for r in rows),'structure',len(out))

def candidate_lists():
 rows=[];notices=[]
 for year in [2020,2022,2024,2026]:
  for kind in ['fcddt','wcddt']:
   sid=f'candidates-{kind}-{year}';b=gzip.decompress((P/f'source/current/{sid}.gz').read_bytes());t=b.decode('utf-8-sig')
   notices.append(dict(source_id=sid,source_sha256=hashlib.sha256(b).hexdigest(),literal_updated_excerpts=[clean(t[max(0,m.start()-20):m.start()+110]) for m in re.finditer(r'Last Updated:|Updated on|Updated:',t)]))
   for ti,tb in enumerate(re.finditer(r'<table\b[^>]*>.*?</table>',t,re.S)):
    heads=[clean(x) for x in re.findall(r'<th(?:\s[^>]*)?>(.*?)</th>',tb[0],re.S)]
    for ri,rr in enumerate(re.finditer(r'<tr(?:\s[^>]*)?>(.*?)</tr>',tb[0],re.S)):
     vals=re.findall(r'<td(?:\s[^>]*)?>(.*?)(?=<td\b|$)',rr[1],re.S)
     if not vals:continue
     fields=dict(zip(heads,[clean(x) for x in vals]));office=fields.get('Office','')
     relevant= ('senator' in office.lower() and 'district' not in office.lower()) or ('President' in office or 'PRESIDENT' in office) or (year==2022 and 'Representative in Congress' in office)
     if relevant:
      # Name before disclosure/contact div, preserve complete raw fields separately.
      cname=fields.get('Candidate',fields.get('Name, Address, Phone',fields.get('Candidate Name and Address',fields.get('Name and Address',''))))
      nmidx=next((j for j,h in enumerate(heads) if h in ['Candidate','Name, Address, Phone','Candidate Name and Address','Name and Address']),None)
      if nmidx is not None:
       cname=clean(re.split(r'<(?:div|br)\b',vals[nmidx],maxsplit=1,flags=re.I)[0]);cname=re.sub(r'\s+',' ',cname).strip();cname=re.split(r' Mailing Address:| Residential Address:| Email #| Qualified| Provisional| Withdrawn',cname)[0].strip()
      rows.append(dict(year=year,kind=kind,table_index=ti,row_index=ri,office=office,candidate_name_prefix=cname,raw_fields=fields,raw_cells=vals,source_id=sid,source_char_start=tb.start()+rr.start(),source_char_end=tb.start()+rr.end()))
 writejson(P/'extracted/candidate-lists.json',rows);writejson(P/'extracted/candidate-list-clocks.json',notices)

if __name__=='__main__':pdf_writeins();participation();candidate_lists()
