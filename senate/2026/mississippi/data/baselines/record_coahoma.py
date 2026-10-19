"""Reproduce the independently read Coahoma Updated physical-grid repair.

Values below were read from the complete original pages, not a peer ledger.
The old v4 machine evidence remains immutable. Columns use all printed bounds,
including TOTAL and unused positions; blank unused positions remain null.
"""
import gzip,json
from sources import *
def main():
    key='sos-2024-county-coahoma-updated'
    names=['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump','Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski','Ty Pinkins','Roger F. Wicker']
    labels={2:['Bobo','Cagle Crossing','Clarksdale Courthouse','Clarksdale #2','Clarksdale #3','Clarksdale #4','Clarksdale #4 North','Clarksdale #5','Coahoma','Dublin','Farrell'],3:['Friars Point','Jonestown','Lula','Lyon','Rena Lara','Roundaway','Sasse Street Fire Station','TOTAL','','','']}
    values={2:[[64,18,314,532,297,864,83,787,143,55,93],[0,0,0,0,1,1,0,1,1,0,1],[0,0,0,2,0,0,0,0,0,0,0],[0,0,0,2,0,0,0,0,0,0,0],[36,28,180,422,61,55,45,137,25,66,32],[0,0,1,0,1,0,0,1,0,0,0],[0,0,2,1,1,0,0,2,0,0,0],[1,0,1,7,6,6,0,4,1,2,1],[0,0,1,0,0,0,0,1,0,0,0],[61,18,299,515,284,838,76,743,138,55,88],[41,29,188,438,67,73,50,166,30,66,39]],3:[[289,397,94,266,30,32,353,4711],[0,0,0,2,0,0,0,7],[0,1,0,2,0,0,0,5],[0,0,0,0,3,0,1,6],[39,23,115,558,144,27,15,2008],[1,0,0,1,0,0,0,5],[1,0,0,0,0,0,0,7],[3,2,1,3,0,0,1,39],[0,0,0,0,0,0,0,2],[277,389,96,254,32,26,344,4533],[49,33,112,574,143,29,19,2146]]}
    pages=[]
    for pg in [2,3]:
        x=json.loads(gzip.decompress((OUT/'extracts/native-v4'/key/f'p{pg:04d}.json.gz').read_bytes()))
        # Physical original lines, including the boundary omitted by v4's split.
        xs=x['grid_x'][1:];assert len(xs)==12
        cols=[]
        for i,(left,right) in enumerate(zip(xs,xs[1:])):
            cols.append(dict(source_column=i+1,native_label_literal=labels[pg][i],unit_type='summary_TOTAL' if pg==3 and i==7 else 'unused' if pg==3 and i>7 else 'source_native_constituent',x_bounds=[left,right]))
        fields=[]
        for name,vs in zip(names,values[pg]):
            old=next(f for f in x['fields'] if f['field']==name)
            fields.append(dict(field=name,source_row=old['source_row'],row_bounds=old['row_bounds'],values=vs+[None]*(11-len(vs))))
        pages.append(dict(page=pg,render_size=x['render_size'],rotation_ccw=x['rotation_ccw'],deskew_angle_ccw=x['deskew_angle_ccw'],columns=cols,fields=fields,evidence=f'qa/coahoma-updated-full-original-p{pg}.png'))
    checks=[]
    for j,name in enumerate(names):
        a=sum(values[2][j])+sum(values[3][j][:7]);b=values[3][j][7];assert a==b,(name,a,b)
        checks.append(dict(candidate=name,component_sum=a,printed_TOTAL=b,difference=0))
    save(OUT/'coahoma-updated-readings.json',dict(source_id=key,raw_sha256=sha(original(key)),fips='28027',scope='2024 updated source only; 18 printed constituents, TOTAL excluded; three unused columns retained as null. No current geography claim.',basis='Complete original p2/3 independently visually read; v4 omitted first physical column at x642/x641. Raw v4 retained unchanged. Column ordinals cannot be joined without physical bounds.',pages=pages,checks=checks))
    print('Coahoma Updated: 18 constituents, all 11 named candidate sums equal printed TOTAL')
if __name__=='__main__':main()
