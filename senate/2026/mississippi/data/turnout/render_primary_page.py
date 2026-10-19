"""Independent original-byte page preview; no numeric extraction."""
import argparse,gzip,io,json
import fitz
from PIL import Image
from acquire_sources import BASE,OUT,receipts,sha

def render(sid,pg,rotation=0,deskew=0,scale=2.5):
 r=next(x for x in receipts if x['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');im=Image.open(io.BytesIO(doc[pg-1].get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png'))).rotate(rotation,expand=True).rotate(deskew,fillcolor=255);dest=OUT/'qa'/f'{sid}-original-p{pg}-r{rotation}.png';im.save(dest);return str(dest)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('sid');ap.add_argument('pages',nargs='+',type=int);ap.add_argument('--rotation',type=int,default=0);a=ap.parse_args()
 for p in a.pages:print(render(a.sid,p,a.rotation))
