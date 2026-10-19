"""Direct complete-original Webster 2020 Senate PDFpages2–3 transcription."""
from record_2020_native_manual_original import build,NAMES
from acquire_sources import OUT,savejson,sha
from PIL import Image

def page(espy,hyde,edwards): return dict(zip(NAMES,(espy,hyde,edwards)))

ROWS={
 2:page([32,23,57,8,27,64,455,46,78,23,7],
        [227,176,76,98,290,264,369,215,164,195,99],
        [3,6,0,3,4,8,15,18,5,8,1]),
 3:page([47,129,43,92,37,30,1198,None,None,None,None],
        [191,330,307,466,278,322,4067,None,None,None,None],
        [5,10,6,7,8,6,113,None,None,None,None]),
}
LABELS={
 2:['Bellefontaine','Big Black','Bluff Springs','Cadaretta','Clarkson','Cumberland','Eupora No. 1','Eupora No. 2','Eupora No. 3','Fame','Fay'],
 3:['Grady','Maben','Mantee','Mathiston','Tomnolen','Walthall','TOTAL','','','',''],
}

def main():
    build('webster','webster',ROWS,LABELS,17,hint_version='v5')
    original=OUT/'qa/2020-native-original-ocr/sos-2020-county-webster/p0003-original.png'
    crop=OUT/'qa/2020-native-original-review/webster-p3c7-hyde-total.png';crop.parent.mkdir(parents=True,exist_ok=True)
    Image.open(original).crop((1380,1270,1530,1385)).resize((1200,920)).save(crop)
    savejson(OUT/'2020-native-webster-correction-history.json',dict(source_id='sos-2020-county-webster',source_page=3,physical_column=7,candidate='Cindy Hyde-Smith',field='source_TOTAL',initial_direct_fullpage_read=4057,corrected_direct_original_crop_read=4067,trigger='Native sum did not close first total read; enlarged original-only crop independently resolves third digit as 6. No vote was allocated to a source constituent.',original_raster=str(original.relative_to(OUT.parent.parent)),original_raster_sha256=sha(original.read_bytes()),source_crop=str(crop.relative_to(OUT.parent.parent)),source_crop_sha256=sha(crop.read_bytes()),source_vintage_change=False))
if __name__=='__main__': main()
