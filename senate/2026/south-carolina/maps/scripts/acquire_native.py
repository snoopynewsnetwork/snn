#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
from acquire import *
from concurrent.futures import ThreadPoolExecutor
URL='https://gis.state.sc.us/arcgis/rest/services/Boundaries_Districts/Voter_Precincts/FeatureServer/0'
def run():
 for phase in ['pre']:
  for kind,flag in [('count','returnCountOnly'),('ids','returnIdsOnly')]:
   fetch('native-'+phase+'-'+kind,URL+'/query',{'f':'json','where':'1=1',flag:'true'},parent='raw/rfa-precinct-layer.body.gz')
 ids=sorted(js('native-pre-ids')['objectIds']);print('Count / allIDs',js('native-pre-count'),len(ids),flush=True)
 chunks=[ids[i:i+80] for i in range(0,len(ids),80)]
 def page(pair):
  i,vals=pair;n=f'native-page-{i:03d}';d=fetch(n,URL+'/query',{'f':'json','objectIds':','.join(map(str,vals)),'outFields':'*','returnGeometry':'true','returnZ':'true','returnM':'true','returnTrueCurves':'true'},parent='raw/native-pre-ids.body.gz');j=js(n);print(n,d['status'],d['original_bytes'],len(j.get('features',[])),j.get('exceededTransferLimit'),j.get('error'),flush=True)
 with ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(page,enumerate(chunks)))
 for kind,flag in [('count','returnCountOnly'),('ids','returnIdsOnly')]:fetch('native-post-'+kind,URL+'/query',{'f':'json','where':'1=1',flag:'true'},parent='raw/rfa-precinct-layer.body.gz')
 fetch('rfa-precinct-layer-post',URL,{'f':'pjson'},parent='raw/rfa-precinct-layer.body.gz')
 print('pre/post IDs equal',js('native-pre-ids')==js('native-post-ids'),flush=True)
if __name__=='__main__':run()
