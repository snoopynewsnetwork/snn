"""Coordinator original-byte/source-object review of the frozen original-first turnout.

No producer parser/import/writer, numerical helper or peer output is used.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv, gzip, hashlib, io, json, re, tarfile, subprocess, tempfile, os, sys

S = Path(__file__).resolve().parents[1]
T = S / 'data/turnout'
# The source-core proof was measured on the immutable original-first phase.
# After the narrow citation/peer metadata repair, reproduce it against that
# exact complete captured phase, never reinterpret the newer current paths.
ORIGINAL_MANIFEST='6eafa8cc1a897b40075d8234681b832282d871490043b98ef3c7f5c878fd2b50'
if hashlib.sha256((T/'asset-manifest.json').read_bytes()).hexdigest()!=ORIGINAL_MANIFEST:
    h=T/'history/resume-citation-reciprocal/turnout-original-first.json'
    cap=json.loads(h.read_bytes());packed=(S/cap['archive_path']).read_bytes()
    assert hashlib.sha256(packed).hexdigest()==cap['archive_sha256'] and len(packed)==cap['archive_bytes']
    with tempfile.TemporaryDirectory(prefix='va-root-original-first-replay-') as tmp:
        state=Path(tmp)/'state';state.mkdir()
        with tarfile.open(fileobj=io.BytesIO(packed),mode='r:gz') as archive:
            for r in cap['bodies']:
                b=(S/r['reference_path']).read_bytes() if r['reference_path'] is not None else archive.extractfile(r['archive_name']).read()
                assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
                target=state/r['path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
        assert hashlib.sha256((state/'data/turnout/asset-manifest.json').read_bytes()).hexdigest()==ORIGINAL_MANIFEST
        for r in json.loads((state/'data/turnout/source/pinned-originals.json').read_bytes()):
            b=(S/r['body_path']).read_bytes();assert hashlib.sha256(b).hexdigest()==r['stored_sha256']
            target=state/r['body_path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
        finding=Path('data/coordinator-turnout-citation-finding/finding.json');target=state/finding;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((S/finding).read_bytes())
        script=state/'data/review_turnout_originals.py';script.write_bytes(Path(__file__).read_bytes())
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        proc=subprocess.run([sys.executable,'-B','-S',str(script)],cwd=state,env=env,capture_output=True,timeout=120)
        assert proc.returncode==0,(proc.stdout.decode(),proc.stderr.decode())
        proof=(state/'data/coordinator-turnout-original-review.json').read_bytes()
        assert proof==(S/'data/coordinator-turnout-original-review.json').read_bytes(),'original measured proof changed'
        print(json.dumps({'status':'pass_exact_immutable_original_first_phase_replay','current_source_or_producer_writes':False,'replayed_captured_bodies':len(cap['bodies']),'original_check_stdout':proc.stdout.decode().strip()}))
    raise SystemExit(0)
N = 0

def ck(value, label=''):
    global N
    N += 1
    assert value, (N, label)

def sha(b): return hashlib.sha256(b).hexdigest()

def load(path):
    p = T / path
    b = p.read_bytes()
    if p.suffix == '.gz': b = gzip.decompress(b)
    return [json.loads(v) for v in b.splitlines()] if '.jsonl' in p.name else json.loads(b)

def pointer(x, path):
    for k in path.split('/')[1:]:
        k = k.replace('~1', '/').replace('~0', '~')
        x = x[int(k)] if isinstance(x, list) else x[k]
    return x

manifest = load('asset-manifest.json')
assets = manifest['owned_assets']
actual = {str(p.relative_to(S)) for p in T.rglob('*') if p.is_file()} | {'turnout.md', 'data/county-turnout.csv'}
ck(len(assets) == len({r['path'] for r in assets}) == 388)
ck({r['path'] for r in assets} == actual - {'data/turnout/asset-manifest.json'})
for r in assets:
    b = (S/r['path']).read_bytes()
    ck(len(b) == r['bytes'] < 40000000 and sha(b) == r['sha256'], r['path'])
for p in T.rglob('*'):
    ck(not set(p.parts) & {'__pycache__', 'node_modules', '.venv', '.pytest_cache'})

w = load('pre-peer-witness.json')
archive = (T/w['archive_path']).read_bytes()
ck(len(archive) == w['archive_bytes'] and sha(archive) == w['archive_sha256'])
ck(w['peer_agent_id'] is None and w['peer_derivative_access_before_witness'] is False)
with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as z:
    ck(len(z.getmembers()) == len(w['bodies']) == 394)
    ck({m.name for m in z.getmembers()} == {r['archive_name'] for r in w['bodies']})
    for r in w['bodies']:
        b = z.extractfile(r['archive_name']).read()
        ck(len(b) == r['bytes'] and sha(b) == r['sha256'])
        ck(b == (S/r['original_path']).read_bytes())

legacy = {}
for r in load('source/pinned-originals.json'):
    ck(sha((T/r['receipt_path']).read_bytes()) == r['receipt_sha256'])
    b = (S/r['body_path']).read_bytes()
    ck(len(b) == r['stored_bytes'] and sha(b) == r['stored_sha256'])
    raw = gzip.decompress(b)
    ck(len(raw) == r['raw_bytes'] and sha(raw) == r['raw_sha256'])
    legacy[r['id']] = raw

raws = {}; request_objects = {}; statuses = Counter(); response_count = 0
for r in load('source/acquisition-index.json')['receipts']:
    packed = (T/r['receipt_path']).read_bytes()
    ck(len(packed) == r['receipt_bytes'] and sha(packed) == r['receipt_sha256'])
    obj = json.loads(packed)
    ck(obj == r['full_receipt'])
    ck(bool(obj['requested_url']) and 'parent_source' in obj)
    request_objects[obj['id']] = obj
    for h in obj['hops']:
        if 'status' in h: statuses[h['status']] += 1
        if not h.get('body_path'): continue
        b = (T/h['body_path']).read_bytes()
        ck(len(b) == h['stored_bytes'] and sha(b) == h['stored_sha256'])
        raw = gzip.decompress(b)
        ck(len(raw) == h['raw_bytes'] and sha(raw) == h['raw_sha256'])
        ck(h['retrieved_at_utc'] and isinstance(h['response_headers'], list) and all(len(pair)==2 for pair in h['response_headers']))
        raws[obj['id']] = raw; response_count += 1
ck(len(request_objects) == 160 and len(load('source/acquisition-index.json')['receipts']) == 165)

def parsed_records(raw, encoding):
    text = raw.decode(encoding)
    physical = text.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(text, newline=''))
    previous = 0; offset = len(raw) - len(text.encode(encoding.replace('-sig', '')))
    for ordinal, cells in enumerate(reader, 1):
        end = reader.line_num
        chunk = ''.join(physical[previous:end])
        body = chunk.encode(encoding.replace('-sig', ''))
        yield ordinal, previous+1, end, offset, offset+len(body), chunk, cells
        offset += len(body); previous = end
    ck(offset == len(raw), 'entire physical source consumed')

native_by_year = {}; locality_by_year = {}; summary = []; numeric_fields = original_records = 0
orders = load('sensitivity-orders.json')
for year, expected in [(2024,2669), (2020,2846), (2018,2825)]:
    e = load(f'extracts/{year}-contest.json')
    raw = legacy[f'elect-{year}-senate-linked-csv']
    html = legacy[f'elect-{year}-senate-historical']
    node = json.loads(re.search(rb'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html).group(1))
    ck(node == load(f'extracts/{year}-complete-next-data.json'))
    contest = node['props']['pageProps']['contest']
    extracted = load(f'extracts/{year}-all-original-rows.jsonl.gz')
    records = list(parsed_records(raw, 'utf-8-sig'))
    ck(len(records) == len(extracted) == e['row_count_including_headers'])
    header = records[0][-1]; party = records[1][-1]
    ck(header == e['header'] and party == e['party_header'])
    roles = {}; vote_cols = []
    for col in e['columns']:
        j = col['column_index']
        candidates = [x for x in contest['candidates'] if x['displayName'] == header[j]]
        ck(len(candidates) == 1 and candidates[0] == col['full_original_candidate_object'])
        ck(col['csv_label'] == header[j] and col['csv_party_label'] == party[j])
        roles[j] = col['role']
        if col['role'] in ['named_candidate','generic_writeins']: vote_cols.append(j)
    parent = None; native = []; parents = []; state = None
    for r, row in zip(records, extracted, strict=True):
        pos, first, last, start, end, literal, cells = r
        ck(row['source_record'] == pos and row['physical_line_start'] == first and row['physical_line_end'] == last)
        ck(row['byte_start'] == start and row['byte_end_exclusive'] == end and row['raw_row_utf8'] == literal)
        ck(row['cells'] == cells)
        original_records += 1
        for a,b in zip(row['cells'], cells, strict=True): ck(a == b)
        if pos <= 2: continue
        ck(row['level'] == cells[0] and row['label'] == cells[1] and row['key'] == f"va:{contest['id']}:csv-record:{pos:04d}")
        counts = {str(j):int(v) for j,v in enumerate(cells[2:],2)}
        ck(counts == row['counts'])
        for j in range(2,len(cells)): ck(row['counts'][str(j)] == int(cells[j])); numeric_fields += 1
        vector = {str(j):counts[str(j)] for j in vote_cols}
        ck(vector == row['candidate_votes'] and sum(vector.values()) == row['reported_candidate_writein_votes'])
        ck(sum(vector.values()) == counts[str(header.index('Total Votes Cast'))])
        ck(all(row[k] is None for k in ['ballots_cast','registered_voters','blank_votes','over_votes','named_valid_writein_allocation']))
        if cells[0] == 'Locality': parent = row; parents.append(row)
        elif cells[0] == 'State': state = row
        else:
            ck(parent is not None and row['parent_key'] == parent['key'] and row['parent_label'] == parent['label'])
            native.append(row)
    ck(len(native) == expected and len(parents) == 133 and len({r['label'] for r in parents}) == 133)
    ck(sum(r['label'].endswith(' City') for r in parents) == 38)
    for col in e['state_controls']:
        j = str(col['column_index'])
        ck(sum(r['counts'][j] for r in native) == col['native_sum'] == state['counts'][j] == col['csv_state'])
        ck(sum(r['counts'][j] for r in parents) == col['locality_sum'])
        obj = next(x for x in contest['candidates'] if x['displayName'] == col['label'])
        ck(obj['nVotes'] == col['html_nVotes'] == col['csv_state'] and obj['nVotesParty1'] == col['html_nVotesParty1'])
    for balance in e['locality_balances']:
        par = next(x for x in parents if x['key'] == balance['parent_key']); j = str(balance['column_index'])
        total = sum(x['counts'][j] for x in native if x['parent_key'] == par['key'])
        ck(total == balance['native_sum'] and par['counts'][j] == balance['locality_value'] and total-par['counts'][j] == balance['native_minus_locality'])
    ranked = sorted(native, key=lambda r:(-r['reported_candidate_writein_votes'], r['source_record']))
    rank = e['native_ranking']; ck([r['key'] for r in ranked] == [r['key'] for r in rank['order']])
    for original, augmented in zip(ranked,rank['order'],strict=True):
        ck(all(augmented[k] == value for k,value in original.items()))
    ranked = rank['order']
    total = sum(r['reported_candidate_writein_votes'] for r in ranked); cumulative = 0; crossing = None
    for i,r in enumerate(ranked,1):
        cumulative += r['reported_candidate_writein_votes']
        ck(r['rank'] == i and r['cumulative_votes'] == cumulative and r['weight_numerator'] == r['reported_candidate_writein_votes'] and r['weight_denominator'] == total)
        if crossing is None and cumulative*5 >= total*4: crossing = i
    ck(total == rank['total'] and crossing == rank['minimum80']['count'])
    ck(sum(r['reported_candidate_writein_votes'] for r in ranked[:15]) == rank['top15']['votes'])
    ck(sum(r['reported_candidate_writein_votes'] for r in ranked[:crossing-1]) == rank['minimum80']['preceding']['votes'])
    ck(orders[f'{year}-native-senate'] == rank)
    native_by_year[year] = ranked; locality_by_year[year] = parents
    summary.append(dict(year=year, native_rows=len(native), parents=133, candidate_generic_votes=total, top15_votes=rank['top15']['votes'], min80_count=crossing, min80_votes=rank['minimum80']['votes'], preceding_votes=rank['minimum80']['preceding']['votes'], nonzero_parent_residuals=e['nonzero_locality_residuals']))

c = load('priority-set.json'); full = c['ordered_units']
ck(len(full) == 2669 and len(c['parent_inventory']) == 133)
ck(c['full_all_unit_order'] == [r['key'] for r in native_by_year[2024]])
ck(c['ordered_priority_keys'] == c['full_all_unit_order'][:1538] and c['ordered_remainder_keys'] == c['full_all_unit_order'][1538:])
legacy_units = {r['key']:r for r in native_by_year[2024]}
json_sources = {k:json.loads(v) for k,v in raws.items() if k == 'enr-2024-senate' or k.startswith('enr-native-')}
state = json_sources['enr-2024-senate']; controls = load('extracts/2024-primary-controls.json')
ck(state['election'] == controls['state_election_metadata'])
ck(state['ballotItemWithBreakdown']['summaryResults'] == controls['state_summary'])
state_options = {o['nativeId']:o for o in state['ballotItemWithBreakdown']['summaryResults']['ballotOptions']}
candidate_sums = Counter(); method_sums = Counter(); seen_objects = set(); method_count = 0
for r in full:
    old = legacy_units[r['key']]
    for k in ['source_id','source_record','physical_line_start','physical_line_end','byte_start','byte_end_exclusive','raw_row_utf8','cells','counts','candidate_votes','reported_candidate_writein_votes','parent_key','parent_label','rank','cumulative_votes','weight_numerator','weight_denominator']:
        ck(r[k] == old[k], k)
    f = r['source_native_constituents']['enr_api']
    obj = pointer(json_sources[f['source_id']], f['source_pointer'])
    ck(obj == f['full_native_object'])
    ck((f['source_id'],f['source_pointer']) not in seen_objects); seen_objects.add((f['source_id'],f['source_pointer']))
    ck(r['source_native_id'] == obj['precinct']['id'] and obj['voteTotal'] == r['reported_candidate_writein_votes'])
    ck({o['nativeId']:o['voteCount'] for o in obj['ballotOptions']} == dict(zip(['cs534','cs535','wi-cc200'],r['candidate_votes'].values())))
    for option in obj['ballotOptions']:
        ck(sum(g['voteCount'] for g in option['groupResults']) == option['voteCount'])
        candidate_sums[option['nativeId']] += option['voteCount']
        for g in option['groupResults']: method_sums[option['nativeId'],g['groupId']] += g['voteCount']; method_count += 1
    ck(r['legal_named_writein_allocation'] is None and r['current_2026_crosswalk'] is None)
ck(len(seen_objects) == 2669 and method_count == 40035)
for k,o in state_options.items():
    ck(candidate_sums[k] == o['voteCount'])
    for g in o['groupResults']: ck(method_sums[k,g['groupId']] == g['voteCount'])
for row in load('extracts/2024-enr-native-methods.jsonl.gz'):
    obj = pointer(json_sources[row['source_id']],row['source_pointer']); ck(obj == row['full_method_object'])
    option = pointer(json_sources[row['source_id']],row['source_pointer'].rsplit('/groupResults/',1)[0])
    ck(option['name'] == row['candidate_name'] and option['party'] == row['party'] and option['nativeId'] == row['candidate_native_id'] and option['id'] == row['candidate_id'])
    ck(option['isWriteIn'] == row['isWriteIn'] and option['isQualifiedWriteIn'] == row['isQualifiedWriteIn'])
for file, key in [('2024-enr-native-objects.jsonl.gz','full_native_object'),('2024-enr-precinct-inventory.jsonl.gz','original_object'),('2024-enr-voter-turnout.jsonl.gz','original_object')]:
    for row in load('extracts/'+file): ck(pointer(json_sources[row['source_id']],row['source_pointer']) == row[key])
for row in load('extracts/2024-enr-local-metadata.json'):
    ck(json_sources[row['source_id']]['election'] == row['election_metadata'])
for p in c['parent_inventory']:
    source = json_sources[p['source_id']]
    ck(p['enr_jurisdiction_id'] == source['jurisdiction']['id'] and p['enr_election_id'] == source['election']['id'])
    ck(p['enr_parent_ballot_item_id'] == source['ballotItemWithBreakdown']['id'])
    ck(p['geometry_or_crossyear_approval'] is False and p['fips'] == '51'+p['locality_code'])
    ck(p['all_native_keys'] == [r['key'] for r in full if r['parent_key'] == p['historical_parent_key']])

# Every published positional CSV projection is checked against the complete raw source.
inventories = load('extracts/csv-source-inventories.json'); projected_rows = full_csv_records = 0
export_rows = None
for inv in inventories:
    sid = inv['source_id']; raw = raws[sid]
    ck(len(raw) == inv['raw_bytes'] and sha(raw) == inv['raw_sha256'])
    filename = {'registration-2024-nov1':'registration-2024-nov1-rows.jsonl.gz'}.get(sid, sid+'-rows.jsonl.gz')
    derived = load('extracts/'+filename)
    by_ordinal = {r['source_record']:r for r in derived}
    ck(len(by_ordinal) == len(derived) == inv['retained_records'])
    retained = set(); all_senate = set(); count = 0; header = None
    for ordinal, first, last, start, end, literal, cells in parsed_records(raw,inv['encoding']):
        count += 1
        if ordinal == 1: header = cells; ck(header == inv['header'])
        if sid == 'enr-2024-results-report' and ordinal > 1 and dict(zip(header,cells)).get('OfficeTitle') == 'Member, United States Senate': all_senate.add(ordinal)
        if ordinal not in by_ordinal: continue
        r = by_ordinal[ordinal]
        ck(r['cells'] == cells and r['raw_row'] == literal and r['physical_line_end'] == last)
        ck((r['byte_start'] == start or (ordinal == 1 and inv['encoding'] == 'utf-8-sig' and raw.startswith(b'\xef\xbb\xbf') and r['byte_start'] == 0 and start == 3)) and r['byte_end_exclusive'] == end)
        ck(raw[r['byte_start']:r['byte_end_exclusive']].decode(inv['encoding']) == r['raw_row'])
        if ordinal > 1: ck((r['fields'] is None and cells == []) or r['fields'] == dict(zip(header,cells)))
        retained.add(ordinal); projected_rows += 1
    ck(count == inv['source_logical_records'] and retained == set(by_ordinal))
    full_csv_records += count
    if sid == 'enr-2024-results-report':
        ck(set(by_ordinal) == all_senate | {1})
        export_rows = by_ordinal

ck(export_rows is not None and len(export_rows) == 8056)
groups = load('extracts/2024-export-constituents.json')
used = []
for g in groups:
    used += g['raw_source_records']
    fs = [export_rows[i]['fields'] for i in g['raw_source_records']]
    sums = Counter()
    for f in fs:
        ck(f['CandidateId'] in ['cs534','cs535','wi-cc200'])
        sums[f['CandidateId']] += int(f['WriteInVote'] if f['CandidateId'] == 'wi-cc200' else f['TOTAL_VOTES'])
    ck(dict(sums) == g['candidate_vector'])
ck(len(used) == len(set(used)) == 8055 and set(used) == set(export_rows)-{1})

finding = json.loads((S/'data/coordinator-turnout-citation-finding/finding.json').read_bytes())
ck(finding['wrong_report_target'] in (S/'turnout.md').read_text())
ck(finding['actual_retained_requested_final_URL'] == request_objects['enr-2024-results-report']['requested_url'])
result = dict(status='pass_independent_original_first_turnout_source_core_with_known_report_citation_defect', checks=N, reviewed_original_first_manifest=dict(path='data/turnout/asset-manifest.json',bytes=(T/'asset-manifest.json').stat().st_size,sha256=sha((T/'asset-manifest.json').read_bytes())), owned_targets=388, complete_pre_peer_witness_bodies=394, fixed_complete_legacy_originals=9, full_request_receipts=165, response_entities=response_count, response_statuses=dict(statuses), raw_legacy_records=original_records, exact_legacy_numeric_positions=numeric_fields, legacy_contests=summary, official_locality_originals=133, complete_2024_native_objects=2669, full_candidate_method_objects=40035, independent_candidate_method_state_balances=15, full_csv_source_records=full_csv_records, exact_selected_csv_records=projected_rows, complete_results_export_constituent_rows=8055, zero_blank_PrecinctId_rows=sum(not r['fields']['PrecinctId'] for k,r in export_rows.items() if k>1), protected_unknowns_fabricated=False, source_counts_keys_orders_or_producer_bytes_changed=False, count_control_associations_only=True, current_or_legal_geography_approval=False, report_citation_repair_pending=True, finding_path='data/coordinator-turnout-citation-finding/finding.json', peer_outputs_read=False, producer_imports_or_writes=False)
(S/'data/coordinator-turnout-original-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],checks=N,legacy_records=original_records,methods=40035,CSV_records=projected_rows)))
