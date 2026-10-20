from common import *
from acquire import *
import re

def follow(parent,key,pattern):
 r=load('maps/requests/'+parent+'.json');ls=[l for l in links_of(r) if re.search(pattern,l['url'])]
 assert len(ls)==1,(key,len(ls));r=fetch(key,ls[0]['url'],parent,'historical Census county context; not precinct geometry');print(key,[e['status'] for e in r['entities']],flush=True)
follow('census-tiger-root','census-tiger2010',r'/TIGER2010/$')
follow('census-tiger2010','census-county2010',r'/COUNTY/$')
follow('census-county2010','census-county2010-2010',r'/2010/$')
follow('census-county2010-2010','census-oregon-county2010',r'tl_2010_41_county10\.zip$')
r=fetch('odot-county-service','https://gis.odot.state.or.us/arcgis1006/rest/services/data_layers/county_boundaries/MapServer?f=pjson','official search exact service','state county-context service discovery');print('odot',len(body_of(r)))
