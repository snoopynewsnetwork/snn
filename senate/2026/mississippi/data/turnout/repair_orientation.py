"""Reinspect compiled county packets whose pages change orientation/layout.
Original page numbers remain fixed; an initial certificate cannot orient later forms.
"""
import concurrent.futures,gzip,io,json,re
import fitz,numpy as np
from PIL import Image
from acquire_sources import BASE,OUT,receipts,sha
from probe_native import ocr,score,deskew,groups
NAMES=['attala','leflore','grenada','montgomery','tippah','humphreys','tunica','jones','kemper','quitman','bolivar','calhoun','tishomingo','newton','george','tallahatchie','warren','franklin','itawamba']
def run(name):
    sid='sos-2024-county-'+name;r=next(r for r in receipts if r['id']==sid);f=OUT/'extracts'/(sid+'-page-probe.json.gz');d=json.loads(gzip.decompress(f.read_bytes()));raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');changes=[]
    for p in d['pages']:
        if score(p['label_probe'])>=15:continue
        page=doc[p['page']-1];scale=min(2.5,3300/max(page.rect.width,page.rect.height));im0=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png')));trials=[]
        for rot in [0,90,-90,180]:
            im=im0.rotate(rot,expand=True);small=im.copy();small.thumbnail((1500,1500));w,h=small.size;st=ocr(small.crop((0,int(h*.15),int(w*.43),int(h*.94))))
            trials.append((score(st),rot,st))
        val,rot,st=max(trials,key=lambda x:x[0])
        required=bool(re.search(r'pinkins|wicker|senate|ballots|registered|under.?votes|over.?votes|blank|absentee|affidavit',st,re.I) or len(re.findall('pres',st,re.I))>=4)
        if not required or (rot==p['rotation_ccw'] and p['required']):continue
        im=im0.rotate(rot,expand=True);w,h=im.size;im,angle=deskew(im);mask=np.array(im)<170
        p.update(required=True,rotation_ccw=rot,label_probe=st,selection_reason='Adaptive reinspection of each compiled packet page',render_size=[w,h],deskew_angle_ccw=angle,horizontal_line_positions=groups(np.flatnonzero(mask.sum(axis=1)>w*.5)),header_vertical_line_positions=groups(np.flatnonzero(mask[int(h*.16):int(h*.28)].sum(axis=0)>.65*(int(h*.28)-int(h*.16)))),full_ocr_tsv=ocr(im,3,True),header_ocr_tsv=ocr(im.crop((0,0,w,int(h*.35))).rotate(-90,expand=True),6,True))
        im.thumbnail((1800,1800));q=OUT/'qa'/f'{sid}-p{p["page"]:02d}-upright.jpg';im.save(q,quality=85);p['preview']=str(q.relative_to(BASE));changes.append((p['page'],rot))
    if changes:
        f.write_bytes(gzip.compress(json.dumps(d,ensure_ascii=False).encode(),mtime=0))
        # Recompute only owned OCR derivatives that were based on the obsolete probe.
        old=OUT/'extracts'/(sid+'-native-grid-v5.json.gz')
        if old.exists():old.unlink()
    return sid,changes
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for x in pool.map(run,NAMES):print(*x,flush=True)
