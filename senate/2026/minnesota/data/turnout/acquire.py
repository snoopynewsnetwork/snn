"""Bounded original public-source acquisition; never changes shared evidence."""
import datetime, gzip, hashlib, json, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'source'
BASE = 'https://www.sos.mn.gov/elections-voting/election-results/'
URLS = {
    **{f'{y}-statistics': f'{BASE}{y}/{y}-general-election-results/{y}-election-statistics/' for y in [2024, 2022, 2020]},
    **{f'{y}-results': f'{BASE}{y}/{y}-general-election-results/' for y in [2024, 2022, 2020]},
    **{f'{y}-precinct-index': f'{BASE}{y}/{y}-general-election-results/{y}-precinct-results-spreadsheet/' for y in [2024, 2022, 2020]},
    '2026-ballot': 'https://www.sos.mn.gov/elections-voting/whats-on-my-ballot/',
    'senate-class-II': 'https://www.senate.gov/senators/Class_II.htm',
    'senate-class-I': 'https://www.senate.gov/senators/Class_I.htm',
    **{f'{y}-statistics-nonwww': f'{BASE}{y}/{y}-general-election-results/{y}-election-statistics/'.replace('www.sos.mn.gov','sos.mn.gov') for y in [2022,2020]},
}

def digest(b): return hashlib.sha256(b).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for sid, url in URLS.items():
        # Existing captures stay immutable unless the operator explicitly removes them.
        old = json.loads((OUT/'acquisition.json').read_text()) if (OUT/'acquisition.json').exists() else []
        prior = next((r for r in old if r['id']==sid),None)
        if prior:
            records.append(prior);continue
        at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        redirects=[]
        class Redirects(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                redirects.append(dict(url=req.full_url,http_status=code,headers=dict(headers),location=newurl))
                return super().redirect_request(req, fp, code, msg, headers, newurl)
        opener=urllib.request.build_opener(Redirects())
        req = urllib.request.Request(url, headers={'User-Agent': 'MN-election-research/1.0', 'Accept-Encoding': 'identity'})
        try:
            with opener.open(req, timeout=45) as response:
                raw = response.read()
                record = dict(id=sid, requested_url=url, final_url=response.url,
                              retrieved_utc=at, http_status=response.status, headers=dict(response.headers),redirects=redirects)
            assert len(raw) < 40_000_000
            packed = gzip.compress(raw, mtime=0)
            path = OUT / f'{sid}.html.gz'
            path.write_bytes(packed)
            record.update(path=str(path.relative_to(HERE)), raw_bytes=len(raw), raw_sha256=digest(raw),
                          stored_bytes=len(packed), stored_sha256=digest(packed),
                          content_check='primary_page' if b'Minnesota Secretary Of State -' in raw[:1000] else ('bot_challenge' if b'Radware' in raw or b'perfdrive' in raw or b'botmanager' in raw else 'inspect_content'))
        except Exception as e:
            record = dict(id=sid, requested_url=url, retrieved_utc=at, error=str(e))
        records.append(record)
        print(sid, record.get('http_status'), record.get('raw_bytes'), record.get('content_check'), flush=True)
    (OUT / 'acquisition.json').write_text(json.dumps(records, indent=2)+'\n')

if __name__ == '__main__': main()
