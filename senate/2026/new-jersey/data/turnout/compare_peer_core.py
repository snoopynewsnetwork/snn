#!/usr/bin/env python3
"""Bounded complete fixed-core comparison. Peer reads come ONLY from immutable captured bytes."""
from pathlib import Path
import json,gzip,hashlib,re,ast,collections,subprocess,tempfile,copy
D=Path(__file__).resolve().parent;ST=D.parent.parent;R=D/'reciprocal-review'
FAIL=[];COUNTS=collections.Counter();DETAIL=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def peer(rel):return json.loads(gzip.decompress((R/'peer-capture/bodies'/(rel+'.gz')).read_bytes()))
def own(rel):return json.loads((D/rel).read_text())
def equal(category,key,a,b):
 COUNTS[category]+=1
 if a!=b:FAIL.append({'category':category,'key':key,'own':a,'peer':b})
def peerbytes(rel):return gzip.decompress((R/'peer-capture/bodies'/(rel+'.gz')).read_bytes())
def layout(sid):
 sid='shared-'+sid if sid.startswith('sos-') else sid
 return gzip.decompress((D/'extract'/(sid+'.txt.gz')).read_bytes()).decode()
def at(sid,page,line):return layout(sid).split('\f')[page-1].splitlines()[line-1]
def rowcheck(o,p,scope):
 fields={'key':'key','source_id':'source_id','page':'page','line':'line','county':'county','county_fips':'county_fips','native_label':'label','values':'votes','source_line':'raw'}
 for a,b in fields.items():equal('native_full_fields',scope+':'+p['key']+':'+a,o[a],p[b])
 equal('native_type',p['key'],o['unit_type'],{'municipal-labelled':'municipality','administrative':'administrative'}[p['type']])
 equal('native_reported_sum',p['key'],sum(v for v in o['values'] if v is not None),p['numeric_sum'])
 spans=list(re.finditer(r'\d[\d,]*',o['source_line']));pc=p['numeric_cells'];cols=[i for i,v in enumerate(o['values']) if v is not None]
 equal('native_all_numeric_spans',p['key'],[{'column':col,'start':s.start(),'end':s.end(),'literal':s[0]} for col,s in zip(cols,spans)],pc)
 equal('native_numeric_span_count',p['key'],len(spans),len(cols))
def main():
 for cap in ['peer-capture.json','peer-return-capture.json']:
  for a in own('reciprocal-review/'+cap)['records']:
   z=(ST/a['capture_path']).read_bytes();b=gzip.decompress(z)
   equal('captured_hashes',a['peer_path']+':stored',(sha(z),len(z)),(a['stored_sha256'],a['stored_bytes']))
   equal('captured_hashes',a['peer_path']+':raw',(sha(b),len(b)),(a['sha256'],a['bytes']))
 equal('initial_peer_witness','sha',sha(peerbytes('source/pre-peer-witness.json')),'d8a93b13b137b8336b2bb47a0ab4373aff6ca5212363dbe76dbb8711137bfc40')
 equal('initial_peer_witness','peer_read',peer('source/pre-peer-witness.json')['peer_read'],False)
 # Definitions are parsed as literal AST, never executed; no peer values construct own outputs.
 src=gzip.decompress((D/'peer-review-freeze/original-first-v1/bodies/data/turnout/build_turnout.py.gz').read_bytes()).decode();tree=ast.parse(src)
 defs=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CANDS' for t in n.targets))
 om=own('extract/native-rows.json');of=own('extract/municipal-footers.json');pn=peer('extract/native-contests.json');fullcount=0
 for scope,counties in pn.items():
  flat=[r for c in counties for r in c['rows']];equal('all_scope_keys',scope,[r['key'] for r in om[scope]],[r['key'] for r in flat]);od={r['key']:r for r in om[scope]}
  for c in counties:
   equal('candidate_definitions',c['source_id'],[{'name':n,'party_ballot_label':p} for n,p in defs[scope]],c['candidates'])
   equal('source_parent_children',c['source_id'],[r['key'] for r in om[scope] if r['county']==c['county']],[r['key'] for r in c['rows']])
   for p in c['rows']:rowcheck(od[p['key']],p,scope);fullcount+=1
   foot=next(r for r in of[scope] if r['county']==c['county']);pf=c['footer']
   for a,b in {'key':'key','source_id':'source_id','page':'page','line':'line','county':'county','county_fips':'county_fips','native_label':'label','values':'votes','source_line':'raw'}.items():equal('all84_source_footers',pf['key']+':'+a,foot[a],pf[b])
   for h in c['headers']:
    for line in h['lines']:equal('complete_header_positions',c['source_id']+f':p{h["page"]}:l{line["line"]}',at(c['source_id'],h['page'],line['line']),line['raw'])
 equal('native_scope_count','all_four',fullcount,2296)
 # Exact complete layout bytes: includes every heading, party/slogan/marker, blank, numeric and unrelated field.
 layout_count=0
 cap=own('reciprocal-review/peer-capture.json')
 for a in cap['records']:
  rel=a['peer_path'].removeprefix('data/baselines/')
  if not rel.endswith('.layout.txt.gz'):continue
  sid=Path(rel).name.removesuffix('.layout.txt.gz');pt=gzip.decompress(peerbytes(rel))
  if sid=='clerk-2020':
   cr=own('source/clerk-2020-reference.json');raw=(D/'source'/cr['reference_path']).read_bytes()
   with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
    f.write(raw);f.flush();ot=subprocess.run(['pdftotext','-layout',f.name,'-'],check=True,capture_output=True).stdout
  else:ot=layout(sid).encode()
  equal('complete_raw_layout_bytes',sid,{'sha256':sha(ot),'bytes':len(ot)},{'sha256':sha(pt),'bytes':len(pt)});layout_count+=1
 # Every full statewide candidate page and all588 county candidate cells, including positions and footer.
 oc=own('extract/state-candidate-controls.json');pc=peer('extract/county-candidate-controls.json')
 for scope,pages in pc.items():
  equal('state_candidate_page_count',scope,len(oc[scope]),len(pages))
  for o,p in zip(oc[scope],pages):
   equal('state_candidate_page',scope+str(p['page']),o['page'],p['page'])
   equal('state_candidate_total',scope+str(p['page']),o['published_total'],p['footer']['votes'])
   for a,b in zip(o['county_cells'],p['counties']):
    key=a['key'];equal('all588_state_candidate_cells',key,{'county':a['county'],'votes':a['votes'],'raw':a['source_line'],'page':o['page'],'line':int(key.rsplit('l',1)[1])},b)
   for h in p['header']:equal('state_raw_header_marker_party',scope+str(p['page'])+str(h['line']),o['raw_page_text'].splitlines()[h['line']-1],h['raw'])
   equal('state_footer_raw_position',scope+str(p['page']),o['raw_page_text'].splitlines()[p['footer']['line']-1],p['footer']['raw'])
 # All native ballots + footers + method/statistic nulls, original raw tokens and exact spans.
 ob=own('extract/ballot-rows.json');obf=own('extract/ballot-footers.json');pb=peer('extract/ballot-records.json');bmap={'registered_voters':'registered_voters','ballots_cast':'ballots_cast','vote_by_mail_ballots_cast':'mail_ballots','provisional_ballots_cast':'provisional_ballots','election_day_provisional_ballots_cast':'election_day_provisional','early_voting_provisional_ballots_cast':'early_voting_provisional'}
 ballot_count=0
 for c in pb:
  year=str(c['year']);orr=[r for r in ob[year] if r['source_id']==c['source_id']];equal('ballot_full_key_arrays',c['source_id'],[r['key'] for r in orr],[r['key'] for r in c['rows']]);od={r['key']:r for r in orr+obf[year]}
  equal('ballot_footer_arrays',c['source_id'],[r['key'] for r in obf[year] if r['source_id']==c['source_id']],[r['key'] for r in c['footers']])
  for p in c['rows']+c['footers']:
   o=od[p['key']];ballot_count+=1
   for a,b in {'key':'key','source_id':'source_id','county':'county','native_label':'label','page':'page','line':'line','source_line':'raw','tokens':'tokens',**bmap}.items():equal('all_ballot_fields',p['key']+':'+a,o[a],p[b])
   equal('published_percent_lossless_mapping',p['key'],str(o['published_percent'])+'%' if o['published_percent'] is not None else None,p['published_percent'])
   for cell in p['cells']:
    equal('ballot_numeric_cell_span',p['key']+str(cell['start']),o['source_line'][cell['start']:cell['end']],cell['literal'])
    a=next((a for a,b in bmap.items() if b==cell['field']),None)
    equal('ballot_numeric_cell_value',p['key']+cell['field'],o[a] if a else 'UNMAPPED',int(cell['literal'].replace(',','')))
  for h in c['headers']:equal('ballot_all_header_positions',c['source_id']+str(h['page'])+str(h['line']),at(c['source_id'],h['page'],h['line']),h['raw'])
 # Administrative statewide controls and literal headings, without treating headings as zero geographies.
 otc=own('extract/turnout-controls.json');ptc=peer('extract/turnout-controls.json');headings=0
 for y,sid in [('2024','sos-2024-turnout'),('2020','2020-official-general-voter-turnout'),('2022','sos-2022-turnout')]:
  mapped={}
  for p in ptc[sid]['rows']:
   equal('turnout_raw_rows',sid+str(p['line']),at(sid,p['page'],p['line']),p['raw'])
   if p['tokens']:mapped[(p['page'],p['line'])]=p
   else:headings+=1
  equal('state_turnout22numeric_rows',y,len(mapped),22)
  for o in otc[y]:
   key=o['key'];p=mapped[(1,int(key.rsplit('l',1)[1]))];equal('turnout_all_statistic_tokens',key,[f'{o["registered_voters"]:,}',f'{o["ballots_cast"]:,}',f'{o["ballots_rejected"]:,}',str(o['published_percent'])+'%',f'{o["election_districts"]:,}'],p['tokens'])
   equal('turnout_all_numeric_raw',key,o['source_line'],p['raw'])
 # All shared contest and ballot/registration orders, independently recomputed from peer's fixed source records.
 oo=own('all-source-orders.json');pp=peer('priority-set.json');co=own('priority-set.json');parent_arrays=[]
 source_orders={scope:[(r['key'],r['county'],r['label'],sum(v for v in r['votes'] if v is not None)) for c in cs for r in c['rows']] for scope,cs in pn.items()}
 for year in ['2024','2020','2022']:
  for fld in ['ballots_cast','registered_voters']:
   source_orders[year+'-'+fld]=[(r['key'],r['county'],r['label'],r[fld]) for c in pb if str(c['year'])==year for r in c['rows'] if r[fld] is not None]
 for scope,rr in source_orders.items():
  rr=sorted(rr,key=lambda t:(-t[3],t[0]));cum=0;pk=[]
  equal('all10_order_lengths',scope,len(oo[scope]),len(rr))
  for i,(key,county,label,votes) in enumerate(rr,1):
   cum+=votes;o=oo[scope][i-1];equal('all10_full_order_objects',key,(o['rank'],o['key'],o['county'],o['native_label'],o['volume'],o['cumulative_votes']),(i,key,county,label,votes,cum));pk.append(key)
  equal('all10_complete_order_arrays',scope,[r['key'] for r in oo[scope]],pk)
 for o,p in zip(co['all_units'],pp['order']):equal('priority_all575_rank_objects',p['key'],(o['rank'],o['key'],o['county'],o['native_label'],o['volume'],o['cumulative_votes']),(p['rank'],p['key'],p['county'],p['label'],p['candidate_votes'],p['cumulative_votes']))
 equal('priority575keys','all',co['complete_ordered_keys'],[r['key'] for r in pp['order']]);equal('priority233keys','all',co['ordered_priority_keys'],pp['priority_keys']);equal('remainder342keys','all',co['remainder']['ordered_keys'],pp['remainder_keys'])
 equal('integer80_controls','all',(co['universe']['reported_total'],co['minimum80']['count'],co['minimum80']['preceding_votes'],co['minimum80']['votes']),(pp['total'],pp['minimum_count'],pp['before_votes'],pp['crossing_votes']))
 for county in co['county_coverage']:
  keys=[r['key'] for r in pp['order'] if r['county']==county['county']];equal('all21_ranked_parent_child_arrays',county['county'],county['ranked_source_unit_keys'],keys);parent_arrays.append({'county':county['county'],'county_fips':county['county_fips'],'ordered_keys':keys})
 # Every inherited receipt body and metadata object, including response headers/redirects/errors.
 refs=peer('source/original-references.json')
 for a in refs:
  if a['receipt_filename']=='clerk-2020-original-reference':
   cr=own('source/clerk-2020-reference.json');equal('clerk_original_reference','hash_size_url',(cr['raw_sha256'],cr['raw_bytes'],cr['url']),(a['raw_sha256'],a['raw_bytes'],a['receipt']['url']));continue
  b=(D/'source'/a['receipt_filename']).read_bytes();equal('all_original_receipt_bytes',a['receipt_filename'],sha(b),a['inherited_receipt_sha256']);equal('all_original_receipt_metadata',a['receipt_filename'],json.loads(b),a['receipt'])
 clerk=peer('extract/clerk-2020-section.json');equal('clerk_literal_section','all',(D/'extract/clerk-2020-new-jersey-section.txt').read_text(),clerk['literal_section']);equal('clerk_vintage_controls','all',(clerk['Booker'],clerk['Mehta']),(2541178,1817052))
 # Negative checks are copies only; prove the compared semantic objects distinguish all requested failure modes.
 # Exercise the same full native-row comparator on corrupted copies, then discard expected failures.
 base=pn['2024-senate'][0]['rows'][0];sparse=next(r for c in pn['2024-senate'] for r in c['rows'] if any(v is None for v in r['votes']));omap={r['key']:r for r in om['2024-senate']}
 for name in ['candidate_vote','candidate_null','source_position','raw_space','numeric_span','administrative_type']:
  changed=copy.deepcopy(sparse if name=='candidate_null' else base)
  if name=='candidate_vote':changed['votes'][0]+=1
  elif name=='candidate_null':changed['votes'][changed['votes'].index(None)]=0
  elif name=='source_position':changed['line']+=1
  elif name=='raw_space':changed['raw']=' '+changed['raw']
  elif name=='numeric_span':changed['numeric_cells'][0]['start']+=1
  else:changed['type']='administrative'
  start=len(FAIL);oldcounts=COUNTS.copy();rowcheck(omap[changed['key']],changed,'negative');detected=len(FAIL)>start;del FAIL[start:];COUNTS.clear();COUNTS.update(oldcounts);equal('negative_fixture_rejected',name,detected,True)
 for name,expected,changed in [('candidate_party',defs['2024-senate'],[(n,'wrong party' if i==0 else party) for i,(n,party) in enumerate(defs['2024-senate'])]),('protected_literal','***',None),('published_zero',0,None),('full_order',co['complete_ordered_keys'],list(reversed(co['complete_ordered_keys']))),('parent_child',parent_arrays[0]['ordered_keys'],parent_arrays[0]['ordered_keys'][:-1])]:
  start=len(FAIL);oldcounts=COUNTS.copy();equal('negative_same_comparator',name,expected,changed);detected=len(FAIL)>start;del FAIL[start:];COUNTS.clear();COUNTS.update(oldcounts);equal('negative_fixture_rejected',name,detected,True)
 crossing_ok=lambda before,cross,total:5*before<4*total<=5*cross
 equal('negative_fixture_rejected','integer80_preceding_at_threshold',crossing_ok(3225436,3229453,4031795),False)
 equal('negative_fixture_rejected','integer80_crossing_below_threshold',crossing_ok(3224325,3225435,4031795),False)
 firstcap=cap['records'][0];raw=peerbytes(firstcap['peer_path'].removeprefix('data/baselines/'))
 hash_ok=lambda body,a:sha(body)==a['sha256'] and len(body)==a['bytes']
 equal('negative_fixture_rejected','captured_hash_corrupted_byte',hash_ok(raw+b'x',firstcap),False)
 equal('negative_fixture_rejected','strict40million_boundary',40000000<40000000,False)
 reverse=json.loads(gzip.decompress((R/'peer-return-capture/bodies/peer-comparison.json.gz').read_bytes()));equal('bounded_reverse_peer_result','all',(reverse['failed'],reverse['differences'],reverse['checks'],reverse['passed']),(0,[],40921,40921))
 result={'status':'pass_bounded_fixed_core_reciprocal' if not FAIL else 'fail','worker_id':'04473229-3e65-45b1-b628-b2fe909eaeee','peer_id':'61054f9e-a14c-44fc-b6b2-7bbc4c84b449','scope':'ONLY captured completed original-first core; excludes later finer extractions/calculators/scenarios/report/final seal','checks':sum(COUNTS.values()),'categories':dict(COUNTS),'differences':FAIL,'native_rows':fullcount,'municipal_footers':84,'primary_candidate_county_cells':588,'ballot_rows_and_footers':ballot_count,'complete_raw_layout_bodies':layout_count,'preserved_non_numeric_turnout_heading_rows':headings,'parent_child_arrays':parent_arrays,'reverse_peer_fixed_core_result':reverse,'schema_distinctions':['Flat versus county-grouped records; all source-position key arrays compared.','municipality versus municipal-labelled means the same source label category; administrative remains distinct.','Numeric published_percent versus literal percent-sign string; exact reversible presentation mapping.','shared- prefix only on own inherited statewide source/text evidence IDs; exact raw page/line/bytes compared.','Own numeric cells represented by candidate vectors plus full literal source line; peer explicit char spans independently reconstructed for every cell.','County footer is nonadditive in both schemas despite peer footer type municipal-labelled.','Empty-token retained heading rows are compared as raw text and excluded only from22numeric control rows per publication.'],'unchanged_arithmetic':{'candidate_universe':'all six printed2024Senate candidates','total':4031795,'top15':631518,'minimum80_count':233,'preceding_votes':3224325,'crossing_votes':3229453,'crossing_key':'2024-official-general-results-us-senate-monmouth:p0001:l0016','remainder_count':342},'acceptance':{'coordinator':False,'current_or_legal_geography':False,'eligible_writein_universe':False,'november2026_returns':False}}
 (R/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':result['checks'],'categories':result['categories'],'difference_count':len(FAIL),'first_differences':FAIL[:6]},indent=2))
 return not FAIL
if __name__=='__main__':raise SystemExit(0 if main() else 1)
