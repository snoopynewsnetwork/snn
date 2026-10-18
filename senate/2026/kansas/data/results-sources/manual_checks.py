#!/usr/bin/env python3
"""Recheck literal visual transcriptions against pinned county controls.
These are human visual checks on full saved scans, not OCR-derived certification.
"""
import csv,gzip,hashlib,json,pathlib
R=pathlib.Path(__file__).resolve().parent
J=lambda p:json.loads(p.read_text())
BY={x['county']:x for x in csv.DictReader((R.parent/'county-turnout.csv').open())}
def source(sid,pages):
 m=J(R/'raw'/f'{sid}.meta.json')
 assert hashlib.sha256(gzip.decompress((R/m['body_path']).read_bytes())).hexdigest()==m['original_sha256']
 return {'source_id':sid,'original_sha256':m['original_sha256'],'pages':pages,'render_paths':[f'extracts/{sid}-page{x}.png' for x in pages]}
checks=[]
for sid,county,pages,vals,extra in [
 ('barton-2024','Barton',[1,2],{'harris':2207,'trump':8205,'kennedy':117,'oliver':41},{'ballots':10684,'registered':16880,'generic_writein':47,'not_assigned_child':47,'child_overlaps_generic':True,'precincts_reported':42,'total_precincts':42,'complete':29,'partially_reported':13,'source_clock':'11/12/2024 10:44AM; timezone not printed'}),
 ('ellis-2024','Ellis',[1,2],{'harris':3511,'trump':9743,'kennedy':186,'oliver':71},{'ballots':13636,'registered':20431,'generic_writein':57,'contest_votes':13568,'source_clock':'11/18/2024 6:45AM; timezone not printed','method_headers':['Election Day','Early Voting','Advance Mail','W,Th,Fri','Provisional'],'literal_method_rows':{'trump':[5689,3447,413,41,153],'harris':[1682,1431,322,12,64],'kennedy':[126,45,8,2,5],'oliver':[44,21,5,0,1],'generic_writein':[32,20,4,1,0]}}),
 ('riley-2024-abstract','Riley',[1],{'harris':12063,'trump':11630,'kennedy':437,'oliver':183},{'canvass_date':'2024-11-14','signatures_and_seal':'visible; original retained; no authenticity assertion beyond observed signed county publication','scope':'rightmost highlighted presidential totals; alternative summary discrepancy retained'})]:
 for k,v in vals.items():assert int(BY[county]['president_2024_'+k])==v,(county,k)
 if 'literal_method_rows' in extra:
  for k,row in extra['literal_method_rows'].items():assert sum(row)==(extra['generic_writein'] if k=='generic_writein' else vals[k])
 checks.append({**source(sid,pages),'county':county,'visual_named_vector':vals,'four_named_total':sum(vals.values()),'matches_accepted_county_control':True,'observations':extra})
vals={'hart':77,'latz':31,'murray':51,'neumann':103,'parelkar':98,'schmidt':86,'soetaert':36,'taylor':165,'anderson':36,'davis':279,'hamilton':427,'marshall':3051,'naramore':713}
comparison={k:{'county_pdf':v,'accepted_sos':int(BY['Franklin']['senate_primary_2026_'+k]),'county_minus_state':v-int(BY['Franklin']['senate_primary_2026_'+k])} for k,v in vals.items()}
checks.append({**source('franklin-primary',[1,2]),'county':'Franklin','election_date':'2026-08-04','visual_named_vector':vals,'comparisons':comparison,'matches_accepted_county_control':all(x['county_minus_state']==0 for x in comparison.values()),'scope':'PDF visibly says OFFICIAL RESULTS but differs from accepted SOS; party primary alternatives, no cause inferred, no vector replacement, not November returns'})
checks.append({**source('riley-canvass',[1]),'county':'Riley','notice_signed':'2026-09-09','published':'2026-09-26','canvass':'2026-11-12 10:00 Central','place':'Riley County Commission Chambers, 115 N. 4th St., Courthouse Plaza East Building, Manhattan','scope':'November3 general election; scanned signed notice visually read'})
checks.append({**source('saline-general-notice',[1,2,3,4]),'county':'Saline','printed_senate_candidates':[{'literal':'Adam Hamilton (D)','name':'Adam Hamilton','party':'Democratic'},{'literal':'Roger Marshall (R)','name':'Roger Marshall','party':'Republican'},{'literal':'David C Graham (L)','name':'David C. Graham','party':'Libertarian'}],'poll_hours':'2026-11-03 07:00–19:00 Central; page4 signedSeptember25,2026','scope':'November3,2026 printed general election notice; full4pages visually read; write-in affidavit list and subsequent withdrawals not established'})
checks.append({**source('riley-generalnotice',[1,2,3,4]),'county':'Riley','poll_hours':'2026-11-03 07:00–19:00 Central; pages1/4','signed':'2026-09-16','published':'2026-09-26','printed_senate_candidates':['Adam Hamilton Democratic','David C Graham Libertarian','Roger Marshall Republican'],'scope':'full4pages visually read; pages3/4 literal pollingplaces preserved, no reportingunit/geometryjoin'})
checks.append({**source('montgomery-generalnotice',[1,2]),'county':'Montgomery','poll_hours':'2026-11-03 07:00–19:00 Central; page2 allpollingplaces','signed':'2026-09-24','printed_senate_candidates':['David C Graham Libertarian','Adam Hamilton Democratic','Roger Marshall Republican'],'scope':'full2pages visually read; pollingplaces preserved separately from reportingunits'})
(R/'manual-visual-checks.json').write_text(json.dumps({'method':'Rendered full saved original pages visually inspected; these literal transcriptions are distinct from machine extraction. Zeroes occur only where explicitly printed.','checks':checks},indent=2)+'\n')
print('manual checks',len(checks),'named candidate controls',sum(len(x.get('visual_named_vector',{})) for x in checks))
