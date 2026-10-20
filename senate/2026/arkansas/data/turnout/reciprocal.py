#!/usr/bin/env python3
"""Bounded captured-final reciprocal, independent adapters from original bytes.

No producer, peer parser, calculator, discovery helper or network is executed.
Every compared peer value is checked against the original source and the
frozen turnout representation; extra 2020 presidential numeric lanes and all
scenarios/outcomes are explicitly outside the numerical comparison.
"""
import argparse,collections,copy,csv,gzip,hashlib,io,json,pathlib,re,tarfile,urllib.parse,xml.etree.ElementTree as ET,zipfile
P=pathlib.Path(__file__).resolve().parent;S=P.parents[1];REPO=P.parents[4];H=P/'history/captured-final-reciprocal'
def sha(b):return hashlib.sha256(b).hexdigest()
class Capture:
    def __init__(self,label):
        self.capture=json.loads((H/'capture.json').read_text());self.spec=self.capture[label];self.records={r['path']:r for r in self.spec['records']}
        b=(H/self.spec['archive']).read_bytes();assert sha(b)==self.spec['archive_sha256'];assert len(b)==self.spec['archive_bytes']
        self.tar=tarfile.open(fileobj=io.BytesIO(b),mode='r:gz')
        assert set(self.tar.getnames())=={r['member'] for r in self.records.values() if r['storage']=='tar-member'}
    def read(self,path):
        r=self.records[path]
        b=(REPO/r['reference_path']).read_bytes() if r['storage']=='immutable-reference' else self.tar.extractfile(r['member']).read()
        assert sha(b)==r['sha256'] and len(b)==r['bytes'],path
        return b
    def own(self,path):return self.read('data/turnout/'+path)
    def peer(self,path):return self.read('data/baselines/'+path)
    def audit(self):
        mfpath=next(path for path in self.records if path.endswith('/asset-manifest.json'))
        mfbody=self.read(mfpath);assert sha(mfbody)==self.spec['manifest_sha256'] and len(mfbody)==self.spec['manifest_bytes']
        mf=json.loads(mfbody);assert set(self.records)=={r['path'] for r in mf['assets']}|{mfpath}
        for r in mf['assets']:
            actual=self.records[r['path']];assert actual['sha256']==r['sha256'] and actual['bytes']==r['bytes']
        for path in self.records:self.read(path)
        return len(self.records)
class Checks:
    def __init__(self):self.count=0;self.groups={}
    def eq(self,a,b,path=''):
        self.count+=1
        assert type(a) is type(b),(path,'type',type(a).__name__,type(b).__name__)
        if isinstance(a,dict):
            assert set(a)==set(b),(path,'keys',set(a)-set(b),set(b)-set(a))
            for k in a:self.eq(a[k],b[k],path+'/'+str(k))
        elif isinstance(a,list):
            assert len(a)==len(b),(path,'length',len(a),len(b))
            for i,(x,y) in enumerate(zip(a,b)):self.eq(x,y,path+'/'+str(i))
        else:assert a==b,(path,'value',str(a)[:120],str(b)[:120])
    def group(self,name,start):self.groups[name]=self.count-start
def indexed(rows,fields):
    result={}
    for row in rows:
        k=tuple(row[f] for f in fields);assert k not in result,('duplicate key',k);result[k]=row
    return result
def pointer(doc,path):
    value=doc
    for part in path.split('/')[1:]:
        part=part.replace('~1','/').replace('~0','~')
        value=value[int(part)] if isinstance(value,list) else value[part]
    return value
def derive(capt,checks):
    """Use only fixed turnout original receipts/bodies; no peer data here."""
    receipts={};raws={};source_paths={}
    for path in capt.records:
        if not(path.startswith('data/turnout/source/') and path.endswith('.receipt.json')):continue
        r=json.loads(capt.read(path));receipts[r['id']]=(path,r)
        if r.get('shared_original_path'):
            source_path=r['shared_original_path'];b=(REPO/source_path).read_bytes()
        else:
            source_path=str(pathlib.PurePosixPath('senate/2026/arkansas')/pathlib.PurePosixPath(path).parent/r['asset'])
            b=capt.read(str(pathlib.PurePosixPath(path).parent/r['asset']))
        body=gzip.decompress(b);assert sha(b)==r['stored_sha256'] and sha(body)==r['raw_sha256']
        assert len(body)==r.get('raw_bytes',r.get('bytes'))
        raws[r['id']]=body;source_paths[r['id']]=(source_path,b)
    assert len(receipts)==490
    docs={}
    def doc(sid):
        if sid not in docs:docs[sid]=json.loads(raws[sid])
        return docs[sid]
    native={};controls=[];candidates=[];inventories=[];metadata=[];turnouts=[]
    csvfields=['lane','year','contest','level','county','county_id','native_id','native_name','candidate_id','candidate','party_id','party_literal','method','votes','source_id','position']
    def candidate(lane,year,title,level,county,fips,nid,name,cid,cname,pid,party,method,votes,sid,pos):
        candidates.append(dict(zip(csvfields,[str(x) if x is not None else '' for x in [lane,year,title,level,county,fips,nid,name,cid,cname,pid,party,method,votes,sid,pos]])))
    def node(lane,year,title,cid,level,fips,nid,sid,pos,obj,county='',name=''):
        api=lane.endswith('-api');choices=obj['choices' if api else 'Candidates'];vfield='totalVotes' if api else 'TotalVotes'
        removed={'locations'} if api else {'Counties','Precincts'}
        controls.append(dict(lane=lane,year=year,contest=title,contest_id=cid,level=level,county_id=fips,native_id=nid,total=obj[vfield],sum_choices=sum(c[vfield] for c in choices),source_id=sid,position=pos,raw={k:v for k,v in obj.items() if k not in removed}))
        info=doc(f'{year}-info')['response'];desc=doc(f'{year}-metadata')['response']['contests'].get(cid) if cid else None
        vector={};parties={};positions=[]
        for i,ch in enumerate(choices):
            if api:
                cname=desc['choices'][ch['choiceID']]['name'];party=info['parties'].get(ch['partyID'],{}).get('partyName','');ccid=ch['choiceID'];pid=ch['partyID'];cp=pos+'/choices/'+str(i)
            else:cname=ch['Name'];party=ch['PartyName'];ccid=pid=None;cp=pos+'/Candidates/'+str(i)
            assert cname not in vector;vector[cname]=ch[vfield];parties[cname]=party;positions.append(dict(source_id=sid,position=cp))
            candidate(lane,year,title,level,county,fips,nid,name,ccid,cname,pid,party,'All',ch[vfield],sid,cp)
        if level=='native':
            official_id=nid if api else None
            constructed='AR:'+lane+':'+fips+':'+urllib.parse.quote(nid,safe='')
            record=dict(key=constructed,lane=lane,year=str(year),contest=title,county_fips=fips,county_name=county,native_id=official_id,native_name=name,candidates=vector,party_literals=parties,source_positions=positions,methods={},votes=obj[vfield])
            native.setdefault(lane,[]).append(record)
    for year in [2020,2022,2024]:
        cid={2020:'560',2022:'1123',2024:'366'}[year];title='U.S. President' if year==2024 else 'U.S. Senate';info=doc(f'{year}-info')['response'];meta=doc(f'{year}-metadata')['response']['contests'];state=doc(f'{year}-federal-state')['response']['contests'][cid]
        # All selected metadata witnesses, including contextual 2020 identity metadata.
        for mid,m in meta.items():
            if m['contestName'] in [title,'U.S. President, Vice President']:
                metadata.append(dict(year=year,contest_id=mid,metadata=m,parties=info['parties'],vote_types=info['voteTypes']))
        node(f'{year}-api',year,title,cid,'state',None,None,f'{year}-federal-state','/response/contests/'+cid,state)
        for fips,obj in state['locations'].items():node(f'{year}-api',year,title,cid,'county',fips,None,f'{year}-federal-state','/response/contests/'+cid+'/locations/'+fips,obj,info['locations'][fips]['locationName'])
        reverse={v['locationName'].upper():k for k,v in info['locations'].items()}
        for fips,loc in info['locations'].items():
            sid=f'{year}-federal-{fips}';obj=doc(sid)['response']['contests'][cid];base='/response/contests/'+cid
            node(f'{year}-api',year,title,cid,'county-native-response',fips,None,sid,base,obj,loc['locationName'])
            for nid,leaf in obj['locations'].items():node(f'{year}-api',year,title,cid,'native',fips,nid,sid,base+'/locations/'+nid,leaf,loc['locationName'],loc['locations'][nid]['locationName'])
            # Descriptor scope is explicit: a separate contextual contest can repeat descriptors.
            for mid,m in meta.items():
                if m['contestName'] not in [title,'U.S. President, Vice President']:continue
                for nid,nloc in loc['locations'].items():inventories.append(dict(year=year,county_id=fips,county=loc['locationName'],native_id=nid,native_name=nloc['locationName'],info_position=f'/response/locations/{fips}/locations/{nid}',raw=nloc,contest_id=mid))
            tsid=f'{year}-turnout-{fips}';tr=doc(tsid)
            turnouts.append(dict(year=year,county_id=fips,county=loc['locationName'],source_id=tsid,publication={k:v for k,v in tr.items() if k!='response'},response=tr['response']))
        full=doc(f'{year}-full');fi,fc=next((i,c) for i,c in enumerate(full['ContestData']) if c['ContestName']==title);base='/ContestData/'+str(fi)
        node(f'{year}-full',year,title,None,'state',None,None,f'{year}-full',base,fc)
        for wi,w in enumerate(fc['Counties']):
            fips=reverse[w['CountyName'].upper()];wp=base+'/Counties/'+str(wi)
            node(f'{year}-full',year,title,None,'county-wrapper',fips,str(wi),f'{year}-full',wp,w,w['CountyName'])
            for pi,pr in enumerate(w['Precincts']):node(f'{year}-full',year,title,None,'native',fips,str(wi)+'/'+str(pi),f'{year}-full',wp+'/Precincts/'+str(pi),pr,w['CountyName'],pr['PrecinctName'])
    # Parse complete ZIP parts directly, then build exact relevant row/cell witnesses.
    z=zipfile.ZipFile(io.BytesIO(raws['2024-xlsx-current']));ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}';strings=[''.join(s.itertext()) for s in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    xmlrows=[];header=None;xnative={};county_names={r['locationName']:f for f,r in doc('2024-info')['response']['locations'].items()}
    for rr in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).find(ns+'sheetData'):
        cells=[]
        for cell in rr:
            vv=cell.find(ns+'v');raw=vv.text if vv is not None else None;value=strings[int(raw)] if cell.get('t')=='s' else raw
            cells.append(dict(position=cell.get('r'),type=cell.get('t'),value=value,raw_value=raw))
        if rr.get('r')=='1':header=[c['value'] for c in cells];header_cells=cells;continue
        values=[c['value'] for c in cells]
        if values[2]!='U.S. President':continue
        row=int(rr.get('r'));xmlrows.append(dict(source_id='2024-xlsx-current',row=row,cells=cells));county,name,title,cname,party=values[:5];fips=county_names[county];key='AR:2024-xlsx:'+fips+':'+urllib.parse.quote(name,safe='')
        r=xnative.setdefault(key,dict(key=key,lane='2024-xlsx',year='2024',contest=title,county_fips=fips,county_name=county,native_id=None,native_name=name,candidates={},party_literals={},source_positions=[],methods={m:{} for m in header[5:9]},votes=0))
        assert cname not in r['candidates'];r['candidates'][cname]=int(values[9]);r['party_literals'][cname]=party;r['votes']+=int(values[9]);r['source_positions'].append(dict(source_id='2024-xlsx-current',position='xl/worksheets/sheet1.xml/J'+str(row)))
        for i in range(5,10):
            candidate('2024-xlsx',2024,title,'native',county,fips,None,name,None,cname,None,party,header[i],int(values[i]),'2024-xlsx-current','xl/worksheets/sheet1.xml/'+cells[i]['position'])
            if i<9:r['methods'][header[i]][cname]=int(values[i])
    native['2024-xlsx']=list(xnative.values())
    return dict(receipts=receipts,raws=raws,source_paths=source_paths,docs=docs,native=native,controls=controls,candidates=candidates,inventories=inventories,metadata=metadata,turnouts=turnouts,xrows=xmlrows,header=header,header_cells=header_cells,zip=z)
def run(write=False):
    own=Capture('own');peer=Capture('peer');check=Checks();start=check.count
    check.eq(own.audit(),1028,'whole-turnout-captured-body-count');check.eq(peer.audit(),314,'whole-baseline-captured-body-count')
    for r in own.capture['shared_originals']:
        b=(REPO/r['path']).read_bytes();check.eq(sha(b),r['sha256'],'shared-stored-hash');check.eq(sha(gzip.decompress(b)),r['raw_sha256'],'shared-raw-hash')
    check.group('all_whole_old_bodies_and_shared_originals',start)
    data=derive(own,check);start=check.count
    pins=json.loads(peer.peer('source/original-pins.json'));check.eq(len(pins),490,'peer-original-pins')
    check.eq({p['receipt']['id'] for p in pins},set(data['receipts']),'all490-source-identities')
    for pin in pins:
        sid=pin['receipt']['id'];path,r=data['receipts'][sid];rb=own.read(path)
        check.eq(pin['receipt_path'],'senate/2026/arkansas/'+path,sid+'/receipt-path');check.eq(pin['receipt_sha256'],sha(rb),sid+'/whole-receipt-bytes');check.eq(pin['receipt'],r,sid+'/all-receipt-metadata')
        source_path,stored=data['source_paths'][sid]
        check.eq(pin['path'],source_path,sid+'/original-path');check.eq(pin['raw_sha256'],sha(data['raws'][sid]),sid+'/raw-sha');check.eq(pin['stored_sha256'],sha(stored),sid+'/stored-sha');check.eq(pin['raw_bytes'],len(data['raws'][sid]),sid+'/raw-size');check.eq(pin['stored_bytes'],len(stored),sid+'/stored-size')
    # The whole original ZIP bytes include every header/shared string/type/raw-v and unrelated row.
    check.eq(data['raws']['2024-xlsx-current'],data['raws']['sos-2024-general-precinct-original'],'same-whole-workbook-publication-bytes')
    ownxml=json.loads(gzip.decompress(own.own('extracted/2024-xlsx-president-raw-rows.json.gz')))
    check.eq(ownxml['headers'],data['header'],'all-ten-headers')
    peerx=[json.loads(line) for line in gzip.decompress(peer.peer('source/xlsx-president-rows.jsonl.gz')).decode().splitlines()]
    check.eq(peerx,data['xrows'],'all19887-peer-raw-workbook-rows')
    for r,actual in zip(ownxml['rows'],data['xrows']):
        check.eq(r['source_row'],actual['row'],'own-row-number')
        expected=[dict(ref=c['position'],type=c['type'],v=c['raw_value'],value=c['value']) for c in actual['cells']]
        check.eq(r['source_cells'],expected,'own-ten-source-cells')
    check.group('all_original_receipt_bytes_metadata_and_workbook_cells',start)
    start=check.count
    def shared(r):return r['contest']==('U.S. President' if int(r['year'])==2024 else 'U.S. Senate')
    pc=json.loads(gzip.decompress(peer.peer('source/contest-controls.json.gz')));pc=[r for r in pc if shared(r)]
    check.eq(indexed(pc,['source_id','position','level']),indexed(data['controls'],['source_id','position','level']),'all-state-county-wrapper-native-raw-controls')
    check.eq(indexed(json.loads(peer.peer('source/native-inventory.json')),['year','contest_id','county_id','native_id']),indexed(data['inventories'],['year','contest_id','county_id','native_id']),'all-raw-native-descriptors-and-context')
    check.eq(indexed(json.loads(peer.peer('source/candidate-metadata.json')),['year','contest_id']),indexed(data['metadata'],['year','contest_id']),'all-selected-complete-metadata')
    check.eq(indexed(json.loads(peer.peer('source/turnout-controls.json')),['year','county_id']),indexed(data['turnouts'],['year','county_id']),'all225-whole-turnout-envelopes')
    candidate_rows=list(csv.DictReader(io.StringIO(gzip.decompress(peer.peer('candidate-records.csv.gz')).decode())))
    candidate_rows=[r for r in candidate_rows if shared(r)]
    check.eq(indexed(candidate_rows,['source_id','position','level']),indexed(data['candidates'],['source_id','position','level']),'all-shared-positional-candidate-party-method-csv-fields')
    pn=[r for r in json.loads(gzip.decompress(peer.peer('native-baselines.json.gz'))) if shared(r)]
    expected_native=[r for rr in data['native'].values() for r in rr]
    check.eq(indexed(pn,['key']),indexed(expected_native,['key']),'all-seven-complete-native-source-vectors-and-positions')
    for lane,expected in data['native'].items():check.eq([r for r in pn if r['lane']==lane],expected,lane+'/complete-original-native-array-order')
    check.group('whole_raw_controls_metadata_native_candidate_method_turnout_fields',start)
    start=check.count
    original_native=json.loads(gzip.decompress(own.own('extracted/source-native-universes.json.gz')))
    for lane,rows in original_native.items():
        wanted=indexed(data['native'][lane],['key']);check.eq({r['key'] for r in rows},{r['key'] for r in wanted.values()},lane+'/exact-coverage')
        for r in rows:
            w=wanted[(r['key'],)]
            for field in ['key','county_fips','county_name','native_id','native_name','candidates','votes']:check.eq(r[field],w[field],lane+'/'+field)
            check.eq(r['ballots_cast'],None,'native-ballots-unknown');check.eq(r['registered_voters'],None,'native-registration-unknown')
            for f in ['blank','undervotes','overvotes']:check.eq(r[f],None,'native-'+f+'-unknown')
            if lane=='2024-xlsx':
                check.eq(r['party_literals'],w['party_literals'],'xlsx-party-literals');check.eq(r['methods'],{m:sum(v.values()) for m,v in w['methods'].items()},'xlsx-method-totals')
                check.eq(r['source_rows'],[int(p['position'].split('/J')[1]) for p in w['source_positions']],'xlsx-complete-source-rows')
            else:
                check.eq(w['source_positions'],[dict(source_id=r['source_id'],position=r['source_pointer']+('/choices/' if lane.endswith('api') else '/Candidates/')+str(i)) for i in range(len(r['candidates']))],'candidate-vs-node-address-companion')
    contract=json.loads(own.own('priority-set.json'));orders=json.loads(peer.peer('independent-complete-orders.json'));statistics=json.loads(own.own('orders/statistics.json'));check.eq(set(orders),set(statistics),'all20-ranking-scopes')
    order_fields=['key','votes','rank','cumulative_votes','share_numerator','share_denominator','cumulative_share_numerator']
    priorities={}
    for lane,st in statistics.items():
        rows=list(csv.DictReader(io.StringIO(own.own('orders/'+lane+'.csv').decode())))
        own_order=[{f:(r[f] if f=='key' else int(r[f])) for f in order_fields} for r in rows]
        # Explicit rank schema includes every peer field; no unexamined object keys are projected away.
        check.eq(orders[lane],own_order,lane+'/whole-rank-objects')
        rerank=sorted(orders[lane],key=lambda r:(-r['votes'],r['key']));check.eq(orders[lane],rerank,lane+'/descending-order')
        total=sum(r['votes'] for r in orders[lane]);cum=0;cross=None
        for i,r in enumerate(orders[lane],1):
            cum+=r['votes'];check.eq(r['rank'],i,'rank');check.eq(r['cumulative_votes'],cum,'cumulative');check.eq(r['share_denominator'],total,'denominator')
            if cross is None and cum*5>=4*total:cross=i
        check.eq(cross,st['minimum80_count'],lane+'/min80');check.eq(total,st['denominator'],lane+'/total');check.eq(sum(r['votes'] for r in orders[lane][:15]),st['top15_votes'],lane+'/top15')
        check.eq(sum(r['votes'] for r in orders[lane][:cross-1]),st['preceding_votes'],lane+'/preceding');check.eq(orders[lane][cross-1]['cumulative_votes'],st['minimum80_votes'],lane+'/crossing');check.eq([r['key'] for r in orders[lane]][cross-1],st['crossing_key'],lane+'/crossing-key')
        check.eq(total-st['minimum80_votes'],st['remainder_votes'],lane+'/remainder');assert st['preceding_votes']*5<4*total<=5*st['minimum80_votes']
        priorities[lane]=dict(units=len(rows),total=total,minimum80=cross,priority_keys=[r['key'] for r in orders[lane][:cross]],remainder_keys=[r['key'] for r in orders[lane][cross:]])
    primary=orders['2024-xlsx'];check.eq(contract['ordered_priority_keys'],priorities['2024-xlsx']['priority_keys'],'full1056priority-array');check.eq(contract['remainder_keys'],priorities['2024-xlsx']['remainder_keys'],'full1785remainder-array');check.eq(contract['top15_keys'],[r['key'] for r in primary[:15]],'full-top15-array')
    matchproof=json.loads(peer.peer('source/native-name-vector-matches.json'))
    check.eq(indexed(matchproof['matched'],['xlsx_key']),{(r['key'],):dict(xlsx_key=r['key'],api_key=r['matched_api_key']) for r in contract['full_order'] if r['matched_api_key'] is not None},'all2836-exact-name-vector-source-matches')
    expected_unmatched={r['key']:r for r in data['native']['2024-xlsx'] if r['key'] in {v['key'] for v in contract['coverage']['source_only_native_units']}}
    check.eq(indexed(matchproof['unmatched'],['key']),{(k,):v for k,v in expected_unmatched.items()},'all-five-whole-unmatched-native-objects')
    diffs=json.loads(own.own('extracted/full-vs-api-county-candidate-differences.json'));peer_diffs=json.loads(peer.peer('source/full-api-differences.json'))
    peer_diffs=[dict(year=int(r['year']),county_fips=r['county'],candidate=r['candidate'],api=r['api'],full=r['full'],full_minus_api=r['full_minus_api']) for r in peer_diffs if r['contest']==('U.S. President' if r['year']=='2024' else 'U.S. Senate')]
    check.eq(indexed(peer_diffs,['year','county_fips','candidate']),indexed(diffs,['year','county_fips','candidate']),'all19-required-county-candidate-discrepancies')
    check.eq([{f:r[f] for f in order_fields} for r in contract['full_order']],primary,'full2841-primary-order-array')
    check.eq(set(contract['priority_parent_fips']),{r['county_fips'] for r in pn if r['key'] in set(contract['ordered_priority_keys'])},'all68-priority-parents')
    for parent in contract['all75parents']:
        fips=parent['county_fips'];check.eq(parent['votes'],sum(r['votes'] for r in data['native']['2024-xlsx'] if r['county_fips']==fips),'parent-complete-votes')
        for lane,constituents in parent['source_native_constituents'].items():
            want={r['key']:r for r in data['native'][lane] if r['county_fips']==fips};check.eq({r['key'] for r in constituents},set(want),'all75parent-all-lane-native-arrays')
            check.eq([r['key'] for r in constituents],[r['key'] for r in data['native'][lane] if r['county_fips']==fips],'complete-parent-source-native-array-order')
            own_rows={r['key']:r for r in original_native[lane]}
            for r in constituents:
                w=own_rows[r['key']]
                # Every field of the constituent object is explicit, including unavailable companions.
                expected=dict(key=w['key'],native_id=w.get('native_id'),native_name=w['native_name'],votes=w['votes'],source_id=w['source_id'],source_pointer=w['source_pointer'],source_rows=w.get('source_rows'),methods=w.get('methods'),matched_api_native_id=w.get('matched_api_native_id'))
                check.eq(r,expected,'whole-parent-native-constituent')
        for year,scope in parent['source_scoped_county_controls'].items():
            cid={ '2024':'366','2022':'1123','2020':'560'}[year];info=data['docs'][year+'-info']['response'];desc=data['docs'][year+'-metadata']['response']['contests'][cid]
            county=data['docs'][year+'-federal-state']['response']['contests'][cid]['locations'][fips]
            check.eq(scope['api_candidate_votes'],{desc['choices'][c['choiceID']]['name']:c['totalVotes'] for c in county['choices']},'whole-parent-candidate-vector');check.eq(scope['api_total_votes'],county['totalVotes'],'parent-total')
            fullturn=data['docs'][year+'-full']['Turnout']['CountyTurnout'];ft=next(r for r in fullturn if r['CountyName'].upper()==info['locations'][fips]['locationName'].upper())
            state_turnout=json.loads(data['raws'][year+'-turnout-state'])
            check.eq(scope['full_turnout'],ft,'all-parent-full-turnout-fields');check.eq(scope['api_turnout'],state_turnout['response']['locations'][fips],'all-parent-api-turnout-fields')
    check.eq(len(contract['all75parents']),75,'all-parent-count');check.eq(len(contract['priority_parent_fips']),68,'priority-parent-count')
    check.group('all20_full_orders_integer_proofs_and_entire_parent_priority_remainder_arrays',start)
    reverse=json.loads(peer.peer('peer-reconciliation.json'));check.eq(reverse['status'],'pass','captured-peer-proof-status');check.eq(reverse['checks'],162714,'captured-peer-proof-count');check.eq(reverse['errors'],[],'captured-peer-proof-errors')
    result=dict(schema='arkansas-captured-final-source-reciprocal-v1',status='pass',checks=check.count,groups=check.groups,errors=[],captured_peer_agent='302e0938-9d85-4b49-99c1-87bbb564364d',captures=dict(own_manifest=own.spec['manifest_sha256'],peer_manifest=peer.spec['manifest_sha256'],own_bodies=1028,peer_bodies=314,own_archive=own.spec['archive_sha256'],peer_archive=peer.spec['archive_sha256']),coverage=dict(original_receipts=490,workbook_candidate_rows=19887,workbook_candidate_cells=198870,whole_shared_workbook_bytes=True,required_candidate_records=len(data['candidates']),raw_required_contest_controls=len(data['controls']),native_descriptors_with_explicit_contest_context=len(data['inventories']),complete_metadata_records=len(data['metadata']),whole_county_turnout_responses=225,source_native_units={k:len(v) for k,v in data['native'].items()},full_orders=20,parents=75,primary_units=2841,priority=1056,remainder=1785,priority_parents=68),captured_reverse_proof=dict(checks=162714,errors=0,scope='captured final original/source/native/field/order/array reciprocal only; not future producer or calculator/scenario/outcome equality'),representations=dict(control_children='Only original locations/Counties/Precincts child subtrees are omitted from a node witness, and every required child node/pointer/coverage is checked separately. Original whole bytes retain all fields and unrelated offices.',source_positions='Peer candidate/cell addresses and own contest-node/worksheet addresses checked by explicit companion expansion, never silently equated.',native_unknowns='Own null/admin/current fields remain unchanged; raw whole native/metadata/turnout witnesses establish unavailable source fields, not peer invented zeros.',metadata_context='All raw shared originals and all four metadata witnesses checked, including contextual2020 identity metadata. Contextual2020 presidential numeric derivatives/scenarios excluded.'),qualifications=dict(coordinator_acceptance=False,geographic_legal_approval=False,current_2026_approval=False,november_feed_approval=False,collector_implemented=False,forecast_calibrated=False,eligible_writein_complete=None,native_ballot_registration_available=False,api_xlsx_current_source_match_gaps=5,api2024_units=2839,xlsx2024_units=2841),excluded_numeric_scopes=['contextual2020president9extraCountyCandidateDifferences/oneExtraDoubledNative','baseline-only scenarios/calculator/targets/outcomes','future or later peer files','outstanding pool/current legal or ballot/geography/feed approvals'],all_order_inventory=priorities)
    if write:(P/'reciprocal.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='all_order_inventory'},indent=2))
    return result,data,contract
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();run(args.write)
