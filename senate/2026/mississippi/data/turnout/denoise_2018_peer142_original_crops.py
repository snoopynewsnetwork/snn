"""Diagnostic line removal on first-pass ambiguous original-cell crops.

The exact initial crops and all prior OCR outputs remain unchanged. Masking
may erase a glyph, so a recognized token is only another visual-review lead.
"""
import argparse
import io
import json
import re
import subprocess
import numpy as np
from PIL import Image
from acquire_sources import BASE, OUT, savejson, sha


def read(src,dst):
    original=src.read_bytes()
    image=Image.open(io.BytesIO(original)).convert('L')
    array=np.array(image).copy()
    dark=array<120
    vertical=dark.mean(axis=0)>=.77
    horizontal=dark.mean(axis=1)>=.77
    array[:,vertical]=255
    array[horizontal,:]=255
    result=Image.fromarray(array).crop((12,8,max(13,image.width-12),max(9,image.height-8)))
    buf=io.BytesIO();result.save(buf,format='PNG');data=buf.getvalue()
    dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
    proc=subprocess.run(['tesseract','stdin','stdout','--psm','11','-c','tessedit_char_whitelist=0123456789Xx,'],
                        input=data,capture_output=True,check=True)
    literal=proc.stdout.decode(errors='replace').strip()
    value=int(literal.replace(',','')) if re.fullmatch(r'\d[\d,]*',literal) else None
    return {'initial_crop_path':str(src.relative_to(BASE)),
            'initial_crop_sha256':sha(original),
            'masked_vertical_column_count':int(vertical.sum()),
            'masked_horizontal_row_count':int(horizontal.sum()),
            'denoised_crop_path':str(dst.relative_to(BASE)),
            'denoised_crop_sha256':sha(data),
            'raw_OCR_PSM11':literal,
            'parsed_single_number_diagnostic':value,
            'status':'numeric_OCR_unaccepted' if value is not None else 'unresolved_OCR_unaccepted'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',action='append');ap.add_argument('--skip-existing',action='store_true');args=ap.parse_args()
    hint=json.loads((OUT/'source/2018-peer142-new64-vote-free-position-hints-v1.json').read_text())
    selected=set(args.source or (s['source_id'] for s in hint['sources']))
    assert selected<={s['source_id'] for s in hint['sources']}
    for source in hint['sources']:
        sid=source['source_id']
        if sid not in selected:continue
        root=OUT/f'qa/2018-peer142-original-tsv/{sid}'
        initial=root/'ambiguous-original-cell-recheck.json'
        dest=root/'denoised-original-cell-diagnostic.json'
        if args.skip_existing and dest.exists():
            old=json.loads(dest.read_text());assert old['source_id']==sid
            print(sid,'prior denoised original OCR retained',flush=True);continue
        body=json.loads(initial.read_text());assert body['source_id']==sid
        rows=[]
        for r in body['rows']:
            src=BASE/r['expanded_original_crop_path']
            assert sha(src.read_bytes())==r['expanded_original_crop_sha256']
            dst=root/'denoised-crops'/f"p{r['source_page']:04d}-r{r['source_row_ordinal']}-c{r['source_column']}.png"
            rows.append({'source_page':r['source_page'],
                         'source_row_ordinal':r['source_row_ordinal'],
                         'source_column':r['source_column'],
                         **read(src,dst)})
        savejson(dest,{'scope':'Diagnostic original-pixel line mask, separate from immutable first/second OCR. A numeric token or blank is not an accepted source value; original complete-page review still required.',
                       'source_id':sid,'source_raw_sha256':source['source_raw_sha256'],
                       'initial_recheck_path':str(initial.relative_to(BASE)),
                       'initial_recheck_sha256':sha(initial.read_bytes()),
                       'positions':len(rows),
                       'single_numeric_OCR_leads':sum(x['parsed_single_number_diagnostic'] is not None for x in rows),
                       'rows':rows})
        print(sid,len(rows),'line-mask leads',sum(x['parsed_single_number_diagnostic'] is not None for x in rows),flush=True)


if __name__=='__main__':main()
