"""Decode complete embedded election JSON; retain setup flags and publisher clocks."""
from pathlib import Path
import gzip, hashlib, json, re

ROOT = Path(__file__).resolve().parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    m = json.loads((ROOT / 'manifest.json').read_bytes())
    observations = []
    for source in ('wlbt-results', 'wlox-results', 'wdam-results', 'wtva-results', 'wtok-results', 'nyt-elections'):
        r = next(r for r in m if r['id'] == source + '-coordinator-oct19-2026')
        z = (ROOT / r['asset']).read_bytes()
        b = gzip.decompress(z)
        assert sha(z) == r['stored_sha256'] and sha(b) == r['raw_sha256']
        t = b.decode(errors='replace')
        elections = []
        for match in re.finditer(r'"selectedElection":', t):
            election, end = json.JSONDecoder().raw_decode(t, match.end())
            assert isinstance(election, dict)
            if election not in elections:
                elections.append(election)
        o = dict(id=r['id'], source_url=r['url'], complete_original_asset=r['asset'], complete_original_raw_sha256=sha(b), HTTP_status=r['status'], fetch_started_at_UTC=r['retrieved_at_utc'], displayTestData_literals=sorted(set(re.findall(r'"displayTestData":(true|false)', t))), decoded_complete_selected_elections=[])
        for election in elections:
            item = dict(header={k:v for k,v in election.items() if k != 'races'}, actual_returned_race_rows=len(election.get('races', [])), MS_Senate_rows=[v for v in election.get('races', []) if v.get('name') == 'U.S. Senate (MS)'])
            if source == 'wtva-results':
                assert election['id'] == '2811' and election['isActive'] is False and election['name'] == '2026 General Election - Nov. 3'
                assert election['updatedDate'] is None and election['hasRecentUpdates'] is False
                assert len(election['races']) == 13 and election['totalResults'] == 13
                assert len(item['MS_Senate_rows']) == 1
                race = item['MS_Senate_rows'][0]
                assert race['id'] == '60393' and race['isTest'] is False and race['reportingInfo'] == ''
                assert [(c['name'],c['party'],c['id'],c['votes']) for c in race['candidates']] == [('Scott Colom','D','150675',0),('Cindy Hyde-Smith','R','150676',0),('Ty Pinkins','I','150677',0)]
                assert o['displayTestData_literals'] == ['true']
                p = ROOT / 'wtva-oct19-complete-selected-election.json.gz'
                derivative = json.dumps(election, ensure_ascii=False, indent=2).encode() + b'\n'
                stored = gzip.compress(derivative, mtime=0)
                if p.exists():
                    assert p.read_bytes() == stored
                else:
                    p.write_bytes(stored)
                item['complete_decoded_selected_election_derivative'] = dict(path=p.name, stored_bytes=len(stored), stored_sha256=sha(stored), decoded_JSON_bytes=len(derivative), decoded_JSON_sha256=sha(derivative), original_JSON_character_range=[match.end(),end])
                item['admission'] = 'inactive_zero_setup_only_no_November_count_admission'
                item['qualification'] = 'Actual embedded newsroom GSync IDs are observed setup identities, not officialENR keys or authenticated changing returns. Per-race isTest=false is retained alongside global displayTestData=true; these flags are not collapsed. updatedDate=null and hasRecentUpdates=false; dataTransformedAt is a transformation clock, not established vote-publication time or measured update cadence. No write-in row or native/county breakdown is supplied by this Senate race.'
            elif source in ('wlbt-results', 'wdam-results', 'wtok-results'):
                assert election == dict(id=None)
                item['admission'] = 'no_selected_election'
            elif source == 'wlox-results':
                assert election['id'] == '2745' and election['isActive'] is False and election['name'] == 'MS Chancery Court Judicial Races'
                item['admission'] = 'inactive_judicial_races_not_MS_Senate'
            o['decoded_complete_selected_elections'].append(item)
        if source == 'nyt-elections':
            assert r['status'] == 403 and not elections
            o['admission'] = 'automated_access_denied'
        o['admitted_November_Senate_counts'] = False
        observations.append(o)
    out = dict(status='pass_complete_embedded_JSON_source_scope_review', captures=len(m), observations=observations, prior_recheck_regex_prefixes_are_discovery_leads_only=True, qualification='This structured decoder supersedes the earlier regex-prefix leads for election-object interpretation while retaining every earlier body/observation. Complete selected JSON is decoded from raw originals, not search/page summaries. WTVA newly selects inactive zero November setup; other stations remain empty/judicial, NYT403. No genuine count sequence, official source keys, candidate completeness or cadence inferred.')
    p = ROOT / 'current-results-structured-review-oct19.json'
    b = (json.dumps(out, indent=2) + '\n').encode()
    if p.exists():
        assert p.read_bytes() == b
    else:
        p.write_bytes(b)
    print(json.dumps(dict(path=p.name, bytes=len(b), sha256=sha(b), captures=len(m), WTVA_current_state='inactive_zero_general_setup_2811', admitted_genuine_counts=False)))


if __name__ == '__main__':
    main()
