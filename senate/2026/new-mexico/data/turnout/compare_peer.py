#!/usr/bin/env python3
"""Bounded independent reciprocal source audit against immutable captured bodies only."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'source'))
from common import *
PEER='9a904675-c599-4e28-8862-663c3496078e'
H=D/'history'

def capture(label):return json.loads((H/label/'capture.json').read_text())
def frozen(label,path):
 r=next(r for r in capture(label)['records']if r['path']==path)
 if r['storage']=='lossless_gzip_body':
  s=(STATE/r['body']).read_bytes();assert sha(s)==r['stored_sha256'];b=gzip.decompress(s)
 else:b=(STATE/r['reference']).read_bytes()
 assert sha(b)==r['sha256']and len(b)==r['bytes'];return b
def own(name):return json.loads(frozen('turnout-pre-peer','data/turnout/'+name))
def peer(name):return json.loads(frozen('baseline-final-peer','data/baselines/'+name))
def main():
 findings=[];checks=0;groups={};mismatches=[]
 def eq(scope,left,right):
  nonlocal checks
  checks+=1;groups[scope.split(':')[0]]=groups.get(scope.split(':')[0],0)+1
  if left!=right:mismatches.append(dict(scope=scope,own=left,peer=right))
 def deep(scope,left,right):
  if type(left)!=type(right):eq(scope+':type',type(left).__name__,type(right).__name__);return
  if isinstance(left,dict):
   eq(scope+':keys',sorted(left),sorted(right))
   for k in left.keys()&right.keys():deep(scope+':'+str(k),left[k],right[k])
  elif isinstance(left,list):
   eq(scope+':length',len(left),len(right))
   for i,(x,y)in enumerate(zip(left,right)):deep(scope+':'+str(i),x,y)
  else:eq(scope,left,right)
 # Exact full snapshots and external originals verified without trusting coordinator totals.
 for label in ['turnout-pre-peer','baseline-final-peer']:
  cap=capture(label)
  for r in cap['records']:eq('snapshot:'+label+':'+r['path'],sha(frozen(label,r['path'])),r['sha256'])
 mf=peer('asset-manifest.json')
 for r in mf['external_original_assets']:
  b=(STATE/r['path']).read_bytes();eq('peer_external_stored:'+r['path'],[sha(b),len(b)],[r['sha256'],r['bytes']])
  if r.get('raw_sha256'):raw=gzip.decompress(b);eq('peer_external_original:'+r['path'],[sha(raw),len(raw)],[r['raw_sha256'],r['raw_bytes']])
 om={r['id']:r for r in own('acquisition.json')};pm={r['id']:r for r in peer('source/original-references.json')}
 for id in sorted(om.keys()&pm.keys()):
  q=dict(pm[id]);origin=q.pop('receipt_origin',None);deep('shared_full_receipt:'+id,om[id],q)
 findings.append(dict(kind='receipt_scope',shared_capture_count=len(om.keys()&pm.keys()),peer_only_source_ids=sorted(pm.keys()-om.keys()),own_only_source_ids=sorted(om.keys()-pm.keys()),difference='Peer receipt_origin is additional provenance annotation; all other full shared receipt objects compared literally. Peer current-roster extras/fresh captures are not declared equal to historical captures or used as turnout inputs.'))
 a=own('original-extract.json');p=peer('original-extract.json');coverage=peer('coverage-controls.json');positions=[]
 for tag,v in a.items():
  w=p[tag];deep('csv_headers:'+tag,v['header_rows'],[w['headers'],w['parties']]);eq('csv_hash:'+tag,v['raw_sha256'],w['raw_sha256']);eq('source_id:'+tag,v['source_id'],w['source_id']);eq('row_coverage:'+tag,len(v['rows']),len(w['rows']))
  for r,t in zip(v['rows'],w['rows']):
   pos=r['source_row_1based'];scope=f'csv_row:{tag}:{pos}'
   for x,y in [(r['source_row_1based'],t['source_row']),(r['level'],t['scope']),(r['county_literal'],t['county_literal']),(r['native_label'],t['label_literal']),(r['administrative'],t['administrative']),(r['native_numeric_id'],t['native_id'])]:eq(scope,x,y)
   deep(scope+':raw_row',r['raw_row'],t['raw_row'])
   eq(scope+':first_two_cells',t['cells'][:2],[dict(column=i+1,header=w['headers'][i],party_literal=w['parties'][i],literal=r['raw_row'][i],value=int(r['raw_row'][i])if r['raw_row'][i].isdigit()else None,masked=False)for i in range(2)])
   for f,g in zip(r['fields'],t['cells'][2:]):
    expected=dict(column=f['column_1based'],header=f['label'],party_literal=f['party_literal'],literal=f['literal'],value=f['value'],masked=f['literal']=='*');deep(scope+':cell:'+str(f['column_1based']),expected,g);positions.append([tag,pos,f['column_1based']])
  for q,z in zip(v['reconciliation'],coverage[tag]['counties']):
   deep('county_native_reconciliation:'+tag+':'+q['county'],[q['county'],q['native_row_count'],q['known_sums'],q['county_minus_known'],q['masked_cells']],[z['county'],z['native_count'],z['known_cell_sums'],z['control_minus_known_unallocated'],z['masked_cells']])
  meta=Page(body(w['page_source_id'])).next();peer_meta=peer('source/'+tag+'-page-data.json');deep('full_embedded_metadata:'+tag,meta,peer_meta);deep('own_stored_page_props:'+tag,v['metadata'],meta['props']['pageProps'])
 # Full parent-child arrays for every contest, not count-only agreement.
 hierarchy={}
 for tag,v in a.items():
  parents=[]
  for r in [r for r in v['rows']if r['level']=='County']:
   children=[t for t in v['rows']if t['level']=='Precinct'and t['county_literal']==r['native_label']];peerchildren=[t for t in p[tag]['rows']if t['scope']=='Precinct'and t['county_literal']==r['native_label']]
   x=[[t['source_row_1based'],t['native_label'],t['administrative'],t['raw_row']]for t in children];y=[[t['source_row'],t['label_literal'],t['administrative'],t['raw_row']]for t in peerchildren];deep('full_parent_child_arrays:'+tag+':'+r['native_label'],x,y);parents.append(dict(parent=r['native_label'],source_row=r['source_row_1based'],children_source_rows=[t['source_row_1based']for t in children]))
  hierarchy[tag]=parents
 b=own('ballot-registration-extract.json');pb=peer('turnout-controls.json');cc=own('canvass-controls.json');rawservices=peer('turnout-original-service-fields.json');ballotrows=0
 for year,v in b.items():
  w=pb[year];eq('ballot_state:'+year,[v['state_ballots_cast'],v['state_eligible_voters']],[w['header']['ballots_cast'],w['header']['eligible_voters']]);eq('ballot_native_count:'+year,len(v['native_rows']),len(w['native_rows']));raw=body(v['source_id']).decode()
  for r,t in zip(v['native_rows'],w['native_rows']):
   offset=r['source_char_start'];line=raw[:offset].count('\n')+1;col=offset-raw.rfind('\n',0,offset)-1
   x=[r['county_id_literal'],'countyturnout'+r['county_id_literal'],[line,col],r['native_label'],r['ballots_cast_literal'],r['eligible_voters_literal'],r['ballots_cast'],r['eligible_voters']]
   y=[t['county_id_literal'],t['parent_source_id'],t['position'],t['label_literal'],t['raw_fields']['county-cast'],t['raw_fields']['county-counted'],t['ballots_cast'],t['eligible_voters']];deep('ballot_native_fields:'+year+':'+str(r['source_byte_start']),x,y);ballotrows+=1
  services=cc['county_controls'][year]['county_service_raw_rows'];deep('full_service_objects:'+year,services,rawservices['turnout-'+year+'-county-service']);deep('peer_service_duplicate:'+year,services,w['county_service'])
  eq('ballot_native_sums:'+year,[v['native_ballots_sum'],v['native_eligible_voters_sum']],[w['native_sum_ballots'],w['native_sum_eligible']])
 # Every selected county/candidate PDF position and every administrative ballot method field.
 pdf=peer('pdf-county-controls.json');pdfpositions=0
 for tag,v in a.items():
  ours=cc['president_2024_county_controls']if tag=='2024-president'else cc['county_controls'][tag[:4]]['candidate_rows'];theirs=pdf['vectors'][tag]
  for i,(r,t)in enumerate(zip(ours,theirs)):
   vals=r.get('county_values');deep('pdf_candidate_vector:'+tag+':'+str(i),vals+[r['state']],t['values']);eq('pdf_candidate_position:'+tag+':'+str(i),[r.get('page',r.get('pdf_page')),r.get('line_1based')],[t['pdf_page'],t['text_line']]);pdfpositions+=len(vals)
   expected=[r['native_label']for r in v['rows']if r['level']=='County'];eq('pdf_county_order:'+tag,expected,t['county_order'])
 am=peer('administrative-method-controls.json')
 for year,v in cc['county_controls'].items():
  eq('ballot_method_source:'+year,v['source_id'],am[year]['source_id']);deep('ballot_method_county_order:'+year,v['county_column_order'],am[year]['county_order'])
  for r,t in zip(v['whole_ballot_method_rows'],am[year]['rows']):deep('whole_ballot_methods:'+year+':'+r['method_literal'],[r['method_literal'],r['county_values']+[r['state']],'\n'.join(r['raw_lines']),r['pdf_page'],r['line_1based']],[t['label'],t['values'],t['raw_line'],t['pdf_page'],t['text_line']])
 sm=peer('state-candidate-methods.json')
 for tag,v in cc['statewide_candidate_methods'].items():
  w=sm[tag];eq('candidate_method_source:'+tag,v['source_id'],w['source_id']);eq('method_complete_section:'+tag,v['raw_section'].split('\n',1)[1].strip(),w['raw_section'].strip());deep('candidate_all_methods:'+tag,[[r[x]for x in ['early','absentee','election_day','total']]for r in v['numeric_rows']],[r['values']for r in w['rows']]);eq('candidate_method_order:'+tag,v['method_column_order'],w['rows'][0]['method_order'])
 # Legacy exports: raw rows include unrelated offices and trailing empties in pinned peer;
 # compare every original row against our independently read original bytes.
 legacy=peer('legacy-original-rows.json')
 for id,v in own('legacy-methods.json').items():
  rows=list(csv.reader(io.StringIO(body(id).decode('utf-8-sig'))));w=legacy[id]
  # Shape is checked explicitly, no vote-only projection.
  if isinstance(w,dict):
   eq('legacy_header:'+id,rows[0],w.get('header',w.get('headers')))
   other=w.get('rows');expected=[r['raw_row']if isinstance(r,dict)else r for r in other];deep('all_legacy_original_rows:'+id,rows[1:],expected)
 # Registration row/clock/scope comparisons preserve blanks and wrapped labels.
 stocks=own('registration-stocks.json');rs=peer('registration-controls.json');rn=peer('registration-native-controls.json');regrows=0
 for month,v in stocks.items():
  date='2024-10-31'if month=='9'else'2024-11-26';w=rs[date];eq('registration_state_source:'+month,v['state']['source_id'],w['source_id'])
  eq('registration_state_row_count:'+month,len(v['state']['rows']),len(w['rows']))
  for r,t in zip(v['state']['rows'],w['rows']):deep('registration_state_fields:'+month+':'+str(r['line_1based']),[r['label_literal'],r['counts']+[r['total']],r['raw_line'],r['line_1based']],[t['county_literal'],t['values'],t['raw_line'],t['text_line']]);regrows+=1
  w=rn[month];eq('registration_native_count:'+month,len(v['county']['rows'])+1,len(w['rows']))
  for r,t in zip(v['county']['rows'],w['rows']):
   x={k:r[k]for k in ['source_id','page','county_literal','label_literal','raw_lines','party_order','counts','total','scope','asof']};x.update(line=r['line_1based'],continuations=r['label_continuations']);y={k:t[k]for k in x};deep('registration_native_fields:'+month+':'+str(r['page'])+':'+str(r['line_1based']),x,y);regrows+=1
  eq('registration_timezone:'+month,v['county']['timezone'],w['timezone'])
  owntext=(D/'source'/('registration-'+month+'-county.txt')).read_text();peertext=frozen('baseline-final-peer','data/baselines/source/registration-'+month+'-county.txt').decode();eq('full_registration_pdf_text:'+month,owntext,peertext)
  for t in w['clocks']:eq('registration_clock_literal:'+month+':'+str(t['page']),t['literal'] in owntext.split('\f')[t['page']-1],True)
 # The old structured stock extract kept grand totals in original text, not as an extra row.
 # Independently add the two explicitly printed source rows without modifying the old witness targets.
 grands={}
 for month in ['9','10']:
  text=(D/'source'/f'registration-{month}-county.txt').read_text();pages=text.split('\f');page=pages[110];line=next((i,l)for i,l in enumerate(page.splitlines(),1)if l.startswith('Grand Total'))
  nums=[int(x.replace(',',''))for x in re.findall(r'\d[\d,]*',line[1])];counts=nums[:8:2];total=nums[8]
  z=dict(source_id=f'registration-{month}-county',page=111,line=line[0],county_literal=None,label_literal='Grand Total',continuations=[],raw_lines=[line[1]],party_order=['DEMOCRATIC','LIBERTARIAN','REPUBLICAN','OTHER'],counts=counts,total=total,scope='grand_total',asof=None)
  t=rn[month]['rows'][-1];deep('registration_grand_total:'+month,z,{k:t[k]for k in z});grands[month]=z;regrows+=1
 dump(D/'registration-grand-controls.json',grands)
 findings.append(dict(kind='explicit_representation_mapping',details=['Peer auxiliary numeric CSV label cell is parsed directly from its digit literal, but native_id remains null; our native_label stays literal with no numeric ID.','PDF county column order comes from the source table/CSV, not dictionary insertion order of the county-only Census alias map.','PDF Election Day 2022/2024 spans header line6 and numeric line7; full two-line raw text and both source positions preserved.','Our original stock object has2201county/native rows per date and full PDF text; peer has those plus one explicit grand-total row. The two grand totals are now independently parsed from original text into registration-grand-controls.json, with old bytes preserved.']))
 # 18 complete source-position tie universes. Full cumulative counts regenerated from own observations.
 orders=own('sensitivity.json');po=peer('source-scoped-orders.json');eq('all18_order_universes',list(orders),list(po));canonical=[]
 for key,v in orders.items():
  w=po[key]
  for field in ['denominator','observed_votes','unit_count','top15_votes','minimum80_count','minimum80_votes','preceding_votes','ordered_priority_keys','ordered_remainder_keys']:deep('canonical_order_scope:'+key+':'+field,v[field],w[field])
  deep('full_canonical_order:'+key,[r['key']for r in v['order']],w['full_order'])
  # Each key's weight is from our independent values, never imported peer votes.
  cumulative=0
  for rank,row in enumerate(v['order'],1):cumulative+=row['votes'];eq('canonical_cumulative:'+key+':'+str(rank),row['cumulative_votes'],cumulative)
  canonical.append(dict(universe=key,denominator=v['denominator'],unit_count=v['unit_count'],minimum80=v['minimum80_count'],crossing_key=v['crossing_key'],order_sha256=sha(json.dumps([r['key']for r in v['order']],ensure_ascii=False).encode())))
 # Exact county-FIPS association and each full 2024 parent/child array.
 peer_counties=list(csv.DictReader(io.StringIO(frozen('baseline-final-peer','data/county-baselines.csv').decode())))
 contract=own('priority-set.json')
 for parent in contract['county_contexts']:
  pp=next(r for r in peer_counties if r['contest']=='2024-senate'and r['county']==parent['source_label'])
  eq('contract_county_fips:'+parent['source_label'],parent['fips'],pp['fips'])
  eq('contract_county_candidate_control:'+parent['source_label'],parent['candidate_votes'],int(pp['all_candidate_votes']))
  children=[f"nm:elstats:14873:{r['county_literal']}:{r['label_literal']}"for r in p['2024-senate']['rows']if r['scope']=='Precinct'and r['county_literal']==parent['source_label']]
  deep('contract_full_child_key_array:'+parent['source_label'],parent['source_native_constituent_keys'],children)
 for id in ['official-2020-file-0','official-2020-file-1','official-2022-file-0','official-2022-file-1','official-2024-file-1','official-2024-file-2','registration-9-state','registration-10-state']:
  eq('full_pdf_text_source_object:'+id,(D/'source'/f'{id}.txt').read_bytes(),frozen('baseline-final-peer','data/baselines/source/'+id+'.txt'))
 # Keep peer's alternate label-tie presentation distinct; preserve its entire immutable body.
 pc=peer('priority-contract.json')['2024-senate'];o=own('priority-set.json');alt=pc['observed_complete_candidate_rows_only']['ordered'];alternate=[f"nm:elstats:14873:{r['county']}:{r['label']}"for r in alt];ours=o['known_observation_scope']['order'];diff=[dict(position=i+1,own_source_position_key=x,peer_label_tie_key=y)for i,(x,y)in enumerate(zip(ours,alternate))if x!=y]
 eq('alternate_order_complete_keys',set(ours),set(alternate));lookup={r['key']:r['candidate_votes']for r in a['2024-senate']['rows']if r['level']=='Precinct'}
 eq('alternate_tie_only',all(lookup[r['own_source_position_key']]==lookup[r['peer_label_tie_key']]for r in diff),True)
 for k in ['certified_native_order','certified_native_top15','certified_native_minimum80']:eq('nonadmission_flags:'+k,pc[k],None)
 eq('nonadmission_flags:dispatch',pc['canonical_dispatch_keys'],[])
 findings.append(dict(kind='tie_presentation',different_positions=len(diff),differences=diff,explanation='Peer original priority-contract uses county/literal-label ties. Our canonical order and peer separate source-scoped-orders use source row. Equal vote counts, full membership and minimum cardinality agree; exact alternate key sequence is preserved, not overwritten.'))
 result=dict(schema_version='nm-turnout-reciprocal-1',peer_agent_id=PEER,peer_capture_manifest_sha256=capture('baseline-final-peer')['manifest_sha256'],peer_capture_index_sha256=sha((H/'baseline-final-peer/capture.json').read_bytes()),own_pre_peer_capture_index_sha256=sha((H/'turnout-pre-peer/capture.json').read_bytes()),peer_original_first_pin_sha256=sha(frozen('baseline-final-peer','data/baselines/source/independent-first-pin.json')),own_original_first_witness_sha256=sha(frozen('turnout-pre-peer','data/turnout/original-first-witness-v2.json')),status='passed_bounded_source_core'if not mismatches else 'qualified_mismatches_retained',comparison_checks=checks,check_groups=groups,coverage=dict(candidate_control_positions=len(positions),native_rows_by_contest={k:sum(r['level']=='Precinct'for r in v['rows'])for k,v in a.items()},ballot_eligible_native_rows=ballotrows,registration_rows=regrows,pdf_candidate_county_cells=pdfpositions,order_universes=len(canonical),priority_native_constituents=2201,priority_county_parents=33),source_position_mapping='CSV one-based row/column; ballot own source-byte/char start mapped to original line/zero-based column; registration original PDF page/line and raw wrapped lines. No alias or cross-year/current native join.',mismatches=mismatches,findings=findings,canonical_orders=canonical,parent_child_arrays=hierarchy,exclusions=['Calculator input validity, calculator outcomes, modeled preferences/scenarios and report prose equality are outside this audit.','Capture is actual finished baseline MF b7889d8a...; no equality claim for later repaired files or future final manifests.','Peer-only current roster/fresh observations are separately preserved, not imported as historical votes.','No legal/current geography/collector/feed/certified-native priority admission.'],coordinator_acceptance=False,accepted_for_dispatch=False)
 dump(D/'peer-reconciliation.json',result);print(json.dumps(dict(status=result['status'],checks=checks,coverage=result['coverage'],mismatches=len(mismatches),first_mismatches=mismatches[:5]),ensure_ascii=False))
if __name__=='__main__':main()
