"""Independent complete original-member/record/cell checks; no producer code."""
from common import *
from collections import Counter,defaultdict
import zipfile,re,xml.etree.ElementTree as ET

def run():
    counts=Counter();inputs=parsed(S/'data/baselines/source/inputs.json')
    bodies={r['id']:gzip.decompress((S/r['body_path']).read_bytes()) for r in inputs}
    archive_hash={k:sha(v) for k,v in bodies.items()}
    members={};inventories=parsed(S/'data/turnout/source/zip-members.json');groups=defaultdict(list)
    for r in inventories:groups[r['source_id']].append(r)
    for sid,rows in groups.items():
        raw=bodies[sid]
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            assert z.namelist()==[r['member'] for r in rows]
            for r,zi in zip(rows,z.infolist(),strict=True):
                b=z.read(zi);verify(b,dict(path=r['member'],bytes=r['bytes'],sha256=r['sha256']))
                assert zi.CRC==r['crc'] and list(zi.date_time)==r['zip_clock']
                members[sid,r['member']]=b;counts['technical_members']+=1
        counts['technical_archives']+=1
    fields=parsed(S/'data/turnout/source/field-layout.json')
    consumed=defaultdict(int)
    with gzip.open(S/'data/turnout/extracts/all-long-rows.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line);b=members[r['source_id'],r['member']];offset=r['byte_offset']
            rb=r['raw_line'].encode('latin1');assert len(rb)==265 and rb.endswith(b'\r\n')
            assert b[offset:offset+265]==rb and offset==(r['line']-1)*265
            assert r['key']==archive_hash[r['source_id']]+':'+r['member']+':'+str(offset)
            for field in fields:
                assert r['fields'][field['name']]==rb[field['start_1']-1:field['end_1']].decode('latin1')
                counts['literal_field_values']+=1
            consumed[r['source_id'],r['member']]+=len(rb);counts['whole_long_records']+=1
    for key,size in consumed.items():assert size==len(members[key])
    # All root/nested/setup short numeric prefixes independently match their corresponding long bodies.
    shorts={2024:'ri-2024-original-data-zip',2020:'ri-2020-observed-short-zip',2022:'ri-2022-observed-short-zip'}
    for year,sid in shorts.items():
        short=[(k,b) for k,b in members.items() if k[0]==sid and b.endswith(b'\r\n')]
        for key,b in short:
            rows=b.splitlines(keepends=True)
            candidates=[(k,bb) for k,bb in members.items() if str(year) in k[0] and ('layout' in k[0] or 'observed-long' in k[0]) and len(bb)==len(rows)*265]
            matches=[]
            prefix=b''.join(row[:101]+b'\r\n' for row in rows)
            for k,bb in candidates:
                if prefix==b''.join(row[:101]+b'\r\n' for row in bb.splitlines(keepends=True)):matches.append(k)
            assert matches,key
            counts['short_long_complete_view_pairs']+=1
    assert counts['short_long_complete_view_pairs']==9
    # Complete OOXML cell positions/types/styles/formula/value and workbook relationships.
    proof=parsed(S/'data/turnout/extracts/writein-original-detail-proof.json')
    rec=parsed(S/'data/turnout/source/acquired/board2024-writeins-xlsx.receipt.json')
    raw=gzip.decompress((S/'data/turnout'/rec['stored_path']).read_bytes())
    assert len(raw)==proof['source_bytes'] and sha(raw)==proof['source_raw_sha256']
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        strings=[''.join(t.text or '' for t in si.iter('{'+ns['m']+'}t')) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
        wx=z.read('xl/workbook.xml');rels=z.read('xl/_rels/workbook.xml.rels')
        relationships={x.attrib['Id']:x.attrib['Target'] for x in ET.fromstring(rels)}
        sheets={x.attrib['name']:x.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'] for x in ET.fromstring(wx).findall('m:sheets/m:sheet',ns)}
        for sheet in proof['sheets']:
            rid=sheets[sheet['sheet']];assert rid==sheet['relationship_id']
            target=relationships[rid];assert ('xl/'+target.lstrip('/') if not target.startswith('/xl/') else target[1:])==sheet['member']
            b=z.read(sheet['member']);assert sha(b)==sheet['member_sha256'] and z.getinfo(sheet['member']).CRC==sheet['member_crc']
            assert sha(wx)==sheet['workbook_xml_sha256'] and sha(rels)==sheet['relationships_xml_sha256']
            actual={}
            for m in re.finditer(rb'<c\b[^>]*?(?:/>|>.*?</c>)',b):
                cell=ET.fromstring(m.group());addr=cell.attrib.get('r','')
                if not re.fullmatch(r'[DE]\d+',addr):continue
                val=cell.find('v');formula=cell.find('f');rv=val.text if val is not None else None;typ=cell.attrib.get('t')
                value=strings[int(rv)] if typ=='s' and rv is not None else rv or ''
                actual[addr]=dict(value=value,raw_v=rv,formula=formula.text if formula is not None else None,xml_type=typ,byte_start=m.start(),byte_end_exclusive=m.end(),raw_xml=m.group().decode(),attributes=cell.attrib)
            assert actual==sheet['cells'],sheet['sheet']
            counts['whole_writein_cells']+=len(actual);counts['writein_municipal_sheets']+=1
        cranston=next(s for s in proof['sheets'] if s['sheet']=='Cranston')
        assert cranston['cells']['D5']['value']=='Mario Frioli ' and cranston['cells']['E5']['value']=='1'
    assert (proof['complete_detail_sum'],proof['complete_local_discrepancies'],proof['historical_row6_detail_sum'],proof['historical_row6_discrepancies'],proof['printed_municipal_total'])==(1227,8,1226,9,1239)
    return dict(status='pass',counts=dict(counts),scope='All44members/sixarchives; every187401 long record and literal field; short numeric complete views; all1955 write-in D/E cells and workbook relationships. No semantic eligibility or chronology inference.')
if __name__=='__main__':
    import sys
    result=run()
    if '--write' in sys.argv:write(R/'qa/original-audit.json',dump(result))
    print(json.dumps(result))
