#!/usr/bin/env python3
"""Reciprocal original-field QA; reads peer, never imports its vote inputs."""
import collections,csv,gzip,io,json,re,zipfile
from pathlib import Path
from extract import D,NEWS,save,csvout,sha,workbook,method
from supplement import Tables
P=D.parent/'turnout'
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def main():
 checks=collections.Counter();pins=[];diff=[];maps=[]
 def peer(name):
  p=P/name;b=p.read_bytes();pins.append(dict(path='../turnout/'+name,bytes=len(b),sha256=sha(b)));return load(p)
 def eq(kind,a,b):
  checks[kind]+=1
  if a!=b:diff.append(dict(kind=kind,own=a,peer=b))
 refs=load(D/'source/reused-originals.json');raw={a['id']:gzip.decompress((D/a['relative_path']).read_bytes())for a in refs};fips=load(D/'source/county-fips.json')
 pref={a['id']:a for a in peer('source/reused-originals.json')}
 for a in refs:
  if a['id']not in pref:continue
  for field in ['url','final_url','retrieved_at_utc','status','headers','raw_sha256','stored_sha256','bytes']:eq('original_receipt_'+field,a[field],pref[a['id']][field])
 # Complete raw objects, not just target candidate values, checked against original XML.
 def rawcompare(own,theirs):
  for sh in theirs['sheets']:
   os=own[sh['sheet']];eq('worksheet_member',os['member'],sh['member']);eq('source_row_sequence',[r['row']for r in os['rows']],[r['row']for r in sh['rows']])
   for a,b in zip(os['rows'],sh['rows']):
    eq('complete_resolved_cell_dictionary',{k:c['value']for k,c in a['cells'].items()},b['cells'])
    eq('complete_cell_metadata_dictionary',{k:dict(address=c['address'],type=c['type'],style=c['style'],raw_value=c['raw_v'],formula=c['formula'])for k,c in a['cells'].items()},b['cell_metadata'])
 for sid,name in [('sos-2024-all-races-xlsx','source/2024-races-rows.json.gz'),('sos-2024-turnout-xlsx','source/2024-stats-rows.json.gz')]:
  theirs=peer(name);eq('original_sha256',sha(raw[sid]),theirs['original_sha256']);rawcompare(workbook(raw[sid]),theirs)
 for theirs in peer('source/historical-workbook-rows.json.gz'):
  z=zipfile.ZipFile(io.BytesIO(raw[theirs['source_id']]));b=z.read(theirs['archive_member']);eq('historical_original_sha256',sha(b),theirs['original_sha256']);rawcompare(workbook(b),theirs)
 units=load(D/'source/native-units.json.gz');controls=load(D/'source/controls.json.gz');positions=load(D/'source/candidate-positions.json.gz');stats=load(D/'source/statistics-positions.json.gz')
 tc={'2020-senate-II':'Senate_Class_II','2020-president':'President','2022-senate-III':'Senate_Class_III','2022-governor':'Governor'}
 hist=peer('historical-native.json.gz');ha=peer('historical-administrative-controls.json.gz');hp=peer('historical-candidate-positions.json.gz');hx={(r['year'],r['contest'],r['source_row']):r for r in hist+ha};hpx={(r['year'],r['contest'],r['source_row'],r['cell']):r for r in hp};methoddiff=[]
 for u in units:
  if u['year']==2024:continue
  r=hx[u['year'],tc[u['contest']],u['row']];eq('native_historical_label',u['label'],r['literal_precinct']);eq('native_historical_county',u['county']+' County',r['county']);eq('native_candidate_vector',[c['votes']for c in u['candidates']],r['candidate_values'])
  for field,pfield in [('source_id','source_id'),('archive_member','archive_member'),('worksheet','sheet')]:eq('native_'+field,u[field],r[pfield])
  ownflag=None if u['method_label_evidence']=='method_not_explicit_in_label'else u['method_label_evidence'].replace(';','|')
  if ownflag!=r['literal_method_flags']:methoddiff.append(dict(contest=u['contest'],source_row=u['row'],literal_label=u['label'],own=ownflag,peer=r['literal_method_flags']))
  maps.append(dict(own_unit_id=u['unit_id'],peer_key=r['key'],source_id=u['source_id'],archive_member=u['archive_member'],workbook_sha256=u['workbook_sha256'],worksheet=u['worksheet'],row=u['row'],label=u['label']))
 for x in positions:
  if x['contest']=='2024-president':continue
  if x['role']in ['separate_county_control','separate_state_control']:continue
  y=hpx[int(x['contest'][:4]),tc[x['contest']],x['row'],x['candidate']['cell']]
  for field,a,b in [('historical_value_null',x['candidate']['votes'],y['value']),('historical_candidate_header',x['candidate']['header_literal'],y['literal_candidate']),('historical_party',x['candidate']['party_header_literal'],y['literal_party']),('raw_cell_present',x['raw_cell']is not None,y['raw_cell_present']),('raw_cell_value',None if x['raw_cell']is None else x['raw_cell']['value'],y['raw_resolved_value'])]:eq(field,a,b)
 # Own county and state control values are independently rechecked by raw cells above.
 pc=list(csv.DictReader((P/'native-2024-candidate-positions.csv').open()));pins.append(dict(path='../turnout/native-2024-candidate-positions.csv',sha256=sha((P/'native-2024-candidate-positions.csv').read_bytes()),bytes=(P/'native-2024-candidate-positions.csv').stat().st_size));px={int(r['source_row']):r for r in pc}
 for x in positions:
  if x['contest']!='2024-president':continue
  r=px[x['row']];c=x['candidate'];eq('2024_candidate',c['name'],r['literal_candidate']);eq('2024_party_null',c['party'],r['literal_party']or None);eq('2024_value',c['votes'],int(r['value']));eq('2024_county',x['county'],r['county']);eq('2024_label',x['label'],r['literal_precinct']);eq('2024_address',c['cell'],r['cell'])
 p24=[u for u in units if u['year']==2024];order=[]
 for u in p24:
  key=f'ID:2024:pres:{fips[u["county"]]}:{u["row"]}';order.append(dict(key=key,unit_id=u['unit_id'],county=u['county'],county_fips=fips[u['county']],literal_unit=u['label'],first_source_row=u['row'],source_rows=';'.join(map(str,u['source_rows'])),candidate_votes=sum(c['votes']for c in u['candidates'])))
  sourceflag=None if u['method_label_evidence']=='method_not_explicit_in_label'else u['method_label_evidence'].replace(';','|');peerflag=next(r['literal_method_flags']for r in pc if int(r['source_row'])==u['row'])or None
  if sourceflag!=peerflag:methoddiff.append(dict(contest=u['contest'],source_row=u['row'],literal_label=u['label'],own=sourceflag,peer=peerflag))
 order.sort(key=lambda r:(-r['candidate_votes'],r['key']));total=sum(r['candidate_votes']for r in order);cum=0
 for i,r in enumerate(order,1):before=cum;cum+=r['candidate_votes'];r.update(rank=i,cumulative=cum,state_named_total=total,priority_minimum80=before*5<total*4,top15=i<=15)
 old=list(csv.DictReader((D/'qa/pre-peer/native-priority-order.csv').open()));changes=[dict(rank=i+1,old_unit=a['unit_id'],new_unit=b['unit_id'],votes=b['candidate_votes'],old_label=a['literal_unit'],new_label=b['literal_unit'])for i,(a,b)in enumerate(zip(old,order))if a['unit_id']!=b['unit_id']]
 eq('unchanged_priority_membership',{r['unit_id']for r in old if r['priority_minimum80']=='True'},{r['unit_id']for r in order if r['priority_minimum80']})
 contract=peer('priority-set.json');keys=[r['key']for r in order];prior=[r['key']for r in order if r['priority_minimum80']];rem=[r['key']for r in order if not r['priority_minimum80']]
 parents=list(dict.fromkeys(r['county_fips']for r in order));children={f:[r['key']for r in order if r['county_fips']==f]for f in sorted(fips.values())};prchildren={f:[k for k in children[f]if k in set(prior)]for f in children};rmchildren={f:[k for k in children[f]if k not in set(prior)]for f in children}
 complete_order=[dict(rank=r['rank'],key=r['key'],votes=r['candidate_votes'],cumulative_votes=r['cumulative'],share_numerator=r['candidate_votes'],share_denominator=total,cumulative_share_numerator=r['cumulative'])for r in order]
 for field,value in [('complete_order',complete_order),('ordered_priority_keys',prior),('ordered_remainder_keys',rem),('ordered_parent_keys',parents),('ordered_child_keys_by_parent',children),('ordered_priority_child_keys_by_parent',prchildren),('ordered_remainder_child_keys_by_parent',rmchildren)]:eq(field,value,contract[field])
 csvout('native-priority-order.csv',order)
 save('priority-contract.json',dict(status='independently_constructed_canonical_source_order_pending_coordinator_acceptance',denominator=total,complete_order=complete_order,ordered_keys=keys,ordered_priority_keys=prior,ordered_remainder_keys=rem,ordered_parent_keys=parents,ordered_child_keys_by_parent=children,ordered_priority_child_keys_by_parent=prchildren,ordered_remainder_child_keys_by_parent=rmchildren,minimum80_count=len(prior),minimum80_votes=sum(r['candidate_votes']for r in order if r['priority_minimum80']),top15_votes=sum(r['candidate_votes']for r in order[:15]),tie_rule=contract['tie_rule'],coordinator_accepted=False))
 for r in order:
  u=next(u for u in p24 if u['unit_id']==r['unit_id']);maps.append(dict(own_unit_id=u['unit_id'],peer_key=r['key'],source_id=u['source_id'],archive_member=None,raw_sha256=sha(raw[u['source_id']]),worksheet=u['worksheet'],rows=u['source_rows'],label=u['label']))
 # Compare integer/null stats and raw rate for every shared source row.
 ps=[]
 for file in ['native-2024-stats.csv','administrative-2024-stats.csv']:
  b=(P/file).read_bytes();pins.append(dict(path='../turnout/'+file,bytes=len(b),sha256=sha(b)))
  for r in csv.DictReader(io.StringIO(b.decode())):ps.append(dict(year=2024,**r))
 ps+=peer('native-2020-stats.json.gz')+peer('administrative-2020-stats.json.gz')
 si={(s['year'],s.get('archive_member'),s['row']):s for s in stats}
 extra=[]
 for r in ps:
  k=(r['year'],r.get('archive_member'),int(r['source_row']))
  if k not in si:extra.append(r);continue
  s=si[k]
  for a,b in [('cutoff','cutoff'),('day','election_day'),('registered','registered'),('ballots','ballots')]:eq('statistics_'+a,s[a],None if r[b]in ['',None]else int(r[b]))
  eq('statistics_label',s['label'],r['literal_precinct']);eq('statistics_raw_turnout',s['source_turnout'],None if r['raw_turnout']==''else r['raw_turnout'])
  eq('statistics_parent',None if s['county']is None else(s['county']if s['county'].endswith(' County')else s['county']+' County'),r['county']or None)
 # Independently fetched HTML differs in clocks/body hash, compare exact table literals.
 own=next(a for a in load(D/'source/acquisition.json')if a['id']=='stats-2022');ta=Tables();ta.feed(gzip.decompress((D/own['stored_path']).read_bytes()).decode());pa=next(a for a in peer('source/requests.json')if a['id']=='stats2022');tb=Tables();tb.feed(gzip.decompress((P/pa['asset']).read_bytes()).decode());eq('all_2022_HTML_table_literals',ta.tables,tb.tables)
 save('qa/source-position-map.json.gz',maps);save('qa/peer-comparison.json',dict(status='pass_with_explicit_representation_differences'if not diff else'FAIL',comparison_counts=dict(checks),total_field_comparisons=sum(checks.values()),unresolved_differences=diff,reordered_tie_ranks=changes,lexical_method_differences=methoddiff,extra_peer_statistics_headings=extra,peer_pins=pins,independent_original_extraction_witness='pre-peer/witness.json',source_position_mapping='source-position-map.json.gz',scope_notes=['Complete original rows/cells/metadata including unrelated offices compared, not imported as vote inputs.','Own literal method inventory does not recognize ABS abbreviation; five raw labels agree despite lexical flag differences. Neither flag scheme is a method partition.','Two peer post-county stats heading records carry all four null fields and are retained in same raw original; own stats derivative omits them as numeric objects.','County-only short name versus County suffix/FIPS representation mapped explicitly from same original county headings; no native cross-year alias.','Earlier six reordered tied pairs retained in pre-peer witness; all canonical985 arrays now constructed from own counts/positions.'],coordinator_acceptance=False,current_geography_approved=False))
 print('comparisons',sum(checks.values()),'unresolved',len(diff),'reordered ranks',len(changes),'lexical flags',len(methoddiff),'extra headings',len(extra))
 assert not diff
if __name__=='__main__':main()
