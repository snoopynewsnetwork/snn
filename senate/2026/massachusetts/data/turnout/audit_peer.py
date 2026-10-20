#!/usr/bin/env python3
"""Bounded reciprocal QA against exact frozen actual-final baseline bodies.

No mutable peer files, coordinator diagnostics, new sources or scenario maths are
inputs. Turnout original-first counts/order are the independent comparison side.
"""
import collections,csv,gzip,hashlib,io,json
from pathlib import Path
D=Path(__file__).resolve().parent;S=D.parent.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
class Capture:
    def __init__(self,path):
        self.path=path;self.body=path.read_bytes();self.manifest=json.loads(self.body);self.entries={e['original_path']:e for e in self.manifest['entries']}
    def get(self,name):
        e=self.entries[name]
        if 'frozen_path'in e:
            z=(S/e['frozen_path']).read_bytes();assert sha(z)==e['stored_sha256']and len(z)==e['stored_bytes'];b=gzip.decompress(z)
        else:b=(S/e['immutable_reference']).read_bytes()
        assert sha(b)==e['sha256']and len(b)==e['bytes'];return b
    def verify(self):
        for n in self.entries:self.get(n)
        for e in self.manifest.get('immutable_reused_input_entities',[]):
            p=S/e.get('path','');b=p.read_bytes()
            if 'stored_sha256'in e:
                assert sha(b)==e['stored_sha256']and len(b)==e['stored_bytes'];raw=gzip.decompress(b);assert sha(raw)==e['raw_sha256']and len(raw)==e['raw_bytes']
            else:assert sha(b)==e['sha256']and len(b)==e['bytes']
    def json(self,n):return json.loads(self.get(n))
    def extract(self,n):return json.loads(gzip.decompress(self.get(n)))
    def csv(self,n):return list(csv.DictReader(io.StringIO(self.get(n).decode())))
def main(write_result=True):
    own=Capture(D/'peer-review-freeze/original-first-v1/snapshot-manifest.json');assert sha(own.body)=='707dcec048f01fa8d557087c142e0f50fce924b7ff089ea97a384d3d16860846'
    resume=Capture(D/'peer-review-freeze/reciprocal-resume-v1/snapshot-manifest.json')
    peer=Capture(D/'peer-review-freeze/baseline-final-v1/snapshot-manifest.json')
    assert peer.manifest['peer_asset_manifest_sha256']=='1121b89786ec0e5decaed86116d18f8e6aef7f28003f5224a976f742a2ce2c40'
    for c in [own,resume,peer]:c.verify()
    assert sha(peer.get('data/baselines/asset-manifest.json'))==peer.manifest['peer_asset_manifest_sha256']
    opins={p['id']:p for p in own.json('data/turnout/source/shared-originals.json')};ppins={p['id']:p for p in peer.json('data/baselines/source/shared-originals.json')['sources']}
    assert set(opins)==set(ppins)
    for sid,o in opins.items():
        p=ppins[sid]
        for f in ['raw_sha256','stored_sha256','bytes','url','status','final_url','retrieved_at_utc','headers']:assert o[f]==p[f],(sid,f)
    stats={};orders=[];contexts=positions=fields=0;by_native={};hierarchy=peer.json('data/baselines/native-hierarchy.json');controls=peer.json('data/baselines/controls.json')
    for tag in ['2024-senate','2020-senate','2022-governor','2024-president']:
        path='extract/'+tag+'-original-extraction.json.gz';a=own.extract('data/turnout/'+path);b=peer.extract('data/baselines/'+path)
        assert a['all_original_csv_rows']==b['original_rows'];assert a['header_rows']['municipal']==b['headers']and a['header_rows']['precinct']==b['source_native_headers']
        assert a['columns']==controls[tag]['columns']and a['party_row_literal']==controls[tag]['parties_ragged']
        assert [(r['raw_text'],r['literal_party_display'])for r in a['html_candidate_cards']]==[(r['raw_text'],r['html_party'])for r in b['candidates_html']]
        assert a['state_control']==controls[tag]['state_values']and a['html_county_sum_minus_state_footer']==controls[tag]['html_county_minus_csv']
        assert a['named_source_votes']==controls[tag]['named_candidate_total']and a['named_plus_AllOthers_votes']==controls[tag]['reported_including_generic']
        footer=next(r['cells']for r in a['html_source_table_rows']if 'total'in r['attributes'].get('class','').split());assert footer==b['html_footer']
        county=[r['cells']for r in a['html_source_table_rows']if 'm_item'in r['attributes'].get('class','').split()];assert county==[r['raw']for r in b['html_county_rows']]
        for oscope,pscope in [('municipal','municipal'),('native','precinct')]:
            objs=a['municipalities'if oscope=='municipal'else 'native_contexts'];other=b['objects'][pscope];assert len(objs)==len(other)
            for x,y in zip(objs,other):
                projection=dict(source_id=x['source_id'],record_ordinal=x['csv_record_ordinal'],key=x['native_key'],city_town=x['literal_tuple'][0],ward=x['literal_tuple'][1],pct=x['literal_tuple'][2],raw_row=x['raw_row'],values=x['values'],method=x['method'],numeric_unit_id=x['numeric_native_id'],registration=x['registration'],overvotes=x['overvotes'],undervotes=x['undervotes'])
                assert projection==y,(tag,oscope,x['native_key']);contexts+=1;fields+=len(x['values'])
                if oscope=='native':by_native[(tag,x['native_key'])]=(x,a['columns'])
            raw=a['all_original_csv_rows'][pscope][-1];state=b['state'][pscope]
            assert state==dict(source_id=objs[0]['source_id'],record_ordinal=len(a['all_original_csv_rows'][pscope]),key=json.dumps(raw[:3],separators=(',',':')),city_town=raw[0],ward=raw[1],pct=raw[2],raw_row=raw,values=a['state_control'],method=None,numeric_unit_id=None,registration=None,overvotes=None,undervotes=None)
        aps=own.extract('data/turnout/extract/'+tag+'-numeric-positions.json.gz')
        mapped=[dict(scope='municipal'if x['source_id'].endswith('municipal-csv')else 'precinct',record_ordinal=x['csv_record_ordinal'],column_ordinal=x['csv_column_ordinal'],header=x['literal_column'],raw=x['raw_value'],value=x['value'])for x in aps]
        # Both preserve positions exactly, but peer puts each scope footer
        # beside that scope while turnout appends the two footers at the end.
        poskey=lambda x:(x['scope'],x['record_ordinal'],x['column_ordinal'])
        assert len({poskey(x)for x in mapped})==len(mapped)==len(b['numeric_positions'])
        assert sorted(mapped,key=poskey)==sorted(b['numeric_positions'],key=poskey);positions+=len(mapped)
        assert b['coverage']==dict(voting_method='not printed; null, no Election Day/early/mail allocation',native_type='literal source context, not approved physical precinct or November2026 ID',generic_writeins='All Others unallocated; eligibility/named scope unknown',registration='not printed in contest exports',blank_semantics='source Blanks; no separately published under/over split in these exports')
        assert a['method_columns_available']is False
        h=hierarchy[tag];assert h['native_count']==a['native_context_count']and h['current2026_approved']is False
        assert len(h['parents'])==351
        for parent,sourceparent in zip(h['parents'],a['municipalities']):
            town=sourceparent['literal_tuple'][0];children=[x for x in a['native_contexts']if x['literal_tuple'][0]==town]
            assert parent['municipal_key']==sourceparent['native_key']and parent['source_record_ordinal']==sourceparent['csv_record_ordinal']and parent['city_town']==town
            assert parent['native_keys']==[x['native_key']for x in children]and parent['numeric_unit_id']is None
            wards=collections.OrderedDict()
            for x in children:wards.setdefault(x['literal_tuple'][1],[]).append(x['native_key'])
            assert parent['ward_groups']==[dict(ward_literal=w,native_keys=keys,source_ward_total_row=False)for w,keys in wards.items()]
            assert parent['source_empty_ward_pct_keys']==[x['native_key']for x in children if x['literal_tuple'][1:]==['','']]
            assert parent['separate_central_administrative_rows']=='not separately labeled in selected exports'
        for oscope,pscope in [('native','precinct'),('municipal','municipal')]:
            for ofield,pfield in [('named_source_votes','all_named'),('named_plus_AllOthers_votes','reported_generic'),('TotalVotesCast','ballots')]:
                op=f'data/turnout/orders/{tag}-{oscope}-{ofield}.csv';pp=f'data/baselines/orders/{tag}-{pscope}-{pfield}.csv';left=own.csv(op);right=peer.csv(pp);assert len(left)==len(right)
                denominator=sum(int(x['votes'])for x in left)
                for x,y in zip(left,right):
                    assert (x['rank'],x['native_key'],x['csv_record_ordinal'],x['votes'],x['cumulative_votes'],x['in_minimum80'])==(y['rank'],y['source_unit_key'],y['record_ordinal'],y['votes'],y['cumulative'],y['minimum80_member'])
                    assert json.loads(x['literal_tuple'])==[y['city_town'],y['ward'],y['pct']]
                    assert int(y['total'])==denominator
                orders.append(dict(own_order=op,peer_order=pp,rows=len(left),universe_mapping=f'{ofield} -> {pfield}',full_counts_literals_ordinals_cumulatives_min80=True))
        stats[tag]=dict(native_contexts=a['native_context_count'],municipal_parents=351,numeric_positions=len(mapped),source_position_array_presentation='Same complete unique scope/record/column objects; peer places each scope footer beside its scope, turnout appends both footers. Original array bodies retained without rewriting.',candidate_headers_parties_HTML_null_method_objects=True,all_parent_children_and_ward_arrays=True)
    baseline=peer.csv('data/county-baselines.csv');assert len(baseline)==len(by_native)==9351
    seen=set()
    for row in baseline:
        k=(row['contest'],row['source_unit_key']);assert k not in seen;seen.add(k);o,cols=by_native[k];vals=o['values'];named=dict(zip(cols[:-3],vals[:-3]))
        assert json.loads(row['candidate_values_json'])==named
        assert [row['city_town'],row['ward'],row['pct']]==o['literal_tuple']and int(row['record_ordinal'])==o['csv_record_ordinal']and row['source_id']==o['source_id']
        assert [int(row[f])for f in ['A_votes','B_votes','other_named_votes','All_Others','named_candidate_total','reported_generic_total','Blanks','Total_Votes_Cast','pair_total']]==[vals[0],vals[1],sum(vals[2:-3]),vals[-3],sum(vals[:-3]),sum(vals[:-2]),vals[-2],vals[-1],vals[0]+vals[1]]
        assert row['A']==cols[0]and row['B']==cols[1]and row['scope']=='precinct'and all(row[f]==''for f in ['method','numeric_unit_id','registration','undervotes','overvotes'])
    oc=own.json('data/turnout/priority-set.json');pc=peer.json('data/baselines/priority-set.json');primary=pc['precinct-named_pair'];s=oc['summary']
    assert primary['membership']==oc['ordered_priority_keys']and primary['total']==s['statewide_votes']and primary['minimum80_count']==s['minimum80_count']and primary['previous_cumulative']==s['preceding_votes']and primary['crossing_cumulative']==s['minimum80_votes']and primary['top15_cumulative']==s['top15_votes']and primary['accepted_by_coordinator']is False
    for p in oc['all_parent_child_maps']:
        h=next(x for x in hierarchy['2024-senate']['parents']if x['municipal_key']==p['municipal_key']);assert h['native_keys']==p['native_keys_source_order']
    reverse=peer.json('data/baselines/peer-audit/comparison.json');assert reverse['status']=='pass_independent_reciprocal_audit_of_immutable_actual_turnout_v1'and reverse['peer_snapshot_manifest_sha256']==sha(own.body)and reverse['exact_priority_agreement']is True
    # Current counts/order/CSV must still equal original-first, not merely peer.
    unchanged=[]
    for path,e in own.entries.items():
        if path=='data/county-turnout.csv'or path.startswith(('data/turnout/extract/','data/turnout/orders/')):
            assert (S/path).read_bytes()==own.get(path);unchanged.append(path)
    result=dict(status='pass_bounded_reciprocal_actual_final_baseline_capture',worker_actual_id='eb66a7f4-a730-4f4d-8382-35941613a2ff',peer_actual_id='41e0bf1a-4609-4a2a-b901-568567431a57',own_original_first_manifest_sha256=sha(own.body),own_resume_capture_sha256=sha(resume.body),peer_final_capture_manifest_sha256=sha(peer.body),peer_final_asset_manifest_sha256=peer.manifest['peer_asset_manifest_sha256'],frozen_peer_assets=len(peer.entries),frozen_peer_input_pins=len(peer.manifest['immutable_reused_input_entities']),common_original_receipts=len(opins),contests=stats,full_shared_objects=contexts,full_candidate_control_fields=fields,full_numeric_source_positions=positions,complete_orders=orders,baseline_CSV_native_rows=9351,primary_exact_agreement=True,all_351_primary_parent_child_maps_match=True,peer_reverse_audit_scope='Actual captured baseline attests to own original-first-v1 only, hash707dcec...; no later-current equality implied.',unchanged_original_first_count_order_assets=unchanged,scope_exclusions=['Eight baseline named_pair orders beyond the shared24 are separate universes, not aliases for all_named.','Baseline calculator/scenario outputs not audited by this turnout question.','Supplemental baseline browser registration observations (including347municipal rows) remain peer evidence, not own original reading.','No current/legal/geometry/feed/eligible-writein approval; coordinator acceptance false.'],coordinator_accepted=False,current_geometry_approved=False)
    if write_result:
        (D/'peer-audit').mkdir(exist_ok=True);(D/'peer-audit/comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['status','full_shared_objects','full_candidate_control_fields','full_numeric_source_positions','baseline_CSV_native_rows','primary_exact_agreement']}));print('full shared orders',len(orders))
    return result
if __name__=='__main__':main()
