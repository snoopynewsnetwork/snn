"""Audit exact historical API captures exposed by the official linked database.

This is preparation, not priority acceptance or November source approval.
"""
import collections
import datetime
import gzip
import hashlib
import json
from pathlib import Path

H = Path(__file__).resolve().parent
API = H / 'history-api'


def response(sid):
    m = json.loads((API / (sid+'.meta.json')).read_text())
    stored = (API / m['body_file']).read_bytes()
    assert len(stored) == m['stored_bytes'] < 40000000
    assert hashlib.sha256(stored).hexdigest() == m['stored_sha256']
    b = gzip.decompress(stored)
    assert len(b) == m['original_bytes'] and hashlib.sha256(b).hexdigest() == m['original_sha256']
    request = (API / m['request_file']).read_bytes()
    assert hashlib.sha256(request).hexdigest() == m['request_sha256']
    j = json.loads(b)
    assert not j.get('errors'), sid
    return j['data']['contestGranularData'], m


def flatten(root):
    result = []
    def walk(node, parents):
        result.append(dict(parent_ids=parents, **node))
        for child in node.get('children') or []:
            walk(child, parents+[node['division']['id']])
    walk(root, [])
    return result


def counts(rows):
    out = {}
    for r in rows:
        key = (r['candidateId'], r['partyId'], r['voteChannelId'])
        assert key not in out
        out[key] = r['votes']
    return out


results = []
all_positions = []
for label in ['2024-pres', '2020-senate', '2022-senate', '2022-governor']:
    combined, cm = response('history-'+label+'-granular-combined')
    methods, mm = response('history-'+label+'-granular-methods')
    root = combined['divisions']
    counties = root['children']
    assert len(counties) == 46 and len({c['division']['id'] for c in counties}) == 46
    assert all(c['division']['divisionTypeName'] == 'County' for c in counties)
    residuals = []
    method_rollup_residuals = []
    for source_mode, node in [(mode,n) for mode,tree in [('combined',root),('methods',methods['divisions'])] for n in flatten(tree)]:
        if not node.get('children'):
            continue
        own = counts(node['granularRow'])
        children = [counts(c['granularRow']) for c in node['children']]
        for key, value in own.items():
            parts = [c.get(key) for c in children]
            if value is None or any(x is None for x in parts):
                (residuals if source_mode == 'combined' else method_rollup_residuals).append(dict(division=node['division'], key=key, status='missing_values_not_zero'))
            elif value != sum(parts):
                (residuals if source_mode == 'combined' else method_rollup_residuals).append(dict(division=node['division'], key=key, parent=value, children=sum(parts), difference=value-sum(parts)))
    combined_nodes = {tuple(n['parent_ids']+[n['division']['id']]): n for n in flatten(root)}
    method_nodes = {tuple(n['parent_ids']+[n['division']['id']]): n for n in flatten(methods['divisions'])}
    assert set(combined_nodes) == set(method_nodes)
    method_residuals = []
    for key, node in combined_nodes.items():
        a = counts(node['granularRow']); b = counts(method_nodes[key]['granularRow'])
        for (candidate, party, channel), value in a.items():
            assert channel == 0
            parts = [v for (c,p,m),v in b.items() if c == candidate and p == party]
            if value is None or not parts or any(v is None for v in parts):
                method_residuals.append(dict(division=key, candidate=candidate, status='missing_not_zero'))
            elif sum(parts) != value:
                method_residuals.append(dict(division=key, candidate=candidate, combined=value, methods=sum(parts), difference=value-sum(parts)))
        for mode, n in [('combined', node), ('methods', method_nodes[key])]:
            for ordinal, value in enumerate(n['granularRow']):
                all_positions.append(dict(contest_label=label, observation_scope=mode, division_path=key,
                                          division=n['division'], raw_ordinal=ordinal, raw_value=value))
    # Pseudocandidate totals/ballots/over-under are controls, not candidate votes.
    candidates = {int(c['candidateId']): c for c in combined['candidates']}
    real_ids = {cid for cid,c in candidates.items() if c['candidate']['pseudocandidate'] in [None, 'ALL_OTHER_CANDIDATES']}
    root_counts = counts(root['granularRow'])
    real_total = sum(v for (cid,party,ch),v in root_counts.items() if cid in real_ids)
    county_totals = {c['division']['name']: sum(v for (cid,party,ch),v in counts(c['granularRow']).items() if cid in real_ids) for c in counties}
    assert real_total == sum(county_totals.values())
    ranked = sorted(county_totals, key=lambda name: (-county_totals[name], name))
    cumulative = 0; n = 0
    while cumulative*5 < real_total*4:
        cumulative += county_totals[ranked[n]]; n += 1
    results.append(dict(contest=label, combined_original_sha256=cm['original_sha256'],
                        methods_original_sha256=mm['original_sha256'], counties=46,
                        native_finer_divisions=sum(len(c.get('children') or []) for c in counties),
                        full_source_division_objects=len(combined_nodes),
                        candidate_and_generic_total=real_total,
                        state_source_candidates=[dict(source_candidate_id=cid, displayName=c['displayName'],
                                                     pseudocandidate=c['candidate']['pseudocandidate'], nVotes=c['nVotes']) for cid,c in candidates.items()],
                        method_names=methods['voteChannels'],
                        all_rollup_residuals=residuals, all_method_residuals=method_residuals,
                        method_hierarchy_rollup_residuals=method_rollup_residuals,
                        method_residual_candidate_counts=dict(collections.Counter(str(r['candidate']) for r in method_residuals)),
                        provisional_full_county_order=ranked, provisional_top15=sum(county_totals[k] for k in ranked[:15]),
                        provisional_min80_count=n, provisional_min80_votes=cumulative,
                        previous_votes=cumulative-county_totals[ranked[n-1]], crossing=ranked[n-1]))
(H / 'coordinator-history-source-positions.jsonl.gz').write_bytes(gzip.compress(
    b''.join((json.dumps(r, ensure_ascii=False, separators=(',', ':'))+'\n').encode() for r in all_positions), mtime=0))
out = dict(status='preflight_with_source_residuals' if any(r['all_rollup_residuals'] or r['all_method_residuals'] for r in results) else 'pass_primary_preflight_only',
           checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), contests=results,
           preserved_source_positions=len(all_positions),
           scope='Official-linked historical database, actual route/query/IDs from public app; raw request/response/original hashes retained. No accepted priority, native crosswalk, certification chronology or November admission.',
           limits=['Legacy official2024/2022/2020 ENR routes returned403 and remain separately retained.',
                   'Pseudocandidate TOTAL_VOTES/TOTAL_BALLOTS/PSEUDOCANDIDATE under-over rows overlap real candidates and are not summed as candidate votes.',
                   'Two-depth division responses retain state/county/precinct hierarchies; no same-ID cross-year or physical approval is inferred.',
                   'Candidate party labels/fusion channels/status flags remain raw; verifiedAt does not establish certification date.',
                   'Initial suggestions query variable errors are retained; corrected v2 queries have separate immutable captures.'])
(H / 'coordinator-primary-preflight.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(dict(status=out['status'], positions=len(all_positions), contests=[{k:r[k] for k in ['contest','counties','native_finer_divisions','candidate_and_generic_total','provisional_min80_count','provisional_min80_votes','previous_votes','crossing']} | dict(rollup_residuals=len(r['all_rollup_residuals']),method_residuals=len(r['all_method_residuals'])) for r in results]), indent=2))
