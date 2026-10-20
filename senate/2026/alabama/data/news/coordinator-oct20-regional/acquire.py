"""One bounded public newsroom observation per source; never a live collector."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
import datetime
import gzip
import hashlib
import json
import re
import requests

H = Path(__file__).resolve().parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def write(p, v):
    p.write_text(json.dumps(v, indent=2, ensure_ascii=False) + '\n')


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.active = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and a.get('href'):
            self.active = dict(href=a['href'], text='')
            self.rows.append(self.active)

    def handle_endtag(self, tag):
        if tag == 'a':
            self.active = None

    def handle_data(self, text):
        if self.active is not None:
            self.active['text'] += text


def main():
    jobs = [
        ('wtvy-results', 'https://www.wtvy.com/politics/election-results/', 'Exact primary publisher results page search result; cached special-primary text is distinct from current raw config'),
        ('wtvy-may-primary-report', 'https://www.wtvy.com/2026/05/20/decision-2026-primary-results-across-area-state/', 'Exact primary WTVY May19 reporting search result'),
        ('lagniappe-current-public-preview', 'https://www.lagniappemobile.com/news/alabama/election_2026/voters-to-decide-on-school-prayer-pledge-taxes/article_0ef75690-a78e-4559-87ec-b6a2cdda426c.html', 'Exact primary publisher September15 public article preview; protected or encoded body is not decoded or bypassed'),
    ]
    for name, url, source in jobs:
        p = H / (name + '.receipt.json')
        if p.exists():
            continue
        row = dict(id=name, source=source, requested_url=url, requested_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), hops=[])
        try:
            current = url
            for i in range(6):
                r = requests.get(current, headers={'User-Agent': 'Public election research; bounded newsroom request', 'Accept-Encoding': 'identity'}, timeout=(15, 35), allow_redirects=False)
                raw = r.content
                assert len(raw) < 40000000, 'Complete response exceeds artifact cap'
                compressed = gzip.compress(raw, mtime=0)
                body = H / (sha(raw) + '.html.gz')
                if body.exists():
                    assert gzip.decompress(body.read_bytes()) == raw
                else:
                    body.write_bytes(compressed)
                row['hops'].append(dict(url=r.url, request_headers=dict(r.request.headers), status=r.status_code, reason=r.reason, response_headers=list(r.raw.headers.items()), body_path=body.name, raw_bytes=len(raw), raw_sha256=sha(raw), stored_bytes=body.stat().st_size, stored_sha256=sha(body.read_bytes())))
                if r.status_code in [301, 302, 303, 307, 308] and r.headers.get('Location'):
                    dest = urljoin(r.url, r.headers['Location'])
                    if re.search(r'/(login|signin|sign-in|account|subscribe|subscription|auth)(/|\?|$)', urlsplit(dest).path, re.I):
                        row['unfollowed_access_redirect'] = dest
                        break
                    current = dest
                    continue
                row['status'] = r.status_code
                row['final_url'] = r.url
                parser = Links()
                parser.feed(raw.decode(r.encoding or 'utf-8', errors='replace'))
                links = [dict(literal_href=x['href'], url=urljoin(r.url, x['href']), text=' '.join(x['text'].split())) for x in parser.rows if re.search(r'election|vot(e|ing)|politic|senate', x['href'] + ' ' + x['text'], re.I)]
                write(H / (name + '.election-links.json'), links)
                break
        except Exception as exc:
            row['client_error'] = repr(exc)
        row['completed_UTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        write(p, row)
        print(name, row.get('status'), row.get('client_error', ''), flush=True)


if __name__ == '__main__':
    main()
