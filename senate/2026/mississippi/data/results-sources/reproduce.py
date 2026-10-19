"""Full offline frozen audit. Default is strictly read-only and network-free.
--write-validation is a pre-freeze packaging step, then seal_manifest.py.
"""
from pathlib import Path
import ast,csv,gzip,json,re,sys
from collections import Counter
from urllib.parse import unquote,urlparse
import acquire as a
import frozen_scope as f
from seal_manifest import owned

def run(write=False):
    checks=[]
    def check(name,value,details=None):
        assert value,(name,details)
        checks.append(dict(name=name,pass_=True,details=details))
    frozen,contract,v2,all11,hist,components=f.run()
    saved=json.loads((a.OUT/'frozen-scope-validation.json').read_bytes())
    f.ordered_equal(frozen,saved)
    check('complete frozen contract, all canonical objects/order/fields and original hashes',True,dict(original_publication_references=len(frozen['originals']),dependency_files=len(frozen['dependencies']),complete_v2_all11_field_comparisons=frozen['preferred_v2_to_turnout_field_checks'],label_representations_retained=len(frozen['retained_label_representation_differences'])))
    cache={}
    def resolve(ref):
        p=ref['path']
        if p not in cache:
            b=(a.ROOT/p).read_bytes();check('read-only exact full body '+p,len(b)==ref['stored_bytes']and a.sha(b)==ref['stored_sha256'])
            raw=gzip.decompress(b)if p.endswith('.gz')else b;cache[p]=json.loads(raw)
        obj=cache[p]
        for token in ref.get('json_pointer','').split('/')[1:]:
            token=token.replace('~1','/').replace('~0','~');obj=obj[int(token)]if isinstance(obj,list)else obj[token]
        return obj
    scope=json.loads((a.OUT/'scope-reference.json').read_bytes())
    check('external historical acceptance path only',scope['external_acceptance_path_only']==f.ACCEPTANCE and set(scope['entire_final_contract'])=={'path','stored_bytes','stored_sha256','json_pointer','storage'})
    f.ordered_equal(resolve(scope['entire_final_contract']),contract)
    f.ordered_equal(resolve(scope['complete_v2_body']),v2)
    f.ordered_equal(resolve(scope['complete_preferred_all11_body']),all11)
    f.ordered_equal(resolve(scope['complete_historical_reference']),hist)
    for ref in scope['historical_source_components']:
        p=ref['path'];b=(a.ROOT/p).read_bytes();check('complete canonical component '+p,len(b)==ref['stored_bytes']and a.sha(b)==ref['stored_sha256'])
    parents=json.loads((a.OUT/'parent-investigations.json').read_bytes());priority=json.loads((a.OUT/'priority-investigations.json').read_bytes());remainder=json.loads((a.OUT/'remainder-inventory.json').read_bytes())
    check('all82 parents, exactly77 priority and five nonpriority',len(parents)==82 and len({p['county_fips']for p in parents})==82 and sum(p['priority_parent']for p in parents)==77)
    check('full887 ordered priority keys',[x['key']for x in priority]==contract['ordered_priority_keys']and len(priority)==887)
    check('full849 ordered remainder keys',[x['key']for x in remainder]==contract['remainder']['ordered_keys']and len(remainder)==849)
    allrows=priority+remainder;check('all1736 ranks preserved',[x['ordered_rank']for x in allrows]==list(range(1,1737)))
    constituent={u['key']:u for u in contract['source_native_constituents']};cols={c['key']:c for c in all11['columns']}
    for i,r in enumerate(allrows):
        f.ordered_equal(resolve(r['full_ranked_object']),contract['all_unit_order'][i])
        f.ordered_equal(resolve(r['full_constituent_object']),constituent[r['key']])
        f.ordered_equal(resolve(r['all11_source_field_object']),cols[r['key']])
        parentidx=int(r['shared_parent_inspection_ref'].split('#/')[-1]);assert parents[parentidx]['county_fips']==r['parent_county_fips']
        assert 'not an independent child feed'in r['inspection_scope']and r['current_native_id']is None and r['current_mapping_approved']is False
    check('all1736 complete ordered rank/constituent/all11 objects recursively equal, shared parent explicit',True)
    for p in parents:
        f.ordered_equal(resolve(p['full_native_array']),v2['parent_all_native_keys'][p['county_fips']])
        f.ordered_equal(resolve(p['priority_native_array']),contract['native_priority_by_parent'][p['county_fips']])
        assert p['full_native_count']==len(resolve(p['full_native_array']))
        assert p['priority_child_count']==len(resolve(p['priority_native_array']))
        assert p['remainder_native_count']==p['full_native_count']-p['priority_child_count']
        for k in ['current_election_id','current_contest_id','current_candidate_ids','current_native_ids','current_candidate_by_method','exact_outstanding_Senate_votes','source_guaranteed_cadence','completion_semantics_current']:assert p[k]is None
        assert p['current_crosswalk_approved']is False
    check('all parent/full-child/priority-child arrays preserve order; current unknowns null',True)
    check('all77 priority parents have actual county-specific bounded requests',all(p['current_primary_requests']>0 for p in parents if p['priority_parent']))
    check('all preferred named raw-field positions retained',sum(p['all_preferred_columns']*11 for p in parents)==24926 and sum(p['historical_named_numeric_positions']for p in parents)==20119 and sum(p['historical_named_null_positions']for p in parents)==4807)
    table=list(csv.DictReader((a.ROOT/'data/official-results-sources.csv').open()))
    check('83-row state plus82county CSV coverage',len(table)==83 and {r['county_fips']for r in table[1:]}==set(v2['parent_all_native_keys']))
    check('CSV never admits November counts/current IDs/exact remainder',all(r['November_counts_admitted']=='false'and not r['current_election_id']and not r['current_contest_id']and not r['exact_outstanding_votes']for r in table))
    directory=json.loads((a.OUT/'county-authority-payload.json').read_bytes())
    check('actual82 authority records and408 commissioner entries, no filling',len(directory['counties'])==82 and sum(len(c['commissioners'])for c in directory['counties'])==408)
    for p in parents:
        obj=directory
        for t in p['state_directory_pointer'].split('/')[1:]:obj=obj[int(t)]if isinstance(obj,list)else obj[t]
        assert obj['county']==p['directory_county_label_literal']and obj['clerk_name']==p['clerk_name_literal']
    check('all82 actual clerk/commission payload references',True)
    rows=[json.loads(p.read_bytes())for p in sorted((a.OUT/'receipts').glob('*.json'))];rr={r['id']:r for r in rows};ledger=json.loads((a.OUT/'source-ledger.json').read_bytes())
    f.ordered_equal(rows,ledger);check('complete acquisition ledger equals every receipt',True,len(rows))
    replay=json.loads((a.OUT/'acquisition-replay.json').read_bytes());jobids=[]
    for stage in replay['stages']:
        pin=stage['job_file'];b=(a.ROOT/pin['path']).read_bytes();assert len(b)==pin['bytes']and a.sha(b)==pin['sha256'];jobs=json.loads(b)
        assert [j['id']for j in jobs]==stage['ordered_request_ids']and len(jobs)==stage['requests']
        for j in jobs:assert rr[j['id']]['requested_url']==j['url']
        jobids.extend(j['id']for j in jobs)
    check('every actual request has exact pinned replay job, no missing or extra outcomes',len(replay['stages'])==28 and len(jobids)==len(set(jobids))==replay['total_requests']==len(rows)and set(jobids)==set(rr))
    decoded=json.loads((a.OUT/'decoding-controls.json').read_bytes());check('decoding controls cover every requested outcome',[r['source']for r in decoded]==[r['id']for r in rows])
    for r,d in zip(rows,decoded):
        assert r['started_at_utc'].endswith('+00:00')and r['finished_at_utc'].endswith('+00:00')
        if 'path'in r:
            wire=a.entity(r);raw=a.body(r)
            assert len(wire)==r['entity_bytes']and a.sha(wire)==r['entity_sha256']
            assert a.sha(raw)==d['decoded_sha256']and len(raw)==d['decoded_bytes']
            assert r['entity_complete']is True
        else:assert r.get('error')and not d['entity_available']
    check('complete requested/error wire entities, encoded/decoded/stored hashes, headers and UTC',True)
    posts=[r for r in rows if r['method']=='POST'];check('only public read-only admin-rule constructor POST',len(posts)==1 and posts[0]['id']=='admin-code-current-secretary-query'and posts[0]['request_json']['tmpAgency']=='54')
    prim=json.loads((a.OUT/'current-primary-index-inventory.json').read_bytes());check('complete actual March primary inventories and unknown literal',all(p['links']==76 and len(p['ordered_literal_links'])==76 for p in prim)and len(prim[1]['unrecognized_literal_links'])==1)
    anomaly=json.loads((a.OUT/'current-primary-index-anomaly.json').read_bytes());check('literal RepublicanCounty/Walthall body distinction retained',anomaly['index_literal']=='Republican County'and anomaly['actual_certificate_county_literal']=='Walthall'and not anomaly['current_November_counts_admitted'])
    sample=json.loads((a.OUT/'sample-controls.json').read_bytes())
    # Recompute original sample counts independently, without invoking a builder.
    import subprocess
    def textpdf(sid):return subprocess.run(['pdftotext','-layout','-','-'],input=a.body(rr[sid]),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout.decode('utf8','replace')
    totals=Counter();seen=[]
    for p in sample['pike2024_downloads']:
        s=textpdf(p['source']);sec=s.split('Senate United States',1)[1].split('3rd Congressional',1)[0]
        vals={name:int(re.search(re.escape(name)+r'\s+([\d,]+)',sec)[1].replace(',',''))for name in ['Ty Pinkins','Roger F. Wicker']}
        assert vals==p['candidates']
        if not p['requested_url'].endswith('/DW.pdf'):totals.update(vals);seen.append(p)
    check('independent Pike25 original precincts close DW and preferred SEMS named controls',len(seen)==25 and dict(totals)=={'Ty Pinkins':7130,'Roger F. Wicker':8205})
    sr=sample['rankin2024'];text=textpdf(sr['source']);sec=text.split('For United States Senate',1)[1].split('\f',1)[0]
    for r in sr['rows_in_source_order']:assert r['raw_line']in sec and sum(r['values'][:3])==r['values'][3]
    check('Rankin full raw ordered rows/method totals and duplicate write-in labels',len(sr['rows_in_source_order'])==7 and sr['rows_in_source_order'][-2]['label_literal']==sr['rows_in_source_order'][-1]['label_literal']=='Write-ins:'and sr['computed_all_candidate_control_sums']==[14333,54758,1329,70420])
    for p in sample['complete_text_position_derivatives']:
        for k in ['complete_text','complete_word_positions','failed_position_stdout']:
            pin=p.get(k)
            if pin:
                b=(a.ROOT/pin['path']).read_bytes();assert len(b)==pin['bytes']and a.sha(b)==pin['sha256']
        if p['complete_word_positions']is None:assert all(x['exit']!=0 and x['stderr']for x in p['position_extraction_attempts'])
    check('complete sample derivatives/positions or honest parser errors retained',True)
    visual=json.loads((a.OUT/'visual-review.json').read_bytes())
    for row in visual['pages']:
        p=row['png'];b=(a.ROOT/p['path']).read_bytes();assert a.sha(b)==p['sha256']and len(b)==p['bytes']
    check('actually reviewed full relevant original pages retained',len(visual['pages'])==10)
    legal=json.loads((a.OUT/'legal-observations.json').read_bytes());check('current primary law/instructions separated from exhaustive legal claims',not legal['complete_current_legal_coverage']and not legal['court']['complete_later_mandate_rehearing_stay_district_docket_verified']and legal['timezone']['source_currency']['up_to_date_as_of']=='2026-10-15')
    for dep in legal['read_only_original_dependencies']:
        for key in ['receipt_pin','original_pin']:
            pin=dep[key];b=(a.ROOT/pin['path']).read_bytes();assert len(b)==pin['bytes']and a.sha(b)==pin['sha256']
        raw=gzip.decompress((a.ROOT/dep['original_pin']['path']).read_bytes());assert len(raw)==dep['raw_bytes']and a.sha(raw)==dep['raw_sha256']
    check('existing primary court originals reused read-only with receipt/stored/raw controls',len(legal['read_only_original_dependencies'])==2)
    files=owned();check('strict per-file size bound',all(p.stat().st_size<40_000_000 for p in files))
    check('no caches, dependency directories or bytecode',all(not any(x in p.parts for x in ['__pycache__','node_modules','.cache'])and p.suffix!='.pyc'for p in a.OUT.rglob('*')))
    for p in files:
        if p.suffix=='.py':ast.parse(p.read_bytes(),filename=str(p))
    check('all owned Python parses',True)
    missing=[];anchors=[]
    for p in files:
        if p.suffix!='.md':continue
        for target in re.findall(r'\]\(([^\s)]+)\)',p.read_text()):
            if target.startswith(('http://','https://','mailto:')):continue
            path,_,frag=target.partition('#');dest=(p.parent/unquote(path)).resolve()if path else p
            pending_packaging=write and dest in [a.OUT/'validation.json',a.OUT/'asset-manifest.json']
            if not dest.exists()and not pending_packaging:missing.append((str(p),target))
            if frag and dest.suffix=='.md'and not path:
                if ('id="'+frag+'"')not in dest.read_text()and not re.search(r'^#+\s+'+re.escape(frag.replace('-',' ')),dest.read_text(),re.M|re.I):anchors.append(target)
    check('all relative Markdown destinations exist',not missing,missing)
    check('explicit generated county anchors resolve',not anchors,anchors)
    acceptance_body=(a.ROOT/f.ACCEPTANCE).read_bytes();acceptance_sha=a.sha(acceptance_body)
    forbidden=[]
    for p in files:
        if p.suffix in ['.md','.json','.py','.csv','.txt']and acceptance_sha.encode()in p.read_bytes():forbidden.append(str(p))
    check('no reverse external acceptance hash in worker files',not forbidden)
    coverage=dict(state_authorities=1,county_authorities=82,priority_parents=77,nonpriority_parents=5,priority_records=887,remainder_records=849,historical_preferred_native=1736,historical_preferred_all11_positions=24926,original_county_publication_references=352,acquisitions=len(rows),HTTP200=sum(r.get('status')==200 for r in rows),county_specific_current_HTTP200=sum(p['current_primary_HTTP200_observations']>0 for p in parents),November_count_entities_admitted=0,current_crosswalks_approved=0,calibrated_probabilities=0)
    result=dict(status='pass_bounded_research_with_explicit_current_and_legal_gaps',checks=len(checks),failures=0,coverage=coverage,check_results=checks,full_payload_verification='frozen-scope-validation.json',external_acceptance_path_only=f.ACCEPTANCE,source_exceptions=['Tunica one Pinkins and Harris unallocated','Leflore2018specialEspy native5853/printed5863 unallocated','2020three source changes and mixed certificate vintages','Montgomery885ballot statistic incompatible','Lincoln corrected15898; registration0unusable','Union58styles candidateweights/pools/targets unknown; parallel/vendor alternatives nonadditive','Current primary index omissions/anomalous literal label','Rankin Poppler bbox crashes; originals/layout text retained'],gaps=legal['unresolved'],current_results_admitted=False,current_geo_approved=False)
    if write:a.save(a.OUT/'validation.json',result)
    else:
        sv=json.loads((a.OUT/'validation.json').read_bytes());f.ordered_equal(result,sv)
        m=json.loads((a.OUT/'asset-manifest.json').read_bytes());check('manifest self-only exclusion',m['exclusion_paths']==['data/results-sources/asset-manifest.json'])
        actual={str(p.relative_to(a.ROOT)):p for p in files};expected={x['path']:x for x in m['entries']}
        check('manifest exact owned path set',set(actual)==set(expected)and len(expected)==len(m['entries']))
        for path,p in actual.items():b=p.read_bytes();assert len(b)==expected[path]['bytes']and a.sha(b)==expected[path]['sha256'],path
        check('all owned manifest bytes/hash/size',True,len(actual))
    return dict(status=result['status'],checks=len(checks),failures=0,coverage=coverage,read_only=not write)
if __name__=='__main__':print(json.dumps(run('--write-validation'in sys.argv),indent=2))
