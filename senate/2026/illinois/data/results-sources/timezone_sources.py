from common import *
for section in ['71.6','71.2']:
 url='https://www.ecfr.gov/current/title-49/subtitle-A/part-71/section-'+section
 m=fetch('law-timezone-'+section,url,basis='exact primary eCFR page opened and verified; ordinary public legal text');inspect(m);print(section,m.get('status'),m.get('raw_bytes'))
