#!/usr/bin/env python3
"""Independent stdlib OOXML + native text extraction. No peer parser/aggregate imported."""
import pathlib,io,gzip,json,hashlib,zipfile,xml.etree.ElementTree as E,collections,posixpath,csv
ROOT=pathlib.Path(__file__).resolve().parent;STATE=ROOT.parent.parent;NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def digest(b):return hashlib.sha256(b).hexdigest()
def writejson(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def workbook(b):
 z=zipfile.ZipFile(io.BytesIO(b));ss=[]
 if 'xl/sharedStrings.xml' in z.namelist():ss=[''.join(n.itertext()) for n in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
 rel={n.attrib['Id']:n.attrib['Target'] for n in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))};out={}
 for sh in E.fromstring(z.read('xl/workbook.xml')).find('s:sheets',NS):
  target=rel[sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']];path=posixpath.normpath(posixpath.join('xl',target)) if not target.startswith('/') else target[1:];rows=[]
  for row in E.fromstring(z.read(path)).findall('.//s:sheetData/s:row',NS):
   cells=[]
   for c in row:
    v=c.find('s:v',NS);v=v.text if v is not None else None;t=c.attrib.get('t');val=ss[int(v)] if t=='s' and v is not None else ''.join(c.find('s:is',NS).itertext()) if t=='inlineStr' else v
    cells.append({'address':c.attrib['r'],'attributes':dict(c.attrib),'raw_value':v,'value':val,'xml':E.tostring(c,encoding='unicode')})
   rows.append({'row':row.attrib['r'],'attributes':dict(row.attrib),'cells':cells})
  out[sh.attrib['name']]={'xml_path':path,'rows':rows}
 return out

def rowsmap(sheet):
 return [{''.join(x for x in c['address'] if x.isalpha()):c['value'] for c in row['cells']} for row in sheet['rows']]
def textfile(id):
 b=gzip.decompress((ROOT/'raw'/f'{id}.body.gz').read_bytes());rows=[];off=0
 for i,line in enumerate(b.splitlines(keepends=True),1):
  rows.append({'line':i,'byte_start':off,'byte_end':off+len(line),'fields':line.rstrip(b'\r\n').decode('cp1252').split(';')});off+=len(line)
 return rows
if __name__=='__main__':
 contractpath=STATE/'data/turnout/priority-set.json';contractbytes=contractpath.read_bytes();accept=json.loads((STATE/'data/coordinator-priority-acceptance.json').read_text());assert digest(contractbytes)==accept['contract_sha256'];contract=json.loads(contractbytes)
 refs=[];records=[];controls={};workbooks={}
 for year in [2024,2022,2020]:
  path=STATE/f'data/news/sos-{year}-precinct-original.html.gz';packed=path.read_bytes();b=gzip.decompress(packed);refs.append({'path':str(path.relative_to(STATE)),'stored_bytes':len(packed),'stored_sha256':digest(packed),'raw_bytes':len(b),'raw_sha256':digest(b),'role':'complete primary original workbook'})
  w=workbook(b);workbooks[year]=w;data=rowsmap(w['Precinct-Results']);head=data[0];selected=[]
  countyrows=rowsmap(w['Counties'])[1:];county_lookup={int(c['A']):c['C'] for c in countyrows if c.get('A') and c.get('C') and c['A'].isdigit()}
  count=0
  for source,row in zip(w['Precinct-Results']['rows'][1:],data[1:]):
   if not row.get('A') or not row['A'].isdigit():continue
   n={'year':year,'sheet':'Precinct-Results','xml_path':w['Precinct-Results']['xml_path'],'row':source['row'],'county_fips':county_lookup[int(row['F'])],'all_cells':source['cells'],'headers_by_column':head};records.append(n);count+=1
   vals={head[col]:val for col,val in row.items() if col in head and head[col]!='TABMODEL'};vals['source_row']=source['row'];vals['county_fips']=n['county_fips'];selected.append(vals)
  controls[str(year)]={'native_rows':count,'counties':len(county_lookup),'sheets':{k:{'xml_path':v['xml_path'],'row_count':len(v['rows'])} for k,v in w.items()},'source_header_by_column':head}
  # Small sheets retain exact fields, source positions and duplicate-header distinctions.
  writejson(ROOT/f'workbook-context-{year}.json',{k:v for k,v in w.items() if k!='Precinct-Results'})
  with gzip.GzipFile(filename='',mode='wb',fileobj=(ROOT/f'native-{year}.jsonl.gz').open('wb'),mtime=0) as out:
   for n in [x for x in records if x['year']==year]:out.write((json.dumps(n,ensure_ascii=False,separators=(',',':'))+'\n').encode())
  controls[str(year)]['county_controls']={}
  prefix='MNGOV' if year==2022 else 'USSEN';fields=[v for v in head.values() if v and v.startswith(prefix)]
  for fips in county_lookup.values():
   rs=[v for v in selected if v['county_fips']==fips];controls[str(year)]['county_controls'][fips]={'native_rows':len(rs),'fields':{f:sum(int(v[f]) for v in rs) for f in fields},'method_fields':{f:sum(int(v[f]) for v in rs if v.get(f) is not None) for f in ['REG7AM','EDR','SIGNATURES','AB_MB','FEDONLYAB','PRESONLYAB','TOTVOTING'] if f in head.values()},'method_blanks':{f:sum(v.get(f) is None for v in rs) for f in ['SIGNATURES','AB_MB','TOTVOTING']}}
  for c in contract['county_order']:
   for n in c['native_constituents'][str(year)]:
    sr=next(v for v in selected if v['source_row']==n['source_row']);assert sr['VTDID']==n['VTDID'] and sr['PCTCODE']==n['PCTCODE'];assert sr['county_fips']==c['county_fips'];assert int(sr[prefix+'TOTAL'])==n['candidate_votes']
 # Exact county contract objects and every constituent, unchanged including administrative/unavailable scopes.
 with gzip.GzipFile(filename='',mode='wb',fileobj=(ROOT/'county-native-contexts.jsonl.gz').open('wb'),mtime=0) as out:
  for c in contract['county_order']:out.write((json.dumps(c,ensure_ascii=False,separators=(',',':'))+'\n').encode())
 writejson(ROOT/'original-references.json',refs);writejson(ROOT/'historical-controls.json',controls)
 # Independent downloaded text controls with byte/line/field indexes.
 ids=['export-2024-state','export-2024-county','export-2024-precinct','export-2024-candidates','export-2024-counties','export-2024-parties','export-2024-precincts','export-2024-statistics','export-primary-state','export-primary-county','export-primary-precinct','export-primary-candidates','export-primary-counties','export-primary-precincts','export-primary-statistics']
 parsed={}
 for id in ids:
  rows=textfile(id);parsed[id]=rows
  with gzip.GzipFile(filename='',mode='wb',fileobj=(ROOT/(id+'.rows.jsonl.gz')).open('wb'),mtime=0) as out:
   for row in rows:out.write((json.dumps(row,separators=(',',':'))+'\n').encode())
 check={'schema':'semicolon; 16 zero-based fields for candidate result files, blank fields retained; 12 fields stats; no candidate-method dimension','rows':{k:len(v) for k,v in parsed.items()},'candidate_county_state':[],'native_candidate_comparisons':0,'native_method_comparisons':0,'differences':[]}
 candfields={'Rebecca Whiting':'USSENLIB','Amy Klobuchar':'USSENDFL','Joyce Lynne Lacey':'USSENIA','Royce White':'USSENR','WRITE-IN':'USSENWI'}
 countyfips={int(c['source_county_code']):c['county_fips'] for c in contract['county_order']}
 native={}
 for n in [n for n in records if n['year']==2024]:
  colvals={''.join(t for t in c['address'] if t.isalpha()):c['value'] for c in n['all_cells']};h=n['headers_by_column'];vals={h[k]:v for k,v in colvals.items()};native[(int(vals['COUNTYCODE']),vals['PCTCODE'])]=vals
 for row in parsed['export-2024-state']:
  a=row['fields'];name=a[7];v=int(a[13]);cty=sum(int(x['fields'][13]) for x in parsed['export-2024-county'] if x['fields'][7]==name);pct=sum(int(x['fields'][13]) for x in parsed['export-2024-precinct'] if x['fields'][7]==name);wb=sum(c['fields'][candfields[name]] for c in controls['2024']['county_controls'].values());check['candidate_county_state'].append({'candidate':name,'state':v,'county_sum':cty,'precinct_sum':pct,'workbook_sum':wb,'equal':v==cty==pct==wb})
 for row in parsed['export-2024-precinct']:
  a=row['fields'];key=(int(a[1]),a[2]);nativeval=int(native[key][candfields[a[7]]]);check['native_candidate_comparisons']+=1
  if nativeval!=int(a[13]):check['differences'].append({'file':'export-2024-precinct','line':row['line'],'key':key,'candidate':a[7],'text':a[13],'workbook':nativeval})
 for row in parsed['export-2024-statistics']:
  a=row['fields'];key=(int(a[1]),a[2]);v=native[key]
  for j,f in [(5,'REG7AM'),(6,'EDR'),(7,'SIGNATURES'),(8,'AB_MB'),(9,'FEDONLYAB'),(10,'PRESONLYAB'),(11,'TOTVOTING')]:
   check['native_method_comparisons']+=1
   if v[f]!=a[j]:check['differences'].append({'file':'export-2024-statistics','line':row['line'],'field_index':j,'key':key,'field':f,'text':a[j],'workbook':v[f]})
 for row in parsed['export-2024-county']:
  a=row['fields'];control=controls['2024']['county_controls'][countyfips[int(a[1])]]['fields'][candfields[a[7]]]
  if control!=int(a[13]):check['differences'].append({'file':'export-2024-county','line':row['line'],'text':a[13],'workbook':control})
 writejson(ROOT/'export-reconciliation.json',check)
 print('original native rows',len(records),'constituents',sum(len(c['native_constituents'][y]) for c in contract['county_order'] for y in ['2024','2022','2020']),'differences',len(check['differences']),check['rows'])
