"""Original-reread Greene2018 literal-case correction; frozen witnesses stay exact."""
import copy,csv,gzip,io,json
from PIL import Image
from sources import OUT,BASE,sha,save,original

SOURCES=['sos-2018-county-greene','sos-2018-runoff-county-greene']
HISTORY=OUT/'source/2018-greene-header-case-correction-v1.json'

def same_or_original_case_correction(before,after):
    if before==after:return True
    if before.get('source_id') not in SOURCES or before['source_id']!=after.get('source_id'):return False
    expected=copy.deepcopy(before);page=next(p for p in expected['pages'] if p['page']==3);col=next(c for c in page['columns'] if c['source_column']==1)
    if col['label_literal']!='McLain':return False
    col['label_literal']='Mclain'
    return expected==after

def readpin(pin):
    z=(BASE/pin['stored_path']).read_bytes();b=gzip.decompress(z);assert len(z)==pin['stored_bytes'] and sha(z)==pin['stored_sha256'] and len(b)==pin['original_bytes'] and sha(b)==pin['original_sha256'];return b

def main():
    sp=OUT/'source/native-2018-94views-v1/snapshot.json';snap=json.loads(sp.read_text());pindict={p['original_path'].split('/')[-1]:p for p in snap['pins']}
    prior=json.loads(readpin(pindict['native-2018-original-readings.json']));rows=list(csv.DictReader(io.StringIO(readpin(pindict['native-2018-original-candidate-votes.csv']).decode())));readings=[];changed=[]
    for sid,bounds in [(SOURCES[0],[684,235,804,474]),(SOURCES[1],[688,320,802,544])]:
        s=next(s for s in prior['sources'] if s['source_id']==sid);page=next(p for p in s['pages'] if p['page']==3);assert page['columns'][0]['label_literal']=='McLain' and sha(original(sid))==s['raw_sha256'];raster=BASE/page['full_original_render_path'];assert sha(raster.read_bytes())==page['render_sha256'];im=Image.open(raster);upright=im.crop(bounds).rotate(-90,expand=True);p=raster.with_name('p0003-column1-upright-header-pixels.png');upright.save(p)
        subset=[r for r in rows if r['source_id']==sid and r['source_page']=='3' and r['source_column']=='1'];assert len(subset)==(4 if s['stage']=='special' else 2) and all(r['literal_native_label']=='McLain' for r in subset)
        for row in subset:changed.append(dict(source_id=sid,PDFpage=3,physical_column=1,candidate=row['candidate'],prior_literal_header='McLain',accepted_literal_header='Mclain',votes=int(row['votes']),role=row['role'],source_raw_sha256=row['source_raw_sha256'],source_key=row['source_key']))
        readings.append(dict(source_id=sid,PDFpage=3,physical_column=1,raw_sha256=s['raw_sha256'],full_original_render_path=page['full_original_render_path'],render_sha256=page['render_sha256'],crop_bounds=bounds,rotation_ccw=-90,literal_header='Mclain',crop=dict(path=str(p.relative_to(BASE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()),image_size=list(upright.size)),basis='Fresh complete original page reread followed by original-pixel upright header crop. Peer/coordinator discrepancy was known before own reread; not prior-blind transcription.'))
    assert len(changed)==6
    save(HISTORY,dict(status='confirmed_original_literal_header_case_correction',prior_witness=dict(path=str(sp.relative_to(BASE)),bytes=sp.stat().st_size,sha256=sha(sp.read_bytes())),prior_pins=snap['pins'],original_readings=readings,changed_candidate_header_fields=changed,changed_source_header_objects=2,votes_roles_positions_raw_hashes_unchanged=True,qualification='Only two actual Greene2018PDF3 physicalc1 header objects and six candidate-row label fields change from derivative McLain to source-printed Mclain. Frozen16/78/94v1 and all earlier originals/aids remain exact, no geographic alias/cross-stage/current-ID normalization or vote adjustment.'))
    print('Confirmed own original Greene header Mclain in both stages; six label fields only')

if __name__=='__main__':main()
