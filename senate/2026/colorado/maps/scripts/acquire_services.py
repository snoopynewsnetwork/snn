"""One-shot exact native service acquisition. Not a live collector."""
import json,urllib.parse
from acquire import ROOT,fetch,body
specs=json.loads((ROOT/'service-specs.json').read_text())
for s in specs:
 k,url,parent=s['id'],s['url'],s['parent'];purpose='native precinct public layer; exact fields/native CRS, no legal/current join'
 def request(suffix,path,params):
  key=k+'-'+suffix;r=fetch([key,url+path+'?'+urllib.parse.urlencode(params),purpose,parent]);assert r['status']==200,(key,r['status']);d=json.loads(body(key));assert 'error'not in d,(key,d);return key,d
 try:
  prekey,pre=request('meta-pre','',{'f':'pjson'});countkey,count=request('count-pre','/query',{'f':'json','where':'1=1','returnCountOnly':'true'});idskey,ids=request('ids-pre','/query',{'f':'json','where':'1=1','returnIdsOnly':'true'})
  allids=ids['objectIds'];assert len(allids)==count['count']==len(set(allids));pages=[];seen=[]
  for i in range(0,len(allids),50):
   key,d=request('page-'+str(i//50+1).zfill(3),'/query',{'f':'json','objectIds':','.join(map(str,allids[i:i+50])),'outFields':'*','returnGeometry':'true','returnZ':'true','returnM':'true','returnTrueCurves':'true'})
   assert not d.get('exceededTransferLimit',False);oid=ids['objectIdFieldName'];pids=[f['attributes'][oid] for f in d['features']];assert set(pids)==set(allids[i:i+50]) and len(pids)==len(allids[i:i+50]);seen+=pids;pages.append(key)
  metakey,post=request('meta-post','',{'f':'pjson'});_,countpost=request('count-post','/query',{'f':'json','where':'1=1','returnCountOnly':'true'});_,idspost=request('ids-post','/query',{'f':'json','where':'1=1','returnIdsOnly':'true'})
  assert set(allids)==set(idspost['objectIds'])==set(seen) and len(seen)==len(allids) and countpost==count
  assert pre==post,'metadata changed during capture; no coherent snapshot claim'
  result=dict(**s,pre_metadata=prekey,post_metadata=metakey,pre_ids=idskey,pages=pages,count=len(allids),equal_pre_post_metadata=True,equal_pre_post_count_ids=True,truncated=False,query_policy='at most50 explicitly requested object IDs/page; all fields; source native CRS; Z/M/true curves requested; no precision/rounding/outputCRS/quantization/generalization/maxoffset',current_legal_match=False)
 except Exception as e:result=dict(**s,failure=repr(e),complete=False)
 (ROOT/'raw'/f'{k}.service.json').write_text(json.dumps(result,indent=2)+'\n');print(k,result.get('count'),result.get('failure',''))
