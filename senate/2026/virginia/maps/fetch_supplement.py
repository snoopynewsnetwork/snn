"""Finite supplement: actual Fairfax mapbooks/change maps and Census VTD ZIP."""
import concurrent.futures,json
from acquire import HERE,fetch,sha,entity
from discover_state import Links
from urllib.parse import urljoin

if __name__=='__main__':
    navigation=json.loads((HERE/'local-map-navigation.json').read_bytes())['parents']
    fairfax=next(p for p in navigation if p['fips']=='51059')
    tasks=[]
    for a in fairfax['all_asset_candidates']:
        if 'Standards' in a['anchor_text']:continue
        tasks.append(('local-asset-51059-'+sha(a['url'].encode())[:12],a['url'],'requests/local-map-51059-b3ec9a8de6df.json actual anchor '+json.dumps(a)))
    r=json.loads((HERE/'requests/census-vtd-directory.json').read_bytes());p=Links();p.feed(entity(r).decode())
    matches=[a for a in p.links if a['href']=='tl_2020_51_vtd20.zip'];assert len(matches)==1
    tasks.append(('census-vtd-2020',urljoin(r['final_url'],matches[0]['href']),'census-vtd-directory actual href '+matches[0]['href']+'; historical Census VTD fallback, not current/legal precincts'))
    (HERE/'supplement-plan.json').write_text(json.dumps({'tasks':tasks,'bound':'all14actualFairfaxbook/change/locatorPDFanchors excluding standards; one actual linked Census Virginia VTD ZIP; no service query'},indent=2)+'\n')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for r in pool.map(lambda t:fetch(*t),tasks):print(r['key'],r['hops'][-1]['status'],r['hops'][-1].get('raw_bytes'),flush=True)
