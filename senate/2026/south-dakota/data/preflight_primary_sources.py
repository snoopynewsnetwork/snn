#!/usr/bin/env python3
"""Original signed canvass county controls; no priority or geography approval."""
from pathlib import Path
import datetime,gzip,hashlib,json,re,subprocess,tempfile
D=Path(__file__).resolve().parent;N=D/'news'
def main():
 mf={a['id']:a for a in json.loads((N/'manifest.json').read_text())};sources={}
 def read(sid):
  a=mf[sid];z=(N/a['asset']).read_bytes();b=gzip.decompress(z);assert hashlib.sha256(z).hexdigest()==a['stored_sha256'] and hashlib.sha256(b).hexdigest()==a['raw_sha256'];assert len(z)<40000000 and a['status']==200
  with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
   f.write(b);f.flush();t=subprocess.run(['pdftotext','-layout',f.name,'-'],check=True,capture_output=True,text=True).stdout
  sources[sid]={'url':a['url'],'raw_sha256':a['raw_sha256'],'raw_bytes':len(b),'stored_bytes':len(z),'pdf_text_pages':t.count('\f')};return t
 def parse(t,start,end,n):
  sec=t.split(start,1)[1].split(end,1)[0];rg=re.compile(r'^([A-Za-z][A-Za-z .\'-]*?)\s+('+r'\s+'.join([r'[0-9][0-9,]*']*n)+r')\s*$');rows={};footer=None
  for ordinal,line in enumerate(sec.splitlines()):
   m=rg.match(line)
   if not m:continue
   name=m[1].strip();v=[int(x.replace(',','')) for x in m[2].split()]
   if name=='Total':assert footer is None;footer=v
   else:assert name not in rows;rows[name]={'votes':v,'source_line':line,'line_ordinal_in_section':ordinal}
  assert len(rows)==66,len(rows);assert footer is not None;assert [sum(r['votes'][i] for r in rows.values()) for i in range(n)]==footer;return {'counties':66,'controls':footer,'contest_votes':sum(footer),'rows':rows}
 tables={'2024_President':{'candidate_columns':['Kamala D Harris Democratic','Chase Oliver Libertarian','Donald J Trump Republican','Robert F Kennedy Jr Independent'],**parse(read('sos-2024-general-canvass'),'Presidential Electors','United States Representative',4)},'2022_Senate_other_ClassIII':{'candidate_columns':['Brian L Bengs Democratic','Tamara J Lesnar Libertarian','John R Thune Republican'],**parse(read('sos-2022-general-canvass'),'United States Senator','United States Representative',3)}}
 if 'sos-2020-general-canvass' in mf and mf['sos-2020-general-canvass'].get('status')==200:
  t=read('sos-2020-general-canvass');(N/'extracts/sos-2020-general-canvass.txt').write_text(t)
  tables['2020_Senate_same_ClassII']={'candidate_columns':['Mike Rounds Republican','Dan Ahlers Democratic'],**parse(t,'United States Senator','United States Representative',2)}
 result={'status':'all_county_control_preflight_pass_priority_unaccepted','sources':sources,'tables':tables,'scope':['All66 county native identities must be preserved; Oglala Lakota current name is not a new county to add to historical Shannon.','2026 ClassII uses2020 Rounds-Ahlers same-seat;2022 Thune-Bengs is otherClassIII/midterm,2024 had no Senate.','Bengs2022 Democratic identity does not redefine his2026 independent candidacy; current final roster requires primary verification.','Current ResultsMedia2026November setup/zero export is not actual counted votes or approved geography.','Actual2024 four county-canvass PDF groups and2022 precinct PDF retained; titles do not prove disjoint native completeness. No precinct or county priority accepted.']}
 (D/'coordinator-primary-preflight.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v['controls'] for k,v in tables.items()}))
if __name__=='__main__':main()
