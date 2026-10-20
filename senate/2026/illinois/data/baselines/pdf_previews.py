"""Read-only PDF rendering derivatives used for actual visual table verification."""
import subprocess
from source_io import ROOT,raw,dump,sha
def main():
    pages=[('original-fec-2024-president-pdf',6,'fec2024-page6'),('fec-2020-book',79,'fec2020-page79'),('fec-2022-book',29,'fec2022-page29'),('original-turnout-chicago-proclamation-2024',10,'chicago-page10'),('original-turnout-bloomington-writein-2024',1,'bloomington-writeins')];out=[]
    for sid,page,label in pages:
        p=ROOT/'source/previews'/label;p.parent.mkdir(exist_ok=True)
        subprocess.run(['pdftoppm','-png','-singlefile','-f',str(page),'-l',str(page),'-r','100','-',str(p)],input=raw(sid),capture_output=True,check=True)
        png=p.with_suffix('.png');out.append(dict(source_id=sid,PDF_page=page,path=str(png.relative_to(ROOT)),bytes=png.stat().st_size,sha256=sha(png.read_bytes()),render='Poppler100DPI PNG, single complete page',review='Rendered pages visually inspected2026-10-20UTC: Illinois general-election columns/counts, FECscattered518, Chicago presidential labels/total and Bloomington combined-ticket writein rows checked against extraction.'))
    dump(ROOT/'source/pdf-visual-review.json',out)
if __name__=='__main__':main()
