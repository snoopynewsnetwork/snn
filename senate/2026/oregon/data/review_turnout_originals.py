"""Coordinator audit of the immutable original-first Oregon turnout handoff.

No producer code imports, source requests or producer writes. The manifest pin
makes the reviewed phase explicit; later reciprocal outputs need their own review.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv, gzip, hashlib, io, json, re, subprocess, tempfile, zipfile

D = Path(__file__).resolve().parent
R = D.parent
T = D / 'turnout'
NEWS = D / 'news'
EXPECTED_MANIFEST = 'c11efbdc93b1d27147ff0636c9a166366872e1fe58602b7675fced37fadfdc84'
CHECKS = 0


def check(value, detail):
    global CHECKS
    CHECKS += 1
    if not value:
        raise AssertionError(detail)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def pin(path):
    raw = path.read_bytes()
    return dict(path=str(path.relative_to(R)), bytes=len(raw), sha256=sha(raw))


def read_csv(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def raw_pdf_text(raw):
    check(raw.startswith(b'%PDF-') and b'%%EOF' in raw[-1024:], 'whole PDF entity')
    proc = subprocess.run(['pdftotext', '-layout', '-', '-'], input=raw,
                          capture_output=True, check=True)
    return proc.stdout.decode()


def main():
    manifest_raw = (T / 'asset-manifest.json').read_bytes()
    check(sha(manifest_raw) == EXPECTED_MANIFEST, 'exact original-phase manifest')
    manifest = json.loads(manifest_raw)
    all_paths = set()
    for row in manifest['owned_assets'] + manifest['shared_assets']:
        path = R / row['path']
        raw = path.read_bytes()
        check(path.resolve().is_relative_to(R.resolve()), 'state-contained asset')
        check((len(raw), sha(raw)) == (row['bytes'], row['sha256']), row['path'])
        check(len(raw) < 40000000, 'strict object limit')
    for row in manifest['owned_assets']:
        check(row['path'] not in all_paths, 'unique owned path')
        all_paths.add(row['path'])
    actual = {str(p.relative_to(R)) for p in T.rglob('*') if p.is_file()}
    actual |= {'turnout.md', 'data/county-turnout.csv'}
    check(actual == all_paths | {'data/turnout/asset-manifest.json'}, 'self-only exclusion')
    check(not any('__pycache__' in Path(p).parts or Path(p).suffix == '.pyc'
                  for p in actual), 'no generated cache')
    witness = load(T / 'pre-peer-witness-v1.json')
    for row in witness['pinned_files']:
        raw = (R / row['path']).read_bytes()
        check((len(raw), sha(raw)) == (row['bytes'], row['sha256']), 'original witness target')

    shared = load(T / 'source/shared-original-pins.json')
    byid = {x['id']: x for x in shared}
    raw_small = {}
    for row in shared:
        if row.get('asset_parts'):
            continue
        stored = (NEWS / row['asset']).read_bytes()
        raw = gzip.decompress(stored)
        check((sha(stored), sha(raw), len(raw)) ==
              (row['stored_sha256'], row['raw_sha256'], row['bytes']), row['id'])
        raw_small[row['id']] = raw
    original_inventory = load(T / 'source/original-inventory.json')
    zip_count = 0
    for year in (2020, 2022):
        row = byid[f'sos-{year}-precinct-zip-observed-download']
        with tempfile.TemporaryFile() as compressed, tempfile.TemporaryFile() as original:
            packed_hash = hashlib.sha256()
            packed_size = 0
            for part in row['asset_parts']:
                packed = (NEWS / part['asset']).read_bytes()
                check((len(packed), sha(packed)) == (part['bytes'], part['sha256']), 'ZIP bytepart')
                compressed.write(packed)
                packed_hash.update(packed)
                packed_size += len(packed)
            check((packed_size, packed_hash.hexdigest()) ==
                  (row['stored_bytes'], row['stored_sha256']), 'ordered gzip stream')
            compressed.seek(0)
            decoded_hash = hashlib.sha256()
            decoded_size = 0
            with gzip.GzipFile(fileobj=compressed) as stream:
                while True:
                    block = stream.read(1048576)
                    if not block:
                        break
                    original.write(block)
                    decoded_hash.update(block)
                    decoded_size += len(block)
            check((decoded_size, decoded_hash.hexdigest()) ==
                  (row['bytes'], row['raw_sha256']), 'whole original ZIP')
            original.seek(0)
            with zipfile.ZipFile(original) as archive:
                check(archive.testzip() is None, 'every ZIP CRC')
                entries = [x for x in original_inventory if x.get('year') == year]
                check(len(entries) == len(archive.infolist()) == 36, 'complete archive members')
                for entry, info in zip(entries, archive.infolist()):
                    check(entry['member_name'] == info.filename, 'original ZIP member order')
                    raw = archive.read(info)
                    check((len(raw), sha(raw), info.CRC) ==
                          (entry['original_bytes'], entry['original_sha256'], entry['CRC32']),
                          info.filename)
                    zip_count += 1

    text = {
        '2024-abstract': raw_pdf_text(raw_small['sos-2024-results-archived-20241212']),
        '2020-abstract': raw_pdf_text(raw_small['sos-2020-actual-abstract-stream13735450']),
        '2022-abstract': raw_pdf_text(b''.join(raw_small[x] for x in (
            'sos-2022-record13735454-range0-163839',
            'sos-2022-record13735454-range163840-327679',
            'sos-2022-record13735454-byte-range-tail'))),
    }
    candidates = read_csv(T / 'county-candidates.csv')
    check(len(candidates) == 864, 'complete selected candidate positions')
    candidate_vectors = defaultdict(dict)
    for row in candidates:
        lines = text[row['source_key']].split('\f')[int(row['PDF_page']) - 1].splitlines()
        literal = lines[int(row['text_line_1based']) - 1]
        check(literal == row['raw_line'], 'fresh original county row/position')
        fields = re.split(r'\s{2,}', literal.strip())
        check(fields[0] == row['county'], 'literal county header')
        values = [int(x.replace(',', '')) for x in fields[1:]]
        check(values[int(row['column_index'])] == int(row['votes']), 'original county candidate value')
        candidate_vectors[(row['contest'], row['county'])][int(row['column_index'])] = int(row['votes'])
    totals = {}
    for footer in load(T / 'source/statewide-footers.json'):
        rows = [x for x in candidates if x['contest'] == footer['contest']]
        source_line = text[footer['source_key']].split('\f')[footer['page'] - 1].splitlines()[footer['line'] - 1]
        check(source_line == footer['raw_line'], 'fresh printed statewide footer')
        values = [int(x.replace(',', '')) for x in re.findall(r'\d[\d,]*', source_line)]
        for index, value in enumerate(values):
            check(sum(int(x['votes']) for x in rows if int(x['column_index']) == index) == value,
                  'every statewide column closes')
        totals[footer['contest']] = sum(values)
    check(totals == {'2024-president': 2244493, '2020-senate': 2321249,
                     '2022-senate': 1927949, '2022-governor': 1952883}, 'source total universes')

    acquired = {}
    receipt_count = 0
    for path in (T / 'source/acquired').glob('*.receipt.json'):
        receipt = load(path)
        receipt_count += 1
        for entity in receipt['response_entities']:
            packed = (path.parent / entity['asset']).read_bytes()
            raw = gzip.decompress(packed)
            check((len(packed), sha(packed), len(raw), sha(raw)) ==
                  (entity['stored_bytes'], entity['stored_sha256'], entity['raw_bytes'], entity['raw_sha256']),
                  'full receipt entity')
        if receipt['response_entities']:
            acquired[receipt['key']] = raw
    participation = read_csv(T / 'participation-controls.csv')
    footers = load(T / 'source/participation-footers.json')
    for footer in footers:
        key = footer['source_key']
        text[key] = raw_pdf_text(acquired[key])
    for row in participation + footers:
        line = text[row['source_key']].split('\f')[int(row['PDF_page']) - 1].splitlines()[int(row['text_line_1based']) - 1]
        check(line == row['raw_line'], 'fresh participation row/position')
        numbers = re.findall(r'-?\d[\d,]*(?:\.\d+)?%?', line)
        integers = [int(x.replace(',', '')) for x in numbers if '%' not in x]
        for field in ('registration_Number_Eligible', 'ballots_Returned'):
            check(int(row[field]) in integers, 'printed participation total field')
    for footer in footers:
        rows = [x for x in participation if int(x['year']) == footer['year']]
        check(len(rows) == 36, 'all participation parents')
        for field in ('registration_Number_Eligible', 'ballots_Returned'):
            check(sum(int(x[field]) for x in rows) == footer[field], 'participation footer closes')

    known = load(T / 'known-native-ranking.json')
    check(len(known['full_order']) == 510, 'known native observations')
    count_by_parent = Counter(x['county'] for x in known['full_order'])
    check(dict(count_by_parent) == {'Multnomah': 107, 'Washington': 155, 'Clackamas': 118,
                                   'Marion': 118, 'Wasco': 12}, 'five literal native sets')
    for county in count_by_parent:
        rows = [x for x in known['full_order'] if x['county'] == county]
        for index in range(8):
            check(sum(x['candidate_vector'][index] for x in rows) ==
                  candidate_vectors[('2024-president', county)][index], 'native column closes original county')
    source_rows = list(csv.DictReader(io.StringIO(acquired['multnomah-2024-sovc2'].decode())))
    observations = [json.loads(x) for x in gzip.decompress((T / 'native/observations.jsonl.gz').read_bytes()).splitlines()]
    raw_fields = 0
    csv_records = set()
    for obs in observations:
        if obs['source_key'] != 'multnomah-2024-sovc2':
            continue
        row = source_rows[obs['CSV_record_1based'] - 2]
        check(obs['raw_source_row'] == row, 'whole native CSV source row')
        field = 'Votes' if obs['kind'] == 'candidate' else obs['label_literal']
        check(int(row[field].replace(',', '')) == obs['value'], 'direct native CSV candidate/control value')
        check(row['Precinct'] == obs['unit_literal'], 'native source ID literal')
        raw_fields += len(row)
        csv_records.add(obs['CSV_record_1based'])
    native_direct_rows = 0
    for key in ('clackamas-2024-canvass', 'marion-2024-canvass'):
        text[key] = raw_pdf_text(acquired[key])
        for obs in observations:
            if obs['source_key'] != key or obs['kind'] != 'candidate':
                continue
            line = text[key].split('\f')[obs['page'] - 1].splitlines()[obs['line'] - 1]
            check(line == obs['raw_line'], 'fresh PDF native row and position')
            values = [int(x.replace(',', '')) for x in line.split()[1:] if re.fullmatch(r'[\d,]+', x)]
            column = obs['canonical_column']
            if key == 'clackamas-2024-canvass' and column == 7:
                column = 10
            check(values[column] == obs['value'], 'direct PDF native candidate position')
            native_direct_rows += 1

    def ranking(value, field):
        rows = value['full_order']
        check(rows == sorted(rows, key=lambda x: (-x[field], x['key'])), 'descending counts and literal-key ties')
        check(len({x['key'] for x in rows}) == len(rows), 'unique keys')
        denominator = sum(x[field] for x in rows)
        check(value['total'] == denominator, 'rank denominator')
        cumulative = 0
        crossing = None
        for rank, row in enumerate(rows, 1):
            cumulative += row[field]
            check((row['rank'], row['cumulative_votes']) == (rank, cumulative), 'complete cumulative sequence')
            if crossing is None and 5*cumulative >= 4*denominator:
                crossing = rank
        m = value['minimum80']
        check(m['count'] == crossing, 'integer first 80 crossing')
        before = sum(x[field] for x in rows[:crossing-1])
        through = before + rows[crossing-1][field]
        check((m['preceding_votes'], m['cumulative_votes']) == (before, through), 'exact threshold predecessor')
        check(m['ordered_keys'] == [x['key'] for x in rows[:crossing]], 'all selected keys')
        check(value['remainder']['keys'] == [x['key'] for x in rows[crossing:]], 'all remainder keys')
        check(value['remainder']['votes'] == denominator-through, 'remainder volume')
        check((value['top15']['numerator'], value['top15']['denominator']) ==
              (sum(x[field] for x in rows[:15]), denominator), 'top15 exact fraction')
    county_orders = load(T / 'county-sensitivities.json')
    for order in county_orders.values():
        ranking(order, 'votes')
    ranking(known, 'reported_votes')
    contract = load(T / 'priority-set.json')
    parents = contract['all_36_county_parents']
    check(len(parents) == 36, 'complete parent inventory')
    unavailable = [x for x in parents if x['unknown_native_membership']]
    check(len(unavailable) == 31, 'explicit unclosed parents')
    for key in ('complete_order', 'ordered_priority_keys', 'top15', 'minimum80', 'remainder'):
        check(contract[key] is None, 'no canonical native dispatch')
    check(sum(x['county_presidential_reported_votes'] for x in unavailable) == 1115972,
          'unknown parents remain in statewide arithmetic')
    check(known['total'] == 1128521 and known['total']+1115972 == 2244493, 'known vs whole state')
    output = dict(status='pass_bounded_original_first_turnout_review', checks=CHECKS,
                  reviewed_manifest=pin(T/'asset-manifest.json'), witness=pin(T/'pre-peer-witness-v1.json'),
                  complete_owned_entries=len(all_paths), complete_shared_assets=len(manifest['shared_assets']),
                  ZIP_members_independently_restored_hashed=zip_count,
                  original_county_candidate_positions=864, exact_contest_totals=totals,
                  original_participation_county_rows=len(participation), original_receipt_entities_verified=True,
                  acquisition_receipts=receipt_count,
                  unique_Multnomah_native_CSV_records=len(csv_records),
                  unique_Multnomah_native_CSV_field_positions=len(csv_records)*len(source_rows[0]),
                  raw_CSV_field_observation_comparisons=raw_fields,
                  direct_Clackamas_Marion_candidate_positions=native_direct_rows,
                  full_county_orders=len(county_orders), known_native_rows=510,
                  known_native_parent_counts=dict(count_by_parent), canonical_native_priority=None,
                  unclosed_2024parents=31, unknown_parent_candidate_votes=1115972,
                  qualifications=['No author extraction or ranking code imported.',
                      'Washington and Wasco raster-derived rows retain OCR and direct visual transcriptions; this audit does not claim an independent all-cell raster transcription.',
                      'Historical native normalization remains partial despite complete original archives.',
                      'No peer/calculator/future-final/current/legal/geographic approval.'])
    path = D/'coordinator-turnout-original-review.json'
    path.write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
