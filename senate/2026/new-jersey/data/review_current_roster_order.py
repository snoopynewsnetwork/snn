"""Bounded coordinator original roster/certification/CD7-order scope review."""
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser
import gzip
import hashlib
import json
import re
import requests
import fitz

S = Path(__file__).resolve().parents[1]
H = S / 'data/results-sources'
O = S / 'data/coordinator-current-roster-order-review'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


class Text(HTMLParser):
    def __init__(self, b):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.feed(b.decode('utf-8-sig', 'replace'))
    def handle_data(self, d):
        self.parts.append(d)


def main():
    O.mkdir(exist_ok=True)
    docs = []
    for key, count in [('general-original-62', 5), ('general-original-63', 3),
                       ('general-original-64', 20), ('leguia-scotus-docket', None)]:
        p = H / 'requests' / (key+'.json')
        r = json.loads(p.read_bytes())
        z = gzip.compress(p.read_bytes(), mtime=0)
        frozen = O / (key+'.receipt.json.gz')
        if not frozen.exists():
            frozen.write_bytes(z)
        else:
            assert gzip.decompress(frozen.read_bytes()) == p.read_bytes()
        hop = r['hops'][-1]
        body_path = H / hop['asset']
        b = body_path.read_bytes()
        assert len(b) == hop['stored_bytes'] and sha(b) == hop['stored_sha256']
        raw = gzip.decompress(b)
        assert len(raw) == hop['raw_bytes'] and sha(raw) == hop['raw_sha256'] and hop['status'] == 200
        row = dict(id=key, frozen_exact_receipt=pin(frozen), original_body=pin(body_path),
                   raw_bytes=len(raw), raw_sha256=sha(raw), requested_url=r['requested_url'])
        if count is not None:
            pdf = fitz.open(stream=raw, filetype='pdf')
            assert len(pdf) == count
            text = '\f'.join(page.get_text() for page in pdf)
            out = O / (key+'.complete-text.txt.gz')
            out.write_bytes(gzip.compress(text.encode(), mtime=0))
            row.update(complete_pages=count, complete_automated_text=pin(out),
                       selected_actually_viewed_original_PDF_pages=[1])
            if key == 'general-original-62':
                assert 'denotes incumbent' in text and all(n in text for n in ['CORY BOOKER', 'JUSTIN MURPHY', 'VERONICA FERNANDEZ', 'JOANNE KUNIANSKY'])
        docs.append(row)
    # Exactly the public docket URL actually observed in the primary search.
    url = 'https://www.supremecourt.gov/search.aspx?filename=%2Fdocket%2Fdocketfiles%2Fhtml%2Fpublic%2F26A358.html'
    started = datetime.now(timezone.utc).isoformat()
    result = dict(requested_url=url, method='GET', started_utc=started, hops=[], status=None, error=None)
    try:
        current = url
        for _ in range(8):
            response = requests.get(current, timeout=(20,45), allow_redirects=False)
            raw = response.content
            same = next((d for d in docs if d['raw_sha256'] == sha(raw)), None)
            if same:
                stored = same['original_body']
            else:
                p = O / (sha(raw)+'.gz')
                p.write_bytes(gzip.compress(raw, mtime=0))
                stored = pin(p)
            result['hops'].append(dict(actual_requested_url=response.url, status=response.status_code,
                                       request_headers=dict(response.request.headers), response_headers=dict(response.headers),
                                       raw_bytes=len(raw), raw_sha256=sha(raw), complete_stored_body=stored))
            result['status'] = response.status_code
            if not response.is_redirect:
                break
            from urllib.parse import urljoin
            current = urljoin(response.url, response.headers['Location'])
        else:
            raise RuntimeError('bounded redirect limit')
        t = Text(raw)
        text = re.sub(r'\s+', ' ', ' '.join(t.parts))
        result['actual_docket_and_denial_observed'] = all(v in text for v in ['26A358', 'Lana Leguia', 'Sep 18 2026', 'denied by Justice Alito'])
    except Exception as e:
        result['error'] = str(e)
    result['finished_utc'] = datetime.now(timezone.utc).isoformat()
    p = O / 'coordinator-docket-recheck.json'
    p.write_text(json.dumps(result, indent=2)+'\n')
    views = [pin(H / 'viewed-pages' / (key+'-p1.png')) for key in ['general-original-62','general-original-63','general-original-64']]
    review = dict(status='pass_bounded_actual_three_page_roster_certification_amendment_review',
                  whole_originals=docs, coordinator_fresh_public_docket_request=pin(p),
                  actual_visual_scope=views,
                  scoped_observations=[
                      'Roster p1 actually prints * denotes incumbent; this resolves Booker asterisk for this current roster only, not historical source flags.',
                      'Scanned signed July27,2026 certification p1 actually covers November3 Senate and House nominees; complete20page original retained.',
                      'Scanned signed September4,2026 amended certification p1 concerns LanaLeguia/HouseDistrict7/AppDivA3541-25 only, not a Senate removal.',
                      'Actual26A358 docket describes a September18 stay-application denial byJusticeAlito in LanaLeguia vNJRepublicanStateCommittee; no Senate remedy or full later-docket exhaustion inferred.'],
                  no_entire_document_manual_visual_claim=True, no_producer_mutation=True,
                  source_scope='Individual exact source bodies/receipts only. No unfinished worker aggregate, source-field normalization, signed-later roster exhaustion, current-feed/geography/choice-ID or November vote approval.')
    p = O / 'review.json'
    p.write_text(json.dumps(review, indent=2)+'\n')
    print(json.dumps(dict(review=pin(p), fresh_docket_status=result['status'], actual_fresh_denial_observed=result.get('actual_docket_and_denial_observed'))))


if __name__ == '__main__':
    main()
