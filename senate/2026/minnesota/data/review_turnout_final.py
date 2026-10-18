#!/usr/bin/env python3
"""Coordinator final turnout manifest, county fields and original named-WI appendix."""
from pathlib import Path
import collections,csv,datetime,gzip,hashlib,io,json,re,runpy,subprocess
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data';T=D/'turnout'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_text())
def main():
    mf=load(T/'asset-manifest.json');assert len(mf['assets'])==61
    for r in mf['assets']:
        b=(ROOT/r['path']).read_bytes();assert len(b)==r['bytes']<40000000 and sha(b)==r['sha256'],r['path']
    for r in mf['shared_original_references']:
        b=(ROOT/r['path']).read_bytes();assert sha(b)==r['stored_sha256'];b=gzip.decompress(b)
        assert len(b)==r['raw_bytes']and sha(b)==r['raw_sha256']
    ns=runpy.run_path(str(D/'review_priority.py'));raw=ns['raw']('sos-2020-canvass-original')
    text=subprocess.run(['pdftotext','-layout','-','-'],input=raw,capture_output=True,check=True).stdout.decode();lines=text.split('\n')
    named=list(csv.DictReader((T/'source/named-writeins-2020.csv').open()));assert len(named)==522
    sums=collections.Counter();counties=collections.Counter()
    for r in named:
        line=lines[int(r['pdftotext_line'])-1].strip();label=r['source_county_label'];assert line.startswith(label)
        tokens=line[len(label):].split();assert all(re.fullmatch(r'\d+',x)for x in tokens)
        assert int(tokens[int(r['source_table_candidate_column'])-1])==int(r['votes'])
        sums[r['source_candidate_label']]+=int(r['votes']);counties[r['county_fips']]+=int(r['votes'])
    assert len(counties)==87 and list(sums.values())==[0,2,5,3,0,22]and sum(sums.values())==32
    main=list(csv.DictReader((D/'county-turnout.csv').open()));contract=load(T/'priority-set.json')
    assert len(main)==87 and [r['county_key']for r in main]==contract['complete_ordered_county_keys']
    originals={}
    for year in [2024,2022,2020]:
        rr=list(csv.DictReader((T/f'county-controls-{year}.csv').open()));originals[str(year)]={r['county_fips']:r for r in rr}
    checks=0
    for i,r in enumerate(main):
        fips=r['county_fips'];assert int(r['rank'])==i+1 and int(r['minimum80'])==(i<24)
        assert int(r['senate_2024_total'])==int(originals['2024'][fips]['USSENTOTAL'])
        for year,table in originals.items():
            for k,v in table[fips].items():
                if year+'_'+k in r:assert r[year+'_'+k]==v;checks+=1
        for prefix in ['2024_USSEN','2024_USPRS','2022_MNGOV','2020_USSEN']:
            for field in ['blank','undervote','overvote','valid_named_writein']:assert r[prefix+'_'+field]==''
        assert int(r['2020_USSEN_named_writein_report_total'])==counties[fips]
        assert int(r['2020_USSEN_generic_minus_named_scope_gap'])==int(originals['2020'][fips]['USSENWI'])-counties[fips]
    c=(T/'priority-set.json').read_bytes();assert sha(c)=='b60b0bc4fed0c0b8618b6f851cc8f25d3c963bbd3ea12debecc5995dff54ceb1'and len(c)==9885383
    a=load(D/'coordinator-priority-acceptance.json');assert a['accepted']and sha((D/a['contract']).read_bytes())==a['contract_sha256']
    for r in a['peer_agreement_witnesses']:
        b=(ROOT/r['path']).read_bytes();assert len(b)==r['bytes']and sha(b)==r['sha256']
    out={'status':'pass_turnout_final_freeze_historical_scope_only','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owned_asset_hashes':61,'shared_original_hashes':len(mf['shared_original_references']),'county_rows':87,'county_source_fields':checks,'fresh_primary_PDF_named_WI_cells':522,'separate_named_WI_report_total':32,'generic_WI_scope':2261,'unattributed_difference':2229,'contract_sha256':sha(c),'frozen_turnout_report_sha256':sha((ROOT/'turnout.md').read_bytes()),'final_turnout_manifest_sha256':sha((T/'asset-manifest.json').read_bytes()),'scope':'Final turnout original/hash/county checks and immutable peer-witness conservation; named appendix overlaps generic, no additive or native allocation. Method/current geography/IDs remain unapproved.'}
    p=D/'coordinator-turnout-final-review.json'
    if p.exists():
        old=load(p)
        if {k:v for k,v in old.items()if k!='checked_utc'}=={k:v for k,v in out.items()if k!='checked_utc'}:out['checked_utc']=old['checked_utc']
    p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
