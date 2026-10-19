"""Fresh original-pixel OCR from immutable, strictly value-free 2018 boxes.

No OCR token is an accepted source value here. Headers and cells are read only
from our hash-verified SOS PDF bytes; page geometry from the peer is targeting
aid and must be independently checked against each original before acceptance.
"""
import argparse
import gzip
import io
import json
import re
import subprocess
from PIL import Image
import fitz
from acquire_sources import BASE, OUT, receipts, sha, savejson

HINT = OUT / 'source/2018-frozen78-vote-free-position-hints-v1.json'
HINT_SHA = 'b30c6255643c90fa06465208ea310df4b9405a5268049f7ff760cbb76ef805f8'


def original(sid):
    receipt = next(r for r in receipts if r['id'] == sid)
    raw = gzip.decompress((BASE / receipt['path']).read_bytes())
    assert sha(raw) == receipt['raw_sha256']
    return raw, receipt


def run_ocr(image, whitelist=None):
    stream = io.BytesIO(); image.save(stream, format='PNG')
    args = ['tesseract', 'stdin', 'stdout', '--psm', '6']
    if whitelist:
        args += ['-c', f'tessedit_char_whitelist={whitelist}']
    proc = subprocess.run(args, input=stream.getvalue(), capture_output=True, check=True)
    return dict(crop_png_sha256=sha(stream.getvalue()),
                raw_original_ocr=proc.stdout.decode(errors='replace').strip())


def extract(source):
    sid = source['source_id']
    raw, receipt = original(sid)
    assert receipt['raw_sha256'] == source['source_raw_sha256']
    doc = fitz.open(stream=raw, filetype='pdf')
    pages = []
    counts = dict(pages=0, header_targets=0, candidate_cell_targets=0,
                  numeric_tokens=0, literal_X_tokens=0, unresolved_tokens=0,
                  geometry_mismatch_pages=0)
    for page_hint in source['pages']:
        number = page_hint['source_pdf_page']
        pix = doc[number-1].get_pixmap(matrix=fitz.Matrix(2.7, 2.7),
                                       colorspace=fitz.csGRAY)
        png = pix.tobytes('png')
        image = Image.open(io.BytesIO(png)).convert('L')
        render_path = OUT / f'qa/2018-frozen78-original-pixels/{sid}/p{number:04d}-original.png'
        render_path.parent.mkdir(parents=True, exist_ok=True)
        render_path.write_bytes(png)
        page = dict(source_pdf_page=number, original_render_path=str(render_path.relative_to(BASE)),
                    original_render_sha256=sha(png), render_size=list(image.size),
                    target_render_size=page_hint['render_size'])
        counts['pages'] += 1
        if list(image.size) != page_hint['render_size']:
            page['status'] = 'source_target_geometry_mismatch_no_values_interpreted'
            pages.append(page); counts['geometry_mismatch_pages'] += 1
            continue
        headers = []
        for col in page_hint['physical_columns']:
            x0,y0,x1,y1 = col['header_bounds']
            assert 0 <= x0 < x1 <= image.width and 0 <= y0 < y1 <= image.height
            crop = image.crop((x0,y0,x1,y1)).rotate(270,expand=True)
            crop = crop.resize((crop.width*2,crop.height*2))
            reading = run_ocr(crop)
            headers.append(dict(source_column=col['source_column'],
                                target_header_box=col['header_bounds'],
                                upright_crop_png_sha256=reading['crop_png_sha256'],
                                raw_original_header_ocr=reading['raw_original_ocr']))
            counts['header_targets'] += 1
        fields = []
        for row in page_hint['candidate_row_positions']:
            y0,y1 = row['candidate_row_bounds'][1], row['candidate_row_bounds'][3]
            cells = []
            for col in page_hint['physical_columns']:
                x0,x1 = col['header_bounds'][0], col['header_bounds'][2]
                box = [x0+5,y0+4,x1-3,y1-4]
                if not (0 <= box[0] < box[2] <= image.width and
                        0 <= box[1] < box[3] <= image.height):
                    cells.append(dict(source_column=col['source_column'],
                                      provisional_crop_box=box,
                                      status='invalid_target_box_no_value'))
                    counts['candidate_cell_targets'] += 1
                    counts['unresolved_tokens'] += 1
                    continue
                crop = image.crop(tuple(box)).resize(((box[2]-box[0])*3,
                                                      (box[3]-box[1])*3))
                reading = run_ocr(crop, '0123456789Xx')
                literal = reading['raw_original_ocr']
                value = int(literal) if re.fullmatch(r'[0-9]+', literal) else None
                status = ('numeric_OCR_unaccepted' if value is not None else
                          'literal_X_OCR_unaccepted' if literal in ('X','x') else
                          'unresolved_or_blank_OCR_unaccepted')
                cells.append(dict(source_column=col['source_column'],
                                  provisional_crop_box=box,
                                  crop_png_sha256=reading['crop_png_sha256'],
                                  raw_original_ocr=literal,
                                  value_if_numeric_unaccepted=value,status=status))
                counts['candidate_cell_targets'] += 1
                counts['numeric_tokens' if value is not None else
                       'literal_X_tokens' if literal in ('X','x') else
                       'unresolved_tokens'] += 1
            fields.append(dict(source_row_ordinal=row['source_row_ordinal'],
                               target_candidate_row_bounds=row['candidate_row_bounds'],
                               cells=cells))
        page.update(headers=headers,fields=fields,status='original_OCR_diagnostic_only')
        pages.append(page)
    result = dict(scope='Fresh OCR of exact SOS2018 original page pixels using peer-frozen value-free positions only. No peer vote, label, role or ID entered input. Raw OCR is provisional; no number or absence is accepted as source vote/zero.',
                  source_id=sid, source_original_path=receipt['path'],
                  source_raw_sha256=receipt['raw_sha256'],
                  value_free_hint_path=str(HINT.relative_to(BASE)),
                  value_free_hint_sha256=HINT_SHA, pages=pages, counts=counts)
    path = OUT / f'qa/2018-frozen78-original-pixels/{sid}/diagnostic.json'
    savejson(path, result)
    return counts


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--source',action='append')
    ap.add_argument('--skip-existing',action='store_true'); args = ap.parse_args()
    assert sha(HINT.read_bytes()) == HINT_SHA
    hints = json.loads(HINT.read_text())
    selected = set(args.source or (s['source_id'] for s in hints['sources']))
    assert selected <= {s['source_id'] for s in hints['sources']}
    for source in hints['sources']:
        sid = source['source_id']
        if sid not in selected:continue
        path = OUT / f'qa/2018-frozen78-original-pixels/{sid}/diagnostic.json'
        if args.skip_existing and path.exists():
            old = json.loads(path.read_text())
            assert old['source_raw_sha256'] == source['source_raw_sha256']
            assert old['value_free_hint_sha256'] == HINT_SHA
            print(sid, 'prior diagnostic retained', flush=True)
        else:
            print(sid, extract(source), flush=True)


if __name__ == '__main__':
    main()
