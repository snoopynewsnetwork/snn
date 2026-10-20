from common import *
from curl_evidence import fetch_curl

def follow(m,id,needle):
 h=HTML(body(m).decode(errors='replace'));a=next((a for a in h.links if needle.lower() in ((a['text'] or '')+' '+a['literal_href']).lower()),None)
 if not a:print(id,'no published link',needle,flush=True);return None
 x=fetch_curl(id,urljoin(m['final_url'],a['literal_href']),m['id'],a['literal_href'],basis='bounded official public FTP directory navigation, selected literal link '+needle);print(id,x.get('status'),x.get('raw_bytes'),flush=True);return x if x.get('status')==200 else None
def main():
 m=parsefile(HERE/'receipts/law-ftp-publicacts104-systemtls.json')
 for id,needle in [('law-ftp-acts-parent','To Parent Directory'),('law-ftp-root','To Parent Directory'),('law-ftp-legislation','Legislation'),('law-ftp-legislation104','104/'),('law-ftp-status104','BillStatus'),('law-ftp-status104html','HTML')]:
  m=follow(m,id,needle)
  if m is None:break
 if m:
  h=HTML(body(m).decode(errors='replace'));matches=[a for a in h.links if '1832' in a['literal_href'] and 'HB' in a['literal_href'].upper()];write(HERE/'law-hb1832-status-link-discovery.json',matches)
  if matches:
   a=matches[0];x=fetch_curl('law-hb1832-actual-status',urljoin(m['final_url'],a['literal_href']),m['id'],a['literal_href'],basis='actual published HB1832 status link from current complete public directory');print(x.get('status'),x.get('raw_bytes'))
if __name__=='__main__':main()
