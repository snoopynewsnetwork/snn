"""Snapshot the observed official layer: native CRS/all fields/Z/M/true curves."""
import json,gzip,urllib.parse
from pathlib import Path
from acquire import fetch,ROOT
L='https://gis.arkansas.gov/arcgis/rest/services/FEATURESERVICES/Boundaries/FeatureServer/11'
def body(label):
 r=json.loads((ROOT/'originals'/label/'receipt.json').read_bytes())
 return gzip.decompress(b''.join((ROOT/x['path']).read_bytes() for x in r['body']['parts']))
ids=json.loads(body('precinct-ids-pre'))['objectIds']
assert len(ids)==len(set(ids))==json.loads(body('precinct-count-pre'))['count']
for i in range(0,len(ids),50):
 label='native-page-%04d'%(i//50)
 if (ROOT/'originals'/label).exists():continue
 wanted=ids[i:i+50]
 params={'objectIds':','.join(map(str,wanted)),'outFields':'*','returnGeometry':'true','returnZ':'true','returnM':'true','returnTrueCurves':'true','f':'json'}
 raw,r=fetch(label,L+'/query?'+urllib.parse.urlencode(params),'precinct-layer-html')
 v=json.loads(raw);got=[x['attributes']['objectid'] for x in v['features']]
 assert set(wanted)==set(got) and len(got)==len(wanted) and not v.get('exceededTransferLimit'),(label,'ID/count mismatch')
for label,url,parent in [('boundaries-service-post',L.rsplit('/',1)[0]+'?f=pjson','precinct-layer-html'),('precinct-layer-post',L+'?f=pjson','precinct-layer-html'),('precinct-count-post',L+'/query?where=1%3D1&returnCountOnly=true&f=json','precinct-layer-html'),('precinct-ids-post',L+'/query?where=1%3D1&returnIdsOnly=true&f=json','precinct-layer-html')]:
 if not (ROOT/'originals'/label).exists():fetch(label,url,parent)
