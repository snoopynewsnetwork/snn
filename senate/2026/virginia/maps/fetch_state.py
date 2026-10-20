"""Finite acquisition of 133 directly linked ZIPs and 133 complete PDFs."""
import concurrent.futures,json
from acquire import HERE,fetch
if __name__=='__main__':
    parents=json.loads((HERE/'state-link-plan.json').read_bytes())['parents']
    tasks=[(f"state-{kind}-{p['fips']}",p[f'{kind}_link']['url'],f"elect-{ 'gis' if kind=='gis' else 'maps'} actual anchor {p[f'{kind}_link']['href']}; explicit {p['parent_label']} {p['parent_key']}") for p in parents for kind in ['gis','pdf']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for record in pool.map(lambda args:fetch(*args),tasks):
            h=record['hops'][-1];print(record['key'],h['status'],h.get('raw_bytes'),flush=True)
