"""Render all104 original2020 county publication TOTAL blocks for direct reading.

Only peer source-position hints (ID/page/boxes/column proposal) are used; no
candidate values or labels enter image generation. Each card re-renders the
hash-checked original PDF and keeps accepted/proposed ordinals distinct.
"""
import gzip,io,json
from pathlib import Path
import fitz
from PIL import Image,ImageDraw
from acquire_sources import BASE,OUT,receipts,sha,savejson
from read_physical_native import physical_x

R={r['id']:r for r in receipts}

def main():
    peer=BASE/'data/baselines/county-2020-publication-controls.json';source=json.loads(peer.read_text())['readings']
    hints=[]
    for x in source:
        p=x['original_positions']
        hints.append(dict(source_id=x['source_id'],source_page=x['source_page'],source_column_accepted=x['source_column_accepted'],source_column_proposed=x['source_column_proposed'],original_header_box=p.get('original_header_box'),original_candidate_block_box=p.get('original_candidate_block_box'),render_size=p['render_size'],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p['deskew_angle_ccw']))
    assert len(hints)==104 and len({x['source_id'] for x in hints})==104
    out=OUT/'qa/2020-county-total-originals';out.mkdir(exist_ok=True)
    entries=[]
    for i,h in enumerate(hints):
        sid=h['source_id'];r=R[sid];raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256']
        doc=fitz.open(stream=raw,filetype='pdf');page=doc[h['source_page']-1]
        im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(h['rotation_ccw'],expand=True).rotate(h['deskew_angle_ccw'],fillcolor=255)
        peer_box_scale=[im.width/h['render_size'][0],im.height/h['render_size'][1]]
        grid=BASE/'data/baselines/extracts/native-v4'/sid/f'p{h["source_page"]:04d}.json.gz'
        g=json.loads(gzip.decompress(grid.read_bytes()));assert g['raw_sha256']==r['raw_sha256']
        xs,inferred_rules=physical_x(g)
        if not xs:xs=g['grid_x'][1:];inferred_rules=[]
        col=h['source_column_accepted'] or h['source_column_proposed'];assert col
        if 1<=col<len(xs):x0,x1=xs[col-1:col+1];grid_status='physical_rules_targetable'
        else:x0,x1=round(im.width*.52),round(im.width*.98);grid_status='no_targetable_physical_rules_broad_original_right_side_only'
        native_candidate_rows=[f['row_bounds'] for f in g['fields'] if f['field'] in ['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards'] and f.get('office_context_ocr')=='senate']
        if h['original_candidate_block_box']:
            y0,y1=[round(y*peer_box_scale[1]) for y in h['original_candidate_block_box'][1::2]];row_box_basis='peer_original_position_hint_scaled_to_own_original_render'
        elif native_candidate_rows:
            y0=min(b[1] for b in native_candidate_rows);y1=max(b[3] for b in native_candidate_rows);row_box_basis='source_original_candidate_row_geometry_hint'
        else:
            y0,y1=round(im.height*.58),round(im.height*.85);row_box_basis='broad_original_lower_page_discovery_crop'
        if h['original_header_box']:hy0,hy1=[round(y*peer_box_scale[1]) for y in h['original_header_box'][1::2]]
        else:hy0,hy1=round(im.height*.13),round(im.height*.33)
        label=im.crop((0,y0,x0,y1));value=im.crop((max(0,x0-15),y0,min(im.width,x1+15),y1));header=im.crop((x0,hy0,x1,hy1)).rotate(-90,expand=True)
        card=Image.new('RGB',(1100,380),'white');dr=ImageDraw.Draw(card)
        dr.text((8,6),f'{i+1:03d} {sid} ORIGINAL PDF p{h["source_page"]} col{col} ({"accepted hint" if h["source_column_accepted"] else "unaccepted proposal"})',fill='black')
        label.thumbnail((700,250));value=value.resize((value.width*2,value.height*2));value.thumbnail((320,240));header.thumbnail((340,85))
        card.paste(label,(8,38));card.paste(value,(745,38));card.paste(header,(745,290))
        png=out/f'{sid}.png';card.save(png)
        full=im.crop((0,y0,im.width,y1));full_band=out/f'{sid}-full-source-band.png';full.save(full_band);full_band_sha=sha(full_band.read_bytes())
        entries.append(dict(source_id=sid,source_raw_sha256=r['raw_sha256'],source_page=h['source_page'],source_column_hint=col,column_hint_status='accepted_by_independent_peer' if h['source_column_accepted'] else 'proposed_by_independent_peer_not_accepted',row_box_basis=row_box_basis,peer_box_scale_to_own_original_render=peer_box_scale,physical_grid_status=grid_status,physical_grid_x=xs,inferred_physical_grid_rules=inferred_rules,source_bounds=[x0,y0,x1,y1],source_header_bounds=[x0,hy0,x1,hy1],source_label_bounds=[0,y0,x0,y1],full_original_render_size=list(im.size),rotation_ccw=h['rotation_ccw'],deskew_angle_ccw=h['deskew_angle_ccw'],hint_file_sha256=sha(peer.read_bytes()),hint_content_policy='Only source ID, page and geometric locator/ordinal fields; no peer candidate values/labels copied.',geometry_reference_sha256=sha(grid.read_bytes()),original_card=str(png.relative_to(BASE)),card_sha256=sha(png.read_bytes()),full_original_candidate_band=str(full_band.relative_to(BASE)) if full_band else None,full_original_candidate_band_sha256=full_band_sha))
    savejson(out/'index.json',dict(scope='Original PDF render source-position review aid; numeric readings still require direct original inspection.',source_count=len(entries),peer_locator_file_sha256=sha(peer.read_bytes()),entries=entries))
    for start in range(0,len(entries),4):
        atlas=Image.new('RGB',(1100,1520),'white')
        for j,e in enumerate(entries[start:start+4]):atlas.paste(Image.open(BASE/e['original_card']),(0,j*380))
        atlas.save(out/f'atlas-{start//4+1:03d}.png')
    print('Original 2020 publication TOTAL cards',len(entries),'atlases',(len(entries)+3)//4)

if __name__=='__main__':main()
