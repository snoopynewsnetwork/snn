#!/usr/bin/env python3
import gzip,json
from pathlib import Path
P=Path(__file__).resolve().parent
units=json.loads(gzip.decompress((P/'native-baselines.json.gz').read_bytes()));api={}
for u in units:
 if u['lane'].endswith('api'):api.setdefault((u['year'],u['contest'],u['county_fips'],u['native_name']),[]).append(u)
double=[];other=[];unmatched=[]
for u in units:
 if not u['lane'].endswith('full'):continue
 matches=api.get((u['year'],u['contest'],u['county_fips'],u['native_name']),[])
 if len(matches)==1:
  v=matches[0]
  if u['candidates']!=v['candidates']:
   r={'full_key':u['key'],'api_key':v['key'],'full_candidates':u['candidates'],'api_candidates':v['candidates'],'exact_double':all(u['candidates'][c]==2*v['candidates'][c] for c in u['candidates'])}
   (double if r['exact_double'] else other).append(r)
 else:unmatched.append(u['key'])
(P/'source/full-api-native-discrepancies.json').write_text(json.dumps({'doubled':double,'other_differences':other,'unmatched_exact_names':unmatched,'basis':'exact same year/contest/county/native literal name; arithmetic witness only'},indent=2)+'\n')
