from common import *
from ftp_status_chain import follow
m=parsefile(HERE/'receipts/law-ftp-ilcs10.json');m=follow(m,'law-ftp-election-code-files','Act 0005')
if m:
 h=HTML(body(m).decode(errors='replace'));print('links',len(h.links),[(a['text'],a['literal_href']) for a in h.links][:18]);write(HERE/'law-election-code-file-discovery.json',h.summary())
