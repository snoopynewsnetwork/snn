"""Read-only structural, whole-reference, source and negative-fixture audit."""
from common import *
from build import generate,raw_receipts,entity,scopeparent
from reconstruct import resolve
from collections import Counter
import copy,re

def research_snapshot_gate(v):
    """Negative-fixture admission specification only; no collector or vote importer."""
    required={'election_date','stage','contest','is_production','genuine_nonzero_returns','source_clock','source_clock_timezone','retrieval_utc','native_ids','admin_scopes','companion_files','null_metadata','authority_chain_verified','full_candidate_universe_verified','overlap_policy','explicit_admission'}
    assert required<=v.keys()
    assert v['election_date']=='2026-11-03' and v['stage']=='general' and v['contest']=='Senator in Congress'
    assert all(v[k] is True for k in ['is_production','genuine_nonzero_returns','authority_chain_verified','full_candidate_universe_verified','explicit_admission'])
    assert v['source_clock'] and v['source_clock_timezone'] and v['retrieval_utc']
    assert isinstance(v['native_ids'],list) and v['native_ids'] and len(set(v['native_ids']))==len(v['native_ids'])
    assert set(v['admin_scopes'])=={'9001','9002','9011','9012'}
    assert v['companion_files'] and v['null_metadata']=={'unavailable':None,'observed_zero':0}
    assert v['overlap_policy']=='one authoritative cumulative scope per unit/time; replace, never add'

def structural(full,inventory,parents):
    assert len(full)==458 and len({r['dispatch_key'] for r in full})==458
    assert [r['ordered_rank'] for r in full]==list(range(1,459))
    assert sum(r['partition']=='priority' for r in full)==242
    assert len(inventory)==497 and sum(r['Senate_total'] is None for r in inventory)==39
    assert sum(r['Senate_total']==0 for r in inventory)==15
    assert len(parents)==43 and len({r['key'] for r in parents})==43
    assert sum(p['directory'] is not None for p in parents)==39
    assert sum(p['priority_parent'] for p in parents)==37
    assert sum(p['historical_Senate_votes'] for p in parents)==491948
    assert sum(p['historical_Senate_votes'] for p in parents if p['directory'] is None)==1473
    for r in full:
        assert r['current_leaf_mapping'] is None and r['independent_feed_count']==0 and r['admitted_November'] is False
        assert r['whole_native']['complete_object'] and r['whole_parent']['complete_object']
    for r in inventory:assert r['current_leaf_mapping'] is None and 'Senate_status' in r
    for p in parents:
        assert p['current_November_source'] is None and p['exact_outstanding'] is None
        assert p['historical_whole_parent']['complete_object']
        if p['directory'] is None:assert p['key'].startswith('RI:state-admin:') and len(p['original_inventory_children'])==1

def run(preseal=False):
    checks=Counter();generated=generate()
    for name,b in generated.items():assert (R/name).read_bytes()==b,name;checks['deterministic_generated_outputs']+=1
    ext=parsed(R/'external-inputs.json')
    assert ext['authority_path']==AUTHORITY and all(p['path']!=AUTHORITY for p in ext['complete_files'])
    for p in ext['complete_files']:verify((S/p['path']).read_bytes(),p);checks['whole_external_file_pins']+=1
    for rec in raw_receipts():
        assert rec['method']=='GET' and rec['submitted_body'] is None and rec['retrieved_at_utc'].endswith('+00:00')
        if rec.get('stored_path'):
            entity(rec);assert rec['body_complete'] and rec['response_headers'] and rec.get('status') is not None
            checks['complete_original_HTTP_entities']+=1
        else:assert rec.get('error') and rec['body_complete'] is False;checks['separate_failure_receipts']+=1
    full=parsed(R/'derived/all-Senate-hierarchy.json');inv=parsed(R/'derived/full-inventory.json');parents=parsed(R/'derived/parent-investigations.json')
    structural(full,inv,parents)
    for collection,fields in [(full,['whole_rank','whole_native','whole_parent']),(inv,['whole_native']),(parents,['historical_whole_parent'])]:
        for r in collection:
            for field in fields:resolve(r[field]);checks['complete_object_references']+=1
    for r in full:
        rank=resolve(r['whole_rank']);n=resolve(r['whole_native']);p=resolve(r['whole_parent'])
        assert n['key']==rank['native_key'] and rank['key']==r['dispatch_key']
        assert n['key'] in p['native_keys'] and scopeparent(n)==p['key']
        assert rank['source_anchor']==r['original_anchor']
        assert n['contests']['Senator in Congress']['candidate_rows']==r['all_historical_candidate_record_keys']
        checks['native_parent_source_hierarchy']+=1
    # Every meaningful structural corruption must be rejected, including total-preserving scope changes.
    mutations=[]
    def reject(name,f):
        try:f()
        except (AssertionError,KeyError,ValueError,TypeError):mutations.append(dict(name=name,rejected=True));return
        raise AssertionError('Negative fixture accepted: '+name)
    reject('missing native context',lambda:structural(full[:-1],inv,parents))
    f=copy.deepcopy(full);f[-1]=copy.deepcopy(f[0]);reject('duplicate historical keys',lambda:structural(f,inv,parents))
    i=copy.deepcopy(inv);next(x for x in i if x['Senate_total'] is None)['Senate_total']=0;reject('unavailable Senate changed to zero',lambda:structural(full,i,parents))
    p=copy.deepcopy(parents);p.pop();reject('missing administrative scope',lambda:structural(full,inv,p))
    f=copy.deepcopy(full);f[0]['whole_native']['complete_object']=False;reject('partial native projection',lambda:structural(f,inv,parents))
    f=copy.deepcopy(full);f[0]['current_leaf_mapping']='0707';reject('historical ID admitted as current',lambda:structural(f,inv,parents))
    rr=copy.deepcopy(full[0]['whole_native']);rr['pointer']='/all_source_native_constituents/1';reject('wrong source object under correct body',lambda:resolve(rr))
    base=dict(election_date='2026-11-03',stage='general',contest='Senator in Congress',is_production=True,genuine_nonzero_returns=True,source_clock='synthetic',source_clock_timezone='UTC',retrieval_utc='synthetic',native_ids=['synthetic-context'],admin_scopes=['9001','9002','9011','9012'],companion_files=['synthetic'],null_metadata={'unavailable':None,'observed_zero':0},authority_chain_verified=True,full_candidate_universe_verified=True,overlap_policy='one authoritative cumulative scope per unit/time; replace, never add',explicit_admission=True)
    research_snapshot_gate(base)
    for name,k,v in [('primary rejected','stage','primary'),('setup rejected','stage','setup'),('staging rejected','is_production',False),('old snapshot rejected','election_date','2024-11-05'),('zero probe rejected','genuine_nonzero_returns',False),('wrong contest rejected','contest','Governor'),('missing native IDs','native_ids',[]),('missing admin scopes','admin_scopes',[]),('missing companions','companion_files',[]),('lost null metadata','null_metadata',{}),('unverified roster','full_candidate_universe_verified',False),('unreviewed admission','explicit_admission',False),('overlap addition rejected','overlap_policy','sum state and towns'),('duplicate current IDs','native_ids',['same','same']),('missing clock timezone','source_clock_timezone',None)]:
        vbase=copy.deepcopy(base);vbase[k]=v;reject(name,lambda:research_snapshot_gate(vbase))
    vbase=copy.deepcopy(base);del vbase['source_clock'];reject('missing clock field',lambda:research_snapshot_gate(vbase))
    checks['rejected_negative_fixtures']=len(mutations)
    # Pin all acquisition/script/data/report relative Markdown links without following external URLs.
    for path in [S/'official-results.md',*sorted(R.rglob('*.md'))]:
        for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if '://' in link or link.startswith('#'):continue
            target=link.split('#')[0]
            if preseal and target in ['asset-manifest.json','final-seal.json']:continue
            assert (path.parent/target).exists(),(path,link);checks['relative_Markdown_links']+=1
    for path in [S/'official-results.md',S/'data/official-results-sources.csv',*sorted(R.rglob('*'))]:
        if path.is_file():assert path.stat().st_size<40000000,path
    return dict(status='pass',authority_path=AUTHORITY,counts=dict(checks),negative_fixtures=mutations,
        scope='Read-only deterministic rebuild, full references and raw/stored bytes, source hierarchy, complete coverage, links and bounds. Admission fixtures are synthetic research safeguards; no collector built or admitted.')
if __name__=='__main__':
    import sys
    result=run(preseal='--write' in sys.argv)
    if '--write' in sys.argv:write(R/'qa/validation.json',dump(result))
    print(json.dumps(result))
