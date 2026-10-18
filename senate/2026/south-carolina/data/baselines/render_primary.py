"""Read original PDF bytes; retain only selected page text/PNG derivatives."""
from extract import *
import subprocess
OUT=SRC/'previews';OUT.mkdir(exist_ok=True)
for sid,pages in [('nara-2024-SC-ascertainment',[1,2]),('house-2020',[62]),('house-2022',[44]),('house-2024',[64]),('candidate-general-print',[1]),('participation-summary',[1]),('absentee-summary',[1])]:
    raw,m=loadbody(SRC/(sid+'.meta.json'))
    for page in pages:
        prefix=OUT/(sid+'-p'+str(page))
        subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-scale-to','1500','-png','-',str(prefix)],input=raw,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        t=subprocess.run(['pdftotext','-f',str(page),'-l',str(page),'-layout','-','-'],input=raw,check=True,stdout=subprocess.PIPE).stdout
        prefix.with_suffix('.txt').write_bytes(t)
        print(sid,page,t[:120].decode(errors='replace').replace('\n',' '))
