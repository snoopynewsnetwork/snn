"""Losslessly retain PDFs; render every page and extract full text separately.

Rendering is automated coverage, not a claim that a person viewed every page.
"""
import gzip,json
import fitz
from acquire import HERE,entity,sha

def render(output=HERE):
    (output/'pdf').mkdir(exist_ok=True); rows=[];seen={}
    for path in sorted((HERE/'requests').glob('*.json')):
        receipt=json.loads(path.read_bytes())
        if receipt['hops'][-1]['status']!=200:continue
        b=entity(receipt)
        if b is None or not b.startswith(b'%PDF'):continue
        key=receipt['key'];digest=sha(b)
        if digest in seen:
            rows.append({'request':key,'same_complete_original_as':seen[digest],'raw_sha256':digest});continue
        seen[digest]=key
        doc=fitz.open(stream=b,filetype='pdf');pages=[];text=[]
        for i,page in enumerate(doc):
            zoom=min(1400/page.rect.width,1400/page.rect.height)
            pix=page.get_pixmap(matrix=fitz.Matrix(zoom,zoom),alpha=False)
            name=f'{key}-page-{i+1:04}.png';png=pix.tobytes('png');(output/'pdf'/name).write_bytes(png)
            txt=page.get_text(sort=False);text.append({'page':i+1,'text':txt,'page_rect':list(page.rect),'rotation':page.rotation})
            pages.append({'page':i+1,'png':'pdf/'+name,'bytes':len(png),'sha256':sha(png),'width':pix.width,'height':pix.height})
        raw=json.dumps(text,ensure_ascii=False,indent=2).encode();(output/'pdf'/f'{key}-text.json.gz').write_bytes(gzip.compress(raw,mtime=0))
        rows.append({'request':key,'raw_sha256':digest,'pages':len(doc),'metadata':doc.metadata,'all_pages_rendered':True,'manual_view_scope':'see manual-review.json; automated rendering is not manual review','renders':pages,'text':'pdf/'+key+'-text.json.gz'})
        print(key,len(doc),flush=True)
    result={'renderer':'PyMuPDF '+fitz.VersionBind,'max_page_pixels':1400,'full_originals_retained':True,'documents':rows,'distinct_documents':len(seen),'all_pages':sum(r.get('pages',0) for r in rows)}
    (output/'pdf-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':render()
