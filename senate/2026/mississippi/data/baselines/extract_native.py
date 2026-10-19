"""Independent complete-page OCR, grid coordinates and source-cell reading aids.

Never substitutes absent cells with zero. Original PDF remains authority.
Only requested candidate/control rows receive numeric cell extraction; all original
pages and their text/OCR positions survive. No cross-year geographic joins.
"""
import argparse,concurrent.futures,csv,gzip,io,json,os,re,subprocess
import fitz,numpy as np
from PIL import Image,ImageOps
from sources import *
def ocr(im,psm=6,tsv=False,numeric=False):
    b=io.BytesIO();im.save(b,format='PNG');cmd=['tesseract','stdin','stdout','--psm',str(psm)]
    if numeric:cmd+=['-c','tessedit_char_whitelist=0123456789,.-']
    if tsv:cmd+=['tsv']
    r=subprocess.run(cmd,input=b.getvalue(),capture_output=True,check=True,env=dict(os.environ,OMP_THREAD_LIMIT='1'))
    return r.stdout.decode()
def words(tsv):return [r for r in csv.DictReader(io.StringIO(tsv),delimiter='\t') if r['level']=='5' and r.get('text','').strip()]
def groups(vals,gap=3):
    out=[]
    for v in vals:
        if out and v-out[-1][-1]<=gap:out[-1].append(int(v))
        else:out.append([int(v)])
    return [round(sum(g)/len(g)) for g in out]
def straighten(im):
    sm=im.copy();sm.thumbnail((1100,1100));best=(-1,0)
    for a in np.arange(-2,2.01,.25):
        p=np.array(sm.rotate(float(a),fillcolor=255));n=(p<150).sum(axis=1);s=sum(np.sort(n)[-35:]**2)
        if s>best[0]:best=(s,float(a))
    return im.rotate(best[1],fillcolor=255),best[1]
def orientation_score(t):return sum(t.lower().count(w)*n for w,n in [('recapitulation',10),('united states',10),('election',3),('senate',10),('president',6),('votes',3),('pinkins',20),('wicker',20),('espy',20),('hyde',20),('bartee',20),('mcdaniel',20)])
def cell_key(s):
    s=s.lower()
    for expr,key in [(r'pinkins','Ty Pinkins'),(r'wicker','Roger F. Wicker'),(r'bartee','Tobey Bernard Bartee'),(r'\bespy\b','Mike Espy'),(r'hyde.?smith','Cindy Hyde-Smith'),(r'mcdaniel','Chris McDaniel'),(r'edwards','Jimmy L. Edwards'),(r'kamala|\bharris\b','Kamala D. Harris'),(r'\btrump\b','Donald J. Trump'),(r'chase oliver','Chase Oliver'),(r'jill stein','Jill Stein'),(r'randall terry','Randall Terry'),(r'ayyadurai','Shiva Ayyadurai'),(r'de la cruz','Claudia De la Cruz'),(r'kennedy','Robert F. Kennedy Jr.'),(r'sonski','Peter Sonski'),(r'write.?in','generic write-in marks'),(r'undervote','undervotes'),(r'overvote','overvotes'),(r'blank','blank ballots'),(r'ballots cast|total ballots','ballots'),(r'registered','registered voters')]:
        if key=='Chris McDaniel' and not re.search(r'chris.*mcdaniel',s):continue
        if key=='Jimmy L. Edwards' and not re.search(r'jimmy.*edwards',s):continue
        if re.search(expr,s):return key
    if 'claudia' in s:return 'Claudia De la Cruz'
    if 'shiva' in s:return 'Shiva Ayyadurai'
    return None
def page_extract(key,page,rawhash):
    d=fitz.open(stream=original(key),filetype='pdf');p=d[page-1];pix=p.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY);im=Image.open(io.BytesIO(pix.tobytes('png')))
    trials=[]
    for rotation in [0,90,180,270]:
        sm=im.rotate(rotation,expand=True);sm.thumbnail((1350,1350));t=ocr(sm,6);trials.append((orientation_score(t),rotation,t))
        if orientation_score(t)>=35:break
    _,rotation,probe=max(trials);im=im.rotate(rotation,expand=True);im,angle=straighten(im);w,h=im.size;a=np.array(im);mask=a<180
    ys=groups(np.flatnonzero(mask.sum(axis=1)>.30*w))
    header=mask[int(h*.14):int(h*.28)].copy();header=header|np.roll(header,1,axis=0)|np.roll(header,-1,axis=0)
    runs=np.zeros(w,dtype=int);maxruns=runs.copy()
    for row in header:
        runs=np.where(row,runs+1,0);maxruns=np.maximum(maxruns,runs)
    xs=groups(np.flatnonzero(maxruns>.55*len(header)))
    # Rule removal only at projection-identified grid lines, preserving entire cell interiors.
    cleaned=a.copy()
    for y in ys:cleaned[max(0,y-2):y+3,:]=255
    for x in xs:cleaned[:,max(0,x-2):x+3]=255
    clean=Image.fromarray(cleaned);full=ocr(clean,6,True)
    rec=dict(parser_version='ms-native-4',source_id=key,raw_sha256=rawhash,page=page,source_rect=list(p.rect),source_pdf_rotation=p.rotation,rotation_ccw=rotation,deskew_angle_ccw=angle,render_size=[w,h],probe_text=probe,pdf_text=p.get_text(),full_ocr_tsv=full,grid_x=xs,grid_y=ys,fields=[],qualification='Machine reading aid; candidate and geography acceptance requires source/control review')
    # SEMS rows are bounded by horizontal rules. Labels and numbers are independent crops.
    if len(xs)>=6 and len(ys)>=6:
        split=min((x for x in xs if .25*w<x<.4*w),key=lambda x:abs(x-.33*w),default=None)
        if split:
            left_words=words(ocr(clean.crop((0,0,split,h)),6,True))
            if cell_key(' '.join(z['text'] for z in left_words)) is None:return rec
            columns=[x for x in xs if x>=split-3]
            headers=[]
            # Find common vertical-label header from first long body horizontal boundary.
            header_end=next((y for y in ys if .25*h<y<.42*h),None)
            if header_end:
                header_start=next((y for y in reversed(ys) if y<header_end-70 and y>.08*h),int(.14*h))
                for j,(l,r) in enumerate(zip(columns,columns[1:]),1):
                    label=''
                    if r-l>10 and header_end-header_start>10:
                        crop=im.crop((l+4,header_start+4,r-4,header_end-4)).rotate(270,expand=True);label=ocr(crop,6).strip()
                    headers.append(dict(source_column=j,bounds=[l,header_start,r,header_end],ocr_label=label))
            rec['columns']=headers
            context='unclassified'
            for rownum,(top,bottom) in enumerate(zip(ys,ys[1:]),1):
                if bottom-top<12 or top<.22*h:continue
                label=' '.join(z['text'] for z in left_words if top<int(z['top'])+int(z['height'])/2<bottom)
                if re.search('united states.*president',label,re.I):context='president'
                if re.search('united states.*senate',label,re.I):context='senate-special' if re.search('special|unexpired',label,re.I) else 'senate'
                if re.search('house|supreme|appeals|circuit|chancery',label,re.I):context='unrelated-office'
                field=cell_key(label)
                if field:
                    # Remove only near-continuous rules WITHIN the complete row.
                    # Erasing a vertical stripe through the whole PDF clips digits
                    # aligned at the right edge, especially zeros and final digits.
                    tiles=[]
                    for l,r in zip(columns,columns[1:]):
                        tile=np.array(im.crop((l,top,r,bottom)))
                        dark=tile<230
                        tile[:,dark.sum(axis=0)>.80*tile.shape[0]]=255
                        tile[dark.sum(axis=1)>.80*tile.shape[1],:]=255
                        tiles.append(ImageOps.expand(Image.fromarray(tile),border=12,fill=255))
                    tileheight=max(z.height for z in tiles)+20;tilewidth=max(z.width for z in tiles)+30
                    montage=Image.new('L',(tilewidth,tileheight*len(tiles)),255)
                    for j,tile in enumerate(tiles):montage.paste(tile,(10,j*tileheight+10))
                    tsv=ocr(montage,6,True,True);ww=words(tsv);cells=[]
                    for j,(l,r) in enumerate(zip(columns,columns[1:]),1):
                        toks=[z for z in ww if (j-1)*tileheight<=int(z['top'])+int(z['height'])/2<j*tileheight]
                        literal=' '.join(z['text'] for z in toks);joined=literal.replace(' ','').replace(',','');v=int(joined) if re.fullmatch(r'[0-9]+',joined) else None
                        cells.append(dict(source_column=j,bounds=[l,top,r,bottom],raw_ocr=literal,value=v,missing_reason=None if v is not None else 'blank_or_unresolved_OCR_not_zero',tokens=toks))
                    rec['fields'].append(dict(source_row=rownum,label_ocr=label,office_context_ocr=context,field=field,row_bounds=[0,top,w,bottom],numeric_ocr_tsv=tsv,montage_tile_height=tileheight,montage_tile_width=tilewidth,montage_padding=22,cells=cells))
    return rec
def run(r,limit=None):
    key=r['id'];dest=OUT/'extracts/native-v4'/key;dest.mkdir(parents=True,exist_ok=True)
    d=fitz.open(stream=original(key),filetype='pdf');pages=range(1,min(len(d),limit or len(d))+1)
    for page in pages:
        path=dest/f'p{page:04d}.json.gz'
        if path.exists():continue
        try:rec=page_extract(key,page,r['raw_sha256'])
        except Exception as e:
            rec=dict(parser_version='ms-native-4',source_id=key,raw_sha256=r['raw_sha256'],page=page,error=repr(e),fields=[],qualification='Unresolved extraction error; original retained, not zero')
        path.write_bytes(gzip.compress(json.dumps(rec,ensure_ascii=False).encode(),mtime=0));print(key,page,len(rec['fields']),rec.get('error',''),flush=True)
    return key,len(d)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prefix',default='sos-2018-');p.add_argument('--only');p.add_argument('--limit',type=int);p.add_argument('--jobs',type=int,default=2);a=p.parse_args()
    rr=[r for r in references().values() if r['id'].startswith(a.prefix) and '-county-' in r['id'] and 'pdf' in str(r.get('headers',{})).lower() and (not a.only or r['id']==a.only)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        for result in pool.map(lambda r:run(r,a.limit),rr):print(result,flush=True)
