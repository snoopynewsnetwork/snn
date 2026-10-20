"""Offline deterministic rebuild into a temporary directory; never acquisition."""
import argparse,contextlib,gzip,hashlib,io,json,socket,tempfile
from pathlib import Path
import build,format_inventory,test_research
from acquire import ROOT,dump
from replay import STATE,strict

def deny(*args,**kwargs):raise RuntimeError('network forbidden during offline reproduction')
def run(write=False):
    old_socket,old_connect=socket.socket,socket.create_connection
    socket.socket=deny;socket.create_connection=deny
    comparisons=[]
    try:
        with tempfile.TemporaryDirectory(prefix='va-official-offline-') as td:
            dest=Path(td)
            products=build.run(dest)
            for relative in products:
                actual=(dest/relative).read_bytes();expected=(STATE/relative).read_bytes()
                assert actual==expected,('non-deterministic product',relative)
                comparisons.append({'path':relative,'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest()})
            formats=format_inventory.run(dest/'data/results-sources')
            for relative in formats:
                actual=(dest/'data/results-sources'/relative).read_bytes();expected=(ROOT/relative).read_bytes()
                assert actual==expected,('non-deterministic full-format extraction',relative)
                comparisons.append({'path':'data/results-sources/'+relative,'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest()})
        with contextlib.redirect_stdout(io.StringIO()):fixtures=test_research.run(False)
        assert fixtures==strict((ROOT/'negative-fixtures.json').read_bytes())
    finally:socket.socket=old_socket;socket.create_connection=old_connect
    result={'status':'pass','network_access':'socket creation/connection denied during rebuild',
      'producer_imports_or_execution':False,'mutable_news_map_optional_peer_dependencies':False,
      'complete_products_rebuilt_byte_identically':comparisons,'negative_cases':fixtures['negative_cases'],
      'scope':'All deterministic reporting/inventory/schema/format products and admission mutations. Original acquisitions, discovery snapshots, manual annotations/rendered views and frozen historical originals are retained evidence, not regenerated network responses. Full historical replay is separately required by audit.py.'}
    if write:dump(ROOT/'reproduction.json',result)
    print(json.dumps({'status':'pass','byte_identical_products':len(comparisons),'negative_cases':fixtures['negative_cases']}))
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();run(a.write)
