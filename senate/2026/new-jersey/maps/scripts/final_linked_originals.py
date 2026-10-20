from acquire import *
from concurrent.futures import ThreadPoolExecutor
S=[('atlantic-county-context-map','https://www.atlanticcountynj.gov/home/showpublisheddocument/4978/638253554751230000','Atlantic','actual county PDF search result; complete county commissioner map, not leaf polygons'),('middlesex-monroe-map','https://www.middlesexcountynj.gov/home/showpublisheddocument/4122/637848569568500000','Middlesex','actual county PDF search result; ward/election map2022'),('middlesex-oldbridge-map','https://www.middlesexcountynj.gov/home/showpublisheddocument/4402/637890053446030000','Middlesex','actual county PDF search result; ward/election map2022'),('middlesex-woodbridge-map','https://www.middlesexcountynj.gov/home/showpublisheddocument/4130/637848569583370000','Middlesex','actual county PDF search result; ward/election map2022')]
for x in links('gloucester-polling-navigation'):
 if x['literal_href']=='/DocumentCenter/View/7497':S.append(('gloucester-polling-roster',x['url'],'Gloucester','gloucester-polling-navigation literal '+x['literal_href']))
write(BASE/'derived/final-linked-sources.json',[{'id':a,'url':b,'county':c,'parent':d} for a,b,c,d in S])
with ThreadPoolExecutor(max_workers=4) as e:list(e.map(lambda x:fetch(x[0],x[1],x[3]),S))
