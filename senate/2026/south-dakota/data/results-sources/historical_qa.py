#!/usr/bin/env python3
"""Fresh OOXML replay and bounded local/PDF candidate-control checks."""
import sys
sys.dont_write_bytecode=True
from common import *
from inspect_sources import workbook
from reconstruct import reconstruct
import re,subprocess,collections

def main():
 c=json.loads((STATE/'data/turnout/priority-set.json').read_text());checks=[]
 news=json.loads((STATE/'data/news/manifest.json').read_text());e=next(x for x in news if x['id']=='sos-2024-public-presidential-precinct-export-684');sources={'2024':(STATE/'data/news'/e['asset'],e['raw_sha256'])}
 for e in json.loads((STATE/'data/baselines/source/senate-public-original-receipts.json').read_text()):sources[e['id'][-4:]]=(STATE/'data/turnout/source'/e['asset'],e['raw_sha256'])
 for y,(p,sha) in sources.items():
  b=gzip.decompress(p.read_bytes());assert hashlib.sha256(b).hexdigest()==sha;w=workbook(b);allrows={};footers={};headers={}
  for s in w['sheets']:
   for row in s['rows']:
    d={x['attributes']['r'].rstrip('0123456789'):x['value_resolved'] for x in row['cells']};rn=int(row['attributes']['r']);key=(s['member'],rn)
    if rn==7:headers[s['attributes']['name']]=d
    if d.get('B') and str(d.get('C','')).isdigit():
     if d['B']=='TOTALS':footers[s['attributes']['name']]=[int(d[k]) for k in ('CDEF' if y=='2024' else 'CDE' if y=='2022' else 'CD')]
     else:allrows[key]=(s['attributes']['name'],d)
  units=c['all_units'] if y=='2024' else c['separate_historical_native_universes'][y]['rows'];assert len(allrows)==len(units)=={'2024':691,'2022':687,'2020':693}[y]
  totals=[0]*(4 if y=='2024' else 3 if y=='2022' else 2)
  for u in units:
   loc=u['source_native_constituents'][0] if y=='2024' else {'member':u['sheet_member'],'row':int(u['source_row'])}
   name,d=allrows[(loc['member'],loc['row'])];assert d['B']==(u['native_label_literal'] if y=='2024' else u['native_label']);assert name==(u['county_literal'] if y=='2024' else u['county'])
   actual=[int(d[k]) for k in ('CDEF' if y=='2024' else 'CDE' if y=='2022' else 'CD')];expected=list(u['candidate_votes'].values()) if y=='2024' else [int(u[k]) for k in (['bengs_dem','lesnar_lib','thune_rep'] if y=='2022' else ['rounds_rep','ahlers_dem'])];assert actual==expected
   totals=[a+b for a,b in zip(totals,actual)]
  assert len(footers)==66
  assert totals=={'2024':[146811,2777,271938,7202],'2022':[91007,14697,242316],'2020':[276208,143970]}[y]
  for s in w['sheets']:
   ds=[d for name,d in allrows.values() if name==s['attributes']['name']];assert [sum(int(d[k]) for d in ds) for k in ('CDEF' if y=='2024' else 'CDE' if y=='2022' else 'CD')]==footers[s['attributes']['name']]
  checks.append({'year':y,'original':pin(p),'raw_sha256':sha,'native_rows':len(allrows),'full_county_footers':len(footers),'candidate_sums':totals,'literal_candidate_headers_all66':headers,'status':'pass original XML values/labels/locators, all county footers; no field repair'})
 # Independent bounded PDF examples: raw original, Poppler, candidate sums at actual published scope.
 reconstruct('shared','sos-2022-precinct-canvass','/tmp/sd-official-qa-2022.pdf');samples=[]
 for county,page,expected in [('Brown',110,[3893,451,9577]),('Hamlin',581,[366,123,2214])]:
  txt=subprocess.check_output(['pdftotext','-f',str(page),'-l',str(page),'-layout','/tmp/sd-official-qa-2022.pdf','-']).decode();rows=[]
  for l in txt.splitlines():
   m=re.match(r'^(.*?)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$',l)
   if m:rows.append({'label_line_literal':m[1],'votes':[int(m[i].replace(',','')) for i in (2,3,4)]})
  total=next(r for r in rows if r['label_line_literal'].strip()=='Total');native=[r for r in rows if r is not total];assert total['votes']==expected==[sum(r['votes'][i] for r in native) for i in range(3)]
  samples.append({'county':county,'original':'data/news/sos-2022-precinct-canvass.html.gz','physical_page_1based':page,'native_rows':len(native),'candidate_order':['Bengs DEM','Lesnar LIB','Thune REP'],'sum':expected,'method_scope':'literal Absentee Precinct if printed, otherwise unsplit/unavailable; not polling-mode allocation','complete_page_text':txt})
 txt=(ROOT/'lincoln-2022.txt').read_text().split('\f')[0];rows=[]
 for l in txt.splitlines():
  m=re.match(r'^(.*?)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$',l)
  if m:rows.append({'label_line_literal':m[1],'votes':[int(m[i].replace(',','')) for i in (2,3,4)]})
 total=next(r for r in rows if r['label_line_literal'].strip()=='Total');native=[r for r in rows if r is not total];assert total['votes']==[7365,912,19703]==[sum(r['votes'][i] for r in native) for i in range(3)]
 samples.append({'county':'Lincoln','receipt':'raw/lincoln-2022.receipt.json','physical_page_1based':1,'native_rows':len(native),'sum':total['votes'],'method_scope':'No method dimension printed; county geography labels/combined groups only','rows':rows})
 txt=(ROOT/'lake-2022.txt').read_text();lake=[]
 for name in ['Brian L Bengs','Tamara J Lesnar','John R Thune']:
  line=next(l for l in txt.splitlines() if l.startswith(name));vals=[int(v.replace(',','')) for v in re.findall(r'\d[\d,]*',line)];assert len(vals)==11 and sum(vals[:10])==vals[-1];lake.append({'candidate_line_literal':line,'P1_through_P10':vals[:10],'total':vals[-1]})
 assert [r['total'] for r in lake]==[1139,164,3615];samples.append({'county':'Lake','receipt':'raw/lake-2022.receipt.json','physical_page_1based':1,'native_columns':10,'candidate_rows':lake,'method_scope':'Unsplit P1-P10 source columns; no2026 join'})
 # County controls are compared by proven original election scope, never current labels.
 hist=c['separate_historical_native_universes']['2022']['rows']
 for sample in samples:
  sums=[sum(int(r[k]) for r in hist if r['county']==sample['county']) for k in ['bengs_dem','lesnar_lib','thune_rep']];assert sums==sample.get('sum',[r['total'] for r in sample.get('candidate_rows',[])])
 dump('historical-source-qa.json',{'complete_OOXML_replay':checks,'bounded_original_PDF_samples':samples,'visual_inspection':'Eight full original first/source pages actually rendered and viewed: Brown2022p110,Hamlin2022p581,Aurora2024certificatep1,Lincoln2022p1,Lincoln2024p1,Lake2022p1,Lincoln2026ballotp1,Hanson2026ballotp1. Lincoln2024scan footer visually12981/227/22621/564 matches frozen signed controls; no full scan-row transcription claimed.','limits':'Numeric original replay covers published workbook scope, not missing194/41 signed votes. No native Yankton PDF rows fabricated. Original2022PDF679/65 companion remains distinct from workbook687/66.'})
 print('historical QA:2071 full workbook native rows/198 footers and4 bounded PDF county samples pass')
if __name__=='__main__':main()
