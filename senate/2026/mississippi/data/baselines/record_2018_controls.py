"""Record independent visual original-label/TOTAL readings, with source boxes."""
from sources import *
SPECIAL='''adams,200,5947,3406,1273
alcorn,113,2039,5795,2052
amite,114,1873,2098,1201
attala,78,2524,2733,970
benton,59,1082,1142,458
calhoun,60,1382,2427,772
chickasaw,71,2725,2261,947
clarke,877,1387,2386,1446
clay,148,4223,2652,674
coahoma,74,4576,1509,468
copiah,160,5230,4336,799
covington,84,2557,2502,1825
forrest,419,9725,8272,4434
franklin,47,1084,1542,550
george,139,1001,2973,2866
grenada,101,3394,3199,1027
hancock,290,3256,6918,3063
harrison,741,18710,24784,7255
hinds,648,57514,17244,3960
issaquena,5,305,217,33
itawamba,59,953,4049,1766
jackson,787,12460,19294,6895
jasper,168,3145,1468,1670
jefferson-davis,73,2830,1467,515
jones,216,6279,4843,11027
kemper,93,1853,1086,389
lamar,294,4486,10190,4909
lawrence,30,1741,3035,368
leake,64,2815,2748,934
lee,245,8164,12240,5068
leflore,185,5863,2199,493
lincoln,87,3604,7870,1068
madison,283,17125,19899,3494
marion,135,2788,4198,1811
marshall,234,5992,3533,1555
monroe,169,4080,5699,1863
montgomery,55,1582,1846,415
neshoba,96,2139,4308,1465
newton,103,2141,3285,1695
noxubee,103,2799,891,180
oktibbeha,249,7091,5543,1480
panola,198,5447,4022,1565
pearl-river,307,2831,6751,5532
perry,42,960,1803,1193
pike,223,5909,4887,1727
pontotoc,90,1925,4988,2683
prentiss,59,1703,4038,1441
rankin,393,13035,29055,9294
scott,76,3208,3517,1078
sharkey,19,1171,515,68
simpson,99,3097,4577,1257
smith,43,1370,2706,1905
stone,62,1230,2836,1239
sunflower,100,5090,1904,374
tallahatchie,61,2460,1395,387
tippah,89,1451,3926,1416
tishomingo,80,895,3529,1502
tunica,88,1725,586,143
union,67,1473,4738,2049
walthall,59,2006,2382,705
warren,182,7505,6159,1802
washington,197,9667,3577,593
wayne,222,2607,2576,1946
webster,42,756,2390,731
wilkinson,140,1597,600,406
winston,107,2996,3039,855
yalobusha,75,2028,2004,561
yazoo,44,3919,2925,626'''
RUNOFF='''adams,6488,4113
alcorn,2084,7120
amite,2099,2912
attala,2804,3473
benton,1224,1387
bolivar,7554,3331
calhoun,1515,3046
carroll,1427,2612
chickasaw,3210,2955
clarke,2156,3486
clay,4965,3036
coahoma,5111,1748
copiah,5891,4694
covington,2855,3828
desoto,17558,25326
forrest,10608,10933
franklin,1244,1957
george,889,4900
greene,661,2422
grenada,3543,3943
harrison,19339,28167
hinds,61892,18464
holmes,5814,974
humphreys,2696,851
issaquena,305,227
itawamba,930,5714
jackon,12821,23119
jasper,3680,2796
jefferson,2807,385
kemper,2207,1270
lafayette,7516,7702
lamar,4936,13200
lawrence,1915,3222
leake,3099,3534
madison,19407,23558
marion,3136,5496
marshall,6334,4462
monroe,4742,7127
montgomery,1709,2036
neshoba,2164,5222
newton,2298,4645
noxubee,3217,900
oktibbeha,7717,6028
panola,6077,4929
pearl-river,2830,10322
perry,1059,2754
pike,6677,5795
pontotoc,2062,7304
prentiss,1836,5206
quitman,1788,684
rankin,13826,34333
scott,3646,4429
simpson,3433,5404
smith,1496,4180
stone,1353,3724
sunflower,5301,2034
tallahatchie,2691,1691
tate,3223,4935
tippah,1562,4868
tishomingo,895,4552
tunica,1937,578
union,1604,6409
walthall,2329,2716
washington,9629,3583
wayne,3042,4036
wilkinson,1966,851
winston,3247,3559
yalobusha,2184,2281
yazoo,4607,3448''' 
FULL_PAGE_SPECIAL='''bolivar,4,7,119,7146,3066,731
carroll,3,4,41,1391,2157,737
choctaw,3,3,48,852,1550,573
claiborne,3,1,60,2756,472,115
desoto,5,9,673,16922,20634,11864
greene,3,3,64,729,1425,1438
holmes,3,6,76,4574,794,196
humphreys,3,3,48,2282,747,150
jefferson,3,2,62,2614,407,132
lafayette,3,8,241,7294,6858,1929
lauderdale,5,8,566,8273,10138,4116
lowndes,3,11,309,8981,8012,2487
quitman,2,11,55,1643,601,141
tate,3,10,170,2760,3622,2058'''
FULL_PAGE_RUNOFF='''choctaw,3,3,1000,1932
desoto,5,9,17558,25326
claiborne,3,3,3095,453
hancock,4,4,3051,8716
jefferson-davis,3,8,3205,1792
jones,5,5,6946,13420
lauderdale,5,8,9180,12224
lee,5,4,9453,16493
leflore,3,8,6234,2499
lincoln,4,9,4008,8536
lowndes,3,11,9786,9263
sharkey,2,11,1192,496
warren,4,2,7957,7082
webster,3,7,845,2937'''
def main():
 dest=OUT/'county-2018-readings.json';x=json.loads(dest.read_text()) if dest.exists() else dict(qualification='Independent visual reading of original candidate-label and printed TOTAL cells; no peer numeric import, allocation or rescaling. Missing counties/candidates remain missing until direct original review. Stage electorates never combined.',candidate_order={'special':['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],'runoff':['Mike Espy','Cindy Hyde-Smith']},readings=[])
 for stage,text in [('special',SPECIAL),('runoff',RUNOFF)]:
  pointers=json.loads((OUT/'source'/f'2018-{stage}-control-review-pointers.json').read_text());lookup={r['source_id']:r for r in pointers};prefix='sos-2018-'+('runoff-' if stage=='runoff' else '')+'county-'
  for line in text.splitlines():
   if not line.strip():continue
   county,*values=line.split(',');key=prefix+county;pointer=lookup[key];assert pointer['selected'] is not None,key
   r=dict(stage=stage,source_id=key,raw_sha256=sha(original(key)),candidate_values=dict(zip(x['candidate_order'][stage],map(int,values))),source_positions=pointer['selected'],evidence=f'qa/2018-{stage}-controls-original-{pointers.index(pointer)//10+1}.png',read_status='independent_visual_original_candidate_label_and_TOTAL')
   x['readings'][:]=[z for z in x['readings'] if z['source_id']!=key];x['readings'].append(r)
 for stage,text in [('special',FULL_PAGE_SPECIAL),('runoff',FULL_PAGE_RUNOFF)]:
  prefix='sos-2018-'+('runoff-' if stage=='runoff' else '')+'county-'
  for line in text.splitlines():
   if not line.strip():continue
   county,page,col,*values=line.split(',');key=prefix+county;evidence=f'qa/{key}-full-original-p{page}.png';assert (OUT/evidence).exists()
   r=dict(stage=stage,source_id=key,raw_sha256=sha(original(key)),candidate_values=dict(zip(x['candidate_order'][stage],map(int,values))),source_positions=dict(page=int(page),source_column=int(col),column_label_literal='TOTAL',candidate_order=x['candidate_order'][stage],qualification='Full original page visually read; machine grid not used as transcription authority.'),evidence=evidence,evidence_sha256=sha((OUT/evidence).read_bytes()),read_status='independent_visual_complete_original_page')
   x['readings'][:]=[z for z in x['readings'] if z['source_id']!=key];x['readings'].append(r)
 x['correction_history']=[dict(source_id='sos-2018-county-choctaw',stage='special',page=3,source_column=3,candidate='Cindy Hyde-Smith',prior_manual_value=1650,corrected_value=1550,evidence='qa/sos-2018-county-choctaw-TOTAL-magnified-p3.png',basis='Independently magnified original cell clearly1550; earlier manual digit reading error, not a source-vintage change.'),dict(source_id='sos-2018-county-quitman',stage='special',page=2,source_column=11,candidate='Mike Espy',prior_manual_value=1543,corrected_value=1643,evidence='qa/sos-2018-county-quitman-TOTAL-magnified-p2.png',basis='Independently magnified original cell clearly1643; earlier manual digit reading error, not a source-vintage change.')]
 # Later direct complete-original physical-grid review is distinct from the
 # immutable machine-derived locator proposal and earlier county TOTAL reading.
 nativepath=OUT/'native-2018-original-readings.json'
 if nativepath.exists():
  native=json.loads(nativepath.read_text());fix=next(r for r in native['sources'] if r['source_id']=='sos-2018-county-issaquena');r=next(r for r in x['readings'] if r['source_id']==fix['source_id']);prior=dict(r['source_positions']);assert prior['source_column']==4 and fix['physical_TOTAL_column']==6 and r['candidate_values']==fix['controls']['printed_TOTAL'] and r['raw_sha256']==fix['raw_sha256']
  r['source_positions']={**prior,'source_column':6,'source_column_scope':'Actual physical numeric column, independently counted on complete original; old merged-machine ordinal4 is preserved in history.'};r['physical_column_correction_history']=dict(prior_source_positions=prior,prior_ledger_pin='data/baselines/source/2018-physical-column-corrections-v1/prior-ledger-pin.json',actual_physical_source_column=6,native_original_evidence='data/baselines/native-2018-original-readings.json',basis='Complete originalPDF2 visibly five named precinct columns thenTOTAL. Grace/Mayersville/Tallula are distinct physical columns merged in old machine grid. Existing target box still pointsTOTAL; four candidate values unchanged. No native ID/cross-stage/current geometry inference.')
 save(dest,x);print(len(x['readings']),'independent county-stage readings')
 controls=json.loads((OUT/'source/primary-state-readings.json').read_text())
 for stage in ['special','runoff']:
  rr=[r for r in x['readings'] if r['stage']==stage];sums={n:sum(r['candidate_values'][n] for r in rr) for n in x['candidate_order'][stage]};print(stage,len(rr),sums,{n:sums[n]-controls['2018-'+stage]['candidates'][n] for n in sums})
if __name__=='__main__':main()
