"""Acquire additional observed primary publications; preserve originals/references."""
from acquire import *
import re, urllib.parse

news={r['id']:r for r in json.loads((DATA/'news/manifest.json').read_text())}
for sid in ['nara-2024-SC-ascertainment','fec-2024-presidential-original']:
    r=news[sid];capture(sid,r['url'],'primary certificate/publication named in coordinator primary-vintage-disagreement.json',shared=DATA/'news'/r['asset'])
for year,shared in [(2020,DATA.parent.parent/'michigan/data/baselines/house-statistics2020.pdf'),
                    (2022,DATA.parent.parent/'ohio/data/baselines/raw/house-2022.pdf'),
                    (2024,DATA.parent.parent/'ohio/data/baselines/raw/house-2024.pdf')]:
    capture('house-'+str(year),f'https://clerk.house.gov/member_info/electionInfo/{year}/statistics{year}.pdf',
            'House Clerk official election statistics; independent check of complete SC candidate vector',shared=shared)

# Selecting an election in a public read-only search form, not a data mutation.
s=requests.Session()
m=capture('candidate-session-select','https://vrems.scvotes.sc.gov/Candidate/SelectElection','candidate-select public search form',session=s)
if not (SRC/'candidate-general-search.meta.json').exists():
    # Fetch a fresh token/cookie pair when resuming an interrupted acquisition.
    if not s.cookies:
        s.get(m['requested_url'],timeout=40)
        # Session initial form must correspond to the retained request token.
        # Existing capture is immutable; keep this additional original separately.
        m=capture('candidate-session-refresh',m['requested_url'],'candidate-session-select fresh CSRF read form',session=s)
    t=gzip.decompress((SRC/m['body_path']).read_bytes()).decode()
    token=re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"',t).group(1)
    body=urllib.parse.urlencode({'ElectionKindSid':'General','ElectionYear':'2026','ElectionID':'22596','__RequestVerificationToken':token}).encode()
    capture('candidate-general-search',m['requested_url'],'candidate-select form, general election22596 from candidate-elections-2026 (no primary carryover)',
            request=body,session=s,content_type='application/x-www-form-urlencoded')
