"""Direct complete eleven-candidate visual reading of 2024 Winston originals.

The original PDF pixels supply every value.  The independent peer's v12 file
is used only for candidate-row geometric hints because the earlier machine
inventory omitted much of these scanned rows; its values are never read here.
"""
import csv,gzip,io,json
import fitz
from PIL import Image
from acquire_sources import BASE,OUT,receipts,sha,savejson
from read_physical_native import PRES24

SID='sos-2024-county-winston';NAMES=PRES24+['Ty Pinkins','Roger F. Wicker']
LABELS2=['American Legion','County Agent','East Winston','Fairground',
 'Lovorn Tractor','Mars Hill','Mill Creek','Nanih Waiya','New National Guard',
 'Noxapater','Shiloh']
LABELS3=['Zion Ridge','TOTAL']+['']*9
V2={
 'Kamala D. Harris':[557,721,143,419,146,200,342,151,95,200,92],
 'Chase Oliver':[1,1,1,2,0,0,2,0,0,0,1],
 'Jill Stein':[1,1,1,4,1,1,3,0,0,0,0],
 'Randall Terry':[2,2,1,1,0,0,0,1,0,0,0],
 'Donald J. Trump':[139,168,395,956,187,356,713,903,265,522,261],
 'Shiva Ayyadurai':[2,0,0,0,1,0,0,3,0,0,0],
 'Claudia De la Cruz':[0,0,0,0,0,0,1,0,0,0,0],
 'Robert F. Kennedy Jr.':[2,7,2,3,2,2,4,3,2,1,2],
 'Peter Sonski':[0,0,0,2,0,1,1,0,0,0,0],
 'Ty Pinkins':[560,730,149,436,152,198,344,161,95,203,94],
 'Roger F. Wicker':[148,168,394,952,188,361,722,890,263,517,264],
}
V3={
 'Kamala D. Harris':[326,3392],
 'Chase Oliver':[0,8],
 'Jill Stein':[0,12],
 'Randall Terry':[1,8],
 'Donald J. Trump':[57,4922],
 'Shiva Ayyadurai':[0,6],
 'Claudia De la Cruz':[0,1],
 'Robert F. Kennedy Jr.':[1,31],
 'Peter Sonski':[0,4],
 'Ty Pinkins':[317,3439],
 'Roger F. Wicker':[70,4937],
}

def main():
    assert list(V2)==list(V3)==NAMES and len(LABELS2)==len(LABELS3)==11
    receipt=next(x for x in receipts if x['id']==SID)
    raw=gzip.decompress((BASE/receipt['path']).read_bytes());assert sha(raw)==receipt['raw_sha256']
    doc=fitz.open(stream=raw,filetype='pdf')
    peer=BASE/'data/baselines/extracts/reviewed-replay/sos-2024-county-winston/independent-presidential-fields-v12.json.gz'
    peer_geometry=json.loads(gzip.decompress(peer.read_bytes()))
    assert peer_geometry['raw_sha256']==receipt['raw_sha256']
    senate=json.loads((OUT/'native-reviewed-2024.json').read_text())['sources'][SID]
    rows=[];pages=[]
    for page_number,values,labels in [(2,V2,LABELS2),(3,V3,LABELS3)]:
        g=next(x for x in peer_geometry['pages'] if x['page']==page_number)
        im=Image.open(io.BytesIO(doc[page_number-1].get_pixmap(matrix=fitz.Matrix(2.5,2.5),colorspace=fitz.csGRAY).tobytes('png')))
        im=im.rotate(g['rotation_ccw'],expand=True).rotate(g['deskew_angle_ccw'],fillcolor=255)
        assert list(im.size)==g['render_size']
        png=OUT/f'qa/winston-allfield-original-p{page_number}.png';im.save(png)
        sp=next(x for x in senate['pages'] if x['page']==page_number)
        assert len(sp['columns'])==11
        for name in NAMES:
            if name in PRES24:
                row=g['columns'][0]['fields'][name]['own_candidate_row_bounds']
                assert row is not None
                y0,y1=round(row[1]),round(row[3])
            else:
                row=sp['columns'][0]['candidate_bounds'][name]
                y0,y1=row[1],row[3]
            for col in range(1,12):
                bounds=sp['columns'][col-1]['header_bounds'];x0,x1=bounds[0],bounds[2]
                role='native_reporting_constituent' if page_number==2 or col==1 else 'source_TOTAL' if col==2 else 'unused_template_column'
                value=values[name][col-1] if role!='unused_template_column' else None
                rows.append(dict(source_id=SID,source_raw_sha256=receipt['raw_sha256'],source_page=page_number,source_column=col,candidate=name,role=role,label_literal=labels[col-1],source_cell_bounds=[x0,y0,x1,y1],direct_original_visual_value=value,original_page_render=str(png.relative_to(BASE)),original_page_render_sha256=sha(png.read_bytes())))
        pages.append(dict(page=page_number,render_size=list(im.size),rotation_ccw=g['rotation_ccw'],deskew_angle_ccw=g['deskew_angle_ccw'],render_path=str(png.relative_to(BASE)),render_sha256=sha(png.read_bytes()),labels_literal=labels,candidate_values=values,unused_template_columns=9 if page_number==3 else 0))
    checks={n:dict(native_sum=sum(V2[n])+V3[n][0],printed_TOTAL=V3[n][1],passes=sum(V2[n])+V3[n][0]==V3[n][1]) for n in NAMES}
    assert all(x['passes'] for x in checks.values()),checks
    assert len(rows)==242 and sum(x['direct_original_visual_value'] is None for x in rows)==99
    savejson(OUT/'winston-allfield-original-readings.json',dict(scope='Complete original PDF2/3 direct visual all11 transcript; 12 native columns, one source TOTAL, nine unused source template columns. Geometry-only row hint from independent peer; no peer numeric/label input.',source_id=SID,source_raw_sha256=receipt['raw_sha256'],geometry_hint_file_sha256=sha(peer.read_bytes()),pages=pages,candidate_checks=checks,rows=rows))
    with (OUT/'winston-allfield-original-cells.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Winston direct original allfield',len(rows),'positions,',len(rows)-99,'numeric, 99 unused null; all11 native sums close')

if __name__=='__main__':main()
