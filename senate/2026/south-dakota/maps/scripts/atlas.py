"""Raster previews of already separate display SVGs; no source geometry edits."""
from common import *
from PIL import Image,ImageDraw
import xml.etree.ElementTree as ET,re,math
def render(p):
 root=ET.parse(p).getroot();im=Image.new('RGB',(1000,760),'white');d=ImageDraw.Draw(im)
 for el in root:
  tag=el.tag.rsplit('}',1)[-1]
  if tag=='text':d.text((float(el.attrib['x']),float(el.attrib['y'])-12),el.text,fill='#152b40')
  if tag=='path':
   for ring in el.attrib['d'].split('M ')[1:]:
    pts=[tuple(map(float,p)) for p in re.findall(r'(-?[0-9.]+),(-?[0-9.]+)',ring)]
    if len(pts)>1:d.line(pts+[pts[0]],fill='#334c66',width=1)
 return im
def main():
 c=json.loads((STATE/CONTRACT).read_bytes());sheet=Image.new('RGB',(1800,11*255),'white');d=ImageDraw.Draw(sheet)
 for i,p in enumerate(c['county_parents']):
  f=p['parent_key'];im=render(MAPS/f'previews/census-{f}.svg');im.thumbnail((290,220));x=i%6*300;y=i//6*255;sheet.paste(im,(x+(300-im.width)//2,y+26));d.text((x+10,y+8),p['county']+' | '+f,fill='black')
 sheet.save(MAPS/'previews/census-atlas.png',optimize=True)
 for n in ['minnehaha','pennington']:render(MAPS/f'previews/{n}-native-linear.svg').save(MAPS/f'previews/{n}-native-linear.png',optimize=True)
if __name__=='__main__':main()
