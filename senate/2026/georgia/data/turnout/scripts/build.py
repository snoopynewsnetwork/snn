#!/usr/bin/env python3
"""Offline Georgia turnout extraction. No data fitting, implicit zeros, deduplication or allocation."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import csv,gzip,hashlib,io,json
R=Path(__file__).resolve().parents[1]; GA=R.parent.parent; S=R/'source'
def sha(b):return hashlib.sha256(b).hexdigest()
def txt(x):
 if x is None:return ''
 if isinstance(x,str):return x
 return next((v['text']for v in x if v.get('languageId')=='en'),' | '.join(v['text']for v in x))
def writej(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def csvout(name,rows):
 assert rows,name
 buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);b=buf.getvalue().encode()
 p=R/name
 p.write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
 return {'path':str(p.relative_to(GA)),'rows':len(rows),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}
source_meta={};verified=[]
for p in sorted(S.glob('*.http.json')):
 m=json.loads(p.read_text());source_meta[m['id']]=m
 if 'error'in m:continue
 stored=(R/m['asset']).read_bytes();raw=gzip.decompress(stored)
 assert sha(stored)==m['stored_sha256'] and sha(raw)==m['raw_sha256']
 assert len(raw)==m['entity_bytes'] and len(stored)==m['stored_bytes'] and len(stored)<40000000
 verified.append(m['id'])
def local(key):
 m=source_meta[key];assert m['status']==200,(key,m)
 return json.loads(gzip.decompress((R/m['asset']).read_bytes()))
refs=json.loads((S/'shared-references.json').read_text());states={};state_sources={};source_rows=[]
for m in refs:
 b=(GA/m['path']).read_bytes();raw=gzip.decompress(b)
 assert sha(b)==m['stored_sha256'] and sha(raw)==m['raw_sha256'] and len(raw)==m['bytes']
 states[m['election_key']]=json.loads(raw);state_sources[m['election_key']]='shared:'+m['id'];source_meta['shared:'+m['id']]=m
states['2020NovGen']=local('state-2020-selected');state_sources['2020NovGen']='state-2020-selected'
EIDS=['2024NovGen','2020NovGen','2021JanFedRun','2022NovGen','2022DecGenRun']
fipsraw=gzip.decompress((S/'county-fips-2020.body.gz').read_bytes()).decode();fipsrows=[r for r in csv.DictReader(io.StringIO(fipsraw),delimiter='|')if r['STATE']=='GA']
assert len(fipsrows)==159
FIPS={r['COUNTYNAME']:r['STATEFP']+r['COUNTYFP']for r in fipsrows}
countywide={};county_rows=[];cand_rows=[];method_rows=[];native_rows=[];clocks=[];recon=[];checks=[];tables=[]
rankings={};controls=[];constituents={};native_method_controls=[];native_candidate_controls=[];candidate_crosswalk=[];method_definitions=[]

def candidate_rows(eid,fips,name,level,unitid,unitname,options,sourceid,pointer,allowed):
 keys=[]
 for ci,o in enumerate(options):
  nm=txt(o['name']);party=o.get('party') or {};key=(nm,o.get('nativeId'),party.get('abbreviation'))
  keys.append(key)
  base={'election_key':eid,'county_fips':fips,'county_name':name,'unit_level':level,'unit_id':unitid,'unit_name':unitname,'option_position':ci,'option_id':o['id'],'candidate_native_id':o.get('nativeId'),'candidate_name':nm,'party_abbreviation':party.get('abbreviation'),'party_id':party.get('id'),'party_name':txt(party.get('name')),'is_write_in':o.get('isWriteIn'),'is_qualified_write_in':o.get('isQualifiedWriteIn'),'state_option_scope':'included_in_state_summary'if nm in allowed else 'additional_county_option_excluded_from_state_summary','votes':o['voteCount'],'votes_json_type':type(o['voteCount']).__name__,'localized_candidate_name_json':json.dumps(o['name'],ensure_ascii=False),'source_id':sourceid,'source_pointer':pointer+f'/{ci}'}
  cand_rows.append(base)
  groups=o.get('groupResults',[])
  assert o['voteCount'] is None or any(g['voteCount'] is None for g in groups) or sum(g['voteCount']for g in groups)==o['voteCount'],base
  for gi,g in enumerate(groups):method_rows.append({**base,'method_position':gi,'method_id':g['groupId'],'method_name':txt(g['groupName']),'method_votes':g['voteCount'],'method_votes_json_type':type(g['voteCount']).__name__,'method_pointer':base['source_pointer']+f'/groupResults/{gi}'})
 assert len(keys)==len(set(keys)),('ambiguous repeated candidate keys',sourceid,pointer)

def ranking(rows,field):
 order=sorted(rows,key=lambda r:(-r[field],r['county_fips']));den=sum(r[field]for r in order);cum=0;out=[];cross=None
 for i,r in enumerate(order,1):
  cum+=r[field];out.append({'rank':i,'key':'GA:county:'+r['county_fips'],'county_fips':r['county_fips'],'county_name':r['county_name'],'votes':r[field],'cumulative_votes':cum,'share_exact':str(Fraction(r[field],den)),'cumulative_share_exact':str(Fraction(cum,den))})
  if cross is None and cum*5>=den*4:cross=i
 top=sum(r[field]for r in order[:15]);crossvotes=out[cross-1]['cumulative_votes'];preceding=0 if cross==1 else out[cross-2]['cumulative_votes']
 assert preceding*5<den*4<=crossvotes*5
 return {'denominator':den,'top15_votes':top,'top15_share_exact':str(Fraction(top,den)),'top15_percent':100*top/den,'minimum_count':cross,'preceding_count':cross-1,'preceding_votes':preceding,'crossing_key':out[cross-1]['key'],'crossing_name':out[cross-1]['county_name'],'crossing_votes':out[cross-1]['votes'],'priority_votes':crossvotes,'priority_share_exact':str(Fraction(crossvotes,den)),'priority_percent':100*crossvotes/den,'remainder_count':len(out)-cross,'remainder_votes':den-crossvotes,'ordered_keys':[r['key']for r in out],'priority_keys':[r['key']for r in out[:cross]],'remainder_keys':[r['key']for r in out[cross:]],'all_order':out}

for eid in EIDS:
 d=states[eid];x=d['ballotItemWithBreakdown'];ss=state_sources[eid];allowed={txt(o['name'])for o in x['summaryResults']['ballotOptions']};stateby={txt(c['locality']['name']):c for c in x['breakdownResults']}
 assert len(stateby)==len(x['breakdownResults'])==159 and set(stateby)==set(FIPS)
 candidate_rows(eid,'','Georgia','state',d['jurisdiction']['id'],'Georgia',x['summaryResults']['ballotOptions'],ss,'/ballotItemWithBreakdown/summaryResults/ballotOptions',allowed)
 for gi,g in enumerate(d['election']['countGroups']):method_definitions.append({'election_key':eid,'county_fips':'','source_id':ss,'source_pointer':f'/election/countGroups/{gi}','group_id':g['groupId'],'group_name':txt(g['groupName']),'is_from_virtual_precinct':g.get('isFromVirtualPrecinct')})
 statecand=Counter({txt(o['name']):o['voteCount']for o in x['summaryResults']['ballotOptions']});sumcand=Counter();countyapps=Counter();state_methods=Counter();sum_native=0;native_count=0;raw_app_total=0;extras=Counter();ballots=0;reg=0;rows=[];methodcompares=0
 lookup={c['jurisdictionId'].lower():c for c in d['localityElections']};childs={txt(c['name']):c for c in d['jurisdiction']['childLocalities']};regby={txt(c['localityName']):c for c in d['voterRegistration']}
 for si,c in enumerate(x['breakdownResults']):
  name=txt(c['locality']['name']);fp=FIPS[name];child=childs[name];slug=child['shortName'];key=eid+'--'+slug;cd=local(key);cx=cd['ballotItemWithBreakdown'];assert txt(cd['jurisdiction']['name'])==name,(key,txt(cd['jurisdiction']['name']),name);assert cx['id']==c['parentBallotItemId'];assert cd['election']['electionDate']==d['election']['electionDate'];assert cd['election']['isOfficialResults'] and cd['election']['isProduction']
  ce=lookup[child['id'].lower()];assert ce['id']==cd['election']['id'];assert cd['election']['totalVoters']==ce['totalVoters'];assert cd['election']['ballotsCast']==ce['ballotsCast']
  for gi,g in enumerate(cd['election']['countGroups']):method_definitions.append({'election_key':eid,'county_fips':fp,'source_id':key,'source_pointer':f'/election/countGroups/{gi}','group_id':g['groupId'],'group_name':txt(g['groupName']),'is_from_virtual_precinct':g.get('isFromVirtualPrecinct')})
  clocks.append({'election_key':eid,'county_fips':fp,'county_name':name,'source_id':key,'election_id':cd['election']['id'],'jurisdiction_id':cd['election']['jurisdictionId'],'date':cd['election']['electionDate'],'as_of':cd['election']['asOf'],'last_updated':cd['election']['lastUpdated'],'is_official':cd['election']['isOfficialResults'],'is_production':cd['election']['isProduction'],'retrieved_utc':source_meta[key]['retrieved_at_utc'],'redacting_precinct_count_groups':cd['election'].get('redactingPrecinctCountGroups'),'precinct_results_protected':cd['election'].get('precinctResultsProtected'),'hide_precincts':cd['election'].get('hidePrecincts'),'include_precinct_results':cd['election'].get('includePrecinctResults'),'include_precinct_statuses':cd['election'].get('includePrecinctStatuses')})
  for o in c['ballotOptions']:sumcand[txt(o['name'])]+=o['voteCount']
  candidate_rows(eid,fp,name,'state_county',c['locality']['id'],name,c['ballotOptions'],ss,f'/ballotItemWithBreakdown/breakdownResults/{si}/ballotOptions',allowed)
  candidate_rows(eid,fp,name,'county',cd['jurisdiction']['id'],name,cx['summaryResults']['ballotOptions'],key,'/ballotItemWithBreakdown/summaryResults/ballotOptions',allowed)
  cp={txt(o['name']):o for o in cx['summaryResults']['ballotOptions']};sp={txt(o['name']):o for o in c['ballotOptions']}
  assert sum(o['voteCount']for o in cp.values())==cx['voteTotal'];assert sum(o['voteCount']for o in sp.values())==c['voteTotal']
  for nm,o in sp.items():
   assert cp[nm]['voteCount']==o['voteCount'],(key,nm,cp[nm]['voteCount'],o['voteCount'])
   candidate_crosswalk.append({'election_key':eid,'county_fips':fp,'county_name':name,'candidate_name':nm,'join_basis':'exact returned candidate display name; counts/methods independently compared','state_option_id':o['id'],'state_native_id':o.get('nativeId'),'state_party':(o.get('party') or {}).get('abbreviation'),'county_option_id':cp[nm]['id'],'county_native_id':cp[nm].get('nativeId'),'county_party':(cp[nm].get('party') or {}).get('abbreviation'),'source_id':key})
   gm={txt(g['groupName']):g['voteCount']for g in o['groupResults']};cm={txt(g['groupName']):g['voteCount']for g in cp[nm]['groupResults']};assert gm==cm,(key,nm,gm,cm);methodcompares+=len(gm)
  for nm,o in cp.items():
   countyapps[nm]+=o['voteCount']
   if nm not in allowed:extras[nm]+=o['voteCount']
  raw_app_total+=cx['voteTotal']
  native=cd['precincts'];breaks=cx['breakdownResults'];turnouts=cd['voterTurnout'];polls=cd['pollingPlaces'];nmapping={p['id']:p for p in native};tmap={t['id']:t for t in turnouts}
  assert len(nmapping)==len(native);assert len(tmap)==len(turnouts)
  if native:
   assert len(breaks)==len(native)==cx['breakdownResultCount'];assert {b['precinct']['id']for b in breaks}==set(nmapping)==set(tmap)
   assert sum(b['voteTotal']for b in breaks)==cx['voteTotal'];nativecand=Counter();nullcand=Counter();presentcand=Counter();nativemethod=Counter();nullmethod=Counter();presentmethod=Counter()
   assert sum(t['ballotsCast']for t in turnouts)==ce['ballotsCast'];assert sum(t['voterRegistration']for t in turnouts)==ce['totalVoters']
   for ni,b in enumerate(breaks):
    pr=b['precinct'];pid=pr['id'];assert pr==nmapping[pid];t=tmap[pid];pn=txt(pr['name']);assert t['precinctName']==pn
    knownvotes=sum(o['voteCount']for o in b['ballotOptions']if o['voteCount'] is not None)
    unknownvotes=any(o['voteCount'] is None for o in b['ballotOptions'])
    assert knownvotes<=b['voteTotal'] if unknownvotes else knownvotes==b['voteTotal']
    named_options=[o for o in b['ballotOptions']if txt(o['name'])in allowed];nv=None if any(o['voteCount']is None for o in named_options)else sum(o['voteCount']for o in named_options)
    nr={'election_key':eid,'county_fips':fp,'county_name':name,'native_key':f'GA:{eid}:{fp}:precinct:{pid}','native_id':pid,'native_name':pn,'localized_native_name_json':json.dumps(pr['name'],ensure_ascii=False),'native_source_position':ni,'inventory_source_position':next(i for i,v in enumerate(native)if v['id']==pid),'precinct_order':pr.get('precinctOrder'),'reporting_status_raw':pr.get('reportingStatus'),'is_virtual_raw':pr.get('isVirtual'),'map_feature_id':pr.get('mapFeatureId'),'classification':'source_precinct; physical/combined/style/central semantics unverified','source_all_option_votes':b['voteTotal'],'state_summary_option_votes':nv,'additional_county_option_votes':None if nv is None else b['voteTotal']-nv,'under_votes_source':b.get('underVoteCount'),'over_votes_source':b.get('overVoteCount'),'blank_votes_source':None,'ballots_cast_source':t['ballotsCast'],'voter_turnout_source':t['voterTurnout'],'voter_registration_source':t['voterRegistration'],'source_id':key,'source_pointer':f'/ballotItemWithBreakdown/breakdownResults/{ni}','turnout_pointer':'/voterTurnout/'+str(next(i for i,v in enumerate(turnouts)if v['id']==pid))}
    native_rows.append(nr);constituents.setdefault(fp,[]).append(nr)
    candidate_rows(eid,fp,name,'precinct',pid,pn,b['ballotOptions'],key,f'/ballotItemWithBreakdown/breakdownResults/{ni}/ballotOptions',allowed)
    for o in b['ballotOptions']:
     nm=txt(o['name'])
     if o['voteCount'] is None:nullcand[nm]+=1
     else:nativecand[nm]+=o['voteCount'];presentcand[nm]+=1
     for g in o['groupResults']:
      mk=(nm,txt(g['groupName']))
      if g['voteCount'] is None:nullmethod[mk]+=1
      else:nativemethod[mk]+=g['voteCount'];presentmethod[mk]+=1
   for nm,o in cp.items():
    unknown=nullcand[nm];known=nativecand[nm];total=o['voteCount']
    assert known<=total if unknown else known==total
    native_candidate_controls.append({'election_key':eid,'county_fips':fp,'county_name':name,'candidate_name':nm,'county_votes':total,'native_known_sum':known,'native_numeric_cells':presentcand[nm],'native_null_cells':unknown,'county_minus_known_sum':total-known,'comparison':'partial known lower bound; unallocated'if unknown else 'exact balance','source_id':key})
   for nm,o in cp.items():
    for g in o['groupResults']:
     mk=(nm,txt(g['groupName']));unknown=nullmethod[mk];known=nativemethod[mk];total=g['voteCount']
     assert (known<=total if unknown else known==total),(key,mk,known,total,unknown)
     native_method_controls.append({'election_key':eid,'county_fips':fp,'county_name':name,'candidate_name':nm,'method_name':mk[1],'county_method_votes':total,'native_observed_method_sum':known,'native_numeric_cells':presentmethod[mk],'native_null_cells':unknown,'county_minus_known_sum':total-known,'comparison':'partial known lower bound; unallocated'if unknown else 'exact balance','source_id':key})
   native_count+=len(native);sum_native+=sum(b['voteTotal']for b in breaks)
  else:assert not breaks and not turnouts
  rg=regby.get(name,{})
  row={'election_key':eid,'election_date':d['election']['electionDate'],'contest_name':txt(x['name']),'county_fips':fp,'county_name':name,'county_key':'GA:county:'+fp,'county_slug':slug,'jurisdiction_id':child['id'],'state_locality_row_id':c['locality']['id'],'state_parent_ballot_item_id':c['parentBallotItemId'],'county_ballot_item_id':cx['id'],'state_summary_option_votes':c['voteTotal'],'county_source_all_option_votes':cx['voteTotal'],'additional_county_option_votes':cx['voteTotal']-c['voteTotal'],'ballots_cast_raw':ce['ballotsCast'],'ballots_cast_usable':int(ce['ballotsCast'])if native else None,'registration_total_raw':ce['totalVoters'],'registration_total_usable':int(ce['totalVoters'])if native else None,'active_registration_raw':rg.get('activeVoters'),'inactive_registration_raw':rg.get('inactiveVoters'),'active_inactive_usable':None,'registration_status_date':'unspecified in app; not eligible-population denominator','native_row_count':len(native),'polling_place_row_count':len(polls),'native_coverage':'complete source precinct identities/totals; candidate/method redactions retained'if native else 'unavailable in county app payload; raw zero ballot/registration placeholders not validated zeros','under_votes_source':cx.get('underVoteCount'),'over_votes_source':cx.get('overVoteCount'),'blank_votes_source':None,'state_source_id':ss,'state_source_pointer':f'/ballotItemWithBreakdown/breakdownResults/{si}','county_source_id':key}
  rows.append(row);county_rows.append(row);countywide[(eid,fp)]=row
  recon.append({'election_key':eid,'county_fips':fp,'county_name':name,'state_scope_votes':c['voteTotal'],'county_all_options':cx['voteTotal'],'extra_option_votes':cx['voteTotal']-c['voteTotal'],'shared_candidate_and_method_cells_agree':True,'native_rows':len(native),'native_all_option_sum':sum(b['voteTotal']for b in breaks)if native else None,'native_candidate_methods_agree':'known lower bounds checked; complete numeric groups balance; null cells unallocated' if native else None,'source_id':key})
  ballots+=ce['ballotsCast'];reg+=ce['totalVoters']
 assert sumcand==statecand and sum(sumcand.values())==x['voteTotal']
 assert sum(statecand.values())==x['voteTotal']
 for o in x['summaryResults']['ballotOptions']:
  for g in o['groupResults']:state_methods[txt(g['groupName'])]+=g['voteCount']
 # Each state method/candidate also reconciles to all state county cells.
 for o in x['summaryResults']['ballotOptions']:
  nm=txt(o['name']);sg={txt(g['groupName']):g['voteCount']for g in o['groupResults']};agg=Counter()
  for c in x['breakdownResults']:
   co=next(v for v in c['ballotOptions']if txt(v['name'])==nm)
   for g in co['groupResults']:agg[txt(g['groupName'])]+=g['voteCount']
  assert dict(agg)==sg
 ranking_main=ranking(rows,'state_summary_option_votes');rankings[eid]=ranking_main
 controls.append({'election_key':eid,'date':d['election']['electionDate'],'contest':txt(x['name']),'state_candidate_total':x['voteTotal'],'state_candidates':dict(statecand),'county_app_candidates':dict(countyapps),'additional_county_options':dict(extras),'county_app_total':raw_app_total,'state_methods':dict(state_methods),'county_count':len(rows),'native_rows':native_count,'native_source_option_votes':sum_native if native_count else None,'county_ballots_raw_sum':ballots,'county_registration_raw_sum':reg,'usable_ballots_registration':native_count>0,'state_ballots_raw':d['election']['ballotsCast'],'state_registration_raw':d['election']['totalVoters'],'state_as_of':d['election']['asOf'],'state_last_updated':d['election']['lastUpdated'],'state_source_id':ss,'shared_candidate_method_cells_checked':methodcompares})
 checks.append({'election_key':eid,'all159_fips':True,'state_candidate_balance':True,'state_candidate_method_balance':True,'county_app_shared_candidates_and_methods_balance':True,'native_rows':native_count,'native_balance':'total votes exact; candidate/method null cells unallocated' if native_count else 'unavailable','extra_options_preserved':dict(extras)})

for name,rows in [('county-controls.csv',county_rows),('candidate-votes.csv.gz',cand_rows),('candidate-method-votes.csv.gz',method_rows),('native-units.csv',native_rows),('source-clocks.csv',clocks),('reconciliation.csv',recon),('native-method-controls.csv',native_method_controls),('candidate-crosswalk.csv',candidate_crosswalk),('native-candidate-controls.csv',native_candidate_controls),('method-definitions.csv',method_definitions)]:tables.append(csvout(name,rows))
native_order=[];cum=0
for i,n in enumerate(sorted(native_rows,key=lambda r:(-r['source_all_option_votes'],r['county_fips'],r['native_id'])),1):
 cum+=n['source_all_option_votes'];native_order.append({'rank':i,**n,'cumulative_source_option_votes':cum})
tables.append(csvout('native-source-total-order.csv',native_order))
writej(R/'state-controls.json',controls);writej(R/'rankings.json',rankings)
main=rankings['2024NovGen'];compat=[]
for q in main['all_order']:
 fp=q['county_fips'];r=countywide[('2024NovGen',fp)];other={e:countywide[(e,fp)]['state_summary_option_votes']for e in EIDS[1:]}
 compat.append({**q,'ranking_universe':'2024 four state-summary candidates; qualified write-ins unallocated','president_2024_state_named_four':q['votes'],'president_2024_county_all_options':r['county_source_all_option_votes'],'county_extra_disqualified_option_votes':r['additional_county_option_votes'],'qualified_writein_2024':None,'ballots_cast_2024':r['ballots_cast_usable'],'registration_app_total_2024':r['registration_total_usable'],'senate_regular_2020_november':other['2020NovGen'],'senate_regular_2021_january_runoff':other['2021JanFedRun'],'senate_otherseat_2022_november':other['2022NovGen'],'senate_otherseat_2022_december_runoff':other['2022DecGenRun'],'top15_named_scope':q['rank']<=15,'minimum80_named_scope':q['rank']<=main['minimum_count'],'native_units_2024':r['native_row_count'],'county_slug':r['county_slug'],'native_jurisdiction_id':r['jurisdiction_id'],'state_locality_row_id':r['state_locality_row_id'],'parent_ballot_item_id':r['state_parent_ballot_item_id']})
buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=list(compat[0]));w.writeheader();w.writerows(compat);(GA/'data/county-turnout.csv').write_text(buf.getvalue())
# Exact scope-specific sensitivities. They must never be mistaken for a full valid-candidate allocation.
rows24=[countywide[('2024NovGen',q['county_fips'])]for q in main['all_order']]
sens={field:ranking(rows24,field)for field in ['county_source_all_option_votes','ballots_cast_usable','registration_total_usable']}
for eid in EIDS[1:]:sens[eid]=rankings[eid]
writej(R/'sensitivity.json',sens)
wi={'source_url':'https://sos.ga.gov/sites/default/files/forms/Write%20In%20Certification%20File%2011222024.pdf','publication_title':'Final Tally of Qualified Write-In Candidates for the November 5, 2024, General Election','observation_type':'independently read official web-parser PDF; original download403; not original bytes','county_allocation':None,'method_allocation':None,'candidates':[{'name':nm,'votes':v,'party':None,'is_qualified_write_in':True}for nm,v in [('Brian Kienitz',13),('Nomusa Venita Smith',3),('Peter Sonski',730),('Jay J Bowman',30),('President R Boddie',14),('Shiva Ayyadurai',37),('Susan Maude Buscher',3),('Emily Mathews',19),('André Ramon McNeil Sr',9)]],'total':858,'named_four_plus_qualified_total':main['denominator']+858,'same_vintage_county_allocation_verified':False}
assert sum(o['votes']for o in wi['candidates'])==858
fec=json.loads((S/'fec-georgia-observation.json').read_text());assert fec['named_four']==main['denominator'];assert fec['full_candidate_votes']==main['denominator']+858;assert 37+30+730+61==858
wi.update({'full_state_candidate_votes_corroborated':5250905,'fec_primary_observation':'source/fec-georgia-observation.json','full_state_universe_verified':True,'county_allocation_still_unavailable':True})
writej(R/'qualified-writeins-observation.json',wi)
D=main['denominator']+858;T=main['top15_votes'];bounds={'assumption':'858 is complete additive qualified-write-in pool at compatible vintage; no county allocation inferred','full_denominator':D,'top15_share_lower_exact':str(Fraction(T,D)),'top15_share_upper_exact':str(Fraction(T+858,D)),'max_possible_top43_votes':main['preceding_votes']+858,'threshold_ceiling':(4*D+4)//5,'named_top44_votes_without_any_writeins':main['priority_votes'],'minimum_count_robust':main['preceding_votes']+858<4*D/5<=main['priority_votes'],'exact_full_candidate_order_verified':False,'minimum44_membership_verified':True}
liberty=json.loads((S/'liberty-bound-observation.json').read_text());lr=countywide[('2024NovGen','13179')];assert sum(o['votes']for o in liberty['named_four'])==lr['state_summary_option_votes']==23028;assert liberty['ballots_cast']==lr['ballots_cast_usable']==23258
assert liberty['ballots_cast']-lr['state_summary_option_votes']==230<252;assert 22353+858<23280
bounds.update({'conditional_membership_proven_same_named44':True,'proof_assumptions':['FEC full statewide5250905 equals namedfour5250047 plus qualified858, corroborating SOS9name certification','Liberty23258officialcompleteballots and23028namedvotes match current app; no subsequently increased incompatible Liberty ballot control established'],'full_state_pool_primary_corroborated':True,'fec_primary_observation':'source/fec-georgia-observation.json','liberty_extra_valid_upper_bound':230,'liberty_max_valid_votes':23258,'habersham_named_lower_bound':23280,'remaining_outsider_max':22353+858,'full_candidate_exact_order_known':False,'full_candidate_exact_shares_known':False,'primary_bound_observation':'source/liberty-bound-observation.json','conditional_minimum44_unordered_keys':main['priority_keys']})
writej(R/'writein-bounds.json',bounds)
coverage=[]
for q in main['all_order']:
 fp=q['county_fips'];r=countywide[('2024NovGen',fp)];cs=[n for n in constituents.get(fp,[])if n['election_key']=='2024NovGen']
 coverage.append({**q,'source_jurisdiction_id':r['jurisdiction_id'],'source_locality_row_id':r['state_locality_row_id'],'county_slug':r['county_slug'],'parent_ballot_item_id':r['state_parent_ballot_item_id'],'native_coverage':'all returned 2024 precinct identities/totals; candidate/method redactions retained; no2026 equivalence asserted','constituent_count':len(cs),'constituents':[{'key':n['native_key'],'native_id':n['native_id'],'native_name':n['native_name'],'source_position':n['native_source_position'],'source_precinct_order':n['precinct_order'],'is_virtual_raw':n['is_virtual_raw'],'classification':n['classification'],'state_summary_option_votes':n['state_summary_option_votes'],'source_all_option_votes':n['source_all_option_votes'],'source_id':n['source_id'],'source_pointer':n['source_pointer'],'geometry_status':'not acquired by turnout worker; current approval unavailable'}for n in cs],'administrative_cases':[{'case':'voting_method','status':'all returned candidate/method cells retained separately; methods are components, not additional reporting geographies'},{'case':'polling_places','status':'0 source rows; unavailable, not proof of no physical polling sites'},{'case':'combined/central/ballot_style','status':'source calls every row precinct and isVirtual=false; finer semantics unverified; do not classify by name'},{'case':'2020/2021/2022_native','status':'county app payloads have no actual finer rows; unavailable, raw placeholders retained'},{'case':'qualified_writeins','status':'858 statewide pool lacks county/native/method allocation'}]})
contract={'schema_version':'ga-turnout-priority-v1','state':'GA','research_date':'2026-10-18','priority_contest':{'election_key':'2024NovGen','date':'2024-11-05','name':'President of the US'},'status':'full statewide candidate universe verified; minimum44 membership proven from ballot bound; exact full-candidate internal/all159 order and shares unavailable; coordinator acceptance is external at the path-only reference','coordinator_accepted':False,'independent_peer_agreement':{'status':json.loads((R/'peer-agreement.json').read_text())['status']if (R/'peer-agreement.json').exists()else'pending','path':'peer-agreement.json','peer_agent_id':'9081a355-f2cc-4c66-8b2e-dbdf11066aa7'},'ranking_universe':'four statewide app summary candidates; all159 counties; no qualified-write-in county allocation; extra local disqualified options separate','full_candidate_priority_order':None,'full_candidate_priority_keys':None,'conditional_full_candidate_minimum_set_unordered_keys':main['priority_keys'],'conditional_membership_basis':'FEC corroborated5250905 full statewide pool plus compatible official Liberty ballot cap; see writein-bounds.json; exact internal/all159 order and shares unknown','coordinator_membership_proof_reference_path':'../coordinator-priority-membership-review.json','coordinator_formal_acceptance_reference':'data/coordinator-priority-acceptance.json' ,'ranking':main,'ordered_priority_keys':main['priority_keys'],'complete_ordered_keys':main['ordered_keys'],'remainder_keys':main['remainder_keys'],'coverage':coverage,'conditional_writein_bounds':bounds,'disjoint_hierarchy':{'state':'Georgia','ranking_units':'159 counties once each; consolidated city/counties remain within their county','constituents':'2024 election-scoped source precinct GUIDs; precinct sums replace county parents when analyzing at native level','voting_methods':'components of each candidate, never additional geographic units'},'native_total':len(native_rows),'geographic_approval':'not current2026 boundaries or official-results dispatch approval'}
contract_bytes=(json.dumps(contract,indent=2,ensure_ascii=False)+'\n').encode()
freeze_path=R/'contract-freeze.json'
if freeze_path.exists():
 freeze=json.loads(freeze_path.read_text());assert sha(contract_bytes)==freeze['sha256']and len(contract_bytes)==freeze['bytes'];assert (R/'priority-set.json').read_bytes()==contract_bytes
else:(R/'priority-set.json').write_bytes(contract_bytes)
writej(R/'extraction-summary.json',{'tables':tables,'checks':checks,'verified_owned_originals':len(verified),'verified_shared_state_originals':len(refs),'county_requests':len(json.loads((S/'requests-counties.json').read_text())),'candidate_rows':len(cand_rows),'candidate_method_rows':len(method_rows),'native_rows':len(native_rows),'complete_candidate_geographic_rank':'unresolved; see writein-bounds.json'})
print(json.dumps({'tables':tables,'state_controls':controls,'named_scope_priority':{k:v for k,v in main.items()if k not in ['all_order','ordered_keys','priority_keys','remainder_keys']},'bounds':bounds},indent=2))
