#!/usr/bin/env python3
"""OCR scanned relevant pages; original page remains source of truth.

No OCR count is accepted without row/column and county-vector reconciliation.
Temporary restored members are outside repo. MODE first scans first 10 pages;
MODE all covers remaining scanned pages for files with geographic blocks.
"""
from pathlib import Path
import concurrent.futures, gzip, hashlib, io, json, os, subprocess, sys
import fitz
from PIL import Image
OUT=Path(__file__).resolve().parents[1]
TMP=Path('/tmp/oregon-turnout-originals')
DEST=OUT/'source'/'ocr'
DEST.mkdir(exist_ok=True)
inv=json.loads((OUT/'source'/'original-inventory.json').read_bytes())

def job(item):
    key,num,rotation=item
    name=f'{key}-p{num:03d}'
    target=DEST/(name+'.txt.gz')
    if target.exists():return
    with fitz.open(TMP/(key+'.pdf')) as d:
        p=d[num-1]
        pix=p.get_pixmap(matrix=fitz.Matrix(2.5,2.5))
        im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        if rotation:im=im.rotate(rotation,expand=True)
        b=io.BytesIO();im.save(b,format='PNG')
    r=subprocess.run(['tesseract','stdin','stdout','--psm','3'],input=b.getvalue(),
                     capture_output=True,check=True,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
    target.write_bytes(gzip.compress(r.stdout,mtime=0))
    (DEST/(name+'.json')).write_text(json.dumps(dict(source_key=key,page=num,rotation_CCW=rotation,
        rendered_dpi=180,engine='tesseract '+subprocess.check_output(['tesseract','--version'],stderr=subprocess.STDOUT).decode().splitlines()[0],
        psm=3,original_member_sha256=next(x['original_sha256']for x in inv if x['source_key']==key),
        OCR_text_sha256=hashlib.sha256(r.stdout).hexdigest(),stderr=r.stderr.decode()),indent=2)+'\n')
    return name

def main():
    mode=sys.argv[1] if len(sys.argv)>1 else 'first'
    tasks=[]
    geographic={'2020-01','2020-06','2020-09','2020-11','2020-12','2020-16','2020-24','2020-27','2020-31','2020-32',
                '2022-05','2022-06','2022-12','2022-16','2022-23','2022-24','2022-25','2022-31','2022-35'}
    for row in inv:
        if 'member_name' not in row or row['original_kind']!='PDF':continue
        key=row['source_key'];text=gzip.decompress((OUT/row['text_path']).read_bytes()).decode().split('\f')
        for i in range(row['pages']):
            if len(text[i].strip())>100:continue
            if mode=='first' and i>=10:continue
            if mode=='all' and (key not in geographic or i<10):continue
            rotation=90 if key in {'2020-02','2020-30'} else 0
            tasks.append((key,i+1,rotation))
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for n,r in enumerate(pool.map(job,tasks)):
            if n%20==0:print(n,len(tasks),r,flush=True)

if __name__=='__main__':main()
