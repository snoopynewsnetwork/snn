"""Bounded local authority acquisition from retained directory/search edges.

Discovery candidates are not vote admission; a full official page must confirm
the locality and office. Each raw search tool result is retained with its limits.
"""
import concurrent.futures,json,re,urllib.parse,hashlib
from acquire import ROOT,fetch,dump
def results(p):
    return [{'title':m[1],'url':m[2]} for m in re.finditer(r'^(.+?) \((https?://[^\n]+)\)\n',p.read_text(),re.M)]
def candidate(r,label):
    title=r['title'];url=r['url'];host=urllib.parse.urlsplit(url).hostname or '';path=urllib.parse.urlsplit(url).path
    if any(s in host for s in ['elections.','elections-es','elections.es.','elections.zh','virginia.gov','lva.','fvap.','wikipedia','reddit','usvote','gop','dems','democrat','republican','vaco.','211virginia','news','law.lis.']):
        if host.endswith('cumberlandcounty.virginia.gov') or host.endswith('madisonco.virginia.gov'):pass
        else:return False
    if re.search(r'\b(NC|FL|TX|TN|NJ|MD|PA)\b',title):return False
    if any(s in host for s in ['countync','countytn','.tx.','.md.','mdvotes','augustaga','countyfl','countynj']):return False
    if any(s in path.lower() for s in ['documentcenter','showpublish','agendacenter','newsflash','agenda','/m/','archive','application','forms','officer','press-release','budget']):return False
    if re.search(r'\.(pdf|xlsx|docx?)$',path,re.I):return False
    signature=re.sub('[^a-z]','',label.lower().replace(' county','').replace(' city',''))
    legacy_local=signature in host.replace('-','') and any(s in host for s in ['county','cova','city','va.','andqueenco'])
    return (host.endswith('.gov') or '.va.us' in host or legacy_local) and bool(re.search(r'registr|elect|vot',title+' '+path,re.I))
def plan():
    rows=json.loads((ROOT/'local-navigation.json').read_bytes());out=[]
    overrides=ROOT/'discovery/static-selections.json'
    explicit=json.loads(overrides.read_bytes()) if overrides.exists() else {}
    for row in rows:
        uid=row['directory_uid'];urls=row['local_urls'];source='directory '+row['directory_request']+' complete URL field'
        if urls:
            url=urls[0];url=url if '://' in url else 'https://'+url
        else:
            p=ROOT/'discovery'/('search-'+uid+'.txt');rs=results(p) if p.exists() else []
            possible=[r for r in rs if candidate(r,row['literal_directory_label'])];url=possible[0]['url'] if possible else None
            source='discovery/'+p.name+' actual observed result URL; official status subject to full-page confirmation'
        if not urls and uid in explicit:url=explicit[uid]['url'];source=explicit[uid]['edge']
        out.append({'label':row['literal_directory_label'],'uid':uid,'url':url,'edge':source})
    dump(ROOT/'local-site-plan.json',out);return out
def run():
    rows=plan()
    def one(r):
        key='local-'+r['uid']
        if not r['url']:return (r['label'],'no static local URL established')
        if (ROOT/'requests'/(key+'.json')).exists():
            old=json.loads((ROOT/'requests'/(key+'.json')).read_bytes())
            if old['requested_url']==r['url']:return (r['label'],'previous observation retained')
            key+='-static-correction'
            if (ROOT/'requests'/(key+'.json')).exists():
                old=json.loads((ROOT/'requests'/(key+'.json')).read_bytes())
                if old['requested_url']==r['url']:return (r['label'],'corrected observation retained')
                key='local-'+r['uid']+'-directory-'+hashlib.sha256(r['url'].encode()).hexdigest()[:10]
                if (ROOT/'requests'/(key+'.json')).exists():return(r['label'],'directory final observation retained')
        x=fetch(key,r['url'],r['edge']);return(r['label'],x.get('final_status'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        for r in ex.map(one,rows):print(*r,flush=True)
if __name__=='__main__':run()
