"""Replay immutable current newsroom originals; no network or November admission."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import gzip
import hashlib
import json

N = Path(__file__).resolve().parent
S = N.parent.parent
O = N / 'coordinator-oct19-recheck'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


class Surface(HTMLParser):
    def __init__(self):
        super().__init__()
        self.frames = []
        self.hidden = 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style']:
            self.hidden += 1
        if tag == 'iframe':
            self.frames.append(dict(attrs))

    def handle_endtag(self, tag):
        if tag in ['script', 'style'] and self.hidden:
            self.hidden -= 1

    def handle_data(self, text):
        if not self.hidden:
            self.text.append(text)


def assignment(text, name):
    return json.JSONDecoder().raw_decode(text.split(name + '=', 1)[1])[0]


def custom_fields(value):
    found = []
    if isinstance(value, dict):
        if isinstance(value.get('customFields'), dict):
            fields = value['customFields']
            if 'displayTestData' in fields or 'overrideGsyncSiteId' in fields:
                found.append(fields)
        for v in value.values():
            found.extend(custom_fields(v))
    elif isinstance(value, list):
        for v in value:
            found.extend(custom_fields(v))
    return found


def main():
    receipt_path = O / 'acquisition-complete-v1.json'
    receipts = json.loads(receipt_path.read_bytes())
    assert len(receipts) == 11 and len({r['id'] for r in receipts}) == 11
    by_id, texts, surfaces, originals = {}, {}, {}, []
    for r in receipts:
        by_id[r['id']] = r
        p = S / r['asset_path']
        b = p.read_bytes()
        raw = gzip.decompress(b)
        assert len(b) == r['stored_bytes'] < 40000000 and sha(b) == r['stored_sha256']
        assert len(raw) == r['raw_bytes'] and sha(raw) == r['raw_sha256']
        texts[r['id']] = raw.decode(errors='replace')
        surface = Surface()
        surface.feed(texts[r['id']])
        surfaces[r['id']] = surface
        originals.append(dict(id=r['id'], source_status=r['status'], complete_stored_original=pin(p),
                              complete_raw_bytes=len(raw), complete_raw_sha256=sha(raw)))
    configs = {}
    for source in ['KJCT-results', 'KKTV-current-results']:
        cache = assignment(texts[source], 'Fusion.contentCache')
        election = {key: value for key, value in cache.items() if key.startswith('gsync-election')}
        configs[source] = dict(complete_election_cache=election,
                               complete_related_custom_fields=custom_fields(assignment(texts[source], 'Fusion.tree')),
                               complete_global_content=assignment(texts[source], 'Fusion.globalContent'))
    def selected(source):
        entries = configs[source]['complete_election_cache']['gsync-elections']
        assert len(entries) == 1
        return next(iter(entries.values()))['data']
    west, south = selected('KJCT-results'), selected('KKTV-current-results')
    assert west['selectedElection'] == {'id': None} and west['elections'] == [] and west['updatedDate'] is None
    assert south['selectedElection']['id'] == '2510'
    assert south['selectedElection']['name'] == '2026 Colorado Primary' and south['selectedElection']['isActive'] is False
    assert any(x.get('displayTestData') is True for x in configs['KKTV-current-results']['complete_related_custom_fields'])
    west_key = next(iter(configs['KJCT-results']['complete_election_cache']['gsync-elections']))
    assert json.loads(west_key)['gsyncSiteId'] == 'kkco'
    ap = {}
    for source in ['Sun-current-results', 'KJCT-linked-Colorado-interactive']:
        ap[source] = [frame for frame in surfaces[source].frames
                      if 'interactives.apelections.org' in frame.get('src', frame.get('data-src', ''))]
    assert len(ap['Sun-current-results']) == 14 and len(ap['KJCT-linked-Colorado-interactive']) == 2
    assert all(by_id[k]['status'] == 403 for k in ['Sun-linked-AP-layout', 'KJCT-linked-AP-Senate', 'KJCT-linked-AP-balance'])
    assert 'primary' in ' '.join(surfaces['Sun-current-results'].text).lower()
    assert by_id['CPR-current-home']['status'] == by_id['NYT-current-hub']['status'] == 403
    cache_path = O / 'complete-GSync-source-objects.json.gz'
    cache_raw = (json.dumps(configs, indent=2, ensure_ascii=False) + '\n').encode()
    cache_bytes = gzip.compress(cache_raw, mtime=0)
    if cache_path.exists():
        assert cache_path.read_bytes() == cache_bytes
    else:
        cache_path.write_bytes(cache_bytes)
    out = dict(status='pass_current_news_source_replay_no_November_admission',
               frozen_receipts=pin(receipt_path), complete_original_entities=originals,
               HTTP_status_counts=dict(Counter(str(r['status']) for r in receipts)),
               actual_AP_frame_chains=ap, complete_GSync_objects=pin(cache_path),
               complete_GSync_reconstructed_bytes=len(cache_raw), complete_GSync_reconstructed_sha256=sha(cache_raw),
               KJCT=dict(selected_election_id=None, elections=0, publisher_update_time=None,
                         configured_GSync_site='kkco', current_November_counts_admitted=False),
               KKTV=dict(selected_election='2026 Colorado Primary', selected_id='2510', active=False,
                         widget_displayTestData=True, November_counts_admitted=False,
                         qualification='Raw cache includeTestResults false and election isTest false remain distinct from widget displayTestData true.'),
               Sun=dict(page_scope='primary', AP_frames=14, sampled_AP_frame_HTTP=403),
               KJCT_interactive=dict(AP_frames=2, sampled_both_HTTP=403, election_payload_unavailable=True),
               source_precedence='AP embeds from different publishers are shared upstream, not independent vote confirmations; '
                                 'GSync configured source is preserved without inferring AP or legal ballot completeness.',
               raw_complete_sources_preserved=True, current_November_feed_admitted=False,
               demonstrated_cadence=False, qualification='Publisher/navigation/config observations only. '
               'Access failures, historical/empty selections and client settings do not supply counted returns, '
               'candidate allocation, exact outstanding votes, legal geography or calibrated probability.')
    target = O / 'review.json'
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(pin(target)))


if __name__ == '__main__':
    main()
