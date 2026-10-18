#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
from acquire import *
from concurrent.futures import ThreadPoolExecutor
import re

def run():
 c=json.loads((ROOT.parent/'data/turnout/priority-set.json').read_text()); names={x['name'] for x in c['counties'] if x['in_priority']};links=json.loads((ROOT/'rfa-pdf-links.json').read_text());selected=[x for x in links if any(x['label'].startswith(n+' County') for n in names)]
 def pdf(x):
  d=fetch('media-'+x['media'].split('/')[-1],'https://www.rfa.sc.gov'+x['media'],parent='../data/map-preflight/rfa-precincts.html.gz');print(x['label'],d['status'],d.get('original_bytes'),flush=True)
 with ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(pdf,selected))
 for n,path in [('rfa-app-item','689fd82b343045988251f0cbad8f1620'),('rfa-webmap-item','3e091943d6414f5fa5c5a1ddb759cbd9'),('rfa-webmap-data','3e091943d6414f5fa5c5a1ddb759cbd9/data')]:
  d=fetch(n,'https://rfa.maps.arcgis.com/sharing/rest/content/items/'+path+'?f=pjson',parent='raw/rfa-app-data.body.gz');print(n,d['status'])
 fetch('rfa-hub-districts','https://gis-rfa.hub.arcgis.com/pages/districts',parent='../data/map-preflight/rfa-jurisdictional.html.gz')
 d=js('rfa-webmap-data')
 def layers(ls):
  for l in ls:
   print(l.get('title'),l.get('url'),l.get('itemId'))
   layers(l.get('layers',[]))
 layers(d.get('operationalLayers',[]))
if __name__=='__main__':run()
