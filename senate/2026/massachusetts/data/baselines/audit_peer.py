#!/usr/bin/env python3
"""Compare own original extraction to immutable actual turnout original-first v1."""
import argparse,csv,gzip,io,json
from pathlib import Path
from extract_originals import ROOT,TAGS,sha,dump
STATE=ROOT.parent.parent
def main(frozen=False):
    manifest=ROOT/'peer-audit/turnout-original-first-snapshot-manifest.json' if frozen else STATE/'data/turnout/peer-review-freeze/original-first-v1/snapshot-manifest.json'
    raw=manifest.read_bytes(); frozen=json.loads(raw); target=ROOT/'peer-audit';target.mkdir(exist_ok=True)
    (target/'turnout-original-first-snapshot-manifest.json').write_bytes(raw)
    entries={r['original_path']:r for r in frozen['entries']}; compared=[]
    def peer(path):
        e=entries[path];owned=target/(path.replace('/','__')+'.gz');z=(owned if frozen else STATE/e['frozen_path']).read_bytes();assert sha(z)==e['stored_sha256']
        b=gzip.decompress(z);assert sha(b)==e['sha256'] and len(b)==e['bytes']
        out=target/(path.replace('/','__')+'.gz');out.write_bytes(z)
        compared.append(dict(original_path=path,frozen_path=e['frozen_path'],sha256=sha(b),bytes=len(b),owned_snapshot=str(out.relative_to(ROOT))))
        return b
    counts={}; orders=[]
    for tag in TAGS:
        own=json.loads(gzip.decompress((ROOT/'extract'/f'{tag}-original-extraction.json.gz').read_bytes()))
        other=json.loads(gzip.decompress(peer(f'data/turnout/extract/{tag}-original-extraction.json.gz')))
        assert own['original_rows']==other['all_original_csv_rows']
        assert own['controls']['state_values']==other['state_control']
        assert own['controls']['html_county_minus_csv']==other['html_county_sum_minus_state_footer']
        comparisons=0
        for scope,pfield in [('precinct','native_contexts'),('municipal','municipalities')]:
            a=own['objects'][scope];b=other[pfield];assert len(a)==len(b)
            for x,y in zip(a,b):
                assert x['key']==y['native_key'] and x['record_ordinal']==y['csv_record_ordinal']
                assert x['raw_row']==y['raw_row'] and x['values']==y['values']
                for field in ['method','registration','undervotes','overvotes']:assert x[field]==y[field]
                assert x['numeric_unit_id']==y['numeric_native_id']; comparisons+=len(x['values'])
            for basis,pbasis in [('all_named','named_source_votes'),('reported_generic','named_plus_AllOthers_votes'),('ballots','TotalVotesCast')]:
                q=f'{tag}-{scope}-{basis}.csv';p=f'{tag}-'+('native' if scope=='precinct' else scope)+f'-{pbasis}.csv'
                a=list(csv.DictReader((ROOT/'orders'/q).open()))
                b=list(csv.DictReader(io.StringIO(peer('data/turnout/orders/'+p).decode())))
                assert len(a)==len(b)
                for x,y in zip(a,b):
                    assert x['source_unit_key']==y['native_key']
                    for of,pf in [('rank','rank'),('record_ordinal','csv_record_ordinal'),('votes','votes'),('cumulative','cumulative_votes')]:assert x[of]==y[pf]
                    assert (x['minimum80_member']=='True')==(y['in_minimum80']=='True')
                orders.append(dict(own=q,peer=p,rows=len(a),full_order_counts_cumulative_min80_match=True))
        # Candidate card text/party display retained independently, not normalized into a coalition.
        assert [c['raw_text'] for c in other['html_candidate_cards']]==[c['raw_text'] for c in own['candidates_html']]
        positions=json.loads(gzip.decompress(peer(f'data/turnout/extract/{tag}-numeric-positions.json.gz')))
        a={(x['scope'],x['record_ordinal'],x['column_ordinal']):(x['header'],x['raw'],x['value']) for x in own['numeric_positions']}
        b={('precinct' if p['source_id'].endswith('precinct-csv') else 'municipal',p['csv_record_ordinal'],p['csv_column_ordinal']):(p['literal_column'],p['raw_value'],p['value']) for p in positions}
        # Both state footers retained. Scopes distinguish overlapping controls.
        assert a==b
        counts[tag]=dict(native=len(own['objects']['precinct']),municipal=351,candidate_control_fields_compared=comparisons,numeric_source_positions=len(a),raw_headers_rows_candidate_metadata_null_method_fields_match=True)
    native=list(csv.DictReader((ROOT/'orders/2024-senate-precinct-named_pair.csv').open()))
    rows=list(csv.DictReader(io.StringIO(peer('data/county-turnout.csv').decode())))
    own=json.loads(gzip.decompress((ROOT/'extract/2024-senate-original-extraction.json.gz').read_bytes()))
    by={x['key']:x for x in own['objects']['precinct']}
    for x,y in zip(native,rows):
        r=by[x['source_unit_key']]
        assert x['source_unit_key']==y['native_key'] and x['rank']==y['rank'] and x['votes']==y['named_source_votes']
        assert [int(y[k]) for k in ['Warren','Deaton','AllOthers','Blanks','source_TotalVotesCast']]==r['values']
    contract=json.loads(peer('data/turnout/priority-set.json'))
    assert contract['ordered_priority_keys']==[r['source_unit_key'] for r in native if r['minimum80_member']=='True']
    dump(target/'comparison.json',dict(status='pass_independent_reciprocal_audit_of_immutable_actual_turnout_v1',own_pre_peer_freeze_sha256=sha((ROOT/'source/original-first-freeze.json').read_bytes()),peer_snapshot_manifest_sha256=sha(raw),peer_worker='eb66a7f4-a730-4f4d-8382-35941613a2ff',contest_checks=counts,complete_orders=orders,compared_exact_bodies=compared,exact_priority_agreement=True,current_geometry_approval=False,coordinator_acceptance=False,qualification='Frozen original-first-v1 bodies only. No later metadata/body changes treated as compared. Historical agreement does not approve current/legal/native write-in scope or live feed.'))
    print(json.dumps({'status':'pass','orders':len(orders),'contests':counts,'bodies':len(compared)}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--frozen',action='store_true');main(ap.parse_args().frozen)
