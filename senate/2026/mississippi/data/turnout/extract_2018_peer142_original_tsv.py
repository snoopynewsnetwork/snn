"""One-pass full-page OCR of new 2018 source cells using vote-free geometry.

All extracted text is an aid. No candidate name, value, source role, native
header or accepted precinct identity comes from the peer into this read.
"""
import argparse
import csv
import gzip
import io
import json
import re
import subprocess
import fitz
from acquire_sources import BASE, OUT, receipts, savejson, sha

HINT=OUT/'source/2018-peer142-new64-vote-free-position-hints-v1.json'
HINT_SHA='7fc12ad227424e27687945661d5c58e86075bac612b146600ed5d290c9fde93e'


def original(sid):
    receipt=next(r for r in receipts if r['id']==sid)
    raw=gzip.decompress((BASE/receipt['path']).read_bytes())
    assert sha(raw)==receipt['raw_sha256']
    return raw,receipt


def tokens(tsv):
    result=[]
    for row in csv.DictReader(io.StringIO(tsv),delimiter='\t'):
        word=row.get('text','').strip()
        if not word:continue
        x,y,w,h=[int(row[field]) for field in ('left','top','width','height')]
        result.append({'text':word,'bounds':[x,y,x+w,y+h],
                       'confidence_literal':row.get('conf')})
    return result


def inside(word,box):
    x0,y0,x1,y1=word['bounds']
    cx=(x0+x1)/2;cy=(y0+y1)/2
    return box[0]<=cx<box[2] and box[1]<=cy<box[3]


def extract(source):
    sid=source['source_id'];raw,receipt=original(sid)
    assert receipt['raw_sha256']==source['source_raw_sha256']
    doc=fitz.open(stream=raw,filetype='pdf')
    pages=[]
    for hint in source['pages']:
        page_num=hint['source_pdf_page']
        pix=doc[page_num-1].get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY)
        png=pix.tobytes('png')
        assert [pix.width,pix.height]==hint['render_size']
        out=OUT/f'qa/2018-peer142-original-tsv/{sid}'
        out.mkdir(parents=True,exist_ok=True)
        raster_path=out/f'p{page_num:04d}-original.png';raster_path.write_bytes(png)
        proc=subprocess.run(['tesseract','stdin','stdout','--psm','11','tsv'],
                            input=png,capture_output=True,check=True)
        tsv=proc.stdout.decode(errors='replace')
        tsv_path=out/f'p{page_num:04d}-original.tsv.gz'
        tsv_stored=gzip.compress(proc.stdout,compresslevel=9,mtime=0)
        tsv_path.write_bytes(tsv_stored)
        words=tokens(tsv)
        fields=[]
        for row in hint['candidate_row_positions']:
            y0,y1=row['candidate_row_bounds'][1],row['candidate_row_bounds'][3]
            cells=[]
            for column in hint['physical_columns']:
                x0,x1=column['header_bounds'][0],column['header_bounds'][2]
                box=[x0+5,y0+4,x1-3,y1-4]
                assert 0<=box[0]<box[2]<=pix.width and 0<=box[1]<box[3]<=pix.height
                hits=[word for word in words if inside(word,box)]
                plain=[word['text'] for word in hits]
                number=int(plain[0].replace(',','')) if len(plain)==1 and re.fullmatch(r'\d[\d,]*',plain[0]) else None
                cells.append({'source_column':column['source_column'],'target_box':box,
                              'original_page_tsv_tokens':hits,'parsed_single_number_diagnostic':number,
                              'status':'numeric_OCR_unaccepted' if number is not None else
                                       'ambiguous_or_blank_OCR_unaccepted'})
            fields.append({'source_row_ordinal':row['source_row_ordinal'],
                           'source_row_target_bounds':row['candidate_row_bounds'],
                           'cells':cells})
        pages.append({'source_pdf_page':page_num,'render_size':[pix.width,pix.height],
                      'original_render_path':str(raster_path.relative_to(BASE)),
                      'original_render_sha256':sha(png),
                      'original_full_page_tsv_path':str(tsv_path.relative_to(BASE)),
                      'original_full_page_tsv_raw_sha256':sha(proc.stdout),
                      'original_full_page_tsv_stored_sha256':sha(tsv_stored),
                      'original_full_page_tsv_stored_bytes':len(tsv_stored),
                      'fields':fields})
    body={'scope':'Fresh complete original-page OCR with immutable vote-free peer geometry only. Every number/absence and every targeting box is provisional until original visual review.',
          'source_id':sid,'source_raw_sha256':receipt['raw_sha256'],
          'source_original_path':receipt['path'],
          'value_free_hint_path':str(HINT.relative_to(BASE)),
          'value_free_hint_sha256':HINT_SHA,
          'pages':pages}
    savejson(OUT/f'qa/2018-peer142-original-tsv/{sid}/diagnostic.json',body)
    return sum(len(f['cells']) for p in pages for f in p['fields'])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',action='append');ap.add_argument('--skip-existing',action='store_true')
    args=ap.parse_args()
    assert sha(HINT.read_bytes())==HINT_SHA
    hints=json.loads(HINT.read_text());selected=set(args.source or (s['source_id'] for s in hints['sources']))
    assert selected<={s['source_id'] for s in hints['sources']}
    for source in hints['sources']:
        sid=source['source_id']
        if sid not in selected:continue
        path=OUT/f'qa/2018-peer142-original-tsv/{sid}/diagnostic.json'
        if args.skip_existing and path.exists():
            old=json.loads(path.read_text())
            assert old['source_raw_sha256']==source['source_raw_sha256'] and old['value_free_hint_sha256']==HINT_SHA
            print(sid,'prior original OCR retained',flush=True)
        else:
            print(sid,extract(source),'original source cell targets',flush=True)


if __name__=='__main__':main()
