#!/usr/bin/env python3
"""Review-pinned shared primary preflight replay, every write redirected here."""
import hashlib,runpy
from pathlib import Path
D=Path(__file__).resolve().parent
def main():
    script=D.parent/'preflight_primary_sources.py'
    expected='3d1ea31458afe26412fa70cc25e4c8e8bdda8b56867c9407da09514cd889765c'
    assert hashlib.sha256(script.read_bytes()).hexdigest()==expected,'Shared preflight changed; review before replay.'
    namespace=runpy.run_path(str(script));out=D/'preflight-replay';out.mkdir(exist_ok=True)
    namespace['main'].__globals__['D']=out
    namespace['main']()
if __name__=='__main__':main()
