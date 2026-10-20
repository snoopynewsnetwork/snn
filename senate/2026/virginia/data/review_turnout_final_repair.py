"""Independent final historical-body/citation/semantic preservation review.

Uses raw archive members and original pins; production renderer is only invoked
in a read-only subprocess to exercise the actual formerly failing URI.
"""
from pathlib import Path
from collections import Counter
import gzip, hashlib, io, json, re, subprocess, sys, tarfile

S=Path(__file__).resolve().parents[1];T=S/'data/turnout';H=T/'history/resume-citation-reciprocal';N=0
def ck(v,label=''):
    global N
    N+=1;assert v,(N,label)
def sha(b):return hashlib.sha256(b).hexdigest()
def js(p):return json.loads(p.read_bytes())

mf=js(T/'asset-manifest.json');assets=mf['owned_assets'];actual={str(p.relative_to(S)) for p in T.rglob('*') if p.is_file()}|{'turnout.md','data/county-turnout.csv'}
ck(len(assets)==411 and {r['path'] for r in assets}==actual-{'data/turnout/asset-manifest.json'})
for r in assets:
    b=(S/r['path']).read_bytes();ck(len(b)==r['bytes']<40000000 and sha(b)==r['sha256'])
for p in T.rglob('*'):ck(not set(p.parts)&{'__pycache__','node_modules','.venv','.pytest_cache'})
captures={};old_bodies={};captured_totals=[]
for name,expected in [('turnout-original-first',389),('baseline-final-peer',300)]:
    index=js(H/(name+'.json'));ck(index['whole_membership_count']==len(index['bodies'])==expected)
    packed=(S/index['archive_path']).read_bytes();ck(len(packed)==index['archive_bytes'] and sha(packed)==index['archive_sha256'])
    with tarfile.open(fileobj=io.BytesIO(packed),mode='r:gz') as z:
        ck({m.name for m in z.getmembers()}=={r['archive_name'] for r in index['bodies'] if r['archive_name'] is not None})
        for r in index['bodies']:
            b=(S/r['reference_path']).read_bytes() if r['reference_path'] is not None else z.extractfile(r['archive_name']).read()
            ck(len(b)==r['bytes'] and sha(b)==r['sha256'])
            if name=='turnout-original-first':old_bodies[r['path']]=b
            else:ck(b==(S/r['path']).read_bytes())
    captures[name]=index;captured_totals.append(expected)
oldmf=json.loads(old_bodies['data/turnout/asset-manifest.json'])
ck(sha(old_bodies['data/turnout/asset-manifest.json'])=='6eafa8cc1a897b40075d8234681b832282d871490043b98ef3c7f5c878fd2b50')
for r in oldmf['owned_assets']:ck(len(old_bodies[r['path']])==r['bytes'] and sha(old_bodies[r['path']])==r['sha256'])
changed=[p for p,b in old_bodies.items() if b!=(S/p).read_bytes()]
expected_changes=['data/turnout/build_turnout.py','data/turnout/final-seal.json','data/turnout/priority-set.json','data/turnout/source/SCHEMA.md','data/turnout/validate_turnout.py','data/turnout/validation.json','turnout.md','data/turnout/asset-manifest.json']
ck(set(changed)==set(expected_changes))
ck(sha((T/'pre-peer-witness.json').read_bytes())=='65318164238e4a7ac04ad9dce4421747cd80a6f13117c61d53fdec3598c69485')
ck(sha((T/'pre-peer-bodies.tar.gz').read_bytes())=='3fdb602bf0e87d43719329f540d2f50ca76dc704462e63de66b86cac3cbc1e15')
old=json.loads(old_bodies['data/turnout/priority-set.json']);current=js(T/'priority-set.json');oldpeer=old.pop('peer');peer=current.pop('peer');ck(old==current)
ck(peer['coordinator_acceptance'] is None and peer['captured_manifest_sha256']=='9b93b5ebf5c4e6d20c7e1216b992886d265c343021f8a10c48f982ecd2e74cbf')
ck(sha(old_bodies['data/county-turnout.csv'])==sha((S/'data/county-turnout.csv').read_bytes())=='5ce44dc51ad9c096013e9b63fd2e73b9b723f34480b185312da5c2cd10bf848f')

finding=js(S/'data/coordinator-turnout-citation-finding/finding.json');url=finding['actual_retained_requested_final_URL'];bad=finding['wrong_report_target'];text=(S/'turnout.md').read_text()
ck(bad in old_bodies['turnout.md'].decode() and bad not in text and url in text)
receipt=js(T/'source/acquired/enr-2024-results-report.receipt.json');ck(receipt['requested_url']==receipt['final_url']==url and receipt['hops'][-1]['status']==200)
cfg=js(T/'review/peer-settings.json');expected=old_bodies['turnout.md'].decode().replace(bad,url)
for r in cfg['report_replacements']:ck(expected.count(r['before'])==1);expected=expected.replace(r['before'],r['after'])
ck(expected==text)
edges=set()
for item in js(T/'source/acquisition-index.json')['receipts']:
    r=item['full_receipt']
    for k in ['requested_url','final_url']:
        if r.get(k):edges.add(r[k])
    for h in r['hops']:
        for k in ['request_url','response_url']:
            if h.get(k):edges.add(h[k])
urls=re.findall(r'\]\((https?://[^)]+)\)',text)
for u in urls:ck(u in edges and not re.search(r'\s',u))
ck(not(Counter(re.findall(r'`([^`\n]+)`',old_bodies['turnout.md'].decode()))-Counter(re.findall(r'`([^`\n]+)`',text))))
examples=['[source]('+url+')',url,'`a931 a5f7 literal0 and2020 va:161257:csv-record:2717`','```\na931 a5f7 and2020 literal0\n```','e5b689ae-a931-4b8a-a5f7-7392e9571c61','va:161257:csv-record:2717']
code='import runpy,json,sys; f=runpy.run_path(sys.argv[1])["render_prose"]; print(json.dumps([f(v) for v in json.load(sys.stdin)]))'
p=subprocess.run([sys.executable,'-B','-c',code,str(T/'render_prose.py')],input=json.dumps(examples+['all133 '+examples[0]]).encode(),capture_output=True,timeout=15)
ck(p.returncode==0 and p.stderr==b'');out=json.loads(p.stdout);ck(out[:-1]==examples and out[-1]=='all 133 '+examples[0])
proof=js(T/'review/reciprocal.json');ck(proof['status']=='pass' and proof['source_value_differences']==[] and proof['comparison_count']==60220)
ck(len(proof['orders'])==17 and proof['native_candidate_method_objects']==40035 and proof['api_complete_scopes']==134 and proof['all_parents']==133)
ck(proof['checker_sha256']==sha((T/'review/reciprocal.py').read_bytes()))
ck(proof['receipts']['own_frozen_receipt_files']==165 and proof['receipts']['own_logical_source_ids']==160 and len(proof['receipts']['preserved_failure_receipts'])==5 and proof['receipts']['shared_successful_full_receipts']==160)
reproduction=js(T/'review/final-reproduction.json');ck(reproduction['status']=='pass' and reproduction['network_calls']==0 and len(reproduction['outputs'])==35)
for r in reproduction['outputs']:
    b=(S/r['path']).read_bytes();ck(len(b)==r['bytes'] and sha(b)==r['sha256'])
seal=js(T/'final-seal.json');ck(seal['reciprocal_proof_sha256']==sha((T/'review/reciprocal.json').read_bytes()) and seal['contract_sha256']==sha((T/'priority-set.json').read_bytes()) and 'asset-manifest' not in json.dumps(seal))
ck(current['coverage']['current_geometry_or_2026_identity_approved'] is False)
result=dict(status='pass_independent_citation_repair_complete_history_and_bounded_reciprocal_preservation',checks=N,exact_final_owned_targets=411,complete_current_owned_files=412,whole_original_captured_bodies=389,whole_final_peer_captured_bodies=300,all_old_manifest_targets_checked=388,unchanged_old_bodies=389-len(changed),changed_old_bodies=changed,original394_body_witness_and_archive_unchanged=True,all_original_contract_semantics_except_peer_exact_equal=True,original_native_CSV_unchanged=True,literal_external_citation_edges_checked=len(urls),actual_production_renderer_examples=len(examples)+1,full_shared_source_core_comparisons=60220,full_source_sensitivity_orders=17,scope_excludes='Peer president, calculator/scenarios/targets/report/outcomes and later/future bytes; no count adoption or geographic/legal identity approval.',isolated_original_rebuild_products=35,all_producer_writes_by_coordinator=False,current_legal_or_feed_approval=False,reviewed_manifest=dict(path='data/turnout/asset-manifest.json',bytes=(T/'asset-manifest.json').stat().st_size,sha256=sha((T/'asset-manifest.json').read_bytes())))
(S/'data/coordinator-turnout-repair-final-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],checks=N,old_bodies=389,peer_bodies=300,unchanged_old_bodies=381)))
