#!/usr/bin/env python3
"""Independent original OOXML audit of annotated Montezuma counts.

Retains the earlier numeric-only preflight as a dated, lossless witness.
No producer imports, candidate allocation or current geographic join.
"""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import io
import json
import re
import zipfile
import xml.etree.ElementTree as E

D = Path(__file__).resolve().parent
S = D.parent
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def main():
    prior_paths = ['preflight_primary_sources.py', 'coordinator-primary-preflight.json',
                   'coordinator-source-preflight.md']
    history = D / 'coordinator-history/annotated-count-interpretation-v1'
    witness = history / 'prior-pins.json'
    if not witness.exists():
        history.mkdir(parents=True, exist_ok=True)
        entries = []
        for name in prior_paths:
            p = D / name
            original = p.read_bytes()
            stored = gzip.compress(original, mtime=0)
            target = history / (name + '.gz')
            target.write_bytes(stored)
            entries.append(dict(original=pin(p), lossless_stored=pin(target)))
        witness.write_text(json.dumps(dict(scope='Prior coordinator interpretation, preserved before correction',
                                          files=entries), indent=2) + '\n')
    frozen = json.loads(witness.read_bytes())
    for entry in frozen['files']:
        p = S / entry['lossless_stored']['path']
        b = p.read_bytes()
        assert pin(p) == entry['lossless_stored']
        raw = gzip.decompress(b)
        assert len(raw) == entry['original']['bytes'] and sha(raw) == entry['original']['sha256']
    earlier = json.loads((D / 'coordinator-primary-preflight.json').read_bytes())
    source = earlier['source']
    p = D / 'news' / source['asset']
    stored = p.read_bytes()
    raw = gzip.decompress(stored)
    assert sha(stored) == source['stored_sha256'] and sha(raw) == source['raw_sha256']
    assert len(raw) == source['bytes']
    z = zipfile.ZipFile(io.BytesIO(raw))
    assert z.testzip() is None
    shared = [''.join(si.itertext()) for si in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS)]
    numeric = Counter()
    inclusive = Counter()
    missing = Counter()
    annotations = []
    complete_rows = []
    footnotes = []
    counties = set()
    with z.open('xl/worksheets/sheet1.xml') as stream:
        for _, row in E.iterparse(stream, events=['end']):
            if row.tag != '{' + NS['m'] + '}row':
                continue
            number = int(row.attrib['r'])
            cells = {}
            for c in row:
                v = c.find('m:v', NS)
                if v is None:
                    continue
                v = v.text
                cells[re.sub('[0-9]', '', c.attrib['r'])] = dict(
                    type=c.get('t'), raw_v=v, text=shared[int(v)] if c.get('t') == 's' else v,
                    source_cell=c.attrib['r'])
            row.clear()
            # All actual native records and explanatory rows precede the error tail.
            # The complete source and dated full-tail preflight remain pinned.
            if number >= 3546:
                break
            text = {col: c['text'] for col, c in cells.items()}
            if 'A' in text and 'B' in text and text['B'].isdigit():
                counties.add(text['A'])
                values = {}
                for col in 'CDEF':
                    value = text.get(col, '')
                    annotated = re.fullmatch(r'([0-9]+)\*', value)
                    if value.isdigit():
                        numeric[col] += int(value)
                        inclusive[col] += int(value)
                        values[col] = int(value)
                    elif annotated:
                        parsed = int(annotated[1])
                        inclusive[col] += parsed
                        values[col] = parsed
                        annotations.append(dict(row=number, column=col, county=text['A'],
                                                native_literal=text['B'], original=cells[col],
                                                parsed_annotated_count=parsed, plain_numeric_lane=None))
                    else:
                        missing[col] += 1
                        values[col] = None
                complete_rows.append(dict(source_row=number, county_literal=text['A'],
                                          native_literal=text['B'], annotated_inclusive_known=values))
            elif any('Due to an error' in x for x in text.values()):
                footnotes.append(dict(source_row=number, complete_original_cells=cells))
    assert len(complete_rows) == 3183 and len(counties) == 64
    assert len(annotations) == 8 and {a['row'] for a in annotations} == {2632, 2633}
    assert {a['county'] for a in annotations} == {'Montezuma'}
    assert all(a['original']['type'] == 's' for a in annotations)
    assert numeric == Counter(earlier['state_known_numeric_sums'])
    assert inclusive == Counter(C=4074612, D=508668, E=4583280, F=3241155)
    assert inclusive['C'] + inclusive['D'] == inclusive['E']
    assert len(footnotes) == 1 and footnotes[0]['source_row'] == 3185
    assert not any(missing[col] for col in 'CEF')
    output = dict(status='pass_independent_annotated_source_count_correction',
                  source_receipt=source, complete_stored_original=pin(p),
                  complete_raw_original=dict(bytes=len(raw), sha256=sha(raw)),
                  prior_interpretation_witness=pin(witness),
                  prior_preflight_unchanged=pin(D / 'coordinator-primary-preflight.json'),
                  native_source_records=3183, literal_county_parents=64,
                  original_annotated_cells=annotations, complete_original_footnote=footnotes,
                  plain_numeric_known_sums=dict(numeric),
                  separately_parsed_annotated_count_additions={c: inclusive[c] - numeric[c] for c in 'CDEF'},
                  annotated_inclusive_known_sums=dict(inclusive), remaining_unprinted_fields=dict(missing),
                  complete_native_source_count_lanes=complete_rows,
                  candidate_priority_changed=False, current_geography_approved=False,
                  qualification='The eight shared strings contain explicit integer counts and literal asterisks. '
                                'Their separate annotated lane corrects the earlier missing-source-count interpretation. '
                                'Remaining blank fields remain null. Neither source-lane totals nor the relocation '
                                'footnote allocate votes or establish an approved physical/current precinct crosswalk.')
    target = D / 'coordinator-annotated-turnout-review.json'
    target.write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(pin(target)))


if __name__ == '__main__':
    main()
