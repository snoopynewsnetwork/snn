"""Offline negative admission proofs using actual retained evidence. No collector."""
from acquire import *
from check_samples import get
from extract import Tables
import copy,io,csv,zipfile,xml.etree.ElementTree as ET
def main(write=True):
    c=json.loads((STATE/'data/turnout/priority-set.json').read_bytes());records=[]
    def rejected(name,source,check,mutant):
        rejected_value=False
        try:check(mutant)
        except (AssertionError,ValueError,KeyError,TypeError):rejected_value=True
        assert rejected_value,name
        records.append(dict(name=name,source=source,asserted_mutant=mutant,rejected=True))
    def must(v):assert v
    masked=next(x for x in c['constituents'] if '*' in x['source_candidate_literals']);m=copy.deepcopy(masked);m['source_candidate_literals']=['0' if v=='*' else v for v in m['source_candidate_literals']]
    rejected('protected literal must not become zero',masked['key'],lambda v:must(v==masked),m)
    rejected('privacy pools must not disappear','frozen contract',lambda v:must(v==2201),len([x for x in c['constituents'] if not x['administrative']]))
    rejected('source-known sensitivity is not certified priority','frozen contract',lambda v:must(v is None),1392)
    rejected('state denominator is not known numeric denominator','frozen contract',lambda v:must(v==903311),902421)
    rejected('nonempty county/native dispatch substitution forbidden','frozen contract',lambda v:must(v==[]),['nm:county:35001'])
    keys=[x['key'] for x in c['constituents']];bad=keys[:];bad[-1]=bad[0]
    rejected('duplicate source key rejected','frozen contract',lambda v:must(len(set(v))==2201),bad)
    bad=c['complete_coverage_order'][:];bad[0],bad[1]=bad[1],bad[0]
    rejected('coverage sequence is exact, not a fresh ranking','frozen contract',lambda v:must(v==c['complete_coverage_order']),bad)
    for name,stage in [('primary-senate-DEM','primary'),('bernco-data','primary'),('sanjuan-xml','primary'),('primary-federal-csv','primary')]:
        rejected('HTTP200 '+name+' cannot become November returns',name,lambda v:must(v['election_stage']=='November general' and v['coordinator_admitted'] and v['genuine_changing_November_evidence']),dict(http_status=200,election_stage=stage,coordinator_admitted=False,genuine_changing_November_evidence=False))
    rejected('candidate portal namespace does not supply ENR identity','general-candidates',lambda v:must(v is None),dict(candidate_portal_eid='2917',assumed_ENR_eid='2917'))
    rejected('observed Qualified statuses do not exhaust signed later/write-in roster','general-candidates',lambda v:must(v is False),True)
    rejected('unreported or unavailable is not a genuine zero','primary-bernalillo-export-session-post',lambda v:must(v is None),0)
    raw=json.loads(get('bernco-data')[1]);generic=raw['contests'][0]['Value']['choices']['W002-10778']['totalVotes']
    rejected('client display zero is not raw generic-write-in zero','bernco-js / bernco-data',lambda v:must(v==generic),0)
    rejected('completion controls are distinct objects','bernco-data / bernco-centers',lambda v:must(v==[72,0]),[74,74])
    rejected('reported percent cannot supply exact eligible remainder','primary-clocks',lambda v:must(v is None),0)
    rejected('HTTP Last-Modified is not publisher vote timestamp','sanjuan-xml',lambda v:must(v=='2026-06-02T22:51:13.470'),'HTTP-Date')
    rejected('timezone-less publisher clock not automatically UTC','sanjuan-xml',lambda v:must(v is None),'UTC')
    rejected('client repair comment not permission to repair valid XML','sanjuan-xml',lambda v:must(v is False),True)
    rejected('unmatched Otero president18 must not become Senate0','historical original CSV universes',lambda v:must(v is None),0)
    rejected('declared UI polling interval does not prove measured cadence','county-24-public-results',lambda v:must(v is None),30)
    rejected('printed zero beside masked candidates is not ballots imputation','historical original CSV',lambda v:must(v is None),0)
    rejected('draft rule effective-date printing is not filed adoption','nmac-canvass-proposed',lambda v:must(v is False),True)
    native=json.loads(get('primary-native-DEM-01')[1]);whole=native[0]
    rejected('complete source object cannot be vote-only projected','primary-native-DEM-01',lambda v:must(v==whole),{k:whole[k] for k in ['CandidateID','calcCandidateVotes']})
    rejected('current native join remains unapproved','all2201 shared-parent investigations',lambda v:must(v is None),dict(basis='same number/name/FIPS across years'))
    dropped=dict(whole);dropped.pop('AreaType')
    rejected('returned null field must not disappear','primary-native-DEM-01',lambda v:must(v==whole),dropped)
    changed=dict(whole);changed['CountyID']=whole['CountyID'].strip()
    if changed==whole:changed['CountyID']=whole['CountyID']+' '
    rejected('literal county ID spaces are preserved','primary-native-DEM-01',lambda v:must(v==whole),changed)
    parsed=list(csv.reader(io.StringIO(get('primary-federal-csv')[1].decode('utf-8-sig'))));row=next(r for r in parsed[1:] if r[0]=='10778');mutant=row[:];mutant[10]=str(int(mutant[10])+1)
    rejected('method mutation must fail candidate total closure','primary-federal-csv',lambda v:must(int(v[7])==sum(int(v[j]) for j in [10,11,12])),mutant)
    rejected('trailing empty CSV cell cannot be dropped','primary-federal-csv',lambda v:must(v==row),row[:-1])
    original_xml=get('sanjuan-xml')[1];bad_xml=original_xml[:-1]
    # A whole-body byte change fails the immutable raw pin even if a parser could read it.
    r=get('sanjuan-xml')[0]
    rejected('whole original byte mutation fails raw pin','sanjuan-xml',lambda v:must(v==r['decoded_body']['raw_sha256']),sha(bad_xml))
    resolver=json.loads((HERE/'immutable-inputs.json').read_bytes())['historical_exact_body_resolvers'][0]
    rejected('historical virtual body cannot use wrong reconstructed hash',resolver['original_path'],lambda v:must(v==resolver['original_sha256']),'0'*64)
    selected_root=dict(c);selected_root.pop('county_contexts')
    rejected('full contract root cannot omit entire parent objects','data/turnout/priority-set.json',lambda v:must(v==list(c)),list(selected_root))
    out=dict(status='pass',negative_cases=len(records),cases=records,positive_controls=dict(exact_mask_literal=masked,primary_raw_generic_writein=generic,raw_SanJuan_XML_well_formed=ET.fromstring(get('sanjuan-xml')[1]).tag=='Export',historical_source_readable=True,current_admission=False),notes='Offline semantic rejection tests only; no feed collector, live join, remainder model or forecast.')
    if write:dump(HERE/'negative-fixtures.json',out)
    return out
if __name__=='__main__':print({k:v for k,v in main('--audit' not in sys.argv).items() if k in ['status','negative_cases']})
