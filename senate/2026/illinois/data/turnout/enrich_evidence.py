#!/usr/bin/env python3
"""Independent text/metadata extraction of original primary PDFs and details.
Shared official originals are referenced by exact hash, not copied or imported
from coordinator/peer numeric analyses. Requires Poppler and beautifulsoup4.
"""
from pathlib import Path
import csv,gzip,hashlib,json,re,subprocess,tempfile
from bs4 import BeautifulSoup
D=Path(__file__).resolve().parent;STATE=D.parent.parent;S=D/'source';E=D/'extract'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    external=[];jobs=[]
    frozen=S/'external-originals.json'
    if frozen.exists():
        external=json.loads(frozen.read_text())
        jobs=[(r['id'],STATE/r['path'],r['stored_sha256'],r['raw_sha256'])for r in external]
    else:
        m=json.loads((STATE/'data/news/coordinator-federal-controls/acquisition-complete-v1.json').read_text())
        r=next(r for r in m if r['id']=='fec-2024-president-pdf');external.append(dict(r,path=r['asset_path'],source_receipt='data/news/coordinator-federal-controls/acquisition-complete-v1.json'));jobs.append((r['id'],STATE/r['asset_path'],r['stored_sha256'],r['raw_sha256']))
        reg=STATE/'data/baselines/source/registry.json';rr=json.loads(reg.read_text())
        for sid in ['fec-2020-book','fec-2022-book','isbe-2026-calendar','isbe-2026-authority-guide']:
            r=next(r for r in rr if r['id']==sid);path=(reg.parent.parent/r['path']).resolve();external.append(dict(r,path=str(path.relative_to(STATE)),source_receipt='data/baselines/source/registry.json'));jobs.append((sid,path,r['stored_sha256'],r['raw_sha256']))
    # Freeze just the relevant primary acquisition ancestors, rather than
    # duplicating the provider's large evolving receipt registry.
    parents=S/'provider-parent-receipts.json'
    if not parents.exists():
        registry=STATE/'data/baselines/source/registry.json.gz'
        if registry.exists():records=json.loads(gzip.decompress(registry.read_bytes()))
        else:records=json.loads((STATE/'data/baselines/source/registry.json').read_text())
        byid={r['id']:r for r in records};needed={r['id']for r in external if r['id']in byid};todo=list(needed)
        while todo:
            r=byid[todo.pop()];parent=r.get('parent_source_id')or r.get('parent_id')
            if isinstance(parent,str)and parent in byid and parent not in needed:needed.add(parent);todo.append(parent)
        selected=[]
        for sid in sorted(needed):
            r=dict(byid[sid]);r['provider_relative_path']=r.get('path');r['path']=str(((STATE/'data/baselines')/r['path']).resolve().relative_to(STATE));selected.append(r)
        parents.write_text(json.dumps({'scope':'Original official acquisition metadata only; independently re-extracted raw bodies, no provider numerical derivatives','original_registry_at_capture':'data/baselines/source/registry.json.gz','original_registry_stored_sha256':sha(registry.read_bytes())if registry.exists()else None,'sources':selected},indent=2)+'\n')
    for r in external:
        if r.get('source_receipt')=='data/baselines/source/registry.json':
            r['original_receipt_path_at_capture']=r['source_receipt'];r['source_receipt']='data/turnout/source/provider-parent-receipts.json';r['frozen_full_leaf_receipt']='data/turnout/source/external-originals.json'
    for p in S.glob('*.receipt.json'):
        r=json.loads(p.read_text())
        if r.get('status')!=200:continue
        f=S/r['asset'];b=gzip.decompress(f.read_bytes())
        if b.startswith(b'%PDF'):jobs.append((r['id'],f,r['stored_sha256'],r['raw_sha256']))
    for sid,p,zh,bh in jobs:
        z=p.read_bytes();b=gzip.decompress(z);assert sha(z)==zh and sha(b)==bh
        with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
            f.write(b);f.flush();out=subprocess.run(['pdftotext','-layout',f.name,'-'],capture_output=True,check=True).stdout
        (E/(sid+'.text.txt.gz')).write_bytes(gzip.compress(out,mtime=0))
    meta=[]
    for p in sorted(S.glob('detail-*.receipt.json')):
        r=json.loads(p.read_text());assert r['status']==200;b=gzip.decompress((S/r['asset']).read_bytes());assert sha(b)==r['raw_sha256'];s=BeautifulSoup(b,'html.parser')
        values={}
        for suffix in ['Name','Office','Party','FiledDate','WriteIn','StatusDate']:
            v=s.find(id='ContentPlaceHolder1_lbl'+suffix);values[suffix]=v.get_text(' ',strip=True)if v else None
        meta.append({'source_id':r['id'],'source_raw_sha256':sha(b),'historical_detail_url':r['final_url'],'fields':values,'status_qualification':'Historical database presentation; post-election metadata dates not assumed filing eligibility dates'})
    assert len(meta)==40
    (E/'candidate-detail-metadata.json').write_text(json.dumps(meta,indent=2)+'\n');(S/'external-originals.json').write_text(json.dumps(external,indent=2)+'\n')
    fec=gzip.decompress((E/'fec-2024-president-pdf.text.txt.gz').read_bytes()).decode()
    assert re.search(r'IL\s+1,569\s+518\s+5,633,310',fec)
    # Keep source spelling and vote counts; no alleged VP/alias merge.
    rows=list(csv.DictReader((E/'statewide-source-rows.csv').open()));x=[r for r in rows if r['year']=='2024'];assert sum(int(r['votes'])for r in x)==5633310
    checks={'fec2024_IL_West_scattered_total_row_exact':True,'state27_named_reporting_rows_total':5633310,'fec_is_separate_publication_of_state_returns_not_independent_underlying_votes':True,'candidate_detail_metadata_rows':40,'local_source_notes':{'chicago':'Official proclamation PDF printed page9 (PDF10) candidate total1,001,481; registration1,498,873; turnout1,018,359. Native three printed totals match. Genericwrite-in10,189 equals local named remainder here only; no statewide inference.','bloomington':'Official write-in list totals204, with explicit combined labels Oliver/Mike ter Maat, Stein/Rudolph Ware, West/Melina Abdullah. No allocation among state raw names/native units.','galesburg':'Official scanned canvass printedpage5(PDF8) has genericwrite-in72, not named write-in allocation.21nativecontexts include20precinctlabels plus blank administrative category context.','mclean':'Official2024 clerk summary has81native source precincts and genericwrite-in455, separate from Bloomington commission.','other_city_sources':'Bounded parent/linked canvass/vendor captures retained, not accepted as complete native valid-write-in allocation.'},'no_native_legal_writein_allocation_created':True}
    cook=gzip.decompress((E/'cook-postelection-2024.text.txt.gz').read_bytes()).decode()
    for literal in ['451,654','14,742','192,412','431,134','658,808','1,089,942','1,640,040']:assert literal in cook
    methods={'source_id':'cook-postelection-2024','authority_id':'16','scope':'Suburban Cook only; historical election ballot methods, not presidential candidate votes','source_printed_page':5,'source_pdf_page_1based':cook[:cook.find('Suburban Cook: Pre-Election Ballots Cast')].count('\f')+1,'source_table':'Suburban Cook: Pre-Election Ballots Cast in Presidential Elections','2024':{'Registered Voters':1640040,'Early Voting':451654,'Grace Period/In-Person Absentee':14742,'Mail Voting':192412,'Election Day*':431134,'Pre-Election Ballots':658808,'Total Ballots Cast':1089942},'2020':{'Registered Voters':1669040,'Early Voting':435413,'Grace Period/In-Person Absentee':17664,'Mail Voting':460281,'Election Day*':274659,'Pre-Election Ballots':913358,'Total Ballots Cast':1188017},'footnote':'*Includes19,195Election Day Registration voters (2024).','candidate_method_counts':None,'statewide_method_coverage':'unavailable in inspected state native exports; local figures never generalized','registration_source_status':'Report table vintage; some report maps retain FINAL DRAFT01.23.25@1030AM labels.'}
    for y in ['2024','2020']:
        a=methods[y];assert a['Early Voting']+a['Grace Period/In-Person Absentee']+a['Mail Voting']==a['Pre-Election Ballots'];assert a['Pre-Election Ballots']+a['Election Day*']==a['Total Ballots Cast']
    (E/'local-ballot-method-controls.json').write_text(json.dumps(methods,indent=2)+'\n')
    # Verify historical general dates and all printed/named Senate controls
    # against separate FEC publications, without importing their derivatives.
    for sid,pattern,counts in [('fec-2020-book',r'ILLINOIS\s+March 17th\s+November 3rd',['3,278,930','2,319,870','237,699','75,673','56,711','5,968,901']),('fec-2022-book',r'ILLINOIS\s+June 28th\s+November 8th',['2,329,136','1,701,055','68,671','4,098,896'])]:
        t=gzip.decompress((E/(sid+'.text.txt.gz')).read_bytes()).decode();assert re.search(pattern,t)
        for n in counts:assert n in t
    checks['FEC2020_2022_general_dates_and_Senate_control_strings_verified']=True
    checks['local_method_control_sums_pass']=True
    (E/'federal-local-evidence-review.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps({'original_PDFs_independently_extracted':len(jobs),'detail_pages':40,'fec2024_control':'pass'}))
if __name__=='__main__':main()
