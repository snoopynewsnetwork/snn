"""Confirm literal Mhoon Landing from both original2018 pages; old witnesses exact."""
import copy,csv,io,json
from PIL import Image
from sources import OUT,BASE,sha,save,original
from record_2018_greene_header_case import readpin,same_or_original_case_correction

SOURCES=['sos-2018-county-tunica','sos-2018-runoff-county-tunica']
HISTORY=OUT/'source/2018-tunica-header-correction-v1.json'

def same_or_documented_header_correction(before,after):
    if same_or_original_case_correction(before,after):return True
    if before.get('source_id') not in SOURCES or before['source_id']!=after.get('source_id'):return False
    expected=copy.deepcopy(before);page=next(p for p in expected['pages'] if p['page']==2);col=next(c for c in page['columns'] if c['source_column']==2)
    if col['label_literal']!='Moon Landing':return False
    col['label_literal']='Mhoon Landing';return expected==after

def main():
    sp=OUT/'source/native-2018-142views-v1/snapshot.json';snap=json.loads(sp.read_text());pins={p['original_path'].split('/')[-1]:p for p in snap['pins']};prior=json.loads(readpin(pins['native-2018-original-readings.json']));rows=list(csv.DictReader(io.StringIO(readpin(pins['native-2018-original-candidate-votes.csv']).decode())));readings=[];changed=[]
    for sid in SOURCES:
        s=next(s for s in prior['sources'] if s['source_id']==sid);page=next(p for p in s['pages'] if p['page']==2);col=page['columns'][1];assert col['source_column']==2 and col['label_literal']=='Moon Landing' and sha(original(sid))==s['raw_sha256'];raster=BASE/page['full_original_render_path'];assert sha(raster.read_bytes())==page['render_sha256'];upright=Image.open(raster).crop(col['header_bounds']).rotate(-90,expand=True);p=raster.with_name('p0002-column2-original-header-upright.png');upright.save(p)
        subset=[r for r in rows if r['source_id']==sid and r['source_page']=='2' and r['source_column']=='2'];assert len(subset)==(4 if s['stage']=='special' else 2) and all(r['literal_native_label']=='Moon Landing' for r in subset)
        for row in subset:changed.append(dict(source_id=sid,PDFpage=2,physical_column=2,candidate=row['candidate'],prior_literal_header='Moon Landing',accepted_literal_header='Mhoon Landing',votes=int(row['votes']),role=row['role'],source_raw_sha256=row['source_raw_sha256'],source_key=row['source_key']))
        readings.append(dict(source_id=sid,PDFpage=2,physical_column=2,raw_sha256=s['raw_sha256'],full_original_render_path=page['full_original_render_path'],render_sha256=page['render_sha256'],crop_bounds=col['header_bounds'],rotation_ccw=-90,literal_header='Mhoon Landing',crop=dict(path=str(p.relative_to(BASE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()),image_size=list(upright.size)),basis='Fresh own complete original page reread followed by unchanged-pixel upright crop. Peer finding known first, not prior-blind transcription.'))
    assert len(changed)==6
    save(HISTORY,dict(status='confirmed_original_literal_header_correction',prior_witness=dict(path=str(sp.relative_to(BASE)),bytes=sp.stat().st_size,sha256=sha(sp.read_bytes())),prior_pins=snap['pins'],original_readings=readings,changed_candidate_header_fields=changed,changed_source_header_objects=2,votes_roles_positions_raw_hashes_unchanged=True,qualification='Only two Tunica2018PDF2physicalc2 source header objects and six candidate-row label fields change from derivative MoonLanding to printed MhoonLanding. All frozen witnesses/originals/aids remain exact; no geographic alias or cross-stage/current-ID join.'))
    print('Confirmed own original Tunica MhoonLanding both stages; six label-only fields')

if __name__=='__main__':main()
