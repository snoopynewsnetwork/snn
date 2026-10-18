"""Independent original combined-native JSON + Clarendon original TXT audit.

Complete shared originals are read-only; every required original summary/details
object and TXT row retained, including controls/flags. No geography normalization.
"""
import collections,csv,gzip,io,json,os,re,zipfile
from acquire import H,sha,body
from extract_legacy import PEER,SPECS
from build_turnout import dump,csvout,rank

def rawsource(sid):
    p=PEER/(sid+'.meta.json');m=json.loads(p.read_text());assert m['http_status']==200,(sid,m['http_status'])
    b=(p.parent/m['body_path']).read_bytes();assert sha(b)==m['stored_sha256']and len(b)==m['stored_bytes']
    raw=gzip.decompress(b)if m.get('stored_encoding','gzip')=='gzip'else b;assert sha(raw)==m['original_sha256']and len(raw)==m['original_bytes']
    return raw,dict(source_id=sid,metadata_path=os.path.relpath(p,H),body_path=os.path.relpath((p.parent/m['body_path']).resolve(),H),stored_sha256=m['stored_sha256'],stored_bytes=m['stored_bytes'],original_sha256=m['original_sha256'],original_bytes=m['original_bytes'],stored_encoding=m.get('stored_encoding','gzip'),requested_url=m['requested_url'],final_url=m['final_url'],retrieved_utc=m['retrieved_utc'],http_status=m['http_status'])
def main():
    rows=list(csv.DictReader((H/'../county-turnout.csv').open()));fips={r['county']:r['county_fips']for r in rows}
    refs={};positions=[];cells=[];units=[];rosters={};checks={};txtpositions=[];txtcells=[];summaryby={}
    for label,(year,title,mapping)in SPECS.items():
        rosters[label]={};countychecks=[];allunits=[];total=0
        g=json.loads(body(label+'-combined'))['data']['contestGranularData'];db={c['division']['name']:c for c in g['divisions']['children']}
        for cname,cfips in fips.items():
            sid=f'legacy{year}-county-{cname.lower()}';summid=sid+'-summary';detid=sid+'-details'
            b,ref=rawsource(summid);refs[summid]=ref;su=json.loads(b)
            summarymatches=[(i,s)for i,s in enumerate(su)if ' '.join(s['C'].split())==title];assert len(summarymatches)==1,(label,cname)
            si,s=summarymatches[0];summaryby[(label,cname)]=s;positions.append(dict(source_id=summid,source_pointer=f'/{si}',contest_label=label,raw_object=s))
            b,ref=rawsource(detid);refs[detid]=ref;de=json.loads(b)
            matches=[(i,d)for i,d in enumerate(de['Contests'])if d['K']==s['K']];assert len(matches)==1
            di,d=matches[0];positions.append(dict(source_id=detid,source_pointer=f'/Contests/{di}',contest_label=label,raw_object=d))
            assert len(s['CH'])==len(s['P'])==len(s['V']);assert len(d['P'])==len(d['V'])
            assert len(d['P'])==len(set(d['P'])),(sid,'duplicate native names in combined scope')
            ids=[mapping['NON'if not p and s['CH'][j]=='Write-In'else p]for j,p in enumerate(s['P'])];assert len(ids)==len(set(ids))
            named_native=[];vectors=[];vsum=collections.Counter()
            for i,(pname,v)in enumerate(zip(d['P'],d['V'])):
                assert len(v)==len(ids);cv=sum(v);vectors.append(tuple(v[ids.index(cid)]for cid in sorted(ids)))
                originalkey=f'SC:enr-json:{label}:{cfips}:row:{i}'
                rec=dict(geography_key=originalkey,contest_label=label,county=cname,county_fips=cfips,native_name=pname,source_native_id=None,native_ordinal=i,raw_identity={'P':pname,'source_ordinal':i},raw_Eid=d.get('Eid'),raw_Cid=d.get('Cid'),candidate_votes=cv,source_id=detid,source_pointer=f'/Contests/{di}',native_name_pointer=f'/Contests/{di}/P/{i}',candidate_vector_pointer=f'/Contests/{di}/V/{i}',summary_source_id=summid,summary_source_pointer=f'/{si}',identity_status='source-native combined reporting row; no physical/DB/current crosswalk asserted')
                units.append(rec);named_native.append(rec);allunits.append(dict(geography_key=originalkey,name=pname,county=cname,candidate_votes=cv));total+=cv
                for j,(cid,vote)in enumerate(zip(ids,v)):
                    vsum[cid]+=vote;cells.append(dict(contest_label=label,county=cname,county_fips=cfips,source_id=detid,summary_source_id=summid,contest_key=s['K'],candidate_ordinal=j,candidate_label=s['CH'][j],party=s['P'][j],history_candidate_id=cid,native_ordinal=i,native_name=pname,votes=vote,source_pointer=f'/Contests/{di}/V/{i}/{j}',native_pointer=f'/Contests/{di}/P/{i}',choice_label_pointer=f'/{si}/CH/{j}'))
            assert list(vsum[cid]for cid in ids)==s['V']
            assert 'T'not in s or sum(s['V'])==s['T']
            for cid,vote in vsum.items():assert vote==next(r['votes']for r in db[cname]['granularRow']if r['candidateId']==cid),(label,cname,cid)
            dbvectors=[tuple(next(r['votes']for r in n['granularRow']if r['candidateId']==cid)for cid in sorted(ids))for n in db[cname]['children']]
            # Equal multisets are a numerical comparison only; no point/ID crosswalk.
            equal=collections.Counter(vectors)==collections.Counter(dbvectors)
            countychecks.append(dict(county=cname,county_fips=cfips,original_native_count=len(d['P']),database_native_count=len(dbvectors),candidate_total=sum(s['V']),source_summary_controls={k:s.get(k)for k in ['regvoters','BCxContest','VF','TP','PR','TV','BC','RC','RO']},candidate_vector_multiset_equal_DB=equal,source_summary_id=summid,source_details_id=detid))
            rosters[label][cfips]=named_native
        nativeorder,nstat=rank(allunits,'candidate_votes');csvout(f'extracts/{label}-original-combined-native-order.csv',nativeorder)
        checks[label]=dict(native_units=len(allunits),total=total,native_ranking=nstat,counties=countychecks)
    # XML is explicitly disabled for pinned 2022 Clarendon. Parse the actual TXT.
    sid='legacy2022-clarendon-pinned-detailtxt';raw,ref=rawsource(sid);z=zipfile.ZipFile(io.BytesIO(raw));assert not z.testzip();assert z.namelist()==['detail.txt'];b=z.read('detail.txt');ref.update(zip_member='detail.txt',member_sha256=sha(b),member_bytes=len(b));refs[sid]=ref
    lines=b.decode().splitlines();txtchecks={}
    for label in ['2022-senate','2022-governor']:
        title=SPECS[label][1];i=next(i for i,line in enumerate(lines)if line.strip()==title+' (Vote For 1)');labels=re.split(r' {2,}',lines[i+1].strip());header=re.split(r' {2,}',lines[i+2].strip());summary=summaryby[(label,'Clarendon')];assert labels==summary['CH']
        assert header[:2]==['County','Registered Voters']and header[-1]=='Total';methods=header[2:8];assert header[8]=='Choice Total'
        block=[];j=i+3
        while j<len(lines)and lines[j].strip():
            fields=re.split(r' {2,}',lines[j].strip());assert len(fields)==2+7*len(labels)+1,(label,j,len(fields))
            txtpositions.append(dict(source_id=sid,contest_label=label,line_ordinal=j,raw_line=lines[j],fields=fields));block.append(fields)
            for cidx,cname in enumerate(labels):
                for midx,mname in enumerate(methods):txtcells.append(dict(contest_label=label,source_id=sid,county='Clarendon',county_fips='45027',native_name=fields[0],level='county_summary'if fields[0]=='Totals:'else'native',candidate_ordinal=cidx,candidate_label=cname,party=summary['P'][cidx],method=mname,votes=int(fields[2+7*cidx+midx]),line_ordinal=j,column_ordinal=2+7*cidx+midx))
                assert sum(map(int,fields[2+7*cidx:8+7*cidx]))==int(fields[8+7*cidx])
            assert sum(int(fields[8+7*x])for x in range(len(labels)))==int(fields[-1]);j+=1
        assert block[-1][0]=='Totals:'and len(block)==29
        for k in range(len(labels)):assert sum(int(x[8+7*k])for x in block[:-1])==int(block[-1][8+7*k])==summary['V'][k]
        txtchecks[label]=dict(native_rows=len(block)-1,total=int(block[-1][-1]),candidate_totals=summary['V'],raw_registration_scope='pinned TXT fields allzero aspublished; not replaced with later currentversion2023registration')
    dump('legacy-json-observations.json',refs);dump('legacy-json-native-rosters.json',rosters);dump('legacy-json-reconciliation.json',dict(required_original_objects=len(positions),native_units=len(units),candidate_native_cells=len(cells),contests=checks,clarendon_TXT=txtchecks))
    (H/'extracts/legacy-json-source-positions.jsonl.gz').write_bytes(gzip.compress(b''.join((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode()for r in positions),mtime=0))
    csvout('extracts/legacy-json-candidate-native.csv.gz',cells)
    csvout('extracts/legacy-json-native-units.csv.gz',({**r,'raw_identity':json.dumps(r['raw_identity']),'raw_Eid':json.dumps(r['raw_Eid']),'raw_Cid':json.dumps(r['raw_Cid'])}for r in units))
    (H/'extracts/clarendon-2022-txt-source-positions.jsonl.gz').write_bytes(gzip.compress(b''.join((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode()for r in txtpositions),mtime=0));csvout('extracts/clarendon-2022-txt-candidate-methods.csv',txtcells)
    contract=json.loads((H/'priority-set.json').read_text());contract['original_combined_json_observations']=refs
    for c in contract['counties']:
        c['original_enr_combined_json_constituents']={label:rosters[label][c['county_fips']]for label in SPECS}
        if c['name']=='Clarendon':c['original_enr_2022_method_source']={'XML':'explicitlydisabled; pinned/current404 retained in peer provenance','source_ref':sid,'format':'original detail.txt in ZIP','position_extract':'extracts/clarendon-2022-txt-source-positions.jsonl.gz','method_extract':'extracts/clarendon-2022-txt-candidate-methods.csv'}
    dump('priority-set.json',contract)
    print(json.dumps(dict(native_units=len(units),candidate_cells=len(cells),totals={k:v['total']for k,v in checks.items()},vector_multiset_disagreements={k:[r['county']for r in v['counties']if not r['candidate_vector_multiset_equal_DB']]for k,v in checks.items()},clarendon_TXT=txtchecks),indent=2))
if __name__=='__main__':main()
