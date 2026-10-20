"""Independent extraction of pinned original entities; stdlib, offline, no peer helpers."""
import csv, gzip, hashlib, io, json, re, collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STATE=ROOT.parent.parent
def dump(path,obj):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(obj,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n'
    path.write_bytes(gzip.compress(text.encode(),mtime=0)) if path.suffix=='.gz' else path.write_text(json.dumps(obj,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
def sources():
    out={}
    for r in json.loads((ROOT/'source/input-pins.json').read_text())['sources']:
        p=STATE/r['receipt_path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['receipt_sha256']
        for e in r['entities']:
            p=STATE/e['path'];b=p.read_bytes();assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
            raw=gzip.decompress(b);assert len(raw)==e['raw_bytes'] and hashlib.sha256(raw).hexdigest()==e['raw_sha256']
        out[r['id']]=gzip.decompress((STATE/r['entities'][-1]['path']).read_bytes())
    return out
def en(v):return next((x['text'] for x in v if x['languageId']=='en'),None)
def records(b, encoding="utf-8-sig"):
    # Tokens plus original logical and physical line positions; original bytes remain pinned.
    r=csv.reader(io.StringIO(b.decode(encoding),newline=''));out=[];last=0
    for i,cells in enumerate(r,1):out.append({'record':i,'line_start':last+1,'line_end':r.line_num,'cells':cells});last=r.line_num
    return out
def historical(key,b):
    raw=records(b);headers=raw[0]['cells'];parties=raw[1]['cells'];total=headers.index('Total Votes Cast');cols=list(range(2,total));rows=[];parent=None
    for rr in raw[2:]:
        c=rr['cells'];assert len(c)==len(headers)
        kind,name=c[:2]
        if kind=='Locality':parent=name
        assert kind in ('State','Locality','Precinct')
        v=[int(c[i]) for i in cols];assert sum(v)==int(c[total])
        rows.append(dict(source_key=f'{key}:record:{rr["record"]}',record=rr['record'],line_start=rr['line_start'],line_end=rr['line_end'],scope=kind,parent=parent if kind!='State' else None,name=name,votes=v,total=int(c[total]),undervotes_literal=c[total+1] if len(c)>total+1 else None))
    parentrows=[r for r in rows if r['scope']=='Locality'];native=[r for r in rows if r['scope']=='Precinct'];state=next(r for r in rows if r['scope']=='State');assert len(parentrows)==133
    discrepancies=[]
    for p in parentrows:
        children=[r for r in native if r['parent']==p['name']];diff=[sum(r['votes'][i] for r in children)-p['votes'][i] for i in range(len(cols))]
        if any(diff):discrepancies.append({'parent':p['name'],'native_minus_parent':diff,'total':sum(diff)})
    obj={'key':key,'headers':headers,'parties':parties,'candidate_columns':[{'position':i,'name':headers[i],'party_literal':parties[i]} for i in cols],'raw_records':raw,'rows':rows,'state':state,'native_count':len(native),'locality_count':133,'native_sums':[sum(r['votes'][i] for r in native) for i in range(len(cols))],'locality_sums':[sum(r['votes'][i] for r in parentrows) for i in range(len(cols))],'discrepancies':discrepancies}
    dump('extracted/'+key+'.json.gz',obj);return obj
def priority(h):
    def ranking(rows):
        ordered=sorted(rows,key=lambda r:(-r['total'],r['record']));total=sum(r['total'] for r in ordered);cum=0;cut=None;result=[]
        for n,r in enumerate(ordered,1):
            cum+=r['total']
            if cut is None and 5*cum>=4*total:cut=n
            result.append(dict(rank=n,source_key=r['source_key'],record=r['record'],parent=r['parent'],name=r['name'],votes=r['votes'],total=r['total'],cumulative=cum))
        return dict(total=total,threshold_numerator=4,threshold_denominator=5,minimum_integer_volume=(4*total+4)//5,minimum80_count=cut,top15_votes=sum(r['total'] for r in ordered[:15]),before_crossing=result[cut-2]['cumulative'],at_crossing=result[cut-1]['cumulative'],order=result,priority_keys=[r['source_key'] for r in result[:max(15,cut)]])
    out={'basis':'2024 Senate CSV printed named candidates plus generic Write-Ins; not legal eligible write-in robustness','tie_rule':'descending total, then numeric logical CSV record ascending','native':ranking([r for r in h['rows'] if r['scope']=='Precinct']),'locality':ranking([r for r in h['rows'] if r['scope']=='Locality'])}
    dump('independent-priority.json',out)
def main():
    src=sources();hist={}
    for y in ('2018','2020','2024'):hist[y+'-senate']=historical(y+'-senate',src['fresh-'+y+'-csv'])
    hist['2024-president']=historical('2024-president',src['president-csv'])
    priority(hist['2024-senate'])
    # Full hydration objects include pseudo-candidates, all party/control objects and alternate nVotesParty fields.
    for y in ('2018','2020','2024','president'):
        k='fresh-'+y+'-html' if y!='president' else 'president-html';t=src[k].decode();j=json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',t)[1]);dump('extracted/'+k+'-hydration.json.gz',j)
    api=[];methods=[];controls=[]
    for k in ['enr-2024-senate']+sorted(x for x in src if x.startswith('enr-native-')):
        d=json.loads(src[k]);b=d['ballotItemWithBreakdown'];code=k.removeprefix('enr-native-') if k.startswith('enr-native-') else 'STATE'
        # Preserve full native/candidate/method/control objects with original JSON array positions.
        api.append(dict(source=k,scope_code=code,ballotItemWithBreakdown=b,precincts=d['precincts'],election=d['election'],localityElections=d['localityElections'],voterRegistration=d['voterRegistration'],voterTurnout=d['voterTurnout'],jurisdiction=d['jurisdiction']))
        scopes=[('summaryResults',b['summaryResults'])]+[(f'breakdownResults/{i}',x) for i,x in enumerate(b['breakdownResults'])]
        for ptr,x in scopes:
            for ci,c in enumerate(x['ballotOptions']):
                groups=c['groupResults'];s=sum(g['voteCount'] for g in groups) if all(g['voteCount'] is not None for g in groups) else None
                controls.append(dict(source=k,path='/ballotItemWithBreakdown/'+ptr+'/ballotOptions/'+str(ci),candidate=c['nativeId'],voteCount=c['voteCount'],method_sum=s,difference=None if s is None else s-c['voteCount']))
                for gi,g in enumerate(groups):methods.append(dict(source=k,scope_code=code,path='/ballotItemWithBreakdown/'+ptr+'/ballotOptions/'+str(ci)+'/groupResults/'+str(gi),candidate_id=c['id'],candidate_nativeId=c['nativeId'],candidate_name=en(c['name']),**g))
    dump('extracted/api-native-objects.json.gz',api);dump('extracted/method-rows.json.gz',methods);dump('extracted/method-controls.json.gz',controls)
    # Retain all requested office rows of full raw bulk file; every other original byte stays in input pins.
    bulk=records(src['enr-2024-results-report'], 'cp1252');header=bulk[0]['cells'];oi=header.index('OfficeTitle');chosen=[r for r in bulk[1:] if r['cells'][oi] in ('Member, United States Senate','President and Vice President')]
    dump('extracted/bulk-requested-offices.json.gz',{'header':header,'rows':chosen,'all_original_rows':len(bulk)-1})
    for key in ('turnout-2018','turnout-2020','turnout-2022','enr-2024-turnout-report','registration-2024-nov1'):
        dump('extracted/'+key+'-records.json.gz',records(src[key]))
    # Summaries do not collapse overlapping district views or interpret blank as zero.
    admin={}
    for key in ('turnout-2018','turnout-2020','turnout-2022','enr-2024-turnout-report'):
        rr=records(src[key]);heads=rr[0]['cells'];groups=collections.defaultdict(list)
        for r in rr[1:]:
            c=r['cells'];view=c[heads.index('district_type')] if 'district_type' in heads else 'undivided report';groups[view].append(c)
        admin[key]={v:dict(rows=len(rs),parents=len(set(c[heads.index('locality')] for c in rs)),literal_sums={h:sum(int(c[i]) for c in rs if c[i]!='') for i,h in enumerate(heads) if h in ('TotalVoteTurnout','ActiveRegisteredVoters','InactiveRegisteredVoters','TotalRegisteredVoters')},blank_counts={h:sum(c[i]=='' for c in rs) for i,h in enumerate(heads)}) for v,rs in groups.items()}
    regall=records(src['registration-2024-nov1']);reg=[r for r in regall if r['cells']];head=reg[0]['cells'];admin['registration-2024-nov1']={'rows':len(reg)-1,'blank_records':len(regall)-len(reg),'parents':len(set(r['cells'][0] for r in reg[1:])),'repeated_state_controls':{h:sorted(set(r['cells'][i] for r in reg[1:])) for i,h in enumerate(head) if h in ('StateTotalLocality','TotalActiveVotersLocality','TotalInActiveVotersLocality','TotalAllVotersLocality','StateTotalPrecincts')}}
    dump('administrative-controls.json',admin)
    dump('source-controls.json',{k:{f:v for f,v in h.items() if f not in ('rows','raw_records')} for k,h in hist.items()})
    print(json.dumps({k:{'native':h['native_count'],'state':h['state']['votes'],'discrepancies':h['discrepancies']} for k,h in hist.items()}))
if __name__=='__main__':main()
