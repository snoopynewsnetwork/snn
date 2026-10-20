"""Bounded observed official public API traversal, current setup research only."""
import concurrent.futures,json,time,urllib.parse
from acquire import ROOT,fetch,body
BASE='https://enr.elections.virginia.gov/results/public/api'
def en(items):return next((x['text'] for x in items if x['languageId']=='en'),None)
def get(job):
    key,url,parent=job
    if (ROOT/'requests'/(key+'.json')).exists():return json.loads((ROOT/'requests'/(key+'.json')).read_bytes())
    time.sleep(.15)
    return fetch(*job)
def run(phase):
    data=json.loads(body('november-data'));eid='2026-November-General';jobs=[]
    senate=next(b for b in data['ballotItems'] if en(b['name'])=='Member, United States Senate')
    if phase==1:
        jobs.append(('november-senate',BASE+'/elections/virginia/'+eid+'/data/ballot-item/'+senate['id'],
          'enr-core-chunk getData/ballot-item constructor; november-data literal Senate UUID'))
        for ch in data['jurisdiction']['childLocalities']:
            jobs.append(('jurisdiction-'+ch['shortName'],BASE+'/jurisdictions/'+ch['shortName'],
              'november-data /jurisdiction/childLocalities literal shortName; enr-core-chunk getJurisdiction constructor'))
    if phase==2:
        b=json.loads(body('november-senate'))['ballotItemWithBreakdown']
        for row in b['breakdownResults']:
            g=row['locality'];slug=g['shortName'];bid=row['parentBallotItemId']
            jobs.append(('senate-'+slug,BASE+'/elections/'+slug+'/'+eid+'/data/ballot-item/'+bid,
             'november-senate whole locality.shortName and parentBallotItemId (client adapts locality to breakdownGroup); enr-main selected locality router uses existing electionId; core getData constructor'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        for r in ex.map(get,jobs):print(r['key'],r.get('final_status'),flush=True)
if __name__=='__main__':
    import sys;run(int(sys.argv[1]))
