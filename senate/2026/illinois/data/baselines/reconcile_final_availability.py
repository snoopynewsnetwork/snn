"""Freeze final peer availability semantics separately from earlier immutable captures."""
import csv,gzip,io,json,collections
from source_io import ROOT,STATE,sha,dump
def main():
    dest=ROOT/'peer-final-availability';dest.mkdir(exist_ok=True);manifest=[];checks=0;errors=[]
    def check(ok,ctx):
        nonlocal checks
        checks+=1
        if not ok:errors.append(ctx)
    def captured(f):
        p=dest/(f if f.endswith('.gz')else f+'.gz')
        if not p.exists():
            b=(STATE/'data/turnout/extract'/f).read_bytes();p.write_bytes(b if f.endswith('.gz')else gzip.compress(b,mtime=0))
        z=p.read_bytes();b=gzip.decompress(z);manifest.append(dict(origin='data/turnout/extract/'+f,capture=str(p.relative_to(ROOT)),bytes=len(z),sha256=sha(z)))
        return b
    pc=list(csv.DictReader(io.StringIO(captured('county-all-years.csv').decode())));mine={(r['year'],r['county_key']):r for r in csv.DictReader((ROOT.parent/'county-baselines.csv').open())}
    for p in pc:
        r=mine[p['year'],p['county_authority_id']]
        for a,b in [('native_generic_source_present','native_generic_writein_source_present'),('native_generic_observed','native_generic_writein_observed'),('native_generic_recorded_sum','native_generic_writein_marks')]:check(r[a]==p[b],['county final availability',p['year'],p['county_authority_id'],a])
    cats=collections.defaultdict(dict)
    for r in csv.DictReader((ROOT/'extract/authority-candidate-category-totals.csv').open()):cats[r['year'],r['JurisdictionID']][r['candidate_or_category_literal']]=int(r['votes'])
    for y in ['2020','2022','2024']:
        authority=[json.loads(l)for l in captured(f'authority-native-{y}.jsonl.gz').splitlines()]
        for p in authority:
            c=cats[y,p['authority_id']];present=any(k.lower()=='write-in'for k in c);recorded=sum(v for k,v in c.items()if k.lower()=='write-in');observed=recorded if present else None
            check(c==p['literal_categories'],['authority all categories final',y,p['authority_id']]);check(p['generic_writein_marks']==observed,['authority observed null vs0',y,p['authority_id']]);check(p['generic_writein_recorded_sum']==recorded and p['generic_writein_source_present']==present,['authority source presence final',y,p['authority_id']])
        units=[json.loads(l)for l in captured(f'native-units-{y}.jsonl.gz').splitlines()];ours={(r['JurisdictionID'],r['PrecinctName']):r for r in json.loads((ROOT/f'extract/{y}-units.json').read_text())}
        for p in units:
            r=ours[p['authority_id'],p['precinct_name_literal']];present=any(k in r['literal_category_record_sums']for k in [r['A_name'],r['B_name']]+list(r['printed_other_missing_candidates']))
            values=[v for v in p['printed_candidate_votes'].values()if v is not None];observed=sum(values)if values else None
            check(r['literal_category_record_sums']==p['literal_categories'],['all native literal category presence',y,r['unit_key']]);check(r['generic_writein_marks']==p['generic_writein_marks'],['native generic null vs0',y,r['unit_key']]);check((p['printed_observed_sum']==observed),['peer observed printed vs administrative unavailable',y,r['unit_key']])
    dump(dest/'manifest.json',manifest);result=dict(status='pass'if not errors else'fail',checks=checks,errors=errors,scope='Final frozen county generic observed/presence/recorded sum, all108authority category availability each year, allnative literal category/observed generic/null administrative semantics. No source-count or primary5540membership change.')
    dump(ROOT/'peer-final-availability-reconciliation.json',result);print(json.dumps({**result,'errors':errors[:5]},indent=2));assert not errors
if __name__=='__main__':main()
