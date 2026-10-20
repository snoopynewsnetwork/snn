"""All authorized outputs only; no network, producer imports or current admission."""
import os,sys,json
os.environ['PYTHONDONTWRITEBYTECODE']='1'
sys.dont_write_bytecode=True
from acquire import HERE
def main(audit=False):
    import replay,check_samples,check_historical,negative_fixtures,validate,seal
    if audit:
        before=seal.audit()
        for module,filename,fn in [(replay,'replay-validation.json',replay.replay),(check_samples,'sample-validation.json',check_samples.main),(check_historical,'historical-validation.json',check_historical.main),(negative_fixtures,'negative-fixtures.json',negative_fixtures.main),(validate,'validation.json',validate.main)]:
            v=fn(False);assert v==json.loads((HERE/filename).read_bytes()),'independently replayed proof '+filename
            print(filename,'pass',v.get('checks',v.get('negative_cases')),flush=True)
        assert seal.audit()==before,'no owned byte changed during read-only audit'
        print(json.dumps(before));return before
    import extract_law,extract,legal_dates,build,report
    replay.replay();extract_law.main();extract.main();check_samples.main();check_historical.main();negative_fixtures.main();legal_dates.main();build.main();report.main();validate.main();result=seal.seal()
    print('sealed',json.dumps(result),flush=True)
    return main(True)
if __name__=='__main__':main('--audit' in sys.argv)
