"""Direct readings of all58 BP009 rows from three complete original pages."""
from pathlib import Path
import hashlib,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/union2024-split-style-original'
PARENTS=[
 (8,'101','Macedonia',414,[('SH13 SS10 SB2','5',414)]),
 (8,'102','Blythe',355,[('SH13 SS10 SB1','5',45),('SH13 SS10 SB2','5',310)]),
 (8,'103','Myrtle',1432,[('M SB1','5',212),('SB1','5',1183),('SB3','10',37)]),
 (8,'104','Glenfield',1060,[('NA1','5',50),('NA2','5',636),('SB1','5',268),('SB3','10',106)]),
 (8,'201','Pinedale',548,[('SH13 SS10 SB2','4',548)]),
 (8,'202','West Union',849,[('SH13 SS10 SB2','4',849)]),
 (8,'203','Sportsplex',1049,[('NA2','4',441),('NA2 SB3','9',0),('NA3','4',90),('SB3','9',518)]),
 (8,'204','Ingomar',1221,[('SS10 SB3','9',1221)]),
 (8,'301',"King's Chapel",602,[('SB3','8',227),('SB4','7',375)]),
 (9,'302','Courthouse',1101,[('NA1 E','3',469),('NA1 W','3',25),('NA2 E','3',0),('NA2 W','3',0),('NA3 E','3',7),('NA3 W','3',166),('NA4 SB3 W','8',92),('NA4 W','3',108),('SB1 E','3',20),('SB3 W','8',63),('SB4 W','7',151)]),
 (9,'303','Central Maintenance',1003,[('NAS','3',686),('SB1','3',317)]),
 (9,'304','Beacon Hill',924,[('NAS','3',37),('SB4','7',887)]),
 (9,'401','Blue Springs',639,[('BS SB4','6',242),('S SB4','6',105),('SB4','6',274),('SB5','1',18)]),
 (9,'402','Hillcrest Church',900,[('NA3','1',404),('NA4','1',481),('SB4','6',15)]),
 (9,'403','Center',510,[('NA4','1',46),('NAS','1',152),('SB4','6',72),('SB5','1',240)]),
 (9,'404','Ellistown Baptist Church',1099,[('S SB4','6',4),('S SB5','1',4),('SB4','6',50),('SB5','1',1041)]),
 (10,'501','Watson Grove Baptist Church',1700,[('NA1','2',482),('NA3','2',395),('NA4','2',543),('NAS','2',280)]),
 (10,'502','Keownville',743,[('NAS','2',665),('SB5','2',78)]),
 (10,'503','Pleasant Ridge',377,[('NAS','2',198),('SB5','2',179)]),
 (10,'504','Jericho',532,[('SB5','2',532)])]
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 parents=[];rows=[]
 for page,code,name,total,splits in PARENTS:
  assert sum(r[2]for r in splits)==total
  parents.append(dict(actual_PDFpage=page,precinct_code_literal=code,precinct_name_literal=name,printed_parent_Total=total,split_rows=len(splits)))
  for i,(split,style,value)in enumerate(splits,1):rows.append(dict(actual_PDFpage=page,parent_precinct_code_literal=code,parent_precinct_name_literal=name,physical_split_row_within_parent=i,split_literal=split,ballot_style_literal=style,party_literal=None,printed_Total_Voters=value))
 assert len(parents)==20 and len(rows)==58 and sum(r['printed_parent_Total']for r in parents)==sum(r['printed_Total_Voters']for r in rows)==17058
 out=dict(source_id='sos-2024-county-union',raw_original_sha256='19a5a0a1138eda18230011669318540099456001a6c1406709743a4dcb384a09',report_literal='Precinct Split Ballot Styles Report',report_number='BP-009',date_literal='11/14/2024',election_literal='11/05/2024 - 2024 PRESIDENTIAL GENERAL ELECTION',fresh_complete_original_pages_visually_read=[pin(QA/f'pdf{p}-complete-original.png')for p in[8,9,10]],parents=parents,split_rows=rows,printed_Grand_Total=17058,qualification='All58rows/20printed parentTOTALs/GrandTOTAL directly read from complete original-page renders before reading baseline row data. Parent codes/names shown once at a group header remain parent context on following split rows, not falsely claimed reprinted values. LiteralNAS and blank Party retained; BallotStyle strings are source-only. The report contains no candidate votes or definition establishing TotalVoters as the separately printed registration17084; arithmetic−26 is not a matched-population discrepancy allocation. No source methods/currentgeometry/cross-publication identity, candidate weights/tie/selected-only targets or887approval follows.')
 p=DATA/'coordinator-union2024-split-style-original-readings.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
