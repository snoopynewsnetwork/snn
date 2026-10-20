"""Bounded full-source-object comparison from captured finished peer bodies only.
No peer writer/calculator/scenario is imported or executed. Neither rank is adopted.
"""
import io,tarfile,zipfile,gzip,json,collections,re,copy,csv
from common import *
from acquire import allreceipts
class Capture:
    def __init__(self):
        self.base=ROOT/'reciprocal/peer-finished-capture';self.index=json.loads((self.base/'capture.json').read_text());parts=[]
        for p in self.index['tar_gzip_parts_in_order']:
            b=(self.base/p['path']).read_bytes();assert sha(b)==p['sha256']and len(b)==p['bytes'];parts.append(b)
        packed=b''.join(parts);assert sha(packed)==self.index['gzip_sha256'];raw=gzip.decompress(packed);assert sha(raw)==self.index['tar_sha256'];self.tar=tarfile.open(fileobj=io.BytesIO(raw))
    def body(self,name):return self.tar.extractfile('data/baselines/'+name).read()
    def obj(self,name):return json.loads(self.body(name))
    def lines(self,name):return [json.loads(l)for l in gzip.decompress(self.body(name)).splitlines()]
def ownlines(name):return [json.loads(l)for l in gzip.decompress((ROOT/name).read_bytes()).splitlines()]
def compare(write=False):
    p=Capture();checks=[];representations=[]
    def ck(scope,condition,detail=None):assert condition,(scope,detail);checks.append(dict(scope=scope,passed=True,detail=detail))
    for item in p.index['all235']:
        b=p.tar.extractfile(item['path']).read();assert sha(b)==item['sha256']and len(b)==item['bytes']
    ck('235_finished_peer_full_bodies_and_pins',len(p.index['all235'])==235,p.index['manifest_sha256'])
    inputs=p.obj('source/inputs.json');ck('original_first_input_pin',sha(p.body('source/inputs.json'))=='0f1cb9f669827e45d604b6686fa4d8267d77e7fc70c962d8e6c3f907ee3260ab')
    source={};receiptproof=[];ownrs=allreceipts();byown={r['id']:r for r in ownrs}
    for r in inputs:
        b=(STATE/r['body_path']).read_bytes();assert sha(b)==r['stored_sha256']and len(b)==r['stored_bytes'];raw=gzip.decompress(b)if r['compression']=='gzip'else b;assert sha(raw)==r['raw_sha256']and len(raw)==r['raw_bytes'];source[r['id']]=raw
        o=byown.get(r['id']);match=None if o is None else o.get('raw_sha256')==r['raw_sha256']
        if match:
            assert original(o)==raw
            # Complete original receipt objects are retained on both sides; acquisition
            # clocks/headers remain source-observation metadata, not vote vintage aliases.
        metadata={k:dict(peer=r.get(k),own=None if o is None else o.get(k),literal_equal=o is not None and r.get(k)==o.get(k))for k in ['url','final_url','status','retrieved_at_utc','headers']}
        receiptproof.append(dict(id=r['id'],path=r['body_path'],stored_sha256=r['stored_sha256'],raw_sha256=r['raw_sha256'],raw_bytes=len(raw),own_same_id_equal_body=match,peer_receipt=r,own_receipt=o,metadata_field_comparison=metadata,metadata_rule='Exact full receipts and raw/header representation differences preserved; retrieval clocks/headers are observation metadata, not substituted vote snapshots.'))
    ck('148_complete_original_entities_and_receipts',len(source)==148)
    originals={r['id']:r for r in inputs};ownall=ownlines('extracts/all-long-rows.jsonl.gz');ownselected=ownlines('extracts/selected-root-rows.jsonl.gz');ownmap={(r['source_id'],r['member'],r['byte_offset']):r for r in ownall}
    # Every selected root/nested/setup record: entire raw line, all parsed fields,
    # padded identities, fourteen slots and source/member/byte/line coordinates.
    peerall=p.lines('witness/selected-all-views.jsonl.gz');fieldmap={'contest':'contest_code','candidate':'candidate_code','reporting_code':'source_code','party':'party','district_type':'district_type_id','district_code':'district_code','contest_title':'contest_title','candidate_name':'candidate_name','reporting_name':'source_name','district_name':'district_name','votes_allowed':'votes_allowed','referendum_flag':'referendum_flag'}
    def raw_record_check(r):
        o=ownmap[(r['input'],r['member'],r['byte_start'])];raw=o['raw_line'].encode();assert r['raw_record'].encode()+b'\r\n'==raw and r['raw_line_sha256']==sha(raw)
        assert r['zip_sha256']==originals[r['input']]['raw_sha256']and r['line']==o['line']and r['byte_end']==o['byte_offset']+len(raw)
        for of,pf in fieldmap.items():assert o['fields'][of]==r[pf]
        assert int(o['fields']['total'])==r['votes'];assert [int(o['fields']['group_'+str(i)])for i in range(1,15)]==r['methods']
    for r in peerall:raw_record_check(r)
    ck('38991_full_five_contest_all_view_records',len(peerall)==38991)
    peerroots=p.lines('witness/root-selected.jsonl.gz');ck('12997_root_source_record_coverage',len(peerroots)==len(ownselected)==12997 and {(r['input'],r['member'],r['byte_start'])for r in peerroots}=={(r['source_id'],r['member'],r['byte_offset'])for r in ownselected})
    # Full ZIP member bytes/metadata, including unrelated offices kept only as originals.
    om={(r['source_id'],r['member']):r for r in json.loads((ROOT/'source/zip-members.json').read_text())};zipproof=[]
    for r in p.obj('source/zip-members.json'):
        o=om[(r['input'],r['member'])];z=zipfile.ZipFile(io.BytesIO(source[r['input']]));i=z.infolist()[r['member_index']];b=z.read(i)
        assert sha(b)==o['sha256']==r['sha256']and len(b)==o['bytes']==r['bytes'];assert int(r['crc32'],16)==o['crc']==i.CRC;assert list(i.date_time)==r['zip_datetime']==o['zip_clock'];assert i.header_offset==r['header_offset']and i.compress_size==r['compress_size']
        zipproof.append(dict(input=r['input'],member=r['member'],sha256=sha(b),bytes=len(b),role='setup'if 'setup'in r['member']else 'root'if '/'not in r['member']else 'nested_or_metadata',nonadditive=True))
    ck('44_complete_zip_members_metadata_and_roles',len(zipproof)==44)
    # Decode all Board result witness cells, including headers and absent/zero fields.
    ow=ownlines('extracts/workbook-selected-rows.jsonl.gz');owmap={(r['source_id'],r['member'],r['row']):r for r in ow};cellcount=0
    for year in ['2020','2022','2024']:
        peerrows=p.lines(f'witness/board{year}-xlsx-selected-cells.jsonl.gz');rid=f'board{year}-xlsx';keys=[]
        for row in peerrows:
            key=(rid,row['member'],row['row']);keys.append(key)
            if row['row']==1:
                o=next(x for x in ow if x['source_id']==rid and x['member']==row['member']);cells=o['header']['cells']
            else:cells=owmap[key]['cells']
            assert set(cells)=={x['cell']for x in row['cells']}
            for cell in row['cells']:
                own=cells[cell['cell']];pv=cell['value'];ov=own['value']
                if pv is None and ov=='':representations.append(dict(scope='empty_xml_cell',source=rid,member=row['member'],cell=cell['cell'],peer=None,own='',mapping='only absent raw_v cell representation'))
                else:assert pv==ov,(rid,row['member'],cell,own)
                assert cell['type']==own['xml_type'];cellcount+=1
        assert {k for k in keys if k[2]!=1}=={k for k in owmap if k[0]==rid}
    ck('all_board_selected_cells_headers_types_raw_values',True,cellcount)
    # Literal 117 municipal HTML child sets; do not erase eleven whitespace differences.
    hierarchy=json.loads((ROOT/'extracts/municipal-hierarchy.json').read_text());links=p.obj('witness/municipal-child-links.json');ownlinks={(par['source_id'],c['code']):(par,c)for par in hierarchy for c in par['children']};whitespace=[]
    for link in links:
        par,c=ownlinks[(link['input'],link['source_code'])];assert link['url']==c['url']and par['key']=='RI:municipality:'+link['municipality_slug'];assert clean(link['label_literal'])==c['label']
        raw=source[link['input']][link['byte_start']:link['byte_end']];assert link['source_code'].encode()in raw
        if link['label_literal']!=c['label']:whitespace.append(dict(source=link['input'],code=c['code'],own_cleaned=c['label'],peer_literal=link['label_literal'],peer_byte_start=link['byte_start'],peer_byte_end=link['byte_end'],original_slice=raw.decode()))
    ck('all117_municipal_full_child_arrays',len(links)==len(ownlinks)==1447,dict(parents=len(hierarchy),literal_whitespace_differences=len(whitespace)))
    # Full HTML rows and raw slices, including party identity, printed percent,
    # label strings with NBSP and all methods, not vote-only projections.
    hc=json.loads((ROOT/'extracts/html-controls.json').read_text());ph=p.lines('witness/html-selected-rows.jsonl.gz')
    for row in ph:
        matches=[x for x in hc if x['source_id']==row['input']and x['contest']==row['contest']and x['candidate']==clean(row['candidate_literal'])];assert len(matches)==1;o=matches[0];assert o['total']==row['votes']and [x['votes']for x in o['methods']]==row['method_votes'];assert [clean(x).rsplit(':',1)[0]for x in row['method_literals']]==[x['label']for x in o['methods']]
        assert source[row['input']]and row['raw_sha256']==sha(source[row['input']]);slice=source[row['input']][row['byte_start']:row['byte_end']];assert b'<tr'in slice and b'</tr>'in slice
    ck('1080_complete_selected_html_row_objects',len(ph)==1080)
    # PDF entire layout text and source-position objects; all nonvote lanes remain separate.
    opdf=json.loads((ROOT/'extracts/pdf-controls.json').read_text());ppdf=p.obj('extracts/board-pdf-selected-lines.json')
    for row in ppdf:
        matches=[x for x in opdf if x['source_id']==row['input']and x['page']==row['page']and x['line']==row['line']];assert len(matches)==1;o=matches[0];assert o['raw_line']==row['raw_line']and o['values']==[row['total']]+row['methods']
        if o['percentage']!=row['pct']:
            assert row['pct']==o['percentage']+'%'and row['pct']in row['raw_line']
            representations.append(dict(scope='PDF_percentage_token',source=row['input'],page=row['page'],line=row['line'],peer=row['pct'],own=o['percentage'],mapping='Own regex captures numeric percentage; peer preserves percent sign. Exact original raw line and all numeric controls are independently equal.'))
    for yr,rid in [('2020','board2020-pdf'),('2022','board2022-pdf'),('2024','boe-2024-summary')]:
        assert gzip.decompress(p.body(f'witness/{rid}.layout.txt.gz'))==gzip.decompress((ROOT/f'source/board-{yr}-summary.layout.txt.gz').read_bytes())
    ck('all41_pdf_candidate_nonvote_objects_and_full_layout_clocks',len(ppdf)==41)
    native=json.loads((ROOT/'native-inventory.json').read_text());nm={(int(x['year']),x['code']):x for x in native};pn=p.obj('extracts/native-inventory.json')
    for row in pn:
        o=nm[(row['year'],row['source_code'])];assert o['reporting_name']==row['source_name'];assert row['parent_kind']in ['municipality','state_administrative_federal']
        parent='RI:state'if row['parent_kind']=='state_administrative_federal'else 'RI:municipality:'+row['parent_key'];assert o['parent_key']==parent
        if row['parent_kind']=='state_administrative_federal':
            assert row['parent_key']=='state-admin-'+row['source_code']and o['dispatch_key']=='RI:state-admin:'+row['source_code']
            representations.append(dict(scope='administrative_parent_schema',year=row['year'],code=row['source_code'],peer_parent_kind=row['parent_kind'],peer_parent_key=row['parent_key'],own_parent_key=o['parent_key'],own_dispatch_key=o['dispatch_key'],mapping='Same disjoint federal source context, no municipal parent or allocation.'))
        for title,q in row['contests'].items():assert q['observed']==(o['contests'][title]['status']=='published')and q['votes']==o['contests'][title]['total']
        assert row['physical_precinct_approved']is False and row['current_2026_equivalence']is None
    ck('1459_native_full_coverage_null_admin_parent_semantics',len(pn)==len(nm)==1459)
    pb=p.lines('extracts/native-baselines.jsonl.gz');sourcegroups=collections.defaultdict(list)
    for row in peerroots:sourcegroups[(row['year'],row['contest_title'].strip(),row['source_code'])].append(row)
    for row in pb:
        o=nm[(row['year'],row['source_code'])];q=o['contests'][row['contest']];assert row['observed']==(q['status']=='published')and row['all_reported_votes']==q['total']
        for field,stat in [('registration','REGISTERED VOTERS - TOTAL'),('election_ballots','BALLOTS CAST - TOTAL'),('election_blank_ballots','BALLOTS CAST - BLANK')]:
            st=o['statistics'][stat];assert row[field]==(None if st is None else st['values'][0])
        assert all(row[k]is None for k in ['contest_ballots','contest_undervotes','contest_overvotes','valid_named_writeins','current_2026_mapping'])
        if not row['observed']:assert row['candidates']==[]and row['methods']is None;continue
        assert row['methods']==q['methods'];sr=sourcegroups[(row['year'],row['contest'],row['source_code'])];assert len(row['candidates'])==len(sr)
        for cc,rr in zip(row['candidates'],sr):assert [cc['candidate_code'],cc['name_raw'],cc['party_raw'],cc['votes'],cc['methods'],cc['line'],cc['byte_start'],cc['byte_end']]==[rr['candidate_code'],rr['candidate_name'],rr['party'],rr['votes'],rr['methods'],rr['line'],rr['byte_start'],rr['byte_end']]
    ck('2460_native_contest_full_candidate_statistics_and_null_objects',len(pb)==2460)
    # Each side's source-count order is independently recalculated using numeric offsets.
    def recompute(rows):
        grouped=collections.defaultdict(list)
        for x in rows:
            if x['year']==2024 and x['contest_title'].strip()=='Senator in Congress':grouped[x['source_code']].append(x)
        vals=[dict(code=k,votes=sum(x['votes']for x in a),byte=min(x['byte_start']for x in a))for k,a in grouped.items()];vals.sort(key=lambda x:(-x['votes'],x['byte']));cum=0;cross=None
        for i,x in enumerate(vals,1):cum+=x['votes'];x['rank']=i;x['cumulative']=cum;cross=i if cross is None and 5*cum>=4*sum(v['votes']for v in vals)else cross
        return vals,cross
    peerorder,cross=recompute(peerroots);ownorder=json.loads((ROOT/'priority-set.json').read_text())['complete_descending_order'];po=p.obj('witness/independent-native-priority.json');pc=p.obj('native-priority-contract.json')
    for calc,reported,own in zip(peerorder,po,ownorder):
        assert [calc['code'],calc['votes'],calc['byte'],calc['rank'],calc['cumulative']]==[reported['source_code'],reported['votes'],reported['first_byte'],reported['rank'],reported['cumulative']]==[own['native_code'],own['votes'],own['source_anchor']['byte_offset'],own['rank'],own['cumulative_votes']]
        parts=reported['key'].split('#');assert parts==[own['source_anchor']['source_raw_sha256'],own['source_anchor']['member'],str(own['source_anchor']['byte_offset'])];assert own['key']==':'.join(parts)
    assert cross==242 and pc['ordered_all_keys']==[x['key']for x in po]and pc['ordered_priority_keys']==[x['key']for x in po[:cross]]and pc['ordered_remainder_keys']==[x['key']for x in po[cross:]]
    ck('independently_recomputed_458_order_top15_exact80_priority_remainder',len(peerorder)==458 and sum(x['votes']for x in peerorder[:15])==34697 and peerorder[240]['cumulative']==393066 and peerorder[241]['cumulative']==394072 and sum(x['votes']for x in peerorder[242:])==97876)
    # Recompute complete independent orders and threshold witnesses for every
    # historical contest, at native and disjoint-parent levels, from each side.
    five=[];parents=p.obj('extracts/parent-baselines.json');ownparents=json.loads((ROOT/'municipal-controls.json').read_text())
    def ranking_evidence(values):
        order=sorted(values,key=lambda x:(-x['votes'],x['tie']));total=sum(x['votes']for x in order);cum=0;cross=None
        for i,x in enumerate(order,1):
            cum+=x['votes'];x['rank']=i;x['cumulative']=cum
            if cross is None and 5*cum>=4*total:cross=i
        assert 5*order[cross-2]['cumulative']<4*total<=5*order[cross-1]['cumulative']
        return dict(total=total,full_order=order,top15_votes=sum(x['votes']for x in order[:15]),minimum80_count=cross,preceding_votes=order[cross-2]['cumulative'],crossing=order[cross-1],priority=order[:cross],remainder=order[cross:],remainder_votes=sum(x['votes']for x in order[cross:]))
    for election,year,title in [('2024-senate',2024,'Senator in Congress'),('2024-president',2024,'Presidential Electors For:'),('2020-senate',2020,'Senator in Congress'),('2020-president',2020,'Presidential Electors For:'),('2022-governor',2022,'Governor')]:
        pg=collections.defaultdict(list);og=collections.defaultdict(list)
        for x in peerroots:
            if x['year']==year and x['contest_title'].strip()==title:pg[x['source_code']].append(x)
        for x in ownselected:
            if str(year)in x['source_id']and x['fields']['contest_title'].strip()==title:og[x['fields']['reporting_code']].append(x)
        pe=ranking_evidence([dict(code=k,votes=sum(x['votes']for x in a),tie=min(x['byte_start']for x in a))for k,a in pg.items()]);oe=ranking_evidence([dict(code=k,votes=sum(int(x['fields']['total'])for x in a),tie=min(x['byte_offset']for x in a))for k,a in og.items()]);assert pe==oe
        pp=[x for x in parents if x['election']==election];mp={}
        for x in pp:
            k='RI:municipality:'+x['parent_key']if x['parent_kind']=='municipality'else 'RI:state-admin:'+x['parent_key'].removeprefix('state-admin-')
            own=next(z for z in ownparents if z['year']==str(year)and z['key']==k);q=own['contests'][title];assert x['all_reported_votes']==(None if q is None else q['total'])
            expected_codes={z['code']for z in native if z['year']==str(year)and z['dispatch_key']==k};assert set(x['all_child_codes'])==expected_codes
            if q is None:assert x['children']==[];continue
            cs=collections.defaultdict(list)
            for code in expected_codes:
                for rr in pg.get(code,[]):cs[rr['candidate_code']].append(rr)
            for cc in x['candidates']:
                aa=cs[cc['candidate_code']];assert {r['candidate_name']for r in aa}=={cc['name_raw']}and {r['party']for r in aa}=={cc['party_raw']};assert sum(r['votes']for r in aa)==cc['votes'];assert [sum(r['methods'][i]for r in aa)for i in range(14)]==cc['methods']
            mp[k]=x['all_reported_votes']
        op={x['key']:x['contests'][title]['total']for x in ownparents if x['year']==str(year)and x['contests'][title]is not None};assert mp==op
        parent_peer=ranking_evidence([dict(code=k,votes=v,tie=k)for k,v in mp.items()]);parent_own=ranking_evidence([dict(code=k,votes=v,tie=k)for k,v in op.items()]);assert parent_peer==parent_own
        five.append(dict(election=election,native=pe,parent=parent_peer,source_count_independence='Both ranks recomputed separately from original-position own/peer candidate records; neither adopts the other rank.'))
    csvparent=list(csv.DictReader(io.StringIO(p.body('parent-rank-sensitivity.csv').decode())))
    parent_primary=five[0]['parent'];assert len(csvparent)==len(parent_primary['full_order'])==43
    for row,calc in zip(csvparent,parent_primary['full_order']):
        k='RI:municipality:'+row['parent_key']if row['parent_kind']=='municipality'else 'RI:state-admin:'+row['parent_key'].removeprefix('state-admin-');assert [k,int(row['votes']),int(row['cumulative']),int(row['rank'])]==[calc['code'],calc['votes'],calc['cumulative'],calc['rank']];assert (row['priority80_sensitivity']=='True')==(calc['rank']<=parent_primary['minimum80_count'])
    ck('five_full_native_and_parent_orders_candidates_children_integer80',len(five)==5,dict(parent_baseline_objects=len(parents),primary_parent_count=43,primary_parent_crossing=21))
    # Every literal Senate D/E cell, including row5, remains present and separate.
    detail=json.loads((ROOT/'extracts/writein-original-detail-proof.json').read_text());dm={(s['member'],k):v for s in detail['sheets']for k,v in s['cells'].items()};peerwi=p.lines('witness/board2024-writeins-xlsx-selected-cells.jsonl.gz');count=0
    for row in peerwi:
        for cell in row['cells']:
            if not re.fullmatch(r'[DE]\d+',cell['cell']):continue
            o=dm[(row['member'],cell['cell'])];assert (None if o['raw_v']is None else o['value'])==cell['value']and o['xml_type']==cell['type'];count+=1
    assert count==len(dm)==1955
    ownsum={x['municipality'].upper():x for x in json.loads((ROOT/'extracts/writein-scope-comparison.json').read_text())};peer_sum=p.obj('extracts/2024-senate-writein-reconciliation.json')
    for row in peer_sum['municipalities']:
        o=ownsum[row['municipality_literal'].upper()];assert row['header_total']==o['printed_top_total']and row['literal_detail_sum']==o['detail_sum']and row['detail_minus_generic']==o['difference']
    ck('1955_writein_cells_headers_literal_names_types_nulls_and_row5',True,dict(complete_detail=detail['complete_detail_sum'],complete_discrepancies=detail['complete_local_discrepancies'],historical_row6_detail=detail['historical_row6_detail_sum'],historical_row6_discrepancies=detail['historical_row6_discrepancies']))
    for rid,ownpath in [('ri-2020-observed-format-description','source/ri-2020-observed-format-description.txt'),('ri-2022-description','source/ri-2022-description.txt'),('board2020-writeins-pdf','source/board-2020-writeins.layout.txt.gz'),('board2022-writeins-pdf','source/board-2022-writeins.layout.txt.gz')]:
        ob=(ROOT/ownpath).read_bytes();ob=gzip.decompress(ob)if ownpath.endswith('.gz')else ob;assert gzip.decompress(p.body('witness/'+rid+'.layout.txt.gz'))==ob
    ck('format_method_slots_and_historical_writein_full_source_limits',True,'Technical2020slot3 unlabelled; Emergency HTML/XLSX, Early2022; generic eligibility remains unknown. Scanned historical text limitations preserved.')
    reverse=p.obj('reciprocal/reconciliation.json');ck('peer_reverse_proof_captured_historical_scope_only',sha(p.body('reciprocal/reconciliation.json'))=='77b4fc4aebcd3dc88aff8fb6de7ae10312b320b5a4ce7ba514bfe1b4ee95ad0a')
    result=dict(schema='turnout-finished-peer-source-core-audit-v1',status='passed',peer_id=p.index['peer_id'],capture_sha256=sha((p.base/'capture.json').read_bytes()),original_first_own_witness_sha256='a88c8c63384f2de6011a80bd7d50bf225e4c5dbcd312b0e469cb3a5777de99f1',checks=checks,scope='Five historical contest full original source objects, receipt metadata, all14slots/rawparty/positions, root/nested/setup, allmunicipal/admin/null/control/ballot/registration/nonvote/method/header lanes, canonical458 order and structural writein detail only.',excluded='No equality claimed for peer calculators/scenarios/targets/report/outcomes/reproduction/current IDs/legal eligibility/approved geometry/later peer bytes. No peer writer run. Reverse proof is historical original-phase evidence only.',representations=representations,child_label_whitespace_differences=whitespace,source_originals_and_receipts=receiptproof,zip_complete_member_proof=zipproof,writein_scopes=dict(complete=1227,complete_local_discrepancies=8,historical_row6=1226,historical_row6_local_discrepancies=9,municipal_generic=1239,state_generic=1244,eligibility=None,allocation=None),coordinator_acceptance=False)
    result['five_contest_independent_full_orders']=five
    if write:dump(ROOT/'reciprocal/source-core-comparison.json',result)
    return result
if __name__=='__main__':
    import sys
    r=compare('--write'in sys.argv);print(dict(status=r['status'],checks=len(r['checks']),whitespace_differences=len(r['child_label_whitespace_differences'])))
