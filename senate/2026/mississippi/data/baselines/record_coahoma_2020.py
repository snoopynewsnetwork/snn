"""Independent complete original2020 Coahoma Senate native readings, both vintages.

All four complete ORIGINAL p2/3 images visually read. Candidate and native labels
are typed below from originals; vote values never come from a residual or peer.
Machine grids miss/merge printed columns; all18 real columns and TOTALc8 are
therefore source-bound explicitly. Original aids remain unchanged.
"""
import gzip,json
from sources import OUT,original,sha,save,references
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
LABELS={2:['Bobo','Cagle Crossing','Clarksdale\nCourthouse','Clarksdale #2','Clarksdale #3','Clarksdale #4','Clarksdale #4 North','Clarksdale #5','Coahoma','Dublin','Farrell'],3:['Friars Point','Jonestown','Lula','Lyon','Rena Lara','Roundaway','Sasse Street Fire\nStation','TOTAL','','','']}
VALUES={
'sos-2020-county-coahoma':{2:[[86,23,419,730,398,1082,110,1114,193,85,137],[33,33,202,488,63,47,61,159,9,80,27],[2,0,5,3,3,7,1,14,0,0,1]],3:[[458,557,133,373,43,46,465,6452],[35,11,125,582,168,27,11,2161],[0,0,2,4,1,0,3,46]]},
'sos-2020-county-coahoma-amended':{2:[[86,22,419,730,383,1056,106,1065,193,83,137],[33,33,202,488,58,46,55,150,9,77,27],[2,0,5,3,3,7,1,14,0,0,1]],3:[[458,557,133,371,43,46,449,6337],[35,11,125,582,167,27,8,2133],[0,0,2,4,1,0,3,46]]}}
# Source-bound physical rules independently located from full original images;
# these restore merged v4 cells and exclude outer scanned-page edges.
GRIDS={('sos-2020-county-coahoma',2):[734,852,971,1089,1208,1326,1444,1562,1680,1798,1915,2033],('sos-2020-county-coahoma',3):[692,810,928,1047,1165,1284,1402,1520,1638,1756,1872,1990],('sos-2020-county-coahoma-amended',2):[733,851,970,1088,1206,1324,1442,1561,1678,1794,1912,2030],('sos-2020-county-coahoma-amended',3):[726,845,964,1082,1200,1318,1436,1555,1671,1789,1906,2024]}
def main():
    sources=[]
    for key,vs in VALUES.items():
        pages=[];checks=[]
        for pg in [2,3]:
            old=json.loads(gzip.decompress((OUT/'extracts/native-v4'/key/f'p{pg:04d}.json.gz').read_bytes()));xs=GRIDS[(key,pg)];columns=[dict(source_column=i+1,label_literal=LABELS[pg][i],role='source_TOTAL' if pg==3 and i==7 else 'unused_template_column' if pg==3 and i>7 else 'source_native_reporting_constituent',x_bounds=[a,b],header_bounds=[a,267,b,494]) for i,(a,b) in enumerate(zip(xs,xs[1:]))];fields=[]
            for name,vals in zip(NAMES,vs[pg]):
                ff=next(f for f in old['fields'] if f['field']==name);fields.append(dict(candidate=name,source_row=ff['source_row'],row_bounds=ff['row_bounds'],values=vals+[None]*(11-len(vals))))
            evidence=OUT/'qa'/f'{key}-full-original-p{pg}.png';pages.append(dict(page=pg,render_size=old['render_size'],rotation_ccw=old['rotation_ccw'],deskew_angle_ccw=old['deskew_angle_ccw'],columns=columns,fields=fields,evidence_path=str(evidence.relative_to(OUT)),evidence_sha256=sha(evidence.read_bytes()),evidence_scale=2.1,coordinate_scale=2.7,position_qualification='Physical rules manually restored from complete original view; boxes are reading positions, no geographic geometry. Source render transform retained; original page3 TOTAL is physical column8 in BOTH vintages.'))
        for i,n in enumerate(NAMES):
            total=sum(vs[2][i])+sum(vs[3][i][:7]);printed=vs[3][i][7];assert total==printed,(key,n,total,printed);checks.append(dict(candidate=n,component_sum=total,printed_TOTAL=printed,difference=0))
        sources.append(dict(source_id=key,raw_sha256=sha(original(key)),county_fips='28027',source_url=references()[key]['url'],pages=pages,checks=checks,native_constituents=18,qualification='Only three2020 Senate candidates transcribed here. Complete original bytes retain all other offices and nine presidential candidates. Generic/write-in not printed in these selected Senate grids is absent-not-zero.'))
    delta={n:VALUES['sos-2020-county-coahoma-amended'][3][i][7]-VALUES['sos-2020-county-coahoma'][3][i][7] for i,n in enumerate(NAMES)};assert delta=={'Mike Espy':-115,'Cindy Hyde-Smith':-28,'Jimmy L. Edwards':0}
    save(OUT/'coahoma-2020-amendment-readings.json',dict(qualification='Independent complete original p2/3 visual reading of both official county-index vintages. Explicit primary county replacement vector equals the statewide original/amended Senate vector; not a residual allocation and not proof no other county/office changed. All104 original/amended county source reconciliation and statewide native gate remain open; publication/certification chronology not inferred.',sources=sources,candidate_delta_amended_minus_original=delta,total_delta=sum(delta.values()),county_csv_matches_amended=True,metadata_correction_history=[dict(source_id='sos-2020-county-coahoma',page=3,prior_machine_TOTAL_source_column=7,corrected_printed_TOTAL_source_column=8,basis='Complete original page visibly prints7constituent columns thenTOTAL; old machine grid merged Lyon/RenaLara. Old aid unchanged.')]))
    print('Coahoma2020both18-native vectors close; explicitprimaryamendmentdelta',delta)
if __name__=='__main__':main()
