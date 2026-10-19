"""Original numeric regions, multiple declared masks, no peer/control fitting.

Raw original windows and transformations survive. Multiple masks/PSMs of one
model are not independent source witnesses and do not establish acceptance.
"""
import argparse,concurrent.futures,gzip,json,math,re
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from sources import OUT,BASE,save,sha
from native_tesseract import NativeTesseract
from extract_replay_president import source_layouts,field_filename
def prepare(im,box):
    a=np.array(im.crop(tuple(box)).convert('L'));background=float(np.percentile(a,80));threshold=min(190,background-40);dark=a<threshold;cols=np.flatnonzero(dark.mean(axis=0)>.80);rows=np.flatnonzero(dark.mean(axis=1)>.90)
    # Only exact near-continuous rule pixels, no dilation into adjacent digits.
    a[:,cols]=255;a[rows,:]=255;lr=[int(x) for x in cols if x<.25*a.shape[1]];rr=[int(x) for x in cols if x>.75*a.shape[1]]
    if lr:a[:,:max(lr)+1]=255
    if rr:a[:,min(rr):]=255
    clean=ImageOps.autocontrast(Image.fromarray(a));return clean,dict(background_percentile80=background,dark_rule_threshold=threshold,vertical_min_fraction=.80,horizontal_min_fraction=.90,vertical_rule_columns=cols.tolist(),horizontal_rule_rows=rows.tolist(),rule_dilation_pixels=0,exterior_left_through=max(lr) if lr else None,exterior_right_from=min(rr) if rr else None,OCR_masks_on_autocontrast=[100,125,150],segmentation_modes=[7,13],qualification='Unchanged original window retained. Only OCR derivative alters rules/contrast; no cross-cell number normalization, invented zero, vote residual or accepted geometry.')
def read_source(s):
    sid=s['source_id'];folder=OUT/'extracts/reviewed-replay'/sid;dest=folder/'independent-presidential-digit-variants-v15.json.gz'
    if dest.exists():return json.loads(gzip.decompress(dest.read_bytes()))
    fields=json.loads(gzip.decompress((folder/field_filename(sid,'v14')).read_bytes()));engine=NativeTesseract();pages=[]
    for p in fields['pages']:
        im=Image.open(BASE/p['raster_path']);assert sha((BASE/p['raster_path']).read_bytes())==p['raster_sha256'];w,h=im.size;columns=[]
        for c in p['columns']:
            ff={}
            for name,f in c['fields'].items():
                if 'transformed_center_y' not in f:ff[name]=dict(proposal_value=None,status='row_locator_unresolved_not_zero');continue
                cy=f['transformed_center_y'];half=f['rowheight']/2;left,right=f['physical_x_bounds'];margin=max(16,math.ceil(w*.008));box=[max(0,math.floor(left-margin)),max(0,math.floor(cy-half-2)),min(w,math.ceil(right+margin)),min(h,math.ceil(cy+half+2))];clean,tr=prepare(im,box);variants=[];counts=Counter()
                for threshold in [100,125,150]:
                    mask=clean.point(lambda x:0 if x<threshold else 255);bounds=ImageOps.invert(mask).getbbox();image=ImageOps.expand(mask.crop(bounds),20,255) if bounds else ImageOps.expand(mask,20,255);image=image.resize((image.width*2,image.height*2))
                    for psm in [7,13]:
                        literal=engine.read(image,psm).strip();ss=literal.replace(',','');value=int(ss) if re.fullmatch(r'\d+',ss) else None;variants.append(dict(binary_threshold=threshold,mask_ink_bounds=bounds,psm=psm,literal=literal,value=value));
                        if value is not None:counts[value]+=1
                best=counts.most_common();value=best[0][0] if best and best[0][1]>=3 and (len(best)==1 or best[0][1]>best[1][1]) and len({v['binary_threshold'] for v in variants if v['value']==best[0][0]})>=2 else None
                ff[name]=dict(proposal_value=value,status='multi_mask_proposal_pending_original_controls' if value is not None else 'conflicting_or_unresolved_masks_not_zero',variants=variants,source_original_reading_window_pixels=box,original_candidate_row_locator_bounds=f['own_candidate_row_bounds'],source_row=f['source_row'],source_row_scope=f['source_row_scope'],ocr_derivative=tr,earlier_whole_page_proposal=f['value'],earlier_whole_page_literal=f.get('literal'),qualification='Mask consensus is one-model arithmetic aid, never source acceptance or a calibrated probability.')
            columns.append({k:c[k] for k in ['source_column','header_bounds','native_label_literal','role']}|dict(fields=ff))
        pages.append({k:p[k] for k in ['page','render_size','rotation_ccw','deskew_angle_ccw','raster_path','raster_sha256']}|dict(columns=columns));print(sid,p['page'],'original digit variants complete',flush=True)
    result=dict(source_id=sid,raw_sha256=s['raw_sha256'],source_field_locator_path=str((folder/field_filename(sid,'v14')).relative_to(BASE)),source_field_locator_sha256=sha((folder/field_filename(sid,'v14')).read_bytes()),OCR_engine_provenance=engine.metadata,qualification='All nine source presidential identities stay distinct. Original numeric-line/full-field fallback windows, three declared masks/twoPSMs, no peer vote/count residual. Proposals/unresolved cells require original source review; no absence-to-zero/current identity claim.',pages=pages);engine.close();dest.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False).encode(),mtime=0));return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--only');ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args();sources,_=source_layouts('native-2024-senate-reviewed-84views.json')
    if a.only:sources=[s for s in sources if s['source_id'] in a.only.split(',')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        for r in pool.map(read_source,sources):print('saved',r['source_id'],flush=True)
if __name__=='__main__':main()
