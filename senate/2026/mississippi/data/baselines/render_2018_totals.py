"""Direct-original printed county TOTAL cells, not OCR transcriptions."""
import gzip,io,json,re
from collections import defaultdict
import fitz
from PIL import Image,ImageDraw
from sources import *
def main():
    ledger=[]
    for stage,prefix,names in [('special','sos-2018-county-',['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel']),('runoff','sos-2018-runoff-county-',['Mike Espy','Cindy Hyde-Smith'])]:
        refs=sorted([r for r in references().values() if r['id'].startswith(prefix) and 'pdf' in str(r.get('headers',{})).lower()],key=lambda r:r['id']);tiles=[]
        for r in refs:
            key=r['id'];tile=Image.new('RGB',(390,55+len(names)*55),'white');draw=ImageDraw.Draw(tile);draw.text((5,5),key.removeprefix(prefix),fill='black');found={};header=None
            doc=fitz.open(stream=original(key),filetype='pdf');rendered={}
            for path in sorted((OUT/'extracts/native-v4'/key).glob('*.gz')):
                x=json.loads(gzip.decompress(path.read_bytes()));cols=[c for c in x.get('columns',[]) if re.search(r'\btotal\b',c['ocr_label'],re.I)]
                for col in cols:
                    for f in x['fields']:
                        if f['field'] not in names:continue
                        if f['field']=='Chris McDaniel' and not re.search('Chris',f['label_ocr'],re.I):continue
                        c=next((c for c in f['cells'] if c['source_column']==col['source_column']),None)
                        if c is None:continue
                        pg=x['page']
                        if pg not in rendered:
                            p=doc[pg-1];im=Image.open(io.BytesIO(p.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(x['rotation_ccw'],expand=True).rotate(x['deskew_angle_ccw'],fillcolor=255);rendered[pg]=im
                        if f['field'] in found:continue # display choice recorded; no vote rows deduplicated
                        found[f['field']]=(rendered[pg].crop(tuple(c['bounds'])),pg,col['source_column'],c['bounds'])
                        if header is None:header=rendered[pg].crop(tuple(col['bounds'])).rotate(270,expand=True)
            if header:
                header.thumbnail((200,35));tile.paste(header,(175,15))
            entry=dict(source_id=key,raw_sha256=r['raw_sha256'],stage=stage,total_cells={})
            for j,name in enumerate(names):
                y=50+j*55;draw.text((5,y+10),name,fill='black')
                if name in found:
                    crop,pg,col,box=found[name];crop.thumbnail((165,50));tile.paste(crop,(215,y));entry['total_cells'][name]=dict(page=pg,source_column=col,source_cell_bounds=box)
                else:draw.text((215,y+10),'NOT LOCATED',fill='red');entry['total_cells'][name]=None
            ledger.append(entry);tiles.append(tile)
        for start in range(0,len(tiles),20):
            subset=tiles[start:start+20];height=tiles[0].height;canvas=Image.new('RGB',(390*5,(len(subset)+4)//5*height),'white')
            for i,tile in enumerate(subset):canvas.paste(tile,((i%5)*390,(i//5)*height))
            canvas.save(str(OUT/'qa'/f'2018-{stage}-county-TOTAL-originals-{start//20+1}.png'))
    save(OUT/'source/2018-total-cell-review-pointers.json',ledger)
if __name__=='__main__':main()
