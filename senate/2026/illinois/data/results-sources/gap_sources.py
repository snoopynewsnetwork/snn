from common import *
from deep_public import run_plan
# Exact official search discoveries; the blank state-directory website fields remain blank.
seeds=[('31','https://greenecountyil.org/county-clerk/elections/'),('40','https://jaspercountyillinois.gov/county-clerk-recorder/elections/election-results/'),('80','https://richlandcounty.illinois.gov/county-clerk-recorder/elections/'),('82','https://salinecounty.illinois.gov/county-clerk-recorder/elections-voting/')]
run_plan([dict(id=f'authority-{aid}-search-official',url=u,parent='directory-detail-'+aid,literal_href=None,basis='bounded primary official web search discovery; independently requested public county publisher; state directory href remains literally blank') for aid,u in seeds],'gap-official')
