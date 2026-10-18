#!/usr/bin/env python3
import json,gzip,collections
from extract import ROOT,STATE,textfile,writejson
controls=json.loads((ROOT/'historical-controls.json').read_text());out={}
for year in [2022,2020]:
 pref='MNGOV' if year==2022 else 'USSEN';natives=[]
 with gzip.open(ROOT/f'native-{year}.jsonl.gz','rt') as f:
  for line in f:
   n=json.loads(line);h=n['headers_by_column'];vals={h[''.join(t for t in c['address'] if t.isalpha())]:c['value'] for c in n['all_cells'] if h[''.join(t for t in c['address'] if t.isalpha())]!='TABMODEL'};natives.append(vals)
 idx={(int(v['COUNTYCODE']),v['PCTCODE']):v for v in natives};state=textfile(f'export-{year}-state');pct=textfile(f'export-{year}-precinct');stats=textfile(f'export-{year}-statistics');county=textfile(f'export-{year}-county') if year==2020 else None
 mapping={x['fields'][7]:pref+x['fields'][10] for x in state};check={'candidate_state_controls':[],'native_candidate_positions':len(pct),'county_candidate_controls':87*len(state),'differences':[],'method_differences':[],'direct_county_export':year==2020,'candidate_names_to_workbook':mapping,'native_rows':len(natives)}
 for row in state:
  a=row['fields'];name=a[7];field=mapping[name];v=int(a[13]);ps=sum(int(x['fields'][13]) for x in pct if x['fields'][7]==name);ws=sum(int(n[field]) for n in natives);check['candidate_state_controls'].append({'candidate':name,'source_party':a[10],'state':v,'precinct_sum':ps,'workbook':ws,'equal':v==ps==ws})
 for row in pct:
  a=row['fields'];v=idx[(int(a[1]),a[2])];f=mapping[a[7]]
  if int(a[13])!=int(v[f]):check['differences'].append({'line':row['line'],'field_index':13,'county_id':a[1],'precinct_id':a[2],'candidate':a[7],'text':a[13],'workbook':v[f]})
 for key in {int(n['COUNTYCODE']) for n in natives}:
  for name,field in mapping.items():
   s=sum(int(n[field]) for n in natives if int(n['COUNTYCODE'])==key);p=sum(int(x['fields'][13]) for x in pct if int(x['fields'][1])==key and x['fields'][7]==name);assert s==p,(year,key,name)
 for row in stats:
  a=row['fields'];v=idx[(int(a[1]),a[2])]
  for j,f in [(5,'REG7AM'),(6,'EDR'),(7,'SIGNATURES'),(8,'AB_MB'),(9,'FEDONLYAB'),(10,'PRESONLYAB'),(11,'TOTVOTING')]:
   if year==2022 and f=='PRESONLYAB':continue
   # pctstats includes president-only column even when workbook2022omits it; do not invent workbookzero.
   if v.get(f)!=a[j]:check['method_differences'].append({'line':row['line'],'field_index':j,'county_id':a[1],'precinct_id':a[2],'field':f,'text':a[j],'workbook':v.get(f)})
 for id in ['state','precinct','statistics','precincts']+(['county'] if year==2020 else []):
  rows=textfile(f'export-{year}-{id}')
  with gzip.GzipFile(filename='',mode='wb',fileobj=(ROOT/f'export-{year}-{id}.rows.jsonl.gz').open('wb'),mtime=0) as f:
   for row in rows:f.write((json.dumps(row,separators=(',',':'))+'\n').encode())
 out[str(year)]=check
writejson(ROOT/'additional-historical-reconciliation.json',out)
for y,c in out.items():print(y,'candidatepositions',c['native_candidate_positions'],'candidate diffs',len(c['differences']),'methoddiffs',len(c['method_differences']),'stateequal',all(x['equal'] for x in c['candidate_state_controls']))
