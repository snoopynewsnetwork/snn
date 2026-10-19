#!/usr/bin/env python3
"""Prepare documented native queries only for literal layers selected from acquired webmaps."""
import argparse,json
from urllib.parse import urlencode
from acquire import *

def load(id):return json.loads(body(json.loads((ROOT/'receipts'/f'{id}.json').read_text())))
def seeds():
 q=[];layers=[]
 for prefix,title,fips,county in [('sarpy','Voting Precinct','31153','Sarpy'),('adams','Precinct','31001','Adams'),('scottsbluff','Voting Precincts','31157','Scotts Bluff')]:
  j=load(prefix+'-webmap');i,l=next((i,l) for i,l in enumerate(j['operationalLayers']) if l.get('title')==title);url=l['url'];layers.append({'prefix':prefix,'url':url,'county_fips':fips,'county':county})
  for kind,params in [('metadata',{'f':'pjson'}),('count-pre',{'where':'1=1','returnCountOnly':'true','f':'json'}),('ids-pre',{'where':'1=1','returnIdsOnly':'true','f':'json'})]:q.append({'id':prefix+'-native-layer-'+kind,'url':url+('' if kind=='metadata' else '/query')+'?'+urlencode(params),'county_fips':fips,'county':county,'parent_receipt':f'maps/receipts/{prefix}-webmap.json','JSON_pointer':f'/operationalLayers/{i}/url','documented_query_parameters':params})
 save_json(ROOT/'service-layers.json',layers);save_json(ROOT/'native-pre-requests.json',q)
def pages():
 q=[]
 for l in json.loads((ROOT/'service-layers.json').read_text()):
  ids=load(l['prefix']+'-native-layer-ids-pre');allids=ids['objectIds'];assert len(set(allids))==len(allids)
  for i in range(0,len(allids),50):
   chunk=allids[i:i+50];params={'objectIds':','.join(map(str,chunk)),'outFields':'*','returnGeometry':'true','returnZ':'true','returnM':'true','returnTrueCurves':'true','f':'json'}
   q.append({'id':l['prefix']+'-native-layer-native-page-'+f'{i//50+1:02}','url':l['url']+'/query?'+urlencode(params),'county':l['county'],'county_fips':l['county_fips'],'parent_receipt':f'maps/receipts/{l["prefix"]}-native-layer-ids-pre.json','native_query_parameters':params,'requested_object_ids':chunk})
 save_json(ROOT/'native-page-requests.json',q)
def post():
 q=[]
 for l in json.loads((ROOT/'service-layers.json').read_text()):
  for kind,params in [('metadata-post',{'f':'pjson'}),('count-post',{'where':'1=1','returnCountOnly':'true','f':'json'}),('ids-post',{'where':'1=1','returnIdsOnly':'true','f':'json'})]:q.append({'id':l['prefix']+'-native-layer-'+kind,'url':l['url']+('' if kind=='metadata-post' else '/query')+'?'+urlencode(params),'county':l['county'],'county_fips':l['county_fips'],'parent_receipt':f'maps/receipts/{l["prefix"]}-webmap.json','documented_query_parameters':params})
 save_json(ROOT/'native-post-requests.json',q)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['seeds','pages','post']);a=p.parse_args();globals()[a.stage]()
