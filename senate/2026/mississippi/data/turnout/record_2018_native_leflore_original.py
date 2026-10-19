"""Direct complete-original Leflore Nov6 special grid, preserving its Espy -10.

Every number below was read from the actual PDF pages 2–3. The county TOTAL
comes from the original printed cell, never from fitting the native sum.
"""
import csv
import gzip
import io
from PIL import Image
import fitz
from acquire_sources import BASE, OUT, receipts, sha, savejson

SOURCE = 'sos-2018-county-leflore'
FIPS = '28083'
HEADERS = {
    2: ['Central Gwd','East Gwd','Minter City','Money','Morgan City','Mvsu',
        'Ne Gwd','North Gwd','North Itta Bena','Rising Sun','Schlater'],
    3: ['Sidon','South Gwd','South Itta Bena','Southeast Gwd','Southwest Gwd',
        'Swiftown','West Gwd','TOTAL','','',''],
}
VALUES = {
    'Tobey Bernard Bartee': {
        2: [6,12,6,0,2,10,18,13,28,11,4],
        3: [4,6,6,37,8,1,13,185,None,None,None]},
    'Mike Espy': {
        2: [206,844,65,28,86,173,450,548,633,334,85],
        3: [141,246,198,839,251,15,711,5863,None,None,None]},
    'Cindy Hyde-Smith': {
        2: [29,11,80,54,41,17,65,1454,58,11,60],
        3: [49,6,37,116,1,14,96,2199,None,None,None]},
    'Chris McDaniel': {
        2: [14,9,12,8,10,8,22,300,18,2,19],
        3: [2,2,4,39,3,1,20,493,None,None,None]},
}


def main():
    receipt=next(r for r in receipts if r['id']==SOURCE)
    raw=gzip.decompress((BASE/receipt['path']).read_bytes())
    assert sha(raw)==receipt['raw_sha256']=='47d8b6e8606b617d690430c0bf927f3b9aaf0542e25f046ee83d27aa400d6b87'
    doc=fitz.open(stream=raw,filetype='pdf')
    pages={};images={}
    for number in (2,3):
        png=doc[number-1].get_pixmap(matrix=fitz.Matrix(4,4),colorspace=fitz.csGRAY).tobytes('png')
        path=OUT/f'qa/2018-leflore-direct-original/p{number:04d}-original-4x.png'
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():assert path.read_bytes()==png
        else:path.write_bytes(png)
        image=Image.open(io.BytesIO(png)).convert('L')
        assert image.size==(3168,2448)
        images[number]=image
        pages[number]=dict(source_pdf_page=number,original_raster=str(path.relative_to(BASE)),
                           raster_sha256=sha(png),render_size=list(image.size),
                           physical_header_literals=HEADERS[number],
                           candidate_block_basis='complete_original_raster_visual_read')
    strips=[]
    for number in (2,3):
        # The entire Espy row, including every numeric column and printed TOTAL.
        strips.append(images[number].crop((1060,1365,3020,1475)))
    canvas=Image.new('L',(1960,250),255)
    canvas.paste(strips[0],(0,0));canvas.paste(strips[1],(0,140))
    strip_path=OUT/'qa/2018-leflore-direct-original/complete-Espy-source-rows-4x.png'
    buf=io.BytesIO();canvas.save(buf,format='PNG');strip_path.write_bytes(buf.getvalue())
    controls=[r for r in csv.DictReader((OUT/'historical-county-candidate-votes.csv').open())
              if r['source_id']==SOURCE]
    rows=[];checks={}
    for candidate,by_page in VALUES.items():
        native_sum=0;total=None
        for page in (2,3):
            assert len(HEADERS[page])==len(by_page[page])==11
            for ordinal,(header,vote) in enumerate(zip(HEADERS[page],by_page[page]),1):
                role=('source_TOTAL' if page==3 and ordinal==8 else
                      'source_native_reporting_constituent' if header else
                      'unused_template_column')
                if role=='source_TOTAL':assert header=='TOTAL' and isinstance(vote,int);total=vote
                elif role=='source_native_reporting_constituent':
                    assert isinstance(vote,int) and vote>=0;native_sum+=vote
                else:assert header=='' and vote is None
                rows.append(dict(source_id=SOURCE,election_date='2018-11-06',
                                 county='Leflore',county_fips=FIPS,
                                 source_raw_sha256=receipt['raw_sha256'],
                                 source_pdf_page=page,physical_source_column=ordinal,
                                 source_native_key=f'{FIPS}:{SOURCE}:p{page}:c{ordinal}',
                                 literal_source_header=header,role=role,
                                 office_context_literal='United States-Senate Special',
                                 candidate=candidate,party_field_literal=None,votes=vote,
                                 original_raster=pages[page]['original_raster'],
                                 reading_basis=('direct_complete_original_page_visual' if vote is not None
                                                else 'visibly_unprinted_template_cell')))
        control=next(r for r in controls if r['candidate']==candidate)
        assert int(control['votes'])==total and control['raw_sha256']==receipt['raw_sha256']
        difference=native_sum-total
        assert difference==(-10 if candidate=='Mike Espy' else 0),(candidate,difference)
        checks[candidate]=dict(native_sum=native_sum,printed_TOTAL=total,
                               county_control=int(control['votes']),
                               native_minus_printed_TOTAL=difference,
                               source_closure=(difference==0),
                               status=('unallocated_original_source_difference' if difference else
                                       'closed_to_printed_source_TOTAL'))
    assert len(rows)==88 and sum(r['role']=='source_native_reporting_constituent' for r in rows)==72
    output=dict(scope='Direct original Leflore Nov6 special Senate grid only. Espy 18 printed native cells total 5853 versus printed TOTAL 5863; -10 remains unallocated. Regular ClassI rows are separate; no runoff/current geography join.',
                source_id=SOURCE,source_original_path=receipt['path'],
                source_raw_sha256=receipt['raw_sha256'],source_pdf_page_count=len(doc),
                pages=[pages[p] for p in (2,3)],native_constituents=18,
                physical_TOTAL_page=3,physical_TOTAL_column=8,
                Espy_full_original_row_strips=dict(path=str(strip_path.relative_to(BASE)),
                                                   sha256=sha(buf.getvalue())),
                candidate_checks=checks,rows=rows)
    savejson(OUT/'2018-leflore-Nov6-native-original-readings.json',output)
    with (OUT/'2018-leflore-Nov6-native-original-cells.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print('Leflore Nov6 original 18 natives / 88 positions: Espy native',
          checks['Mike Espy']['native_sum'],'printed',checks['Mike Espy']['printed_TOTAL'])


if __name__=='__main__':main()
