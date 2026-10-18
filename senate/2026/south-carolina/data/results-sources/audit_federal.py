#!/usr/bin/env python3
"""Verify reused complete federal originals and exact SC source-page controls."""
import pathlib,json,gzip,hashlib,subprocess,re
from acquire import ROOT
T=ROOT.parent/'turnout';D=ROOT.parent;pin=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(ident):
 mp=T/'source'/f'{ident}.meta.json';m=json.loads(mp.read_text());p=(mp.parent/m['body_path']).resolve();b=p.read_bytes();assert sha(b)==m['stored_sha256'] and len(b)==m['stored_bytes'];raw=gzip.decompress(b) if p.suffix=='.gz' else b;assert sha(raw)==m['original_sha256'] and len(raw)==m['original_bytes'];pin.extend([{'path':str(p),'bytes':len(b),'sha256':sha(b),'role':'reused complete federal original '+ident},{'path':str(mp),'bytes':mp.stat().st_size,'sha256':sha(mp.read_bytes()),'role':'federal acquisition metadata'}]);s=subprocess.run(['pdftotext','-layout','-','-'],input=raw,capture_output=True,check=True).stdout.decode();return m,s.split('\f')
controls={}
for ident in ['nara-2024','house-2024','house-2020','house-2022']:
 m,pages=load(ident)
 if ident=='nara-2024':
  txt='\n'.join(pages);vals=[1483747,1028452,12669,8117,6744,5352,3059]
  for v in vals:assert f'{v:,}' in txt
  controls[ident]={'source_url':m['requested_url'],'pages':[1,2],'one_per_slate_votes':vals,'total':sum(vals),'repeated_VP_and_elector_rows_not_additive':True,'document_date':'2024-12-09'}
 else:
  matches=[(i+1,p) for i,p in enumerate(pages) if 'SOUTH CAROLINA' in p and 'FOR UNITED STATES' in p.upper()];page,txt=matches[0];sc=txt[txt.index('SOUTH CAROLINA'):];prefix=sc.split('FOR UNITED STATES REPRESENTATIVE')[0] if 'FOR UNITED STATES REPRESENTATIVE' in sc else sc.split('For United States Representative')[0]
  values={'house-2024':[1483747,1028452,12669,8117,6744,3059],'house-2020':[1110828,1369137,32845],'house-2022':[1066274,627616,1812]}[ident]
  for v in values:assert f'{v:,}' in prefix
  if ident=='house-2024':assert '5,352' not in prefix
  if ident=='house-2020':assert '2,294' not in prefix and 'Constitution' in prefix
  controls[ident]={'source_url':m['requested_url'],'PDF_page':page,'original_section_text':prefix,'displayed_candidate_values':values,'displayed_sum':sum(values),'scope':'presidential six displayed rows; Terry5352 omitted' if ident=='house-2024' else 'three named Senate candidates; generic writein2294 omitted' if ident=='house-2020' else 'Senate all three including1812writeins'}
m=next(x for x in json.loads((D/'news/manifest.json').read_text()) if x['id']=='fec-2024-presidential-original');p=D/'news'/m['asset'];b=p.read_bytes();raw=gzip.decompress(b);assert sha(b)==m['stored_sha256'] and sha(raw)==m['raw_sha256'];pin.append({'path':str(p),'bytes':len(b),'sha256':sha(b),'role':'FEC2024 original'});s=subprocess.run(['pdftotext','-layout','-','-'],input=raw,capture_output=True,check=True).stdout.decode();rows=[]
for i,page in enumerate(s.split('\f')):
 for j,line in enumerate(page.splitlines()):
  if re.match(r'^SC\s',line):rows.append({'PDF_page':i+1,'line_ordinal_on_page':j,'raw_line':line,'page_header':page[:1200]})
for value in [3059,1028452,12669,8117,5352,1483747,6744,2548140]:assert any(f'{value:,}' in r['raw_line'] for r in rows)
controls['fec-2024']={'URL':m['url'],'final_URL':m['final_url'],'SC_original_row_locators':rows,'seven_slate_total':2548140,'scope':'separate candidate-column pages; not extra votes beyond NARA/ENR/DB'}
(ROOT/'federal-controls.json').write_text(json.dumps({'status':'pass_reused_original_bytes_and_SC_controls','original_pins':pin,'controls':controls,'visual_review':'NARA bothpages; House2024SC,House2020SC,House2022SC existing original-page renders independently inspected'},indent=2)+'\n');print('Federal original controls pass;',len(rows),'FEC SC rows')
