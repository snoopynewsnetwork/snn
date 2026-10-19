"""Additional original county fields and explicit source-volume differences."""
from source_io import *
from build import readjl
import re

TITLES={'US President':'2024-president','US Senator 6 YR':'2024-senate-regular','US Senator 2 YR':'2024-senate-special'}
def main():
    contexts=[];stats=[];controls=json.loads((OUT/'extracts/state-controls.json').read_text())
    for county in ['Nemaha','Clay','Nance','Gosper']:
        sid=f'sos-2024-county-{county.lower()}-indexed-official';t,info=pdftext(sid)
        for pn,page in enumerate(t.split('\f'),1):
            lines=page.splitlines()
            if 'Registered Voters - Total'in page:
                ff=[]
                for ln,line in enumerate(lines,1):
                    m=re.fullmatch(r'\s*(Ballots Cast - (?:Total|Blank))\s+([\d,]+(?:\s+[\d,]+)*)\s*',line)
                    if m:ff.append({'label_literal':m[1],'counts':[int(v.replace(',',''))for v in m[2].split()],'raw_line':line,'source_line_1based':ln})
                stats.append({'source_id':sid,'county':county,'actual_pdf_page':pn,'kind':'county_summary',
                  'registered_total':int(re.search(r'Registered Voters - Total\s+([\d,]+)',page)[1].replace(',','')),
                  'fields':ff,'raw_page':page})
            starts=[i for i,l in enumerate(lines)if l.strip()in TITLES]
            for i in starts:
                title=lines[i].strip();end=next((j for j in range(i+1,len(lines))if lines[j].strip()in TITLES or re.match(r'^\s*(Congress Dist\.|2024 GN Election Summary|Official Results|Gosper Election Summary| - )',lines[j])),len(lines))
                ff=[]
                for ln in range(i+1,end):
                    m=re.fullmatch(r'\s*(.*?)\s{2,}([\d,]+(?:\s+[\d,]+)*)\s*',lines[ln])
                    if m and m[1]and not m[1].startswith(('Vote For','TOTAL','Page')):
                        ff.append({'label_literal':m[1],'counts':[int(v.replace(',',''))for v in m[2].split()],
                          'source_line_1based':ln+1,'raw_line':lines[ln]})
                assert ff and len({r['label_literal']for r in ff})==len(ff),(county,title,ff)
                n=len(ff[0]['counts']);assert n in [1,4]and all(len(r['counts'])==n for r in ff)
                for r in ff:
                    if n==4:assert r['counts'][0]==sum(r['counts'][1:]),r
                f={r['label_literal']:r['counts']for r in ff};candidate=[l for l in f if l.startswith(('Rep ','Dem ','Pet ','Lmn ','Lib '))]
                for j in range(n):
                    cv=sum(f[l][j]for l in candidate+['Write-In Totals'])
                    if 'Total Votes Cast'in f:assert cv==f['Total Votes Cast'][j]
                    if 'Contest Totals'in f:assert cv+f['Overvotes'][j]+f['Undervotes'][j]==f['Contest Totals'][j]
                assert f['Write-In Totals']==f['Not Assigned']
                contexts.append({'source_id':sid,'county':county,'actual_pdf_page':pn,'contest':TITLES[title],'contest_label_literal':title,
                  'kind':'county_summary','native_id_literal':None,'native_label_literal':None,
                  'method_columns':['TOTAL']if n==1 else ['TOTAL','Election Day','Early Voting','Provisional'],
                  'fields':ff,'raw_block':'\n'.join(lines[i:end]),'missing_fields_are_unavailable':True})
    checks=[]
    for r in contexts:
        f={v['label_literal']:v['counts'][0]for v in r['fields']};contest=r['contest']
        names=(['Rep Pete Ricketts','Dem Preston Love Jr.']if contest.endswith('special')else ['Rep Deb Fischer','Pet Dan Osborn','Write-In Totals']if contest.endswith('regular')else ['Rep Trump/Vance','Dem Harris/Walz','Lib Oliver/ter Maat','Lmn West/Abdullah','Pet Stein/Kpadenou','Write-In Totals'])
        assert [f[n]for n in names]==controls[contest]['counties'][r['county']]['values'],r
        checks.append({'source_id':r['source_id'],'contest':contest,'state_scope_values':[f[n]for n in names]})
    jlwrite(OUT/'extracts/additional-summary-contexts.jsonl.gz',contexts)
    jwrite(OUT/'extracts/additional-summary-statistics.json',stats)
    jwrite(OUT/'extracts/additional-summary-controls.json',checks)
    # Independent local Douglas PDF-to-BIFF candidate and ballot comparison.
    du=readjl(OUT/'extracts/douglas-native.jsonl.gz');vol=[];pdfchecks=[]
    headings={'2024-senate-special':'For United States Senator Two-Year Term','2024-senate-regular':'For United States Senator',
      '2024-president':'For President And Vice President Of The United States','2022-governor':'For Governor','2020-senate':'For United States Senator'}
    prefixes={'2024-senate-special':['Pete Ricketts','Preston Love Jr.','Write-In Totals'],
      '2024-senate-regular':['Deb Fischer','Dan Osborn','Write-In Totals'],'2024-president':['Donald J. Trump','Kamala D. Harris','Chase Oliver','Cornel West','Jill Stein','Write-In Totals'],
      '2022-governor':['Jim Pillen','Carol Blood','Scott Zimmerman','Write-In Totals'],'2020-senate':['Ben Sasse','Chris Janicek','Gene Siadek','Preston Love, Jr.','Not Assigned']}
    for contest,title in headings.items():
        y=int(contest[:4]);sid=f'county-douglas-{y}-summary-pdf';t,_=pdftext(sid)
        m=re.search(r'^\s*'+re.escape(title)+r'\s*$',t,re.M);assert m
        block=t[m.end():];n=re.search(r'^\s*For ',block,re.M);block=block[:n.start()]if n else block
        rr=[r for r in du if r['contest']==contest];v=[]
        for k,name in enumerate(prefixes[contest]):
            line=next(l for l in block.splitlines()if re.match(r'^\s*'+re.escape(name)+r'(?:\s|\()',l))
            count=int(re.search(r'(\d[\d,]*)\s*$',line)[1].replace(',',''))
            assert count==sum(r['candidate_fields'][k]['votes']for r in rr)
            pdfchecks.append({'source_id':sid,'contest':contest,'label_prefix':name,'source_line':line,'value':count});v.append(count)
        if contest=='2020-senate':
            parent=int(re.search(r'^Write-In Totals\s+([\d,]+)',block,re.M)[1].replace(',',''));assert parent==v[-1]+v[-2]
        ballot=int(re.search(r'^Ballots Cast - Total\s+([\d,]+)',t,re.M)[1].replace(',',''))
        total=sum(r['contest_volume_arithmetic']for r in rr)
        vol.append({'source_id':sid,'contest':contest,'county':'Douglas','separate_summary_ballots':ballot,
          'native_candidate_generic_over_under_arithmetic':total,'difference_arithmetic_minus_ballots':total-ballot,
          'cause':None,'repaired':False})
    casts={c:{r['native_label_literal']:r['contest_volume_arithmetic']for r in du if r['contest']==c}for c in ['2024-president','2024-senate-special','2024-senate-regular']}
    contrasts=[{'source_ward_precinct_literal':n,**{c:casts[c][n]for c in casts}}for n in casts['2024-president']if len({casts[c][n]for c in casts})>1]
    assert contrasts==[{'source_ward_precinct_literal':'03-02','2024-president':1202,'2024-senate-special':1201,'2024-senate-regular':1201}]
    ls=json.loads((OUT/'extracts/lancaster-statistics.json').read_text())
    lreg=sum(r['registered_total']for r in ls)
    lballots=sum(next(f['counts'][0]for f in r['fields']if f['label_literal']=='Ballots Cast - Total')for r in ls)
    state_reg=controls['2024-registration']['counties']['Lancaster']['values'][-1]
    state_voting=controls['2024-voting-method']['counties']['Lancaster']['values'][-1]
    assert (len(ls),lreg,state_reg,lreg-state_reg,lballots,state_voting)==(199,206570,206406,164,161160,161160)
    resident=next(r for r in ls if r['native_label_literal']=='New or Former Resident');assert resident['registered_total']==0
    jwrite(OUT/'extracts/local-volume-reconciliation.json',{'Douglas_source_volume':vol,'Douglas_within2024_contrasts':contrasts,'Douglas_local_PDF_candidate_fields':pdfchecks,
      'Lancaster_native_statistics_vs_state':{'source_id':'county-lancaster-2024-final-precinct-pdf-actual-archive','statistics_contexts':199,
        'registered_native_sum':lreg,'state_canvass_registered_total':state_reg,'local_minus_state_registered':lreg-state_reg,
        'native_ballots_sum_all199':lballots,'state_Total_Voting':state_voting,'ballots_difference':lballots-state_voting,
        'resident_registered':0,'Senate_context_count':198,'Senate_context_ballots':161159,
        'qualification':'Local native registration and statewide canvass snapshots disagree; no equal status/date definition, rescale or residual assignment. Presidential resident ballot is separate from Senate contexts.'},
      'separate_local_registration_vs_state':[{**r,'canvass_registered_total':controls['2024-registration']['counties'][r['county']]['values'][-1],
        'local_minus_state_registered':r['registered_total']-controls['2024-registration']['counties'][r['county']]['values'][-1]}for r in stats]})
    print('Additional textPDF contexts',len(contexts),'DouglasPDF candidate comparisons',len(pdfchecks))
if __name__=='__main__':main()
