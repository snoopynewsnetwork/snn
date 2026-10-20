"""Read complete immutable newsroom observations without executing client code."""
from pathlib import Path
from html.parser import HTMLParser
import gzip
import hashlib
import json
import re
import urllib.parse

N = Path(__file__).resolve().parent
S = N.parent.parent
O = N / 'coordinator-oct19-recheck'


def sha(value):
    return hashlib.sha256(value).hexdigest()


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.frames = []
        self.scripts = []
        self.visible = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style'):
            self.skip += 1
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs)
        if tag == 'iframe':
            self.frames.append(attrs)
        if tag == 'script' and attrs.get('src'):
            self.scripts.append(attrs)

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1

    def handle_data(self, value):
        if not self.skip:
            self.visible.append(value)


def main():
    path = O / 'acquisition-complete-v1.json'
    observations = json.loads(path.read_bytes())
    assert len(observations) == 13
    rows = []
    bodies = {}
    parsed = {}
    for entry in observations:
        row = {k: entry[k] for k in ['id', 'url', 'parent_id', 'literal_href', 'retrieved_at_utc', 'status', 'final_url']}
        if entry.get('asset_path'):
            stored = (S / entry['asset_path']).read_bytes()
            raw = gzip.decompress(stored)
            assert sha(stored) == entry['stored_sha256'] and len(stored) == entry['stored_bytes'] < 40_000_000
            assert sha(raw) == entry['raw_sha256'] and len(raw) == entry['raw_bytes']
            row.update(original_reference=entry['asset_path'], original_bytes=len(raw), original_sha256=sha(raw))
            bodies[entry['id']] = raw
            if b'<html' in raw.lower():
                page = Page()
                page.feed(raw.decode('utf-8', errors='replace'))
                parsed[entry['id']] = page
                row.update(complete_literal_links=page.links, complete_literal_iframes=page.frames,
                           complete_literal_external_scripts=page.scripts)
        rows.append(row)
    config = bodies['spotlight-config-oct19'].decode()
    app = bodies['spotlight-app-oct19'].decode()
    data = json.loads(bodies['spotlight-data-oct19'])
    assert data['electionDate'] == '2026-09-15' and len(data['contests']) == 33
    assert data['reporting'] == dict(reported=530, total=530, percentage=100, label='Election districts reporting statewide')
    options = []
    for contest in data['contests']:
        for candidate in contest['candidates']:
            assert sum(candidate[k] for k in ['machineVotes', 'absenteeVotes', 'earlyVotes']) == candidate['votes']
            options.append(dict(contest_id=contest['id'], party=contest.get('party'), **candidate))
    assert 'pollIntervalMs: 20000' in config and '2026-09-15T20:00:00-04:00' in config
    assert 'Math.max(15000, Number(config.pollIntervalMs) || 20000)' in app
    assert 'fetch(config.apiUrl' in app
    fox_frames = parsed['fox29-results-oct19'].frames
    ap_frames = [x for x in fox_frames if 'interactives.apelections.org' in x.get('src', '')]
    assert len(ap_frames) == 10
    assert any(x.get('src') == 'https://media.foxtv.com/wtxf/elections/2026_DE_PRIMARY.html' for x in fox_frames)
    static = Page()
    static.feed(bodies['fox29-static-oct19'].decode())
    fox_text = ' '.join(' '.join(static.visible).split())
    wboc_text = ' '.join(' '.join(parsed['wboc-results-oct19'].visible).split())
    assert 'Primary' in wboc_text and '30,896' in wboc_text and '9,052' in wboc_text
    assert '99%' in fox_text and '30,896' in fox_text
    abc_text = ' '.join(' '.join(parsed['6abc-primary-oct19'].visible).split())
    assert 'Primary' in abc_text or 'primary' in abc_text
    assert next(x for x in observations if x['id'] == 'fox29-AP-first-oct19')['status'] == 403
    assert next(x for x in observations if x['id'] == 'nyt-elections-oct19')['status'] == 403
    out = dict(status='pass_bounded_current_newsroom_original_review_no_November_admission',
               immutable_observation_manifest=dict(path=str(path.relative_to(S)), bytes=path.stat().st_size, sha256=sha(path.read_bytes())),
               observations=rows,
               spotlight_complete_metadata={k: v for k, v in data.items() if k != 'contests'},
               spotlight_all_candidate_method_objects=options,
               spotlight_client_interval_ms=20000, observed_changing_publisher_cadence=False,
               FOX29_AP_frames=10, AP_sample_access=403,
               completion_disagreement='WBOC primary Senate displays100%; FOX29 static primary table99%. Neither supplies exact outstanding November votes.',
               source_presentation_note='HTML was parsed from every complete body regardless of response-header key case; initial convenience link extraction omitted some lowercase-header responses. Originals and headers are unchanged.',
               current_November_counts_or_forecast_approved=False,
               limits='All located count products in this bounded inspection are September primary or unavailable. A client refresh interval and stale:false do not prove current data, upstream release cadence, independent vote gathering or November access. Shared AP presentations are one upstream chain.')
    target = O / 'review.json'
    value = (json.dumps(out, indent=2) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == value
    else:
        target.write_bytes(value)
    print(json.dumps(dict(path=str(target.relative_to(S)), bytes=len(value), sha256=sha(value))))


if __name__ == '__main__':
    main()
