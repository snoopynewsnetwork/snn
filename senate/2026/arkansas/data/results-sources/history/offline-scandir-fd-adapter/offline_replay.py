"""Deny network, producer imports/writers, helper discovery; rebuild into tmp."""
import sys,json,tempfile,os,gzip
from pathlib import Path
from replay import loads,STATE,HERE,digest
import build
def run():
    roles=loads(gzip.decompress((HERE/'historical-source-roles.json.gz').read_bytes()))
    refs=loads(gzip.decompress((HERE/'original-references.json.gz').read_bytes()))
    allowed={str((STATE/x['path']).resolve()) for x in roles}
    allowed.add(str((STATE/'data/coordinator-priority-acceptance.json').resolve()))
    allowed.update([str((STATE/'official-results.md').resolve()),str((STATE/'data/official-results-sources.csv').resolve())])
    repo=HERE.parents[4]
    for x in refs:allowed.update([str((repo/x['path']).resolve()),str((repo/x['receipt_path']).resolve())])
    # Own exact sealed input bodies are checked by final manifest, and every HTTP body by receipt.
    runtime=[Path(sys.base_prefix).resolve(),Path('/usr/share').resolve(),Path('/System/Library').resolve(),Path('/Library/Developer/CommandLineTools').resolve()]
    counters={'network_denials':0,'external_write_denials':0,'non_pdftotext_process_denials':0,'helper_read_denials':0}
    with tempfile.TemporaryDirectory(prefix='arkansas-question3-offline-') as tmp:
        target=Path(tmp).resolve()
        def under(p,root):return p==root or root in p.parents
        def guard(event,args):
            if event.startswith('socket.') or event in ['urllib.Request','http.client.connect']:
                counters['network_denials']+=1;raise PermissionError('offline network denied')
            if event=='subprocess.Popen':
                if Path(str(args[0])).name!='pdftotext':counters['non_pdftotext_process_denials']+=1;raise PermissionError('only read-only pdftotext allowed')
            if event=='open':
                path,mode,flags=args
                if isinstance(path,int):return
                p=Path(os.fsdecode(path)).resolve();write=(isinstance(mode,str) and any(x in mode for x in ['w','a','x','+'])) or (isinstance(flags,int) and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)))
                if write:
                    if not under(p,target):counters['external_write_denials']+=1;raise PermissionError('write outside temporary output denied')
                elif not(under(p,HERE) or under(p,target) or str(p) in allowed or any(under(p,r) for r in runtime) or str(p)=='/dev/null'):
                    counters['helper_read_denials']+=1;raise PermissionError('mutable helper/peer read denied: '+str(p))
            if event in ['os.listdir','os.scandir']:
                p=Path(os.fsdecode(args[0])).resolve()
                if not (under(p,HERE) or under(p,target) or any(under(p,r) for r in runtime)):raise PermissionError('external directory discovery denied')
        sys.addaudithook(guard)
        # Exercise guards, not merely a claim that no network happened.
        import socket
        for fn in [lambda:socket.socket(),lambda:open(STATE/'data/forbidden-writer-fixture','w'),lambda:open(STATE/'live-polling-strategy.md','rb')]:
            try:fn()
            except PermissionError:pass
            else:raise AssertionError('guard did not reject')
        import subprocess
        try:subprocess.run(['python3','-c','pass'])
        except PermissionError:pass
        else:raise AssertionError('writer process guard did not reject')
        outputs=build.outputs();proof=[]
        for name,b in outputs.items():
            generated=target/(name if not name.startswith('@') else ('official-results-sources.csv' if name=='@csv' else 'official-results.md'))
            generated.parent.mkdir(parents=True,exist_ok=True);generated.write_bytes(b)
            original=HERE/name if not name.startswith('@') else STATE/('data/official-results-sources.csv' if name=='@csv' else 'official-results.md')
            expected=original.read_bytes();assert b==expected,('deterministic output mismatch',name)
            proof.append({'output':name,'bytes':len(b),'sha256':digest(b)})
    return {'status':'pass','outputs':proof,'count':len(proof),'guard_exercised':counters,'network':'denied','producer_imports_and_writers':'denied','mutable_aggregate_helper_peer_reads':'denied except individually pinned immutable original/source bodies and full frozen graph roles','reconstruction':'exact bytes in temporary outputs; no owned writes'}
if __name__=='__main__':print(json.dumps(run(),sort_keys=True))
