"""One read-only SOAP operation exposed by the published directory client."""
from acquire import R,put
import requests,datetime,json
url='https://sos.oregon.gov/elections/_vti_bin/Lists.asmx'
b=b'<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><GetListCollection xmlns="http://schemas.microsoft.com/sharepoint/soap/" /></soap:Body></soap:Envelope>'
r={'key':'sos-directory-soap','parent':'sos-sharepoint-client','method':'POST','requested_url':url,'request_body':put(b),'request_headers':{'Content-Type':'text/xml; charset=utf-8','SOAPAction':'http://schemas.microsoft.com/sharepoint/soap/GetListCollection'},'entities':[],'error':None}
try:
 x=requests.post(url,data=b,headers=r['request_headers'],allow_redirects=False,timeout=35)
 r['entities'].append({'url':url,'status':x.status_code,'headers':dict(x.headers),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'body':put(x.content)})
except Exception as e:r['error']=type(e).__name__+': '+str(e)
r['final_url']=url;(R/'requests/sos-directory-soap.json').write_text(json.dumps(r,indent=2)+'\n');print(r['error'],[(x['status'],x['body']['raw_bytes']) for x in r['entities']])
