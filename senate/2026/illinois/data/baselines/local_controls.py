"""Independent local PDF source extraction; no aliases/native allocations inferred."""
import csv,gzip,json,re,subprocess
from source_io import ROOT,raw,dump
from extract import csvwrite
def main():
    texts={}
    for sid in ['original-turnout-chicago-proclamation-2024','original-turnout-bloomington-writein-2024']:
        text=subprocess.run(['pdftotext','-layout','-','-'],input=raw(sid),capture_output=True,check=True).stdout
        (ROOT/f'extract/{sid}.txt.gz').write_bytes(gzip.compress(text,mtime=0));texts[sid]=text.decode()
    sid='original-turnout-chicago-proclamation-2024';pages=texts[sid].split('\f');matches=[(i,p)for i,p in enumerate(pages,1)if '775,699'in p and 'President & Vice President, U.S.'in p];assert len(matches)==1
    page,text=matches[0];left='\n'.join(l[:70].rstrip()for l in text.splitlines());part=left.split('President & Vice President, U.S.',1)[1].split('U.S. Representative, 1st District',1)[0];rows=[];total=None
    for pos,line in enumerate(part.splitlines(),1):
        m=re.match(r'\s*(.*?)\s+([\d,]+)\s+([\d.]+%)\s*$',line)
        if m:rows.append(dict(source_id=sid,PDF_page=page,source_block_line=pos,label_literal=m[1],votes=int(m[2].replace(',','')),percentage_literal=m[3],line_literal=line))
        elif line.strip()=='Shanahan':
            assert rows and rows[-1]['label_literal'].startswith('IND - Robert F. Kennedy Jr. & Nicole')
            rows[-1]['label_literal']+='\n'+line.strip();rows[-1]['line_literal']+='\n'+line
        t=re.match(r'\s*Total\s+([\d,]+)\s*$',line)
        if t:total=int(t[1].replace(',',''))
    assert total==1001481 and sum(r['votes']for r in rows)==total
    csvwrite(ROOT/'extract/chicago-2024-presidential-source-rows.csv',rows)
    native={r['candidate_or_category_literal']:int(r['votes'])for r in csv.DictReader((ROOT/'extract/authority-candidate-category-totals.csv').open())if r['year']=='2024'and r['JurisdictionID']=='105'}
    # Explicit first-three publication descriptions only; no write-in row joins.
    assert [r['votes']for r in rows[:3]]==[native['Kamala D. Harris'],native['Donald J. Trump'],native['Robert F. Kennedy Jr.']]
    printed=sum(r['votes']for r in rows[:3]);generic=sum(v for k,v in native.items()if k.lower()=='write-in');assert total-printed==generic==10189
    sid='original-turnout-bloomington-writein-2024';rows2=[]
    for pos,line in enumerate(texts[sid].splitlines(),1):
        m=re.match(r'\s*(.*?)\s+Total valid write-in votes cast\s+(\d+)\s*$',line)
        if m:rows2.append(dict(source_id=sid,PDF_page=1,source_line=pos,ticket_or_name_literal=m[1],votes=int(m[2]),line_literal=line))
    assert len(rows2)==10 and sum(r['votes']for r in rows2)==204
    csvwrite(ROOT/'extract/bloomington-2024-writein-source-rows.csv',rows2)
    dump(ROOT/'extract/local-source-controls.json',dict(Chicago=dict(source_id='original-turnout-chicago-proclamation-2024',PDF_page=page,local_named_total=total,three_printed=printed,additional_named=total-printed,native_generic_marks=generic,additional_named_equals_generic=True,qualification='Local named labels differ from statewide labels; no aliases or precinct allocation inferred.'),Bloomington=dict(source_id=sid,source_rows=10,valid_writein_total=204,qualification='Certain local ticket labels combined, explicit source zeros preserved. Not allocated across statewide aliases/native units.')))
    print(json.dumps({'Chicago_rows':len(rows),'Chicago_total':total,'Bloomington_writein_rows':len(rows2),'Bloomington_total':204}))
if __name__=='__main__':main()
