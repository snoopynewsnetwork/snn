#!/usr/bin/env python3
"""Coordinator preflight of retained linked primary files, not dispatch acceptance."""
from pathlib import Path
from collections import Counter
import datetime,gzip,hashlib,io,json,re,subprocess,zipfile
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parent
NEWS=ROOT/'news';sources={r['id']:r for r in json.loads((NEWS/'manifest.json').read_text())}
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def raw(source):
 m=sources[source];s=(NEWS/m['asset']).read_bytes();b=gzip.decompress(s)
 assert m['status']==200 and hashlib.sha256(s).hexdigest()==m['stored_sha256'] and hashlib.sha256(b).hexdigest()==m['raw_sha256'] and len(b)==m['bytes']
 return b
def sheet(z,number):
 ss=[''.join(t.itertext())for t in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]if'xl/sharedStrings.xml'in z.namelist()else[]
 for row in E.fromstring(z.read(f'xl/worksheets/sheet{number}.xml')).findall('m:sheetData/m:row',ns):
  d={}
  for c in row:
   v=c.find('m:v',ns);value=v.text if v is not None else''
   if c.get('t')=='s':value=ss[int(value)]
   elif c.get('t')=='inlineStr':value=''.join(c.find('m:is',ns).itertext())
   if value:d[re.sub(r'\d+$','',c.get('r'))]=value
  yield int(row.get('r')),d
checks=[]
for source in sources:
 if source.startswith('sos-20'):
  b=raw(source);record={'source_id':source,'URL':sources[source]['url'],'original_bytes':len(b),'original_sha256':sources[source]['raw_sha256']}
  if b.startswith(b'PK'):
   with zipfile.ZipFile(io.BytesIO(b))as z:
    assert z.testzip()is None
    w=E.fromstring(z.read('xl/workbook.xml'));record['worksheets']=[e.get('name')for e in w.iter()if e.tag.endswith('}sheet')];record['ZIP_members']=len(z.namelist())
  else:assert b.startswith(b'%PDF-')
  checks.append(record)
with zipfile.ZipFile(io.BytesIO(raw('sos-2024-president-county')))as z:
 sums=Counter();county=Counter();count=0
 for row,d in sheet(z,1):
  if row==1:continue
  if not d.get('J','').isdigit():continue
  assert d['G']=='President / Vice President'
  votes=int(d['J']);sums[d['H']]+=votes;county[d['E']]+=votes;count+=1
 assert len(county)==105 and count==18268
 turnout=list(sheet(z,2));assert turnout[0][1]=={'A':'County','B':'Ballots Cast','C':'Registered Voters','D':'Turnout %'}
 county_turnout={d['A']:{'ballots_cast':int(d['B']),'registered_voters':int(d['C']),'turnout_literal':d['D']}for row,d in turnout[1:]if d.get('B','').isdigit()and d.get('C','').isdigit()}
 turnout_state=county_turnout.pop('Total')
 county_name_aliases={'Comanche ':'Comanche'}
 assert {county_name_aliases.get(n,n)for n in county}==set(county_turnout)
 for metric in ['ballots_cast','registered_voters']:assert sum(r[metric]for r in county_turnout.values())==turnout_state[metric]
text=subprocess.run(['pdftotext','-layout','-','-'],input=raw('sos-2024-general-canvass'),stdout=subprocess.PIPE,check=True).stdout.decode()
section=text.split('President / Vice President',1)[1].split('United States House of Representatives 1',1)[0]
controls={}
for label in sums:
 match=re.search(re.escape(label)+r'\s+([\d,]+)\s+([\d.]+)%',section);assert match,label
 controls[label]=int(match[1].replace(',',''));assert controls[label]==sums[label]
ranked=sorted(county,key=lambda name:(-county[name],name));den=sum(county.values());running=0;priority=[]
for name in ranked:
 if running*5>=den*4:break
 priority.append(name);running+=county[name]
primary2026=subprocess.run(['pdftotext','-layout','-','-'],input=raw('sos-2026-primary-canvass'),stdout=subprocess.PIPE,check=True).stdout.decode().split('United States Senate',1)[1].split('United States House of Representatives 1',1)[0]
primary_counts=Counter()
for party,name,votes in re.findall(r'^\s+([DR])-([^\n]+?)\s+([\d,]+)\s+[\d.]+%',primary2026,re.M):primary_counts[party]+=int(votes.replace(',',''))
assert len(re.findall(r'^\s+[DR]-',primary2026,re.M))==13
result={'status':'pass','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Retained primary-source preflight only; workers must independently reconcile full native topology, source units and exact county priority before acceptance.','primary_files':checks,'2024_named_candidate_controls':controls,'county_coverage':105,'broader_2024_native_rows':count,'2024_named_candidate_denominator':den,'top15_votes':sum(county[n]for n in ranked[:15]),'provisional_priority_count':len(priority),'provisional_priority_votes':running,'provisional_preceding_votes':running-county[priority[-1]],'provisional_priority_names':priority,'crossing':{'county':priority[-1],'votes':county[priority[-1]]},'county_turnout_controls':county_turnout,'2026_primary_certified_party_sums':dict(primary_counts),'limits':['Broader2024 source has district/location/counties/precinct/candidate rows, not a county-only table despite captureID.','Precinct workbooks each have separate Johnson/Sedgwick/Shawnee/Wyandotte worksheets; determine overlap/complement before aggregation.','VTD fields, local precinct codes and county names are distinct; preserve zero rows, string/native IDs and unknown crosswalks.','Reported named candidate universe excludes unreported write-in/under/over categories; do not infer those categories zero.','Current2026 primary certification differs preliminary NPR/AP snapshots; no causal chronology inferred from metadata alone.']}
result['county_name_aliases']=county_name_aliases
result['published_turnout_state_footer']=turnout_state
out=ROOT/'coordinator-primary-preflight.json'
if out.exists():
 old=json.loads(out.read_text())
 if {k:v for k,v in old.items()if k!='checked_utc'}=={k:v for k,v in result.items()if k!='checked_utc'}:result['checked_utc']=old['checked_utc']
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k not in('primary_files','county_turnout_controls')},indent=2))
