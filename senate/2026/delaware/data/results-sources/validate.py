"""Offline raw/whole-field/semantic/order/coverage/negative/ownership QA."""
import collections,csv,gzip,hashlib,io,json,re,sys
from pathlib import Path
from freeze import R,S,load,pin,sha,sem,pointer
from extract import text,write
checks=0
def ck(v,label):
    global checks
    assert v,label;checks+=1
def admission(v):
    return bool(v.get('http')==200 and v.get('electiondate')=='2026-11-03' and v.get('office')=='U.S. Senator' and v.get('status')not in ['TEST','SETUP','ZERO_SETUP'] and v.get('genuine_changing_return') is True and v.get('identity_proved') is True)
def main():
    f=load(R/'frozen-references.json.gz');cache={};refs=0
    ck(f['external_authority_path']=='data/coordinator-priority-acceptance.json','acceptance path only')
    ck('acceptance_sha256'not in f and 'acceptance_bytes'not in f,'no reverse acceptance pin')
    for e in [f['contract']]+f['complete_companions']+f['full_asset_references']+f['producer_seals']:
        actual=pin(S/e['path']);ck(all(actual[k]==e[k]for k in actual),'full file pin '+e['path'])
        if e in f['complete_companions']:
            obj=load(S/e['path']);cache[e['path']]=obj;ck(sem(obj)==e['full_semantic_sha256'],'whole companion semantic');ck(len(obj)==e['complete_length'],'whole companion length')
            if 'complete_header'in e:ck(obj[0]==e['complete_header'],'full CSVheader')
            if 'complete_reconstructed_bytes'in e:
                b=gzip.decompress((S/e['path']).read_bytes());ck(len(b)==e['complete_reconstructed_bytes'] and sha(b)==e['complete_reconstructed_sha256'],'full gzip reconstruction')
    c=load(S/f['contract']['path']);cache[f['contract']['path']]=c
    ck(len(c)==len(f['root_fields'])==42 and len(f['complete_companions'])==42 and len(f['complete_objects'])==16388,'full frozen scope')
    for v in f['root_fields']:ck(sem(pointer(c,v['pointer']))==v['full_recursive_semantic_sha256'],'root wholefield semantic')
    for v in f['complete_objects']:
        if v['file']not in cache:cache[v['file']]=load(S/v['file'])
        obj=cache[v['file']];obj=obj[v['JSONL_record']-1]if'JSONL_record'in v else pointer(obj,v['pointer'])
        ck(sem(obj)==v['full_recursive_semantic_sha256'],'full object semantic')
    ck(c['formal_coordinator_acceptance']is False and c['current_geography_approved']is False,'frozen producer falseflags')
    # Every saved request: exact whole rawbody/storedbody/redirects and complete header pairs.
    requests=[]
    for p in sorted((R/'raw').glob('*.receipt.json')):
        v=load(p);requests.append(v)
        for entity in [v]+v['redirects']:
            b=(R/entity['asset']).read_bytes();raw=gzip.decompress(b)
            ck(len(b)==entity['stored_bytes'] and sha(b)==entity['stored_sha256'],'stored HTTPentity')
            ck(len(raw)==entity['raw_bytes'] and sha(raw)==entity['raw_sha256'],'complete HTTPentity')
            ck(len(b)<40_000_000,'strict object size')
        ck(v['method']=='GET' and v['body']is None and v['November_counts_admitted']is False,'bounded source only GET')
        ck(v['status']is None or isinstance(v['response_headers'],list),'all headers retained')
    index=load(R/'source-index.json');ck({v['source_id']for v in index}=={v['id']for v in requests},'complete request inventory')
    # All current HTML full-field/source slices, including blank cells and captions.
    for v in requests:
        p=R/f'extracts/{v["id"]}.json.gz'
        if not p.exists():continue
        d=load(p)
        if 'tables'not in d:continue
        t=gzip.decompress((R/v['asset']).read_bytes()).decode('utf-8-sig')
        for table in d['tables']:
            raw=t[table['source_start']:table['source_end']];ck(raw.lower().startswith('<table') and raw.lower().rstrip().endswith('</table>'),'whole current table '+v['id'])
            if table['caption']:
                cap=table['caption'];ck(t[cap['source_start']:cap['source_end']]==cap['raw_html'],'full caption/party scope')
            for row in table['rows']:
                for cell in row['cells']:
                    raw=t[cell['source_start']:cell['source_end']];inner=re.sub(r'^<(td|th)\b[^>]*>|</(?:td|th)\s*>$','',raw,flags=re.S|re.I)
                    ck(text(inner)==cell['text'],'exact current cell text incl blank')
        for script in d['scripts']:
            raw=t[script['source_start']:script['source_end']];ck(script['body']==re.search(r'<script\b[^>]*>(.*?)</script\s*>',raw,re.S|re.I)[1],'complete inline script')
    pri=load(R/'priority-entry-investigations.json.gz');rem=load(R/'remainder-entry-investigations.json.gz');parents=load(R/'parent-investigations.json')
    ck(len(pri)==311 and len(rem)==219 and len(parents)==3,'311+219/all3')
    ck([v['native_key']for v in pri]==c['ordered_priority_keys'],'exact priority order')
    ck([v['native_key']for v in rem]==c['ordered_remainder_keys'],'exact remainder order')
    keys=[v['native_key']for v in pri+rem];ck(len(set(keys))==530 and set(keys)=={v['native_key']for v in c['full_order']},'full unique530')
    ck(sum(v['votes']for v in c['full_order'])==500606 and c['priority_votes']==400539 and c['preceding_votes']==399708 and c['remainder_votes']==100067,'exact denominator/minimum/remainder')
    ck(399708*5<500606*4<=400539*5 and c['crossing_key']=='ElectionDistrict0807','exact integer threshold')
    for i,v in enumerate(pri+rem):
        ck(v['historical_parent']in [x['parent']for x in parents],'historical parent only')
        ck(len(v['complete_source_candidate_rows'])==3,'all3 complete candidate refs')
        ck(all(v[k]is None for k in ['current_election_leaf','current_geography','current_method','current_candidate_IDs','current_contest_ID','current_reporting_ID']) and v['live_approval']is False,'no inferred native current joins')
        ck(all(v[k]for k in ['access_gap','legal_gap','candidate_gap','statistics_gap','native_compatibility_gap']),'entry-specific gap fields')
    # Follow every embedded full pin/pointer in the built investigation datasets.
    def visit(v):
        nonlocal refs
        if isinstance(v,dict):
            if isinstance(v.get('file'),dict) and 'path'in v['file']:
                e=v['file'];actual=pin(S/e['path']);ck(all(actual[k]==e[k]for k in actual),'embedded full pin');refs+=1
                if 'pointer'in v and v['pointer']:
                    if e['path']not in cache:cache[e['path']]=load(S/e['path'])
                    pointer(cache[e['path']],v['pointer']);ck(True,'resolvable full object pointer')
                if 'JSONL_record'in v:
                    if e['path']not in cache:cache[e['path']]=load(S/e['path'])
                    ck(0<v['JSONL_record']<=len(cache[e['path']]),'resolvable full JSONLrecord')
            for x in v.values():visit(x)
        elif isinstance(v,list):
            for x in v:visit(x)
    for v in [pri,rem,parents,load(R/'full-hierarchy.json'),load(R/'source-only-unavailable-cases.json')]:visit(v)
    hierarchy=load(R/'full-hierarchy.json');ck(hierarchy['county_children']==c['county_native_hierarchy'],'full hierarchy all fields')
    ck(len(c['all_available_source_constituents'])==1495 and len(c['administrative_cases'])==6 and len(c['unavailable_administrative_cases'])==10,'native union and unavailable cases')
    # Detect cross-election CSV even though HTTP200 and filename PR2026.
    rows=list(csv.DictReader(io.StringIO(gzip.decompress((R/'raw/primary-csv.body.gz').read_bytes()).decode('utf-8-sig'))))
    expected=['office','candidatename','partyname','electiondate','machinevotessum','absenteevotessum','earlyvotessum','totalvotessum','totalvotespercentage','xmlreporttime','electionname']
    ck(list(rows[0])==expected and len(rows)==829 and len({v['electiondate']for v in rows})==12,'complete CSV schema/multiple elections')
    senate=[x for x in rows if x['office']=='U.S. Senator'];current=[x for x in senate if x['electiondate']=='2026-09-15T00:00:00.000']
    ck(len(senate)==17 and len(current)==6,'row-level primary scope')
    ck(not any(x['electiondate'].startswith('2026-11-03')for x in rows),'no November2026CSV rows')
    ck(all(x['electionname']=='2026 Primary Election' and x['xmlreporttime']=='2026-09-18T14:47:00.000'for x in current),'primary sourceclock/name')
    ck(all(int(x['machinevotessum'])+int(x['absenteevotessum'])+int(x['earlyvotessum'])==int(x['totalvotessum'])for x in current),'actual primary method sums')
    # HTML county columns reconcile to each state primary sample; alternative views excluded.
    d=load(R/'extracts/primary.json.gz');t=gzip.decompress((R/'raw/primary.body.gz').read_bytes()).decode();lo=t.index('id="cty"');hi=t.index('id="wilm"');matched=0
    for table in d['tables']:
        if lo<table['source_start']<hi and 'USSenator'in str(table['attrs']):
            header=[x['normalized_text']for x in table['rows'][0]['cells']]
            for row in table['rows'][1:]:
                fields=dict(zip(header,[x['normalized_text']for x in row['cells']]));sample=next(x for x in current if x['candidatename']==fields['Candidate Name'])
                ck(sum(int(fields[p])for p in ['New Castle','Kent','Sussex'])==int(fields['State'])==int(sample['totalvotessum']),'all3parent sample arithmetic');matched+=1
    ck(matched==6,'complete current primary county samples')
    candidates=load(R/'extracts/current-candidate-literal-rows.json.gz');ck(len(candidates)==2 and all(v['current_vendor_choice_IDs']is None and v['final_signed_later_exhaustiveness']is False for v in candidates),'current qualified/declared scope')
    ck(len(candidates[1]['all_tables'])==4,'all four writein views retained')
    # A nonvote field mutation must fail full semantic integrity even if votes match.
    sample=cache['data/turnout/extracts/candidate-rows.jsonl.gz'][0];mut=json.loads(json.dumps(sample));mut['party']='MUTATED';ck(sem(mut)!=sem(sample) and mut['numeric']==sample['numeric'],'wholefield negative party mutation')
    cases=load(R/'negative-fixtures.json')
    for v in cases:ck(admission(v['input'])==v['expected_admitted'],v['name'])
    ck(all(not admission(dict(http=v.get('status'),electiondate=None))for v in requests),'HTTP200alone cannot admit')
    ck(load(R/'build-coverage.json')['current_outstanding_ballots']is None,'unknown remaining pool')
    # Source-specific findings and semantic gates that a generic link list would miss.
    primary=gzip.decompress((R/'extracts/primary.txt.gz').read_bytes()).decode()
    ck('do not mean all ballots are counted'in primary and 'updated manually'in primary,'primary completion distinctions')
    law=gzip.decompress((R/'extracts/law-c055.txt.gz').read_bytes()).decode();ck('5509A.'in law and '30 days before'in law and 'before the polls close'in law,'operative cure/processing scope')
    hb=gzip.decompress((R/'extracts/hb444-engrossed.txt.gz').read_bytes()).decode();ck('takes effect on July 1, 2027'in hb,'future effective law negative')
    report=S/'official-results.md';tx=report.read_text()
    for href in re.findall(r'\]\(([^)]+)\)',tx):
        if '://'in href or href.startswith('#'):continue
        target=report.parent/href.split('#')[0]
        deferred=target in [R/'validation.json',R/'manifest.json'] and '--check'not in sys.argv
        ck(target.exists() or deferred,'relative report link '+href)
    ck(all(p.stat().st_size<40_000_000 for p in R.rglob('*')if p.is_file()),'strict maximum stored object size')
    result=dict(status='pass',checks=checks,requests=len(requests),complete_reference_checks=16388,embedded_full_references=refs,priority=311,remainder=219,full_native=530,parents=3,CSV_rows=829,CSV_election_dates=12,negative_fixtures=len(cases),offline=True,current_geography_approved=False,current_November_returns_admitted=False,current_choice_or_reporting_IDs_approved=False,live_cadence_or_exact_remainder_approved=False,collector_or_probability_approval=False)
    if '--check'in sys.argv:ck(load(R/'validation.json')==result,'read-only validation exact')
    else:write('validation.json',result)
    print('PASS',result['checks'],'offline checks;',len(requests),'full request receipts;',refs,'embedded full references')
if __name__=='__main__':main()
