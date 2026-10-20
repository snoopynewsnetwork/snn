"""Independent administrative controls, ballot publication and captured peer scope audit."""
import collections,csv,gzip,hashlib,html,io,json,re,tarfile,zipfile,xml.etree.ElementTree as ET
from extract import ROOT,STATE,sources,records,dump,en
def main():
    src=sources();annual={}
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>',src['turnout-summary'].decode(),re.S):
        cells=[html.unescape(re.sub('<[^>]+>','',re.sub(r'<!--.*?-->','',v,flags=re.S))).strip() for v in re.findall(r'<td[^>]*>(.*?)</td>',m[1],re.S)]
        if cells and cells[0] in ('2018','2020','2022','2024'):
            annual[cells[0]]=dict(raw_cells=cells,registered=int(cells[1].replace(',','')),total_voting=int(cells[3].replace(',','')),source_char_start=m.start(),source_char_end=m.end())
    dump('annual-controls.json',annual)
    admin={};allparents={en(x['locality']['name']) for x in json.loads(src['enr-2024-senate'])['ballotItemWithBreakdown']['breakdownResults']}
    for year in ('2018','2020','2022'):
        rr=records(src['turnout-'+year]);heads=rr[0]['cells'];hi={x:i for i,x in enumerate(heads)};views={}
        for view in ('Local','Congressional'):
            subset=[r for r in rr[1:] if r['cells'][hi['district_type']]==view];tuples=collections.defaultdict(list)
            for r in subset:tuples[tuple(r['cells'][hi[h]] for h in ['locality','precinct','district','district_type'])].append(r['record'])
            votes=sum(int(r['cells'][hi['TotalVoteTurnout']]) for r in subset if r['cells'][hi['TotalVoteTurnout']]!='');views[view]=dict(rows=len(subset),parent_count=len(set(r['cells'][hi['locality']] for r in subset)),missing_parents=sorted(allparents-set(r['cells'][hi['locality']] for r in subset)),duplicate_source_tuples=[{'tuple':list(k),'records':v} for k,v in tuples.items() if len(v)>1],observed_TotalVoteTurnout_sum=votes,observed_minus_annual=votes-annual[year]['total_voting'],scope='Overlapping views, repeated tuples not deduplicated. Sum of observed source rows, not established disjoint ballots.')
        admin[year]=views
    dump('administrative-coverage.json',admin)
    apis=json.loads(gzip.decompress((ROOT/'extracted/api-native-objects.json.gz').read_bytes()));state=next(x for x in apis if x['scope_code']=='STATE');native=[x for x in apis if x['scope_code']!='STATE'];turn=records(src['enr-2024-turnout-report']);hh=turn[0]['cells'];report={}
    for h in hh[4:]:
        i=hh.index(h);report[h]=dict(sum=sum(int(r['cells'][i]) for r in turn[1:] if r['cells'][i]!=''),missing_records=[r['record'] for r in turn[1:] if r['cells'][i]==''])
    api={h:{'sum':sum(v[h] for x in native for v in x['voterTurnout'] if v[h] is not None),'null':[(x['source'],v['id']) for x in native for v in x['voterTurnout'] if v[h] is None]} for h in ['ballotsCast','voterTurnout','voterRegistration']}
    scope=dict(turnout_csv=report,api_native=api,api_native_voterTurnout_records=sum(len(x['voterTurnout']) for x in native),api_native_inventory_count=sum(len(x['precincts']) for x in native),api_native_without_voterTurnout=[{'source':x['source'],'native_id':p['id'],'name':p['name']} for x in native for p in x['precincts'] if p['id'] not in {v['id'] for v in x['voterTurnout']}],api_local_election_ballotsCast_sum=sum(x['election']['ballotsCast'] for x in native),api_state_election=state['election'],api_state_voterRegistration_sum={k:sum(v[k] for v in state['voterRegistration']) for k in ['activeVoters','inactiveVoters','total']},annual2024=annual['2024'],turnout_csv_minus_annual=report['TotalVoteTurnout']['sum']-annual['2024']['total_voting'])
    dump('turnout-scope-controls.json',scope)
    rr=records(src['registration-2024-nov1']);header=rr[0]['cells'];reggroups=collections.defaultdict(list)
    for r in rr[1:]:
        if r['cells']:reggroups[r['cells'][0]].append(r)
    reg=[]
    num=lambda t:int(t.replace(',',''))
    for parent,rs in reggroups.items():
        totals={h:sorted({r['cells'][i] for r in rs}) for i,h in enumerate(header) if h in ['TotalPrecinctsInLocality','TotalActiveVotersPrecinctLocality','TotalInActiveVotersPrecinctLocality','TotalAllVotersPrecinctLocality']};assert all(len(v)==1 for v in totals.values());sums={h:sum(num(r['cells'][header.index(h)]) for r in rs if r['cells'][header.index(h)]!='') for h in ['ActiveVoters','InactiveVoters','AllVoters']};assert sums['ActiveVoters']==num(totals['TotalActiveVotersPrecinctLocality'][0]);assert sums['InactiveVoters']==num(totals['TotalInActiveVotersPrecinctLocality'][0]);assert sums['AllVoters']==num(totals['TotalAllVotersPrecinctLocality'][0]);reg.append(dict(source_parent=parent,records=[r['record'] for r in rs],controls=totals,sums=sums,precinct_rows=len(rs)))
    dump('registration-controls.json',reg)
    # Later acquired official ballot workbook: separate append-only pins, never rewrite original-first pin set.
    p=ROOT/'source/acquired/ballot-federal-xlsx.receipt.json';receipt=json.loads(p.read_text());f=ROOT/receipt['hops'][-1]['body_path'];raw=gzip.decompress(f.read_bytes());dump('source/additional-pins.json',{'receipt_path':str(p.relative_to(STATE)),'receipt_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'receipt':receipt,'entity':{'path':str(f.relative_to(STATE)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'raw_sha256':hashlib.sha256(raw).hexdigest(),'raw_bytes':len(raw)}})
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)] if 'xl/sharedStrings.xml' in z.namelist() else []
        sheet=ET.fromstring(z.read('xl/worksheets/sheet1.xml'));rows=[]
        for r in sheet.findall('.//s:sheetData/s:row',ns):
            cells=[]
            for c in r.findall('s:c',ns):
                v=c.find('s:v',ns);text=v.text if v is not None else ''.join(c.itertext());text=strings[int(text)] if c.get('t')=='s' else text;cells.append({'position':c.get('r'),'type':c.get('t'),'value':text})
            if any(c['value']=='Member, United States Senate' for c in cells):rows.append({'row':r.get('r'),'cells':cells})
    dump('current-ballot-publication.json',{'authority':'ELECT November 3 2026 Federal Offices workbook; index states updated10/6/26. Snapshot of published general-election roster, not an inferred primary nominee/current feed ID.','rows':rows,'mapping_status':'Names/party from this final-election publication only; later amendments and operational feed IDs need recheck.','current_api_candidate_ids':None});assert len(rows)==2
    # Additional peer comparisons from exact captured bytes only.
    with tarfile.open(ROOT/'peer-capture.tar.gz','r:gz') as t:
        read=lambda n:json.load(t.extractfile('data/turnout/'+n));peerannual=read('extracts/state-turnout-summary.json');peerreg=read('extracts/registration-nov1-controls.json');peeradmin=read('extracts/administrative-turnout-controls.json');peerscope=read('extracts/2024-turnout-scope-controls.json');orders=read('sensitivity-orders.json');peerprimary=read('extracts/2024-primary-controls.json');diff=[];compared=[]
        def ck(field,a,b):
            compared.append(field)
            if a!=b:diff.append({'field':field,'own':a,'peer':b})
        for y,v in annual.items():ck('annual-'+y,v['raw_cells'],peerannual[y]['raw_cells'])
        for g in reg:
            co=g['source_parent'][10:13];pr=next(x for x in peerreg['localities'] if x['locality_code']==co);ck('registration-'+co+'-records',g['records'],pr['source_records']);ck('registration-'+co+'-sums',g['sums'],pr['precinct_sums'])
        for h in ['TotalVoteTurnout','TotalRegisteredVoters']:
            ck('turnout-'+h+'-sum',report[h]['sum'],peerscope['turnout_csv'][h]['observed_sum']);ck('turnout-'+h+'-null-positions',report[h]['missing_records'],peerscope['turnout_csv'][h]['missing_rows'])
        ck('state-election-whole-object',state['election'],peerprimary['state_election_metadata']);ck('native-method-observation-count',sum(len(c['groupResults']) for x in native for n in x['ballotItemWithBreakdown']['breakdownResults'] for c in n['ballotOptions']),peerprimary['method_observation_count'])
        # Each historical raw token/header/position and native descending order, independently derived.
        for year,cid in [('2024','161257'),('2020','144564'),('2018','134055')]:
            orig=records(src['fresh-'+year+'-csv']);peerlines=[json.loads(x) for x in gzip.decompress(t.extractfile('data/turnout/extracts/'+year+'-all-original-rows.jsonl.gz').read()).decode().splitlines()];ck('all-raw-token-cells-'+year,[r['cells'] for r in orig],[r['cells'] for r in peerlines]);ck('all-raw-record-positions-'+year,[r['record'] for r in orig],[r['source_record'] for r in peerlines]);own=json.loads(gzip.decompress((ROOT/'extracted'/ (year+'-senate.json.gz')).read_bytes()));rows=sorted([r for r in own['rows'] if r['scope']=='Precinct'],key=lambda r:(-r['total'],r['record']));matching=[(k,v) for k,v in orders.items() if str(year) in k and 'senate' in k.lower()];
            for k,v in matching:
                scope_rows=rows if '-native-' in k else sorted([r for r in own['rows'] if r['scope']=='Locality'],key=lambda r:(-r['total'],r['record']));ck('comparator-order-'+k,[f'va:{cid}:csv-record:{r["record"]:04d}' for r in scope_rows],[r['key'] for r in v['order']])
        dump('peer-additional-reconciliation.json',{'scope':'Captured entire raw historical token/record fields, comparator order where named, all registration parent sums/records, annual controls, turnout null positions and state election object. No later peer bytes or peer calculator/model claim.','comparisons':compared,'differences':diff,'sensitivity_order_keys':list(orders),'administrative_control_peer_fields':{y:list(v) for y,v in peeradmin.items()}})
    print('additional peer differences',len(diff),'ballot Senate rows',2)
if __name__=='__main__':main()
