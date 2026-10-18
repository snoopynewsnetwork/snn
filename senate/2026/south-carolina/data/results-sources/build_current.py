#!/usr/bin/env python3
"""Offline current identity and bounded historical-version checks."""
import csv,io,json,re,pathlib,hashlib,collections
from acquire import ROOT,entity

def raw(n):return entity(json.loads((ROOT/'raw'/f'{n}.meta.json').read_text()))
def dump(n,v):(ROOT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')

def build():
 elections=json.loads(raw('candidate-elections'));assert next(x for x in elections if x['electionId']=='22596')['electionDate']=='2026-11-03T00:00:00'
 csvrows=list(csv.DictReader(io.StringIO(raw('candidate-senate-export-search2').decode('utf-8-sig'))));assert len(csvrows)==14
 html=raw('candidate-general-senate-results-search2').decode();trs=re.findall(r'<tr data-index="(\d+)" data-key="(\d+)">(.*?)</tr>',html,re.S);assert len(trs)==14
 current=[]
 for (ordinal,cid,tr),row in zip(trs,csvrows):
  name=(row['Ballot Name (first - middle)']+' '+row['Ballot Name (last - suffix)']).strip();assert name in tr
  current.append({'row_ordinal':int(ordinal),'candidate_tracking_id':cid,'name_on_ballot':name,'raw_export_row':row,'html_source':'candidate-general-senate-results-search2','csv_source':'candidate-senate-export-search2','tracking_election_id':'22596','tracking_office_value':'376','result_candidate_id':None,'identity_scope':'public candidate tracker; no ENR equivalence'})
 active=[x for x in current if x['raw_export_row']['Status']=='Active'];assert {x['name_on_ballot'] for x in active}=={'Annie Andrews','Darline Graham','Mark Hackett','Kasie Whitener'}
 dump('current-ballot.json',{'election_selector_original':elections,'tracking_office':{'value':'376','label':'U.S. Senate'},'records':current,'active_count':4,'sample_ballot_access':'individual ballot link requires voter lookup; no credentials/PII lookup attempted','official_crosschecks':['greenville-candidates original PDF p1','charleston-parent current On the Ballot'],'write_in_scope':'General Senate write-ins allowed; state guidance no filing form/fee required, notification encouraged; defeated primary candidates may not actively campaign as write-ins. No complete qualified named write-in universe established. Generic total retained separately when published.','ENR_current_ids':None})
 samples={n:json.loads(raw('lancaster-2026-primary-'+n)) for n in ['summary','details','sum','status','config']};settings=json.loads(raw('lancaster-settings-english'));checks=[]
 for i,s in enumerate(samples['summary']):
  dt=next(x for x in samples['details']['Contests'] if x['K']==s['K']);assert len(dt['P'])==len(dt['V'])==len(dt['T']);assert len(set(dt['P']))==len(dt['P'])
  assert len(s['V'])==len(s['CH'])==len(s['P']);assert [sum(v[j] for v in dt['V']) for j in range(len(s['V']))]==s['V']
  for v,t in zip(dt['V'],dt['T']):assert sum(v)==t
  assert sum(s['V'])==s['T'];checks.append({'summary_pointer':'/'+str(i),'contest_key':s['K'],'raw_candidates':s['CH'],'raw_party_labels':s['P'],'total':s['T'],'native_positions':len(dt['P']),'summary_PR':s['PR'],'summary_TP':s['TP'],'Eid':dt['Eid'],'Cid':dt['Cid']})
 old=json.loads(raw('lancaster-old-summary'));diffs=[]
 for s in samples['summary']:
  prev=next(x for x in old if x['K']==s['K']);assert prev['CH']==s['CH']
  for i,(a,b) in enumerate(zip(prev['V'],s['V'])):
   if a!=b:diffs.append({'contest_key':s['K'],'candidate_position':i,'raw_candidate':s['CH'][i],'old':a,'new':b,'delta':b-a})
 assert raw('lancaster-current-version')==raw('lancaster-version-second')==b'375573'
 dump('bounded-client-checks.json',{'status':'pass','application_election_id':'126323','pinned_version':'375573','earlier_linked_version':'374486','observed_election_date':settings['settings']['electiondetails']['electiondate'],'publisher_update_clock':settings['websiteupdatedat'],'timezone_fields':{'literal_clock_zone':'EDT','timezoneoffset':settings['settings']['timezoneoffset'],'isdaylightsaving':settings['settings']['isdaylightsaving']},'settings_raw_edition':settings,'all_contest_checks':checks,'old_new_candidate_deltas':diffs,'two_pointer_observations_equal':True,'current_november_admitted':False,'scope':'Two archived versions plus repeated stable pre-election pointer observations do not establish election-night cadence, correction lag or November availability.'})
 dump('admission-gates.json',{'status':'no_genuine_November_results_admitted','required_election_date':'2026-11-03','state':'SC','office':'U.S. Senate Class II regular general','candidate_tracking_election_id':'22596','tracking_ids_are_ENR_ids':False,'required_candidates':[{'name':r['name_on_ballot'],'party':r['raw_export_row']['Party'],'tracking_id':r['candidate_tracking_id'],'ENR_id':None} for r in active],'write_ins':'retain generic and named original source positions; determine overlap and eligibility before summing','reject':['test/synthetic flags','June or August primary/runoff','2024pres or2020/2022 archives','null/empty election selection','HTML challenge/maintenance/redirect shells','November label with dashes/no numeric count records'],'required_checks':['official parent-to-publication chain','genuine election/stage/office/seat/date','current result-native contest/candidate/method keys','source timestamp+zone+retrieval+publication status','all46 expected county identities and unmatched rows','source-native expected reporting universe; current unknown stays null','candidate/method/county/state reconciliation without overlap','replace coherent cumulative snapshots; preserve decreases and raw flags'],'expected_counties':[{'county':x['name'],'fips':x['county_fips'],'geography_key':x['geography_key'],'native_current_units':None,'native_current_unit_approval':'unverified'} for x in json.loads((ROOT.parent/'turnout/priority-set.json').read_text())['counties']],'running_collector':False,'guaranteed_cadence':None,'exact_outstanding_Senate_votes':None,'calibrated_Needle':False})
 print('Current tracker14/fouractive; all',len(checks),'Lancaster contests checked;',len(diffs),'archived candidate deltas')
if __name__=='__main__':build()
