"""Original-based bounded PDF controls, complete token positions and previews.
Uses Poppler locally, no peer parser/calculator and no current native joins.
"""
from pathlib import Path
import gzip,json,re,subprocess
from collections import Counter,defaultdict
import acquire as a

def pdftext(b):return subprocess.run(['pdftotext','-layout','-','-'],input=b,stdout=subprocess.PIPE,check=True).stdout.decode('utf8','replace')
def n(s):return int(s.replace(',',''))
def run(render=False):
    rows=[json.loads(p.read_bytes())for p in sorted((a.OUT/'receipts').glob('*.json'))]
    rr={r['id']:r for r in rows};out=a.OUT/'pdf-evidence';out.mkdir(exist_ok=True)
    pike=[];proof=[]
    ids=[r['id']for r in rows if '-sample-'in r['id'] and r.get('status')==200 and r['id'].startswith(('county-28113','county-28121'))]
    for sid in ids:
        r=rr[sid];b=a.body(r)
        if not b.startswith(b'%PDF'):continue
        text=pdftext(b);path=out/(a.sha(b)+'.txt');path.write_text(text)
        cp=subprocess.run(['pdftotext','-bbox-layout','-','-'],input=b,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        attempts=[dict(command='pdftotext -bbox-layout - -',exit=cp.returncode,stderr=cp.stderr.decode('utf8','replace'))]
        if cp.returncode:
            cp=subprocess.run(['pdftotext','-bbox','-','-'],input=b,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            attempts.append(dict(command='pdftotext -bbox - -',exit=cp.returncode,stderr=cp.stderr.decode('utf8','replace')))
        bx=cp.stdout
        xp=out/(a.sha(b)+('.bbox.xml.gz'if cp.returncode==0 else '.failed-bbox-stdout.gz'));xp.write_bytes(gzip.compress(bx,mtime=0))
        proof.append(dict(source=sid,source_raw_sha256=a.sha(b),complete_text=a.pin(path),complete_word_positions=a.pin(xp)if cp.returncode==0 else None,failed_position_stdout=a.pin(xp)if cp.returncode else None,extraction='Complete original PDF and layout-text pages/row order retained. Bbox positions only where successful; Poppler errors are explicit. No glyph-independent claim for scan-only pages.',position_extraction_attempts=attempts))
        if '/2024_general/' in r['requested_url']:
            sec=text.split('Senate United States',1)[1].split('3rd Congressional',1)[0]
            candidates={name:n(re.search(re.escape(name)+r'\s+([\d,]+)',sec)[1])for name in ['Ty Pinkins','Roger F. Wicker']}
            controls={k:n(re.search(re.escape(k)+r'\s+([\d,]+)',sec)[1])for k in ['Write-In Totals','Total Votes Cast','Contest Totals']}
            assert sum(candidates.values())+controls['Write-In Totals']==controls['Total Votes Cast']
            label=re.search(r'\(\d+\) [^\n]+',text)
            pike.append(dict(source=sid,requested_url=r['requested_url'],source_raw_sha256=a.sha(b),label_literal=label[0]if label else None,candidates=candidates,controls=controls,footer_clocks=re.findall(r'(?:Precinct Summary|Election Summary) - [^\n]+',text)))
    dw=next(x for x in pike if x['requested_url'].endswith('/DW.pdf'))
    assert dw['candidates']=={'Ty Pinkins':7130,'Roger F. Wicker':8205}
    assert dw['controls']=={'Write-In Totals':36,'Total Votes Cast':15371,'Contest Totals':15607}
    constituents=[x for x in pike if x is not dw]
    dup=defaultdict(list)
    for x in constituents:dup[x['source_raw_sha256']].append(x['requested_url'])
    duplicate=[v for v in dup.values() if len(v)>1]
    # Exposed hrefs are not sufficient proof of disjointness: preserve duplicate
    # originals and the diagnostic sum without silently fitting the county total.
    observed_sums={name:sum(x['candidates'][name]for x in constituents)for name in dw['candidates']}
    assert len(constituents)==25 and observed_sums==dw['candidates'] and not duplicate
    rank_sid='county-28121-home-child-3-deep-2-sample-0';rt=pdftext(a.body(rr[rank_sid]));sec=rt.split('For United States Senate',1)[1].split('\f',1)[0]
    columns=['Absentee Voting','Election Day Voting','Affidavit Voting','Total'];rankrows=[]
    for line in sec.splitlines():
        label=None
        for possible in ['Roger F. Wicker','Ty Pinkins','Cast Votes:','Undervotes:','Overvotes:','Write-ins:']:
            if line.strip().startswith(possible):label=possible;break
        if label:
            nums=re.findall(r'(?<![\w.])[\d,]+(?:\.\d+)?%?',line[len(line)-len(line.lstrip()):][len(label):])
            vals=[n(x)for x in nums if not x.endswith('%')]
            assert len(vals)==4,(line,vals);assert sum(vals[:3])==vals[3]
            rankrows.append(dict(ordinal=len(rankrows),label_literal=label,party_cell_literal=''if label in ['Roger F. Wicker','Ty Pinkins']else None,values=vals,raw_line=line))
    assert len(rankrows)==7 and [r['label_literal']for r in rankrows[-2:]]==['Write-ins:','Write-ins:']
    assert rankrows[0]['values']==[11017,39574,951,51542] and rankrows[1]['values']==[2904,14016,347,17267]
    assert [sum(r['values'][i]for r in rankrows[:2])for i in range(4)]==rankrows[2]['values']
    ballot_controls=[sum(rankrows[j]['values'][i]for j in [2,3,4,5,6])for i in range(4)]
    assert ballot_controls==[14333,54758,1329,70420]
    contract=json.loads((a.ROOT/'data/turnout/priority-set.json').read_bytes())
    rankbasis=[x for x in contract['all_unit_order']if x['parent_county_fips']=='28121']
    assert {name:sum(x['candidate_votes'][name]for x in rankbasis)for name in ['Ty Pinkins','Roger F. Wicker']}=={'Ty Pinkins':17267,'Roger F. Wicker':51542}
    pikebasis=[x for x in contract['all_unit_order']if x['parent_county_fips']=='28113']
    assert {name:sum(x['candidate_votes'][name]for x in pikebasis)for name in dw['candidates']}==dw['candidates']
    render_jobs={'fifth-sept9-doc255':[1,2],'clarification-sept10-child-2':[1],'sample-ballot':[1],rank_sid:[1],dw['source']:[1,2],'admin-rule-current-linked-confirmation':[6,7,8]}
    renders=[]
    for sid,pages in render_jobs.items():
        b=a.body(rr[sid])
        for page in pages:
            prefix=out/(sid+'-p'+str(page));png=Path(str(prefix)+'.png')
            if render:
                subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-scale-to','1600','-png','-',str(prefix)],input=b,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if png.exists():renders.append(dict(source=sid,raw_sha256=a.sha(b),actual_pdf_page=page,png=a.pin(png)))
    result=dict(status='pass_bounded_original_controls_with_explicit_extraction_limits',
                complete_text_position_derivatives=proof,pike2024_downloads=pike,
                pike2024_duplicate_original_groups=duplicate,pike2024_download_position_sum_diagnostic=observed_sums,
                pike2024_county_DW=dw,pike2024_disjoint_native_join_approved=False,
                rankin2024=dict(source=rank_sid,columns_in_source_order=columns,rows_in_source_order=rankrows,computed_all_candidate_control_sums=ballot_controls,printed_ratio='70420 of 101036 = 69.70%',reported_precincts_literal='46 of 46 = 100.00%',source_clock_literal='11/15/2024 2:33 PM; timezone absent',current_method_definition_approved=False),
                independent_county_to_SEMS_named_controls_pass=['Pike2024','Rankin2024'],renders=renders,current_counts_admitted=False)
    a.save(a.OUT/'sample-controls.json',result);return result
if __name__=='__main__':
    import sys
    r=run('--render'in sys.argv);print(r['status'],r['pike2024_download_position_sum_diagnostic'],r['pike2024_duplicate_original_groups'])
