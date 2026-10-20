#!/usr/bin/env python3
"""Independent positional canvass/turnout controls; raw text and visual overrides retained."""
import csv,gzip,hashlib,io,json,pathlib,re,subprocess
from extract_originals import BASE,STATE,load_original,save

def main():
    for y in [2024,2022,2020]:
        receipt=json.loads((BASE/f'source/canvass-{y}.receipt.json').read_text())
        packed=(STATE/'data/news'/receipt['asset']).read_bytes();assert hashlib.sha256(packed).hexdigest()==receipt['stored_sha256']
        raw=gzip.decompress(packed);assert hashlib.sha256(raw).hexdigest()==receipt['raw_sha256']
        save(f'source/canvass-{y}.receipt.json',receipt)
        pdf=pathlib.Path('/private/tmp')/f'al-partisan-{y}.pdf';pdf.write_bytes(raw)
        p=subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True)
        (BASE/f'source/canvass-{y}-pdftotext.txt.gz').write_bytes(gzip.compress(p.stdout,mtime=0));(BASE/f'source/canvass-{y}-parser-stderr.txt').write_bytes(p.stderr)
    own=json.loads((BASE/'source/county-observations.json').read_text())
    names={x['county']:x['county_fips'] for x in own};names['St. Clair']=names['StClair'];names['St_ Clair']=names['StClair']
    aliases={'Uefferson':'Jefferson','ilalladega':'Talladega','!Tallapoosa':'Tallapoosa','il uscaloosa':'Tuscaloosa','1walker':'Walker','1wilcox':'Wilcox','1wmston':'Winston','Nale':'Hale'}
    specifications={2024:([4,5],['Kamala D. Harris','Donald J. Trump','Robert F. Kennedy Jr.','Jill Stein','Chase Oliver','Write-In'],0),2022:([3,4],['Will Boyd','Katie Britt','John Sophocleus','Write-In'],3),2020:([2,3],['Doug Jones','Tommy Tuberville','Write-In'],4)}
    rows=[];controls=[];differences=[]
    for y,(pages,cands,skip) in specifications.items():
        text=gzip.decompress((BASE/f'source/canvass-{y}-pdftotext.txt.gz').read_bytes()).decode(); pp=text.split('\f')
        for page in pages:
            lines=pp[page].splitlines();ref=next(l for l in lines if l.lstrip().startswith('Baldwin' if page==pages[0] else 'Houston'))
            ends=[m.end() for m in re.finditer(r'\d[\d,]*',ref)];edges=[0]+[(a+b)//2 for a,b in zip(ends,ends[1:])]+[max(ends)+5]
            for ln,line in enumerate(lines,1):
                label=line[:max(0,ends[0]-10)].strip(); county=aliases.get(label,label)
                if y==2022 and page==4 and label=='Total':county='Henry'
                is_total=label in ('!Total','Total') and page==pages[0]
                if county not in names and not is_total:continue
                if not re.search(r'\d',line):continue
                # Column identity is fixed by page geometry, not by residuals or peer data.
                parts=[]
                for i in range(len(ends)):
                    region=line[edges[i]:edges[i+1]]
                    # Assign complete tokens by their right edge. Never cut a thousands
                    # digit off a long value at a midpoint between short sample values.
                    numeric=[m for m in re.finditer(r'\d[\d,]*',line) if min(range(len(ends)),key=lambda j:abs(m.end()-ends[j]))==i]
                    tok=numeric[-1].group() if numeric else ('‐' if '‐' in region else '')
                    parts.append({'raw_region':region,'text_token':tok,'value':int(tok.replace(',','')) if tok and tok[0].isdigit() else None,'cell_type':'number' if tok and tok[0].isdigit() else ('dash' if tok else 'blank'),'character_interval_0based':[edges[i],edges[i+1]]})
                override=None
                if y==2024 and county in ('Hale','Winston'):
                    v={'Hale':[3868,3369,30,10,13,15],'Winston':[884,10191,36,8,10,20]}[county]
                    override={'reason':'Damaged embedded OCR; complete rendered page independently read','image':f'source/visual-2024-{page+1:03d}.png','values':v}
                    for p,n in zip(parts,v):p.update(value=n,cell_type='visual_number')
                cr=[{'candidate':c,'source_column':skip+i+1,**parts[skip+i]} for i,c in enumerate(cands)]
                ob={'year':y,'county':'Total' if is_total else county,'county_fips':None if is_total else names[county],'pdf_page_1based':page+1,'printed_page':page-pages[0]+1 if y!=2022 else page,'text_line_1based_on_page':ln,'raw_line':line,'raw_label':label,'candidate_cells':cr,'visual_override':override,'label_qualification':'2022 Henry label detached in text; complete page image prints Henry' if y==2022 and county=='Henry' else None}
                (controls if is_total else rows).append(ob)
        yr=[r for r in rows if r['year']==y];assert len(yr)==67 and len({r['county_fips'] for r in yr})==67
        control=next(x for x in controls if x['year']==y)
        for i,c in enumerate(cands):
            assert sum(x['candidate_cells'][i]['value'] or 0 for x in yr)==control['candidate_cells'][i]['value'],(y,c)
        for r in yr:
            x=next(x for x in own if x['year']==y and x['county_fips']==r['county_fips']);xm={c['candidate_literal'].strip():c for c in x['candidate_rows']}
            for c in r['candidate_cells']:
                xc=xm[c['candidate']]
                if c['value']!=xc['votes']:differences.append({'year':y,'county_fips':r['county_fips'],'county':r['county'],'candidate':c['candidate'],'pdf_value':c['value'],'pdf_cell_type':c['cell_type'],'xls_sum':xc['votes'],'xls_unknown_cells':xc['unknown_cells'],'difference_xls_minus_pdf':None if c['value'] is None else xc['votes']-c['value'],'pdf_page':r['pdf_page_1based'],'raw_line':r['raw_line']})
    save('source/canvass-county-cells.json',rows);save('source/canvass-state-controls.json',controls);save('source/canvass-xls-disagreements.json',differences)
    refs=[];ballots=[]
    for y,h in [(2024,'f1cfb4e8619bbf4a0efbea0582abdbe40b9b23285d611740038901bc328b528b'),(2022,'823fe88d82277f6ea8cb42b4d1a0fc9f214608c0568b94afab009d75fbb678ca')]:
        b,ref=load_original(h);refs.append(ref);p=pathlib.Path('/private/tmp')/f'al-partisan-ballots-{y}.pdf';p.write_bytes(b)
        result=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True);save_text=BASE/f'source/ballots-{y}-pdftotext.txt';save_text.write_bytes(result.stdout);(BASE/f'source/ballots-{y}-parser-stderr.txt').write_bytes(result.stderr)
    nd=json.loads((BASE/'source/ballots-2020.receipt.json').read_text())
    b=gzip.decompress((STATE/'data/news'/nd['asset']).read_bytes());assert hashlib.sha256(b).hexdigest()==nd['raw_sha256'];p=pathlib.Path('/private/tmp/al-partisan-ballots-2020.pdf');p.write_bytes(b);res=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True);(BASE/'source/ballots-2020-pdftotext.txt').write_bytes(res.stdout);(BASE/'source/ballots-2020-parser-stderr.txt').write_bytes(res.stderr)
    for y in [2024,2022,2020]:
        lines=(BASE/f'source/ballots-{y}-pdftotext.txt').read_text().splitlines()
        for i,l in enumerate(lines,1):
            m=re.match(r'^\s*([A-Za-z. _]+?)\s{2,}(\d[\d,]*.*)$',l)
            if not m:continue
            n=m[1].strip(); n={'De Kalb':'DeKalb','St. Clair':'St. Clair'}.get(n,n)
            if n not in names and n!='Total':continue
            tokens=re.findall(r'\d[\d,]*(?:\.\d+)?%?',m[2]);assert len(tokens)==7,(y,n,tokens)
            vals=[int(t.replace(',','')) for t in tokens[:5]]
            ballots.append({'year':y,'county':n,'county_fips':None if n=='Total' else names[n],'registered_voters':vals[0],'ballots_cast':vals[1],'democrat_ballots_or_straight_party':vals[2],'republican_ballots_or_straight_party':vals[3],'absentee_ballots':vals[4],'turnout_printed':tokens[5],'absentee_pct_printed':tokens[6],'raw_line':l,'source_line_1based':i,'registration_definition':'Registered Voters as printed; active/inactive status and as-of extract date unspecified','party_definition':'2024 Democrat/Republican Ballots; 2022/2020 straight-party columns; not candidate vote totals'})
        assert len([r for r in ballots if r['year']==y])==68,(y,len([r for r in ballots if r['year']==y]))
    for h in ['e099bfe2a257a5ba0993a56361959fb989f38041dbc8da12a5dad31cfeebab29','adde72e6d3cf62dbff70beed20758b52680664f0211678a8f7fd18d9d1960849','9a8da843edc524791a6e46bc545cf208936fe23e1b63ec794b8ca5a0114b6559','dbb8540ace50584ad92c20fec3fc9fef0f5f24a3d317b13d2ed4eb7d578a00a0','a3a109642073bd075596e0d2a0d3fa5c5a692b1178f12e13532a73987c2c89c6','707afb050c7bc052ce8eca51ced59b56641acedfb7c28e7ae5a1e164da2f71ae','4f1a69210a68808985d5982feb526f3e241d743bd7b690604f785192be5614ae','5c2800a156f356c1150f95c8d606f543dd233e95ceb24f8e5f9a5ae7ef2a40db']:
        _,ref=load_original(h);refs.append(ref)
    save('source/supplementary-original-references.json',refs);save('source/ballot-registration-controls.json',ballots)
    print(json.dumps({'canvass_county_rows':len(rows),'disagreements':differences,'ballot_registration_rows':len(ballots)},indent=2))
if __name__=='__main__':main()
