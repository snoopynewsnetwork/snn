"""Independent complete historical CSV/PDF controls from immutable original bytes."""
from acquire import *
import csv,io,subprocess,tempfile,collections
def main(write=True):
    refs=json.loads((STATE/'data/turnout/acquisition.json').read_bytes());byid={r['id']:r for r in refs};checks=0
    def ck(v,label):
        nonlocal checks
        assert v,label;checks+=1
    def original(n):
        r=byid[n];b=(STATE/r['asset']).read_bytes();ck(sha(b)==r['stored_sha256'],'stored '+n);raw=gzip.decompress(b) if r.get('compression')=='gzip' else b;ck(sha(raw)==r['raw_sha256'],'raw '+n);return raw
    cases={'2024-senate':'elstats-2024-senate-linked-csv','2020-senate':'elstats-observed-2020-senate-native-csv','2022-governor':'elstats-observed-2022-governor-native-csv','2024-president':'elstats-observed-2024-president-native-csv'}
    parsed={};summary={}
    for name,sid in cases.items():
        rows=list(csv.reader(io.StringIO(original(sid).decode('utf-8-sig'))));header=rows[:2];n=len(header[0])-4;county=None;counties={};native=[];state=None
        for pos,row in enumerate(rows[2:],3):
            if row[0]=='State':state=row
            elif row[0]=='County':county=row[1];counties[county]=row
            elif row[0]=='Precinct':native.append(dict(source_row=pos,county=county,raw_row=row))
        ck(len(counties)==33 and len(native)=={'2024-senate':2201,'2020-senate':1959,'2022-governor':2196,'2024-president':2202}[name],'whole universe '+name)
        for j in range(2,2+n):ck(sum(int(r[j]) for r in counties.values())==int(state[j]),'all county candidate closure '+name)
        parsed[name]=dict(headers=header,rows=rows,counties=counties,native=native,state=state,candidate_count=n)
        summary[name]=dict(source_id=sid,header_rows=header,total_csv_rows=len(rows),county_count=len(counties),native_count=len(native),privacy_rows=sum(x['raw_row'][1]=='Voter Privacy' for x in native),candidate_mask_cells=sum(z=='*' for x in native for z in x['raw_row'][2:2+n]),all_mask_cells=sum(z=='*' for row in rows for z in row),state_raw_row=state,all_county_raw_rows=list(counties.values()))
    contract=json.loads((STATE/'data/turnout/priority-set.json').read_bytes());native=parsed['2024-senate']['native'];ck(len(native)==len(contract['constituents']),'complete target contract')
    for source,c in zip(native,contract['constituents']):
        row=source['raw_row'];ck(c['source_row_1based']==source['source_row'] and c['county_source_label']==source['county'] and c['native_id_literal']==row[1] and c['source_candidate_literals']==row[2:4],'all raw source target identity/positions')
    pdfs=json.loads((STATE/'data/baselines/pdf-county-controls.json').read_bytes());fresh={};proofs=[];cells=0
    for case,vectors in pdfs['vectors'].items():
        for vector in vectors:
            sid=vector['source_id']
            if sid not in fresh:
                raw=original(sid)
                run=subprocess.run(['pdftotext','-layout','-','-'],input=raw,check=True,capture_output=True);fresh[sid]=run.stdout.decode()
            line=vector['raw_line'];ck(line in fresh[sid],case+' original PDF complete control line')
            values=[int(x) for x in re.findall(r'(?<!\S)-?\d+(?!\S)',line)];ck(values==vector['values'] and len(values)==34,case+' all original numeric fields')
            candidate=values[-1];p=parsed[case];matches=[j for j in range(2,2+p['candidate_count']) if int(p['state'][j])==candidate];ck(len(matches)==1,'unambiguous original numeric control lane');j=matches[0]
            for county,value in zip(vector['county_order'],values[:-1]):ck(int(p['counties'][county][j])==value,'all33 independent PDF county control');cells+=1
            ck(sum(values[:-1])==values[-1],'whole PDF vector state sum');proofs.append(dict(contest=case,source_id=sid,source_raw_line=line,all_values=values,candidate_csv_column_1based=j+1,county_order=vector['county_order']))
    ck(cells==495,'all495 original PDF cells')
    out=dict(status='pass',checks=checks,independent_original_pdf_candidate_cells=cells,historical_universes=summary,complete_pdf_control_lines=proofs,known2024_native_candidate_total=sum(sum(int(z) for z in x['raw_row'][2:4]) for x in native if all(z.isdigit() for z in x['raw_row'][2:4])),masked_native_rows=sum(any(z=='*' for z in x['raw_row'][2:4]) for x in native),no_mask_reconstruction=True,current_count_admitted=False)
    if write:dump(HERE/'historical-validation.json',out)
    return out
if __name__=='__main__':
    v=main('--audit' not in sys.argv);print({k:v[k] for k in ['status','checks','independent_original_pdf_candidate_cells','known2024_native_candidate_total','masked_native_rows']})
