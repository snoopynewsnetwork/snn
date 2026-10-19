"""Compare all directly read BP009 source rows; retain unknown candidate pools."""
from pathlib import Path
import gzip,hashlib,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/union2024-split-style-original'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 p=DATA/'coordinator-union2024-split-style-original-readings.json';own=json.loads(p.read_bytes());assert pin(p)['sha256']=='b353ceb6b5bcd7c0db9f9894b03055165db86ca2b06344f04dd8891afbba824f';peer=DATA/'baselines/union-split-ballot-style-readings.json';frozen=QA/'baseline-split-style-readings.json.gz'
 if frozen.exists():b=gzip.decompress(frozen.read_bytes())
 else:b=peer.read_bytes();frozen.write_bytes(gzip.compress(b,mtime=0))
 assert len(b)==75354 and sha(b)=='1020476ea284cc6756e02d61e6988f823dd76053047035653890a2928bbc0517';j=json.loads(b);assert j['raw_sha256']==own['raw_original_sha256']and j['source_id']==own['source_id'];assert j['printed_grand_TOTAL_voters']==own['printed_Grand_Total']==17058
 assert len(j['parents'])==len(own['parents'])==20 and len(j['split_rows'])==len(own['split_rows'])==58
 for o,r in zip(own['parents'],j['parents']):assert(o['actual_PDFpage'],o['precinct_code_literal'],o['precinct_name_literal'],o['printed_parent_Total'],o['split_rows'])==(r['PDFpage'],r['precinct_code_literal'],r['precinct_name_literal'],r['printed_TOTAL_voters'],r['split_rows'])
 zeros=0
 for o,r in zip(own['split_rows'],j['split_rows']):
  assert(o['actual_PDFpage'],o['parent_precinct_code_literal'],o['parent_precinct_name_literal'],o['physical_split_row_within_parent'],o['split_literal'],o['ballot_style_literal'],o['party_literal'],o['printed_Total_Voters'])==(r['PDFpage'],r['precinct_code_literal'],r['precinct_name_literal'],r['split_row_within_printed_parent'],r['split_literal'],r['ballot_style_literal'],r['party_literal'],r['total_voters'])
  assert r['source_raw_sha256']==own['raw_original_sha256']and r['source_id']==own['source_id']and r['role']=='source_split_ballot_style_administrative_row';assert r['Senate_candidate_votes']is None and r['presidential_candidate_votes']is None and r['pair_weight']is None and r['selected_only_break_even']is None;assert r['tie_target_status']==r['Aplus1_target_status']=='unknown_candidate_allocation';zeros+=r['total_voters']==0
 assert zeros==3 and j['candidate_allocation_available']is False and j['printed_total_voters_definition']is None and j['profile_registration_separate']==17084 and j['split_total_minus_profile_registration']==-26
 out=dict(status='pass_bounded_fresh_original_all58_UnionBP009_split_style_rows_and_unknown_targets',coordinator_original_readings=pin(p),frozen_producer_ledger=dict(original_path=str(peer.relative_to(ROOT)),original_bytes=len(b),original_sha256=sha(b),lossless_copy=pin(frozen)),complete_original_pages_freshly_read=3,split_rows=58,parent_TOTALs=20,printed_Grand_Total=17058,printed_zero_TotalVoters_rows=3,all_Party_cells_unprinted_null=True,all_candidate_pools_weights_and_selected_targets_unknown=True,printed_TotalVoters_minus_separate_profile_registration=-26,qualification='All58split/code/style/TotalVoters/blankParty rows and20printed parentTOTALs agree the coordinator complete-original transcript after source reading. Three explicit0TotalVoters rows remain source observations with unknown candidate allocation; they do not become candidate0or no-positive-pool cases. LiteralNAS stays uppercaseS, sourcecodes and parent group context are not current geographic IDs. TotalVoters17058 and separately printed registration17084 lack a proven matched-population definition; no26voter allocation/cause or candidate split inferred. Administrative view remains nonadditive to preferredSEMS/vendorprofiles and all candidate win targets unavailable. No native887/currentgeography or full-method approval.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 target=DATA/'coordinator-union2024-split-style-review.json';raw=(json.dumps(out,indent=2)+'\n').encode()
 if target.exists():assert target.read_bytes()==raw
 else:target.write_bytes(raw)
 print(json.dumps(pin(target)))
if __name__=='__main__':main()
