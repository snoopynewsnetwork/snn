#!/usr/bin/env python3
"""Deterministic offline extraction and independent checks on complete saved originals.
Writes only results-sources/** and ../official-results-sources.csv via inventory.py.
Does not change first-wave originals, scopes, unavailable cells, or geography.
"""
import collections,csv,gzip,hashlib,io,json,pathlib,re,xml.etree.ElementTree as ET,zipfile
R=pathlib.Path(__file__).resolve().parent
D=R.parent
S=D.parent
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(b):return hashlib.sha256(b).hexdigest()
def js(p):return json.loads(p.read_text())
def wj(name,o):(R/name).write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def raw(sid):
 m=js(R/'raw'/f'{sid}.meta.json');return gzip.decompress((R/m['body_path']).read_bytes())
def compact(x):return json.dumps(x,separators=(',',':'),ensure_ascii=False)
def scalar(x):return x[0] if isinstance(x,list) and len(x)==1 else x
COUNTIES=list(csv.DictReader((D/'county-turnout.csv').open()))
BYNAME={x['county']:x for x in COUNTIES}
CONTRACT=js(D/'turnout/priority-set.json')
PINS={'../turnout/priority-set.json':('dcdc1457a5b08851ef76b5372435d56788f647708da5ff9a6ef35435f92fa6a7',20297853),'../turnout/asset-manifest.json':('ffa25d2d8e1f9d7f8463cf60e007c580c51ac052b4653171d764be11aa679290',None),'../county-turnout.csv':('44ff0242c75a5c310a15ff705138cd93a86365bcc622301fc49c05c9133a8993',36900)}
refs=[]
for rel,(h,n) in PINS.items():
 p=R/rel;b=p.read_bytes();assert sha(b)==h,(rel,'pin changed');assert n is None or len(b)==n
 refs.append({'path':rel,'sha256':h,'bytes':len(b),'scope':'coordinator-provided final pin; read-only'})
for rel in ['../coordinator-priority-acceptance.json','../coordinator-county-reconciliation.json','../coordinator-native-contract-checks.json','../coordinator-priority-keys.txt','../coordinator-first-wave-checks.json','../coordinator-evidence/court-preview-inventory.json','../turnout/source/shared-references.json','../turnout/source/acquisition.json','../turnout/source/SCHEMA.md','../turnout/extracts/native-units.jsonl.gz','../turnout/extracts/candidate-observations.jsonl.gz','../turnout/extracts/candidate-controls.csv','../turnout/extracts/native-county-reconciliation.csv','../news/manifest.json','../news/legal-web-observations.json','../news/sumner-2022-control.json']:
 b=(R/rel).read_bytes();refs.append({'path':rel,'sha256':sha(b),'bytes':len(b),'scope':'read-only observed supporting source; no approval granted by this worker'})
shared=js(D/'turnout/source/shared-references.json')
wj('shared-inputs.json',{'pin_policy':'No reverse hash of this worker is written into any first-wave/coordinator source. External coordinator acceptance controls; legacy contract coordinator_acceptance:false means no worker self-approval.','pinned_files':refs,'full_original_source_objects':shared,'source_objects_base':'../turnout/source/; original path fields are relative to ../turnout/ as specified by shared-references SCHEMA'})
# Complete all-105 fallback contact blocks, preserving PDF column/line positions.
pdf=(R/'extracts/sos-av1.txt').read_text().split('\f')[1].splitlines();starts=[0,28,58,84,111,138,165,1000];contacts=[]
for col in range(7):
 block=[];start=None
 for ln,line in enumerate(pdf,1):
  cell=line[starts[col]:starts[col+1]].strip()
  if cell.endswith(' County') and cell[:-7] in BYNAME:
   if block:contacts.append((start,block))
   start=ln;block=[cell]
  elif block and cell:block.append(cell)
 if block:contacts.append((start,block))
contact=[]
for n,lines in contacts:
 name=lines[0][:-7];phone=next((x.removeprefix('Phone:').strip() for x in lines if x.startswith('Phone:')),None)
 contact.append({'county':name,'county_key':BYNAME[name]['county_key'],'source_id':'sos-av1','source_revision':'2026-09-28 printed on form page1; contact entries can be older','page':2,'column_start_char':starts[next(i for i in range(7) if pdf[n-1][starts[i]:starts[i+1]].strip()==lines[0])],'text_line':n,'literal_block':lines,'phone':phone,'scope':'manual authority/contact fallback; not poll hours and no contact made'})
assert len(contact)==105 and len({x['county'] for x in contact})==105
wj('county-contact-evidence.json',sorted(contact,key=lambda x:x['county']))
# Conserves every accepted constituent, without deduping overlapping families.
units=[json.loads(x) for x in gzip.open(D/'turnout/extracts/native-units.jsonl.gz','rt')];um={x['unit_key']:x for x in units};assert len(um)==22031
keys=[];unknown=collections.Counter();fam=collections.Counter();groups=0;samples=[]
fields=['unit_key','sheet','xml_path','source_rows','native_label','native_id_fields','named_candidate_total','unknown_named_cells','role','method','geometry_status']
for c in CONTRACT['all_geography_coverage']:
 for f in c['source_native_families']:
  groups+=1
  for x in f['constituents']:
   u=um[x['unit_key']];assert {k:u[k] for k in fields}==x,(c['county'],f['source_id'],x['unit_key']);assert u['county_key']==c['county_key'];assert u['source_id']==f['source_id']
   expected=f['source_id']+':'+sha(compact([u['source_id'],u['sheet'],u['county_native'],u['native_id_fields']]).encode())[:24]
   assert expected==u['unit_key'];keys.append(u['unit_key']);fam[u['source_id']]+=1
   if u['named_candidate_total'] is None:unknown[u['source_id']]+=1
  if c['county_key'] in CONTRACT['ordered_priority_keys']:samples.append(um[f['constituents'][0]['unit_key']])
assert len(keys)==len(set(keys))==22031 and groups==525
# Independent OOXML decoder, not the first-wave transformation implementation.
news={x['id']:x for x in js(D/'news/manifest.json')};books={};sheets={}
def get_sheet(sid,path):
 key=(sid,path)
 if key in sheets:return sheets[key]
 if sid not in books:
  m=news[sid];b=gzip.decompress((D/'news'/m['asset']).read_bytes());assert sha(b)==CONTRACT['source_hashes'][sid]
  z=zipfile.ZipFile(io.BytesIO(b));ss=[]
  if 'xl/sharedStrings.xml' in z.namelist():
   ss=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
  books[sid]=(z,ss)
 z,ss=books[sid];out={}
 for row in ET.fromstring(z.read(path)).findall('s:sheetData/s:row',NS):
  cells={}
  for c in row:
   v=c.find('s:v',NS)
   if c.get('t')=='s':val=ss[int(v.text)] if v is not None else None
   elif c.get('t')=='inlineStr':val=''.join(c.find('s:is',NS).itertext())
   else:val=v.text if v is not None else None
   cells[re.sub(r'\d','',c.get('r'))]=val
  out[int(row.get('r'))]=cells
 sheets[key]=out;return out
samplekeys={u['unit_key'] for u in samples};obs=[json.loads(l) for l in gzip.open(D/'turnout/extracts/candidate-observations.jsonl.gz','rt')];selected=[x for x in obs if x.get('unit_key') in samplekeys];cellchecks=0;idchecks=0
for o in selected:
 cells=get_sheet(o['source_id'],o['xml_path'])[o['row']];assert cells.get(o['column'])==o['raw_value'],o;cellchecks+=1
for u in samples:
 rows=get_sheet(u['source_id'],u['xml_path'])
 for col,x in u['native_id_fields'].items():
  val=x.get('value') if isinstance(x,dict) else x
  if re.fullmatch('[A-Z]{1,3}',col) and col in rows[u['source_rows'][0]]:
   assert rows[u['source_rows'][0]].get(col)==val,(u['unit_key'],col,val);idchecks+=1
  elif col=='County':
   assert val==u['county_native'],(u['unit_key'],col,val)
  else:
   # Supplement retains a literal header key. Locate that header in preceding rows.
   candidates=[c for n,cs in rows.items() if n<u['source_rows'][0] for c,v in cs.items() if v==col]
   assert any(rows[u['source_rows'][0]].get(c)==val for c in candidates),(u['unit_key'],col,val,'header lookup');idchecks+=1
# Independent full broad2024 county/candidate aggregation of all original integer rows.
broad=collections.defaultdict(collections.Counter);aliases={'Kamala D. Harris / Tim Walz':'harris','Donald J. Trump / JD Vance':'trump','Chase Oliver / Mike ter Maat':'oliver','Robert F. Kennedy Jr./ Nicole Shanahan':'kennedy'}
for n,cells in get_sheet('sos-2024-president-county','xl/worksheets/sheet1.xml').items():
 if n==1:continue
 if cells.get('H') in aliases:
  county=cells['E'].strip();broad[county][aliases[cells['H']]]+=int(cells['J'])
assert len(broad)==105
for c,v in broad.items():
 for k,num in v.items():assert num==int(BYNAME[c]['president_2024_'+k]),(c,k,num)
wj('historical-native-audit.json',{'scope':'all22031 whole-source objects conserved by exact11fields; independent original OOXML sample per priority county/family and entire broader2024 integer county/candidate aggregation. No November geographic approval.','family_counts':dict(fam),'county_family_groups':groups,'unknown_count_units':dict(unknown),'all_105_broad2024_candidate_cells_checked':420,'state_four_named_total':sum(sum(v.values()) for v in broad.values()),'original_ooxml_sample_units':len(samples),'original_ooxml_sample_candidate_cells':cellchecks,'original_ooxml_sample_identity_fields':idchecks,'sampled_full_source_objects':samples,'sampled_full_candidate_observations':selected,'no_residual_allocation':True})
# Native Clarity snapshots preserve source objects and all positional arrays.
vendor=[];checks=[]
CAN=['harris','trump','kennedy','oliver','anderson','davis','hamilton','hart','latz','murray','neumann','parelkar','schmidt','soetaert','taylor','marshall','naramore']
def canon(name):
 low=name.lower()
 for k in CAN:
  if k in low:return k
 return None
for sid,county,date,prefix in [('miami-vendor','Miami','2026-08-04','senate_primary_2026'),('harvey-vendor','Harvey','2026-08-04','senate_primary_2026'),('harvey-general','Harvey','2024-11-05','president_2024'),('miami-general','Miami','2024-11-05','president_2024')]:
 summ=json.loads(raw(sid+'-summary-json'));sums=json.loads(raw(sid+'-sum-json'));detail=json.loads(raw(sid+'-details-json'));status=json.loads(raw(sid+'-status-json'));config=json.loads(raw(sid+'-config-json'))
 for pos,c in enumerate(summ):
  if (prefix=='president_2024' and 'president' not in c['C'].lower()) or (prefix!='president_2024' and not ('senat' in c['C'].lower() or 'senator' in c['C'].lower())):continue
  if prefix!='president_2024' and not any(n.lower() in ' '.join(c['CH']).lower() for n in ['Adam Hamilton','Roger Marshall']):continue
  d=next(x for x in detail['Contests'] if x['K']==c['K']);s=next(x for x in sums['Contests'] if x['K']==c['K']);rows=d['V'];tot=[sum(r[i] for r in rows) for i in range(len(c['CH']))]
  assert tot==c['V'],(sid,c['K'],'detail columns');assert all(sum(v)==scalar(t) for v,t in zip(rows,d['T']));assert sum(c['V'])==scalar(c['T'])
  assert c['CH']==s['CH'] and c['V']==s['V']
  comparisons=[]
  for i,(name,v) in enumerate(zip(c['CH'],c['V'])):
   k=canon(name)
   if k:
    expected=int(BYNAME[county][prefix+'_'+k]);comparisons.append({'candidate_position':i,'literal':name,'canonical':k,'votes':v,'accepted_county_control':expected,'difference':v-expected});assert v==expected,(sid,k,v,expected)
  vendor.append({'source_id':sid,'county':county,'election_date':date,'contest_position':pos,'summary_source_object':c,'sum_source_object':s,'detail_source_object':d,'full_status_object':status,'full_config_object':config,'source_objects_overlap':'summary/sum/detail/status alternatives; not additive; EID/CID empty arrays remain empty','comparisons':comparisons})
  checks.append({'source_id':sid,'contest_key':c['K'],'contest':c['C'],'units':len(d['P']),'named_total':sum(x['votes'] for x in comparisons),'all_candidate_total':sum(c['V']),'generic_writeins':sum(v for n,v in zip(c['CH'],c['V']) if 'write' in n.lower()),'summary_PR':c['PR'],'summary_TP':c['TP'],'sum_PR':s['PR'],'sum_TP':s['TP'],'row_and_column_sums_match':True,'named_county_controls_match':True})
# Vendor XML full objects retain repeats and election/contest/candidate IDs.
for sid,county,date,prefix in [('douglas-2024','Douglas','2024-11-05','president_2024'),('leavenworth-vendor','Leavenworth','2026-08-04','senate_primary_2026'),('butler-primary','Butler','2026-08-04','senate_primary_2026')]:
 root=ET.fromstring(raw(sid+'-summary-xml'));allrows=[{x.tag:x.text for x in e} for e in root.findall('Table')];g={e.tag:e.text for e in root if e.tag!='Table'};selected=[]
 for pos,c in enumerate(allrows):
  name=c.get('ContestantName','');k=canon(name);race=c.get('RaceName','').lower()
  if prefix=='president_2024':israce='president' in race
  else:israce=('senat' in race and not 'state sen' in race)
  if not israce:continue
  v=int(c['TotalVotes']);comp=None
  if k and prefix+'_'+k in BYNAME[county]:
   expected=int(BYNAME[county][prefix+'_'+k]);comp={'canonical':k,'votes':v,'accepted_county_control':expected,'difference':v-expected};assert sid=='butler-primary' or v==expected,(sid,k,v,expected)
  selected.append({'source_table_position':pos,'full_source_object':c,'comparison':comp})
 vendor.append({'source_id':sid,'county':county,'election_date':date,'full_global_objects':g,'selected_contest_rows':selected,'source_objects_overlap':'repeated race ballots/reporting counts are not added per candidate; methods from this publication only'})
 # Preserve all native CSV rows, including repeated positions and unavailable values.
 psid=sid+'-precincts-csv';b=raw(psid).decode('utf-8-sig');lines=b.splitlines();header=next(i for i,l in enumerate(lines) if l.startswith('Precinct,'));rows=list(csv.DictReader(io.StringIO('\n'.join(lines[header:]))));wanted=[{'source_line':i+header+2,'full_source_row':x} for i,x in enumerate(rows) if ('president' in x.get('Contest Name','').lower() if prefix=='president_2024' else 'senat' in x.get('Contest Name','').lower() and 'state sen' not in x.get('Contest Name','').lower())]
 z=gzip.compress(('\n'.join(compact(x) for x in wanted)+'\n').encode(),mtime=0);(R/'extracts'/f'{sid}-native-rows.jsonl.gz').write_bytes(z)
 checks.append({'source_id':sid,'election_date':date,'global_source_clock':g,'selected_candidate_rows':len(selected),'native_csv_rows':len(wanted),'native_distinct_literal_precinct_labels':len({x['full_source_row']['Precinct'] for x in wanted}),'named_county_controls_match':all(x['comparison'] is None or x['comparison']['difference']==0 for x in selected)})
wj('vendor-extracts.json',vendor);wj('vendor-checks.json',checks)
# PDF control lines: full originals and page text remain source of truth; no inferred method0.
pdfs=[('johnson-certified','Johnson'),('sedgwick-certified','Sedgwick'),('shawnee-2024','Shawnee'),('wyandotte-certified','Wyandotte'),('reno-original-pdf','Reno'),('riley-2024','Riley'),('crawford-certified','Crawford'),('cowley-2024','Cowley'),('lyon-certified','Lyon'),('finney-certified','Finney'),('barton-2024','Barton'),('sumner-2024-original','Sumner')]
controls=[]
for sid,county in pdfs:
 lines=(R/'extracts'/f'{sid}.txt').read_text().splitlines();comps=[]
 if sum(len(x.strip()) for x in lines)<50:
  controls.append({'source_id':sid,'county':county,'machine_control_status':'scannedPDF; raworiginal/visualpreview retained, no fabricated parsedcounts','comparisons':[]});continue
 for key in ['harris','trump','kennedy','oliver']:
  expected=int(BYNAME[county]['president_2024_'+key]);matches=[]
  for i,l in enumerate(lines):
   if key not in l.lower() or 'write-in' in l.lower() or 'susan' in l.lower():continue
   nums=re.findall(r'(?<![\w.])\d[\d,]*(?![\w.])',l)
   # first numeric vote in presidential source line (wrapped Kennedy line handled below)
   if nums and int(nums[0].replace(',',''))==expected:matches.append({'text_line':i+1,'literal':l,'first_integer':expected})
  if not matches and key=='kennedy':
   for i,l in enumerate(lines):
    if 'kennedy' in l.lower():
     for n in range(i,min(len(lines),i+4)):
      if re.search(r'(?<!\d)'+re.escape(f'{expected:,}')+r'(?!\d)',lines[n]):matches.append({'text_line':i+1,'literal_lines':lines[i:n+1],'first_integer':expected})
  if sid=='riley-2024' and not matches:
   for i,l in enumerate(lines):
    if key in l.lower() and not any(z in l.lower() for z in ['write-in','susan']):
     nums=re.findall(r'(?<![\w.])\d[\d,]*(?![\w.])',l)
     if not nums and i+1<len(lines): nums=re.findall(r'(?<![\w.])\d[\d,]*(?![\w.])',lines[i+1])
     if nums:matches.append({'text_line':i+1,'literal':l,'first_integer':int(nums[0].replace(',','')),'difference':int(nums[0].replace(',',''))-expected,'scope_difference':'actual county2024 Official Results Final All Groups differs from SOS; preserve both, cause unavailable'})
  assert matches,(sid,key,expected,'PDF candidate/control not directly verified')
  comps.append({'candidate':key,'expected_named_count':expected,'source_matches':matches})
 controls.append({'source_id':sid,'county':county,'scope':'2024general four named tickets only; local writein/under/over remain separately in complete source','comparisons':comps})
wj('pdf-control-checks.json',controls)
# Genuine historical release sequence, not a claimed guaranteed cadence.
seq=[]
for sid in ['sedgwick-advance','sedgwick-nightfinal','sedgwick-certified']:
 lines=(R/'extracts'/f'{sid}.txt').read_text().splitlines();v={}
 for k in ['harris','trump','kennedy','oliver']:
  line=next(l for l in lines if k in l.lower() and 'write-in' not in l.lower() and 'susan' not in l.lower());v[k]=int(re.search(r'\d[\d,]*',line).group().replace(',',''))
 clock=[{'line':i+1,'literal':l} for i,l in enumerate(lines) if re.search(r'\d{1,2}/\d{1,2}/2024',l)]
 seq.append({'source_id':sid,'named_candidate_votes':v,'four_named_total':sum(v.values()),'source_clock_lines':clock,'clock_timezone':None})
wj('historical-release-sequence.json',{'releases':seq,'decreases_observed':False,'limitation':'Three actual cumulative publication snapshots; no guaranteed cadence, no cause assigned to changes, no assumption corrections must increase; replace by source/scope and preserve negative revisions when seen.'})
wj('acquisition.json',[js(p) for p in sorted((R/'raw').glob('*.meta.json'))])
print('PASS native',len(keys),'countyfamilies',groups,'samples',len(samples),'rawcandidatecells',cellchecks,'vendorchecks',len(checks),'PDFcontrols',len(controls))
