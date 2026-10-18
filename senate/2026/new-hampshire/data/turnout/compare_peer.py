#!/usr/bin/env python3
"""Reciprocal comparison with the actual independently extracting peer.

Peer paths are strictly read-only. This does not alter the frozen contract.
Only the explicit schema alias ballots_cast -> ballots_total is applied.
"""
import collections
import csv
import gzip
import hashlib
import json
import pathlib

ROOT=pathlib.Path(__file__).resolve().parent
STATE=ROOT.parent.parent
PEER=STATE/'data/baselines'


def sha(b):return hashlib.sha256(b).hexdigest()
def jl(p):return [json.loads(x)for x in gzip.decompress(p.read_bytes()).splitlines()]
def field_alias(d):return {('ballots_total'if k=='ballots_cast'else k):v for k,v in d.items()}
def locator(d):
    if 'sheet'in d:return dict(sheet=d['sheet'],source_row=d['source_row'],label_column=d.get('label_column',d.get('source_column_start','A')))
    return dict(page=d['page'],line=d['line'])


def main():
    peer_files=['data/county-baselines.csv','data/baselines/native-fields.jsonl.gz','data/baselines/peer-reconciliation.json','data/baselines/priority.csv','data/baselines/priority-set.json','data/baselines/source/references.json','data/baselines/county-controls.json','data/baselines/reconciliation.json','data/baselines/state-baselines.json','data/baselines/source/controls.json']
    peer_assets=[dict(path=s,bytes=(STATE/s).stat().st_size,sha256=sha((STATE/s).read_bytes()))for s in peer_files]
    q=json.loads((ROOT/'priority-set.json').read_text());pq=json.loads((PEER/'priority-set.json').read_text())
    peerrows=jl(PEER/'native-fields.jsonl.gz')
    groups=collections.defaultdict(list)
    for r in peerrows:groups[r['source_id']].append(r)
    assert set(groups)=={r['source_id']for r in q['source_native_coverage']}
    mismatches=[];checks=[];fieldchecks=0;rawchecks=0;typechecks=0;poschecks=0
    for coverage in q['source_native_coverage']:
        sid=coverage['source_id'];ours=jl(ROOT/coverage['path']);peers=groups[sid]
        def index(rows):
            out={(r['county'],r['native_label']):r for r in rows};assert len(out)==len(rows)==320;return out
        own=index(ours);other=index(peers)
        if set(own)!=set(other):mismatches.append(dict(source_id=sid,type='native_literal_roster',only_own=sorted(set(own)-set(other)),only_peer=sorted(set(other)-set(own))))
        for key in own.keys()&other.keys():
            x,y=own[key],other[key]
            for label,a,b in [('fields',x['fields'],field_alias(y['fields'])),('raw_fields',x['raw_fields'],field_alias(y['raw_fields'])),('source_locator',locator(x['source_locator']),locator(y['source_locator']))]:
                if a!=b:mismatches.append(dict(source_id=sid,county=key[0],native_label=key[1],type=label,own=a,peer=b))
            fieldchecks+=len(x['fields']);rawchecks+=len(x['raw_fields']);poschecks+=1
            if 'cell_types'in x and 'cell_types'in y:
                xt=dict(zip(x['fields'],x['cell_types']));yt=field_alias(y['cell_types'])
                if xt!=yt:mismatches.append(dict(source_id=sid,county=key[0],native_label=key[1],type='BIFF_cell_types',own=xt,peer=yt))
                typechecks+=len(xt)
        checks.append(dict(source_id=sid,own_rows=len(own),peer_rows=len(other),fields_and_raw_values_and_source_positions_equal=not any(m['source_id']==sid for m in mismatches)))
    oc=list(csv.DictReader((ROOT.parent/'county-turnout.csv').open()));pc=list(csv.DictReader((PEER/'priority.csv').open()))
    assert len(oc)==len(pc)==320
    shared=sorted(set(oc[0])&set(pc[0]))
    for i,(x,y)in enumerate(zip(oc,pc),1):
        for k in shared:
            if x[k]!=y[k]:mismatches.append(dict(source_id='priority_csv',rank=i,field=k,own=x[k],peer=y[k]))
        if json.loads(y['source_locator_json'])!=dict(label_column='A',sheet=x['source_sheet'],source_row=int(x['source_row'])):mismatches.append(dict(source_id='priority_csv',rank=i,field='locator'))
    comparisons=[('full_ordered_keys',q['full_ordered_keys'],pq['full_ordered_keys']),('ordered_priority_keys',q['ordered_priority_keys'],pq['ordered_priority_keys']),('denominator',q['denominator'],pq['denominator']),('top15',q['top15']['votes'],pq['top15_votes']),('minimum80_count',q['minimum80']['count'],pq['minimum80_count']),('minimum80_votes',q['minimum80']['votes'],pq['minimum80_votes']),('preceding_votes',q['minimum80']['preceding_votes'],pq['preceding_votes']),('crossing_key',q['minimum80']['crossing_key'],pq['crossing_key'])]
    for label,x,y in comparisons:
        if x!=y:mismatches.append(dict(source_id='priority_contract',field=label,own=x,peer=y))
    owncontrols=json.loads((ROOT/'controls.json').read_text());ownaudit={r['source_id']:r for r in json.loads((ROOT/'reconciliation.json').read_text())}
    controlchecks=0;controlfields=0
    for r in json.loads((PEER/'source/controls.json').read_text()):
        sid=r['source_id'];scope=r['scope']
        x=next(x for x in owncontrols[sid]['footers']if x['county']==r['county'])if scope=='county_footer'else owncontrols[sid]['summary'][r['county']if scope=='county_summary'else 'TOTALS']
        for label,ownvalue,peervalue in [('fields',x['fields'],field_alias(r['fields'])),('raw_fields',x['raw_fields'],field_alias(r['raw_fields'])),('source_locator',locator(x['source_locator']),locator(r['source_locator']))]:
            if ownvalue!=peervalue:mismatches.append(dict(source_id=sid,county=r['county'],type='full_control_'+scope+'_'+label,own=ownvalue,peer=peervalue))
        controlchecks+=1;controlfields+=len(x['fields'])
    for r in json.loads((PEER/'county-controls.json').read_text()):
        x=next(x for x in owncontrols[r['source_id']]['footers']if x['county']==r['county'])
        if x['fields']!=r['fields']or locator(x['source_locator'])!=locator(r['source_locator']):mismatches.append(dict(source_id=r['source_id'],county=r['county'],type='county_footer'))
    for r in json.loads((PEER/'reconciliation.json').read_text()):
        x=ownaudit[r['source_id']]
        if field_alias(r['state_control'])!=x['state']or field_alias(r['numeric_native_sums'])!=x['native_numeric_sums']:mismatches.append(dict(source_id=r['source_id'],type='state_control_or_native_sum'))
    baseline=list(csv.DictReader((STATE/'data/county-baselines.csv').open()));assert len(baseline)==960
    for sid in ['sos-2024-president-archived-original','sos-archived-2022-ge-us-senator-5-xls','sos-2020-senate-archived-original']:
        own={(r['county'],r['native_label']):r for r in jl(ROOT/'native'/f'{sid}.jsonl.gz')}
        bs=[r for r in baseline if r['source_id']==sid];assert len(bs)==320
        for r in bs:
            x=own[(r['county'],r['native_label'])]
            if json.loads(r['raw_fields_json'])!=x['raw_fields']:mismatches.append(dict(source_id=sid,county=r['county'],native_label=r['native_label'],type='baseline_CSV_raw_fields'))
            for k,v in x['fields'].items():
                if r[k]!=(''if v is None else str(v)):mismatches.append(dict(source_id=sid,county=r['county'],native_label=r['native_label'],type='baseline_CSV_field',field=k))
    refs={r['id']:r for r in json.loads((PEER/'source/references.json').read_text())}
    ownrefs={r['source_id']:r for r in json.loads((ROOT/'source-inventory.json').read_text())}
    for sid in groups:
        r=refs[sid];b=(STATE/r['path']).read_bytes();assert sha(b)==r['stored_sha256']
        decoded=gzip.decompress(b)
        if r.get('metadata_path'):
            m=json.loads((STATE/r['metadata_path']).read_text())
            if m.get('http_content_decoding')=='gzip':decoded=gzip.decompress(decoded)
        if sha(decoded)!=ownrefs[sid]['original_sha256']:mismatches.append(dict(source_id=sid,type='decoded_original_hash'))
    evidence=dict(status='agreed_after_independent_full_comparison'if not mismatches else 'disagreements_require_resolution',peer_agent_id='d272caf4-db4f-4c84-8950-c5e0fabe93e7',agreement_claimed=not mismatches,
                  comparison_scope='Independent workers extracted original bytes separately. This reciprocal script reads stable peer outputs and never imports them into own count/build inputs or edits peer files.',
                  explicit_schema_aliases=dict(peer_ballots_cast='own ballots_total',peer_label_column='own source_column_start or default A'),
                  peer_assets=peer_assets,source_native_checks=checks,counts=dict(source_rosters=len(groups),native_records=len(peerrows),parsed_field_checks=fieldchecks,raw_field_checks=rawchecks,BIFF_type_checks=typechecks,position_checks=poschecks,control_records=controlchecks,control_fields=controlfields,priority_csv_shared_fields=len(shared),priority_csv_rows=320,baseline_csv_rows=960),
                  mismatches=mismatches,priority_arithmetic=dict(denominator=826189,top15_votes=185659,minimum80_count=143,minimum80_votes=662624,preceding_count=142,preceding_votes=660378,crossing_geography='Tilton',crossing_votes=2246),
                  coordinator_acceptance_authority='data/coordinator-priority-acceptance.json',coordinator_acceptance='External authority only; historical acceptance is not granted by this worker record.',geographic_approval='No current geometry, cross-year boundary equivalence, clerk authority or November 2026 precinct approval established.')
    # The coordinator acceptance pins the earlier reciprocal record. Preserve
    # its exact accepted bytes; put expanded control checks in a supplement.
    acceptance_path=STATE/'data/coordinator-priority-acceptance.json'
    if acceptance_path.exists():
        acceptance=json.loads(acceptance_path.read_text())
        accepted_peer=acceptance.get('peer_agreement',{})
        if accepted_peer:
            assert sha((STATE/accepted_peer['path']).read_bytes())==accepted_peer['sha256']
        destination=ROOT/'peer-control-agreement.json'
    else:destination=ROOT/'peer-agreement.json'
    destination.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(status=evidence['status'],counts=evidence['counts'],mismatch_count=len(mismatches))))
    if mismatches:raise SystemExit(1)


if __name__=='__main__':main()
