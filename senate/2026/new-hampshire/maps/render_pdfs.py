#!/usr/bin/env python3
"""Raster previews of every acquired original PDF page; no original edits."""
from acquire import ROOT,body
import fitz,json,pathlib
from PIL import Image,ImageDraw
out=[];panels=[]
for mpath in sorted((ROOT/'source').glob('*.meta.json')):
 m=json.loads(mpath.read_text())
 if m.get('format')!='pdf' or m.get('status')!=200:continue
 b=body(m['id']);doc=fitz.open(stream=b,filetype='pdf');pages=[];texts=[]
 for i,p in enumerate(doc):
  name=f"previews/{m['id']}-page{i+1}.png";scale=min(1.5,1200/max(p.rect.width,p.rect.height));pix=p.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False);pix.save(str(ROOT/name));text=p.get_text();texts.append(text)
  pages.append({'page':i+1,'preview':name,'page_points':[p.rect.width,p.rect.height],'pixels':[pix.width,pix.height],'extracted_text_characters':len(text)})
  im=Image.open(ROOT/name).convert('RGB');im.thumbnail((380,320));panel=Image.new('RGB',(400,360),'white');panel.paste(im,((400-im.width)//2,30));ImageDraw.Draw(panel).text((5,5),m['id']+f' p{i+1}',fill='black');panels.append(panel)
 (ROOT/'derived'/f"{m['id']}-text.txt").write_text('\n\f\n'.join(texts))
 out.append({'id':m['id'],'page_count':len(doc),'pages':pages,'pdf_metadata':doc.metadata,'original_sha256':m['original_sha256'],'visual_review':'pending'})
for start in range(0,len(panels),9):
 ims=panels[start:start+9];sheet=Image.new('RGB',(1200,360*((len(ims)+2)//3)),'#ddd')
 for i,im in enumerate(ims):sheet.paste(im,((i%3)*400,(i//3)*360))
 sheet.save(ROOT/'previews'/f'contact-{start//9+1:02d}.jpg',quality=90)
(ROOT/'derived/pdf-pages.json').write_text(json.dumps(out,indent=2)+'\n');print('PDFs',len(out),'pages',len(panels),'contact sheets',(len(panels)+8)//9)
