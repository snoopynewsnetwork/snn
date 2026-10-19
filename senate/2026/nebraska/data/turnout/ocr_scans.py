"""Reproducible OCR of complete retained scans; OCR is a reading aid only.

All pages retained in order in gzip text; raw PDF bytes remain authoritative.
Selected-contest numeric transcription must reconcile and be visually checked.
"""
from source_io import *
import concurrent.futures, re

IDS=['sos-2024-county-deuel-indexed-unofficial','sos-2024-county-garfield-indexed-official','sos-2024-county-york-indexed-official']
def main():
    receipts=[]
    for sid in IDS:
        b=original(sid)
        with tempfile.TemporaryDirectory(prefix='ne-turnout-ocr-')as td:
            td=Path(td);pdf=td/'original.pdf';pdf.write_bytes(b)
            info=subprocess.check_output(['pdfinfo',str(pdf)]).decode();pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1])
            def page(p):
                stem=td/str(p)
                subprocess.run(['pdftoppm','-f',str(p),'-singlefile','-scale-to','2200','-png',str(pdf),str(stem)],check=True,capture_output=True)
                txt=subprocess.check_output(['tesseract',str(stem)+'.png','stdout','--psm','6'],stderr=subprocess.DEVNULL)
                if p==1:(OUT/'source'/f'{sid}-page1.png').write_bytes(stem.with_suffix('.png').read_bytes())
                return {'actual_pdf_page':p,'text':txt.decode(),'ocr_engine':'tesseract --psm 6','render':'pdftoppm -scale-to 2200 PNG'}
            with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(page,range(1,pages+1)))
            jlwrite(OUT/'extracts'/f'{sid}.ocr-pages.jsonl.gz',rows)
            receipts.append({'source_id':sid,'raw_sha256':sha(b),'actual_pages':pages,'ocr_pages':len(rows),
              'qualification':'OCR aid, not automatic authoritative transcription. Original complete images remain in exact-hash PDF reference.'})
            print(sid,pages,flush=True)
    jwrite(OUT/'extracts/scan-coverage.json',receipts)
if __name__=='__main__':main()
