"""Independent complete original 2024 candidate-label/cell review using xlrd2.0.2.

Run with a separate Python environment containing xlrd==2.0.2. No producer
parser, typed derivative or peer count input is read. No package is kept here.
"""
from pathlib import Path
from collections import Counter
import gzip, hashlib, io, json, zipfile
import xlrd

S=Path(__file__).resolve().parents[1]
original='4ecca55fc235018aeb2385debd375e6fa7aaa553c5bd67786add08d850efcc96'
p=S/'data/turnout/source/http'/(original+'.gz')
raw=gzip.decompress(p.read_bytes())
assert hashlib.sha256(raw).hexdigest()==original and xlrd.__version__=='2.0.2'
z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
totals=Counter();members=[]
names=['Kamala D. Harris','Donald J. Trump','Robert F. Kennedy Jr.','Chase Oliver','Jill Stein','Write-In']
for info in z.infolist():
    b=z.read(info);book=xlrd.open_workbook(file_contents=b,formatting_info=True);sheet=book.sheet_by_index(0)
    headers=[(c,sheet.cell_value(0,c)) for c in range(3,sheet.ncols) if sheet.cell_value(0,c)!=''];records=[]
    for r in range(1,sheet.nrows):
        contest=sheet.cell_value(r,0);candidate=sheet.cell_value(r,2)
        if not isinstance(contest,str) or contest.strip()!='PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES' or not isinstance(candidate,str) or candidate.strip() not in names:
            continue
        cells=[dict(column1=c+1,header_literal=v,type=sheet.cell_type(r,c),value=sheet.cell_value(r,c)) for c,v in headers]
        assert all(c['type']==xlrd.XL_CELL_NUMBER for c in cells)
        n=sum(c['value'] for c in cells);assert n==int(n)
        totals[candidate.strip()]+=int(n)
        records.append(dict(row1=r+1,candidate_literal=candidate,party_literal=sheet.cell_value(r,1),contest_literal=contest,sum=int(n),cells=cells))
    assert len(records)==6
    members.append(dict(member=info.filename,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),CRC32=f'{info.CRC:08x}',native_columns=len(headers),candidate_rows=records))
assert len(members)==67
out=dict(status='independent_original_xlrd_2024_candidate_labels_values_no_imputation',reader='xlrd2.0.2 in /tmp/snn-coordinator-xls-review only, no repo dependency/cache',original_ZIP_raw_sha256=original,whole_members=members,statewide_literal_label_sums=dict(totals),reported_candidate_generic_total=sum(totals.values()),native_columns=sum(r['native_columns'] for r in members),source_or_peer_mutation=False,canvass_concordance_not_assumed=True)
d=S/'data/coordinator-candidate-scope-review';d.mkdir(exist_ok=True)
b=(json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode()
f=d/'2024-original-native-candidate-cells.json.gz'
if f.exists():assert gzip.decompress(f.read_bytes())==b
else:f.write_bytes(gzip.compress(b,mtime=0))
summary={k:v for k,v in out.items() if k!='whole_members'}
expected=(json.dumps(summary,indent=2)+'\n').encode()
if (d/'native-sums.json').exists():assert (d/'native-sums.json').read_bytes()==expected
else:(d/'native-sums.json').write_bytes(expected)
print(json.dumps(summary))
