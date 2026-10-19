"""Direct original reading of Lincoln's separate unofficial summary/statistics.

The full original PDF is retained unchanged. No source residual is assigned
to an unprinted overvote, undervote, blank, candidate or reporting method.
"""
import csv
import gzip
import json
import fitz
from PIL import Image
from acquire_sources import BASE, OUT, receipts, savejson, sha, source

SID='sos-2024-county-lincoln'
EXPECTED_RASTERS={9:'71f32ce3192e0e3fb5762ade747f045a76cf3ee20b8523c14e5ae12a0f2f7794',
                  10:'659d2427746bd6199e62d1faac057f09a5b2f02de52213e88e7045e355f06937',
                  11:'8847165b6ac93c7d9a4e9c5d3d3e978158de7ade3bb7712bc3d8473c692b86de'}


def preserve_prior(path,name):
    folder=OUT/'source/canvass-pre-lincoln-v1';folder.mkdir(parents=True,exist_ok=True)
    stored_path=folder/(name+'.json.gz')
    current=json.loads(path.read_text())
    if stored_path.exists():
        old=gzip.decompress(stored_path.read_bytes())
        prior=json.loads(old)
    else:
        rows=current['sources'] if name=='summary' else current
        rows=[s for s in rows if s['source_id']!=SID]
        prior=dict(current,sources=rows) if name=='summary' else rows
        assert len(rows)==(14 if name=='summary' else 12)
        old=json.dumps(prior,ensure_ascii=False,indent=2).encode()+b'\n'
        stored_path.write_bytes(gzip.compress(old,compresslevel=9,mtime=0))
    old_rows=prior['sources'] if name=='summary' else prior
    current_rows=current['sources'] if name=='summary' else current
    old_ids={s['source_id'] for s in old_rows}
    assert len(old_ids)==len(old_rows)
    assert [s for s in current_rows if s['source_id'] in old_ids]==old_rows
    if name=='summary':
        assert {s['source_id'] for s in current_rows}-{s['source_id'] for s in old_rows}<={SID}
    else:
        assert {s['source_id'] for s in current_rows}-{s['source_id'] for s in old_rows}<={SID,'sos-2024-county-montgomery'}
    return {'path':str(stored_path.relative_to(BASE)),
            'raw_sha256':sha(old),'raw_bytes':len(old),
            'stored_sha256':sha(stored_path.read_bytes()),
            'stored_bytes':stored_path.stat().st_size}


def main():
    receipt=next(r for r in receipts if r['id']==SID)
    raw=source(SID);assert sha(raw)==receipt['raw_sha256']
    doc=fitz.open(stream=raw,filetype='pdf');assert len(doc)==11
    pages=[]
    for n,digest in EXPECTED_RASTERS.items():
        pix=doc[n-1].get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY)
        png=pix.tobytes('png');assert sha(png)==digest
        path=OUT/f'qa/2024-lincoln-panels-original-p{n}.png';path.write_bytes(png)
        pages.append({'page':n,'render_path':str(path.relative_to(BASE)),
                      'render_sha256':digest,'render_size':[pix.width,pix.height]})
    crop=OUT/'qa/2024-lincoln-panel-pres-sen-original-crop.png'
    image=Image.open(OUT/'qa/2024-lincoln-panels-original-p10.png')
    image.crop((45,265,570,1120)).resize((1050,1710)).save(crop)
    assert sha(crop.read_bytes())=='c43aaa74553528a78ac20aac3f0049012548f5a564fc7fe4022c0f3285f6a76f'
    senate={'Ty Pinkins':[4080],'Roger F. Wicker':[11599],
            'Write-In Totals':[47],'Contest Totals':[15898],
            'Overvotes':None,'Undervotes':None}
    president={'Kamala D. Harris / Tim Walz':[4262],
               'Chase Oliver / Mike ter Maat':[26],
               'Jill Stein / Rudolph Ware':[12],
               'Randall Terry / Stephen E. Broden':[11],
               'Donald J. Trump / JD Vance':[11432],
               'Shiva Ayyadurai / Crystal Ellis':[3],
               'Claudia De la Cruz / Karina Garcia':[6],
               'Robert F. Kennedy Jr. / Nicole Shanahan':[40],
               'Peter Sonsk / Lauren Onak':[10],
               'Write-In Totals':[27],'Contest Totals':[15898]}
    county=next(r for r in csv.DictReader((BASE/'data/county-turnout.csv').open()) if r['fips']=='28085')
    assert [int(county['2024_senate_pinkins']),int(county['2024_senate_wicker'])]==[4080,11599]
    assert int(county['2024_president_candidate_votes'])==sum(x[0] for k,x in president.items() if k not in ('Write-In Totals','Contest Totals'))==15802
    checks={'senate_named':15679,'president_named':15802,'senate_generic':47,'president_generic':27,
            'both_printed_contest_totals':15898,'Senate_unallocated_after_named_and_generic':172,
            'president_unallocated_after_named_and_generic':69,
            'statistics_ballots_cast':15898,'statistics_ballots_minus_contest_total':0}
    assert checks['senate_named']==4080+11599 and 15898-15679-47==172
    assert 15898-15802-27==69 and 15898-15898==0
    summary={'source_id':SID,'page':10,'source_status_literal':'Unofficial',
             'source_clock_literal':'Nov. 15, 2024 9:19AM','source_timezone':None,
             'methods':['TOTAL'],'senate':senate,'president':president,
             'precincts_reported_literal':'30 of 30',
             'evidence':'data/turnout/qa/2024-lincoln-panels-original-p10.png',
             'method_dimension':'county_aggregate_only_no_printed_method_split',
             'other_source_fields':{'page_number_literal':'No. 4059 P. 10/11',
                                    'footer_generated_literal':'Election Summary - 11/13/2024 4:20 PM',
                                    'circuit_clerk_stamp_literal':'NOV 13 2024'}}
    stats={'source_id':SID,'page':9,'election_date':'2024-11-05',
           'report_status_literal':'Unofficial','source_clock_literal':'Nov. 15, 2024 9:18AM',
           'source_clock_timezone':None,
           'reading_basis':'Direct visual reading of complete hash-checked original PDF page9; OCR locator not numeric authority',
           'preview':'data/turnout/qa/2024-lincoln-panels-original-p9.png',
           'registered_voters_total':0,'ballots_cast_total':15898,
           'ballots_cast_blank':None,'source_turnout_percent_literal':'0.00%',
           'precincts_reporting_literal':'30 of 30','methods_literal':None,
           'ballots_cast_by_method':None,'blank_by_method':None,
           'other_source_fields':{'page_number_literal':'No. 4059 P. 9/11',
                                  'footer_generated_literal':'Election Summary - 11/13/2024 4:20 PM',
                                  'circuit_clerk_stamp_literal':'NOV 13 2024'},
           'qualification':'Printed zero registered voters and 0.00% turnout are source values, unusable as a participation denominator; no registration-date or active-voter equivalence inferred. Blank/method/under/over unavailable on this panel.'}
    savejson(OUT/'2024-lincoln-original-panel-readings.json',{
        'scope':'Lincoln original unofficial PDFpages9–10; summary, statistics and clocks separate from signed statewide controls. Page11 unrelated offices retained in original PDF only.',
        'source_id':SID,'source_raw_sha256':receipt['raw_sha256'],
        'source_original_path':receipt['path'],'pages':pages,
        'candidate_crop_path':str(crop.relative_to(BASE)),
        'candidate_crop_sha256':sha(crop.read_bytes()),
        'summary':summary,'statistics':stats,'source_arithmetic':checks})
    summaries=OUT/'canvass-summary-readings.json';statistics=OUT/'canvass-statistics-readings.json'
    prior_pins={'summary':preserve_prior(summaries,'summary'),
                'statistics':preserve_prior(statistics,'statistics')}
    existing=json.loads(summaries.read_text());existing['sources']=[s for s in existing['sources'] if s['source_id']!=SID]+[summary]
    savejson(summaries,existing)
    rows=[s for s in json.loads(statistics.read_text()) if s['source_id']!=SID]+[stats]
    savejson(statistics,rows)
    savejson(OUT/'source/canvass-pre-lincoln-v1/pins.json',prior_pins)
    print('Lincoln original unofficial panels: Senate15679 named/47 generic, President15802 named/27 generic, contest15898, ballots15898, registration printed0 unusable')


if __name__=='__main__':main()
