"""Candidate/publication identity and source-scoped write-in sensitivity audit."""
from source_io import *
from build import readjl,rank
import re,csv,io

def main():
    # Independently read the same exact primary originals, never peer derivatives.
    acq=json.loads((ROOT/'data/baselines/source/acquisition.json').read_text());refs=[]
    parent=original('sos-previous-elections').decode()
    for r in acq:
        if r['id']not in ['historical-lists-2','historical-lists-3','historical-lists-4']:continue
        p=ROOT/'data/baselines'/r['asset'];stored=p.read_bytes();raw=gzip.decompress(stored)
        assert sha(stored)==r['stored_sha256']and sha(raw)==r['raw_sha256']and len(raw)==r['raw_bytes']
        href=r['url'].removeprefix('https://sos.nebraska.gov');assert href in parent
        with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
            f.write(raw);f.flush();text=subprocess.check_output(['pdftotext','-layout',f.name,'-'])
        gzwrite(OUT/'extracts'/f'{r["id"]}.txt.gz',text)
        refs.append({'receipt':r,'reference_path':str(p.relative_to(ROOT)),'parent_source_id':'sos-previous-elections','literal_parent_href':href,
          'independently_verified_raw_bytes':len(raw),'independently_verified_raw_sha256':sha(raw)})
    jwrite(OUT/'source/peer-primary-original-references.json',refs)
    current,info=pdftext('sos-final-general-candidate-pdf');pp=current.split('\f');assert len(pp)-1==24
    raw=original('sos-final-general-candidate-pdf');receipt=json.loads((OUT/'source/current-final-list.receipt.json').read_text())
    assert receipt['raw_sha256']==sha(raw)
    names=[('Pete Ricketts','Republican'),('Mike Marvin','Legal Marijuana NOW'),('Robin Richards','Nebraska Working People'),('Chuck Conboy','America First'),('Dan Osborn','By Petition')]
    first=pp[0];lines=first.splitlines();roster=[]
    for name,party in names:
        i=next(i for i,l in enumerate(lines)if name in l and l.startswith('For United States Senator'))
        assert re.search(r'\s6\s+1\s',lines[i])
        roster.append({'name':name,'party_printed':party,'actual_pdf_page':1,'source_line_1based':i+1,
          'raw_source_lines':lines[i:i+3],'term_years':6,'vote_for':1,'unique_ENR_candidate_ID':None})
    catalog=json.loads(original('sos-enr-observed-candidates'))['d'];assert len(catalog)==625
    selected=[{'source_position_1based':i+1,**r}for i,r in enumerate(catalog)if 'United States Senator'in r.get('desc','')];assert len(selected)==5
    assert {r['ID']for r in selected}=={148}
    for r in roster:
        match=[p for p in selected if ' '.join(p['name'].split())==r['name']];assert len(match)==1
        assert match[0]['Party'].casefold()==r['party_printed'].casefold()
    jwrite(OUT/'extracts/current-catalog-complete.json',catalog)
    notice,_=pdftext('sos-2026-general-certification-notice-pdf');assert 'September 11, 2026'in notice
    exports=[]
    for sid in ['sos-2024-observed-public-all-csv-archive','sos-2024-observed-public-statewide-csv-archive']:
        rr=list(csv.reader(io.StringIO(original(sid).decode('utf-8-sig'))));head=rr[0];selectedrows=[{'source_row_1based':i+2,'fields':dict(zip(head,row[:15])),'unheaded_trailing_field':row[15]}for i,row in enumerate(rr[1:])if row[0]in ['12246','12464']]
        exports.append({'source_id':sid,'header':head,'Senate_rows':selectedrows,'scope':'public race/area export; not a native-precinct export. Preserve CandidateID, PartyCode, source clock and counters independently.'})
    local=readjl(OUT/'extracts/additional-summary-contexts.jsonl.gz')+readjl(OUT/'extracts/scan-verified-contexts.jsonl.gz')
    generic={}
    for c in local:
        if c['contest']=='2024-senate-special':
            generic.setdefault(c['county'],{'source_id':c['source_id'],'generic_writein_marks':0,'source_contexts':[]})
            n=next(f['counts'][0]for f in c['fields']if f['label_literal']=='Write-In Totals')
            generic[c['county']]['generic_writein_marks']+=n;generic[c['county']]['source_contexts'].append({'actual_pdf_page':c['actual_pdf_page'],'native_label_literal':c.get('native_label_literal'),'marks':n})
    for county,path in [('Douglas','douglas-native.jsonl.gz'),('Lancaster','lancaster-native-methods.jsonl.gz')]:
        rr=[r for r in readjl(OUT/'extracts'/path)if r['contest']=='2024-senate-special']
        n=sum(r['candidate_fields'][-1]['votes']if county=='Douglas'else next(v['counts'][0]for v in r['fields']if v['label_literal']=='Write-In Totals')for r in rr)
        generic[county]={'source_id':rr[0]['source_id'],'generic_writein_marks':n,'native_contexts':len(rr)}
    assert len(generic)==9 and sum(r['generic_writein_marks']for r in generic.values())==1117
    c=json.loads((OUT/'priority-set.json').read_text());prefix=c['primary_ranking']['minimum80'];D=c['primary_ranking']['denominator']
    Eoutside=(5*prefix['votes']-4*D)//4+1;Einside=4*D-5*prefix['preceding_votes']
    assert Eoutside==233 and Einside==1795
    # Explicitly incomplete marked-vote sensitivity, without filling any missing
    # generic value. Only selected native sources431 contain generic observations.
    nn=c['constituents'];partial=rank([{'key':r['key'],'name':r['county']+' / '+r['native_label_literal'],
      'votes':r['priority_votes_state_scope']+(r['generic_writeins']if r['generic_writeins']is not None else 0)}for r in nn])
    unknown=sum(r['generic_writeins']is None for r in nn);assert unknown==895
    jwrite(OUT/'extracts/candidate-universe.json',{'current_final_roster':roster,'current_catalog_rows':selected,
      'current_list_raw_sha256':sha(raw),'current_fresh_download_matches_original':True,'current_certification_announcement_date':'2026-09-11',
      'current_primary_source':'sos-final-general-candidate-pdf','current_choice_ID_scope':'ID148 is shared contest/search ID, never a unique choice key.',
      'current_eligible_writein_complete':None,'later_withdrawal_or_court_audit_complete':False,'current_counts_admitted':False,
      'historical_public_Senate_exports':exports,'historical_named_candidate_controls':'extracts/state-controls.json',
      'local_special_generic_writein_observations':generic,'local_special_generic_writein_marks_nine_counties':1117,
      'statewide_special_generic_writein_marks':None,'statewide_special_eligible_named_writein_votes':None,
      'qualified_scope':'Official2024canvass special table has only Ricketts/Love; generic county marks cannot be relabeled eligible named votes or allocated. September final candidate list is not a later affidavit/withdrawal roster. Current statutes observed2026 are not retroactively assumed identical2024law.',
      'source_native_missing_generic_contexts':unknown,'selected_source_native_observed_generic_contexts':431,
      'writein_bounds':{'known_eligible_votes_lower_bound':0,'coarse_additional_ballot_capacity_upper_bound':30231,
        'coarse_upper_bound_calculation':'965236 statewide Total Voting minus935005 state-reported named special votes; includes under/over/blank/non-Senate eligible contexts. Not observed write-ins, not a source residual allocation.',
        'membership_robustness_established':False,
        'conditional_extra_eligible_outside_fixed765_to_drop_below80':Eoutside,
        'conditional_extra_eligible_inside_fixed764_to_reach80':Einside,
        'condition':'Algebra only, assuming such additional genuine eligible votes exist in those fixed sets. No placement or existence asserted; unknown eligibility and geography can change order/membership.'},
      'incomplete_observed_generic_sensitivity':{'qualification':'Adds ONLY actual Douglas701 and Lancaster377 observations to their same original native contexts;895othercontexts unavailable and do not receive imputed generic zeros. This is a partial-observation scenario, not a complete total-vote ranking.',
        'named_plus_available_generic_sum':partial['denominator'],'minimum80_count':partial['minimum80']['count'],
        'minimum80_votes':partial['minimum80']['votes'],'crossing_key':partial['minimum80']['crossing_key'],
        'priority_key_symmetric_difference':sorted(set(partial['minimum80']['ordered_keys'])^set(c['ordered_priority_keys']))}})
    print('current final choices',len(roster),'local special generic9county',1117,'selected native generic431',1078,'eligible universe unresolved; outside233 condition')
if __name__=='__main__':main()
