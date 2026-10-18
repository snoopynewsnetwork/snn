"""Download pinned county originals only from observed state county/version roster.

State settings `participatingcounties` contains county|EID|version|clock|template.
Web02 appcomponents getCountyInfo constructs ../../county/EID/version/json/;
its report widget constructs ../VID/reports/detailxml.zip. The 2024 app's
getReportUri constructs the identical county data root. No IDs are guessed.
"""
from acquire import *
from extract import loadbody
import ast,urllib.parse
for year in [2024,2020,2022]:
    j=json.loads(loadbody(SRC/f'legacy{year}-electionsettings.meta.json')[0])
    value=j['settings']['electiondetails']['participatingcounties']
    roster=value if isinstance(value,list) else ast.literal_eval(value)
    assert len(roster)==46
    for pos,value in enumerate(roster):
        county,eid,version,clock,template=value.split('|')
        url=f'https://www.enr-scvotes.org/SC/{urllib.parse.quote(county)}/{eid}/{version}/reports/detailxml.zip'
        capture(f'legacy{year}-county-'+county.lower(),url,
                f'legacy{year}-electionsettings /settings/electiondetails/participatingcounties ordinal{pos} raw{value}; observed getCountyInfo/getReportUri and reportsWidget filename')
        for filename in ['details.json','en/summary.json']:
            capture(f'legacy{year}-county-'+county.lower()+'-'+filename.split('/')[-1].split('.')[0],
                    f'https://www.enr-scvotes.org/SC/{urllib.parse.quote(county)}/{eid}/{version}/json/{filename}',
                    f'legacy{year}-electionsettings participatingcounties ordinal{pos} raw{value}; Web02getCountyPrecinctDetails/getCountyContests/getSummary and 2024getUri enum Details/Summary; English confirmed by state config')
