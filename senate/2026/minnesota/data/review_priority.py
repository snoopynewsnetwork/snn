"""Coordinator original OOXML/native/county/priority reconciliation; no worker parser imported."""
import collections
import datetime
import gzip
import hashlib
import io
import json
import re
import subprocess
import xml.etree.ElementTree as E
import zipfile
from pathlib import Path

H = Path(__file__).resolve().parent
N = H / 'news'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
captures = {r['id']: r for r in json.loads((N / 'manifest.json').read_text())}


def raw(sid):
    m = captures[sid]
    b = (N / m['asset']).read_bytes()
    assert hashlib.sha256(b).hexdigest() == m['stored_sha256']
    b = gzip.decompress(b)
    assert len(b) == m['bytes'] and hashlib.sha256(b).hexdigest() == m['raw_sha256']
    return b


def workbook(sid):
    z = zipfile.ZipFile(io.BytesIO(raw(sid)))
    assert z.testzip() is None
    strings = [''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS)]
    rels = {r.attrib['Id']: r.attrib['Target'] for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    sheets = {}
    for sheet in E.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS):
        path = rels[sheet.attrib[R]]
        path = path.lstrip('/') if path.startswith('/') else 'xl/'+path
        rows = []
        for row in E.fromstring(z.read(path)).findall('s:sheetData/s:row', NS):
            cells = {}
            for cell in row:
                v = cell.find('s:v', NS)
                if cell.attrib.get('t') == 'inlineStr':
                    value = ''.join(cell.find('s:is', NS).itertext())
                elif v is None:
                    value = None
                else:
                    value = strings[int(v.text)] if cell.attrib.get('t') == 's' else v.text
                cells[cell.attrib['r']] = dict(value=value, type=cell.attrib.get('t'),
                                               formula=cell.findtext('s:f', namespaces=NS))
            rows.append(dict(source_id=sid, sheet=sheet.attrib['name'], source_row=int(row.attrib['r']), cells=cells))
        sheets[sheet.attrib['name']] = rows
    return sheets

def main():
    import csv
    import math
    contract_path=H/'turnout/priority-set.json'
    contract_bytes=contract_path.read_bytes()
    assert len(contract_bytes)==9885383 and hashlib.sha256(contract_bytes).hexdigest()=='b60b0bc4fed0c0b8618b6f851cc8f25d3c963bbd3ea12debecc5995dff54ceb1'
    contract=json.loads(contract_bytes)
    assert contract['coordinator_acceptance_path']=='data/coordinator-priority-acceptance.json'
    checks=0;native_counts={};sources={};by_year={};county_controls={};notes={}
    for year,prefix,count in [(2024,'USSEN',4103),(2022,'MNGOV',4103),(2020,'USSEN',4110)]:
        sid=f'sos-{year}-precinct-original';sheets=workbook(sid);rs=sheets['Precinct-Results']
        labels=[c['value']for c in rs[0]['cells'].values()]
        duplicates={k for k,n in collections.Counter(labels).items()if n>1}
        columns={re.sub(r'\d+$','',k):v['value']+('__'+re.sub(r'\d+$','',k)if v['value']in duplicates else'')for k,v in rs[0]['cells'].items()}
        originals={}
        for r in rs[1:]:
            d={columns[re.sub(r'\d+$','',k)]:v['value']for k,v in r['cells'].items()}
            if d.get('VTDID')in[None,'','End of worksheet']:continue
            assert re.fullmatch(r'\d{9}',d['VTDID'])
            originals[r['source_row']]=d
        cmap={}
        for r in sheets['Counties'][1:]:
            v=[x['value']for x in r['cells'].values()]
            if len(v)>=3 and v[0]and re.fullmatch(r'\d+',v[0]):cmap[v[0]]=(v[1],v[2])
        assert len(cmap)==87
        with gzip.open(H/f'turnout/native-{year}.csv.gz','rt')as f:peer=list(csv.DictReader(f))
        assert len(peer)==len(originals)==count and len({r['native_key']for r in peer})==count
        controls=collections.defaultdict(collections.Counter);numeric=set()
        for r in peer:
            row=originals[int(r['source_row'])]
            assert r['source_id']==sid and r['source_sheet']=='Precinct-Results'
            for key in set(row)&set(r):
                assert (row[key]if row[key]is not None else'')==r[key],(year,r['source_row'],key)
                checks+=1
            name,fips=cmap[row['COUNTYCODE']]
            assert row['COUNTYNAME'].upper()==name and row['VTDID']==fips+row['PCTCODE']
            assert r['county_fips']==fips and r['county_key']=='MN:county:'+fips and r['native_key']==f'MN:{year}:VTDID:'+row['VTDID']
            candidate_fields=[k for k in row if k.startswith(prefix)and k!=prefix+'TOTAL']
            assert sum(int(row[k])for k in candidate_fields)==int(row[prefix+'TOTAL'])
            numeric_fields=[k for k in ['REG7AM','EDR','SIGNATURES','AB_MB','FEDONLYAB','PRESONLYAB','TOTVOTING']if k in row]
            numeric_fields += [k for k in row if k in r and k.startswith(('USSEN','USPRS','MNGOV'))]
            for key in numeric_fields:
                assert re.fullmatch(r'\d+',row[key]);controls[fips][key]+=int(row[key]);numeric.add(key)
        by_year[str(year)]={r['native_key']:r for r in peer};native_counts[str(year)]=count
        county_rows=list(csv.DictReader((H/f'turnout/county-controls-{year}.csv').open()));assert len(county_rows)==87
        for r in county_rows:
            for key in numeric:assert int(r[key])==controls[r['county_fips']][key];checks+=1
        county_controls[str(year)]=controls
        sources[str(year)]={'source_id':sid,'sha256':captures[sid]['raw_sha256'],'original_bytes':captures[sid]['bytes'],'native_rows':count,'selected_source_columns_checked':len(numeric)}
        notes[str(year)]=[x['cells']for x in sheets['Notes']]
        context=json.loads((H/'turnout/source/workbook-context.json').read_text())[str(year)]
        assert context['columns']==columns
    original2024=county_controls['2024'];values={k:v['USSENTOTAL']for k,v in original2024.items()}
    ranked=sorted(values,key=lambda k:(-values[k],k));total=sum(values.values())
    assert total==3189323 and sum(values[k]for k in ranked[:15])==2308744
    assert sum(values[k]for k in ranked[:23])==2543408 and sum(values[k]for k in ranked[:24])==2567977
    assert values[ranked[23]]==24569 and ranked[23]=='27007'
    assert 5*2543408<4*total<=5*2567977
    keys=['MN:county:'+k for k in ranked]
    assert keys==contract['complete_ordered_county_keys'] and keys[:24]==contract['ordered_priority_keys'] and keys[24:]==contract['remainder_keys']
    constituent_count=0;seen={year:set()for year in by_year}
    for i,r in enumerate(contract['county_order']):
        assert r['key']==keys[i] and r['votes']==values[r['county_fips']] and r['rank']==i+1
        assert r['cumulative_votes']==sum(values[k]for k in ranked[:i+1]) and r['in_priority']==(i<24)
        for year,units in r['native_constituents'].items():
            for u in units:
                key=u['native_key'];assert key not in seen[year];seen[year].add(key)
                source=by_year[year][key];assert source['county_fips']==r['county_fips']
                for k in ['source_id','source_sheet','source_row','VTDID','PCTCODE','PCTNAME','MCDNAME','WARD','MAILBALLOT','unit_kind','method_warning','current_2026_equivalence']:
                    assert u[k]==source[k],(year,key,k)
                prefix='MNGOV'if year=='2022'else'USSEN';assert u['candidate_votes']==int(source[prefix+'TOTAL'])
                assert u['current_2026_equivalence']=='unavailable' and u['native_municipal_id']is None
                constituent_count+=1
    assert constituent_count==12316 and all(seen[y]==set(by_year[y])for y in seen)
    assert (contract_path.read_bytes())==contract_bytes
    out={'status':'pass_historical_dispatch_original_scope_review','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'independence':'Standalone original OOXML cell-address/relationship/duplicate-header parser; no worker code imported. Original CountyFIPS lookup, all selected native/county fields, full order and every contract constituent compared.',
         'sources':sources,'native_rows':native_counts,'complete_counties':87,'native_constituents':constituent_count,'source_field_comparisons':checks,
         'denominator':total,'top15_votes':2308744,'priority_count':24,'priority_votes':2567977,'preceding_count':23,'preceding_votes':2543408,
         'crossing':{'county':'Beltrami','county_fips':'27007','votes':24569},'remainder_count':63,'remainder_votes':621346,
         'contract_bytes':len(contract_bytes),'contract_sha256':hashlib.sha256(contract_bytes).hexdigest(),
         'scope':'Reported Senate candidates plus generic WI volume, not demonstrated valid named allocation. DFL source affiliation retained. Method/ballot discrepancies and warnings remain unallocated; no current election geography/IDs or cross-year physical join approved.'}
    p=H/'coordinator-native-contract-review.json'
    if p.exists():
        old=json.loads(p.read_text())
        if {k:v for k,v in old.items()if k!='reviewed_utc'}=={k:v for k,v in out.items()if k!='reviewed_utc'}:out['reviewed_utc']=old['reviewed_utc']
    p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()


