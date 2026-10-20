"""One bounded enacted-act status check, using the already observed FTP index."""
from common import *
from curl_evidence import fetch_curl

def main():
 m=parsefile(HERE/'receipts/law-ftp-status104html.json')
 h=HTML(body(m).decode());links=[a for a in h.links if re.search(r'10400SB3731\.html$',a['literal_href'],re.I)]
 assert len(links)==1
 a=links[0];r=fetch_curl('law-sb3731-actual-status',urljoin(m['final_url'],a['literal_href']),m['id'],a['literal_href'],basis='literal SB3731 status link in complete published official directory; check 104-0852 effective date')
 print(r['status'],r.get('raw_bytes'))
if __name__=='__main__':main()
