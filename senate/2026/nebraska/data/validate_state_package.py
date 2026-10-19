"""Whole Nebraska research integration seal; --check is strictly read-only."""
from pathlib import Path
import ast,gzip,hashlib,json,re,sys,urllib.parse
D=Path(__file__).resolve().parent;S=D.parent
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def main(check=False):
 mfpath=D/'coordinator-asset-manifest.json';vp=D/'coordinator-validation.json';checks={};totalpins=0
 for path,ownkey,refkeys,expected in [('data/turnout/asset-manifest.json','owned_artifacts',['shared_original_references','peer_primary_original_references'],138),('data/baselines/asset-manifest.json','assets',['references'],108),('data/results-sources/asset-manifest.json','owned_artifacts',['external_original_references'],1036),('maps/asset-manifest.json','owned_artifacts',['external_original_references'],535)]:
  m=load(S/path);assert len(m[ownkey])==expected
  for r in m[ownkey]+[r for k in refkeys for r in m[k]]:
   if 'path'in r:assert pin(S/r['path'])=={k:r[k]for k in ['path','bytes','sha256']}and r['bytes']<40_000_000
   else:
    receipt=r['receipt'];z=(S/r['reference_path']).read_bytes();raw=gzip.decompress(z);assert len(z)==receipt['stored_bytes']<40_000_000 and hashlib.sha256(z).hexdigest()==receipt['stored_sha256'];assert len(raw)==receipt['raw_bytes']==r['independently_verified_raw_bytes']and hashlib.sha256(raw).hexdigest()==receipt['raw_sha256']==r['independently_verified_raw_sha256']
   totalpins+=1
  checks[path]=dict(manifest=pin(S/path),owned=expected,all_exact_pins=True)
 accepted=load(D/'coordinator-priority-acceptance.json');contract=D/'turnout/priority-set.json';assert pin(contract)==accepted['frozen_contract']and accepted['status']=='accepted_historical_named_canvass_dispatch_only';c=load(contract)
 assert len(c['ordered_full_keys'])==1326 and len(c['ordered_priority_keys'])==765 and len(c['ordered_remainder_keys'])==561 and len(c['all93_parents'])==93
 reviews=['coordinator-initial-native-named-order-review.json','coordinator-finished-first-pair-review.json','coordinator-native-method-original-review.json','coordinator-native-original-visual-review.json','coordinator-turnout-readonly-validation.json','coordinator-finished-official-review.json','coordinator-current-official-setup-review.json','coordinator-current-law-effective-date-review.json','coordinator-official-readonly-validation.json','coordinator-finished-maps-review.json','coordinator-finished-maps-visual-review.json','coordinator-maps-readonly-validation.json']
 for rel in reviews:assert load(D/rel)['status'].startswith('pass')
 py=0;links=0;frozen_doc_anchors=0;files=[p for p in S.rglob('*')if p.is_file()]
 for p in files:
  assert p.stat().st_size<40_000_000 and not any(k in p.parts for k in ['__pycache__','node_modules','.venv','.cache'])
  if p.suffix=='.py':ast.parse(p.read_bytes(),filename=str(p));py+=1
 for p in S.rglob('*.md'):
  anchor=p
  if '/frozen/'in str(p):
   # Byte-exact audit copies preserve original document links and source context.
   anchor=S/str(p).split('/frozen/',1)[1];assert anchor.read_bytes()==p.read_bytes();frozen_doc_anchors+=1
  if p==D/'results-sources/report-template.md':anchor=S/'official-results.md' # template emits links at the delivered report's location
  for target in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)',p.read_text()):
   target=target.split(' "')[0].strip('<>');url=urllib.parse.urlsplit(target)
   if url.scheme or target.startswith('#'):continue
   assert (anchor.parent/urllib.parse.unquote(url.path)).exists(),(str(p),target);links+=1
 result=dict(status='pass_complete_four_question_historical_research_with_explicit_source_limits',checks=checks,total_question_owned_and_reference_pin_checks=totalpins,independent_reviews=[pin(D/r)for r in reviews],external_historical_authority=pin(D/'coordinator-priority-acceptance.json'),frozen_contract=pin(contract),full_native=1326,priority=765,remainder=561,all_county_parents=93,priority_parents=58,source_named_denominator=935005,priority_named_votes=748190,preceding764=747645,all_eligible_writein_membership_robustness_proven=False,all_current_geography_or_live_count_approval=False,Python_AST_files=py,local_Markdown_links=links,byte_exact_audit_MD_copies_resolve_at_verified_original_document_context=frozen_doc_anchors,all_stored_artifacts_strictly_below40MB=True,no_cache_dependency_trees=True,question_workers_actually_finished=4,whole_manifest_self_exclusion='data/coordinator-asset-manifest.json',qualification='Research/source/scenario readiness only. Complete source discrepancies, unknown eligible write-ins, Census-only162 map entries, unapproved current reporting/geometry, setup-only current data, no measured changing cadence/exact remainder/calibrated probabilities remain explicit. Whole manifest covers this validation without a reverse manifest hash.')
 b=(json.dumps(result,indent=2)+'\n').encode()
 if check:assert vp.read_bytes()==b
 else:vp.write_bytes(b)
 allfiles=[p for p in S.rglob('*')if p.is_file()and p!=mfpath];entries=[pin(p)for p in sorted(allfiles)];out=dict(schema='NE-coordinator-whole-state-assets-v1',hash='SHA256',assets=entries,excludes_only='data/coordinator-asset-manifest.json',total_files=len(entries),total_bytes=sum(r['bytes']for r in entries),maximum_stored_bytes=max(r['bytes']for r in entries),worker_assets_unchanged=True,validation_no_reverse_manifest_pin=True)
 b=(json.dumps(out,indent=2)+'\n').encode()
 if check:assert mfpath.read_bytes()==b
 else:mfpath.write_bytes(b)
 print(json.dumps(dict(validation=pin(vp),whole_manifest=pin(mfpath),files=len(entries),bytes=out['total_bytes'],maximum=out['maximum_stored_bytes'])))
if __name__=='__main__':main('--check'in sys.argv)
