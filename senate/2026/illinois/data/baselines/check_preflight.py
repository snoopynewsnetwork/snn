"""Required coordinator helper replay, redirecting every write to owned paths."""
import runpy
from source_io import ROOT,STATE
def main():
    helper=ROOT/'source/preflight-primary-source-code.py';module=runpy.run_path(str(helper));main=module['main'];main.__globals__['D']=ROOT/'source';main.__globals__['N']=STATE/'data/news';main()
if __name__=='__main__':main()
