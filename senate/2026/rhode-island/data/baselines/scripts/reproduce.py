"""Rebuild deterministic extracts in an isolated temporary tree; production paths stay read-only.
Original public bodies are symlinked by individually fixed receipt references and hash checked.
Does not rerun acquisition, freeze, peer capture, seal or manifest.
"""
import json,os,shutil,subprocess,sys,tempfile
from common import *
def main():
    with tempfile.TemporaryDirectory(prefix='ri-baseline-reproduce-') as tmp:
        state=Path(tmp)/'rhode-island';dest=state/'data/baselines';dest.mkdir(parents=True)
        shutil.copytree(BASE/'scripts',dest/'scripts')
        (dest/'source').mkdir();shutil.copy2(BASE/'source/inputs.json',dest/'source/inputs.json')
        shutil.copytree(BASE/'source/acquired',dest/'source/acquired')
        for r in inputs().values():
            target=state/r['body_path'];target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():target.symlink_to((STATE/r['body_path']).resolve())
        for folder in ['witness','extracts','qa','scenarios']:(dest/folder).mkdir(exist_ok=True)
        # Priority is itself recomputed independently from the raw original roots below.
        for script in ['extract_originals.py','publications.py','build.py','controls.py','supplements.py']:
            if script=='build.py':
                rows=[json.loads(l) for l in gzip.decompress((dest/'witness/root-selected.jsonl.gz').read_bytes()).splitlines()]
                groups={}
                for r in rows:
                    if r['year']!=2024 or r['contest_title'].strip()!='Senator in Congress':continue
                    v=groups.setdefault(r['source_code'],dict(source_code=r['source_code'],name=r['source_name'].strip(),first_byte=r['byte_start'],line=r['line'],votes=0,key=f"{r['zip_sha256']}#{r['member']}#{r['byte_start']}"));v['votes']+=r['votes']
                ranked=sorted(groups.values(),key=lambda x:(-x['votes'],x['first_byte']));total=sum(x['votes'] for x in ranked);cum=0
                for i,x in enumerate(ranked,1):old=cum;cum+=x['votes'];x.update(rank=i,cumulative=cum,priority=old*5<total*4)
                (dest/'witness/independent-native-priority.json').write_text(json.dumps(ranked,indent=2,ensure_ascii=False)+'\n')
            p=subprocess.run([sys.executable,'-B',str(dest/'scripts'/script)],capture_output=True,text=True)
            if p.returncode:raise RuntimeError(script+': '+p.stderr)
        paths=['witness/root-selected.jsonl.gz','witness/selected-all-views.jsonl.gz','source/field-layout.json','source/zip-members.json',
            'witness/independent-controls.json','witness/independent-native-priority.json','extracts/native-inventory.json',
            'extracts/native-baselines.jsonl.gz','extracts/state-baselines.json','extracts/parent-baselines.json',
            'extracts/publication-controls.json','extracts/state-denominator-controls.json','extracts/2024-senate-writein-reconciliation.json',
            'native-priority-contract.json','native-targets.csv','state-scenarios.csv','parent-selected-targets.csv',
            'parent-contributions.csv','scenario-settings.json','../county-baselines.csv']
        paths += [str(p.relative_to(BASE)) for p in sorted((BASE/'scenarios').glob('*-historical*.json'))]
        checks=[{'path':p,'original_sha256':sha((BASE/p).read_bytes()),'reproduced_sha256':sha((dest/p).read_bytes()),
                 'equal':(BASE/p).read_bytes()==(dest/p).read_bytes()} for p in paths]
        print(json.dumps({'all_equal':all(r['equal'] for r in checks),'files':checks},indent=2))
        if not all(r['equal'] for r in checks):raise SystemExit(1)
if __name__=='__main__':main()
