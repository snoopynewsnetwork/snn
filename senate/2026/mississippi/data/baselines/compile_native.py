"""Inventory every original/page and preserve every extracted source cell.

Do not deduplicate by candidate or normalize native labels. County/source/page/
row/column is the immutable observation key; TOTAL and blank positions survive.
"""
import csv,gzip,io,json,re,urllib.parse
from collections import defaultdict
import fitz
from sources import *
from build_counties import writecsv
def main():
    ledger=json.loads((OUT/'native-readings.json').read_text());annotations={(r['source_id'],r['page'],r['source_column']):r for r in ledger['unit_annotations']}
    counties=list(csv.DictReader((BASE/'data/county-baselines.csv').open()));cf={r['county'].lower():r['fips'] for r in counties};cf['jefferson davis']=cf['jeff davis']
    expected=defaultdict(dict)
    for r in csv.DictReader((OUT/'candidate-votes.csv').open()):
        name=r['candidate_literal']
        if r['contest']=='2024-president':name=re.match(r'Presidential Electors for (.*?) for President',name).group(1)
        expected[(r['contest'],r['fips'])][name]=int(r['votes'])
    sources=[];rows=[];checks=[];allunits=[]
    rr=[r for r in references().values() if re.match(r'sos-(2018|2020|2024)-(runoff-)?county-',r['id']) and 'pdf' in str(r.get('headers',{})).lower()]
    for r in rr:
        key=r['id'];label=urllib.parse.unquote(r['url'].rsplit('/',1)[-1]).removesuffix('.pdf');county=re.sub(r'[_ ]?(Amended|Updated)$','',label,flags=re.I).lower();fid=cf.get(county)
        override=next((v for v in ledger.get('county_identity_overrides',[]) if v['source_id']==key),None)
        if override:fid=override['fips']
        # Literal route typo is preserved; no automatic Jackon->Jackson identity.
        source=dict(source_id=key,source_label=label,fips=fid,county_identity_status='official county-index label + EAC name' if fid else 'unresolved literal route; direct page identity required',raw_sha256=r['raw_sha256'],original_path=r['path'],source_url=r['url'])
        if override:source['county_identity_status']='independent direct original cover identity; literal route typo retained';source['county_identity_evidence']=override
        doc=fitz.open(stream=original(key),filetype='pdf');source['pdf_pages']=len(doc);source['extracted_pages']=0;source['extraction_errors']=[];units={};bycandidate=defaultdict(list);summary=defaultdict(list)
        for pg in range(1,len(doc)+1):
            p=OUT/'extracts/native-v4'/key/f'p{pg:04d}.json.gz'
            if not p.exists():continue
            source['extracted_pages']+=1;x=json.loads(gzip.decompress(p.read_bytes()))
            if x.get('error'):source['extraction_errors'].append(dict(page=pg,error=x['error']));continue
            columns={c['source_column']:c for c in x.get('columns',[])}
            for addition in ledger['additional_rows']:
                if addition['source_id']==key and addition['page']==pg:
                    assert not any(f['field']==addition['field'] and f['source_row']==addition['source_row'] for f in x['fields'])
                    cc=[]
                    for j,v in enumerate(addition['values'],1):
                        h=columns[j];cc.append(dict(source_column=j,value=v,raw_ocr='[manual original-source reading]',bounds=[h['bounds'][0],addition['row_bounds'][1],h['bounds'][2],addition['row_bounds'][3]]))
                    x['fields'].append(dict(source_row=addition['source_row'],field=addition['field'],office_context_ocr=addition['office_context'],label_ocr=addition['label_literal'],cells=cc,manual_evidence=addition['evidence']))
            for f in x['fields']:
                for c in f['cells']:
                    header=columns.get(c['source_column'],{});label=header.get('ocr_label','');typ='summary_TOTAL' if re.search(r'\btotal\b',label,re.I) else 'blank_or_unresolved_label' if not re.search('[A-Za-z0-9]',label) else 'source_native_unit_label_OCR_unverified'
                    annotation=annotations.get((key,pg,c['source_column']),{});typ=annotation.get('unit_type',typ)
                    rec=dict(source_id=key,source_raw_sha256=r['raw_sha256'],fips=fid,page=pg,source_row=f['source_row'],source_column=c['source_column'],observation_key=f'{key}:p{pg}:r{f["source_row"]}:c{c["source_column"]}',unit_key=f'{key}:p{pg}:c{c["source_column"]}',native_label_ocr=label,native_label_literal=annotation.get('native_label_literal'),unit_type=typ,office_context_ocr=f['office_context_ocr'],field=f['field'],field_label_ocr=f['label_ocr'],value=c['value'],raw_ocr=c['raw_ocr'],source_cell_bounds=json.dumps(c['bounds']),render_size=json.dumps(x['render_size']),rotation_ccw=x['rotation_ccw'],deskew_angle_ccw=x['deskew_angle_ccw'],extraction_status='manual_original_source_reading' if f.get('manual_evidence') else 'unreviewed_OCR_not_transcription_authority',manual_evidence=f.get('manual_evidence',annotation.get('evidence')))
                    rows.append(rec)
                    units[rec['unit_key']]=dict(source_id=key,fips=fid,page=pg,source_column=c['source_column'],unit_key=rec['unit_key'],native_label_ocr=label,unit_type=typ,header_bounds=header.get('bounds'))
                    office=f['office_context_ocr']
                    if f['field']=='Chris McDaniel' and not re.search('Chris',f['label_ocr'],re.I):office='unrelated-office'
                    # Candidate identities are explicit and unique to these
                    # published required contests, even if an office heading's
                    # scan is unreadable. Raw OCR context is preserved above.
                    if key.startswith('sos-2024-'):
                        if f['field'] in ['Ty Pinkins','Roger F. Wicker']:office='senate'
                        elif f['field'] in ['Kamala D. Harris','Donald J. Trump','Chase Oliver','Jill Stein','Randall Terry','Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski']:office='president'
                    elif key.startswith('sos-2020-') and f['field'] in ['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']:office='senate'
                    if typ=='summary_TOTAL':summary[(office,f['field'])].append(rec)
                    elif typ not in ['blank_or_unresolved_label','unused']:bycandidate[(office,f['field'])].append(rec)
        source['source_column_positions']=len(units);source['non_total_labeled_positions']=sum(u['unit_type']=='source_native_unit_label_OCR_unverified' for u in units.values());source['summary_positions']=sum(u['unit_type']=='summary_TOTAL' for u in units.values());source['blank_or_unresolved_positions']=sum(u['unit_type']=='blank_or_unresolved_label' for u in units.values());allunits.extend(units.values())
        for (office,name),cells in bycandidate.items():
            contest=('2018-runoff' if '2018-runoff-' in key else '2018-special') if key.startswith('sos-2018-') and name in (['Mike Espy','Cindy Hyde-Smith'] if '2018-runoff-' in key else ['Mike Espy','Cindy Hyde-Smith','Tobey Bernard Bartee','Chris McDaniel']) and office!='unrelated-office' else key[4:8]+'-'+office
            values=[c['value'] for c in cells];missing=sum(v is None for v in values);s=sum(v for v in values if v is not None);ex=expected.get((contest,fid),{}).get(name);printed=summary.get((office,name),[])
            checks.append(dict(source_id=key,fips=fid,contest=contest,office_context_ocr=office,candidate=name,native_positions=len(cells),unresolved_values=missing,native_numeric_sum=s,expected_county_value=ex,difference_from_expected=None if ex is None else s-ex,source_TOTAL_values=[c['value'] for c in printed],status='incomplete_OCR' if missing else 'numeric_match_pending_identity_review' if ex==s else 'source_control_or_OCR_review_required'))
        source['complete_page_inventory']=source['extracted_pages']==source['pdf_pages'];sources.append(source)
    if rows:
        stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        (OUT/'native-raw-cells.csv.gz').write_bytes(gzip.compress(stream.getvalue().encode(),mtime=0))
    save(OUT/'native-unit-inventory.json',allunits);save(OUT/'native-source-inventory.json',sources);save(OUT/'native-control-checks.json',checks)
    save(OUT/'native-coverage.json',dict(source_documents=len(sources),expected_pages=sum(r['pdf_pages'] for r in sources),extracted_pages=sum(r['extracted_pages'] for r in sources),complete_page_sources=sum(r['complete_page_inventory'] for r in sources),source_cell_rows=len(rows),unresolved_county_routes=[r['source_id'] for r in sources if r['fips'] is None],qualification='Inventory and machine aids only; unresolved cells are not zero; no complete native acceptance from statewide match'))
    print((OUT/'native-coverage.json').read_text())
if __name__=='__main__':main()
