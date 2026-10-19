"""Independent original-PDF OCR aids for the 2020 Senate native grid.

Only vote-free peer source-position hints select the physical PDF pages, row
bands and approximate column boundaries. Every OCR pixel is rendered anew
from the hash-checked SOS original. OCR is provisional until original visual
review, native/source TOTAL reconciliation, and independent peer agreement.
"""
import argparse,gzip,io,json,re,subprocess
from pathlib import Path
import fitz
import numpy as np
from PIL import Image,ImageOps
from acquire_sources import BASE,OUT,receipts,sha,savejson

QAROOT=OUT/'qa/2020-native-original-ocr'

def source_candidate_rows(page,mode):
    """Split broad Senate blocks by candidate order using only page geometry.

    Some frozen position hints supply the same whole three-row Senate box for
    all candidates. Calling OCR on it three times manufactures identical bad
    aids. The evenly divided bands remain *provisional targeting*, not
    accepted digit or exact cell polygons.
    """
    rows=page['candidate_rows']
    if mode not in ('candidate-subrows-v1','candidate-subrows-v2') or len({tuple(r['row_bounds']) for r in rows})!=1:
        return [dict(r,derivation='source_hint_candidate_row') for r in rows]
    assert len(rows)==3
    x1,y1,x2,y2=rows[0]['row_bounds']
    assert y2-y1>=90,(page['page'],rows)
    edges=[y1,round(y1+(y2-y1)/3),round(y1+2*(y2-y1)/3),y2]
    return [dict(r,row_bounds=[x1,edges[i],x2,edges[i+1]],
                 broad_source_hint_row_bounds=r['row_bounds'],
                 derivation='equal_thirds_of_original_three_candidate_Senate_band')
            for i,r in enumerate(rows)]

def render(doc,page):
    original=doc[page['page']-1]
    z=page['render_scale']
    im=Image.open(io.BytesIO(original.get_pixmap(matrix=fitz.Matrix(z,z),colorspace=fitz.csGRAY).tobytes('png')))
    if page['rotation_ccw']:
        im=im.rotate(page['rotation_ccw'],expand=True,fillcolor=255)
    if page['deskew_angle_ccw']:
        im=im.rotate(page['deskew_angle_ccw'],expand=False,fillcolor=255)
    return im

def vertical_lines(im,page,row):
    cols=page['columns'];bounds=[cols[0]['header_bounds'][0]]+[c['header_bounds'][2] for c in cols]
    _,y1,_,y2=row['row_bounds'];margin=max(3,int((y2-y1)*(.27 if row.get('derivation','').startswith('equal_thirds') and row.get('ocr_margin_version')=='v2' else .16)))
    a=np.asarray(im)[y1+margin:y2-margin,:]
    if not len(a):raise ValueError('empty candidate band')
    score=(a<128).sum(axis=0)
    lines=[]
    for x in bounds:
        lo=max(0,x-16);hi=min(im.width,x+17)
        v=max(range(lo,hi),key=lambda k:int(score[k]))
        lines.append(dict(position=v,black_pixels=int(score[v]),band_height=len(a),hint=x))
    if any(lines[i+1]['position']<=lines[i]['position'] for i in range(len(lines)-1)):
        raise ValueError('physical grid lines not increasing')
    return lines

def ocr(crop,psm):
    out=io.BytesIO();crop.save(out,format='PNG')
    p=subprocess.run(['tesseract','stdin','stdout','--psm',str(psm),'-c','tessedit_char_whitelist=0123456789'],input=out.getvalue(),capture_output=True,check=True)
    return p.stdout.decode().strip()

def cell_read(im,row,left,right):
    _,y1,_,y2=row['row_bounds'];margin=max(3,int((y2-y1)*(.27 if row.get('derivation','').startswith('equal_thirds') and row.get('ocr_margin_version')=='v2' else .16)))
    box=(left+3,y1+margin,right-3,y2-margin)
    if box[0]>=box[2] or box[1]>=box[3]:raise ValueError('bad source cell window')
    raw=im.crop(box).convert('L')
    mask=ImageOps.invert(raw).point(lambda q:255 if q>110 else 0)
    ink=np.asarray(mask);count=int((ink>0).sum());b=mask.getbbox()
    if not b:
        return dict(original_window=list(box),ink_bbox=None,ink_pixel_count=0,ocr_psm7='',ocr_psm13='',provisional_value=None)
    close=raw.crop(b);scaled=close.resize((close.width*4,close.height*4))
    padded=Image.new('L',(scaled.width+80,scaled.height+80),255);padded.paste(scaled,(40,40))
    v7=ocr(padded,7);v13=ocr(padded,13)
    return dict(original_window=list(box),ink_bbox=[box[0]+b[0],box[1]+b[1],box[0]+b[2],box[1]+b[3]],ink_pixel_count=count,ocr_psm7=v7,ocr_psm13=v13,provisional_value=int(v7) if re.fullmatch(r'\d+',v7) else None)

def extract(source,hint_sha,mode='legacy'):
    assert mode in ('legacy','candidate-subrows-v1','candidate-subrows-v2')
    sid=source['source_id'];r=next(x for x in receipts if x['id']==sid)
    raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256']==source['source_raw_sha256']
    doc=fitz.open(stream=raw,filetype='pdf');outdir=(QAROOT if mode=='legacy' else OUT/f'qa/2020-native-original-ocr-subrows-{mode[-2:]}')/sid;outdir.mkdir(parents=True,exist_ok=True)
    pages=[];rows=[]
    for page in source['pages']:
        im=render(doc,page);expected=page['render_size']
        delta=[im.width-expected[0],im.height-expected[1]]
        # The peer's historic page render used expand=False for deskew, yet
        # some original scans may differ by a few border pixels. Retain both.
        if max(map(abs,delta))>8:raise ValueError((sid,page['page'],'transform',im.size,expected))
        path=outdir/f'p{page["page"]:04d}-original.png';im.save(path)
        receipt=dict(source_page=page['page'],original_raster=str(path.relative_to(BASE)),raster_sha256=sha(path.read_bytes()),render_size=list(im.size),position_hint_size=expected,size_delta=delta,rotation_ccw=page['rotation_ccw'],deskew_ccw=page['deskew_angle_ccw'])
        pages.append(receipt)
        for row in (page['candidate_rows'] if mode=='legacy' else source_candidate_rows(page,mode)):
            if mode!='legacy':row['ocr_margin_version']='v2' if mode=='candidate-subrows-v2' else 'legacy'
            lines=vertical_lines(im,page,row)
            for i,col in enumerate(page['columns']):
                z=cell_read(im,row,lines[i]['position'],lines[i+1]['position'])
                item=dict(source_id=sid,source_raw_sha256=r['raw_sha256'],source_page=page['page'],source_column=col['source_column'],candidate=row['candidate'],role_hint=col['role'],left_rule=lines[i],right_rule=lines[i+1],**z)
                if mode!='legacy':item.update(candidate_row_derivation=row['derivation'],candidate_row_bounds=row['row_bounds'],broad_source_hint_row_bounds=row.get('broad_source_hint_row_bounds'))
                rows.append(item)
    assert len(rows)==sum(len(p['columns'])*len(p['candidate_rows']) for p in source['pages'])
    data=dict(scope='Provisional original-pixel two-PSM OCR, not accepted vote transcript. Positions-only peer hints; no peer numeric or label values used.' if mode=='legacy' else 'Provisional original-pixel two-PSM OCR, not accepted vote transcript. Positions-only peer hints; no peer numeric or label values used. Any equal-thirds candidate row targeting is provisional and retained beside the broad source hint.',source_id=sid,source_raw_sha256=r['raw_sha256'],position_hint_sha256=hint_sha,pages=pages,rows=rows)
    if mode!='legacy':data['mode']=mode
    path=OUT/f'{"2020-native-original-ocr" if mode=="legacy" else "2020-native-original-ocr-subrows-"+mode[-2:]}/{sid}.json.gz';path.parent.mkdir(exist_ok=True)
    path.write_bytes(gzip.compress((json.dumps(data,ensure_ascii=False,sort_keys=True)+'\n').encode(),mtime=0))
    native=sum(x['role_hint']=='source_native_reporting_constituent' for x in rows)
    ambiguous=sum(x['ocr_psm7']!=x['ocr_psm13'] for x in rows if x['role_hint']!='unused_template_column')
    unresolved=sum(x['provisional_value'] is None for x in rows if x['role_hint']!='unused_template_column')
    print(sid,len(rows),native,'two-PSM differences',ambiguous,'unresolved',unresolved,flush=True)
    return dict(source_id=sid,path=str(path.relative_to(BASE)),stored_sha256=sha(path.read_bytes()),stored_bytes=path.stat().st_size,source_raw_sha256=r['raw_sha256'],row_count=len(rows),numeric_role_unresolved=unresolved,two_PSM_differences=ambiguous)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',action='append');ap.add_argument('--hints-version',choices=['v1','v2','v3','v4','v5','v6','v7'],default='v1');ap.add_argument('--mode',choices=['legacy','candidate-subrows-v1','candidate-subrows-v2'],default='legacy');a=ap.parse_args()
    hint_path=OUT/f'source/2020-native-position-hints-{a.hints_version}.json'
    raw=hint_path.read_bytes();hint=json.loads(raw);source_ids=set(a.source or [s['source_id'] for s in hint['sources']]);sources=[s for s in hint['sources'] if s['source_id'] in source_ids]
    assert len(sources)==len(source_ids)
    results=[extract(s,sha(raw),a.mode) for s in sources]
    if not a.source:
        savejson(OUT/'2020-native-original-ocr-index.json',dict(scope='All positional-hint source views; provisional original OCR only.',position_hint_sha256=sha(raw),sources=results))
if __name__=='__main__':main()
