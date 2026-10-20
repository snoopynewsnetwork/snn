"""Immutable final native/authority full-order reciprocal capture and comparison."""
import csv,gzip,io,json
from source_io import ROOT,STATE,sha,dump
def main():
    checks=0;errors=[];manifest=[];dest=ROOT/'peer-priority-capture';dest.mkdir(exist_ok=True)
    def check(ok,context):
        nonlocal checks
        checks+=1
        if not ok:errors.append(context)
    cases=[('native','printed_observed_sum','native-2024-printed-observed'),('native','printed_plus_generic_observed','native-2024-printed-plus-generic-records'),('authority','printed_observed_sum','authority-2024-printed'),('authority','printed_plus_generic_observed','authority-2024-printed-plus-generic-records')]
    for level,field,ours in cases:
        f=f'{level}-2024-order-{field}.jsonl.gz';origin=STATE/'data/turnout/extract'/f;b=origin.read_bytes();p=dest/f
        if p.exists():assert p.read_bytes()==b,'Immutable capture changed; version separately.'
        else:p.write_bytes(b)
        manifest.append(dict(origin=str(origin.relative_to(STATE)),captured=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)))
        peer=[json.loads(l)for l in gzip.decompress(b).splitlines()];minep=ROOT/'priority'/(ours+'.csv'+('.gz'if level=='native'else''));mb=minep.read_bytes();mb=gzip.decompress(mb)if minep.suffix=='.gz'else mb;mine=list(csv.DictReader(io.StringIO(mb.decode())));check(len(mine)==len(peer),[ours,'whole coverage'])
        for pos,(m,r)in enumerate(zip(mine,peer),1):
            check(m['JurisdictionID']==r['authority_id'],[ours,pos,'authority literal ID'])
            if level=='native':check(m['PrecinctName']==r['precinct_name_literal'],[ours,pos,'literal precinct'])
            recorded=r.get('printed_known_recorded_sum',r.get(field))if field=='printed_observed_sum'else r[field]
            if recorded is None:recorded=0 # Only explicit empty source-record aggregation, never an observed vote zero.
            check(int(m['ranking_value'])==recorded,[ours,pos,'recorded scope value'])
            check(int(m['cumulative_votes'])==r['cumulative_votes'],[ours,pos,'cumulative'])
            check(int(m['state_denominator'])==r['share_denominator'],[ours,pos,'denominator'])
            check(int(m['order_position'])==r['order_position'],[ours,pos,'full order position'])
            rank=int(m['rank'])if m['rank']else None;check(rank==r['rank'],[ours,pos,'observed rank including null admin'])
    dump(dest/'manifest.json',manifest);result=dict(status='pass'if not errors else'fail',checks=checks,errors=errors,scope='Both full10062native orders and108authority orders; explicit null admin ranks after observed numeric zero; source-known printed and printed-plus-generic scopes kept separate.',contract='Native printed-known N5592368,minimum5540,4473789->4474312; no legal-native eligibility or current-geometry approval')
    dump(ROOT/'peer-native-priority-reconciliation.json',result);print(json.dumps({**result,'errors':errors[:5]},indent=2));assert not errors
if __name__=='__main__':main()
