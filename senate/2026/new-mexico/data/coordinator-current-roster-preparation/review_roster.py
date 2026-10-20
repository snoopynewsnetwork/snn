"""Bounded official general-roster snapshot; no historical votes or feed join."""
from pathlib import Path
import gzip
import hashlib
import json
from bs4 import BeautifulSoup

D = Path(__file__).resolve().parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=p.name, bytes=len(b), sha256=sha(b))


def main():
    r = json.loads((D / 'linked-candidate-list.receipt.json').read_bytes())
    for item in r['hops']:
        b = item['body']
        z = (D / b['path']).read_bytes()
        assert len(z) == b['stored_bytes'] and sha(z) == b['stored_sha256']
        raw = gzip.decompress(z)
        assert len(raw) == b['raw_bytes'] and sha(raw) == b['raw_sha256']
    soup = BeautifulSoup(raw, 'html.parser')
    grid = soup.find('table', id='ctl00_MainContent_rgCandidate_ctl00')
    assert grid is not None
    headers = [dict(raw_text=c.get_text(), attributes=dict(c.attrs)) for c in grid.find_all('th')]
    selected = []
    all_rows = grid.find_all('tr')
    for ordinal, tr in enumerate(all_rows, 1):
        cells = tr.find_all('td', recursive=False)
        if cells and cells[0].get_text(' ', strip=True) == 'United States Senator':
            selected.append(dict(table_row_1based=ordinal, row_attributes=dict(tr.attrs),
                                 cells=[dict(column_1based=i, attributes=dict(c.attrs), raw_text=c.get_text()) for i,c in enumerate(cells,1)]))
    assert len(selected) == 4
    values = [[c['raw_text'].strip() for c in r['cells']] for r in selected]
    assert any('BEN R LUJAN' in v and 'DEM' in v and 'Qualified' in v for v in values)
    assert any('LARRY E MARKER' in v and 'REP' in v and 'Qualified' in v for v in values)
    o = dict(status='pass_bounded_actual_current_general_candidate_portal_source_snapshot',
             source_receipt=pin(D / 'linked-candidate-list.receipt.json'), full_raw_body=r['body'],
             parent_receipt=pin(D / 'sos-home.receipt.json'),
             literal_title=soup.title.get_text(), full_headers=headers, Senate_rows=selected,
             portal_table_rows_including_headers_and_pagers=len(all_rows),
             source_names_and_parties=[dict(name=v[4], party=v[8], status=v[21],
                                           literal_ballot_order=v[20], filing_clock_literal=v[19],
                                           filing_clock_timezone=None) for v in values],
             limits='Current official General Election Contest/Candidate List snapshot only. All source cells remain in original body and selected Senate rows. No signed ballot/final later amendment/writein exhaustion or current result-choice ID approval; primary writein history is not a general-ballot flag. No votes, worker launch or priority acceptance.',
             source_clock_timezone_unknown=True, current_feed_or_geography_approved=False)
    (D / 'review.json').write_text(json.dumps(o, indent=2)+'\n')
    inventory = [pin(p) for p in sorted(D.iterdir()) if p.is_file() and p.name != 'acquisition-complete-v1.json']
    (D / 'acquisition-complete-v1.json').write_text(json.dumps(dict(scope='Bounded two-GET original-source preparation only', exact_files=inventory, no_question_worker_launched=True), indent=2)+'\n')
    print(json.dumps(dict(Senate_rows=4, Qualified=2, Disqualified=2, raw_bytes=len(raw), full_raw_sha256=sha(raw), review=pin(D/'review.json'))))


if __name__ == '__main__':
    main()
