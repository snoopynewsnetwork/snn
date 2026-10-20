"""Independently decode originals and check literal scope, fields and controls."""
from acquire import *
from extract import Tables
import collections,csv,io,zipfile,xml.etree.ElementTree as ET
def get(n):
    r=json.loads((HERE/'receipts'/f'{n}.json').read_bytes());return r,body(r)
def main(write=True):
    checks=0
    def ck(v,label):
        nonlocal checks
        assert v,label;checks+=1
    receipts=[]
    for f in sorted((HERE/'receipts').glob('*.json')):
        r=json.loads(f.read_bytes());receipts.append(r)
        for field in ['body','decoded_body','request_body']:
            v=r.get(field)
            if not v:continue
            b=(STATE/v['path']).read_bytes();ck(len(b)==v['bytes'] and sha(b)==v['sha256'] and len(b)<40000000,f.name+field)
            raw=gzip.decompress(b);ck(len(raw)==v['raw_bytes'] and sha(raw)==v['raw_sha256'],f.name+' raw '+field)
        for x in r.get('redirects',[]):
            v=x['body'];b=(STATE/v['path']).read_bytes();ck(sha(b)==v['sha256'] and sha(gzip.decompress(b))==v['raw_sha256'],'whole redirect body')
        ck(r['current_count_admitted'] is False and r['current_change_admitted'] is False,'no current admission')
    csv_rows={}
    for n in ['primary-federal-csv','primary-all-csv']:
        r,b=get(n);csv_rows[n]=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
    rows=csv_rows['primary-federal-csv'];ck(len(rows)==11 and len(rows[0])==13,'complete bounded federal CSV')
    senate=[r for r in rows[1:] if r[0]=='10778'];ck(len(senate)==3,'Senate whole observed field')
    for row in senate:ck(int(row[7])==sum(int(row[j]) for j in [10,11,12]),'state candidate method closure')
    statewide={r[4]:int(r[7]) for r in senate};county_checks=[]
    for party in ['DEM','REP']:
        r,b=get('primary-senate-'+party);v=json.loads(b);names={x['CountyName'] for x in v};ck(len(names)==33,'all county response '+party)
        totals=collections.Counter()
        for x in v:totals[x['CandidateID']]+=int(x['calcCandidateVotes'])
        ck(dict(totals)=={r[4]:int(r[7]) for r in senate if r[2]==party},'county closes state '+party)
        seen=set()
        for x in v:
            cid=x['CountyID'].strip()
            if cid in seen:continue
            seen.add(cid);n='primary-native-'+party+'-'+cid;r,b=get(n);native=json.loads(b)
            ck(all(y['CountyID'].strip()==cid and y['CountyName']==x['CountyName'] and y['RaceID']==10778 and y['PartyCode']==party for y in native),'native literal scope '+n)
            candidates=sorted({y['CandidateID'] for y in native});masked=sum(y['calcCandidateVotes']=='*' for y in native);sums=collections.Counter()
            for y in native:
                if str(y['calcCandidateVotes']).isdigit():sums[y['CandidateID']]+=int(y['calcCandidateVotes'])
            controls={y['CandidateID']:int(y['calcCandidateVotes']) for y in v if y['CountyID'].strip()==cid}
            county_checks.append(dict(county=x['CountyName'],county_id_literal=x['CountyID'],party=party,response_rows=len(native),native_ids=len({y['StatePrecinctID'] for y in native}),blank_native_ids=sum(y['StatePrecinctID'] in [None,''] for y in native),candidate_ids=candidates,candidate_mask_cells=masked,known_candidate_sums=dict(sums),county_control=controls,control_minus_known={k:controls[k]-sums[k] for k in controls},every_native_field_preserved_by_raw_body=r['decoded_body'],cross_year_current_join=None))
    r,b=get('general-candidates');p=Tables(b);t=next(t for t in p.tables if any(k=='id' and val=='ctl00_MainContent_rgCandidate_ctl00' for k,val in t['attributes']));rr=[[''.join(x['text_parts']).strip() for x in row['cells']] for row in t['rows']]
    ck(len(rr[0])==24,'full general roster header');general=[dict(source_table_row=i+1,complete_cells=r,complete_headers=rr[0]) for i,r in enumerate(rr) if len(r)==24 and r[0]=='United States Senator']
    ck(len(general)==4,'four observed portal Senate status rows');ck([r['complete_cells'][21] for r in general]==['Qualified','Qualified','Disqualified','Disqualified'],'literal statuses')
    r,b=get('primary-bernalillo-export-session-post');z=zipfile.ZipFile(io.BytesIO(b));worksheets=[]
    for name in z.namelist():
        raw=z.read(name);ck(sha(raw)==sha(z.read(name)),'complete ZIP entry')
        if name.startswith('xl/worksheets/') and name.endswith('.xml'):
            t=ET.fromstring(raw);ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            worksheets.append(dict(name=name,rows=len(t.findall('.//s:row',ns)),cells=len(t.findall('.//s:c',ns)),dimensions=[x.attrib for x in t.findall('s:dimension',ns)],sha256=sha(raw)))
    ck(len(worksheets)==1 and worksheets[0]['rows']==0 and worksheets[0]['cells']==0,'actual county-labelled workbook empty; not zero votes')
    r,b=get('bernco-data');v=json.loads(b);centers=json.loads(get('bernco-centers')[1]);bc=[]
    for obj in v['contests']:
        c=obj['Value']
        if c['name'].endswith('UNITED STATES SENATOR'):
            for choice in c['choices'].values():ck(choice['totalVotes']==sum(choice[k] for k in ['absentee','early','electionDay']),'Bernalillo method closure')
            bc.append(obj)
    ck(len(bc)==2 and centers['totalVotingCenters']==74 and v['juristiction']['totalVotingCenters']==72,'conflicting complete center objects retained')
    r,b=get('sanjuan-xml');root=ET.fromstring(b);xml_tags=collections.Counter(x.tag for x in root.iter());contests=root.findall('contests/contest');sc=[tree(c) for c in contests if c.get('name','').endswith('UNITED STATES SENATOR')]
    ck(len(sc)==2,'XML primary Senate namespaces observed before counts');ck(root.find('jurisdiction').get('timestamp').startswith('2026-06-02'),'XML actual primary clock')
    groups=root.findall('.//resultgroup');allchoices=[c for x in contests for c in x.findall('choice')];choice_ids=collections.Counter(x.get('id') for x in allchoices)
    xml=dict(root=root.tag,root_attributes=root.attrib,jurisdiction=root.find('jurisdiction').attrib,root_children=[x.tag for x in root],whole_tag_counts=dict(xml_tags),senate_contests=sc,counting_groups=[tree(x) for x in root.findall('countingGroups/*')],resultgroup_attributes=[x.attrib for x in groups],blank_choice_ids=choice_ids.get('',0),duplicate_choice_ids={k:v for k,v in choice_ids.items() if v>1},publisher_timezone=None,raw_well_formed=True,client_patch_applied=False,client_parser_comment_is_not_current_raw_evidence=True)
    out=dict(status='pass',checks=checks,acquisitions=len(receipts),complete_csv_row_counts={k:len(v) for k,v in csv_rows.items()},primary_state_candidate_rows=senate,primary_county_native_checks=county_checks,general_portal_status_rows=general,signed_or_later_roster_exhausted=False,general_portal_ENR_join=None,county_labelled_workbook=worksheets,bernco_full_senate_objects=bc,bernco_juristiction=v['juristiction'],bernco_centers=centers,sanjuan_xml=xml,current_count_admitted=False,current_change_admitted=False)
    if write:dump(HERE/'sample-validation.json',out)
    return out
def tree(e):return dict(tag=e.tag,attributes=dict(e.attrib),text=e.text,tail=e.tail,children=[tree(c) for c in e])
if __name__=='__main__':
    v=main('--audit' not in sys.argv);print(json.dumps({k:v[k] for k in ['status','checks','acquisitions','complete_csv_row_counts','current_count_admitted']}))
