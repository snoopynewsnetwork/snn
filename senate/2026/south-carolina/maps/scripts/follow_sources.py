#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
from acquire import *
from county_sources import Links
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

def run():
 rows=json.loads((ROOT/'county-observed-links.json').read_text());jobs=[]
 for r in rows:
  for i,x in enumerate(r['links']):
   u=x['url'];label=x['label'].lower()
   if ((r['county']=='Anderson' and 'polling locations'==label) or (r['county']=='Florence' and 'precincts and polling' in label) or (r['county']=='Sumter' and ('sumter county precincts' in label or 'polling locations'==label)) or (r['county']=='Horry' and 'interactive precinct' in label) or (r['county']=='Beaufort' and label=='district maps') or (r['county']=='Pickens' and label=='election districts')):jobs.append((r['county'].lower()+'-follow-'+str(i),u,r['capture']))
 jobs.extend([('greenville-gis-app','https://www.gcgis.org/apps/voterinfo','county-greenville literal javascript popUp URL'),('greenville-elections','https://www.greenvillecounty.org/VoterRegistration/','county-greenville'),('horry-app-data','https://gisportal.horrycounty.org/portal/sharing/rest/content/items/ae801c3df926436e81add8a16eecd297/data?f=pjson','county-horry linked app')])
 def get(job):
  n,u,p=job;d=fetch(n,u,parent=p);print(n,d['status'],d.get('original_bytes'),flush=True);return d
 with ThreadPoolExecutor(max_workers=3) as ex:out=list(ex.map(get,jobs))
 result=[]
 for d in out:
  if d.get('headers',{}).get('Content-Type','').startswith('text/html'):
   s=Links();s.feed(body(d['id']).decode(errors='replace'));base=urljoin(d['final_url'],s.base or '');ll=[{'url':urljoin(base,x['url']),'label':x['label'].strip(),'tag':x['tag']} for x in s.links if any(y in (x['url']+' '+x['label']).lower() for y in ['precinct','arcgis','\.pdf','map'])];result.append({'id':d['id'],'links':ll})
 (ROOT/'follow-observed-links.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':run()
