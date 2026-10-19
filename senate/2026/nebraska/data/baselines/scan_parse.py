#!/usr/bin/env python3
"""Parse our independent PSM3 reading aid; manual repairs cite original image rows.
No peer transcription is used as numeric input. See scan-manual-repairs.json.
"""
import sys
sys.dont_write_bytecode=True
from extract import BASE,jsonl,dump
import gzip,json,re
PATTERNS=[('Rep Trump/Vance',r'Rep\s+Trump/Vance_?'),('Dem Harris/Walz',r'Dem\s+Harris/Walz'),('Lib Oliver/ter Maat',r'Lib\s+Oliver/ter Maat'),('Lmn West/Abdullah',r'L.m?n\s+West/Abd(?:ullah|utlah)'),('Pet Stein/Kpadenou',r'Pet\s+Stein/Kpadenou'),('Rep Deb Fischer',r'Rep\s+Deb Fischer'),('Pet Dan Osborn',r'Pet\s+Dan Osborn'),('Rep Pete Ricketts',r'Rep\s+Pete Ricket[tl]s'),('Dem Preston Love Jr.',r'Dem\s+Preston Love Jr\.?'),('Write-In Totals',r'Write[- ]?[Ilt]n Totals'),('Not Assigned',r'Not\s?Assigned'),('Total Votes Cast',r'Total Votes Cast'),('Overvotes',r'(?:_\.?\s*)?Overvotes'),('Undervotes',r'Undervotes'),('Contest Totals',r'Contest Totals')]
def main():
 repairs=json.loads((BASE/'source/scan-manual-repairs.json').read_text())if(BASE/'source/scan-manual-repairs.json').exists()else{}
 contexts=[];unresolved=[];labels=json.loads((BASE/'source/scan-manual-labels.json').read_text())
 for county in ['york','garfield','deuel']:
  pp=[json.loads(s)for s in gzip.decompress((BASE/f'extracts/extra-{county}-ocr.jsonl.gz').read_bytes()).splitlines()]
  for p in pp:
   text=p['OCR']['3'];headers=list(re.finditer(r'^US (President|Senator [26] YR)\s*$',text,re.M))
   for i,h in enumerate(headers):
    name=h[0].strip();block=text[h.end():headers[i+1].start()if i+1<len(headers)else len(text)]
    # Last selected Senate block must end before unrelated Congress office.
    block=re.split(r'^Congress Dist\.',block,flags=re.M)[0]
    fields={};rawlines={};n=1 if county=='garfield'else 4
    for line in block.splitlines():
     for label,pattern in PATTERNS:
      m=re.match(r'\s*'+pattern+r'(.*)',line,re.I)
      if m:
       tail=m[1];vals=[int(v.replace(',',''))for v in re.findall(r'\d[\d,]*',tail)]
       # Deuel president and regular Senate methods are printed blank, not zero.
       expected=1 if county=='deuel'and name!='US Senator 2 YR'else n
       key=f'{county}|{p["page"]}|{name}|{label}'
       if key in repairs:vals=repairs[key]['values']
       if len(vals)!=expected:
        unresolved.append(dict(key=key,raw_line=line,parsed=vals,expected=expected));vals=None
       if vals is not None and expected==1 and n==4:vals=vals+[None]*3
       fields[label]=vals;rawlines[label]=line;break
    for key,repair in repairs.items():
     prefix=f'{county}|{p["page"]}|{name}|'
     if key.startswith(prefix)and key.removeprefix(prefix)not in fields:
      vals=repair['values'];fields[key.removeprefix(prefix)]=vals+[None]*3 if county=='deuel'and name!='US Senator 2 YR'else vals
    contexts.append(dict(source_id=p['source_id'],county=county,page=p['page'],label=labels[county][str(p['page'])],native_id_literal=None,contest=name,kind='county_summary'if county=='deuel'else'alternate_source_native_context',method_columns=['TOTAL']if n==1 else['TOTAL','Election Day','Early Voting','Provisional'],fields=fields,original_OCR_lines=rawlines,original_image_path=p['image_path'],image_sha256=p['image_sha256'],manual_repair_keys=[k for k in repairs if k.startswith(f'{county}|{p["page"]}|{name}|')]))
 jsonl('extracts/independent-scan-contexts.jsonl.gz',contexts);dump('extracts/scan-unresolved.json',unresolved)
 print(json.dumps(dict(contexts=len(contexts),unresolved=len(unresolved))));print(json.dumps(unresolved,indent=2))
if __name__=='__main__':main()
