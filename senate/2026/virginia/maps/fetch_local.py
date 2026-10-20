"""Read exact public locality selectors, then one linked registrar URL per priority parent."""
import concurrent.futures,json,re
from acquire import HERE,fetch,entity

def run(parent):
    opts=json.loads((HERE/'directory-selectors.json').read_bytes())['options']
    label=parent['parent_label'].upper().replace('KING AND QUEEN COUNTY','KING & QUEEN COUNTY')
    selected=[o for o in opts if o['label']==label]
    assert len(selected)==1,(label,selected)
    key='registrar-lookup-'+parent['fips']
    result=fetch(key,'https://vote.elections.virginia.gov/VoterInformation/PublicContactLookup', 'elect-directory actual form and option '+json.dumps(selected[0]), {'LocalityUid':selected[0]['value']})
    b=entity(result)
    match=re.search(r'<strong>URL</strong>\s*</p>\s*<p>(.*?)</p>',b.decode(),re.S) if b else None
    url=match.group(1).strip() if match else None
    record={'parent_key':parent['parent_key'],'parent_label':parent['parent_label'],'fips':parent['fips'],'selector':selected[0],'lookup_receipt':f'requests/{key}.json','published_registrar_url':url}
    if url and url.startswith(('http://','https://')):
        site=fetch('registrar-site-'+parent['fips'],url,key+' literal public URL field; no contact sent')
        record['site_receipt']='requests/registrar-site-'+parent['fips']+'.json'
        record['site_final_url']=site['final_url'];record['site_status']=site['hops'][-1]['status']
    return record

if __name__=='__main__':
    parents=[p for p in json.loads((HERE/'state-link-plan.json').read_bytes())['parents'] if p['priority_children']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows=[]
        for r in pool.map(run,parents): rows.append(r);print(r['parent_label'],r.get('site_status'),flush=True)
    (HERE/'local-navigation.json').write_text(json.dumps({'scope':'all108priorityparents; actual public selector and one published registrar URL each','parents':rows},indent=2)+'\n')
