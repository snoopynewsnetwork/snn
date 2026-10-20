"""Independent direct original row/cell/header checks plus whole structure lines.
No imported producer parser, no mutable manifest or optional review dependency.
"""
from common import *
import re,html,collections

def clean(s):return ' '.join(html.unescape(re.sub('<[^>]+>',' ',s)).split())
def main():
 receipts=read(M/'source/historical-receipts.json');originals={};checks=0
 for item in receipts:
  r=item['receipt'];p=(S/'data/turnout/extracts'/item['path']).resolve();b=p.read_bytes();assert sha(b)==r['stored_sha256'];raw=gzip.decompress(b);assert sha(raw)==r['raw_sha256'];originals[r['id']]=raw.decode('utf-8-sig');checks+=2
 rows=read(S/'data/turnout/extracts/candidate-rows.jsonl.gz');tables=read(S/'data/turnout/extracts/tables.json');native=collections.defaultdict(set)
 for t in tables:
  s=originals[t['source_id']][t['table_start']:t['table_end']];assert s.startswith('<table') and s.rstrip().endswith('</table>')
  heads=[clean(m.group()) for m in re.finditer(r'<th\b[^>]*>.*?</th>',s,re.S|re.I)];assert heads==t['headers'];checks+=3
 for r in rows:
  s=originals[r['source_id']];table=s[r['table_start']:r['table_end']];row=s[r['row_start']:r['row_end']];assert row.startswith('<tr') and row.rstrip().endswith('</tr>') and row in table;checks+=3
  cells=re.findall(r'<td\b[^>]*>.*?</td>',row,re.S|re.I);assert len(cells)==len(r['cells']);checks+=1
  for j,(raw,cell) in enumerate(zip(cells,r['cells'])):
   assert raw==cell['raw_cell_html'] and j==cell['column'];assert clean(raw)==cell['text'];assert r['raw_fields'][cell['key']]==cell['text'];checks+=4
   label=re.search(r'data-label=["\']([^"\']*)["\']',raw)
   if label:assert html.unescape(label.group(1))==cell['key'];checks+=1
  for key,val in r['numeric'].items():
   raw=r['raw_fields'].get(key)
   expected=int(raw.replace(',','')) if raw is not None and re.fullmatch(r'[\d,]+',raw) else None
   assert expected==val;checks+=1
  if r['native_key'].startswith('ElectionDistrict'):native[(r['year'],r['office_key'])].add(r['native_key'])
 counts=[len(native[k]) for k in [(2024,'USSenator'),(2024,'PresidentandVicePresident'),(2020,'USSenator'),(2020,'PresidentandVicePresident'),(2022,'RepresentativeinCongress')]]
 assert counts==[530,533,436,439,516],counts
 # The fresh structure PDF text is an independent rendering of the exact original.
 structure=read(S/'data/turnout/extracts/structure-2024.json');text=(M/'previews/pdf/parent-7e63ed2c00c8/full-text.txt').read_text();lines=text.splitlines();parsed={}
 for lineno,line in enumerate(lines,1):
  m=re.match(r'^\s*(KENT|NEW CASTLE|SUSSEX)\s+(\d{2})-(\d{2})([12]?)\s+',line)
  if m:
   county,rd,ed,foot=m.groups();k='ElectionDistrict'+rd+ed;assert k not in parsed;parsed[k]=dict(county=county,rd=rd,ed=ed,footnote=foot or None,raw_line=line)
 assert len(parsed)==537 and set(parsed)==set(structure)
 for k,v in parsed.items():
  for field,value in v.items():assert structure[k][field]==value,(k,field);checks+=1
 # Workbook is a whole original ZIP too; audit every CRC/member and preserve all raw XML cells.
 workbook=next(read(p) for p in sorted((M/'source').glob('*.receipt.json')) if read(p)['url'].endswith('.xlsx'))
 import zipfile,io,zlib,xml.etree.ElementTree as ET
 z=zipfile.ZipFile(io.BytesIO(body(workbook)));members=[];sheets=[]
 for info in z.infolist():
  raw=z.read(info.filename);assert zlib.crc32(raw)&0xffffffff==info.CRC;members.append(dict(name=info.filename,bytes=len(raw),sha256=sha(raw),crc32=f'{info.CRC:08x}'))
  if re.match(r'xl/worksheets/sheet\d+.xml$',info.filename):
   root=ET.fromstring(raw);sheets.append(dict(member=info.filename,rows=[ET.tostring(row,encoding='unicode') for row in root.findall('.//{*}row')]))
 write('qa/structure-workbook-audit.json.gz',dict(source_id=workbook['id'],members=members,complete_sheet_rows=sheets))
 write('qa/historical-original-audit.json',dict(status='pass',checks=checks,candidate_rows=len(rows),tables=len(tables),native_scopes=counts,structure_rows=len(parsed),every_available_raw_cell_header_party_null_and_source_position_checked=True,all_unrelated_original_bodies_retained=True))
 print('PASS',checks,'original-field checks')
if __name__=='__main__':main()
