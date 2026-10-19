#!/usr/bin/env python3
"""Verify independent printed2024 vectors against literal raw OOXML candidate keys.
Poppler text extraction preserves page/line positions; two typographic apostrophes
are explicitly paired for this within-election presentation comparison only.
"""
from pathlib import Path
import csv,gzip,hashlib,json,re,subprocess,tempfile
D=Path(__file__).resolve().parent;N=D.parent/'news';H=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def text(raw):
 with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
  f.write(raw);f.flush();return subprocess.check_output(['pdftotext','-layout',f.name,'-']).decode()
def main():
 m={x['id']:x for x in json.loads((N/'manifest.json').read_text())};rec=m['sos-2024-canvass'];stored=(N/rec['asset']).read_bytes();raw=gzip.decompress(stored)
 assert H(stored)==rec['stored_sha256']and H(raw)==rec['raw_sha256'];txt=text(raw);(D/'source/canvass2024.txt').write_text(txt);pages=txt.split('\f')
 b=json.loads(gzip.decompress((D/'source/2024-races-rows.json.gz').read_bytes()));rr=[r for r in b['sheets'][0]['rows']if r['cells'].get('D')=='United States President'];native={}
 for r in rr:
  a=r['cells'];native.setdefault((a['A'].removesuffix(' County'),a['B']),{})[a['F']]=int(a['G'])
 order=[r['cells']['F']for r in rr[:13]];counties=sorted({c for c,p in native},key=lambda c:-len(c));positions=[];aliases={('Bingham','MORGAN’S PASTURE 28'):('Bingham',"MORGAN'S PASTURE 28"),('Cassia','121 Starrh’s Ferry'):('Cassia',"121 Starrh's Ferry")};state=None;seen=set()
 for pi,p in enumerate(pages[3:29],4):
  for li,l in enumerate(p.splitlines(),1):
   matches=list(re.finditer(r'(?<![\w.])\d[\d,]*(?![\w.])',l))
   if len(matches)<13:continue
   values=[int(x.group().replace(',',''))for x in matches[-13:]]
   if 'Race Total'in l:state=values;positions.append(dict(page=pi,line=li,role='statewide_race_control',original_line=l,values=values));continue
   prefix=l[:matches[-13].start()].strip();c=next(c for c in counties if prefix.startswith(c+' '));pk=(c,prefix[len(c):].strip());key=aliases.get(pk,pk)
   assert key not in seen;seen.add(key);assert values==[native[key][name]for name in order],(key,pi,li)
   positions.append(dict(page=pi,line=li,role='native_president',printed_county=pk[0],printed_precinct=pk[1],OOXML_county=key[0]+' County',OOXML_precinct=key[1],explicit_typographic_pair=pk!=key,original_line=l,values=values))
 assert len(seen)==985 and seen==set(native)
 assert state==[sum(x[name]for x in native.values())for name in order]
 # Statistical rows include dash turnout when registration is zero.
 b=json.loads(gzip.decompress((D/'source/2024-stats-rows.json.gz').read_bytes()));stat={(r['cells']['A'].removesuffix(' County'),r['cells']['B']):r for r in b['sheets'][0]['rows'][1:]};seen=set();statpositions=[]
 for pi,p in enumerate(pages[287:],288):
  for li,l in enumerate(p.splitlines(),1):
   matches=list(re.finditer(r'(?<![\w.])(?:\d[\d,]*(?:\.\d+)?%?|-(?=\s|$))(?![\w.])',l))
   if len(matches)<5:continue
   nums=matches[-5:]
   if not all(re.fullmatch(r'\d[\d,]*',x.group())for x in nums[:4]):continue
   prefix=l[:nums[0].start()].strip();c=next((c for c in counties if prefix.startswith(c+' ')),None)
   if c is None:continue
   label=prefix[len(c):].strip();pk=(c,label);key=(c,'Total'if label=='County Total'else label);key=aliases.get(key,key)
   assert key in stat,(pi,li,pk);assert key not in seen;seen.add(key);r=stat[key];values=[int(x.group().replace(',',''))for x in nums[:4]];assert values==[int(r['cells'][col])for col in 'CDEF']
   statpositions.append(dict(page=pi,line=li,role='overlapping_county_control'if key[1]=='Total'else'native_statistics',printed_county=c,printed_precinct=label,OOXML_precinct=key[1],OOXML_source_row=r['row'],values=values,original_line=l))
 assert len(seen)==1030 and seen==set(stat),(len(seen),len(stat),set(stat)-seen)
 (D/'source/printed-2024-positions.json.gz').write_bytes(gzip.compress((json.dumps(dict(category_order=order,president=positions,statistics=statpositions),ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
 # Reuse existing national originals by exact hash; independently extract their original PDFs.
 refs=[];national={};base=D.parents[2]/'new-hampshire/data/turnout/source'
 for sid in ['fec-pres-2024','house-clerk-2024']:
  r=json.loads((base/(sid+'.json')).read_text());p=base/r['body_path'];b=p.read_bytes();pdf=gzip.decompress(b);assert H(b)==r['stored_sha256']and H(pdf)==r['original_sha256'];t=text(pdf);(D/'source'/(sid+'.txt')).write_text(t)
  refs.append(dict(id=sid,original_record_path=str((base/(sid+'.json')).relative_to(D.parents[2])),original_asset_path=str(p.relative_to(D.parents[2])),original_sha256=H(pdf),stored_sha256=H(b),original_bytes=len(pdf),stored_bytes=len(b),requested_url=r['requested_url'],final_url=r['final_url'],retrieved_utc=r['retrieved_utc'],status=r['status'],headers_record_path=str((base/r['headers_path']).relative_to(D.parents[2])),original_metadata_sha256=H((base/(sid+'.json')).read_bytes()),headers_sha256=r['headers_sha256']))
  national[sid]=t
 dump(D/'source/reused-national-originals.json',refs)
 (D/'source/pdf-primary-controls.json').write_text(json.dumps(dict(source_original_sha256=H(raw),printed_presidential_native_vectors=985,printed_statistical_native_rows=986,printed_overlapping_statistical_county_rows=44,all_presidential_categories_equal_OOXML=True,all_4_statistical_integer_columns_equal_OOXML=True,printed_presidential_state_vector=state,category_order=order,explicit_presentation_pairs=[dict(printed=list(k),OOXML=list(v))for k,v in aliases.items()],printed_county_footer_pair=dict(PDF='County Total',OOXML='Total'),national_sources_reused=True),indent=2)+'\n')
 print('Printed 985x13 presidential cells + 1030x4 statistical controls match original OOXML.')
 # Save two bounded source-page previews for visual confirmation.
 with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
  f.write(raw);f.flush()
  for page in [29,303]:subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','2000','-singlefile','-png',f.name,str(D/'source'/f'canvass2024-page{page}')],check=True,stdout=subprocess.DEVNULL)
if __name__=='__main__':main()
