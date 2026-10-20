from common import *
from curl_evidence import fetch_curl
seeds=[('law-current-19-8','https://www.ilga.gov/legislation/ilcs/fulltext?DocName=001000050K19-8'),('law-public-act-0852','https://my.ilga.gov/documents/legislation/PublicActs/104/104-0852.htm'),('law-act-0852-status','https://my.ilga.gov/Legislation/BillStatus?DocNum=3731&DocTypeID=SB&GAID=18&LegId=167004&SessionID=114'),('law-hb1832-amendment','https://ftp.ilga.gov/Legislation/104/HB/10400HB1832sam003.htm')]
for id,url in seeds:
 m=fetch_curl(id,url,basis='actual primary official search result; alternate system TLS with verification enabled');print(id,m.get('status'),m.get('raw_bytes'))
