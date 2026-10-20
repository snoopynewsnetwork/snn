"""Offline exact bounded newsroom access and literal locality-link review."""
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
    for p in sorted(H.glob('*.receipt.json')):
        r = json.loads(p.read_bytes())
        assert r['status'] == 200
        for hop in r['hops']:
            z = (H / hop['body_path']).read_bytes()
            b = gzip.decompress(z)
            assert (len(z), sha(z)) == (hop['stored_bytes'], hop['stored_sha256'])
            assert (len(b), sha(b)) == (hop['raw_bytes'], hop['raw_sha256'])
        raw = b.decode('utf-8', errors='replace')
        title = re.search(r'<title[^>]*>(.*?)</title>', raw, re.S | re.I)
        observations.append(dict(id=r['id'], receipt=pin(p), status=r['status'], final_url=r['final_url'],
                                 complete_hops=len(r['hops']), title=html.unescape(title[1]) if title else None,
                                 raw_bytes=len(b), raw_sha256=sha(b)))
    assert len(observations) == 4
    links = json.loads((H / 'cardinal-current-guide.election-links.json').read_bytes())
    localities = {x['url']: x['text'] for x in links if '/how-to-vote-in-' in x['url']}
    assert localities['https://cardinalnews.org/how-to-vote-in-richmond/'] == 'Richmond'
    assert localities['https://cardinalnews.org/how-to-vote-in-richmond-county/'] == 'Richmond County'
    assert len(localities) == 132
    report = dict(status='pass_bounded_primary_Virginia_regional_news_review', complete_requests=4, HTTP200=4,
                  observations=observations,
                  Cardinal_literal_locality_pattern_links=[dict(url=u, text=t) for u, t in localities.items()],
                  literal_pattern_matches=132, guide_introduction_claims_locality_pages=133,
                  coverage_qualification='The132 extracted unique how-to-vote-in URL pattern matches are a bounded navigation inventory, not proof of missing pages, official authority completeness or a current identity crosswalk. Entire raw guide remains retained.',
                  source_scope='Current2026 Cardinal guide and actual separately linked Richmond city/county pages; WHRO October9 AnotherView local program page. Newsroom/civic/analyst context, no numericNovemberSenatefeed/countsupplier/cadence measured.',
                  raw_definition='Requests-decoded HTTP entity bytes, not compressed wire frames.',
                  no_contact_form_account_social_or_audio_downloads=True,
                  all_native_official_or_candidate_mapping_approved=False,
                  genuine_November_counts_or_measured_cadence_admitted=False,
                  original_news_manifest_unchanged=True)
    (H / 'review.json').write_text(json.dumps(report, indent=2) + '\n')
    p = H / 'acquisition-complete-v1.json'
    entries = [pin(f) for f in sorted(H.iterdir()) if f.is_file() and f != p]
    assert all(x['bytes'] < 40000000 for x in entries)
    p.write_text(json.dumps(dict(files=entries, excludes_only=p.name, only_self_excluded=True, no_reverse_inventory_pin=True), indent=2) + '\n')
    print(json.dumps(dict(review=pin(H / 'review.json'), inventory=pin(p), files=len(entries))))


if __name__ == '__main__':
    main()
