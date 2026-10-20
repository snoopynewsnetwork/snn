#!/usr/bin/env python3
"""Preserve source-scoped participation headers and literal administrative rows.

Repeated county headers are presentations, never additive increments. Tables
whose axes are not safely parsed stay literal with their source positions.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import csv,gzip,io,json,re
from native_extract import OUT,INV,pages,read

def main():
    rows=[];index=[]
    keys=[(r['source_key'],False)for r in INV if r.get('original_kind')=='PDF']
    keys+=[('2024-Wasco',False)]
    keys +=[(k,True)for k in ['washington-2024-precincts','washington-2024-ballots','multnomah-2024-president',
        'multnomah-2024-registration','clackamas-2024-canvass','marion-2024-canvass','benton-2020-precincts','benton-2022-precincts']]
    for key,acquired in keys:
        for pg,text,layer in pages(key,acquired):
            lines=text.splitlines();required=[];identities=[]
            for i,line in enumerate(lines,1):
                norm=re.sub(r'\s+',' ',line.strip())
                if re.search(r'(?:U\.?S\.? Senator|Governor|President and Vice President)',norm,re.I):required.append(i)
                if re.fullmatch(r'Precinct\s*\d[\w/-]*',norm)or re.match(r'^\d{2}\s*-\s*[A-Za-z]',norm):identities.append(dict(line=i,literal=norm))
                if re.search(r'Total Ballots Cast:|Registered Voters(?: - Total|:)|Ballots Cast - (?:Total|Blank)|blank ballots|Number Eligible|Ballots Returned',norm,re.I):
                    row=dict(source_key=key,page=pg,line=i,text_layer=layer,literal_source_row=line,
                        presentation_scope='literal repeated administrative/participation row; nonadditive until axes resolved')
                    for label,pat in [('overall_report_ballots_cast',r'Total Ballots Cast:\s*([\d,]+)'),('overall_report_registered_voters',r'Registered Voters:\s*([\d,]+)')]:
                        m=re.search(pat,norm)
                        if m:row[label]=int(m[1].replace(',',''))
                    rows.append(row)
            index.append(dict(source_key=key,page=pg,text_layer=layer,text_characters=len(text),
                printed_header_lines=lines[:8],printed_header_timezone=None,
                required_contest_heading_lines=required,literal_identity_rows=identities,
                qualification='OCR headings/identities are unreviewed locators where indicated, not complete legal/native inventory'))
    # Umatilla's original CSV has an explicit three-column participation table.
    rs=list(csv.reader(io.StringIO(read('2020-29'))))
    header_index=next(i for i,r in enumerate(rs)if 'Registered Voters - Total'in r)
    header=rs[header_index]
    for i,r in enumerate(rs[header_index+1:],header_index+2):
        if len(r)<5 or not r[1]:break
        if not(re.match(r'^\d',r[1])or r[1].lower()in ['total','totals']):break
        rows.append(dict(source_key='2020-29',CSV_record_1based=i,unit_literal=r[1],
            registered_voters=int(r[2].replace(',','')),ballots_cast=int(r[3].replace(',','')),
            blank_ballots=int(r[4].replace(',','')),literal_source_row=r,
            presentation_scope='STATISTICS table; repeated candidate-contest ballots are separate nonadditive presentations'))
    for name,data in [('participation-source-rows.jsonl.gz',rows),('whole-native-page-index.jsonl.gz',index)]:
        b=''.join(json.dumps(x,ensure_ascii=False)+'\n'for x in data).encode();(OUT/'native'/name).write_bytes(gzip.compress(b,mtime=0))
    print('Participation/source rows',len(rows),'original PDF pages indexed',len(index))
if __name__=='__main__':main()
