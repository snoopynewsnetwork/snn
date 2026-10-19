"""Direct visual transcript of both complete 2024 Tunica SEMS original pages.

The nine candidate arrays below were read from the re-rendered original PDF,
not from an OCR aid or another worker's data.  Page 7 has eleven printed
reporting columns.  Page 8 has Workforce Center, TOTAL, then blank template
columns.  The source's party-label strip is outside those numeric columns.
"""
import csv,gzip,io,json
from pathlib import Path
import fitz
from PIL import Image
from acquire_sources import BASE,OUT,receipts,sha,savejson
from read_physical_native import PRES24

SID='sos-2024-county-tunica'
LABELS7=['Austin Park','Dundee Community\nCenter','Hambrick','Mhoon Landing',
         'New Sub Park','Robinsonville\nCommunity Center','Tunica',
         'Tunica Auditorium','Tunica Economic\nComplex','Verner Park',
         'White Oak Rec.\nCenter']
# Candidate order is the literal printed order on both original pages.
V7={
 'Kamala D. Harris':[36,233,207,6,219,166,130,232,123,173,200],
 'Chase Oliver':[0,0,0,0,0,0,0,1,0,1,0],
 'Jill Stein':[0,0,0,0,0,0,0,0,0,1,0],
 'Randall Terry':[0,1,0,0,0,1,0,0,0,0,0],
 'Donald J. Trump':[33,95,8,61,46,30,265,33,105,31,49],
 'Shiva Ayyadurai':[0,0,0,0,0,0,0,0,0,0,1],
 'Claudia De la Cruz':[0,0,1,0,0,0,0,1,0,0,1],
 'Robert F. Kennedy Jr.':[0,5,1,0,2,1,1,0,5,4,0],
 'Peter Sonski':[0,0,0,0,0,1,0,0,0,0,0],
}
V8={
 'Kamala D. Harris':[111,1836],
 'Chase Oliver':[1,3],
 'Jill Stein':[0,1],
 'Randall Terry':[0,2],
 'Donald J. Trump':[43,799],
 'Shiva Ayyadurai':[0,1],
 'Claudia De la Cruz':[0,3],
 'Robert F. Kennedy Jr.':[2,21],
 'Peter Sonski':[0,1],
}

def main():
    assert list(V7)==list(V8)==PRES24 and all(len(a)==11 for a in V7.values())
    receipt=next(x for x in receipts if x['id']==SID)
    raw=gzip.decompress((BASE/receipt['path']).read_bytes())
    assert sha(raw)==receipt['raw_sha256']
    doc=fitz.open(stream=raw,filetype='pdf')
    g=json.loads(gzip.decompress((OUT/'extracts/physical-native-v3/sos-2024-county-tunica.json.gz').read_bytes()))
    pages=[];rows=[]
    for page_number,values,labels,numeric_start in [(7,V7,LABELS7,2),(8,V8,['Workforce Center','TOTAL'],2)]:
        pg=next(p for p in g['pages'] if p['page']==page_number)
        im=Image.open(io.BytesIO(doc[page_number-1].get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png')))
        im=im.rotate(pg['rotation_ccw'],expand=True).rotate(pg['deskew_angle_ccw'],fillcolor=255)
        assert list(im.size)==pg['render_size']
        png=OUT/f'qa/tunica-presidential-original-p{page_number}.png';im.save(png)
        original_rows={f['candidate_position_hint']:f for f in pg['fields'] if f['candidate_position_hint'] in PRES24}
        assert len(original_rows)==9
        for name in PRES24:
            f=original_rows[name]
            for source_col,value in enumerate(values[name],1):
                aid_cell=f['cells'][numeric_start+source_col-2]
                assert aid_cell['source_column']==numeric_start+source_col-1
                role='source_TOTAL' if page_number==8 and source_col==2 else 'native_reporting_constituent'
                rows.append(dict(source_id=SID,source_raw_sha256=receipt['raw_sha256'],source_page=page_number,source_column=source_col,candidate=name,role=role,label_literal=labels[source_col-1],source_candidate_row=f.get('source_row'),original_cell_bounds=aid_cell['bounds'],direct_original_visual_value=value,original_page_render=str(png.relative_to(BASE)),original_page_render_sha256=sha(png.read_bytes())))
        pages.append(dict(page=page_number,source_page_index=page_number-1,render_size=list(im.size),rotation_ccw=pg['rotation_ccw'],deskew_angle_ccw=pg['deskew_angle_ccw'],render_path=str(png.relative_to(BASE)),render_sha256=sha(png.read_bytes()),labels_literal=labels,numeric_column_count=len(labels),candidate_values=values,original_party_column_note='Numeric column 1 in this ledger follows the printed party-label strip; provisional physical-native-v3 c1 is not a vote column.'))
    checks={name:dict(native_sum=sum(V7[name])+V8[name][0],printed_TOTAL=V8[name][1],passes=sum(V7[name])+V8[name][0]==V8[name][1]) for name in PRES24}
    assert all(x['passes'] for x in checks.values())
    savejson(OUT/'tunica-presidential-original-readings.json',dict(scope='Complete direct original SEMS PDF pages 7 and 8 presidential nine-candidate visual transcription; source-specific party-strip alignment; no county or other source allocation.',source_id=SID,source_raw_sha256=receipt['raw_sha256'],pages=pages,candidate_checks=checks,source_native_count=12,source_TOTAL_count=1,unused_template_columns_page8=9,rows=rows))
    with (OUT/'tunica-presidential-original-cells.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Tunica direct original presidential rows',len(rows),'all nine sums close printed source TOTAL')

if __name__=='__main__':main()
