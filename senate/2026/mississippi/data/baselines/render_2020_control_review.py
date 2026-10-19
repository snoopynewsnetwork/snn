"""Complete original TOTAL numeric cells and labels; never typed candidate votes."""
import gzip,io,json,re
import fitz
from PIL import Image,ImageDraw
from sources import OUT,original,save
def main():
    tiles=[];pointers=[];gaps=[]
    for path in sorted((OUT/'extracts/historical-cells-v2').glob('sos-2020*.json.gz')):
        x=json.loads(gzip.decompress(path.read_bytes()));key=x['source_id'];matches=[(p,c) for p in x['pages'] for c in p['columns'] if c['role']=='source_TOTAL_OCR_proposed']
        if not matches:
            for pg in x['pages']:
                old=json.loads(gzip.decompress((OUT/'extracts/native-v4'/key/f'p{pg["page"]:04d}.json.gz').read_bytes()))
                for c in old.get('columns',[]):
                    if not re.search(r'\btotal\b',c['ocr_label'],re.I):continue
                    physical=[z for z in pg['columns'] if abs(z['header_bounds'][0]-c['bounds'][0])<3 and abs(z['header_bounds'][2]-c['bounds'][2])<3]
                    if len(physical)==1:matches.append((pg,physical[0]))
        if len(matches)!=1:gaps.append(dict(source_id=key,raw_sha256=x['raw_sha256'],TOTAL_candidates=len(matches),extracted_native_pages=len(x['pages'])));continue
        pg,c=matches[0];doc=fitz.open(stream=original(key),filetype='pdf');page=doc[pg['page']-1];im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(pg['rotation_ccw'],expand=True).rotate(pg['deskew_angle_ccw'],fillcolor=255)
        tile=Image.new('RGB',(850,280),'white');d=ImageDraw.Draw(tile);index=len(tiles)+1;d.text((5,5),f'{index}. {key.removeprefix("sos-2020-county-")}; p{pg["page"]} c{c["source_column"]}',fill='black');hb=c['header_bounds'];head=im.crop((hb[0]-2,hb[1]-8,hb[2]+2,hb[3]+8)).rotate(270,expand=True);head.thumbnail((240,40));tile.paste(head,(570,25));entry=dict(source_id=key,raw_sha256=x['raw_sha256'],review_card=index,page=pg['page'],source_column=c['source_column'],header_bounds=hb,render_size=pg['render_size'],rotation_ccw=pg['rotation_ccw'],deskew_angle_ccw=pg['deskew_angle_ccw'],fields=[])
        for j,f in enumerate(pg['fields']):
            cell=next(z for z in f['cells'] if z['source_column']==c['source_column']);label=im.crop(tuple(f['label_box']));label.thumbnail((530,60));value=im.crop(tuple(cell['full_source_cell_box']));value.thumbnail((210,60));y=70+j*65;tile.paste(label,(5,y));tile.paste(value,(580,y));entry['fields'].append(dict(proposed_candidate=f['proposed_candidate'],label_box=f['label_box'],numeric_box=cell['full_source_cell_box']))
        tiles.append(tile);pointers.append(entry)
    for j in range(0,len(tiles),10):
        sub=tiles[j:j+10];atlas=Image.new('RGB',(1700,280*((len(sub)+1)//2)),'white')
        for k,t in enumerate(sub):atlas.paste(t,((k%2)*850,(k//2)*280))
        atlas.save(OUT/'qa'/f'2020-controls-original-{j//10+1}.png')
    save(OUT/'source/2020-control-review-pointers.json',pointers);save(OUT/'source/2020-control-review-gaps.json',gaps);print(len(pointers),'original TOTAL cards;',len(gaps),'pending original packet repairs')
if __name__=='__main__':main()
