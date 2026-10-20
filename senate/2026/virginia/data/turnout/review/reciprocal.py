#!/usr/bin/env python3
"""Rederive own source core in isolation, then compare captured final peer extracts."""
import collections,csv,gzip,io,json,os,re,shutil,subprocess,sys,tempfile,traceback
from pathlib import Path
from captured import T,S,H,sha,Capture
O=Capture('turnout-original-first');P=Capture('baseline-final-peer')
R=T/'review';checks=[];distinctions=[]
def eq(label,a,b):
 assert a==b,label
 checks.append({'check':label,'sha256_canonical':sha(json.dumps(a,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())})
def pj(n):return P.json('data/baselines/'+n)
def ownbody(id):
 ix=json.loads((T/'source/acquisition-index.json').read_text());rec=next(x['full_receipt'] for x in ix['receipts'] if x['full_receipt']['id']==id and x['full_receipt']['hops'][-1].get('status')==200);hop=rec['hops'][-1];b=(T/hop['body_path']).read_bytes();assert sha(b)==hop['stored_sha256'];raw=gzip.decompress(b);assert sha(raw)==hop['raw_sha256'];return raw

def run():
 result={'peer_agent_id':'8bfac51f-775a-4104-ad5c-42daa3bfdc4c','captured_manifest_sha256':P.index['manifest_sha256'],'captured_peer_witness_sha256':'0ceae3b881ee35bfc226f28313b657a0b09c23f34f7ad982d1695fad1526d56c','scope':'Shared three-Senate raw/source/native/parent/method/administrative/registration and17 sensitivity orders only. Peer calculator/scenarios/targets/outcomes/president/later metadata excluded. Captured full source metadata compared; representation adapters preserve original positions and literals.','coordinator_acceptance':None,'eligible_named_writein_or_current_geography_approval':False}
 # Own original-source re-extraction/calculation happens in isolation, before using peer numerical arrays below.
 with tempfile.TemporaryDirectory(prefix='va-turnout-offline-',dir='/private/tmp') as tmp:
  state=Path(tmp)/'virginia';out=state/'data/turnout';out.mkdir(parents=True);(out/'source').symlink_to(T/'source',target_is_directory=True)
  for n in ['extract_originals.py','source_controls.py','build_turnout.py','render_prose.py']:
   code=(T/n).read_text()
   if n=='build_turnout.py':code=code.replace(' from apply_review_metadata import apply\n apply(STATE,HERE)\n','') # Exclude only post-calculation status hook from the original-core comparison stage.
   (out/n).write_text(code)
  guard='''import sys,runpy\nfrom pathlib import Path\ndef audit(event,args):\n if event.startswith('socket.'):raise PermissionError('offline network denied')\n if event=='open':\n  p=str(args[0])\n  if '/data/baselines/' in p or '/data/news/manifest.json' in p or 'coordinator-primary-preflight' in p or 'preflight_primary_sources' in p:raise PermissionError('mutable/helper/peer discovery denied: '+p)\nsys.addaudithook(audit)\nsys.path.insert(0,str(Path(sys.argv[1]).parent))\nrunpy.run_path(sys.argv[1],run_name='__main__')\n'''
  gp=Path(tmp)/'guard.py';gp.write_text(guard);runs=[]
  for name in ['extract_originals.py','source_controls.py','build_turnout.py']:
   p=subprocess.run([sys.executable,'-B',str(gp),str(out/name)],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});runs.append({'script':name,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,p.stderr
  invariant=[]
  for e in O.index['bodies']:
   rel=e['path'];candidate=state/rel
   if candidate.exists() and '/source/' not in rel and candidate.suffix!='.py' and rel!='turnout.md':
    # Every emitted original semantic body, including contract, is byte-identical at this pre-metadata stage.
    eq('isolated-byte-invariant:'+rel,candidate.read_bytes().hex(),O.read(rel).hex());invariant.append(rel)
  wrong=json.loads((H/'finding-finding.json').read_text())['wrong_report_target'];right=json.loads((H/'finding-finding.json').read_text())['actual_retained_requested_final_URL'];eq('only-pre-metadata-report-change-is-confirmed-citation',(state/'turnout.md').read_text(),O.read('turnout.md').decode().replace(wrong,right))
  result['isolation']={'network_calls':0,'denied_routes':['sockets','mutable news manifest','coordinator numeric preflight/helper','all peer paths'],'runs':runs,'byte_invariant_outputs':invariant,'report_change':'only confirmed literal citation repair before peer status metadata','metadata_isolation':'Only the two-line post-calculation apply_review_metadata hook is excluded here. Final-reproduction separately executes that hook and checks only permitted status/report edits.'}
  # Compare complete original historical tokens, source positions, fields, candidate/party headers and full hydration objects.
  rawmaps={}
  for y,cid in [(2024,161257),(2020,144564),(2018,134055)]:
   raw=ownbody(f'fresh-{y}-csv');rd=csv.reader(io.StringIO(raw.decode('utf-8-sig'),newline=''));rr=[];last=0
   for i,cells in enumerate(rd,1):rr.append({'record':i,'line_start':last+1,'line_end':rd.line_num,'cells':cells});last=rd.line_num
   peer=pj(f'extracted/{y}-senate.json.gz');eq(f'{y}-all-raw-record-tokens-positions',rr,peer['raw_records']);eq(f'{y}-candidate-party-headers',rr[:2],[{'record':1,'line_start':1,'line_end':1,'cells':peer['headers']},{'record':2,'line_start':2,'line_end':2,'cells':peer['parties']}])
   derived=[];parent=None;tc=rr[0]['cells'].index('Total Votes Cast')
   for r in rr[2:]:
    cells=r['cells'];scope=cells[0]
    if scope=='Locality':parent=cells[1]
    derived.append({'source_key':f'{y}-senate:record:{r["record"]}','record':r['record'],'line_start':r['line_start'],'line_end':r['line_end'],'scope':scope,'parent':None if scope=='State' else parent,'name':cells[1],'votes':[int(v) for v in cells[2:tc]],'total':int(cells[tc]),'undervotes_literal':cells[-1] if 'Undervotes' in rr[0]['cells'] else None})
   eq(f'{y}-all-native-parent-state-field-objects',derived,peer['rows']);rawmaps[y]=derived
   hydration=json.loads(re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',ownbody(f'fresh-{y}-html').decode()).group(1));eq(f'{y}-complete-hydration-including-alternates-null-admin-notes',hydration,pj(f'extracted/fresh-{y}-html-hydration.json.gz'))
  # Complete required original API objects, all fields of every independently extracted relevant scope.
  apis=pj('extracted/api-native-objects.json.gz');assert len(apis)==134 and len({a['source'] for a in apis})==134;ownapis={};native_method=0
  for peer in apis:
   source=peer['source'];raw=json.loads(ownbody(source));ownapis[source]=raw
   for key in peer:
    if key not in ['source','scope_code']:eq(source+':complete-object:'+key,raw[key],peer[key])
  for peer in pj('extracted/method-rows.json.gz'):
   source=peer['source'];raw=ownapis[source];v=raw
   for token in peer['path'].split('/')[1:]:v=v[int(token)] if isinstance(v,list) else v[token]
   eq('method-source-constituent:'+source+peer['path'],{'groupId':v['groupId'],'groupName':v['groupName'],'voteCount':v['voteCount']},{k:peer[k] for k in ['groupId','groupName','voteCount']})
   if source.startswith('enr-native-') and '/breakdownResults/' in peer['path']:native_method+=1
  assert native_method==40035
  independently_derived_methods=[]
  for source,raw in ownapis.items():
   def walk(v,path):
    if isinstance(v,dict):
     if 'groupResults' in v and 'nativeId' in v:
      for i,g in enumerate(v['groupResults']):independently_derived_methods.append({'source':source,'scope_code':'STATE' if source=='enr-2024-senate' else source.rsplit('-',1)[1],'path':path+'/groupResults/'+str(i),'candidate_id':v['id'],'candidate_nativeId':v['nativeId'],'candidate_name':next(n['text'] for n in v['name'] if n['languageId']=='en'),'groupId':g['groupId'],'groupName':g['groupName'],'voteCount':g['voteCount']})
     for k,x in v.items():walk(x,path+'/'+k)
    elif isinstance(v,list):
     for i,x in enumerate(v):walk(x,path+'/'+str(i))
   walk(raw['ballotItemWithBreakdown'],'/ballotItemWithBreakdown')
  sortmethod=lambda rs:sorted(rs,key=lambda x:(x['source'],x['path']))
  eq('complete-method-source-candidate-context-and-omission-coverage',sortmethod(independently_derived_methods),sortmethod(pj('extracted/method-rows.json.gz')))
  associations=pj('native-associations.json.gz');localraw={p['name']:p for p in rawmaps[2024] if p['scope']=='Locality'};children=collections.defaultdict(list)
  for peer in associations:
   r=rawmaps[2024][peer['historical']['record']-3];eq('native-full-association:'+str(r['record']),r,peer['historical']);raw=ownapis[peer['api_source']];j=int(peer['api_pointer'].rsplit('/',1)[1]);eq('native-full-source-object:'+str(r['record']),raw['ballotItemWithBreakdown']['breakdownResults'][j],peer['api_native']);children[r['parent']].append(r['record'])
  parents=pj('parent-identities.json');assert len(parents)==133
  stateparents={r['locality']['mapFeatureId']:r['locality'] for r in ownapis['enr-2024-senate']['ballotItemWithBreakdown']['breakdownResults']}
  for label,p in parents.items():
   api=ownapis['enr-native-'+p['code']];eq('parent-full-election:'+label,api['election'],p['api_election']);eq('parent-full-voterturnout:'+label,api['voterTurnout'],p['voterTurnout']);eq('parent-source-record-reference:'+label,localraw[label]['record'],p['historical_record'])
  assert len(associations)==2669 and len({a['historical']['record'] for a in associations})==2669
  assert sorted(a['historical']['record'] for a in associations)==sorted(r['record'] for r in rawmaps[2024] if r['scope']=='Precinct')
  for label,p in parents.items():
   api=ownapis['enr-native-'+p['code']];eq('parent-full-source-identity:'+label,p['source_parent'],stateparents[p['code']]);eq('parent-fips-jurisdiction:'+label,[p['fips'],p['api_jurisdiction']],['51'+p['code'],api['jurisdiction']['id']])
  annual=json.loads((out/'extracts/state-turnout-summary.json').read_text());peerannual=pj('annual-controls.json');html=ownbody('turnout-summary').decode()
  for y,p in peerannual.items():
   eq('annual-full-required-control:'+y,{k:annual[y][k] for k in ['raw_cells','registered','total_voting']},{k:p[k] for k in ['raw_cells','registered','total_voting']});segment=html[p['source_char_start']:p['source_char_end']];assert str(annual[y]['registered']).replace(',','') in re.sub(r'[,<][^>]*>|,','',segment) or annual[y]['raw_cells'][1] in segment
  for c in pj('extracted/method-controls.json.gz'):
   v=ownapis[c['source']]
   for token in c['path'].split('/')[1:]:v=v[int(token)] if isinstance(v,list) else v[token]
   eq('full-method-candidate-control:'+c['source']+c['path'],[c['candidate'],c['voteCount'],c['method_sum'],c['difference']],[v['nativeId'],v['voteCount'],sum(g['voteCount'] for g in v['groupResults']),sum(g['voteCount'] for g in v['groupResults'])-v['voteCount']])
  result['full_child_arrays']={k:sorted(v) for k,v in children.items()}
  # Full raw administrative/registration/bulk required-office rows, including BOM and actual blank CRLF record.
  for source in ['turnout-2018','turnout-2020','turnout-2022','enr-2024-turnout-report','registration-2024-nov1']:
   raw=ownbody(source);rd=csv.reader(io.StringIO(raw.decode('utf-8-sig'),newline=''));rs=[];last=0
   for i,cells in enumerate(rd,1):rs.append({'record':i,'line_start':last+1,'line_end':rd.line_num,'cells':cells});last=rd.line_num
   eq(source+':complete-records-with-header-and-blank',rs,pj('extracted/'+source+'-records.json.gz'))
   if source=='registration-2024-nov1':
    assert raw.startswith(b'\xef\xbb\xbf') and len(raw.splitlines(keepends=True)[0])==550 and rs[-1]['record']==2538 and rs[-1]['cells']==[] and raw.endswith(b'\r\n\r\n');result['registration_roles']={'header_byte_span':[0,550],'includes_BOM':True,'blank_logical_record':2538,'blank_raw_bytes_hex':'0d0a','fields':None,'data_rows':2536}
  raw=ownbody('enr-2024-results-report');rd=csv.reader(io.StringIO(raw.decode('cp1252'),newline=''));rs=[];last=0;header=next(rd);last=rd.line_num
  for i,cells in enumerate(rd,2):
   if cells[header.index('OfficeId')]=='cc200':rs.append({'record':i,'line_start':last+1,'line_end':rd.line_num,'cells':cells})
   last=rd.line_num
  bulk=pj('extracted/bulk-requested-offices.json.gz');eq('bulk-senate-entire-source-rows-including48-null-id-zero',rs,[r for r in bulk['rows'] if r['cells'][header.index('OfficeId')]=='cc200']);eq('bulk-complete-header',header,bulk['header'])
  # All17 orders are own independently regenerated original-source results; peer used only for comparison.
  own=json.loads((out/'sensitivity-orders.json').read_text());peer=pj('all-source-sensitivity-orders.json.gz');eq('17-order-names',sorted(own),sorted(peer));orders={}
  for key,z in own.items():
   p=peer[key];a=[{'key':r['key'],'record':r['source_record'],'value':r['reported_candidate_writein_votes'],'rank':r['rank'],'cumulative':r['cumulative_votes']} for r in z['order']];eq(key+':complete-ordered-units-cumulative',a,p['order']);m=z['minimum80'];eq(key+':threshold-controls',[z['total'],len(a),m['count'],m['preceding']['votes'],m['votes'],(4*z['total']+4)//5],[p['total'],p['known_count'],p['minimum80_count'],p['preceding_votes'],p['crossing_votes'],p['minimum_integer_volume']]);eq(key+':unknown-source-identity-set',sorted(z.get('unknown_keys',[])),sorted(p['unknown_keys']))
   if z.get('unknown_keys',[])!=p['unknown_keys']:distinctions.append({'scope':key,'representation':'unknown-key array traversal order; same exact keys and masks, no values changed','own_order':z.get('unknown_keys',[]),'peer_order':p['unknown_keys'],'peer_to_own_permutation':[z['unknown_keys'].index(x) for x in p['unknown_keys']]})
   orders[key]={'units':len(a)+len(p['unknown_keys']),'known':len(a),'top15_votes':sum(r['value'] for r in a[:15]),'denominator':z['total'],'minimum80_count':m['count'],'preceding':m['preceding'],'crossing_key':m['crossing_key'],'crossing_votes':m['votes'],'remainder_count':m['remainder_count'],'remainder_votes':m['remainder_votes'],'complete_order_sha256':sha(json.dumps(a,separators=(',',':')).encode())}
  result['orders']=orders
 # Complete receipt metadata comparison by frozen receipt identity, not logical ID alone; no-body failures distinct.
 ix=json.loads((T/'source/acquisition-index.json').read_text());success={e['full_receipt']['id']:e for e in ix['receipts'] if e['full_receipt']['hops'][-1].get('status')==200};fail=[e for e in ix['receipts'] if e['full_receipt']['hops'][-1].get('body_path') is None];pins=pj('source/input-pins.json')['sources'];shared=[]
 for p in pins:
  if p['id'] in success:
   e=success[p['id']];eq('shared-complete-request-redirect-status-header-clock-body-receipt:'+p['id'],e['full_receipt'],p['receipt']);eq('shared-receipt-bytehash:'+p['id'],e['receipt_sha256'],p['receipt_sha256']);shared.append(p['id'])
 assert len(ix['receipts'])==165 and len({e['full_receipt']['id'] for e in ix['receipts']})==160 and len(fail)==5 and len(shared)==160
 result['receipts']={'own_frozen_receipt_files':165,'own_logical_source_ids':160,'shared_successful_full_receipts':160,'preserved_failure_receipts':fail,'not_equated':'Five earlier no-body sandbox DNS receipts remain separate from160successful retries. Peer fixed shared source pins contain successful receipts; its extra sources are outside shared core. No clocks or errors replaced.'}
 for n in ['peer-reconciliation.json','peer-additional-reconciliation.json','peer-all-order-audit.json']:
  x=pj(n);assert x['differences']==[];result.setdefault('captured_reverse_proof',[]).append({'path':n,'sha256':sha(P.read('data/baselines/'+n)),'scope':x['scope'],'differences':x['differences']})
 result['checker_sha256']=sha(Path(__file__).read_bytes())
 result['source_position_adapter']='Peer parent historical_record is an integer reference to its independently extracted complete historical row; own parent is the whole row object. References checked against exact raw record numbers and full row equality above.'
 result.update(status='pass',comparison_count=len(checks),checks=checks,representation_distinctions=distinctions,native_candidate_method_objects=native_method,api_complete_scopes=134,historical_native_counts={'2024':2669,'2020':2846,'2018':2825},all_parents=133,source_value_differences=[])
 return result
if __name__=='__main__':
 try:
  result=run();(R/'reciprocal.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','comparison_count','api_complete_scopes','native_candidate_method_objects','historical_native_counts']}))
 except Exception:
  stamp=str(len(list(H.glob('reciprocal-failure-*'))));(H/f'reciprocal-failure-{stamp}.txt').write_text(traceback.format_exc());(H/f'reciprocal-failure-{stamp}.py.gz').write_bytes(gzip.compress(Path(__file__).read_bytes(),mtime=0));raise
