"""Independent original PDF rasters and discrepancy cards for Hinds Pres.

The provisional original-pixel OCR is compared to peer only to select eight
cells for visual rereading. The cards contain only original PDF pixels.
"""
import csv,gzip,io,json
from pathlib import Path
import fitz
from PIL import Image,ImageDraw
from acquire_sources import BASE,OUT,receipts,sha,savejson

SID='sos-2024-county-hinds'
def main():
    r=next(x for x in receipts if x['id']==SID)
    raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256']
    doc=fitz.open(stream=raw,filetype='pdf')
    a={(int(x['source_page']),int(x['source_column']),x['candidate']):x for x in csv.DictReader((OUT/'presidential-original-aid-cells.csv').open()) if x['source_id']==SID}
    p={(int(x['source_page']),int(x['source_column']),x['candidate']):x for x in csv.DictReader((BASE/'data/baselines/native-allfield-additional-candidate-votes.csv').open()) if x['source_id']==SID and x['candidate'] not in ['Ty Pinkins','Roger F. Wicker']}
    assert len(a)==len(p)==990 and set(a)==set(p)
    diffs=sorted(k for k in a if a[k]['compiled_provisional_value']!=p[k]['value'])
    assert len(diffs)==8
    out=OUT/'qa/hinds-presidential-original-review';out.mkdir(exist_ok=True)
    pages=[];ims={}
    for n in range(2,12):
        page=doc[n-1];im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),colorspace=fitz.csGRAY).tobytes('png'))).rotate(-90,expand=True)
        assert im.size==(1980,1530)
        path=out/f'{SID}-p{n:02d}-original.png';im.save(path)
        pages.append(dict(source_page=n,render_path=str(path.relative_to(BASE)),render_sha256=sha(path.read_bytes()),render_size=list(im.size),rotation_ccw=-90))
        ims[n]=im
    cards=[]
    for k in diffs:
        n,c,name=k;box=json.loads(a[k]['original_cell_bounds']);im=ims[n]
        expanded=(max(0,box[0]-75),max(0,box[1]-24),min(im.width,box[2]+75),min(im.height,box[3]+24))
        crop=im.crop(expanded).resize(((expanded[2]-expanded[0])*4,(expanded[3]-expanded[1])*4))
        path=out/f'p{n:02d}-c{c:02d}-{name.replace(" ","-")}.png';crop.save(path)
        cards.append(dict(source_page=n,source_column=c,candidate=name,original_cell_bounds=box,expanded_original_bounds=list(expanded),card_path=str(path.relative_to(BASE)),card_sha256=sha(path.read_bytes()),provisional_original_OCR=a[k]['compiled_provisional_value'],scope='Original source pixels only; peer value is not drawn/imported.'))
    canvas=Image.new('RGB',(1250,400*len(cards)),'white');dr=ImageDraw.Draw(canvas)
    for i,x in enumerate(cards):
        dr.text((8,i*400+8),f'p{x["source_page"]} c{x["source_column"]} {x["candidate"]} original crop; OCR {x["provisional_original_OCR"]}',fill='black')
        pic=Image.open(BASE/x['card_path']);pic.thumbnail((1230,355));canvas.paste(pic,(8,i*400+35))
    atlas=out/'eight-original-exception-atlas.png';canvas.save(atlas)
    savejson(OUT/'hinds-presidential-original-review-index.json',dict(source_id=SID,source_raw_sha256=r['raw_sha256'],source_original_path=r['path'],source_page_count=len(doc),original_position_aid_sha256=sha((OUT/'presidential-original-aid-cells.csv').read_bytes()),peer_position_comparison_sha256=sha((BASE/'data/baselines/native-allfield-additional-candidate-votes.csv').read_bytes()),position_count=len(a),original_OCR_discrepancy_count=len(diffs),pages=pages,cards=cards,atlas_path=str(atlas.relative_to(BASE)),atlas_sha256=sha(atlas.read_bytes())))
    print('Hinds original presidential positions',len(a),'exception cards',len(cards))
if __name__=='__main__':main()
