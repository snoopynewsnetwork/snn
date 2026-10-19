"""Original-only visual review surfaces for five small 2024 SEMS views.

The already independent original-pixel aid is compared post-extraction to the
peer only to select cells for rereading; no peer value appears on images.
"""
import csv,gzip,io,json
import fitz
from PIL import Image,ImageDraw
from acquire_sources import BASE,OUT,receipts,sha,savejson

SLUGS=['benton','greene','wilkinson','noxubee','issaquena']
SID=lambda slug:'sos-2024-county-'+slug
def build(slugs=SLUGS,tag='small',peer_position_only=False):
    aid=list(csv.DictReader((OUT/'presidential-original-aid-cells.csv').open()))
    peerfile=BASE/'data/baselines/native-allfield-additional-candidate-votes.csv'
    peer=list(csv.DictReader(peerfile.open()))
    native=json.loads(gzip.decompress((OUT/'native-constituents-reviewed.json.gz').read_bytes()))
    rr={r['id']:r for r in receipts}
    out=OUT/f'qa/{tag}-presidential-original-review';out.mkdir(exist_ok=True)
    sources=[]
    for slug in slugs:
        sid=SID(slug);r=rr[sid];raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256']
        doc=fitz.open(stream=raw,filetype='pdf')
        a={(int(x['source_page']),int(x['source_column']),x['candidate']):x for x in aid if x['source_id']==sid}
        own_positions={(u['source_page'],u['source_column'],name) for u in native if u['source_id']==sid for name in ['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump','Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski']}
        p={k:None for k in own_positions} if peer_position_only else {(int(x['source_page']),int(x['source_column']),x['candidate']):x for x in peer if x['source_id']==sid and x['candidate'] not in ['Ty Pinkins','Roger F. Wicker']}
        assert set(p)==own_positions and set(a).issubset(own_positions)
        missing_positions=sorted(own_positions-set(a))
        # Missing aid positions are explicit original-page reading assignments.
        # The recorder requires a manual entry for every one of them; no
        # candidate value or absence is inferred from the peer or county sum.
        errors=[] if peer_position_only else sorted(k for k in a if a[k]['compiled_provisional_value']!=p[k]['value'])
        geometry={u['source_page']:(u['render_size'],u['rotation_ccw'],u['deskew_angle_ccw']) for u in native if u['source_id']==sid}
        images={};pages=[]
        for n in sorted(geometry):
            target,rotation,deskew=geometry[n];page=doc[n-1]
            candidates=[]
            for zoom in [2.5,2.7]:
                base=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(zoom,zoom),colorspace=fitz.csGRAY).tobytes('png'))).rotate(rotation,expand=True,fillcolor=255)
                for applied_deskew in [0,deskew]:
                    im=base.rotate(applied_deskew,expand=True,fillcolor=255) if applied_deskew else base
                    candidates.append((abs(im.width-target[0])+abs(im.height-target[1]),zoom,applied_deskew,im))
            delta,zoom,applied_deskew,im=min(candidates,key=lambda x:x[0])
            if sid=='sos-2024-county-grenada' and n==4:
                # This source's Senate/native table was downsampled on p4,
                # while the independent presidential aid bounds were made on
                # a full 2.7x rendering. Preserve the latter as a distinct
                # source-position raster; do not pretend the boxes align with
                # the smaller native header workbench.
                delta,zoom,applied_deskew,im=next(x for x in candidates if x[1]==2.7 and x[2]==deskew)
            elif delta>4:
                # Some scanned publications were downsampled for the source
                # position workbench on only one page. Recover that page's
                # transform from its recorded dimensions, still rendering the
                # original PDF bytes independently rather than copying a raster.
                source_width=page.rect.height if int(rotation)%180 else page.rect.width
                approximate=target[0]/source_width
                for offset in range(-24,25):
                    z=approximate+offset*0.00025
                    if z<=0:continue
                    base=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(z,z),colorspace=fitz.csGRAY).tobytes('png'))).rotate(rotation,expand=True,fillcolor=255)
                    for d in [0,deskew]:
                        candidate=base.rotate(d,expand=True,fillcolor=255) if d else base
                        score=abs(candidate.width-target[0])+abs(candidate.height-target[1])
                        if score<delta:delta,zoom,applied_deskew,im=score,z,d,candidate
                        if delta<=4:break
                    if delta<=4:break
            assert delta<=4 or (sid=='sos-2024-county-grenada' and n==4),(sid,n,target,delta,zoom,applied_deskew)
            path=out/f'{sid}-p{n:02d}-original.png';im.save(path);images[n]=im
            pages.append(dict(source_page=n,raw_sha256=r['raw_sha256'],render_size=list(im.size),target_geometry_size=target,size_delta_pixels=delta,fitz_zoom=zoom,rotation_ccw=rotation,deskew_hint_ccw=deskew,applied_deskew_ccw=applied_deskew,full_original_raster=str(path.relative_to(BASE)),raster_sha256=sha(path.read_bytes())))
        cards=[]
        for n,c,name in errors:
            x=a[n,c,name];im=images[n];b=json.loads(x['original_cell_bounds'])
            box=(max(0,b[0]-45),max(0,b[1]-25),min(im.width,b[2]+45),min(im.height,b[3]+25))
            assert box[0]<box[2] and box[1]<box[3],(sid,n,c,name,b,im.size)
            crop=im.crop(box);crop=crop.resize((crop.width*4,crop.height*4))
            path=out/f'{sid}-p{n:02d}-c{c:02d}-{name.replace(" ","-")}.png';crop.save(path)
            cards.append(dict(source_page=n,source_column=c,candidate=name,aid_bounds=b,expanded_original_bounds=list(box),original_card=str(path.relative_to(BASE)),card_sha256=sha(path.read_bytes()),independent_original_OCR=x['compiled_provisional_value']))
        canvas=Image.new('RGB',(1250,max(400,360*len(cards))),'white');dr=ImageDraw.Draw(canvas)
        for i,x in enumerate(cards):
            dr.text((5,i*360+4),f'{sid} p{x["source_page"]} c{x["source_column"]} {x["candidate"]} original; OCR {x["independent_original_OCR"]}',fill='black')
            im=Image.open(BASE/x['original_card']);im.thumbnail((1235,330));canvas.paste(im,(6,i*360+26))
        atlas=out/f'{sid}-exceptions-original-atlas.png';canvas.save(atlas)
        source=dict(source_id=sid,source_raw_sha256=r['raw_sha256'],source_original_path=r['path'],source_page_count=len(doc),position_count=len(a),original_OCR_peer_disagreement_count=len(errors),pages=pages,cards=cards,atlas=str(atlas.relative_to(BASE)),atlas_sha256=sha(atlas.read_bytes()))
        if missing_positions:source['original_aid_missing_positions']=[dict(source_page=n,source_column=c,candidate=name) for n,c,name in missing_positions]
        sources.append(source)
    savejson(OUT/f'{tag}-presidential-original-review-index.json',dict(scope=f'{len(slugs)} independent original-pixel workbench views; '+('source-position inventory only; no peer numeric comparison or exception cards.' if peer_position_only else 'peer comparison only selects original-only discrepancy cards, not vote imports.'),peer_comparison_file_sha256=None if peer_position_only else sha(peerfile.read_bytes()),sources=sources))
    print([(x['source_id'],x['position_count'],x['original_OCR_peer_disagreement_count']) for x in sources])
def main():build()
if __name__=='__main__':main()
