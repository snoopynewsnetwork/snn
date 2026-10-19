#!/usr/bin/env python3
"""Reproduce complete PDF text, legal section and vendor balance inspections.
Saved entities are authoritative; scan text absence stays explicitly unknown.
"""
import gzip,json,re,subprocess,sys,collections,csv,io
sys.dont_write_bytecode=True
from acquire import D,readj,writej,decoded,sha
from htmlkit import Tree
def main():
    (D/'extracts').mkdir(exist_ok=True);out=[]
    for p in sorted((D/'receipts').glob('*.json')):
        r=readj(p)
        if r.get('http_status')!=200:continue
        b=decoded(r['id'])
        if not b.startswith(b'%PDF'):continue
        t=subprocess.run(['pdftotext','-layout','-','-'],input=b,capture_output=True,check=True).stdout;pages=t.decode(errors='replace').split('\f');pages=pages[:-1]if pages[-1]==''else pages
        (D/'extracts'/(r['id']+'.txt.gz')).write_bytes(gzip.compress(t,mtime=0))
        senate=[dict(actual_pdf_page=i+1,text=text)for i,text in enumerate(pages)if re.search(r'Senat|Sen\.',text,re.I)]
        out.append(dict(source_id=r['id'],pages=len(pages),text_layer_nonempty_pages=sum(bool(x.strip())for x in pages),senate_pages=senate,methods_literal_observed=sorted(set(re.findall(r'Election Day|Early Voting|Provisional|Absentee|TOTAL|Total Votes Cast|Overvotes|Undervotes|Write-In Totals|Write.In Scatterings|ELECTION DAY|EARLY VOTING',t.decode(errors='replace')))),first_page=pages[0]if pages else '',classification='Complete original text derivative. Election identity and operative dates remain source-specific; no November vote admission. Textless scans require visual/manual inspection for numeric use.'))
    writej(D/'pdf-inspections.json',out)
    s=decoded('law-chapter32-retry1').decode();ms=list(re.finditer(r'<strong>(32-[\d.]+)\.\s*\n',s));sections=[]
    for i,m in enumerate(ms):
        text=s[m.start():ms[i+1].start()if i+1<len(ms)else len(s)];sections.append(dict(statute=m[1],source_byte_character_position=m.start(),html=text,text=Tree(text).root.text(),source_id='law-chapter32-retry1'))
    writej(D/'law-sections.json',sections)
    vendor=[]
    for root in ['clarity-portal-cass-web-config','clarity-portal-sarpy-web-config','clarity-cass-extra-235-web-config']:
        conf=json.loads(decoded(root));version=decoded(root+'-version').decode().strip();settings=json.loads(decoded(root+'-electionsettings'));summary=json.loads(decoded(root+'-sum'));detail=json.loads(decoded(root+'-details'));vt=json.loads(decoded(root+'-vt'));status=json.loads(decoded(root+'-status'))
        summaries={x['K']:x for x in summary['Contests']};details={x['K']:x for x in detail['Contests']};methods={x['K']:x for x in vt['Contests']};senates=[]
        for key,r in summaries.items():
            assert len(r['CH'])==len(r['V'])==len(r['P'])==len(r['CHAggId']);assert sum(r['V'])==r['T'],(root,key)
            if key in details:
                d=details[key];assert len(d['P'])==len(d['V'])==len(d['T']);assert all(len(x)==len(r['CH'])for x in d['V']);assert [sum(v[i]for v in d['V'])for i in range(len(r['CH']))]==r['V'],(root,key,'detail')
            if key in methods:
                m=methods[key];assert len(m['Votes'])==len(r['CH']);assert all(len(v)==len(vt['Types'])for v in m['Votes']);assert [sum(v)for v in m['Votes']]==r['V'],(root,key,'methods')
            if 'Senat'in r['C']:
                senates.append(dict(summary_complete=r,detail_complete=details.get(key),method_complete=methods.get(key)))
        assert len(status['P'])==len(status['S'])==len(status['R'])==len(status['B'])==len(status['C'])==len(status['CONTEST'])
        priorid=root+'-prior-sum';priorreceipt=readj(D/'receipts'/(priorid+'.json'));comparison=dict(source_id=priorid,status=priorreceipt['http_status'],complete_entity_retained=True)
        if priorreceipt['http_status']==200:
            prior=json.loads(decoded(priorid));ps={r['K']:r for r in prior['Contests']};comparison['complete_senate_prior_objects']=[r for r in prior['Contests']if 'Senat'in r['C']];comparison['changed_senate_summary_keys']=[r['K']for r in summary['Contests']if 'Senat'in r['C']and ps.get(r['K'])!=r]
        ed=settings['settings']['electiondetails']
        vendor.append(dict(config_source_id=root,complete_configuration=conf,version=version,source_clock=settings['websiteupdatedat'],election_identity={k:ed.get(k)for k in ['electionid','internalname','electiondate','istestmode','chkisfinalupload','chkiscanvasupload']},literal_zone_config={k:settings['settings'].get(k)for k in ['timezoneoffset','isdaylightsaving']},status_complete=status,methods_order=vt['Types'],complete_senate_contexts=senates,prior_version_comparison=comparison,all_contest_schema_balance_checks=len(summaries),current_November_returns=False,qualification='Primary2026 or historical2024. Source configuration/final flags, publication headers and zero state counters remain separately scoped. Version sample is not measured election-night cadence.'))
    writej(D/'vendor-inspections.json',vendor)
    # Store exact constructor evidence with positions in the full originals.
    patterns={'state-app-retry1':['var ServiceRoot','GetCandidates','SearchResults.aspx?ID='], 'code-0':['function BuildCounty','GetMapData?type=','category=CTY'], 'code-1':['function BuildPrecincts','GetMapData?type=','category=PREC'], 'code-4':['class BaseEnrService','FileName["Version"]','FileName["WebConfig"]','./${FileName.WebConfig}','getCountyVersion(state']}
    evidence=[]
    for sid,needles in patterns.items():
        text=decoded(sid).decode(errors='replace')
        for needle in needles:
            i=text.find(needle);assert i>=0,(sid,needle);evidence.append(dict(source_id=sid,decoded_character_position=i,needle=needle,excerpt=text[max(0,i-100):i+1800]))
    writej(D/'constructor-evidence.json',evidence)
    exports=[]
    for sid in ['export-5','export-6']:
        rows=list(csv.reader(io.StringIO(decoded(sid).decode('utf-8-sig'))));assert len(rows[0])==14 and all(len(r)==15 and r[-1]==''for r in rows[1:]);sen=[dict(source_row_1based=i+2,complete_fields=r)for i,r in enumerate(rows[1:])if r[0]=='13224'];assert len(sen)==5 and all(r['complete_fields'][11]=='0'for r in sen)
        exports.append(dict(source_id=sid,complete_header=rows[0],unheaded_trailing_empty_column_preserved=True,rows=len(rows)-1,Senate_complete_rows=sen,source_clock_values=sorted({r['complete_fields'][9]for r in sen}),source_timezone=None,API_clock_null_is_distinct=True,qualification='Literal CSV CurrentDateTime differs from null API time and October6HTML clock. Generated/request timing is not vote-publication cadence or finality. BallotOrder is empty here, not copied from API.'))
    writej(D/'current-export-inspections.json',exports)
    print(json.dumps(dict(PDFs=len(out),complete_PDF_pages=sum(x['pages']for x in out),legal_sections=len(sections),vendor_elections=len(vendor),vendor_contests_checked=sum(x['all_contest_schema_balance_checks']for x in vendor),constructor_excerpts=len(evidence))))
if __name__=='__main__':main()
