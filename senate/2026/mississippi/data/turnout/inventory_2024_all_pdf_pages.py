"""Complete page-level OCR locator for original preferred 2024 county PDFs.

Reuses previously pinned first/last page OCR verbatim. Every other page is
rendered from the exact source original. OCR is never a vote transcription.
"""
import gzip
import json
import subprocess
import fitz
from acquire_sources import BASE, OUT, receipts, savejson, sha
from inventory_2024_county_panels import classify


def main():
    prior_path=OUT/'source/2024-county-panel-ocr-inventory.json'
    prior=json.loads(prior_path.read_text())
    assert prior['source_views']==82
    prior_sources={s['source_id']:s for s in prior['sources']}
    results=[]
    for receipt in receipts:
        sid=receipt['id']
        if sid not in prior_sources:
            continue
        old=prior_sources[sid]
        assert old['raw_sha256']==receipt['raw_sha256']
        raw=gzip.decompress((BASE/receipt['path']).read_bytes())
        assert sha(raw)==receipt['raw_sha256']
        doc=fitz.open(stream=raw,filetype='pdf')
        assert len(doc)==old['page_count']
        by_page={p['pdf_page']:p for p in old['pages']}
        pages=[]
        for i,page in enumerate(doc,1):
            if i in by_page:
                pages.append(by_page[i]);continue
            pix=page.get_pixmap(matrix=fitz.Matrix(1.7,1.7),colorspace=fitz.csGRAY)
            data=pix.tobytes('png')
            proc=subprocess.run(['tesseract','stdin','stdout','--psm','11'],
                                input=data,capture_output=True,check=True)
            output=proc.stdout.decode(errors='replace')
            pages.append({'pdf_page':i,'render_size':[pix.width,pix.height],
                          'render_sha256':sha(data),'ocr_text':output,
                          'keyword_locator':classify(output)})
        assert [p['pdf_page'] for p in pages]==list(range(1,len(doc)+1))
        results.append({'source_id':sid,'raw_sha256':receipt['raw_sha256'],
                        'page_count':len(doc),'pages':pages})
        print(sid,len(doc),[p['pdf_page'] for p in pages if any(p['keyword_locator'].values())],flush=True)
    assert len(results)==82
    body={'scope':'Every page of all82 preferred original county PDFs, OCR locator only; no numeric field, missing status or source absence accepted from OCR.',
          'prior_locator_path':'data/turnout/source/2024-county-panel-ocr-inventory.json',
          'prior_locator_sha256':sha(prior_path.read_bytes()),
          'source_views':82,'total_pdf_pages':sum(s['page_count'] for s in results),
          'sources':results}
    raw=(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    stored=gzip.compress(raw,compresslevel=9,mtime=0)
    path=OUT/'source/2024-county-panel-full-ocr-inventory.json.gz'
    path.write_bytes(stored)
    savejson(OUT/'2024-county-panel-locator-controls.json',{
        'source_views':82,'total_pdf_pages':body['total_pdf_pages'],
        'raw_sha256':sha(raw),'raw_bytes':len(raw),
        'stored_path':'data/turnout/source/2024-county-panel-full-ocr-inventory.json.gz',
        'stored_sha256':sha(stored),'stored_bytes':len(stored),
        'keyword_hits_by_source':{s['source_id']:[{'page':p['pdf_page'],
                                                   'keywords':[k for k,v in p['keyword_locator'].items() if v]}
                                                  for p in s['pages'] if any(p['keyword_locator'].values())]
                                  for s in results}})


if __name__=='__main__':main()
