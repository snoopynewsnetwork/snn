#!/usr/bin/env python3
"""Rebuild visual contact sheets; previews only, no source geometry alterations."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image,ImageDraw
import json,fitz
ROOT=Path(__file__).resolve().parents[1];inv=json.loads((ROOT/'county-inventory.json').read_text())
for group in range(2):
 board=Image.new('RGB',(1200,1460),'white');draw=ImageDraw.Draw(board)
 for j,c in enumerate(inv[group*12:(group+1)*12]):
  x=(j%3)*400;y=(j//3)*365;p=ROOT/'counties'/c['county_fips'];im=Image.open(p/'paper2025-page1.png');im.thumbnail((380,325));board.paste(im,(x+(400-im.width)//2,y+26));draw.text((x+10,y+6),str(c['rank'])+'. '+c['county']+' actual PDF page',fill='black')
 board.save(ROOT/f'qa-paper-contact-{group+1}.jpg',quality=85)
for vintage in ['2024','2022','current']:
 for group in range(2):
  board=Image.new('RGB',(1200,1240),'white');draw=ImageDraw.Draw(board)
  for j,c in enumerate(inv[group*12:(group+1)*12]):
   x=(j%3)*400;y=(j//3)*310;p=ROOT/'counties'/c['county_fips']/(vintage+'.svg');d=fitz.open(stream=p.read_bytes(),filetype='svg');pdf=fitz.open('pdf',d.convert_to_pdf());pix=pdf[0].get_pixmap(matrix=fitz.Matrix(.5,.5),alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((380,270));board.paste(im,(x+(400-im.width)//2,y+27));draw.text((x+10,y+5),str(c['rank'])+'. '+c['county']+' '+vintage+' native',fill='black')
  board.save(ROOT/f'qa-native-{vintage}-contact-{group+1}.jpg',quality=85)
print('24 paper and72 native preview contact sheets rendered')
p=ROOT/'counties/27019/waconia-current.svg';d=fitz.open(stream=p.read_bytes(),filetype='svg');pdf=fitz.open('pdf',d.convert_to_pdf());pdf[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(str(ROOT/'qa-waconia-preview.png'))
