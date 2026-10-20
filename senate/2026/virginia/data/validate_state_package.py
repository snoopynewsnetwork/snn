"""Coordinator complete publication inventory; --check is entirely read-only."""
from pathlib import Path
import ast,hashlib,json,re,sys,urllib.parse
S=Path(__file__).resolve().parents[1];D=S/'data';CACHE={}
def load(p):return json.loads(p.read_bytes())
def pin(p):
    p=p.resolve()
    if p not in CACHE:
        b=p.read_bytes();CACHE[p]={'path':str(p.relative_to(S)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    return CACHE[p]
def main(check=False):
    mf=D/'coordinator-asset-manifest.json';validation=D/'coordinator-validation.json';seals=[];n=0
    for role,path,key,count,extras in [
        ('turnout','data/turnout/asset-manifest.json','owned_assets',411,['turnout.md','data/county-turnout.csv']),
        ('baselines','data/baselines/asset-manifest.json','files',299,['county-partisanship.md','data/county-baselines.csv']),
        ('official','data/results-sources/asset-manifest.json','files',2661,['official-results.md','data/official-results-sources.csv']),
        ('maps','maps/asset-manifest.json','files',2803,['precinct-maps.md'])]:
        p=S/path;m=load(p);rows=m[key]
        actual={str(f.relative_to(S)) for f in p.parent.rglob('*') if f.is_file() and f!=p}|set(extras)
        assert len(rows)==len({r['path'] for r in rows})==count and {r['path'] for r in rows}==actual,role
        for r in rows:
            assert pin(S/r['path'])=={k:r[k] for k in ['path','bytes','sha256']} and r['bytes']<40000000,r['path'];n+=1
        seals.append({'role':role,'manifest':pin(p),'owned_targets_excluding_only_manifest':count})
    authority=load(D/'coordinator-priority-acceptance.json');contract=load(D/'turnout/priority-set.json');full=contract['ordered_units']
    assert pin(D/'turnout/priority-set.json')==authority['frozen_contract']
    assert len(contract)==len(authority['complete_root_field_semantics'])==25
    assert len(authority['complete_source_companion_files'])==471 and authority['complete_source_object_count']==3474062
    assert len(authority['complete_source_object_reference_bodies'])==24 and len(authority['frozen_file_pins'])==721 and len(authority['historical_full_body_resolvers'])==1172
    assert len(full)==2669 and len(contract['parent_inventory'])==133
    assert authority['ordered_full_keys']==[u['key'] for u in full]
    assert authority['ordered_priority_keys']==[u['key'] for u in full[:1538]] and authority['ordered_remainder_keys']==[u['key'] for u in full[1538:]]
    assert authority['primary_source_denominator']==4445535 and authority['top15_votes']==80617 and authority['priority_parent_count']==108
    for k in ['current_geography_approved','current_November_returns_admitted','current_choice_or_reporting_IDs_approved','legal_native80_robustness_approved','live_cadence_or_exact_remainder_approved','collector_or_probability_approval']:assert authority[k] is False
    names=['coordinator-turnout-original-review.json','coordinator-turnout-repair-final-review.json','coordinator-baseline-final-review.json','coordinator-baseline-cli-review.json','coordinator-priority-validation.json','coordinator-newsroom-original-review.json','coordinator-official-final-review.json','coordinator-maps-final-review.json']
    for name in names:assert load(D/name)['status'].startswith('pass'),name
    syntax=links=0
    for p in S.rglob('*'):
        assert not {'__pycache__','node_modules','.venv','venv','.pytest_cache'}&set(p.relative_to(S).parts),p
        if not p.is_file():continue
        assert p.stat().st_size<40000000 and not p.is_symlink(),p
        if p.suffix=='.py':ast.parse(p.read_bytes(),filename=str(p));syntax+=1
        if p.suffix!='.md':continue
        for target in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)',p.read_text()):
            target=target.split(' "')[0].strip('<>');u=urllib.parse.urlsplit(target)
            if u.scheme or u.netloc or not u.path:continue
            base=S if p.name=='report-template.md' else p.parent
            dest=(base/urllib.parse.unquote(u.path)).resolve()
            assert dest.exists() or (not check and dest in [mf.resolve(),validation.resolve()]),(p,target)
            links+=1
    result={'status':'pass_complete_four_question_bounded_historical_research','actual_original_question_workers_finished':4,'producer_seals':seals,'exact_question_owned_hash_checks':n,'independent_reviews':[pin(D/name) for name in names],'external_historical_source_authority':pin(D/'coordinator-priority-acceptance.json'),'frozen_contract':pin(D/'turnout/priority-set.json'),'complete_roots':25,'whole_companions':471,'every_recursive_object':3474062,'ordered_partitions':24,'fixed_file_pins':721,'historical_body_resolvers':1172,'all_native_historical_records':2669,'priority':1538,'remainder':1131,'all_parents':133,'counties':95,'independent_cities':38,'priority_parent_chains':108,'denominator':4445535,'top15_votes':80617,'minimum80_votes':3557034,'preceding_votes':3555604,'integer80threshold':3556428,'current_native_setup_objects':2528,'current_candidate_method_setup_entries':37920,'genuine_November_votes_admitted':False,'map_original_ZIPs':134,'map_features':4997,'all_XY_pairs':4783111,'all_PDF_pages_automatically_rendered':912,'coordinator_actual_whole_map_images_viewed':2,'approved_leaf_polygon_joins':0,'all_producer_bytes_unchanged':True,'Python_AST_files':syntax,'local_Markdown_links':links,'whole_manifest_excludes_only':'data/coordinator-asset-manifest.json','validation_has_no_reverse_manifest_pin':True,'qualification':'Completed bounded research only. Missing Covington state-directory record, Charlotte/Highland local static chains, chapter approval-date public-access limits, source chronology/generic36/turnout differences, later roster/write-in/legal exhaustion, old/current IDs/geometry, genuine changing returns, measured cadence, eligible pool, collector/forecast/calibration remain unknown or unapproved. Legacy preparation scripts and their dated diagnostics are retained as history, not final reconstruction inputs.'}
    b=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
    if check:assert validation.read_bytes()==b
    else:validation.write_bytes(b)
    CACHE.pop(validation.resolve(),None)
    rows=[pin(p) for p in sorted(S.rglob('*')) if p.is_file() and p!=mf]
    whole={'schema':'VA-coordinator-complete-published-state-inventory-v1','assets':rows,'excludes_only':'data/coordinator-asset-manifest.json','total_files':len(rows),'total_bytes':sum(r['bytes'] for r in rows),'maximum_stored_bytes':max(r['bytes'] for r in rows),'all_producer_bytes_unchanged':True,'validation_has_no_reverse_manifest_pin':True}
    b=(json.dumps(whole,ensure_ascii=False,indent=2)+'\n').encode()
    if check:assert mf.read_bytes()==b
    else:mf.write_bytes(b)
    print(json.dumps({'status':result['status'],'validation':pin(validation),'files_excluding_manifest':len(rows),'total_bytes':whole['total_bytes'],'maximum_stored_bytes':whole['maximum_stored_bytes']}))
if __name__=='__main__':main('--check' in sys.argv)
