"""Locate possible statistics/method/summary panels in original county PDFs.

This is a visual-page OCR locator only. It neither accepts numerical glyphs nor
interprets a page without a keyword hit as proof that a field is unavailable.
"""
import argparse
import gzip
import io
import json
import subprocess
from PIL import Image
import fitz
from acquire_sources import BASE, OUT, receipts, savejson, sha


def classify(text):
    t=' '.join(text.lower().split())
    return {name: (word in t) for name,word in {
        'statistics':'statistics', 'registration':'registered voters',
        'ballots_cast':'ballots cast', 'contest_totals':'contest totals',
        'write_in_totals':'write-in totals', 'under_votes':'undervotes',
        'over_votes':'overvotes', 'method_absentee':'absentee',
        'method_affidavit':'affidavit', 'turnout':'turnout',
    }.items()}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',action='append')
    args=ap.parse_args()
    seen=set(args.source or [])
    selected=[r for r in receipts if r['id'].startswith('sos-2024-county-') and
              r['id'] not in ('sos-2024-county-recap-index','sos-2024-county-coahoma','sos-2024-county-pike') and
              (not seen or r['id'] in seen)]
    assert len(selected)==(len(seen) if seen else 82)
    results=[]
    for receipt in selected:
        raw=gzip.decompress((BASE/receipt['path']).read_bytes())
        assert sha(raw)==receipt['raw_sha256']
        doc=fitz.open(stream=raw,filetype='pdf')
        page_results=[]
        candidates={0,1,len(doc)-1,len(doc)-2,len(doc)-3}
        for index in sorted(i for i in candidates if 0<=i<len(doc)):
            page=doc[index]
            pix=page.get_pixmap(matrix=fitz.Matrix(1.7,1.7),colorspace=fitz.csGRAY)
            data=pix.tobytes('png')
            proc=subprocess.run(['tesseract','stdin','stdout','--psm','11'],
                                input=data,capture_output=True,check=True)
            text=proc.stdout.decode(errors='replace')
            page_results.append({'pdf_page':index+1,'render_size':[pix.width,pix.height],
                                 'render_sha256':sha(data),'ocr_text':text,
                                 'keyword_locator':classify(text)})
        results.append({'source_id':receipt['id'],'raw_sha256':receipt['raw_sha256'],
                        'page_count':len(doc),'inspected_page_count':len(page_results),
                        'pages':page_results})
        print(receipt['id'],len(doc),[(p['pdf_page'],[k for k,v in p['keyword_locator'].items() if v]) for p in page_results if any(p['keyword_locator'].values())],flush=True)
    savejson(OUT/'source/2024-county-panel-ocr-inventory.json',{
        'scope':'Original-PDF page locator only, first two and last three pages per preferred publication; OCR does not accept a value or establish panel absence elsewhere.',
        'source_views':len(results),'sources':results})


if __name__=='__main__':main()
