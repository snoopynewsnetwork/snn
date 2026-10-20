#!/usr/bin/env python3
"""Read only frozen original-first packages; write bounded source-core evidence only.
Never imports or executes peer code. No network or peer live-path reads.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import csv,gzip,hashlib,io,json,re,tarfile,collections,argparse,copy
T=Path(__file__).resolve().parents[1];S=T.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def enc(x):return (json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode()
def leaves(x):
 if isinstance(x,dict):return sum(leaves(v) for v in x.values())
 if isinstance(x,list):return sum(leaves(v) for v in x)
 return 1
class Frozen:
 def __init__(self,path):
  self.path=path;self.inv=json.loads((path/'inventory.json').read_bytes());self.idx={r['path']:r for r in self.inv['entries']};self.data={}
  assert len(self.idx)==len(self.inv['entries'])
  for a in self.inv['archives']:
   b=(path/a['path']).read_bytes();assert (len(b),sha(b))==(a['bytes'],a['sha256'])
   with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz')as f:
    for m in f:self.data[(a['path'],m.name)]=f.extractfile(m).read()
 def read(self,path):
  r=self.idx[path];b=self.data[r['archive'],r['member']] if 'archive'in r else (S/r['immutable_original_path']).read_bytes()
  assert (len(b),sha(b))==(r['bytes'],r['sha256']),path
  return b
 def verify(self):
  for k in self.idx:self.read(k)
  for r in self.inv.get('external_immutable_originals',[]):
   b=(S/r['path']).read_bytes();assert (len(b),sha(b))==(r['bytes'],r['sha256'])
 def js(self,path):return json.loads(self.read(path))
 def csv(self,path):return list(csv.DictReader(io.StringIO(self.read(path).decode())))
 def jl(self,path):return [json.loads(l)for l in gzip.decompress(self.read(path)).decode().splitlines()]
O=Frozen(T/'source/history/pre-reciprocal-v1');P=Frozen(T/'source/peer-capture-v1')
def oj(n):return O.js('data/turnout/'+n)
def pj(n):return P.js('data/baselines/'+n)
def oc(n):return O.csv('data/turnout/'+n)
def pc(n):return P.csv('data/baselines/'+n)
def ol(n):return O.jl('data/turnout/'+n)
def pl(n):return P.jl('data/baselines/'+n)
def metric(rows):
 total=sum(v for k,v in rows);s=0;out=[]
 for i,(k,v) in enumerate(sorted(rows,key=lambda t:(-t[1],t[0])),1):s+=v;out.append(dict(key=k,votes=v,rank=i,cumulative_votes=s))
 n=next(i for i,r in enumerate(out,1)if 5*r['cumulative_votes']>=4*total)
 return dict(total=total,full_order=out,top15_votes=sum(r['votes']for r in out[:15]),minimum80=n,preceding_votes=out[n-2]['cumulative_votes']if n>1 else 0,crossing_key=out[n-1]['key'],crossing_votes=out[n-1]['cumulative_votes'],priority_keys=[r['key']for r in out[:n]],remainder_keys=[r['key']for r in out[n:]],remainder_votes=total-out[n-1]['cumulative_votes'])
def audit():
 O.verify();P.verify();evidence={};adapters={};positions=set();maps=[]
 # Full old manifest and every old witness target use reconstructed bodies, not overwritten paths.
 mf=oj('asset-manifest.json')
 for r in mf['owned_assets']:
  b=O.read(r['path']);assert (len(b),sha(b))==(r['bytes'],r['sha256'])
 for r in oj('pre-peer-witness-v1.json')['pinned_files']:
  b=O.read(r['path']);assert (len(b),sha(b))==(r['bytes'],r['sha256'])
 pm=pj('asset-manifest.json')
 for r in pm['assets']:
  b=P.read(r['path']);assert (len(b),sha(b))==(r['bytes'],r['sha256'])
 for r in pj('source/pre-peer-body-map.json'):
  b=gzip.decompress(P.read('data/baselines/'+r['frozen_body']));assert sha(b)==r['raw_sha256']
  w=next(w for w in pj('source/pre-peer-witness.json')['files']if w['path']==r['witness_path']);assert (len(b),sha(b))==(w['bytes'],w['sha256'])
 history=pj('source/history/seal-input-repair-v1/inventory.json');historical={}
 for r in history['owned_files']:
  stored=P.read('data/baselines/'+r['body']);assert (len(stored),sha(stored))==(r['stored_bytes'],r['stored_sha256']);body=gzip.decompress(stored);assert (len(body),sha(body))==(r['bytes'],r['sha256']);historical[r['path']]=body
 old_peer_mf=json.loads(historical['data/baselines/asset-manifest.json'])
 for r in old_peer_mf['assets']:
  body=historical[r['path']];assert (len(body),sha(body))==(r['bytes'],r['sha256']),r['path']
 evidence['peer_historical_packaging']=dict(restored_bodies=len(historical),old_manifest_targets=len(old_peer_mf['assets']),historical_exclusions=old_peer_mf['self_hash_exclusions'],qualification='All prior bodies/manifest targets verified against reconstructed historical bytes; superseded exclusions are retained historical definitions, never current rules.')
 evidence['frozen_history']=dict(own_bodies=len(O.idx),peer_bodies=len(P.idx),old_owned_manifest_targets=len(mf['owned_assets']),old_shared_targets=len(mf['shared_assets']),own_witness_targets=len(oj('pre-peer-witness-v1.json')['pinned_files']),peer_witness_targets=len(pj('source/pre-peer-body-map.json')),peer_manifest_sha256=sha(P.read('data/baselines/asset-manifest.json')),scope='600 peer bodies are frozen provenance, not 600 semantic equality claims')
 oi=oj('source/original-inventory.json')+oj('source/acquired/pdf-text-inventory.json');pi=pj('source/independent-original-inventory.json');pidx={r['source_key']:r for r in pi};originals=[];texts={}
 for r in oi:
  k=r['source_key'];p=pidx.get(k)
  if not p:continue
  assert (r['original_sha256'],r['original_bytes'])==(p['raw_sha256'],p['raw_bytes']),k
  path=r.get('text_path','source/acquired/'+k+'.layout.txt.gz');raw=gzip.decompress(O.read('data/turnout/'+path));pr=gzip.decompress(P.read('data/baselines/'+p['text_path']))
  assert raw==pr,k;assert sha(raw)==r['text_sha256']==p['text_raw_sha256'];texts[k]=raw.decode(errors='replace')
  if 'member_name'in r:assert (r['member_name'],r['ZIP_member_ordinal'],r['CRC32'])==(p['origin']['member'],p['origin']['ordinal'],p['origin']['CRC'])
  originals.append(dict(source_key=k,original_sha256=r['original_sha256'],original_bytes=r['original_bytes'],text_sha256=sha(raw),pages=r.get('pages',r.get('PDF_pages')),own_inventory=r,peer_inventory=p))
 evidence['originals']=dict(shared_entities=len(originals),archive_members=sum('member_name'in r['own_inventory']for r in originals),full_raw_identity_and_full_text_equal=True,peer_only_sources=[r for r in pi if r['source_key']not in texts],objects=originals,qualification='Unrelated offices remain in complete original bytes and full text; no extra-office normalization implied.')
 # Full receipts, including failed responses, headers, redirects, requests and clocks.
 receipts=pj('source/inputs/original-receipts-v1.json');receiptmap=[]
 for r in receipts:
  source=r['source'];path=r['receipt_path'];match=None
  if path=='data/turnout/source/shared-original-pins.json':
   match=next((v for v in oj('source/shared-original-pins.json')if v.get('id')==source.get('id')),None)
  elif path in O.idx:match=O.js(path)
  if match is not None:assert source==match,source.get('id',path)
  receiptmap.append(dict(peer_receipt_path=path,source_id=source.get('id'),full_receipt_equal=match==source if match is not None else None,peer_only=match is None,source=source))
 evidence['receipts']=dict(compared_full_objects=sum(r['full_receipt_equal']is True for r in receiptmap),peer_only=sum(r['peer_only']for r in receiptmap),objects=receiptmap)
 def rowtext(k,page,line):return texts[k].split('\f')[int(page)-1].splitlines()[int(line)-1]
 cs=oc('county-candidates.csv');ps=pc('county-candidates.csv');ix={(r['contest'],r['county'],int(r['source_candidate_column'])-1):r for r in ps};assert len(ix)==len(cs)==864
 specs=collections.defaultdict(list)
 for c in oj('candidate-universe.json'):specs[c['contest']].append(c['candidate'])
 for c in cs:
  p=ix[c['contest'],c['county'],int(c['column_index'])]
  for a,b in [('county_fips','fips'),('candidate','candidate'),('party_label','party_source'),('votes','votes'),('source_key','source_key'),('PDF_page','page'),('text_line_1based','line'),('raw_line','raw_line')]:assert c[a]==p[b],(c,a)
  assert c['raw_line']==rowtext(c['source_key'],c['PDF_page'],c['text_line_1based'])
  positions.add((c['source_key'],int(c['PDF_page']),int(c['text_line_1based']),'candidate',int(c['column_index'])))
  maps.append(dict(kind='county_candidate',original_position=[c['source_key'],int(c['PDF_page']),int(c['text_line_1based']),int(c['column_index'])],own=c,peer=p,comparison='all identity/count/party/raw/locator fields; derived key/scope aliases explicit'))
 sf=pj('state-controls.json')
 for f in oj('source/statewide-footers.json'):
  p=sf[f['contest']];assert all(f[k]==p[k]for k in ['values','page','line','raw_line']);assert f['raw_line']==rowtext(f['source_key'],f['page'],f['line'])
  assert [sum(int(c['votes'])for c in cs if c['contest']==f['contest']and int(c['column_index'])==j)for j in range(len(f['values']))]==f['values']
  page=texts[f['source_key']].split('\f')[f['page']-1];assert pj('source/abstract-evidence.json')[f['contest']]['full_page']==page
 evidence['county']=dict(candidate_positions=864,county_vectors=144,full_abstract_pages=4,statewide_footers=4,all_compared_fields_equal=True,candidate_universe=oj('candidate-universe.json'),candidate_scope='Misc. generic unresolved eligibility; party/source headers retained verbatim in equal full original pages')
 adapters['county']=dict(column='own zero-based column_index = peer one-based source_candidate_column - 1',scope={'named_ballot_candidate':'named candidate','reported_Misc_unresolved_writein_validity':'generic Misc/write-in (not eligibility)'},keys='Own candidate_key is derived. Literal candidate and party fields agree; full source headers retained, no header inferred from normalized names.')
 # Independently re-tokenize every published participation group and clock from equal original pages.
 participation=pc('participation-controls.csv');ptotal={(r['year'],r['county']):r for r in participation if r['group_source']=='Total'}
 pp=[]
 for r in participation:
  page=texts[r['source_key']].split('\f')[int(r['page'])-1];line=rowtext(r['source_key'],r['page'],r['line']);assert line==r['raw_line']
  header=next(l for l in page.splitlines()if re.search('Republican|Independent|Pacific Green|We The People|Other|^\\s+Total\\s*$',l));groups=re.split(r'\s{2,}',header.strip());idx=groups.index(r['group_source']);tail=re.match(r'^\s*'+re.escape(r['county'])+r'\s+(.+)$',line)[1].split();a,b,pct=tail[3*idx:3*idx+3]
  assert (int(a.replace(',','')),int(b.replace(',','')),pct)==(int(r['Number Eligible']),int(r['Ballots Returned']),r['Percent Voting_source'])
  pp.append(dict(peer=r,source_header=header,source_field_offset=3*idx,source_clock_lines=page.splitlines()[:7]))
  for field in range(3):positions.add((r['source_key'],int(r['page']),int(r['line']),'participation',3*idx+field))
 for r in oc('participation-controls.csv'):
  p=ptotal[r['year'],r['county']]
  for a,b in [('registration_Number_Eligible','Number Eligible'),('ballots_Returned','Ballots Returned'),('source_key','source_key'),('PDF_page','page'),('text_line_1based','line'),('raw_line','raw_line')]:assert r[a]==p[b]
 for year in ['2020','2022','2024']:
  groups={r['group_source']for r in participation if r['year']==year}
  for group in groups:
   rr=[r for r in participation if r['year']==year and r['group_source']==group];footer=next(r for r in rr if r['county']=='Total');assert len(rr)==37
   for field in ['Number Eligible','Ballots Returned']:assert sum(int(r[field])for r in rr if r['county']!='Total')==int(footer[field])
 monthly=pc('monthly-registration.csv');mi={(r['year'],r['county']):r for r in monthly}
 for r in monthly:
  line=rowtext(r['source_key'],r['page'],r['line']);assert line==r['raw_line'];v=re.match(r'^\s*'+re.escape(r['county'])+r'\s+(.+)$',line)[1].split()
  assert [int(v[i].replace(',',''))for i in [0,1,3]]==[int(r[k])for k in ['this_month','last_month','prior_year_month']]
 for year in ['2020','2022','2024']:
  rr=[r for r in monthly if r['year']==year];footer=next(r for r in rr if r['county']=='Total');assert len(rr)==37
  for field in ['this_month','last_month','prior_year_month']:assert sum(int(r[field])for r in rr if r['county']!='Total')==int(footer[field])
 for r in oc('monthly-registration.csv'):
  p=mi[r['year'],r['county']]
  for a,b in [('this_month','this_month'),('last_month','last_month'),('earlier_reference','prior_year_month'),('page','page'),('line','line'),('source_key','source_key'),('raw_line','raw_line')]:assert r[a]==p[b]
  assert r['change_percent_literal']in r['raw_line']and r['earlier_change_percent_literal']in r['raw_line']
 evidence['participation']=dict(own_total_rows=108,peer_group_rows=len(participation),group_records=pp,monthly_own_county_rows=108,monthly_peer_rows_including_footers=len(monthly),monthly_full_rows=monthly,full_source_text_and_clocks_equal=True,qualification='Peer party groups are source-verified here, not adopted into own county total export. Monthly population/date is distinct from election eligible/returned.')
 # Native full-object adapters. All fields retained in frozen objects; representation-only/unmapped fields are explicit.
 units=oj('native/units.json');pu=pj('native-units.json');nix={(r['source_key'],r['contest'],r['unit_literal']):r for r in units if r['presentation']=='native'};shared=[];diff=[];control_diff=[];control_count=0;candidate_count=0
 aliases={'ballots_source':'ballots','registered_voters_source':'registered_voters','over_voted_ballots_source':'over_voted_ballots','overvotes_source':'overvotes_in_ballot_heading','undervotes_source':'undervotes_in_ballot_heading','Overvotes':'overvotes','Undervotes':'undervotes','Cast Votes excluding Misc_source':'Cast Votes'}
 for p in pu:
  key=p['source_key'],p['contest'],p['unit_label'];o=nix.get(key)
  if o is None:continue
  assert (o['county'],o['county_fips'])==(p['county'],p['fips'])
  fields=[]
  for j,name in enumerate(specs[p['contest']]):
   a=o['choices'].get(str(j));b=p['candidates'].get(name);equal=a==b
   if str(j)in o['choices']and name in p['candidates']:
    candidate_count+=1
    if not equal:diff.append(dict(key=key,candidate=name,own=a,peer=b,own_locators=o['locators'],peer_positions=p['source_positions']))
   fields.append(dict(kind='candidate',own_field=str(j),peer_field=name,own=a,peer=b,status='equal'if equal else 'missing_or_different',own_present=str(j)in o['choices'],peer_present=name in p['candidates']))
  for name,b in p['controls'].items():
   target=aliases.get(name,name);present=target in o['fields'];a=o['fields'].get(target);origin='normalized control'
   if name=='Miscellaneous Write-In' and p['source_key']=='clackamas-2024-canvass':a=o['choices'].get('7');present='7'in o['choices'];origin='same raw column also candidate Misc, nonadditive'
   if not present:
    # Exact CSV literals remain in all own locator dictionaries, including null/empty party strings.
    raw=[q['raw_source_row'] for q in o['locators']if 'raw_source_row'in q and name in q['raw_source_row']]
    if raw and all(q[name]==b for q in raw):present=True;a=b;origin='full own CSV locator dictionaries'
   if present:
    control_count+=1
    if a!=b:control_diff.append(dict(key=key,field=name,own=a,peer=b,own_locators=o['locators'],peer_positions=p['source_positions']))
   fields.append(dict(kind='control',peer_field=name,own_field=target,own=a,peer=b,own_present=present,status='equal'if present and a==b else 'unmapped_or_different',binding=origin))
  # Full semantic schema disposition: every key of both objects accounted for, never asserted equal wholesale.
  shared.append(dict(original_key=key,own_unit_key=o['unit_key'],peer_unit_key=p['unit_key'],own_object_sha256=sha(enc(o)),peer_object_sha256=sha(enc(p)),own_fields=sorted(o),peer_fields=sorted(p),field_comparisons=fields,own_locators=o['locators'],peer_source_positions=p['source_positions'],peer_control_observations=p.get('control_observations'),own_native_id=o.get('source_native_id'),own_native_contest_id=o.get('native_contest_id'),peer_method_source=p.get('method_source'),own_additive=o['additive'],own_admin_role=o['presentation'],peer_overlap=p.get('source_overlap'),peer_missing_columns=p.get('missing_candidate_columns'),peer_unresolved_conflict=p.get('unresolved_normalization_conflict'),peer_acceptance=[p.get('current_source_accepted'),p.get('geography_accepted')]))
  assert not p.get('current_source_accepted')and not p.get('geography_accepted')
 evidence['native_semantic_mapping']=dict(shared_objects=len(shared),shared_candidate_cells=candidate_count,candidate_differences=diff,shared_control_cells=control_count,control_differences=control_diff,objects=shared,own_only_objects=[r for r in units if (r['source_key'],r['contest'],r['unit_literal'])not in {(p['source_key'],p['contest'],p['unit_label'])for p in pu}],peer_only_objects=[p for p in pu if (p['source_key'],p['contest'],p['unit_label'])not in nix],qualification='Whole normalized objects are compared under explicit field disposition, not claimed byte/schema equal. Pair-margin/model fields are outside turnout audit; methods/source positions/admin/controls remain explicit. Unmapped controls/locators are differences in extraction scope, not zero.')
 adapters['native']=dict(identity='Exact (source_key, contest, literal unit label). Never across years/current geography.',control_fields=aliases,metadata_disposition={'source_key/county/fips/contest/unit_label':'exact mapped identity','candidates/controls':'all fields examined; missing/null retained','source_positions/control_observations':'full arrays retained in mapping, exact raw row mapping below','method_source/source_overlap':'source presentation metadata retained, never added','unit_key/unit_kind':'versioned representation, not geographic equivalence','A/B/A_votes/B_votes/pair_votes/A_pair_share':'peer partisanship-derived fields excluded from source-core equality; preserved in captured full objects','unresolved_normalization_conflict/missing_candidate_columns':'explicit extraction status, not repaired','reported_all_choice_votes':'recomputed only for closed known/source scopes','current_source_accepted/geography_accepted':'false checked'})
 # Unique raw records, not each repeated derived control. Full CSV dictionaries preserve empty/null/method fields.
 obs=ol('native/observations.jsonl.gz');rawix={}
 for r in obs:
  if 'raw_source_row'in r:rawix[r['source_key'],r['CSV_record_1based']]=r['raw_source_row']
 rawcomparisons=[];rawmissing=[]
 for p in pl('source/raw-native-rows.jsonl.gz'):
  if isinstance(p['raw'],dict)and 'csv_record'in p['position']:
   key=p['source_key'],p['position']['csv_record']
   if key in rawix:
    ownraw=rawix[key];peerraw=p['raw'];representation='full dictionary exact'
    if isinstance(ownraw,list) and set(peerraw)=={'headers','fields'}:
     assert ownraw==peerraw['fields'];originalrows=list(csv.reader(io.StringIO(texts[key[0]])));assert peerraw['headers']in originalrows[:key[1]]
     representation='own literal row list = peer fields; peer full header independently verified in same original CSV before source row'
    else:assert ownraw==peerraw
    rawcomparisons.append(dict(source_key=key[0],csv_record=key[1],fields=len(ownraw),raw_sha256=sha(enc(ownraw)),representation=representation,peer_headers=peerraw.get('headers')if isinstance(peerraw,dict)else None))
   else:rawmissing.append(p)
 dedup={(r['source_key'],r['csv_record']):r for r in rawcomparisons};assert len(dedup)==len(rawcomparisons)
 m2024=[r for r in rawcomparisons if r['source_key']=='multnomah-2024-sovc2'];assert len(m2024)==856 and sum(r['fields']for r in m2024)==11128
 evidence['raw_CSV']=dict(unique_records=len(rawcomparisons),unique_raw_fields=sum(r['fields']for r in rawcomparisons),Multnomah2024_records=856,Multnomah2024_fields=11128,records=rawcomparisons,peer_only_raw_records=rawmissing,qualification='Records counted once by original CSV row, never once per derived counter. Full raw dictionary equality includes blanks, choice/slate labels and all choice counters.')
 # Every shared raw PDF/text object is bound to a source page/line or explicitly unmatched.
 textmap=[];unique_text=set()
 def rawstrings(value,path=()):
  if isinstance(value,str):
   if not path or path[-1]=='raw_line':yield path,value
  elif isinstance(value,dict):
   for a,b in value.items():yield from rawstrings(b,path+(a,))
  elif isinstance(value,list):
   for i,b in enumerate(value):yield from rawstrings(b,path+(i,))
 ownlines={(r['source_key'],r.get('page'),r.get('line'),r.get('raw_line'))for r in obs if 'raw_line'in r}
 for number,r in enumerate(pl('source/raw-native-rows.jsonl.gz')):
  if r['source_key']not in texts:continue
  if isinstance(r['raw'],dict)and 'csv_record'in r['position']:continue
  for subpath,line in rawstrings(r['raw']):
   key=r['source_key'];pos=r['position'];flat=pos
   while isinstance(flat,list):flat=flat[0]if flat else {}
   page=flat.get('page');matched=[]
   if page is not None:
    pages=texts[key].split('\f')
    if page<=len(pages):matched=[i for i,v in enumerate(pages[page-1].splitlines(),1)if v==line]
   if not matched:
    # Group outer position may name the contest heading; child carries own page.
    for pg,body in enumerate(texts[key].split('\f'),1):
     found=[i for i,v in enumerate(body.splitlines(),1)if v==line]
     if found:matched=[(pg,i)for i in found];break
   ownobs=[(a,b)for k,a,b,v in ownlines if k==key and v==line] if not matched else []
   ocr=None;extraction=flat.get('extraction')
   if not matched and not ownobs and isinstance(extraction,str) and extraction in O.idx and extraction.endswith('.txt.gz'):
    body=gzip.decompress(O.read(extraction));lines=body.decode().splitlines();hits=[i for i,v in enumerate(lines,1)if v==line]
    if hits:ocr=dict(path=extraction,raw_sha256=sha(body),matching_lines_1based=hits,original_position=flat)
   status='equal_original_text'if matched else 'equal_own_source_observation'if ownobs else 'equal_frozen_own_OCR_text'if ocr else 'source_only_no_exact_own_text_locator'
   item=dict(peer_raw_object=number,source_key=key,peer_outer_position=pos,subpath=subpath,raw_line=line,own_text_matches=matched,own_observation_matches=ownobs,own_OCR_match=ocr,status=status)
   textmap.append(item);unique_text.add((key,tuple(map(str,matched or ownobs)),line))
 evidence['raw_text_positions']=dict(objects_or_nested_rows=len(textmap),unique_raw_rows=len(unique_text),status_counts=dict(collections.Counter(r['status']for r in textmap)),mapping=textmap,qualification='Every shared raw text object examined in full. Repeated derived controls do not inflate unique raw-row count. Unmatched OCR/visual/extraction source-only rows remain explicit and are not claimed equal normalization.')
 # Method rows: source line/dictionary and literal lanes, not ballot categories.
 methods=[]
 for m in pj('native-method-lanes.json'):
  x=dict(m);key=m['source_key'];raw=m.get('raw_fields');line=m.get('raw_line');matched=False
  if raw is not None:
   rec=m['position'].get('csv_record');matched=rawix.get((key,rec))==raw
   if matched:
    expected=[dict(method_literal='Total',votes_literal=raw['Total Votes']),dict(method_literal='Vote by Mail',votes_literal=raw['Vote by Mail Votes'])];assert m['lanes']==expected
  elif key in texts and line is not None:
   pos=m['position'];page=texts[key].split('\f')[pos['page']-1];matched=line in page.splitlines()
   if matched:
    pcts=list(re.finditer(r'\d+(?:\.\d+)?%',line));labels=[v['method_literal']for v in m['lanes']]
    if labels==['AB','ED','EV']:
     values=[int(v.replace(',',''))for v in re.findall(r'\d[\d,]*',line[pcts[0].end():])];assert [v['votes']for v in m['lanes']]==values
    elif labels==['Absentee Voting','Total']:
     values=[int(v.replace(',',''))for v in re.findall(r'(\d[\d,]*)\s+\d+(?:\.\d+)?%',line)];assert [v['votes']for v in m['lanes']]==values
    else:raise AssertionError(('unmapped method columns',m))
  x['own_original_raw_position_verified']=matched;methods.append(x)
 evidence['methods']=dict(rows=len(methods),own_original_positions_verified=sum(m['own_original_raw_position_verified']for m in methods),rows_with_no_own_original_position=[m for m in methods if not m['own_original_raw_position_verified']],full_objects=methods,qualification='Full source method labels/lanes retained nonadditive. No inferred election-day/absentee allocation.')
 # Known full 510-source object closure and both tie-key representations.
 known=oj('known-native-ranking.json');kn=[];knownmaps=[];px={p['unit_key']:p for p in pu};bindings=pj('source/nonadditive-presentation-bindings.json')
 source_2024=[p for p in pu if p['contest']=='2024-president'and p['source_key']!='multnomah-2024-president'];assert len(source_2024)==510
 for p in source_2024:
  key='OR:2024-11-05:'+p['fips']+':president:'+p['unit_label'].removeprefix('Precinct ');o=next(r for r in known['full_order']if r['key']==key);vec=[p['candidates'][n]for n in specs['2024-president']];assert vec==o['candidate_vector'];kn.append((key,sum(vec)))
  for presentation in o['source_presentations']:
   pp=next(v for v in pu if v['source_key']==presentation['source_key']and v['unit_label']==presentation['literal_unit']and v['contest']=='2024-president');assert [pp['candidates'][n]for n in specs['2024-president']]==vec
  knownmaps.append(dict(own_key=key,peer_source_key=p['unit_key'],peer_source_positions=p['source_positions'],own_presentations=o['source_presentations'],source_native_constituent_ids=o['source_native_constituent_ids'],current_result_id=o['current_result_id'],current_geometry_id=o['current_geometry_id'],candidate_vector=vec))
 mk=metric(kn);assert [r['key']for r in known['full_order']]==[r['key']for r in mk['full_order']]
 assert (known['total'],known['top15']['numerator'],known['minimum80']['count'],known['minimum80']['preceding_votes'],known['minimum80']['cumulative_votes'],known['remainder']['votes'])==(mk['total'],mk['top15_votes'],mk['minimum80'],mk['preceding_votes'],mk['crossing_votes'],mk['remainder_votes'])
 source_order=metric([(r['unit_key'],sum(r['candidates'].values()))for r in source_2024]);stored=pc('known-native-order.csv');assert [(r['key'],int(r['votes']),int(r['cumulative_votes']))for r in stored]==[(r['key'],r['votes'],r['cumulative_votes'])for r in source_order['full_order']]
 assert len(bindings)==107 and all(not b['additive']and b['candidate_vectors_equal']for b in bindings)
 for r in pc('known-native-controls.csv'):
  p=px[r['key']];q=px[next(b['alternative_source_key']for b in bindings if b['native_source_key']==r['key'])]if p['source_key']=='multnomah-2024-sovc2'else p
  c=q['controls'];pick=lambda *ks:next((c[k]for k in ks if k in c),None)
  for a,b in [('reported_choices',sum(p['candidates'].values())),('ballots_source',pick('ballots_source','Total Ballots Cast')),('registration_source',pick('registered_voters_source','Registered Voters')),('overvotes_source',pick('Overvotes')),('undervotes_source',pick('Undervotes'))]:assert int(r[a])==b
  assert int(r['reported_choices'])+int(r['overvotes_source'])+int(r['undervotes_source'])==int(r['ballots_source'])
 evidence['known_2024']=dict(source_objects=len(source_2024),including_overlapping_PDF_objects=len(source_2024)+107,candidate_cells=4080,control_rows=510,nonadditive_bindings=bindings,canonical_key_order=mk,peer_source_key_order=source_order,mapping=knownmaps,qualification='Source-local ties can differ; full order recomputed under each exact key. Versioned FIPS/native re-expression agrees. Not current/legal geometry approval.')
 # Fourteen county sensitivity orders rebuilt from peer OWN source counts/participation, never substituted in turnout products.
 ranks={};ourranks=oj('county-sensitivities.json')
 for ct in specs:
  for scope in ['reported_votes','named_votes']:
   vals=collections.defaultdict(int)
   for c in ps:
    if c['contest']==ct and (scope=='reported_votes'or c['candidate']!='Misc.'):vals[c['fips']]+=int(c['votes'])
   ranks[ct+'_'+scope]=metric(list(vals.items()))
 fips={r['county']:r['county_fips']for r in cs}
 for year in ['2020','2022','2024']:
  for ownfield,peerfield in [('ballots_Returned','Ballots Returned'),('registration_Number_Eligible','Number Eligible')]:ranks[year+'_statistical_'+ownfield]=metric([(fips[r['county']],int(r[peerfield]))for r in participation if r['year']==year and r['group_source']=='Total'and r['county']!='Total'])
 for key,m in ranks.items():
  r=ourranks[key];assert [(v['key'],v['votes'],v['cumulative_votes'])for v in r['full_order']]==[(v['key'],v['votes'],v['cumulative_votes'])for v in m['full_order']]
  assert (r['top15']['numerator'],r['minimum80']['count'],r['minimum80']['preceding_votes'],r['minimum80']['cumulative_votes'],r['minimum80']['ordered_keys'],r['remainder']['keys'],r['remainder']['votes'])==(m['top15_votes'],m['minimum80'],m['preceding_votes'],m['crossing_votes'],m['priority_keys'],m['remainder_keys'],m['remainder_votes'])
 evidence['county_orders']=ranks
 # Native normalized coverage, with exact divergent source objects retained. No repair from peer numeric values.
 ore=oj('native/county-reconciliation.json');pre=pj('native-reconciliation.json');coverage={}
 for ct in specs:
  a={r['county']for r in ore if r['contest']==ct and r['complete_candidate_vectors_and_county_columns_close']};b={r['county']for r in pre if r['contest']==ct and r['column_closed']}
  coverage[ct]=dict(own_closed=sorted(a),peer_closed=sorted(b),own_only=sorted(a-b),peer_only=sorted(b-a),own_source_groups=[r for r in ore if r['contest']==ct and r['county']in(a^b)],peer_source_groups=[r for r in pre if r['contest']==ct and r['county']in(a^b)])
 evidence['coverage']=coverage
 contract=oj('priority-set.json');pcontract=pj('priority-contract.json');assert contract['complete_order']is None and contract['top15']is None and contract['minimum80']is None and contract['ordered_priority_keys']is None
 assert pcontract['canonical_statewide_native_order']is None and pcontract['canonical_minimum80']is None
 parents=contract['all_36_county_parents'];assert len(parents)==36 and sum(p['county_presidential_reported_votes']for p in parents)==2244493
 assert sum(p['county_presidential_reported_votes']for p in parents if p['unknown_native_membership'])==1115972
 evidence['contract']=dict(all_36_parents=parents,unknown_parent_count=31,unknown_parent_votes=1115972,canonical_complete_order=None,canonical_priority=None,canonical_remainder=None,coordinator_accepted=False,current_election_accepted=False,current_geometry_accepted=False,all_peer_source_core_acceptance=False)
 vp=oc('nonadditive-vice-president.csv');pv=pc('nonadditive-vice-president.csv')
 assert len(vp)==len(pv)==216
 vpnames=['Nicole Shanahan','Mike ter Maat','JD Vance','Rudolph Ware','Tim Walz','Misc.'];vpparties=['WTP','L','R','PG','D',''];prescols=['0','2','4','5','6','7'];vi={(r['county'],r['candidate']):r for r in pv}
 for r in vp:
  j=prescols.index(r['overlaps_presidential_column']);p=vi[r['county'],vpnames[j]]
  assert r['votes']==p['votes']and r['raw_line']==p['raw_line']and r['PDF_page']==p['source_page']and r['text_line_1based']==p['source_line']and r['nonadditive']=='True'and p['additive']=='False'and p['party_source']==vpparties[j]
  assert r['raw_line']==rowtext(r['source_key'],r['PDF_page'],r['text_line_1based'])
 evidence['vice_president']=dict(own_full_rows=vp,peer_full_rows=pv,scope='Full same original abstract VP page retained, six overlapping columns not added. Schemas/literal names remain separate.')
 evidence['reverse_peer_proof']=dict(path='captured data/baselines/peer-reconciliation.json',sha256=sha(P.read('data/baselines/peer-reconciliation.json')),full_proof=pj('peer-reconciliation.json'),qualification='Historical reverse proof covers its captured own turnout phase only; no final/future equality claim.')
 return dict(schema='oregon.turnout.reciprocal-source-core-v1',peer_agent_id='7c03df8c-f908-40a8-a289-369e4aa26e69',own_original_first_witness_sha256=sha(O.read('data/turnout/pre-peer-witness-v1.json')),peer_original_first_witness_sha256=sha(P.read('data/baselines/source/pre-peer-witness.json')),status='bounded_source_core_agreement_with_explicit_historical_extraction_differences',adapters=adapters,evidence=evidence,county_position_map=maps,unique_county_and_participation_source_field_positions=len(positions),qualification='Not an equality claim for peer calculator/scenarios/live/report/future outputs. No count repair or peer numeric adoption. All canonical/current/geographic/coordinator acceptance remains false or unavailable.')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();result=audit();b=enc(result);dest=T/'peer-reconciliation.json'
 full=T/'source/reciprocal-full-evidence.json.gz';z=gzip.compress(b,mtime=0);assert len(z)<40000000
 e=result['evidence'];summary={k:v for k,v in result.items()if k not in ['evidence','county_position_map']}
 summary.update(full_evidence=dict(path='source/reciprocal-full-evidence.json.gz',raw_bytes=len(b),raw_sha256=sha(b),stored_bytes=len(z),stored_sha256=sha(z)),counts=dict(own_frozen_bodies=len(O.idx),peer_frozen_bodies=len(P.idx),shared_originals=e['originals']['shared_entities'],county_candidate_positions=864,participation_group_rows=e['participation']['peer_group_rows'],monthly_source_rows=e['participation']['monthly_peer_rows_including_footers'],shared_native_objects=e['native_semantic_mapping']['shared_objects'],shared_candidate_cells=e['native_semantic_mapping']['shared_candidate_cells'],shared_control_comparisons=e['native_semantic_mapping']['shared_control_cells'],candidate_differences=len(e['native_semantic_mapping']['candidate_differences']),control_differences=len(e['native_semantic_mapping']['control_differences']),unique_raw_CSV_records=e['raw_CSV']['unique_records'],unique_raw_CSV_fields=e['raw_CSV']['unique_raw_fields'],raw_text_status=e['raw_text_positions']['status_counts'],method_rows=e['methods']['rows'],known_native_rows=510,county_orders=14),coverage=e['coverage'])
 sb=enc(summary)
 if a.write:full.write_bytes(z);dest.write_bytes(sb)
 else:assert full.read_bytes()==z and dest.read_bytes()==sb,'reciprocal full evidence and summary reproduce exactly'
 e=result['evidence'];print(json.dumps(dict(status=result['status'],shared_originals=e['originals']['shared_entities'],shared_native_objects=e['native_semantic_mapping']['shared_objects'],candidate_differences=len(e['native_semantic_mapping']['candidate_differences']),control_differences=len(e['native_semantic_mapping']['control_differences']),unique_CSV_fields=e['raw_CSV']['unique_raw_fields'],proof_sha256=sha(b))))
if __name__=='__main__':main()
