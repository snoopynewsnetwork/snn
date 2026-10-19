"""Reconstruct direct-original candidate strips for independent visual review."""
import argparse,gzip,io,json
import fitz
from PIL import Image,ImageDraw
from sources import *
def render(key,fields):
    doc=fitz.open(stream=original(key),filetype='pdf');tiles=[]
    for path in sorted((OUT/'extracts/native-v4'/key).glob('*.gz')):
        x=json.loads(gzip.decompress(path.read_bytes()));ff=[f for f in x['fields'] if f['field'] in fields]
        if not ff:continue
        page=x['page'];p=doc[page-1];im=Image.open(io.BytesIO(p.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(x['rotation_ccw'],expand=True).rotate(x['deskew_angle_ccw'],fillcolor=255)
        for f in ff:
            t,b=f['row_bounds'][1],f['row_bounds'][3];strip=im.crop((0,t,im.width,b));tile=Image.new('RGB',(im.width,strip.height+24),'white');tile.paste(strip,(0,24));ImageDraw.Draw(tile).text((12,5),f'{key} PDF page {page}, field {f["field"]}, original row {f["source_row"]}',fill='black');tiles.append(tile)
    if not tiles:return
    width=max(t.width for t in tiles);canvas=Image.new('RGB',(width,sum(t.height for t in tiles)+8*len(tiles)),'white');y=0
    for tile in tiles:canvas.paste(tile,(0,y));y+=tile.height+8
    dest=OUT/'qa'/f'{key}-direct-original-strips.png';canvas.save(dest);print(dest)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('--fields',default='Ty Pinkins|Roger F. Wicker');a=p.parse_args();render(a.source,a.fields.split('|'))
