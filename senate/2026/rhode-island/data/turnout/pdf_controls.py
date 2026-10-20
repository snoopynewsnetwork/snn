"""Reproducible Poppler extraction and publication-scoped controls; no guessed residuals."""
import subprocess,re
from common import *
from acquire import allreceipts
def run():
    out=[];rs=allreceipts()
    for rid in ['ri-2022-description','ri-2020-observed-format-description']:
        r=next(r for r in rs if r['id']==rid)
        text=subprocess.run(['pdftotext','-layout','-','-'],input=original(r),capture_output=True,check=True).stdout
        (ROOT/f'source/{rid}.txt').write_bytes(text)
    for year in ['2024','2022','2020']:
        rid='boe-2024-summary' if year=='2024' else f'board{year}-pdf'
        r=next(r for r in rs if r['id']==rid);b=original(r)
        # Poppler reads stdin; no second stored original PDF.
        text=subprocess.run(['pdftotext','-layout','-','-'],input=b,capture_output=True,check=True).stdout
        gzwrite(ROOT/f'source/board-{year}-summary.layout.txt.gz',text)
        contest='STATISTICS'
        for pi,page in enumerate(text.decode().split('\f'),1):
            if pi>2:break
            for li,line in enumerate(page.splitlines(),1):
                cl=clean(line)
                if cl in ['Presidential Electors For:','Senator in Congress','Governor']:contest=cl
                if cl.startswith('Representative in Congress'):contest='unrelated'
                if contest=='unrelated':continue
                m=re.match(r'^\s*(.*?)\s{2,}([\d,]+)\s+(?:((?:\d+)?\.\d+)%?\s+)?([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$',line)
                if m:
                    label=m[1];values=[int(m[i].replace(',','')) for i in [2,4,5,6]]
                    if 'PRECINCT' in label:continue
                    out.append(dict(year=year,source_id=rid,source_raw_sha256=sha(b),page=pi,line=li,raw_line=line,label=label,contest=contest,values=values,percentage=m[3]))
                elif 'Registered Voters - Total' in line or 'REGISTERED VOTERS - TOTAL' in line:
                    nums=re.findall(r'\d[\d,]*',line);assert len(nums)==1
                    out.append(dict(year=year,source_id=rid,source_raw_sha256=sha(b),page=pi,line=li,raw_line=line,label='Registered Voters - Total',contest='STATISTICS',values=[int(nums[0].replace(',',''))]))
    dump(ROOT/'extracts/pdf-controls.json',out)
    print([(r['year'],r['contest'],r['label'],r['values']) for r in out])
if __name__=='__main__':run()
