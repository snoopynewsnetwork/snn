"""Derive all 17 captured turnout sensitivity orders from our own original evidence."""
import collections,gzip,json,tarfile
from extract import ROOT,dump,sources,records,en
from reconcile import norm
def main():
    src=sources();hist={y:json.loads(gzip.decompress((ROOT/'extracted'/f'{y}-senate.json.gz').read_bytes())) for y in ('2024','2020','2018')};ids={'2024':'161257','2020':'144564','2018':'134055'};pr={r['name']:r for r in hist['2024']['rows'] if r['scope']=='Locality'};ass=json.loads(gzip.decompress((ROOT/'native-associations.json.gz').read_bytes()));parentinfo=json.loads((ROOT/'parent-identities.json').read_text());apis=json.loads(gzip.decompress((ROOT/'extracted/api-native-objects.json.gz').read_bytes()));api={a['scope_code']:a for a in apis};spec={}
    def key(y,r):return f'va:{ids[y]}:csv-record:{r["record"]:04d}'
    def put(name,rows):spec[name]=rows
    for y,h in hist.items():
        for scope,k in [('Precinct','native'),('Locality','locality-summary')]:put(f'{y}-{k}-senate',[(key(y,r),r['record'],r['total']) for r in h['rows'] if r['scope']==scope])
    put('2024-named-only-component',[(key('2024',r),r['record'],sum(r['votes'][:2])) for r in hist['2024']['rows'] if r['scope']=='Precinct'])
    for field in ['ballotsCast','totalVoters']:put('2024-enr-local-metadata-'+field,[(key('2024',r),r['record'],api[parentinfo[name]['code']]['election'][field]) for name,r in pr.items()])
    for field in ['api-ballotsCast','TotalVoteTurnout','TotalRegisteredVoters']:
        rows=[]
        for a in ass:
            r=a['historical']
            if field=='api-ballotsCast':value=a['api_voter_turnout']['ballotsCast'] if a['api_voter_turnout'] else None
            else:
                t=a['turnout_csv'];s=t['record']['cells'][t['header'].index(field)];value=int(s) if s else None
            rows.append((key('2024',r),r['record'],value))
        put('2024-native-'+field,rows)
    reg=json.loads((ROOT/'registration-controls.json').read_text());put('2024-nov1-registration',[(key('2024',pr[next(n for n,p in parentinfo.items() if p['code']==r['source_parent'][10:13])]),pr[next(n for n,p in parentinfo.items() if p['code']==r['source_parent'][10:13])]['record'],r['sums']['AllVoters']) for r in reg])
    for y in ('2018','2020','2022'):
        rr=records(src['turnout-'+y]);h=rr[0]['cells'];sums=collections.defaultdict(int)
        for r in rr[1:]:
            if r['cells'][h.index('district_type')]=='Congressional':sums[norm(r['cells'][h.index('locality')])]+=int(r['cells'][h.index('TotalVoteTurnout')])
        put(y+'-congressional-observed-turnout',[(key('2024',r),r['record'],sums.get(norm(n))) for n,r in pr.items()])
    h=hist['2018'];put('2018-native-aggregated-parents',[(key('2018',r),r['record'],sum(z['total'] for z in h['rows'] if z['scope']=='Precinct' and z['parent']==r['name'])) for r in h['rows'] if r['scope']=='Locality'])
    own={}
    for name,rows in spec.items():
        known=sorted([r for r in rows if r[2] is not None],key=lambda x:(-x[2],x[1]));V=sum(r[2] for r in known);cum=0;out=[];cross=None
        for rank,(k,rec,v) in enumerate(known,1):
            cum+=v;out.append(dict(key=k,record=rec,value=v,rank=rank,cumulative=cum))
            if cross is None and 5*cum>=4*V:cross=rank
        own[name]=dict(total=V,known_count=len(known),universe_count=len(rows),unknown_keys=sorted(r[0] for r in rows if r[2] is None),minimum80_count=cross,preceding_votes=out[cross-2]['cumulative'],crossing_votes=out[cross-1]['cumulative'],minimum_integer_volume=(4*V+4)//5,order=out)
    with tarfile.open(ROOT/'peer-capture.tar.gz','r:gz') as t:peer=json.load(t.extractfile('data/turnout/sensitivity-orders.json'))
    differences=[];checked={}
    for k,p in peer.items():
        a=own[k];errors=[]
        for f,v,w in [('total',a['total'],p['total']),('known_count',a['known_count'],p['count']),('minimum80_count',a['minimum80_count'],p['minimum80']['count']),('preceding_votes',a['preceding_votes'],p['minimum80']['preceding']['votes']),('crossing_votes',a['crossing_votes'],p['minimum80']['votes']),('order_keys',[x['key'] for x in a['order']],[x['key'] for x in p['order']]),('all_values',[x['value'] for x in a['order']],[x['reported_candidate_writein_votes'] for x in p['order']]),('all_cumulative',[x['cumulative'] for x in a['order']],[x['cumulative_votes'] for x in p['order']])]:
            if v!=w:errors.append(f)
        if 'unknown_keys' in p and sorted(p['unknown_keys'])!=a['unknown_keys']:errors.append('unknown_keys')
        checked[k]={'units':a['universe_count'],'known':a['known_count'],'minimum80_count':a['minimum80_count'],'differences':errors}
        if errors:differences.append({'order':k,'fields':errors})
    dump('all-source-sensitivity-orders.json.gz',own);dump('peer-all-order-audit.json',{'orders':checked,'differences':differences,'scope':'All17captured peer orders independently derived. Unknown keys preserved; known-only thresholds are not complete native ballot80 claims. Source key formatting is a declared translation, never a crossyear native join.'});print('all-order differences',differences)
if __name__=='__main__':main()
