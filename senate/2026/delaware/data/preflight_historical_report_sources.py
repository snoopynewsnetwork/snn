"""Original historical ED/candidate/method positions; no current identity or dispatch approval."""
from pathlib import Path
import collections,csv,gzip,hashlib,html,io,json,re
D=Path(__file__).resolve().parent;N=D/'news'
def sh(b):return hashlib.sha256(b).hexdigest()
def main():
 mf={x['id']:x for x in json.loads((N/'manifest.json').read_bytes())}
 def raw(sid):
  x=mf[sid];z=(N/x['asset']).read_bytes();assert sh(z)==x['stored_sha256'];b=gzip.decompress(z);assert len(b)==x['bytes']and sh(b)==x['raw_sha256'];return b
 specs=[('2020_SEN','sos-observed-2020-general-report','sos-observed-2020-state-csv','USSenator','U.S. Senator'),('2020_PRES','sos-observed-2020-general-report','sos-observed-2020-state-csv','PresidentandVicePresident','President and Vice President'),('2022_HOUSE','official-2022-report','sos-observed-2022-state-csv','RepresentativeinCongress','Representative in Congress')]
 results={};flat=[]
 method_alias={'Machine Votes':'machinevotessum','Absentee Votes':'absenteevotessum','Early Voting Votes':'earlyvotessum','Total Votes':'totalvotessum'}
 for ek,sid,csvsid,css,office in specs:
  text=raw(sid).decode('utf-8-sig');state=[r for r in csv.DictReader(io.StringIO(raw(csvsid).decode('utf-8-sig')))if r['office']==office];controls={r['candidatename']:r for r in state};counts=collections.Counter();units={};method_sums=collections.Counter();native_counts=collections.Counter()
  pattern=r'<h4 class="electiondistrict-title '+css+r' ([^"]+)">(.*?)</h4>\s*<table[^>]*>(.*?)</table>'
  for match in re.finditer(pattern,text,re.S):
   key=match[1];assert key not in units;label=html.unescape(re.sub('<[^>]+>','',match[2])).strip();rows=[]
   for ri,rm in enumerate(re.finditer(r'<tr>(.*?)</tr>',match[3],re.S),1):
    fields={k:html.unescape(re.sub('<[^>]+>','',v)).strip()for k,v in re.findall(r'<td data-label="([^"]+)">(.*?)</td>',rm[1],re.S)}
    if not fields:continue
    candidate=fields['Candidate'];assert candidate in controls and fields['Party']==controls[candidate]['partyname'];assert candidate not in [r['raw_fields']['Candidate']for r in rows]
    values={m:(int(fields[m].replace(',',''))if m in fields else None)for m in method_alias};assert values['Total Votes']==sum(v for m,v in values.items()if m!='Total Votes'and v is not None)
    for m,v in values.items():
     if v is not None:method_sums[(candidate,m)]+=v
     else:counts['unprinted_native_method_fields']+=1
     flat.append({'election_scope':ek,'source_id':sid,'source_raw_sha256':mf[sid]['raw_sha256'],'literal_native_key':key,'literal_native_label':label,'candidate':candidate,'source_row_ordinal_in_table_including_header':ri,'method':m,'raw_literal':fields.get(m),'numeric_value':v,'availability':'literal_numeric'if v is not None else'not_a_printed_source_column','decoded_HTML_table_character_start':match.start(),'decoded_HTML_row_character_start':match.start(3)+rm.start()})
    native_counts[candidate]+=1;rows.append({'raw_fields':fields,'source_row_ordinal_in_table_including_header':ri,'candidate_method_values':values})
   assert len(rows)==len(controls);units[key]={'literal_label':label,'decoded_HTML_character_start':match.start(),'source_rows':rows};counts['native_candidate_rows']+=len(rows)
  assert units
  for candidate,control in controls.items():
   for method,col in method_alias.items():assert method_sums[(candidate,method)]==int(control[col]),(ek,candidate,method,method_sums[(candidate,method)],control[col])
  results[ek]={'official_office_literal':office,'source_id':sid,'state_CSV_source_id':csvsid,'native_contexts':len(units),'candidate_rows':counts['native_candidate_rows'],'candidate_count':len(controls),'candidate_method_positions_including_unprinted':counts['native_candidate_rows']*4,'unprinted_method_fields_retained_null':counts['unprinted_native_method_fields'],'printed_method_columns':[m for m in method_alias if any(row['candidate_method_values'][m]is not None for u in units.values()for row in u['source_rows'])],'state_named_candidate_total':sum(int(r['totalvotessum'])for r in state),'state_raw_candidate_method_controls':state,'source_native_units_by_literal_key':units,'source_report_clock_literals':sorted({r['xmlreporttime']for r in state})}
 pres=results['2020_PRES']['source_native_units_by_literal_key'];sen=results['2020_SEN']['source_native_units_by_literal_key'];only=sorted(set(pres)-set(sen));assert only==['ElectionDistrict0218','ElectionDistrict3117','ElectionDistrict4117']
 onlyrows={k:pres[k]for k in only};assert [r['candidate_method_values']['Total Votes']for r in onlyrows['ElectionDistrict0218']['source_rows']]==[1,0,0,0]
 assert all(r['candidate_method_values']['Total Votes']==0 for k in only if k!='ElectionDistrict0218'for r in onlyrows[k]['source_rows'])
 sources=[sid for _,sid,csvsid,_,_ in specs]+[csvsid for _,sid,csvsid,_,_ in specs]+['sos-observed-general-archive','sos-observed-2020-writeins','sos-observed-2022-writeins'];sourcepins={sid:{**mf[sid],'raw_entity_verified':True}for sid in dict.fromkeys(sources)}
 for sid in sourcepins:raw(sid)
 out={'status':'pass_historical_literal_ED_candidate_method_sums_only_priority_unaccepted','source_pins':sourcepins,'contests':results,'2020_president_only_ED_tables_absent_from_Senate':onlyrows,'all_native_contexts_across_three_contest_scopes':sum(x['native_contexts']for x in results.values()),'candidate_method_positions_including_nulls':len(flat),'complete_selected_source_positions':flat,'qualification':['2020Senate is sameClassII;2022at-largeHouse is an actual recent-midterm alternative, not a nonexistent2022Senate/governor contest.','EarlyVoting Votes is not a printed2020native column and remains null there despite stateCSVearlyvotessum0; no native0fabrication.','County/RD/ED/Wilmington source views overlap; only the literal ED partitions enter these sums, not geographic joins or additive extra levels.','Separate original official write-in PDFs remain complete source bodies; no county/method totals are allocated to EDs or added twice to another source scope.','Literal ED keys across2020redistricting/2022/2024 are not a verified crossyear/currentphysical/reporting crosswalk. No final allcandidate priority or current legal/live feed approval.'],'formal_priority_accepted':False,'current_geography_approved':False}
 p=D/'coordinator-historical-report-preflight.json';b=(json.dumps(out,indent=2)+'\n').encode();p.write_bytes(b);print(json.dumps({'path':str(p),'bytes':len(b),'sha256':sh(b),'contests':{k:{kk:vv for kk,vv in x.items()if kk in ['native_contexts','candidate_rows','candidate_count','state_named_candidate_total','unprinted_method_fields_retained_null']}for k,x in results.items()},'positions':len(flat)}))
if __name__=='__main__':main()
