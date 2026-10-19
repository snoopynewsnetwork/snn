"""Repair small-label OCR omissions using full original presidential recap pages.
Never use absence of an OCR keyword as proof a reporting unit is absent.
"""
import gzip,io,json,re
import fitz,numpy as np
from PIL import Image
from acquire_sources import BASE,OUT,receipts,sha
from probe_native import ocr,deskew,groups
for r in receipts:
    f=OUT/'extracts'/(r['id']+'-page-probe.json.gz')
    if not f.exists():continue
    d=json.loads(gzip.decompress(f.read_bytes()));changed=[];raw=None;doc=None
    for p in d['pages']:
        st=p['label_probe'].lower()
        if p['required'] or len(re.findall(r'pres',st))<4:continue
        if raw is None:raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf')
        page=doc[p['page']-1];scale=min(2.5,3300/max(page.rect.width,page.rect.height));im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png'))).rotate(p['rotation_ccw'],expand=True);w,h=im.size;im,angle=deskew(im);a=np.array(im);mask=a<170
        p.update(required=True,selection_reason='presidential recap page; do not drop Senate from garbled small-label OCR',deskew_angle_ccw=angle,horizontal_line_positions=groups(np.flatnonzero(mask.sum(axis=1)>w*.5)),header_vertical_line_positions=groups(np.flatnonzero(mask[int(h*.16):int(h*.28)].sum(axis=0)>.65*(int(h*.28)-int(h*.16)))),full_ocr_tsv=ocr(im,3,True),header_ocr_tsv=ocr(im.crop((0,0,w,int(h*.35))).rotate(-90,expand=True),6,True))
        im.thumbnail((1800,1800));q=OUT/'qa'/f'{r["id"]}-p{p["page"]:02d}-upright.jpg';im.save(q,quality=85);p['preview']=str(q.relative_to(BASE));changed.append(p['page'])
    if changed:f.write_bytes(gzip.compress(json.dumps(d,ensure_ascii=False).encode(),mtime=0));print(r['id'],changed,flush=True)
