"""Observed Department links and FirstMap public JS constructor, bounded acquisition.
All source URLs come from actual saved parent bytes or explicit official entry roots.
"""
from common import *
from acquire import fetch
import urllib.parse,json,concurrent.futures

def main():
 home=read(M/'source/maps-home-network.receipt.json');links=home['literal_links']
 # Complete visible parent map index, structure and municipal companion chains.
 selected=[]
 for l in links:
  h=l['literal']
  if '/maps/ed/' in l['url'] or 'DEDistrictStructure_2022_2032' in h or 'wilmington' in h.lower() or 'locations.html' in h: selected.append(l)
 unique={l['url']:l for l in selected}
 jobs=[]
 for j,l in enumerate(unique.values()):jobs.append(('parent-'+sha(l['url'].encode())[:12],l['url'],home['id'],l['literal']))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:parent=list(pool.map(lambda a:fetch(*a),jobs))
 ed=next(r for r in parent if '/maps/ed/'in r['url'])
 edlinks=ed['literal_links']
 for county,rd in [('newcastle','01'),('kent','11'),('sussex','04')]:
  l=next(l for l in edlinks if f'/{county}/rep-district-ed-overview_{rd}.pdf'in l['url'])
  fetch('county-'+county+'-overview',l['url'],ed['id'],l['literal'],research_scope='shared parent example; no result key match')
 for token in ['rded_07-08.pdf','rded_08-07.pdf']:
  l=next(l for l in edlinks if token in l['url']);fetch('literal-'+token[:-4],l['url'],ed['id'],l['literal'],research_scope='orientation control; no reporting join')
 hub=next(l for l in links if '/maps/delaware::election-districts-1'in l['url']);fetch('firstmap-hub',hub['url'],home['id'],hub['literal'])
 old=read(M/'source/reused-original-receipts.json');constructor=next(r for r in old if r['id']=='FirstMap-dataset-metadata')
 data=fetch('firstmap-dataset',constructor['url'],'firstmap-hub',constructor.get('literal_href'),public_constructor=constructor['constructor_literal'],constructor_call=constructor['literal_call'],constructor_evidence_id=constructor['constructor_source'],observed_dataset_id=constructor['literal_dataset_id'])
 layer=json.loads(body(data))['data']['attributes']['url']
 fetch('firstmap-service',layer.rsplit('/',1)[0]+'?f=json','firstmap-dataset',layer,constructor='ArcGIS public parent service metadata for observed layer')
 pre={}
 for phase in ['pre','post']:
  for kind,q in [('metadata',None),('count',{'f':'json','where':'1=1','returnCountOnly':'true'}),('ids',{'f':'json','where':'1=1','returnIdsOnly':'true'})]:
   url=layer+('?f=json' if q is None else '/query?'+urllib.parse.urlencode(q));r=fetch('native-'+phase+'-'+kind,url,'firstmap-dataset',layer);pre[phase+'-'+kind]=json.loads(body(r))
  if phase=='pre':
   ids=sorted(pre['pre-ids']['objectIds']);assert len(ids)==len(set(ids))==pre['pre-count']['count']
   def batch(j):
    group=ids[j:j+50];q=dict(f='json',objectIds=','.join(map(str,group)),outFields='*',returnGeometry='true',returnTrueCurves='true',returnZ='true',returnM='true')
    r=fetch(f'native-batch-{j//50+1:02}',layer+'/query?'+urllib.parse.urlencode(q),'native-pre-ids',layer,requested_object_ids=group,query_parameters=q)
    x=json.loads(body(r));got=[f['attributes'][pre['pre-ids']['objectIdFieldName']] for f in x['features']];assert len(got)==len(group) and set(got)==set(group)
   with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(batch,range(0,len(ids),50)))
 assert pre['pre-metadata']==pre['post-metadata'] and pre['pre-count']==pre['post-count'] and pre['pre-ids']==pre['post-ids']
 write('qa/fresh-acquisition-comparison.json',dict(status='pass',pre_post_metadata_exact=True,pre_post_count_exact=True,pre_post_ids_exact=True,count=pre['pre-count']['count'],page_bound=50))
if __name__=='__main__':main()
