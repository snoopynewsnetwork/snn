#!/usr/bin/env python3
"""Deterministic complete reporting-unit ranking and source-scoped sensitivity build."""
import collections,copy,csv,gzip,json,re
from pathlib import Path
from extract_originals import HERE,STATE,dump,gzjsonl,rank
from source_controls import entity,english,num

def rows(name):return [json.loads(x) for x in gzip.decompress((HERE/f'extracts/{name}.jsonl.gz').read_bytes()).splitlines()]
def writecsv(path,rs,fields):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
def compact(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n')
def reduced(r):return {k:v for k,v in r.items() if k not in ['order']}
def pct(v,d):return f'{100*v/d:.10f}'
def ranking_for_values(rs,label):
 known=[dict(key=r['key'],label=r['label'],source_record=int(r['key'].rsplit(':',1)[1]),reported_candidate_writein_votes=r['value']) for i,r in enumerate(rs,1) if r['value'] is not None]
 out=rank(known);out['scope']=label;out['tie_rule']='descending value then ascending historical parent/native record number embedded in key; no cross-year native equivalence';out['unknown_keys']=[r['key'] for r in rs if r['value'] is None];out['universe_count']=len(rs);out['not_an_80percent_claim_for_unknown_full_universe']=bool(out['unknown_keys']);return out

def main():
 contests={y:json.loads((HERE/f'extracts/{y}-contest.json').read_text()) for y in [2024,2020,2018]}
 h=contests[2024];native=h['native_ranking'];parents=h['locality_summary_ranking']
 bridge=json.loads((HERE/'extracts/2024-parent-identities.json').read_text());pb={x['historical_literal_label']:x for x in bridge};pn={x['enr_literal_label']:x for x in bridge};pc={x['locality_code']:x for x in bridge}
 ass=json.loads((HERE/'extracts/2024-count-associations.json').read_text());bykey={x['historical_key']:x for x in ass};byid={x['enr_native_id']:x for x in ass}
 ap={r['full_native_object']['precinct']['id']:r for r in rows('2024-enr-native-objects')};export=json.loads((HERE/'extracts/2024-export-constituents.json').read_text());exbyid={r['enr_native_id']:r for r in export};exbyname={(r['locality_code'],r['enr_export_literal_name']):r for r in export}
 turnout=rows('enr-2024-turnout-report-rows');tby={}
 for r in turnout:
  if r['fields']:
   f=r['fields'];parent=pn[f['locality']];e=exbyname[parent['locality_code'],f['precinct']];tby[e['enr_native_id']]=r
 assert len(tby)==2669
 vturn={r['original_object']['id']:r for r in rows('2024-enr-voter-turnout')}
 sensitivity={};administrative={}
 localmetas=json.loads((HERE/'extracts/2024-enr-local-metadata.json').read_text())
 for field in ['ballotsCast','totalVoters']:
  sensitivity['2024-enr-local-metadata-'+field]=ranking_for_values([{'key':pb[x['parent_label']]['historical_parent_key'],'label':x['parent_label'],'value':int(x['election_metadata'][field]) if x['election_metadata'][field] is not None else None} for x in localmetas], '2024 official API locality election metadata '+field+'; all133; scope differs from annual turnout and native CSV; no inferred ballot semantics')
 named=[dict(key=r['key'],label=r['label'],parent_label=r['parent_label'],source_record=r['source_record'],reported_candidate_writein_votes=r['candidate_votes']['2']+r['candidate_votes']['3']) for r in native['order']]
 sensitivity['2024-named-only-component']=rank(named)
 sensitivity['2024-named-only-component']['scope']='Kaine+Cao reported component only; excluding all generic marks does not resolve legal named write-in universe'
 summary_html=entity('turnout-summary').decode();import html
 # Read actual HTML table; retain row text and exact cells for each required November year.
 summ={}
 for tr in re.findall(r'<tr\b[^>]*>(.*?)</tr>',summary_html,re.S|re.I):
  cells=[html.unescape(re.sub('<[^>]+>','',x)).strip() for x in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',tr,re.S|re.I)]
  if cells and cells[0] in ['2018','2020','2022','2024']:summ[int(cells[0])]={'year':int(cells[0]),'raw_cells':cells,'registered':num(cells[1]),'total_voting':num(cells[3]),'published_turnout_rate':cells[4],'absentee_included_in_total':num(cells[5]),'source_id':'turnout-summary','registration_scope':'active + inactive + overseas, as explicitly defined on page; annual November report stock; not Nov1 snapshot'}
 assert set(summ)=={2018,2020,2022,2024}
 dump(HERE/'extracts/state-turnout-summary.json',summ)
 for y in [2018,2020,2022]:
  rawrows=rows(f'turnout-{y}-rows');rs=[r for r in rawrows if r['fields']];views={}
  for dt in ['Congressional','Local']:
   sel=[r for r in rs if r['fields']['district_type']==dt];cols=rawrows[0]['cells'][6:];groups=collections.defaultdict(list)
   for r in sel:groups[r['fields']['locality']].append(r)
   views[dt]={'row_count':len(sel),'locality_count':len(groups),'source_tuple_duplicate_groups':[],'fields':{},'localities':[]}
   keys=collections.defaultdict(list)
   for r in sel:keys[tuple(r['fields'][k] for k in ['locality','precinct','district','district_type'])].append(r['source_record'])
   views[dt]['source_tuple_duplicate_groups']=[{'tuple':k,'source_records':v} for k,v in keys.items() if len(v)>1]
   for k in cols:views[dt]['fields'][k]={'observed_sum':sum(num(r['fields'][k]) for r in sel if num(r['fields'][k]) is not None),'missing_rows':[r['source_record'] for r in sel if num(r['fields'][k]) is None]}
   for label in [r['label'] for r in parents['order']]:
    p=pb[label];rr=groups[p['enr_literal_label']];values={k:(sum(num(r['fields'][k]) for r in rr if num(r['fields'][k]) is not None) if any(num(r['fields'][k]) is not None for r in rr) else None) for k in cols}
    views[dt]['localities'].append({'parent_key':p['historical_parent_key'],'label':label,'source_literal_label':p['enr_literal_label'],'source_records':[r['source_record'] for r in rr],'fields_observed_sums':values,'source_case':'observed source rows' if rr else 'unavailable: no rows in this source view','missing_field_rows':{k:[r['source_record'] for r in rr if num(r['fields'][k]) is None] for k in cols}})
  administrative[y]=views
  con=views['Congressional'];sensitivity[f'{y}-congressional-observed-turnout']=ranking_for_values([{'key':r['parent_key'],'label':r['label'],'value':r['fields_observed_sums']['TotalVoteTurnout']} for r in con['localities']],f'{y} administrative Congressional-view observed-row TotalVoteTurnout sum; all133 parents; repeated source tuples unresolved where present; not a proved disjoint ballot universe or certified final ballots')
  con['turnout_minus_annual_summary']=con['fields']['TotalVoteTurnout']['observed_sum']-summ[y]['total_voting'];con['registration_minus_annual_summary']=con['fields']['TotalRegisteredVoters']['observed_sum']-summ[y]['registered']
 dump(HERE/'extracts/administrative-turnout-controls.json',administrative)
 # November1 registration: repeated parent/state summary columns are controls, never independent records to add.
 rr=[r for r in rows('registration-2024-nov1-rows') if r['fields']];regby=collections.defaultdict(list)
 for r in rr:
  f=r['fields'];m=re.fullmatch(r'Locality: (\d{3}) (.*)',f['Locality']);assert m
  regby[m.group(1)].append(r)
 reg=[]
 for code,rs in sorted(regby.items()):
  f=rs[0]['fields'];fields=['TotalActiveVotersPrecinctLocality','TotalInActiveVotersPrecinctLocality','TotalAllVotersPrecinctLocality','TotalPrecinctsInLocality']
  assert all(all(r['fields'][k]==f[k] for r in rs) for k in fields)
  totals={k:num(f[k]) for k in fields};reg.append({'locality_code':code,'label':pc[code]['historical_literal_label'],'source_literal_locality':f['Locality'],'source_records':[r['source_record'] for r in rs],'totals':totals,'precinct_sums':{k:sum(num(r['fields'][k]) for r in rs if num(r['fields'][k]) is not None) for k in ['ActiveVoters','InactiveVoters','AllVoters']},'precinct_count':len(rs)})
 assert len(reg)==133
 regstate={k:num(rr[0]['fields'][k]) for k in ['StateTotalLocality','TotalActiveVotersLocality','TotalInActiveVotersLocality','TotalAllVotersLocality','StateTotalPrecincts']}
 assert sum(r['totals']['TotalAllVotersPrecinctLocality'] for r in reg)==regstate['TotalAllVotersLocality']
 for r in reg:
  assert r['precinct_sums']['AllVoters']==r['totals']['TotalAllVotersPrecinctLocality'];assert r['precinct_count']==r['totals']['TotalPrecinctsInLocality']
 dump(HERE/'extracts/registration-nov1-controls.json',{'scope':'2024-11-01 generated snapshot linked under October statistics; active and inactive displayed separately; military/overseas/temp source fields overlap and not added to AllVoters','state_repeated_controls':regstate,'localities':reg})
 sensitivity['2024-nov1-registration']=ranking_for_values([{'key':pb[r['label']]['historical_parent_key'],'label':r['label'],'value':r['totals']['TotalAllVotersPrecinctLocality']} for r in reg],'2024-11-01 AllVoters registration stock, not turnout')
 # 2024 source-native turnout/ballot scopes; missing fields remain null. No inferred zeros.
 metrics=['TotalVoteTurnout','TotalRegisteredVoters','Early Voting','Election Day','Mailed Absentee','Provisional','Post-Election'];turnstate={k:{'observed_sum':sum(num(r['fields'][k]) for r in tby.values() if num(r['fields'][k]) is not None),'missing_rows':[r['source_record'] for r in tby.values() if num(r['fields'][k]) is None]} for k in metrics}
 api_turn_fields={k:{'observed_sum':sum(r['original_object'][k] for r in vturn.values() if r['original_object'][k] is not None),'missing_native_count':2669-len(vturn)+sum(r['original_object'][k] is None for r in vturn.values())} for k in ['ballotsCast','voterTurnout','voterRegistration']}
 dump(HERE/'extracts/2024-turnout-scope-controls.json',{'turnout_csv':turnstate,'api_voterTurnout':api_turn_fields,'state_summary':summ[2024],'turnout_csv_minus_annual_total_voting':turnstate['TotalVoteTurnout']['observed_sum']-summ[2024]['total_voting'],'scope_warning':'Observed counts only; native nulls unresolved. Current state metadata literal ballotsCast0 remains setup/aggregate field, not substituted for turnout. API ballotsCast, API voterTurnout, CSV TotalVoteTurnout and annual Total Voting remain distinct.'})
 sensitivity['2024-native-api-ballotsCast']=ranking_for_values([{'key':r['key'],'label':r['parent_label']+' / '+r['label'],'value':int(vturn[bykey[r['key']]['enr_native_id']]['original_object']['ballotsCast']) if bykey[r['key']]['enr_native_id'] in vturn else None} for r in native['order']], '2024 native API ballotsCast observed field; 133 absent native virtual/admin entries remain unknown; distinct from local election metadata and turnout CSV')
 for metric in ['TotalVoteTurnout','TotalRegisteredVoters']:
  sensitivity['2024-native-'+metric]=ranking_for_values([{'key':r['key'],'label':r['parent_label']+' / '+r['label'],'value':num(tby[bykey[r['key']]['enr_native_id']]['fields'][metric])} for r in native['order']],f'2024 turnout CSV observed {metric}; unknown native records kept separately')
 # Source-native to parent aggregations retain every parent and every child, including nonpriority remainder.
 parentrows=[];regmap={r['label']:r for r in reg}
 for p in parents['order']:
  name=p['label'];children=[r for r in native['order'] if r['parent_key']==p['key']];tv=[tby[bykey[r['key']]['enr_native_id']] for r in children];c18=contests[2018];c20=contests[2020]
  vals={}
  for y,c in [(2018,c18),(2020,c20)]:
   lit=next(r for r in c['locality_summary_ranking']['order'] if r['label']==name);nn=[r for r in c['native_ranking']['order'] if r['parent_label']==name];vals[f'senate_{y}_locality_summary']=lit['reported_candidate_writein_votes'];vals[f'senate_{y}_native_sum']=sum(r['reported_candidate_writein_votes'] for r in nn)
  parentrows.append({'rank':p['rank'],'locality':name,'locality_code':pb[name]['locality_code'],'fips':pb[name]['fips'],'parent_key':p['key'],'senate_2024_reported_marks':p['reported_candidate_writein_votes'],'senate_2024_kaine':p['candidate_votes']['2'],'senate_2024_cao':p['candidate_votes']['3'],'senate_2024_generic_writeins':p['candidate_votes']['4'],'cumulative_votes':p['cumulative_votes'],'top15':p['rank']<=15,'parent_minimum80':p['rank']<=parents['minimum80']['count'],'native_unit_count':len(children),'native_priority_unit_count':sum(r['rank']<=native['minimum80']['count'] for r in children),'source_turnout2024_observed_sum':sum(num(r['fields']['TotalVoteTurnout']) for r in tv if num(r['fields']['TotalVoteTurnout']) is not None),'turnout2024_missing_rows':sum(r['fields']['TotalVoteTurnout']=='' for r in tv),'nov1_2024_registration':regmap[name]['totals']['TotalAllVotersPrecinctLocality'],**vals})
 writecsv(HERE/'locality-turnout.csv',parentrows,list(parentrows[0]))
 for y,c in contests.items():
  sensitivity[f'{y}-native-senate']=c['native_ranking'];sensitivity[f'{y}-locality-summary-senate']=c['locality_summary_ranking']
  if y==2018:
   vals=[dict(key=r['key'],label=r['label'],source_record=r['source_record'],reported_candidate_writein_votes=sum(n['reported_candidate_writein_votes'] for n in c['native_ranking']['order'] if n['parent_label']==r['label'])) for r in c['locality_summary_ranking']['order']];sensitivity['2018-native-aggregated-parents']=rank(vals)
 compact(HERE/'sensitivity-orders.json',sensitivity)
 unitcsv=[];units=[]
 for r in native['order']:
  a=bykey[r['key']];api=ap[a['enr_native_id']];e=exbyid[a['enr_native_id']];t=tby[a['enr_native_id']];v=vturn.get(a['enr_native_id']);p=pb[r['parent_label']]
  u={**r,'parent_locality_code':p['locality_code'],'parent_fips':p['fips'],'source_native_constituents':{'historical_csv':{'source_id':r['source_id'],'logical_record':r['source_record'],'byte_start':r['byte_start'],'byte_end_exclusive':r['byte_end_exclusive'],'literal_label':r['label'],'native_id':None,'native_id_status':'historical CSV does not publish UUID'},'enr_api':api,'enr_results_export':e,'enr_turnout_csv':t,'enr_voter_turnout':v,'association':a},'administrative_case': 'source virtual/provisional' if a['isVirtual'] else 'source isVirtual=false; reporting record, geometry not approved','source_native_id':a['enr_native_id'],'isVirtual':a['isVirtual'],'legal_named_writein_allocation':None,'current_2026_crosswalk':None}
  units.append(u)
  f=t['fields'];n=r['reported_candidate_writein_votes'];unitcsv.append({'rank':r['rank'],'unit_key':r['key'],'historical_record':r['source_record'],'locality':r['parent_label'],'locality_code':p['locality_code'],'fips':p['fips'],'historical_literal_label':r['label'],'enr_native_id':a['enr_native_id'],'enr_literal_label':a['enr_literal_label'],'source_is_virtual':a['isVirtual'],'kaine_reported':r['candidate_votes']['2'],'cao_reported':r['candidate_votes']['3'],'generic_writein_reported_marks':r['candidate_votes']['4'],'reported_candidate_writein_marks':n,'state_denominator':native['total'],'share':str(n/native['total']),'cumulative_votes':r['cumulative_votes'],'top15':r['rank']<=15,'minimum80':r['rank']<=native['minimum80']['count'],'remainder':r['rank']>native['minimum80']['count'],'turnout_csv_TotalVoteTurnout':f['TotalVoteTurnout'],'turnout_csv_TotalRegisteredVoters':f['TotalRegisteredVoters'],'api_ballotsCast':v['original_object']['ballotsCast'] if v else None,'api_voterTurnout':v['original_object']['voterTurnout'] if v else None,'blank_votes':None,'under_votes_current_api':api['full_native_object']['underVoteCount'],'over_votes_current_api':api['full_native_object']['overVoteCount']})
 writecsv(STATE/'data/county-turnout.csv',unitcsv,list(unitcsv[0]))
 contract={'schema_version':'va-turnout-source-known-v1','state':'VA','election_date':'2024-11-05','contest':'U.S. Senate; Kaine/Cao; other Class I seat','primary_universe':'all2669 literal historical CSV Precinct records; disjoint candidate/generic-mark partition reconciled through official ENR native/locality/state controls','denominator':native['total'],'denominator_label':'reported named-candidate votes + generic write-in marks; NOT ballots or proven legal named eligible votes','tie_rule':'descending exact integer reported marks; ties ascending 1-based logical record in pinned complete historical CSV including two header rows','coverage':{'locality_parents':133,'counties':95,'independent_cities':38,'native_units':2669,'api_native_objects':2669,'api_candidate_method_objects':40035,'export_candidate_rows':8055,'export_constituent_groups':2669,'export_blank_id_zero_rows_retained':48,'all_priority_and_remainder_in_arithmetic':True,'current_geometry_or_2026_identity_approved':False},'top15':native['top15'],'minimum80':native['minimum80'],'ordered_top15_keys':[r['key'] for r in units[:15]],'ordered_priority_keys':[r['key'] for r in units[:native['minimum80']['count']]],'full_all_unit_order':[r['key'] for r in units],'ordered_remainder_keys':[r['key'] for r in units[native['minimum80']['count']:]],'ordered_units':units,'parent_inventory':[{**p,'all_native_keys':[r['key'] for r in units if r['parent_key']==p['historical_parent_key']]} for p in bridge],'source_controls':'extracts/2024-primary-controls.json','full_historical_source_records':{str(y):f'extracts/{y}-all-original-rows.jsonl.gz' for y in contests},'comparator_all_orders':'sensitivity-orders.json','parent_sensitivity_order':[r['key'] for r in parents['order']],'parent_priority_keys':[r['key'] for r in parents['order'][:parents['minimum80']['count']]],'unavailable_cases':{'historical_csv_uuid':'not published; independently retained linked ENR UUIDs through count-control associations','2020_2018_native_candidate_methods':'no separate vote-channel candidate breakdown established; literal central absentee/provisional/CD labels retained, turnout-administrative methods separate','generic_writein_eligible_named_allocation':None,'2026_identity_or_geometry':None,'current_api_under_over_blank':'null under/over retained; blank absent; historical change log observations separately retained without replayed final controls','turnout_csv_2024_null_TotalVoteTurnout_rows':131,'registration_null_native_rows':133},'peer':{'peer_agent_id':None,'agreement_status':'pending unlaunched independent peer; complete pre-peer body witness required; no acceptance claimed'},'coordinator_acceptance':'pending; worker source-known exact ranking only'}
 compact(HERE/'priority-set.json',contract)
 # Human report text plus full order in linked artifacts; all133 parent order included directly.
 n=native;m=n['minimum80'];pa=parents['minimum80'];s18=contests[2018]['native_ranking'];s20=contests[2020]['native_ranking']
 report=f'''# Virginia reporting-volume ranking

Original-first research observed 2026-10-20 UTC. **The primary unit is each of the 2,669 literal 2024 Senate source records, within all 133 Virginia locality parents (95 counties and 38 independent cities).** The compatibility name `county-turnout.csv` contains those native reporting records. The 2026 election is the regular Class II seat; the 2024 Kaine–Cao Class I contest is the stated priority baseline. These are historical reported marks, not a 2026 forecast. Fractions are exact; displayed percentages are rounded to10 decimal places.

**Top 15: {n['top15']['votes']:,} / {n['total']:,} = {pct(n['top15']['votes'],n['total'])}%. Minimum descending 80% set: {m['count']:,} records, {m['votes']:,} / {n['total']:,} = {pct(m['votes'],n['total'])}%.** The preceding {m['preceding']['count']:,} records contribute {m['preceding']['votes']:,} ({pct(m['preceding']['votes'],n['total'])}%); **{m['crossing_parent']} / `{m['crossing_label']}`** ({m['crossing_key']}) adds 1,430 and crosses. The remainder is {m['remainder_count']:,} records / {m['remainder_votes']:,} marks. Sorting largest first maximizes the sum for any fixed record count, so no {m['preceding']['count']:,}-record set reaches 80%. Calculation is exact integer `5*cumulative >= 4*state_total`; source-record order breaks ties. Source: [official historical Senate CSV](https://va2.elstats.civera.com/api/download_contest/161257_table.csv?split_party=false), linked by the [official contest](https://historical.elections.virginia.gov/contest/161257).

The complete ordered minimum set, ordered remainder, every native constituent and all parent coverage are in the [dispatch contract](data/turnout/priority-set.json); the [complete 2,669-row order](data/county-turnout.csv) retains integers and flags. [Source schema](data/turnout/source/SCHEMA.md) defines fields and exact source positions. Source-known priority has **not** been accepted by the coordinator or independently agreed by a peer; peer_agent_id is null. The package is sealed before peer access for later bounded reciprocal comparison.

| Rank | Locality parent | Literal source record | Reported marks | Cumulative |
| ---: | --- | --- | ---: | ---: |
'''
 for r in units[:15]:report+=f"| {r['rank']} | {r['parent_label']} | {r['label']} | {r['reported_candidate_writein_votes']:,} | {r['cumulative_votes']:,} |\n"
 report+='''
## Primary source and candidate controls

The Department's [current primary index](https://www.elections.virginia.gov/resultsreports/election-results/) links the historical database and explains certification authority. The historical page embeds complete candidate/source objects, including its verification clock. Historical verifiedAt is2026-05-18T14:20:50Z for2024,2025-10-23T21:35:07Z for2020 and null for2018; these are database fields, not established certification dates. Its 2024 CSV and HTML are byte-identical between retained October18 originals and fresh October20 retrievals. We independently extracted the originals before reading any coordinator numeric helper or peer derivative. The [individual original pins](data/turnout/source/pinned-originals.json) and [HTTP receipts](data/turnout/source/acquisition-index.json) retain requests, redirects, status, headers, UTC retrieval, clocks, raw/stored hashes and sizes. Legacy receipts do not retain intermediate redirect headers; fresh complete receipts establish the same entities. No failure response is treated as a source-value zero.

Following the historical page's actual official link and static client routes recovered the [state Senate original](https://enr.elections.virginia.gov/results/public/api/elections/Virginia/2024NovemberGeneral/data/ballot-item/01000000-c7a0-1ae0-d0e3-08dcde4d9db3) and all133 linked locality Senate originals. They identify 2024-11-05, official=true, production=true; the state asOf is 2025-03-05T14:57:37.4930252Z, lastUpdated 2025-03-05T14:57:04.382766Z. These are publication clocks, not an independently recovered certification certificate/date. The state literal ballotsCast=0 is preserved separately and cannot be used as actual statewide ballots. No current2026 counts, cadence or crosswalk is inferred. Full-state [candidate/method reconciliation](data/turnout/extracts/2024-primary-controls.json) closes at native, locality and state levels.

| Candidate/source category | Party | Native sum = locality sum = state CSV = official ENR |
| --- | --- | ---: |
| Timothy M. Kaine, ENR cs534 | Democratic | 2,417,115 |
| Hung Cao, ENR cs535 | Republican | 2,019,911 |
| Generic Write-Ins / ENR wi-cc200 | null party; generic marks | 8,509 |
| Sum | all reported candidate/write-in marks | 4,445,535 |

Generic write-ins are **not** proven eligible named-candidate allocations. ENR marks this category isWriteIn=true, isQualifiedWriteIn=false; historical pseudocandidate is ALL_OTHER_CANDIDATES even though isWriteIn=false there. Both original objects survive. No source candidates/party keys are deduplicated or recoded. Excluding all generic marks gives a separate named-candidate denominator of4,437,026, not a resolved legal universe; a legal native80% set is unavailable. The historical HTML also retains alternate nVotesParty1 values (Kaine2,418,944/Cao2,020,475/total4,439,419) inconsistent with its displayed nVotes and with each other as a complete denominator. These unqualified fields are preserved, never substituted. Their chronology/cause remains unresolved. The current official ENR independently agrees with the selected nVotes/CSV vector.

Each historical record has one unique complete candidate vector within its explicit locality parent matching one ENR native object. This is a **count-control association**, not proof of geometric or cross-year identity. Both labels, UUID, virtual flag, source positions and full candidate/method objects remain in the contract. Parent case associations and the explicit King and Queen County ↔ KING & QUEEN COUNTY display alias are recorded; cities never join surrounding counties. ENR labels may include trailing ballot-style annotations; the unaltered names remain. All2,669 UUIDs are unique. The complete source precinct inventory also has2,669 records; these are reporting identities, not approved polygons, polling-site counts or VTDs. See [all associations](data/turnout/extracts/2024-count-associations.json) and [parent native/FIPS identities](data/turnout/extracts/2024-parent-identities.json).

The exact published bulk [Election Results CSV](https://enr.elections.virginia.gov/cdn/results/d2c804ee-4ec2-46bb-91d7-5b41526eab03/Election%20Results_e5b689ae-a931-4b8a-a5f7-7392e9571c61.csv) contains8,055 Senate candidate rows (2,685 triplets), including16 extra all-zero triplets with blank PrecinctId at eight named precincts. Every one of those48 rows survives with its source position; none is discarded or treated as a new physical precinct. Grouping the literal export locality code and name, with every constituent retained, yields2,669 count groups agreeing with the API. Named candidates use TOTAL_VOTES; the generic row uses its separate WriteInVote field (TOTAL_VOTES literal0). The [constituent ledger](data/turnout/extracts/2024-export-constituents.json) keeps native IDs, blank IDs, raw row positions and association rules.

## Methods and denominator sensitivity

All40,035 native candidate×method observations reconcile exactly through all133 parents to the15 state controls. Early Voting, Election Day, Mailed Absentee, Provisional and Post-Election group UUIDs remain source scoped. Virtual provisional source records can rank very high and need no assumed polygon. Historical under/over/ballot/registration fields absent in2024 stay unknown. The current API under/over fields are null; blank votes are unavailable. Do not label contest votes ballots cast or classify a ballots-minus-votes difference as undervotes.

| Method | Kaine | Cao | Generic marks | Total marks |
| --- | ---: | ---: | ---: | ---: |
'''
 controls=json.loads((HERE/'extracts/2024-primary-controls.json').read_text());ss=controls['state_summary']['ballotOptions']
 for i,g in enumerate(ss[0]['groupResults']):
  vs=[c['groupResults'][i]['voteCount'] for c in ss];report+=f"| {english(g['groupName'])} | {vs[0]:,} | {vs[1]:,} | {vs[2]:,} | {sum(vs):,} |\n"
 report+='''
The linked official [2024 Election Turnout CSV](https://enr.elections.virginia.gov/cdn/results/d2c804ee-4ec2-46bb-91d7-5b41526eab03/Election%20Turnout_0869920c-fc10-402c-9c5c-f335d00f3d1f.csv) has2,669 rows but131 blank TotalVoteTurnout cells and133 blank registration cells; these remain null. Its observed TotalVoteTurnout sums4,537,976, **2,662 above** the Department's separate annual Total Voting4,535,314. Its method observed sums are Early1,840,166; Election Day2,066,279; Mailed451,513; Provisional124,454; Post-Election55,564. These sum to its own reported total without explaining its difference from the annual report. The observed report total exceeds selected Senate marks by92,441; the annual report difference is89,779. Neither difference is an undervote control.

The local API voterTurnout array has2,536 records: source ballotsCast sums4,407,747, source voterTurnout4,537,976 and source voterRegistration6,434,637. The133 absent virtual/admin entries are unavailable in that array. Local election metadata sums ballotsCast4,526,538 and totalVoters6,482,067; the statewide [registration endpoint](https://enr.elections.virginia.gov/results/public/api/elections/Virginia/2024NovemberGeneral/vr) also reports6,482,067 across133 localities (active6,024,883/inactive457,184). Thus an exact all-record final-ballots80% set is not established; observed-source sensitivities retain all unknown keys explicitly. Full native ballots-versus-voterTurnout controls are [separate](data/turnout/extracts/2024-turnout-scope-controls.json).

The Department's [annual turnout report](https://www.elections.virginia.gov/resultsreports/registrationturnout-statistics/) says its figures are published after certification; Total Registered includes active, inactive and overseas voters. The report's annual stock is not automatically a fixed-day/month registration snapshot. The complete [November1,2024 registration original](https://www.elections.virginia.gov/media/registration-statistics/2024/10/csv/Daily_Registrant_Count_By_Locality_2024_11_01_054233.csv), linked under October on the [2024 index](https://www.elections.virginia.gov/resultsreports/registration-statistics/2024-registration-statistics/), has2,536 precinct records and133 parent controls. AllVoters6,374,437 = active5,888,756 + inactive485,681. Every precinct and parent sum reconciles. The source also preserves military/overseas/temp columns; they are not added again to AllVoters. This snapshot is60,200 below annual registration6,434,637 and107,630 below ENR current totalVoters6,482,067. Differences remain date/status/source scoped. Registration is a stock, not ballots or eligible-population turnout.

| Year | Annual Total Registered | Annual Total Voting | Published rate | Absentee included in Total Voting |
| ---: | ---: | ---: | --- | ---: |
'''
 for y in [2024,2022,2020,2018]:
  x=summ[y];report+=f"| {y} | {x['registered']:,} | {x['total_voting']:,} | {x['published_turnout_rate']} | {x['absentee_included_in_total']:,} |\n"
 report+='''
The separate observed-source sensitivity orders retain every unknown record and every nonpriority parent. Their80% thresholds apply only to the stated observed denominator. API parent ballotsCast is a separate source field, not a resolution of the annual/CSV discrepancy.

| Separate source universe | Top15 numerator / denominator | Minimum80 count/votes | Preceding votes | Remainder votes | Unknown records |
| --- | --- | --- | ---: | ---: | ---: |
'''
 for key in ['2024-named-only-component','2024-native-TotalVoteTurnout','2024-native-api-ballotsCast','2024-native-TotalRegisteredVoters','2024-nov1-registration','2024-enr-local-metadata-ballotsCast','2024-enr-local-metadata-totalVoters','2018-congressional-observed-turnout','2020-congressional-observed-turnout','2022-congressional-observed-turnout']:
  z=sensitivity[key];q=z['minimum80'];report+=f"| {key} | {z['top15']['votes']:,} / {z['total']:,} | {q['count']:,} / {q['votes']:,} | {q['preceding']['votes']:,} | {q['remainder_votes']:,} | {len(z.get('unknown_keys',[]))} |\n"
 report+='''
## Actual Senate midterm and same-seat comparator

Virginia held **neither Senate nor governor in2022**. Its2022 administrative turnout is separate House/local participation context, not an invented statewide contest. The actual recent Senate midterm is [2018 Kaine–Stewart–Waters](https://historical.elections.virginia.gov/contest/134055); [2020 Warner–Gade](https://historical.elections.virginia.gov/contest/144564) is the same Class II seat as2026. All133 parents, every central absentee/CD/provisional label and all2,825/2,846 literal native source records survive; no cross-year precinct mapping is assumed. Both historical HTML pages explicitly warn of conflicting official and unofficial source totals. Their arithmetic closure is not a resolution of original certification/amendment chronology. Complete CSV/HTML entities and exact fields remain pinned.

| Contest | Named candidates and party | Native/state reported vector including generic | Native total | Locality-summary total |
| --- | --- | --- | ---: | ---: |
| 2018 Senate | Kaine Democratic; Stewart Republican; Waters Libertarian | 1,910,370 / 1,374,313 / 61,565 / generic5,509 | 3,351,757 | 3,351,721 |
| 2020 Senate | Warner Democratic; Gade Republican | 2,466,500 / 1,934,199 / generic4,388 | 4,405,087 | 4,405,087 |

2018 named candidate vectors close at every level. Its generic native/state total5,509 differs from summed locality summaries5,473 by36: Fairfax City+1, Richmond City+10, Roanoke County+25 (native minus parent). Counts are unallocated and unrepaired; both full orders/denominators survive. Literal Undervotes0 throughout2018 and2020 does not establish actual ballot-universe semantics. Generic marks have no proven eligible named allocation in either year. These are source-known comparisons with published source-conflict qualifications.

| Source-known contest universe | Top15 native marks | Top15 share | Minimum80 count | Preceding count/votes | Crossing native record | Cumulative80 / remainder |
| --- | ---: | ---: | ---: | --- | --- | --- |
'''
 for y in [2024,2020,2018]:
  r=contests[y]['native_ranking'];q=r['minimum80'];report+=f"| {y} Senate native/state | {r['top15']['votes']:,} | {pct(r['top15']['votes'],r['total'])}% | {q['count']:,} | {q['preceding']['count']:,} / {q['preceding']['votes']:,} | {q['crossing_parent']} / {q['crossing_label']} | {q['votes']:,} / {q['remainder_votes']:,} |\n"
 report+='''
The2020 native top15 is dominated by large central absentee/CD groups; the much smaller2024 top15 share reflects different source grouping as well as participation. It is not evidence of a comparable change in physical geographic concentration. At statewide source-reported Senate denominators,2018 is75.3960% of2024 and2020 is99.0901% of2024 (full precision in scripts/integers). Scaling every historical volume by one common factor leaves that year's source-scoped geographic weights unchanged; it does not establish a2026 projection. All locality/native orders for each universe, source-specific registration and turnout sensitivities are in [sensitivity-orders.json](data/turnout/sensitivity-orders.json).

Complete administrative originals [2018](https://apps.elections.virginia.gov/SBE_CSV/ELECTIONS/ELECTIONTURNOUT/Turnout-2018%20November%20General.csv), [2020](https://apps.elections.virginia.gov/SBE_CSV/ELECTIONS/ELECTIONTURNOUT/Turnout-2020%20November%20General.csv) and [2022](https://apps.elections.virginia.gov/SBE_CSV/ELECTIONS/ELECTIONTURNOUT/Turnout-2022%20November%20General.csv) each cover133 localities. Local and Congressional views overlap and must never be added. Every original row/district/method/null is retained. The Congressional view supplies only an observed-row-sum sensitivity; it is not proved to be a complete disjoint ballot universe and is not substituted for annual final totals.2018 repeats13 Congressional locality/precinct/district tuples and2020 repeats2;2018 registration repeats within those rows. Every distinct source position survives without deduplication. The Local view covers127 parents in2018,132 in2020 and133 in2022; absent cases remain null. The Congressional view covers133 in each year. Curbside fields are retained separately and not added as another method to totals. Missing registration is not zero. See [all source-view controls](data/turnout/extracts/administrative-turnout-controls.json).

| Administrative Congressional view | Native rows | Observed TotalVoteTurnout | Annual difference | Observed registration | Missing registration rows |
| --- | ---: | ---: | ---: | ---: | ---: |
'''
 for y in [2018,2020,2022]:
  z=administrative[y]['Congressional'];report+=f"| {y} | {z['row_count']:,} | {z['fields']['TotalVoteTurnout']['observed_sum']:,} | {z['turnout_minus_annual_summary']:+,} | {z['fields']['TotalRegisteredVoters']['observed_sum']:,} | {len(z['fields']['TotalRegisteredVoters']['missing_rows'])} |\n"
 report+=f'''
## Separate locality-parent sensitivity

Aggregating the established2024 source records to all133 locality parents gives top15 **2,483,152 / 4,445,535 = {pct(2483152,4445535)}%**. The minimum parent set is44 localities /3,577,883 ({pct(3577883,4445535)}%);43 yield3,556,301 ({pct(3556301,4445535)}%), and Botetourt County adds21,582. All89 remaining localities contribute867,652. This parent sensitivity does not replace the1,538-native-record priority. See [all133 parent rows](data/turnout/locality-turnout.csv). Locality FIPS use Virginia51 + the official source's COUNTYFP mapFeatureId; source UUID/code scopes remain distinct. A county-equivalent FIPS is not a precinct crosswalk.

| Rank | Locality parent | 2024 Senate marks | Cumulative | Native records | Native priority records | 2018 native-sum marks | 2020 marks |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
'''
 for r in parentrows:report+=f"| {r['rank']} | {r['locality']} | {r['senate_2024_reported_marks']:,} | {r['cumulative_votes']:,} | {r['native_unit_count']} | {r['native_priority_unit_count']} | {r['senate_2018_native_sum']:,} | {r['senate_2020_native_sum']:,} |\n"
 report+='''
## Reproduction, QA and bounded gaps

Run from the repository root with Python3 standard library and bytecode disabled:

```sh
python3 -B senate/2026/virginia/data/turnout/extract_originals.py
python3 -B senate/2026/virginia/data/turnout/source_controls.py
python3 -B senate/2026/virginia/data/turnout/build_turnout.py
python3 -B senate/2026/virginia/data/turnout/validate_turnout.py
```

`acquire.py` and `acquire_localities.py` reproduce public acquisition separately; offline builds read the frozen source index and pinned full entities, never a mutable newsroom aggregate or peer discovery. Full unrelated-office data remains in original bodies without an unnecessary second derivative. The complete source change-log CSV is losslessly retained; selected Senate/contest-independent ballot/turnout entries preserve positions, original snapshot/timestamp strings and under/over controls. Timezone, full historical revision replay and certification chronology remain unresolved; a snapshot label is not asserted to be a clock or certificate. The [change-log original](https://enr.elections.virginia.gov/cdn/results/d2c804ee-4ec2-46bb-91d7-5b41526eab03/Election%20Change%20Log_8d8cefda-3e5d-49be-932d-b24063bebd27.csv) is77,397,161 raw bytes and2,573,053 stored gzip bytes: complete, never truncated. Every stored artifact is strictly below40,000,000 bytes. No dependencies/cache directories are retained.

[validation.json](data/turnout/validation.json) records whole-state candidates, all parents/native IDs, methods, distinct denominator scopes, exact minimum integer crossing and order/remainder, source/raw/asset hashes, membership, source positions, relative links and negative fixtures. The [complete asset manifest](data/turnout/asset-manifest.json) excludes only itself; the [pre-peer witness](data/turnout/pre-peer-witness.json) freezes the full body inventory before independent peer derivative access. The final seal does not digest the later manifest, avoiding reverse digest cycles. A final read-only audit follows sealing.

Material gaps remain bounded: eligible named write-in allocation; current2026 reporting/geometric compatibility; original2018/2020 certification/source-conflict chronology; unexplained turnout/registration scope differences and blank cells; final under/over/blank universe; historical change-log replay; independent peer agreement and coordinator acceptance. These do not change the exact explicitly reported2024 mark universe. No live collector, forecast, calibrated Needle, precinct polygon approval or cadence has been implemented or claimed. The old original-results directory returned403 and the obsolete original-document route404; complete failure entities and receipts remain, while the successful official historical/linked ENR alternatives supply the package. No future feed/rule/docket exhaustion is a finish gate.
'''
 # Compute comparative ratios from exact integers, avoiding hardcoded display drift.
 report=report.replace('75.3960%',f"{100*3351757/4445535:.4f}%").replace('99.0901%',f"{100*4405087/4445535:.4f}%")
 from render_prose import render_prose
 report=render_prose(report)
 (STATE/'turnout.md').write_text(report)
 from apply_review_metadata import apply
 apply(STATE,HERE)
 print('built',len(units),'native;',len(parentrows),'parents; contract bytes',(HERE/'priority-set.json').stat().st_size)
if __name__=='__main__':main()
