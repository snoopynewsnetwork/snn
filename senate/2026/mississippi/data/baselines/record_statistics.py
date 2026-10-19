"""Independent visual readings of complete original 2024 statistics panels."""
from sources import *
def main():
 rows=[]
 def add(county,page,reg,ballots,blank,turnout,precincts,methods=None,**kw):
  key='sos-2024-county-'+county
  rows.append(dict(source_id=key,raw_sha256=sha(original(key)),page=page,method_labels=methods or ['TOTAL'],registered_voters_total=reg,registration_definition='Printed Registered Voters - Total; active/inactive/status date not specified on panel.',ballots_cast_total=ballots,ballots_cast_blank=blank,printed_turnout_percent=turnout,precinct_reporting_literal=precincts,timezone=None,evidence=f'qa/{key}-summary-review-p{page}.png',**kw))
 add('attala',9,12389,[7786],[1],'62.85%',['20 of 20'],status_literal='Official Results',clock_literal='11/14/2024 2:24 PM')
 add('leflore',1,19442,[9584],None,'49.30%',['18 of 18'],status_literal='Official Results',clock_literal='11/14/2024 4:50 PM',received_stamp_literal='8:35 am, Nov 15, 2024')
 add('grenada',11,13752,[9837],[3],'71.53%',['13 of 13'],status_literal='Official Election Results',clock_literal='11/13/2024 1:27 PM')
 add('jones',15,0,[27955,24450,3361,115,29],None,'0.00%',['38 of 38','38','0','38','0'],['TOTAL','Election Day','Absentee','Affidavit','5 Day Absentee'],status_literal='UNOFFICIAL RESULTS',clock_literal='11/13/2024 7:38 PM',qualification='Printed zero registration and0.00% retained; not treated as evidence of an empty county register. Precinct counts across methods are not additive.')
 add('tippah',12,13785,[9646,8189,1237,217,0,0,3],[0,0,0,0,0,0,0],'69.97%',['21 of 21','21','0','21','0','0','21'],['TOTAL','Election Day','Absentee','Affidavit','Voter ID Affidavit','5 Day Absentee','Resolution'],status_literal='OFFICIAL RESULTS',clock_literal='11/15/2024 2:17 PM',handwritten_note='From the Server 11/15/2024 matching Sems')
 add('kemper',2,7038,[4166],None,'59.19%',['14 of 14'],status_literal='Official Results',clock_literal='11/15/2024 12:18 PM')
 add('tishomingo',9,13287,[9094],[0],'68.44%',['13 of 13'],status_literal='Unofficial Results',clock_literal='11/08/2024 10:28 AM')
 add('tunica',2,0,[2745],[1],'0.00%',['12 of 12'],status_literal='Official Results',clock_literal='11/15/2024 3:18 PM',qualification='Printed zero registration and0.00% retained; not evidence of no registered people.')
 add('union',11,17084,[12533,10796,1657,80,0,0,0],[1,0,1,0,0,0,0],'73.36%',['20 of 20','20','0','20','0','0','0'],['TOTAL','Election Day','Absentee','Affidavit','Voter ID Affidavit','5 Day Absentee','Resolution'],status_literal='Official Results',clock_literal='11/14/2024 4:52 PM',additional_reporting_rows={'Precincts Complete':['0 of 20','20','0','20','0','0','0'],'Precincts Partially Reported':['20 of 20','0','0','0','0','0','0'],'Absentee/Early Precincts Reporting':['20 of 20','0','20','0','0','0','0']},qualification='Apparently conflicting source reporting rows retained verbatim; no inference of completion from totals alone.')
 add('winston',6,0,[8459],None,'0.00%',['12 of 12'],status_literal='Official',clock_literal='11/14/2024 6:09 PM',qualification='Printed zero registration and0.00% retained; not evidence of no registered people.')
 add('pike',12,24692,[12824],None,'51.94%',['25 of 25'],status_literal='Certified Results',clock_literal='11/15/2024 3:05 PM',vintage_scope='Original 56-page packet; not updated10-page publication. No updated ballot/registration allocation inferred.')
 add('lauderdale',2,41572,[27597,23766,3337,467,21,6],None,'66.38%',['37 of 37','37','0','37','0','37'],['TOTAL','Election Day','Absentee','Affidavit','5 Day Absentee','Resolution'],status_literal='Official Results',clock_literal='11/14/2024 12:00 PM',qualification='County ballots27597; Senate opportunities27593 includingResolution2 versus countyResolution6. Separate source scopes.')
 for r in rows:
  assert len(r['ballots_cast_total'])==len(r['method_labels'])
  if len(r['method_labels'])>1:assert sum(r['ballots_cast_total'][1:])==r['ballots_cast_total'][0]
 save(OUT/'canvass-statistics-readings.json',dict(qualification='Independent direct original visual readings. Null means absent on selected panel, not zero. Raw full originals and all-page OCR preserve other fields. No source clock is a live release cadence.',readings=rows))
 print('12 independently read original statistics panels; all printed ballot method vectors close')
if __name__=='__main__':main()
