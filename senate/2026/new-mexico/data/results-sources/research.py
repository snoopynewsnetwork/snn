"""Explicit acquisition stages; no feed collector. Run with Python -B."""
from acquire import *
import re,concurrent.futures
def batch(tasks):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda x:fetch(*x),tasks))
def directory():
    r=json.loads((HERE/'receipts/county-directory.json').read_bytes());s=body(r).decode()
    out=[]
    for name,block in re.findall(r'<h3[^>]*>(.*?)</h3>(.*?)(?=<h3|<h2|$)',s,re.S):
        if 'Clerk:' not in block:continue
        name=re.sub('<[^>]+>','',name).strip();p=Page(block.encode(),r['final_url']);text=' '.join(' '.join(p.text).split())
        links=[x for x in p.links if x['url'] and x['url'].startswith(('http:','https:'))]
        out.append(dict(county_label=name,directory_block_html=block,directory_text=text,directory_links=p.links,clerk_label=re.search(r'Clerk:\s*(.*?\([DR]\))',text).group(1) if re.search(r'Clerk:\s*(.*?\([DR]\))',text) else None,landing_link=links[0] if links else None))
    assert len(out)==33,len(out);dump(HERE/'directory.json',out)
    batch([(f'county-{i+1:02d}',x['landing_link']['url'],'county-directory',x['landing_link']) for i,x in enumerate(out) if x['landing_link']])
def state():
    p=page('county-directory')
    labels=['Election Results','Absentee and Early Voting','Military and Overseas Voting','Election Laws & Codes']
    tasks=[('sos-home','https://www.sos.nm.gov/',None,'primary state homepage'),('sos-handbook','https://www.sos.nm.gov/candidate-and-campaigns/how-to-become-a-candidate/nm-election-handbook/',None,'primary search result'),('sos-chaptered','https://www.sos.nm.gov/legislation-and-lobbying/signed-chaptered-bills/',None,'primary search result')]
    for i,label in enumerate(labels):
        x=next(x for x in p['links'] if x['label']==label);tasks.append((f'sos-{i}',x['url'],'county-directory',x))
    batch(tasks)
if __name__=='__main__':globals()[sys.argv[1]]()
