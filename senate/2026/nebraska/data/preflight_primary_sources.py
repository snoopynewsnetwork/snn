#!/usr/bin/env python3
"""Original canvass preflight; source tables and candidate identities stay separate."""
from pathlib import Path
import collections,datetime,gzip,hashlib,json,re,subprocess,tempfile
D=Path(__file__).resolve().parent;N=D/'news'
def main():
 mf={a['id']:a for a in json.loads((N/'manifest.json').read_text())};sources={};pages={}
 for year in [2024,2022,2020]:
  sid=f'sos-{year}-canvass';a=mf[sid];z=(N/a['asset']).read_bytes();b=gzip.decompress(z)
  assert hashlib.sha256(z).hexdigest()==a['stored_sha256'] and hashlib.sha256(b).hexdigest()==a['raw_sha256'] and len(b)==a['bytes'];assert a['status']==200
  with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
   f.write(b);f.flush();t=subprocess.run(['pdftotext','-layout',f.name,'-'],check=True,capture_output=True,text=True).stdout
  pages[year]=t.split('\f');sources[year]={'id':sid,'url':a['url'],'sha256':a['raw_sha256'],'bytes':len(b),'pdf_text_pages':len(pages[year])-1}
 def parse(pp,n):
  rg=re.compile(r'([A-Za-z][A-Za-z .\'-]*?)\s+('+r'\s+'.join([r'[0-9][0-9,]*']*n)+r')(?=\s{2,}|$)');allrows={};footer=None
  for p in pp:
   for ordinal,line in enumerate(p.splitlines()):
    if line.startswith('General Election'):continue
    for m in rg.finditer(line):
     name=m[1].strip();v=[int(x.replace(',','')) for x in m[2].split()]
     if name=='Total':assert footer is None;footer=v
     elif name not in ['Page']:assert name not in allrows,(name,line);allrows[name]={'votes':v,'raw_line':line,'line_ordinal':ordinal}
  assert len(allrows)==93,len(allrows);assert footer is not None;assert [sum(r['votes'][i] for r in allrows.values()) for i in range(n)]==footer
  return {'county_count':93,'state_controls':footer,'county_rows':allrows}
 tables={
  '2024_Senate_ClassI_six_year':{'candidate_columns':['Deb Fischer Republican','Dan Osborn By Petition','Write-In Scatterings'],**parse([pages[2024][15]],3)},
  '2024_Senate_ClassII_two_year':{'candidate_columns':['Pete Ricketts Republican','Preston Love Jr Democratic'],**parse([pages[2024][16]],2)},
  '2020_Senate_ClassII_six_year':{'candidate_columns':['Ben Sasse Republican','Chris Janicek Democratic','Gene Siadek Libertarian','Preston Love Jr Write-In','Write-In Scatterings'],**parse([pages[2020][15],pages[2020][16]],5)}}
 for t in tables.values():t['contest_votes']=sum(t['state_controls'])
 result={'status':'original_county_controls_pass_priority_unaccepted','sources':sources,'tables':tables,'scope':['2026 ClassII regular must distinguish2024 same-seat special from2024 independent-led otherClassI race.','Osborn raw By Petition is not Democrat; show named-opposition scenarios separately.','Preston Love Jr2020 qualified write-in and2024 Democratic nominee are source-specific identities; generic scattering separate.','2022 gubernatorial midterm is not a Senate election.','County tables do not establish native precinct completeness/current geography. Independent workers must recover native controls and complete candidate universes.']}
 (D/'coordinator-primary-preflight.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:t['state_controls'] for k,t in tables.items()}))
if __name__=='__main__':main()
