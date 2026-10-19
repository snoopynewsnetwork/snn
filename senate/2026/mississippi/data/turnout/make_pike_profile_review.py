"""Original scanned Pike profile panels and untouched source-position OCR aids."""
import gzip,io,json,subprocess
import fitz
from PIL import Image,ImageDraw
from acquire_sources import BASE,OUT,receipts,sha,savejson

def main():
 sid='sos-2024-county-pike';r=next(r for r in receipts if r['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');dest=OUT/'qa/pike-profiles';dest.mkdir(exist_ok=True);cards=[];inventory=[]
 for n in range(15,57):
  page=doc[n-1];full=dest/f'original-p{n}.png'
  if full.exists():im=Image.open(full)
  else:im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(3.5,3.5),colorspace=fitz.csGRAY).tobytes('png')));im.save(full)
  box=[50,250,1050,1790];crop=im.crop(box);cp=dest/f'original-crop-p{n}.png';crop.save(cp)
  pointer=dict(source_id=sid,raw_sha256=r['raw_sha256'],source_page=n,render_scale=3.5,render_size=list(im.size),crop_bounds=box,original_render_path=str(full.relative_to(BASE)),render_sha256=sha(full.read_bytes()),crop_path=str(cp.relative_to(BASE)))
  savejson(dest/f'original-p{n}-pointer.json',pointer)
  tp=dest/f'original-crop-p{n}.tsv.gz'
  if tp.exists():tsv=gzip.decompress(tp.read_bytes())
  else:tsv=subprocess.run(['tesseract',str(cp),'stdout','--psm','6','tsv'],capture_output=True,check=True).stdout;tp.write_bytes(gzip.compress(tsv,mtime=0))
  import csv
  words=[z['text'] for z in csv.DictReader(io.StringIO(tsv.decode()),delimiter='\t') if z.get('text','').strip()];text=' '.join(words);candidate=all(term in text.lower() for term in ['statistics','president','senate']);inventory.append(dict(source_page=n,original_render_path=str(full.relative_to(BASE)),raw_OCR_text=text,proposed_profile_start=candidate,classification='source-position discovery only, requires original page review'))
  if candidate:
   can=Image.new('RGB',(1000,1580),'white');can.paste(crop,(0,40));ImageDraw.Draw(can).text((8,8),f'UNALTERED ORIGINAL Pike PDF p{n} 3.5x',fill='black');cards.append(can)
  print('original section page',n,'proposed profile start',candidate,flush=True)
 old=dest/'alternating-page-initial-review'
 if not old.exists():
  old.mkdir()
  for q in dest.glob('review-*.png'):q.rename(old/q.name)
 for i in range(0,len(cards),3):
  canvas=Image.new('RGB',(3000,1580),'white')
  for j,im in enumerate(cards[i:i+3]):canvas.paste(im,(1000*j,0))
  canvas.save(dest/f'review-{i//3+1}.png')
 savejson(dest/'page-inventory.json',dict(source_id=sid,raw_sha256=r['raw_sha256'],pages=inventory,proposed_profile_starts=[p['source_page'] for p in inventory if p['proposed_profile_start']],qualification='Complete42-page section inventory. Initial alternating-page hypothesis rejected because original profiles span variable page counts; initial panels retained, not accepted.'))
 print(len(cards),'proposed original profile starts;',len(inventory),'pages inspected by fresh source OCR discovery')
if __name__=='__main__':main()
