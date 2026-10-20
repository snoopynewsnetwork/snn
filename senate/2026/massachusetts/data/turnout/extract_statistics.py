#!/usr/bin/env python3
"""Parse saved direct-primary browser observations without inventing local cells.

The raw HTTP statistics downloads were blocked. These browser text observations
are supplemental source-scoped statewide controls, never original HTTP entities.
"""
import datetime,json,re
from pathlib import Path
from fractions import Fraction
D=Path(__file__).resolve().parent
def main():
    text=(D/'source/browser-statistics-observation.txt').read_text()
    state=text.split('## State Elections',1)[1].split('## State Primaries',1)[0]
    out=[]
    dates={2020:'2020-10-24',2022:'2022-10-29',2024:'2024-10-26'}
    method_dates={2020:'November 3, 2020',2022:'November 8, 2022',2024:'November 5, 2024'}
    for year in [2020,2022,2024]:
        m=re.search(r'\b'+str(year)+r'\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|\s*([\d.]+)%',state);assert m
        reg,total=(int(m[i].replace(',',''))for i in [1,2])
        section=text.split(method_dates[year]+' State Election',1)[1].split('* * *',1)[0]
        values=re.search(r'Mail [–-] ([\d.]+)%.*?Early [–-] ([\d.]+)%.*?Election Day [–-] ([\d.]+)%.*?Total Ballots Cast [–-] ([\d,]+)',section,re.S);assert values,section
        pd=json.loads((D/'controls.json').read_bytes());contest=next(r for r in pd if r['contest']==('2024-senate'if year==2024 else '2022-governor'if year==2022 else '2020-senate'))
        methodtotal=int(values[4].replace(',',''))
        out.append(dict(year=year,registration=reg,registration_date=dates[year],registration_status='Source says Registered Voters; no active-only or voting-eligible definition inferred',turnout_table_TotalVotesCast=total,turnout_table_percent_literal=m[3]+'%',turnout_table_fraction_exact=str(Fraction(total,reg)),method_index_TotalBallotsCast=methodtotal,method_index_percentages_literal=dict(mail=values[1]+'%',early=values[2]+'%',election_day=values[3]+'%'),numeric_method_counts=None,method_workbook_municipal_counts=None,municipal_registration_counts=None,native_registration_counts=None,PD43_TotalVotesCast=contest['state_control'][-1],PD43_minus_turnout_table=contest['state_control'][-1]-total,PD43_minus_method_index=contest['state_control'][-1]-methodtotal,provenance=dict(turnout_table='https://www.sec.state.ma.us/divisions/elections/research-and-statistics/voter-turnout-statistics.htm',methods='https://www.sec.state.ma.us/divisions/elections/research-and-statistics/early-voting-statistics.htm',observation_file='data/turnout/source/browser-statistics-observation.txt',original_http_status=403,qualification='Browser-extracted primary text only; full original statistics entities unavailable after retained direct/alternate-route attempts. No reconstructed XLSX/PDF, inferred municipal allocation, rounded-percentage integer conversion or discrepancy repair.')))
    (D/'statistics-controls.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Parsed 3 separate statewide registration/turnout/method controls; local cells remain unavailable.')
if __name__=='__main__':main()
