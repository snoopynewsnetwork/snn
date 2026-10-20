#!/usr/bin/env python3
"""Independent original-first extraction. No peer numerical/parser inputs.
Requires xlrd==2.0.2; original ZIP bodies remain stored once in ../turnout.
"""
import csv, gzip, hashlib, io, json, pathlib, shutil, struct, sys, zipfile
import xlrd
from urllib.parse import quote

BASE = pathlib.Path(__file__).resolve().parent
STATE = BASE.parent.parent
HTTP = STATE/'data/turnout/source/http'
HASHES = {2024:'4ecca55fc235018aeb2385debd375e6fa7aaa553c5bd67786add08d850efcc96',2022:'4ea186b9e9eefa7786b3708b8ffd2da5755a9ba5c018b4ff9d47a2ceec46983a',2020:'471fc54cfc87984c8e6325c4baef6933545044cd6482a153c234b97f74d4693d'}
def sha(b): return hashlib.sha256(b).hexdigest()
def save(name,obj):
    p=BASE/name; p.parent.mkdir(parents=True,exist_ok=True)
    b=(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def load_original(h):
    rp=next(p for p in HTTP.glob('*.receipt.json') if json.loads(p.read_text())['original_sha256']==h)
    d=json.loads(rp.read_text()); chunks=[]
    for part in d['parts']:
        p=HTTP.parent.parent/part['path']; b=p.read_bytes()
        assert sha(b)==part['sha256'] and len(b)==part['bytes']; chunks.append(b)
    b=gzip.decompress(b''.join(chunks)); assert sha(b)==h and len(b)==d['original_bytes']
    dst=BASE/'source/receipts'/rp.name; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(rp,dst)
    return b,{'receipt':str(dst.relative_to(BASE)),'receipt_sha256':sha(dst.read_bytes()),'metadata':d,'shared_root':'../turnout','original_sha256':h}
def num(cell):
    t,v=cell
    if t==2:
        assert v>=0 and v==int(v)
        return int(v)
    return None
def complete_sum(values): return sum(values) if all(v is not None for v in values) else None
def rank(rows):
    ordered=sorted(rows,key=lambda u:(-u['reported_contest_votes'],u['key']))
    total=sum(u['reported_contest_votes'] for u in ordered); cum=0; crossing=None
    out=[]
    for i,u in enumerate(ordered,1):
        cum+=u['reported_contest_votes']
        out.append({'rank':i,'key':u['key'],'county_fips':u['county_fips'],'votes':u['reported_contest_votes'],'cumulative_votes':cum})
        if crossing is None and 5*cum>=4*total: crossing=i
    return {'total':total,'threshold_integer':(4*total+4)//5,'minimum80_count':crossing,'top15_votes':sum(u['reported_contest_votes'] for u in ordered[:15]),'full_order':out,'priority_keys':[u['key'] for u in ordered[:crossing]],'remainder_keys':[u['key'] for u in ordered[crossing:]],'all67_parents':sorted(set(u['county_fips'] for u in rows))}
def main():
    census,ref=load_original('9f6e5f6eb6ac2f5e9a36d5fd01dec77991bddc75118f748a069441a4782970d6')
    fips={r['COUNTYNAME'].removesuffix(' County'):r['STATEFP']+r['COUNTYFP'] for r in csv.DictReader(io.StringIO(census.decode()),delimiter='|') if r['STATE']=='AL'}
    # Explicit source-identity spelling mapping, not a precinct crosswalk.
    refs=[ref]; books=[]; natives=[]; counties=[]; inventories=[]
    for year,h in HASHES.items():
        raw,ref=load_original(h); refs.append(ref); z=zipfile.ZipFile(io.BytesIO(raw))
        assert z.testzip() is None and len(z.infolist())==67
        for zi in z.infolist():
            body=z.read(zi); county=zi.filename.removeprefix(f'{year}-General-').removesuffix('.xls')
            census_name={'StClair':'St. Clair','St_Clair':'St. Clair','St. Clair':'St. Clair','Saint Clair':'St. Clair'}.get(county,county)
            cf=fips[census_name]
            wb=xlrd.open_workbook(file_contents=body,formatting_info=True)
            # All formula records retained positionally, including raw RPN bytes.
            cd=xlrd.compdoc.CompDoc(body); stream=cd.get_named_stream('Workbook') or cd.get_named_stream('Book')
            formulas=[]; pos=0
            while pos+4<=len(stream):
                op,size=struct.unpack_from('<HH',stream,pos); payload=stream[pos+4:pos+4+size]
                if op==6:
                    r,c=struct.unpack_from('<HH',payload); formulas.append({'stream_offset':pos,'row':r+1,'column':c+1,'payload_hex':payload.hex()})
                pos+=4+size
            ob={'year':year,'county':county,'county_fips':cf,'zip_sha256':h,'member':zi.filename,'member_sha256':sha(body),'member_bytes':len(body),'zip_crc32':zi.CRC,'zip_timestamp':list(zi.date_time),'formulas':formulas,'sheets':[]}
            for s in wb.sheets():
                def cell(r,c):
                    x=s.cell(r,c);return [x.ctype,x.value]
                cols=[c for c in range(3,s.ncols) if s.cell_value(0,c)!='']
                assert all(isinstance(s.cell_value(0,c),str) and s.cell_value(0,c).strip() for c in cols)
                selected=[]; desc=[]; ignored_nonblank=[]
                for r in range(s.nrows):
                    t=str(s.cell_value(r,0)).strip(); n=str(s.cell_value(r,2)).strip()
                    desc.append({'row':r+1,'cells':[cell(r,c) for c in range(3)]})
                    relevant=(year==2024 and t=='PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES') or (year!=2024 and t=='UNITED STATES SENATOR')
                    admin=t.startswith(('REGISTERED VOTERS','BALLOTS CAST','STRAIGHT PARTY'))
                    if r==0 or relevant or admin:
                        selected.append({'row':r+1,'role':'header' if r==0 else ('contest' if relevant else 'admin'),'cells':[cell(r,c) for c in range(s.ncols)]})
                        if r>0:
                            ignored_nonblank.extend([{'row':r+1,'column':c+1,'cell':cell(r,c)} for c in range(3,s.ncols) if c not in cols and cell(r,c)[0] not in (0,6)])
                assert not ignored_nonblank
                sh={'name':s.name,'nrows':s.nrows,'ncols':s.ncols,'merged_cells':s.merged_cells,'native_columns_1based':[c+1 for c in cols],'row_descriptors':desc,'selected_rows':selected,'unheaded_selected_values':ignored_nonblank}
                ob['sheets'].append(sh)
                candidates=[row for row in selected if row['role']=='contest' and row['cells'][2][1].strip() not in ('Over Votes','Under Votes')]
                assert len(candidates)=={2024:6,2022:4,2020:3}[year]
                units=[]
                for c in cols:
                    literal=s.cell_value(0,c); key=f'AL:{year}:general:{cf}:col{c+1:03d}:'+quote(literal,safe='')
                    cr=[{'source_row':r['row'],'contest_literal':r['cells'][0][1],'party_literal':r['cells'][1][1],'candidate_literal':r['cells'][2][1],'cell':r['cells'][c],'votes':num(r['cells'][c])} for r in candidates]
                    ad=[{'source_row':r['row'],'contest_literal':r['cells'][0][1],'field_literal':r['cells'][2][1],'cell':r['cells'][c],'value':num(r['cells'][c])} for r in selected if r['role']=='admin' or (r['role']=='contest' and r['cells'][2][1].strip() in ('Over Votes','Under Votes'))]
                    vals=[x['votes'] for x in cr]
                    u={'key':key,'year':year,'county':county,'county_fips':cf,'member':zi.filename,'member_sha256':sha(body),'zip_sha256':h,'sheet':s.name,'source_column':c+1,'native_header_literal':literal,'candidate_rows':cr,'administrative_rows':ad,'reported_contest_votes':sum(x for x in vals if x is not None),'complete_contest_votes':complete_sum(vals),'unknown_candidate_cells':sum(x is None for x in vals),'method_scope':'literal source header only; physical geometry and exclusive voting method unverified'}
                    units.append(u);natives.append(u)
                ca=[]
                for i,r in enumerate(candidates):
                    vals=[u['candidate_rows'][i]['votes'] for u in units]
                    ca.append({'source_row':r['row'],'candidate_literal':r['cells'][2][1],'party_literal':r['cells'][1][1],'votes':complete_sum(vals),'reported_sum':sum(x for x in vals if x is not None),'unknown_cells':sum(x is None for x in vals)})
                admins=[]
                for i,a in enumerate(units[0]['administrative_rows']):
                    vals=[u['administrative_rows'][i]['value'] for u in units]
                    admins.append({**{k:a[k] for k in ['source_row','contest_literal','field_literal']},'complete_sum':complete_sum(vals),'reported_sum':sum(x for x in vals if x is not None),'unknown_cells':sum(x is None for x in vals)})
                counties.append({'key':f'AL:{year}:general:{cf}:county','year':year,'county':county,'county_fips':cf,'member':zi.filename,'member_sha256':sha(body),'native_count':len(units),'candidate_rows':ca,'administrative_rows':admins,'reported_contest_votes':sum(u['reported_contest_votes'] for u in units),'complete_contest_votes':complete_sum([u['complete_contest_votes'] for u in units])})
            books.append(ob)
        nr=[u for u in natives if u['year']==year]; co=[u for u in counties if u['year']==year]
        assert len(co)==67 and len({u['key'] for u in nr})==len(nr)
        labels=[r['candidate_literal'].strip() for r in co[0]['candidate_rows']]
        assert all(len({r['candidate_literal'].strip() for r in c['candidate_rows']})==len(labels) for c in co)
        inventories.append({'year':year,'native':rank(nr),'county':rank(co),'native_count':len(nr),'candidate_controls':[{ 'candidate':label,'sum':sum(next(r for r in c['candidate_rows'] if r['candidate_literal'].strip()==label)['reported_sum'] for c in co),'unknown_cells':sum(next(r for r in c['candidate_rows'] if r['candidate_literal'].strip()==label)['unknown_cells'] for c in co)} for label in labels]})
    save('source/original-references.json',refs)
    save('source/typed-workbooks.json.gz',books)
    save('source/native-observations.json.gz',natives)
    save('source/county-observations.json',counties)
    save('source/independent-inventory.json',inventories)
    # Freeze hashes before any read of peer derivative evidence.
    witness={'phase':'v3: correct own statewide inventory grouping to literal candidate identity, after original Jefferson reread; v2 expanded administrative raw scope to STRAIGHT PARTY; all prior versions retained. v1 original-first archive predates peer read. No peer numbers/parser/order adopted.','xlrd_version':xlrd.__version__,'source_identity_mapping':'ZIP member county identity to literal Census county; St. Clair spelling only','files':[]}
    for p in sorted((BASE/'source').rglob('*')):
        if p.is_file() and (p.name in ('original-references.json','typed-workbooks.json.gz','native-observations.json.gz','county-observations.json','independent-inventory.json') or (p.parent.name=='receipts' and p.name in [pathlib.Path(r['receipt']).name for r in refs])):witness['files'].append({'path':str(p.relative_to(BASE)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size})
    save('source/original-first-witness.json',witness)
    print(json.dumps([{ 'year':i['year'],'native_count':i['native_count'],'native80':i['native']['minimum80_count'],'county80':i['county']['minimum80_count'],'total':i['native']['total'],'candidate_controls':i['candidate_controls']} for i in inventories],indent=2))
if __name__=='__main__': main()
