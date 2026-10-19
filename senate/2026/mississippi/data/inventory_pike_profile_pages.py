"""Independent complete-page inventory of original Pike profile section."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import io
import json
import subprocess
import tempfile
from PIL import Image

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
DEST=DATA/'coordinator-qa/pike-profile-review'
def sha(b):return hashlib.sha256(b).hexdigest()

def main():
    raw=gzip.decompress((DATA/'news/sos-2024-county-pike.html.gz').read_bytes())
    assert sha(raw)=='c036b699e98807c6c80f61afbd43545aa900d07380975dac1ab75bf0d4d25c63'
    def one(page,pdf):
        prefix=DEST/f'inventory-p{page}'
        path=prefix.with_suffix('.png')
        if not path.exists():
            subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-r','90',
                            '-singlefile','-png',str(pdf),str(prefix)],check=True,capture_output=True)
        im=Image.open(path)
        crop=im.crop((0,0,im.width,180))
        buff=io.BytesIO();crop.save(buff,format='PNG')
        result=subprocess.run(['tesseract','stdin','stdout','--psm','6'],input=buff.getvalue(),
                              capture_output=True,check=True).stdout.decode()
        return {'source_page':page,'whole_original_render':str(path.relative_to(ROOT)),
                'render_sha256':sha(path.read_bytes()),'header_crop_pixels':[0,0,im.width,180],
                'render_dpi':90,'raw_header_OCR':result}
    with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
        f.write(raw);f.flush()
        with ThreadPoolExecutor(max_workers=4) as pool:
            result=list(pool.map(lambda p:one(p,f.name),range(15,57)))
    p=DEST/'independent-42page-inventory.json'
    p.write_text(json.dumps({'source_sha256':sha(raw),'pages':result},indent=2)+'\n')
    for r in result:print(r['source_page'],r['raw_header_OCR'].replace('\n',' | ')[:250])

if __name__=='__main__':main()
