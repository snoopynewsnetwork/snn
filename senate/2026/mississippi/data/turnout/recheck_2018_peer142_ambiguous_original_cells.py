"""Second original-pixel OCR pass only on first-pass ambiguous source cells.

Selection uses our own original-page OCR status, never peer values. Expanded
crop windows remain provisional and can include adjacent printed material.
"""
import argparse
import io
import json
import re
import subprocess
from PIL import Image
from acquire_sources import BASE, OUT, savejson, sha

HINT=OUT/'source/2018-peer142-new64-vote-free-position-hints-v1.json'
HINT_SHA='7fc12ad227424e27687945661d5c58e86075bac612b146600ed5d290c9fde93e'


def read_cell(image,box,path):
    x0,y0,x1,y1=box
    broad=[max(0,x0-7),max(0,y0-5),min(image.width,x1+7),min(image.height,y1+5)]
    crop=image.crop(tuple(broad))
    crop=crop.resize((crop.width*3,crop.height*3))
    buf=io.BytesIO();crop.save(buf,format='PNG');data=buf.getvalue();path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    proc=subprocess.run(['tesseract','stdin','stdout','--psm','6','-c','tessedit_char_whitelist=0123456789Xx,'],
                        input=data,capture_output=True,check=True)
    literal=proc.stdout.decode(errors='replace').strip()
    value=int(literal.replace(',','')) if re.fullmatch(r'\d[\d,]*',literal) else None
    return {'expanded_original_crop_path':str(path.relative_to(BASE)),
            'expanded_original_crop_sha256':sha(data),
            'expanded_original_crop_bounds':broad,
            'raw_original_OCR_PSM6':literal,
            'parsed_single_number_diagnostic':value,
            'status':'numeric_OCR_unaccepted' if value is not None else 'unresolved_OCR_unaccepted'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',action='append');ap.add_argument('--skip-existing',action='store_true');args=ap.parse_args()
    assert sha(HINT.read_bytes())==HINT_SHA
    sources=json.loads(HINT.read_text())['sources']
    selected=set(args.source or (s['source_id'] for s in sources))
    assert selected<={s['source_id'] for s in sources}
    for s in sources:
        sid=s['source_id']
        if sid not in selected:continue
        path=OUT/f'qa/2018-peer142-original-tsv/{sid}/ambiguous-original-cell-recheck.json'
        if args.skip_existing and path.exists():
            old=json.loads(path.read_text());assert old['source_id']==sid and old['hint_sha256']==HINT_SHA
            print(sid,'prior ambiguous recheck retained',flush=True);continue
        first_path=OUT/f'qa/2018-peer142-original-tsv/{sid}/diagnostic.json'
        first=json.loads(first_path.read_text());assert first['source_raw_sha256']==s['source_raw_sha256']
        reviewed=[]
        for page in first['pages']:
            raster=BASE/page['original_render_path']
            assert sha(raster.read_bytes())==page['original_render_sha256']
            image=Image.open(raster).convert('L')
            for field in page['fields']:
                for cell in field['cells']:
                    if cell['parsed_single_number_diagnostic'] is not None:continue
                    n=page['source_pdf_page'];row=field['source_row_ordinal'];col=cell['source_column']
                    crop_path=OUT/f'qa/2018-peer142-original-tsv/{sid}/ambiguous-crops/p{n:04d}-r{row}-c{col}.png'
                    reading=read_cell(image,cell['target_box'],crop_path)
                    reviewed.append({'source_page':n,'source_row_ordinal':row,'source_column':col,
                                     'first_pass_tokens':[x['text'] for x in cell['original_page_tsv_tokens']],
                                     **reading})
        savejson(path,{'scope':'Second original-pixel OCR of all first-pass ambiguous cells, selected without peer values; neither crop geometry nor numeric OCR accepted until direct source review.',
                       'source_id':sid,'source_raw_sha256':s['source_raw_sha256'],
                       'first_original_diagnostic_path':str(first_path.relative_to(BASE)),
                       'first_original_diagnostic_sha256':sha(first_path.read_bytes()),
                       'hint_sha256':HINT_SHA,'rechecked_positions':len(reviewed),
                       'single_numeric_OCR_leads':sum(x['parsed_single_number_diagnostic'] is not None for x in reviewed),
                       'rows':reviewed})
        print(sid,len(reviewed),'ambiguous',flush=True)


if __name__=='__main__':main()
