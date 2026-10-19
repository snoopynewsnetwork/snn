"""Re-read primary summary/statistics pages at peer-shared page pointers only."""
import concurrent.futures,csv,gzip,io,json,re
import fitz
from PIL import Image
from sources import *
from extract_native import ocr,words,cell_key
def pointers():
    refs=[]
    for filename in ['canvass-summary-readings.json','canvass-statistics-readings.json']:
        p=BASE/'data/turnout'/filename;raw=p.read_bytes();x=json.loads(raw);a=x if isinstance(x,list) else x['sources']
        for r in a:refs.append(dict(source_id=r['source_id'],page=r['page'],kind='statistics' if 'statistics' in filename else 'candidate_summary',pointer_reference=str(p.relative_to(BASE)),pointer_reference_sha256=sha(raw)))
    save(OUT/'source/summary-page-pointers.json',refs);return refs
def read(r):
    key=r['source_id'];pg=r['page'];dest=OUT/'extracts/summary-pages'/f'{key}-p{pg}.json.gz';dest.parent.mkdir(exist_ok=True)
    if dest.exists() and json.loads(gzip.decompress(dest.read_bytes())).get('parser_version')=='summary-2':return
    d=fitz.open(stream=original(key),filetype='pdf');p=d[pg-1];scale=min(2.5,3300/max(p.rect.width,p.rect.height));im=Image.open(io.BytesIO(p.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png')))
    native=OUT/'extracts/native-v4'/key/f'p{pg:04d}.json.gz';rot=json.loads(gzip.decompress(native.read_bytes())).get('rotation_ccw',0) if native.exists() else 0;im=im.rotate(rot,expand=True);rendersize=list(im.size)
    tsv=ocr(im,6,True);ww=words(tsv);lines={}
    for w in ww:lines.setdefault((w['block_num'],w['par_num'],w['line_num']),[]).append(w)
    rr=[];context='unclassified'
    for ws in lines.values():
        line=' '.join(w['text'] for w in ws)
        if re.search(r'president.*united|united.*president|president of the united',line,re.I):context='president'
        if re.search(r'senate.*united|united.*senate',line,re.I):context='senate'
        if re.search(r'house of rep|supreme court|circuit court|school board',line,re.I):context='unrelated'
        field=cell_key(line)
        if re.search('contest totals',line,re.I):field='contest opportunities'
        if field:
            nums=[dict(literal=w['text'],value=int(w['text'].replace(',','')),box=[int(w[k]) for k in ['left','top','width','height']]) for w in ws if re.fullmatch(r'\d[\d,]*',w['text'])]
            rr.append(dict(office_context=context,field=field,line_ocr=line,number_tokens=nums,raw_words=ws))
    preview=OUT/'qa'/f'{key}-summary-review-p{pg}.png';im.thumbnail((1800,2200));im.save(preview)
    dest.write_bytes(gzip.compress(json.dumps(dict(**r,parser_version='summary-2',raw_sha256=sha(original(key)),render_size=rendersize,rotation_ccw=rot,pdf_text=p.get_text(),full_ocr_tsv=tsv,required_rows=rr,preview=str(preview.relative_to(BASE)),qualification='Independently rendered/read original; shared pointer contains page only. Numeric/label OCR still subject to direct visual/control review.'),ensure_ascii=False).encode(),mtime=0))
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for _ in pool.map(read,pointers()):pass
