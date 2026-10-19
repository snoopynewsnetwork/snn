"""Direct complete-original Perry 2020 Senate PDFpages2–3 transcription."""
from record_2020_native_manual_original import build,NAMES
from acquire_sources import OUT,savejson,sha
from PIL import Image

def page(espy,hyde,edwards): return dict(zip(NAMES,(espy,hyde,edwards)))

ROWS={
 2:page([86,391,47,43,19,90,136,74,103,116,24],
        [375,95,109,249,53,184,143,459,33,114,200],
        [10,4,4,9,1,7,7,16,1,7,9]),
 3:page([220,119,83,4,1555,None,None,None,None,None,None],
        [1031,239,858,62,4204,None,None,None,None,None,None],
        [42,6,18,1,142,None,None,None,None,None,None]),
}
LABELS={
 2:['Arlington 4100','Beaumont District 1 1030','Beaumont Senior Citizens 5120','Courthouse 5110','Deep Creek 5150','Hintonville 4090','Indian Springs 1010','Janice 5140','Miracle Temple COGIC 1040','New Augusta Community Center','Prospect 2050'],
 3:['Richton Holly Street 3060','Richton Multi Purpose 4080','Runnelstown 2040','Thompson Hill 5130','TOTAL','','','','','',''],
}

def main():
    build('perry','perry',ROWS,LABELS,15,hint_version='v5')
    original=OUT/'qa/2020-native-original-ocr/sos-2020-county-perry/p0002-original.png'
    crop=OUT/'qa/2020-native-original-review/perry-p2c3-header.png';crop.parent.mkdir(parents=True,exist_ok=True)
    Image.open(original).crop((925,275,1065,515)).rotate(270,expand=True).resize((960,560)).save(crop)
    savejson(OUT/'2020-native-perry-correction-history.json',dict(source_id='sos-2020-county-perry',source_page=2,physical_column=3,field='literal_source_header',initial_direct_fullpage_read='Beaumont Senior Citizens 1120',corrected_direct_original_crop_read='Beaumont Senior Citizens 5120',trigger='Literal label disagreement in later frozen85 peer comparison; vote values and roles already matched; original crop independently resolves printed digit.',original_raster=str(original.relative_to(OUT.parent.parent)),original_raster_sha256=sha(original.read_bytes()),source_crop=str(crop.relative_to(OUT.parent.parent)),source_crop_sha256=sha(crop.read_bytes()),count_change=False,source_vintage_change=False))
if __name__=='__main__': main()
