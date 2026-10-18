#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
from acquire import *
from build_geometry import dump
import fitz
from PIL import Image
from io import BytesIO

def run():
 out=[];names=['greenville-2026-polling','anderson-follow-33','florence-follow-13','sumter-follow-9','sumter-follow-19']
 for n in names:
  rec=json.loads((ROOT/'raw'/f'{n}.request.json').read_text());b=body(n);r={'source_id':n,'original_capture':'raw/'+n+'.request.json','original_path':rec['path'],'original_sha256':sha(b),'original_bytes':len(b),'requested_url':rec['requested_url'],'status':rec['status'],'classification':'polling-location roster; no polygon equivalence established'}
  if b.startswith(b'%PDF'):
   doc=fitz.open(stream=b,filetype='pdf');r.update(page_count=len(doc),metadata=doc.metadata,pages=[]);text=[]
   for i,p in enumerate(doc):
    pp=ROOT/'qa'/f'{n}-page-{i+1:02d}.png';p.get_pixmap(matrix=fitz.Matrix(1500/max(p.rect.width,p.rect.height),1500/max(p.rect.width,p.rect.height)),alpha=False).save(pp);r['pages'].append({'page':i+1,'preview':str(pp.relative_to(ROOT)),'media_box':list(p.mediabox)});text.append(p.get_text(sort=True))
   txt=ROOT/'derived'/f'{n}.txt';txt.write_text('\n\f\n'.join(text));r['text_path']=str(txt.relative_to(ROOT))
  elif b.startswith(b'\xff\xd8'):
   r['classification']='historical precinct/polling-location roster raster (2022 label); not a map or polygon file' if n=='sumter-follow-19' else 'polling-location roster raster (2026 label); not polygon geometry'
   im=Image.open(BytesIO(b));r['image_size']=list(im.size);im.thumbnail((1600,1600));pp=ROOT/'qa'/f'{n}.png';im.save(pp);r['preview']=str(pp.relative_to(ROOT))
  else:r['classification']='not admitted map/roster; inspect original content and HTTP status'
  out.append(r)
 # Reuse exact peer original: do not duplicate PDF bytes.
 p=ROOT.parent/'data/results-sources/raw/lexington-parent-child-85.meta.json';meta=json.loads(p.read_text());fp=p.parent/'lexington-parent-child-85.body.gz';b=gzip.decompress(fp.read_bytes());assert sha(b)==meta['original_sha256'];doc=fitz.open(stream=b,filetype='pdf');r={'source_id':'lexington-november-notice-peer-original','external_original_path':str(fp.relative_to(ROOT.parent)),'external_metadata_path':str(p.relative_to(ROOT.parent)),'original_metadata':meta,'classification':'November 3, 2026 precinct notice/polling roster; not polygon file or geographic crosswalk','page_count':len(doc),'pages':[]};texts=[]
 for i,pag in enumerate(doc):
  pp=ROOT/'qa'/f'lexington-november-notice-page-{i+1:02d}.png';pag.get_pixmap(matrix=fitz.Matrix(1500/max(pag.rect.width,pag.rect.height),1500/max(pag.rect.width,pag.rect.height)),alpha=False).save(pp);r['pages'].append({'page':i+1,'preview':str(pp.relative_to(ROOT)),'media_box':list(pag.mediabox)});texts.append(pag.get_text(sort=True))
 txt=ROOT/'derived/lexington-november-notice.txt';txt.write_text('\n\f\n'.join(texts));r['text_path']=str(txt.relative_to(ROOT));out.append(r);dump('supplement-inventory.json',out);print([(r['source_id'],r.get('page_count'),r['classification']) for r in out])
if __name__=='__main__':run()
