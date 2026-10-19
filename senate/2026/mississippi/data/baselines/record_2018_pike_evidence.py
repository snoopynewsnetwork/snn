"""Retain failed first Pike2018 native reading and original-row correction."""
import gzip,json
from PIL import Image
from sources import OUT,BASE,save,sha,original

def main():
    prior=json.loads((OUT/'source/2018-pike-initial-reading-v1-pin.json').read_text());stored=(BASE/prior['stored_path']).read_bytes();raw=gzip.decompress(stored);assert len(stored)==prior['stored_bytes'] and sha(stored)==prior['stored_sha256'] and len(raw)==prior['original_bytes'] and sha(raw)==prior['original_sha256']
    sid='sos-2018-county-pike';folder=OUT/'qa/historical-native-originals'/sid;evidence=[]
    for pg in [2,3,4]:
        receipt=json.loads((folder/f'p{pg:04d}-render.json').read_text());raster=BASE/receipt['full_original_render_path'];assert sha(raster.read_bytes())==receipt['render_sha256'] and sha(original(sid))==receipt['raw_sha256'];bounds=[675,900,2010,966];crop=Image.open(raster).crop(bounds).resize((2670,132));path=folder/f'p{pg:04d}-Espy-complete-original-row-2x.png';crop.save(path);evidence.append(dict(PDFpage=pg,path=str(path.relative_to(BASE)),bytes=path.stat().st_size,sha256=sha(path.read_bytes()),original_crop_bounds=bounds,display_scale=2,full_original_render_path=receipt['full_original_render_path'],render_sha256=receipt['render_sha256']))
    receipt=json.loads((folder/'p0002-render.json').read_text())
    save(OUT/'source/2018-pike-original-reading-correction.json',dict(source_id=sid,source_raw_sha256=receipt['raw_sha256'],PDFpage=2,physical_column=11,candidate='Mike Espy',literal_native_label='(11) Leggett\nCommunity',render_sha256=receipt['render_sha256'],initial_manual_value=158,accepted_original_glyph=168,initial_failed_builder=dict(native_sum=5899,printed_TOTAL=5909,no_new_derivative_or_witness_written=True),prior_builder=prior,evidence=evidence,qualification='Complete original Espy rows reread after failed closure. PDF2c11 visibly168, not158; no residual allocation/source change. Initial builder bytes remain exact.'))

if __name__=='__main__':main()
