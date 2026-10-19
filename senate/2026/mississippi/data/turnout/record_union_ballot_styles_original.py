"""Direct transcription of Union's nonadditive BP-009 split/style report.

No candidate votes appear on these pages. Codes and literal split labels are
source-only identities; they do not crosswalk SEMS, vendor profiles or 2026.
"""
import json

import fitz

from acquire_sources import BASE, OUT, receipts, savejson, sha, source


SID = 'sos-2024-county-union'
RASTERS = {
    8: 'e7775339c27a3dc12b64c9d88cf056f64671b0b567272b9f86c5b4927eb3d894',
    9: 'f0960fa7f6f24eda91e1ea3a89911c116264a8c97be4f671f22fb5e7268a6621',
    10: 'ebbe915172f501241533461edf156ce69d459674bdab58c4069c88443ffababb',
}
# page | printed code | printed parent name | parent TOTAL | split,style,voters;
# Source Party column is blank for every printed split row.
DATA = '''8|101|Macedonia|414|SH13 SS10 SB2,5,414
8|102|Blythe|355|SH13 SS10 SB1,5,45;SH13 SS10 SB2,5,310
8|103|Myrtle|1432|M SB1,5,212;SB1,5,1183;SB3,10,37
8|104|Glenfield|1060|NA1,5,50;NA2,5,636;SB1,5,268;SB3,10,106
8|201|Pinedale|548|SH13 SS10 SB2,4,548
8|202|West Union|849|SH13 SS10 SB2,4,849
8|203|Sportsplex|1049|NA2,4,441;NA2 SB3,9,0;NA3,4,90;SB3,9,518
8|204|Ingomar|1221|SS10 SB3,9,1221
8|301|King's Chapel|602|SB3,8,227;SB4,7,375
9|302|Courthouse|1101|NA1 E,3,469;NA1 W,3,25;NA2 E,3,0;NA2 W,3,0;NA3 E,3,7;NA3 W,3,166;NA4 SB3 W,8,92;NA4 W,3,108;SB1 E,3,20;SB3 W,8,63;SB4 W,7,151
9|303|Central Maintenance|1003|NAS,3,686;SB1,3,317
9|304|Beacon Hill|924|NAS,3,37;SB4,7,887
9|401|Blue Springs|639|BS SB4,6,242;S SB4,6,105;SB4,6,274;SB5,1,18
9|402|Hillcrest Church|900|NA3,1,404;NA4,1,481;SB4,6,15
9|403|Center|510|NA4,1,46;NAS,1,152;SB4,6,72;SB5,1,240
9|404|Ellistown Baptist Church|1099|S SB4,6,4;S SB5,1,4;SB4,6,50;SB5,1,1041
10|501|Watson Grove Baptist Church|1700|NA1,2,482;NA3,2,395;NA4,2,543;NAS,2,280
10|502|Keownville|743|NAS,2,665;SB5,2,78
10|503|Pleasant Ridge|377|NAS,2,198;SB5,2,179
10|504|Jericho|532|SB5,2,532'''


def main():
    receipt = next(r for r in receipts if r['id'] == SID)
    raw = source(SID)
    assert sha(raw) == receipt['raw_sha256']
    doc = fitz.open(stream=raw, filetype='pdf')
    assert len(doc) >= 10
    folder = OUT / 'qa/2024-union-original-ballot-styles'
    folder.mkdir(parents=True, exist_ok=True)
    pages = []
    for page, digest in RASTERS.items():
        pix = doc[page - 1].get_pixmap(matrix=fitz.Matrix(3, 3), colorspace=fitz.csGRAY)
        png = pix.tobytes('png')
        assert sha(png) == digest
        path = folder / f'p{page}-original.png'
        path.write_bytes(png)
        pages.append({'pdf_page': page, 'render_path': str(path.relative_to(BASE)),
                      'render_sha256': digest, 'render_size': [pix.width, pix.height]})
    parents, splits = [], []
    for line in DATA.splitlines():
        p, code, name, total, children = line.split('|')
        page, total = int(p), int(total)
        parsed = []
        for i, child in enumerate(children.split(';'), 1):
            label, style, voters = child.split(',')
            row = {'source_id': SID, 'pdf_page': page, 'printed_precinct_code': code,
                   'printed_precinct_name': name, 'split_ordinal_within_parent': i,
                   'printed_split_literal': label, 'printed_ballot_style_literal': style,
                   'printed_party_literal': None, 'printed_total_voters': int(voters),
                   'role': 'ballot_style_split_administrative_nonadditive_to_candidate_native',
                   'key': f'union-bp009:p{page}:code{code}:split{i}'}
            parsed.append(row)
            splits.append(row)
        assert sum(x['printed_total_voters'] for x in parsed) == total, code
        parents.append({'source_id': SID, 'pdf_page': page, 'printed_precinct_code': code,
                        'printed_precinct_name': name, 'printed_TOTAL_voters': total,
                        'role': 'printed_parent_TOTAL_nonadditive_to_splits_or_candidate_native',
                        'key': f'union-bp009:p{page}:code{code}:TOTAL'})
    assert len(parents) == 20 and len(splits) == 58
    assert len({x['key'] for x in parents + splits}) == 78
    assert sum(x['printed_TOTAL_voters'] for x in parents) == 17058
    profile = json.loads((OUT / 'native-profile-controls.json').read_text())
    union = next(c for c in profile['checks'] if c['source_id'] == SID)
    # This is a separate source/report measure. The discrepancy is descriptive,
    # not a reason to adjust either printed source total.
    assert union['source_id'] == SID
    body = {'source_id': SID, 'source_raw_sha256': receipt['raw_sha256'],
            'source_original_path': receipt['path'], 'report_literal': 'Precinct Split Ballot Styles Report',
            'report_number_literal': 'BP-009', 'date_literal': '11/14/2024',
            'election_literal': '11/05/2024 - 2024 PRESIDENTIAL GENERAL ELECTION',
            'pages': pages, 'split_rows': splits, 'parent_TOTAL_rows': parents,
            'printed_Grand_Total_voters': 17058, 'vendor_profile_registered_voters_separate': 17084,
            'difference_split_report_minus_vendor_registration': -26,
            'candidate_votes_available_on_these_pages': False,
            'split_label_literal_qualification': 'NAS is retained as the glyph appears in the original; no expansion to NA5 or geography join is made.',
            'total_voters_definition': 'Not defined on the three printed pages beyond the column heading; do not equate to ballots or registration.',
            'scope': 'All58 printed split/style rows and20 printed parent totals across original PDFpages8–10; nonadditive to candidate/native/profile views.'}
    savejson(OUT / '2024-union-ballot-styles-original-reading.json', body)
    print('Union BP-009 original: 58 split/style rows, 20 parent TOTALs, Grand Total17058; no candidate allocation')


if __name__ == '__main__':
    main()
