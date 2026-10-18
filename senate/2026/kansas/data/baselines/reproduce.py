"""Sequential offline build, with no shared-file mutation or network."""
import os,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def main():
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    for script,args in [('build.py',[]),('calculate.py',[]),('sumner_methods.py',[]),('live_remainder.py',['--examples']),('reconcile_peer.py',[]),('render_report.py',[]),('validate.py',[])]:
        subprocess.run([sys.executable,'-S',str(H/script)]+args,env=env,check=True)
if __name__=='__main__':main()
