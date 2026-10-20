from common import *
from ftp_status_chain import follow
m=parsefile(HERE/'receipts/law-ftp-election-code-files.json');m=follow(m,'law-ftp-complete-election-code','001000050F.html')
if m:print(m['id'],m.get('raw_bytes'))
