"""Independent original PDF TOTAL-cell OCR aid for104 2020 publications.

The cards were rendered from original hash-checked PDFs with position-only
hints. This pass reads the source pixels; county/peer values are not inputs.
"""
import json,subprocess,tempfile
from pathlib import Path
from PIL import Image
from acquire_sources import BASE,OUT,sha,savejson

def main():
    root=OUT/'qa/2020-county-total-originals';idx=json.loads((root/'index.json').read_text());out=[]
    with tempfile.TemporaryDirectory(prefix='ms-2020-total-ocr-') as td:
        tmp=Path(td)/'target.png'
        for e in idx['entries']:
            card=Image.open(BASE/e['original_card'])
            if e['physical_grid_status']=='physical_rules_targetable':
                # Fixed card placement; left fragments, table rule and header
                # are excluded. Each printed numeric target is retained as a
                # separate OCR line, in source candidate row order.
                crop=card.crop((845,38,980,280));crop.save(tmp)
                results=[]
                for psm in [6,11]:
                    r=subprocess.run(['tesseract',str(tmp),'stdout','--psm',str(psm),'-c','tessedit_char_whitelist=0123456789'],capture_output=True,check=True)
                    literal=r.stdout.decode('utf-8','replace');lines=[x.strip() for x in literal.splitlines() if x.strip()]
                    values=[int(x) if x.isdigit() else None for x in lines]
                    results.append(dict(psm=psm,raw_text=literal,lines=lines,values=values))
                selected=results[0]['values'] if len(results[0]['values'])==3 and results[0]['values']==results[1]['values'] else None
            else:results=[];selected=None
            out.append(dict(source_id=e['source_id'],source_raw_sha256=e['source_raw_sha256'],source_page=e['source_page'],source_column_hint=e['source_column_hint'],column_hint_status=e['column_hint_status'],physical_grid_status=e['physical_grid_status'],source_bounds=e['source_bounds'],original_card=e['original_card'],original_card_sha256=e['card_sha256'],candidate_order_source_review_required=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards'],OCR_psm_results=results,provisional_three_values=selected,scope='Original OCR aid only. Values require direct source/header/candidate visual review, especially ordinal proposals.'))
    savejson(OUT/'2020-publication-original-total-ocr-aid.json',dict(source_count=len(out),three_value_OCR_agreement=sum(x['provisional_three_values'] is not None for x in out),untargetable_geometry=sum(x['physical_grid_status']!='physical_rules_targetable' for x in out),readings=out))
    print(len(out),'original source cards',sum(x['provisional_three_values'] is not None for x in out),'3-value OCR agreements',sum(x['physical_grid_status']!='physical_rules_targetable' for x in out),'untargetable physical grids')

if __name__=='__main__':main()
