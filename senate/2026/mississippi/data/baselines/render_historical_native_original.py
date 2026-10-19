"""Render complete retained historical original PDF pages for direct source reading."""
import argparse,gzip,io,json
import fitz
from PIL import Image
from sources import OUT,BASE,original,sha,save
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--pages',required=True);ap.add_argument('--rotation',type=int);a=ap.parse_args();raw=original(a.source);doc=fitz.open(stream=raw,filetype='pdf');folder=OUT/'qa/historical-native-originals'/a.source;folder.mkdir(parents=True,exist_ok=True)
    for page in map(int,a.pages.split(',')):
        aid=OUT/'extracts/native-v4'/a.source/f'p{page:04d}.json.gz';meta=json.loads(gzip.decompress(aid.read_bytes()));assert meta['raw_sha256']==sha(raw);rotation=a.rotation if a.rotation is not None else meta.get('rotation_ccw',0);angle=meta.get('deskew_angle_ccw',0);pix=doc[page-1].get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY);im=Image.open(io.BytesIO(pix.tobytes('png'))).rotate(rotation,expand=True).rotate(angle,fillcolor=255);target=folder/f'p{page:04d}-original.png';im.save(target);assert target.stat().st_size<40000000
        save(folder/f'p{page:04d}-render.json',dict(source_id=a.source,raw_sha256=sha(raw),original_bytes=len(raw),PDFpage=page,PDFpage_count=len(doc),source_pdf_rotation=doc[page-1].rotation,source_rect=list(doc[page-1].rect),render_scale=2.7,rotation_ccw=rotation,deskew_angle_ccw=angle,render_size=list(im.size),full_original_render_path=str(target.relative_to(BASE)),render_bytes=target.stat().st_size,render_sha256=sha(target.read_bytes()),qualification='Complete original page raster, no crop or line removal. Parser orientation is only a proposal until complete page visually reviewed; no candidate/native acceptance from rendering.'))
        print(a.source,page,list(im.size),target.stat().st_size)
if __name__=='__main__':main()
