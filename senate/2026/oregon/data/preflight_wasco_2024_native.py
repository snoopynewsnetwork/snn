"""Check one observed complete official county original, not statewide coverage."""
from pathlib import Path
import collections
import gzip
import hashlib
import json
import re
import subprocess
import tempfile

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
QA = DATA / 'qa/wasco-2024-native-original'
NAMES = ['Robert F Kennedy Jr / Nicole Shanahan', 'Cornel West',
         'Chase Oliver / Mike ter Maat', 'Randall Terry',
         'Donald J Trump / JD Vance', 'Jill Stein / Rudolph Ware',
         'Kamala D Harris / Tim Walz', 'Write-in', 'Total', 'Overvotes', 'Undervotes']


def sha(body):
    return hashlib.sha256(body).hexdigest()


def pin(path):
    body = path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)), bytes=len(body), sha256=sha(body))


def keep(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == body, ('Previously retained derivative changed', path)
    else:
        path.write_bytes(body)
    return pin(path)


def main():
    manifest = json.loads((DATA / 'news/manifest.json').read_bytes())
    source = next(r for r in manifest if r['id'] == 'sos-observed-2024-wasco-native-original')
    stored = (DATA / 'news' / source['asset']).read_bytes()
    raw = gzip.decompress(stored)
    assert sha(stored) == source['stored_sha256']
    assert (len(raw), sha(raw)) == (525495, 'cfc1366731321f860e51c232e6f87eb3a4295f80bc2930eb91ddb212037db77d')
    assert source['status'] == 200 and source['bytes'] == len(raw)
    assert source['headers']['Content-Length'] == str(len(raw))
    assert raw.startswith(b'%PDF-') and raw.rstrip().endswith(b'%%EOF')
    QA.mkdir(parents=True, exist_ok=True)
    renders = []
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / 'original.pdf'
        pdf.write_bytes(raw)
        info = subprocess.check_output(['pdfinfo', '-rawdates', str(pdf)]).decode()
        assert re.search(r'Pages:\s+46\b', info)
        text = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-']).decode()
        for page in [1, 5, 28, 46]:
            prefix = Path(tmp) / f'page-{page}'
            subprocess.run(['pdftoppm', '-f', str(page), '-singlefile', '-r', '120',
                            '-png', str(pdf), str(prefix)], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            renders.append(dict(actual_PDFpage=page, dpi=120,
                                original_render=keep(QA / f'page-{page}-original.png',
                                                     prefix.with_suffix('.png').read_bytes())))
    textpin = keep(QA / 'whole-original-layout-text.txt.gz', gzip.compress(text.encode(), mtime=0))
    pages = text.split('\f')
    assert len(pages) == 47 and not pages[0].strip() and not pages[-1].strip()
    lines = [(p, n, line) for p, page in enumerate(pages, 1)
             for n, line in enumerate(page.splitlines(), 1)]
    # The signed/stamped first page is image-only. These fields were read from
    # the complete original raster; no blind-to-existing-county-controls claim.
    first = dict(source_label_literal='Precinct 01', actual_PDFpages=[1],
                 reading_basis='Direct complete original-page visual reading; page1 has no extractable text',
                 ballot_header_raw='1831 ballots (2 over voted ballots, 2 overvotes, 16 undervotes), 2977 registered voters, turnout 61.50%',
                 ballots=1831, over_voted_ballots=2, header_overvotes=2,
                 header_undervotes=16, registration=2977, turnout_percent_literal='61.50%',
                 choices=[dict(source_name_literal=name, votes=value, actual_PDFpage=1,
                               reading_basis='Direct complete original raster')
                          for name, value in zip(NAMES, [35, 3, 14, 1, 901, 12, 842, 5, 1813, 2, 16])])
    records = [first]
    for index, (page, ordinal, line) in enumerate(lines):
        if line.strip() != 'United States President and Vice President (Vote for 1)':
            continue
        label = next(a.strip() for _, _, a in reversed(lines[:index])
                     if re.fullmatch(r'Precinct \d+', a.strip()))
        hp, hn, header = lines[index + 1]
        m = re.fullmatch(r'\s*(\d+) ballots \((\d+) over voted ballots, (\d+) overvotes, (\d+) undervotes\), (\d+) registered voters, turnout (\d+\.\d+%)\s*', header)
        assert m, header
        choices = []
        for pp, nn, value_line in lines[index + 2:]:
            cm = re.fullmatch(r'\s*(.*?)\s+(\d+)\s*(\d+\.\d+%)?\s*', value_line)
            if cm and cm[1] in NAMES:
                assert cm[1] == NAMES[len(choices)], (label, cm[1], choices)
                choices.append(dict(source_name_literal=cm[1], votes=int(cm[2]),
                                    actual_PDFpage=pp, text_line=nn, raw_line=value_line,
                                    printed_percent_literal=cm[3]))
            if len(choices) == len(NAMES):
                break
        assert len(choices) == 11
        records.append(dict(source_label_literal=label,
                            actual_PDFpages=sorted({page, *[r['actual_PDFpage'] for r in choices]}),
                            reading_basis='Original PDF text layer, cross-page running headers excluded; representative full originals visually checked',
                            heading_actual_PDFpage=page, heading_text_line=ordinal,
                            ballot_header_actual_PDFpage=hp, ballot_header_text_line=hn,
                            ballot_header_raw=header, ballots=int(m[1]),
                            over_voted_ballots=int(m[2]), header_overvotes=int(m[3]),
                            header_undervotes=int(m[4]), registration=int(m[5]),
                            turnout_percent_literal=m[6], choices=choices))
    assert [r['source_label_literal'] for r in records] == [f'Precinct {n:02d}' for n in range(1, 13)]
    sums = collections.Counter()
    for r in records:
        values = [c['votes'] for c in r['choices']]
        assert sum(values[:8]) == values[8]
        assert values[9:] == [r['header_overvotes'], r['header_undervotes']]
        assert values[8] + values[9] + values[10] == r['ballots']
        assert r['over_voted_ballots'] == r['header_overvotes']
        for name, value in zip(NAMES, values):
            sums[name] += value
    assert sum(r['ballots'] for r in records) == 13527
    assert sum(r['registration'] for r in records) == 19064
    abstract_path = DATA / 'coordinator-primary-preflight.json'
    abstract = json.loads(abstract_path.read_bytes())
    county = next(r for r in abstract['county_rows'] if r['county_literal'] == 'Wasco')
    assert [sums[n] for n in NAMES[:8]] == county['values'] == [251, 15, 73, 14, 6837, 81, 6069, 51]
    out = dict(status='pass_bounded_complete_original_Wasco2024_presidential_native_exemplar_only',
               original_response_receipt=source, complete_original_EOF=True, actual_PDF_pages=46,
               original_pdfinfo_rawdates=info, original_text_derivative=textpin,
               complete_original_renders=renders, records=records,
               source_native_contexts=12, candidate_positions=96,
               explicit_Total_Overvotes_Undervotes_positions=36,
               county_source_choice_sums=dict(sums), source_ballots=13527,
               source_registration=19064, source_overvotes=8, source_undervotes=128,
               county_abstract_comparison=dict(input=pin(abstract_path), county_row=county,
                                              numeric_eight_column_comparisons=8, differences=0),
               first_page_original_reading=dict(signed_name_literal='Lisa Gambee',
                                               title_literal='Wasco County Clerk',
                                               certification_date_printed='27th day of November, 2024',
                                               printed_report_clock='2024-11-27 11:28:45',
                                               printed_clock_zone=None,
                                               page1_President_ballots=1831,
                                               page1_other_contests_include_ballots1830=True),
               qualification='One observed county original, not all36 native counties. Twelve literal Precinct labels are source-scoped; no numeric backend IDs, method split or current/cross-year geography is inferred. All Counter Groups is the printed report scope, not a method allocation. Write-in51 numerically equals the abstract Misc.51, without proving valid named-write-in eligibility/allocation. Contests elsewhere on page1 print1830 ballots while President/House print1831; source contest-specific ballot fields remain distinct. PDF metadata, printed report clock, HTTP Last-Modified and retrieval clock are retained separately. Page1 was visually transcribed; other eleven presidential blocks use the complete source text layer, including page continuations. Representative full original pages1/5/28/46 were visually inspected; no claim all46 pages were glyph-reviewed.',
               statewide_native_complete=False, current_geography_approved=False,
               formal_priority_accepted=False)
    result = keep(DATA / 'coordinator-wasco-2024-native-preflight.json',
                  (json.dumps(out, indent=2) + '\n').encode())
    print(json.dumps(dict(output=result, native_contexts=12, source_candidate_positions=96,
                          candidate_sums=[sums[n] for n in NAMES[:8]], ballots=13527)))


if __name__ == '__main__':
    main()
