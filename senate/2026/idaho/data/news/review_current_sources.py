"""Offline review of bounded October19 newsroom and primary page observations."""
from pathlib import Path
import gzip, hashlib, json, re

N = Path(__file__).resolve().parent
S = N.parent.parent
O = N/'coordinator-oct19-recheck'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))

def main():
    source = O/'acquisition-complete-v1.json'
    rows = json.loads(source.read_bytes())
    assert len(rows) == 13 and len({r['id'] for r in rows}) == 13
    bodies = {}
    for r in rows:
        b = (S/r['asset_path']).read_bytes()
        assert len(b) == r['stored_bytes'] < 40_000_000 and sha(b) == r['stored_sha256']
        raw = gzip.decompress(b)
        assert len(raw) == r['raw_bytes'] and sha(raw) == r['raw_sha256']
        bodies[r['id']] = raw.decode('utf-8-sig',errors='replace')
    old = N/'manifest.json'
    assert len(json.loads(old.read_bytes())) == 16
    embedded = {}
    decoder = json.JSONDecoder()
    for key in ['selectedElection','globalSettings','electionData']:
        found = []
        for m in re.finditer('"'+key+'"'+r'\s*:\s*',bodies['kmvt-results']):
            try:
                value,end = decoder.raw_decode(bodies['kmvt-results'][m.end():])
            except json.JSONDecodeError:
                continue
            found.append(value)
        embedded[key] = found
    assert embedded['selectedElection'] == [{'id':None}]
    test = sorted(set(re.findall(r'"displayTestData"\s*:\s*(true|false)',bodies['kmvt-results'])))
    assert test == ['true']
    kifi = bodies['kifi-results']
    conf = json.loads(re.search(r'var npgElection = (\{[^;]+\});',kifi)[1])
    assert conf['refreshInterval'] == '60000'
    js = bodies['kifi-election-public-js']
    assert '?action=npg_refresh&mode=' in js and '300000' in js
    refresh = json.loads(bodies['kifi-actual-full-refresh'])
    assert refresh['success'] is True
    races = re.findall(r'data-race-name="([^"]*)"',refresh['data']['html'])
    assert len(races) == 26
    assert races[:2] == ['REP - WY US Senate','DEM - WY US Senate']
    assert refresh['data']['report_time'] == '2026-08-19 09:42:35 am'
    e = json.loads(bodies['kifi-actual-full-refresh'])
    p = O/'complete-kifi-returned-html.json.gz'
    b = gzip.compress((json.dumps(e,indent=2)+'\n').encode(),mtime=0)
    if p.exists(): assert p.read_bytes() == b
    else: p.write_bytes(b)
    out = dict(status='pass_bounded_current_sources_not_Idaho_November_count_admission',
        immutable_acquisition=pin(source), prior16_observations=pin(old),
        prior_original_ledger_unchanged=True, new_complete_observations=13,
        statuses={r['id']:r['status'] for r in rows},
        KMVT_complete_selected_objects=embedded, KMVT_displayTestData=test,
        KIFI_actual_public_refresh=dict(parent='kifi-results',constructor='npgElection.ajaxUrl + action=npg_refresh + mode=full + actual public nonce',
            complete_response=pin(p), report_time_literal=refresh['data']['report_time'],
            source_timezone=None, all26_returned_race_names=races,
            configured_full_refresh_milliseconds=60000,
            configured_ticker_and_featured_refresh_milliseconds=300000,
            observed_publication_cadence=False, Idaho_November_2026_returns=False,
            supplier_not_established=True),
        official_ballot_and_candidate_pages=dict(
            election='2026-11-03', general_information='https://voteidaho.gov/idaho-general-election/',
            filing_page='https://voteidaho.gov/candidate-filing/',
            actual_public_candidate_search='https://run.voteidaho.gov/search',
            full_complete_JS_bundle_retained=True,
            public_shell_does_not_establish_final_candidate_roster=True,
            primary_observed_links_only_no_private_API_or_authentication_attempt=True),
        current_results_index_review='Separate immutable map preparation retains fresh actual May-primary results parent; no November admission.',
        all_genuine_November_counts_and_cadence_approval=False,
        qualification='All complete responses/errors remain source-scoped. KTVB linked guide403 and NYT403; KMVT selection null/test-enabled; KIFI public response August Wyoming primary/local races. HTTP200, a refresh timer, current filing shell and navigation are not Idaho November votes or a stable eligible-candidate/result-ID universe.')
    target = O/'review.json'
    b = (json.dumps(out,indent=2)+'\n').encode()
    if target.exists(): assert target.read_bytes() == b
    else: target.write_bytes(b)
    print(json.dumps(pin(target)))

if __name__ == '__main__':
    main()
