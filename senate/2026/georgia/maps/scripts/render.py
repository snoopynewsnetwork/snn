#!/usr/bin/env python3
"""Offline PDF rendering/text extraction; derivatives never replace originals."""
import json, math
import fitz
from PIL import Image, ImageDraw
from acquire import ROOT, dump
from materialize import materialize

materialize();qa=ROOT/'qa';qa.mkdir(exist_ok=True);out=[];tiles=[]
for p in sorted((ROOT/'originals').glob('*.pdf')):
    d=fitz.open(p);name=p.stem;pages=[];text=[]
    for i,page in enumerate(d):
        text.append(f'\n--- Original PDF page {i+1} ---\n'+page.get_text())
        pix=page.get_pixmap(matrix=fitz.Matrix(1000/max(page.rect.width,page.rect.height),1000/max(page.rect.width,page.rect.height)),alpha=False)
        if i==0 or (name=='cherokee-current-pdf' and i in (1,21,42)):
            pix.save(qa/f'{name}-page{i+1}.png')
        im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((260,220))
        tile=Image.new('RGB',(280,260),'white');tile.paste(im,((280-im.width)//2,22));ImageDraw.Draw(tile).text((7,240),f'{name[:33]} p{i+1}',fill='black')
        tiles.append(tile)
        pages.append(dict(page=i+1,width_pt=page.rect.width,height_pt=page.rect.height,rotation=page.rotation,mediabox=list(page.mediabox),cropbox=list(page.cropbox),text_chars=len(text[-1])))
    (qa/f'{name}.txt').write_text('\n'.join(text))
    out.append(dict(id=name,original=str(p.relative_to(ROOT)),page_count=len(d),metadata=d.metadata,pages=pages,text_path=f'qa/{name}.txt',preview=f'qa/{name}-page1.png'))
for i in range(0,len(tiles),16):
    group=tiles[i:i+16];sheet=Image.new('RGB',(1120,260*math.ceil(len(group)/4)), '#d5dce3')
    for j,tile in enumerate(group):sheet.paste(tile,((j%4)*280,(j//4)*260))
    sheet.save(qa/f'contact-{i//16+1:02}.png')
dump(qa/'pdf-inspection.json',out)
print(json.dumps(dict(pdf_count=len(out),pages=len(tiles),contact_sheets=math.ceil(len(tiles)/16))))
