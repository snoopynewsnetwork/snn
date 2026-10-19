"""Direct original-image readings of25 Pike original-publication profiles.

Every count is typed from the complete office/profile reading panels. Fresh
original OCR supplies row targeting/literals only, never accepted vote values.
"""
import csv,gzip,io,json,re
from collections import defaultdict
from acquire_sources import BASE,OUT,receipts,savejson,sha
from read_physical_native import PRES24

# page,printed label,registration/ballots/blank/printed turnout,
# canonical ninePres + generic/TotalVotesCast/ContestTotals;
# Pinkins/Wicker/generic/TotalVotesCast/ContestTotals
READINGS=[
 (15,'(01) New Hope Baptist Church',[1053,456,0,43.30],[420,0,0,1,28,1,0,2,0,0,452,456],[394,45,1,440,456]),
 (17,'(02) S MCCOMB BAPTIST CHURCH',[551,203,0,36.84],[165,0,1,0,34,0,0,1,0,0,201,203],[160,40,0,200,203]),
 (19,'(03) Summit United Methodist Church',[580,307,0,52.93],[216,0,1,0,85,0,0,0,0,1,303,307],[214,87,2,303,307]),
 (21,'(04) Mlk Center',[982,433,0,44.09],[402,0,2,0,21,0,1,2,0,2,430,433],[383,28,1,412,433]),
 (23,'(05) North McComb Baptist Church',[876,463,0,52.85],[219,2,0,0,227,2,1,5,1,6,463,463],[216,236,1,453,463]),
 (25,'(06) Presley Event Center',[493,194,0,39.35],[178,0,0,0,14,0,0,0,0,1,193,194],[173,17,1,191,194]),
 (26,'(07) St Mary Free Will Bapt. Ch.',[942,458,0,48.62],[358,0,0,0,94,1,0,0,0,1,454,458],[338,103,0,441,458]),
 (28,'(08) Fernwood Baptist Church',[1134,533,0,47.00],[360,0,0,1,166,0,0,4,1,0,532,533],[345,184,1,530,533]),
 (29,'(09) Magnolia Comm Ctr.',[1175,521,0,44.34],[356,1,0,0,151,0,0,2,1,1,512,521],[348,164,3,515,521]),
 (30,'(10) Braswell Education Complex',[1381,633,0,45.84],[346,1,1,1,264,0,1,2,0,2,618,633],[347,270,4,621,633]),
 (32,'(11) St. James Miss. Bapt. Church',[633,278,0,43.92],[165,0,0,0,108,0,0,1,0,0,274,278],[162,111,0,273,278]),
 (34,'(12) Navilla Baptist Church Fellowship Hall',[1465,760,0,51.88],[307,1,1,1,439,1,0,6,1,0,757,760],[308,445,2,755,760]),
 (36,'(13) Holmesville Comm.',[975,533,0,54.67],[212,1,1,0,314,0,0,2,2,0,532,533],[203,328,1,532,533]),
 (38,'(14) Calvary Baptist Church',[958,606,0,63.26],[158,1,0,2,440,1,0,0,0,2,604,606],[154,446,1,601,606]),
 (40,'(15) Friendship Bapt. Church',[896,541,0,60.38],[93,1,2,1,435,1,0,5,0,1,539,541],[91,447,1,539,541]),
 (42,'(16) Summit City Hall',[531,304,0,57.25],[178,1,0,0,119,0,0,2,0,0,300,304],[167,124,1,292,304]),
 (43,'(17) SMCC Work Force Training Ctr',[1465,920,0,62.80],[258,1,0,0,654,0,0,4,0,2,919,920],[242,671,2,915,920]),
 (44,'(18) Johnston Chapel Meth. Church',[1336,884,0,66.17],[103,3,2,1,773,1,0,0,0,1,884,884],[112,766,0,878,884]),
 (45,'(19) Pisgah Methodist Church',[1163,705,0,60.62],[150,1,1,0,549,0,0,1,0,1,703,705],[138,561,0,699,705]),
 (46,'(20) Pike Co. Nat. Bank',[810,407,0,50.25],[241,0,1,0,160,1,0,2,0,1,406,407],[227,171,3,401,407]),
 (47,'(21) Old Progress Volunteer Fire Station',[1435,676,0,47.11],[348,1,1,1,316,0,2,3,0,2,674,676],[332,334,2,668,676]),
 (49,'(22) Church of Christ',[1164,621,1,53.35],[384,0,1,1,222,0,1,3,1,3,616,621],[376,236,2,614,621]),
 (51,'(23) West McComb Bapt. Church',[915,467,0,51.04],[174,0,0,1,288,0,0,1,0,1,465,467],[171,292,1,464,467]),
 (53,'(24) Our Lady of Hope',[1277,629,0,49.26],[216,2,0,0,402,0,0,4,1,3,628,629],[218,405,0,623,629]),
 (55,'(25) Osyka City Hall',[502,292,0,58.17],[84,0,0,0,201,0,1,0,1,0,287,292],[79,208,0,287,292]),
]
ALIASES=dict(zip(PRES24,['harris','chase','stein','randall','donald','shiva','claudia','kennedy','sonsk']))|{'Ty Pinkins':'pinkins','Roger F. Wicker':'wicker'}

def rawlines(page):
 p=OUT/f'qa/pike-profiles/original-crop-p{page}.tsv.gz';g=defaultdict(list)
 for r in csv.DictReader(io.StringIO(gzip.decompress(p.read_bytes()).decode()),delimiter='\t'):
  if r['text'].strip():g[r['block_num'],r['par_num'],r['line_num']].append(r)
 return [dict(text=' '.join(r['text'] for r in rr),bounds=[min(int(r['left']) for r in rr)+50,min(int(r['top']) for r in rr)+250,max(int(r['left'])+int(r['width']) for r in rr)+50,max(int(r['top'])+int(r['height']) for r in rr)+250],words=rr) for rr in g.values()]

def main():
 sid='sos-2024-county-pike';r=next(r for r in receipts if r['id']==sid);profiles=[];gaps=[]
 names=PRES24+['president_generic_write_in','president_total_votes_cast','president_contest_total','Ty Pinkins','Roger F. Wicker','senate_generic_write_in','senate_total_votes_cast','senate_contest_total','registration_total','ballots_cast_total','ballots_blank','voter_turnout_percent']
 inventory=json.loads((OUT/'qa/pike-profiles/page-inventory.json').read_text());assert [x[0] for x in READINGS]==inventory['proposed_profile_starts']
 for page,label,statistics,pres,sen in READINGS:
  ll=rawlines(page);pi=next(i for i,l in enumerate(ll) if 'president' in l['text'].lower());si=next(i for i,l in enumerate(ll) if 'senate' in l['text'].lower());sections={'president':ll[pi:si],'senate':ll[si:],'statistics':ll[:pi]};fields={}
  for n,v in zip(names,pres+sen+statistics):
   office='statistics' if n in names[-4:] else 'senate' if n in ['Ty Pinkins','Roger F. Wicker'] or n.startswith('senate_') else 'president';rows=sections[office]
   if n in ALIASES:matches=[l for l in rows if ALIASES[n] in l['text'].lower().replace('plnkins','pinkins') or n=='Kamala D. Harris' and 'haris' in l['text'].lower()]
   else:
    pattern='ite-in tot' if n.endswith('_generic_write_in') else 'total votes cast' if n.endswith('_total_votes_cast') else 'contest tota' if n.endswith('_contest_total') else 'registered voters' if n=='registration_total' else 'ballots cast - total' if n=='ballots_cast_total' else 'ballots cast - blank' if n=='ballots_blank' else None
    matches=[l for l in rows if pattern in l['text'].lower() or n.endswith('_generic_write_in') and 'write-n tot' in l['text'].lower()] if pattern is not None else [l for l in rows if re.match(r'^vot[ea]r\s+t',l['text'].lower())]
   exact=len(matches)==1;bound=matches[0]['bounds'] if exact else [50,250,1050,1790];literal=matches[0]['text'] if exact else None
   if not exact:gaps.append(dict(page=page,field=n,position_precision='Complete original profile block only; fresh OCR row targeting unavailable/ambiguous',matches=len(matches)))
   fields[n]=dict(value=v,literal=None,bounds=bound,raw_OCR_row_literal=literal,raw_OCR_row_records=matches,position_precision='Original full-row OCR targeting; manually read complete original profile' if exact else 'Original whole-profile bounds; no exact row targeting claimed',reading_basis='Direct unaltered original image, typed all required numeric fields; raw OCR only aids row targeting')
  if page==49:fields['Peter Sonski']['correction_history']=[dict(prior_manual_value=0,accepted_original_visual_value=1,basis='Reopened complete unaltered original PDF49, clearly printed Peter Sonsk row1. Initial panel transcription omitted this nonzero row; no residual allocation.',evidence='data/turnout/qa/pike-profiles/original-p49.png')]
  pointer=json.loads((OUT/f'qa/pike-profiles/original-p{page}-pointer.json').read_text());code=re.match(r'\((\d+)\)',label)[1]
  profile=dict(key=f'28113:{sid}:p{page}:profile',source_id=sid,source_raw_sha256=r['raw_sha256'],source_page=page,county_fips='28113',native_label_literal=label,printed_native_id=code,printed_native_id_scope='Printed Pike original ES&S precinct code, source view only. No source-vintage, SEMS or current/crossyear join established.',role='native_vendor_profile_source_view',method_literal='TOTAL',fields=fields,coordinate_system='Original fitz3.5 gray render pixels; full source OCR-row bounds or explicit complete profile block fallback',render_size=pointer['render_size'],review_status='independent_original_visual_review_all_required_profile_fields',unprinted_fields={'under':None,'over':None,'method_breakdown':None},source_clock_literal=None,source_clock_context={'verified_source_pages':[15,55],'literal':'11/15/2024 3:07 PM','qualification':'Context from complete first/last original profiles, not independently read for every profile footer; timezone absent.'},source_status_context={'verified_source_pages':[15,55],'literal':'Certified Results'},original_visual_evidence=pointer,source_OCR_rows=ll)
  profile['candidate_identity_mapping']=dict(president=dict(zip(PRES24,['D Kamala D. Harris / Tim Walz','L Chase Oliver / Mike ter Maat','G Jill Stein / Rudolph Ware','C Randall Terry / Stephen E. Broden','R Donald J. Trump / JD Vance','I Shiva Ayyadurai / Crystal Ellis','I Claudia De la Cruz / Karina Garcia','I Robert F. Kennedy Jr. / Nicole','I Peter Sonsk / Lauren Onak'])),senate={'Ty Pinkins':'D Ty Pinkins','Roger F. Wicker':'R Roger F. Wicker'})
  profile['candidate_identity_qualification']='Canonical named identities map to printed office/ticket rows, retaining printed party and truncated ticket literal separately. Source sorts candidate rows by vote count within each profile; canonical vector order is not a source-row ordinal. No named write-in adjudication is inferred.'
  profile['unallocated_contest_residuals']={office:fields[office+'_contest_total']['value']-sum(fields[n]['value'] for n in nn)-fields[office+'_generic_write_in']['value'] for office,nn in [('president',PRES24),('senate',['Ty Pinkins','Roger F. Wicker'])]}
  for office,nn in [('president',PRES24),('senate',['Ty Pinkins','Roger F. Wicker'])]:assert fields[office+'_total_votes_cast']['value']==sum(fields[n]['value'] for n in nn)+fields[office+'_generic_write_in']['value'],(page,office)
  profiles.append(profile)
 sums={n:sum(p['fields'][n]['value'] for p in profiles) for n in names if n!='voter_turnout_percent'}
 savejson(OUT/'native-profile-pike-readings.json',dict(source_id=sid,raw_sha256=r['raw_sha256'],profiles=profiles,field_sums=sums,source_position_qualifications=gaps,qualification='All25 original Pike ES&S profiles, actual variable-length section PDF15–56. Original vintage only; updated county total and all native/current source identities remain distinct. Full source percentages/party/ticket labels retained in original bytes/renders and fresh raw OCR; numerical extraction scope is candidate/generic/contest/statistics fields. Under/over not printed; contest residuals unallocated. Initial21 alternating-page discovery rejected before any accepted extraction.'))
 print('25 direct-original Pike profiles;',len(names)*len(profiles),'numeric fields;',len(gaps),'explicit source-row targeting gaps');print(json.dumps(sums))

if __name__=='__main__':main()
