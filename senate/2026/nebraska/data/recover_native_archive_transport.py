"""One paced recovery pass for the76 retained connection-refused attempts."""
from pathlib import Path
import datetime,gzip,hashlib,json,time
import requests

DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 path=NEWS/'manifest.json';manifest=json.loads(path.read_bytes())
 failed=[r for r in manifest if r['id'].startswith('sos-2024-special-native-archive-cty-')
         and not r.get('status')and '-recovery'not in r['id']]
 successful_retries={r.get('retry_of')for r in manifest if r.get('status')==200}
 pending=[r for r in failed if r['id']not in successful_retries]
 known={r['id']for r in manifest};session=requests.Session();consecutive_transport_failures=0
 for count,base in enumerate(pending,1):
  key=base['id']+'-paced-transport-recovery1'
  if key in known:continue
  row={'id':key,'url':base['url'],'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'retry_of':base['id'],'archive_record':base.get('archive_record'),
       'historical_county_id_literal':base.get('historical_county_id_literal'),
       'discovery_basis':'Single paced recovery of a retained transport failure, same actual CDX URL/time. No numeric or source-ID inference.',
       'transport':'requests.Session, default certificate verification, four-second spacing between observations'}
  try:
   response=session.get(base['url'],timeout=35)
   body=response.content;asset=NEWS/(key+'.html.gz');asset.write_bytes(gzip.compress(body,mtime=0))
   warning=response.headers.get('warning','');closed=b'</html>'in body.lower();truncated='truncat'in warning.lower()
   row.update(status=response.status_code,final_url=response.url,
     redirects=[{'url':h.url,'status':h.status_code,'location':h.headers.get('Location')}for h in response.history],
     raw_sha256=sha(body),bytes=len(body),asset=asset.name,stored_sha256=sha(asset.read_bytes()),headers=dict(response.headers),
     archive_entity_completeness={'declared_archive_truncation_warning':warning or None,
      'archive_truncated_by_length':truncated,'HTML_closing_tag_present':closed,
      'complete_entity_claimed':response.status_code==200 and closed and not truncated,
      'qualification':'Archive200 can retain length truncation. Candidate-position completeness remains separate.'})
   consecutive_transport_failures=0
  except requests.RequestException as error:
   row['error']=str(error);consecutive_transport_failures+=1
  manifest.append(row);known.add(key);path.write_text(json.dumps(manifest,indent=2)+'\n')
  if count%5==0 or consecutive_transport_failures:print('paced',count,'of',len(pending),'status',row.get('status'),'consecutiveTransportFailures',consecutive_transport_failures,flush=True)
  if consecutive_transport_failures>=3:
   print('stopped after three repeated transport failures; remaining actual URLs are not retried in this pass',flush=True);break
  time.sleep(4)
 print('paced pass ended',flush=True)
if __name__=='__main__':main()
