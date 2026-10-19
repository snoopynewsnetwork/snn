"""Direct readings from complete original 2020 Kemper/Winston SEMS pages 2–3.

These vectors and literal headers were transcribed from the independently
rendered originals before consulting county controls or peer numeric cells.
The latter checks are deliberately performed by build() only afterward.
"""
from PIL import Image
from acquire_sources import BASE,OUT,receipts,sha,savejson
from record_2020_native_manual_original import build,NAMES

def page(a,b,c): return dict(zip(NAMES,(a,b,c)))

def main():
    build('kemper','kemper',{
      2:page(
        [264,500,112,65,27,135,113,308,133,216,407],
        [123,157,241,47,116,25,14,193,180,107,106],
        [3,2,6,0,3,1,0,5,2,3,4]),
      3:page([230,252,203,2965]+[None]*7,
             [170,119,122,1720]+[None]*7,
             [3,4,4,40]+[None]*7)
    },{
      2:['Band Building','Courthouse','Damascus','Farmers Market','Fort Stevens','Kellis Store','Kemper Springs','LITTLE ROCK COMMUNITY CENTER','Lynville','Mount Nebo','Porterville'],
      3:['Preston','Scooba A-L','Scooba M-Z','TOTAL']+['']*7
    },14,hint_version='v3',allowed_peer_label_differences={(2,9):('Lynville','Lynnville')})
    build('winston','winston',{
      2:page(
        [715,761,174,665,190,274,435,210,97,271,98],
        [96,153,423,972,219,350,688,883,252,482,277],
        [6,5,8,29,4,7,8,14,11,16,5]),
      3:page([413,4303]+[None]*9,
             [51,4846]+[None]*9,
             [1,114]+[None]*9)
    },{
      2:['American Legion','County Agent','East Winston','Fairground','Lovorn Tractor','Mars Hill','Mill Creek','Nanih Waiya','New National Guard','Noxapater','Shiloh'],
      3:['Zion Ridge','TOTAL']+['']*9
    },12,hint_version='v3')
    source='sos-2020-county-kemper'
    original=OUT/f'qa/2020-native-original-ocr/{source}/p0002-original.png'
    crop=original.with_name('lynnville-original-header-upright.png')
    Image.open(original).crop((1660,270,1795,515)).rotate(270,expand=True).resize((980,540)).save(crop)
    savejson(OUT/'2020-native-kemper-header-review.json',dict(
      scope='Original literal header differs from peer derivative at one physical column; values and roles agree. An interim proposed two-n edit was rejected after upright original reinspection.',
      source_id=source,source_raw_sha256=next(r['raw_sha256'] for r in receipts if r['id']==source),
      source_page=2,source_column=9,initial_visual_read='Lynville',interim_peer_prompted_read='Lynnville',accepted_original_read='Lynville',frozen65_peer_derivative_label='Lynnville',current_peer_derivative_status='Independently corrected by peer after original reread; current mutable CSV excluded from this frozen reciprocal test.',
      full_original_raster=str(original.relative_to(BASE)),full_original_raster_sha256=sha(original.read_bytes()),
      expanded_original_crop=str(crop.relative_to(BASE)),expanded_original_crop_sha256=sha(crop.read_bytes())))

if __name__=='__main__': main()
