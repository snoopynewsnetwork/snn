#!/usr/bin/env python3
"""Original-only baselines/scenarios; never imports peer numbers or rankings."""
from pathlib import Path
import json,csv,gzip,re,math
from extract_originals import D,STATE,S,E,COUNTIES,FIPS,CANDIDATES,save,sha,BY,body
from calculator import state

def csvsave(path,rows):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def jsoncol(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def typed_controls():
 raw=json.loads((E/'turnout-controls.json').read_text());out={}
 for sid,scope in raw.items():
  year=next(str(y) for y in [2024,2020,2022] if str(y) in sid);rows=[]
  for r in scope['rows']:
   if len(r['tokens'])!=5:continue
   vals=r['tokens'];name=next((c for c in COUNTIES if re.match(r'^\s*'+re.escape(c)+r'\s',r['raw'],re.I)),None)
   rows.append({**r,'county':name,'county_fips':FIPS.get(name),'registered_voters':int(vals[0].replace(',','')),'ballots_cast':int(vals[1].replace(',','')),'ballots_rejected':int(vals[2].replace(',','')),'published_percent':vals[3],'election_districts':int(vals[4].replace(',','')),'type':'county' if name else 'state-footer'})
  assert len(rows)==22
  for field in ['registered_voters','ballots_cast','ballots_rejected','election_districts']:assert sum(r[field] for r in rows if r['county'])==next(r[field] for r in rows if not r['county']),(sid,field)
  out[year]=rows
 save(E/'typed-turnout-controls.json',out);return out

def main():
 native=json.loads((E/'native-contests.json').read_text());controls=json.loads((E/'county-candidate-controls.json').read_text());ball=json.loads((E/'ballot-records.json').read_text());tc=typed_controls();counties=[];natives=[];checks=[];ledger=[]
 for scope,cs in native.items():
  for c in cs:
   v=c['footer']['votes'];N=sum(v);P=v[0]+v[1]
   candidates=[{**d,'votes':n} for d,n in zip(c['candidates'],v)]
   for j,candidate in enumerate(c['candidates']):
    total=sum(z['footer']['votes'][j] for z in cs);co=[x for x in controls[scope] if x['footer']['votes']==total];assert len(co)==1
    official=co[0];assert candidate['name'].split()[-1].upper() in '\n'.join(x['raw'] for x in official['header']).upper(),(scope,candidate)
    cell=next(r for r in official['counties'] if r['county']==c['county']);assert v[j]==cell['votes'],(scope,c['county'],candidate)
    checks.append({'scope':scope,'county':c['county'],'candidate':candidate['name'],'municipal_footer':v[j],'county_pdf_cell':cell['votes'],'pass':True})
   county={'scope':scope,'county':c['county'],'county_fips':FIPS[c['county']],'unit_key':scope+':county:'+FIPS[c['county']],'source_id':c['source_id'],'source_footer_key':c['footer']['key'],'A_name':c['candidates'][0]['name'],'A_party':c['candidates'][0]['party_ballot_label'],'A':v[0],'B_name':c['candidates'][1]['name'],'B_party':c['candidates'][1]['party_ballot_label'],'B':v[1],'other_named':sum(v[2:]),'published_candidate_total':N,'pair_votes':P,'pair_participation':P/N if N else None,'A_pair_share':v[0]/P if P else None,'A_pair_margin_pp':100*(v[0]-v[1])/P if P else None,'A_all_published_share':v[0]/N if N else None,'A_minus_B_votes':v[0]-v[1],'A_minus_B_all_published_margin_pp':100*(v[0]-v[1])/N if N else None,'plurality_name':c['candidates'][v.index(max(v))]['name'],'full_candidates_json':jsoncol(candidates),'denominator_scope':'published numeric named candidate columns; statewide eligible/generic WI not supplied'}
   counties.append(county)
   for r in c['rows']:
    vs=r['votes'];N=r['numeric_sum'];P=(vs[0] or 0)+(vs[1] or 0);nr={k:county[k] for k in ['scope','county','county_fips','A_name','A_party','B_name','B_party','denominator_scope']}
    nr.update(unit_key=r['key'],source_id=r['source_id'],page=r['page'],line=r['line'],native_label=r['label'],unit_type=r['type'],A=vs[0],B=vs[1],other_named=sum(x for x in vs[2:] if x is not None),published_candidate_total=N,pair_votes=P,pair_participation=P/N if N else None,A_pair_share=vs[0]/P if P else None,A_pair_margin_pp=100*(vs[0]-vs[1])/P if P else None,A_minus_B_votes=(vs[0] or 0)-(vs[1] or 0),literal_null_columns=jsoncol([j for j,x in enumerate(vs) if x is None]),full_candidates_json=jsoncol([{**d,'votes':n} for d,n in zip(c['candidates'],vs)]),source_row=r['raw']);natives.append(nr)
 # Candidate/ballot links are exact source-local labels and year/county only; no aliases or residual allocation.
 bmap={};ballrows=[]
 for bc in ball:
  for br in bc['rows']:
   k=(str(bc['year']),bc['county'],br['label']);assert k not in bmap;bmap[k]=br;ballrows.append(br)
 for r in counties:
  y=r['scope'].split('-')[0];control=next((x for x in tc.get(y,[]) if x['county']==r['county']),None)
  r.update(source_registered_stock=control['registered_voters'] if control else None,source_ballots_cast=control['ballots_cast'] if control else None,source_ballots_rejected=control['ballots_rejected'] if control else None,source_election_districts=control['election_districts'] if control else None,ballot_registration_control_source=control['source_id'] if control else None,ballot_control_definition='published county stock/ballots, not eligible population; active/inactive definition and exact snapshot date unestablished' if control else '2018 general ballot/registration control not in retained portfolio; candidate denominator remains complete')
 links=[]
 for r in natives:
  y=r['scope'].split('-')[0];br=bmap.get((y,r['county'],r['native_label']))
  r.update(exact_label_ballot_source_key=br['key'] if br else None,source_registered_stock=br['registered_voters'] if br else None,source_ballots_cast=br['ballots_cast'] if br else None,ballot_join_status='exact literal source label within county/year, independent publication vintage retained' if br else 'no exact linked ballot record; not zero')
  links.append({'candidate_key':r['unit_key'],'scope':r['scope'],'ballot_source_key':br['key'] if br else None,'literal_label':r['native_label'],'county':r['county'],'published_candidate_total':r['published_candidate_total'],'ballots_cast':br['ballots_cast'] if br else None,'candidate_minus_ballots':r['published_candidate_total']-br['ballots_cast'] if br and br['ballots_cast'] is not None else None,'allocation':None})
 save(D/'exact-label-ballot-links.json',links);csvsave(D/'ballot-native.csv',[{k:(jsoncol(v) if isinstance(v,(list,dict)) else v) for k,v in r.items()} for r in ballrows]);save(D/'ballot-link-summary.json',{scope:{'candidate_rows':sum(r['scope']==scope for r in links),'exact_links':sum(r['scope']==scope and r['ballot_source_key'] is not None for r in links),'no_exact_link':sum(r['scope']==scope and r['ballot_source_key'] is None for r in links)} for scope in native})
 csvsave(STATE/'data/county-baselines.csv',counties);csvsave(D/'native-baselines.csv',natives);save(E/'candidate-reconciliation.json',checks)
 # Ballot originals are independent denominators. Exact-label joins only; source disagreements are unallocated.
 for c in ball:
  year=str(c['year']);county=c['county'];footer=c['footers'];assert len(footer)==1,(year,county,len(footer))
  for field in ['registered_voters','ballots_cast','mail_ballots','provisional_ballots','election_day_provisional','early_voting_provisional']:
   observed=[r[field] for r in c['rows'] if r[field] is not None];footer_val=footer[0][field]
   if footer_val is not None:assert sum(observed)==footer_val,(year,county,field,sum(observed),footer_val)
  control=next(r for r in tc[year] if r['county']==county)
  for field in ['registered_voters','ballots_cast']:
   if footer[0][field]!=control[field]:ledger.append({'kind':'municipal-ballot-footer_vs_state-control','year':year,'county':county,'field':field,'municipal_footer':footer[0][field],'state_control':control[field],'difference':footer[0][field]-control[field],'source_rows':[footer[0]['raw'],control['raw']],'allocation':None})
 for scope in ['2024-senate','2024-president']:
  nr=[r for c in native[scope] if c['county']=='Monmouth' for r in c['rows'] if 'Neptune' in r['label']];br=[r for c in ball if c['year']==2024 and c['county']=='Monmouth' for r in c['rows'] if 'Neptune' in r['label']]
  ledger.append({'kind':'literal-Neptune-candidate_vs_ballot-labels','scope':scope,'candidate_rows':nr,'ballot_rows':br,'allocation':None,'interpretation':'Candidate-versus-ballot label/vector discrepancy remains literal; no swap or alias allocation.'})
 clerk=json.loads((E/'clerk-2020-section.json').read_text());current=[sum(c['footer']['votes'][j] for c in native['2020-senate']) for j in [0,1]]
 ledger.append({'kind':'SOS-current2020_minus_HouseClerk2020','SOS':current,'Clerk':[clerk['Booker'],clerk['Mehta']],'difference':[current[0]-clerk['Booker'],current[1]-clerk['Mehta']],'allocation':None,'cause':'not inferred from publication dates'})
 sid='2024-official-general-results-president-somerset';caption_text=gzip.decompress((E/(sid+'.layout.txt.gz')).read_bytes()).decode();caption_rows=[{'page':pn,'line':ln,'raw':l} for pn,page in enumerate(caption_text.split('\f'),1) for ln,l in enumerate(page.splitlines(),1) if 'Kenndy' in l];assert len(caption_rows)==1
 ledger.append({'kind':'literal-candidate-caption_vs_cross-publication-display','source_id':sid,'literal_caption':'Robert F. Kenndy Jr.','display_candidate':'Robert F. Kennedy Jr.','source_rows':caption_rows,'source_raw_sha256':BY[sid]['raw_sha256'],'count_or_order_change':False,'allocation':None,'interpretation':'The original Somerset printed caption omits e; standardized cross-publication display is separate. Full original caption/party/position persists; counts and column order are unchanged.'})
 save(D/'discrepancy-ledger.json',ledger)
 # Each historical contest retains its own source-native universe and electorate.
 scenarios=[]
 for scope in native:
  scenarios.append({'id':'repeat-'+scope,'source_scope':scope,'geographies':['county','native'],'volume_basis':scope+' published candidate total per native unit','mix_basis':scope+' actual native publication, no cross-year join','pair_participation':scope+' own per-unit pair/published-total','preference':scope+' own A/pair','county_volume_anchor':scope,'preference_anchor':scope,'participation_anchor':scope})
 for level,anchor in [('low','2018-senate'),('base','2024-senate'),('high','2020-senate')]:
  scenarios.append({'id':'historical-volume-'+level,'source_scope':'2024-senate','geographies':['county','native'],'volume_basis':anchor+' actual county all-published named votes','mix_basis':anchor+' county mix; within-county 2024 Senate candidate/native weights retained hypothetically','pair_participation':'2024-senate local pair/published-total; county aggregate exactly matches2024county participation','preference':'2024 Senate native preferences; all nonpriority units retained','county_volume_anchor':anchor,'preference_anchor':'2024-senate','participation_anchor':'2024-senate'})
 for anchor in ['2018-senate','2020-senate','2024-president']:
  scenarios.append({'id':'county-preference-'+anchor,'source_scope':'2024-senate','geographies':['county'],'volume_basis':'2024 Senate published candidate total per county','mix_basis':'2024 Senate actual county mix','pair_participation':'2024 Senate county pair/published-total','preference':anchor+' actual county A/pair, applied as hypothetical named-pair preference; no native cross-year identity inference','county_volume_anchor':'2024-senate','preference_anchor':anchor,'participation_anchor':'2024-senate'})
 for anchor in ['2018-senate','2020-senate','2024-president']:
  scenarios.append({'id':'county-participation-'+anchor,'source_scope':'2024-senate','geographies':['county'],'volume_basis':'2024 Senate published candidate total per county','mix_basis':'2024 Senate actual county mix','pair_participation':anchor+' county pair/published-total','preference':'2024 Senate actual county A/pair','county_volume_anchor':'2024-senate','preference_anchor':'2024-senate','participation_anchor':anchor})
 save(D/'scenario-settings.json',scenarios);rowsout=[];states=[];countyby={(r['scope'],r['county']):r for r in counties}
 for sc in scenarios:
  scope=sc['source_scope']
  for level in sc['geographies']:
   originals=[r for r in (counties if level=='county' else natives) if r['scope']==scope];us=[];meta={}
   for r in originals:
    c=countyby[scope,r['county']];volc=countyby[sc['county_volume_anchor'],r['county']];pref=countyby[sc['preference_anchor'],r['county']];part=countyby[sc['participation_anchor'],r['county']]
    scale=volc['published_candidate_total']/c['published_candidate_total'];V=r['published_candidate_total']*scale
    p=(part['pair_participation'] if sc['participation_anchor']!=scope else r['pair_participation']) or 0
    T=V*p;share=(pref['A_pair_share'] if sc['preference_anchor']!=scope else r['A_pair_share']);share=.5 if share is None else share
    # Other candidates retain explicit source-local relative weights within their own pool.
    named=json.loads(r['full_candidates_json']);oc=sum((x['votes'] or 0) for x in named[2:]);other={x['name']:(V-T)*(x['votes'] or 0)/oc if oc else 0 for x in named[2:]}
    assert abs(sum(other.values())-(V-T))<1e-6,(sc['id'],r['unit_key'])
    us.append({'key':r['unit_key'],'pair':T,'share':share});meta[r['unit_key']]={'county':r['county'],'label':r.get('native_label',r['county']),'county_fips':r['county_fips'],'V':V,'other':other,'original':r,'participation':p}
   assert len(us)==(21 if level=='county' else len([r for r in natives if r['scope']==scope]))
   for target in [0,.01]:
    calc=state(us,target);V=sum(r['V'] for r in meta.values());other={}
    for r in meta.values():
     for name,n in r['other'].items():other[name]=other.get(name,0)+n
    A=sum(r['pair']*r['share_bounded_target'] for r in calc['rows']);B=calc['pair_votes']-A;field={'A':A,'B':B,**other};leaders=[k for k,v in field.items() if abs(v-max(field.values()))<1e-6]
    states.append({'scenario':sc['id'],'level':level,'source_scope':scope,'units':len(us),'target_pair_margin':target,'published_candidate_volume':V,'pair_volume':calc['pair_votes'],'other_volume':sum(other.values()),'baseline_net':calc['baseline_net'],'unbounded_shift_share_pp':calc['unbounded_shift_pp'],'bounded_shift_share_pp':calc['bounded_shift_pp'],'clipped_units':calc['clipped_units'],'actual_net':calc['actual_net'],'target_net':calc['target_net'],'target_all_published_margin_pp':100*calc['target_net']/V,'A_votes':A,'B_votes':B,'A_all_published_share':A/V,'full_other_votes':other,'A_unique_plurality':leaders==['A'],'plurality_leaders':leaders,'minimum_positive_improvement_pp':calc['minimum_positive_improvement_pp']})
    for row in calc['rows']:
     m=meta[row['key']];rr=m['original'];P0=rr['pair_votes'];s0=rr['A_pair_share'];pr=row['selected_only_raw_share']
     rowsout.append({'scenario':sc['id'],'level':level,'source_scope':scope,'target_pair_margin':target,'county':m['county'],'county_fips':m['county_fips'],'native_label':m['label'],'unit_key':row['key'],'published_candidate_volume':m['V'],'pair_participation':m['participation'],'other_candidate_votes_json':jsoncol(m['other']),**{k:v for k,v in row.items() if k!='key'},'target_all_published_margin_pp':100*row['target_net']/m['V'] if m['V'] else None,'A_target_all_published_share':row['pair']*row['share_bounded_target']/m['V'] if m['V'] else None,'local_unit_tie_share_shift_pp':100*(.5-s0) if s0 is not None else None,'local_unit_Aplus1_share_shift_pp':100*(.505-s0) if s0 is not None else None,'local_unit_Aplus1_net_votes':.01*P0,'selected_only_A_all_published_share':pr*row['pair']/m['V'] if pr is not None and m['V'] else None})
 csvsave(D/'targets.csv',rowsout);save(D/'state-scenarios.json',states)
 # Exact source-based order for every election, ballot and registration measure, independent of peer.
 order={}
 def ordered(items,metric):
  arr=sorted([r for r in items if r[metric] is not None],key=lambda r:(-r[metric],r['key']));total=sum(r[metric] for r in arr);cum=0;result=[]
  for i,r in enumerate(arr,1):cum+=r[metric];result.append({'key':r['key'],'rank':i,'county':r['county'],'volume':r[metric],'cumulative':cum,'denominator':total,'minimum80':5*(cum-r[metric])<4*total})
  return result
 for scope,cs in native.items():order[scope]=ordered([r for c in cs for r in c['rows']],'numeric_sum')
 for year in [2024,2020,2022]:
  for measure in ['ballots_cast','registered_voters']:order[f'{year}-{measure}']=ordered([r for c in ball if c['year']==year for r in c['rows']],measure)
 save(D/'all-source-orders.json',order)
 # All21 source chains remain read-only original references, not inherited vote derivatives.
 fine={'Atlantic':['atlantic-canvass'],'Bergen':['bergen-2024-district'],'Morris':['morris-2024-7','morris-2024-8','morris-2024-9','morris-2024-10','morris-2024-11'],'Salem':['salem-2024-results','salem-2024-4','salem-2024-5'],'Sussex':['sussex-2024-archive-download-0','sussex-2024-archive-download-1','sussex-2024-archive-download-2'],'Union':['union-results-download-3']};chains=[]
 for county in COUNTIES:
  slug=county.lower().replace(' ','');cl=[{'id':sid,'receipt':r['receipt'],'body_reference':r['body_reference'],'raw_sha256':r['raw_sha256']} for sid,r in BY.items() if sid.startswith(slug+'-clerk-')]
  fs=[{'id':sid,'url':BY[sid]['receipt'].get('final_url'),'raw_sha256':BY[sid]['raw_sha256'],'body_reference':BY[sid]['body_reference']} for sid in fine.get(county,[])]
  chains.append({'county':county,'county_fips':FIPS[county],'clerk_chain_originals':cl,'official_directory_source':'county-officials','administrative_roles':'County Clerk / County Board of Elections / Superintendent or Commissioner of Registration retained distinctly in full official directory; no role substitution','finer_sources':fs,'finer_status':'historical finer constituents retained, suppression/overlap remain' if fs else 'state municipal/admin scope verified; complete finer source not established in bounded original portfolio','current_native_roster_approved':False})
 save(D/'county-chains.json',chains)
 # Every575row retains county-scoped finer evidence references, with no false per-unit crosswalk.
 p=json.loads((D/'priority-set.json').read_text());save(D/'native-hierarchy.json',{'main_scope':'state ->21 nonadditive county parents ->575 disjoint2024Senate source rows','all_units':[{'key':r['unit_key'],'county':r['county'],'county_fips':r['county_fips'],'label':r['native_label'],'type':r['unit_type'],'in_priority':r['unit_key'] in p['priority_keys'],'county_scoped_finer_sources':fine.get(r['county'],[]),'finer_unit_crosswalk':None} for r in natives if r['scope']=='2024-senate'],'county_chains_path':'county-chains.json','finer_layers_additive_to_main':False,'geometry_or_current_identity_inferred':False})
 print(json.dumps({'county_rows':len(counties),'native_rows':len(natives),'reconciled_candidate_county_cells':len(checks),'target_rows':len(rowsout),'state_scenarios':len(states),'discrepancies':len(ledger)}))
if __name__=='__main__':main()
