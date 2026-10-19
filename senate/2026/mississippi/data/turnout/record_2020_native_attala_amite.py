"""Complete Attala/Amite original 2020 Senate grids and Amite reread history."""
from PIL import Image,ImageEnhance,ImageOps
from acquire_sources import OUT,BASE,receipts,sha,savejson
from record_2020_native_manual_original import build
E='Mike Espy';H='Cindy Hyde-Smith';J='Jimmy L. Edwards'
ATTALA_LABELS={
 2:['Berea','Carmack','East','Ethel','Hesterville','Liberty Chapel','Mcadams','Mccool','Newport','North Central','North East'],
 3:['North West','Possumneck','Providence','Sallis','South Central','South West','Thompson','Williamsville','Zama','TOTAL',''],
}
ATTALA={
 2:{
 E:[14,13,213,125,23,66,158,115,139,38,875],
 H:[118,191,553,196,191,184,132,152,152,246,264],
 J:[2,1,11,3,1,7,4,3,1,6,6],
 },
 3:{
 E:[290,81,35,558,364,254,9,365,89,3824,None],
 H:[397,125,234,251,356,93,129,740,184,4888,None],
 J:[13,1,8,7,14,2,3,9,6,108,None],
 },
}
AMITE_LABELS={
 2:['Amite River','Ariel','Berwick','Crosby','East Centreville','East Fork','East Gloster','East Liberty','Gloster','Homochitto','Liberty'],
 3:['New Zion','Oneil','Riceville','Smithdale','South Liberty','Tangipahoa','Tickfaw','Vance Park','Walls','Zion Hill','TOTAL'],
}
AMITE={
 2:{
 E:[195,224,224,96,154,83,83,66,455,9,150],
 H:[141,69,105,92,225,359,155,173,124,55,403],
 J:[2,0,4,2,2,7,4,4,7,1,8],
 },
 3:{
 E:[46,15,157,137,201,61,120,25,184,65,2750],
 H:[275,234,188,230,99,382,121,194,388,335,4347],
 J:[5,1,0,5,5,5,2,0,6,4,74],
 },
}
def amite_correction_evidence():
    sid='sos-2020-county-amite';rawsha=next(r['raw_sha256'] for r in receipts if r['id']==sid)
    qa=OUT/'qa/2020-native-original-ocr'/sid
    corrections=[]
    for page,column,candidate,prior,accepted in [(2,8,J,5,4),(3,4,E,132,137)]:
        original=qa/f'p{page:04d}-original.png';im=Image.open(original).convert('L')
        crop=im.crop((690,1190,2025,1440));crop=ImageEnhance.Contrast(ImageOps.autocontrast(crop,cutoff=1)).enhance(2).resize((2670,500))
        path=qa/f'p{page:04d}-senate-original-expanded.png';crop.save(path)
        corrections.append(dict(source_id=sid,source_raw_sha256=rawsha,source_page=page,source_column=column,candidate=candidate,initial_visual_read=prior,accepted_visual_reread=accepted,full_original_raster=str(original.relative_to(BASE)),full_original_raster_sha256=sha(original.read_bytes()),expanded_original_crop=str(path.relative_to(BASE)),expanded_original_crop_sha256=sha(path.read_bytes()),reason='Expanded contrast of the same original PDF candidate row; no residual or peer value used to select glyph.'))
    savejson(OUT/'2020-native-amite-correction-history.json',dict(scope='Two initial visual transcription errors retained separately before accepted complete original grids.',corrections=corrections))
if __name__=='__main__':
    build('attala','attala',ATTALA,ATTALA_LABELS,20,'v2')
    amite_correction_evidence()
    build('amite','amite',AMITE,AMITE_LABELS,21,'v2')
