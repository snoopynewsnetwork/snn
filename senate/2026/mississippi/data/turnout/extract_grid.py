"""Recover native SEMS grid cells with page/box/literal evidence and balance flags.

No OCR value is silently corrected by a county/state residual. Empty is unknown.
Aggregate TOTAL columns and unused template columns remain distinct from units.
"""
import argparse,concurrent.futures,csv,gzip,io,json,re
import fitz,numpy as np
from PIL import Image,ImageOps
from acquire_sources import BASE,OUT,receipts,sha,savejson
from probe_native import ocr,groups

def tokens(tsv):
    return [r for r in csv.DictReader(io.StringIO(tsv),delimiter='\t',quoting=csv.QUOTE_NONE) if r.get('text','').strip()]
def makeimage(r,page):
    raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];d=fitz.open(stream=raw,filetype='pdf');p=d[page['page']-1];scale=min(2.5,3300/max(p.rect.width,p.rect.height));im=Image.open(io.BytesIO(p.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png')))
    return im.rotate(page['rotation_ccw'],expand=True).rotate(page.get('deskew_angle_ccw',0),expand=False,fillcolor=255)
def batchnumbers(crops):
    # Each source cell has a separate vertically indexed OCR line in a white frame.
    step=90;width=400;canvas=Image.new('L',(width,step*len(crops)),255)
    for i,im in enumerate(crops):
        im=ImageOps.autocontrast(im);im.thumbnail((width-30,step-30));canvas.paste(im,(15,i*step+15))
    t=ocr(canvas,6,True,whitelist='0123456789,');res=[]
    rr=tokens(t)
    for i in range(len(crops)):
        tt=[r['text'] for r in rr if i*step<=int(r['top'])+int(r['height'])/2<(i+1)*step]
        text=' '.join(tt);clean=text.replace(',','').strip();res.append(dict(ocr_literal=text,value=int(clean) if clean.isdigit() else None))
    return res,t
def cellnumber(crop):
    a=np.array(crop);black=a<160
    # Erase only near-continuous table rules, preserving touching digit pixels.
    rows=np.flatnonzero(black.sum(axis=1)>a.shape[1]*.5);cols=np.flatnonzero(black.sum(axis=0)>a.shape[0]*.5)
    a[rows,:]=255;a[:,cols]=255
    h,w=a.shape;region=[int(w*.17),2,w-1,int(h*.65)]
    clean=Image.fromarray(a).crop(region);clean=clean.resize((clean.width*3,clean.height*3))
    clean=ImageOps.expand(clean,20,255)
    text=ocr(clean,7,whitelist='0123456789').strip()
    return dict(ocr_literal=text,value=int(text) if text.isdigit() else None,removed_rule_rows=rows.tolist(),removed_rule_columns=cols.tolist())
def run(sid):
    target=OUT/'extracts'/(sid+'-native-grid-v5.json.gz')
    if target.exists():return sid,'cached'
    pr=OUT/'extracts'/(sid+'-page-probe.json.gz')
    if not pr.exists():return sid,'no_probe_yet'
    data=json.loads(gzip.decompress(pr.read_bytes()));r=next(r for r in receipts if r['id']==sid);pages=[];header_reference=None
    for p in data['pages']:
        if not p['required']:continue
        tt=tokens(p['full_ocr_tsv']);cand={}
        for name,pattern in [('Ty Pinkins','pinkins|pinkin|pinks'),('Roger F. Wicker','wicker|wicke')]:
            matches=[x for x in tt if re.search(pattern,x['text'],re.I) and int(x['left'])<p['render_size'][0]*.30]
            if matches:cand[name]=min(matches,key=lambda x:int(x['top']))
        presidential_template=len(re.findall(r'pres',p['label_probe'],re.I))>=4
        if presidential_template:
            for name,ratio in [('Ty Pinkins',.785),('Roger F. Wicker',.82)]:
                if name not in cand:cand[name]={'top':str(round(p['render_size'][1]*ratio)),'height':'0','position_method':'SEMS presidential/Senate template row, requires visual verification'}
        if not cand:continue
        im=makeimage(r,p);w,h=im.size;xs=p.get('header_vertical_line_positions',[]);ys=p.get('horizontal_line_positions',[])
        if not presidential_template:
            pages.append(dict(page=p['page'],status='non_presidential_template_requires_separate_extraction',candidates_found=list(cand)));continue
        mask=np.array(im)<170;projection=mask.sum(axis=1);tops=np.argsort(projection)[-25:];extents=[]
        for yy in tops:
            xx=np.flatnonzero(mask[yy])
            if len(xx) and xx[-1]-xx[0]>w*.45:extents.append((int(xx[0]),int(xx[-1])))
        if not extents:pages.append(dict(page=p['page'],status='unresolved_form_extent'));continue
        formleft,formright=[int(np.median([e[j] for e in extents])) for j in [0,1]];formwidth=formright-formleft
        expected_header_height=formwidth*.1253
        gaps=[(b-a,a,b) for a,b in zip(ys,ys[1:]) if h*.08<a<b<h*.5 and expected_header_height*.8<b-a<expected_header_height*1.2]
        if gaps:
            _,header_y0,header_y1=max(gaps)
            header_reference=(header_y0/h,header_y1/h)
        elif header_reference:header_y0,header_y1=[round(h*x) for x in header_reference]
        else:header_y0,header_y1=round(h*.145),round(h*.294)
        band=mask[header_y0+4:header_y1-4];vx=groups(np.flatnonzero(band.sum(axis=0)>band.shape[0]*.65));pred=formleft+formwidth*.294
        near=[x for x in vx if abs(x-pred)<formwidth*.035];left=min(near,key=lambda x:abs(x-pred)) if near else round(pred);right=formright;n=11
        edges=[round(left+(right-left)*i/n) for i in range(n+1)]
        headerheight=header_y1-header_y0
        for name,ratio in [('Ty Pinkins',3.32),('Roger F. Wicker',3.57)]:
            predicted=header_y1+headerheight*ratio
            if cand[name].get('position_method') or abs(int(cand[name]['top'])-predicted)>headerheight*.35:cand[name]={'top':str(round(predicted)),'height':'0','position_method':'Source SEMS grid row geometry; visual/balance verification required'}
        cols=[]
        for j,(x0,x1) in enumerate(zip(edges,edges[1:])):
            box=[x0+4,header_y0+4,x1-4,header_y1-4];crop=im.crop(box).rotate(-90,expand=True);label=ocr(crop,6).strip()
            cols.append(dict(source_column=j+1,header_box=box,label_ocr=label,identity_status='unreviewed',votes={}))
        allcrops=[];positions=[]
        for name,t in cand.items():
            cy=int(t['top'])+int(t['height'])/2
            below=[y for y in ys if y>cy];above=[y for y in ys if y<cy];y0=max(above) if above else round(cy-h*.02);y1=min(below) if below else round(cy+h*.02)
            if not h*.02<y1-y0<h*.065:y0=round(cy-h*.016);y1=round(cy+h*.022)
            for j,(x0,x1) in enumerate(zip(edges,edges[1:])):
                box=[x0-1,y0,x1+2,y1+1];allcrops.append(im.crop(box));positions.append((name,j,box))
        nums=[cellnumber(crop) for crop in allcrops]
        for (name,j,box),num in zip(positions,nums):cols[j]['votes'][name]=dict(num,box=box)
        pages.append(dict(page=p['page'],status='unreviewed_grid_extraction',render_size=[w,h],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p.get('deskew_angle_ccw'),columns=cols))
    target.write_bytes(gzip.compress(json.dumps(dict(source_id=sid,raw_sha256=r['raw_sha256'],pages=pages),ensure_ascii=False).encode(),mtime=0))
    return sid,len(pages),sum(len(p.get('columns',[])) for p in pages)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--only');ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args()
    sources=[r['id'] for r in receipts if r['id'].startswith('sos-2024-county-') and 'pdf' in str(r.get('headers',{})).lower() and (not a.only or r['id'].endswith(a.only))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        for x in pool.map(run,sources):print(*x,flush=True)
