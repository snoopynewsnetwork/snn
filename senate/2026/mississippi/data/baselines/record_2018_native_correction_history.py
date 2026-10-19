"""Reproduce explicit original-glyph corrections; never allocate a residual."""
import json
from PIL import Image
from sources import OUT,BASE,save,sha,original

def main():
    sid='sos-2018-runoff-county-alcorn';folder=OUT/'qa/historical-native-originals'/sid
    receipt=json.loads((folder/'p0002-render.json').read_text());assert sha(original(sid))==receipt['raw_sha256'];raster=BASE/receipt['full_original_render_path'];assert sha(raster.read_bytes())==receipt['render_sha256'];im=Image.open(raster);pins=[]
    for name,box in [('espy-complete-row',[100,548,2060,625]),('espy-pinecrest',[1925,550,2055,625])]:
        p=folder/(name+'-original-crop.png');im.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3)).save(p);pins.append(dict(path=str(p.relative_to(BASE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()),original_raster_bounds=box,display_scale=3,qualification='Crop derived only from complete original raster, enlarged for glyph reading; not a geographic or exact digit polygon.'))
    initial=[115,3,121,149,282,132,75,21,66,120,98,144,84,409,57,121,89]
    corrected=initial.copy();corrected[10]=96
    save(OUT/'source/2018-native-correction-history.json',dict(source_id=sid,source_raw_sha256=receipt['raw_sha256'],PDFpage=2,physical_column=11,label_literal='Pinecrest',candidate='Mike Espy',initial_manual_value=98,accepted_original_glyph=96,initial_native_vector=initial,accepted_native_vector=corrected,printed_TOTAL=2084,initial_sum=sum(initial),accepted_sum=sum(corrected),basis='Initial full-page glance98 failed native sum. Complete original row and enlarged actual Pinecrest cell visibly read96; all other original row glyphs reread, not a residual allocation. Failed attempt occurred before new50-view ledger publication; existing46-view and earlier frozen objects unchanged.',full_original_render_path=receipt['full_original_render_path'],render_sha256=receipt['render_sha256'],evidence=pins))

if __name__=='__main__':main()
