"""Bounded map-specific actual-anchor traversal of accessible registrar sites.

At most 2 first-level map pages and 2 relevant original assets per priority parent.
403/challenge sources are recorded and not retried or bypassed.
"""
import concurrent.futures,json,re
from urllib.parse import urljoin,urlsplit
from acquire import HERE,entity,fetch,sha
from discover_state import Links

def candidates(receipt):
    b=entity(receipt)
    if b is None or receipt['hops'][-1]['status']!=200:return []
    text=b.decode('utf-8',errors='replace')
    if any(s in text[:10000].lower() for s in ['cf-chl-','verify you are human','access denied','captcha']):return []
    p=Links();p.feed(text);out=[];seen=set()
    for a in p.links:
        url=urljoin(receipt['final_url'],a['href']); label=a['text'].strip(); hay=(label+' '+url).lower()
        if not url.startswith(('https://','http://')) or a['href'].startswith('#') or re.search(r'login|signin|account|admin|contact|facebook|twitter|instagram|mailto|challenge|security|youtube|apply|complaint|application|sample.*ballot|meeting.*(?:minutes|archives)|minutes|zoning',hay):continue
        if not re.search(r'\bprecinct|polling.{0,35}(?:location|place|map)|(?:district.{0,35}map|map.{0,35}district)|\bgis\b|redistrict',hay):continue
        if url in seen:continue
        seen.add(url)
        score=10*bool(re.search(r'precinct.{0,45}map|map.{0,45}precinct',hay))+8*url.lower().endswith(('.pdf','.zip'))+4*bool(re.search(r'2024|2020|2018|histor',hay))+2*bool(re.search(r'\bgis\b',hay))
        out.append({'url':url,'anchor_text':label,'original_href':a['href'],'score':score})
    return sorted(out,key=lambda a:-a['score'])

def run(parent):
    out={'parent_key':parent['parent_key'],'parent_label':parent['parent_label'],'fips':parent['fips'],'visited':[],'all_relevant_candidates':[],'bound':'2 map-specific first-level anchors; 2 linked PDF/ZIP assets; challenge stops source'}
    if not parent.get('site_receipt'):out['gap']='directory did not return public URL (see complete lookup response)';return out
    r=json.loads((HERE/parent['site_receipt']).read_bytes()); selected=candidates(r)
    out['all_relevant_candidates']=selected
    for a in selected[:2]:
        key='local-map-'+parent['fips']+'-'+sha(a['url'].encode())[:12];rec=fetch(key,a['url'],parent['site_receipt']+' actual anchor '+json.dumps(a))
        out['visited'].append({'receipt':'requests/'+key+'.json','link':a,'status':rec['hops'][-1]['status']})
        if rec['hops'][-1]['status']==200 and not entity(rec).startswith((b'%PDF',b'PK')):
            sub=[x for x in candidates(rec) if urlsplit(x['url']).path.lower().endswith(('.pdf','.zip'))]
            out.setdefault('all_asset_candidates',[]).extend(sub)
            for asset in sub[:2]:
                subkey='local-asset-'+parent['fips']+'-'+sha(asset['url'].encode())[:12];rr=fetch(subkey,asset['url'],'requests/'+key+'.json actual anchor '+json.dumps(asset))
                out['visited'].append({'receipt':'requests/'+subkey+'.json','link':asset,'status':rr['hops'][-1]['status']})
    if not selected:out['gap']='no eligible map-specific actual anchors in successful static registrar HTML, or access failure/challenge; state originals retained'
    return out

if __name__=='__main__':
    parents=json.loads((HERE/'local-navigation.json').read_bytes())['parents']
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows=[]
        for r in pool.map(run,parents):rows.append(r);print(r['parent_label'],len(r['visited']),flush=True)
    (HERE/'local-map-navigation.json').write_text(json.dumps({'parents':rows,'filter_version':2},indent=2)+'\n')
