"""Complete owned validation/sealing and final READ-ONLY audit."""
import datetime as dt,gzip,json,os,re,subprocess,sys
from pathlib import Path
from urllib.parse import urljoin
from replay_authority import OWN,STATE,parse,digest
from html_tools import receipts,entity,links
from build_data import validate
from negative_fixtures import audit_stored

MANIFEST=OWN/'asset-manifest.json'
REPORT=STATE/'official-results.md';CSV=STATE/'data/official-results-sources.csv'

def owned_files():
    return sorted([REPORT,CSV]+[p for p in OWN.rglob('*') if p.is_file() and p!=MANIFEST])

def check_manifest():
    m=parse(MANIFEST.read_bytes());files=owned_files()
    assert [str(p.relative_to(STATE)) for p in files]==[x['path'] for x in m['files']]
    for p,x in zip(files,m['files']):
        b=p.read_bytes();assert len(b)==x['bytes'] and digest(b)==x['sha256']
    assert m['excludes_only']=='data/results-sources/asset-manifest.json'
    return len(files)

def check_http():
    rs=receipts();index=parse((OWN/'source-index.json').read_bytes())
    assert [n for n,r in rs]==[x['receipt'] for x in index]
    observations={n:r for n,r in rs};hops=0;anchors=0
    for (n,r),ix in zip(rs,index):
        rb=(OWN/n).read_bytes();assert len(rb)==ix['receipt_bytes'] and digest(rb)==ix['receipt_sha256']
        assert dt.datetime.fromisoformat(r['ended_utc'])>=dt.datetime.fromisoformat(r['started_utc'])
        assert r['method'] in ['GET','POST'] and r['configured_headers']
        if not r['hops']:
            assert r['status']=='unavailable-no-response'
            assert all(r[k] is None for k in ['response_status','response_headers','response_body'])
        for h in r['hops']:
            assert h['headers'] and h['request_headers']
            chunks=[]
            for p in h['body']['parts']:
                z=(OWN/p['path']).read_bytes()
                assert len(z)==p['bytes'] and digest(z)==p['sha256'] and len(z)<40000000
                chunks.append(z)
            b=gzip.decompress(b''.join(chunks))
            assert len(b)==h['body']['bytes'] and digest(b)==h['body']['sha256']
            hops+=1
        p=r.get('parent_evidence')
        if isinstance(p,dict) and p.get('parent_receipt') and p.get('position') and p.get('attrs',{}).get('href'):
            candidates=links(p['parent_receipt'])
            assert any(x['attrs']==p['attrs'] and list(x['position'])==p['position'] and x['url']==p['url'] for x in candidates),(n,'actual anchor')
            assert p['url']==r['requested_url']
            anchors+=1
    samples=parse((OWN/'complete-public-json-samples.json').read_bytes())
    assert len(samples)==4
    for s in samples:
        r,b=entity(s['receipt']);assert parse(b)==s['full_source_object']
        assert len(s['full_source_object'])==45 and s['current_count_admission'] is False
    return {'requests':len(rs),'whole_response_hops':hops,'actual_published_anchor_checks':anchors,'whole_json_samples':len(samples)}

def check_pdfs_history_links():
    pdfs=parse((OWN/'pdf-index.json').read_bytes())
    for x in pdfs:
        _,b=entity(x['receipt']);assert b.startswith(b'%PDF') and len(b)==x['original_bytes'] and digest(b)==x['original_sha256']
        text=gzip.decompress((OWN/x['text']).read_bytes());assert len(text)==x['text_bytes'] and digest(text)==x['text_sha256']
        assert (OWN/x['stderr']).exists()
    assert sum('/sample-ballots/2026/gen/' in x['url'] for x in pdfs)==67
    manual=parse((OWN/'visual/manual-readings.json').read_bytes())
    for x in manual['readings']:
        b=(OWN/x['render']).read_bytes();assert len(b)==x['render_bytes'] and digest(b)==x['render_sha256']
        assert x['actually_visually_inspected'] is True and x['full_page_normalized_bbox']==[0,0,1,1]
    history=0
    for p in (OWN/'history').rglob('*'):
        if p.is_file() and p.suffix=='.gz':gzip.decompress(p.read_bytes());history+=1
    link_count=0
    for p in [REPORT,*OWN.rglob('*.md')]:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            target=target.strip('<>').split('#')[0]
            if not target or re.match(r'https?://|mailto:',target):continue
            assert (p.parent/target).resolve().exists(),(p,target)
            link_count+=1
    return {'complete_pdf_entities':len(pdfs),'whole_county_specimens':67,'manual_page_readings':len(manual['readings']),
            'whole_history_gzip_objects':history,'local_markdown_links':link_count}

def checks():
    files=owned_files()
    for p in files:
        assert p.stat().st_size<40000000,('strict bound',p,p.stat().st_size)
        assert not any(x in ['__pycache__','node_modules','.venv','venv','.cache'] for x in p.parts)
    validate(parse(gzip.decompress((OWN/'historical-hierarchy.json.gz').read_bytes())))
    http=check_http();pdf=check_pdfs_history_links();negative=audit_stored()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    run=subprocess.run([sys.executable,str(OWN/'scripts/offline_rebuild.py')],env=env,capture_output=True)
    assert run.returncode==0,run.stderr.decode()
    assert not run.stderr,run.stderr.decode()
    proof=parse(run.stdout);assert proof['status']=='PASS'
    assert proof==parse((OWN/'qa/offline-proof.json').read_bytes()),'saved exact isolated proof differs'
    assert proof['all_temp_outputs_byte_identical'] and len(proof['actual_route_probes'])==7
    return {'status':'PASS','acceptance_path':'data/coordinator-priority-acceptance.json',
        'http':http,'PDF_history_links':pdf,'stored_negative_inputs':negative,
        'source_authority':proof['source_graph'],'originals':proof['originals'],
        'isolated_reconstruction':True,'current_legal_geography_November_cadence_pool_collector_forecast_calibration_approval':False}

def seal():
    result=checks();(OWN/'qa/validation.json').write_text(json.dumps(result,indent=2)+'\n')
    validation=(OWN/'qa/validation.json').read_bytes()
    seal={'schema':'AL-official-results-final-seal-v1','status':'bounded-source-research-complete-for-coordinator-review',
      'sealed_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'acceptance_path':'data/coordinator-priority-acceptance.json',
      'validation':{'path':'data/results-sources/qa/validation.json','bytes':len(validation),'sha256':digest(validation)},
      'historical_native_contexts':2085,'priority':887,'remainder':1198,'all_parents':67,'priority_parents':63,
      'producer_flags_changed':False,'current_approvals':False,'manifest_digest_in_seal':False,
      'instruction':'manifest written last; final audit is read-only; coordinator alone accepts/publishes'}
    (OWN/'final-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
    files=[]
    for p in owned_files():
        b=p.read_bytes();files.append({'path':str(p.relative_to(STATE)),'bytes':len(b),'sha256':digest(b)})
    manifest={'schema':'AL-official-results-exact-membership-v1','excludes_only':'data/results-sources/asset-manifest.json','files':files}
    MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':'SEALED','files':len(files)}))

if __name__=='__main__':
    if '--seal' in sys.argv:seal()
    elif '--audit' in sys.argv:
        count=check_manifest();result=checks();assert check_manifest()==count
        print(json.dumps({**result,'status':'FINAL READ-ONLY PASS','manifest_targets':count},indent=2))
    else:print(json.dumps(checks(),indent=2))
