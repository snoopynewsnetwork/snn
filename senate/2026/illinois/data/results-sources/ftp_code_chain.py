from common import *
from ftp_status_chain import follow
m=parsefile(HERE/'receipts/law-ftp-root.json');m=follow(m,'law-ftp-ilcs-index','ILCS')
if m:
 h=HTML(body(m).decode(errors='replace'));write(HERE/'law-ilcs-directory-discovery.json',h.summary());print([(a['text'],a['literal_href']) for a in h.links][:40])
