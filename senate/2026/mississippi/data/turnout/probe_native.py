"""Find required 2024 Senate pages in COMPLETE county PDFs, orient scans.

Produces source-position reading aids, not silently accepted vote transcriptions.
Every PDF page is probed for required contests and participation/control labels.
"""
from pathlib import Path
import concurrent.futures,csv,gzip,io,json,os,re,subprocess
import fitz,numpy as np
from PIL import Image
from acquire_sources import BASE,OUT,receipts,source,sha,savejson
def ocr(im,psm=6,tsv=False,whitelist=None):
    b=io.BytesIO();im.save(b,format='PNG');args=['tesseract','stdin','stdout','--psm',str(psm)]
    if whitelist:args+=['-c','tessedit_char_whitelist='+whitelist]
    if tsv:args+=['tsv']
    r=subprocess.run(args,input=b.getvalue(),capture_output=True,env=dict(os.environ,OMP_THREAD_LIMIT='1'),check=True)
    return r.stdout.decode()
def score(s):return sum(s.lower().count(w)*n for w,n in [('pinkins',10),('wicker',10),('senate',8),('president',3),('official',2),('recapitulation',4),('united states',4),('election',1)])
def groups(xs,gap=4):
    gs=[]
    for x in xs:
        if gs and x-gs[-1][-1]<=gap:gs[-1].append(int(x))
        else:gs.append([int(x)])
    return [int(sum(g)/len(g)) for g in gs]
def deskew(im):
    small=im.copy();small.thumbnail((1200,1200));best=(0,0)
    for angle in np.arange(-2,2.01,.2):
        a=np.array(small.rotate(float(angle),expand=False,fillcolor=255));s=(a<160).sum(axis=1);val=np.sum(np.sort(s)[-35:]**2)
        if val>best[0]:best=(val,float(angle))
    return im.rotate(best[1],expand=False,fillcolor=255),best[1]
def run(r):
    out=OUT/'extracts'/(r['id']+'-page-probe.json.gz')
    if out.exists():return r['id'],'cached'
    raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];d=fitz.open(stream=raw,filetype='pdf');pages=[]
    default_rotation=None
    for i,p in enumerate(d):
        scale=min(2.5,3300/max(p.rect.width,p.rect.height));im=Image.open(io.BytesIO(p.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png')))
        if i==0 or default_rotation is None:
            trials=[]
            for rot in [0,90,-90,180]:
                trial=im.rotate(rot,expand=True);small=trial.copy();small.thumbnail((1500,1500));w,h=small.size
                st=ocr(small.crop((0,int(h*.2),int(w*.34),int(h*.92))))
                trials.append((score(st),rot,st))
            s,rot,st=max(trials,key=lambda x:x[0]);
            if i>=1:default_rotation=rot
        else:
            rot=default_rotation;temp=im.rotate(rot,expand=True);small=temp.copy();small.thumbnail((1500,1500));w,h=small.size;st=ocr(small.crop((0,int(h*.2),int(w*.34),int(h*.92))))
        im=im.rotate(rot,expand=True);w,h=im.size
        required=bool(re.search(r'pinkins|wicker|senate|ballots|registered|under.?votes|over.?votes|blank|absentee|affidavit',st,re.I))
        rec=dict(page=i+1,rotation_ccw=rot,source_rect=list(p.rect),label_probe=st,required=required,render_size=[w,h])
        if required:
            im,angle=deskew(im);a=np.array(im);mask=a<170
            ys=groups(np.flatnonzero(mask.sum(axis=1)>w*.5));xs=groups(np.flatnonzero(mask[int(h*.16):int(h*.28)].sum(axis=0)>.65*(int(h*.28)-int(h*.16))))
            rec.update(deskew_angle_ccw=angle,horizontal_line_positions=ys,header_vertical_line_positions=xs,
                       full_ocr_tsv=ocr(im,3,True),header_ocr_tsv=ocr(im.crop((0,0,w,int(h*.35))).rotate(90,expand=True),6,True))
            im.thumbnail((1800,1800));q=OUT/'qa'/f'{r["id"]}-p{i+1:02d}-upright.jpg';im.save(q,quality=85);rec['preview']=str(q.relative_to(BASE))
        pages.append(rec)
    data=dict(source_id=r['id'],raw_sha256=r['raw_sha256'],pdf_pages=len(d),pages=pages,qualification='OCR and grid locations are unreviewed reading aids. Native cells must reconcile independently.')
    out.write_bytes(gzip.compress(json.dumps(data,ensure_ascii=False).encode(),mtime=0))
    return r['id'],len(d),sum(p['required'] for p in pages)
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--only');ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args()
    selected=[r for r in receipts if r['id'].startswith('sos-2024-county-') and 'pdf' in str(r.get('headers',{})).lower() and (not a.only or r['id'].endswith(a.only))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        for x in pool.map(run,selected):print(*x,flush=True)
