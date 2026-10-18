from common import *
qs=js(ROOT/'requests.json');seen={x['url'] for x in qs}
for line in (ROOT/'local-discovery.txt').read_text().splitlines():
 if not line.strip():continue
 f,u=line.split('|',1)
 if u in seen:continue
 n=sum(x.get('county_fips')==f and x.get('role')=='local_parent' for x in qs)+1
 qs.append({'id':f'local-{f}-{n}','url':u,'county_fips':f,'role':'local_parent','parent':'Independent primary-site web search discovery; authority checked in retained destination'})
 seen.add(u)
save(ROOT/'requests.json',qs)
