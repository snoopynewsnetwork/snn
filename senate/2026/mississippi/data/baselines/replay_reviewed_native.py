"""Read original rasters independently at source-bound position hints.

The hint snapshot deliberately excludes all peer labels, roles and vote values.
The peer ledger is read only by the subsequent comparison, after independent
readings have been written. Original, transformed raster, OCR and disagreements
are retained. Long straight rules are removed only from an OCR derivative.
"""
import argparse, concurrent.futures, gzip, io, json, re, subprocess
from pathlib import Path
import fitz
import numpy as np
from PIL import Image
from sources import BASE, OUT, original, sha, save
from compile_vision_grid import pixels

NAMES=['Ty Pinkins','Roger F. Wicker']
PEER=BASE/'data/coordinator-qa/native-2024-25views/native-reviewed-2024.json.gz'

def hint_snapshot():
    dest=OUT/'source/native-reviewed-25view-positions.json.gz'
    if dest.exists(): return json.loads(gzip.decompress(dest.read_bytes()))
    stored=PEER.read_bytes();raw=gzip.decompress(stored)
    assert sha(raw)=='2501822b1b432b8eaeb1257c47b0d002082089ef86281c0dfa7ff4030ab7015f'
    x=json.loads(raw);sources=[]
    for key,s in x['sources'].items():
        pages=[]
        for p in s['pages']:
            pages.append({k:p[k] for k in ['page','render_size','rotation_ccw','deskew_angle_ccw']} | {'columns':[{'source_column':c['source_column'],'header_bounds':c['header_bounds'],'candidate_bounds':c['candidate_bounds']} for c in p['columns']]})
        sources.append(dict(source_id=key,raw_sha256=s['raw_sha256'],pages=pages))
    result=dict(reference_path=str(PEER.relative_to(BASE)),reference_stored_sha256=sha(stored),reference_original_sha256=sha(raw),qualification='Positions only: no peer label, role, printed ID, vote value or OCR imported. Each original is independently rendered and read.',sources=sources)
    dest.write_bytes(gzip.compress(json.dumps(result).encode(),mtime=0));return result

def remove_long_rules(im):
    """Remove near-continuous straight dark runs; never crop a source cell."""
    a=np.array(im.convert('L'));dark=(a<190).astype(np.int32);mask=np.zeros(a.shape,bool)
    settings=[(0,70,61),(1,140,122)]
    for axis,length,threshold in settings:
        b=dark if axis==0 else dark.T
        pref=np.vstack([np.zeros((1,b.shape[1]),np.int32),np.cumsum(b,axis=0,dtype=np.int32)])
        windows=(pref[length:]-pref[:-length])>=threshold
        # Range-add qualifying windows into a pixel mask along each scan line.
        delta=np.zeros((b.shape[0]+1,b.shape[1]),np.int32)
        delta[:len(windows)]+=windows;delta[length:length+len(windows)]-=windows
        m=np.cumsum(delta[:-1],axis=0)>0
        mask|=m if axis==0 else m.T
    # Only the original dark rule pixels are removed; white background remains.
    removed=mask & (a<230);a[removed]=255
    return Image.fromarray(a),dict(vertical_window=70,vertical_min_dark=61,horizontal_window=140,horizontal_min_dark=122,dark_threshold=190,removed_pixels=int(removed.sum()),qualification='OCR derivative only. Original raster and bytes preserved; removed lines can intersect glyphs, so disagreements require original review.')

def read_source(s,clean=True):
    key=s['source_id'];dest=OUT/'extracts/reviewed-replay'/key;dest.mkdir(parents=True,exist_ok=True)
    raw=original(key);assert sha(raw)==s['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');pages=[]
    for p in s['pages']:
        target=dest/f'p{p["page"]:04d}.json.gz'
        if target.exists():pages.append(json.loads(gzip.decompress(target.read_bytes())));continue
        page=doc[p['page']-1];rw,rh=p['render_size'];rot=p['rotation_ccw'];scale=(rh if rot in [90,-90,270] else rw)/page.rect.width
        im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png'))).rotate(rot,expand=True).rotate(p['deskew_angle_ccw'],fillcolor=255)
        assert max(abs(im.width-rw),abs(im.height-rh))<=1
        png=dest/f'p{p["page"]:04d}-original.png';im.save(png)
        cleaned,transform=remove_long_rules(im);cpng=dest/f'p{p["page"]:04d}-rules-removed.png';cleaned.save(cpng)
        inp=cpng if clean else png
        process=subprocess.run([str(OUT/'qa/vision-ocr'),str(inp)],capture_output=True,text=True,check=True);v=json.loads(process.stdout)
        v.update(source_id=key,raw_sha256=s['raw_sha256'],page=p['page'],render_size=list(im.size),rotation_ccw=rot,deskew_angle_ccw=p['deskew_angle_ccw'],raster_path=str(png.relative_to(BASE)),raster_sha256=sha(png.read_bytes()),ocr_raster_path=str(inp.relative_to(BASE)),ocr_raster_sha256=sha(inp.read_bytes()),ocr_derivative_transform=transform,columns=p['columns'])
        target.write_bytes(gzip.compress(json.dumps(v,ensure_ascii=False).encode(),mtime=0));pages.append(v);print(key,p['page'],len(v['words']),flush=True)
    return dict(source_id=key,raw_sha256=s['raw_sha256'],pages=pages)

def independent_fields(s):
    pages=[]
    for p in s['pages']:
        w,h=p['render_size'];columns=[]
        for c in p['columns']:
            fields={}
            for name,box in c['candidate_bounds'].items():
                tokens=[]
                for z in p['words']:
                    b=pixels(z,w,h);cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
                    if box and box[0]<cx<box[2] and box[1]<cy<box[3]:tokens.append(dict(text=z['text'],box=b,confidence=z['confidence']))
                lit=' '.join(z['text'] for z in sorted(tokens,key=lambda z:z['box'][0]));sval=lit.replace(',','').strip()
                fields[name]=dict(value=int(sval) if re.fullmatch(r'\d+',sval) else None,literal=lit,tokens=tokens,source_box=box,status='independent_original_OCR_pending_comparison' if re.fullmatch(r'\d+',sval) else 'blank_or_unresolved_not_zero')
            columns.append(dict(source_column=c['source_column'],header_bounds=c['header_bounds'],fields=fields))
        pages.append(dict(page=p['page'],render_size=p['render_size'],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p['deskew_angle_ccw'],raster_path=p['raster_path'],raster_sha256=p['raster_sha256'],columns=columns))
    return dict(source_id=s['source_id'],raw_sha256=s['raw_sha256'],pages=pages,qualification='Independent original numeric OCR at shared physical bounds, no control fitting. Peer labels/values not imported. Comparison and original review required.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--only');ap.add_argument('--jobs',type=int,default=2);args=ap.parse_args();ss=hint_snapshot()['sources']
    if args.only:ss=[s for s in ss if s['source_id']==args.only]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for s in pool.map(read_source,ss):
            dest=OUT/'extracts/reviewed-replay'/s['source_id']/'independent-fields.json.gz';dest.write_bytes(gzip.compress(json.dumps(independent_fields(s),ensure_ascii=False).encode(),mtime=0))
            print('saved',s['source_id'],flush=True)
if __name__=='__main__':main()
