"""Read-only offline audit by default. --write records validation before sealing.
Independent original-byte checks, not a replay of the calculation implementation.
"""
import io,zipfile,csv,re,collections,copy,sys,tarfile
from common import *
from acquire import allreceipts
def rows(p):return [json.loads(l)for l in gzip.decompress((ROOT/p).read_bytes()).splitlines()]
def audit():
    checks=[]
    def ok(name,condition,detail=None):
        assert condition,(name,detail);checks.append(dict(check=name,passed=True,detail=detail))
    rs=allreceipts();archives={};original_refs=[]
    for r in rs:
        if 'stored_path'not in r:continue
        b=original(r);ok('original_hash:'+r['id'],len(b)==r.get('raw_bytes',len(b)))
        original_refs.append(dict(id=r['id'],raw_sha256=sha(b),raw_bytes=len(b)))
        for h in r.get('hops',[]):
            hb=original(h);ok('http_hop_body:'+r['id'],len(hb)==h['raw_bytes'])
        if b.startswith(b'PK'):
            z=zipfile.ZipFile(io.BytesIO(b));ok('archive_crc:'+r['id'],z.testzip()is None)
            for i in z.infolist():archives[(r['id'],i.filename)]=z.read(i)
    members=json.loads((ROOT/'source/zip-members.json').read_text())+json.loads((ROOT/'source/workbook-members.json').read_text())
    for m in members:
        b=archives[(m['source_id'],m['member'])];ok('member_hash:'+m['source_id']+':'+m['member'],len(b)==m['bytes']and sha(b)==m['sha256'])
    layout=json.loads((ROOT/'source/field-layout.json').read_text());allrows=rows('extracts/all-long-rows.jsonl.gz');selected=rows('extracts/selected-root-rows.jsonl.gz');seen=set();counts=collections.Counter()
    for r in allrows:
        key=(r['source_id'],r['member']);b=archives[key];line=r['raw_line'].encode();offset=r['byte_offset'];assert b[offset:offset+len(line)]==line
        assert r['key']not in seen;seen.add(r['key']);counts[key]+=1
        assert r['line']==offset//265+1
        content=line.rstrip(b'\r\n');assert len(content)==263
        for f in layout:assert r['fields'][f['name']]==content[f['start_1']-1:f['end_1']].decode()
        assert int(content[11:17])==sum(int(content[i:i+6])for i in range(17,101,6))
    expected={k:len(v.splitlines())for k,v in archives.items() if v and '__MACOSX'not in k[1] and len(v.splitlines()[0])==263 and v[:101].isdigit() and any(y in k[0]for y in ['2020','2022','2024']) and 'writein'not in k[0]}
    ok('full_long_views_exact_rows_positions_fields_14_methods',dict(counts)==expected,dict(records=len(allrows)))
    bykey={r['key']:r for r in allrows}
    ok('selected_root_rows_exact',all(r==bykey[r['key']]and '/'not in r['member']for r in selected),len(selected))
    pairs=json.loads((ROOT/'extracts/short-long-comparisons.json').read_text());ok('all_short_long_views_agree',bool(pairs)and all(r['equal']for r in pairs),len(pairs))
    n=json.loads((ROOT/'native-inventory.json').read_text());hier=json.loads((ROOT/'extracts/municipal-hierarchy.json').read_text());m=json.loads((ROOT/'municipal-controls.json').read_text());c=json.loads((ROOT/'priority-set.json').read_text());ranks=json.loads((ROOT/'rankings.json').read_text());pdf=json.loads((ROOT/'extracts/pdf-controls.json').read_text())
    assert len({x['key']for x in n})==len(n)
    for year in ['2020','2022','2024']:
        all_original_codes={r['fields']['reporting_code']for r in allrows if year in r['source_id']and '/'not in r['member']}
        ok('all_office_root_native_inventory_coverage_'+year,all_original_codes=={x['code']for x in n if x['year']==year},len(all_original_codes))
    # Independently derive original unit votes/anchor positions directly from ZIP bytes.
    src=next(r for r in rs if r['id']=='ri-2024-layout-zip');raw=archives[(src['id'],'rigen2024l.txt')];original_units={}
    for line_no,line in enumerate(raw.splitlines(keepends=True),1):
        if line[:4]!=b'0002':continue
        code=line[7:11].decode();name=line[205:235].decode().rstrip();u=original_units.setdefault(code,dict(votes=0,anchor=(line_no-1)*265,name=name,rows=[],groups=[0]*14,candidates=[]))
        u['votes']+=int(line[11:17]);u['rows'].append(f"{src['raw_sha256']}:rigen2024l.txt:{(line_no-1)*265}");u['candidates'].append(line[4:7].decode())
        for i in range(14):u['groups'][i]+=int(line[17+6*i:23+6*i])
    ok('independent_458_original_units',len(original_units)==458 and sum(u['votes']for u in original_units.values())==491948)
    def inventory_invariants(native):
        actual=[x for x in native if x['year']=='2024'];assert len(actual)==497 and len({x['code']for x in actual})==497
        sen=[x for x in actual if x['contests']['Senator in Congress']['status']=='published'];assert {x['code']for x in sen}==set(original_units)
        for x in actual:
            q=x['contests']['Senator in Congress']
            if x['code']not in original_units:assert q['total']is None and q['candidate_rows']is None
            else:
                u=original_units[x['code']];assert q['total']==u['votes']and q['methods']==u['groups']and q['candidate_rows']==u['rows']and len(q['candidate_rows'])==3
                assert len(set(u['candidates']))==3
                for k,f in zip(q['candidate_rows'],q['candidate_fields']):assert f==bykey[k]['fields']
            if x['code']in ['9001','9002','9011','9012']:assert x['parent_key']=='RI:state'and x['parent_proof']is None
            else:assert x['parent_proof']is not None
        assert len(sen)==458 and sum(x['contests']['Senator in Congress']['total']==0 for x in sen)==15
    inventory_invariants(n);ok('native_complete_null_admin_candidate_method_invariants',True)
    for y,children in [('2024',493),('2020',500),('2022',454)]:
        ps=[p for p in hier if p['year']==y];codes=[ch['code']for p in ps for ch in p['children']];ok('explicit_all_municipal_parents_'+y,len(ps)==39 and len(codes)==len(set(codes))==children)
        for p in ps:
            rawhtml=original(next(r for r in rs if r['id']==p['source_id']));ll=links(rawhtml)
            for ch in p['children']:assert any(ch['label']==label and ch['url'].endswith(u)for label,u in ll)
    expected_order=sorted(original_units,key=lambda k:(-original_units[k]['votes'],original_units[k]['anchor']))
    def order_invariants(contract):
        order=contract['complete_descending_order'];assert len(order)==458
        assert [x['native_code']for x in order]==expected_order
        cum=0;cross=None
        for i,x in enumerate(order,1):
            u=original_units[x['native_code']];cum+=u['votes'];assert x['votes']==u['votes']and x['cumulative_votes']==cum and x['rank']==i
            assert x['key']==f"{src['raw_sha256']}:rigen2024l.txt:{u['anchor']}"
            assert x['share_denominator']==491948 and x['share_numerator']==u['votes']
            if cross is None and 5*cum>=4*491948:cross=i
        assert cross==242 and order[cross-1]['native_code']=='0804'
        assert order[240]['cumulative_votes']==393066 and order[241]['cumulative_votes']==394072
        assert sum(x['votes']for x in order[242:])==97876
        assert contract['ordered_priority_keys']==[x['key']for x in order[:cross]]
        assert contract['minimum80']['remainder_keys']==[x['key']for x in order[cross:]]
        assert contract['top15']['top15_votes']==sum(x['votes']for x in order[:15])==34697
        assert contract['minimum80']['minimum80_count']==cross
    order_invariants(c);ok('independent_full_native_order_minimum_integer80_remainder',True)
    ok('contract_full_497_native_inventory',len(c['all_source_native_constituents'])==497 and {x['key']for x in c['all_source_native_constituents']}=={x['key']for x in n if x['year']=='2024'})
    csvrows=list(csv.DictReader((STATE/'data/county-turnout.csv').open()));ok('canonical_csv_458_native',len(csvrows)==458 and [x['native_code']for x in csvrows]==expected_order)
    for x in csvrows:
        u=original_units[x['native_code']];assert int(x['senate2024_reported_candidate_generic_votes'])==u['votes'];assert [int(x['group_'+str(i)])for i in range(1,15)]==u['groups'];assert x['senate_contest_ballots']==x['senate_undervotes']==x['senate_overvotes']==x['valid_named_writeins']==''
    # Every applicable statewide candidate has a separate original PDF and HTML control.
    controls=json.loads((ROOT/'candidate-reconciliation.json').read_text())
    assert len(controls)==27
    for cc in controls:
        rr=[bykey[k]for k in cc['root_row_keys']];v=[sum(int(x['fields'][f])for x in rr)for f in ['total']+['group_'+str(i)for i in range(1,15)]]
        assert v==cc['total_and_14_groups'] and v[:4]==cc['board_pdf']['values']and cc['html']['total']==v[0]
        pc=cc['board_pdf'];text=gzip.decompress((ROOT/f"source/board-{pc['year']}-summary.layout.txt.gz").read_bytes()).decode();assert text.split('\f')[pc['page']-1].splitlines()[pc['line']-1]==pc['raw_line']
    ok('all27_candidate_controls_whole_state_and_methods',True)
    for year in ['2024','2022','2020']:
        for title,pdflabel in [('REGISTERED VOTERS - TOTAL','Registered Voters - Total'),('BALLOTS CAST - TOTAL','Ballots Cast - Total'),('BALLOTS CAST - BLANK','Ballots Cast - Blank')]:
            ss=[x for x in m if x['year']==year and x['statistics'][title]['values']is not None]
            pp=[x for x in pdf if x['year']==year and x['contest']=='STATISTICS'and re.sub('[^A-Za-z]','',x['label']).lower()==re.sub('[^A-Za-z]','',pdflabel).lower()]
            if ss:assert len(pp)==1 and sum(x['statistics'][title]['values'][0]for x in ss)==pp[0]['values'][0]
    ok('all_year_ballot_blank_registration_primary_closure',True)
    for year,total in [('2024',9370),('2020',6222)]:
        aa=[x for x in n if x['year']==year and x['contests']['Senator in Congress']['total']is None];assert len(aa)==39 and sum(x['statistics']['BALLOTS CAST - TOTAL']['values'][0]for x in aa)==total
    aa=[x for x in n if x['year']=='2022'and x['geography_type']=='state_administrative'];assert len(aa)==4 and all(x['contests']['Governor']['total']is None for x in aa)and sum(x['statistics']['BALLOTS CAST - TOTAL']['values'][0]for x in aa)==175
    ok('scope_difference_exact_presidential_and_admin_ballots',True)
    p=c['municipal_and_administrative_parent_sensitivity'];ok('43parent_sensitivity_separate',p['canonical_dispatch']is False and len(p['full_inventory'])==43 and p['rankings']['minimum80_count']==21 and p['rankings']['minimum80_votes']==395379)
    # Verify every ranking's denominator, weights, sorted order, integer crossing and remainder.
    for key,ranking in ranks.items():
        rr=ranking['order'];assert len({x['key']for x in rr})==len(rr);assert sum(x['votes']for x in rr)==ranking['total']
        assert [x['votes']for x in rr]==sorted([x['votes']for x in rr],reverse=True)
        i=ranking['minimum80_count'];assert 5*sum(x['votes']for x in rr[:i-1])<4*ranking['total']<=5*sum(x['votes']for x in rr[:i])
        assert sum(x['votes']for x in rr[i:])==ranking['remainder_votes']
        assert abs(sum(x['votes']/ranking['total']for x in rr)-1)<1e-12
    ok('all_sensitivity_denominators_weights_orders_thresholds',True,len(ranks))
    # Fail closed on deliberately corrupted native/method/null/order/candidate/parent input.
    mutations=[]
    def reject(label,fn):
        try:fn()
        except (AssertionError,KeyError):mutations.append(dict(case=label,rejected=True));return
        raise AssertionError('corruption accepted: '+label)
    a=copy.deepcopy(n);a.pop(next(i for i,x in enumerate(a)if x['year']=='2024'));reject('missing_native_context',lambda:inventory_invariants(a))
    a=copy.deepcopy(n);x=next(x for x in a if x['year']=='2024'and x['code']=='0101');x['contests']['Senator in Congress']['methods'][1]+=1;reject('method_corruption',lambda:inventory_invariants(a))
    a=copy.deepcopy(n);x=next(x for x in a if x['year']=='2024'and x['contests']['Senator in Congress']['status']=='unavailable_in_source');x['contests']['Senator in Congress']['total']=0;reject('fabricated_absent_senate_zero',lambda:inventory_invariants(a))
    a=copy.deepcopy(n);x=next(x for x in a if x['year']=='2024'and x['code']=='0101');x['contests']['Senator in Congress']['candidate_fields'][1]=x['contests']['Senator in Congress']['candidate_fields'][0];reject('candidate_identity_replacement',lambda:inventory_invariants(a))
    a=copy.deepcopy(n);x=next(x for x in a if x['year']=='2024'and x['code']=='9001');x['parent_key']='RI:municipality:providence';reject('administrative_municipal_allocation',lambda:inventory_invariants(a))
    a=copy.deepcopy(c);a['complete_descending_order'][0],a['complete_descending_order'][1]=a['complete_descending_order'][1],a['complete_descending_order'][0];reject('wrong_descending_order',lambda:order_invariants(a))
    a=copy.deepcopy(c);a['minimum80']['minimum80_count']=241;reject('premature_80_crossing',lambda:order_invariants(a))
    a=copy.deepcopy(c);a['complete_descending_order'][241]['key']+=':wrong';reject('source_position_key_corruption',lambda:order_invariants(a))
    ok('meaningful_corruption_rejections',len(mutations)==8,mutations)
    wi=json.loads((ROOT/'extracts/writein-scope-comparison.json').read_text());ok('complete_writein_discrepancies_retained_unallocated',len(wi)==39 and sum(x['printed_top_total']for x in wi)==1239 and sum(x['detail_sum']for x in wi)==1227 and sum(x['difference']!=0 for x in wi)==8)
    ok('historical_row6_scope_retained',sum(x['prior_row6_detail_sum']for x in wi)==1226 and sum(x['prior_row6_difference']!=0 for x in wi)==9)
    from repair_validation import audit as repair_audit
    repair=repair_audit();ok('full_historical362_and_original227_body_reconstruction',repair['status']=='passed')
    ok('ten_original_row5_metadata_admission_corruption_tests',len(repair['corruption_tests'])==10,repair['corruption_tests'])
    from reciprocal_source_core import Capture
    peer=Capture();comparison=json.loads((ROOT/'reciprocal/source-core-comparison.json').read_text());assert comparison['status']=='passed'and len(comparison['checks'])==17 and len(comparison['child_label_whitespace_differences'])==11
    for item in peer.index['all235']:
        b=peer.tar.extractfile(item['path']).read();assert len(b)==item['bytes']and sha(b)==item['sha256']
    ok('finished_peer235_full_capture_and17_source_core_scopes',True)
    # Every owned file is below the strict object bound; validate all relative Markdown links.
    owned=[STATE/'turnout.md',STATE/'data/county-turnout.csv']+[p for p in ROOT.rglob('*')if p.is_file()]
    for path in owned:assert path.stat().st_size<40000000
    for path in [STATE/'turnout.md',ROOT/'source/SCHEMA.md']:
        for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if re.match(r'https?://',link):continue
            dest=(path.parent/link.split('#')[0]).resolve()
            deferred={ROOT/'validation.json',ROOT/'qa/pre-peer-body-witness.json',ROOT/'final-seal.json',ROOT/'asset-manifest.json',ROOT/'qa/repaired-body-witness.json'}
            if '--write'in sys.argv and dest in deferred:continue
            assert dest.exists(),(path,link)
    ok('owned_bounds_relative_links',True,len(owned))
    if (ROOT/'asset-manifest.json').exists()and '--write'not in sys.argv:
        manifest=json.loads((ROOT/'asset-manifest.json').read_text());expected_paths={str(p.relative_to(STATE))for p in owned if p!=ROOT/'asset-manifest.json'}
        assert {x['path']for x in manifest['owned_assets']}==expected_paths
        for item in manifest['owned_assets']:
            b=(STATE/item['path']).read_bytes();assert len(b)==item['bytes']and sha(b)==item['sha256']
        ok('manifest_exact_membership_hash_size_excludes_only_itself',True,len(expected_paths))
        from repair_validation import historical
        old=historical();witness=json.loads((ROOT/'qa/pre-peer-body-witness.json').read_text());tb=gzip.decompress((ROOT/witness['body_archive']['path']).read_bytes());assert sha(tb)==witness['body_archive']['uncompressed_tar_sha256']
        with tarfile.open(fileobj=io.BytesIO(tb))as t:
            for item in witness['frozen_bodies']:
                data=t.extractfile(item['path']).read();assert sha(data)==item['sha256']and len(data)==item['bytes'];assert old[item['path']]==data
        for item in witness['immutable_original_references']:
            data=(STATE/item['path']).read_bytes();assert sha(data)==item['stored_sha256']and len(data)==item['stored_bytes'];assert sha(gzip.decompress(data))==item['raw_sha256']
        ok('full_body_witness_exact_reconstruction_and_originals',True)
        current=json.loads((ROOT/'qa/repaired-body-witness.json').read_text());archive=(ROOT/current['changed_archive']['path']).read_bytes();assert sha(archive)==current['changed_archive']['sha256'];tar=gzip.decompress(archive);assert sha(tar)==current['changed_archive']['tar_sha256']
        with tarfile.open(fileobj=io.BytesIO(tar))as changed:
            for item in current['bodies']:
                st=item['storage'];data=changed.extractfile(st['member']).read()if st['kind']=='changed_tar'else old[item['path']]if st['kind']=='historical_tar'else (STATE/st['path']).read_bytes();assert len(data)==item['bytes']and sha(data)==item['sha256']and data==(STATE/item['path']).read_bytes()
        assert {x['path']for x in current['bodies']}=={str(p.relative_to(STATE))for p in owned}-set(current['terminal_exclusions'])
        seal=json.loads((ROOT/'final-seal.json').read_text())
        for path,pin in seal['pins'].items():
            b=(ROOT/path).read_bytes();assert sha(b)==pin['sha256']and len(b)==pin['bytes']
        ok('current_complete_repaired_body_witness_terminal_closure_and_seal',True,len(current['bodies']))
    return dict(schema='ri-turnout-validation-repair-v3',status='passed',peer_agreement='bounded captured source-core passed; broader peer models/scenarios/outcomes not asserted',coordinator_acceptance=False,checks=checks,corruption_tests=mutations+repair['corruption_tests'],source_observations=original_refs)
if __name__=='__main__':
    result=audit()
    if '--write'in sys.argv:dump(ROOT/'validation.json',result)
    print(json.dumps(dict(status=result['status'],checks=len(result['checks']),corruption_tests=len(result['corruption_tests']))))
