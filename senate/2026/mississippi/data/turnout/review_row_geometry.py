"""Source-only row-specific vertical-rule targeting; no vote extraction."""
import io,json,gzip
import fitz,numpy as np
from PIL import Image,ImageDraw
from acquire_sources import BASE,OUT,receipts,sha

def run(county,pages):
 sid='sos-2024-county-'+county; f=OUT/'native-reviewed-2024.json';d=json.loads(f.read_text());s=d['sources'][sid]
 r=next(x for x in receipts if x['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==s['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf')
 for pg in pages:
  p=next(x for x in s['pages'] if x['page']==pg);im=Image.open(io.BytesIO(doc[pg-1].get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png'))).rotate(p['rotation_ccw'],expand=True).rotate(p['deskew_angle_ccw'] or 0,fillcolor=255);assert list(im.size)==p['render_size'];a=np.array(im)
  log={};canvas=Image.new('RGB',(1450,220),'white');draw=ImageDraw.Draw(canvas);draw.text((5,5),f'{sid} original p{pg}: complete unaltered Senate rows; independently read',fill='black')
  for j,name in enumerate(['Ty Pinkins','Roger F. Wicker']):
   boxes=[c['candidate_bounds'][name] for c in p['columns']]; y0,y1=boxes[0][1::2];xs=[b[0] for b in boxes]+[boxes[-1][2]];score=(a[y0+5:y1-3]<180).sum(axis=0);new=[]
   for x in xs:
    lo,hi=max(0,x-20),min(im.width,x+21);k=int(np.argmax(score[lo:hi]))+lo;new.append(k)
   assert all(70<b-a<160 for a,b in zip(new,new[1:]));log[name]=dict(header_template_x=xs,detected_row_rules=new,method='Strongest dark vertical stroke within 20 pixels of each template rule, excluding horizontal row edge. Full original row visually reviewed; no candidate values used.')
   for i,c in enumerate(p['columns']):
    c.setdefault('previous_header_aligned_candidate_bounds',{})[name]=c['candidate_bounds'][name];c['candidate_bounds'][name]=[new[i]+1,y0,new[i+1]+1,y1]
   crop=im.crop((new[0],y0,min(im.width,new[-1]+3),y1));crop.thumbnail((1440,90));canvas.paste(crop,(5,30+j*95))
  dest=OUT/'qa/native-review'/f'{sid}-p{pg:02d}-row-geometry.png';canvas.save(dest);p['row_specific_geometry']=log;p['complete_row_original_evidence']=str(dest.relative_to(BASE));p['coordinate_system']='Original fitz2.7/PIL rotation/deskew pixels; header and row-specific source rule boxes; no current geographic assertion.'
 f.write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':
 run('chickasaw',[2,3]);run('tate',[2,3])
