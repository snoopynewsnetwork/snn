"""Reproduce complete Jones2018 runoff-row evidence and first reading history."""
import gzip,json
from PIL import Image
from sources import OUT,BASE,save,sha,original

def main():
    prior=json.loads((OUT/'source/2018-jones-initial-reading-v1-pin.json').read_text());z=(BASE/prior['stored_path']).read_bytes();raw=gzip.decompress(z);assert len(z)==prior['stored_bytes'] and sha(z)==prior['stored_sha256'] and len(raw)==prior['original_bytes'] and sha(raw)==prior['original_sha256'];sid='sos-2018-runoff-county-jones';folder=OUT/'qa/historical-native-originals'/sid;evidence=[]
    for pg,ys in [(2,[548,608]),(3,[546,605]),(4,[544,603]),(5,[543,602])]:
        receipt=json.loads((folder/f'p{pg:04d}-render.json').read_text());raster=BASE/receipt['full_original_render_path'];assert sha(raster.read_bytes())==receipt['render_sha256'] and sha(original(sid))==receipt['raw_sha256'];bounds=[630,ys[0],1940,ys[1]];im=Image.open(raster).crop(bounds).resize((2620,(ys[1]-ys[0])*2));p=folder/f'p{pg:04d}-Espy-complete-original-row-2x.png';im.save(p);evidence.append(dict(PDFpage=pg,path=str(p.relative_to(BASE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()),original_crop_bounds=bounds,display_scale=2,full_original_render_path=receipt['full_original_render_path'],render_sha256=receipt['render_sha256']))
    receipt=json.loads((folder/'p0005-render.json').read_text())
    save(OUT/'source/2018-jones-original-reading-correction.json',dict(source_id=sid,source_raw_sha256=receipt['raw_sha256'],PDFpage=5,physical_column=2,candidate='Mike Espy',literal_native_label='SPRINGHILL/\nMAULDIN',render_sha256=receipt['render_sha256'],initial_manual_value=152,accepted_original_glyph=182,initial_failed_builder=dict(native_sum=6916,printed_TOTAL=6946,no_new_derivative_or_witness_written=True),prior_builder=prior,evidence=evidence,qualification='All four complete original Espy rows reread after failed closure. PDF5c2 visibly182 not152; direct glyph correction, no residual allocation. Initial builder bytes exact.'))

if __name__=='__main__':main()
