"""One bounded public election-link layer per retained official local page."""
import concurrent.futures,json,re,urllib.parse
from acquire import ROOT,body,fetch,dump,forbidden
from inspect_sources import htmlview
def classify(url,label):
    s=(url+' '+label).lower()
    if any(w in s for w in ['login','sign-in','facebook','twitter','instagram','youtube','contact form','complaint','register to vote','absentee application','donate','subscribe','security challenge','captcha','privacy','officer-of','election-officer','serve as','campaign finance']):return None
    if re.search(r'\b(201\d|202[0-5])\b',s):return None
    if 'electoral' in s and 'board' in s:return 'board'
    if re.search(r'results?|enr\.|electionnight',s):return 'results'
    if re.search(r'sample.?ballot|specimen|november.*2026|2026.*november|2026.*general|general.*2026',s):return 'current_notice_or_ballot'
    if re.search(r'registrar|office.of.elections|voter.registration|voter-registr|voting.elections|elections.voting',s):return 'office'
    return None
def plan():
    rows=json.loads((ROOT/'local-site-plan.json').read_bytes());out=[]
    for row in rows:
        if not row['url']:continue
        key='local-'+row['uid'];p=ROOT/'requests'/(key+'.json')
        if not p.exists():continue
        rec=json.loads(p.read_bytes())
        if rec['requested_url']!=row['url']:
            matches=[]
            for p in sorted((ROOT/'requests').glob(key+'*.json')):
                x=json.loads(p.read_bytes())
                if x['requested_url']==row['url']:matches.append(x)
            if not matches:continue
            rec=matches[0];key=rec['key']
        if rec['requested_url']!=row['url']:continue
        if not rec['hops']:continue
        base=rec['final_url'];h=htmlview(body(key));chosen={};seen=set()
        for pos,l in enumerate(h.links):
            href=l['literal_url']
            if l['tag']!='a' or not href:continue
            url=urllib.parse.urljoin(base,href)
            if forbidden(url) or url.split('#')[0]==base.split('#')[0] or url in seen:continue
            role=classify(url,l['text'])
            if role and role not in chosen:
                outputkey='follow-'+row['uid']+'-'+role
                prior=ROOT/'requests'/(outputkey+'.json')
                if prior.exists() and json.loads(prior.read_bytes())['requested_url']!=url:outputkey+='-static-correction'
                chosen[role]={'key':outputkey,'uid':row['uid'],'label':row['label'],'url':url,
                  'role':role,'parent_request':key,'link_position':pos,'complete_link':l}
                seen.add(url)
        # Each role has a distinct research purpose; four actual links maximum.
        out.extend(chosen.values())
    dump(ROOT/'local-followup-plan.json',out);return out
def run():
    jobs=plan()
    def one(j):
        if (ROOT/'requests'/(j['key']+'.json')).exists():return j['key'],'already retained'
        r=fetch(j['key'],j['url'],j['parent_request']+' actual HTML link position '+str(j['link_position'])+' '+j['role'])
        return j['key'],r.get('final_status')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        for r in ex.map(one,jobs):print(*r,flush=True)
if __name__=='__main__':run()
