"""Explicit publication-clock/status literals, separate from retrieval/ZIP/HTTP clocks."""
import gzip,re
from common import *
def main():
    out=[]
    for ident in ['boe-2024-summary','board2020-pdf','board2022-pdf','ri-2020-observed-format-description','ri-2022-description','board2020-writeins-pdf','board2022-writeins-pdf','writein-guide']:
        p=BASE/'witness'/f'{ident}.layout.txt.gz'
        if not p.exists():continue
        b=gzip.decompress(p.read_bytes());s=b.decode();offset=0
        for page,content in enumerate(s.split('\f'),1):
            for line_no,line in enumerate(content.splitlines(keepends=True),1):
                if any(t in line for t in ['OFFICIAL RESULTS','Run Date:','Election Summary -','Rev.','General Election 2024','Tuesday November 3, 2020','November 8, 2022','RIGEN22']):
                    out.append({'input':ident,'page':page,'text_line':line_no,'text_byte_start':offset,'literal':line.rstrip('\r\n'),
                        'timezone_stated':None,'meaning':'Publication text/status clock, not retrieval time or a proven correction sequence'})
                offset+=len(line.encode())
            offset+=1
    write_json('source/publication-vintages.json',out)
    print('Publication clock/status literals',len(out))
if __name__=='__main__':main()
