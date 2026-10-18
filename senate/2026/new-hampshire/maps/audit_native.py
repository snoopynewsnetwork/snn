#!/usr/bin/env python3
"""Independently reopen primary BIFF/OOXML/PDF at every literal roster locator.
No turnout/baseline parser imports and no peer writes. Source objects copied byte-for-byte.
"""
import sys,pathlib,json,gzip,hashlib,io,zipfile,re,subprocess,xml.etree.ElementTree as ET,collections
from acquire import ROOT,sha
sys.path.insert(0,'/tmp/snn-xls-reading-libs')
import xlrd
STATE=ROOT.parent;TURN=STATE/'data/turnout';C=json.loads((TURN/'priority-set.json').read_text());shared={x['id']:x for x in json.loads((TURN/'source/shared-originals.json').read_text())}
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def ooxml(b):
 z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None
 strings=[''.join(n.itertext()) for n in ET.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml'in z.namelist() else []
 rels={n.get('Id'):n.get('Target') for n in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))};out={}
 for sh in ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS):
  name=rels[sh.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/');name=name if name.startswith('xl/') else 'xl/'+name
  rows={}
  for row in ET.fromstring(z.read(name)).findall('.//s:row',NS):
   cells={}
   for cell in row:
    col=re.sub(r'\d+','',cell.get('r'));node=cell.find('s:v',NS);v=node.text if node is not None else ''
    if cell.get('t')=='s':v=strings[int(v)]
    elif cell.get('t')=='inlineStr':v=''.join(cell.find('s:is',NS).itertext())
    elif v and cell.get('t')not in ['str','e']:v=float(v)
    cells[col]=v
   rows[int(row.get('r'))]=cells
  out[sh.get('name')]=rows
 return out
controls=json.loads((TURN/'controls.json').read_text());refs=[];audits=[];allfields=0;allcontrols=0;balances=[];(ROOT/'compatibility/native').mkdir(parents=True,exist_ok=True)
for fam in C['source_native_coverage']:
 source=fam['source_id'];p=TURN/fam['path'];b=p.read_bytes();assert sha(b)==fam['sha256'];
 if '--check-only' not in sys.argv:(ROOT/'compatibility'/fam['path']).write_bytes(b)
 rows=[json.loads(l) for l in gzip.decompress(b).splitlines()];assert len(rows)==320 and len({(r['county'],r['native_label'])for r in rows})==320
 mp=TURN/'source'/f'{source}.json';m=json.loads(mp.read_text()) if mp.exists() else shared[source];origp=(TURN/m['shared_path']).resolve() if 'shared_path'in m else TURN/'source'/m['body_path'];stored=origp.read_bytes();assert sha(stored)==m['stored_sha256'];raw=gzip.decompress(stored)
 if m.get('http_content_decoding')=='gzip':raw=gzip.decompress(raw)
 expected=m.get('decoded_original_sha256',m.get('original_sha256',m.get('raw_sha256')));assert sha(raw)==expected
 refs.append({'source_id':source,'path':str(origp.relative_to(STATE)),'bytes':len(stored),'sha256':sha(stored),'decoded_original_bytes':len(raw),'decoded_original_sha256':sha(raw),'metadata':m,'metadata_path':str(mp.relative_to(STATE)) if mp.exists() else 'data/turnout/source/shared-originals.json','scope':'Exact read-only source vintage, never current geography'})
 if raw.startswith(b'%PDF-'):pages=subprocess.run(['pdftotext','-layout','-','-'],input=raw,capture_output=True,check=True).stdout.decode().split('\f');book=None
 elif raw.startswith(b'PK'):book=ooxml(raw)
 else:book=xlrd.open_workbook(file_contents=raw,formatting_info=True)
 sums=collections.Counter();nulls=collections.Counter();bycounty={};checks=0
 controlrows=list(controls[source]['summary'].values())+controls[source]['footers']
 for ri,r in enumerate(rows+controlrows):
  native=ri<320
  assert r['source_id']==source and r['source_native_id']is None
  if native:
   c=fam['constituents'][ri];assert (r['county'],r['native_label'],r['source_locator'])==(c['county'],c['native_label'],c['locator'])
  expectedvals=list(r['raw_fields'].values())
  if r['sheet']is None:
   line=pages[r['page']-1].splitlines()[r['line']-1].strip();assert line.startswith(r['native_label']);assert line[len(r['native_label']):].split()==[str(v)for v in expectedvals if str(v)]
  elif isinstance(book,dict):
   row=book[r['sheet']][r['source_row']];headers=[v for k,v in book[r['sheet']].items() if k<r['source_row']and all(x in v.values()for x in ['Republican','Democratic','Undeclared','Total'])];assert headers
   header=headers[-1];order=['Republican','Democratic','Undeclared','Total']+list(map(float,range(1,len(expectedvals)-3)));cols=[next(k for k,v in header.items()if v==x)for x in order];assert [row.get(k,'')for k in cols]==expectedvals;assert r['native_label']in row.values()
  else:
   sh=book.sheet_by_name(r['sheet']);vs=sh.row_values(r['source_row']-1);positions=[i for i,x in enumerate(vs)if str(x).strip()==r['native_label'].strip() and vs[i+1:i+1+len(expectedvals)]==expectedvals];assert len(positions)==1,(source,r['native_label']);pos=positions[0]
   if 'cell_types'in r:assert list(sh.row_types(r['source_row']-1))[pos+1:pos+1+len(expectedvals)]==r['cell_types']
  for k,v in r['fields'].items():
   rawv=r['raw_fields'][k]
   if isinstance(rawv,(int,float)):assert int(rawv)==rawv==v
   elif str(rawv).strip()in ['','-','–','—']:assert v is None
   else:assert int(str(rawv).replace(',',''))==v
   if native:
    if v is not None:sums[k]+=v;bycounty.setdefault(r['county'],collections.Counter())[k]+=v
    else:nulls[k]+=1
    checks+=1
   else:allcontrols+=1
 state=controls[source]['summary'].get('TOTALS',{}).get('fields',{});balances.append({'source_id':source,'primary_verified_summary':controls[source]['summary'],'primary_verified_footers':controls[source]['footers'],'leaf_minus_state':{k:sums[k]-v for k,v in state.items()if v is not None},'detail_minus_county_footer':[{'county':r['county'],'deltas':{k:bycounty[r['county']][k]-v for k,v in r['fields'].items()if v is not None}}for r in controls[source]['footers']]})
 audits.append({'source_id':source,'exact_roster_path':'compatibility/'+fam['path'],'roster_sha256':sha(b),'exact_objects':len(rows),'all_original_fields_checked':checks,'numeric_field_subtotals':dict(sums),'null_field_counts':dict(nulls),'county_subtotals':bycounty,'current_geometry_join':'not attempted; independent vintage objects retained'})
 allfields+=checks
# Full descending sequence and integer crossing independently calculated from primary-verified literal objects.
pres=[json.loads(l)for l in gzip.decompress((TURN/'native/sos-2024-president-archived-original.jsonl.gz').read_bytes()).splitlines()]
from urllib.parse import quote
for r in pres:r['volume']=sum(r['fields'][k]for k in ['harris_walz','trump_vance','oliver_ter_maat','stein_ware','generic_write_ins'] if r['fields'][k]is not None)
pres.sort(key=lambda r:(-r['volume'],r['county_fips'],r['native_label'].strip()));keys=['nh-2024-pres:'+r['county_fips']+':'+quote(r['native_label'].strip(),safe='')for r in pres]
assert keys==C['full_ordered_keys'];assert keys[:143]==C['ordered_priority_keys'];assert sum(r['volume']for r in pres)==826189;assert sum(r['volume']for r in pres[:15])==185659
before=sum(r['volume']for r in pres[:142]);after=before+pres[142]['volume'];assert (before,after,pres[142]['native_label'])==(660378,662624,'Tilton');assert 5*before<4*826189<=5*after
assert len(audits)==23 and allfields==34880
if '--check-only' not in sys.argv:(ROOT/'source/native-original-references.json').write_text(json.dumps(refs,indent=2)+'\n')
if '--check-only' not in sys.argv:(ROOT/'compatibility/diagnostics.json').write_text(json.dumps({'status':'pass','source_rosters':23,'source_scoped_objects':7360,'original_fields_checked':allfields,'no_cross_year_join':True,'no_vote_allocation':True,'ordered_320_verified':True,'minimum80_count':143,'denominator':826189,'top15':185659,'first142':before,'first143':after,'sources':audits},indent=2)+'\n')
if '--check-only' not in sys.argv:(ROOT/'compatibility/primary-control-balances.json').write_text(json.dumps({'control_fields_verified':allcontrols,'sources':balances,'policy':'All original controls and known defects retained; delta is diagnostic, never rescale/correct native fields.'},indent=2)+'\n')
print('PASS',len(audits),'rosters;7360 primary-locator objects;',allfields,'fields;320ordered;143crossing')
