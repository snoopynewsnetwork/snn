"""Independent original-cell2020 county Senate TOTAL readings, bounded progress.

Only rows whose original candidate labels and complete TOTAL digits were read
are entered. Wrong-block/cropped cards remain explicit repair gaps. Proposed
column ordinals are NOT accepted without full physical-column page review.
"""
import csv,json
from sources import OUT,BASE,save,sha,original
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
VALUES={1:[3641,11616,378],2:[3824,4888,108],3:[9330,4317,102],4:[1923,3716,84],5:[1320,2811,78],6:[1320,2811,78],7:[3907,555,26],8:[6337,2133,46],9:[6452,2161,46],10:[6730,6062,118],11:[3637,5604,131],12:[75467,23661,910],14:[3135,1023,29],15:[3135,1023,29],16:[1680,8818,251],17:[19334,33608,1325],18:[3758,2400,44],19:[9422,19917,641],20:[2965,1720,40],21:[10806,12127,432],23:[8157,19588,693],24:[13537,17082,501],25:[4123,4991,92],26:[13372,22739,745],27:[7936,2914,57],28:[5256,11378,168],29:[13843,13010,369],31:[4177,7821,187],32:[6441,10516,314],33:[2264,2738,86],34:[3602,7797,234],35:[3290,6659,176],36:[4138,1178,21],37:[10870,8592,313],38:[5053,17814,780],40:[3164,10803,337],41:[2307,883,48],42:[20315,48502,1664],43:[1511,663,7],44:[1511,663,7],45:[4303,7381,138],46:[1977,6202,130],47:[2051,5609,198],49:[3316,2309,64],50:[2432,7394,208],51:[2432,7394,208],52:[1594,7216,256],53:[2717,814,42],54:[2993,4005,86],55:[10853,9912,246],56:[10853,9912,246],57:[13155,4891,109],58:[3954,5984,144],59:[1198,4067,113],60:[3005,3415,88]}
REJECT={13:'Source label crops are2020 presidential candidates JoJorgensen/BrockPierce/KanyeWest, not Senate; adjacent-row proposal rejected',22:'Source crops are President heading/Biden/Trump, not Senate; adjacent-row proposal rejected',30:'Source labels are presidential candidates JoJorgensen/BrockPierce/KanyeWest; Senate proposal rejected',39:'Source labels are presidential candidates, not Senate; row proposal rejected',48:'Rightmost TOTAL digits clipped in this reading aid; full original required',61:'Rightmost TOTAL digits clipped in this reading aid; full original required'}
MERGED={2,23,36,42,54}
def main():
    pointers=json.loads((OUT/'source/2020-control-review-pointers.json').read_text());assert len(pointers)==61;readings=[];gaps=[];expected={}
    for r in csv.DictReader((OUT/'candidate-votes.csv').open()):
        if r['contest']=='2020-senate':expected.setdefault(r['county'].lower().replace(' ','-'),{})[r['candidate_literal']]=int(r['votes'])
    for i,p in enumerate(pointers,1):
        if i not in VALUES:gaps.append(p|dict(accepted_candidate_values=None,reason=REJECT[i]));continue
        key=p['source_id'];assert sha(original(key))==p['raw_sha256'];label=key.removeprefix('sos-2020-county-').removesuffix('-amended');label='jeff-davis' if label=='jefferson-davis' else label;ex=expected[label];vals=dict(zip(NAMES,VALUES[i]));evidence=OUT/'qa'/f'2020-controls-original-{(i-1)//10+1}.png';rec={k:v for k,v in p.items() if k!='source_column'};rec.update(candidate_values=vals,source_column_proposed=p['source_column'],source_column_accepted=8 if key in ['sos-2020-county-coahoma','sos-2020-county-coahoma-amended'] else None,source_column_scope='Coahoma accepted from complete original fullpage; others are targeting proposals pending full physical-column review',evidence_path=str(evidence.relative_to(OUT)),evidence_sha256=sha(evidence.read_bytes()),basis='Independent visual reading of complete original candidate labels and TOTAL digits from original-only cards; no county/state residual allocation',geometry_qualification='Reading crop spans adjacent native and TOTAL columns; right-hand TOTAL digits independently read, exact physical TOTAL ordinal pending' if i in MERGED else 'Complete numeric source cells; full-page native/column ordinal review still separate',county_csv_control=ex,county_csv_difference={n:vals[n]-ex[n] for n in NAMES})
        readings.append(rec)
    save(OUT/'county-2020-readings.json',dict(qualification='Bounded progress, not all82counties/104publications. Accepted numeric candidate readings and unaccepted machine column ordinals remain separate. All originals/pages and failed reading aids unchanged. Source-vintage differences retained; missing is not zero.',readings=readings,reading_card_repair_gaps=gaps,other_packet_gaps=json.loads((OUT/'source/2020-control-review-gaps.json').read_text()),source_vintage_candidate_differences=[dict(source_id=r['source_id'],differences=r['county_csv_difference']) for r in readings if any(r['county_csv_difference'].values())],numeric_source_views=len(readings),numeric_candidate_fields=3*len(readings),county_native_complete=False))
    print(len(readings),'source-vintage numeric controls;',len(gaps),'rejected/pending cards; additional43packet repairs')
    for r in readings:
        if any(r['county_csv_difference'].values()):print(r['source_id'],r['county_csv_difference'])
if __name__=='__main__':main()
