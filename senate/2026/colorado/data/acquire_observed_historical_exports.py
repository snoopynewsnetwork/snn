"""Recover only actual published public contest pages and literal CSV links."""
from pathlib import Path
import gzip,importlib.util,json
from bs4 import BeautifulSoup
N=Path(__file__).resolve().parent/'news'
PAGES=[('sos-history-observed-2024-president-contest','https://historicalelectiondata.coloradosos.gov/contest/26499','2024-11-05'),('sos-history-observed-2022-senate-contest','https://historicalelectiondata.coloradosos.gov/contest/25990','2022-11-08'),('sos-history-observed-2020-senate-contest','https://historicalelectiondata.coloradosos.gov/contest/3602','2020-11-03')]
def main():
 spec=importlib.util.spec_from_file_location('fetch',N/'fetch_evidence.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);m=json.loads((N/'manifest.json').read_bytes());known={r['id']:r for r in m}
 def get(sid,url,parent,basis):
  if sid in known:assert known[sid]['url']==url;return known[sid]
  r=mod.fetch((sid,url));r.update(parent_source_id=parent,discovery_basis=basis);m.append(r);known[sid]=r;(N/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(sid,r.get('status'),r.get('bytes'),flush=True);return r
 for sid,url,date in PAGES:
  r=get(sid,url,'sos-historical-database','Actual indexed primary public contest page;2020ID3602 additionally observed in candidate45SSR and published route constructor. No guessed election/candidate IDs.')
  assert r.get('status')==200
  s=BeautifulSoup(gzip.decompress((N/r['asset']).read_bytes()),'html.parser');p=json.loads(s.find('script',id='__NEXT_DATA__').get_text())['props']['pageProps'];assert p['contest']['event']['startDate'].startswith(date)
  link=next(a for a in s.find_all('a',href=True)if'/api/download_contest/'in a['href']);csvid=sid.replace('-contest','-table-csv')
  get(csvid,link['href'],sid,'Literal SSR anchorhref '+link['href']+'; no guessed endpoint parameters or division filters.')
if __name__=='__main__':main()
