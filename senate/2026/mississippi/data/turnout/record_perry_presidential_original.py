"""Visual transcript of every 2024 Perry original SEMS presidential cell.

All candidate vectors are typed from the full original PDF pages 2 and 3.
The preliminary machine aid missed page 3 rows below the office heading.
"""
import csv,gzip,io,json
import fitz
from PIL import Image
from acquire_sources import BASE,OUT,receipts,sha,savejson
from read_physical_native import PRES24

SID='sos-2024-county-perry'
LABELS2=['Arlington 4100','Beaumont District 1\n1030','Beaumont Voting\nPrecinct 5120',
         'Buck Creek 4110','Courthouse 5110','Deep Creek 5150','Hintonville 4090',
         'Indian Springs 1010','Janice 5140','McSwain Community\nCenter',
         'New Augusta\nCommunity Center']
LABELS3=['Prospect 2050','Richton Holly Street\n3060','Richton Multi Purpose\n4080',
         'Runnelstown 2040','Thompson Hill 5130','TOTAL']
V2={
 'Kamala D. Harris':[64,296,26,4,33,14,76,118,49,78,72],
 'Chase Oliver':[1,0,0,0,1,0,1,0,0,0,0],
 'Jill Stein':[1,2,0,0,1,0,1,0,0,0,0],
 'Randall Terry':[0,0,0,0,0,1,0,0,0,1,0],
 'Donald J. Trump':[407,97,107,118,181,68,196,247,483,33,82],
 'Shiva Ayyadurai':[0,0,0,0,0,0,0,0,0,0,0],
 'Claudia De la Cruz':[0,0,0,0,1,0,0,0,0,0,0],
 'Robert F. Kennedy Jr.':[1,0,1,0,1,0,0,1,1,1,0],
 'Peter Sonski':[0,0,0,0,0,0,0,0,0,0,0],
}
V3={
 'Kamala D. Harris':[11,109,76,48,4,1078],
 'Chase Oliver':[0,3,1,1,0,8],
 'Jill Stein':[0,1,1,1,0,8],
 'Randall Terry':[0,0,2,0,0,4],
 'Donald J. Trump':[155,1072,205,913,61,4425],
 'Shiva Ayyadurai':[0,2,1,1,0,4],
 'Claudia De la Cruz':[0,1,0,0,0,2],
 'Robert F. Kennedy Jr.':[0,0,2,1,0,9],
 'Peter Sonski':[0,0,1,0,0,1],
}

def main():
    assert list(V2)==list(V3)==PRES24
    assert all(len(x)==11 for x in V2.values()) and all(len(x)==6 for x in V3.values())
    receipt=next(x for x in receipts if x['id']==SID)
    raw=gzip.decompress((BASE/receipt['path']).read_bytes());assert sha(raw)==receipt['raw_sha256']
    doc=fitz.open(stream=raw,filetype='pdf')
    grid=json.loads(gzip.decompress((OUT/'extracts/physical-native-v3/sos-2024-county-perry.json.gz').read_bytes()))
    pages=[];rows=[]
    for page_number,values,labels in [(2,V2,LABELS2),(3,V3,LABELS3)]:
        pg=next(p for p in grid['pages'] if p['page']==page_number)
        im=Image.open(io.BytesIO(doc[page_number-1].get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png')))
        im=im.rotate(pg['rotation_ccw'],expand=True).rotate(pg['deskew_angle_ccw'],fillcolor=255)
        assert list(im.size)==pg['render_size']
        png=OUT/f'qa/perry-presidential-original-p{page_number}.png';im.save(png)
        xs=pg['physical_numeric_grid_x']
        # Page 3 rows below Harris were omitted from the provisional OCR aid.
        ys2=[(538,616),(616,686),(686,758),(758,830),(830,902),(902,974),
             (974,1046),(1046,1118),(1118,1190)]
        ys3=[(470,533),(533,610),(610,682),(682,754),(754,826),(826,898),
             (898,970),(970,1042),(1042,1114)]
        ys=ys2 if page_number==2 else ys3
        for i,name in enumerate(PRES24):
            y0,y1=ys[i]
            for source_col,value in enumerate(values[name],1):
                x0,x1=xs[source_col-1:source_col+1]
                role='source_TOTAL' if page_number==3 and source_col==6 else 'native_reporting_constituent'
                rows.append(dict(source_id=SID,source_raw_sha256=receipt['raw_sha256'],source_page=page_number,source_column=source_col,candidate=name,role=role,label_literal=labels[source_col-1],printed_candidate_order=i+1,original_cell_bounds=[x0,y0,x1,y1],direct_original_visual_value=value,original_page_render=str(png.relative_to(BASE)),original_page_render_sha256=sha(png.read_bytes())))
        pages.append(dict(page=page_number,render_size=list(im.size),rotation_ccw=pg['rotation_ccw'],deskew_angle_ccw=pg['deskew_angle_ccw'],render_path=str(png.relative_to(BASE)),render_sha256=sha(png.read_bytes()),labels_literal=labels,candidate_values=values,unused_template_columns=5 if page_number==3 else 0,manual_row_geometry_reason='Page 3 provisional machine candidate-row extraction omitted eight printed presidential rows.' if page_number==3 else None))
    checks={n:dict(native_sum=sum(V2[n])+sum(V3[n][:-1]),printed_TOTAL=V3[n][-1],passes=sum(V2[n])+sum(V3[n][:-1])==V3[n][-1]) for n in PRES24}
    assert all(x['passes'] for x in checks.values())
    savejson(OUT/'perry-presidential-original-readings.json',dict(scope='Full original PDF pages 2/3 nine-candidate direct visual transcription; all 16 native columns plus printed TOTAL. No cross-county allocation.',source_id=SID,source_raw_sha256=receipt['raw_sha256'],pages=pages,candidate_checks=checks,source_native_count=16,source_TOTAL_count=1,rows=rows))
    with (OUT/'perry-presidential-original-cells.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Perry direct original presidential rows',len(rows),'all nine sums close printed source TOTAL')

if __name__=='__main__':main()
