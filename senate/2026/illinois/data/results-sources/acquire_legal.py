from common import *
from concurrent.futures import ThreadPoolExecutor
SEEDS=[
('law-full-code','https://www.ilga.gov/legislation/ILCS/details?ActID=170&ActName=Election+Code.&ChapAct=FullText&Chapter=ELECTIONS&ChapterID=3&MajorTopic=GOVERNMENT&SeqStart=','primary official search result; complete current code'),
('court-bost-2026','https://www.supremecourt.gov/opinions/25pdf/24-568new_4gcj.pdf','primary official search result; actual Jan14 opinion'),
('court-watson-2026','https://www.supremecourt.gov/opinions/25pdf/24-1260_g3cn.pdf','primary official search result; actual Jun29 opinion'),
('ag-watson','https://www.illinoisattorneygeneral.gov/news/story/attorney-general-raoul-issues-statement-in-response-to-supreme-court-decision-on-mail-in-ballots','official AG primary search result'),
('ag-usps-tro','https://www.illinoisattorneygeneral.gov/news/story/update-attorney-general-raoul-secures-order-temporarily-blocking-the-us-postal-services-unlawful-mail-voting-rule','official AG primary search result Aug28'),
('ag-usps-september','https://illinoisattorneygeneral.gov/news/story/attorney-general-raoul-issues-statement-after-supreme-court-blocks-us-postal-services-unlawful-mail-voting-rule','official AG primary search result Sep14'),
('ag-june2025-order','https://illinoisattorneygeneral.gov/News-Room/Current-News/FILE_0522.pdf','official court order indexed at AG; exact primary search discovery'),
('law-public-acts-index','https://my.ilga.gov/ftp/Public%20Acts/104/','official primary public acts index discovered by search'),
('law-acts-synopsis','https://my.ilga.gov/documents/reports/static/Public%20Acts%20Syn.pdf','official current public acts synopsis discovered by search')]
def work(x):
 id,url,b=x;m=fetch(id,url,basis=b);inspect(m);return id,m.get('status'),m.get('raw_bytes'),m.get('error')
with ThreadPoolExecutor(max_workers=3) as pool:
 for x in pool.map(work,SEEDS):print(x,flush=True)
