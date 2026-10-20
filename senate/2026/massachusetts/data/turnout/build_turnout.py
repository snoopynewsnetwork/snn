#!/usr/bin/env python3
"""Offline independent extraction of original PD43 CSV/HTML and exact rankings.

Python standard library only. All writes remain in this assignment's owned paths.
No coordinator diagnostic or peer derivative is an input.
"""
import collections,csv,gzip,hashlib,io,json,re
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path

D=Path(__file__).resolve().parent
STATE=D.parent.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def gzjson(p,x):p.write_bytes(gzip.compress((json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n').encode(),mtime=0))
def key(t):return json.dumps(list(t),ensure_ascii=False,separators=(',',':'))
def number(s):
    if s=='':return None
    assert re.fullmatch(r'\d{1,3}(?:,\d{3})*|\d+',s),repr(s)
    return int(s.replace(',',''))
class Node:
    def __init__(self,tag='',attrs=()):self.tag=tag;self.attrs=dict(attrs);self.children=[]
    def text(self):return ' '.join(''.join(c if isinstance(c,str)else c.text()+' 'for c in self.children).split())
    def descendants(self,tag=None,cls=None,id=None):
        for c in self.children:
            if isinstance(c,Node):
                if (tag is None or c.tag==tag)and(cls is None or cls in c.attrs.get('class','').split())and(id is None or c.attrs.get('id')==id):yield c
                yield from c.descendants(tag,cls,id)
class HTML(HTMLParser):
    void={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self,b):
        super().__init__(convert_charrefs=True);self.root=Node();self.stack=[self.root];self.feed(b.decode('utf-8-sig'))
    def handle_starttag(self,t,a):
        n=Node(t,a);self.stack[-1].children.append(n)
        if t not in self.void:self.stack.append(n)
    def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t)
    def handle_endtag(self,t):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==t:self.stack=self.stack[:i];break
    def handle_data(self,t):self.stack[-1].children.append(t)
def csvwrite(p,rows):
    assert rows
    with p.open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def source_read(pin):
    p=STATE/pin['immutable_body_path'];z=p.read_bytes();b=gzip.decompress(z)
    assert sha(z)==pin['stored_sha256']and sha(b)==pin['raw_sha256']and len(b)==pin['bytes']
    return b
def rank(records,field):
    ordered=sorted(records,key=lambda r:(-r[field],*r['literal_tuple'],r['csv_record_ordinal']))
    total=sum(r[field]for r in ordered);assert total>0
    cum=0;out=[]
    for i,r in enumerate(ordered,1):
        before=cum;cum+=r[field]
        out.append(dict(rank=i,native_key=r['native_key'],literal_tuple=r['literal_tuple'],csv_record_ordinal=r['csv_record_ordinal'],votes=r[field],cumulative_votes=cum,share_exact=str(Fraction(r[field],total)),cumulative_share_exact=str(Fraction(cum,total)),weight=r[field]/total,in_top15=i<=15,in_minimum80=5*before<4*total))
    n=next(i for i,r in enumerate(out,1)if 5*r['cumulative_votes']>=4*total)
    before=out[n-2]['cumulative_votes']if n>1 else 0
    assert 5*before<4*total<=5*out[n-1]['cumulative_votes']
    s=dict(field=field,units=len(out),statewide_votes=total,top15_votes=sum(r['votes']for r in out[:15]),minimum80_count=n,preceding_count=n-1,preceding_votes=before,crossing_key=out[n-1]['native_key'],crossing_tuple=out[n-1]['literal_tuple'],crossing_votes=out[n-1]['votes'],minimum80_votes=out[n-1]['cumulative_votes'],remainder_count=len(out)-n,remainder_votes=total-out[n-1]['cumulative_votes'])
    for label,num in [('top15',s['top15_votes']),('preceding',before),('minimum80',s['minimum80_votes'])]:s[label+'_share_exact']=str(Fraction(num,total));s[label+'_percent']=100*num/total
    return out,s
def parse_contest(tag,prefix,pins):
    raw={scope:list(csv.reader(io.StringIO(source_read(pins[prefix+'-'+scope+'-csv']).decode('utf-8-sig'))))for scope in ['municipal','precinct']}
    m,n=raw['municipal'],raw['precinct'];assert m[0][3:]==n[0][3:]and m[1]==n[1]and m[-1]==n[-1]
    cols=n[0][3:];assert cols[-3:]==['All Others','Blanks','Total Votes Cast']
    width=len(cols);parents={};native=[];positions=[]
    def record(row,ordinal,scope):
        assert len(row)==width+3,(tag,ordinal,row)
        vals=[number(x)for x in row[3:]];assert None not in vals,(tag,row)
        assert sum(vals[:-1])==vals[-1],(tag,scope,ordinal)
        t=row[:3]
        obj=dict(native_key=key(t),literal_tuple=t,csv_record_ordinal=ordinal,source_id=prefix+'-'+scope+'-csv',source_scope=scope,raw_row=row,values=vals,named_source_votes=sum(vals[:-3]),named_plus_AllOthers_votes=sum(vals[:-2]),AllOthers=vals[-3],Blanks=vals[-2],TotalVotesCast=vals[-1],method=None,undervotes=None,overvotes=None,registration=None,municipal_fips=None,numeric_native_id=None,administrative_identity=None,context_type='unallocated_municipal_context'if scope=='precinct'and t[1:]==['','']else 'literal_ward_precinct_context'if scope=='precinct'else 'municipal_parent',geometry_status='not_established')
        for c,(raw_value,val)in enumerate(zip(row[3:],vals),4):positions.append(dict(source_id=obj['source_id'],csv_record_ordinal=ordinal,csv_column_ordinal=c,literal_column=cols[c-4],raw_value=raw_value,value=val))
        return obj
    for i,r in enumerate(m[2:-1],3):
        assert r[0]not in parents;parents[r[0]]=record(r,i,'municipal')
    assert len(parents)==351
    seen=set();agg=collections.defaultdict(lambda:[0]*width)
    for i,r in enumerate(n[2:-1],3):
        o=record(r,i,'precinct');assert o['native_key']not in seen;seen.add(o['native_key']);assert r[0]in parents;native.append(o)
        for j,v in enumerate(o['values']):agg[r[0]][j]+=v
    assert set(agg)==set(parents)
    for town,p in parents.items():assert agg[town]==p['values'],(tag,town)
    state=record(n[-1],len(n),'precinct');state2=record(m[-1],len(m),'municipal');assert state['values']==state2['values']
    assert [sum(r['values'][i]for r in parents.values())for i in range(width)]==state['values']
    doc=HTML(source_read(pins[prefix+'-view'])).root
    table=next(doc.descendants('table',id='precinct_data'))
    table_rows=[]
    for i,tr in enumerate(table.descendants('tr'),1):
        cells=[c for c in tr.children if isinstance(c,Node)and c.tag in ['td','th']]
        table_rows.append(dict(html_table_row_ordinal=i,attributes=tr.attrs,cells=[c.text()for c in cells],cell_attributes=[c.attrs for c in cells]))
    footer=next(r for r in table_rows if 'total'in r['attributes'].get('class','').split())
    assert [number(v)for v in footer['cells'][1:]]==state['values']
    county=[r for r in table_rows if 'm_item'in r['attributes'].get('class','').split()];assert len(county)==14
    county_values=[[number(x)for x in r['cells'][1:]]for r in county]
    difference=[sum(r[i]for r in county_values)-state['values'][i]for i in range(width)]
    cards=[]
    for c in doc.descendants('div',cls='candidate'):
        party=next(c.descendants(cls='party'),None);name=next(c.descendants(cls='display_name'),None)
        cards.append(dict(literal_name=name.text()if name else None,literal_party_display=party.text()if party else None,attributes=c.attrs,raw_text=c.text()))
    assert len(cards)==width-3
    out=dict(contest=tag,source_prefix=prefix,header_rows={s:raw[s][:2]for s in raw},all_original_csv_rows=raw,columns=cols,party_row_literal=m[1],state_control=state['values'],named_source_votes=state['named_source_votes'],named_plus_AllOthers_votes=state['named_plus_AllOthers_votes'],municipalities=list(parents.values()),native_contexts=native,html_candidate_cards=cards,html_source_table_rows=table_rows,html_county_sum_minus_state_footer=difference,municipal_native_field_comparisons=351*width,native_context_count=len(native),method_columns_available=False,source_positions_count=len(positions))
    gzjson(D/'extract'/f'{tag}-original-extraction.json.gz',out)
    gzjson(D/'extract'/f'{tag}-numeric-positions.json.gz',positions)
    return out
def main():
    (D/'extract').mkdir(exist_ok=True);(D/'orders').mkdir(exist_ok=True)
    pins={r['id']:r for r in json.loads((D/'source/shared-originals.json').read_bytes())}
    contests={}
    for tag,prefix in [('2024-senate','sos-2024-senate'),('2020-senate','sos-observed-2020-senate'),('2022-governor','sos-observed-2022-governor'),('2024-president','sos-observed-2024-president')]:contests[tag]=parse_contest(tag,prefix,pins)
    results={};orders={}
    for tag,c in contests.items():
        for scope,records in [('native',c['native_contexts']),('municipal',c['municipalities'])]:
            for field in ['named_source_votes','named_plus_AllOthers_votes','TotalVotesCast']:
                label=f'{tag}-{scope}-{field}';order,s=rank(records,field);results[label]=s;orders[label]=order
                csvwrite(D/'orders'/f'{label}.csv',[dict(r,literal_tuple=key(r['literal_tuple']))for r in order])
    c=contests['2024-senate'];label='2024-senate-native-named_source_votes';primary=orders[label];summary=results[label];N=summary['minimum80_count'];records={r['native_key']:r for r in c['native_contexts']}
    municipal_order=orders['2024-senate-municipal-named_source_votes'];parentmap=[]
    for p in c['municipalities']:
        children=[r['native_key']for r in c['native_contexts']if r['literal_tuple'][0]==p['literal_tuple'][0]]
        parentmap.append(dict(municipal_key=p['native_key'],literal_city_town=p['literal_tuple'][0],csv_record_ordinal=p['csv_record_ordinal'],values=p['values'],native_keys_source_order=children,native_keys_priority_order=[r['native_key']for r in primary if r['native_key']in set(children)],native_context_count=len(children),all_children_present=True,numeric_id=None,fips=None,aggregation='sum children; parent overlaps children and must never be added'))
    contract=dict(schema_version='MA-turnout-native-v1',state='MA',state_fips='25',election='2024-11-05 General U.S. Senate (Class I)',target_election='2026-11-03 Regular Class II',primary_source_id='sos-2024-senate-precinct-csv',source_body_sha256=pins['sos-2024-senate-precinct-csv']['raw_sha256'],source_entity_path=pins['sos-2024-senate-precinct-csv']['immutable_body_path'],candidate_universe=dict(named_source_columns=c['columns'][:-3],denominator=c['named_source_votes'],AllOthers_separate=c['state_control'][-3],eligible_named_writein_allocation=None,qualification='Exact named source records only. All Others is a separate generic source category. No legal or write-in robustness inference.'),tie_rule='descending integer named-source votes, exact original City/Town, Ward, Pct literal tuple lexicographically, original CSV record ordinal only if needed',summary=summary,coverage=dict(municipal_parents=351,native_contexts=len(primary),all_native_rows_retained=True,all_351_parent_child_maps_present=True,missing_native_rows=[],administrative_units='No separately labeled central/absentee/administrative unit in the CSV. No inference that administrative votes are absent; allocation within native contexts unavailable.',numeric_native_ids=None,municipal_fips=None,ward_totals='No ward-total rows in selected CSV; ward grouping is nonadditive hierarchy only.',method='Unavailable for each native context in PD43 CSV.'),ordered_priority_keys=[r['native_key']for r in primary[:N]],ordered_top15_keys=[r['native_key']for r in primary[:15]],ordered_remainder_keys=[r['native_key']for r in primary[N:]],all_unit_order=[dict(r,source_record=records[r['native_key']])for r in primary],all_parent_child_maps=parentmap,municipal_sensitivity=dict(summary=results['2024-senate-municipal-named_source_votes'],full_order=municipal_order,ordered_priority_keys=[r['native_key']for r in municipal_order if r['in_minimum80']],dispatch_substitute=False),sensitivity_orders={k:dict(summary=results[k],all_unit_order=orders[k])for k in orders if k.startswith('2024-senate-')and k not in [label,'2024-senate-municipal-named_source_votes']},cross_year_join='None. Historical rosters are distinct source contexts; matching labels do not establish equal boundaries.',current_geometry_approved=False,independent_peer_agreement=False,coordinator_accepted=False,review_status='independent original extraction complete; peer and coordinator acceptance pending')
    peer_path=D/'peer-audit/comparison.json'
    if peer_path.exists():
        review=json.loads(peer_path.read_bytes())
        assert review['status']=='pass_bounded_reciprocal_actual_final_baseline_capture'
        assert review['own_original_first_manifest_sha256']=='707dcec048f01fa8d557087c142e0f50fce924b7ff089ea97a384d3d16860846'
        contract['independent_peer_agreement']=True
        contract['review_status']='bounded reciprocal agreement against frozen actual final baseline; coordinator acceptance and current geometry pending'
        contract['bounded_peer_audit']=dict(path='data/turnout/peer-audit/comparison.json',sha256=sha(peer_path.read_bytes()),peer_actual_id=review['peer_actual_id'],peer_final_capture_manifest_sha256=review['peer_final_capture_manifest_sha256'],scope='Frozen actual-final baseline only; own original-first count/order/CSV unchanged. Metadata-only review additions, no later-current peer equality inferred.')
    dump(D/'priority-set.json',contract)
    enriched=[]
    for row in primary:
        r=records[row['native_key']]
        enriched.append(dict(rank=row['rank'],native_key=r['native_key'],city_town=r['literal_tuple'][0],ward=r['literal_tuple'][1],precinct=r['literal_tuple'][2],state_fips='25',municipal_fips='',source_numeric_native_id='',CSV_record_ordinal=r['csv_record_ordinal'],Warren=r['values'][0],Deaton=r['values'][1],named_source_votes=r['named_source_votes'],AllOthers=r['AllOthers'],named_plus_AllOthers_votes=r['named_plus_AllOthers_votes'],Blanks=r['Blanks'],source_TotalVotesCast=r['TotalVotesCast'],separate_ballots_cast='',undervotes='',overvotes='',registered_voters='',method='',source_id=r['source_id'],source_body_sha256=contract['source_body_sha256'],cumulative_named_votes=row['cumulative_votes'],share_exact=row['share_exact'],cumulative_share_exact=row['cumulative_share_exact'],weight=row['weight'],in_top15=row['in_top15'],in_minimum80=row['in_minimum80']))
    csvwrite(STATE/'data/county-turnout.csv',enriched)
    controls=[]
    for tag,c in contests.items():
        controls.append(dict(contest=tag,source_id=c['source_prefix'],columns=c['columns'],state_control=c['state_control'],named_source_votes=c['named_source_votes'],named_plus_AllOthers_votes=c['named_plus_AllOthers_votes'],municipal_count=351,native_context_count=c['native_context_count'],municipal_native_field_comparisons=c['municipal_native_field_comparisons'],source_positions_count=c['source_positions_count'],html_candidate_cards=c['html_candidate_cards'],html_county_sum_minus_state_footer=c['html_county_sum_minus_state_footer'],unallocated_municipal_contexts=[r['native_key']for r in c['native_contexts']if r['context_type']=='unallocated_municipal_context']))
    dump(D/'controls.json',controls);dump(D/'ranking-summaries.json',results)
    impacts={}
    for k,o in orders.items():
        if k.startswith('2024-senate-native')and k!=label:
            selected=[r['native_key']for r in o if r['in_minimum80']];base=contract['ordered_priority_keys']
            impacts[k]=dict(summary=results[k],positions_changed=sum(a['native_key']!=b['native_key']for a,b in zip(primary,o)),priority_added=[x for x in selected if x not in set(base)],priority_removed=[x for x in base if x not in set(selected)],primary_priority_votes_under_sensitivity=sum(records[x][results[k]['field']]for x in base))
    dump(D/'sensitivity-impacts.json',impacts)
    alternative=sorted(contests['2024-senate']['native_contexts'],key=lambda r:(-r['named_source_votes'],r['csv_record_ordinal']))
    altkeys=[r['native_key']for r in alternative];basekeys=[r['native_key']for r in primary]
    dump(D/'alternative-order-presentation.json',dict(rule='descending integer named-source votes, then original CSV record ordinal (alternative only)',statewide_votes=summary['statewide_votes'],minimum80_count=N,minimum80_votes=sum(r['named_source_votes']for r in alternative[:N]),positions_changed=sum(a!=b for a,b in zip(altkeys,basekeys)),priority_added=[k for k in altkeys[:N]if k not in set(basekeys[:N])],priority_removed=[k for k in basekeys[:N]if k not in set(altkeys[:N])],full_ordered_keys=altkeys,not_primary=True))
    inside=sum(records[k]['AllOthers']for k in basekeys[:N]);outside=sum(records[k]['AllOthers']for k in basekeys[N:])
    C=summary['minimum80_votes'];B=summary['preceding_votes'];T=summary['statewide_votes']
    outside_break=(5*C-4*T)//4+1;inside_preceding=4*T-5*B
    assert 5*C>=4*(T+outside_break-1)and 5*C<4*(T+outside_break)
    assert 5*(B+inside_preceding-1)<4*(T+inside_preceding-1)and 5*(B+inside_preceding)>=4*(T+inside_preceding)
    dump(D/'writein-scope-bounds.json',dict(source='independent original native CSV extraction',named_statewide=T,fixed_priority_count=N,fixed_priority_named_votes=C,fixed_preceding_count=N-1,fixed_preceding_named_votes=B,AllOthers_inside_fixed_priority=inside,AllOthers_outside_fixed_priority=outside,minimum_additional_eligible_wholly_outside_breaks_fixed_priority80=outside_break,minimum_additional_eligible_wholly_inside_fixed_preceding_reaches80=inside_preceding,qualification='Counterfactual integer algebra only. Additional genuinely eligible votes wholly outside fixed1470 with none inside, or wholly inside fixed1469 with none outside. No actual eligibility/allocation or resulting candidate-vote order/cardinality is established. Matching full-AllOthers membership does not prove legal/write-in robustness.'))
    for k in ['2024-senate-native-named_source_votes','2024-senate-municipal-named_source_votes','2024-senate-native-named_plus_AllOthers_votes','2024-senate-native-TotalVotesCast']:print(k,json.dumps(results[k]))
if __name__=='__main__':main()
