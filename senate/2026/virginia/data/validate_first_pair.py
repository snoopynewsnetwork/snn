"""Seal/check reviewed first-pair component; not whole-state/current approval."""
from pathlib import Path
import hashlib, json, re, sys, urllib.parse
S=Path(__file__).resolve().parents[1];D=S/'data'
def pin(p):
    b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def main(check):
    seals=[];count=0
    for role,n,total,extra in [('turnout','data/turnout/asset-manifest.json',411,['turnout.md','data/county-turnout.csv']),('baselines','data/baselines/asset-manifest.json',299,['county-partisanship.md','data/county-baselines.csv'])]:
        p=S/n;m=load(p);rows=m['owned_assets'] if role=='turnout' else m['files'];actual={str(f.relative_to(S)) for f in p.parent.rglob('*') if f.is_file() and f!=p}|set(extra)
        assert len(rows)==len({r['path'] for r in rows})==total and actual=={r['path'] for r in rows}
        for r in rows:assert pin(S/r['path'])=={k:r[k] for k in ['path','bytes','sha256']} and r['bytes']<40000000;count+=1
        seals.append(dict(role=role,manifest=pin(p),exact_owned_targets=total))
    original_refs=load(D/'turnout/source/pinned-originals.json')
    for r in original_refs:
        p=S/r['body_path'];assert p.stat().st_size==r['stored_bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['stored_sha256']
    current=load(D/'turnout/priority-set.json');units=current['ordered_units'];assert len(units)==2669 and len(current['parent_inventory'])==133 and len(current['ordered_priority_keys'])==1538 and len(current['ordered_remainder_keys'])==1131
    assert sum(r['reported_candidate_writein_votes'] for r in units)==4445535 and sum(r['reported_candidate_writein_votes'] for r in units[:1537])==3555604 and sum(r['reported_candidate_writein_votes'] for r in units[:1538])==3557034
    assert len(dict.fromkeys(r['parent_key'] for r in units[:1538]))==108
    for name in ['coordinator-turnout-original-review.json','coordinator-turnout-repair-final-review.json','coordinator-baseline-final-review.json','coordinator-baseline-cli-review.json']:assert load(D/name)['status'].startswith('pass')
    markdown=[S/'README.md',S/'research-review.md',S/'research-dispatch.md',S/'turnout.md',S/'county-partisanship.md']+list((D/'turnout').rglob('*.md'))+list((D/'baselines').rglob('*.md'))
    links=0
    for p in markdown:
        for u in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)',p.read_text()):
            u=u.split(' "')[0].strip('<>');x=urllib.parse.urlsplit(u)
            if x.scheme or x.netloc or not x.path:continue
            assert (p.parent/urllib.parse.unquote(x.path)).exists(),(p,u);links+=1
    result=dict(status='pass_reviewed_first_pair_historical_source_and_conditional_scenarios',actual_question_workers_finished=2,whole_state_four_question_complete=False,producer_seals=seals,exact_producer_hashes=count,complete_shared_originals=[dict(path=r['body_path'],stored_sha256=r['stored_sha256'],stored_bytes=r['stored_bytes'],raw_sha256=r['raw_sha256']) for r in original_refs],independent_original_source_checks=790790,independent_repair_preservation_checks=2286,independent_baseline_source_math_checks=869122,actual_independent_CLI_cases=66,exact_captured_peer_comparisons=60220,native_count=2669,all_parent_localities=133,priority_native_count=1538,priority_parent_count=108,remainder_native_count=1131,reported_candidate_generic_total=4445535,top15_marks=80617,integer80threshold=3556428,preceding_marks=3555604,prefix_marks=3557034,required_baseline_contests=4,all_native_baseline_rows=11009,current_producer_bytes_unchanged=True,local_Markdown_links=links,external_full_source_authority_next=True,coordinator_legal_current_geometry_feed_eligibleWI_live_probability_approval=False,review_proofs=[pin(D/n) for n in ['coordinator-turnout-original-review.json','coordinator-turnout-repair-final-review.json','coordinator-baseline-final-review.json','coordinator-baseline-cli-review.json']])
    b=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode();p=D/'coordinator-first-pair-validation.json'
    if check:assert p.read_bytes()==b
    else:p.write_bytes(b)
    print(json.dumps(dict(status=result['status'],producer_targets=count,validation=pin(p),priority_parent_count=108)))
if __name__=='__main__':main('--check' in sys.argv)
