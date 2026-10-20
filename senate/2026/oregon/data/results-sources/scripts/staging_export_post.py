"""Single source-observed anonymous CSV export, retained only as staging negative."""
from acquire import R,put
from inspect_sources import inspect
from urllib.parse import urlencode,urljoin
import gzip,json,re,requests,datetime
key='sos-staging-csv-negative';p=R/'requests'/(key+'.json')
if p.exists():raise SystemExit('immutable key already captured')
d=json.loads(gzip.decompress((R/'structures/sos-staging-export-negative.json.gz').read_bytes()))
fields={}
for t in d['tokens']:
 if t[0] in ['start','empty'] and t[2]=='input':
  a=dict(t[3])
  if a.get('type')=='hidden' and 'name' in a:fields[a['name']]=a.get('value','')
a=next(a for a in d['links'] if a['label'].strip()=='Statewide Export')
fields['__EVENTTARGET']=re.search(r"__doPostBack\('([^']+)'",a['href']).group(1);fields['__EVENTARGUMENT']=''
# Literal CSV label is for radio MainContent_rblTypes_0, value1.
assert any(t[0] in ['start','empty'] and t[2]=='input' and dict(t[3]).get('id')=='MainContent_rblTypes_0' and dict(t[3]).get('value')=='1' for t in d['tokens'])
fields['ctl00$MainContent$rblTypes']='1';b=urlencode(fields).encode();url=d['final_url']
r={'key':key,'parent':'sos-staging-export-negative','method':'POST','requested_url':url,'request_body':put(b),'request_headers':{'Content-Type':'application/x-www-form-urlencoded'},'entities':[],'error':None,'admitted':False,'purpose':'negative fixture; unlinked staging, never genuine November counts'}
try:
 x=requests.post(url,data=b,headers=r['request_headers'],timeout=40,allow_redirects=False)
 r['entities'].append({'url':url,'status':x.status_code,'headers':dict(x.headers),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'body':put(x.content)})
except Exception as e:r['error']=type(e).__name__+': '+str(e)
r['final_url']=url;p.write_text(json.dumps(r,indent=2)+'\n');o=inspect(r);print(o['status'],o['format'],o['text'][:700])
