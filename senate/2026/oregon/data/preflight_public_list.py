#!/usr/bin/env python3
"""Read-only SOAP calls actually used by the anonymous published history client."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET

D = Path(__file__).resolve().parent
N = D/'news'
URL = 'https://sos.oregon.gov/elections/_vti_bin/{}.asmx'
NS = 'http://schemas.microsoft.com/sharepoint/soap/'
sha = lambda b: hashlib.sha256(b).hexdigest()
def fetch(id, service, action, parameters):
    mf = json.loads((N/'manifest.json').read_text())
    existing = next((x for x in mf if x['id']==id),None)
    if existing:
        return gzip.decompress((N/existing['asset']).read_bytes())
    soap = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
    body = ET.SubElement(soap,'{http://schemas.xmlsoap.org/soap/envelope/}Body')
    call = ET.SubElement(body,'{'+NS+'}'+action)
    for k,v in parameters.items():
        ET.SubElement(call,'{'+NS+'}'+k).text=v
    request = ET.tostring(soap,encoding='utf-8',xml_declaration=True)
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with tempfile.TemporaryDirectory() as temp:
        out = Path(temp)/'body';headers=Path(temp)/'headers'
        run = subprocess.run(['curl','--silent','--show-error','--max-time','35','--location',
                              '-H','Content-Type: text/xml; charset=utf-8',
                              '-H','SOAPAction: '+NS+action,'--data-binary','@-',
                              '--dump-header',str(headers),'--output',str(out),'--write-out','%{json}',URL.format(service)],
                             input=request,capture_output=True)
        result = json.loads(run.stdout) if run.stdout else {}
        raw = out.read_bytes() if out.exists() else b''
        header_bytes = headers.read_bytes() if headers.exists() else b''
    stored = gzip.compress(raw,mtime=0);asset=id+'.html.gz';(N/asset).write_bytes(stored)
    header_asset=id+'.headers.txt';(N/header_asset).write_bytes(header_bytes)
    entry={'id':id,'url':URL.format(service),'request_method':'POST',
           'read_only_action':action,'request_XML':request.decode(),'request_sha256':sha(request),
           'template_authority':'Official historical-data.aspx anonymous webpart + saved oregon-sharepoint.js Lists/Views read-only client',
           'retrieved_at_utc':start,'completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'status':result.get('http_code'),'final_url':result.get('url_effective'),
           'headers':{'raw_response_and_redirect_headers':header_asset},'curl_exit':run.returncode,
           'curl_error':run.stderr.decode(),'asset':asset,'stored_sha256':sha(stored),
           'raw_sha256':sha(raw),'bytes':len(raw),'stored_bytes':len(stored)}
    mf.append(entry);(N/'manifest.json').write_text(json.dumps(mf,indent=2)+'\n')
    print(id,entry['status'],len(raw))
    return raw

if __name__=='__main__':
    raw=fetch('sos-history-public-list-collection','Lists','GetListCollection',{})
    if not raw.lstrip().startswith(b'<'):
        (D/'coordinator-history-public-list.json').write_text(json.dumps({'status':'public_read_only_route_denied','list_url':'/elections/Lists/History','view_name':'public','observed_HTTP_status':401,'body_sha256':sha(raw),'scope':'Published anonymous history client route tested once; no credentials, current results or source completeness inferred.'},indent=2)+'\n')
        raise SystemExit(0)
    root=ET.fromstring(raw)
    matches=[x for x in root.iter() if x.tag.endswith('List') and '/elections/Lists/History/' in x.get('DefaultViewUrl','')]
    assert len(matches)==1,[(x.get('Title'),x.get('DefaultViewUrl'))for x in root.iter()if x.tag.endswith('List')]
    name=matches[0].get('Title')
    raw=fetch('sos-history-public-views','Views','GetViewCollection',{'listName':name})
    views=[x for x in ET.fromstring(raw).iter() if x.tag.endswith('View') and x.get('DisplayName','').lower()=='public']
    assert len(views)==1
    view=views[0].get('Name')
    raw=fetch('sos-history-public-rows','Lists','GetListItems',{'listName':name,'viewName':view})
    rows=[x.attrib for x in ET.fromstring(raw).iter() if x.tag.endswith('row')]
    (D/'coordinator-history-public-list.json').write_text(json.dumps({'status':'public_list_originals_only','list':name,'view':view,'rows':rows},indent=2)+'\n')
    print('Read-only public rows',len(rows))
