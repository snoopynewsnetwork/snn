"""Independent original/source/asset/target review; never import worker modules."""
from pathlib import Path
from collections import defaultdict
import ast,csv,gzip,hashlib,io,json,math,re,subprocess
D=Path(__file__).resolve().parent;S=D.parent;B=D/'baselines';T=D/'turnout'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def csvrows(p):return list(csv.DictReader(io.StringIO(gzip.decompress(p.read_bytes()).decode())))if p.suffix=='.gz'else list(csv.DictReader(p.open()))
def close(a,b,tol=2e-6):assert math.isfinite(a)and math.isfinite(b)and abs(a-b)<=tol,(a,b)
def clip(x):return max(0,min(1,x))
def freeze(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==b,str(p)
 else:p.write_bytes(b)
def root(rows,margin):
 events=defaultdict(float);V=sum(v for v,q in rows);target=(1+margin)*V/2
 for v,q in rows:
  if v:events[-q]+=v;events[1-q]-=v
 keys=sorted(events);area=0.;slope=0.;prev=keys[0]
 for x in keys:
  end=area+slope*(x-prev)
  if slope>0 and area-1e-9<=target<=end+1e-9:return prev+(target-area)/slope
  area=end;slope+=events[x];prev=x
 assert abs(area-target)<1e-6;return keys[-1]
def main():
 checks={};qa=D/'coordinator-qa/final-first-pair-v1';owned=set();refs=set();assetstats={}
 for directory,ok,rk in [(T,'owned_paths','reused_read_only_objects'),(B,'owned_assets','read_only_references')]:
  mf=load(directory/'asset-manifest.json');entries=mf[ok];paths=set()
  for r,is_owned in [(r,True)for r in entries]+[(r,False)for r in mf[rk]]:
   p=S/r['path'];assert pin(p)=={k:r[k]for k in ['path','bytes','sha256']};assert p.stat().st_size<40_000_000
   if is_owned:assert r['path']not in paths;paths.add(r['path'])
   else:refs.add(r['path'])
  rootpaths=[S/('turnout.md'if directory==T else'county-partisanship.md'),D/('county-turnout.csv'if directory==T else'county-baselines.csv')];actual={str(p.relative_to(S))for p in [*directory.rglob('*'),*rootpaths]if p.is_file()}
  assert actual==paths|{str((directory/'asset-manifest.json').relative_to(S))};assert not owned.intersection(paths);owned.update(paths)
  assert not any(p.name in ['__pycache__','node_modules','.venv']for p in directory.rglob('*'))
  for p in directory.rglob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
  assetstats[directory.name]=dict(owned=len(entries),references=len(mf[rk]),reference_input_pins_also_owned=sorted(paths.intersection(r['path']for r in mf[rk])),exact_membership=True,manifest=pin(directory/'asset-manifest.json'),validation=pin(directory/'validation.json'))
  for p in [*rootpaths,directory/'asset-manifest.json',directory/'validation.json']:freeze(qa/'frozen'/str(p.relative_to(S)),p.read_bytes())
 checks['frozen_assets']=assetstats
 originals={a['id']:a for a in load(D/'news/manifest.json')};pdfs={};sourcepins=[]
 for year,sid in [(2024,'sos-2024-general-canvass'),(2022,'sos-2022-general-canvass'),(2020,'sos-2020-general-canvass')]:
  a=originals[sid];z=(D/'news'/a['asset']).read_bytes();raw=gzip.decompress(z);assert len(raw)==a['bytes']and sha(raw)==a['raw_sha256']and sha(z)==a['stored_sha256'];pdfs[year]=subprocess.run(['pdftotext','-layout','-','-'],input=raw,capture_output=True,check=True).stdout.decode().split('\f');sourcepins.append(a)
 # Candidate controls use signed canvasses. Turnout/registration locators refer
 # to the separate, fully retained election-return archive books.
 archivepdfs={};archivepins=[]
 for year in [2024,2022,2020]:
  a=load(T/f'source/returns-{year}-archive.receipt.json');p=T/'source'/a['asset'];z=p.read_bytes();raw=gzip.decompress(z)
  assert len(z)==a['stored_bytes']and sha(z)==a['stored_sha256']and len(raw)==a['raw_bytes']and sha(raw)==a['raw_sha256']
  archivepdfs[year]=subprocess.run(['pdftotext','-layout','-','-'],input=raw,capture_output=True,check=True).stdout.decode().split('\f');archivepins.append(dict(receipt=pin(T/f'source/returns-{year}-archive.receipt.json'),body=pin(p),original=a))
 county=csvrows(D/'county-baselines.csv');assert len(county)==198;signed={};original_fields=0;registration_fields=0
 for r in county:
  year=int(r['year']);countyname=r['county'];line=pdfs[year][int(r['pdf_page'])-1].splitlines()[int(r['pdf_line'])-1];n={2024:4,2022:3,2020:2}[year];m=re.fullmatch(r'\s*'+re.escape(countyname)+r'\s+('+r'\s+'.join([r'\d[\d,]*']*n)+r')\s*',line);assert m,(year,countyname,line)
  values=[int(x.replace(',',''))for x in m[1].split()];A,BB,O=(values[0],values[2],values[1]+values[3])if year==2024 else(values[0],values[2],values[1])if year==2022 else(values[1],values[0],0)
  assert [A,BB,O,A+BB+O,A+BB]==[int(r[k])for k in ['a_votes','b_votes','other_named_votes','all_named_votes','pair_votes']];original_fields+=len(values);signed[year,countyname]=dict(vector=values,A=A,B=BB,other=O,total=sum(values),fips=r['county_fips'])
  tl=archivepdfs[year][int(r['turnout_pdf_page'])-1].splitlines()[int(r['turnout_pdf_line'])-1];assert tl==r['turnout_raw_line'],(year,countyname,repr(tl),repr(r['turnout_raw_line']));namepattern=re.escape(countyname)if countyname!='Oglala Lakota'else r'(?:Oglala\s+)?Lakota';m=re.search(r'(?:^|\s)'+namepattern+r'\s+([\d,]+)\s+([\d,]+)\s+([\d.]+)\s*%',tl);assert m,(year,countyname,tl)
  assert int(m[1].replace(',',''))==int(r['turnout_table_registered'])and int(m[2].replace(',',''))==int(r['votes_cast_source_label'])and m[3]==r['turnout_percent_literal'];registration_fields+=3
  rl=archivepdfs[year][int(r['registration_pdf_page'])-1].splitlines()[int(r['registration_pdf_line'])-1];assert rl==r['registration_raw_line'];tail=rl.strip()[len(countyname):];numbers=[int(x.replace(',',''))for x in tail.split()];assert numbers[-1]==int(r['registration_active'])and numbers[-2]==int(r['registration_inactive']);registration_fields+=len(numbers)
 assert original_fields==594 and len(signed)==198
 controls={y:[sum(v['vector'][j]for(y2,c),v in signed.items()if y2==y)for j in range({2024:4,2022:3,2020:2}[y])]for y in [2024,2022,2020]};assert controls=={2024:[146859,2778,272081,7204],2022:[91007,14697,242316],2020:[276232,143987]}
 checks['original_signed_county_controls']=dict(county_vectors=198,candidate_fields=original_fields,turnout_registration_fields=registration_fields,controls=controls,source_originals=sourcepins,separate_turnout_registration_originals=archivepins,locator_scope='Candidate PDF locators refer to signed canvasses; turnout and registration PDF locators refer to distinct election-return archive books. Initial coordinator source-selection error retained; worker locators unchanged.')
 # Independently hash-stream the complete ordered 2020 gzip without materializing another PDF.
 a=originals['sos-2020-general-county-canvass'];parts=[]
 for r in a['asset_parts']:
  b=(D/'news'/r['asset']).read_bytes();assert len(b)==r['bytes']and sha(b)==r['sha256']and len(b)<40_000_000;parts.append(b)
 z=b''.join(parts);assert len(z)==a['stored_bytes']and sha(z)==a['stored_sha256'];digest=hashlib.sha256();n=0
 with gzip.GzipFile(fileobj=io.BytesIO(z))as stream:
  while True:
   block=stream.read(8_000_000)
   if not block:break
   digest.update(block);n+=len(block)
 assert n==149141181 and digest.hexdigest()==a['raw_sha256'];checks['ordered_original_reconstruction']=dict(raw_bytes=n,raw_sha256=digest.hexdigest(),ordered_parts=len(parts),stored_bytes=len(z),no_duplicate_original_created=True)
 # Full three-book original transcript was produced before comparison to any worker votes.
 audit=load(D/'coordinator-initial-public-native-review.json');p=S/audit['original_derived_transcript']['path'];assert pin(p)==audit['original_derived_transcript'];books=json.loads(gzip.decompress(p.read_bytes()));native={}
 for y,v in books.items():
  for r in v['units']:
   vv=r['candidate_values'];A,BB,O=(vv[0],vv[2],vv[1]+vv[3])if y=='2024'else(vv[0],vv[2],vv[1])if y=='2022'else(vv[1],vv[0],0)
   native[r['key']]=dict(A=A,B=BB,other=O,total=sum(vv),county=r['county_literal'],year=int(y),label=r['native_label_literal'],candidate_values=vv)
 c=load(T/'priority-set.json');assert pin(T/'priority-set.json')['sha256']=='a1c97454c68c1f30bdb6b7755cd826326e7380318eae74b6452465ee23e9c275'
 ownorder=sorted(books['2024']['units'],key=lambda r:(-r['contest_votes'],r['county_fips'],r['worksheet_ordinal'],r['source_row']));assert c['complete_ordered_keys']==[r['key']for r in ownorder]and c['ordered_priority_keys']==c['complete_ordered_keys'][:304]and c['remainder']['ordered_keys']==c['complete_ordered_keys'][304:]
 for r in c['all_units']:
  n=native[r['key']];assert r['county_literal']==n['county']and r['native_label_literal']==n['label']and list(r['candidate_votes'].values())==n['candidate_values'];assert r['source_native_constituents'][0]['row']==next(a['source_row']for a in ownorder if a['key']==r['key']);assert all(v is None for v in r['separate_fields'].values())
 for parent in c['county_parents']:
  selected=[r for r in c['all_units']if r['county_parent_key']==parent['parent_key']];assert parent['ordered_all_native_keys']==[r['key']for r in selected]and parent['ordered_priority_native_keys']==[r['key']for r in selected if r['priority80']]
 assert len(c['county_parents'])==66 and len(c['ordered_priority_parent_keys'])==39 and not c['coordinator_acceptance']['accepted']and not c['certification_robustness']['proven']
 for year in [2022,2020]:
  rows=c['separate_historical_native_universes'][str(year)]['rows'];assert len(rows)=={2022:687,2020:693}[year]
  for r in rows:
   n=native[r['key']];cols=['bengs_dem','lesnar_lib','thune_rep']if year==2022 else['rounds_rep','ahlers_dem'];assert [int(r[k])for k in cols]==n['candidate_values']and r['native_label']==n['label']and r['county']==n['county']
 checks['complete_native_contract']=dict(primary_native=691,priority=304,remainder=387,all_parents=66,priority_parents=39,source_votes=428728,top15=61003,prefix303=342947,prefix304=343402,source_integer_target=342983,separate_signed_integer_target=343138,signed_membership_robustness_proven=False,original_public_historical_native=dict(year2022=687,year2020=693),separate_signed2022_PDF_scope=dict(native=679,parents=65,missing='Yankton'),all_source_scoped_unavailable_objects_preserved=True)
 # Reconstruct inputs from signed county/raw native votes and declared volumes.
 states=load(B/'state-targets.json');settings={r['scenario']:r for r in load(B/'scenario-settings.json')};rows=csvrows(B/'unit-targets.csv.gz');selected=csvrows(B/'selected-unit-break-even.csv.gz');groups=defaultdict(list);sg={}
 for r in rows:groups[r['scenario'],r['target']].append(r)
 for r in selected:sg[r['scenario'],r['target'],r['unit_key']]=r
 totals={y:sum(v['total']for(y2,c),v in signed.items()if y2==y)for y in [2024,2022,2020]};maxerr=0.;maxshift=0.;formulas=0
 for s in states:
  rr=groups[s['scenario'],s['target']];setting=settings[s['scenario']];year=s['preference_year'];geo=s['geography'];level=s['historical_volume_level'];assert len(rr)==setting['units']and len({r['unit_key']for r in rr})==len(rr);iscounty=geo=='all66_counties';volyear={'low':2022,'base':2020,'high':2024}.get(level);inputs=[];allvol=[]
  for r in rr:
   if iscounty:
    a=signed[year,r['county']];volume=signed[volyear,r['county']]['total'];v=volume*(a['A']+a['B'])/a['total'];q=a['A']/(a['A']+a['B'])
   else:
    # Producer calculator keys omit 'public-' in the same original workbook
    # position key; this is an exact source-position representation conversion.
    sourcekey=r['unit_key'].replace(':sheet',':public-sheet')if year in [2022,2020]else r['unit_key'];a=native[sourcekey];assert a['year']==year and a['county']==r['county']and a['label']==r['native_label'];den=sum(v['total']for v in native.values()if v['year']==year);scale=1 if level=='observed'else totals[volyear]/den;volume=a['total']*scale;v=(a['A']+a['B'])*scale;q=a['A']/(a['A']+a['B'])if a['A']+a['B']else.5
   close(float(r['pair_volume']),v);close(float(r['all_candidate_volume']),volume)
   if v:close(float(r['baseline_a_share']),q,1e-12)
   else:assert r['baseline_a_share']==''
   inputs.append((v,q));allvol.append(volume)
  V=sum(v for v,q in inputs);F=sum(allvol);M=sum(v*(2*q-1)for v,q in inputs);margin=0 if s['target']=='tie'else.01;delta=root(inputs,margin);close(s['pair_total'],V);close(s['baseline_net'],M);close(s['bounded_shift'],delta,1e-12);maxshift=max(maxshift,abs(s['bounded_shift']-delta));net=0.
  for r,(v,q),volume in zip(rr,inputs,allvol):
   qs=clip(q+delta);n=v*(2*qs-1);net+=n
   if v:close(float(r['target_a_share']),qs,1e-12)
   else:assert r['target_a_share']==''
   close(float(r['target_net']),n);close(float(r['baseline_net']),v*(2*q-1));close(float(r['net_gain']),n-v*(2*q-1));close(float(r['pair_weight']),v/V,1e-12);close(float(r['all_candidate_weight']),volume/F,1e-12);close(float(r['net_gain_per_one_share_pp']),.02*v)
   sr=sg[s['scenario'],s['target'],r['unit_key']];other=M-v*(2*q-1)
   if v:
    needed=(margin*V-other+v)/(2*v);close(float(sr['required_share']),needed);close(float(sr['other_fixed_net']),other);close(float(sr['selected_pair_volume']),v)
   else:assert sr['status']=='no_positive_pool'and sr['required_share']==''
   formulas+=12
  close(net,margin*V);close(s['target_all_candidate_margin_pp'],100*margin*V/F);close(sum(s['historical_final_candidate_votes'].values()),F);close(sum(s['current_named_pair_candidate_votes'].values()),V);maxerr=max(maxerr,abs(net-margin*V))
 checks['independent_targets']=dict(state_groups=len(states),settings=len(settings),unit_rows=len(rows),selected_rows=len(selected),formula_checks=formulas,solver='Own saturation-breakpoint integration; inputs independently reconstructed from original signed county and public native source votes, no worker imports/bisection',maximum_shift_fraction_error=maxshift,maximum_net_vote_error=maxerr,nonpriority_included=True)
 # Independent live final-denominator and selected-other-net equations.
 live=load(B/'live-synthetic-scenarios.json');liveformulas=0
 for case in live:
  x=case['input'];out=case['result'];counted=x['counted'];A=x['a'];Bname=x['b'];units=x['remaining']
  assert out.get('probability')is None
  if any(v<0 for v in counted.values()):assert out['status']=='invalid_negative_or_nonfinite_counted';continue
  if any(u['remaining_total']is None for u in units):assert out['status']=='unknown_remaining_pool';continue
  if any(u['remaining_total']<0 for u in units):assert out['status']=='invalid_negative_or_nonfinite_remaining';continue
  if any(u['a_pair_share']is None and sum(u.get('other_shares',{}).values())<1 and u['remaining_total']>0 for u in units):assert out['status']=='unknown_remaining_preference';continue
  final=dict(counted);U=0.;contrib={}
  for u in units:
   p=u['remaining_total']*(1-sum(u.get('other_shares',{}).values()));U+=p;q=clip(u['a_pair_share']or 0);ga=p*q;gb=p*(1-q);final[A]+=ga;final[Bname]+=gb;contrib[u['key']]=(p,ga-gb)
   for name,share in u.get('other_shares',{}).items():final[name]+=u['remaining_total']*share
  assert final==out['final_candidate_votes']and out['counted_fixed']==counted;FP=counted[A]+counted[Bname]+U;FA=sum(final.values());close(out['final_pair_denominator'],FP);close(out['final_all_candidate_denominator'],FA)
  if U:close(out['required_remaining_a_pair_share'],(x['target_pair_margin']*FP-counted[A]+counted[Bname]+U)/(2*U))
  if case['selected_result']:
   z=case['selected_result'];v,own=contrib[z['selected_key']];other=sum(net for key,(p,net)in contrib.items()if key!=z['selected_key'])
   if v:close(z['required_share'],(x['target_pair_margin']*FP-counted[A]+counted[Bname]-other+v)/(2*v))
   else:assert z['status']=='no_positive_pool'
  liveformulas+=1
 checks['independent_live']=dict(cases=len(live),non_unknown_numeric_cases=liveformulas,counted_fixed=True,final_denominators_and_selected_elsewhere_net_verified=True,probability=False)
 checks['qualified_gaps']=dict(public2024_signed_gap194_unallocated=True,public2020_signed_gap41_unallocated=True,public2022_all66_exact=True,PDF2022_Yankton_native_unavailable=True,registration_stock_scope_differences_2022_plus4_2020_minus11=True,current_ballot_download_limit=True,current_IDs_geography_cadence_remainder_probability_approved=False)
 out=dict(status='pass_frozen_first_pair_public_historical_scope_only',checks=checks,frozen_contract=pin(T/'priority-set.json'),frozen_owned_entries=[pin(S/p)for p in sorted(owned)],formal_dispatch_acceptance=False,qualification='Original/native ranks, signed county controls, raw references and declared scenarios checked independently. Public source priority is not a certified native minimum or geometry/candidate/live approval. All source discrepancies remain unallocated. Final writer-intercept turnout and baseline read-only producer validations are separate checks.')
 p=D/'coordinator-finished-first-pair-review.json';freeze(p,(json.dumps(out,indent=2)+'\n').encode());print(json.dumps(pin(p)))
if __name__=='__main__':main()
