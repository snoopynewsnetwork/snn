#!/usr/bin/env python3
"""Original all21-county Senate controls and published vintage disagreement."""
from pathlib import Path
import gzip,hashlib,json,re,subprocess,tempfile
D=Path(__file__).resolve().parent;N=D/'news';ROOT=D.parent
COUNTIES=['ATLANTIC','BERGEN','BURLINGTON','CAMDEN','CAPE MAY','CUMBERLAND','ESSEX','GLOUCESTER','HUDSON','HUNTERDON','MERCER','MIDDLESEX','MONMOUTH','MORRIS','OCEAN','PASSAIC','SALEM','SOMERSET','SUSSEX','UNION','WARREN']
def pdftext(b):
 with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
  f.write(b);f.flush();return subprocess.run(['pdftotext','-layout',f.name,'-'],check=True,capture_output=True,text=True).stdout

def main():
 mf={a['id']:a for a in json.loads((N/'manifest.json').read_text())};tables={};sources={}
 C={2024:['ANDY KIM (w)','CURTIS BASHAW','CHRISTINA KHALIL','KENNETH R. KAPLAN','PATRICIA G. MOONEYHAM','JOANNE KUNIANSKY'],2020:['CORY BOOKER (w) *','RIKIN "RIK" MEHTA','MADELYN R. HOFFMAN','VERONICA FERNANDEZ','DANIEL BURKE'],2018:['ROBERT MENENDEZ (w)','BOB HUGIN','MADELYN R. HOFFMAN','MURRAY SABRIN','NATALIE LYNN RIVERA','TRICIA FLANAGAN','KEVIN KIMPLE','HANK SCHROEDER']}
 pattern=re.compile(r'^\s+('+'|'.join(COUNTIES)+r')\s+.*?\s+([0-9][0-9,]*)\s*$')
 for year,names in C.items():
  sid=f'sos-{year}-senate-county';a=mf[sid];z=(N/a['asset']).read_bytes();b=gzip.decompress(z);assert hashlib.sha256(z).hexdigest()==a['stored_sha256'] and hashlib.sha256(b).hexdigest()==a['raw_sha256'];text=pdftext(b);pages=text.split('\f');candidates=[]
  for i,name in enumerate(names):
   p=pages[i];assert name in p;rows={};total=None
   for no,line in enumerate(p.splitlines()):
    m=pattern.match(line)
    if m:assert m[1] not in rows;rows[m[1]]={'votes':int(m[2].replace(',','')),'source_line':line,'line_ordinal':no}
    m=re.match(r'^\s+Total\s+([0-9][0-9,]*)\s*$',line)
    if m:assert total is None;total=int(m[1].replace(',',''))
   assert set(rows)==set(COUNTIES) and sum(r['votes'] for r in rows.values())==total,(year,name,len(rows),total)
   candidates.append({'literal_candidate_header':name,'PDF_page':i+1,'state_total':total,'county_rows':rows})
  tables[str(year)]={'candidates':candidates,'reported_named_total':sum(c['state_total'] for c in candidates),'counties':21,'candidate_county_cells':21*len(candidates)};sources[str(year)]=a
 clerk=ROOT.parent/'michigan/data/baselines/house-statistics2020.pdf';b=clerk.read_bytes();t=pdftext(b);section=t.split('NEW JERSEY',1)[1].split('FOR UNITED STATES REPRESENTATIVE',1)[0];vals={}
 for key,pattern in [('Cory Booker',r'Cory A\. Booker[^\n]+?([0-9][0-9,]*)\s*$'),('Rikin Mehta',r'Rikin[^\n]+?Mehta[^\n]+?([0-9][0-9,]*)\s*$')]:
  m=re.search(pattern,section,re.M);assert m;vals[key]=int(m[1].replace(',',''))
 assert vals=={'Cory Booker':2541178,'Rikin Mehta':1817052}
 difference={'Booker':tables['2020']['candidates'][0]['state_total']-vals['Cory Booker'],'Mehta':tables['2020']['candidates'][1]['state_total']-vals['Rikin Mehta']};assert difference=={'Booker':61,'Mehta':39}
 result={'status':'original_county_controls_pass_with_vintage_gap_priority_unaccepted','sources':sources,'tables':tables,'Clerk2020_primary_reference':{'path':str(clerk.relative_to(ROOT.parent)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'candidate_controls':vals},'current_SOS_minus_Clerk2020':difference,'scope':['Current2020SOSPDF literal date10/14/2021;2024PDF12/05/2024. Date disagreement does not prove correction cause.','All21county vectors reconcile source footers; no allocation/rescaling to remove61/39votes.','Candidate header flags(w)and* retained verbatim; identity/party and write-in scope require source documentation.','2022no statewideSenate/Gov; actual2018Senatemidterm original nowreconcilesall21/eightcandidates;separate2022ballot/House context remainsdistinct.','County tables are not native precinct completeness or current approval; independent question workers required.']};(D/'coordinator-primary-preflight.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'state_controls':{k:[r['state_total'] for r in v['candidates']] for k,v in tables.items()},'SOS_minus_Clerk2020':difference}))
if __name__=='__main__':main()
