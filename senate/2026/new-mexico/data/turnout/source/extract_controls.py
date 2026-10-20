#!/usr/bin/env python3
"""Independent PDF/JSON controls. PDF positions are page/line in retained Poppler text."""
from common import *
import subprocess,tempfile

def text_pdf(id):
 b=body(id);assert b.startswith(b'%PDF-')
 with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
  f.write(b);f.flush();p=subprocess.run(['pdftotext','-layout',f.name,'-'],capture_output=True,check=True)
 path=D/'source'/f'{id}.txt';path.write_bytes(p.stdout);return p.stdout.decode()
def numbers(line):return [int(v.replace(',',''))for v in re.findall(r'(?<![\w.])-?\d[\d,]*(?![\w.])',line)]
def main():
 out={};a=json.loads((D/'original-extract.json').read_text());turnout=json.loads((D/'ballot-registration-extract.json').read_text())
 census=Page(body('census-county-fips')).tables[0];geo={r[6]:dict(zip(census[0],r))for r in census[1:]};assert len(geo)==33
 # Source-exact county names differ by one accent. Retain both, with this explicit county-only crosswalk.
 geo['Dona Ana']=geo.pop('Doña Ana');dump(D/'county-identifiers.json',geo)
 for year,tag,id,starts in [(2024,'2024-senate','official-2024-file-2',['MARTIN HEINRICH','NELLA LOUISE']),(2020,'2020-senate','official-2020-file-1',['BEN R LUJAN','MARK V RONCHETTI','BOB WALSH']),(2022,'2022-governor','official-2022-file-1',['MICHELLE LUJAN','MARK V RONCHETTI','KAREN EVETTE'])]:
  s=text_pdf(id);lines=s.split('\f')[0].splitlines();counties=[r for r in a[tag]['rows']if r['level']=='County'];names=[r['native_label']for r in counties];rows=[]
  for start in starts:
   match=[(i,l)for i,l in enumerate(lines,1)if l.strip().startswith(start)];assert len(match)==1,(id,start)
   i,l=match[0];vals=numbers(l)
   if len(vals)!=34:
    # A wrapped name can precede its numeric line. Preserve both lines and never slide columns.
    candidates=[(j,lines[j-1])for j in range(i+1,min(i+4,len(lines)+1))if len(numbers(lines[j-1]))==34];assert len(candidates)==1,(id,start,vals);j,l=candidates[0];vals=numbers(l)
   else:j=i
   assert len(vals)==34 and sum(vals[:-1])==vals[-1]
   # CSV candidate order follows starts above; all 33 individual entries must agree, not just their sum.
   ci=starts.index(start);expected=[c['fields'][ci]['value']for c in counties];assert vals[:-1]==expected,(id,start)
   rows.append(dict(label_start=start,pdf_page=1,line_1based=i,numeric_line_1based=j,raw_lines=lines[i-1:j],county_values=vals[:-1],state=vals[-1],candidate_csv_column_1based=ci+3))
  ballot_methods=[]
  for method in ['Absentee','Early','Election Day']:
   i,l=next((i,l)for i,l in enumerate(lines,1)if l.startswith(method));vals=numbers(l)
   if len(vals)!=34:assert method=='Election Day';j=i+1;l=lines[j-1];vals=numbers(l)
   else:j=i
   assert len(vals)==34 and sum(vals[:-1])==vals[-1]
   ballot_methods.append(dict(method_literal=method,pdf_page=1,line_1based=i,numeric_line_1based=j,raw_lines=lines[i-1:j],county_values=vals[:-1],state=vals[-1]))
  service=json.loads(body(f'turnout-{year}-county-service'));assert len(service)==33;service_by_name={r['CountyName']:r for r in service};assert set(service_by_name)==set(names)
  discrepancies=[]
  for k,c in enumerate(names):
   b=sum(m['county_values'][k]for m in ballot_methods);t=next(v for v in turnout[str(year)]['counties']if v['county_literal']==c);z=service_by_name[c]
   assert t['ballots_cast_native_sum']==int(z['calcVoterTurnout'])
   if b!=t['ballots_cast_native_sum']:discrepancies.append(dict(county=c,pdf_ballots=b,portal_ballots=t['ballots_cast_native_sum'],pdf_minus_portal=b-t['ballots_cast_native_sum']))
   assert t['eligible_voters_native_sum']==z['Voters'],(year,c,t['eligible_voters_native_sum'],z['Voters'])
  pdf_state_ballots=sum(m['state']for m in ballot_methods)
  assert sum(z['Voters']for z in service)==turnout[str(year)]['state_eligible_voters']
  out[str(year)]=dict(source_id=id,county_column_order=names,candidate_rows=rows,whole_ballot_method_rows=ballot_methods,county_service_source_id=f'turnout-{year}-county-service',county_service_raw_rows=service,all_county_candidate_controls_agree=True,portal_county_native_state_ballots_and_eligible_agree=True,pdf_ballots_vs_portal_discrepancies=discrepancies,pdf_state_ballots=pdf_state_ballots,pdf_ballots_minus_portal=pdf_state_ballots-turnout[str(year)]['state_ballots_cast'],date_run_literals=re.findall(r'Date Run:[^\n]+',s),pdf_pages=len(s.split('\f'))-1)
 # All relevant statewide methods from original method summaries, including all 2024 president candidates.
 sums={}
 for tag,id,start,end in [('2024-senate','official-2024-file-1','United States Senator','United States Representative'),('2024-president','official-2024-file-1','President and Vice President','United States Senator'),('2020-senate','official-2020-file-0','United States Senator','United States Representative'),('2022-governor','official-2022-file-0','Governor and Lieutenant Governor','Secretary of State')]:
  s=text_pdf(id);p=s.split('\f')[0];section=p[p.index(start):p.index(end,p.index(start)+len(start))];records=[]
  for m in re.finditer(r'(?m)^.*?\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$',section):
   line=m[0];v=list(map(int,m.group(1,2,3,4)));assert sum(v[:3])==v[3];records.append(dict(raw_numeric_line=line,early=v[0],absentee=v[1],election_day=v[2],total=v[3]))
  assert sorted(r['total']for r in records)==sorted(f['value']for f in a[tag]['rows'][0]['fields'][:a[tag]['candidate_count']])
  sums[tag]=dict(source_id=id,page=1,raw_section=section,method_column_order=['Early','Absentee','Election Day','Total'],numeric_rows=records,source_scoped_names_and_line_wrapping_preserved=True)
  pres=a['2024-president'];counties=[r for r in pres['rows']if r['level']=='County'];lines=(D/'source/official-2024-file-2.txt').read_text().split('\f')[0].splitlines();pr=[]
 for ci,prefix in enumerate(['KAMALA D HARRIS','DONALD J TRUMP','ROBERT F KENNEDY','JILL STEIN','CHASE OLIVER','CLAUDIA DE LA CRUZ','LAURA EBKE']):
  ix,line=next((i,l)for i,l in enumerate(lines,1)if l.startswith(prefix));vals=numbers(line);assert len(vals)==34 and sum(vals[:-1])==vals[-1];assert vals[:-1]==[c['fields'][ci]['value']for c in counties]
  pr.append(dict(csv_column_1based=ci+3,label_start=prefix,page=1,line_1based=ix,raw_line=line,county_values=vals[:-1],state=vals[-1]))
 dump(D/'canvass-controls.json',dict(county_controls=out,statewide_candidate_methods=sums,president_2024_county_controls=pr))
 # Dated registration stocks: keep all original county/native rows and all party lanes, without cross-source native joins.
 registration={}
 for month in [9,10]:
  reg={}
  for lane in ['state','county']:
   id=f'registration-{month}-{lane}';s=text_pdf(id);pages=s.split('\f');records=[];pending=None
   for page_no,page in enumerate(pages,1):
    if not page.strip():continue
    lines=page.splitlines();county_match=re.search(r'(?m)^(.+?) County\s+As of (.+)$',page);county=county_match[1].strip()if county_match else None
    for ln,line in enumerate(lines,1):
     if lane=='state':
      m=re.match(r'^(.+?)\s{2,}([\d,].*)$',line)
      if not m:continue
      label=m[1];tail=m[2]
      if label not in geo and label!='TOTAL':continue
      counts=re.findall(r'(\d[\d,]*)\s+[\d.]+\s*%',tail);total=re.search(r'(\d[\d,]*)\s*$',tail)
      assert total,(id,line)
      header=next(l for l in lines if l.startswith('COUNTY'));positions=[header.index(w)for w in ['DEMOCRATIC','LIBERTARIAN','REPUBLICAN','NO','OTHER']];counts=[None]*5
      for cm in re.finditer(r'(\d[\d,]*)\s+[\d.]+\s*%',line):
       j=min(range(5),key=lambda j:abs(positions[j]-cm.start()));assert counts[j]is None;counts[j]=int(cm[1].replace(',',''))
      total=int(total[1].replace(',',''));assert sum(x for x in counts if x is not None)<=total
      if all(x is not None for x in counts):assert sum(counts)==total
      records.append(dict(source_id=id,page=page_no,line_1based=ln,label_literal=label,raw_line=line,county_literal=label if label!='TOTAL'else None,party_order=['DEMOCRATIC','LIBERTARIAN','REPUBLICAN','NO PARTY/INDEPENDENT/DECLINED TO SELECT','OTHER'],counts=counts,total=total,asof=re.search(r'As of ([^\n]+)',page)[1].strip(),registration_status=None))
     else:
      header=next((l for l in lines if l.startswith('PRECINCT')and'DEMOCRATIC'in l),None)
      # Last page has a distinct statewide summary layout, retained as text; county totals below close its directly printed totals.
      if header is None:continue
      width=header.index('DEMOCRATIC');label=line[:width].strip();tail=line[width:]
      nums=re.findall(r'-?\d[\d,]*',tail)
      if label and len(nums)in [9,10]and '%'in tail and not line.startswith('10/')and not line.startswith('11/'):
       vals=[int(x.replace(',',''))for x in nums];counts=vals[0:8:2];total=vals[8];assert sum(counts)==total,(id,page_no,line,counts,total)
       r=dict(source_id=id,page=page_no,line_1based=ln,county_literal=county,label_literal=label,label_continuations=[],raw_lines=[line],party_order=['DEMOCRATIC','REPUBLICAN','LIBERTARIAN','OTHER'],counts=counts,total=total,asof=county_match[2]if county_match else None,registration_status=None,scope='county_total'if label=='TOTAL'else 'native')
       records.append(r);pending=r
      elif pending is not None and label and not any(w in line for w in ['PRECINCT','County','Voter Registration','by County','Page:'])and not re.match(r'^\d{1,2}/\d{1,2}/',line.strip())and not re.search(r'\d',label):
       # Wrapped Hidalgo labels are part of the literal source identity, not another geography.
       pending['label_continuations'].append(label);pending['raw_lines'].append(line)
   reg[lane]=dict(source_id=id,rows=records,source_clocks=re.findall(r'\d{1,2}/\d{1,2}/\d{4} [\d:]+ [AP]M',s),timezone=None,pdf_pages=len(pages)-1)
  assert len([r for r in reg['state']['rows']if r['label_literal']!='TOTAL'])==33
  assert len([r for r in reg['county']['rows']if r['scope']=='county_total'])==33
  # These are independent reports with distinct run clocks; report discrepancies instead of coercing agreement.
  reg['state_report_total']=next(r['total']for r in reg['state']['rows']if r['label_literal']=='TOTAL')
  reg['county_report_native_sum']=sum(r['total']for r in reg['county']['rows']if r['scope']=='native')
  reg['county_report_county_totals_sum']=sum(r['total']for r in reg['county']['rows']if r['scope']=='county_total')
  reg['county_native_reconciliation']=[]
  for c in [r for r in reg['county']['rows']if r['scope']=='county_total']:
   kids=[r for r in reg['county']['rows']if r['scope']=='native'and r['county_literal']==c['county_literal']];n=sum(r['total']for r in kids)
   reg['county_native_reconciliation'].append(dict(county_literal=c['county_literal'],native_rows=len(kids),known_native_sum=n,printed_county_total=c['total'],printed_minus_native=c['total']-n))
  reg['state_vs_county_report_reconciliation']=[]
  for c in [r for r in reg['state']['rows']if r['label_literal']!='TOTAL']:
   other=next(r for r in reg['county']['rows']if r['scope']=='county_total'and r['county_literal']==c['label_literal'].upper());reg['state_vs_county_report_reconciliation'].append(dict(county_literal=c['label_literal'],state_report_count=c['total'],county_report_count=other['total'],county_minus_state_report=other['total']-c['total']))
  registration[str(month)]=reg
 dump(D/'registration-stocks.json',registration)
 print('PDF county/state controls agree all 33; registration stocks',[(k,v['state_report_total'],v['county_report_native_sum'])for k,v in registration.items()])
if __name__=='__main__':main()
