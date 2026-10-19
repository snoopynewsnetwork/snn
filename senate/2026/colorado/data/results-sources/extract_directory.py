#!/usr/bin/env python3
"""Parse all 64 roster blocks; retain raw layout lines and literal blanks/wraps."""
import json,gzip,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=json.loads(gzip.decompress((ROOT/'document-extracts.json.gz').read_bytes()))['sos-directory-roster']['text']
dirs=json.loads((ROOT/'directory-rows.json').read_text());names={q['county_literal'].upper():q['county_literal'] for q in dirs};out={};current=None
for page,body in enumerate(s.split('\f'),1):
 for line_no,line in enumerate(body.splitlines(),1):
  match=re.match(r'^([A-Z ]+?)\s{2,}(.+?)\s{2,}(\([0-9]{3}\).+?)\s{2,}([0-9]{2})\s*$',line)
  if match and match[1].strip() in names:
   name=names[match[1].strip()];current={'county_literal':name,'county_label_literal':match[1].strip(),'roster_county_id_literal':match[4],'page':page,'start_line':line_no,'address_column':match.start(2),'contact_column':match.start(3),'id_column':match.start(4),'layout_lines':[]};out[name]=current
  if current and current['page']==page:
   if line.startswith('Revised '):current=None;continue
   current['layout_lines'].append(line)
for name,q in out.items():
 lines=q['layout_lines'];
 while lines and not lines[-1].strip():lines.pop()
 a,c,i=q['address_column'],q['contact_column'],q['id_column'];q['literal_columns']=[{'left':line[:a].rstrip(),'address':line[a:c].strip(),'contact':line[c:i].strip(),'id':line[i:].strip()} for line in lines];q['clerk_literal']=' '.join(z['left'].strip() for z in q['literal_columns'][1:] if z['left'].strip());q['address_literal_lines']=[z['address'] for z in q['literal_columns']];q['contact_literal_lines']=[z['contact'] for z in q['literal_columns']];q['phone_literal']=q['literal_columns'][0]['contact'];q['fax_literal_lines']=[z['contact'] for z in q['literal_columns'] if z['contact'].lower().startswith('fax')];q['email_literal_lines']=[z['contact'] for z in q['literal_columns'] if '@' in z['contact'] or (z['contact'] and not z['contact'].lower().startswith('fax') and not z['contact'].startswith('('))];q['source_receipt']='sos-directory-roster';q['directory_revision_literal']='Revised 08.28.2026'
assert set(out)==set(q['county_literal'] for q in dirs),(len(out),set(names.values())-set(out))
(ROOT/'directory-contacts.json').write_text(json.dumps([out[q['county_literal']] for q in dirs],indent=2,ensure_ascii=False)+'\n');print('contacts',len(out));print('literal Summit email',out['Summit']['email_literal_lines']);print('literal Costilla email',out['Costilla']['email_literal_lines'])
