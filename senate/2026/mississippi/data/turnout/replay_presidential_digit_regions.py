"""Independent second OCR pass on original 2024 presidential cell interiors.

This is a reading aid, never an accepted transcript or residual allocator. It
targets the right-aligned original digits without touching row/column rules.
"""
import gzip, io, json, random
from pathlib import Path
import fitz
import numpy as np
from PIL import Image, ImageOps
from acquire_sources import BASE, OUT, receipts, sha, savejson
from read_native_positions import ocr
from read_physical_native import PRES24

R={x['id']:x for x in receipts}

def original_page(sid,page,record):
    r=R[sid];raw=gzip.decompress((BASE/r['path']).read_bytes())
    assert sha(raw)==r['raw_sha256']
    doc=fitz.open(stream=raw,filetype='pdf');p=doc[page-1]
    image=Image.open(io.BytesIO(p.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png')))
    image=image.rotate(record['rotation_ccw'],expand=True).rotate(record['deskew_angle_ccw'],fillcolor=255)
    assert list(image.size)==record['render_size']
    return image

def digit_region(image,box):
    a=np.array(image.crop(tuple(box)))
    h,w=a.shape
    # Source digits align to the upper right. Keep a broad interior; erase only
    # near-complete printed table rules, not glyphs. No candidate-aware edits.
    a=a[3:min(h-3,55),max(0,w-74):max(1,w-4)].copy()
    if not a.size:return Image.new('L',(50,50),255)
    dark=a<150
    a[np.flatnonzero(dark.sum(axis=1)>a.shape[1]*.85),:]=255
    dark=a<150
    a[:,np.flatnonzero(dark.sum(axis=0)>a.shape[0]*.85)]=255
    ys,xs=np.nonzero(a<200)
    if len(xs):a=a[max(0,int(ys.min())-3):min(a.shape[0],int(ys.max())+4),max(0,int(xs.min())-3):min(a.shape[1],int(xs.max())+4)]
    return ImageOps.expand(Image.fromarray(a).resize((max(16,a.shape[1]*4),max(16,a.shape[0]*4))),border=16,fill=255)

def batch_ocr(crops):
    if not crops:return []
    step=max(x.height for x in crops)+24;width=max(x.width for x in crops)+40
    canvas=Image.new('L',(width,step*len(crops)),255)
    for i,c in enumerate(crops):canvas.paste(c,(20,i*step+12))
    t,tt=ocr(canvas,6,True);rows=[]
    for i in range(len(crops)):
        tokens=[x for x in tt if i*step<=int(x['top'])+int(x['height'])/2<(i+1)*step]
        literal=' '.join(x['text'] for x in sorted(tokens,key=lambda x:int(x['left'])))
        digits=literal.replace(' ','').replace(',','')
        rows.append(dict(raw_ocr=literal,value=int(digits) if digits.isdigit() else None,tokens=tokens))
    return rows

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--sample',type=int,default=0);ap.add_argument('--only');a=ap.parse_args()
    working=json.loads((OUT/'native-reviewed-2024.json').read_text())
    roles={(sid,p['page'],c['source_column']):c['role'] for sid,s in working['sources'].items() for p in s['pages'] for c in p['columns']}
    items=[]
    for path in sorted((OUT/'extracts/physical-native-v3').glob('sos-2024-county-*.json.gz')):
        if a.only and a.only not in path.name:continue
        data=json.loads(gzip.decompress(path.read_bytes()));sid=data['source_id']
        for p in data['pages']:
            for f in p['fields']:
                name=f['candidate_position_hint']
                if name not in PRES24:continue
                for c in f['cells']:
                    role=roles.get((sid,p['page'],c['source_column']))
                    if role!='native_reporting_constituent' or c['value'] is not None:continue
                    items.append(dict(source_id=sid,page=p['page'],source_column=c['source_column'],candidate=name,original_ocr=c['raw_ocr'],original_value=c['value'],bounds=c['bounds'],page_record=p,raw_sha256=data['raw_sha256']))
    if a.sample:random.Random(19).shuffle(items);items=items[:a.sample]
    results=[];cache={}
    for start in range(0,len(items),22):
        chunk=items[start:start+22];crops=[]
        for x in chunk:
            key=(x['source_id'],x['page'])
            if key not in cache:cache[key]=original_page(*key,x['page_record'])
            crops.append(digit_region(cache[key],x['bounds']))
        reads=batch_ocr(crops)
        for x,v in zip(chunk,reads):
            x={k:y for k,y in x.items() if k!='page_record'}
            results.append(x|{'second_ocr':v})
        cache.clear()  # large original rasters are reproducible, not retained in RAM
    path=OUT/('presidential-null-digit-region-sample.json' if a.sample else 'presidential-null-digit-region-aid.json.gz')
    if a.sample:savejson(path,dict(scope='Unaccepted independent original-only OCR reading aid',count=len(results),readings=results))
    else:path.write_bytes(gzip.compress(json.dumps(dict(scope='Unaccepted independent original-only OCR reading aid',count=len(results),readings=results)).encode(),mtime=0))
    print(len(results),'second-pass recognized',sum(x['second_ocr']['value'] is not None for x in results),'stored',path)

if __name__=='__main__':main()
