#!/usr/bin/env python3
"""Build bounded state, ballot, clock and rule observations from retained originals."""
import datetime,gzip,json,re,subprocess,tempfile,pathlib
from zoneinfo import ZoneInfo
from acquire import ROOT,SOURCE,dump,sha
from inspect_html import inspect,decode_body
STATE=ROOT.parent.parent
def main():
    metas={}
    for p in SOURCE.glob('*.json'):
        m=json.load(open(p))
        if isinstance(m,dict) and 'body_path' in m:
            metas[m['source_id']]=m
            if m['http_status']==200 and not decode_body(m).startswith(b'%PDF'):inspect(m['source_id'])
    stateids=[s for s in metas if s.startswith('sos-current')]
    dump(ROOT/'state-inspection.json',{'state_authority':'New Hampshire Secretary of State','election_scope':'2026-11-03 regular Class II United States Senate','current_channels':[metas[s] for s in sorted(stateids)],'current_result_feed_verified':False,'current_numeric_election_contest_candidate_ids':None,'current_feed_test_flag':None,'current_count_scope':None,'current_completion_semantics':None,'known_refresh_seconds':None,'exact_remaining_votes':None,'authority_chain':'Moderator public count and signed local returns → clerk certification/forwarding → SOS examination/canvass → governor federal certificate after recount/appeal provisions. Statutory electronic filing is not evidence of a public API.','fallbacks':['retained official historical SOS originals and independent federal controls','actual clerk-linked static local returns; chronology/status retained','indexed primary current pages and bounded 2026 archived originals where direct access failed'],'gaps':'Direct SOS403 responses are access evidence, not empty data. No current November general candidate payload or verified current-ID crosswalk acquired.'})
    refs=json.load(open(SOURCE/'current-ballot-references.json'));r=refs[0];p=STATE/r['path'];stored=p.read_bytes();b=gzip.decompress(stored)
    assert sha(stored)==r['stored_sha256'] and sha(b)==r['original_sha256'] and len(b)==3214033
    with tempfile.TemporaryDirectory(prefix='nh-official-ballot-') as td:
        q=pathlib.Path(td)/'ballot.pdf';q.write_bytes(b)
        subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to','2000','-png',str(q),str(ROOT/'qa/farmington-ballot-page1')],check=True,capture_output=True)
    dump(ROOT/'current-ballot-review.json',{'original_reference':r,'primary_parent':'https://www.farmington.nh.us/1206/Town-Clerk-Tax-Collector','exact_link':'https://www.farmington.nh.us/DocumentCenter/View/3121','method':'Independent visual reading of original page1 rendered with Poppler; image-only source, not OCR inference.','visible_header':['FARMINGTON','GENERAL ELECTION','NOVEMBER 3, 2026'],'contest_literal':'UNITED STATES SENATOR','vote_limit':1,'printed_candidates_in_order':[{'name':'John E. Sununu','party':'Republican'},{'name':'Edmond Laplante','party':'Constitution'},{'name':'Chris Pappas','party':'Democratic'}],'write_in_space':True,'current_result_candidate_ids':None,'scope':'Farmington general sample, not a primary nominee list or verified statewide ballot-style/ID crosswalk.','preview':'qa/farmington-ballot-page1.png','original_pages':2})
    hours=[]
    for sid,place,opening,closing,pattern in [
        ('municipal-bedford-pages2','Bedford High School',7,19,r'7:00AM - 7:00PM'),
        ('municipal-windham-pages2','Windham High School Auditorium',7,20,r'7:00\s+AM\s*-\s*8:00\s+PM'),
        ('municipal-dover-pages1','Six published ward polling locations',7,19,r'Polls will be open from 7 a.m. to 7 p.m.'),
        ('municipal-charlestown-clerk-deep1','Charlestown Senior Center,223 Old Springfield Rd',8,19,r'8:00 AM – 7:00 PM'),
        ('municipal-new-boston-pages2','New Boston Central School',7,19,r'7am-7pm')]:
        a=json.load(open(ROOT/'derived'/(sid+'.json')));match=re.search(pattern,a['text']);assert match,sid
        dt=datetime.datetime(2026,11,3,closing,tzinfo=ZoneInfo('America/New_York'))
        hours.append({'source_id':sid,'url':a['url'],'election':'2026-11-03 general','polling_place_scope':place,'opening_local':f'{opening:02}:00','closing_local':f'{closing:02}:00','closing_utc':dt.astimezone(datetime.timezone.utc).isoformat(),'time_zone':dt.tzname(),'character_position':match.start(),'literal_hours':match[0]})
    hours.append({'source_id':'sample-moultonborough-polls','url':metas['sample-moultonborough-polls']['requested_url'],'election':'2026-11-03 general','polling_place_scope':'Moultonborough Academy,25 Blake Road','opening_local':'07:00','closing_local':'19:00','time_zone':'EST','closing_utc':'2026-11-04T00:00:00+00:00','method':'Image-only original page1 independently visually read, October6 notice/October9 posting; preview retained.'})
    dump(ROOT/'poll-hours-evidence.json',{'legal_clock_source':'rsa-time-21-36','timezone':'America/New_York','election_day':'2026-11-03','utc_offset_seconds':-18000,'local_hours':hours,'scope':'Examples explicitly tied to current general; not a statewide full-hours roster. Office opening hours, March local and September primary hours excluded. Voters in line at scheduled close retain statutory rights; local close is not completion.'})
    sections={'rsa-659-chapter':['659:12','659:13','659:20-a','659:23-a','659:49','659:50','659:53','659:63','659:64','659:64-a','659:65','659:67','659:71','659:73','659:74','659:75','659:81','659:84'],
              'rsa-660-chapter':['660:1','660:2','660:3','660:4','660:5','660:6','660:25','660:26'],
              'rsa-657-chapter':['657:1','657:17','657:17-a','657:17-c','657:21-a','657:22','657:23-a','657:26'],
              'rsa-654-chapter':['654:1','654:7-a','654:12']}
    positions=[]
    for sid,keys in sections.items():
        a=json.load(open(ROOT/'derived'/(sid+'.json')));t=a['text']
        for key in keys:
            match=re.search(r'Section '+re.escape(key)+r'\s',t)
            if match:
                end=t.find('Section ',match.end());positions.append({'source_id':sid,'section':key,'character_position':match.start(),'text':t[match.start():end if end>=0 else None]})
    dump(ROOT/'rule-evidence.json',{'primary_statute_positions':positions,'court_order_scope':[
        {'source_id':'court-sep4-order','case':'26-1740','date':'2026-09-04','scope':'First Circuit denies stay of May28 HB1569 QVA/CVA injunction; order expressly addresses September8 primary and November3 general. Restores specified citizenship/challenge affidavits, not waiver of all qualifications.'},
        {'source_id':'court-scotus-appendix','pages':[67,70,71,72,73,74,75],'date':'2026-10-05/07/14','scope':'Oct5 narrow preliminary injunction of April23 guidance, not HB323 statute; officials may consider student ID with other evidence under specified identity-verification provisions. District stay deniedOct7; FirstCircuit renewedstay deniedOct14 (Dunlap would grant).'},
        {'source_id':'court-scotus-docket','date':'2026-10-18 snapshot','scope':'26A512 application filedOct15; response requested11amEDTOct19. Captured docket lists no stay disposition; future action requires recheck.'},
        {'source_id':'court-saucedo-order','date':'2018-08-14','scope':'2018DNH160 permanently enjoins then659:50III signaturematching process. Current statute renumbered/amended; do not infer an automatic mismatch rejection or invented cure/provisional window from literal statutory comparison alone.'}],
        'unresolved':'Current comprehensive2026 clerk cure/signature instructions and all subsequent docket actions not established. No unsupported general post-election cure/provisional pool or outstanding-vote quantity.'})
    print('PASS: original general ballot pins; explicit local hours/EST conversions; statute positions and narrow court scopes retained')
if __name__=='__main__':main()
