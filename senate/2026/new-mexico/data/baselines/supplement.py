#!/usr/bin/env python3
"""Source clocks, disagreements, fresh page observations and cross-contest literal scope."""
import gzip,hashlib,json,re,runpy,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;S=D/'source';STATE=D.parents[1]
def load(p):return json.loads(p.read_text())
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def main():
    E=load(D/'original-extract.json');refs={r['id']:r for r in load(S/'original-references.json')};t=load(D/'turnout-controls.json');bm=load(D/'administrative-method-controls.json');reg=load(D/'registration-controls.json');rn=load(D/'registration-native-controls.json');dis={};clocks={}
    for yr,v in t.items():
        raw=gzip.decompress((STATE/refs[v['source_id']]['asset']).read_bytes()).decode();m=re.search(r'Results last updated:.*?(\d+/\d+/\d+\s+\d+:\d+\s*[AP]M\s*MT)',re.sub(r'<[^>]+>',' ',raw),re.S)
        if not m:
            m=re.search(r'\d+/\d+/\d+\s+\d+:\d+\s*[AP]M\s*MT',raw)
        clocks[yr]={'portal_source_clock_literal':m.group(1)if m and m.lastindex else (m.group(0)if m else None),'timezone_literal':'MT'if m else None,'UTC_conversion':None,'native_negative_eligible':[u for u in v['native_rows']if u['eligible_voters']<0]}
        cs={r['CountyName']:int(r['calcVoterTurnout'])for r in v['county_service']};b=bm[yr];diff=[{'county':c,'pdf_method_header_total':sum(r['values'][i]for r in b['rows']),'portal_ballots':cs[c],'difference_pdf_minus_portal':sum(r['values'][i]for r in b['rows'])-cs[c]}for i,c in enumerate(b['county_order'])if sum(r['values'][i]for r in b['rows'])!=cs[c]]
        dis[yr]={'portal_ballots':v['header']['ballots_cast'],'pdf_header_ballots':b['header_total'],'pdf_minus_portal':b['header_total']-v['header']['ballots_cast'],'county_disagreements':diff,'portal_native_eligible_sum_minus_header':v['native_sum_eligible']-v['header']['eligible_voters'],'date_run_literals':re.findall(r'Date Run:[^\n]+',(S/f"{b['source_id']}.txt").read_text())}
    stocks={}
    for date,key in [('2024-10-31','9'),('2024-11-26','10')]:
        v=rn[key]['rows'];state={r['county_literal'].upper():r for r in reg[date]['rows']};comparisons=[]
        for r in v:
            if r['scope']!='county_total':continue
            native=sum(u['total']for u in v if u['scope']=='native'and u['county_literal']==r['county_literal']);sr=state[r['county_literal']]['values'][-1]
            if native!=r['total']or sr!=r['total']:comparisons.append({'county_literal':r['county_literal'],'state_table_total':sr,'county_table_total':r['total'],'native_total_sum':native,'county_minus_state':r['total']-sr,'native_minus_county':native-r['total']})
        stocks[date]={'state_report_total':state['TOTAL']['values'][-1],'county_table_total_sum':sum(r['total']for r in v if r['scope']=='county_total'),'native_sum':sum(r['total']for r in v if r['scope']=='native'),'differences':comparisons,'no_blank_party_filled':True,'no_crosswalk_claimed':True}
    metadata_dis=[]
    for k,v in E.items():
        meta=load(S/v['page_data_path'])['props']['pageProps']['contest']
        for c in meta['candidates']:
            if c.get('nVotesParty1')is not None and c['nVotesParty1']!=c['nVotes']:metadata_dis.append({'contest':k,'candidate_in_contest_id':c['id'],'display_name':c['displayName'],'nVotes':c['nVotes'],'nVotesParty1':c['nVotesParty1'],'difference':c['nVotes']-c['nVotesParty1'],'treatment':'preserve distinct source fields; nVotes agrees CSV/PDF; no party-key deduplication or suppressed allocation'})
    sen={(r['county_literal'],r['label_literal'])for r in E['2024-senate']['rows']if r['scope']=='Precinct'};pres={(r['county_literal'],r['label_literal'])for r in E['2024-president']['rows']if r['scope']=='Precinct'}
    save(D/'source-disagreements.json',{'ballots':dis,'registration_stocks':stocks,'page_metadata_distinct_lanes':metadata_dis,'2024_literal_key_president_only':sorted(pres-sen),'2024_literal_key_senate_only':sorted(sen-pres),'literal_key_comparison_not_crosswalk':True,'suppression_diagnostics':'coverage-controls.json; residuals unallocated; not scenario inputs'})
    save(D/'source-clocks.json',clocks)
    fresh=load(S/'fresh-observations.json');Tables=runpy.run_path(str(S/'extract.py'))['Tables'];out={}
    for r in fresh:
        if r['status']!=200:continue
        raw=gzip.decompress((STATE/r['asset']).read_bytes())
        if r['id']=='current-roster-linked-candidate-list':
            p=Tables();p.feed(raw.decode());rows=[a for a in p.rows if a['cells']and a['cells'][0]['text']=='United States Senator'];assert len(rows)==4
            original=load(D/'current-senate-status-records.json')['rows'];sig=lambda a:[[c['text']for c in b['cells']]for b in a]
            out['general_roster']={'fresh_receipt':r,'rows':rows,'all24cells_equal_pinned_original':sig(rows)==sig(original),'not_signed_ballot_mapping':True}
        elif r['id']=='elstats-2024-senate-linked-csv':out['fresh_senate_csv']={'receipt':r,'same_raw_hash_as_pinned_original':r['raw_sha256']==E['2024-senate']['raw_sha256']}
        elif r['id']=='official-2025-handbook':
            p=S/'official-2025-handbook.temporary.pdf';p.write_bytes(raw);subprocess.run(['pdftotext','-layout',str(p),str(S/'official-2025-handbook.txt')],check=True);p.unlink();out['legal_handbook']={'receipt':r,'sections':['1-13-11 tie by lot','1-14-18 plurality recanvass','1-15-12 general Senate election','1-15-13 Senate canvass as state officers','1-22-16 municipal runoff separate scope']}
    out['bounded_failed_final_notice']=[r for r in fresh if r['id']=='otero-2026-general-notice']
    save(D/'fresh-source-review.json',out)
    print(json.dumps({'source_metadata_lane_differences':len(metadata_dis),'literal_president_only':sorted(pres-sen),'stock_disagreements_retained':stocks.keys()if False else list(stocks)}))
if __name__=='__main__':main()
