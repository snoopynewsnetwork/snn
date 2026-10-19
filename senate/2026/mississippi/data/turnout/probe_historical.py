"""Independent original-page inventory for actual2018 special/runoff and2020 Senate.

Each page has its own orientation decision. Relevant text is source-positioned;
this is a reading aid, with county/native candidate balancing still required.
"""
import argparse,concurrent.futures,gzip,io,json,re
import fitz,numpy as np
from PIL import Image
from acquire_sources import BASE,OUT,receipts,sha
from probe_native import ocr,deskew,groups
def score(s):
    return sum(s.lower().count(t)*w for t,w in [('espy',10),('hyde',10),('mcdaniel',10),('bartee',10),('edwards',10),('senate',5),('president',2),('official',1),('recapitulation',2)])
def run(r):
    target=OUT/'extracts'/(r['id']+'-historical-probe.json.gz')
    if target.exists():return r['id'],'cached'
    raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');pages=[]
    for i,page in enumerate(doc):
        scale=min(2.5,3300/max(page.rect.width,page.rect.height));im0=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png')));trials=[]
        for rot in [0,90,-90,180]:
            im=im0.rotate(rot,expand=True);small=im.copy();small.thumbnail((1500,1500));w,h=small.size;st=ocr(small.crop((0,int(h*.15),int(w*.45),int(h*.94))))
            trials.append((score(st),rot,st))
        val,rot,st=max(trials,key=lambda x:x[0]);required=bool(re.search('espy|hyde|mcdaniel|bartee|edwards|senate|ballots|registered|under.?vote|over.?vote|absentee|affidavit',st,re.I));im=im0.rotate(rot,expand=True);w,h=im.size
        p=dict(page=i+1,rotation_ccw=rot,render_size=[w,h],source_rect=list(page.rect),label_probe=st,required=required)
        if required:
            im,angle=deskew(im);mask=np.array(im)<170;p.update(deskew_angle_ccw=angle,full_ocr_tsv=ocr(im,3,True),horizontal_line_positions=groups(np.flatnonzero(mask.sum(axis=1)>w*.5)))
            preview=im.copy();preview.thumbnail((1800,1800));q=OUT/'qa'/f'{r["id"]}-p{i+1:02d}-historical-upright.jpg';preview.save(q,quality=85);p['preview']=str(q.relative_to(BASE))
        pages.append(p)
    target.write_bytes(gzip.compress(json.dumps(dict(source_id=r['id'],raw_sha256=r['raw_sha256'],pdf_pages=len(doc),qualification='Independent original OCR reading aid, not unreviewed transcription authority',pages=pages),ensure_ascii=False).encode(),mtime=0))
    return r['id'],len(doc),sum(p['required'] for p in pages)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--prefix',default='sos-2018-runoff-county-');ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args();selected=[r for r in receipts if r['id'].startswith(a.prefix) and 'pdf' in str(r.get('headers',{})).lower()]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        for x in pool.map(run,selected):print(*x,flush=True)
