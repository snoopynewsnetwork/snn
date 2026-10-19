#!/usr/bin/env python3
"""Retain official source presentation, exact source clocks and unresolved flag disagreements."""
from pathlib import Path
import json,gzip,zipfile,io,xml.etree.ElementTree as E,re,subprocess,tempfile,html
from extract import D,dump,Tables

def main():
 pp=json.loads((D/'source/historical-page-props.json').read_text());summary=json.loads((D/'baseline-summary.json').read_text());annotations=[]
 namedWI={2024:['Peter Sonski and Lauren Onak','Claudia De la Cruz and Karina Garcia','Chris Garrity and Cody Ballard','Shiva Ayyadurai and Crystal Ellis','Bill Frankel and Steve Jenkins','Brian Anthony Perry and Mark Sbani'],2022:['Tom Harvey','Joanne Rock','John Carleton Rutledge'],2020:['Bruce Lohmiller','Danny Skelly','Michael Sanchez']}
 # Explicit independent abstract headers; no surname-based inference.
 for y in [2024,2022,2020]:
  for c in pp[str(y)]['contest']['candidates']:
   pseudo=c['candidate']['pseudocandidate'];printed=None if pseudo else c['displayName']in namedWI[y]
   annotations.append(dict(year=y,candidate_in_contest_id=c['id'],candidate_id=c['candidate']['id'],display_name=c['displayName'],pseudocandidate=pseudo,app_isWriteIn=c['isWriteIn'],app_isMasked=c['isMasked'],printed_Write_In_marker=printed,flag_disagreement=printed is not None and printed!=c['isWriteIn'],source_scope='official abstract printed marker only; not complete legal eligibility or invalid/generic WI universe',nVotes=c['nVotes']))
 dump(D/'source/candidate-presentation.json',annotations)
 z=zipfile.ZipFile(io.BytesIO(gzip.decompress((D/'source/current-candidates-xlsx.gz').read_bytes())));ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};ss=[''.join(x.itertext())for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)];rs=[]
 for row in E.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('m:sheetData/m:row',ns):
  cells=[]
  for c in row:
   v=c.find('m:v',ns);val=ss[int(v.text)]if c.get('t')=='s'and v is not None else v.text if v is not None else None;cells.append(dict(attributes=c.attrib,raw_v=v.text if v is not None else None,decoded=val))
  if any(c['decoded']=='US Senate'for c in cells):rs.append(dict(source_row=row.attrib['r'],cells=cells))
 assert len(rs)==9;roster=json.loads((D/'source/current-senate-roster.json').read_text())['rows']
 for a,b in zip(rs,roster):assert [c['decoded']for c in a['cells']]==b['fields']
 dump(D/'source/current-senate-spreadsheet-rows.json',rs)
 for name in ['calendar','rules','court-sept14']:
  with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
   f.write(gzip.decompress((D/'source'/(name+'.gz')).read_bytes()));f.flush();text=subprocess.check_output(['pdftotext','-layout',f.name,'-']).decode()
  (D/'source'/(name+'.txt')).write_text(text)
 raw=gzip.decompress((D/'source/law2026.gz').read_bytes()).decode('cp1252');text=html.unescape(re.sub('<[^>]*>',' ',raw));text=re.sub(r'\s+',' ',text);(D/'source/law2026.txt').write_text(text)
 legal={}
 for term in ['1-11-101.','1-10-105.','1-1-106.','1-8.3-111.','1-8.3-113.','1-7.5-107.3.']:
  start=text.rfind(term);assert start>=0;legal[term]=dict(source='law2026',decoded_text_character_offset=start,context=text[start:start+6000])
 dump(D/'source/legal-positions.json',legal)
 dump(D/'source/presentation-qualifications.json',dict(legal_outcome='highest number of votes among all legal candidates; tied highest Senate candidates determined by lot after recounts per1-11-101(2); pair ties and pair+1 are benchmarks only',court='September14,2026SCOTUS26A305 application to stay preliminary injunction DENIED; not a new Colorado arrival deadline',rules_vintage='temporarily adopted/effective10/09/2026',calendar_vintage='lastupdated7/10/2025; has typos including12-Novmeber and literal Sep24Saturday inconsistent with2026; cite verified legal provision not calendar typography',UOCAVA_disagreement='Clerks page says electronic returns received7pmNov3; current2026Title1§1-8.3-111/-113 states timely submitted ballots receivedclosebusiness eighthday; retain differing presentation without inferred electronic remainingpool. Actual2026calendar moves holiday eighthdayNov11 toNov12. No numeric live pool is inferred.',mail_rule='ordinary ballot received7pmNov3; postmark alone insufficient; Rule7.4.10 preserves initial timely intercounty receipt',cure='Rule7.6.5 text eighthday11:59pm; actual2026calendar/clerks pageNov12 holiday adjustment; live estimate must retain source category/status and deadline clock',outstanding_definition='No numeric outstanding pool observed. Issued,returned,date-stamped,SCOREcredit,signature accepted,opened,tabulated,published and certified are separate stages. Count only explicitly stated uncounted candidate-vote pool in calculator, with unknown accepted/eligible participation left unknown.',gaps=['Current final official candidate names/party/write-in flags verified; no current live vendor candidate IDs or precinct joins inferred.','Generic/unqualified/invalid write-in and separate blank/over/under counts absent from selected originals; null, not zero.','No current measured remaining vote pool, timing/cadence calibration, transfer/lower-preference/candidate effects, geometry approval or2026 turnout projection.']))
 print('source presentation and current roster verification PASS')
if __name__=='__main__':main()
