"""Original Pike vendor-profile42-page raster/OCR inventory, source positions.

Preserves every page15–56 rather than guessing an alternating page stride.
No peer numeric field, source label or candidate order enters extraction.
"""
import concurrent.futures,gzip,io,json,re,subprocess
import fitz
from PIL import Image
from sources import OUT,BASE,original,sha,save
def main():
    key='sos-2024-county-pike';raw=original(key);digest=sha(raw);folder=OUT/'extracts/pike-vendor-original';folder.mkdir(exist_ok=True);doc=fitz.open(stream=raw,filetype='pdf');assert len(doc)==56;tasks=[];rotations={pg:doc[pg-1].rotation for pg in range(15,57)}
    for pg in range(15,57):
        path=folder/f'p{pg:02d}-original.png';dest=folder/f'p{pg:02d}-vision.json.gz'
        if not path.exists():doc[pg-1].get_pixmap(matrix=fitz.Matrix(2.4,2.4),colorspace=fitz.csGRAY).save(str(path))
        tasks.append((pg,path,dest))
    def run(task):
        pg,path,dest=task
        if dest.exists():return json.loads(gzip.decompress(dest.read_bytes()))
        result=subprocess.run([str(OUT/'qa/vision-ocr'),str(path)],capture_output=True,text=True,check=True);x=json.loads(result.stdout);b=path.read_bytes();x.update(source_id=key,source_raw_sha256=digest,source_page=pg,source_pdf_page_rotation=rotations[pg],render_scale=2.4,rotation_ccw=0,deskew_angle_ccw=0,render_size=list(Image.open(path).size),full_original_render_path=str(path.relative_to(BASE)),render_sha256=sha(b),engine='Own Apple Vision accurate en-US, language correction false; raw full original page, no cell simplification',qualification='Original profile page OCR aid, not accepted field values. Candidate source order varies; do not assume ballot order or normalize whole source views.');dest.write_bytes(gzip.compress(json.dumps(x,ensure_ascii=False).encode(),mtime=0));return x
    pages=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for x in pool.map(run,tasks):
            obs=x.get('observations',[]);head=[z for z in obs if re.search(r'^\(\d{1,2}\)',z['text'])];offices=[z for z in obs if re.search(r'Statistics|President United|Senate United|Registered Voters|Ballots Cast|Total Votes Cast|Contest Totals',z['text'],re.I)];pages.append(dict(source_id=key,raw_sha256=digest,source_page=x['source_page'],full_original_render_path=x['full_original_render_path'],render_sha256=x['render_sha256'],render_size=x['render_size'],own_raw_OCR_path=str((folder/f'p{x["source_page"]:02d}-vision.json.gz').relative_to(BASE)),source_profile_header_observations=head,required_office_or_control_label_observations=offices,field_acceptance=False));print('originalPikevendorpage',x['source_page'],'profileheaders',[z['text'] for z in head],flush=True)
    save(OUT/'pike-vendor-page-inventory.json',dict(source_id=key,raw_sha256=digest,actual_PDF_pages=list(range(15,57)),page_count=42,qualification='Complete original42-page vendor section inventory; no alternating-page or constant-profile-length assumption. Every source observation preserved, original candidate order and profile continuity require source review; no numeric acceptance from sums.',pages=pages))
if __name__=='__main__':main()
