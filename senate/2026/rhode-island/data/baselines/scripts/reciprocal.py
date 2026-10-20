"""Read only captured final peer bodies. Never imports a peer count into production."""
import collections,csv,gzip,io,json,tarfile
from common import *
def main():
    cap=json.loads((BASE/'reciprocal/capture-additional.json').read_text())
    index={x['path']:x for x in cap if not x.get('missing')}
    def raw(name):
        r=index[name];b=gzip.decompress((BASE/r['frozen_path']).read_bytes());assert sha(b)==r['sha256'];assert len(b)==r['bytes'];return b
    def j(name):return json.loads(raw(name))
    checks=[];differences=[];literal_labels=[]
    def check(name,good,scope=None):
        checks.append({'check':name,'passed':bool(good),'scope':scope})
        if not good:differences.append(name)
    expected={'data/turnout/priority-set.json':'7d788cf5c2efa884b86332833cb18a54e481b261f2f6cbab5206ac9d20e10aac',
        'data/county-turnout.csv':'b88359a99851da1558c2ce8bd3e101f3b4463170f10b2922b8c1cafe78e7bc9e',
        'data/turnout/native-inventory.json':'68c2293eaa846162911033445bc6503a353dbe018867b8a7dd421bdde535ad1e',
        'data/turnout/candidate-reconciliation.json':'5bda32bd1bf5a7938da12c96119f03ea1e4d5afbb0a3cabd367f3644e53ea987',
        'data/turnout/asset-manifest.json':'52015c24dd3702f0a5678947ac4262fd5ad19b3a23601ee8d62795e1f9943f9f'}
    for p,digest in expected.items():check('captured advertised hash '+p,sha(raw(p))==digest)
    own=read_gz('witness/root-selected.jsonl.gz');peer=[json.loads(x) for x in gzip.decompress(raw('data/turnout/extracts/selected-root-rows.jsonl.gz')).splitlines()]
    def anchor(r):return r['zip_sha256'],r['member'],r['byte_start']
    mine={anchor(r):r for r in own};theirs={tuple(r['key'].split(':')[:2])+ (int(r['byte_offset']),):r for r in peer}
    check('root source anchor full set',mine.keys()==theirs.keys(),len(mine))
    for k,r in mine.items():
        p=theirs[k]
        check('root raw bytes/terminator/line '+str(k),r['raw_record']==p['raw_line'].rstrip('\r\n') and r['line']==p['line'] and sha(p['raw_line'].encode('latin1'))==r['raw_line_sha256'])
    allpeer=[json.loads(x) for x in gzip.decompress(raw('data/turnout/extracts/all-long-rows.jsonl.gz')).splitlines()]
    api={tuple(r['key'].split(':')[:2])+(int(r['byte_offset']),):r for r in allpeer}
    views=read_gz('witness/selected-all-views.jsonl.gz')
    check('all selected root/nested/setup raw fields and methods',all(anchor(r) in api and r['raw_record']==api[anchor(r)]['raw_line'].rstrip('\r\n') and
         r['line']==api[anchor(r)]['line'] and sha(api[anchor(r)]['raw_line'].encode('latin1'))==r['raw_line_sha256'] for r in views),len(views))
    inv=json.loads((BASE/'extracts/native-inventory.json').read_text());pinv=j('data/turnout/native-inventory.json');pi={(int(r['year']),r['code']):r for r in pinv}
    check('complete all-source inventory set',{(r['year'],r['source_code']) for r in inv}==set(pi),len(inv))
    stats=json.loads((BASE/'extracts/native-statistics.json').read_text());si={(r['year'],r['source_code'],r['statistic']):r for r in stats}
    for r in inv:
        p=pi[r['year'],r['source_code']];k=f"{r['year']}:{r['source_code']}"
        parent='RI:municipality:'+r['parent_key'] if r['parent_kind']=='municipality' else 'RI:state-admin:'+r['source_code']
        check('parent tuple '+k,p['dispatch_key']==parent)
        check('literal source name '+k,p['reporting_name']==r['source_name'])
        if r['child_html']:
            h=r['child_html'];q=p['parent_proof']
            check('municipal child original source/URL proof '+k,q['child_url']==h['url'] and q['raw_sha256']==inputs()[h['input']]['raw_sha256'])
            if q['label']!=h['label_literal']:
                literal_labels.append({'year':r['year'],'code':r['source_code'],'own_literal':h['label_literal'],'peer_display':q['label'],
                    'same_after_whitespace_collapse':' '.join(h['label_literal'].split())==q['label'],
                    'original_body_sha256':inputs()[h['input']]['raw_sha256'],'own_label_byte_start':h['byte_start']})
        else:check('no invented municipal parent proof '+k,p['parent_proof'] is None)
        for t,c in r['contests'].items():
            pc=p['contests'][t];check('contest availability/total '+k+t,(pc['total']==c['votes']) and (pc['status']=='published')==c['observed'])
        for name in ['REGISTERED VOTERS - TOTAL','BALLOTS CAST - TOTAL','BALLOTS CAST - BLANK']:
            me=si.get((r['year'],r['source_code'],name));pp=p['statistics'].get(name)
            check('statistic raw/native/null '+k+name,(me is None and pp is None) or (me is not None and pp is not None and pp['values']==[me['total']]+me['methods'] and pp['columns'].get('A')==me['source_name'] and pp['key'].endswith(':row'+str(me['row']))))
    cand=j('data/turnout/candidate-reconciliation.json')
    for p in cand:
        rr=[r for r in own if r['year']==int(p['year']) and r['contest_code']==p['source_native_contest'] and r['candidate_code']==p['source_native_candidate']]
        check('candidate full raw identity/control '+p['year']+p['source_native_contest']+p['source_native_candidate'],
            len(rr)==p['native_count'] and all(r['party']==p['party'] and r['candidate_name']==p['candidate_name'] for r in rr) and
            [sum(r['votes'] for r in rr)]+[sum(r['methods'][i] for r in rr) for i in range(14)]==p['total_and_14_groups'])
    ranks=json.loads((BASE/'witness/independent-native-priority.json').read_text());csvpeer=list(csv.DictReader(io.StringIO(raw('data/county-turnout.csv').decode())))
    check('all458 full descending source-position order',len(csvpeer)==len(ranks)==458 and all(r['key'].split('#')==[p['archive_raw_sha256'],p['member'],p['first_senate_record_byte_offset']] and r['source_code']==p['native_code'] and r['votes']==int(p['senate2024_reported_candidate_generic_votes']) and r['rank']==int(p['rank']) and r['cumulative']==int(p['cumulative_votes']) for r,p in zip(ranks,csvpeer)))
    contract=j('data/turnout/priority-set.json');ordered=[r['key'].replace('#',':') for r in ranks if r['priority']]
    check('exact integer80 contract ordered priority',ordered==contract['ordered_priority_keys'] and len(ordered)==242 and ranks[240]['cumulative']*5<491948*4<=ranks[241]['cumulative']*5)
    peer_receipts=j('data/turnout/source/inputs/original-receipts.json');pri={r['id']:r for r in peer_receipts}
    receipti=json.loads((BASE/'reciprocal/peer-acquired-receipts-index.json').read_text())
    rb=(BASE/'reciprocal/peer-acquired-receipts.tar.gz').read_bytes();assert sha(rb)==receipti['archive_sha256']
    with tarfile.open(fileobj=io.BytesIO(rb)) as tar:
        for r in receipti['members']:
            b=tar.extractfile(r['member']).read();assert sha(b)==r['sha256'];pri[r['id']]=json.loads(b)
    check('148 original receipt/header/body witnesses',all(r['id'] in pri and all(v==pri[r['id']].get(k) for k,v in r['original_receipt'].items()) for r in inputs().values()),len(inputs()))
    manifest=j('data/turnout/asset-manifest.json')
    result={'schema':'ri-baseline-reciprocal-v1','peer_agent_id':'5bf8df2e-5c2f-4e0e-a51e-2021afca7bea',
        'all_passed':not differences,'checks':checks,'differences':differences,'checks_count':len(checks),
        'literal_child_label_representation_differences':literal_labels,'literal_label_byte_equality':not literal_labels,
        'captured_scope':'Final turnout core bodies in capture-additional.json only; no later report/calculator/seal equality asserted',
        'representation_differences':['Native key delimiters: own # versus peer colon, compared only via original SHA/member/byte tuple.',
            'Own raw_record excludes CRLF but raw_line_sha256 covers original terminator; peer raw_line includes CRLF.',
            'Eleven child labels collapse repeated whitespace in peer displayed text; literal source strings and original byte offsets are preserved in own witness. No peer file or source key edited.',
            'Own parent_key is municipality slug or state-admin-code; peer dispatch_key uses RI namespace and state administrative parent remains RI:state.',
            '2022 Board statistic-only federal contexts added as unavailable Governor after independently checking preserved original cells; initial selected-contest inventory is frozen in pre-peer witness.',
            'Own CSV is five-contest long form with absent contest rows; peer CSV is ranked 458-context 2024 Senate priority table.'],
        'coordinator_acceptance':False,'current_native_geometry_approved':False,'peer_production_edited':False,'peer_counts_used_as_inputs':False}
    write_json('reciprocal/reconciliation.json',result)
    print('Reciprocal checks',len(checks),'differences',differences[:20])
if __name__=='__main__':main()
