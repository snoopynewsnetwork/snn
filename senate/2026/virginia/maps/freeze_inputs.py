"""Freeze individual original inputs and acquisition context, never the authority."""
import json
from acquire import HERE,sha
if __name__=='__main__':
    assert not (HERE/'final-seal.json').exists()
    inputs=[HERE.parent/'data/turnout/priority-set.json']
    inputs+=sorted((HERE/'requests').glob('*.json'))+sorted((HERE/'originals').glob('*'))
    inputs+=[HERE/name for name in ['state-link-plan.json','directory-selectors.json','local-navigation.json','local-map-navigation.json','supplement-plan.json']]
    rows=[]
    for p in inputs:
        b=p.read_bytes();assert len(b)<40000000;rows.append({'path':str(p.relative_to(HERE.parent)),'bytes':len(b),'sha256':sha(b)})
    (HERE/'input-pins.json').write_text(json.dumps({'schema':'VA-maps-individual-original-inputs-v1','authority_path':'data/coordinator-priority-acceptance.json','authority_storage':'path only; no copied body or digest','files':rows,'producer_execution':False,'current_or_unfinished_official_dependency':False},indent=2)+'\n')
    print(len(rows),'fixed individual inputs')
