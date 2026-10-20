"""Offline bounded newsroom receipt/body review and acyclic inventory."""
from pathlib import Path
from collections import Counter
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
    rows = []
    bodies = {}
    raw = {}
    for p in sorted(H.glob('*.receipt.json')):
        r = json.loads(p.read_bytes())
        for h in r['hops']:
            z = (H / h['body_path']).read_bytes()
            b = gzip.decompress(z)
            assert (len(z), sha(z)) == (h['stored_bytes'], h['stored_sha256'])
            assert (len(b), sha(b)) == (h['raw_bytes'], h['raw_sha256'])
            assert len(z) < 40000000
            bodies[h['raw_sha256']] = h
        raw[r['id']] = b.decode('utf-8', errors='replace')
        t = re.search(r'<title[^>]*>(.*?)</title>', raw[r['id']], re.S | re.I)
        rows.append(dict(id=r['id'], receipt=pin(p), status=r.get('status'), complete_response_hops=len(r['hops']),
                         final_url=r.get('final_url'), title=html.unescape(re.sub('<[^>]+>', '', t[1])) if t else None,
                         raw_bytes=len(b), raw_sha256=sha(b)))
    assert len(rows) == 5 and Counter(x['status'] for x in rows) == {200: 4, 403: 1}
    linked = 'https://www.thewesterlysun.com/lwv-voter-guide-2026/pdf_2221745c-3c98-4ef0-9afa-6abba911f478.html'
    assert linked in raw['westerly-home']
    assert '2026 General Nov. 3' in raw['current-general-guide']
    report = dict(status='pass_bounded_primary_newsroom_access_and_guide_review',
                  observations=rows, complete_requests=5, complete_response_entities=len(bodies),
                  HTTP200=4, HTTP403=1,
                  raw_definition='Requests-decoded HTTP entity bytes, not compressed wire frames.',
                  Westerly_guide_parent_href_exact=True,
                  web_search_qualification='Initial queries accidentally used site.domain rather than site:domain and are not scoped absence evidence. Correct explicit domain-filter searches reported robots exclusions for the three local domains; those are web-reader access observations, separate from the normal bounded HTTP receipts here.',
                  source_scope={
                      'newport':'Homepage403 Access Restricted, complete body retained. No numeric November product or automation established.',
                      'westerly':'Actual public homepage200 links LWV Voter Guide2026. Exact linked HTML holder200 acquired. Reporting/guide context only; no Senate count origin, November scoreboard or release cadence established.',
                      'block_island':'Actual public homepage200 with publisher title; no election link identified by the bounded link inspection. This is not proof the publisher has no election coverage.',
                      'current':'Exact current General Nov3 voter-guide page200, with state-office/bond preparation. No usable Senate numeric feed or independent count supply established.'},
                  all_selected_requests_public_read_only=True, no_social_or_account_links_requested=True,
                  genuine_November_counts_or_ids_or_measured_cadence_admitted=False,
                  original_news_manifest_unchanged=True,
                  qualification='Regional access/guide evidence only, not complete geographic coverage, eligible candidate universe, vote totals, source independence, cadence or a collector. Existing board-derived Journal source and AP/shared channels remain overlapping evidence.')
    (H / 'review.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    p = H / 'acquisition-complete-v1.json'
    entries = [pin(f) for f in sorted(H.iterdir()) if f.is_file() and f != p]
    assert all(x['bytes'] < 40000000 for x in entries)
    inventory = dict(status='complete_bounded_source_inventory', files=entries, excludes_only=p.name,
                     only_self_excluded=True, no_reverse_inventory_pin_in_review=True)
    p.write_text(json.dumps(inventory, indent=2) + '\n')
    print(json.dumps(dict(review=pin(H / 'review.json'), inventory=pin(p), files=len(entries))))


if __name__ == '__main__':
    main()
