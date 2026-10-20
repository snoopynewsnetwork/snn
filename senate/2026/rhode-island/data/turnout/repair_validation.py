"""Original OOXML detail, historical reconstruction and bounded repair fixtures."""
import io,gzip,zipfile,tarfile,xml.etree.ElementTree as E,re,json,copy
from common import *
def historical():
    base=ROOT/'history/pre-repair-v1';c=json.loads((base/'capture.json').read_text());b=(base/c['archive']['path']).read_bytes();assert sha(b)==c['archive']['sha256'];raw=gzip.decompress(b);assert sha(raw)==c['archive']['tar_sha256'];t=tarfile.open(fileobj=io.BytesIO(raw));refs={x['path']:x for x in c['immutable_original_refs']};allold={}
    for item in c['all362']:
        data=(STATE/item['path']).read_bytes()if item['path']in refs else t.extractfile(item['path']).read();assert sha(data)==item['sha256']and len(data)==item['bytes'];allold[item['path']]=data
    old=json.loads(allold['data/turnout/asset-manifest.json']);assert sha(allold['data/turnout/asset-manifest.json'])=='52015c24dd3702f0a5678947ac4262fd5ad19b3a23601ee8d62795e1f9943f9f'
    assert len(allold)==362 and len(old['owned_assets'])==361
    for item in old['owned_assets']:
        data=allold[item['path']];assert sha(data)==item['sha256']and len(data)==item['bytes']
    # Prior227body witness remains exact, reconstructing its historical bodies,
    # including overwritten report/script/summary rather than reading current files.
    w=json.loads(allold['data/turnout/qa/pre-peer-body-witness.json']);assert sha(allold['data/turnout/qa/pre-peer-body-witness.json'])=='a88c8c63384f2de6011a80bd7d50bf225e4c5dbcd312b0e469cb3a5777de99f1';wa=allold['data/turnout/qa/pre-peer-bodies.tar.gz'];assert sha(wa)=='30ef7f528ad0fc42dfa7a382acec7fc687faecbdc74b097fb6359a31f8685eb2'
    with tarfile.open(fileobj=io.BytesIO(gzip.decompress(wa)))as wt:
        for item in w['frozen_bodies']:
            data=wt.extractfile(item['path']).read();assert sha(data)==item['sha256']and len(data)==item['bytes'];assert data==allold[item['path']]
    for item in w['immutable_original_references']:
        data=(STATE/item['path']).read_bytes();assert sha(data)==item['stored_sha256']and sha(gzip.decompress(data))==item['raw_sha256']
    return allold
def original_wi():
    r=json.loads((ROOT/'source/acquired/board2024-writeins-xlsx.receipt.json').read_text());b=original(r);z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip()is None;ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};ss=[''.join(x.itertext())for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)];rel={x.attrib['Id']:x.attrib['Target']for x in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))};expected={}
    for sheet in E.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',ns):
        rid=sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'];path=rel[rid];member=path.lstrip('/')if path.startswith('/')else 'xl/'+path;xml=z.read(member);cells={}
        for cell in E.fromstring(xml).findall('.//m:sheetData/m:row/m:c',ns):
            address=cell.attrib['r']
            if not re.fullmatch('[DE][0-9]+',address):continue
            v=cell.find('m:v',ns);f=cell.find('m:f',ns);raw=None if v is None else v.text;value=ss[int(raw)]if cell.attrib.get('t')=='s'else (raw or '')
            cells[address]=dict(value=value,raw_v=raw,xml_type=cell.attrib.get('t'),formula=None if f is None else f.text,attributes=dict(cell.attrib))
        head=next(int(k[1:])for k,v in cells.items()if k.startswith('D')and v['value']=='U.S. Senator in Congress:');top=min(int(k[1:])for k,v in cells.items()if k.startswith('E')and int(k[1:])>head and re.fullmatch('[0-9]+',v['value'])and not cells.get('D'+k[1:],{}).get('value'))
        admitted=[]
        for k,v in cells.items():
            if not k.startswith('D')or int(k[1:])<=head or int(k[1:])==top:continue
            number=cells.get('E'+k[1:]);label=v['value']
            if label and label.strip().lower()!='total'and number and re.fullmatch('[0-9]+',number['value']):admitted.append(int(k[1:]))
        expected[member]=dict(sheet=sheet.attrib['name'],relationship_id=rid,member_sha256=sha(xml),member_crc=z.getinfo(member).CRC,cells=cells,detail_rows=sorted(admitted),xml=xml,header_row=head,headline_row=top)
    return b,z,expected
def assert_detail(proof):
    b,z,expected=original_wi();assert proof['source_raw_sha256']==sha(b)and proof['source_bytes']==len(b);assert len(proof['sheets'])==39
    sums=[];previous=[];heads=[];count=0
    for s in proof['sheets']:
        e=expected[s['member']];assert s['sheet']==e['sheet']and s['relationship_id']==e['relationship_id']and s['member_sha256']==e['member_sha256']and s['member_crc']==e['member_crc'];assert s['header_row']==e['header_row']and s['headline_row']==e['headline_row'];assert set(s['cells'])==set(e['cells']);assert s['detail_rows']==e['detail_rows']and len(set(s['detail_rows']))==len(s['detail_rows'])
        for address,x in s['cells'].items():
            for field in ['value','raw_v','xml_type','formula','attributes']:assert x[field]==e['cells'][address][field]
            assert e['xml'][x['byte_start']:x['byte_end_exclusive']].decode()==x['raw_xml'];assert E.fromstring(x['raw_xml']).attrib['r']==address;count+=1
        sums.append(sum(int(e['cells']['E'+str(r)]['value'])for r in e['detail_rows']));previous.append(sum(int(e['cells']['E'+str(r)]['value'])for r in e['detail_rows']if r>=6));heads.append(int(e['cells']['E'+str(e['headline_row'])]['value']))
    assert proof['all_literal_cells']==count==1955;assert proof['complete_detail_sum']==sum(sums)==1227 and proof['historical_row6_detail_sum']==sum(previous)==1226 and proof['printed_municipal_total']==sum(heads)==1239
    assert proof['complete_local_discrepancies']==sum(a!=b for a,b in zip(sums,heads))==8 and proof['historical_row6_discrepancies']==sum(a!=b for a,b in zip(previous,heads))==9
    assert proof['eligibility']is None and proof['allocation']is None
    cran=next(s for s in proof['sheets']if s['sheet']=='Cranston');assert cran['relationship_id']=='rId7'and cran['member']=='xl/worksheets/sheet7.xml'and cran['cells']['D5']['value']=='Mario Frioli 'and cran['cells']['E5']['value']=='1'and 5 in cran['detail_rows']
def audit(write=False):
    old=historical();proof=json.loads((ROOT/'extracts/writein-original-detail-proof.json').read_text());assert_detail(proof);tests=[]
    def reject(label,mutation):
        q=copy.deepcopy(proof);mutation(q)
        try:assert_detail(q)
        except (AssertionError,KeyError):tests.append(dict(case=label,rejected=True));return
        raise AssertionError('admitted corrupt detail: '+label)
    def cran(q):return next(s for s in q['sheets']if s['sheet']=='Cranston')
    reject('actual_missing_row5_D5_cell',lambda q:cran(q)['cells'].pop('D5'))
    reject('actual_row5_omission_from_detail_admission',lambda q:cran(q)['detail_rows'].remove(5))
    reject('stale_row6_summary1226',lambda q:q.update(complete_detail_sum=1226,complete_local_discrepancies=9))
    reject('source_body_hash_corruption',lambda q:q.update(source_raw_sha256='0'*64))
    reject('worksheet_member_crc_metadata_corruption',lambda q:cran(q).update(member_crc=0))
    reject('worksheet_relationship_metadata_corruption',lambda q:cran(q).update(relationship_id='rId8'))
    reject('duplicate_source_detail_admission',lambda q:cran(q)['detail_rows'].append(5))
    reject('trailing_space_name_loss',lambda q:cran(q)['cells']['D5'].update(value='Mario Frioli'))
    reject('invented_eligible_writein_admission',lambda q:q.update(eligibility=True))
    reject('source_position_corruption',lambda q:cran(q)['cells']['E5'].update(byte_start=0))
    # Protected source/native/order/CSV/witness bodies must remain byte-exact.
    protected=['data/county-turnout.csv','data/turnout/priority-set.json','data/turnout/native-inventory.json','data/turnout/parent-sensitivity.csv','data/turnout/parent-sensitivity.json','data/turnout/rankings.json','data/turnout/candidate-reconciliation.json','data/turnout/state-controls.json','data/turnout/municipal-controls.json','data/turnout/extracts/selected-root-rows.jsonl.gz','data/turnout/extracts/all-long-rows.jsonl.gz','data/turnout/extracts/2024-senate-writein-cells.json','data/turnout/qa/pre-peer-body-witness.json','data/turnout/qa/pre-peer-bodies.tar.gz']
    for path in protected:assert (STATE/path).read_bytes()==old[path]
    changed=[dict(path=path,old_sha256=sha(b),new_sha256=sha((STATE/path).read_bytes()),old_bytes=len(b),new_bytes=(STATE/path).stat().st_size)for path,b in old.items()if (STATE/path).read_bytes()!=b]
    result=dict(schema='row5-original-detail-repair-audit-v1',status='passed',historical362_and_old361_manifest_targets_verified=True,original227_full_body_witness_and148_originals_unchanged=True,protected_bodies=[dict(path=x,sha256=sha(old[x]),bytes=len(old[x]))for x in protected],source_proof=dict(path='extracts/writein-original-detail-proof.json',sha256=sha((ROOT/'extracts/writein-original-detail-proof.json').read_bytes())),narrow_correction='Original Cranston D5 Mario Frioli trailing space / E5 numeric1 included structurally. Full1227/eight; prior row6-only1226/nine preserved. Printed1239/state generic1244 unchanged.',corruption_tests=tests,changed_prior_bodies_at_audit=changed,peer_baseline_was_not_repaired=True)
    if write:dump(ROOT/'qa/repair-validation.json',result)
    return result
if __name__=='__main__':
    import sys
    x=audit('--write'in sys.argv);print(dict(status=x['status'],tests=len(x['corruption_tests']),protected=len(x['protected_bodies'])))
