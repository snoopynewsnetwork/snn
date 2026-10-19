"""Retain failed first manual reading and source-only Scott2018 rereading."""
import gzip,json
from PIL import Image
from sources import OUT,BASE,save,sha,original

def main():
    prior=json.loads((OUT/'source/2018-scott-initial-reading-v1-pin.json').read_text());stored=(BASE/prior['stored_path']).read_bytes();raw=gzip.decompress(stored);assert len(stored)==prior['stored_bytes'] and sha(stored)==prior['stored_sha256'] and len(raw)==prior['original_bytes'] and sha(raw)==prior['original_sha256']
    sid='sos-2018-runoff-county-scott';folder=OUT/'qa/historical-native-originals'/sid;evidence=[]
    for pg in [2,3,4]:
        receipt=json.loads((folder/f'p{pg:04d}-render.json').read_text());raster=BASE/receipt['full_original_render_path'];assert sha(raster.read_bytes())==receipt['render_sha256'] and sha(original(sid))==receipt['raw_sha256'];im=Image.open(raster);bounds=[680,630,2020,698];crop=im.crop(bounds).resize((2680,136));path=folder/f'p{pg:04d}-Hyde-complete-original-row-2x.png';crop.save(path);evidence.append(dict(PDFpage=pg,path=str(path.relative_to(BASE)),bytes=path.stat().st_size,sha256=sha(path.read_bytes()),original_crop_bounds=bounds,display_scale=2,full_original_render_path=receipt['full_original_render_path'],render_sha256=receipt['render_sha256']))
    receipt=json.loads((folder/'p0003-render.json').read_text())
    save(OUT/'source/2018-scott-original-reading-correction.json',dict(source_id=sid,source_raw_sha256=receipt['raw_sha256'],PDFpage=3,physical_column=6,candidate='Cindy Hyde-Smith',literal_native_label='Beat 4/Ludlow',render_sha256=receipt['render_sha256'],initial_manual_value=226,accepted_original_glyph=228,initial_failed_builder=dict(native_sum=4427,printed_TOTAL=4429,no_new_derivative_or_witness_written=True),prior_builder=prior,evidence=evidence,qualification='Fresh complete original Hyde-Smith rows reread after failed closure. PDF3c6 glyph visibly228, not226. Source correction from original pixels, no allocation of a residual or change to original/frozen witnesses.'))

if __name__=='__main__':main()
