"""Read-only bounded repair/captured-core/history audit and actual renderer regression."""
import collections,copy,gzip,json,re,sys,tarfile
from pathlib import Path
from captured import T,S,H,sha,Capture
sys.path.insert(0,str(T))
from render_prose import render_prose

def audit(preseal=False):
 old=Capture('turnout-original-first');peer=Capture('baseline-final-peer');checks={};detail={}
 def ck(n,test):assert test,n;checks[n]=True
 for cap in [old,peer]:
  for path in cap.entries:cap.read(path)
 ck('complete_original389_and_peer300_body_or_exact_reference_captures',len(old.entries)==389 and len(peer.entries)==300)
 ck('exact_original_manifest_witness_and_whole_archive_pins',sha(old.read('data/turnout/asset-manifest.json'))=='6eafa8cc1a897b40075d8234681b832282d871490043b98ef3c7f5c878fd2b50' and sha((T/'pre-peer-witness.json').read_bytes())=='65318164238e4a7ac04ad9dce4421747cd80a6f13117c61d53fdec3598c69485' and sha((T/'pre-peer-bodies.tar.gz').read_bytes())=='3fdb602bf0e87d43719329f540d2f50ca76dc704462e63de66b86cac3cbc1e15')
 witness=json.loads((T/'pre-peer-witness.json').read_text())
 with tarfile.open(T/'pre-peer-bodies.tar.gz') as tar:
  ck('original_whole_witness_membership394',set(tar.getnames())=={e['archive_name'] for e in witness['bodies']} and len(witness['bodies'])==394)
  for e in witness['bodies']:
   b=tar.extractfile(e['archive_name']).read();assert sha(b)==e['sha256'] and len(b)==e['bytes'];assert b==(old.read(e['original_path']) if e['original_path'] in old.entries else (S/e['original_path']).read_bytes())
 ck('all_original_prepeer_witness_exact_bodies_preserved_against_history',True)
 finding=json.loads((H/'finding-finding.json').read_text());receipt=T/'source/acquired/enr-2024-results-report.receipt.json'
 ck('existing_actual_results_receipt_unchanged',len(receipt.read_bytes())==3438 and sha(receipt.read_bytes())=='fc240b6ba30520c7ac80c2d7bfdb2ca0c568a3bab29bc50ac8dd3a3b2d5cb364')
 r=json.loads(receipt.read_text());actual=r['requested_url'];ck('correct_citation_bound_to_actual_request_and_final200',actual==finding['actual_retained_requested_final_URL'] and r['final_url']==actual and r['hops'][-1]['status']==200)
 # Execute the exact prior production formatter body to demonstrate the original defect, without importing old producer code.
 src=old.read('data/turnout/build_turnout.py').decode();start=src.index(" report=re.sub(r'\\b(all|");end=src.index(" (STATE/'turnout.md').write_text(report)",start);namespace={'re':re};exec('def old_renderer(report):\n'+src[start:end]+' return report\n',namespace)
 ck('historical_actual_renderer_defect_reproduced_not_claimed_previously_caught',namespace['old_renderer']('[source]('+actual+')')=='[source]('+finding['wrong_report_target']+')')
 # Adversarial tokens exercise the actual new renderer and the actual failed UUID, rather than a stand-in formatter.
 examples=['[source]('+actual+')',actual,'`a931 a5f7 literal0 and2020 va:161257:csv-record:2717`','```\na931 a5f7 and2020 literal0\n```','e5b689ae-a931-4b8a-a5f7-7392e9571c61','va:161257:csv-record:2717']
 ck('actual_production_renderer_preserves_external_targets_code_source_ids',all(render_prose(x)==x for x in examples))
 ck('renderer_still_formats_only_prose',render_prose('all133 '+examples[0])=='all 133 '+examples[0])
 cfg=json.loads((T/'review/peer-settings.json').read_text());expected=old.read('turnout.md').decode().replace(finding['wrong_report_target'],actual)
 for e in cfg['report_replacements']:assert expected.count(e['before'])==1;expected=expected.replace(e['before'],e['after'])
 text=(S/'turnout.md').read_text();ck('report_only_confirmed_citation_and_permitted_peer_history_metadata_changed',text==expected)
 edges=set();ix=json.loads((T/'source/acquisition-index.json').read_text())
 for e in ix['receipts']:
  rec=e['full_receipt']
  for k in ['requested_url','final_url']:
   if rec.get(k):edges.add(rec[k])
  for hop in rec['hops']:
   for k in ['request_url','response_url']:
    if hop.get(k):edges.add(hop[k])
 targets=re.findall(r'\]\((https?://[^)]+)\)',text);ck('every_generated_external_literal_citation_matches_retained_actual_request_edge',all(t in edges and not re.search(r'\s',t) for t in targets));detail['literal_external_targets']=[{'target':t,'role':'exact retained request/response edge'} for t in targets]
 # Exact before/after code span inventory covers every generated code/source identifier; newly added pins are verified captured identities.
 beforecodes=re.findall(r'`([^`\n]+)`',old.read('turnout.md').decode());aftercodes=re.findall(r'`([^`\n]+)`',text)
 ck('all_prior_code_and_source_identifiers_preserved',not (collections.Counter(beforecodes)-collections.Counter(aftercodes)))
 ck('new_peer_identifiers_are_actual_captured_pins',sha(peer.read('data/baselines/pre-peer-witness.json'))==cfg['peer_metadata']['captured_pre_peer_witness_sha256'] and peer.index['manifest_sha256']==cfg['peer_metadata']['captured_manifest_sha256'])
 before=json.loads(old.read('data/turnout/priority-set.json'));current=json.loads((T/'priority-set.json').read_text())
 def invariant(c):
  a=copy.deepcopy(c);p=a.pop('peer');o=copy.deepcopy(before);o.pop('peer');assert a==o
  rs=c['ordered_units'];assert len(rs)==2669 and len({r['key'] for r in rs})==2669
  assert rs==sorted(rs,key=lambda x:(-x['reported_candidate_writein_votes'],x['source_record']))
  k=c['minimum80']['count'];total=sum(r['reported_candidate_writein_votes'] for r in rs);assert total==4445535 and 5*sum(r['reported_candidate_writein_votes'] for r in rs[:k])>=4*total and 5*sum(r['reported_candidate_writein_votes'] for r in rs[:k-1])<4*total
  assert c['ordered_priority_keys']+c['ordered_remainder_keys']==[r['key'] for r in rs]
  assert all(r['current_2026_crosswalk'] is None and r['legal_named_writein_allocation'] is None for r in rs)
 invariant(current);ck('all_original_contract_semantics_arrays_nulls_admin_fields_unchanged_except_peer',current['peer']==cfg['peer_metadata'])
 ck('native_csv_exact_original_bytes',sha((S/'data/county-turnout.csv').read_bytes())=='5ce44dc51ad9c096013e9b63fd2e73b9b723f34480b185312da5c2cd10bf848f')
 def bad(name,change):
  x=copy.deepcopy(current);change(x)
  try:invariant(x)
  except AssertionError:checks['negative_'+name]=True;return
  raise AssertionError('negative fixture escaped '+name)
 bad('omitted_source_unit',lambda x:x['ordered_units'].pop())
 bad('mask_null_to_zero',lambda x:x['ordered_units'][0]['source_native_constituents']['enr_api']['full_native_object'].__setitem__('underVoteCount',0))
 # Swap a real equal-volume pair to exercise the literal source-record tie rule.
 i=next(i for i in range(2668) if current['ordered_units'][i]['reported_candidate_writein_votes']==current['ordered_units'][i+1]['reported_candidate_writein_votes'])
 def swap(x):x['ordered_units'][i],x['ordered_units'][i+1]=x['ordered_units'][i+1],x['ordered_units'][i]
 bad('actual_tie_order',swap);bad('integer_crossing',lambda x:x['minimum80'].__setitem__('count',1537));bad('remainder_omission',lambda x:x['ordered_remainder_keys'].pop());bad('independent_city_parent_merge',lambda x:x['ordered_units'][3].__setitem__('parent_label','Richmond County'));bad('administrative_virtual_flag',lambda x:x['ordered_units'][0].__setitem__('isVirtual',False));bad('current_approval',lambda x:x['ordered_units'][0].__setitem__('current_2026_crosswalk',{'approved':True}))
 ck('negative_literal_uuid_mangling_detected',finding['wrong_report_target'] not in edges and namespace['old_renderer'](examples[0])!=render_prose(examples[0]))
 proof=json.loads((T/'review/reciprocal.json').read_text());ck('actual_captured_full_source_core_and_all17_orders_agreement',proof['status']=='pass' and proof['source_value_differences']==[] and len(proof['orders'])==17 and proof['native_candidate_method_objects']==40035 and proof['api_complete_scopes']==134 and proof['all_parents']==133 and proof['checker_sha256']==sha((T/'review/reciprocal.py').read_bytes()))
 ck('full_receipt_clock_failure_scopes_preserved',proof['receipts']['own_frozen_receipt_files']==165 and proof['receipts']['own_logical_source_ids']==160 and len(proof['receipts']['preserved_failure_receipts'])==5 and proof['receipts']['shared_successful_full_receipts']==160)
 reproduction=json.loads((T/'review/final-reproduction.json').read_text());ck('isolated_offline_original_semantics_and_final_report_reproduction',reproduction['status']=='pass' and reproduction['network_calls']==0 and reproduction['unchanged_native_csv_sha256']=='5ce44dc51ad9c096013e9b63fd2e73b9b723f34480b185312da5c2cd10bf848f')
 ck('coordinator_legal_geography_approval_not_claimed',current['coordinator_acceptance']==before['coordinator_acceptance'] and current['peer']['coordinator_acceptance'] is None and current['coverage']['current_geometry_or_2026_identity_approved'] is False)
 if not preseal:
  seal=json.loads((T/'final-seal.json').read_text());ck('review_finalseal_pins_and_no_reverse_manifest_cycle',seal['schema']=='va-turnout-citation-reciprocal-final-v2' and seal['original_witness_sha256']==sha((T/'pre-peer-witness.json').read_bytes()) and seal['reciprocal_proof_sha256']==sha((T/'review/reciprocal.json').read_bytes()) and seal['contract_sha256']==sha((T/'priority-set.json').read_bytes()) and 'asset-manifest' not in json.dumps(seal))
 return {'status':'pass','checks':checks,'details':detail,'source_core_comparisons':proof['comparison_count'],'scope_exclusions':proof['scope'],'representation_distinctions_count':len(proof['representation_distinctions']),'prior_validator_limitation':'Original external citation mangling was not detected by pre-repair validation; exact history and real production regression retained.'}
