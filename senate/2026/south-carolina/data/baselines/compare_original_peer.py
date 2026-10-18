"""Full-field reciprocal original-source comparison, read-only peer inputs."""
from extract import *
def main():
    peer=DATA/'turnout/extracts';checks=[]
    def compare(name,a,b,fields,key):
        aa={key(r):r for r in a};bb={key(r):r for r in b};assert len(aa)==len(a)and len(bb)==len(b)
        errors=[];counts=collections.Counter()
        for k in aa.keys()&bb.keys():
            for f in fields:
                av,bv=aa[k][f],bb[k][f]
                if f in ['raw_attributes','raw_identity','raw_Eid','raw_Cid']:av,bv=json.loads(av),json.loads(bv)
                if av!=bv:
                    counts[f]+=1
                    if len(errors)<15:errors.append(dict(key=k,field=f,ours=av,peer=bv))
        checks.append(dict(scope=name,ours=len(a),peer=len(b),fields=fields,keys_only_ours=len(aa.keys()-bb.keys()),keys_only_peer=len(bb.keys()-aa.keys()),mismatches=dict(counts),examples=errors,status='pass'if aa.keys()==bb.keys()and not counts else 'differences'))
    def read(p):return list(csv.DictReader(gzip.open(p,'rt')if p.suffix=='.gz'else open(p)))
    a=[]
    for r in read(BASE/'legacy-candidate-methods.csv.gz'):
        if r['source_id'].endswith('detailtxt'):continue
        a.append(dict(contest_label=r['contest_label'],source_id=r['source_id'],county=r['county'],county_fips=r['county_fips'],contest_key=r['source_contest_key'],choice_key=r['source_choice_key'],choice_text=r['source_choice_text'],party=r['source_party'],history_candidate_id=r['analysis_candidate_id'],method=r['method_name'],native_name=r['native_name'],native_ordinal=r['native_ordinal'],votes=r['votes'],source_pointer=r['source_pointer'],raw_attributes=r['raw_attributes']))
    b=read(peer/'legacy-candidate-methods.csv.gz');compare('every original XML native method cell and repaired all-child locator',a,b,list(a[0]),lambda r:(r['contest_label'],r['source_id'],r['source_pointer']))
    aa=[];nativea=[];cache={}
    for r in read(BASE/'legacy-native-baselines.csv.gz'):
        sid=r['source_id'];ss=sid.removesuffix('-details')+'-summary'
        if sid not in cache:
            cache[sid]=json.loads(loadbody(SRC/(sid+'.meta.json'))[0]);cache[ss]=json.loads(loadbody(SRC/(ss+'.meta.json'))[0])
        fields=r['source_pointer'].strip('/').split('/');ci=int(fields[1]);pi=int(fields[-1]);d=cache[sid]['Contests'][ci];si,s=next((i,v)for i,v in enumerate(cache[ss])if v['K']==d['K']);ids=json.loads(r['choice_analysis_ids']);vector=json.loads(r['raw_choice_vector'])
        nativea.append(dict(contest_label=r['contest_label'],county=r['county'],county_fips=r['county_fips'],native_name=r['name'],source_native_id='',native_ordinal=str(pi),raw_identity=compact(dict(P=r['name'],source_ordinal=pi)),raw_Eid=compact(d['Eid']),raw_Cid=compact(d['Cid']),candidate_votes=r['candidate_votes'],source_id=sid,source_pointer=f'/Contests/{ci}',native_name_pointer=r['source_pointer'],candidate_vector_pointer=f'/Contests/{ci}/V/{pi}',summary_source_id=ss,summary_source_pointer=f'/{si}'))
        for i,v in enumerate(vector):aa.append(dict(contest_label=r['contest_label'],county=r['county'],county_fips=r['county_fips'],source_id=sid,summary_source_id=ss,contest_key=d['K'],candidate_ordinal=str(i),candidate_label=s['CH'][i],party=s['P'][i]or'',history_candidate_id=str(ids[i]),native_ordinal=str(pi),native_name=r['name'],votes=str(v),source_pointer=f'/Contests/{ci}/V/{pi}/{i}',native_pointer=r['source_pointer'],choice_label_pointer=f'/{si}/CH/{i}'))
    b=read(peer/'legacy-json-native-units.csv.gz');compare('every original combinedJSON native identity/count/source field',nativea,b,list(nativea[0]),lambda r:(r['contest_label'],r['source_id'],r['native_name_pointer']))
    b=read(peer/'legacy-json-candidate-native.csv.gz');compare('every original combinedJSON candidate-native field',aa,b,list(aa[0]),lambda r:(r['contest_label'],r['source_id'],r['source_pointer']))
    aa=[]
    for r in read(BASE/'legacy-candidate-methods.csv.gz'):
        if not r['source_id'].endswith('detailtxt'):continue
        aa.append(dict(contest_label=r['contest_label'],source_id=r['source_id'],county=r['county'],county_fips=r['county_fips'],native_name=r['native_name'],level='native',candidate_ordinal=r['choice_ordinal'],candidate_label=r['source_choice_text'],party=r['source_party'],method=r['method_name'],votes=r['votes'],line_ordinal=str(int(r['source_pointer'].split('/')[3])-1),column_ordinal=str(2+int(r['choice_ordinal'])*7+int(r['method_ordinal']))))
    b=[r for r in read(peer/'clarendon-2022-txt-candidate-methods.csv')if r['level']=='native'];compare('all1176 Clarendon enabledTXT native cells',aa,b,list(aa[0]),lambda r:(r['contest_label'],r['native_name'],r['candidate_ordinal'],r['method']))
    result=dict(status='pass'if all(r['status']=='pass'for r in checks)else 'differences_retained',peer_agent_id='46dcb766-b312-4aaf-ac85-921179115c95',comparisons=checks,scope_note='Different source-position inventories and geography-key conventions are explicit; numerical/raw source fields and actual locators are compared. No current/physical join.',peer_hashes={str(p.relative_to(DATA)):sha(p.read_bytes())for p in [peer/'legacy-candidate-methods.csv.gz',peer/'legacy-json-native-units.csv.gz',peer/'legacy-json-candidate-native.csv.gz',peer/'clarendon-2022-txt-candidate-methods.csv']})
    dump(BASE/'peer-original-reconciliation.json',result);print(compact(dict(status=result['status'],checks=[dict(scope=r['scope'],rows=r['ours'],mismatches=r['mismatches'],only_ours=r['keys_only_ours'],only_peer=r['keys_only_peer'])for r in checks])))
if __name__=='__main__':main()
