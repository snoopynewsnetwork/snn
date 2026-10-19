"""Verify the immutable reciprocal38 witness and source-specific TOTAL audit."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def loadpins(snapshot):
 out={}
 for p in snapshot['pins']:
  z=(ROOT/p['stored_path']).read_bytes();assert len(z)==p['stored_bytes']and sha(z)==p['stored_sha256'];raw=gzip.decompress(z);assert len(raw)==p['original_bytes']and sha(raw)==p['original_sha256'];out[Path(p['original_path']).name]=raw
 return out
def save(name,a):
 p=DATA/name;b=(json.dumps(a,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable coordinator proof changed'
 else:p.write_bytes(b)
 return pin(p)
def main():
 ownpath=DATA/'baselines/source/native-2020-104views-v1/snapshot.json';ownraw=ownpath.read_bytes();assert sha(ownraw)=='1ff6e98fd18f70ec473ce0b5adac5e082f4f1900a7d03d6090e9181150a71568';own=json.loads(ownraw);items=loadpins(own)
 sp=DATA/'baselines/source/native-2020-peer-38views-v2/snapshot.json';rp=sp.with_name('reconciliation.json');assert pin(sp)['sha256']=='e345046b0ac94fef2923886e13c6131768757a1e02f870d55ea50bb865d85960';assert pin(rp)['sha256']=='1ea06a3e33a2c9a91e4b4570d95ec79fd3104c7853a7636de788b63d5f2fe3a1';snap=json.loads(sp.read_bytes());result=json.loads(rp.read_bytes());assert snap['own_original_witness']==pin(ownpath)==result['own_original_witness'];peer=loadpins(snap);assert len(peer)==76
 ownflat=list(csv.DictReader(io.StringIO(items['native-2020-additional-candidate-votes.csv'].decode())));key=lambda r:(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']);bykey={key(r):r for r in ownflat};assert len(bykey)==len(ownflat)
 assert snap['own_flat_input']==next(p for p in own['pins']if p['original_path'].endswith('native-2020-additional-candidate-votes.csv'))
 roots=[DATA/'coordinator-qa/turnout-2020-native-twelve',DATA/'coordinator-qa/turnout-2020-native-extensions'];frozenmatches=[];metadata_changes=[];counts=collections.Counter();sources={};seen=set()
 version65=DATA/'baselines/source/native-2020-65views-v1/snapshot.json';v65=json.loads(version65.read_bytes());assert pin(version65)['sha256']=='054551bc1b6ff204c8319843ac2046d0f58cf0fbd0e5730c61b035f68a9f0f02';v65flat=next(p['original_sha256']for p in v65['pins']if p['original_path'].endswith('native-2020-additional-candidate-votes.csv'))
 for filename,raw in peer.items():
  matches=[p/(filename+'.gz')for p in roots if(p/(filename+'.gz')).exists()];assert matches,filename
  old=gzip.decompress(matches[0].read_bytes());assert all(gzip.decompress(p.read_bytes())==old for p in matches)
  match=dict(peer_original_derivative=filename,previous_coordinator_lossless_copy=pin(matches[0]),previous_original_bytes=len(old),previous_original_sha256=sha(old),new_frozen_original_bytes=len(raw),new_frozen_original_sha256=sha(raw),exact_body_identity=old==raw)
  if old!=raw:
   assert filename.endswith('.json');a=json.loads(old);b=json.loads(raw);keys={k for k in a.keys()|b.keys()if a.get(k)!=b.get(k)};assert keys<={'peer_file_sha256','accepted_source_literal_label_differences','scope','peer_snapshot_sha256'}
   assert {k:v for k,v in a.items()if k not in keys}=={k:v for k,v in b.items()if k not in keys}
   if filename=='2020-native-alcorn-original-readings.json':assert keys=={'peer_file_sha256'}and b['peer_file_sha256']==snap['own_flat_input']['original_sha256']
   else:
    assert b['peer_snapshot_sha256']==pin(version65)['sha256']and b['accepted_source_literal_label_differences']==[] and 'immutable 65views-v1 peer' in b['scope']
    if 'peer_file_sha256'in keys:assert b['peer_file_sha256']==v65flat
   match['later_peer_comparison_metadata_differences']=[dict(field=k,earlier_present=k in a,earlier_value=a.get(k),new_present=k in b,new_value=b.get(k))for k in sorted(keys)];metadata_changes.append(match)
  frozenmatches.append(match)
  if not filename.endswith('.csv'):continue
  for r in csv.DictReader(io.StringIO(raw.decode())):
   k=key(r);assert k not in seen;seen.add(k);a=bykey[k];assert r['source_raw_sha256']==a['source_raw_sha256'];assert r['native_source_key']==a['source_key'];assert r['votes']==a['votes']and r['role']==a['role'];assert ' '.join(r.get('literal_native_label',r.get('label_literal')).split())==' '.join(a['literal_native_label'].split());counts[a['role']]+=1;sources[k[0]]=a['source_raw_sha256']
 assert len(seen)==result['compared_positions']==2277 and len(sources)==result['source_publications']==38 and len(metadata_changes)==17
 assert dict(counts)==result['candidate_positions_by_role']==dict(source_native_reporting_constituent=1554,source_TOTAL=114,unused_template_column=609)
 assert result['native_constituents']==518 and not result['value_role_differences']and not result['label_differences_after_whitespace_only'];assert sources==result['source_raw_hashes']
 rasterpairs=[]
 for r in result['source_page_render_pairs']:
  a=pin(ROOT/r['own_raster']);b=pin(ROOT/r['peer_raster']);assert a['sha256']==r['own_raster_sha256']and b['sha256']==r['peer_raster_sha256'];assert r['same_raster_bytes']==(a['sha256']==b['sha256']);rasterpairs.append(dict(source_id=r['source_id'],actual_PDFpage=r['PDFpage'],baseline=a,turnout=b,same_bytes=r['same_raster_bytes']))
 peerproof=save('coordinator-historical-native-2020-peer38v2-review.json',dict(status='pass_bounded_immutable_reciprocal38_fields_with_explicit_comparison_metadata_changes',snapshot=pin(sp),reciprocal_result=pin(rp),baseline_original104_witness=pin(ownpath),frozen_derivative_bodies=len(peer),body_comparisons_to_prior_coordinator_original_replay_copies=frozenmatches,exact_body_matches=59,later_metadata_only_JSON_changes=metadata_changes,source_publications=38,source_native_observations_across_versions=518,compared_candidate_positions=2277,candidate_positions_by_role=dict(counts),source_original_hashes=sources,original_raster_pairs=rasterpairs,qualification='All38 CSVs and21 JSONs exactly match earlier coordinator-frozen original-reading bodies. Seventeen JSONs differ ONLY in explicitly recorded later peer-comparison declarations: peer file hash, added immutable65 reference, empty label-difference metadata and comparison scope wording. Every original row/value/label/source/raster/physical hint is unchanged. Earlier declarations/copies remain intact; new hashes are not relabelled as initial transcription-time references. Initial strict byte-identity validation rejected the first such difference before publishing a proof. Recomputed source hash/key/page/physical ordinal/value/role/whitespace-only header comparisons match the independent immutable104 original ledger. Both raster hashes survive without equal geometry, parsed IDs, missing parties, source-vintage/current identity approval. This is38 publications, not complete104 independent replay or whole historical-method acceptance.',separate_worker_metadata_update_history_requested=True,formal_native887_dispatch_accepted=False,historical_native_independent_complete=False,current_geography_approved=False))
 original_path=DATA/'baselines/native-2020-physical-TOTAL-audit.json';copy=DATA/'coordinator-qa/native-2020-physical-TOTAL-audit.json.gz'
 if copy.exists():auditraw=gzip.decompress(copy.read_bytes())
 else:auditraw=original_path.read_bytes();assert sha(auditraw)=='3fc0b46011e06b099c04971cfaf702924f005cdef93f0caba1d322cdfffedf93';copy.write_bytes(gzip.compress(auditraw,mtime=0))
 assert sha(auditraw)=='3fc0b46011e06b099c04971cfaf702924f005cdef93f0caba1d322cdfffedf93';audit=json.loads(auditraw)
 oldpath=DATA/'coordinator-qa/county-2020-publication-controls.json.gz';old=json.loads(gzip.decompress(oldpath.read_bytes()));old_byid={r['source_id']:r for r in old['readings']};ledger_sources={}
 for name in ['coahoma-2020-amendment-readings.json','native-2020-additional-readings.json']:
  for s in json.loads(items[name])['sources']:assert s['source_id']not in ledger_sources;ledger_sources[s['source_id']]=s
 assert len(ledger_sources)==len(audit['readings'])==len(old_byid)==104 and audit['complete_all104']and audit['selected82_complete'];accepted=unaccepted=proposed=0;proposed_diffs=[];physical=[];selected_sums=collections.Counter()
 for r in audit['readings']:
  sid=r['source_id'];s=ledger_sources[sid];prior=old_byid[sid];assert s['raw_sha256']==prior['raw_sha256']==r['raw_sha256'];found=[]
  for p in s['pages']:
   for col in p['columns']:
    if col['role']=='source_TOTAL':found.append((p,col))
  assert len(found)==1;p,col=found[0];now=dict(PDFpage=p['page'],physical_column=col['source_column'],header_bounds=col['header_bounds']);assert now==r['actual_original_reviewed_TOTAL'];assert r['earlier_county_control_accepted_physical_column']==prior['source_column_accepted']and r['earlier_machine_proposed_column']==prior['source_column_proposed'];assert r['candidate_values']==prior['candidate_values']
  vals={f['candidate']:f['values'][p['columns'].index(col)]for f in p['fields']};assert vals==r['candidate_values']
  if prior['source_column_accepted']is not None:accepted+=1;assert r['earlier_accepted_column_agrees']and prior['source_column_accepted']==col['source_column']
  else:unaccepted+=1;assert prior['source_column_proposed']is not None
  if prior['source_column_proposed']is not None:
   proposed+=1;agrees=prior['source_column_proposed']==col['source_column'];assert r['earlier_proposal_agrees']==agrees
   if not agrees:proposed_diffs.append(dict(source_id=sid,earlier_machine_proposal=prior['source_column_proposed'],earlier_accepted_physical_column=prior['source_column_accepted'],proposal_had_no_accepted_replacement=prior['source_column_accepted']is None,new_original_physical_TOTAL=now,candidate_values_unchanged=vals))
  if r['selected_for82']:selected_sums.update(vals)
  physical.append(dict(source_id=sid,raw_sha256=s['raw_sha256'],actual_original_TOTAL=now,selected_for82=r['selected_for82']))
 assert accepted==51 and unaccepted==53 and proposed==55 and len(proposed_diffs)==11
 assert sum(r['proposal_had_no_accepted_replacement']for r in proposed_diffs)==10
 superseded=[r for r in proposed_diffs if not r['proposal_had_no_accepted_replacement']];assert len(superseded)==1 and superseded[0]['source_id']=='sos-2020-county-coahoma'and superseded[0]['earlier_accepted_physical_column']==8 and superseded[0]['earlier_machine_proposal']==7
 assert dict(selected_sums)==audit['selected82_native_candidate_sums']=={'Mike Espy':578691,'Cindy Hyde-Smith':709511,'Jimmy L. Edwards':23152}
 totalproof=save('coordinator-2020-native-physical-TOTAL-review.json',dict(status='pass_all104_source_bound_native_TOTAL_locators_with_prior_history_retained',original_audit_path=str(original_path.relative_to(ROOT)),original_audit_bytes=len(auditraw),original_audit_sha256=sha(auditraw),lossless_original_audit_copy=pin(copy),prior_complete_county_control_ledger_copy=pin(oldpath),immutable_native104_witness=pin(ownpath),source_publications=104,original_physical_TOTAL_positions=physical,earlier_accepted51_all_agree=True,earlier_unaccepted_source_locators=53,all_retained_nonnull_machine_proposals=55,all_machine_proposal_differences=proposed_diffs,unaccepted_locator_proposal_differences=10,superseded_proposal_difference_on_already_accepted_Coahoma=1,selected82_candidate_sums=dict(selected_sums),qualification='New physical positions exactly match each immutable original native source grid, raw hash and candidate TOTAL vector. All earlier51 accepted columns agree. Ten of53 previously unaccepted locators have differing machine proposals; a further retained old Coahoma original proposal7 was already superseded by accepted8, which agrees with the new physical audit. There are55 nonnull proposals in all, including both Coahoma records with accepted replacements; eleven total proposal differences are not eleven still-unaccepted source locators. The full earlier ledger survives losslessly without mutating proposals or candidate counts. Bounds remain reading evidence, not certified numeric polygons or geographic IDs. This source-metadata review is not a fresh coordinator glyph reread of all104 grids or full independent historical-method/current identity acceptance.',formal_native887_dispatch_accepted=False,current_geography_approved=False))
 print(json.dumps(dict(reciprocal38=peerproof,physical_TOTAL104=totalproof,all_machine_proposal_differences=11,still_unaccepted_proposal_differences=10)))
if __name__=='__main__':main()
