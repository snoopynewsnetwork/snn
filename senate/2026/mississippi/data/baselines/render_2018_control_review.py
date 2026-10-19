"""Original labels, column header and TOTAL cells for visual transcription."""
import gzip,io,json,re
import fitz
from PIL import Image,ImageDraw
from sources import *
def main():
 for stage,prefix in [('special','sos-2018-county-'),('runoff','sos-2018-runoff-county-')]:
  tiles=[];pointers=[]
  for r in sorted([r for r in references().values() if r['id'].startswith(prefix) and 'pdf' in str(r.get('headers',{})).lower()],key=lambda z:z['id']):
   key=r['id'];p=OUT/'extracts/2018-blocks'/f'{key}.json.gz';tile=Image.new('RGB',(850,320 if stage=='special' else 190),'white');draw=ImageDraw.Draw(tile);draw.text((5,5),key.removeprefix(prefix),fill='black');entry=dict(source_id=key,raw_sha256=r['raw_sha256'],selected=None)
   if p.exists():
    x=json.loads(gzip.decompress(p.read_bytes()));matches=[(pg,c) for pg in x['pages'] for c in pg['columns'] if c['unit_type']=='summary_TOTAL']
    if not matches:
     # A second original-header OCR pass may miss TOTAL. Recover only its
     # physical box from the earlier raw pass; visual header remains displayed.
     for pg in x['pages']:
      old=json.loads(gzip.decompress((OUT/'extracts/native-v4'/key/f'p{pg["page"]:04d}.json.gz').read_bytes()))
      for c in old.get('columns',[]):
       if re.search(r'\btotal\b',c['ocr_label'],re.I):
        physical=min(pg['columns'],key=lambda z:abs(z['header_box'][0]-c['bounds'][0])+abs(z['header_box'][2]-c['bounds'][2]))
        if abs(physical['header_box'][0]-c['bounds'][0])<3 and abs(physical['header_box'][2]-c['bounds'][2])<3:matches.append((pg,physical))
    if matches:
     pg,c=matches[0];doc=fitz.open(stream=original(key),filetype='pdf');page=doc[pg['page']-1];im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(pg['rotation_ccw'],expand=True).rotate(pg['deskew_angle_ccw'],fillcolor=255)
     header=im.crop(tuple(c['header_box'])).rotate(270,expand=True);header.thumbnail((250,30));tile.paste(header,(580,5));entry['selected']=dict(page=pg['page'],source_column=c['source_column'],header_box=c['header_box'],fields=[])
     for j,f in enumerate(pg['fields']):
      cell=next(z for z in f['cells'] if z['source_column']==c['source_column']);label=im.crop(tuple(f['label_box']));label.thumbnail((510,60));value=im.crop(tuple(cell['box']));value.thumbnail((210,60));y=45+j*65;tile.paste(label,(5,y));tile.paste(value,(580,y));draw.text((790,y+10),str(pg['page'])+':'+str(c['source_column']),fill='black');entry['selected']['fields'].append(dict(candidate=f['candidate'],label_box=f['label_box'],cell_box=cell['box']))
    else:draw.text((10,50),'TOTAL NOT LOCATED: original packet review required',fill='red')
   else:draw.text((10,50),'BLOCK AID PENDING',fill='red')
   tiles.append(tile);pointers.append(entry)
  for start in range(0,len(tiles),10):
   sub=tiles[start:start+10];h=tiles[0].height;canvas=Image.new('RGB',(1700,h*((len(sub)+1)//2)),'white')
   for i,t in enumerate(sub):canvas.paste(t,((i%2)*850,(i//2)*h))
   canvas.save(str(OUT/'qa'/f'2018-{stage}-controls-original-{start//10+1}.png'))
  save(OUT/'source'/f'2018-{stage}-control-review-pointers.json',pointers)
if __name__=='__main__':main()
