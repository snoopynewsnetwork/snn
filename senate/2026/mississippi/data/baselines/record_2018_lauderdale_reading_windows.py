"""Reproduce supplementary right-edge source reading crops; no value repair."""
import json
from PIL import Image
from sources import OUT,BASE,sha,save

def main():
    records=[]
    for stage in ['county','runoff-county']:
        sid=f'sos-2018-{stage}-lauderdale';folder=OUT/'qa/historical-native-originals'/sid
        for page in [2,3]:
            receipt=json.loads((folder/f'p{page:04d}-render.json').read_text());p=BASE/receipt['full_original_render_path'];assert sha(p.read_bytes())==receipt['render_sha256'];im=Image.open(p);bounds=[1880,500,2050,1100];q=folder/f'p{page:04d}-rightmost-original-reading.png';im.crop(tuple(bounds)).resize((510,1800)).save(q)
            records.append(dict(source_id=sid,PDFpage=page,raw_sha256=receipt['raw_sha256'],full_original_render_path=receipt['full_original_render_path'],render_sha256=receipt['render_sha256'],reading_crop_bounds=bounds,crop_display_scale=3,path=str(q.relative_to(BASE)),bytes=q.stat().st_size,sha256=sha(q.read_bytes()),qualification='Unfiltered original rightmost table reading window,3x display scale only. Complete source already visually reviewed; no restoration of clipped glyphs, residual fitting or substitute-office values.'))
    save(OUT/'source/2018-lauderdale-right-edge-reading-windows.json',dict(records=records,candidate_values_changed=False))
if __name__=='__main__':main()
