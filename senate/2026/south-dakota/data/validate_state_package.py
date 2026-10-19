"""Whole South Dakota integration seal; --check never writes research assets."""
from pathlib import Path
import ast,hashlib,json,re,sys,urllib.parse
D=Path(__file__).resolve().parent;S=D.parent
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def main(check=False):
 mfpath=D/'coordinator-asset-manifest.json';vp=D/'coordinator-validation.json';checks={};total=0
 configs=[('data/turnout/asset-manifest.json','owned_paths','reused_read_only_objects',112),('data/baselines/asset-manifest.json','owned_assets','read_only_references',110),('data/results-sources/asset-manifest.json','owned_assets','read_only_dependencies',526),('maps/asset-manifest.json','owned_assets',None,591)]
 for rel,ownkey,refkey,count in configs:
  m=load(S/rel);owned=m[ownkey];refs=m[refkey] if refkey else load(S/m['read_only_reference_manifest']);assert len(owned)==count
  for p in owned+refs:
   assert pin(S/p['path'])=={k:p[k] for k in ['path','bytes','sha256']} and p['bytes']<40_000_000;total+=1
  checks[rel]=dict(manifest=pin(S/rel),owned=count,references=len(refs),all_exact_pins=True)
 acceptance=load(D/'coordinator-priority-acceptance.json');contract=D/'turnout/priority-set.json';assert pin(contract)==acceptance['frozen_contract']
 assert acceptance['status']=='accepted_historical_public_native_source_dispatch_only'
 assert not acceptance['certified_minimum_or_membership_approved'] and not acceptance['current_geography_approved'] and not acceptance['current_November_returns_admitted']
 c=load(contract);assert len(c['all_units'])==691 and len(c['ordered_priority_keys'])==304 and len(c['county_parents'])==66
 assert sum(v['contest_votes'] for v in c['all_units'][:303])==342947 and sum(v['contest_votes'] for v in c['all_units'][:304])==343402
 assert sum(v['contest_votes'] for v in c['all_units'][304:])==85326
 reviews=['coordinator-finished-first-pair-review.json','coordinator-initial-public-native-review.json','coordinator-native-original-visual-review.json','coordinator-turnout-readonly-validation.json','coordinator-finished-official-review.json','coordinator-current-ballot-law-visual-review.json','coordinator-finished-maps-review.json','coordinator-finished-maps-visual-review.json']
 for rel in reviews:assert load(D/rel)['status'].startswith('pass')
 py=links=archived_docs=0
 for p in S.rglob('*'):
  if not p.is_file():continue
  assert p.stat().st_size<40_000_000 and not any(v in p.parts for v in ['__pycache__','node_modules','.venv','.cache'])
  if p.suffix=='.py':ast.parse(p.read_bytes(),filename=str(p));py+=1
 for p in S.rglob('*.md'):
  anchor=p
  if '/frozen/' in str(p):
   anchor=S/str(p).split('/frozen/',1)[1];assert anchor.read_bytes()==p.read_bytes();archived_docs+=1
  for target in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)',p.read_text()):
   target=target.split(' "')[0].strip('<>');u=urllib.parse.urlsplit(target)
   if u.scheme or target.startswith('#'):continue
   assert (anchor.parent/urllib.parse.unquote(u.path)).exists(),(str(p),target);links+=1
 result=dict(status='pass_complete_four_question_historical_research_with_explicit_source_limits',question_manifests=checks,total_question_owned_and_reference_pin_checks=total,independent_reviews=[pin(D/r) for r in reviews],external_historical_authority=pin(D/'coordinator-priority-acceptance.json'),frozen_contract=pin(contract),question_workers_actually_finished=4,primary_source_native=691,primary_priorities=304,remainder=387,all_county_parents=66,priority_parents=39,source_denominator=428728,separate_signed_denominator=428922,priority_votes=343402,preceding303=342947,certified_native_minimum_or_membership_robustness_proven=False,all_current_geography_or_live_count_approval=False,Python_AST_files=py,local_Markdown_links=links,byte_exact_archived_reports_link_at_verified_original_context=archived_docs,all_stored_artifacts_strictly_below40MB=True,no_cache_dependency_trees=True,whole_manifest_self_exclusion='data/coordinator-asset-manifest.json',qualification='Research/source/scenario readiness only. Public/signed194 and41 vote gaps, separate2022PDF/Yankton omission, registration/source conflicts,96 Census-only map entries, native invalid/curve geometry, incompatible current654/656/673 setup and missingCharlesMix, current crosswalk/later law/ballot scope, changing cadence/exact remainder/calibrated probability limits remain explicit. Whole manifest includes this validation without a reverse manifest hash.')
 b=(json.dumps(result,indent=2)+'\n').encode()
 if check:assert vp.read_bytes()==b
 else:vp.write_bytes(b)
 entries=[pin(p) for p in sorted(S.rglob('*')) if p.is_file() and p!=mfpath]
 out=dict(schema='SD-coordinator-whole-state-assets-v1',hash='SHA256',assets=entries,excludes_only='data/coordinator-asset-manifest.json',total_files=len(entries),total_bytes=sum(v['bytes'] for v in entries),maximum_stored_bytes=max(v['bytes'] for v in entries),worker_assets_unchanged=True,validation_no_reverse_manifest_pin=True)
 b=(json.dumps(out,indent=2)+'\n').encode()
 if check:assert mfpath.read_bytes()==b
 else:mfpath.write_bytes(b)
 print(json.dumps(dict(validation=pin(vp),whole_manifest=pin(mfpath),files=len(entries),total_bytes=out['total_bytes'],maximum=out['maximum_stored_bytes'])))
if __name__=='__main__':main('--check' in sys.argv)
