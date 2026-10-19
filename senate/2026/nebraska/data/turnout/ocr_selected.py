"""Second independent OCR layout mode on all selected scanned contest pages.

Keeps complete original pages as numbered PNGs for visual transcription review.
The images are reading derivatives, never substitutes for original PDFs.
"""
from source_io import *
import concurrent.futures
CONFIG={'deuel':[1,2],'garfield':[1,6,13,14],'york':[1,9,18,25,32,41,50,57,63,69,75,82,89]}
def main():
    for county,pages in CONFIG.items():
        sid=f'sos-2024-county-{county}-indexed-'+('unofficial'if county=='deuel'else 'official');raw=original(sid)
        with tempfile.TemporaryDirectory(prefix='ne-turnout-selected-')as td:
            td=Path(td);p=td/'original.pdf';p.write_bytes(raw)
            def page(pn):
                stem=td/str(pn)
                subprocess.run(['pdftoppm','-f',str(pn),'-singlefile','-scale-to','3000','-png',str(p),str(stem)],check=True,capture_output=True)
                img=stem.with_suffix('.png')
                if county=='deuel':
                    subprocess.run(['magick',str(img),'-rotate','90',str(td/f'r{pn}.png')],check=True,capture_output=True);img=td/f'r{pn}.png'
                dest=OUT/'source'/f'{county}-page{pn}.png';dest.write_bytes(img.read_bytes())
                txt=subprocess.check_output(['tesseract',str(img),'stdout','--psm','3'],stderr=subprocess.DEVNULL)
                return {'source_id':sid,'actual_pdf_page':pn,'image':str(dest.relative_to(ROOT)),
                  'text':txt.decode(),'render':'pdftoppm -scale-to 3000 PNG; Deuel only rotated90 clockwise','OCR':'tesseract --psm 3'}
            with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(page,pages))
            jlwrite(OUT/'extracts'/f'{county}-selected-psm3.jsonl.gz',rows)
            print(county,len(rows),flush=True)
if __name__=='__main__':main()
