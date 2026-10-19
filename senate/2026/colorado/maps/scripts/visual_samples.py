"""Selected static render samples; viewing is recorded separately after inspection."""
import json,sys
import fitz
from PIL import Image,ImageDraw
from acquire import ROOT
samples=[('arapahoe-pdf-root-fix',0),('boulder-mapdata-follow-1-final',0),('county-fremont-map-1-asset-2-0',0),('county-mesa-map-1-asset-1-follow-1',1),('county-delta-map-1',19),('weld-precinct-pdf',0),('county-la-plata-map-2',0),('county-park-map-1-asset-1',0),('county-mesa-map-1-asset-1-follow-1',3),('county-mesa-map-1-asset-1-follow-1',69),('el-paso-precinct-example',0),('sos-clerk-roster',0)]
records=[];thumbs=[]
for key,i in samples:
 p=ROOT/'assets'/f'{key}.pdf';doc=fitz.open(p);page=doc[i];scale=min(1800/page.rect.width,1800/page.rect.height);path=ROOT/'qa'/f'view-{key}-page-{i+1}.png';page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False).save(path)
 records.append(dict(source_pdf=str(p.relative_to(ROOT)),page=i+1,whole_page_png=str(path.relative_to(ROOT)),scope='selected whole page rendered1800px; manual inspection recorded separately'))
 im=Image.open(path).convert('RGB');im.thumbnail((740,610));tile=Image.new('RGB',(780,660),'white');tile.paste(im,((780-im.width)//2,35));ImageDraw.Draw(tile).text((12,12),key+' / p'+str(i+1),fill='black');thumbs.append(tile)
for j in range(0,len(thumbs),4):
 sheet=Image.new('RGB',(1560,1320),'#e5edf0')
 for i,im in enumerate(thumbs[j:j+4]):sheet.paste(im,((i%2)*780,(i//2)*660))
 sheet.save(ROOT/'qa'/f'whole-page-contact-{j//4+1}.png')
# Dense-map crop is a separate inspection derivative; source PDF untouched.
p=ROOT/'assets/arapahoe-pdf-root-fix.pdf';d=fitz.open(p);r=d[0].rect;clip=fitz.Rect(r.width*.07,r.height*.25,r.width*.42,r.height*.7);scale=1600/clip.width;d[0].get_pixmap(matrix=fitz.Matrix(scale,scale),clip=clip,alpha=False).save(ROOT/'qa/arapahoe-dense-crop.png')
records.append(dict(source_pdf='assets/arapahoe-pdf-root-fix.pdf',page=1,crop_rect_points=list(clip),png='qa/arapahoe-dense-crop.png',scope='separate dense western-map crop; not wholepage'))
# Native/Census whole previews already generated from exact source coordinates.
keys=['adams-native','douglas-native','fremont-native','archuleta-native','census-denver','census-summit']
for j in range(0,len(keys),3):
 sheet=Image.new('RGB',(1650,450),'white')
 for i,k in enumerate(keys[j:j+3]):
  im=Image.open(ROOT/'previews'/f'{k}.png').convert('RGB');im.thumbnail((550,450));sheet.paste(im,(i*550,0))
 sheet.save(ROOT/'qa'/f'native-contact-{j//3+1}.png')
(ROOT/'qa/selected-render-samples.json').write_text(json.dumps(records,indent=2)+'\n')
print(len(records),'selected render records')
