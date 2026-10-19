"""Inventory source-scoped 2024 ballot, method and registration availability.

The full-page OCR inventory is a locator. Only directly read panels supply
numeric fields; a missing OCR hit does not become a source zero or proof that
the publication omitted the field.
"""
import gzip
import json

from acquire_sources import BASE, OUT, receipts, savejson, sha


def main():
    locator_path = OUT / 'source/2024-county-panel-full-ocr-inventory.json.gz'
    stored = locator_path.read_bytes()
    raw = gzip.decompress(stored)
    inventory = json.loads(raw)
    assert inventory['source_views'] == 82 and inventory['total_pdf_pages'] == 803
    summary_path = OUT / 'canvass-summary-readings.json'
    statistics_path = OUT / 'canvass-statistics-readings.json'
    summary = {r['source_id']: r for r in json.loads(summary_path.read_text())['sources']}
    statistics = {r['source_id']: r for r in json.loads(statistics_path.read_text())}
    e013_path = OUT / '2024-extra-e013-original-summary-readings.json'
    e013 = {r['source_id']: r for r in json.loads(e013_path.read_text())['sources']}
    assert len(summary) == 15 and len(statistics) == 14
    assert len(e013) == 3
    receipt = {r['id']: r for r in receipts}
    records = []
    for source in inventory['sources']:
        sid = source['source_id']
        assert receipt[sid]['raw_sha256'] == source['raw_sha256']
        assert len(source['pages']) == source['page_count']
        assert [p['pdf_page'] for p in source['pages']] == list(range(1, source['page_count'] + 1))
        summary_record = summary.get(sid)
        stats_record = statistics.get(sid)
        e013_record = e013.get(sid)
        summary_page = summary_record['page'] if summary_record else None
        stats_page = stats_record['page'] if stats_record else None
        for page_number in (summary_page, stats_page):
            assert page_number is None or 1 <= page_number <= source['page_count']
        candidate_pages = [p['pdf_page'] for p in source['pages'] if p['keyword_locator'].get('contest_totals')]
        stats_pages = [p['pdf_page'] for p in source['pages'] if p['keyword_locator'].get('statistics')]
        record = {
            'source_id': sid,
            'source_raw_sha256': source['raw_sha256'],
            'source_original_path': receipt[sid]['path'],
            'source_pdf_pages_inspected_by_original_page_OCR': source['page_count'],
            'original_page_OCR_statistics_locator_pages': stats_pages,
            'original_page_OCR_contest_locator_pages': candidate_pages,
            'direct_original_summary_page': summary_page,
            'direct_original_statistics_page': stats_page,
            'direct_original_E013_named_candidate_summary_page': e013_record['pdf_page'] if e013_record else None,
            'direct_original_E013_named_candidate_rows': len(e013_record['candidate_rows']) if e013_record else 0,
            'direct_original_summary_status_literal': summary_record['source_status_literal'] if summary_record else None,
            'direct_original_statistics_status_literal': stats_record['report_status_literal'] if stats_record else None,
            'summary_method_labels_literal': summary_record['methods'] if summary_record else None,
            'statistics_method_labels_literal': stats_record['methods_literal'] if stats_record else None,
            'statistics_registered_voters_field_printed': stats_record is not None and stats_record['registered_voters_total'] is not None,
            'statistics_ballots_cast_field_printed': stats_record is not None and stats_record['ballots_cast_total'] is not None,
            'statistics_blank_field_printed': stats_record is not None and stats_record['ballots_cast_blank'] is not None,
            'senate_generic_write_in_row_printed': summary_record is not None and summary_record['senate'].get('Write-In Totals') is not None,
            'senate_overvote_row_printed': summary_record is not None and summary_record['senate'].get('Overvotes') is not None,
            'senate_undervote_row_printed': summary_record is not None and summary_record['senate'].get('Undervotes') is not None,
            'field_availability_status': 'direct_original_standard_summary_or_statistics_panel_read' if summary_record or stats_record else ('direct_original_E013_named_candidate_only' if e013_record else 'not_located_by_allpage_original_OCR_no_numeric_field_accepted'),
            'availability_qualification': 'No OCR absence is treated as proof a field was never published; unreviewed source fields remain unavailable here, not zero.' if not (summary_record or stats_record or e013_record) else ('E-013 provides named candidate county aggregates only; no generic, ballot, registration or method field is accepted.' if e013_record and not (summary_record or stats_record) else 'Only the separately linked direct-original panel transcription supplies numeric fields; absent rows in that panel remain null.'),
        }
        records.append(record)
    assert len(records) == 82 and len({r['source_id'] for r in records}) == 82
    assert sum(r['direct_original_summary_page'] is not None for r in records) == 14
    assert sum(r['direct_original_statistics_page'] is not None for r in records) == 13
    assert 'sos-2024-county-pike-updated' in {r['source_id'] for r in records}
    assert 'sos-2024-county-pike' in summary and 'sos-2024-county-pike' in statistics
    alternative = [
        {'source_id': 'sos-2024-county-pike', 'source_raw_sha256': receipt['sos-2024-county-pike']['raw_sha256'],
         'source_original_path': receipt['sos-2024-county-pike']['path'],
         'direct_original_summary_page': summary['sos-2024-county-pike']['page'],
         'direct_original_statistics_page': statistics['sos-2024-county-pike']['page'],
         'scope': 'Original nonadditive Pike publication; its panel and vendor fields do not become updated-Pike native or ballot values.'},
        {'source_id': 'sos-2024-county-coahoma', 'source_raw_sha256': receipt['sos-2024-county-coahoma']['raw_sha256'],
         'source_original_path': receipt['sos-2024-county-coahoma']['path'],
         'direct_original_summary_page': None, 'direct_original_statistics_page': None,
         'scope': 'Original nonadditive Coahoma publication outside the preferred82 full-page locator; no ballot/method panel value accepted.'},
    ]
    body = {
        'scope': 'All82 preferred original county publications, plus two explicit nonadditive alternatives. Numeric ballot/registration/generic/method/under/over fields are only in the separate direct-original panel ledgers; locator misses are unavailable in this review and never zero.',
        'preferred_source_views': 82,
        'preferred_source_pdf_pages_allpage_OCR_located': 803,
        'preferred_direct_original_summary_panels': 14,
        'preferred_direct_original_statistics_panels': 13,
        'separate_nonadditive_original_Pike_summary_panels': 1,
        'separate_nonadditive_original_Pike_statistics_panels': 1,
        'summary_panel_source_count_all_versions': 15,
        'statistics_panel_source_count_all_versions': 14,
        'separate_preferred_E013_candidate_only_summary_pages': 3,
        'separate_preferred_E013_candidate_only_source_ids': sorted(e013),
        'direct_original_E013_reading_path': str(e013_path.relative_to(BASE)),
        'direct_original_E013_reading_sha256': sha(e013_path.read_bytes()),
        'fullpage_OCR_locator_stored_path': str(locator_path.relative_to(BASE)),
        'fullpage_OCR_locator_stored_sha256': sha(stored),
        'fullpage_OCR_locator_stored_bytes': len(stored),
        'fullpage_OCR_locator_raw_sha256': sha(raw),
        'fullpage_OCR_locator_raw_bytes': len(raw),
        'direct_original_summary_reading_path': str(summary_path.relative_to(BASE)),
        'direct_original_summary_reading_sha256': sha(summary_path.read_bytes()),
        'direct_original_statistics_reading_path': str(statistics_path.relative_to(BASE)),
        'direct_original_statistics_reading_sha256': sha(statistics_path.read_bytes()),
        'preferred_sources': records,
        'nonadditive_alternative_sources': alternative,
    }
    savejson(OUT / '2024-field-availability.json', body)
    print('2024 field availability', len(records), 'preferred source views;', len(summary), 'direct original summary panels', len(statistics), 'statistics panels')


if __name__ == '__main__':
    main()
