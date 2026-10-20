#!/usr/bin/env python3
"""Reproduce selected original-page and Washington source-row raster QA."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import csv,gzip,io,json,tempfile
import fitz
from PIL import Image,ImageDraw
from extract_originals import body
OUT=Path(__file__).resolve().parents[1];SRC=OUT/'source';QA=SRC/'qa'

def original(key):
    if key=='washington-2024-precincts':
        r=json.loads((SRC/'acquired'/f'{key}.receipt.json').read_bytes());return gzip.decompress((SRC/'acquired'/r['response_entities'][-1]['asset']).read_bytes())
    pins={r['id']:r for r in json.loads((SRC/'shared-original-pins.json').read_bytes())}
    inv=next(r for r in json.loads((SRC/'original-inventory.json').read_bytes())if r['source_key']==key)
    return b''.join(body(pins[s])for s in inv['original_source_ids'])

def main():
    QA.mkdir(exist_ok=True)
    specs=[('2024-abstract',1,'2024-president-state-controls'),('2024-abstract',2,'2024-vice-president-overlap'),
        ('2020-abstract',2,'2020-senate-state-controls'),('2022-abstract',1,'2022-senate-state-controls'),
        ('2022-abstract',4,'2022-governor-state-controls'),('2024-Wasco',1,'2024-Wasco-p1')]
    for key,page,name in specs:
        with fitz.open(stream=original(key),filetype='pdf')as d:d[page-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(QA/(name+'.png')))
    plans={
        'washington-audit-0':{1:[28,31,33,40,41,44,48,50,53,59,60,62,64],2:[11,15,17,18,19,21,25,26,33,35,36,39,41,42,47,50,55,60,69],3:[14,27,28,32,41]},
        'washington-audit-1':{4:[27,30,32,39,40,43,47,49,52,57,58,59,61,63,72],5:[13,15,16,17,19,23,24,27,28,31,33,34,37,39,40,45,48,49,53,58,67],6:[11,16,24,25,29,38]},
        'washington-audit-controls':{3:[11,20,21,30,35,36,38],6:[17,18,27,32,33,35],7:[26],8:[22,23,71],9:[17,18,27,32,33,35]}}
    (QA/'render-plan.json').write_text(json.dumps(dict(primary_pages=specs,Washington_TSV_lines=plans,
        scope='Original raster clips only; no arithmetic or source image editing. OCR derivatives supply crop coordinates.'),indent=2)+'\n')
    with fitz.open(stream=original('washington-2024-precincts'),filetype='pdf')as d:
        for name,plan in plans.items():
            images=[]
            for pg,selected in plan.items():
                rows=csv.DictReader(io.StringIO(gzip.decompress((SRC/'refined-ocr'/f'washington-2024-precincts-p{pg:03d}.tsv.gz').read_bytes()).decode()),delimiter='\t',quoting=csv.QUOTE_NONE)
                groups={}
                for r in rows:
                    if r['text'].strip():groups.setdefault(tuple(r[x]for x in ['page_num','block_num','par_num','line_num']),[]).append(r)
                for ln,rs in enumerate(groups.values(),1):
                    if ln not in selected:continue
                    y=min(int(r['top'])for r in rs);h=max(int(r['top'])+int(r['height'])for r in rs)-y;p=d[pg-1]
                    pix=p.get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(15,(y-8)/4,p.rect.width-5,(y+h+8)/4))
                    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((1900,85));images.append((pg,ln,im))
            can=Image.new('RGB',(2100,sum(max(55,im.height+8)for _,_,im in images)),'white');dr=ImageDraw.Draw(can);y=0
            for pg,ln,im in images:dr.text((2,y+8),f'p{pg} L{ln}',fill='black');can.paste(im,(130,y));y+=max(55,im.height+8)
            can.save(QA/(name+'.png'))
if __name__=='__main__':main()
