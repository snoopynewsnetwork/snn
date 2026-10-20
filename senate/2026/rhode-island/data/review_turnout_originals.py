"""Coordinator independent fixed-width/source-anchor review; no producer imports/writes."""
from pathlib import Path
import json,gzip,hashlib,io,zipfile,tarfile,collections
S=Path(__file__).resolve().parents[1];T=S/'data/turnout';N=0

def sha(b):return hashlib.sha256(b).hexdigest()
def ck(x,why):
 global N
 N+=1
 if not x:raise AssertionError(why)
def load(p):return json.loads(p.read_bytes())
fields=[('contest',0,4),('candidate',4,7),('reporting_code',7,11),('total',11,17)]+[(f'group_{i}',17+6*(i-1),23+6*(i-1)) for i in range(1,15)]+[('party',101,104),('district_type',104,107),('district_code',107,111),('contest_title',111,167),('candidate_name',167,205),('reporting_name',205,235),('district_name',235,260),('votes_allowed',260,262),('referendum_flag',262,263)]
m=load(T/'asset-manifest.json');actual={str(p.relative_to(S)) for p in T.rglob('*') if p.is_file()}|{'turnout.md','data/county-turnout.csv'};ck(len(m['owned_assets'])==len({r['path'] for r in m['owned_assets']})==361,'unique complete MF');ck(actual=={r['path'] for r in m['owned_assets']}|{'data/turnout/asset-manifest.json'},'only MF excluded')
for r in m['owned_assets']:
 b=(S/r['path']).read_bytes();ck(len(b)==r['bytes']<40000000 and sha(b)==r['sha256'],'complete exact owned byte '+r['path'])
w=load(T/'qa/pre-peer-body-witness.json');stored=(T/w['body_archive']['path']).read_bytes();raw=gzip.decompress(stored);ck(sha(stored)==w['body_archive']['stored_sha256'] and sha(raw)==w['body_archive']['uncompressed_tar_sha256'],'lossless complete witness archive')
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
 for r in w['frozen_bodies']:
  b=tar.extractfile(r['path']).read();ck(len(b)==r['bytes'] and sha(b)==r['sha256'] and b==(S/r['path']).read_bytes(),'every original-first body target')
for r in w['immutable_original_references']:
 z=(S/r['path']).read_bytes();ck(len(z)==r['stored_bytes'] and sha(z)==r['stored_sha256'],'exact original stored body');b=gzip.decompress(z) if r['compression']=='gzip' else z;ck(len(b)==r['raw_bytes'] and sha(b)==r['raw_sha256'],'entire original reconstructed body')
inputs=load(T/'source/inputs/original-receipts.json');all_saved=iter(gzip.open(T/'extracts/all-long-rows.jsonl.gz','rt'));selected_saved=iter(gzip.open(T/'extracts/selected-root-rows.jsonl.gz','rt'));prefixes={};inventory=load(T/'source/zip-members.json');im={(r['source_id'],r['member']):r for r in inventory};seen=set();long_n=selected_n=0;root_years=collections.Counter();totals=collections.defaultdict(lambda:collections.defaultdict(int));sen={};anchors={}
for receipt in inputs:
 z=(T/receipt['stored_path']).read_bytes();b=gzip.decompress(z) if receipt.get('compression')=='gzip' else z;ck(sha(z)==receipt['stored_sha256'] and sha(b)==receipt['raw_sha256'],'original individual input entity')
 if not b.startswith(b'PK'):continue
 arc=zipfile.ZipFile(io.BytesIO(b));ck(arc.testzip() is None,'whole original ZIP CRC');year=next(y for y in ['2020','2022','2024'] if y in receipt['id'])
 for info in arc.infolist():
  member=arc.read(info);meta=im[receipt['id'],info.filename];seen.add((receipt['id'],info.filename));ck(len(member)==meta['bytes'] and sha(member)==meta['sha256'] and info.CRC==meta['crc'],'every original ZIP member/role')
  if info.is_dir() or '__MACOSX' in info.filename:continue
  lines=member.splitlines(keepends=True);width=len(lines[0].rstrip(b'\r\n'));ck(width in [101,263],'literal fixed-width original');prefix=[];offset=0;view='setup' if 'setup' in info.filename else 'nested_results' if '/' in info.filename else 'root'
  for line_no,rawline in enumerate(lines,1):
   content=rawline.rstrip(b'\r\n');ck(len(content)==width and content[:101].isdigit(),'full original byte width/prefix');prefix.append(content[:101])
   if width==263:
    f={name:content[a:b].decode('ascii') for name,a,b in fields};v=[int(content[a:a+6]) for a in range(11,101,6)];ck(v[0]==sum(v[1:]),'total equals all14slots');r=json.loads(next(all_saved));ck(r['source_id']==receipt['id'] and r['member']==info.filename and r['line']==line_no and r['byte_offset']==offset and r['raw_line']==rawline.decode('ascii'),'all long view exact source positions/bytes');ck(r['fields']==f and r['key']==receipt['raw_sha256']+':'+info.filename+':'+str(offset),'all complete literal long fields/key');long_n+=1
    title=f['contest_title'].strip()
    if view=='root' and title in ['Senator in Congress','Presidential Electors For:','Governor']:
     ck(json.loads(next(selected_saved))==r,'every full selected-root original object');selected_n+=1;root_years[year,title]+=1;totals[year,title][f['candidate'],f['party'],f['candidate_name']]+=v[0]
     if year=='2024' and title=='Senator in Congress':
      code=f['reporting_code'];sen[code]=sen.get(code,0)+v[0]
      if code not in anchors:anchors[code]=(offset,r['key'],line_no)
   offset+=len(rawline)
  ck(offset==len(member),'entire member record consumption');prefixes[year,view,width]=prefix
ck(next(all_saved,None) is None and next(selected_saved,None) is None,'no omitted/additional derived original rows');ck(seen==set(im),'complete all6ZIP member inventory')
for year in ['2020','2022','2024']:
 for view in ['root','nested_results','setup']:ck(prefixes[year,view,101]==prefixes[year,view,263],'complete short/long view equality')
rank=sorted(sen,key=lambda k:(-sen[k],anchors[k][0]));ck(len(rank)==458 and sum(sen.values())==491948,'finer all458/state candidate denominator');c=load(T/'priority-set.json');ck(len(c['complete_descending_order'])==458 and len(c['all_source_native_constituents'])==497,'complete source/native inventory');cum=0
for i,(code,r) in enumerate(zip(rank,c['complete_descending_order']),1):
 cum+=sen[code];off,key,line=anchors[code];ck((r['rank'],r['native_code'],r['votes'],r['cumulative_votes'],r['key'])==(i,code,sen[code],cum,key),'complete independent finer order/cumulative/sourceanchor');ck(r['source_anchor']['byte_offset']==off and r['source_anchor']['line']==line,'original source anchor tuple')
k=next(i for i in range(1,459) if sum(sen[x] for x in rank[:i])*5>=491948*4);ck(k==242 and sum(sen[x] for x in rank[:241])==393066 and sum(sen[x] for x in rank[:242])==394072,'integer minimum80 crossing');ck(rank[241]=='0804' and sen['0804']==1006 and anchors['0804'][0]==1075900,'literal crossing source position');ck(c['ordered_priority_keys']==[anchors[x][1] for x in rank[:242]],'all exact ordered priority keys');ck(c['top15']['top15_votes']==sum(sen[x] for x in rank[:15])==34697,'top15 sourceknown');ck(sum(v==0 for v in sen.values())==15,'observed zero not unavailable')
result={'status':'pass_independent_original_first_native_source_review','checks':N,'MF_owned_entries':361,'full_witness_bodies':len(w['frozen_bodies']),'immutable_original_bodies':len(w['immutable_original_references']),'complete_ZIP_members':len(seen),'all_long_original_records':long_n,'all_long_literal_field_values':long_n*len(fields),'complete_selected_root_candidate_records':selected_n,'selected_contest_root_rows':{'|'.join(k):v for k,v in root_years.items()},'unique_selected_candidate_identities':sum(len(v) for v in totals.values()),'all_native_primary':458,'all_inventory':497,'top15':34697,'primary_source_votes':491948,'minimum80':242,'preceding_votes':393066,'priority_votes':394072,'crossing_code':'0804','crossing_votes':1006,'remainder_contexts':216,'remainder_votes':97876,'zero_published_Senate':15,'native_missing_Senate_cases':39,'peer_or_coordinator_priority_accepted':False,'scope':'Raw all-view fixedwidth/header-party-field preservation, original byte-position keys, complete finer order and immutablebody seal. Board/workbook/municipal/statistical controls separately retained and producer verified; no legalwritein/currentgeo/live approval.'}
(S/'data/coordinator-turnout-original-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
