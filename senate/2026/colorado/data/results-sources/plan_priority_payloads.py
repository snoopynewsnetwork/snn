#!/usr/bin/env python3
"""Exact45 priority-parent primary samples from complete state tuples and acquired language configs."""
import json,gzip,zlib
from pathlib import Path
from inspect_sources import read_receipt
ROOT=Path(__file__).resolve().parent;STATE=ROOT.parents[1]
rs=json.loads((ROOT/'acquisition.json').read_text());done={r['url'] for r in rs};plan=[]
def obj(r):
 b=read_receipt(r);enc=next((v for k,v in r['headers'].items() if k.lower()=='content-encoding'),'');return json.loads(gzip.decompress(b) if enc=='gzip' else zlib.decompress(b) if enc=='deflate' else b)
state=next(r for r in rs if r['id']=='feed-535-54');tuples=obj(state)['settings']['electiondetails']['participatingcounties'];priority=json.loads((STATE/'data/coordinator-priority-acceptance.json').read_text())['ordered_priority_parent_literals']
for entry in tuples:
 county,eid,version,clock,status=entry.split('|')
 if county.replace('_',' ') not in priority:continue
 base=f'https://results.enr.clarityelections.com/CO/{county}/{eid}/{version}/json';r=next(r for r in rs if r['url']==base+'/config.json');conf=obj(r)
 for name in ['electionsettings.json','summary.json','status.json','details.json']:
  lang='/'+conf['lang'] if name in ['electionsettings.json','summary.json'] else '';u=base+lang+'/'+name
  if u in done:continue
  plan.append(dict(id='priority-primary-'+county+'-'+name.replace('.json',''),county=county.replace('_',' '),url=u,parent=r['id'],basis='Observed BaseEnrService getUri and exact primary tuple/config, complete public response',constructor={'complete_state_tuple':entry,'config_receipt':r['id'],'source_clock_literal':clock,'source_status_literal':status,'literal_filename':name,'language_argument':conf['lang'] if lang else None,'source_scope':'2026 June primary only; not current November identities or votes'}))
(ROOT/'requests-priority-payloads.json').write_text(json.dumps(plan,indent=2)+'\n');print('requests',len(plan))
