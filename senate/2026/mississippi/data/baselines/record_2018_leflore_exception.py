"""Keep the original Leflore2018 Espy grid/TOTAL disagreement unallocated."""
import json
from PIL import Image
from sources import OUT,BASE,sha,save,original

def main():
    sid='sos-2018-county-leflore';initial=OUT/'source/2018-leflore-initial-native-reading-failure.json';body=initial.read_bytes();assert sha(body)=='fa906af4a247db1af93083e2cfeeedb1686825524e139a67e441cec46f8c7fdf';d=json.loads(body);assert sha(original(sid))==d['source_raw_sha256'];evidence=[]
    for item in d['complete_original_row_evidence']:
        pg=item['PDFpage'];receipt=json.loads((OUT/'qa/historical-native-originals'/sid/f'p{pg:04d}-render.json').read_text());raster=BASE/receipt['full_original_render_path'];assert receipt['raw_sha256']==d['source_raw_sha256'] and sha(raster.read_bytes())==receipt['render_sha256'];im=Image.open(raster);crop=im.crop(item['bounds']);target=BASE/item['crop_path'];crop.resize((crop.width*2,crop.height*2),Image.Resampling.BICUBIC).save(target);assert target.stat().st_size==item['bytes'] and sha(target.read_bytes())==item['sha256'];evidence.append(dict(item,full_original_render_path=receipt['full_original_render_path'],render_sha256=receipt['render_sha256']))
    sums={'Tobey Bernard Bartee':185,'Mike Espy':5853,'Cindy Hyde-Smith':2199,'Chris McDaniel':493};totals=dict(sums,**{'Mike Espy':5863});delta={c:sums[c]-totals[c] for c in sums};assert sum(sum(v) for v in d['initial_direct_vectors'].values())==5853
    save(OUT/'source/2018-leflore-native-TOTAL-exception-v1.json',dict(source_id=sid,raw_sha256=d['source_raw_sha256'],stage='special',native_source_columns=18,printed_TOTAL_PDFpage=3,printed_TOTAL_physical_column=8,native_candidate_sums=sums,printed_TOTAL=totals,native_minus_printed_TOTAL=delta,all_vectors_close=False,initial_reading=dict(path=str(initial.relative_to(BASE)),bytes=len(body),sha256=sha(body)),complete_original_row_evidence=evidence,reading_basis='All18 Espy native cells reread directly on both complete original pages and both enlarged complete source row strips. The same original values remain; printed5863 is independently visible. Otherthree candidate vectors close. No placement, scaling or residual correction of10votes.',qualification='One exact publication native grid has ten fewer named Espy votes than its printed countyTOTAL. This remains a primary source-scope disagreement; candidate totals/state certification and native source weights must remain separate. No release chronology, cross-year/current identity, valid-write-in, omitted method, probability or2026 turnout inference.'))
    print('Retained Leflore2018 native Espy5853 vs printed5863, unallocated -10')

if __name__=='__main__':main()
