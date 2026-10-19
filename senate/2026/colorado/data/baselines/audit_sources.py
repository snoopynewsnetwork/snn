#!/usr/bin/env python3
"""Read-only shared-original discovery inventory and exact observed download chains."""
from pathlib import Path
import json,gzip,hashlib,re
D=Path(__file__).resolve().parent;N=D.parent/'news'
def main():
 originals=json.loads((N/'manifest.json').read_text());target=D/'source/discovery-evidence.json'
 if not target.exists():target.write_text(json.dumps([dict(x,path='../news/'+x['asset'])for x in originals if x['id'].startswith('sos-')],indent=2)+'\n')
 frozen=json.loads(target.read_text());lookup={x['id']:x for x in frozen}
 for x in frozen:
  b=(D/x['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==x['stored_sha256'];r=gzip.decompress(b);assert len(r)==x['bytes']and hashlib.sha256(r).hexdigest()==x['raw_sha256']
 chains=[]
 for year,k in [(2024,'president'),(2022,'senate'),(2020,'senate')]:
  sid=f'sos-history-observed-{year}-{k}-contest';x=lookup[sid];h=gzip.decompress((D/x['path']).read_bytes()).decode();hrefs=re.findall(r'href="([^"]+)"',h);dl=[h for h in hrefs if '_table.csv'in h];assert len(dl)==1
  chains.append(dict(parent_id=sid,child_id=f'sos-history-observed-{year}-{k}-table-csv',literal_download_href=dl[0],qualification='Observed unchanged public download anchor, not inferred private API'))
 chains += [dict(parent_id='sos-results',child_id='sos-archive'),dict(parent_id='sos-results',child_id='sos-2024-abstract'),dict(parent_id='sos-2022-general-abstract-index',child_id='sos-2022-senate-abstract'),dict(parent_id='sos-2022-general-abstract-index',child_id='sos-2022-governor-abstract'),dict(parent_id='sos-2020-booklet-cdx',child_id='sos-2020-booklet-archive',qualification='actual exact-URL CDX capture recovery after retained direct404'),dict(parent_id='sos-2020-signed-cdx',child_id='sos-2020-signed-archive',qualification='actual exact-URL CDX capture recovery after retained direct404')]
 (D/'source/source-chains.json').write_text(json.dumps(chains,indent=2)+'\n');print(len(frozen),'primary source original references PASS')
if __name__=='__main__':main()
