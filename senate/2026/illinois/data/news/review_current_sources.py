"""Bounded regional source replay; no newsroom data admitted as November counts."""
from pathlib import Path
from html.parser import HTMLParser
import gzip
import hashlib
import json

N = Path(__file__).resolve().parent
S = N.parent.parent
O = N / 'coordinator-oct19-recheck'


def sha(value):
    return hashlib.sha256(value).hexdigest()


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style']:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ['script', 'style']:
            self.skip -= 1

    def handle_data(self, value):
        if not self.skip:
            self.text.append(value)


def assignment(text, name):
    return json.JSONDecoder().raw_decode(text.split(name + '=', 1)[1])[0]


def fields(value):
    out = []
    if isinstance(value, dict):
        if isinstance(value.get('customFields'), dict) and 'displayTestData' in value['customFields']:
            out.append(value['customFields'])
        for child in value.values():
            out.extend(fields(child))
    elif isinstance(value, list):
        for child in value:
            out.extend(fields(child))
    return out


def main():
    receipt_path = O / 'acquisition-complete-v1.json'
    receipts = json.loads(receipt_path.read_bytes())
    assert len(receipts) == 8
    by_id = {x['id']: x for x in receipts}
    bodies = {}
    for item in receipts:
        stored = (S / item['asset_path']).read_bytes()
        raw = gzip.decompress(stored)
        assert len(stored) == item['stored_bytes'] < 40_000_000 and sha(stored) == item['stored_sha256']
        assert len(raw) == item['raw_bytes'] and sha(raw) == item['raw_sha256']
        bodies[item['id']] = raw
    wsil = by_id['wsil-home-oct19']
    assert wsil['status'] == 200 and wsil['final_url'] == 'https://www.kfvs12.com/'
    assert wsil['redirects'][0]['status'] == 301 and wsil['redirects'][0]['headers']['Location'] == 'https://www.kfvs12.com/'
    assert by_id['wqad-home-oct19']['status'] == 200 and by_id['wqad-linked-oct19']['status'] == 403
    assert by_id['nyt-elections-oct19']['status'] == 403
    original = bodies['kfvs-results-oct19'].decode()
    cache = assignment(original, 'Fusion.contentCache')
    config = {k: v for k, v in cache.items() if k.startswith('gsync-election')}
    selected = next(iter(config['gsync-elections'].values()))['data']
    assert selected['selectedElection'] == {'id': None} and selected['elections'] == [] and selected['updatedDate'] is None
    widgets = fields(assignment(original, 'Fusion.tree'))
    assert any(x['displayTestData'] is True for x in widgets)
    assert all(json.loads(k)['includeTestResults'] is False for k in config['gsync-elections'])
    page = Page()
    page.feed(bodies['wsil-legacy-ftp-indexed-oct19'].decode())
    text = ' '.join(' '.join(page.text).split())
    assert 'account suspended' in text.lower()
    scope = dict(complete_election_cache=config, complete_widget_custom_fields=widgets,
                 complete_global_content=assignment(original, 'Fusion.globalContent'))
    value = (json.dumps(scope, indent=2) + '\n').encode()
    target = O / 'KFVS-complete-source-objects.json.gz'
    compressed = gzip.compress(value, mtime=0)
    if target.exists():
        assert target.read_bytes() == compressed
    else:
        target.write_bytes(compressed)
    result = dict(status='pass_regional_original_source_replay_no_November_admission',
                  immutable_observations=dict(path=str(receipt_path.relative_to(S)), bytes=receipt_path.stat().st_size, sha256=sha(receipt_path.read_bytes())),
                  complete_source_objects=dict(path=str(target.relative_to(S)), bytes=len(compressed), sha256=sha(compressed), original_JSON_bytes=len(value), original_JSON_sha256=sha(value)),
                  complete_originals=[{k: x[k] for k in ['id', 'url', 'final_url', 'retrieved_at_utc', 'status', 'asset_path', 'raw_bytes', 'raw_sha256', 'stored_sha256']} for x in receipts],
                  WSIL_actual_homepage_redirect=dict(status=301, target='https://www.kfvs12.com/', independent_vote_supplier_established=False),
                  KFVS_selected_election=None, KFVS_source_elections=0, KFVS_publisher_updatedDate=None,
                  KFVS_widget_test_display=True, KFVS_request_includeTestResults=False,
                  indexed_legacy_FTP_scope='Actual HTTP200 Account Suspended page; search-index Kentucky2026 text is stale discovery only and excluded from accepted counts',
                  WQAD_Illinois_guide_HTTP=403, NYT_HTTP=403, current_November_counts_admitted=False,
                  limits='Actual bounded navigation and original/error bytes only. Empty/test settings, old neighboring-state results and a homepage do not establish November count availability, supplier independence, legal coverage, measured cadence or exact remaining Illinois votes.')
    target = O / 'review.json'
    value = (json.dumps(result, indent=2) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == value
    else:
        target.write_bytes(value)
    print(json.dumps(dict(path=str(target.relative_to(S)), bytes=len(value), sha256=sha(value))))


if __name__ == '__main__':
    main()
