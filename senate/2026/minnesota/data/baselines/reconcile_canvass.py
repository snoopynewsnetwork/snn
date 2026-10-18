"""Independent primary2020 PDF county controls; pdftotext and stdlib."""
import gzip,json,re,subprocess,hashlib
from extract import H,S,N,readcsv,writecsv,dump

def main():
 m={r['id']:r for r in json.loads((N/'manifest.json').read_text())}['sos-2020-canvass-original'];b=gzip.decompress((N/m['asset']).read_bytes());assert hashlib.sha256(b).hexdigest()==m['raw_sha256']
 text=subprocess.run(['pdftotext','-layout','-','-'],input=b,stdout=subprocess.PIPE,check=True).stdout.decode();county={r['COUNTYNAME'].casefold():r for r in readcsv(H/'county-controls-2020.csv')};rows=[];required=[];section='';page=1
 for line_no,line in enumerate(text.splitlines(),1):
  if 'Minnesota Voter Statistics' in line:section='stats'
  if re.match(r'\s*U\.S\. President',line):section='president'
  if re.match(r'\s*U\.S\. Senator\s*$',line):
   if any(r['field']=='USSENWI' for r in rows):break
   section='senate'
  if re.match(r'\s*U\.S\. Representative',line):section='representative'
  mt=re.search(r'Page (\d+) of 122',line)
  if mt:page=int(mt.group(1))+1
  if section not in ['stats','senate']:continue
  fields=re.split(r'\s{2,}',line.strip());name=fields[0].casefold()
  if name not in county:continue
  nums=[x for f in fields[1:] for x in f.split()]
  if not nums or not all(re.fullmatch('[0-9,]+',x) for x in nums):continue
  cols=['REG7AM','EDR','AB_MB','FEDONLYAB','PRESONLYAB','TOTVOTING'] if section=='stats' else ['USSENLMN','USSENGLC','USSENR','USSENDFL'] if len(nums)==4 else ['USSENWI']
  assert len(nums)==len(cols),(line,cols)
  r=county[name];required.append(dict(text_line=line_no,section=section,literal=line))
  for field,v in zip(cols,nums):
   count=int(v.replace(',',''));own=int(r[field]);rows.append(dict(county_fips=r['county_fips'],workbook_county=r['COUNTYNAME'],pdf_county=fields[0],field=field,workbook=own,pdf=count,difference=own-count,pdftotext_line=line_no,source_pdf_sha256=m['raw_sha256']))
 assert len(rows)==957 and len({(r['county_fips'],r['field']) for r in rows})==957
 assert all(r['difference']==0 for r in rows)
 writecsv(S/'canvass-2020-reconciliation.csv',rows);dump(S/'canvass-2020-source-lines.json',required)
 dump(S/'canvass-2020-check.json',dict(status='pass',county_fields=957,differences=0,pdf_sha256=m['raw_sha256'],command='pdftotext -layout - -',generic_scope='PDF WRITE-IN bucket; no eligible named allocation inferred',county_label_mapping='case-insensitive exact text only; original spellings retained'))
 named=[];fields=[];in_senate=False
 names=['Josh D. Ondich','John Berman','George A. Dennis Jr','Stephen W Carlson','Jason U. Shaver','Rob Barrett, Jr.']
 for line_no,line in enumerate(text.splitlines(),1):
  if 'Josh D. Ondich' in line:in_senate=True;fields=names[:4]
  if in_senate and 'Jason U. Shaver' in line:fields=names[4:]
  if in_senate and re.match(r'\s*U\.S\. Representative',line):break
  if not in_senate:continue
  ff=re.split(r'\s{2,}',line.strip());name=ff[0].casefold()
  if name not in county:continue
  nums=[x for f in ff[1:] for x in f.split()]
  assert len(nums)==len(fields)
  for candidate,v in zip(fields,nums):named.append(dict(contest='2020-senate',county_fips=county[name]['county_fips'],pdf_county=ff[0],candidate_name=candidate,source_party='WRITE-IN',votes=int(v.replace(',','')),pdftotext_line=line_no,source_pdf_sha256=m['raw_sha256'],scope='separate named write-in appendix; overlaps generic WI, never add'))
 assert len(named)==522 and len({(r['county_fips'],r['candidate_name']) for r in named})==522
 writecsv(S/'named-writeins-2020.csv',named)
 control={n:sum(r['votes'] for r in named if r['candidate_name']==n) for n in names}
 dump(S/'named-writeins-2020-controls.json',dict(candidate_totals=control,named_writeins=sum(control.values()),generic_writeins=2261,generic_minus_named=2261-sum(control.values()),scope='Scope difference, not an allocation of the residual to invalid/eligible individuals. No native named allocation is supplied.'))
 print('957 county candidate/statistic controls match primary2020 canvass')
if __name__=='__main__':main()
