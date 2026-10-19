#!/usr/bin/env python3
"""Meaningful offline whole-state QA. No network, peer writes or Git operations.
Writes validation first, then manifest pins it; manifest excludes its own self-hash.
"""
import collections,csv,datetime,gzip,hashlib,io,json,re,sys,zipfile
from fractions import Fraction
from pathlib import Path
import xml.etree.ElementTree as E
sys.dont_write_bytecode=True
from extract import shared,own
D=Path(__file__).resolve().parent;STATE=D.parent.parent;DATA=D.parent
checks=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def check(label,condition,detail=None):
 checks.append({'check':label,'pass':bool(condition),**({'detail':detail}if detail is not None else{})})
 if not condition:raise AssertionError(label+': '+str(detail))
def read(p):return list(csv.DictReader(p.open()))
def j(p):return json.loads(p.read_text())
def pin(p):return {'path':str(p.relative_to(STATE)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
def main():
 c=j(D/'priority-set.json');r=read(D/'native-2024.csv');compat=read(DATA/'county-turnout.csv');ctrl=j(D/'certified-controls.json');fp=j(D/'county-fips.json')['counties'];parents=j(D/'native-2024-parent-reconciliation.json')
 check('FIPS66 unique realSD46codes inclOglala46102',len(fp)==66 and len(set(fp.values()))==66 and all(v.startswith('46')and len(v)==5 for v in fp.values())and fp['Oglala Lakota']=='46102')
 check('primarynative691unique leaves all66parents',len(r)==691 and len({v['key']for v in r})==691 and len({v['county_fips']for v in r})==66)
 check('CSVcompatibility retains every native field/row/order',len(compat)==691 and all(all(v[k]==q[k]for k in v)for v,q in zip(r,compat)))
 check('strictnumeric native descending sort',r==sorted(r,key=lambda v:(-int(v['contest_votes']),v['county_fips'],int(v['sheet_ordinal']),int(v['source_row']))))
 totals=[sum(int(v[k])for v in r)for k in ['harris_dem','oliver_lib','trump_rep','kennedy_ind']]
 check('allfourcandidate nativecontrols',totals==[146811,2777,271938,7202],totals)
 check('all691candidate sums',all(int(v['contest_votes'])==sum(int(v[k])for k in ['harris_dem','oliver_lib','trump_rep','kennedy_ind'])for v in r))
 total=sum(int(v['contest_votes'])for v in r);check('exactweights totalone',sum((Fraction(int(v['contest_votes']),total)for v in r),Fraction())==1)
 check('candidatevotes distinctnullable ballotregblankunderOverWritein fields',all(v[k]==''for v in r for k in ['ballots_cast','registered_voters','blank_ballots','undervotes','overvotes','generic_writein_votes','valid_named_writein_votes','official_native_numeric_id']))
 cumulative=0
 for i,v in enumerate(r,1):
  cumulative+=int(v['contest_votes']);check(f'native rank/cumulative{ i}',int(v['rank'])==i and int(v['cumulative_votes'])==cumulative)
 check('completecontract nativeorder',c['complete_ordered_keys']==[v['key']for v in r]and [v['key']for v in c['all_units']]==c['complete_ordered_keys'])
 check('contract primarycandidate and nativeconstituent addresses all691',all(v['contest_votes']==int(q['contest_votes'])and v['candidate_votes']=={k:int(q[k])for k in ['harris_dem','oliver_lib','trump_rep','kennedy_ind']}and v['source_native_constituents'][0]['row']==int(q['source_row'])and v['source_native_constituents'][0]['candidate_cell_addresses']==q['source_cells'].split(',')for v,q in zip(c['all_units'],r)))
 check('top15exact sourcefraction',c['top15']['votes']==sum(int(v['contest_votes'])for v in r[:15])==61003 and c['top15']['denominator']==428728)
 m=c['minimum80'];check('exactminimal integer80crossing',m['count']==304 and m['votes']==343402 and m['preceding_votes']==342947 and 5*m['preceding_votes']<4*total<=5*m['votes']and m['integer_threshold_ceiling']==342983)
 check('crossing Hamlin literal455 exactsourcekey',r[303]['native_label']=='Precinct-26'and r[303]['county']=='Hamlin'and int(r[303]['contest_votes'])==455 and m['crossing_key']=='sd:2024:pres:46057:sheet32:row14')
 check('priorityall304 and remainderall387 disjointexhaustive',c['ordered_priority_keys']==c['complete_ordered_keys'][:304]and c['remainder']['ordered_keys']==c['complete_ordered_keys'][304:]and c['remainder']['votes']==85326 and c['remainder']['count']==387)
 check('all66 ancestors disjointparentchildren;39priorityparents',len(c['county_parents'])==66 and len({p['parent_key']for p in c['county_parents']})==66 and sorted(k for p in c['county_parents']for k in p['ordered_all_native_keys'])==sorted(c['complete_ordered_keys'])and c['priority_parent_count']==39)
 for p in parents:
  rr=[v for v in r if v['county']==p['county']];check('2024nativefooter '+p['county'],len(rr)==p['source_native_rows'] and [sum(int(v[k])for v in rr)for k in ['harris_dem','oliver_lib','trump_rep','kennedy_ind']]==p['candidate_footer'])
 check('native-certified24county194gap unallocated',sum(any(p['unofficial_minus_certified'])for p in parents)==24 and [sum(p['unofficial_minus_certified'][k]for p in parents)for k in range(4)]==[-48,-1,-143,-2])
 check('certifiedrobustness explicitlyunproved',c['certification_robustness']['proven']is False and c['certification_robustness']['signed_integer80_target']==343138 and c['certification_robustness']['source303_short_of_signed_target']==191)
 for y,expected in [('2024',[146859,2778,272081,7204]),('2022',[91007,14697,242316]),('2020',[276232,143987])]:
  t=ctrl[y];check(y+'signed66countywholecandidateclosure',len(t['counties'])==66 and [sum(v['candidate_votes'][i]for v in t['counties'].values())for i in range(len(expected))]==t['candidate_controls']==expected)
  check(y+'signedcandidate sourcepositions bounds',all(1<=v['source_pdf_page']<=50 and v['source_page_line_1based']>=1 and v['literal_line'].strip().startswith(n)for n,v in t['counties'].items()))
 # Validate primary CSV directly against original source ZIP, independent of retained OOXML derivative.
 raw,a=shared(c['source_id']);z=zipfile.ZipFile(io.BytesIO(raw));check('primary originalZIPCRC',z.testzip()is None);ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 strings=[''.join(v.itertext())for v in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)];decoded={}
 for v in r:
  member=v['sheet_member']
  if member not in decoded:
   decoded[member]={row.get('r'):{cell.get('r'):cell for cell in row.findall('m:c',ns)}for row in E.fromstring(z.read(member)).findall('m:sheetData/m:row',ns)}
  cells=decoded[member][v['source_row']];row=int(v['source_row']);label=cells['B'+str(row)];check('originalnativecell '+v['key'],strings[int(label.find('m:v',ns).text)]==v['native_label'] and all(cells[col+str(row)].get('t')=='n'and int(cells[col+str(row)].find('m:v',ns).text)==int(v[field])for col,field in zip('CDEF',['harris_dem','oliver_lib','trump_rep','kennedy_ind'])))
 headings=j(D/'candidate-header-presentation.json');check('publishercontradictoryheaders preserved not repaired',any(not h['headers_agree']and h['literal_header_cells']['D']=='Donald J. Trump and JD Vance 'and h['literal_header_cells']['E']=='Donald J. Trump and JD Vance 1'for h in headings)and any(h['headers_agree']for h in headings))
 hist=j(D/'historical-public-native-reconciliation.json')
 for y,n,fields,expected in [('2022',687,['bengs_dem','lesnar_lib','thune_rep'],[91007,14697,242316]),('2020',693,['rounds_rep','ahlers_dem'],[276208,143970])]:
  rr=read(D/f'native-{y}-public.csv');h=hist[y];check(y+'completepublicnativeuniverse',len(rr)==n and len({v['key']for v in rr})==n and len({v['county_fips']for v in rr})==66 and [sum(int(v[k])for v in rr)for k in fields]==expected)
  check(y+'publicnative all66footers closed',len(h['county_reconciliation'])==66 and all([sum(int(v[k])for v in rr if v['county']==p['county'])for k in fields]==p['candidate_footer']for p in h['county_reconciliation']))
 check('2022publicallsignedcountycontrolsexact',all(not any(p['public_minus_certified'])for p in hist['2022']['county_reconciliation']))
 check('2020public41gap21countiesexplicit',sum(any(p['public_minus_certified'])for p in hist['2020']['county_reconciliation'])==21 and [sum(p['public_minus_certified'][i]for p in hist['2020']['county_reconciliation'])for i in range(2)]==[-24,-17])
 nr=read(D/'native-2022.csv');nb=j(D/'native-2022-reconciliation.json');check('2022PDF679rows65countiesmissingYankton',len(nr)==679 and len({v['county']for v in nr})==65 and nb['missing_native_counties']==['Yankton']and nb['missing_native_candidate_controls']['Yankton']==[2462,340,6051])
 check('2022PDF wholecandidateknownplusmissing balances',[sum(int(v[k])for v in nr)+nb['missing_native_candidate_controls']['Yankton'][i]for i,k in enumerate(['bengs_dem','lesnar_lib','thune_rep'])]==[91007,14697,242316])
 books=j(D/'turnout-registration-controls.json');sensitivity=j(D/'sensitivities.json')
 for y in ['2024','2022','2020']:
  tt=books['turnout'][y];rt=books['registration_table'][y];check(y+'all66ballot+turnoutregistrationtable sums',len(tt)==67 and sum(v['votes_cast_source_label']for n,v in tt.items()if n!='TOTAL')==tt['TOTAL']['votes_cast_source_label'] and sum(v['registered_voters_turnout_table']for n,v in tt.items()if n!='TOTAL')==tt['TOTAL']['registered_voters_turnout_table'])
  check(y+'all66active+inactive stocktable sums',len(rt)==67 and sum(v['total_active']for n,v in rt.items()if n!='Total')==rt['Total']['total_active'] and sum(v['inactive']for n,v in rt.items()if n!='Total')==rt['Total']['inactive'])
  for field,s in sensitivity[y].items():
   check(y+'sensitivity fullorder and mininteger80 '+field,len(s['order'])==s['unit_count']and len({v['key']for v in s['order']})==s['unit_count']and s['order'][-1]['cumulative_votes']==s['denominator']and s['preceding_votes']*5<s['denominator']*4<=s['minimum80_votes']*5 and all(a['votes']>=b['votes']for a,b in zip(s['order'],s['order'][1:])))
 check('registrationdefinitiondiscrepancies4andminus11 preserved',books['turnout']['2022']['TOTAL']['registered_voters_turnout_table']-books['registration_table']['2022']['Total']['total_active']==4 and books['turnout']['2020']['TOTAL']['registered_voters_turnout_table']-books['registration_table']['2020']['Total']['total_active']==-11)
 for y in ['2024','2022','2020']:
  m=[v for v in j(D/'source-method-controls.json')if v['year']==y];check(y+'methodpartial+unspecified entirestate arithmetic',sum(v['contest_votes']for v in m)==(428728 if y=='2024'else sum(hist[y]['candidate_totals']))and sum(v['native_rows']for v in m)==(691 if y=='2024'else hist[y]['native_rows']))
 cs=j(D/'current-candidate-scope.json');check('current2026party/status not historicalstaticD',cs['current2026_Bengs_identity'].startswith('Independent')and len(cs['Senate_rows'])==3 and cs['current2026_Democratic_choice'].startswith('none_active')and [v['complete_source_td_cells'][13]for v in cs['Senate_rows']]==['Withdrawn','Active','Active']and [v['complete_source_td_cells'][2]for v in cs['Senate_rows']]==['DEM','IND','REP'])
 # Verify every captured entity and every reused original, including failed requests and ordered parts.
 captures=[]
 for p in sorted((D/'source').glob('*.receipt.json')):
  a=j(p)
  if 'error'in a:check('documentedtransportfailure '+p.name,'asset'not in a);continue
  z=(p.parent/a['asset']).read_bytes();raw=gzip.decompress(z);check('raw/storedcapturehash '+p.name,sha(z)==a['stored_sha256']and len(z)==a['stored_bytes']<40000000 and sha(raw)==a['raw_sha256']and len(raw)==a['raw_bytes']);captures.append({'receipt':str(p.relative_to(STATE)),'status':a['http_status'],'raw_bytes':len(raw)})
 refs=j(D/'source/source-references.json')['selected_receipts'];reuse=[]
 for a in refs:
  if 'asset'in a or 'asset_parts'in a:
   raw,_=shared(a['id']);check('sharedoriginalhash '+a['id'],sha(raw)==a['raw_sha256'])
   for o in a['stored_objects']:
    p=STATE/o['path'];check('sharedstoredobject '+o['path'],p.stat().st_size==o['bytes']<40000000 and sha(p.read_bytes())==o['sha256']);reuse.append(o)
 # Recheck retained complete workbook member hashes against exact original ZIPs.
 for p in sorted((D/'extracts').glob('*OOXML.json.gz')):
  v=json.loads(gzip.decompress(p.read_bytes()))
  if 'source_id'not in v:continue
  sid=v['source_id'];raw,_=(own(sid)if sid.startswith('public-native-senate-')else shared(sid));zz=zipfile.ZipFile(io.BytesIO(raw))
  check('completeOOXML actualoriginal memberhashes '+p.name,zz.testzip()is None and len(v['zip_members'])==len(zz.infolist())and all(sha(zz.read(m['name']))==m['sha256']and len(zz.read(m['name']))==m['bytes']and f"{zz.getinfo(m['name']).CRC:08x}"==m['crc32']for m in v['zip_members']))
 peer=j(D/'peer-agreement.json');check('independentpeerfullagreement',peer['status']=='pass'and all(v['pass']for v in peer['checks']),{'peer_id':peer['actual_peer_id'],'checks':len(peer['checks'])})
 for v in peer['pinned_inputs']:
  p=STATE/v['path'];check('peercomparisoninputstillstable '+v['path'],p.stat().st_size==v['bytes']and sha(p.read_bytes())==v['sha256'])
 # Every local Markdown destination exists and stays within project. No network check claimed.
 broken=[];links=0
 for p in [STATE/'turnout.md',D/'source/SCHEMA.md']:
  for dest in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if re.match(r'[a-z]+:',dest):continue
   q=(p.parent/dest.split('#')[0]).resolve();links+=1
   if not q.exists()and q not in [D/'validation.json',D/'asset-manifest.json']:broken.append({'document':str(p),'destination':dest})
 check('alllocalMarkdownlinks resolve or target declared finalQAoutputs',not broken,{'links':links,'broken':broken})
 report=(STATE/'turnout.md').read_text();order=report.split('## Complete 691-row native order',1)[1];lines=[l for l in order.splitlines()if re.match(r'\| \d+ \|',l)]
 check('reportcomplete691order includesallremainder',len(lines)==691 and '| 691 |'in lines[-1]and '428,728'in lines[-1]and '191 votes short'in report)
 check('noownedcachedependencydirectories',not any(p.is_dir()and p.name in ['__pycache__','node_modules','.venv']for p in D.rglob('*')))
 check('externalacceptance not selfasserted',not c['coordinator_acceptance']['accepted']and not c['certification_robustness']['proven'])
 outputs=[STATE/'turnout.md',DATA/'county-turnout.csv']+[p for p in D.rglob('*')if p.is_file()and p.name not in ['asset-manifest.json','validation.json']]
 check('everyownedobjectstrictlybelow40millionbytes',all(p.stat().st_size<40000000 for p in outputs))
 result={'status':'pass','scope':'offline original/raw/stored/native/candidate/method/ballot/registration/priority/link/bounds and read-only independent peer agreement','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'check_count':len(checks),'checks':checks,'captures':captures,'primary_source_counts':{'2024_public_native':691,'2024_county_parents':66,'2022_public_native':687,'2020_public_native':693,'2022_signedPDF_native':679,'2022_signedPDF_county_parents':65,'signed_county_vectors':198},'material_source_gaps':['2024public/signed194votes;certifiedminimum/membershiprobustnessunproved','2020public/signed41votes','2022originalprecinctPDFomitsYankton;separatepublicworkbookcomplete','nativeballots/registration/blank/under/over and methodsubsplits unavailable','noapproved2026geometryorcurrentENRIDs','Lincolnpublicationballot observedthroughweb;exactPDFnotretainedhere'],'coordinator_acceptance':False}
 (D/'validation.json').write_text(json.dumps(result,indent=2)+'\n');outputs.append(D/'validation.json')
 # Manifest has no self-hash; all other owned files, including this script and QA, pinned.
 manifest={'schema_version':1,'base':'senate/2026/south-dakota','owned_paths':[pin(p)for p in sorted(outputs)],'reused_read_only_objects':list({o['path']:o for o in reuse}.values()),'self_hash_rule':'asset-manifest.json excludes itself; every other owned file is pinned. Validation written first to avoid circular hash.','no_duplicate_large_originals':True,'stored_object_limit_exclusive':40000000}
 (D/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 for p in [STATE/'turnout.md',D/'source/SCHEMA.md']:
  for dest in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if not re.match(r'[a-z]+:',dest):assert (p.parent/dest.split('#')[0]).resolve().exists(),dest
 print(json.dumps({'status':'pass','checks':len(checks),'owned_assets':len(outputs),'largest_owned_bytes':max(p.stat().st_size for p in outputs),'peer_checks':len(peer['checks'])}))
if __name__=='__main__':main()
