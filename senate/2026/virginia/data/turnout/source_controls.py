#!/usr/bin/env python3
"""Extract original controls; preserve every selected source position; no residual allocation."""
import collections,csv,gzip,io,json,re
from pathlib import Path
from extract_originals import HERE,STATE,dump,gzjsonl,rank,sha
A=HERE/'source/acquired'
def entity(id):
 rp=A/f'{id}.receipt.json'
 ix=json.loads((HERE/'source/acquisition-index.json').read_text());entry=next(x for x in ix['receipts'] if x['receipt_path']==str(rp.relative_to(HERE)))
 assert sha(rp.read_bytes())==entry['receipt_sha256']
 r=json.loads(rp.read_text());h=r['hops'][-1];assert h['status']==200
 b=(HERE/h['body_path']).read_bytes();assert sha(b)==h['stored_sha256'];raw=gzip.decompress(b);assert sha(raw)==h['raw_sha256'];return raw

def source_csv(id,encoding='utf-8-sig',predicate=lambda cells,header:True):
 raw=entity(id);text=raw.decode(encoding);lines=raw.splitlines(keepends=True);reader=csv.reader(io.StringIO(text,newline=''));pos=0;offset=0;rs=[];header=None;total=0
 for n,cells in enumerate(reader,1):
  end=reader.line_num;chunk=b''.join(lines[pos:end]);start=offset;offset+=len(chunk);pos=end;total=n
  if n==1:header=cells
  if n==1 or predicate(cells,header):
   rs.append({'source_id':id,'source_record':n,'physical_line_end':end,'byte_start':start,'byte_end_exclusive':offset,'encoding':encoding,'raw_row':chunk.decode(encoding),'cells':cells,'fields':dict(zip(header,cells)) if n>1 and cells else None})
 assert offset==len(raw)
 gzjsonl(HERE/f'extracts/{id}-rows.jsonl.gz',rs)
 return [r for r in rs[1:] if r['fields']],{'source_id':id,'header':header,'source_logical_records':total,'retained_records':len(rs),'raw_bytes':len(raw),'raw_sha256':sha(raw),'encoding':encoding}
def english(x):return next(y['text'] for y in x if y['languageId']=='en')
def num(x):return None if x=='' else int(x.replace(',',''))
def main():
 h=json.loads((HERE/'extracts/2024-contest.json').read_text());historical=h['native_ranking']['order'];parents=h['locality_summary_ranking']['order'];pby={r['label']:r for r in parents}
 state=json.loads(entity('enr-2024-senate'));b=state['ballotItemWithBreakdown'];assert state['election']['isOfficialResults'] is True and state['election']['isProduction'] is True and state['election']['electionDate']=='2024-11-05'
 aliases={'KING & QUEEN COUNTY':'King and Queen County'}
 bridge=[];apirows=[];associations=[];methods=[];checks=[];precincts=[];voterturnout=[];localmeta=[]
 for i,local in enumerate(b['breakdownResults']):
  name=english(local['locality']['name']);label=aliases.get(name) or next(r['label'] for r in parents if r['label'].upper()==name)
  code=local['locality']['mapFeatureId'];id='enr-native-'+code;obj=json.loads(entity(id));lb=obj['ballotItemWithBreakdown'];assert obj['election']['electionDate']=='2024-11-05' and obj['election']['isProduction'] and obj['election']['isOfficialResults']
  assert obj['jurisdiction']['shortName']==local['locality']['shortName'];assert lb['id']==local['parentBallotItemId'];assert len(lb['breakdownResults'])==lb['breakdownResultCount']
  bridge.append({'historical_parent_key':pby[label]['key'],'historical_literal_label':label,'enr_literal_label':name,'locality_code':code,'enr_state_locality_object':local['locality'],'enr_jurisdiction_id':obj['jurisdiction']['id'],'enr_election_id':obj['election']['id'],'enr_parent_ballot_item_id':lb['id'],'name_association_rule':'explicit ampersand/and alias' if name in aliases else 'case-only parent display association; city/county suffix preserved','source_id':id,'source_pointer':f'/ballotItemWithBreakdown/breakdownResults/{i}','map_feature_field':state['election']['map']['featureIdField'],'fips':'51'+code,'fips_basis':'Virginia state51 + source COUNTYFP mapFeatureId; administrative county-equivalent, includes independent cities','geometry_or_crossyear_approval':False})
  localmeta.append({'source_id':id,'parent_label':label,'locality_code':code,'election_metadata':obj['election'],'jurisdiction_id':obj['jurisdiction']['id']})
  lookup=collections.defaultdict(list)
  for r in historical:
   if r['parent_label']==label:lookup[tuple(r['candidate_votes'][str(j)] for j in [2,3,4])].append(r)
  assert len(lookup)==len(lb['breakdownResults'])
  for j,r in enumerate(lb['breakdownResults']):
   cs={c['nativeId']:c['voteCount'] for c in r['ballotOptions']};assert len(cs)==len(r['ballotOptions'])==3
   v=tuple(cs[k] for k in ['cs534','cs535','wi-cc200']);matches=lookup[v];assert len(matches)==1
   old=matches[0];ptr=f'/ballotItemWithBreakdown/breakdownResults/{j}'
   record={'source_id':id,'source_pointer':ptr,'parent_label':label,'locality_code':code,'full_native_object':r}
   apirows.append(record)
   associations.append({'historical_key':old['key'],'historical_source_record':old['source_record'],'historical_literal_label':old['label'],'enr_source_id':id,'enr_source_pointer':ptr,'enr_native_id':r['precinct']['id'],'enr_literal_label':english(r['precinct']['name']),'locality_code':code,'parent_label':label,'candidate_vector':cs,'basis':'unique complete candidate vector within explicit locality parent; source labels retained as published','scope':'count-control association only; no geometry/current-identity equivalence asserted','isVirtual':r['precinct']['isVirtual']})
   assert sum(cs.values())==r['voteTotal']
   for c in r['ballotOptions']:
    assert sum(g['voteCount'] for g in c['groupResults'])==c['voteCount']
    for k,g in enumerate(c['groupResults']):methods.append({'source_id':id,'source_pointer':ptr+f'/ballotOptions/{r["ballotOptions"].index(c)}/groupResults/{k}','historical_key':old['key'],'locality_code':code,'native_id':r['precinct']['id'],'candidate_id':c['id'],'candidate_native_id':c['nativeId'],'candidate_name':c['name'],'party':c['party'],'isWriteIn':c['isWriteIn'],'isQualifiedWriteIn':c['isQualifiedWriteIn'],'full_method_object':g})
  for k,arr in [('precincts',precincts),('voterTurnout',voterturnout)]:
   for j,x in enumerate(obj[k]):arr.append({'source_id':id,'source_pointer':f'/{k}/{j}','parent_label':label,'locality_code':code,'original_object':x})
  for c in local['ballotOptions']:
   nid=c['nativeId'];s=sum(next(z['voteCount'] for z in r['ballotOptions'] if z['nativeId']==nid) for r in lb['breakdownResults']);assert s==c['voteCount']
   for g in c['groupResults']:
    n=sum(m['full_method_object']['voteCount'] for m in methods if m['locality_code']==code and m['candidate_native_id']==nid and m['full_method_object']['groupId']==g['groupId']);assert n==g['voteCount']
  assert local['voteTotal']==lb['voteTotal']==pby[label]['reported_candidate_writein_votes']
 assert len(associations)==2669 and len({r['historical_key'] for r in associations})==2669 and len({r['enr_native_id'] for r in associations})==2669
 for c in b['summaryResults']['ballotOptions']:
  nid=c['nativeId'];s=sum(next(z['voteCount'] for z in r['full_native_object']['ballotOptions'] if z['nativeId']==nid) for r in apirows);assert s==c['voteCount']
  for g in c['groupResults']:
   n=sum(m['full_method_object']['voteCount'] for m in methods if m['candidate_native_id']==nid and m['full_method_object']['groupId']==g['groupId']);assert n==g['voteCount'];checks.append({'candidate_native_id':nid,'method_id':g['groupId'],'method_name':g['groupName'],'native_sum':n,'state_control':g['voteCount'],'difference':n-g['voteCount']})
 dump(HERE/'extracts/2024-parent-identities.json',bridge);dump(HERE/'extracts/2024-count-associations.json',associations)
 gzjsonl(HERE/'extracts/2024-enr-native-objects.jsonl.gz',apirows);gzjsonl(HERE/'extracts/2024-enr-native-methods.jsonl.gz',methods);gzjsonl(HERE/'extracts/2024-enr-precinct-inventory.jsonl.gz',precincts);gzjsonl(HERE/'extracts/2024-enr-voter-turnout.jsonl.gz',voterturnout);dump(HERE/'extracts/2024-enr-local-metadata.json',localmeta)
 inventories=[]
 report,inv=source_csv('enr-2024-results-report','cp1252',lambda c,h:bool(c) and c[h.index('OfficeId')]=='cc200');inventories.append(inv)
 export_groups=collections.defaultdict(list)
 for r in report:export_groups[(r['fields']['LocalityCode'],r['fields']['PrecinctName'])].append(r)
 zero_null_rows=[r for r in report if r['fields']['PrecinctId']==''];assert len(zero_null_rows)==48
 assert all(r['fields']['TOTAL_VOTES']=='0' and r['fields']['WriteInVote']=='0' for r in zero_null_rows)
 exportcontrols={}
 for c in ['cs534','cs535','wi-cc200']:
  rs=[r for r in report if r['fields']['CandidateId']==c];exportcontrols[c]={'TOTAL_VOTES':sum(int(r['fields']['TOTAL_VOTES']) for r in rs),'WriteInVote':sum(int(r['fields']['WriteInVote']) for r in rs),'rows':len(rs)}
 assert exportcontrols['cs534']['TOTAL_VOTES']==2417115 and exportcontrols['cs535']['TOTAL_VOTES']==2019911 and exportcontrols['wi-cc200']['WriteInVote']==8509
 # Reconcile all bulk report locality/precinct-label vectors with API voterTurnout labels through exact raw names.
 vt_by=collections.defaultdict(list)
 for r in apirows:
  literal=english(r['full_native_object']['precinct']['name']);base=re.sub(r' \([^()]*\)$','',literal)
  vt_by[r['locality_code'],base].append(r)
 api_byid={r['full_native_object']['precinct']['id']:r for r in apirows};exportlinks=[]
 for (code,name),rs in export_groups.items():
  matches=vt_by[code,name];assert len(matches)==1,(code,name,len(matches))
  a=matches[0];cs={c['nativeId']:c['voteCount'] for c in a['full_native_object']['ballotOptions']}
  v={c:sum(int(r['fields']['WriteInVote' if c=='wi-cc200' else 'TOTAL_VOTES']) for r in rs if r['fields']['CandidateId']==c) for c in cs};assert v==cs
  exportlinks.append({'locality_code':code,'enr_export_literal_name':name,'enr_native_id':a['full_native_object']['precinct']['id'],'api_source_id':a['source_id'],'api_pointer':a['source_pointer'],'raw_source_records':[r['source_record'] for r in rs],'raw_precinct_ids':[r['fields']['PrecinctId'] for r in rs],'candidate_vector':v,'all_rows_retained':True,'association_rule':'exact locality code + exact bulk name after removal of one explicit trailing parenthetical API style annotation; full labels and every constituent retained; no geometry equivalence'})
 assert len(exportlinks)==2669;dump(HERE/'extracts/2024-export-constituents.json',exportlinks)
 turn,inv=source_csv('enr-2024-turnout-report');inventories.append(inv)
 for y in [2018,2020,2022]:
  _,inv=source_csv(f'turnout-{y}');inventories.append(inv)
 reg,inv=source_csv('registration-2024-nov1');inventories.append(inv)
 # Only required Senate and contest-independent ballot/registration controls are extracted from the full log.
 log,inv=source_csv('enr-2024-change-log','cp1252',lambda c,h:bool(c) and (c[h.index('Contest')]=='Member, United States Senate' or c[h.index('Contest')]==''));inventories.append(inv)
 logscope=collections.Counter((r['fields']['Contest'],r['fields']['FieldName']) for r in log)
 dump(HERE/'extracts/csv-source-inventories.json',inventories)
 dump(HERE/'extracts/2024-primary-controls.json',{'state_election_metadata':state['election'],'state_summary':b['summaryResults'],'locality_count':len(bridge),'native_count':len(apirows),'method_observation_count':len(methods),'candidate_method_controls':checks,'export_controls':exportcontrols,'export_candidate_rows':len(report),'export_blank_id_rows':len(zero_null_rows),'all_blank_id_rows_literal_zero':True,'export_constituent_groups':len(exportlinks),'precinct_inventory_objects':len(precincts),'voter_turnout_objects':len(voterturnout),'log_retained_records':len(log),'log_scope_counts':[{'contest':k[0],'field':k[1],'rows':v} for k,v in sorted(logscope.items())],'log_warning':'Timestamp strings and snapshot labels retained literally; no timezone or certification chronology inferred; not a completed revision replay.'})
 print('controls complete',len(bridge),len(apirows),len(methods),len(exportlinks),len(log))
if __name__=='__main__':main()
