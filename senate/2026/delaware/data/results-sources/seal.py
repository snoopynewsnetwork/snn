"""Complete owned manifest. Excludes only itself; readonly --check."""
import json,sys
from freeze import R,S,load,pin
def owned():
    p=[S/'official-results.md',S/'data/official-results-sources.csv']+[x for x in R.rglob('*')if x.is_file() and x!=R/'manifest.json']
    assert not any(x.suffix=='.pyc' or '__pycache__'in x.parts for x in p)
    return sorted(p,key=lambda x:str(x.relative_to(S)))
def main():
    actual=[pin(p)for p in owned()]
    if '--check'in sys.argv:
        m=load(R/'manifest.json');assert m['owned']==actual;assert m['exclude_only']=='data/results-sources/manifest.json';print('PASS manifest',len(actual),'files',sum(x['bytes']for x in actual),'bytes');return
    (R/'manifest.json').write_text(json.dumps(dict(schema='DE-official-complete-owned-seal-v1',owned=actual,exclude_only='data/results-sources/manifest.json',current_approvals=False),indent=2)+'\n');print('Sealed',len(actual),'owned files')
if __name__=='__main__':main()
