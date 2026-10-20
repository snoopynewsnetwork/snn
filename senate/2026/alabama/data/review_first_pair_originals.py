"""Coordinator independent whole original XLS/source/candidate/order review.
Run under the isolated /tmp xlrd2.0.2 reader; no producer module is imported.
Default creates one coordinator proof; --check compares it read-only.
"""
from pathlib import Path
from collections import Counter
from urllib.parse import quote
import csv,gzip,hashlib,io,json,subprocess,sys,tempfile,zipfile
import xlrd
S=Path(__file__).resolve().parents[1];D=S/'data';T=D/'turnout';B=D/'baselines'
N=0
def ck(ok,label):
 global N
 N+=1
 if not ok:raise AssertionError(label)
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def pin(p):
 b=p.read_bytes();return {'path':str(p.resolve().relative_to(S.resolve())),'bytes':len(b),'sha256':sha(b)}
manifest_pins=[]
for root,field,count,digest,extra in [(T,'assets',145,'4e2a1f5ab3c66508444c112f9e6430006dce94f795a172837c7b95eaee557207',['turnout.md','data/county-turnout.csv']),(B,'assets',306,'13ec2553cbeafdbf4111f1decd6c686e14d5fbfb8c196c70d3e95836f7016254',['county-partisanship.md','data/county-baselines.csv'])]:
 mf=read(root/'asset-manifest.json');ck(len(mf[field])==count and sha((root/'asset-manifest.json').read_bytes())==digest,'exact sealed producer manifest')
 actual={str(p.resolve().relative_to(S.resolve()))for p in root.rglob('*')if p.is_file()and p!=root/'asset-manifest.json'}|set(extra)
 ck(actual=={r['path']for r in mf[field]},'complete exact membership')
 for r in mf[field]:ck(pin(S/r['path'])==r and r['bytes']<40000000,'complete sealed body '+r['path'])
 manifest_pins.append(pin(root/'asset-manifest.json'))
source_bodies={};source_pins=[];receipts=0
for r in read(T/'source/original-receipts.json'):
 p=Path(r['shared_path']);stored=p.read_bytes();raw=gzip.decompress(stored)
 ck(sha(stored)==r['stored_sha256'] and sha(raw)==r['raw_sha256'],'complete shared original')
 source_bodies[sha(raw)]=raw;source_pins.append(pin(p));receipts+=1
for p in sorted((T/'source/http').glob('*.receipt.json')):
 r=read(p);parts=[]
 for v in r['parts']:
  b=(T/v['path']).read_bytes();ck(len(b)==v['bytes']<40000000 and sha(b)==v['sha256'],'complete ordered HTTP source part');parts.append(b)
 raw=gzip.decompress(b''.join(parts));ck(len(raw)==r['original_bytes']and sha(raw)==r['original_sha256'],'complete HTTP original and literal receipt')
 source_bodies[sha(raw)]=raw;receipts+=1
for p in sorted((B/'source/http').glob('*.receipt.json')):
 r=read(p);stored=(B/r['stored_path_relative_baselines']).read_bytes();raw=gzip.decompress(stored)
 ck(len(stored)==r['stored_bytes'] and sha(stored)==r['stored_sha256'] and len(raw)==r['original_bytes']and sha(raw)==r['original_sha256'],'complete independent baseline current original receipt')
 source_bodies[sha(raw)]=raw;receipts+=1
books={(r['year'],r['member']):r for r in read(B/'source/typed-workbooks.json.gz')}
bnative=read(B/'source/native-observations.json.gz');bn={(r['year'],r['member'],r['source_column']):r for r in bnative}
bcounty={(r['year'],r['member']):r for r in read(B/'source/county-observations.json')}
ck(len(bnative)==len(bn)==6270,'all baseline source-native identities')
cells=selected=descriptors=positions=0;orders={};candidate_totals={};members=[];allown={};jefferson={}
zipsha={2024:'4ecca55fc235018aeb2385debd375e6fa7aaa553c5bd67786add08d850efcc96',2022:'4ea186b9e9eefa7786b3708b8ffd2da5755a9ba5c018b4ff9d47a2ceec46983a',2020:'471fc54cfc87984c8e6325c4baef6933545044cd6482a153c234b97f74d4693d'}
for year,h in zipsha.items():
 z=zipfile.ZipFile(io.BytesIO(source_bodies[h]));ck(len(z.infolist())==67 and z.testzip() is None,'complete source ZIP all67 members')
 traw={r['member']['name']:r for r in read(T/f'source/workbooks-{year}.json.gz')};tnative=read(T/f'native-units-{year}.json');tn={(r['source_member'],r['column_1based']):r for r in tnative};own=[];totals=Counter()
 ck(len(tn)==len(tnative)=={2024:2085,2022:2074,2020:2111}[year],'complete native universe')
 for info in z.infolist():
  body=z.read(info);msha=sha(body);wb=xlrd.open_workbook(file_contents=body,formatting_info=True);td=traw[info.filename];bd=books[year,info.filename]
  ck(msha==td['member']['sha256']==bd['member_sha256']and len(body)==td['member']['bytes']==bd['member_bytes']and info.CRC==td['member']['zip_crc32'],'every complete original member')
  ck(len(wb.sheets())==len(td['sheets'])==len(bd['sheets'])==1,'all original sheets')
  ws=wb.sheet_by_index(0);ts=td['sheets'][0];bs=bd['sheets'][0]
  ck((ws.name,ws.nrows,ws.ncols)==(ts['name'],ts['nrows'],ts['ncols'])==(bs['name'],bs['nrows'],bs['ncols']),'sheet name/counts')
  ck(ws.merged_cells==[tuple(v)for v in ts['merged_cells']]==[tuple(v)for v in bs['merged_cells']],'all merged cell records')
  for ri,rr in enumerate(ts['rows']):
   ck(rr['row_1based']==ri+1 and len(rr['values'])==len(rr['types'])==ws.ncols,'complete typed original row shape')
   for ci,(typ,val)in enumerate(zip(rr['types'],rr['values'])):
    ck((typ,val)==(ws.cell_type(ri,ci),ws.cell_value(ri,ci)),'every raw source typed cell');cells+=1
  for rr in bs['row_descriptors']:
   for ci,v in enumerate(rr['cells']):ck(v==[ws.cell_type(rr['row']-1,ci),ws.cell_value(rr['row']-1,ci)],'every baseline original descriptor');descriptors+=1
  for rr in bs['selected_rows']:
   for ci,v in enumerate(rr['cells']):ck(v==[ws.cell_type(rr['row']-1,ci),ws.cell_value(rr['row']-1,ci)],'every baseline selected typed cell');selected+=1
  cols=[i for i in range(3,ws.ncols)if str(ws.cell_value(0,i)).strip()]
  ck([i+1 for i in cols]==bs['native_columns_1based'],'every native literal header column')
  contest='PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES'if year==2024 else'UNITED STATES SENATOR'
  rows=[i for i in range(1,ws.nrows)if str(ws.cell_value(i,0)).strip()==contest]
  cand=[i for i in rows if str(ws.cell_value(i,2)).strip()not in ['Under Votes','Over Votes']]
  admin=[i for i in range(1,ws.nrows)if str(ws.cell_value(i,0)).strip().startswith(('REGISTERED VOTERS','BALLOTS CAST'))or str(ws.cell_value(i,0)).strip()=='STRAIGHT PARTY']
  cr=bcounty[year,info.filename]
  for ci in cols:
   tu=tn[info.filename,ci+1];bu=bn[year,info.filename,ci+1];header=ws.cell_value(0,ci);key=f'AL:{year}:general:{bd["county_fips"]}:col{ci+1:03}:'+quote(header,safe='')
   ck(key==tu['key']==bu['key']and header==tu['native_label']==bu['native_header_literal']and ws.name==tu['source_sheet']==bu['sheet'],'complete original native identity/header/key')
   ck(msha==tu['member_sha256']==bu['member_sha256'],'native original member reference')
   count=0
   for category,rrs,bfield in [('candidate_votes',cand,'candidate_rows'),('contest_other_fields',[i for i in rows if i not in cand],None),('administrative_fields',admin,None)]:
    ck(len(tu[category])==len(rrs),'all candidate/admin/under-over source records')
    for out,ri in zip(tu[category],rrs):
     typ=ws.cell_type(ri,ci);raw=ws.cell_value(ri,ci);value=int(raw)if isinstance(raw,(int,float))else None
     ck((out['row_1based'],out['column_1based'],out['contest_literal'],out['party_literal'],out['candidate_literal'],out['xls_type'],out['raw_value'],out['value'])==(ri+1,ci+1,ws.cell_value(ri,0),ws.cell_value(ri,1),ws.cell_value(ri,2),typ,raw,value),'whole turnout candidate/admin source-cell object');positions+=1
     bb=next(r for r in bu['candidate_rows']if r['source_row']==ri+1)if bfield else next(r for r in bu['administrative_rows']if r['source_row']==ri+1)
     ck(bb['cell']==[typ,raw] and bb['contest_literal']==ws.cell_value(ri,0)and bb.get('candidate_literal',bb.get('field_literal'))==ws.cell_value(ri,2)and bb.get('votes',bb.get('value'))==value,'whole baseline source-cell object')
     if bfield:
      ck(bb['party_literal']==ws.cell_value(ri,1),'literal party remains source label')
      ck(typ==2 and value is not None,'candidate observed numeric not invented zero');count+=value;totals[str(ws.cell_value(ri,2)).strip()]+=value
   ck(count==tu['reported_candidate_votes']==bu['reported_contest_votes']==bu['complete_contest_votes'],'each independently summed native candidate vector')
   own.append({'key':key,'votes':count,'county_fips':bd['county_fips']})
  for row in cr['candidate_rows']:
   ri=row['source_row']-1;total=sum(ws.cell_value(ri,ci)for ci in cols)
   ck(row['votes']==row['reported_sum']==total and row['unknown_cells']==0 and row['candidate_literal']==ws.cell_value(ri,2)and row['party_literal']==ws.cell_value(ri,1),'every literal county candidate sum')
   if year==2024 and bd['county']=='Jefferson':jefferson[str(ws.cell_value(ri,2)).strip()]={'row':ri+1,'sum':int(total)}
  members.append({'year':year,'member':info.filename,'sha256':msha,'CRC32':info.CRC,'native_columns':len(cols)})
 order=sorted(own,key=lambda r:(-r['votes'],r['key']));den=sum(r['votes']for r in own);cum=0;cross=None
 for i,r in enumerate(order,1):
  cum+=r['votes'];tr=tnative[i-1];ck(tr['key']==r['key']and tr['rank']==i and tr['cumulative_votes']==cum,'entire original-count native descending order')
  if cross is None and 5*cum>=4*den:cross=i;crosssum=cum;before=cum-r['votes']
 summary=read(T/'native-rank-summary.json')[str(year)]
 ck((summary['denominator'],summary['minimum80_count'],summary['minimum80_votes'],summary['preceding_votes'])==(den,cross,crosssum,before),'exact full original-count integer80 threshold')
 ck(summary['priority_keys']==[r['key']for r in order[:cross]]and summary['remainder_keys']==[r['key']for r in order[cross:]],'all priority and remainder source keys')
 ck(dict(totals)==read(T/'statewide-controls.json')[str(year)],'all original literal candidate totals versus full primary control')
 candidate_totals[str(year)]=dict(totals);allown[year]=own;orders[str(year)]={'native':len(own),'denominator':den,'top15':sum(r['votes']for r in order[:15]),'minimum80':cross,'prefix':crosssum,'preceding':before,'crossing':order[cross-1]['key']}
ck(jefferson['Jill Stein']=={'row':12,'sum':994}and jefferson['Chase Oliver']=={'row':13,'sum':731},'Jefferson candidate order regression grouped by literal identity, never rowordinal')
# Independently render full original PDFs to text and verify retained exact source positions.
pdfrows=read(T/'canvass-cells.json');bpdf=read(B/'source/canvass-county-cells.json');pdfproof=[]
for year,rawhash in [(2024,'88ec1f92e29aca3a715981f8540fad2351e8dfde8bc252022821ce108efad49d'),(2022,'2f924587c91a72f161913a110612125bbc17b78151e20963a0003774666091ed'),(2020,'2cb5744552cf0574234fa8e731adbe83ccee5ae3421ee4e8e28c35c47a6d7176')]:
 with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
  f.write(source_bodies[rawhash]);f.flush();proc=subprocess.run(['pdftotext','-layout',f.name,'-'],capture_output=True,check=True)
 ck(proc.stdout==(T/f'source/sos-{year}-canvass-original.txt').read_bytes(),'complete primary PDF original independent text replay')
 pages=proc.stdout.decode().split('\f')
 for r in [r for r in pdfrows if r['source']==f'sos-{year}-canvass-original']:
  line=pages[r['pdf_page_1based']-1].splitlines()[r['extracted_line_1based']-1];ck(line==r['raw_line'],'complete PDF raw source row/position')
  for cell,name in zip(r['cells'],r['candidate_names_in_order']):
   if cell.get('visual_transcription'):
    ck(year==2024 and r['county']in ['Hale','Winston'],'bounded actual visual override only')
   elif cell['value']is not None:
    start,end=cell['character_span_0based'];ck(line[start:end]==cell['literal']and int(cell['literal'].replace(',',''))==cell['value'],'original PDF integer token span')
   if r['county']is not None:
    br=next(v for v in bpdf if v['year']==year and v['county_fips']==r['county_fips']);bc=next(v for v in br['candidate_cells']if v['candidate']==name);ck(bc['value']==cell['value'],'independent literal canvass county candidate including nulls')
 pdfproof.append({'year':year,'raw_sha256':rawhash,'whole_text_sha256':sha(proc.stdout),'warnings_sha256':sha(proc.stderr)})
# Check the actual viewed original Hale/Winston transcription values; do not infer blank as0.
for county,values in [('Hale',[3868,3369,30,10,13,15]),('Winston',[884,10191,36,8,10,20])]:
 r=next(r for r in pdfrows if r['source']=='sos-2024-canvass-original'and r['county']==county);ck(r['target_contest_numeric_values']==values,'whole original manually viewed row '+county)
ck(sum(c['value']is None for r in pdfrows for c in r['cells'])==3,'three PDF missing/dash observations remain literal null')
contract=read(T/'priority-set.json');full=[r['key']for r in sorted(allown[2024],key=lambda r:(-r['votes'],r['key']))]
ck(contract['full_order']==contract['certified_statewide_native_order']==full and contract['ordered_priority_keys']==full[:887]and contract['remainder_keys']==full[887:],'entire primary native contract')
for p in contract['parents']:
 children=[r['key']for r in allown[2024]if r['county_fips']==p['county_fips']]
 ck(p['constituent_keys']==children and p['priority_constituent_keys']==[k for k in children if k in set(full[:887])]and p['remainder_constituent_keys']==[k for k in children if k not in set(full[:887])],'every full parent/priority/remainder array')
out={'status':'pass_independent_complete_original_first_pair_source_review','checks':N,'reader':'xlrd2.0.2 isolated /tmp reader; no producer import','producer_manifests':manifest_pins,'whole_original_members':len(members),'raw_turnout_typed_cells':cells,'baseline_selected_typed_cells':selected,'baseline_descriptor_cells':descriptors,'source_candidate_admin_positions':positions,'all_native_records':len(bn),'complete_literal_label_candidate_controls':candidate_totals,'full_original_count_orders':orders,'Jefferson_literal_order_regression':jefferson,'PDF_source_replays':pdfproof,'manual_visual_scope':'Two complete original2024 canvass physical pages5/6 (including Hale,Winston,Jefferson and blankWilcoxStein); other pages text/source-position audit only. Earlier independent sharedp6 inspection retained separately.','source_receipts_checked':receipts,'source_or_peer_writes':False,'source_residual_allocation':False,'current_or_legal_geography_approval':False}
body=(json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode();p=D/'coordinator-first-pair-original-review.json'
if '--check'in sys.argv:ck(p.read_bytes()==body,'exact frozen review replay')
else:p.write_bytes(body)
print(json.dumps({k:v for k,v in out.items()if k not in ['complete_literal_label_candidate_controls','PDF_source_replays','Jefferson_literal_order_regression']}))
