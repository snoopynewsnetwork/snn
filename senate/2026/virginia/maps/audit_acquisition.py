"""Independent full-entity reconstruction and explicit observed access classes."""
import collections,gzip,json,sys
from acquire import HERE,sha

def audit():
    rows=[];counts=collections.Counter();seen=set()
    for path in sorted((HERE/'requests').glob('*.json')):
        record=json.loads(path.read_bytes())
        for i,hop in enumerate(record['hops']):
            if not hop['complete_body']:
                kind='DNS/no response' if 'nodename' in hop.get('error','') else 'transport/no complete response'
                assert hop['raw_sha256'] is None and hop['status'] is None;size=None
            else:
                stored=b''
                for part in hop['parts']:
                    chunk=(HERE/part['path']).read_bytes();assert len(chunk)==part['bytes']<40000000 and sha(chunk)==part['sha256'];stored+=chunk;seen.add(part['path'])
                assert len(stored)==hop['stored_gzip_bytes'] and sha(stored)==hop['stored_gzip_sha256']
                raw=gzip.decompress(stored);assert len(raw)==hop['raw_bytes'] and sha(raw)==hop['raw_sha256'];size=len(raw)
                text=raw[:100000].decode('utf-8',errors='replace').lower()
                status=hop['status']
                if status in (301,302,303,307,308):kind='complete redirect response'
                elif status==403:kind='403 access denied; no retry or bypass'
                elif status==404:kind='404 complete not-found entity'
                elif status>=400:kind=str(status)+' complete HTTP error entity'
                elif raw.startswith(b'%PDF'):kind='complete PDF original'
                elif raw.startswith(b'PK\x03\x04'):kind='complete ZIP original'
                elif any(x in text for x in ('cf-chl-','verify you are human','captcha')):kind='HTML contains challenge-related string; active challenge not established; no execution/bypass claim'
                elif any(x in record['final_url'] for x in ('experience.arcgis.com','webappviewer','hub.arcgis.com','opendata.arcgis.com')):kind='complete app/portal HTML; runtime native service not acquired'
                elif '<html' in text or '<!doctype html' in text:kind='complete static HTML entity; not native geometry'
                else:kind='complete other response entity; no geometry claim'
            counts[kind]+=1
            rows.append({'receipt':'requests/'+path.name,'hop':i,'source_parent_edge':record['source_parent_edge'],'actual_url':hop['url'],'status':hop['status'],'observed_access_class':kind,'complete_entity':hop['complete_body'],'raw_bytes':size,'raw_sha256':hop['raw_sha256'],'stored_parts':hop['parts'],'admitted_leaf_join':False})
    return {'status':'pass','scope':'every full request, redirect/error/success entity and no-body failure','request_receipts':len(list((HERE/'requests').glob('*.json'))),'response_observations':len(rows),'unique_stored_parts':len(seen),'classes':dict(counts),'request_header_qualification':'Explicitly supplied headers retained; urllib automatic wire headers not separately captured.','runtime_private_service_claim':False,'records':rows}

if __name__=='__main__':
    value=audit();text=json.dumps(value,indent=2)+'\n';out=HERE/'acquisition-audit.json'
    if '--check' in sys.argv:assert out.read_text()==text
    else:out.write_text(text)
    print(json.dumps({k:v for k,v in value.items() if k!='records'},indent=2))
