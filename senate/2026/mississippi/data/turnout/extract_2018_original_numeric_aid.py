"""Independent unaccepted numeric OCR aid from original 2018 PDF pixels.

Only vote-free geometry is imported from the machine locator witness. Every
recognized glyph comes from a freshly rendered exact original PDF. This does
not create accepted native votes, zeros, roles, labels or geography.
"""
import argparse
import csv
import gzip
import io
import json
import re
import subprocess
from PIL import Image
import fitz
from acquire_sources import BASE,OUT,receipts,sha,savejson

TARGET=OUT/'source/2018-vote-free-targets-v1.json'
TARGET_SHA='10ae518a2a0c7925848f2dd7f1c55dca8b954e0c2bf0390a01eedf3cb3ea2e38'

def render(page,hint):
    png=page.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png')
    image=Image.open(io.BytesIO(png)).convert('L')
    if hint['rotation_ccw']:
        image=image.rotate(hint['rotation_ccw'],expand=True,fillcolor=255)
    if hint['deskew_angle_ccw']:
        image=image.rotate(hint['deskew_angle_ccw'],expand=False,fillcolor=255)
    output=io.BytesIO();image.save(output,format='PNG')
    return image,output.getvalue()

def tsv_words(png):
    proc=subprocess.run(['tesseract','stdin','stdout','--psm','11','tsv'],
                        input=png,capture_output=True,check=True)
    words=[]
    for row in csv.DictReader(io.StringIO(proc.stdout.decode(errors='replace')),delimiter='\t'):
        literal=row['text'].strip()
        if not literal:continue
        box=[int(row['left']),int(row['top']),int(row['left'])+int(row['width']),int(row['top'])+int(row['height'])]
        words.append(dict(text=literal,bounds=box,confidence=row['conf']))
    return words,proc.stdout

def cell_second_pass(image,box):
    x0,y0,x1,y1=box
    window=(max(0,x0+3),max(0,y0+5),min(image.width,x1+15),min(image.height,y1-5))
    if window[0]>=window[2] or window[1]>=window[3]:return dict(status='invalid_target_box')
    crop=image.crop(window)
    crop=crop.resize((crop.width*3,crop.height*3))
    stream=io.BytesIO();crop.save(stream,format='PNG')
    proc=subprocess.run(['tesseract','stdin','stdout','--psm','6',
                         '-c','tessedit_char_whitelist=0123456789'],
                        input=stream.getvalue(),capture_output=True,check=True)
    literal=proc.stdout.decode(errors='replace').strip()
    return dict(crop_box=list(window),crop_png_sha256=sha(stream.getvalue()),
                raw_ocr=literal,value_if_numeric=int(literal) if re.fullmatch(r'[0-9]+',literal) else None,
                status='cell_psm6_numeric_unaccepted' if re.fullmatch(r'[0-9]+',literal) else 'cell_psm6_missing_or_ambiguous')

def original(sid):
    receipt=next(r for r in receipts if r['id']==sid)
    raw=gzip.decompress((BASE/receipt['path']).read_bytes())
    assert sha(raw)==receipt['raw_sha256']
    return raw,receipt

def extract(source,second_pass=False):
    sid=source['source_id'];raw,receipt=original(sid)
    assert receipt['raw_sha256']==source['source_raw_sha256']
    doc=fitz.open(stream=raw,filetype='pdf')
    pages=[];counts=dict(targeted_cells=0,single_numeric_token=0,no_token=0,ambiguous_or_noninteger=0)
    for hint in source['pages']:
        pg=hint['page'];image,png=render(doc[pg-1],hint)
        size=list(image.size)
        if size!=hint['render_size']:
            pages.append(dict(source_pdf_page=pg,render_size=size,target_render_size=hint['render_size'],
                              status='render_geometry_mismatch_no_cell_interpretation',
                              original_render_sha256=sha(png)))
            continue
        words,tsv=tsv_words(png)
        fields=[]
        for field in hint['fields']:
            cells=[]
            for cell in field['cells']:
                x0,y0,x1,y1=cell['box']
                present=[w for w in words if x0<=((w['bounds'][0]+w['bounds'][2])/2)<x1 and y0<=((w['bounds'][1]+w['bounds'][3])/2)<y1]
                ints=[w for w in present if re.fullmatch(r'[0-9][0-9,]*',w['text'])]
                value=int(ints[0]['text'].replace(',','')) if len(present)==len(ints)==1 else None
                status='single_numeric_token_unaccepted' if value is not None else 'no_token' if not present else 'ambiguous_or_noninteger'
                counts['targeted_cells']+=1;counts[status if status!='single_numeric_token_unaccepted' else 'single_numeric_token']+=1
                entry=dict(source_column=cell['source_column'],target_box=cell['box'],
                           raw_original_ocr_tokens=present,value_if_unambiguous=value,status=status)
                if second_pass and (status!='single_numeric_token_unaccepted' or cell['source_column']==len(hint['columns'])):
                    entry['second_pass']=cell_second_pass(image,cell['box'])
                cells.append(entry)
            fields.append(dict(candidate=field['candidate'],row_source_ordinal=field['row_source_ordinal'],
                               candidate_label_target_box=field['candidate_label_box'],cells=cells))
        tsv_path=OUT/f'qa/2018-native-numeric-aid/{sid}/p{pg:04d}-original-ocr.tsv.gz'
        tsv_path.parent.mkdir(parents=True,exist_ok=True)
        stored=gzip.compress(tsv,mtime=0);tsv_path.write_bytes(stored)
        pages.append(dict(source_pdf_page=pg,render_size=size,original_render_sha256=sha(png),
                          tsv_stored_path=str(tsv_path.relative_to(BASE)),tsv_stored_sha256=sha(stored),
                          tsv_raw_sha256=sha(tsv),fields=fields))
    output=dict(scope='Machine numeric OCR diagnostic only, independently rendered from exact original raw PDF; vote-free locator geometry is unaccepted and may miss rows, columns, printed X or zeros. Missing is not zero. No candidate value enters official or priority controls from this aid.',
                source_id=sid,source_original_path=receipt['path'],source_raw_sha256=receipt['raw_sha256'],
                vote_free_target_sha256=TARGET_SHA,pages=pages,counts=counts)
    diagnostic_path=OUT/f'qa/2018-native-numeric-aid/{sid}/diagnostic.json'
    diagnostic_path.parent.mkdir(parents=True,exist_ok=True)
    savejson(diagnostic_path,output)
    return counts

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',action='append');parser.add_argument('--cell-second-pass',action='store_true');parser.add_argument('--skip-existing',action='store_true');a=parser.parse_args()
    assert sha(TARGET.read_bytes())==TARGET_SHA
    hints=json.loads(TARGET.read_text())
    selected=set(a.source or [s['source_id'] for s in hints['sources']])
    known={s['source_id'] for s in hints['sources']};assert selected<=known
    for source in hints['sources']:
        if source['source_id'] not in selected:continue
        diagnostic_path=OUT/f"qa/2018-native-numeric-aid/{source['source_id']}/diagnostic.json"
        if a.skip_existing and diagnostic_path.exists():
            previous=json.loads(diagnostic_path.read_text())
            assert previous['source_raw_sha256']==source['source_raw_sha256']
            assert previous['vote_free_target_sha256']==TARGET_SHA
            print(source['source_id'],'previous diagnostic retained',flush=True)
            continue
        print(source['source_id'],extract(source,a.cell_second_pass),flush=True)

if __name__=='__main__':main()
