#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
from acquire import *
from collections import Counter,defaultdict
import re,fitz,subprocess

def run():
 fs=[]
 for p in sorted((ROOT/'raw').glob('native-page-*.request.json')):fs+=js(p.stem.replace('.request',''))['features']
 by=defaultdict(list)
 for f in fs:by[f['attributes']['CodeMapNum']].append(f)
 print('map label counts',[(k,len(v)) for k,v in by.items()]);print('geometry',Counter(tuple(x.get('geometry',{}).keys()) for x in fs))
 c=json.loads((ROOT.parent/'data/turnout/priority-set.json').read_text());rows=[]
 for county in c['counties']:
  prefix='P-'+county['county_fips'][-2:]+'-';ff=[f for k,v in by.items() if k.startswith(prefix) for f in v]
  rows.append({'county':county['name'],'county_fips':county['county_fips'],'native_count':len(ff),'map_labels':dict(Counter(f['attributes']['CodeMapNum'] for f in ff)),'bills':sorted(set(str(f['attributes']['Bill']) for f in ff)),'effective_dates':sorted(set(str(f['attributes']['EffectiveDate']) for f in ff)),'local_urls':sorted(set(str(f['attributes']['Local_Voter_Reg']) for f in ff)),'map_urls':sorted(set(str(f['attributes']['RFAMapURL']) for f in ff))})
 (ROOT/'native-scope-inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
 links=json.loads((ROOT/'rfa-pdf-links.json').read_text());pdf=[]
 for link in links:
  n='media-'+link['media'].split('/')[-1];m=ROOT/'raw'/f'{n}.request.json'
  if not m.exists():continue
  d=json.loads(m.read_text());doc=fitz.open(stream=body(n),filetype='pdf');texts=[p.get_text(sort=True) for p in doc];(ROOT/'derived'/f'{n}.txt').write_text('\n\f\n'.join(texts));pages=[]
  for i,p in enumerate(doc):
   out=ROOT/'qa'/f'{n}-page-{i+1:02d}'
   if not out.with_suffix('.png').exists():subprocess.run(['pdftoppm','-f',str(i+1),'-l',str(i+1),'-singlefile','-scale-to','1800','-png',str(ROOT/d['path']),str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   pages.append({'page':i+1,'media_box':list(p.mediabox),'crop_box':list(p.cropbox),'rotation':p.rotation,'preview':str(out.with_suffix('.png').relative_to(ROOT)),'text_path':'derived/'+n+'.txt'})
  startxref=re.findall(rb'startxref\s+(\d+)',body(n));pdf.append({'id':n,'label':link['label'],'parent_media':link['media'],'original':d['path'],'sha256':d['original_sha256'],'bytes':d['original_bytes'],'metadata':doc.metadata,'pages':pages,'page_count':len(doc),'pdf_startxref_offsets':[int(x) for x in startxref],'printed_date_candidates':sorted(set(re.findall(r'(?:\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\b\d{1,2}/\d{1,2}/\d{2,4})',' '.join(texts),re.I)))})
  print(n,len(doc),doc.metadata.get('creationDate'),pdf[-1]['printed_date_candidates'],flush=True)
 (ROOT/'pdf-inventory.json').write_text(json.dumps(pdf,indent=2)+'\n')
if __name__=='__main__':run()
