#!/usr/bin/env python3
"""Source-native attribute control batches; geometry uses original GPKG, never this export."""
import sys,json
sys.dont_write_bytecode=True
from acquire import fetch,read,ROOT
sources={'current':('https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_sos/bdry_votingdistricts/FeatureServer/0',4105),'results':('https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_sos/bdry_electionresults_2022_2030/FeatureServer/0',4103),'results2022':('https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_sos/bdry_electionresults_2022_2030/FeatureServer/1',4103)}
for key,(url,n) in sources.items():
 b,_=fetch(key+'-ids-pre',url+'/query',{'where':'1=1','returnIdsOnly':'true','f':'json'});ids=sorted(json.loads(b)['objectIds']);assert len(ids)==n
 fetch(key+'-count-pre',url+'/query',{'where':'1=1','returnCountOnly':'true','f':'json'})
 if key=='results2022':fetch(key+'-layer',url,{'f':'pjson'})
 for i in range(0,len(ids),250):
  fetch(f'{key}-attributes-{i//250:03}',url+'/query',{'objectIds':','.join(map(str,ids[i:i+250])),'outFields':'*','returnGeometry':'false','returnZ':'true','returnM':'true','returnTrueCurves':'true','f':'json'})
 fetch(key+'-ids-post',url+'/query',{'where':'1=1','returnIdsOnly':'true','f':'json'})
 fetch(key+'-count-post',url+'/query',{'where':'1=1','returnCountOnly':'true','f':'json'})
