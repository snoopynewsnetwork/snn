#!/usr/bin/env python3
"""DB-internal exact-native-path method gaps; no cross-view imputation."""
import json,gzip,pathlib,collections
from acquire import ROOT
T=ROOT.parent/'turnout';c=json.loads((T/'priority-set.json').read_text());out=[];summary={}
def d(s):return json.loads(gzip.decompress((T/c['source_observations'][s]['body_path']).read_bytes()))['data']['contestGranularData']
def walk(n,p='/data/contestGranularData/divisions'):
 yield p,n
 for i,ch in enumerate(n.get('children') or []):yield from walk(ch,p+'/children/'+str(i))
for label in ['2024-pres','2020-senate','2022-senate','2022-governor']:
 a=d(label+'-combined');b=d(label+'-methods');bm=dict(walk(b['divisions']));actual={r['candidateId'] for r in a['candidates'] if r['candidate']['pseudocandidate'] in [None,'ALL_OTHER_CANDIDATES']};leafcontexts=set();allactual=0;pseudo=0
 for p,n in walk(a['divisions']):
  m=bm[p];assert n['division']==m['division']
  for row in n['granularRow']:
   parts=[r for r in m['granularRow'] if (r['candidateId'],r['partyId'])==(row['candidateId'],row['partyId'])];delta=row['votes']-sum(x['votes'] for x in parts)
   if delta:
    isactual=row['candidateId'] in actual;allactual+=isactual;pseudo+=not isactual
    if isactual and not n.get('children'):leafcontexts.add(p)
    out.append({'contest':label,'pointer':p,'division':n['division'],'raw_combined_row':row,'raw_method_rows':parts,'method_sum':sum(x['votes'] for x in parts),'combined_minus_methods':delta,'actual_candidate':isactual,'native_leaf':not n.get('children')})
 summary[label]={'actual_candidate_mismatch_cells_all_levels':allactual,'actual_candidate_leaf_contexts':len(leafcontexts),'pseudo_control_mismatch_cells':pseudo}
(ROOT/'DB-method-balance.json.gz').write_bytes(gzip.compress((json.dumps({'summary':summary,'differences':out,'scope':'Exact source-native DB paths only. Zero/absent/masked stay as returned. Original XML methods are separate observations, never filled into DB gaps.'},indent=2)+'\n').encode(),mtime=0));print(summary)
