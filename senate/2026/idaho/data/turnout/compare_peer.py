#!/usr/bin/env python3
"""Bounded reciprocal QA of immutable peer extraction snapshots, not a new extraction.
Own original counts/keys are never replaced by peer fields. No peer/shared writes.
"""
from pathlib import Path
from collections import Counter,defaultdict
from html.parser import HTMLParser
import csv,gzip,hashlib,json,tarfile,io,re
D=Path(__file__).resolve().parent;S=D.parent.parent;Q=D/'peer-qa';P=Q/'peer-snapshot';H=lambda b:hashlib.sha256(b).hexdigest()
def j(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def c(p):return list(csv.DictReader(p.open()))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.cell=None;self.row=[];self.table=[];self.tables=[]
 def handle_starttag(self,t,a):
  if t=='table':self.table=[]
  if t=='tr':self.row=[]
  if t in ['td','th']:self.cell=[]
 def handle_data(self,s):
  if self.cell is not None:self.cell.append(s)
 def handle_endtag(self,t):
  if t in ['td','th']and self.cell is not None:self.row.append(''.join(self.cell).strip());self.cell=None
  if t=='tr'and self.row:self.table.append(self.row)
  if t=='table':self.tables.append(self.table)
def main():
 pins=j(Q/'peer-snapshot-manifest.json')
 for r in pins['files']:
  b=(D/r['snapshot']).read_bytes();assert len(b)==r['bytes']and H(b)==r['sha256']
 witness=j(Q/'pre-peer-witness.json');wb=(D/witness['archive']).read_bytes();assert H(wb)==witness['archive_sha256'];tar=tarfile.open(fileobj=io.BytesIO(gzip.decompress(wb)))
 for r in witness['files']:b=tar.extractfile(r['path']).read();assert len(b)==r['bytes']and H(b)==r['sha256']
 failures=[];counts=Counter();differences=[]
 def eq(kind,own,peer,pos):
  counts[kind]+=1
  if own!=peer:failures.append(dict(field=kind,position=pos,own=own,peer=peer))
 ownrefs={r['id']:r for r in j(D/'source/reused-originals.json')};peerrefs={r['id']:r for r in j(P/'source/reused-originals.json')}
 for sid,r in peerrefs.items():
  f=S/'data/baselines'/r['relative_path'];b=f.read_bytes();assert H(b)==r['stored_sha256']and H(gzip.decompress(b))==r['raw_sha256']
  if sid in ownrefs:
   for field in ['url','final_url','raw_sha256','stored_sha256','bytes','retrieved_at_utc','status','headers']:eq('shared_original_'+field,ownrefs[sid][field],r[field],sid)
 # Construct complete owned original-cell lookup from frozen own extraction, not peer values.
 books=[j(D/'source/2024-races-rows.json.gz'),j(D/'source/2024-stats-rows.json.gz')]+j(D/'source/historical-workbook-rows.json.gz');cells={};sheetmeta={};rows={}
 for b in books:
  for sh in b['sheets']:
   sheetmeta[(b['source_id'],b['archive_member'],sh['sheet'])]=(sh['member'],b['original_sha256'])
   for r in sh['rows']:
    key=(b['source_id'],b['archive_member'],sh['sheet'],r['row']);rows[key]=r
    for col,value in r['cells'].items():
     x=r['cell_metadata'][col];cells[key+(col,)]=dict(address=x['address'],value=value,type=x['type'],style=x['style'],raw_v=x['raw_value'],formula=x['formula'])
 own24=c(D/'native-2024-candidate-positions.csv');ownhist=j(D/'historical-candidate-positions.json.gz');owncontrols=c(D/'historical-county-candidate-controls.csv');pos24={(r['source_id'],None,r['sheet'],int(r['source_row']),'G'):r for r in own24};ph={(r['source_id'],r['archive_member'],r['sheet'],r['source_row'],re.sub(r'\d','',r['cell'])):r for r in ownhist};pc={(r['source_id'],r['archive_member'],r['sheet'],int(r['source_row']),re.sub(r'\d','',r['cell'])):r for r in owncontrols}
 contests={'2024-president':(2024,'President'),'2020-senate-II':(2020,'Senate_Class_II'),'2020-president':(2020,'President'),'2022-senate-III':(2022,'Senate_Class_III'),'2022-governor':(2022,'Governor')}
 headers={'2020-senate-II':('IJKL',6,5,5,4),'2020-president':('BCDEFGH',6,5,5,4),'2022-senate-III':('BCDEF',6,5,4,3),'2022-governor':('BCDEFG',7,6,5,4)}
 peers=j(P/'source/candidate-positions.json.gz');peerposindex={(r['contest'],r['source_id'],r['archive_member'],r['worksheet'],r['row'],r['column']):r for r in peers};shared_hist=set();shared24=set();nulls=Counter()
 rolemap={'native':'native_candidate','county_footer':'overlapping_county_footer','state_or_appendix_control':'post_county_control_or_appendix'}
 for r in peers:
  key=(r['source_id'],r['archive_member'],r['worksheet'],r['row'],r['column']);base=key[:-1];cand=r['candidate'];original=cells.get(key);row=rows[base];eq('worksheet_member',sheetmeta[key[:3]][0],r['worksheet_member'],key)
  if 'raw_cells'in r:
   eq('entire_raw_2024_cell_object',{col:cells[base+(col,)]for col in row['cells']},r['raw_cells'],key);eq('2024_vote',int(row['cells']['G']),cand['votes'],key);eq('2024_raw_candidate',row['cells']['F'],cand['name'],key);eq('2024_raw_party',row['cells'].get('E'),cand['party'],key);eq('2024_raw_header_literal',row['cells']['F'],cand['header_literal'],key)
   own=pos24[key];shared24.add(key)
   eq('2024_source_county',own['county'],r['county'],key);eq('2024_source_label',own['literal_precinct'],r['label'],key);eq('2024_count_value',int(own['value']),cand['votes'],key)
   expectedrole='noncandidate_category'if own['role']=='noncandidate'else'native_candidate';eq('2024_category_role',expectedrole,r['role'],key)
  else:
   eq('historical_raw_target_cell',original,r['raw_cell'],key);eq('historical_raw_label_cell',cells.get(base+('A',)),r['raw_label_cell'],key)
   iscounty='county'in r['role']and r['role']=='separate_county_control'or r['role']=='separate_state_control'
   cols,cn,cp,pn,pp=headers[r['contest']];hn,hp=(cn,cp)if iscounty else(pn,pp)
   rawheader=cells[key[:3]+(hn,key[4])]['value'];rawparty=cells[key[:3]+(hp,key[4])]['value']
   eq('historical_exact_header_literal',rawheader,cand['header_literal'],key);eq('historical_exact_party_header',rawparty,cand['party_header_literal'],key);eq('historical_party',rawparty,cand['party'],key)
   expectedvalue=None if original is None or original['value']is None or not re.fullmatch(r'\d+',original['value'])else int(original['value']);eq('historical_original_candidate_value_null',expectedvalue,cand['votes'],key)
   eq('historical_raw_unit_label',row['cells'].get('A'),r['label'],key)
   if key in ph:
    own=ph[key];shared_hist.add(key);eq('historical_own_candidate_value_null',own['value'],cand['votes'],key);eq('historical_own_raw_header',own['literal_candidate'],cand['header_literal'],key);eq('historical_own_role',rolemap[own['role']],r['role'],key)
    if own['county']is None:eq('historical_noncounty_admin_parent',None,r['county'],key)
    else:eq('historical_county_parent_representation',own['county'],r['county']+' County',key)
   elif key in pc:
    own=pc[key];eq('historical_separate_county_control',int(own['votes']),cand['votes'],key);eq('historical_separate_county_header',own['literal_candidate'],cand['name'],key);eq('historical_separate_county_party',own['literal_party'],cand['party'],key);eq('historical_county_control_parent',own['county'],r['county']+' County',key)
   else:eq('separate_state_control_role','separate_state_control',r['role'],key)
   if r['role']=='native_candidate'and cand['votes']is None:nulls[r['contest']]+=1
  eq('candidate_cell_address',r['column']+str(r['row']),cand['cell'],key)
 eq('all_2024_selected_source_positions',set(pos24),shared24,'2024');eq('all_historical_native_footer_admin_positions',set(ph),shared_hist,'historical')
 # All native contexts, native candidate/noncandidate fields, nulls, source positions and parent scope.
 peerunits=j(P/'source/native-units.json.gz');ownunits24={int(r['source_first_row']):r for r in c(D/'native-2024-president.csv')};ownhn={(r['year'],r['contest'],r['source_row']):r for r in j(D/'historical-native.json.gz')};canonical=[];methoddif=[];nativecounts=Counter()
 for r in peerunits:
  nativecounts[r['contest']]+=1;year,contest=contests[r['contest']]
  if year==2024:
   eq('native_2024_source_id','sos-2024-all-races-xlsx',r['source_id'],r['unit_id']);eq('native_2024_archive_member',None,r['archive_member'],r['unit_id']);eq('native_2024_worksheet','raw_races',r['worksheet'],r['unit_id']);eq('native_explicit_year_scope',(2024,'native'),(r['year'],r['scope']),r['unit_id'])
   o=ownunits24[r['row']];eq('native_2024_context_county',o['county'],r['county'],r['unit_id']);eq('native_2024_context_label',o['literal_precinct'],r['label'],r['unit_id']);eq('native_2024_context_source_rows',list(range(int(o['source_first_row']),int(o['source_last_row'])+1)),r['source_rows'],r['unit_id']);eq('native_2024_context_named_votes',int(o['candidate_votes']),sum(x['votes']for x in r['candidates']),r['unit_id']);eq('native_2024_context_noncandidate_votes',int(o['overvotes'])+int(o['undervotes']),sum(x['votes']for x in r['noncandidate']),r['unit_id']);key=o['key'];canonical.append(dict(peer_unit_id=r['unit_id'],canonical_key=key,county=r['county'],literal_label=r['label'],votes=sum(x['votes']for x in r['candidates']),source_rows=r['source_rows']))
   ownflag=o['literal_method_flags']or None
  else:
   o=ownhn[(year,contest,r['row'])];eq('native_historical_context_county',o['county'],r['county']+' County',r['unit_id']);eq('native_historical_context_label',o['literal_precinct'],r['label'],r['unit_id']);eq('native_historical_context_candidate_vector',o['candidate_values'],[x['votes']for x in r['candidates']],r['unit_id']);eq('native_historical_context_source_id',o['source_id'],r['source_id'],r['unit_id']);eq('native_historical_context_archive_member',o['archive_member'],r['archive_member'],r['unit_id']);eq('native_historical_context_worksheet',o['sheet'],r['worksheet'],r['unit_id']);ownflag=o['literal_method_flags']
   eq('historical_native_source_row_list',[o['source_row']],r['source_rows'],r['unit_id']);eq('native_historical_explicit_year_scope',(year,'native'),(r['year'],r['scope']),r['unit_id'])
   eq('historical_native_workbook_hash',sheetmeta[(r['source_id'],r['archive_member'],r['worksheet'])][1],r['workbook_sha256'],r['unit_id'])
  for cand in r['candidates']+r['noncandidate']:
   col=re.sub(r'\d','',cand['cell']);pp=peerposindex[(r['contest'],r['source_id'],r['archive_member'],r['worksheet'],cand['source_row'],col)];eq('native_duplicate_candidate_object_full_source_backed',pp['candidate'],cand,(r['unit_id'],col,cand['source_row']))
  peerflag=None if r['method_label_evidence']=='method_not_explicit_in_label'else r['method_label_evidence'].replace(';','|')
  if ownflag!=peerflag:methoddif.append(dict(contest=r['contest'],row=r['row'],literal_label=r['label'],own_lexical_flag=ownflag,peer_lexical_flag=peerflag,source_label_unchanged=True))
  eq('method_peer_flag_source_backed',peerflag,'|'.join(t for t in ['absentee','early','mail','provisional','central','election day']if t in r['label'].lower())or None,r['unit_id'])
 eq('native_context_counts',{'2024-president':985,'2020-senate-II':974,'2020-president':974,'2022-senate-III':999,'2022-governor':999},dict(nativecounts),'all_native')
 # Independent peer counts, source-position mapping -> canonical order. No votes imported into own ledger.
 oldpeer=c(P/'native-priority-order.csv');oldpeer_units={r['row']:r for r in peerunits if r['contest']=='2024-president'}
 for r in oldpeer:
  u=oldpeer_units[int(r['first_source_row'])];eq('earlier_peer_order_every_literal_source_row_field',(u['unit_id'],u['county'],u['label'],';'.join(str(x)for x in u['source_rows'])),(r['unit_id'],r['county'],r['literal_unit'],r['source_rows']),r['rank']);eq('earlier_peer_order_vote_and_total',(sum(x['votes']for x in u['candidates']),905057),(int(r['candidate_votes']),int(r['state_named_total'])),r['rank'])
 ownorder=c(D/'native-order.csv');canonical.sort(key=lambda r:(-r['votes'],r['canonical_key']));eq('canonical_full985_order',[r['key']for r in ownorder],[r['canonical_key']for r in canonical],'985')
 cumulative=0;reorders=[]
 byrow={r['source_rows'][0]:r for r in canonical}
 for i,(o,r)in enumerate(zip(ownorder,canonical),1):
  cumulative+=r['votes'];eq('canonical_every_rank_vote',int(o['candidate_votes']),r['votes'],i);eq('canonical_every_cumulative_vote',int(o['cumulative_votes']),cumulative,i)
  op=oldpeer[i-1]
  if int(op['first_source_row'])!=r['source_rows'][0]:reorders.append(dict(rank=i,votes=r['votes'],canonical_key=r['canonical_key'],canonical_literal_label=r['literal_label'],earlier_peer_source_row=int(op['first_source_row']),earlier_peer_literal_label=op['literal_unit']))
 eq('minimum528_membership',set(r['key']for r in ownorder[:528]),set(byrow[int(r['first_source_row'])]['canonical_key']for r in oldpeer[:528]),'528')
 contract=j(D/'priority-set.json');newmaps={};primaps={};remmaps={}
 for parent in contract['all_county_constituents']:
  f=parent['key'];cc=[r for r in canonical if r['county']==parent['county']];newmaps[f]=[r['canonical_key']for r in cc];primaps[f]=[r['canonical_key']for r in canonical[:528]if r['county']==parent['county']];remmaps[f]=[r['canonical_key']for r in canonical[528:]if r['county']==parent['county']]
 for field,m in [('ordered_child_keys_by_parent',newmaps),('ordered_priority_child_keys_by_parent',primaps),('ordered_remainder_child_keys_by_parent',remmaps)]:eq('canonical_all44_'+field,contract[field],m,field)
 eq('canonical_ordered528',contract['ordered_priority_keys'],[r['canonical_key']for r in canonical[:528]],'528');eq('canonical_ordered457_remainder',contract['ordered_remainder_keys'],[r['canonical_key']for r in canonical[528:]],'457')
 # Check each independent county/state/footer/admin candidate control, keyed by original positions.
 peercontrols=j(P/'source/controls.json.gz');owncounty={(r['county'],r['literal_party']or None,r['literal_candidate']):int(r['votes'])for r in c(D/'county-candidate-2024.csv')}
 for u in peercontrols:
  if u['contest']=='2024-president':
   eq('2024_county_control_full_source_row_coverage',sorted(int(r['source_row'])for r in own24 if r['county']==u['county']),u['source_rows'],u['county']);eq('2024_county_control_scope_and_nonadditive_position',('county',None),(u['scope'],u['row']),u['county'])
   for cat in u['candidates']+u['noncandidate']:eq('2024_all44_county_candidate_and_noncandidate_controls',owncounty[(u['county'],cat['party'],cat['name'])],cat['votes'],(u['county'],cat['name']))
  else:
   for cat in u['candidates']:
    cell=cat['cell'];col=re.sub(r'\d','',cell);eq('control_duplicate_candidate_object_full_source_backed',peerposindex[(u['contest'],u['source_id'],u['archive_member'],u['worksheet'],u['row'],col)]['candidate'],cat,(u['unit_id'],col));raw=cells.get((u['source_id'],u['archive_member'],u['worksheet'],u['row'],col));expected=None if raw is None or raw['value']is None or not re.fullmatch(r'\d+',raw['value'])else int(raw['value']);eq('historical_all_county_state_footer_admin_control_cells',expected,cat['votes'],(u['unit_id'],col))
 # Complete shared statistics raw cells and fields; owned extra nonnumeric admin headings remain separate.
 peerstats=j(P/'source/statistics-positions.json.gz');ownstat24={int(r['source_row']):r for r in c(D/'native-2024-stats.csv')+c(D/'administrative-2024-stats.csv')};ownstat20={r['source_row']:r for r in j(D/'native-2020-stats.json.gz')+j(D/'administrative-2020-stats.json.gz')};seen20=set()
 for r in peerstats:
  member=r.get('archive_member');base=(r['source_id'],member,r['worksheet'],r['row']);row=rows[base];eq('stat_entire_raw_cell_objects',{col:cells[base+(col,)]for col in row['cells']},r['raw_cells'],base)
  columns='CDEF'if r['year']==2024 else'DEFG'
  for col,field in zip(columns,['cutoff','day','registered','ballots']):eq('stat_original_integer_null_'+field,None if row['cells'].get(col)is None else int(row['cells'][col]),r[field],base)
  eq('stat_original_raw_turnout',row['cells'].get('G'if r['year']==2024 else'H'),r['source_turnout'],base)
  if r['year']==2024:
   o=ownstat24[r['row']];eq('stat_2024_nonadditive_role','overlapping_county_footer'if o['literal_precinct']=='Total'else'native',r['role'],base);eq('stat_2024_literal_county',o['county'],r['county'],base);eq('stat_2024_literal_label',o['literal_precinct'],r['label'],base)
  elif member and'_pct'in member:
   seen20.add(r['row']);o=ownstat20[r['row']];eq('stat2020_nonadditive_role',{'native':'native','county_footer':'overlapping_county_footer','state_or_appendix_control':'post_county_control'}[o['role']],r['role'],base);eq('stat_2020_literal_label',o['literal_precinct'],r['label'],base);eq('stat_2020_parent_representation',o['county'],r['county']+' County'if r['county']is not None else None,base)
 ownextra20=[dict(source_row=r,literal_label=o['literal_precinct'],role=o['role'],fields={field:o[field]for field in ['cutoff','election_day','registered','ballots']})for r,o in ownstat20.items()if r not in seen20]
 expectedextra=[1147,1151];eq('explicit_statistical_admin_headings_not_derived_by_peer',expectedextra,sorted(r['source_row']for r in ownextra20),'2020')
 # Exact residual and unmatched-zero row scope, not allocated.
 dis=j(P/'source/2024-statistics-disagreements.json');ownres=c(D/'literal-stats-race-comparisons.csv');ownnon={(r['county'],r['literal_precinct']):(int(r['source_first_row'])if'source_first_row'in r else int(r['president_source_first_row']),int(r['stats_source_row']),int(r['race_all_categories']),int(r['stats_ballots']),int(r['ballots_minus_race']))for r in ownres if int(r['ballots_minus_race'])}
 eq('all7_residual_exact_positions_and_values',ownnon,{(r['county'],r['label']):(r['race_rows'][0],r['stats_row'],r['all_category'],r['ballots'],r['ballots_minus_all_category'])for r in dis['nonzero']},'Boundary')
 eq('stats_only_zero_context',[(r['county'],r['literal_precinct'],r['source_row'],r['cutoff'],r['election_day'],r['registered'],r['ballots'])for r in contract['stats_only_contexts']],[(r['county'],r['label'],r['row'],r['cutoff'],r['day'],r['registered'],r['ballots'])for r in dis['stats_only']],'Bingham')
 # Compare all published2022 tables from the independently fetched peer raw original (not peer counts).
 acq=j(P/'source/acquisition.json');a=next(r for r in acq if r['id']=='stats-2022');path=S/'data/baselines'/a['stored_path'];rawstored=path.read_bytes();assert H(rawstored)==a['stored_sha256'];raw=gzip.decompress(rawstored);assert H(raw)==a['raw_sha256'];t=Tables();t.feed(raw.decode());own_tables=j(D/'source/stats2022-tables.json.gz');eq('all2022_original_HTML_tables_headers_literals_and_values',own_tables,t.tables,'2022GeneralStats')
 # Keep reference to exact independently fetched original, without another copy of the original body.
 external=dict(peer_path=str(path.relative_to(S)),original_sha256=H(raw),stored_sha256=H(rawstored),original_bytes=len(raw),stored_bytes=len(rawstored),requested_url=a['requested_url'],final_url=a['final_url'],retrieved_utc=a['retrieved_utc'],status=a['status'],meaning='Independently fetched2022 original compared by all literal tables; dynamic HTML body hashes may differ.',duplicate_original_saved=False)
 countycontrol=j(P/'source/historical-reconciliation.json');ownhr=j(D/'historical-reconciliation.json')
 for r in countycontrol:
  year,contest=contests[r['contest']];o=next(x for x in ownhr if x['year']==year and x['contest']==contest);eq('historical_state_candidate_control_vector',[dict(name=x['candidate'],party=x['literal_party'],votes=x['votes'])for x in o['candidates']],r['candidates'],r['contest'])
 # Mapping is a source-position mapping only: explicit row identity + exact original SHA/member/sheet.
 mapping=[dict(peer_unit_id=r['peer_unit_id'],turnout_source_position_key=r['canonical_key'],county=r['county'],literal_label=r['literal_label'],source_id='sos-2024-all-races-xlsx',original_sha256=ownrefs['sos-2024-all-races-xlsx']['raw_sha256'],archive_member=None,worksheet='raw_races',worksheet_member='xl/worksheets/sheet1.xml',source_rows=r['source_rows'])for r in canonical]
 (Q/'source-position-map.json.gz').write_bytes(gzip.compress((json.dumps(mapping,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
 output=dict(status='pass_shared_original_fields_with_explicit_presentation_differences'if not failures else'FAIL_unresolved_fields',peer_agent_id=pins['peer_agent_id'],immutable_peer_snapshot_manifest='peer-snapshot-manifest.json',pre_peer_owned_witness='pre-peer-witness.json',original_basis_preserved=True,no_peer_votes_imported=True,comparison_counts=dict(counts),total_field_checks=sum(counts.values()),unresolved_differences=failures,native_counts=dict(nativecounts),null_native_candidate_cells=dict(nulls),full985_source_position_mapping='source-position-map.json.gz',earlier_peer_literal_order_reordered_ranks=reorders,canonical_order_rule=contract['tie_rule'],canonical_order_and_maps_agree_after_explicit_peer_position_mapping=not failures,earlier_peer_order_is_not_mislabeled_canonical=True,method_lexical_flag_differences=methoddif,owned_additional_stats2020_admin_headings=ownextra20,representational_differences=['Turnout analytical keys include ID/year/contest/FIPS/source-row; peer uses contest/source-row. Exact originalSHA/member/worksheet/row mapping is explicit and changes no source native ID.','Historical county parent strings use the county-workbook raw short name on the peer versus official Census county/FIPS parent on turnout. Raw county headings/cells remain literal in both; the comparison appends County only to this explicit parent representation, not precinct or polling-place labels.','Peer candidate F:<offset> or column keys are source-local locators; turnout compares candidate party/name/header/cell objects rather than treating those keys as global candidate identities.','Raw cells/types/styles/formulas/nulls compare exactly before numerical counts. No missing cell is filled with zero.','Peer historical separate county/state candidate controls add990 source positions to turnout22770 native/footer/admin +12805 president positions; turnout original complete workbook rows independently retain every such control.','Two nonnumeric2020 statistics appendix headings (Statewide row1147,Ada County row1151) are explicitly inventoried by turnout but not separate peer statistic objects. They remain in the same pinned original, carry all four null numeric fields, and are not county/native votes.','The peer separate2020 county-workbook statewide statistics control carries county=TOTAL and role=state_control. TOTAL is its literal administrative label, not a45th county or Washington child; raw cells/values match the same original.','Literal method word flags differ only as documented; source labels and all method/statistical controls remain unchanged. These flags are not a method partition.'],independently_acquired2022_statistics_original=external,primary_vote_controls=dict(denominator=905057,top15=65391,preceding527=723753,crossing528=724515,crossing_context='Shoshone County / Osburn',crossing_votes=762,remainder_contexts=457,remainder_votes=180542),coordinator_acceptance=False,current_geography_approved=False,current_sample_scope='Only the original pinned TwinFallsLD24 primary PDF body supports its four printed names. No statewide/later write-in exhaustion, result-choice IDs or geometry acceptance follows.')
 save(Q/'comparison.json',output)
 print(json.dumps({k:v for k,v in output.items()if k in ['status','total_field_checks','unresolved_differences','method_lexical_flag_differences','owned_additional_stats2020_admin_headings']},indent=2,default=str))
 if failures:raise SystemExit(1)
if __name__=='__main__':main()
