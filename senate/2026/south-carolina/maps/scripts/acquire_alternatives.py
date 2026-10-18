#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
from acquire import *
SOURCES=[('horry-local','https://gisportal.horrycounty.org/server/rest/services/publicview/VoterPrecincts/MapServer/0','raw/horry-webmap-data.body.gz'),('beaufort-local','https://gis.beaufortcountysc.gov/server/rest/services/Political/MapServer/0','raw/beaufort-webmap-data.body.gz'),('pickens-local','https://services1.arcgis.com/59960rq18IxUcAVI/arcgis/rest/services/Precincts_2010/FeatureServer/0','raw/pickens-webmap-data.body.gz')]
def run():
 for n,u,p in SOURCES:
  fetch(n+'-layer',u,{'f':'pjson'},parent=p)
  for phase in ['pre','post']:
   for kind,flag in [('count','returnCountOnly'),('ids','returnIdsOnly')]:fetch(n+'-'+phase+'-'+kind,u+'/query',{'f':'json','where':'1=1',flag:'true'},parent='raw/'+n+'-layer.body.gz')
   if phase=='pre':
    ids=sorted(js(n+'-pre-ids').get('objectIds',[]))
    for i in range(0,len(ids),80):
     q=n+f'-page-{i//80:03d}';d=fetch(q,u+'/query',{'f':'json','objectIds':','.join(map(str,ids[i:i+80])),'outFields':'*','returnGeometry':'true','returnZ':'true','returnM':'true','returnTrueCurves':'true'},parent='raw/'+n+'-pre-ids.body.gz');print(q,d['status'],d['original_bytes'],len(js(q).get('features',[])),flush=True)
  print(n,'schema',[(x['name'],x['type']) for x in js(n+'-layer').get('fields',[])],flush=True)
if __name__=='__main__':run()
