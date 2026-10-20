"""Follow actual official archive/report anchors only; preserve earlier observations."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
N=Path(__file__).resolve().parent/'news'
def main():
 sp=importlib.util.spec_from_file_location('f',N/'fetch_evidence.py');f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f);m=json.loads((N/'manifest.json').read_bytes());known={r['id']:r for r in m}
 def get(sid,parent,a):
  url=urljoin(known[parent].get('final_url',known[parent]['url']),a['href'])
  if sid in known:assert known[sid]['url']==url
  else:
   r=f.fetch((sid,url));r.update(parent_source_id=parent,discovery_basis='Literal actual primary HTML anchor '+a['href']);m.append(r);known[sid]=r;(N/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
  r=known[sid];assert r.get('status')==200,(sid,r);b=(N/r['asset']).read_bytes();assert hashlib.sha256(b).hexdigest()==r['stored_sha256'];b=gzip.decompress(b);assert hashlib.sha256(b).hexdigest()==r['raw_sha256'];print(sid,r['status'],len(b));return None if b.startswith(b'%PDF-')else BeautifulSoup(b,'html.parser')
 def soup(sid):return BeautifulSoup(gzip.decompress((N/known[sid]['asset']).read_bytes()),'html.parser')
 a=next(a for a in soup('state-results').find_all('a',href=True)if'election_archive.html'in a['href']);archive=get('sos-observed-general-archive','state-results',a)
 for sid,needle in [('sos-observed-2020-general-report','/reports/GE2020.html'),('sos-observed-2020-writeins','elect20/elect20_general/pdf/GE2020'),('sos-observed-2022-writeins','elect22/elect22_general/GE2022_Official_WriteIn')]:
  a=next(a for a in archive.find_all('a',href=True)if needle in a['href']);s=get(sid,'sos-observed-general-archive',a)
  if sid.endswith('general-report'):
   a=next(a for a in s.find_all('a',href=True)if'csv'in a['href'].lower());get('sos-observed-2020-state-csv',sid,a)
 a=next(a for a in soup('official-2022-report').find_all('a',href=True)if'csv'in a['href'].lower());get('sos-observed-2022-state-csv','official-2022-report',a)
if __name__=='__main__':main()
