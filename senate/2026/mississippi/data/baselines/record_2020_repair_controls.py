"""Independent original whole-block2020 county TOTAL reading repairs.

Values are read from unaltered full original header/candidate blocks, never
selected from a CSV residual. A missing entry remains a pending visual reading.
"""
import csv,json
from PIL import Image
from sources import OUT,save,sha
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
# Reviewcard: (TOTAL physical column, three original printed candidate values).
VALUES={1:(9,[8190,5416,152]),2:(9,[7736,5416,152]),3:(11,[2750,4347,74]),4:(6,[1868,2320,92]),5:(6,[1868,2320,92]),6:(11,[2138,4341,112]),7:(5,[4134,3913,112]),8:(5,[4134,3913,112]),9:(2,[3053,5169,125]),10:(4,[6171,4006,109]),11:(4,[6171,4006,109]),12:(5,[3637,5604,131])}
VALUES.update({13:(9,[31115,43171,1768]),14:(2,[14871,16079,695]),15:(4,[1570,2833,54]),16:(1,[1844,8811,260]),17:(3,[1196,4395,129]),18:(3,[5120,5654,157]),20:(11,[30367,43180,2152]),21:(6,[367,309,5]),22:(7,[4556,4102,92]),23:(7,[4556,4102,92]),24:(2,[3428,476,12])})
VALUES.update({25:(7,[3758,2400,44]),26:(2,[3428,476,12]),27:(3,[2318,4222,57]),28:(3,[2318,4222,57]),29:(1,[4177,7821,187]),30:(3,[8590,6904,212]),31:(3,[8590,6904,212]),32:(11,[7953,7425,220]),33:(4,[9048,8044,257]),34:(5,[2714,7651,229]),35:(5,[2694,7603,227]),36:(2,[4649,5933,151])})
VALUES.update({37:(7,[7020,2623,42]),38:(10,[4694,8071,256]),39:(10,[2660,9572,424]),40:(9,[13155,4891,109]),41:(10,[2702,1295,80]),42:(2,[4303,4846,114]),43:(2,[5804,4551,79]),44:(6,[6798,1230,36]),45:(8,[10806,12127,432]),46:(11,[25374,30038,823]),47:(5,[1555,4204,142]),48:(7,[7020,2623,42]),49:(2,[3005,3415,88])})
VALUES[19]=(4,[5651,14537,573])
def main():
    pointers=json.loads((OUT/'source/2020-repair-block-pointers.json').read_text());expected={}
    for r in csv.DictReader((OUT/'candidate-votes.csv').open()):
        if r['contest']=='2020-senate':expected.setdefault(r['county'].lower().replace(' ','-'),{})[r['candidate_literal']]=int(r['votes'])
    rows=[];pending=[]
    for i,p in enumerate(pointers,1):
        if i==19:
            prior=p;p=dict(p)
            evidence=OUT/'qa/sos-2020-county-hancock-full-original-p4.png'
            p.update(page=4,render_size=list(Image.open(evidence).size),raster_path=str(evidence.relative_to(OUT.parents[1])),raster_sha256=sha(evidence.read_bytes()),original_header_box=[520,195,1540,390],original_candidate_block_box=[105,910,1540,1095],fresh_original_candidate_label_anchors=[],rejected_discovery_proposal=prior,qualification='Complete original PDF4 independently rendered/read; discovery PDF3 has no TOTAL and is retained as rejected proposal, not accepted geography or zero.')
        if i not in VALUES:pending.append(p|dict(reason='Original displayed header has11native constituents and noTOTAL; later original page required' if i==19 else 'Not yet visually reviewed'));continue
        col,vs=VALUES[i];label=p['source_id'].removeprefix('sos-2020-county-').removesuffix('-amended');label='jeff-davis' if label=='jefferson-davis' else label;ex=expected[label];evidence=OUT/'qa'/f'2020-repair-whole-blocks-{(i-1)//4+1}.png';values=dict(zip(NAMES,vs));rows.append(p|dict(source_column_accepted=col,candidate_values=values,reading_basis='Independent full original native header and three Senate rows visually read; TOTAL ordinal counted from complete displayed source header, not prior machine grid',evidence_path=str(evidence.relative_to(OUT)),evidence_sha256=sha(evidence.read_bytes()),county_csv_control=ex,county_csv_difference={n:values[n]-ex[n] for n in NAMES}))
        if i==19:
            evidence=OUT/'qa/sos-2020-county-hancock-full-original-p4.png';rows[-1].update(evidence_path=str(evidence.relative_to(OUT)),evidence_sha256=sha(evidence.read_bytes()))
    save(OUT/'county-2020-repair-readings.json',dict(qualification='Bounded original repairs to failed/cropped/wrong-block machine aids. All49 repair publications now have original-read three-candidate county TOTALs. Original/unamended and Amended publications remain separate. This is not full-native acceptance, chronology or residual fitting.',readings=rows,pending_whole_original_review=pending,numeric_source_views=len(rows),candidate_fields=3*len(rows),source_vintage_candidate_differences=[dict(source_id=r['source_id'],differences=r['county_csv_difference']) for r in rows if any(r['county_csv_difference'].values())],correction_history=[dict(source_id='sos-2020-county-amite',page=3,candidate='Mike Espy',prior_manual_value=2730,corrected_value=2750,basis='Initial whole-block atlas clipped top of digit5; complete expanded unaltered originalTOTAL clearly2750',evidence='qa/amite-2020-original-TOTAL-expanded.png')]))
    print(len(rows),'wholeoriginalcounty-vintageSenatecontrols; pending',len(pending))
    for r in rows:
        if any(r['county_csv_difference'].values()):print(r['source_id'],r['county_csv_difference'])
if __name__=='__main__':main()
