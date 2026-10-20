"""Bounded coordinator raw-source key/category diagnostic; no priority approval."""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json

D = Path(__file__).resolve().parent
N = D / 'news'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    pinpath = D / 'coordinator-native-category-source-pin.json'
    if pinpath.exists():
        source = json.loads(pinpath.read_bytes())
    else:
        source = next(e for e in json.loads((N / 'manifest.json').read_bytes()) if e['id'] == 'sos-2024-president-csv')
        pinpath.write_text(json.dumps(source, indent=2) + '\n')
    stored = (N / source['asset']).read_bytes()
    raw = gzip.decompress(stored)
    assert sha(stored) == source['stored_sha256'] and sha(raw) == source['raw_sha256'] and len(raw) == source['bytes']
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    headers = reader.fieldnames
    rows = [dict(source_CSV_line=i, fields=r) for i, r in enumerate(reader, 2)]
    assert len(rows) == 59623 and len(headers) == 12
    names = Counter()
    group = defaultdict(list)
    full = set()
    for row in rows:
        r = row['fields']
        names[r['CandidateName']] += int(r['VoteCount'])
        group[(r['JurisdictionID'], r['PrecinctName'])].append(row)
        full.add((r['JurisdictionID'], r['JurisContainerID'], r['JurisName'], r['PrecinctName']))
    printed = ['Kamala D. Harris', 'Donald J. Trump', 'Robert F. Kennedy Jr.']
    assert [names[n] for n in printed] == [3062863, 2449079, 80426]
    count_by_candidate = {}
    for name in printed:
        selected = [r for r in rows if r['fields']['CandidateName'] == name]
        keys = [(r['fields']['JurisdictionID'], r['fields']['PrecinctName']) for r in selected]
        assert len(keys) == len(set(keys))
        count_by_candidate[name] = len(keys)
    unavailable = []
    no_printed = []
    for (authority, precinct), values in group.items():
        have = {r['fields']['CandidateName'] for r in values}
        item = dict(authority_ID=authority, literal_precinct=precinct, missing_printed_names=[n for n in printed if n not in have], full_original_rows=values)
        if not have.intersection(printed):
            no_printed.append(item)
        elif any(n not in have for n in printed):
            unavailable.append(item)
    assert len(full) == 11535 and len(group) == 10062
    assert len(no_printed) == 4 and all(e['literal_precinct'] == '' for e in no_printed)
    assert len(unavailable) == 15 and all(e['missing_printed_names'] == ['Robert F. Kennedy Jr.'] for e in unavailable)
    out = dict(status='pass_bounded_original_native_category_diagnostic_only', source_pin='coordinator-native-category-source-pin.json',
               complete_original_headers=headers, raw_rows=len(rows), authority_IDs=len({r['fields']['JurisdictionID'] for r in rows}),
               authority_container_name_precinct_contexts=len(full), authority_literal_precinct_grouping_contexts=len(group),
               source_printed_candidate_rows=count_by_candidate, raw_candidate_category_sums=dict(names),
               blank_precinct_nonprinted_only_contexts=no_printed, printed_candidate_missing_contexts=unavailable,
               source_grouping_scope='Diagnostic projection only. Raw container/name/category rows are all retained; no container or authority equivalence, physical crosswalk, legal eligibility or zero imputation is approved.',
               material_qualifications=['Four blank-precinct contexts publish generic write-in/under/over observations only, not zero named candidates:Marshall,Menard,Lawrence,CityofGalesburg.',
                                        'Fifteen printed-candidate contexts omit Kennedy rows; null source absence is not an observed zero despite statewide known-sum closure.',
                                        'City category rows can change container while authority+literalprecinct remains the same; preserve all original12fields/sourcepositions and establish compatibility explicitly.',
                                        'Statewide named write-ins and raw generic marks remain unallocated across native contexts. Priority/count/eligible-universe robustness awaits actual independent firstpair.'])
    p = D / 'coordinator-native-category-review.json'
    b = (json.dumps(out, indent=2) + '\n').encode()
    if p.exists():
        assert p.read_bytes() == b
    else:
        p.write_bytes(b)
    print(json.dumps(dict(path=str(p), bytes=len(b), sha256=sha(b), raw_rows=len(rows), no_printed_contexts=len(no_printed), missing_Kennedy_contexts=len(unavailable))))


if __name__ == '__main__':
    main()
