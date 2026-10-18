#!/usr/bin/env python3
"""Bounded, explicit public downloads; shared originals are referenced, never copied.

Run with one or more source IDs, or --all. Existing captures are immutable unless
--refresh is explicitly given. Failed HTTP bodies and redirect chains are retained.
"""
import argparse, datetime, gzip, json, urllib.error, urllib.request
from sources import HERE, sha

SPECS = {
    'senate-class-ii': ('https://www.senate.gov/senators/Class_II.htm', 'U.S. Senate official class roster: Marshall and2020 seat cycle'),
    'senate-class-iii': ('https://www.senate.gov/senators/Class_III.htm', 'U.S. Senate official class roster: Moran and2022 seat cycle'),
    'current-results-index': ('https://www.sos.ks.gov/elections/election-results.html', 'official root'),
    'statistics-index': ('https://www.sos.ks.gov/elections/election-statistics.html', 'SOS historical election statistics'),
    'results-data-page': ('https://www.sos.ks.gov/elections/election-results-data.html', 'current-results-index: 2024 Presidential Election Results Data'),
    'registration-index': ('https://www.sos.ks.gov/elections/voter-registration-statistics.html', 'current-results-index: Voter Registration Statistics'),
    'county-offices': ('https://www.sos.ks.gov/elections/county_election_officers.aspx', 'current-results-index: County Election Offices'),
    'turnout-2022': ('https://www.sos.ks.gov/elections/22elec/2022-General-Election-Turnout-Information.xlsx', 'current-results-index: 2022 General Election Turnout Information'),
    'certification-2024': ('https://sos.ks.gov/media/press-releases/2024/12-03-24-state-board-of-canvassers-certifies-kansas-general-election-results.html', 'SOS 2024 certification announcement'),
    'county-codes-2020': ('https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt', 'Census geographic codes reference'),
    'statute-25-1132': ('https://www.kslegislature.gov/li/b2025_26/statute/025_000_0000_chapter/025_011_0000_article/025_011_0032_section/025_011_0032_k/', 'Kansas Legislature current statutory section'),
    'statute-25-1220': ('https://www.kslegislature.gov/li/b2025_26/statute/025_000_0000_chapter/025_012_0000_article/025_012_0020_section/025_012_0020_k/', 'military/overseas: receipt deadline'),
    'advance-info': ('https://www.sos.ks.gov/elections/advance-voting-information.html', 'current-results-index: Advance Voting Information'),
    'uocava-info': ('https://www.sos.ks.gov/elections/military-overseas-citizens.html', 'current-results-index: Military and Overseas Citizens'),
    'statute-25-1221': ('https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_012_0000_article/025_012_0021_section/025_012_0021_k/', 'Article 12: federal services receipt'),
    'statute-25-1216': ('https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_012_0000_article/025_012_0016_section/025_012_0016_k/', 'uocava-info: electronic transmission'),
    'statute-25-1136': ('https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_011_0000_article/025_011_0036_section/025_011_0036_k/', 'Article 11: late ballots and provisional treatment'),
    'statute-25-3002': ('https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_030_0000_article/025_030_0002_section/025_030_0002_k/', 'Kansas canvass and write-in law'),
    'statistics-data': ('https://www.sos.ks.gov/elections/election-statistics-data.html', 'statistics-index: chart data'),
    'registration-2024-november': ('https://www.sos.ks.gov/elections/vr-statistics/2024/11-2024-Voter-Registration-Numbers-by-County.xlsx', 'registration-index: November 2024 county numbers'),
    'registration-2026-october': ('https://www.sos.ks.gov/elections/vr-statistics/2026/10-2026-Voter-Registration-Numbers-by-County.xlsx', 'registration-index: October 2026 county numbers'),
    'inactive-2026-october': ('https://www.sos.ks.gov/elections/vr-statistics/2026/Inactive-Voters/2026-10-01-Percentage-of-Inactive-Voters-by-County.xlsx', 'registration-index: October 2026 inactive county numbers'),
    'johnson-results-2024': ('https://www.jocoelection.org/elections/november-5-2024-general-election', 'Johnson County Election Office historical election page'),
    'sumner-results-index': ('https://www.sumnercountyks.gov/government/county_clerk/elections/election_results.php', 'Sumner county historical election results page'),
}

class Redirects(urllib.request.HTTPRedirectHandler):
    def __init__(self): self.chain = []
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append({'requested_url': req.full_url, 'status': code, 'headers': dict(headers.items()), 'location': newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch(source_id):
    url, parent = SPECS[source_id]
    redirects = Redirects()
    opener = urllib.request.build_opener(redirects)
    at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    request = urllib.request.Request(url, headers={'User-Agent': 'KansasHistoricalElectionResearch/1.0', 'Accept-Encoding': 'identity'})
    try:
        response = opener.open(request, timeout=45)
    except urllib.error.HTTPError as e:
        response = e
    except Exception as e:
        return {'id': source_id, 'requested_url': url, 'parent': parent, 'retrieved_at_utc': at, 'error': repr(e)}
    with response:
        wire = response.read()
        headers = dict(response.headers.items())
        encoding = response.headers.get('Content-Encoding', '').lower()
        raw = gzip.decompress(wire) if encoding == 'gzip' else wire
        stored = gzip.compress(raw, mtime=0)
        path = 'source/'+source_id+'.body.gz'
        assert len(stored) < 40_000_000
        (HERE/path).write_bytes(stored)
        return {'id': source_id, 'requested_url': url, 'final_url': response.geturl(), 'parent': parent,
                'retrieved_at_utc': at, 'status': response.status, 'headers': headers,
                'redirects': redirects.chain, 'response_body_sha256': sha(wire), 'response_body_bytes': len(wire),
                'content_decoding': encoding or 'identity', 'raw_sha256': sha(raw), 'raw_bytes': len(raw),
                'path': path, 'stored_sha256': sha(stored), 'stored_bytes': len(stored)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ids', nargs='*', choices=list(SPECS))
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    manifest = HERE/'source/acquisition.json'
    captures = {r['id']: r for r in json.loads(manifest.read_text())} if manifest.exists() else {}
    for source_id in SPECS if args.all else args.ids:
        if source_id not in captures or args.refresh:
            captures[source_id] = fetch(source_id)
            manifest.write_text(json.dumps(list(captures.values()), indent=2)+'\n')
        m = captures[source_id]
        print(source_id, m.get('status'), m.get('raw_bytes'), m.get('error', ''))
