#!/usr/bin/env python3
"""Independent extraction of federal primary PDF controls, reusing exact raw originals."""
import gzip,hashlib,json,re,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent/'baselines/source'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    tables=json.loads((D/'extracts/primary-county-tables.json').read_text());out=[];refs=[]
    mappings={
        '2024':{'Rick Scott (REP)':'Rick Scott, Republican','Debbie Mucarsel-Powell (DEM)':'Debbie Mucarsel-Powell, Democrat','Feena Bonoan (LPF)':'Feena Bonoan, Libertarian Party of Florida','Tuan TQ Nguyen (NPA)':'Tuan “T Q” Nguyen, No Party Affiliation','Ben Everidge (NPA)':'Ben Everidge, No Party Affiliation','Howard Knepper (WRI)':'Howard Knepper, Write-in'},
        '2022':{'Marco Rubio (REP)':'Marco Rubio, Republican','Val Demings (DEM)':'Val Butler Demings, Democrat','Dennis Misigoy (LPF)':'Dennis Misigoy, Libertarian','Steven B. Grant (NPA)':'Steven B. Grant, No Party Affiliation','Tuan TQ Nguyen (NPA)':'Tuan “TQ” Nguyen, No Party Affiliation','Uloma Uma Ekpete (WRI)':'Uloma Uma Ekpete, Write-in','Edward A. Gray (WRI)':'Edward A. Gray, Write-in','Howard Knepper (WRI)':'Howard Knepper, Write-in','Moses Quiles (WRI)':'Moses Quiles, Write-in'}}
    for y,mapping in mappings.items():
        receipt=json.loads((P/f'clerk-{y}.receipt.json').read_text());pdf=P/f'clerk-{y}.body.gz';stored=pdf.read_bytes();raw=gzip.decompress(stored);assert sha(raw)==receipt['raw_sha256'] and len(raw)==receipt['raw_bytes'] and receipt['status']==200;assert sha(stored)==receipt['stored_sha256']
        text=subprocess.run(['pdftotext','-layout','-','-'],input=raw,stdout=subprocess.PIPE,check=True).stdout.decode();start=re.search(r'\n\s*FLORIDA\s*\n',text).end();end=text.index('FOR UNITED STATES REPRESENTATIVE',start);fl=text[start:end];found={}
        for page,pagetext in enumerate(text.split('\f'),1):
            for linepos,line in enumerate(pagetext.splitlines(),1):
                m=re.match(r'\s*(.+?)\s*\.{3,}\s*([\d,]+)\s*$',line)
                if m and m[1] in mapping.values() and line.strip() in fl:
                    assert m[1] not in found;found[m[1]]=(int(m[2].replace(',','')),page,linepos)
        assert set(found)==set(mapping.values())
        for dos,clerk in mapping.items():
            v,page,line=found[clerk];expected=tables[y+'_senate']['statewide'][dos];assert v==expected
            out.append(dict(context=y+'_senate',dos_header=dos,clerk_printed_candidate_party=clerk,clerk_votes=v,dos_all_county_sum=expected,difference=0,source_url=receipt['requested_url'],raw_sha256=receipt['raw_sha256'],pdf_page_1based=page,text_line_1based_on_page=line,mapping_scope='explicit source name/party identity mapping; original printed identities preserved'))
        refs.append(dict(source_id='clerk-'+y,stored_original_relative_to_this_source='../../baselines/source/'+pdf.name,stored_sha256=sha(stored),stored_bytes=len(stored),storage='gzip; exact raw original PDF reconstructed with gzip.decompress',raw_sha256=sha(raw),raw_bytes=len(raw),original_receipt=receipt,reuse='Read-only exact original PDF; independent pdftotext extraction in verify_federal.py, no peer derivative values'))
    (D/'source/federal-original-references.json').write_text(json.dumps(refs,indent=2)+'\n');(D/'extracts/federal-candidate-reconciliation.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print('PASS',len(out),'independent federal Senate candidate controls')
if __name__=='__main__':main()
