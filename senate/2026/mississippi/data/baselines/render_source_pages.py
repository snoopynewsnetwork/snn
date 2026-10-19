"""Reproduce complete original-page review rasters (no OCR overlay)."""
import argparse,gzip,io,json
import fitz
from PIL import Image
from sources import *
def render(key,pg,scale=2.1):
 path=OUT/'extracts/native-v4'/key/f'p{pg:04d}.json.gz';x=json.loads(gzip.decompress(path.read_bytes()));doc=fitz.open(stream=original(key),filetype='pdf');p=doc[pg-1]
 im=Image.open(io.BytesIO(p.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY).tobytes('png'))).rotate(x['rotation_ccw'],expand=True).rotate(x['deskew_angle_ccw'],fillcolor=255)
 dest=OUT/'qa'/f'{key}-full-original-p{pg}.png';im.save(str(dest));return str(dest)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('pages');a=ap.parse_args()
 for pg in map(int,a.pages.split(',')):print(render(a.source,pg))
