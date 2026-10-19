"""Direct original statistics/candidate incompatibility; no ballot replacement."""
from pathlib import Path
import gzip,hashlib,json,subprocess,tempfile
from review_allfield_milestone import load,sources,NAMES
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/montgomery-2024-original-panels'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 original=DATA/'turnout/source/sos-2024-county-montgomery.body.gz';pdf=gzip.decompress(original.read_bytes());assert len(pdf)==624685 and sha(pdf)=='dc1a44fd5ea6fa3021a44f3df38f028cd3b272ba92a90fb151536caa599bfc9d';QA.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory()as td:
  p=Path(td)/'original.pdf';p.write_bytes(pdf)
  for page in [1,2,3,4,5]:
   output=QA/f'pdf{page}-complete-original.png'
   if not output.exists():subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-scale-to','3500','-png',str(p),str(output.with_suffix(''))],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 statistics=dict(actual_PDFpage=3,printed_report_page='1 of 3',report_status='Official Results',election_date='November 5, 2024',county='Montgomery County',registered_voters_total=6291,ballots_cast_total=885,ballots_cast_blank=1,turnout_percent_literal='14.07%',election_day_precincts_reporting_literal='14 of 14',footer_literal='Election Summary - 11/15/2024 10:24 AM',timezone=None)
 votes=dict(zip(NAMES,[1737,5,1,5,2658,3,3,8,4,1678,2671]));pres=sum(votes[n]for n in NAMES[:9]);sen=sum(votes[n]for n in NAMES[-2:]);assert(pres,sen)==(4424,4349)
 summary=dict(actual_PDFpage=1,printed_report_page='2 of 3',report_status='Official Results',candidate_votes=votes,presidential_generic_WriteIn_Totals=3,Senate_generic_WriteIn_Totals=13,precincts_reporting_literal_both_contests='14 of 14',footer_literal='Election Summary - 11/15/2024 10:25 AM',receipt_stamp_literal='By Secretary of State Elections Division at 1:04 pm, Nov 15, 2024',timezone=None,unprinted_Contest_Totals=None,unprinted_overvotes=None,unprinted_undervotes=None,unprinted_candidate_method_split=None)
 _,items,sp=load('82views','94576fcfa4b7b245e2d5baa9e8366e4489594804f41694ea04a9f6315e46b336');s=sources(items)['sos-2024-county-montgomery'];assert s['raw_sha256']==sha(pdf);total={}
 for p in s['pages']:
  roles=p.get('roles')or[{'summary_TOTAL':'source_TOTAL','unused':'unused_template_column'}.get(c['unit_type'],'source_native_reporting_constituent')for c in p['columns']]
  for i,role in enumerate(roles):
   if role=='source_TOTAL':total={f.get('candidate',f.get('field')):f['values'][i]for f in p['fields']}
 assert total==votes
 out=dict(status='pass_bounded_fresh_original_Montgomery2024_statistics_incompatible_with_named_contests',source_id='sos-2024-county-montgomery',source_URL='https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Montgomery.pdf',stored_original=pin(original),raw_original_bytes=len(pdf),raw_original_sha256=sha(pdf),fresh_complete_original_renders=[pin(QA/f'pdf{p}-complete-original.png')for p in [1,2,3,4,5]],statistics=statistics,summary=summary,immutable_independent_preferred82_named_source_witness=sp,all11_named_summary_values_match_independent_original_native_TOTAL=True,source_arithmetic=dict(Senate_named=sen,Senate_named_plus_generic=sen+13,presidential_named=pres,presidential_named_plus_generic=pres+3,statistics_ballots=885,Senate_named_minus_statistics_ballots=sen-885,presidential_named_minus_statistics_ballots=pres-885),qualification='Fresh full original PDF1/3 were visually read after the primary lead; fullPDF2/4/5 also viewed for actual packet context. Statistics885ballots/6291registered/blank1/14.07%/14of14 is retained literally, not replaced by named4349Senate/4424presidential or a county-derived guess. The same actualpacket summary separately prints13genericSenate and3genericPres; eligibility/allocation unknown. SummaryactualPDF1printed2of3 and statisticsactualPDF3printed1of3 have distinct10:25/10:24exportclocks; receipt1:04pm and HTTPmetadata are separate, zones absent. Neither reordering nor incompatible values establishes cause/publication chronology/method scope or a current completion measure. No combined-ballot denominator, candidate-method/native generic allocation, currentgeometry or887approval follows. Older availability14preferredsummary/12statistics audit remains exact as a prior unavailable-in-review scope; newly found Montgomery shows why OCRmiss is not sourceabsence.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-montgomery-2024-original-panel-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
