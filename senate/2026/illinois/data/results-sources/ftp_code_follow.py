from common import *
from ftp_status_chain import follow
m=parsefile(HERE/'receipts/law-ftp-ilcs-index.json');m=follow(m,'law-ftp-ilcs10','Ch 0010')
if m:
 h=HTML(body(m).decode(errors='replace'));print([(a['text'],a['literal_href']) for a in h.links][:40]);write(HERE/'law-ilcs10-directory-discovery.json',h.summary())
