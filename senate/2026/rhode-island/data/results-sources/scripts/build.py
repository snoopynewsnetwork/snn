"""Deterministic source inventory and complete reference-based investigations."""
from common import *
from htmltools import Tree,Node
from collections import Counter,defaultdict
import re

def raw_receipts():
    rows=[]
    for p in parsed(R/'inputs.json')['receipts']:
        b=(S/p['path']).read_bytes();verify(b,p);rows.append(json.loads(b))
    return rows
def entity(r):
    b=(S/r['stored_path']).read_bytes()
    assert sha(b)==r['stored_sha256'] and len(b)==r['stored_bytes']
    raw=gzip.decompress(b);assert sha(raw)==r['raw_sha256'] and len(raw)==r['raw_bytes']
    return raw
def ref(path,pointer='',value=None):
    p=pin(S/path)
    return dict(**p,pointer=pointer,full_object_semantic_sha256=sem(value) if value is not None else None,complete_object=True)
def textlang(v):return ' | '.join(x.get('text') or '' for x in v or [])
def schema(v):
    fields=defaultdict(Counter)
    def rec(v,p=''):
        fields[p][type(v).__name__]+=1
        if isinstance(v,dict):
            for k,x in v.items():rec(x,p+'/'+k.replace('~','~0').replace('/','~1'))
        elif isinstance(v,list):
            for x in v:rec(x,p+'/*')
    rec(v);return {k:dict(v) for k,v in sorted(fields.items())}
def compact(s):return re.sub(r'\s+',' ',s).strip()
def scopeparent(r):
    return 'RI:state-admin:'+r.get('native_code',r.get('code','')) if r['parent_key']=='RI:state' else r['parent_key']
def enacted(n):
    if isinstance(n,str):return n
    if n.tag in ['head','style','script'] or 'line-through' in n.attrs.get('style',''):return ''
    return ''.join(enacted(x) for x in n.children)+ ('\n' if n.tag in ['tr','p','h1','h2','h3'] else '')

def generate():
    out={};receipts=raw_receipts();byid={r['id']:r for r in receipts}
    c=parsed(S/'data/turnout/priority-set.json');rank=c['complete_descending_order'];inv=c['all_source_native_constituents'];parents=c['municipal_and_administrative_parent_sensitivity']['full_inventory']
    def put(name,obj):out['derived/'+name]=dump(obj)
    # Parse complete raw directory tables, preserving blanks, literal fields, attributes and original row positions.
    dr=byid['board-directory-network'];raw=entity(dr);src=raw.decode('utf-8');tree=Tree(src);tables=[]
    for ti,t in enumerate(tree.root.find(['table'])):
        rows=[]
        for ri,tr in enumerate(t.find(['tr'])):
            cells=[dict(tag=n.tag,attrs=n.attrs,text=n.text(),raw_html=src[n.start:n.end],character_start=n.start,character_end=n.end) for n in tr.children if isinstance(n,Node) and n.tag in ['td','th']]
            if cells:rows.append(dict(row_ordinal=ri,cells=cells,raw_html=src[tr.start:tr.end],character_start=tr.start,character_end=tr.end))
        tables.append(dict(table_ordinal=ti,rows=rows))
    table=next(t for t in tables if len(t['rows'])==40)
    directory=dict(source_receipt=pin(R/'acquired/board-directory-network.receipt.json'),raw_entity_sha256=dr['raw_sha256'],tables=tables,rows_scope='All39 rows and header, every literal cell and blank; website last-updated2022 is not a roster freshness guarantee. SOS reader directory is a separate representation with raw HTTP unavailable.')
    put('municipality-directory.json',directory)
    drows={compact(row['cells'][0]['text']).replace(' (Block Island)',''):row for row in table['rows'][1:]}
    # Complete HTML links, embedded srcs, DOM text and every table per actual response. CSS/JS kept as raw originals.
    observations=[];htmls={};jsons={};all_schemas={}
    for r in receipts:
        ob=dict(receipt=pin(R/'acquired'/f"{r['id']}.receipt.json"),id=r['id'],status=r.get('status'),url=r['url'],final_url=r.get('final_url'),retrieved_at_utc=r['retrieved_at_utc'],raw_bytes=r.get('raw_bytes'),raw_sha256=r.get('raw_sha256'),body_complete=r['body_complete'],error=r.get('error'),source_clock=None,source_clock_timezone=None)
        if r.get('stored_path'):
            raw=entity(r);ob['original_body']=pin(S/r['stored_path'])
            if raw.lstrip().startswith((b'{',b'[')):
                try:v=json.loads(raw)
                except (ValueError,UnicodeError):v=None
                if v is not None:
                    jsons[r['id']]=v;all_schemas[r['id']]=dict(body=ob['original_body'],raw_sha256=r['raw_sha256'],schema=schema(v))
            elif b'<html' in raw[:2000].lower() or b'<!doctype html' in raw[:2000].lower():
                txt=raw.decode('utf-8','replace');t=Tree(txt);links=t.links(r.get('final_url',r['url']))
                h=dict(receipt=ob['receipt'],links=links,embedded=[dict(tag=n.tag,attrs=n.attrs,character_offset=n.start) for n in t.root.find(['img','iframe','object','embed','base'])],text=t.root.text(),tables=[[[dict(tag=cell.tag,attrs=cell.attrs,text=cell.text()) for cell in tr.children if isinstance(cell,Node) and cell.tag in ['td','th']] for tr in table.find(['tr'])] for table in t.root.find(['table'])])
                htmls[r['id']]=h;put('html/'+r['id']+'.json',h)
                if r['id'].startswith('act2026-'):out['derived/legal/'+r['id']+'.enacted.txt']=enacted(t.root).encode()
            elif raw.startswith(b'%PDF'):ob['format']='PDF; complete bytes; full Poppler layout and pdfinfo retained separately; selected visual scope is in visual-review.json'
        observations.append(ob)
    put('observations.json',observations);put('current-json-schemas.json',all_schemas)
    # Public current navigation evidence; no November route is guessed.
    jurisdiction=jsons['results-jurisdiction'];assert len(jurisdiction['elections'])==10
    assert not any(e['electionDate']=='2026-11-03' for e in jurisdiction['elections'])
    put('current-navigation.json',dict(jurisdiction_body_ref=ref(byid['results-jurisdiction']['stored_path']),published_elections=jurisdiction['elections'],November_event=None,November_Senate_contest=None,November_choice_ids=None,November_reporting_units=None,November_method_ids=None,admitted=False,scope='No November event in this captured navigation. This is not a claim about all future or undiscovered publications.'))
    export=jsons['primary-shared-export'];assert len(export['localResults'])==40
    export_byname={x['name']:i for i,x in enumerate(export['localResults'])}
    products=[];checks=Counter()
    for r in receipts:
        if not r['id'].startswith('primary-local-'):continue
        v=jsons[r['id']];j=v['jurisdiction'];e=v['election'];name=textlang(j['name'])
        assert e['isPrimary'] and e['electionDate']=='2026-09-09' and e['isProduction']
        sen=[(i,x) for i,x in enumerate(v['ballotItems']) if 'Senator in Congress' in textlang(x['name'])]
        exi=export_byname[name];ex=export['localResults'][exi]
        for _,item in sen:
            assert sum(o['voteCount'] for o in item['summaryResults']['ballotOptions'])==item['voteTotal']
            for choice in item['summaryResults']['ballotOptions']:
                assert sum(g['voteCount'] for g in choice['groupResults'])==choice['voteCount'];checks['primary_method_choice_checks']+=1
        # Full export all candidates/all native rows/all methods independently balance, not only Senate.
        for item in ex['ballotItems']:
            for choice in item['ballotOptions'] or []:
                assert sum(g['voteCount'] for g in choice['groupResults'])==choice['voteCount'];checks['export_choice_method_balances']+=1
                if choice['precinctResults'] is not None:
                    assert sum(p['voteCount'] for p in choice['precinctResults'])==choice['voteCount'];checks['export_choice_precinct_balances']+=1
                    for p in choice['precinctResults']:
                        assert sum(g['voteCount'] for g in p['groupResults'])==p['voteCount'];checks['export_native_method_balances']+=1
        products.append(dict(name=name,receipt=pin(R/'acquired'/f"{r['id']}.receipt.json"),full_body_ref=ref(r['stored_path']),
            jurisdiction_ref=dict(pointer='/jurisdiction',full_object_semantic_sha256=sem(j)),election_ref=dict(pointer='/election',full_object_semantic_sha256=sem(e)),
            complete_shared_export_ref=dict(**pin(S/byid['primary-shared-export']['stored_path']),pointer='/localResults/'+str(exi),full_object_semantic_sha256=sem(ex),complete_object=True),
            primary_precinct_objects=len(v['precincts']),primary_ballot_items=len(v['ballotItems']),Senate_summary_refs=[dict(pointer='/ballotItems/'+str(i),full_object_semantic_sha256=sem(x),name=textlang(x['name']),voteTotal=x['voteTotal']) for i,x in sen],
            countGroups=e['countGroups'],groupReportingStatus=e['groupReportingStatus'],precinctReportingStatus=e['precinctReportingStatus'],precinctsReporting=e['precinctsReporting'],ballotsCast=e['ballotsCast'],totalVoters=e['totalVoters'],
            asOf=e['asOf'],lastUpdated=e['lastUpdated'],nextUpdateAt=e['nextUpdateAt'],clock_timezone='UTC from literal Z',
            isOfficialResults=e['isOfficialResults'],publicReportCategories=e['publicReportCategories'],mediaExportPath=j['mediaExportPath'],
            outstanding_ballots=None,measured_update_cadence=None,current_leaf_mapping=None,admitted_November=False,
            completion_scope='Primary tenant reporting statuses and native precinct inventory only; not final eligible ballots, November units, current geometry or ballots remaining. Shared export and state/local summaries overlap.'))
    for stateitem in [x for x in export['results']['ballotItems'] if 'Senator in Congress' in x['name']]:
        for choice in stateitem['ballotOptions']:
            total=0
            for loc in export['localResults']:
                items=[x for x in loc['ballotItems'] if x['id']==stateitem['id'] and x['name']==stateitem['name']]
                assert len(items)==1
                matches=[x for x in items[0]['ballotOptions'] if (x['id'],x['name'],x['politicalParty'])==(choice['id'],choice['name'],choice['politicalParty'])];assert len(matches)==1
                total+=matches[0]['voteCount']
            assert total==choice['voteCount'];checks['state_local_Senate_choice_balances']+=1
    put('primary-products.json',products);put('primary-product-checks.json',dict(status='pass',counts=dict(checks),scope='Current primary snapshot full export all choices/native/method balances; Senate state-local controls. No November admission.'))
    prod={p['name']:i for i,p in enumerate(products)}
    municipal_requests=parsed(R/'municipal-initial-requests.json');destbyid={r['id']:r for r in municipal_requests}
    rows=[];priorityparents=list(dict.fromkeys(r['parent_key'] for r in rank[:242]));assert len(priorityparents)==37
    findings=parsed(R/'municipal-findings.json')
    for pi,p in enumerate(parents):
        municipal=p['geography_type']=='municipality';name=p['name'];suffix=''
        if municipal:
            drw=drows[name];idx=next(i for i,row in enumerate(table['rows']) if row==drw)
            # Directory request IDs follow the actual SOS alphabetical table, not geographic native-code ranges.
            names=[compact(row['cells'][0]['text']).replace(' (Block Island)','') for row in table['rows'][1:]]
            # SOS puts Westerly after West Warwick, while Board HTML puts Westerly before them.
            reader=parsed(R/'acquired/sos-directory.web-reader.json')['result']
            linked_names={int(n):label for n,label in re.findall('(\\d+)†([^†\\n]+)†',reader) if 1<=int(n)<=39}
            sos_names=[linked_names[i].replace(' Town Hall','').replace(' City Hall','') for i in range(1,40)]
            so=sos_names.index(name)+1;mid=f'municipal-{so:02}'
            localobs=[r['id'] for r in receipts if r['id']==mid or r['id'].startswith(mid+'-')]
            assert mid in byid and mid in destbyid
            dirs=dict(Board_directory_pointer='/tables/'+str(table['table_ordinal'])+'/rows/'+str(idx),Board_fields=drw['cells'],SOS_link_ordinal=so,SOS_destination=destbyid[mid],SOS_raw_HTTP_status=byid['sos-directory'].get('status'),SOS_raw_fields_available=False,SOS_reader_representation='data/results-sources/acquired/sos-directory.web-reader.json')
            product=prod[name]
        else:
            localobs=[];dirs=None;product=prod['Federal']
        historical=ref('data/turnout/priority-set.json','/municipal_and_administrative_parent_sensitivity/full_inventory/'+str(pi),p)
        childrank=[r for r in rank if scopeparent(r)==p['key']]
        rows.append(dict(key=p['key'],name=name,priority_parent=p['key'] in priorityparents,authority_kind='local Board of Canvassers under state Board supervision' if municipal else 'Board/state administrative historical source context; never municipally allocated',
            historical_whole_parent=historical,directory=dirs,municipal_observation_ids=localobs,
            current_primary_product_ref=dict(path='data/results-sources/derived/primary-products.json',pointer='/'+str(product),whole_object=True),
            ordered_priority_children=[r['key'] for r in childrank if r['rank']<=242],ordered_remainder_children=[r['key'] for r in childrank if r['rank']>242],
            original_inventory_children=p['native_keys'],historical_Senate_votes=p['contests']['Senator in Congress']['total'],
            current_November_source=None,current_native_compatibility=None,current_geometry=None,exact_outstanding=None,measured_cadence=None,
            source_specific_scope=f"{name}: complete historical parent with {len(p['native_keys'])} inventory children and {len(childrank)} observed Senate contexts; primary-only product has {products[product]['primary_precinct_objects']} precinct objects, {products[product]['primary_ballot_items']} ballot items and its own UTC source clocks. These are different publication universes; there is no native join.",
            municipal_finding=findings[name] if municipal else 'Four historical administrative source contexts retain independent full parent objects under the Board; the current primary Federal tenant is a separate event namespace and supplies no cross-year/native allocation.',
            correction_policy='Retain cumulative replacements/decreases and unresolved scope conflicts. Do not add root, local tenant and shared export; canvass/certification governs final totals. No actual successive update sequence captured.',
            unavailable_authorities=['November Board event/contest/choice/reporting IDs absent from captured current navigation','Full final statewide candidate/eligible write-in and signed certification instrument not established','Independent later court/order clearance and measured release cadence not established']))
    put('parent-investigations.json',rows)
    parentidx={r['key']:i for i,r in enumerate(rows)};invidx={r['key']:i for i,r in enumerate(inv)}
    investigations=[]
    for r in rank:
        ni=invidx[r['native_key']];native=inv[ni];pi=parentidx[scopeparent(r)]
        investigations.append(dict(ordered_rank=r['rank'],dispatch_key=r['key'],partition='priority' if r['rank']<=242 else 'explicit_remainder',
            whole_rank=ref('data/turnout/priority-set.json','/complete_descending_order/'+str(r['rank']-1),r),
            whole_native=ref('data/turnout/priority-set.json','/all_source_native_constituents/'+str(ni),native),
            whole_parent=rows[pi]['historical_whole_parent'],shared_parent_investigation=dict(path='data/results-sources/derived/parent-investigations.json',pointer='/'+str(pi),whole_object=True),
            original_anchor=r['source_anchor'],all_historical_candidate_record_keys=native['contests']['Senator in Congress']['candidate_rows'],
            current_leaf_mapping=None,independent_feed_count=0,admitted_November=False,
            conclusion='Complete historical source context investigated through shared parent chain, full original candidate/method/statistic/null objects and current primary publication. Neither the delimiter key nor label/native number is a current source ID.'))
    put('priority-investigations.json',investigations[:242]);put('remainder-investigations.json',investigations[242:]);put('all-Senate-hierarchy.json',investigations)
    put('full-inventory.json',[dict(original_inventory_ordinal=i,whole_native=ref('data/turnout/priority-set.json','/all_source_native_constituents/'+str(i),n),parent_investigation_pointer='/'+str(parentidx[scopeparent(n)]),Senate_status=n['contests']['Senator in Congress']['status'],Senate_total=n['contests']['Senator in Congress']['total'],role=n['role'],current_leaf_mapping=None) for i,n in enumerate(inv)])
    put('ordered-priority-parent-investigations.json',[dict(key=k,whole_investigation_pointer='/'+str(parentidx[k])) for k in priorityparents])
    # Substantive authority CSV: all39 actual municipal chains plus state/Secretary/four disjoint admin contexts.
    columns=['authority_key','name','authority_kind','priority_parent','historical_inventory_contexts','historical_observed_Senate_contexts','historical_Senate_votes','priority_contexts','remainder_contexts','Board_directory_raw_fields_json','SOS_linked_destination','municipal_observations_json','primary_source_URL','primary_precinct_objects','primary_ballot_items','primary_ballotsCast_literal','primary_totalVoters_literal','primary_asOf_UTC','primary_lastUpdated_UTC','primary_countGroups_json','primary_groupReportingStatus_json','primary_precinctReportingStatus_json','shared_export_URL','November_source','November_contest_ID','November_choice_IDs','November_reporting_IDs','current_leaf_mapping','exact_outstanding','measured_cadence','admitted_November','whole_parent_ref_json','qualification']
    buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=columns,lineterminator='\n');w.writeheader()
    for p in rows:
        product=products[int(p['current_primary_product_ref']['pointer'][1:])];pr=parsed(S/product['receipt']['path']);d=p['directory']
        w.writerow(dict(authority_key=p['key'],name=p['name'],authority_kind=p['authority_kind'],priority_parent=p['priority_parent'],historical_inventory_contexts=len(p['original_inventory_children']),historical_observed_Senate_contexts=len(p['ordered_priority_children'])+len(p['ordered_remainder_children']),historical_Senate_votes=p['historical_Senate_votes'],priority_contexts=len(p['ordered_priority_children']),remainder_contexts=len(p['ordered_remainder_children']),Board_directory_raw_fields_json=json.dumps(d['Board_fields'],ensure_ascii=False) if d else 'null',SOS_linked_destination=d['SOS_destination']['url'] if d else '',municipal_observations_json=json.dumps(p['municipal_observation_ids']),primary_source_URL=pr['url'],primary_precinct_objects=product['primary_precinct_objects'],primary_ballot_items=product['primary_ballot_items'],primary_ballotsCast_literal=product['ballotsCast'],primary_totalVoters_literal=product['totalVoters'],primary_asOf_UTC=product['asOf'],primary_lastUpdated_UTC=product['lastUpdated'],primary_countGroups_json=json.dumps(product['countGroups']),primary_groupReportingStatus_json=json.dumps(product['groupReportingStatus']),primary_precinctReportingStatus_json=json.dumps(product['precinctReportingStatus']),shared_export_URL=byid['primary-shared-export']['url'],admitted_November=False,whole_parent_ref_json=json.dumps(p['historical_whole_parent']),qualification=p['source_specific_scope']))
    for key,name,role,ids in [('RI:state','State Board of Elections','State/federal tabulation, recount and certification authority',['board-home','board-history','results-jurisdiction']),('RI:secretary','Secretary of State','Election administration, ballot preparation, directory and calendar; distinct from Board count certification',['sos-home','sos-directory','sos-calendar'])]:
        w.writerow(dict(authority_key=key,name=name,authority_kind=role,municipal_observations_json=json.dumps(ids),primary_source_URL=byid['results-jurisdiction']['url'] if key=='RI:state' else byid['sos-home']['url'],admitted_November=False,qualification='Whole source responses and roles retained; no current November feed/roster admission. County names are not election reporting substitutes.'))
    out['../official-results-sources.csv']=buf.getvalue().encode()
    return out

if __name__=='__main__':
    import sys
    result=generate()
    if '--check' in sys.argv:
        for name,b in result.items():assert (R/name).read_bytes()==b,name
        print('deterministic full rebuild comparison passed',len(result))
    else:
        for name,b in result.items():write(R/name,b)
        print('built',len(result),'outputs')
