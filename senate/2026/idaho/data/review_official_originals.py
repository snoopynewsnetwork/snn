"""Coordinator-only, producer-free replay of the acquired official originals.

Read-only with respect to every question package. The sole output is a separate
coordinator review; no current primary identifier is matched to a historical leaf.
"""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import posixpath
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

D = Path(__file__).resolve().parent
S = D.parent
R = D / 'results-sources'
N = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
C = Counter()


def check(value, kind):
    assert value, kind
    C[kind] += 1


def sha(value):
    return hashlib.sha256(value).hexdigest()


def load(path):
    value = path.read_bytes()
    return json.loads(gzip.decompress(value) if path.suffix == '.gz' else value)


def pin(path):
    value = path.read_bytes()
    return dict(path=str(path.relative_to(S)), bytes=len(value), sha256=sha(value))


def raw_source(name):
    path = R / 'receipts' / (name + '.json')
    receipt = load(path)
    stored = (R / receipt['stored_path']).read_bytes()
    value = gzip.decompress(stored)
    check(receipt['http_status'] == 200, 'acquired_original_HTTP200')
    check(len(value) == receipt['raw_bytes'] and sha(value) == receipt['raw_sha256'], 'original_bytes_hash')
    check(len(stored) == receipt['stored_bytes'] and sha(stored) == receipt['stored_sha256'], 'stored_bytes_hash')
    check(receipt['method'] == 'GET' and receipt['retrieved_utc'] and receipt['final_url'], 'complete_source_identity')
    return receipt, value


class Visible(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1

    def handle_data(self, value):
        if not self.skip:
            self.values.append(value)


def visible(value):
    parser = Visible()
    parser.feed(value.decode())
    return ' '.join(' '.join(parser.values).split())


def cells(row, shared):
    out = {}
    for cell in row.findall('m:c', N):
        v = cell.find('m:v', N)
        f = cell.find('m:f', N)
        raw = v.text if v is not None else None
        value = raw
        if cell.get('t') == 's' and raw is not None:
            value = shared[int(raw)]
        elif cell.get('t') == 'inlineStr':
            inline = cell.find('m:is', N)
            value = ''.join(inline.itertext()) if inline is not None else None
        out[re.sub(r'\d+$', '', cell.get('r'))] = dict(
            address=cell.get('r'), value=value, type=cell.get('t'),
            style=cell.get('s'), raw_v=raw, formula=f.text if f is not None else None)
    return out


def compare_export(name):
    receipt, raw = raw_source(name)
    saved = load(R / 'extracted' / (name + '-xlsx.json.gz'))
    check(saved['raw_sha256'] == sha(raw), 'export_original_identity')
    archive = zipfile.ZipFile(io.BytesIO(raw))
    check(archive.testzip() is None, 'export_complete_ZIP_CRC')
    shared = []
    if 'xl/sharedStrings.xml' in archive.namelist():
        shared = [''.join(x.itertext()) for x in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('m:si', N)]
    check(shared == saved['shared_strings'], 'export_all_shared_strings')
    rels = {x.get('Id'): x.get('Target') for x in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
    originals = ET.fromstring(archive.read('xl/workbook.xml')).findall('m:sheets/m:sheet', N)
    check(len(originals) == len(saved['sheets']), 'export_all_sheets')
    summary = []
    for definition, derivative in zip(originals, saved['sheets']):
        target = rels[definition.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
        member = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        check(definition.get('name') == derivative['name'] and member == derivative['member'], 'export_sheet_identity')
        count = 0
        # Streaming source XML preserves every explicit blank and metadata cell.
        with archive.open(member) as stream:
            for event, row in ET.iterparse(stream, events=('end',)):
                if row.tag != '{' + N['m'] + '}row':
                    continue
                check(count < len(derivative['rows']), 'export_no_omitted_original_row')
                item = derivative['rows'][count]
                check(int(row.get('r')) == item['row'] and dict(row.attrib) == item['attributes'], 'export_original_row_attributes')
                original = cells(row, shared)
                check(original == item['cells'], 'export_every_cell_value_type_style_formula_null')
                C['explicit_original_cells_replayed'] += len(original)
                count += 1
                row.clear()
        check(count == len(derivative['rows']), 'export_no_extra_derivative_row')
        header = {k: v['value'] for k, v in derivative['rows'][0]['cells'].items() if v['value'] is not None}
        check('Contest ID' in header.values() and 'Choice ID' in header.values(), 'separate_export_identity_namespaces')
        summary.append(dict(name=definition.get('name'), rows=count, header=header))
        C['complete_export_rows'] += count
    return dict(receipt=pin(R / 'receipts' / (name + '.json')), raw_sha256=sha(raw), sheets=summary)


def main():
    contract = load(D / 'turnout/priority-set.json')
    directory_receipt, directory_raw = raw_source('directory-csv')
    directory = list(csv.DictReader(io.StringIO(directory_raw.decode('cp1252'))))
    check(len(directory) == 44 and len({x['County'] for x in directory}) == 44, '44_original_authorities')
    check(directory == load(R / 'directory-native.json')['rows'], 'every_directory_field_and_blank')
    parents = load(R / 'parent-investigations.json')
    selected = {x['county'] for x in parents[1:] if x['priority_child_count']}
    check(len(selected) == 32, '32_deep_priority_parents')
    primary = []
    exports = []
    for county in [None] + [x['County'] for x in directory]:
        slug = county.lower().replace(' ', '-') + '-county-id' if county else 'id'
        receipt, raw = raw_source('data-' + slug)
        data = json.loads(raw)
        election = data['election']
        check(election['electionDate'] == '2026-05-19' and election['isPrimary'] is True, 'wrong_election_excluded_from_November')
        check(election['countGroups'] is None and election['nextUpdateAt'] is None, 'unknown_method_and_next_update')
        check(election['asOf'].endswith('Z'), 'source_UTC_clock_explicit')
        for item in data['ballotItems']:
            summary = item.get('summaryResults')
            if summary is not None:
                check(sum(x['voteCount'] for x in summary['ballotOptions']) == item['voteTotal'], 'full_primary_option_vector_sum')
                C['complete_primary_candidate_options'] += len(summary['ballotOptions'])
            check(item['underVoteCount'] is None and item['overVoteCount'] is None, 'unprinted_under_over_unknown')
        primary.append(dict(county=county, original_receipt=pin(R / 'receipts' / ('data-' + slug + '.json')),
                            primary_precincts=len(data['precincts']), ballot_items=len(data['ballotItems']),
                            asOf=election['asOf'], lastUpdated=election['lastUpdated'],
                            metadata_ballotItemCount=election['ballotItemCount'], ballotsCast=election['ballotsCast']))
        if county is None or county in selected:
            exports.append(compare_export('native-export-' + slug))
    check(len(primary) == 45 and len(exports) == 33, 'all_state_county_data_and_priority_exports')
    _, jurisdiction_raw = raw_source('jurisdiction-id')
    jurisdiction = json.loads(jurisdiction_raw)
    # Original configuration is preserved in full; only the observed public list
    # establishes which elections were available in this bounded inspection.
    check('nov2026' not in jurisdiction_raw.decode().lower(), 'no_invented_November_jurisdiction')
    for path, keys in [('priority-investigations.json', 'ordered_priority_keys'), ('remainder-monitoring.json', 'ordered_remainder_keys')]:
        rows = load(R / path)
        check([x['historical_key'] for x in rows] == contract[keys], 'full_ordered_investigation_identity')
        for x in rows:
            check(not x['current_approved'] and all(x[k] is None for k in ('current_leaf_id', 'current_contest_id', 'current_choice_ids', 'current_method', 'current_geometry')), 'no_historical_current_join')
    legal = []
    assertions = {
        'section-34-1205': ['within nine (9) days', '2025, ch. 113, sec. 18'],
        'section-34-1211': ['within twenty-one (21) days after the primary', 'within twenty-one (21) days after the general'],
        'section-34-702A': ['eleventh Friday before the primary', '2026, ch. 333, sec. 3'],
        'section-34-1007': ['prior to December 31, 2020'],
        'section-34-2309': ['may request a recount', 'five (5) votes, whichever is greater'],
        'bill-S1356-final-status': ['07/01/2026 SECTION 1-11; 01/01/2027 SECTION 12'],
    }
    for name, required in assertions.items():
        receipt, raw = raw_source(name)
        text = visible(raw)
        for literal in required:
            check(literal.lower() in text.lower(), 'operative_legal_literal_distinct_scope')
        legal.append(dict(receipt=pin(R / 'receipts' / (name + '.json')), original_raw_sha256=sha(raw), checked_literals=required))
    receipt, raw = raw_source('bill-S1356-pdf')
    with tempfile.TemporaryDirectory(prefix='idaho-coordinator-law-') as tmp:
        path = Path(tmp) / 'original.pdf'
        path.write_bytes(raw)
        text = subprocess.check_output(['pdftotext', '-layout', str(path), '-']).decode()
    normalized = ' '.join(text.split())
    check('SECTION 13.' in normalized and 'Sections 1 through 11' in normalized and 'July 1, 2026' in normalized and 'Section 12' in normalized and 'January 1, 2027' in normalized, 'original_bill_split_effective_clause')
    check('SECTION 3. That Section 34-702A' in normalized, 'writein_code_is_July_section_not_delayed_section12')
    out = dict(status='pass_independent_original_primary_exports_and_operative_text_review', checks=dict(C),
               complete_primary_sources=primary, complete_priority_and_state_exports=exports, legal_original_literals=legal,
               actual_original_bill_receipt=pin(R / 'receipts/bill-S1356-pdf.json'),
               coverage=dict(authorities=44, primary_data_entities=45, complete_original_exports=33, priority=528, remainder=457),
               limits='Observed May primary data/identifiers are excluded from November. Source plans and client refresh behavior are not measured cadence. Signed/enrolled final status, full later court and eligible-write-in scope, current geometry and exact outstanding votes remain qualified; no approval follows from this audit.')
    target = D / 'coordinator-official-original-review.json'
    value = (json.dumps(out, indent=2) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == value
    else:
        target.write_bytes(value)
    print(json.dumps(pin(target)))


if __name__ == '__main__':
    main()
