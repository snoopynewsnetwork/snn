"""Literal numeric transcription checked against complete rendered scan pages.

All numbers below were visually read from retained source images, not inferred
from residuals/OCR. PSM3/PSM6 OCR are separate reading aids. Original PDFs are
the authority. Zero is present only where visibly printed. No native crosswalk.
"""
from source_io import *
import collections

PRES=['Rep Trump/Vance','Dem Harris/Walz','Lib Oliver/ter Maat','Lmn West/Abdullah','Pet Stein/Kpadenou','Write-In Totals','Not Assigned','Total Votes Cast','Overvotes','Undervotes','Contest Totals']
REG=['Rep Deb Fischer','Pet Dan Osborn','Write-In Totals','Not Assigned','Total Votes Cast','Overvotes','Undervotes','Contest Totals']
SPECIAL=['Rep Pete Ricketts','Dem Preston Love Jr.','Write-In Totals','Not Assigned','Total Votes Cast','Overvotes','Undervotes','Contest Totals']
def matrix(s):return [[int(v)for v in row.split()]for row in s.split(';')]

# Every vector is in printed TOTAL / Election Day / Early Voting / Provisional order.
YORK=[
(1,'Stewart Thayer','338 253 84 1','0 0 0 0',
 '262 201 61 0;62 41 20 1;0 0 0 0;1 1 0 0;2 2 0 0;2 1 1 0;2 1 1 0;329 246 82 1;1 0 1 0;8 7 1 0;338 253 84 1',
 '237 178 59 0;95 69 25 1;0 0 0 0;0 0 0 0;332 247 84 1;0 0 0 0;6 6 0 0;338 253 84 1',
 '280 213 67 0;48 31 16 1;0 0 0 0;0 0 0 0;328 244 83 1;0 0 0 0;10 9 1 0;338 253 84 1'),
(9,'New York-Waco-Beaver-West Blue','578 406 171 1','0 0 0 0',
 '465 334 130 1;94 58 36 0;3 2 1 0;2 2 0 0;2 2 0 0;3 2 1 0;3 2 1 0;569 400 168 1;1 1 0 0;8 5 3 0;578 406 171 1',
 '408 284 123 1;153 111 42 0;4 3 1 0;4 3 1 0;565 398 166 1;0 0 0 0;13 8 5 0;578 406 171 1',
 '479 343 135 1;86 55 31 0;1 0 1 0;1 0 1 0;566 398 167 1;0 0 0 0;12 8 4 0;578 406 171 1'),
(18,'Hays McFadden','498 414 79 5','1 1 0 0',
 '394 325 64 5;90 76 14 0;2 2 0 0;1 1 0 0;1 1 0 0;1 1 0 0;1 1 0 0;489 406 78 5;1 1 0 0;8 7 1 0;498 414 79 5',
 '334 275 56 3;146 124 20 2;0 0 0 0;0 0 0 0;480 399 76 5;0 0 0 0;18 15 3 0;498 414 79 5',
 '397 330 64 3;83 68 14 1;0 0 0 0;0 0 0 0;480 398 78 4;1 1 0 0;17 15 1 1;498 414 79 5'),
(25,'Leroy-Baker','329 192 136 1','1 0 1 0',
 '262 152 109 1;53 32 21 0;5 4 1 0;1 1 0 0;1 1 0 0;1 0 1 0;1 0 1 0;323 190 132 1;1 0 1 0;5 2 3 0;329 192 136 1',
 '228 127 101 0;90 59 30 1;0 0 0 0;0 0 0 0;318 186 131 1;1 1 0 0;10 5 5 0;329 192 136 1',
 '275 163 111 1;45 26 19 0;0 0 0 0;0 0 0 0;320 189 130 1;0 0 0 0;9 3 6 0;329 192 136 1'),
(32,'MABL','688 429 253 6','0 0 0 0',
 '526 355 166 5;140 59 80 1;2 1 1 0;0 0 0 0;0 0 0 0;2 1 1 0;2 1 1 0;670 416 248 6;7 6 1 0;11 7 4 0;688 429 253 6',
 '467 306 159 2;208 114 90 4;1 1 0 0;1 1 0 0;676 421 249 6;0 0 0 0;12 8 4 0;688 429 253 6',
 '551 362 184 5;115 52 62 1;2 2 0 0;2 2 0 0;668 416 246 6;1 1 0 0;19 12 7 0;688 429 253 6'),
(41,'Brown-Henderson','936 631 301 4','0 0 0 0',
 '747 519 226 2;162 90 70 2;3 3 0 0;3 2 1 0;2 2 0 0;2 1 1 0;2 1 1 0;919 617 298 4;7 5 2 0;10 9 1 0;936 631 301 4',
 '712 485 225 2;197 124 71 2;3 3 0 0;3 3 0 0;912 612 296 4;0 0 0 0;24 19 5 0;936 631 301 4',
 '766 532 232 2;141 72 67 2;3 3 0 0;3 3 0 0;910 607 299 4;0 0 0 0;26 24 2 0;936 631 301 4'),
(50,'WARD 1','585 370 209 6','0 0 0 0',
 '435 275 154 6;130 82 48 0;5 3 2 0;3 3 0 0;4 3 1 0;1 1 0 0;1 1 0 0;578 367 205 6;3 0 3 0;4 3 1 0;585 370 209 6',
 '393 239 148 6;182 124 58 0;1 1 0 0;1 1 0 0;576 364 206 6;0 0 0 0;9 6 3 0;585 370 209 6',
 '454 286 163 5;113 75 37 1;1 1 0 0;1 1 0 0;568 362 200 6;1 0 1 0;16 8 8 0;585 370 209 6'),
(57,'WARD 2A','602 386 211 5','0 0 0 0',
 '404 265 136 3;183 108 73 2;6 5 1 0;4 3 1 0;1 1 0 0;0 0 0 0;0 0 0 0;598 382 211 5;4 4 0 0;0 0 0 0;602 386 211 5',
 '330 199 129 2;260 177 80 3;3 3 0 0;3 3 0 0;593 379 209 5;0 0 0 0;9 7 2 0;602 386 211 5',
 '403 266 134 3;175 108 65 2;2 2 0 0;2 2 0 0;580 376 199 5;0 0 0 0;22 10 12 0;602 386 211 5'),
(63,'WARD 2B','552 375 173 4','0 0 0 0',
 '376 268 106 2;150 90 58 2;6 4 2 0;2 2 0 0;2 1 1 0;6 2 4 0;6 2 4 0;542 367 171 4;4 4 0 0;6 4 2 0;552 375 173 4',
 '285 191 92 2;248 172 74 2;4 2 2 0;4 2 2 0;537 365 168 4;0 0 0 0;15 10 5 0;552 375 173 4',
 '388 271 115 2;143 90 51 2;0 0 0 0;0 0 0 0;531 361 166 4;0 0 0 0;21 14 7 0;552 375 173 4'),
(69,'WARD 3','512 317 189 6','0 0 0 0',
 '331 223 103 5;164 85 78 1;0 0 0 0;0 0 0 0;1 0 1 0;3 1 2 0;3 1 2 0;499 309 184 6;3 3 0 0;10 5 5 0;512 317 189 6',
 '281 176 101 4;215 126 87 2;0 0 0 0;0 0 0 0;496 302 188 6;0 0 0 0;16 15 1 0;512 317 189 6',
 '353 235 113 5;142 69 72 1;0 0 0 0;0 0 0 0;495 304 185 6;0 0 0 0;17 13 4 0;512 317 189 6'),
(75,'WARD 4A','830 520 307 3','0 0 0 0',
 '544 356 186 2;235 129 105 1;14 10 4 0;4 4 0 0;5 4 1 0;11 7 4 0;11 7 4 0;813 510 300 3;2 1 1 0;15 9 6 0;830 520 307 3',
 '510 325 185 0;287 172 113 2;1 1 0 0;1 1 0 0;798 498 298 2;1 1 0 0;31 21 9 1;830 520 307 3',
 '600 389 208 3;199 111 88 0;2 1 1 0;2 1 1 0;801 501 297 3;0 0 0 0;29 19 10 0;830 520 307 3'),
(82,'WARD 4B','705 476 224 5','0 0 0 0',
 '488 348 136 4;184 112 72 0;9 4 5 0;3 2 1 0;2 2 0 0;4 3 1 0;4 3 1 0;690 471 215 4;1 0 0 1;14 5 9 0;705 476 224 5',
 '429 296 130 3;258 172 84 2;0 0 0 0;0 0 0 0;687 468 214 5;0 0 0 0;18 8 10 0;705 476 224 5',
 '524 370 151 3;158 91 65 2;1 0 1 0;1 0 1 0;683 461 217 5;0 0 0 0;22 15 7 0;705 476 224 5'),
(89,'New or Former Resident','1 0 1 0','0 0 0 0',
 '0 0 0 0;1 0 1 0;0 0 0 0;0 0 0 0;0 0 0 0;0 0 0 0;0 0 0 0;1 0 1 0;0 0 0 0;0 0 0 0;1 0 1 0',None,None)]

def main():
    records=[];statistics=[]
    sid='sos-2024-county-york-indexed-official';original(sid)
    for pn,label,bal,blank,pr,reg,sp in YORK:
        statistics.append({'source_id':sid,'county':'York','actual_pdf_page':pn,'native_label_literal':label,
          'Ballots Cast - Total':matrix(bal)[0],'Ballots Cast - Blank':matrix(blank)[0],'Registered Voters - Total':None})
        for contest,labels,vals in [('2024-president',PRES,pr),('2024-senate-regular',REG,reg),('2024-senate-special',SPECIAL,sp)]:
            if vals is None:continue
            counts=matrix(vals);assert len(counts)==len(labels)
            records.append({'source_id':sid,'county':'York','actual_pdf_page':pn,'native_label_literal':label,'native_id_literal':None,
              'contest':contest,'method_columns':['TOTAL','Election Day','Early Voting','Provisional'],
              'fields':[{'label_literal':n,'counts':v}for n,v in zip(labels,counts)],'transcription':'Full rendered original page visually checked; all literal numbers including zeros retained.'})
    sid='sos-2024-county-garfield-indexed-official';original(sid)
    for pn,label,bal,pr,reg,sp in [(1,'City of Burwell',579,[490,82,3,1,0,0,0,3,579],[429,133,3,0,14,579],[494,63,1,0,21,579]),(6,'Rural Garfield County',445,[403,34,2,0,0,2,0,4,445],[362,71,1,0,11,445],[408,22,1,0,14,445])]:
        statistics.append({'source_id':sid,'county':'Garfield','actual_pdf_page':pn,'native_label_literal':label,'Ballots Cast - Total':[bal],
          'Ballots Cast - Blank':[0],'Registered Voters - Total':None})
        for contest,labels,vals in [('2024-president',PRES[:6]+PRES[-3:],pr),('2024-senate-regular',REG[:3]+REG[-3:],reg),('2024-senate-special',SPECIAL[:3]+SPECIAL[-3:],sp)]:
            assert len(labels)==len(vals)
            records.append({'source_id':sid,'county':'Garfield','actual_pdf_page':pn,'native_label_literal':label,'native_id_literal':None,
              'contest':contest,'method_columns':['TOTAL'],'fields':[{'label_literal':n,'counts':[v]}for n,v in zip(labels,vals)],
              'transcription':'Full rendered original page visually checked. No Not Assigned or Total Votes Cast row is printed; those are not invented.'})
    # Deuel explicitly leaves method cells blank for president/regular Senate.
    sid='sos-2024-county-deuel-indexed-unofficial';original(sid)
    statistics.append({'source_id':sid,'county':'Deuel','actual_pdf_page':1,'native_label_literal':None,'kind':'county_summary',
      'Ballots Cast - Total':[1024,787,237,0],'Ballots Cast - Blank':None,'Registered Voters - Total':1412})
    for contest,labels,vals in [('2024-president',PRES[:8],[[843,None,None,None],[151,None,None,None],[14,None,None,None],[1,None,None,None],[3,None,None,None],[2,None,None,None],[2,None,None,None],[1014,None,None,None]]),
      ('2024-senate-regular',REG[:5],[[724,None,None,None],[276,None,None,None],[2,None,None,None],[2,None,None,None],[1002,None,None,None]]),
      ('2024-senate-special',SPECIAL[:5],matrix('851 677 174 0;143 81 62 0;0 0 0 0;0 0 0 0;994 758 236 0'))]:
        records.append({'source_id':sid,'county':'Deuel','actual_pdf_page':2,'native_label_literal':None,'native_id_literal':None,'kind':'county_summary',
          'contest':contest,'method_columns':['TOTAL','Election Day','Early Voting','Provisional'],
          'fields':[{'label_literal':n,'counts':v}for n,v in zip(labels,vals)],'transcription':'Full rotated original page visually checked; blank cells are null, not zero. UNOFFICIAL publication; missing under/over not inferred.'})
    controls=json.loads((OUT/'extracts/state-controls.json').read_text())
    checks=[]
    for r in records:
        f={v['label_literal']:v['counts']for v in r['fields']}
        for label,v in f.items():
            if len(v)==4 and all(x is not None for x in v):assert v[0]==sum(v[1:]),(r,label,v)
        candidates=[n for n in f if n.startswith(('Rep ','Dem ','Lib ','Lmn ','Pet '))]
        for j in range(len(r['method_columns'])):
            if 'Total Votes Cast'in f and all(f[n][j]is not None for n in candidates+['Write-In Totals']):assert sum(f[n][j]for n in candidates+['Write-In Totals'])==f['Total Votes Cast'][j],r
            if 'Contest Totals'in f:
                total=f['Total Votes Cast'][j]if 'Total Votes Cast'in f else sum(f[n][j]for n in candidates+['Write-In Totals'])
                assert total+f['Overvotes'][j]+f['Undervotes'][j]==f['Contest Totals'][j],r
        if 'Not Assigned'in f:assert f['Not Assigned']==f['Write-In Totals']
    for county in ['York','Garfield','Deuel']:
        for contest in ['2024-senate-special','2024-senate-regular','2024-president']:
            rr=[r for r in records if r['county']==county and r['contest']==contest]
            labels=(SPECIAL if contest.endswith('special')else REG if contest.endswith('regular')else PRES)
            cols=(labels[:2]if contest.endswith('special')else labels[:3]if contest.endswith('regular')else labels[:6])
            # Regular state scattering corresponds to this county generic label;
            # special state table has no generic column. Candidate order is explicit.
            if contest=='2024-president':cols=labels[:6]
            totals=[sum(next(f['counts'][0]for f in r['fields']if f['label_literal']==n)for r in rr)for n in cols]
            assert totals==controls[contest]['counties'][county]['values'],(county,contest,totals)
            checks.append({'county':county,'contest':contest,'native_or_summary_contexts':len(rr),'state_scope_controls':totals})
    jlwrite(OUT/'extracts/scan-verified-contexts.jsonl.gz',records)
    jwrite(OUT/'extracts/scan-verified-statistics.json',statistics)
    jwrite(OUT/'extracts/scan-verified-controls.json',{'candidate_checks':checks,'all_transcribed_numeric_fields_internally_balanced':True,
      'York_presidential_only_Senate_unavailable':{'actual_pdf_page':89,'label_literal':'New or Former Resident','presidential_ballots':[1,0,1,0],'Senate':None},
      'Garfield_attachment_pages':[{'actual_pdf_page':13,'scope':'Holt certification of Burwell School District100; no Senate native context'},
        {'actual_pdf_page':14,'scope':'Valley school district email; no Senate native context'}],
      'identity_qualification':'These are alternate independent PDF publication contexts. No join to state HTML IDs/names, polygons, cross-year or2026 units is approved.'})
    print('verified scan contexts',len(records),'candidate checks',len(checks))
if __name__=='__main__':main()
