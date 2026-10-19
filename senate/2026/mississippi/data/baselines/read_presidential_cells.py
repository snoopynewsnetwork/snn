"""Independent full-original cell OCR, including explicit zero glyphs.

Never reads a peer numerical field. Complete source cell is preserved by its
original raster/hash/box; only an OCR derivative has detected rules removed.
Two segmentation modes and the earlier separate Vision reading are retained.
"""
import argparse,concurrent.futures,gzip,json,re,csv,math
from collections import defaultdict
import numpy as np
from PIL import Image,ImageOps
from sources import OUT,BASE,save
from extract_native import ocr,cell_key
from extract_replay_president import transform,NAMES,manual_row,source_layouts,field_filename
from replay_reviewed_native import hint_snapshot

def numeric_image(im,box,adaptive=False,expanded=False,line_regions=False):
    a=np.array(im.crop(tuple(box)).convert('L'));threshold=min(210,float(np.percentile(a,80))-45) if adaptive else 210;dark=a<threshold
    vf=.45 if expanded and not line_regions else .70;cols=np.flatnonzero(dark.sum(axis=0)>vf*a.shape[0]);rows=np.flatnonzero(dark.sum(axis=1)>.80*a.shape[1])
    for x in cols:a[:,max(0,x-2):min(a.shape[1],x+3)]=255
    for y in rows:a[max(0,y-1):min(a.shape[0],y+2),:]=255
    # Padding in targeting boxes can include the preceding cell's final glyph.
    # The continuously printed vertical rules, detected from THIS original cell,
    # delimit its content. Whiten only the exterior side of those detected rules.
    lrules=[int(x) for x in cols if x<.20*a.shape[1]];rrules=[int(x) for x in cols if x>.80*a.shape[1]]
    exterior_left=max(lrules)+2 if lrules else None;exterior_right=min(rrules)-2 if rrules else None
    if exterior_left is not None:a[:,:exterior_left]=255
    if exterior_right is not None:a[:,exterior_right:]=255
    if expanded and not line_regions:a=np.where(a<threshold,0,255).astype('uint8')
    clean=Image.fromarray(a)
    if adaptive:clean=ImageOps.autocontrast(clean)
    clean=ImageOps.expand(clean,15,255);clean=clean.resize((clean.width*2,clean.height*2))
    return clean,dict(dark_threshold=threshold,adaptive_to_original_cell_background=adaptive,background_reference_percentile=80 if adaptive else None,background_offset=45 if adaptive else None,autocontrast=adaptive,binary_OCR_derivative=expanded and not line_regions,numeric_line_region=line_regions,vertical_min_fraction=vf,horizontal_min_fraction=.80,vertical_rule_columns=cols.tolist(),horizontal_rule_rows=rows.tolist(),vertical_dilation=2,horizontal_dilation=1,whiten_exterior_left_through=exterior_left,whiten_exterior_right_from=exterior_right,padding=15,upscale=2,qualification='OCR-only derivative of complete original cell. Rule removal may intersect a border-touching glyph; disagreements stay for original review. Adaptive threshold prevents gray scan background being mistaken for continuous rules; old fixed210 results retained separately. Expanded boxes keep slanted/right-aligned border digits inside original reading window; no exact printed boundary claim.')

def read_source(s,tag=None,celltag=None,adaptive=False,expanded=False,library=False,line_regions=False):
    key=s['source_id'];dest=OUT/'extracts/reviewed-replay'/key/(f'independent-presidential-cells-{celltag or tag}.json.gz' if celltag or tag else 'independent-presidential-cells-v3.json.gz' if key=='sos-2024-county-jackson' else 'independent-presidential-cells-v2.json.gz')
    if dest.exists():return json.loads(gzip.decompress(dest.read_bytes()))
    engine=None
    if library:
        from native_tesseract import NativeTesseract
        engine=NativeTesseract()
    vision=json.loads(gzip.decompress((OUT/'extracts/reviewed-replay'/key/field_filename(key,tag)).read_bytes()));pages=[]
    for p in s['pages']:
        vp=next(z for z in vision['pages'] if z['page']==p['page']);old=json.loads(gzip.decompress((OUT/'extracts/native-v4'/key/f'p{p["page"]:04d}.json.gz').read_bytes()));im=Image.open(BASE/vp['raster_path']);w,h=im.size;columns=[]
        for c in p['columns']:
            box=c['candidate_bounds']['Ty Pinkins'];left,right=box[0],box[2];vc=next(z for z in vp['columns'] if z['header_bounds']==c['header_bounds']);fields={}
            for name in NAMES:
                fs=[f for f in old.get('fields',[]) if f['field']==name]
                repair=manual_row(key,p['page'],name,tag);locator=repair if repair else old
                if repair:fs=[dict(field=name,source_row=repair['source_row'],row_bounds=repair['row_bounds'])]
                if len(fs)!=1:fields[name]=dict(value=None,status='candidate_row_not_located_not_zero');continue
                f=fs[0];oldx=(left+right)/2*locator['render_size'][0]/w;_,top=transform(oldx,f['row_bounds'][1],locator,vp);_,bottom=transform(oldx,f['row_bounds'][3],locator,vp)
                margin=16 if expanded else 2;cb=[max(0,math.floor(left-margin)),max(0,math.floor(top-2)),min(w,math.ceil(right+margin)),min(h,math.ceil(bottom+2))];clean,tr=numeric_image(im,cb,adaptive,expanded,line_regions);literals={};values={}
                for psm in [6,7]:
                    lit=(engine.read(clean,psm) if engine else ocr(clean,psm,False,True)).strip();ss=lit.replace(',','').strip();literals[str(psm)]=lit;values[str(psm)]=int(ss) if re.fullmatch(r'\d+',ss) else None
                agree=values['6'] is not None and values['6']==values['7'];val=values['6'] if agree else None;vz=vc['fields'][name];vv=vz.get('value');conflict=val is not None and vv is not None and val!=vv
                fields[name]=dict(value=val,readings=literals,segmentation_values=values,full_source_cell_box=cb,source_row=f['source_row'],source_row_scope=repair.get('source_row_scope') if repair else 'Source parser full-table row index',own_candidate_row_bounds=f['row_bounds'],ocr_derivative=tr,whole_page_vision_value=vv,whole_page_vision_literal=vz.get('literal'),status='conflicting_independent_engines_pending_original_review' if conflict else 'two_segmentation_modes_and_vision_agree' if agree and vv==val else 'two_segmentation_modes_agree_vision_unresolved' if agree else 'unresolved_not_zero')
            columns.append(dict(source_column=c['source_column'],header_bounds=c['header_bounds'],native_label_literal=vc['native_label_literal'],role=vc['role'],fields=fields))
        pages.append({k:vp[k] for k in ['page','render_size','rotation_ccw','deskew_angle_ccw','raster_path','raster_sha256']}|dict(columns=columns));print(key,p['page'],'cell rows read',flush=True)
    result=dict(source_id=key,raw_sha256=s['raw_sha256'],pages=pages,qualification='Independent original full-cell OCR, all nine named presidential candidates. Not accepted from county closure alone; conflicts/missing values retained and no zeros invented.')
    if engine:result['OCR_engine_provenance']=engine.metadata;engine.close()
    dest.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False).encode(),mtime=0));return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--only');ap.add_argument('--jobs',type=int,default=3);ap.add_argument('--ledger');ap.add_argument('--tag');ap.add_argument('--cell-tag');ap.add_argument('--adaptive',action='store_true');ap.add_argument('--expanded',action='store_true');ap.add_argument('--library',action='store_true');ap.add_argument('--line-regions',action='store_true');args=ap.parse_args();sources,_=source_layouts(args.ledger)
    if args.only:sources=[s for s in sources if s['source_id'] in args.only.split(',')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        from functools import partial
        for s in pool.map(partial(read_source,tag=args.tag,celltag=args.cell_tag,adaptive=args.adaptive,expanded=args.expanded,library=args.library,line_regions=args.line_regions),sources):print('saved',s['source_id'],flush=True)
if __name__=='__main__':main()
