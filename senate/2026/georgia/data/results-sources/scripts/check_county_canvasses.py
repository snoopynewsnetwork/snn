from common import *
import re
names=['Brian Kienitz','Nomusa Venita Smith','Peter Sonski','Jay J Bowman','President R Boddie','Shiva Ayyadurai','Susan Maude Buscher','Emily Mathews','André Ramon McNeil Sr']
records=[]
for rec in js(ROOT/'extracts/download-index.json'):
 if rec.get('type')!='PDF':continue
 text=gzip.decompress((ROOT/rec['text_path']).read_bytes()).decode();first=text.split('\f')[0]
 if 'Election Summary Report' not in first or 'L&A' in first or 'Logic and Accuracy' in first:continue
 if not re.search(r'November\s+0?5,?\s+2024',first):continue
 start=text.find('President of the US')
 if start<0:continue
 end=text.find('US House',start)
 if end<0:end=text.find('United States House',start)
 block=text[start:end] if end>=0 else text[start:]
 if not all(n in block for n in ['Donald J. Trump','Kamala D. Harris']):continue
 source_rows=[]
 for line_no,line in enumerate(block.splitlines()):
  m=re.match(r'\s*(.*?)\s+WRITE-IN\s+(.*)',line)
  if not m:continue
  label=m.group(1);nums=[int(x.replace(',','')) for x in m.group(2).split() if re.fullmatch(r'\d[\d,]*',x)]
  valid=len(nums)==5 and sum(nums[:4])==nums[4]
  source_rows.append({'printed_name':label,'source_line':line,'presidential_section_text_line_ordinal':line_no,'method_values_in_printed_order':nums[:4] if valid else None,'total':nums[4] if valid else None,'raw_integer_tokens':nums,'source_classification':'printed WRITE-IN; exact name variant retained without automatic candidate join'})
 generic=[]
 for line_no,line in enumerate(block.splitlines()):
  if 'Unresolved Write-In' in line:
   nums=[int(x.replace(',','')) for x in line.split() if re.fullmatch(r'\d[\d,]*',x)];generic.append({'source_line':line,'section_line_ordinal':line_no,'raw_integer_tokens':nums,'total':nums[4] if len(nums)==5 and sum(nums[:4])==nums[4] else None})
 # Exact matching only, with terminal period separately visible; Mathews vs Matthews is not normalized.
 found={r['printed_name'].rstrip('.') for r in source_rows};unknown=[n for n in names if n not in found]
 f=re.search(r'(13\d{3})',rec['id']);records.append({'source_id':rec['id'],'county_fips_from_acquisition':f.group(1) if f else None,'source_page_start':text[:start].count('\f')+1,'raw_sha256':rec['raw_sha256'],'printed_clock':re.findall(r'\d{1,2}/\d{1,2}/2024\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M',first)[:1],'printed_clock_timezone':None,'printed_status':re.findall(r'(?im)^\s*((?:Unofficial and Incomplete|Official and Complete|OFFICIAL AND COMPLETE))\s*$',first),'printed_WRITE_IN_rows':source_rows,'generic_unresolved':generic,'absent_exact_named_rows_unknown':unknown,'no_allocation_into_frozen_contract':True,'same_vintage_as_final_state858_unproven':True})
save(ROOT/'extracts/county-canvass-writeins.json',records)
print([(r['source_id'],[(x['printed_name'],x['total']) for x in r['printed_WRITE_IN_rows'] if x['total']]) for r in records])
