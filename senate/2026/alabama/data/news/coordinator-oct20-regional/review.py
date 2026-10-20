"""Offline complete receipt and published embedded widget review."""
from pathlib import Path
import gzip
import hashlib
import html
import json
import re

H = Path(__file__).resolve().parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=p.name, bytes=len(b), sha256=sha(b))


def main():
    observations = []
    originals = {}
    for p in sorted(H.glob('*.receipt.json')):
        r = json.loads(p.read_bytes())
        assert r['status'] == 200
        for hop in r['hops']:
            z = (H / hop['body_path']).read_bytes()
            b = gzip.decompress(z)
            assert (len(z), sha(z)) == (hop['stored_bytes'], hop['stored_sha256'])
            assert (len(b), sha(b)) == (hop['raw_bytes'], hop['raw_sha256'])
        text = b.decode('utf-8', errors='replace')
        originals[r['id']] = text
        title = re.search(r'<title[^>]*>(.*?)</title>', text, re.S | re.I)
        observations.append(dict(id=r['id'], receipt=pin(p), status=r['status'], final_url=r['final_url'],
                                 complete_hops=len(r['hops']), title=html.unescape(title[1]) if title else None,
                                 raw_bytes=len(b), raw_sha256=sha(b)))
    assert len(observations) == 3
    source = originals['wtvy-results']
    marker = 'Fusion.contentCache='
    cache, length = json.JSONDecoder().raw_decode(source.split(marker, 1)[1])
    complete = {k:v for k,v in cache.items() if 'election' in k}
    p = H / 'wtvy-complete-embedded-election-cache.json'
    p.write_text(json.dumps(complete, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    queries = complete['gsync-elections']
    assert len(queries) == 1
    query, value = next(iter(queries.items()))
    assert json.loads(query) == {'arc-site':'wtvy', 'includeTestResults':False}
    data = value['data']
    selected = data['selectedElection']
    assert (selected['id'], selected['name'], selected['isActive']) == ('2782','2026 General Election - Alabama',False)
    assert len(selected['races']) == 24 and data['totalElections'] == len(data['elections']) == 3
    assert all(c['votes'] == 0 for r in selected['races'] for c in r['candidates'])
    senate = next(r for r in selected['races'] if r['name'] == 'U.S. Senate - Class II')
    raw_flag = source.find('displayTestData')
    assert raw_flag >= 0
    literal_flag_context = source[raw_flag - 100:raw_flag + 100]
    assert 'displayTestData":true' in literal_flag_context.replace(chr(92), '')
    report = dict(status='pass_bounded_primary_Alabama_regional_and_complete_widget_review',
                  complete_requests=3, HTTP200=3, observations=observations,
                  complete_embedded_election_object=pin(p), selected_election_id=selected['id'],
                  selected_election_name=selected['name'], selected_isActive=selected['isActive'],
                  full_selected_races=len(selected['races']), complete_selected_Senate_object=senate,
                  backend_request_parameters=json.loads(query), publisher_updatedDate=data['updatedDate'],
                  dataTransformedAt=data['dataTransformedAt'], literal_frontend_flag_context=literal_flag_context,
                  all_selected_candidate_counts_zero=True,
                  entire_other_state_election_list=data['elections'],
                  source_qualification='Fresh HTTP body is an inactive General-labelled Alabama template with allzero votes, frontend displayTestData true and backend includeTestResults false; isTest false in list/races does not approve counts. Cached web-reader text instead presents Alabama special House primary. Both observations remain separate without correction chronology or proof of actual November election date/ballot completeness.',
                  reporting_scope='WTVY May19 primary report is dated primary reporting. Lagniappe September15 public-preview title/lead concerns November amendments; encoded/protected text is retained raw and never decoded or accessed through auth.',
                  raw_definition='Requests-decoded HTTP entity bytes, not compressed wire frames.',
                  no_auth_paywall_decode_account_contact_or_social_actions=True,
                  current_November_votes_choice_ids_cadence_or_count_supplier_approved=False,
                  original_news_manifest_unchanged=True,
                  qualification='Observed widget keys are setup evidence only. Cross-state Alabama/Georgia/Florida entries and shared publisher infrastructure are not additive or independent votes. No Senate roster/legal-writein completeness, forecast, outstanding pool or live collector.')
    (H / 'review.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    p = H / 'acquisition-complete-v1.json'
    entries = [pin(f) for f in sorted(H.iterdir()) if f.is_file() and f != p]
    assert all(x['bytes'] < 40000000 for x in entries)
    p.write_text(json.dumps(dict(files=entries, excludes_only=p.name, only_self_excluded=True, no_reverse_inventory_pin=True), indent=2) + '\n')
    print(json.dumps(dict(review=pin(H / 'review.json'), inventory=pin(p), files=len(entries))))


if __name__ == '__main__':
    main()
