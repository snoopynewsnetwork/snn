"""Independent original-source historical native blocks, versioned reading aids.

All physical columns, including TOTAL/blank/admin positions, survive. Candidate
row-offset recovery is a proposed position only; fresh original row-label OCR
is retained and must agree before accepting identity. No zeros are invented,
no count is selected to fit a county control, no peer vote/label is read.
"""
import argparse,concurrent.futures,gzip,io,json,re
from collections import Counter
import fitz
from PIL import Image
from sources import OUT,original,references,sha
from extract_native import ocr,words,cell_key
from read_presidential_cells import numeric_image

NAMES={'2020':['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards'],'2018-special':['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],'2018-runoff':['Mike Espy','Cindy Hyde-Smith']}
def read(r):
    key=r['id'];stage='2020' if key.startswith('sos-2020-') else '2018-runoff' if '-runoff-' in key else '2018-special';names=NAMES[stage];dest=OUT/'extracts/historical-cells-v2'/f'{key}.json.gz';dest.parent.mkdir(exist_ok=True)
    if dest.exists():return key,'cached'
    raw=original(key);doc=fitz.open(stream=raw,filetype='pdf');pages=[]
    for path in sorted((OUT/'extracts/native-v4'/key).glob('*.gz')):
        x=json.loads(gzip.decompress(path.read_bytes()));ff=[f for f in x.get('fields',[]) if f['field'] in names and (f['field']!='Chris McDaniel' or 'chris' in f['label_ocr'].lower()) and (f['field']!='Jimmy L. Edwards' or 'jimmy' in f['label_ocr'].lower())]
        if not ff or not x.get('columns'):continue
        offsets=Counter(f['source_row']-1-names.index(f['field']) for f in ff);start=offsets.most_common(1)[0][0];ys=x['grid_y'];w,h=x['render_size']
        if start<0 or start+len(names)>=len(ys):continue
        page=doc[x['page']-1];im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(x['rotation_ccw'],expand=True).rotate(x['deskew_angle_ccw'],fillcolor=255)
        xs=x['grid_x'];candidates=[z for i,z in enumerate(xs) if i and .23*w<z<.43*w and z-xs[i-1]>.15*w];split=candidates[0] if candidates else x['columns'][0]['bounds'][0];cols=[z for z in xs if z>=split-3];header=x['columns'][0]['bounds'][1::2];columns=[]
        for c,(l,rgt) in enumerate(zip(cols,cols[1:]),1):
            hb=[l,header[0],rgt,header[1]];label=ocr(im.crop(tuple(hb)).rotate(270,expand=True),6).strip();columns.append(dict(source_column=c,header_bounds=hb,label_ocr=label,role='source_TOTAL_OCR_proposed' if re.search(r'\btotal\b',label,re.I) else 'blank_or_unresolved_header_not_zero' if not re.search(r'[A-Za-z0-9]',label) else 'source_native_header_OCR_pending_review'))
        fields=[]
        for j,name in enumerate(names):
            top,bottom=ys[start+j:start+j+2];labelbox=[0,top,split,bottom];label=ocr(im.crop(tuple(labelbox)),6).strip();actual=cell_key(label);tiles=[];transforms=[];boxes=[]
            for l,rgt in zip(cols,cols[1:]):
                box=[l-2,top-2,rgt+2,bottom+2];clean,tr=numeric_image(im,box);tiles.append(clean);transforms.append(tr);boxes.append(box)
            tw=max(t.width for t in tiles)+30;th=max(t.height for t in tiles)+30;montage=Image.new('L',(tw,th*len(tiles)),255)
            for k,t in enumerate(tiles):montage.paste(t,(15,k*th+15))
            readings={};tsvs={}
            for psm in [6,4]:
                tsv=ocr(montage,psm,True,True);tsvs[str(psm)]=tsv;ww=words(tsv);cells=[]
                for k in range(len(tiles)):
                    tokens=[z for z in ww if k*th<=int(z['top'])+int(z['height'])/2<(k+1)*th];lit=' '.join(z['text'] for z in tokens);ss=lit.replace(',','').strip();cells.append(dict(literal=lit,value=int(ss) if re.fullmatch(r'\d+',ss) else None,tokens=tokens))
                readings[str(psm)]=cells
            cells=[]
            for k in range(len(tiles)):
                a=readings['6'][k];b=readings['4'][k];agree=a['value'] is not None and a['value']==b['value'];cells.append(dict(source_column=k+1,full_source_cell_box=boxes[k],readings={p:readings[p][k] for p in ['6','4']},value=a['value'] if agree else None,status='two_segmentation_modes_agree_pending_source_controls' if agree else 'unresolved_not_zero',ocr_derivative_transform=transforms[k]))
            fields.append(dict(proposed_candidate=name,fresh_original_label_ocr=label,fresh_label_candidate_key=actual,source_row=start+j+1,label_box=labelbox,field_identity_status='fresh_original_label_OCR_agrees' if actual==name else 'original_visual_label_review_required',cells=cells,full_numeric_montage_tsv=tsvs,montage_geometry=dict(tile_width=tw,tile_height=th,columns=1,source_cells=len(tiles),padding=15),row_bounds=[0,top,w,bottom]))
        pages.append(dict(page=x['page'],render_size=list(im.size),rotation_ccw=x['rotation_ccw'],deskew_angle_ccw=x['deskew_angle_ccw'],source_pdf_rect=x['source_rect'],columns=columns,fields=fields,block_position_basis=dict(candidate_offsets=dict(offsets),selected_physical_start=start),qualification='Independent original bytes, all physical columns and fresh label/numeric OCR. Row order recovery is a targeting proposal only; unresolved fields not zero; not accepted from controls alone.'))
    result=dict(source_id=key,raw_sha256=sha(raw),stage=stage,original_pdf_pages=len(doc),pages=pages,qualification='Versioned machine reading aid only. Original byte source positions and all source pages retained separately; this requested-contest derivative need not duplicate unrelated office tables. No cross-year/current native identity claim.')
    dest.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False).encode(),mtime=0));return key,len(pages)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--year',choices=['2020','2018'],required=True);ap.add_argument('--only');ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args();rr=[r for r in references().values() if re.match(f'sos-{a.year}-(runoff-)?county-',r['id']) and 'pdf' in str(r.get('headers',{})).lower() and (not a.only or r['id']==a.only)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        for k,n in pool.map(read,rr):print(k,n,flush=True)
if __name__=='__main__':main()
