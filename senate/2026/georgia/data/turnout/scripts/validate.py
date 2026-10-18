#!/usr/bin/env python3
"""Offline source-position, coverage, arithmetic, integrity, link and peer QA."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import csv,gzip,hashlib,json,re,urllib.parse
R=Path(__file__).resolve().parents[1];GA=R.parent.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def rows(p):
 with (gzip.open(p,'rt')if p.suffix=='.gz'else p.open())as f:return list(csv.DictReader(f))
meta={json.loads(p.read_text())['id']:json.loads(p.read_text())for p in (R/'source').glob('*.http.json')}
refs=json.loads((R/'source/shared-references.json').read_text());chain=json.loads((R/'source/source-chain-references.json').read_text());refmap={r['id']:r for r in chain};sources={};rawcheck=[]
for k,m in meta.items():
 if 'error'in m:continue
 p=R/m['asset'];b=p.read_bytes();raw=gzip.decompress(b)
 assert len(b)==m['stored_bytes']and len(raw)==m['entity_bytes']and sha(b)==m['stored_sha256']and sha(raw)==m['raw_sha256']
 sources[k]=p;rawcheck.append({'id':k,'status':m['status'],'raw_sha256':m['raw_sha256'],'stored_sha256':m['stored_sha256'],'bytes':m['stored_bytes']})
for m in chain:
 p=GA/m['path'];b=p.read_bytes();raw=gzip.decompress(b)
 assert sha(b)==m['stored_sha256']and sha(raw)==m['raw_sha256']and len(raw)==m['bytes']and len(b)==m['stored_bytes']and len(raw)==m['entity_bytes']
 sources['shared:'+m['id']]=p
for m in refs:assert sources['shared:'+m['id']]==GA/m['path']
@lru_cache(maxsize=16)
def rawjson(k):return json.loads(gzip.decompress(sources[k].read_bytes()))
def ptr(k,p):
 x=rawjson(k)
 for v in p.strip('/').split('/'):
  v=v.replace('~1','/').replace('~0','~');x=x[int(v)]if isinstance(x,list)else x[v]
 return x
vs=rows(R/'candidate-votes.csv.gz');ms=rows(R/'candidate-method-votes.csv.gz');nr=rows(R/'native-units.csv');cc=rows(R/'county-controls.csv');cr=rows(GA/'data/county-turnout.csv');recon=rows(R/'reconciliation.csv')
assert len(vs)==15280 and len(ms)==61120 and len(nr)==2701 and len(cc)==795 and len(cr)==159
assert len({(r['source_id'],r['source_pointer'])for r in vs})==len(vs)
assert len({(r['source_id'],r['method_pointer'])for r in ms})==len(ms)
source_cells=0
for r in vs:
 o=ptr(r['source_id'],r['source_pointer']);assert r['votes']==(''if o['voteCount']is None else str(o['voteCount']));assert r['votes_json_type']==type(o['voteCount']).__name__;assert r['option_id']==o['id'];assert r['candidate_native_id']==(''if o.get('nativeId')is None else str(o['nativeId']));assert json.loads(r['localized_candidate_name_json'])==o['name'];source_cells+=5
 assert r['option_position']==r['source_pointer'].split('/')[-1]
 party=o.get('party')or{}
 for f,k in [('party_abbreviation','abbreviation'),('party_id','id')]:assert r[f]==(''if party.get(k)is None else party[k]);source_cells+=1
 for f,k in [('is_write_in','isWriteIn'),('is_qualified_write_in','isQualifiedWriteIn')]:assert r[f]==(''if o.get(k)is None else str(o[k]));source_cells+=1
for r in ms:
 g=ptr(r['source_id'],r['method_pointer']);assert r['method_id']==g['groupId'];assert r['method_votes']==(''if g['voteCount']is None else str(g['voteCount']));assert r['method_votes_json_type']==type(g['voteCount']).__name__;assert r['method_position']==r['method_pointer'].split('/')[-1];source_cells+=4
assert sum(r['votes']==''for r in vs if r['unit_level']=='precinct')==40
assert sum(r['method_votes']==''for r in ms if r['unit_level']=='precinct')==22416
assert all(not r['under_votes_source']and not r['over_votes_source']and not r['blank_votes_source']for r in nr+cc)
assert all(r['is_virtual_raw']=='False'for r in nr)
assert sum(int(r['polling_place_row_count'])for r in cc)==0
assert len({(r['election_key'],r['county_fips'],r['native_id'])for r in nr})==2701
for r in nr:
 d=rawjson(r['source_id']);b=ptr(r['source_id'],r['source_pointer']);p=d['precincts'][int(r['inventory_source_position'])];t=ptr(r['source_id'],r['turnout_pointer'])
 assert b['precinct']==p and p['id']==r['native_id']and t['id']==p['id'];assert r['native_source_position']==r['source_pointer'].split('/')[-1];assert Fraction(r['source_all_option_votes'])==b['voteTotal'];assert Fraction(r['ballots_cast_source'])==t['ballotsCast'];assert Fraction(r['voter_registration_source'])==t['voterRegistration'];source_cells+=7
EIDS=['2024NovGen','2020NovGen','2021JanFedRun','2022NovGen','2022DecGenRun'];fipsraw=gzip.decompress((R/'source/county-fips-2020.body.gz').read_bytes()).decode();fips={r['STATEFP']+r['COUNTYFP']:r['COUNTYNAME']for r in csv.DictReader(fipsraw.splitlines(),delimiter='|')if r['STATE']=='GA'};assert len(fips)==159
for eid in EIDS:
 rs=[r for r in cc if r['election_key']==eid];assert len(rs)==159 and {r['county_fips']for r in rs}==set(fips)
 for r in rs:assert r['county_name']==fips[r['county_fips']]
 if eid!='2024NovGen':assert all(r['native_row_count']=='0'and not r['ballots_cast_usable']and not r['registration_total_usable']and Fraction(r['ballots_cast_raw'])==0 and Fraction(r['registration_total_raw'])==0 for r in rs)
rs24=[r for r in cc if r['election_key']=='2024NovGen'];assert sum(int(r['state_summary_option_votes'])for r in rs24)==5250047;assert sum(int(r['county_source_all_option_votes'])for r in rs24)==5250066
assert sum(int(r['ballots_cast_usable'])for r in rs24)==5297264;assert sum(int(r['registration_total_usable'])for r in rs24)==7219868
for r in rs24:
 ns=[n for n in nr if n['county_fips']==r['county_fips']];assert len(ns)==int(r['native_row_count']);assert sum(int(n['source_all_option_votes'])for n in ns)==int(r['county_source_all_option_votes']);assert sum(Fraction(n['ballots_cast_source'])for n in ns)==int(r['ballots_cast_usable']);assert sum(Fraction(n['voter_registration_source'])for n in ns)==int(r['registration_total_usable'])
controls=json.loads((R/'state-controls.json').read_text());rank=json.loads((R/'rankings.json').read_text());sens=json.loads((R/'sensitivity.json').read_text());rankchecks={}
for eid,v in rank.items():
 rs=sorted((r for r in cc if r['election_key']==eid),key=lambda r:(-int(r['state_summary_option_votes']),r['county_fips']));order=['GA:county:'+r['county_fips']for r in rs];assert order==v['ordered_keys'];den=sum(int(r['state_summary_option_votes'])for r in rs);assert den==v['denominator'];assert sum(Fraction(int(r['state_summary_option_votes']),den)for r in rs)==1
 cum=0;cross=None
 for i,r in enumerate(rs,1):
  cum+=int(r['state_summary_option_votes']);assert cum==v['all_order'][i-1]['cumulative_votes']
  if cross is None and 5*cum>=4*den:cross=i;cv=cum;pv=cum-int(r['state_summary_option_votes'])
 assert cross==v['minimum_count']and cv==v['priority_votes']and pv==v['preceding_votes'];assert 5*pv<4*den<=5*cv;assert sum(int(r['state_summary_option_votes'])for r in rs[:15])==v['top15_votes'];assert sum(int(r['state_summary_option_votes'])for r in rs[cross:])==v['remainder_votes'];rankchecks[eid]={'counties':159,'denominator':den,'exact_integer_crossing':True,'minimum':cross,'weights_sum':'1'}
for v in sens.values():assert 5*v['preceding_votes']<4*v['denominator']<=5*v['priority_votes']and len(v['all_order'])==159 and len(set(v['ordered_keys']))==159
nc=rows(R/'native-candidate-controls.csv');nm=rows(R/'native-method-controls.csv');assert len(nc)==638 and len(nm)==2552
assert sum(int(r['native_null_cells'])for r in nc)==40;assert sum(int(r['native_null_cells'])for r in nm)==22416
assert sum(int(r['native_known_sum'])for r in nc)==5250048;assert sum(int(r['county_minus_known_sum'])for r in nc)==18
assert sum(int(r['native_observed_method_sum'])for r in nm)==2307296;assert sum(int(r['county_minus_known_sum'])for r in nm)==2942770
assert len({r['county_fips']for r in nm if int(r['native_null_cells'])})==130
crosswalk=rows(R/'candidate-crosswalk.csv');assert sum(r['state_native_id']!=r['county_native_id']or r['state_party']!=r['county_party']for r in crosswalk)==18
# Independent federal primary whole-state control, preserving exact page/row positions.
fec=json.loads((R/'source/fec-georgia-observation.json').read_text());fm=refmap['fec-2024-presidential-original'];assert fec['raw_sha256']==fm['raw_sha256']=='c99a431e08cb779002ebecb373cee54745c3b691df2f0b322f36688364f6d823'
pages=(R/'source/fec-2024-presidential.txt').read_text().split('\f')
for page,vals in [(2,[37,30]),(3,[2548017]),(4,[20684,730,18229]),(5,[2663117]),(6,[61,5250905])]:
 line=next(x for x in pages[page-1].splitlines()if re.match(r'^GA\s',x));nums=[int(x.replace(',',''))for x in re.findall(r'\d[\d,]*',line)];assert nums==vals,(page,line,nums)
assert 37+30+730+61==858 and 5250047+858==5250905
lib=json.loads((R/'source/liberty-bound-observation.json').read_text());assert lib['source_raw_sha256']==meta['liberty-2024-summary-image-1']['raw_sha256'];assert len(lib['shown_writeins'])==8 and sum(x['votes']for x in lib['shown_writeins'])==1;assert sum(x['votes']==0 for x in lib['shown_writeins'])==7;assert lib['not_shown'][0]['votes']is None;assert lib['reported_total_votes']==23028+121+1==23150;assert 23258-23150==108
b=json.loads((R/'writein-bounds.json').read_text());assert b['threshold_ceiling']==4200724;assert 4199292+858==4200150<4200724<=4222572;assert 23258<23280 and 22353+858==23211<23280;assert 81514-80491==1023>858
contract=json.loads((R/'priority-set.json').read_text());assert contract['coordinator_accepted']is False;assert contract['full_candidate_priority_order']is None and contract['full_candidate_priority_keys']is None;assert contract['ordered_priority_keys']==rank['2024NovGen']['priority_keys'];assert contract['conditional_full_candidate_minimum_set_unordered_keys']==rank['2024NovGen']['priority_keys'];assert len(contract['coverage'])==159
nativekeys={r['native_key']for r in nr};cs=[x for c in contract['coverage']for x in c['constituents']];assert len(cs)==2701 and {x['key']for x in cs}==nativekeys;assert all(len(c['administrative_cases'])==5 for c in contract['coverage']);assert contract['complete_ordered_keys']==rank['2024NovGen']['ordered_keys']
freeze=json.loads((R/'contract-freeze.json').read_text());assert sha((R/'priority-set.json').read_bytes())==freeze['sha256']and (R/'priority-set.json').stat().st_size==freeze['bytes'];assert contract['coordinator_formal_acceptance_reference']=='data/coordinator-priority-acceptance.json'
acceptance_path=GA/contract['coordinator_formal_acceptance_reference'];acceptance=json.loads(acceptance_path.read_text())if acceptance_path.exists()else None
if acceptance is not None:assert freeze['sha256']in json.dumps(acceptance), 'External review must identify the exact frozen contract'
peer_side_path=GA/'data/baselines/peer-reconciliation.json';peer_side=json.loads(peer_side_path.read_text());assert peer_side['status'].startswith('pass')and not peer_side['disagreements']
for fn,v in peer_side['peer_artifact_pins'].items():assert sha((R/fn).read_bytes())==v['sha256']and (R/fn).stat().st_size==v['bytes']
peer=json.loads((R/'peer-agreement.json').read_text());assert peer['status']=='pass'and not peer['differences']and peer['source_position_candidate_method_rows_compared']==76400
for m in peer['peer_inputs'].values():assert sha((GA/m['path']).read_bytes())==m['sha256']
support=json.loads((R/'source/supporting-references.json').read_text())
for v in support:assert sha((GA/v['path']).read_bytes())==v['sha256']and (GA/v['path']).stat().st_size==v['bytes']
clerk=(GA/support[1]['path']).read_text().split('GEORGIA',1)[1].split('FOR UNITED STATES REPRESENTATIVE',1)[0]
for label,count in [('Republican',2663117),('Democratic',2548017),('Libertarian',20684),('Green',18229)]:
 match=re.search(label+r'\s*\.+\s*([\d,]+)',clerk);assert match and int(match[1].replace(',',''))==count
proof=GA/'data/coordinator-priority-membership-review.json';assert proof.exists();assert json.loads(proof.read_text())['status']=='pass_exact44_membership_without_imputed_allocation';coordinator_proof={'path':'data/coordinator-priority-membership-review.json','sha256':sha(proof.read_bytes()),'scope':'independent membership proof only; no coordinator formal acceptance inferred'}
# Discovery routes were observed in retained scripts, not guessed.
service=gzip.decompress(sources['shared:sos-results-service-chunk-js'].read_bytes()).decode();main=gzip.decompress(sources['shared:sos-results-main-js'].read_bytes()).decode();assert '${this.baseUrl}/elections/${t}/${r}/data'in service and '/ballot-item/${o}'in service and 'endpoint:"/results/public/api"'in main
req=json.loads((R/'source/requests-counties.json').read_text());assert len(req)==795 and len({r['url']for r in req})==795;assert all(meta[r['id']]['status']==200 and meta[r['id']]['url']==r['url']for r in req)
full24=rawjson('shared:sos-2024-general-api-data');offices=[next(t['text']for t in r['name']if t['languageId']=='en')for r in full24['ballotItems']];assert not any(re.search(r'US Senate|Governor',n,re.I)for n in offices)
# All relative markdown links in owned report/docs resolve; anchors are not source substitutions.
linkchecks=[]
for p in [GA/'turnout.md',*R.rglob('*.md')]:
 for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',p.read_text()):
  u=target.split('#',1)[0]
  if not u or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',u):continue
  dest=(p.parent/urllib.parse.unquote(u.strip('<>'))).resolve();assert dest.exists()or dest in {(R/'validation.json').resolve(),(R/'asset-manifest.json').resolve()},(str(p),u);assert GA.parent in dest.parents or dest==GA.parent;linkchecks.append({'from':str(p.relative_to(GA)),'target':u})
owned=[GA/'turnout.md',GA/'data/county-turnout.csv',*sorted(p for p in R.rglob('*')if p.is_file()and p.name!='asset-manifest.json')];assert all(p.stat().st_size<40000000 for p in owned);assert not any(p.name in ['__pycache__','node_modules','.venv']for p in R.rglob('*'))
result={'status':'pass_with_explicit_material_gaps','source_original_hash_checks':len(rawcheck),'shared_original_hash_checks':len(chain),'source_position_field_checks':source_cells,'all_county_rows':795,'all_2024_native_identities':2701,'source_option_rows':len(vs),'source_method_rows':len(ms),'native_null_candidate_cells':40,'native_null_method_cells':22416,'native_known_option_sum':5250048,'native_unallocated_option_residual':18,'native_known_method_sum':2307296,'native_unallocated_method_residual':2942770,'whole_state_candidate_and_method_balances':'pass; all five reported source scopes','full2024_candidate_universe':{'named_four':5250047,'qualified_writeins':858,'total':5250905,'FEC_original_hash':fec['raw_sha256']},'rank_checks':rankchecks,'minimum44_membership':'proven from complete full-state pool and compatible Liberty ballot ceiling; no county write-in allocation invented','full_candidate_exact_order_shares':'unavailable; bounds retained','top15_membership':'proven1023gap>858','coordinator_membership_proof':coordinator_proof,'coordinator_formal_acceptance':'external decision at path-only reference'if acceptance is not None else False,'coordinator_formal_acceptance_reference':contract['coordinator_formal_acceptance_reference'],'external_acceptance_status':acceptance.get('status')if acceptance is not None else'unavailable; pending','worker_contract_coordinator_accepted_flag':False,'frozen_contract_sha256':freeze['sha256'],'independent_peer_checks':peer_side['check_count'],'independent_peer_reconciliation_path':'data/baselines/peer-reconciliation.json','peer_comparison':'pass; all76400rows/all795county/all2701native/all5orders and native residual controls','peer_inputs':peer['peer_inputs'],'relative_links_checked':len(linkchecks),'max_object_bytes':max(p.stat().st_size for p in owned),'all_objects_strictly_below_40000000':True,'material_gaps':['Most qualified write-in county/method allocations; exact full-candidate county order/top15/44shares unavailable.','Original SOS qualified-write-in certification/list bytes blocked; FEC original corroborates complete statewide universe.','Earlier four elections have no native rows/usable ballots/registration in recovered app; original ZIP routes403.','2024 native candidate/method redactions remain null and unallocated.','Native physical/combined/style/central semantics and approved2026boundaries/crosswalks unverified.','Formal coordinator acceptance is external and not claimed.']}
if acceptance is not None:result['material_gaps'].remove('Formal coordinator acceptance is external and not claimed.')
(R/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
owned=[GA/'turnout.md',GA/'data/county-turnout.csv',*sorted(p for p in R.rglob('*')if p.is_file()and p.name!='asset-manifest.json')]
assets=[{'path':str(p.relative_to(GA)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}for p in owned]
manifest={'scope':'All owned turnout report/data assets; manifest itself excluded to avoid self-reference. Source originals use lossless gzip; relative paths from Georgia directory.','owned_assets':assets,'external_read_only_sources':chain,'external_supporting_references':support,'external_coordinator_proof':coordinator_proof,'external_coordinator_acceptance_reference_path':contract['coordinator_formal_acceptance_reference'],'external_acceptance_status':acceptance.get('status')if acceptance is not None else'pending; no worker assertion','acceptance_reference_policy':'Path only; no acceptance hash or reverse pin.','peer_inputs':peer['peer_inputs'],'largest_owned_asset_bytes':max(a['bytes']for a in assets),'all_strictly_below_40000000':all(a['bytes']<40000000 for a in assets)}
(R/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');assert (R/'asset-manifest.json').stat().st_size<40000000
for x in linkchecks:assert (GA/x['from']).parent.joinpath(urllib.parse.unquote(x['target'])).resolve().exists()
print(json.dumps({k:v for k,v in result.items()if k not in ['peer_inputs','rank_checks']},indent=2))
