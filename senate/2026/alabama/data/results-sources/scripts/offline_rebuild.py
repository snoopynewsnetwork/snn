"""Deny network and mutable inputs while reconstructing into temporary outputs.

Only fixed full source pins from path-only acceptance and explicit individual
original references may be read outside owned outputs and Python/xlrd runtime.
Producer code can be read as source history for hashing, never executed.
"""
import contextlib,io,json,os,socket,subprocess,sys,tempfile
from pathlib import Path
import replay_authority as authority
import replay_originals as originals
import build_data
from negative_fixtures import run as negatives

STATE=authority.STATE;OWN=authority.OWN

def main():
    a=authority.parse((STATE/authority.ACCEPTANCE).read_bytes())
    allowed={str((STATE/authority.ACCEPTANCE).resolve()),str((STATE/authority.CONTRACT['path']).resolve())}
    for key in ['frozen_file_pins','complete_source_companion_files','complete_source_object_reference_bodies']:
        allowed.update(str((STATE/x['path']).resolve()) for x in a[key])
    for r in a['historical_full_body_resolvers']:
        st=r['storage'];pin=st.get('archive') or st.get('file')
        allowed.add(str((STATE/pin['path']).resolve()))
    witness=authority.parse((STATE/'data/turnout/source/original-first-witness.json').read_bytes())
    for s in witness['sources']:
        if s['kind']=='shared_original':allowed.add(str((STATE.parents[2]/s['receipt']['shared_path']).resolve()))
        else:
            path=STATE/'data/turnout'/s['receipt'];allowed.add(str(path.resolve()))
            r=authority.parse(path.read_bytes())
            allowed.update(str((STATE/'data/turnout'/p['path']).resolve()) for p in r['parts'])
    for x in a['complete_source_companion_files']:
        if '/baselines/source/http/' in x['path'] and x['path'].endswith('.receipt.json'):
            r=authority.parse((STATE/x['path']).read_bytes())
            if r.get('stored_path_relative_baselines'):
                allowed.add(str((STATE/'data/baselines'/r['stored_path_relative_baselines']).resolve()))
    ownprefix=str(OWN.resolve())+os.sep
    reporting={str((STATE/'official-results.md').resolve()),str((STATE/'data/official-results-sources.csv').resolve())}
    runtime=[str(Path(sys.base_prefix).resolve())+os.sep,'/private/tmp/al-turnout-deps/']
    with tempfile.TemporaryDirectory(prefix='al-official-isolated-') as td:
        temp=Path(td).resolve();tempprefix=str(temp)+os.sep
        def within(p,prefix):return p.startswith(prefix) or p==prefix.rstrip(os.sep)
        def guard(event,args):
            if event.startswith('socket.') or event in ['subprocess.Popen','os.system','os.posix_spawn','os.exec']:
                raise PermissionError('offline network/subprocess route denied')
            if event=='exec':
                code=args[0];filename=getattr(code,'co_filename','')
                if str(STATE) in filename and not filename.startswith(str(OWN)):
                    raise PermissionError('producer/peer/helper execution denied')
            if event=='open':
                name,mode,flags=args
                if isinstance(name,int):return
                p=str(Path(name).resolve());writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT)))
                if writing:
                    if not within(p,tempprefix):raise PermissionError('non-temporary output denied')
                elif not (p in allowed or p in reporting or within(p,ownprefix) or within(p,tempprefix) or any(within(p,x) for x in runtime)):
                    raise PermissionError('unlisted mutable/source discovery route denied: '+p)
            if event in ['os.listdir','os.scandir']:
                name=args[0]
                if isinstance(name,int):return
                p=str(Path(name or '.').resolve())
                if not (within(p,ownprefix) or within(p,tempprefix) or any(within(p,x) for x in runtime)):
                    raise PermissionError('external directory discovery denied')
        sys.addaudithook(guard)
        probes=[]
        def rejected(name,fn):
            try:fn()
            except PermissionError as e:probes.append({'route':name,'status':'DENIED','reason':str(e)})
            else:raise AssertionError('unsafe route allowed: '+name)
        rejected('network socket',lambda:socket.socket())
        rejected('mutable newsroom aggregate',lambda:(STATE/'data/news/manifest.json').read_bytes())
        rejected('current helper discovery',lambda:list((STATE/'data/turnout/scripts').iterdir()))
        rejected('producer writer execution',lambda:exec(compile('pass',str(STATE/'data/turnout/scripts/build.py'),'exec')))
        rejected('new peer discovery',lambda:list((STATE.parent/'arkansas').iterdir()))
        rejected('owned output mutation',lambda:(OWN/'qa/SHOULD-NOT-EXIST').write_text('denied'))
        rejected('producer subprocess',lambda:subprocess.run([sys.executable,'-c','pass']))
        with contextlib.redirect_stdout(io.StringIO()) as captured:
            source=authority.replay()
            original,_=originals.replay()
            negative=negatives(write=False)
        outputs=build_data.assemble();rebuilt=[]
        destination=temp/'results-sources';destination.mkdir()
        for rel,b in outputs.items():
            p=destination/rel;p.write_bytes(b)
            assert b==(OWN/rel).read_bytes(),('deterministic byte mismatch',rel)
            rebuilt.append({'path':rel,'bytes':len(b),'sha256':authority.digest(b)})
        build_data.validate(authority.parse(__import__('gzip').decompress(outputs['historical-hierarchy.json.gz'])))
        result={'status':'PASS','acceptance_path':authority.ACCEPTANCE,'source_graph':source['checks'],
             'originals':original['counts'],'negative_fixtures':negative,'actual_route_probes':probes,
             'reconstructed_outputs':rebuilt,'all_temp_outputs_byte_identical':True,'network_used':False,
             'producer_imports_or_execution':False,'mutable_aggregate_or_peer_inputs':False,
             'current_legal_geographic_live_approval':False}
        print(json.dumps(result,indent=2))

if __name__=='__main__':main()
