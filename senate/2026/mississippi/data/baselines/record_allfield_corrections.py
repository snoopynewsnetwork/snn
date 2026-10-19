"""Preserve failed manual aids and original-only rereading evidence."""
from PIL import Image
from sources import OUT,BASE,save,sha
def main():
    evidence=[]
    for page in [2,3]:
        source=OUT/f'extracts/reviewed-replay/sos-2024-county-stone/p{page:04d}-original.png'
        dest=OUT/f'qa/stone-p{page}-kennedy-original-row.png'
        im=Image.open(source);w,h=im.size
        box=(int(w*.27),int(h*.62),int(w*.98),int(h*.69))
        im.crop(box).resize((int(w*1.42),int(h*.14))).save(dest)
        evidence.append(dict(path=str(dest.relative_to(BASE)),sha256=sha(dest.read_bytes()),original_raster_path=str(source.relative_to(BASE)),original_raster_sha256=sha(source.read_bytes()),crop_bounds_pixels=box,resize='2x reading enlargement; no glyph edits'))
    save(OUT/'native-allfield-correction-history.json',dict(corrections=[dict(source_id='sos-2024-county-stone',PDFpage=2,candidate='Robert F. Kennedy Jr.',prior_unaccepted_whole_page_manual_vector=[0,4,2,2,2,1,1,0,1,1,4],original_re_read_vector=[0,0,4,2,2,1,1,0,1,1,4],basis='Initial whole-page typed vector failed printed TOTAL. Enlarged complete original candidate row independently reread; source glyphs, not allocation of the two-vote residual. Failed build did not publish an accepted Stone ledger.',evidence=evidence)]))
if __name__=='__main__':main()
