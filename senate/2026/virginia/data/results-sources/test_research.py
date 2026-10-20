"""Actual source-derived mutation checks and explicit synthetic control fixture."""
import argparse,copy,csv,gzip,io,json,re,urllib.parse
from acquire import ROOT,body,dump
from replay import strict,STATE,AUTHORITY,semantic,companion
from admission import full_context,vote_admission,partition
from build import source_link
def run(write=False):
    cases=[]
    def rejects(name,fn):
        try:fn()
        except (ValueError,AssertionError,KeyError,IndexError,StopIteration,TypeError):cases.append({'case':name,'rejected':True})
        else:raise AssertionError('negative fixture accepted: '+name)
    def denies(name,e,c,v):
        r=vote_admission(e,c,v);assert not r['admitted'],name;cases.append({'case':name,'rejected':True,'reasons':r['issues']})
    raw=body('november-senate');x=strict(raw);e=x['election'];c=x['ballotItemWithBreakdown']
    v={'observed_contest_id':c['id'],'complete_body_verified':True,'authority_chain_verified':True,'genuine_release_verified':False,'date_of_genuine_release':'2026-10-20'}
    denies('actual production November zero setup',e,c,v)
    pos=copy.deepcopy(c);pos['voteTotal']=1;good={**v,'genuine_release_verified':True,'date_of_genuine_release':'2026-11-03'}
    # Explicitly synthetic positive contract test; no actual votes are created or
    # admitted. It proves the guard does not reject every conceivable observation.
    assert vote_admission(e,pos,good)['admitted'];cases.append({'case':'synthetic positive guard control','synthetic_only':True})
    for field,value,name in [('electionDate','2024-11-05','old election with positive counts'),('electionDate','2026-08-04','wrong primary election date'),('isPrimary',True,'primary flag'),('isProduction',False,'staging/test flag')]:
        q=copy.deepcopy(e);q[field]=value;denies(name,q,pos,good)
    denies('wrong native contest ID',e,pos,{**good,'observed_contest_id':'old-or-foreign-id'})
    denies('positive pre-election numbers',e,pos,{**good,'date_of_genuine_release':'2026-10-20'})
    denies('HTTP200 and production alone insufficient',e,pos,{**good,'genuine_release_verified':False})
    denies('truncated entity flag',e,pos,{**good,'complete_body_verified':False})
    denies('third-party discovered URL alone insufficient',e,pos,{**good,'authority_chain_verified':False})
    rejects('truncated JSON body',lambda:strict(raw[:-1]))
    rejects('duplicate JSON key',lambda:strict(b'{"native":1,"native":2}'))
    rejects('nonfinite exponent',lambda:strict(b'{"votes":1e999}'))
    a=strict(AUTHORITY.read_bytes());contract=strict((STATE/a['frozen_contract']['path']).read_bytes());unit=contract['ordered_units'][0]
    changes=[('missing admin case',lambda u:u.pop('administrative_case')),('missing typed raw cells',lambda u:u.pop('cells')),
      ('missing full candidate party context',lambda u:u['source_native_constituents']['enr_api']['full_native_object']['ballotOptions'][0].pop('party')),
      ('missing native virtual flag',lambda u:u['source_native_constituents']['enr_api']['full_native_object']['precinct'].pop('isVirtual')),
      ('null changed to zero',lambda u:u.__setitem__('ballots_cast',0)),('wrong source position',lambda u:u.__setitem__('source_record',u['source_record']+1)),
      ('wrong native UUID',lambda u:u.__setitem__('source_native_id','wrong-id')),
      ('method ordering changed',lambda u:u['source_native_constituents']['enr_api']['full_native_object']['ballotOptions'][0]['groupResults'].reverse()),
      ('parent source context removed',lambda u:u.pop('parent_label'))]
    full_context(unit,copy.deepcopy(unit))
    for name,mutate in changes:
        q=copy.deepcopy(unit);mutate(q);rejects(name,lambda q=q:full_context(q,unit))
    f=next(f for f in a['complete_source_companion_files'] if f['format']=='csv_full_header_and_all_rows');b=(STATE/f['path']).read_bytes();rows=companion(f,b)
    rejects('CSV header dropped',lambda:full_context(rows[1:],rows))
    rejects('CSV final row dropped',lambda:full_context(rows[:-1],rows))
    rejects('full companion replaced by vote-only projection',lambda:full_context({'votes':1},unit))
    f=next(f for f in a['complete_source_companion_files'] if f['format']=='jsonl_full_ordered_array');b=(STATE/f['path']).read_bytes();rows=companion(f,b)
    rejects('JSONL ordered records permuted',lambda:full_context(rows[::-1],rows))
    s={'election_id':'observed','contest_id':'observed','parent_id':'parent','native_id':'native','method_id':None,'snapshot':'same','level':'native'}
    assert partition([s])
    rejects('duplicate source keys',lambda:partition([s,s]))
    rejects('overlapping state and native totals',lambda:partition([s,{**s,'level':'state','native_id':None}]))
    rejects('two cumulative snapshots combined',lambda:partition([s,{**s,'native_id':'other','snapshot':'later'}]))
    failed=next(json.loads(p.read_bytes()) for p in sorted((ROOT/'requests').glob('*.json')) if json.loads(p.read_bytes()).get('final_url') is None)
    link=source_link({'request':failed['key'],'url':None,'requested_url':failed['requested_url']})
    assert urllib.parse.unquote(re.search(r'\]\((.*)\)$',link).group(1))==failed['requested_url']
    assert '](None)' not in link
    uuid=c['id'];url='https://enr.elections.virginia.gov/results/public/api/elections/virginia/2026-November-General/data/ballot-item/'+uuid
    assert uuid in source_link({'request':'explicit source-edge regression','url':url})
    cases.append({'case':'actual failed-request link fallback and intact observed UUID target','regression_passed':True})
    rejects('formatter cannot invent missing request URL',lambda:source_link({'request':'missing actual URL','url':None}))
    result={'status':'pass','cases':cases,'negative_cases':sum(c.get('rejected',False) for c in cases),'actual_current_returns_admitted':False,'fixture_scope':'source integrity/admission only; no new scenario/outcome/forecast work'}
    if write:dump(ROOT/'negative-fixtures.json',result)
    print(json.dumps({'status':'pass','negative_cases':result['negative_cases']}));return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();run(a.write)
