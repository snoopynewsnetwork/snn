"""Reproduce complete Jackson2018 special original-row correction evidence."""
import gzip,json
from PIL import Image
from sources import OUT,BASE,save,sha,original

def main():
    prior=json.loads((OUT/'source/2018-jackson-initial-reading-v1-pin.json').read_text());z=(BASE/prior['stored_path']).read_bytes();raw=gzip.decompress(z);assert len(z)==prior['stored_bytes'] and sha(z)==prior['stored_sha256'] and len(raw)==prior['original_bytes'] and sha(raw)==prior['original_sha256'];sid='sos-2018-county-jackson';folder=OUT/'qa/historical-native-originals'/sid;evidence=[]
    for pg,ys in [(2,[956,1012]),(3,[954,1010]),(4,[952,1008])]:
        receipt=json.loads((folder/f'p{pg:04d}-render.json').read_text());raster=BASE/receipt['full_original_render_path'];assert sha(raster.read_bytes())==receipt['render_sha256'] and sha(original(sid))==receipt['raw_sha256'];bounds=[670,ys[0],2010,ys[1]];im=Image.open(raster).crop(bounds).resize((2680,(ys[1]-ys[0])*2));p=folder/f'p{pg:04d}-Hyde-complete-original-row-2x.png';im.save(p);evidence.append(dict(PDFpage=pg,path=str(p.relative_to(BASE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()),original_crop_bounds=bounds,display_scale=2,full_original_render_path=receipt['full_original_render_path'],render_sha256=receipt['render_sha256']))
    receipt=json.loads((folder/'p0003-render.json').read_text())
    save(OUT/'source/2018-jackson-original-reading-correction.json',dict(source_id=sid,source_raw_sha256=receipt['raw_sha256'],PDFpage=3,physical_column=7,candidate='Cindy Hyde-Smith',literal_native_label='OS Armory',render_sha256=receipt['render_sha256'],initial_manual_value=590,accepted_original_glyph=690,initial_failed_builder=dict(native_sum=19194,printed_TOTAL=19294,no_new_derivative_or_witness_written=True),prior_builder=prior,evidence=evidence,qualification='All three complete original Hyde-Smith rows reread after failed closure. PDF3c7 visibly690 not590; no residual allocation. Initial source-builder bytes preserved exact.'))

if __name__=='__main__':main()
