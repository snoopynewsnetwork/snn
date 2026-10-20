"""Independent positional extraction. Reads every byte of every original ZIP member.
All views retained, root chosen only later by control agreement. No coordinator parser.
"""
import io,zipfile,collections,json
from common import *
FIELDS=[('contest',0,4),('candidate',4,7),('reporting_code',7,11),('total',11,17)]+[(f'group_{i}',17+6*(i-1),23+6*(i-1)) for i in range(1,15)]+[('party',101,104),('district_type',104,107),('district_code',107,111),('contest_title',111,167),('candidate_name',167,205),('reporting_name',205,235),('district_name',235,260),('votes_allowed',260,262),('referendum_flag',262,263)]
def extract():
    inventory=[]; rows=[]; prefixes={}
    for r in inputs():
        b=original(r)
        if not b.startswith(b'PK'):continue
        z=zipfile.ZipFile(io.BytesIO(b)); assert z.testzip() is None
        for info in z.infolist():
            member=z.read(info)
            meta=dict(source_id=r['id'],archive_raw_sha256=sha(b),member=info.filename,bytes=len(member),sha256=sha(member),crc=info.CRC,zip_clock=info.date_time)
            inventory.append(meta)
            if '__MACOSX' in info.filename or info.is_dir():continue
            lines=member.splitlines(keepends=True);long=len(lines[0].rstrip(b'\r\n'))==263
            seq=[];offset=0
            for i,line in enumerate(lines,1):
                content=line.rstrip(b'\r\n'); assert len(content)==(263 if long else 101)
                assert content[:101].isdigit()
                seq.append(content[:101])
                if long:
                    f={k:content[a:b].decode('ascii') for k,a,b in FIELDS}
                    assert int(f['total'])==sum(int(f['group_'+str(j)]) for j in range(1,15))
                    rows.append(dict(key=f"{r['raw_sha256']}:{info.filename}:{offset}",source_id=r['id'],member=info.filename,line=i,byte_offset=offset,raw_line=line.decode('ascii'),fields=f))
                offset+=len(line)
            meta['records']=len(seq);meta['numeric_prefix_sha256']=sha(b'\n'.join(seq));prefixes[(r['id'],info.filename)]=seq
    # Pair by year and member view, independently of archive timestamp.
    comparisons=[]
    for y in ['2020','2022','2024']:
        ms=[m for m in inventory if y in m['source_id'] and 'records'in m]
        for a in ms:
            for b in ms:
                if a['source_id']==b['source_id'] or len(prefixes[(a['source_id'],a['member'])][0])!=101:continue
                if a['member'].lower().count('/')!=b['member'].lower().count('/'):continue
                if ('setup' in a['member'])!=('setup' in b['member']):continue
                comparisons.append(dict(year=y,a=[a['source_id'],a['member']],b=[b['source_id'],b['member']],equal=prefixes[(a['source_id'],a['member'])]==prefixes[(b['source_id'],b['member'])]))
    dump(ROOT/'source/zip-members.json',inventory);dump(ROOT/'extracts/short-long-comparisons.json',comparisons)
    gzwrite(ROOT/'extracts/all-long-rows.jsonl.gz',b''.join((json.dumps(r,separators=(',',':'))+'\n').encode() for r in rows))
    dump(ROOT/'source/field-layout.json',[dict(name=k,start_1=a+1,end_1=b) for k,a,b in FIELDS])
    selected=[r for r in rows if '/' not in r['member'] and r['fields']['contest_title'].strip() in ['Senator in Congress','Presidential Electors For:','Governor']]
    gzwrite(ROOT/'extracts/selected-root-rows.jsonl.gz',b''.join((json.dumps(r,separators=(',',':'))+'\n').encode() for r in selected))
    for year in ['2020','2022','2024']:
        s=[r for r in selected if year in r['source_id']]
        c=collections.defaultdict(lambda:[0]*15)
        for r in s:
            f=r['fields'];v=[int(f['total'])]+[int(f['group_'+str(i)]) for i in range(1,15)];k=(f['contest'],f['contest_title'].strip(),f['candidate'],f['party'],f['candidate_name'])
            c[k]=[a+b for a,b in zip(c[k],v)]
        print(year,[(k,v[:4]) for k,v in c.items()])
if __name__=='__main__':extract()
