#!/usr/bin/env python3
"""Offline deterministic rebuild; no network calls or writes outside owned paths."""
import sys
sys.dont_write_bytecode=True
from inspect_sources import run as inspect
from build_geometry import run as geometry
from build_alternatives import run as alternatives
from build_supplements import run as supplements
from build_compatibility import run as compatibility
from build_package import run as package
from build_report import run as report
from seal import run as seal
from validate import run as validate
from pathlib import Path
from PIL import Image,ImageDraw
import json
ROOT=Path(__file__).resolve().parents[1]
def contact_sheet():
 pdf=json.loads((ROOT/'pdf-inventory.json').read_text());sheet=Image.new('RGB',(1600,2050),'#e7edf2');draw=ImageDraw.Draw(sheet)
 for i,r in enumerate(pdf):
  im=Image.open(ROOT/r['pages'][0]['preview']).convert('RGB');im.thumbnail((385,370));x=i%4*400;y=i//4*410;sheet.paste(im,(x+(400-im.width)//2,y+28));draw.text((x+8,y+5),r['label'].split(' County')[0]+' '+r['label'].split()[-1],fill='black')
 sheet.save(ROOT/'qa/priority-pdf-contact-sheet.jpg',quality=88)
if __name__=='__main__':
 for f in [inspect,geometry,alternatives,supplements,compatibility,package,report,contact_sheet,seal,validate,seal]:f()
 sys.argv.append('--verify-manifest');validate()
