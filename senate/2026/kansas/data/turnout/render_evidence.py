#!/usr/bin/env python3
"""Reproduce retained first-page primary PDF presentation previews."""
import json, subprocess
from sources import HERE, source_bytes, sha

PDFS=['sos-2024-general-canvass','sos-2022-general-canvass','sos-2020-general-canvass','sos-2026-primary-canvass']

if __name__=='__main__':
    for sid in PDFS:
        out=HERE/'extracts'/f'{sid}-page1'
        subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to','1400','-png','-',str(out)],input=source_bytes(sid),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        print(out.name+'.png')
    for page in [1,2]:
        sid='sumner-2022-actual-linked-summary'
        out=HERE/'extracts'/f'{sid}-page{page}'
        subprocess.run(['pdftoppm','-f',str(page),'-singlefile','-scale-to','1400','-png','-',str(out)],input=source_bytes(sid),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        print(out.name+'.png')
