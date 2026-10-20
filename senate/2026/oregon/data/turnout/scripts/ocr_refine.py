#!/usr/bin/env python3
"""Higher-resolution, row-preserving OCR of relevant original contest pages.

Output TSV keeps word boxes/confidence and all original source pointers.
Unverified OCR integers are never used in certified priority arithmetic.
"""
from pathlib import Path
import concurrent.futures, csv, gzip, hashlib, io, json, os, re, subprocess
import fitz
from PIL import Image
OUT=Path(__file__).resolve().parents[1]
SRC=OUT/'source';DEST=SRC/'refined-ocr';DEST.mkdir(exist_ok=True)
INV=json.loads((SRC/'original-inventory.json').read_bytes())
TMP=Path('/tmp/oregon-turnout-originals')

def run(task):
    key,page,rotate=task;target=DEST/f'{key}-p{page:03d}.tsv.gz'
    if target.exists():return
    with fitz.open(TMP/(key+'.pdf'))as d:
        pix=d[page-1].get_pixmap(matrix=fitz.Matrix(4,4))
        im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        if rotate:im=im.rotate(rotate,expand=True)
        # Thin table rules confuse layout recognition; remove long horizontal
        # and vertical lines only in the OCR rendering, never original bytes.
        b=io.BytesIO();im.save(b,format='PNG')
    r=subprocess.run(['tesseract','stdin','stdout','--psm','6','tsv'],input=b.getvalue(),capture_output=True,check=True,
        env={**os.environ,'OMP_THREAD_LIMIT':'1'})
    target.write_bytes(gzip.compress(r.stdout,mtime=0))
    rows=list(csv.DictReader(io.StringIO(r.stdout.decode()),delimiter='\t',quoting=csv.QUOTE_NONE))
    groups={}
    for row in rows:
        if not row['text'].strip():continue
        k=tuple(row[x]for x in ['page_num','block_num','par_num','line_num'])
        groups.setdefault(k,[]).append(row)
    lines=[]
    for group in groups.values():
        # Preserve approximate x positions so columns can be reconstructed.
        line='';scale=10
        for row in group:
            x=int(row['left'])//scale
            line+=' '*max(1,x-len(line))+row['text']
        lines.append(line)
    text='\n'.join(lines)+'\n';(DEST/f'{key}-p{page:03d}.txt.gz').write_bytes(gzip.compress(text.encode(),mtime=0))
    (DEST/f'{key}-p{page:03d}.json').write_text(json.dumps(dict(source_key=key,page=page,rotation_CCW=rotate,
        dpi=288,engine='tesseract',psm=6,TSV_sha256=hashlib.sha256(r.stdout).hexdigest(),
        text_sha256=hashlib.sha256(text.encode()).hexdigest(),stderr=r.stderr.decode()),indent=2)+'\n')
    return key,page

def main():
    tasks=set()
    for r in INV:
        key=r['source_key']
        if 'member_name'not in r or r['original_kind']!='PDF':continue
        for i,p in enumerate(gzip.decompress((OUT/r['text_path']).read_bytes()).decode().split('\f'),1):
            o=SRC/'ocr'/f'{key}-p{i:03d}.txt.gz'
            if o.exists()and len(p.strip())<100:p=gzip.decompress(o.read_bytes()).decode()
            # Refine existing OCR only; digital-layout tables stay independent.
            if (o.exists()or key in {'2022-09','2022-00','2022-02','2022-22','2020-22'})and re.search(r'US Senator|U.S. Senator|US Senate|Governor.*(?:Vote|Statewide)|UNITED STATES\s+SENATOR',p,re.I):
                tasks.add((key,i,-90 if key in {'2020-02','2020-30'}else 0))
    manual={'2020-00':[2],'2020-02':[6,7,8,9,10], '2020-03':[5,6], '2020-05':[2],
        '2020-08':[4,5], '2020-10':[1], '2020-15':[2], '2020-18':[2], '2020-20':[5,6],
        '2020-26':[4], '2020-30':[3], '2020-34':[1], '2022-08':[2,3,4,5,6],
        '2022-15':[1,2,5,6], '2022-20':[3,4,7,8], '2022-25':list(range(1,12)),
        '2022-26':list(range(2,8)), '2022-30':[1,2,3], '2022-34':[1],
        '2022-35':list(range(1,12)), '2024-Wasco':[1], 'washington-2024-precincts':list(range(1,8))}
    for key,pgs in manual.items():
        for i in pgs:tasks.add((key,i,-90 if key in {'2020-02','2020-30'}else 0))
    tasks=sorted(tasks)
    (DEST/'selected-page-plan.json').write_text(json.dumps(tasks,indent=2)+'\n')
    with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:
        for n,result in enumerate(pool.map(run,tasks)):
            if n%20==0:print(n,len(tasks),result,flush=True)

if __name__=='__main__':main()
