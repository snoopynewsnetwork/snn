"""Independent original-byte OCR at peer-shared *positions only*.

No peer candidate value, OCR literal or label is copied. The complete hint
derivative contains only source IDs/hashes/page transformations and pixel boxes.
"""
import argparse,concurrent.futures,gzip,io,json,os,re,subprocess
import fitz,numpy as np
from PIL import Image,ImageOps
from sources import *
from extract_native import ocr
def hints():
    dest=OUT/'source/native-2024-layout-hints.json.gz'
    if dest.exists():return json.loads(gzip.decompress(dest.read_bytes()))
    result=[]
    for path in sorted((BASE/'data/turnout/extracts').glob('*-native-grid-v5.json.gz')):
        stored=path.read_bytes();x=json.loads(gzip.decompress(stored));pages=[]
        for p in x['pages']:
            pages.append(dict(page=p['page'],render_size=p.get('render_size'),rotation_ccw=p.get('rotation_ccw'),deskew_angle_ccw=p.get('deskew_angle_ccw'),columns=[dict(source_column=c['source_column'],header_box=c.get('header_box'),candidate_boxes={name:z.get('box') for name,z in c.get('votes',{}).items()}) for c in p.get('columns',[])]))
        result.append(dict(source_id=x['source_id'],raw_sha256=x['raw_sha256'],layout_reference=str(path.relative_to(BASE)),layout_reference_stored_sha256=sha(stored),pages=pages,qualification='Positions only imported; all peer labels, OCR literals and numeric values deliberately excluded. Independently re-read original bytes.'))
    dest.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False).encode(),mtime=0));return result
def read(r):
    dest=OUT/'extracts/direct-layout'/f'{r["source_id"]}.json.gz';dest.parent.mkdir(exist_ok=True)
    if dest.exists():return r['source_id'],'cached'
    assert sha(original(r['source_id']))==r['raw_sha256'];doc=fitz.open(stream=original(r['source_id']),filetype='pdf');pages=[]
    for p in r['pages']:
        if not p['columns']:pages.append(dict(page=p['page'],status='no_box_hints_original_inventory_required'));continue
        page=doc[p['page']-1];rot=p['rotation_ccw'];rw,rh=p['render_size'];scale=(rh if rot in [90,-90,270] else rw)/page.rect.width
        im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png'))).rotate(rot,expand=True)
        if abs(im.width-rw)>1 or abs(im.height-rh)>1:raise ValueError((r['source_id'],p['page'],im.size,p['render_size']))
        im=im.rotate(p['deskew_angle_ccw'],expand=False,fillcolor=255);columns=[]
        for c in p['columns']:
            header=c['header_box'];label=ocr(im.crop(tuple(header)).rotate(270,expand=True),6).strip() if header else None;fields={}
            for name,box in c['candidate_boxes'].items():
                if box is None:fields[name]=dict(value=None,status='no_layout_box');continue
                raw=im.crop(tuple(box));a=np.array(raw);dark=a<220
                # Only near-continuous grid rules inside complete source cell.
                rulecols=np.flatnonzero(dark.sum(axis=0)>.82*a.shape[0]);rulerows=np.flatnonzero(dark.sum(axis=1)>.82*a.shape[1]);a[:,rulecols]=255;a[rulerows,:]=255
                clean=ImageOps.expand(Image.fromarray(a),15,255);readings={}
                for mode in [6,7]:readings[str(mode)]=ocr(clean,mode,False,True).strip()
                values=[]
                for v in readings.values():
                    cleaned=v.replace(',','').strip()
                    if re.fullmatch(r'\d+',cleaned):values.append(int(cleaned))
                agreed=len(values)==2 and values[0]==values[1]
                fields[name]=dict(value=values[0] if agreed else None,status='independent_OCR_consensus_pending_original_control_review' if agreed else 'unresolved_independent_readings',box=box,readings=readings,removed_near_continuous_rule_columns=rulecols.tolist(),removed_near_continuous_rule_rows=rulerows.tolist())
            columns.append(dict(source_column=c['source_column'],header_box=header,native_label_ocr=label,fields=fields))
        pages.append(dict(page=p['page'],render_size=list(im.size),rotation_ccw=rot,deskew_angle_ccw=p['deskew_angle_ccw'],columns=columns))
    dest.write_bytes(gzip.compress(json.dumps(dict(source_id=r['source_id'],raw_sha256=r['raw_sha256'],layout_reference=r['layout_reference'],layout_reference_stored_sha256=r['layout_reference_stored_sha256'],qualification='Independent original bytes/cell OCR. No peer values or labels imported. Unresolved is not zero.',pages=pages),ensure_ascii=False).encode(),mtime=0));return r['source_id'],sum(len(p.get('columns',[])) for p in pages)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--only');ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args();rr=[r for r in hints() if not a.only or r['source_id']==a.only]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        for result in pool.map(read,rr):print(*result,flush=True)
