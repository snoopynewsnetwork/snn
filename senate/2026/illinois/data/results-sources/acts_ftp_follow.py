from common import *
from curl_evidence import fetch_curl
m=fetch_curl('law-ftp-publicacts104-systemtls','https://ftp.ilga.gov/Public%20Acts/104/',basis='exact primary official search-discovered public act directory; standard HTTPS public mirror');h=inspect(m);print(m.get('status'),m.get('raw_bytes'))
for suffix in ['104-0852.htm','104-0532.htm','104-0434.htm','104-0695.htm']:
 a=next((a for a in h.links if (a['literal_href'] or '').endswith(suffix)),None)
 if a:
  x=fetch_curl('law-ftp-'+suffix[:-4],urljoin(m['final_url'],a['literal_href']),m['id'],a['literal_href'],basis='literal public act link from complete official directory; selected current/future acts named in current code search');inspect(x);print(x['id'],x.get('status'),x.get('raw_bytes'),flush=True)
x=fetch('state-directory-print','https://www.elections.il.gov/electionoperations/electionauthoritiesprint.aspx',basis='actual primary state printable authority directory search discovery');inspect(x);print(x['id'],x.get('status'))
