#!/usr/bin/env python3
"""Discover only actual published links and stage bounded request plans.

python3 discover.py seeds|follow|fetch PLAN.json
No guessed paths/IDs. Review staged plans before requesting them.
"""
import concurrent.futures,json,pathlib,re,sys,urllib.parse
sys.dont_write_bytecode=True
from acquire import D,fetch,decoded as body,readj,writej
from htmlkit import Tree,links
S=D.parent.parent
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def seeds():
    c=readj(S/'data/turnout/priority-set.json');directory=body('sos-directory-retry1').decode();root=Tree(directory).root
    portal=Tree(body('county-portal-retry1').decode()).root;pr={}
    for tr in portal.all('tr'):
        cells=[x for x in tr.children if getattr(x,'tag',None)=='td']
        if len(cells)==3:
            aa=list(cells[1].all('a'));pr[cells[0].text()]=dict(cells=[x.text() for x in cells],attributes=tr.attrs,links=[dict(attributes=x.attrs,text=x.text(),url=urllib.parse.urljoin('https://countyelectionresults.nebraska.gov/default.aspx',x.attrs.get('href','')))for x in aa])
    records=[];jobs=[]
    for p in c['all93_parents']:
        name=p['county'];nodeid=slug(name).replace('-','_');matches=[n for n in root.all('div') if n.attrs.get('id')==nodeid]
        assert len(matches)==1,(name,len(matches));n=matches[0]
        aa=[x for x in n.all('a') if x.attrs.get('href','').startswith(('http:','https:'))]
        record=dict(parent_key=p['parent_key'],county=name,county_fips=p['county_fips'],priority_parent=bool(p['priority_child_keys']),directory_source_id='sos-directory-retry1',directory_node_attributes=n.attrs,directory_text=n.text(),directory_fields_original_html=re.search(r'<div[^>]+id="'+re.escape(nodeid)+r'".*?</div>',directory,re.S).group(0),directory_website_links=[dict(attributes=x.attrs,text=x.text(),url=x.attrs['href'])for x in aa],county_portal_row=pr.get(name),portal_missing_row_is_not_zero=name not in pr)
        records.append(record)
        for i,x in enumerate(aa):jobs.append(dict(id='county-'+slug(name)+'-landing'+(f'-{i}' if i else ''),url=x.attrs['href'],parent='sos-directory-retry1',basis=f'Literal website href in current SOS directory node {n.attrs}',county=name,stage='directory-landing'))
    writej(D/'directory-records.json',records);writej(D/'landing-plan.json',jobs)
    writej(D/'seed-links.json',{sid:links(body(sid).decode(errors='replace'),readj(D/'receipts'/(sid+'.json'))['final_url'])for sid in ['sos-directory-retry1','county-portal-retry1','state-app-retry1','sos-elections-retry1']})
    print('Directory records',len(records),'landings',len(jobs),'priority parents',sum(x['priority_parent']for x in records),'portal rows',len(pr))
def follow(plan):
    jobs=readj(D/plan);priority={x['county']for x in readj(D/'directory-records.json')if x['priority_parent']};out=[];evidence={}
    for job in jobs:
        sid=job['id'];r=readj(D/'receipts'/(sid+'.json'))
        if r['http_status']!=200:continue
        s=body(sid).decode(errors='replace');ll=links(s,r['final_url']);evidence[sid]=ll
        if job.get('county')not in priority:continue
        cand=[]
        for x in ll:
            if x['tag']not in ['a','iframe'] or not x['url'].startswith(('https:','http:')):continue
            if re.search(r'(election.{0,10}result|result.{0,10}election|results?\.aspx|clarityelections|enhancedvoting|precinct.{0,15}(detail|report)|2026.{0,20}general)',x['text']+' '+x['url'],re.I):cand.append(x)
        if not cand:
            cand=[x for x in ll if x['tag']=='a' and re.search(r'election|voting',x['text']+' '+x['url'],re.I)and x['url'].startswith(('http:','https:'))]
        seen=set()
        for x in cand:
            url=x['url'].split('#')[0]
            if url in seen or url==r['final_url'].split('#')[0]:continue
            seen.add(url)
            if len(seen)>4:break
            out.append(dict(id=sid+'-linked-'+str(len(seen)),url=url,parent=sid,basis='Literal published link: '+json.dumps(x,ensure_ascii=False),county=job['county'],stage='linked-publication',source_link=x))
    writej(D/(pathlib.Path(plan).stem+'-links.json'),evidence);writej(D/(pathlib.Path(plan).stem+'-follow.json'),out);print('Discovered',len(out),'requests from',len(evidence),'complete parents')
def request(plan):
    jobs=readj(D/plan)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3)as ex:
        for j,r in zip(jobs,ex.map(lambda j:fetch(j['id'],j['url'].replace(' ','%20'),j['parent'],j['basis']),jobs)):
            print(j['id'],r['http_status'],r.get('raw_bytes'),r.get('error'),flush=True)
if __name__=='__main__':
    if sys.argv[1]=='seeds':seeds()
    elif sys.argv[1]=='follow':follow(sys.argv[2])
    elif sys.argv[1]=='fetch':request(sys.argv[2])
