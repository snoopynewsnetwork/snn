"""Independent narrow extraction of recovered Sumner primary control/methods."""
import re
from build import H,S,csvout,jdump
from calculate import selected
import csv
def main():
    sid='sumner-2022-actual-linked-summary'; text=S.pdf(sid); pages=text.split('\f'); section=pages[1].split('U.S. Hse of Reps')[0]
    (H/'source/sumner-2022-selected-pages.txt').write_text(pages[0]+'\f'+section)
    methods=['TOTAL','Election Day','Absentee','Wednesday','Thursday','Monday','Provisional']; out=[]; counts={}
    for pg,block in [(1,pages[0]),(2,section)]:
        for line_no,line in enumerate(block.splitlines(),1):
            label=re.split(r'\s{2,}',line.strip())[0]
            if (pg==1 and label.startswith('Ballots Cast -')) or (pg==2 and label in ['REP Jerry Moran','LIB David C. Graham','DEM Mark R. Holland','Write-In Totals','Not Assigned','Total Votes Cast','Overvotes','Undervotes','Contest Totals']):
                nums=[int(n.replace(',','')) for n in re.findall(r'[0-9][0-9,]*',line[len(line)-len(line.lstrip())+len(label):])]
                assert len(nums)==7,(label,nums)
                counts[label]=dict(zip(methods,nums))
                for col,(method,v) in enumerate(zip(methods,nums)):
                    out.append(dict(source_id=sid,county='Sumner',county_fips='20191',election_date='2022-11-08',source_status='OFFICIAL RESULTS',source_clock='11/17/2022 1:11 PM; timezone unspecified',pdf_page=pg,text_line=line_no,source_line=line,source_label=label,method=method,source_method_column=col,votes=v,role='overlapping_total' if method=='TOTAL' else ('nested_write_in_subtotal' if label=='Not Assigned' else 'method_detail')))
    for method in methods:
        vals={label:vs[method] for label,vs in counts.items()}
        assert vals['REP Jerry Moran']+vals['LIB David C. Graham']+vals['DEM Mark R. Holland']+vals['Write-In Totals']==vals['Total Votes Cast']
        assert vals['Total Votes Cast']+vals['Undervotes']+vals['Overvotes']==vals['Contest Totals']==vals['Ballots Cast - Total']
    csvout('source/sumner-2022-method-controls.csv',out)
    rows=list(csv.DictReader((H.parent/'county-baselines.csv').open())); T=sum(int(r['senate_2022_pair_votes']) for r in rows); M=sum(int(r['senate_2022_d_minus_r_net_votes']) for r in rows); targets=[]
    for method in methods[1:]:
        a=counts['DEM Mark R. Holland'][method]; b=counts['REP Jerry Moran'][method]; pool=a+b
        for margin in [0.,.01]:
            q=selected(pool,M-(a-b),T,margin)
            targets.append(dict(source_id=sid,county='Sumner',county_fips='20191',historical_method=method,pair_votes=pool,A_holland=a,B_moran=b,other_graham=counts['LIB David C. Graham'][method],generic_write_in=counts['Write-In Totals'][method],baseline_A_share=a/pool if pool else None,pair_weight_of_all105=pool/T,baseline_net=a-b,nominal_plus1share_pp_net_gain=.02*pool,goal_pair_margin_pp=margin*100,local_pair_tie_share=.5 if pool else None,local_pair_Aplus1_share=.505 if pool else None,selected_only_other_net=M-(a-b),selected_only_required_A_share=q['required_share_unbounded'],selected_only_status=q['status']))
    csvout('sumner-method-targets.csv',targets)
    jdump('sumner-source-check.json',dict(status='pass',source_id=sid,original_sha256=S.sha(S.raw(sid)),method_identity_count=6,source_method_heading_note='Wednesday heading wraps Wednesda / y in PDF; retained source text; combined display spelling only',ballots=counts['Ballots Cast - Total']['TOTAL'],named_Senate_votes=sum(counts[n]['TOTAL'] for n in ['REP Jerry Moran','LIB David C. Graham','DEM Mark R. Holland']),SOS_workbook_ballots=1403,source_disagreement='7932 county official ballots versus1403 SOS turnout cell; cause unestablished, no redistribution',not_current_method_mapping=True))
    print('Sumner6 method identities,77 source cells and12 conditional target rows verified')
if __name__=='__main__':main()
