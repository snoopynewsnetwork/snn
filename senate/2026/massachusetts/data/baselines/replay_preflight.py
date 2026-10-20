"""Reviewed shared script, every input pinned and output redirected to owned paths."""
import importlib.util,json,tempfile
from pathlib import Path
from extract_originals import ROOT,originals
def main():
    sources=originals();p=ROOT.parent/'preflight_primary_sources.py'
    with tempfile.TemporaryDirectory(prefix='ma-baseline-preflight-') as td:
        n=Path(td);pins=[]
        for sid in ['sos-2024-senate-municipal-csv','sos-2024-senate-precinct-csv']:
            receipt=sources[sid][0].copy();receipt.pop('shared_path');pins.append(receipt)
            (n/receipt['asset']).symlink_to((ROOT/sources[sid][0]['shared_path']).resolve())
        (n/'manifest.json').write_text(json.dumps(pins))
        spec=importlib.util.spec_from_file_location('reviewed_shared_preflight',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.D=ROOT/'source/preflight-replay';module.N=n;module.main()
if __name__=='__main__':main()
