"""Bounded read-only observed public directory selectors, no personal input."""
import concurrent.futures,json,time
from html.parser import HTMLParser
from acquire import ROOT,body,fetch,dump
class Options(HTMLParser):
    def __init__(self):super().__init__();self.rows=[];self.active=None
    def handle_starttag(self,t,a):
        if t=='option':self.active={'attributes':dict(a),'text':''}
    def handle_data(self,d):
        if self.active is not None:self.active['text']+=d
    def handle_endtag(self,t):
        if t=='option' and self.active is not None:
            self.rows.append(self.active);self.active=None
def run():
    p=Options();p.feed(body('state-directory').decode());rows=[r for r in p.rows if r['attributes'].get('value')]
    assert len(rows)==133 and len({r['text'] for r in rows})==133
    def one(r):
        key='directory-'+r['attributes']['value'];url='https://vote.elections.virginia.gov/VoterInformation/PublicContactLookup'
        if (ROOT/'requests'/(key+'.json')).exists():return json.loads((ROOT/'requests'/(key+'.json')).read_bytes())
        return fetch(key,url,'state-directory form action/method POST and literal LocalityUid option '+r['text'],submitted_fields={'LocalityUid':r['attributes']['value']})
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for r in ex.map(one,rows):print(r['key'],r.get('final_status'),flush=True)
    dump(ROOT/'directory-options.json',{'source_request':'state-directory','complete_options_in_order':p.rows})
def retry_after_backoff():
    options=json.loads((ROOT/'directory-options.json').read_bytes())['complete_options_in_order']
    for row in options:
        uid=row['attributes'].get('value')
        if not uid:continue
        key='directory-'+uid;r=json.loads((ROOT/'requests'/(key+'.json')).read_bytes())
        if r.get('final_status')!=403:continue
        key+='-retry'
        if (ROOT/'requests'/(key+'.json')).exists():continue
        time.sleep(3)
        r=fetch(key,'https://vote.elections.virginia.gov/VoterInformation/PublicContactLookup',
          'single unchanged public read-only retry after backoff; original403 retained; literal state-directory option '+row['text'],
          submitted_fields={'LocalityUid':uid})
        print(key,r.get('final_status'),flush=True)
        # One retry per distinct selector only. No changed identity, auth,
        # alternate security route or repeated retry of a denied selector.
if __name__=='__main__':
    import sys
    retry_after_backoff() if '--retry-after-backoff' in sys.argv else run()
