"""Original ISBE/FEC source-scope comparison, with no native allocation."""
from pathlib import Path
import gzip
import hashlib
import json
import re
import subprocess
from urllib.parse import urljoin
from bs4 import BeautifulSoup

N = Path(__file__).resolve().parent
D = N.parent
S = D.parent
O = N / 'coordinator-federal-controls'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    p = O / 'acquisition-complete-v1.json'
    if not p.exists():
        p.write_bytes((O / 'acquisition.json').read_bytes())
    acquisition = {e['id']: e for e in json.loads(p.read_bytes())}
    bodies = {}
    for key, e in acquisition.items():
        z = (S / e['asset_path']).read_bytes()
        b = gzip.decompress(z)
        assert sha(z) == e['stored_sha256'] and len(z) == e['stored_bytes']
        assert sha(b) == e['raw_sha256'] and len(b) == e['raw_bytes']
        assert e['status'] == 200
        bodies[key] = b
    parent = BeautifulSoup(bodies['fec-parent'], 'html.parser')
    assert any(urljoin(acquisition['fec-parent']['final_url'], a['href']) == acquisition['fec-2024-president-pdf']['url']
               for a in parent.find_all('a', href=True))
    layout = subprocess.run(['pdftotext', '-layout', '-', '-'], input=bodies['fec-2024-president-pdf'], stdout=subprocess.PIPE, check=True).stdout
    assert gzip.decompress((O / 'FEC2024-complete-layout.txt.gz').read_bytes()) == layout
    ilrows = []
    for page, text in enumerate(layout.decode().split('\f'), 1):
        for line in text.splitlines():
            if re.match(r'^IL\s', line):
                ilrows.append(dict(page=page, complete_literal_layout_row=line))
    assert len(ilrows) == 6
    assert re.findall(r'[\d,]+', ilrows[5]['complete_literal_layout_row']) == ['1,569', '518', '5,633,310']
    ledger = {e['id']: e for e in json.loads((N / 'manifest.json').read_bytes())}
    source = ledger['sos-observed-2024-federal-statewide-page']
    z = (N / source['asset']).read_bytes()
    raw = gzip.decompress(z)
    assert sha(z) == source['stored_sha256'] and sha(raw) == source['raw_sha256']
    dom = BeautifulSoup(raw, 'html.parser')
    title = dom.find(string=lambda s: s and s.strip() == 'PRESIDENT AND VICE PRESIDENT')
    table = title.find_parent('div').find_next('table')
    rows = []
    for tr in table.find_all('tr'):
        cells = [c.get_text(' ', strip=True) for c in tr.find_all(['th', 'td'])]
        if not cells or cells[0] in ['Candidate', 'Vote Totals']:
            continue
        assert len(cells) == 4
        rows.append(dict(literal_candidate=cells[0], literal_party=cells[1], literal_votes=cells[2],
                         votes=int(cells[2].replace(',', '')), literal_percentage=cells[3]))
    assert len(rows) == 27 and sum(r['votes'] for r in rows) == 5633310
    byname = {r['literal_candidate']: r['votes'] for r in rows}
    three = ['Kamala D. Harris', 'Donald J. Trump', 'Robert F. Kennedy Jr.']
    seven = ['Jill Stein', 'Chase Oliver', 'Claudia De La Cruz', 'Cornel West', 'Peter Sonski', 'Shiva Ayyadurai', 'Joseph Kishore']
    remainder = [r for r in rows if r['literal_candidate'] not in three + seven]
    assert sum(byname[n] for n in three) == 5592368
    assert sum(byname[n] for n in seven) == 40424
    assert len(remainder) == 17 and sum(r['votes'] for r in remainder) == 518
    x = dict(status='pass_bounded_original_FEC_ISBE_statewide_scope_reconciliation',
             complete_immutable_FEC_receipts=[acquisition[k] for k in acquisition], complete_ISBE_original_reference=source,
             complete_literal_ISBE_rows=rows, complete_literal_FEC_IL_rows=ilrows,
             reported_statewide_total=5633310, three_shared_printed_candidate_total=5592368,
             seven_additional_source_names_total=40424, other17ISBE_source_rows_total=518,
             FEC_page6_literal_scattered_writein_total=518, unallocated_native_generic_total=57411,
             native_generic_minus_state_additional_source_rows=16469,
             actually_viewed='Complete original FEC PDFpage6 raster; ILrow printsWest1569/scattered518/total5633310. Other pages independently text-inspected, not visually claimed.',
             qualifications=['FEC compilation identifies state election offices as source; it is an independent federal publication, not independent underlying votes or a new state certification.',
                             'State17row sum equalsFECscattered518; this arithmetic does not approve individual candidate aliases, running-mate aggregation, eligibility or a crosswalk.',
                             'All27source labels/parties/percentages remain literal; no16,469gap allocation or native write-in distribution inferred. This is preparation, not final priority or current IDs.'])
    target = O / 'review.json'
    value = (json.dumps(x, indent=2) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == value
    else:
        target.write_bytes(value)
    print(json.dumps(dict(path=str(target.relative_to(S)), bytes=len(value), sha256=sha(value))))


if __name__ == '__main__':
    main()
