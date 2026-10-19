"""Source-position-preserving PDF text/OCR reading aids, never final authority.

Only requested pages are OCRed. Original full bytes include unrelated offices.
TSV retains every OCR token, source PDF/page, pixel box, confidence and orientation.
"""
from pathlib import Path
import argparse, concurrent.futures, gzip, io, json, os, subprocess
import fitz
from PIL import Image
from acquire_sources import BASE,OUT,receipts,sha,savejson

def extract(r,limit=4):
    path=OUT/'extracts'/(r['id']+'.json.gz')
    if path.exists():return r['id'],'cached'
    raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256']
    doc=fitz.open(stream=raw,filetype='pdf');pages=[]
    for i in range(min(limit,len(doc))):
        page=doc[i];scale=min(2.5,3600/max(page.rect.width,page.rect.height));pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY)
        img=Image.open(io.BytesIO(pix.tobytes('png')))
        # Scanners sometimes store portrait pages with landscape content.
        # Keep original orientation, plus all orientations if explicitly requested later.
        p=subprocess.run(['tesseract','stdin','stdout','--psm','3','tsv'],input=pix.tobytes('png'),capture_output=True,env=dict(os.environ,OMP_THREAD_LIMIT='1'),check=True)
        pages.append(dict(page=i+1,source_rect=list(page.rect),render_width=img.width,render_height=img.height,
                          text=page.get_text(),ocr_tsv=p.stdout.decode(),stderr=p.stderr.decode(),rotation=page.rotation))
    data=dict(source_id=r['id'],raw_sha256=r['raw_sha256'],pdf_pages=len(doc),ocr_pages=len(pages),
              qualification='Unreviewed OCR reading aid. Original PDF is transcription authority.',pages=pages)
    path.write_bytes(gzip.compress(json.dumps(data,ensure_ascii=False).encode(),mtime=0))
    return r['id'],len(doc)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prefix',default='sos-2024-county-');p.add_argument('--limit',type=int,default=4);p.add_argument('--jobs',type=int,default=3);a=p.parse_args()
    selected=[r for r in receipts if r['id'].startswith(a.prefix) and r['path'].endswith('.gz') and 'pdf' in r.get('headers',{}).get('Content-Type',r.get('headers',{}).get('content-type','')).lower()]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        for x in pool.map(lambda r:extract(r,a.limit),selected): print(*x,flush=True)
