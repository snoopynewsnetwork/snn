"""Full descending rankings, exact integer 80% contracts and universe sensitivity."""
import csv,json,collections
from source_io import ROOT,dump,sha
from extract import csvwrite
def rank(rows,value,key):
    rr=sorted(rows,key=lambda r:(-r[value],r.get('printed_observed_sum')is None if value=='printed_votes'else False,str(r['JurisdictionID']),r['PrecinctName'])if key=='unit_key'else(-r[value],str(r[key])))
    total=sum(r[value]for r in rr);cum=0;out=[];cross=None
    for i,r in enumerate(rr,1):
        prev=cum;cum+=r[value]
        if cross is None and 5*cum>=4*total:cross=i
        unavailable=key=='unit_key'and value=='printed_votes'and r.get('printed_observed_sum')is None
        out.append({**r,'rank':None if unavailable else i,'order_position':i,'ranking_value':r[value],'ranking_value_scope':'empty recorded sum0 only, observed total unavailable'if unavailable else'source-record sum in declared universe','state_denominator':total,'share':r[value]/total,'cumulative_votes':cum,'cumulative_share':cum/total,'at_least_80_integer':5*cum>=4*total,'previous_cumulative_votes':prev})
    return out,{'denominator':total,'minimum_count':cross,'before_votes':out[cross-1]['previous_cumulative_votes'],'crossing_votes':out[cross-1]['cumulative_votes'],'crossing_share':out[cross-1]['cumulative_share'],'top15_share':sum(r[value]for r in rr[:15])/total,'keys':[r[key]for r in rr[:cross]],'full_order':[r[key]for r in rr],'tie_break':'Descending exact integer votes, then literal authority ID string and literal precinct string for native; otherwise source key string','threshold_contract':'5*cumulative >=4*denominator; preceding cumulative strictly below; no floating-point decision'}
def main():
    rows=list(csv.DictReader((ROOT.parent/'county-baselines.csv').open()));contracts={}
    for year in ['2020','2022','2024']:
        rr=[r for r in rows if r['year']==year]
        for value in ['all_named_votes','native_printed_votes','native_raw_mark_universe','ballots_cast']:
            r2=[dict(r,**{value:int(r[value])})for r in rr]
            out,co=rank(r2,value,'county_key');key=f'county-{year}-{value}'
            csvwrite(ROOT/f'priority/{key}.csv',out);contracts[key]=co
    # All disjoint source-native authorities, recorded printed candidates only.
    rows=list(csv.DictReader((ROOT/'extract/authority-candidate-category-totals.csv').open()));t=collections.Counter();generic=collections.Counter();names={r['JurisdictionID']:r['authority_name_native']for r in csv.DictReader((ROOT/'authority-inventory.csv').open())}
    printed={'Kamala D. Harris','Donald J. Trump','Robert F. Kennedy Jr.'}
    for r in rows:
        if r['year']=='2024' and r['candidate_or_category_literal']in printed:t[r['JurisdictionID']]+=int(r['votes'])
        if r['year']=='2024' and r['candidate_or_category_literal'].lower()=='write-in':generic[r['JurisdictionID']]+=int(r['votes'])
    rr=[dict(JurisdictionID=j,authority=names[j],printed_votes=v,printed_plus_generic_record_sum=v+generic[j])for j,v in t.items()]
    out,co=rank(rr,'printed_votes','JurisdictionID');contracts['authority-2024-printed']=co;csvwrite(ROOT/'priority/authority-2024-printed.csv',out)
    out,co=rank(rr,'printed_plus_generic_record_sum','JurisdictionID');contracts['authority-2024-printed-plus-generic-records']=co;csvwrite(ROOT/'priority/authority-2024-printed-plus-generic-records.csv',out)
    units=json.loads((ROOT/'extract/2024-units.json').read_text());rr=[]
    for r in units:
        known=sum(v for v in [r['A'],r['B'],r['printed_other_observed']]if v is not None)
        present=any(k in r['literal_category_record_sums']for k in printed)
        rr.append(dict(unit_key=r['unit_key'],JurisdictionID=r['JurisdictionID'],PrecinctName=r['PrecinctName'],printed_votes=known,printed_known_recorded_sum=known,printed_observed_sum=known if present else None,printed_plus_generic_record_sum=known+r['generic_writein_recorded_sum'],generic_source_present=r['generic_writein_source_present'],A_missing=r['A']is None,B_missing=r['B']is None,other_candidates_missing=json.dumps(r['printed_other_missing_candidates']),method=r['method'],universe='known printed record sum; missing candidate values remain null in source units; not complete legal native vote totals'))
    out,co=rank(rr,'printed_votes','unit_key');contracts['native-2024-printed-observed']=co;csvwrite(ROOT/'priority/native-2024-printed-observed.csv.gz',out)
    out,co=rank(rr,'printed_plus_generic_record_sum','unit_key');contracts['native-2024-printed-plus-generic-records']=co;csvwrite(ROOT/'priority/native-2024-printed-plus-generic-records.csv.gz',out)
    key='county-2024-all_named_votes';base=set(contracts[key]['keys'])
    sensitivity={}
    for k in ['county-2024-native_printed_votes','county-2024-native_raw_mark_universe','county-2024-ballots_cast']:
        other=set(contracts[k]['keys']);sensitivity[k]={'minimum80_same_membership_as_named':base==other,'added_keys':sorted(other-base),'omitted_keys':sorted(base-other),'minimum_count':contracts[k]['minimum_count']}
    dump(ROOT/'priority/contracts.json',{'status':'independent_historical_arithmetic_only_coordinator_geographic_acceptance_pending','contracts':contracts,'county_scope_sensitivity':sensitivity,'native_valid_named_priority_status':'Not established by unallocated native generic marks. Authority/native printed-record priorities are scoped alternatives, not legal-valid native allocation.','current_geometry_approved':False})
    print(json.dumps({'county_valid2024':contracts[key],'scope_sensitivity':sensitivity},indent=2))
if __name__=='__main__':main()
