#!/usr/bin/env python3
"""Parse source-aligned registration columns; retain blanks, wrapping and page positions."""
import json,re
from pathlib import Path
D=Path(__file__).resolve().parent
def main():
    out={}
    for vintage in ['9','10']:
        src=f'registration-{vintage}-county';text=(D/'source'/f'{src}.txt').read_text();rows=[];clocks=[];county=None
        for page_no,page in enumerate(text.split('\f'),1):
            lines=page.splitlines();cs=re.search(r'^(.+?) County\s+As of (.+)$',page,re.M)
            if cs:county=cs.group(1).strip();asof=cs.group(2).strip()
            elif 'Grand Total' in page:county=None
            else:continue
            clock=re.search(r'^\d+/\d+/\d+[^\n]+',page,re.M)
            if clock:clocks.append({'page':page_no,'literal':clock.group(0),'timezone':None})
            head=next(l for l in lines if 'DEMOCRATIC' in l and 'TOTAL' in l)
            cols=sorted((head.index(label),label)for label in ['DEMOCRATIC','REPUBLICAN','LIBERTARIAN','OTHER','TOTAL']);start=cols[0][0]
            prior=None
            for i,line in enumerate(lines,1):
                # Numeric row must begin with a native/source label and contain a printed total.
                lab=line[:start].strip()
                if not lab or line==head or 'County' in line or 'As of' in line or lab.startswith(('New Mexico','by County','10/','11/')):continue
                slices=[]
                for j,(a,_)in enumerate(cols):
                    # A font-aligned number may begin left of its header; never cut digits.
                    while a>start and a<len(line) and line[a]in '0123456789,' and line[a-1]in '0123456789,':a-=1
                    slices.append(line[a:(cols[j+1][0]if j+1<len(cols)else len(line))])
                def first(s):
                    m=re.search(r'([\d,]+)',s);return int(m.group(1).replace(',',''))if m else None
                vals=[first(s)for s in slices]
                if lab in ('TOTAL','Grand Total'):
                    tokens=re.findall(r'[\d,]+',line[start:])
                    assert len(tokens)==9,(lab,line)
                    vals=[int(tokens[j].replace(',',''))for j in [0,2,4,6,8]]
                if vals[-1]is not None and (lab.startswith(('PCT','PRECINCT','TOTAL','Grand','Precinct','ABSENTEE','EARLY'))or any(v is not None for v in vals[:-1])):
                    prior={'source_id':src,'page':page_no,'line':i,'county_literal':county,'label_literal':lab,'continuations':[],'raw_lines':[line],'party_order':[c[1]for c in cols[:-1]],'counts':vals[:-1],'total':vals[-1],'raw_slices':slices,'scope':'grand_total'if lab=='Grand Total'else ('county_total'if lab=='TOTAL'else 'native'),'asof':asof if county else None};rows.append(prior)
                elif prior and lab and not line[start:].replace('%','').strip():prior['continuations'].append(lab);prior['raw_lines'].append(line)
        out[vintage]={'source_id':src,'rows':rows,'clocks':clocks,'timezone':None}
    (D/'registration-native-controls.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print({k:{s:sum(r['scope']==s for r in v['rows'])for s in ['native','county_total','grand_total']}for k,v in out.items()})
if __name__=='__main__':main()
