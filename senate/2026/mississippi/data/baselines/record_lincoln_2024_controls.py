"""Independent full-original Lincoln2024statistics and required contest controls.
Peer correction known beforehand; own complete PDF9–11 rendered/read separately.
No peer numeric import, no source-vintage/priority/validwritein allocation.
"""
import gzip,json
from PIL import Image
from sources import OUT,BASE,sha,save,original

def main():
    folder=OUT/'source/canvass-before-lincoln-v1';folder.mkdir(exist_ok=True);sp=folder/'snapshot.json';files=['canvass-readings.json','canvass-statistics-readings.json']
    if not sp.exists():
        pins=[]
        for name in files:
            p=OUT/name;raw=p.read_bytes();d=json.loads(raw);assert len(d['readings'])==(14 if name==files[0] else 12);q=folder/(name+'.gz');z=gzip.compress(raw,mtime=0);q.write_bytes(z);pins.append(dict(original_path=str(p.relative_to(BASE)),original_bytes=len(raw),original_sha256=sha(raw),stored_path=str(q.relative_to(BASE)),stored_bytes=len(z),stored_sha256=sha(z)))
        save(sp,dict(pins=pins,qualification='Exact owned prior14summary/12statistics checkpoint, never overwritten. Lincoln absent then, not an earlier wrong numerical reading in this package. Peer first15898 correction known before own original reread.'))
    snap=json.loads(sp.read_text());prior={}
    for pin in snap['pins']:
        z=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(z);assert len(z)==pin['stored_bytes'] and sha(z)==pin['stored_sha256'] and len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256'];prior[pin['original_path'].split('/')[-1]]=json.loads(raw)
    sid='sos-2024-county-lincoln';h=sha(original(sid));root=OUT/'qa/historical-native-originals'/sid;evidence=[]
    for page in [9,10,11]:
        p=root/f'p{page:04d}-render.json';r=json.loads(p.read_text());assert r['raw_sha256']==h and sha((BASE/r['full_original_render_path']).read_bytes())==r['render_sha256'];evidence.append(dict(PDFpage=page,receipt_path=str(p.relative_to(BASE)),receipt_sha256=sha(p.read_bytes()),raster_path=r['full_original_render_path'],raster_sha256=r['render_sha256']))
    pres=[4262,26,12,11,11432,3,6,40,10];sen=[4080,11599];assert sum(pres)==15802 and sum(sen)==15679
    panel=dict(source_id=sid,raw_sha256=h,page=10,method_labels=['TOTAL'],president=dict(candidates=[[v] for v in pres],generic_write_in_marks=[27],overvotes=None,undervotes=None,contest_opportunities=[15898]),senate=dict(candidates=[[v] for v in sen],generic_write_in_marks=[47],overvotes=None,undervotes=None,contest_opportunities=[15898]),timezone=None,reported_precincts='30 of 30',status_literal='Unofficial',clock_literal='11/13/2024 4:20 PM',fax_clock_literal='Nov.15.2024 9:19AM',source_note='Please refer to the Statewide Election Management Systems to determine if a runoff election is necessary; generic all-office report note, not Senate outcome law.',president_final_label_literal='I Peter Sonsk / Lauren Onak',source_label_qualification='Literal truncation Sonsk retained; mapped to same printed nine-candidate ballot order/source SEMS PeterSonski, not a new candidate or2026 mapping.',evidence=evidence[1]['raster_path'].removeprefix('data/baselines/'))
    stats=dict(source_id=sid,raw_sha256=h,page=9,method_labels=['TOTAL'],registered_voters_total=0,registration_definition='Printed Registered Voters - Total0 is unusable, not evidence of an empty register; active/inactive/status date unspecified.',ballots_cast_total=[15898],ballots_cast_blank=None,printed_turnout_percent='0.00%',precinct_reporting_literal=['30 of 30'],timezone=None,status_literal='Unofficial',clock_literal='11/13/2024 4:20 PM',fax_clock_literal='Nov.15.2024 9:18AM',certification_stamp_literal='NOV13 2024',evidence=evidence[0]['raster_path'].removeprefix('data/baselines/'),qualification='Complete original PDF9 direct reading15898; no previous wrong ballot reading owned here. Blank/under/over absent on selected panel are null, not zeros. Statistics-minus-contest0; residual172Senate69President arithmetic only, no allocation.')
    summary=json.loads((OUT/files[0]).read_text());summary['readings']=[r for r in summary['readings'] if r['source_id']!=sid]+[panel];statledger=json.loads((OUT/files[1]).read_text());statledger['readings']=[r for r in statledger['readings'] if r['source_id']!=sid]+[stats]
    for filename,doc in [(files[0],summary),(files[1],statledger)]:
        before=prior[filename]['readings'];after=[r for r in doc['readings'] if r['source_id']!=sid];assert before==after,'Prior accepted source readings unchanged'
        save(OUT/filename,doc)
    crop=root/'p0009-statistics-original-4x.png';im=Image.open(BASE/evidence[0]['raster_path']);bounds=[40,230,580,460];im.crop(tuple(bounds)).resize((2160,920)).save(crop)
    save(OUT/'source/2024-lincoln-independent-controls.json',dict(source_id=sid,source_raw_sha256=h,reading_basis='Own complete original PDF9/10/11 direct reading after peer15898 alert, no blind-first claim. Allrequired candidate rows typed from originals and matched county controls afterward.',original_pages=evidence,statistics_ballots=15898,president_named=15802,president_generic=27,president_unclassified_residual=69,senate_named=15679,senate_generic=47,senate_unclassified_residual=172,statistics_minus_each_contest=0,registration_printed=0,registration_usable=False,crop=dict(path=str(crop.relative_to(BASE)),bytes=crop.stat().st_size,sha256=sha(crop.read_bytes()),bounds=bounds,display_scale=4),prior_checkpoint=dict(path=str(sp.relative_to(BASE)),bytes=sp.stat().st_size,sha256=sha(sp.read_bytes())),prior_source_readings_unchanged=True,raw_ballot_change=False,native_priority_or_valid_writein_allocation=False))
    print('Lincoln2024independent original ballots15898, Sen15679+47+172, Pres15802+27+69; prior14/12 unchanged')
if __name__=='__main__':main()
