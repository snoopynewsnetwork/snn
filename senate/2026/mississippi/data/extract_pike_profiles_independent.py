"""Coordinator extraction from original Pike scan, before field comparison.

Only source hash and page starts are borrowed as discovery positions. Neither
worker labels nor numbers enter rendering/OCR. Original whole pages are kept.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
import subprocess
import tempfile

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
DEST = DATA / 'coordinator-qa/pike-profile-review'
PAGES = [15,17,19,21,23,25,26,28,29,30,32,34,36,38,40,42,43,44,45,46,47,49,51,53,55]

def sha(b):
    return hashlib.sha256(b).hexdigest()

def main():
    DEST.mkdir(exist_ok=True)
    receipts = json.loads((DATA / 'turnout/source/acquisition.json').read_bytes())
    meta = next(r for r in receipts if r['id'] == 'sos-2024-county-pike')
    stored = (ROOT / meta['path']).read_bytes()
    raw = gzip.decompress(stored)
    assert sha(stored) == meta['stored_sha256']
    assert sha(raw) == meta['raw_sha256'] == 'c036b699e98807c6c80f61afbd43545aa900d07380975dac1ab75bf0d4d25c63'
    def page_extract(page, pdf):
        prefix = DEST / f'independent-p{page}'
        image = prefix.with_suffix('.png')
        if not image.exists():
            subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-r','180',
                            '-singlefile','-png',str(pdf),str(prefix)],check=True,
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out = prefix.with_suffix('.ocr.txt.gz')
        if not out.exists():
            r = subprocess.run(['tesseract',str(image),'stdout','--psm','6'],
                               check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            out.write_bytes(gzip.compress(r.stdout,mtime=0))
        text = gzip.decompress(out.read_bytes()).decode()
        return {'source_page':page,'whole_original_render':str(image.relative_to(ROOT)),
                'render_sha256':sha(image.read_bytes()),'dpi':180,
                'ocr_file':str(out.relative_to(ROOT)),'ocr_stored_sha256':sha(out.read_bytes()),
                'ocr_text_sha256':sha(text.encode()),'text':text}
    with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
        tmp.write(raw)
        tmp.flush()
        with ThreadPoolExecutor(max_workers=4) as pool:
            result = list(pool.map(lambda p:page_extract(p,tmp.name),PAGES))
    payload = {'source_metadata':meta,'original_sha256':sha(raw),'page_starts':PAGES,
               'extraction_basis':'Whole exact original pages, Poppler180dpi then Tesseract psm6. Page-start positions only are discovery inputs; worker field values and labels are not extraction inputs.',
               'pages':result}
    target = DEST / 'independent-original-ocr.json.gz'
    target.write_bytes(gzip.compress((json.dumps(payload,indent=2)+'\n').encode(),mtime=0))
    print(json.dumps({'pages':len(result),'artifact':str(target.relative_to(ROOT)),
                      'sha256':sha(target.read_bytes())}))

if __name__ == '__main__':
    main()
