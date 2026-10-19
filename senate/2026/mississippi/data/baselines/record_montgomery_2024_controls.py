"""Direct complete-original Montgomery statistics; retain incompatible scope."""
import gzip,json
from PIL import Image
from sources import OUT,BASE,sha,save,original
SID='sos-2024-county-montgomery'
def main():
 path=OUT/'canvass-statistics-readings.json';d=json.loads(path.read_text());previous=dict(d);previous['readings']=[r for r in d['readings'] if r['source_id']!=SID]
 folder=OUT/'source/canvass-before-montgomery-v1';sp=folder/'snapshot.json'
 # Freeze exact prior13-body on first application; reproduce compares semantics
 # because the prior Lincoln builder may serialize the same objects again.
 if not sp.exists():
  assert len(previous['readings'])==13 and not any(r['source_id']==SID for r in d['readings']);folder.mkdir(exist_ok=True);r=path.read_bytes();z=gzip.compress(r,mtime=0);p=folder/(path.name+'.gz');p.write_bytes(z);save(sp,dict(original_path=str(path.relative_to(BASE)),original_bytes=len(r),original_sha256=sha(r),stored_path=str(p.relative_to(BASE)),stored_bytes=len(z),stored_sha256=sha(z)))
 pin=json.loads(sp.read_text());z=(BASE/pin['stored_path']).read_bytes();r=gzip.decompress(z);assert sha(z)==pin['stored_sha256'] and sha(r)==pin['original_sha256'];assert json.loads(r)==previous
 raster=OUT/'qa/historical-native-originals'/SID/'p0003-original.png';receipt=raster.with_name('p0003-render.json');crop=raster.with_name('p0003-statistics-original-3x.png');bounds=[45,230,565,485];Image.open(raster).crop(bounds).resize((1560,765)).save(crop)
 h=sha(original(SID));assert h=='dc1a44fd5ea6fa3021a44f3df38f028cd3b272ba92a90fb151536caa599bfc9d'
 row=dict(source_id=SID,raw_sha256=h,page=3,method_labels=['TOTAL'],registered_voters_total=6291,registration_definition='Printed Registered Voters - Total; active/inactive/status/date unspecified.',ballots_cast_total=[885],ballots_cast_blank=[1],printed_turnout_percent='14.07%',precinct_reporting_literal=['14 of 14'],timezone=None,evidence=str(raster.relative_to(OUT)),status_literal='Official Results',clock_literal='11/15/2024 10:24 AM',qualification='Printed statistics ballots885 cannot contain the separately printed named Senate4349 or President4424. Same packet does not establish equal report electorate/status; preserve885 literally, never use as repaired statewide county ballot volume or allocate residual.')
 d['readings']=previous['readings']+[row];save(path,d)
 def pin(p):return dict(path=str(p.relative_to(BASE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
 proof=dict(status='pass_direct_complete_original_statistics_reading',source_id=SID,raw_sha256=h,original_page=pin(raster),render_receipt=pin(receipt),crop=pin(crop)|dict(original_pixel_bounds=bounds,display_scale=3),statistics=row,separately_printed_named_Senate=4349,separately_printed_named_President=4424,statistics_minus_named_Senate=885-4349,statistics_minus_named_President=885-4424,summary_clock='11/15/2024 10:25 AM',zones=None,common_electorate_or_chronology_inferred=False,prior13_statistics_unchanged=True,prior_witness=pin(sp),qualification='Actual visible885 and14.07% retained. Incompatible source controls are not interpreted as partial-count timing, cast-ballot correction or denominator repair. Original panel includes no candidate-specific method allocation.')
 save(OUT/'source/2024-montgomery-independent-controls.json',proof);print('MontgomeryPDF3 actual885/6291/blank1; incompatible named controls retained')
if __name__=='__main__':main()
