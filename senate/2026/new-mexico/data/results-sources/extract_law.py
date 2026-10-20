"""Whole public PDF text and exact bounded operative sections; no network."""
from acquire import *
import subprocess,tempfile
NAMES=['handbook-2025','law-2025-index','law-2026-summary','otero-signed-order','law-2025-sb16-final','law-2026-sb264-final','law-2026-sb73-final','county-09-official2024','nm-elections-code-frame-pdf','nm-state-constitution-frame-pdf','nm-us-constitution-frame-pdf','court-2026-election-judges','general-proclamation','nmac-canvass-proposed','dona-general-sample','otero-general-sample']
TERMS=['1-1-24','1-4-8','1-4-5.7','1-6-5','1-6-5.6','1-6-5.7','1-6-8','1-6-8.1','1-6-9','1-6-10','1-6-10.1','1-6-14','1-6-23','1-6B-3','1-6B-6','1-6B-7','1-6B-8','1-6B-13','1-12-1','1-12-12','1-12-43.1','1-12-20','1-12-25.1','1-12-25.2','1-12-25.3','1-12-25.4','1-12-27','1-12-27.1','1-13-1','1-13-4','1-13-5','1-13-11','1-13-12','1-13-13','1-13-15','1-13-16','1-13-18','1-13-24','1-14-1','1-14-3','1-14-14','1-14-15','1-14-18','1-14-23','1-14-24','1-15-12','1-15-13','1-15-14']
def main():
    for n in NAMES:
        r=json.loads((HERE/'receipts'/f'{n}.json').read_bytes())
        run=subprocess.run(['pdftotext','-layout','-','-'],input=body(r),check=True,capture_output=True);(HERE/(n+'.txt')).write_bytes(run.stdout)
    s=(HERE/'nm-elections-code-frame-pdf.txt').read_text();heads=list(re.finditer(r'^[\f]*([0-9]+-[0-9A-Z]+-[0-9]+(?:\.[0-9]+)?)\.\s+[^\n]+',s,re.M));out={}
    for t in TERMS:
        matches=[(i,m) for i,m in enumerate(heads) if m.group(1)==t]
        if not matches:out[t]=dict(status='heading not found; full PDF/text retained');continue
        i,m=matches[0];start=m.start(1);end=heads[i+1].start() if i+1<len(heads) else len(s)
        out[t]=dict(start_line=s.count('\n',0,start)+1,physical_pdf_page_1based=s.count('\f',0,start)+1,complete_section_including_annotations=s[start:end])
    dump(HERE/'operative-code-sections.json',out)
    print('whole PDF texts',len(NAMES),'bounded complete section contexts',len(TERMS))
if __name__=='__main__':main()
