"""Independent original source-header OCR, no peer label used as input."""
import concurrent.futures,gzip,json
from PIL import Image
from sources import OUT,BASE,save,sha
from extract_native import ocr
from replay_reviewed_native import hint_snapshot
def run(s):
    dest=OUT/'extracts/reviewed-replay'/s['source_id']/'independent-headers.json.gz'
    if dest.exists():return s['source_id']
    prior=OUT/'extracts/direct-layout'/f'{s["source_id"]}.json.gz';old=json.loads(gzip.decompress(prior.read_bytes())) if prior.exists() else {};pages=[]
    for p in s['pages']:
        png=OUT/'extracts/reviewed-replay'/s['source_id']/f'p{p["page"]:04d}-original.png';im=Image.open(png);cols=[]
        oldcols=next((q.get('columns',[]) for q in old.get('pages',[]) if q['page']==p['page']),[])
        for c in p['columns']:
            hb=c['header_bounds'];oc=next((q for q in oldcols if q['header_box']==hb),None)
            label=oc['native_label_ocr'] if oc else ocr(im.crop(tuple(hb)).rotate(270,expand=True),6).strip()
            cols.append(dict(source_column=c['source_column'],header_bounds=hb,label_ocr=label,reading_origin='own earlier original-header OCR at exact same box' if oc else 'fresh own original-header OCR',qualification='Original-source OCR, pending independent label comparison/visual repairs; blank OCR is not evidence of absence.'))
        pages.append(dict(page=p['page'],render_size=list(im.size),raster_path=str(png.relative_to(BASE)),raster_sha256=sha(png.read_bytes()),columns=cols))
    dest.write_bytes(gzip.compress(json.dumps(dict(source_id=s['source_id'],raw_sha256=s['raw_sha256'],pages=pages),ensure_ascii=False).encode(),mtime=0));return s['source_id']
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for key in pool.map(run,hint_snapshot()['sources']):print(key,flush=True)
if __name__=='__main__':main()
