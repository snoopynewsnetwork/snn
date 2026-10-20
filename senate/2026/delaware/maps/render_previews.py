"""Rasterize all exact affine SVG polyline positions for static visual QA.
Raster pixel quantization affects only PNGs, not SVG/native source coordinates.
"""
from common import *
from PIL import Image,ImageDraw
import xml.etree.ElementTree as ET

def main():
 outputs=[]
 for r in read(M/'previews/affine-transforms.json'):
  root=ET.parse(S/r['path']).getroot();x,y,w,h=map(float,root.attrib['viewBox'].split());scale=1600/h
  im=Image.new('RGB',(int(w*scale)+1,1601),'white');d=ImageDraw.Draw(im)
  for p in root.findall('.//{http://www.w3.org/2000/svg}polyline'):
   points=[tuple(float(v)*scale for v in xy.split(',')) for xy in p.attrib['points'].split()]
   if len(points)>1:d.line(points,fill='#174b6b',width=1)
  title=root.find('{http://www.w3.org/2000/svg}text').text;d.text((12,12),title,fill='#142b3c')
  out=M/Path(r['path']).relative_to('maps');out=out.with_suffix('.png');im.save(out);outputs.append(dict(svg=pin(S/r['path']),png=pin(out),raster_scale=scale,scope='all SVG polyline positions; source ring order maintained; only final raster pixel quantization'))
 write('qa/raster-previews.json',outputs)
if __name__=='__main__':main()
