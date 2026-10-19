"""Coordinator fresh original OOXML replay; no producer imports or vote inputs."""
from pathlib import Path
from collections import defaultdict
import csv,gzip,hashlib,io,json,posixpath,re,zipfile
from xml.etree import ElementTree as E
D=Path(__file__).resolve().parent;S=D.parent;T=D/'turnout';N=D/'news';M='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}';R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def freeze(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
def main():
 news={r['id']:r for r in json.loads((N/'manifest.json').read_bytes())};sources={};books={};members={}
 cpath=T/'source/census-counties2020.body.gz';a=json.loads((T/'source/census-counties2020.receipt.json').read_bytes());z=cpath.read_bytes();raw=gzip.decompress(z);assert sha(z)==a['stored_sha256']and sha(raw)==a['raw_sha256']
 counties={r['COUNTYNAME'].removesuffix(' County').casefold():r['STATEFP']+r['COUNTYFP']for r in csv.DictReader(io.StringIO(raw.decode()),delimiter='|')if r['STATE']=='SD'};assert len(counties)==66
 for year in [2024,2022,2020]:
  if year==2024:
   receipt=news['sos-2024-public-presidential-precinct-export-684'];p=N/receipt['asset'];n=receipt['bytes']
  else:
   receipt=json.loads((T/f'source/public-native-senate-{year}.receipt.json').read_bytes());p=T/'source'/receipt['asset'];n=receipt['raw_bytes']
  z=p.read_bytes();raw=gzip.decompress(z);assert len(raw)==n and sha(raw)==receipt['raw_sha256']and sha(z)==receipt['stored_sha256'];sources[str(year)]=dict(receipt=receipt,exact_stored_original=pin(p));zf=zipfile.ZipFile(io.BytesIO(raw));assert zf.testzip()is None
  members[str(year)]=[dict(name=i.filename,bytes=i.file_size,CRC32=i.CRC,sha256=sha(zf.read(i.filename)))for i in zf.infolist()]
  strings=[''.join(si.itertext())for si in E.fromstring(zf.read('xl/sharedStrings.xml')).findall(M+'si')];rels={x.get('Id'):x.get('Target')for x in E.fromstring(zf.read('xl/_rels/workbook.xml.rels'))};units=[];footers={};headers={}
  sheets=E.fromstring(zf.read('xl/workbook.xml')).find(M+'sheets');assert len(sheets)==66
  for ordinal,sheet in enumerate(sheets,1):
   literal=sheet.get('name');fips=counties[literal.casefold()];target=rels[sheet.get(R)];target=target.lstrip('/')if target.startswith('/')else posixpath.normpath('xl/'+target);rows={}
   for row in E.fromstring(zf.read(target)).find(M+'sheetData'):
    values={}
    for cell in row.findall(M+'c'):
     v=cell.find(M+'v');value=v.text if v is not None else None
     if cell.get('t')=='s':value=strings[int(value)]
     elif cell.get('t')=='inlineStr':value=''.join(cell.find(M+'is').itertext())
     values[re.sub(r'\d+$','',cell.get('r'))]=dict(value=value,type=cell.get('t'),address=cell.get('r'))
    rows[int(row.get('r'))]=values
   head=rows[7];cols=list('CDEF')[:4 if year==2024 else 3 if year==2022 else 2];headers[literal]=[head[k]['value']for k in cols];assert head['B']['value']=='Precinct'
   end=next(i for i,r in rows.items()if r.get('B',{}).get('value')=='TOTALS');values=[]
   for i,r in rows.items():
    if not 7<i<end:continue
    vector=[]
    for col in cols:
     f=r[col];assert f['type']=='n'and re.fullmatch(r'\d+',f['value']);vector.append(int(f['value']))
    assert isinstance(r['B']['value'],str)and r['B']['value'];key=f'sd:2024:pres:{fips}:sheet{ordinal}:row{i}'if year==2024 else f'sd:{year}:senate:{fips}:public-sheet{ordinal}:row{i}'
    unit=dict(key=key,county_literal=literal,county_fips=fips,worksheet_ordinal=ordinal,worksheet_member=target,source_row=i,native_label_literal=r['B']['value'],candidate_headers=headers[literal],candidate_values=vector,candidate_cell_addresses=[r[col]['address']for col in cols],contest_votes=sum(vector));units.append(unit);values.append(vector)
   footer=[int(rows[end][col]['value'])for col in cols];assert [sum(v[j]for v in values)for j in range(len(cols))]==footer;footers[literal]=footer
  assert len(units)=={2024:691,2022:687,2020:693}[year];assert len({u['key']for u in units})==len(units)
  assert all(h==next(iter(headers.values()))for h in headers.values());total=[sum(v[j]for v in footers.values())for j in range(len(cols))];books[str(year)]=dict(headers=next(iter(headers.values())),totals=total,county_footers=footers,units=units)
 assert books['2024']['totals']==[146811,2777,271938,7202]
 assert books['2022']['totals']==[91007,14697,242316]
 # Read signed county controls from the independently original-reconciled coordinator preflight.
 signed=json.loads((D/'coordinator-primary-preflight.json').read_bytes())['tables'];deltas={}
 for year,key in [('2024','2024_President'),('2022','2022_Senate_other_ClassIII'),('2020','2020_Senate_same_ClassII')]:
  official=signed[key];headers=books[year]['headers'];expected_names=['Kamala','Chase','Donald','Robert']if year=='2024'else ['Brian','Tamara','John']if year=='2022'else ['Mike','Dan']
  # Bind by original candidate names, never by matching numerical counts.
  if year=='2020':
   assert len(headers)==2
   rounds=next(i for i,h in enumerate(headers)if'Mike Rounds'in h);ahlers=next(i for i,h in enumerate(headers)if'Ahlers'in h);order=[rounds,ahlers]
  else:order=list(range(len(headers)))
  dc={c:[books[year]['county_footers'][c][order[j]]-r['votes'][j]for j in range(len(order))]for c,r in official['rows'].items()};deltas[year]=dict(candidate_public_minus_signed=[sum(v[j]for v in dc.values())for j in range(len(order))],county_differences={c:v for c,v in dc.items()if any(v)})
 assert deltas['2024']['candidate_public_minus_signed']==[-48,-1,-143,-2]and len(deltas['2024']['county_differences'])==24
 assert deltas['2022']['county_differences']=={}
 assert deltas['2020']['candidate_public_minus_signed']==[-24,-17]and len(deltas['2020']['county_differences'])==21
 units=sorted(books['2024']['units'],key=lambda u:(-u['contest_votes'],u['county_fips'],u['worksheet_ordinal'],u['source_row']));assert sum(u['contest_votes']for u in units[:15])==61003
 assert sum(u['contest_votes']for u in units[:303])==342947 and sum(u['contest_votes']for u in units[:304])==343402 and units[303]['key']=='sd:2024:pres:46057:sheet32:row14'
 assert 5*342947<4*428728<=5*343402
 # Scope audit only: no original extraction depends on this working peer body.
 p=T/'priority-set.json';body=p.read_bytes();peer=json.loads(body);assert peer['complete_ordered_keys']==[u['key']for u in units]
 pi={r['key']:r for r in peer['all_units']};assert len(pi)==691
 for u in units:
  r=pi[u['key']];assert r['native_label_literal']==u['native_label_literal']and r['county_literal']==u['county_literal']and list(r['candidate_votes'].values())==u['candidate_values']and r['contest_votes']==u['contest_votes']
 qa=D/'coordinator-qa/initial-public-native-v1';freeze(qa/'turnout-contract-at-review.json.gz',gzip.compress(body,mtime=0));freeze(qa/'original-derived-three-books.json.gz',gzip.compress((json.dumps(books,indent=2)+'\n').encode(),mtime=0))
 out=dict(status='pass_independent_original_public_native_scope_not_signed_priority_acceptance',source_originals=sources,complete_ZIP_members=members,native_counts=dict(year2024=691,year2022=687,year2020=693),source_candidate_headers={y:b['headers']for y,b in books.items()},source_candidate_totals={y:b['totals']for y,b in books.items()},signed_source_discrepancies=deltas,public_primary=dict(denominator=428728,top15=61003,minimum80=304,votes=343402,preceding303=342947,crossing=units[303],remainder387=85326,priority_parents=len({u['county_fips']for u in units[:304]})),certified_robustness=dict(signed_denominator=428922,signed_integer_target=343138,source_integer_target=342983,first303_signed_target_deficit=191,total_source_deficit194_unallocated=True,certified_minimum_or_membership_proven=False),original_derived_transcript=pin(qa/'original-derived-three-books.json.gz'),working_peer_snapshot=pin(qa/'turnout-contract-at-review.json.gz'),qualification='No producer imports/vote inputs. Direct original XML, celltypes/positions, allcandidate headers and source footers re-read independently; registered Census county codes applied by literal county names with casefold only. 2024 named-four public ranking is not certified native membership; no unknown-vote allocation/current joins. This bounded working-contract comparison is not final peer freeze or historical dispatch acceptance.')
 p=D/'coordinator-initial-public-native-review.json';freeze(p,(json.dumps(out,indent=2)+'\n').encode());print(json.dumps(pin(p)))
if __name__=='__main__':main()
