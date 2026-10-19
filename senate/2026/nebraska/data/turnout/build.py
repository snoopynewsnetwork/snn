"""Build complete county and native historical priority from independent extracts."""
from source_io import *
import csv, io, re
from decimal import Decimal, localcontext

def readjl(p):return [json.loads(l)for l in gzip.decompress(p.read_bytes()).decode().splitlines()]
def csvwrite(p,rows):
    buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);p.write_text(buf.getvalue())
def percentage(n,d):
    with localcontext()as ctx:
        ctx.prec=40;return str(Decimal(100)*Decimal(n)/Decimal(d))
def rank(rows):
    """Exact integer threshold, votes descending then explicit stable key ascending."""
    order=sorted(rows,key=lambda r:(-r['votes'],r['key']));total=sum(r['votes']for r in order);cum=0
    for i,r in enumerate(order,1):
        r['rank']=i;r['cumulative_before_votes']=cum;cum+=r['votes'];r['cumulative_votes']=cum
        r['share_numerator']=r['votes'];r['share_denominator']=total;r['share_percent']=percentage(r['votes'],total)
        r['cumulative_percent']=percentage(cum,total)
    k=next(i for i,r in enumerate(order,1)if 5*r['cumulative_votes']>=4*total)
    return {'denominator':total,'coverage_count':len(order),'tie_rule':'votes descending, stable key ascending',
      'top15':{'count':15,'votes':sum(r['votes']for r in order[:15]),'share_percent':percentage(sum(r['votes']for r in order[:15]),total),'ordered_keys':[r['key']for r in order[:15]]},
      'minimum80':{'count':k,'votes':order[k-1]['cumulative_votes'],'share_percent':order[k-1]['cumulative_percent'],
        'preceding_count':k-1,'preceding_votes':order[k-1]['cumulative_before_votes'],
        'preceding_share_percent':percentage(order[k-1]['cumulative_before_votes'],total),
        'crossing_key':order[k-1]['key'],'crossing_name':order[k-1]['name'],'crossing_votes':order[k-1]['votes'],
        'ordered_keys':[r['key']for r in order[:k]]},
      'remainder':{'count':len(order)-k,'votes':total-order[k-1]['cumulative_votes'],'ordered_keys':[r['key']for r in order[k:]]},
      'full_order':order}

def main():
    a=json.loads((OUT/'extracts/state-controls.json').read_text())
    codes=list(csv.DictReader(io.StringIO(gzip.decompress((OUT/'source/census-county-codes.body.gz').read_bytes()).decode()),delimiter='|'))
    codes={r['COUNTYNAME'].removesuffix(' County'):r for r in codes if r['STATE']=='NE'}
    assert len(codes)==93 and set(codes)==set(a['2024-senate-special']['counties'])
    countyrows=[]
    for name,rr in a['2024-senate-special']['counties'].items():
        fips=codes[name]['STATEFP']+codes[name]['COUNTYFP'];r={'county':name,'county_fips':fips,'priority_key':'NE:county:'+fips}
        for tid in ['2024-senate-special','2024-senate-regular','2024-president','2022-governor','2020-senate']:
            vv=a[tid]['counties'][name]['values'];tag=tid.replace('-','_')
            r[tag+'_contest_votes_state_reported']=sum(vv)
            for col,v in zip(a[tid]['candidate_columns'],vv):
                key=re.sub(r'[^a-z0-9]+','_',col['name'].lower()).strip('_')
                r[tag+'_'+key]=v
        for y in [2024,2022,2020]:
            reg=a[f'{y}-registration']['counties'][name]['values'];meth=a[f'{y}-voting-method']['counties'][name]['values']
            r[f'{y}_source_precinct_count']=reg[0];r[f'{y}_registered_voters_canvass']=reg[-1];r[f'{y}_total_voting_canvass']=meth[-1]
            reglabels={2024:['Republican','Democratic','Libertarian','Legal Marijuana NOW','No Labels Nebraska','Nonpartisan'],2022:['Republican','Democratic','Libertarian','Legal Marijuana NOW','Nonpartisan'],2020:['Republican','Democratic','Libertarian','Nonpartisan']}[y]
            methodlabels={2024:['polling_place','early_voting','all_mail_precincts','provisional_ballot','military_overseas','new_former_resident'],2022:['at_polls','all_mail_precincts','provisional','early_voting','military_overseas'],2020:['at_polls','all_mail_precincts','provisional','early_voting','military_overseas','new_former_resident']}[y]
            for l,v in zip(reglabels,reg[1:-1]):r[f'{y}_registration_'+re.sub(r'[^a-z0-9]+','_',l.lower())]=v
            for l,v in zip(methodlabels,meth[:-1]):r[f'{y}_total_voting_method_{l}']=v
        r['2024_special_generic_writeins_state_table']=None;r['2024_special_blank_state_table']=None
        r['2024_special_under_state_table']=None;r['2024_special_over_state_table']=None
        countyrows.append(r)
    county_rank=rank([{'key':r['priority_key'],'name':r['county'],'county_fips':r['county_fips'],
      'votes':r['2024_senate_special_contest_votes_state_reported']}for r in countyrows])
    indices={r['key']:r for r in county_rank['full_order']};countyrows.sort(key=lambda r:indices[r['priority_key']]['rank'])
    for r in countyrows:
        q=indices[r['priority_key']];r.update({'priority_rank':q['rank'],'priority_share_numerator':q['votes'],
          'priority_share_denominator':county_rank['denominator'],'priority_cumulative_votes':q['cumulative_votes'],
          'in_top15':q['rank']<=15,'in_minimum80':q['rank']<=county_rank['minimum80']['count']})
    csvwrite(ROOT/'data/county-turnout.csv',countyrows)
    hist=readjl(OUT/'extracts/historical-html-native.jsonl.gz');coverage=json.loads((OUT/'extracts/historical-html-coverage.json').read_text())
    doug=readjl(OUT/'extracts/douglas-native.jsonl.gz');lanc=readjl(OUT/'extracts/lancaster-native-methods.jsonl.gz')
    lstat=json.loads((OUT/'extracts/lancaster-statistics.json').read_text());lindex={s['native_label_literal']:s for s in lstat}
    native=[];unavailable=[];alternates=[]
    for r in hist:
        rec={'source_id':r['source_id'],'county':r['county'],'county_fips':codes[r['county']]['STATEFP']+codes[r['county']]['COUNTYFP'],
          'source_county_id_literal':r['source_county_id_literal'],'native_id_literal':r['native_id_literal'],
          'native_label_literal':r['native_label_literal'],'source_position':r['source_header_row_id'],
          'source_kind':'historical_state_HTML','kind':r['kind'],'source_complete':r['entity_complete'],
          'candidate_values':[c['votes']if c else None for c in r['candidates']],
          'generic_writeins':None,'ballots':None,'registration':None,'blank':None,'under':None,'over':None,
          'method':'combined_unknown','map_identity_status':'unapproved; source ID is publication-scoped'}
        rec.update({k:r[k]for k in ['publication_status_literal','source_update_clock_literal','source_clock_timezone']})
        rec['source_candidate_objects']=r['candidates']
        rec['key']='NE:2024-special:html:'+r['source_county_id_literal']+':'+str(r['native_id_literal'])
        if r['kind']=='administrative_countywide':
            rec['included_in_rank']=False;rec['reason']='Separate source administrative row; never add county total to included children.';alternates.append(rec)
        elif r['entity_complete']:
            rec['included_in_rank']=True;native.append(rec)
        else:
            rec['included_in_rank']=False;rec['reason']='Explicitly truncated archive entity; not joined to complete county original.';alternates.append(rec)
    for r in doug:
        if r['contest']!='2024-senate-special':continue
        native.append({'key':'NE:2024-special:douglas-biff:'+r['native_id_literal'],'source_id':r['source_id'],
          'county':'Douglas','county_fips':'31055','source_county_id_literal':None,'native_id_literal':r['native_id_literal'],
          'native_label_literal':r['native_label_literal'],'source_position':{'sheet':r['sheet'],'row_1based':r['source_row_1based']},
          'source_kind':'county_BIFF','kind':r['kind'],'source_complete':True,'included_in_rank':True,
          'candidate_values':r['state_scope_candidate_values'],'generic_writeins':r['candidate_fields'][-1]['votes'],
          'reported_candidate_and_generic_votes':r['reported_total_votes'],'ballots':None,'registration':None,'blank':None,
          'under':r['under'],'over':r['over'],'contest_volume_arithmetic':r['contest_volume_arithmetic'],
          'method':r['method'],'map_identity_status':'unapproved; literal workbook Ward-Precinct only'})
    for r in lanc:
        if r['contest']!='2024-senate-special':continue
        f={v['label_literal']:v['counts']for v in r['fields']};s=lindex[r['native_label_literal']];st={v['label_literal']:v['counts']for v in s['fields']}
        native.append({'key':'NE:2024-special:lancaster-pdf:page-'+str(r['actual_pdf_page']),
          'source_id':r['source_id'],'county':'Lancaster','county_fips':'31109','source_county_id_literal':None,
          'native_id_literal':None,'native_label_literal':r['native_label_literal'],'source_position':{'actual_pdf_page':r['actual_pdf_page']},
          'source_kind':'county_PDF','kind':r['kind'],'source_complete':True,'included_in_rank':True,
          'candidate_values':[f['Rep Pete Ricketts'][0],f['Dem Preston Love Jr.'][0]],
          'generic_writeins':f['Write-In Totals'][0],'reported_candidate_and_generic_votes':f['Total Votes Cast'][0],
          'ballots':st['Ballots Cast - Total'][0],'registration':s['registered_total'],'blank':st['Ballots Cast - Blank'][0],
          'under':f['Undervotes'][0],'over':f['Overvotes'][0],'method_columns':r['method_columns'],
          'candidate_method_values':{'Rep Pete Ricketts':f['Rep Pete Ricketts'],'Dem Preston Love Jr.':f['Dem Preston Love Jr.']},
          'map_identity_status':'unapproved; native PDF label and page position, no separate published ID'})
    unavailable.append({'key':'NE:2024:lancaster-pdf:New or Former Resident','county':'Lancaster','county_fips':'31109',
      'native_label_literal':'New or Former Resident','source_id':'county-lancaster-2024-final-precinct-pdf-actual-archive',
      'source_position':{'statistics_page':lindex['New or Former Resident']['actual_pdf_page']},'priority_contest_votes':None,
      'kind':'presidential_only_administrative_context','reason':'One early-voting presidential ballot, no Senate section; never impute a zero Senate record.',
      'included_in_rank':False,'current_equivalence':None})
    assert len(native)==1326 and len({r['key']for r in native})==1326
    for county in codes:
        units=[r for r in native if r['county']==county]
        assert [sum(r['candidate_values'][j]for r in units)for j in range(2)]==a['2024-senate-special']['counties'][county]['values'],county
    nr=rank([{'key':r['key'],'name':r['county']+' / '+r['native_label_literal'],'county':r['county'],
      'votes':sum(r['candidate_values'])}for r in native]);assert nr['denominator']==935005
    nindex={r['key']:r for r in nr['full_order']}
    for r in native:r['rank']=nindex[r['key']]['rank'];r['priority_votes_state_scope']=sum(r['candidate_values'])
    native.sort(key=lambda r:r['rank']);jlwrite(OUT/'extracts/selected-native-disjoint.jsonl.gz',native)
    nativecsv=[{'rank':r['rank'],'key':r['key'],'county':r['county'],'county_fips':r['county_fips'],
      'source_id':r['source_id'],'source_kind':r['source_kind'],'native_id_literal':r['native_id_literal'],
      'native_label_literal':r['native_label_literal'],'ricketts':r['candidate_values'][0],'love':r['candidate_values'][1],
      'priority_votes_state_scope':sum(r['candidate_values']),'generic_writeins_source_scoped':r['generic_writeins'],
      'ballots_source_scoped':r['ballots'],'registered_source_scoped':r['registration'],'blank_source_scoped':r['blank'],
      'undervotes_source_scoped':r['under'],'overvotes_source_scoped':r['over'],
      'cumulative_votes':nindex[r['key']]['cumulative_votes'],'in_native_min80':r['rank']<=nr['minimum80']['count']}for r in native]
    csvwrite(OUT/'native-turnout.csv',nativecsv)
    sensitivity={}
    for tid,field in [('2024-senate-regular','2024_senate_regular_contest_votes_state_reported'),('2024-president','2024_president_contest_votes_state_reported'),
      ('2022-governor','2022_governor_contest_votes_state_reported'),('2020-senate','2020_senate_contest_votes_state_reported'),
      ('2024-total-voting','2024_total_voting_canvass'),('2022-total-voting','2022_total_voting_canvass'),('2020-total-voting','2020_total_voting_canvass'),
      ('2024-registration','2024_registered_voters_canvass'),('2022-registration','2022_registered_voters_canvass'),('2020-registration','2020_registered_voters_canvass')]:
        rr=rank([{'key':r['priority_key'],'name':r['county'],'votes':r[field]}for r in countyrows]);pp=set(county_rank['minimum80']['ordered_keys'])
        rr['fixed_special_priority_set_votes']=sum(r['votes']for r in rr['full_order']if r['key']in pp)
        rr['fixed_special_priority_set_share_percent']=percentage(rr['fixed_special_priority_set_votes'],rr['denominator']);sensitivity[tid]=rr
    jwrite(OUT/'sensitivity.json',sensitivity)
    allparents=[{'parent_key':'NE:county:'+r['county_fips'],'county':r['county'],'county_fips':r['county_fips'],
      'full_child_keys':[n['key']for n in native if n['county']==r['county']],
      'priority_child_keys':[n['key']for n in native if n['county']==r['county']and n['rank']<=nr['minimum80']['count']],
      'full_child_named_votes':sum(n['priority_votes_state_scope']for n in native if n['county']==r['county']),
      'priority_child_named_votes':sum(n['priority_votes_state_scope']for n in native if n['county']==r['county']and n['rank']<=nr['minimum80']['count'])}
      for r in sorted(countyrows,key=lambda r:r['county_fips'])]
    contract={'schema_version':'NE-turnout-priority-v2','status':'provisional_native_priority_independently_reconciled_pending_peer_and_coordinator_review',
      'state':'NE','election':'2024-11-05 general','priority_contest':'2024 Class II two-year Senate special',
      'denominator_scope':'State canvass reported candidate universe: Pete Ricketts Republican and Preston Love Jr Democratic. Generic write-ins in local originals are separate incomplete statewide scope, never assumed zero.',
      'candidate_controls':{'Pete Ricketts Republican':585103,'Preston Love Jr. Democratic':349902},
      'priority_level':'source_native_reporting_unit','primary_ranking':nr,
      'ordered_priority_keys':nr['minimum80']['ordered_keys'],
      'ordered_full_keys':[r['key']for r in nr['full_order']],
      'ordered_remainder_keys':nr['remainder']['ordered_keys'],
      'all93_parents':allparents,
      'parent_full_child_map':{r['parent_key']:r['full_child_keys']for r in allparents},
      'parent_priority_child_map':{r['parent_key']:r['priority_child_keys']for r in allparents},
      'child_parent_map':{n['key']:'NE:county:'+n['county_fips']for n in native},
      'county_concentration_sensitivity_only':county_rank,
      'coverage':{'county_count':93,'county_fips_source':'Census 2020 national county code file','selected_native_count':1326,
        'partition':{'complete_historical_state_HTML':895,'Douglas_BIFF':233,'Lancaster_PDF':198},
        'no_cross_publication_unit_join':True,'whole_state_in_arithmetic':True},
      'constituents':native,'administrative_and_partial_alternates':alternates,'unavailable_cases':unavailable,
      'county_source_coverage':coverage,
      'writein_universe_scope':{'statewide_named_candidate_universe_reconciled':True,
        'statewide_special_generic_writein_total':None,'eligible_named_writein_complete':None,
        'local_generic_writeins_are_not_assumed_legally_eligible':True,
        'unallocated_total_voting_minus_named_ceiling':965236-935005,
        'ceiling_qualification':'Coarse maximum using separate statewide Total Voting; includes non-Senate eligibility, blank/under/over and other noncandidate categories. It is not observed write-ins or an allocation. Later source-scoped bounds are retained separately.',
        'priority_membership_robust_to_unknown_eligible_writeins':None},
      'hierarchy':'Count either all counties or selected disjoint native partition. Do not sum levels, overlapping alternates, methods with TOTAL, or summary/footer rows with children.',
      'current_geography_approval':False,'coordinator_acceptance':False,'independent_peer_agreement':None}
    extra=OUT/'extracts/scan-verified-contexts.jsonl.gz'
    if extra.exists():
        scans=readjl(extra)
        contract['additional_native_source_contexts']=[{'key':'NE:2024-special:'+r['county'].lower()+'-alternate-pdf:page-'+str(r['actual_pdf_page']),
          'included_in_primary_rank':False,'reason':'Alternate original PDF native observation. No join to state HTML unit IDs is established.',**r}
          for r in scans if r['contest']=='2024-senate-special'and r.get('kind')!='county_summary']
        yorkresident=next(r for r in scans if r['county']=='York'and r['native_label_literal']=='New or Former Resident')
        contract['unavailable_cases'].append({'key':'NE:2024:york-alternate-pdf:New or Former Resident','county':'York','county_fips':'31185',
          'native_label_literal':'New or Former Resident','source_id':yorkresident['source_id'],'source_position':{'actual_pdf_page':89},
          'priority_contest_votes':None,'kind':'presidential_only_administrative_context','reason':'One early-voting presidential ballot and no Senate section. Alternate PDF, no source-ID join to HTML.',
          'included_in_rank':False,'current_equivalence':None,'original_presidential_context':yorkresident})
        contract['additional_administrative_contexts']=[{'source_id':'sos-2024-county-garfield-indexed-official','actual_pdf_page':pn,
          'kind':'school_district_attachment','priority_contest_votes':None,'included_in_rank':False,
          'reason':reason}for pn,reason in [(13,'Holt certification for Burwell School District100; no Senate context.'),(14,'Valley county school-district email attachment; no Senate context.')]]
    universe=OUT/'extracts/candidate-universe.json'
    if universe.exists():
        u=json.loads(universe.read_text());contract['candidate_universe_evidence']={'path':'data/turnout/extracts/candidate-universe.json','sha256':sha(universe.read_bytes())}
        contract['writein_universe_scope'].update({'known_local_generic_marks_nine_counties':u['local_special_generic_writein_marks_nine_counties'],
          'known_generic_marks_in_selected431_native_contexts':1078,'selected_native_generic_unavailable_contexts':895,
          'membership_robustness_established':False,'bounds':u['writein_bounds']})
    proof=OUT/'peer-agreement.json'
    if proof.exists():
        p=json.loads(proof.read_text())
        if p['status']=='pass_reciprocal_read_only_original_extraction_agreement':
            contract['status']='named_scope_peer_reconciled_pending_coordinator_acceptance'
            contract['independent_peer_agreement']={'path':'data/turnout/peer-agreement.json','sha256':sha(proof.read_bytes()),
              'peer_agent_id':p['peer_agent_id'],'scope':'Shared independent original candidate/native/method/volume fields, full order/minimum and all93parentmaps; no eligible-writein/current-geometry approval.'}
    universeproof=OUT/'source/peer-universe-QA.json'
    if universeproof.exists():
        pp=json.loads(universeproof.read_text())
        assert pp['status']=='pass'and pp['peer_sha256']==sha(universe.read_bytes())
        contract['independent_peer_universe_QA']={'path':'data/turnout/source/peer-universe-QA.json','sha256':sha(universeproof.read_bytes()),
          'scope':'Independently original-extracted46scan/12textcontexts,1117ninecounty generic,1078selected/895unknown, candidate identities/source IDs and conditional bounds. Eligible named write-in universe remains unproved.'}
    volume=OUT/'extracts/local-volume-reconciliation.json'
    if volume.exists():
        v=json.loads(volume.read_text())
        contract['source_scoped_volume_registration_comparisons']={'path':'data/turnout/extracts/local-volume-reconciliation.json','sha256':sha(volume.read_bytes()),
          'Lancaster_native_statistics_vs_state':v['Lancaster_native_statistics_vs_state'],
          'Douglas_source_volume':v['Douglas_source_volume'],
          'qualification':'Separate publications/status/date scopes. These disagreements remain unrepaired and do not change reconciled named-candidate ranking.'}
    jwrite(OUT/'priority-set.json',contract)
    print(json.dumps({'county_top15_votes':county_rank['top15']['votes'],'county_min80_count':county_rank['minimum80']['count'],
      'primary_native_top15_votes':nr['top15']['votes'],'primary_native_min80_count':nr['minimum80']['count'],
      'primary_native_min80_votes':nr['minimum80']['votes'],'native_remainder_votes':nr['remainder']['votes'],'all93_parent_maps':len(allparents)}))
if __name__=='__main__':main()
