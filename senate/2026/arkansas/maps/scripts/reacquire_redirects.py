import gzip,json,urllib.parse
from acquire import fetch,ROOT
for old in ['official-gis-old-product','official-gis-update']:
 r=json.loads((ROOT/'originals'/old/'receipt.json').read_bytes());url=r['request']['url'];chain=[]
 for hop in range(8):
  label=old+'-wholehop-'+str(hop);raw,rec=fetch(label,url,old if hop==0 else chain[-1])
  chain.append(label)
  status=(rec.get('metrics') or {}).get('http_code')
  if status not in [301,302,303,307,308]:break
  h=gzip.decompress(b''.join((ROOT/x['path']).read_bytes() for x in rec['headers']['parts'])).decode('iso-8859-1')
  location=[line.split(':',1)[1].strip() for line in h.splitlines() if line.lower().startswith('location:')][-1]
  url=urllib.parse.urljoin(url,location)
 else:raise RuntimeError('redirect bound exceeded')
 (ROOT/'originals'/(old+'-whole-chain.json')).write_text(json.dumps({'initial_probe':old,'complete_hops':chain,'rule':'Every hop body/header/status retained; follows literal response Location only'},indent=2)+'\n')
