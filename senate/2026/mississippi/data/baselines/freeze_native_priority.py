"""Freeze a coherent independently checked887-native proposal, no acceptance.

Existing immutable witness is verified, never overwritten. Changes require a
new explicitly named version, not repair of a frozen peer/coordinator artifact.
"""
import datetime,gzip,json
from sources import OUT,BASE,sha,save
def main():
    root=OUT/'source/native-priority-v1';root.mkdir(exist_ok=True);dest=root/'snapshot.json';files=['native-priority-contract.json','native-source-orders.json','native-full-order.csv','native-order-peer-reconciliation.json']
    if dest.exists():
        x=json.loads(dest.read_text())
        for p in x['pins']:
            raw=(BASE/p['original_path']).read_bytes();stored=(BASE/p['frozen_path']).read_bytes();assert sha(raw)==p['original_sha256'] and len(raw)==p['original_bytes'];assert sha(stored)==p['stored_sha256'] and gzip.decompress(stored)==raw
        print('Existing immutablev1 native887proposal pins verified, unchanged');return
    contract=json.loads((OUT/files[0]).read_text());order=json.loads((OUT/files[1]).read_text());recon=json.loads((OUT/files[3]).read_text());p=order['preferred82_view'];assert p['count']==1736 and p['minimum80']['count']==887;assert contract['ordered_native_keys']==[r['key'] for r in p['full_descending_order']];assert contract['ordered_priority_native_keys']==contract['ordered_native_keys'][:887];assert contract['ordered_nonpriority_native_keys']==contract['ordered_native_keys'][887:];assert recon['compared_preferred_native_units']==1736 and recon['exact_order_key_candidate_parent_rank_cumulative_disagreements']==0;assert not contract['coordinator_accepted'] and not contract['current2026_geography_approved'];assert set(contract['parent_all_native_keys'])==set(contract['parent_priority_native_keys']) and len(contract['parent_all_native_keys'])==82;assert sum(map(len,contract['parent_all_native_keys'].values()))==1736;assert sum(map(len,contract['parent_priority_native_keys'].values()))==887
    pins=[]
    for f in files:
        src=OUT/f;raw=src.read_bytes();packed=gzip.compress(raw,mtime=0);copy=root/(f+'.gz');assert not copy.exists();assert len(packed)<40000000;copy.write_bytes(packed);pins.append(dict(original_path=str(src.relative_to(BASE)),original_bytes=len(raw),original_sha256=sha(raw),frozen_path=str(copy.relative_to(BASE)),stored_bytes=len(packed),stored_sha256=sha(packed),reconstruction='Exact ordered original bytes by lossless gzip decompression; no normalization'))
    save(dest,dict(status='independent_worker_887_native_proposal_pending_coordinator_acceptance',snapshot_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),primary_geography_scope='1736 disjoint preferred historical2024 SEMS native units, all82counties; exact minimum80 sorted prefix887. County41 is sensitivity only.',source_native_named_denominator=1215400,certified_county_named_denominator=1215401,unallocated_primary_difference={'county':'Tunica','candidate':'Ty Pinkins','native_minus_certified':-1,'placement':None},native_top15_votes=60019,minimum80=p['minimum80'],nonpriority_count=849,nonpriority_source_votes=242744,working_peer_optional_ID_addition_scope='43 source-position optional ID extractions retained separately from unchanged frozen84 metadata in reconciliation; no byte-for-byte old-ID agreement or current-ID assertion',pins=pins,input_native_ledger_path=contract['input_ledger_path'],input_native_ledger_sha256=contract['input_ledger_sha256'],coordinator_accepted=False,full_original_field_method_native_history_gate=False,current2026_geography_approved=False));print('Frozen coherentv1:all1736keys,887priority/849nonpriority,82parent-childlists,84sourceorders and independent reciprocal proof')
if __name__=='__main__':main()
