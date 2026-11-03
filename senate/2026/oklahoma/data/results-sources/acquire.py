#!/usr/bin/env python3
"""Acquire public evidence for the Oklahoma official-results channel inventory.

Writes only inside this directory: raw/ (original response bytes; text types
gzip-compressed with mtime 0, PDFs stored as downloaded), source-manifest.json
(one record per request: URL, redirect chain, HTTP status, selected headers,
UTC retrieval time, original and stored SHA-256/byte counts, parent, channel
and note) and oker-bundle-endpoints.json (a derived inventory; see below).

Access rule (research-owner decision): public pages only. This script performs
no sign-in, sends no credentials or tokens, completes no guestbook or gated
flow and never calls the OK Election Results (OKER) application's API
(/OKERS/enrapi/...). The OKER single-page app shell, its static
assets/config.json and its public JavaScript bundle are fetched like any
browser would fetch them. The bundle is NOT stored: it embeds the app's own
anonymous sign-in credential. Only its SHA-256, byte count and a derived list
of API route names (with whether each call attaches a bearer token) are kept.
No credential value is read, printed or written.

Channels:
  * State Election Board (SEB) pages on oklahoma.gov, the SEB-linked static
    November 2026 election list and early-voting list on hosting.okelections,
    the SEB county election board directory (OK Voter Portal /cebinfo) and
    PDFs linked from SEB pages.
  * SEB Interactive Statistics (EIS) absentee dashboard: the public
    DevExpress item-data endpoint the page itself calls, with an explicit
    Election Date filter (no sign-in exists on this site).
  * OSCN statute text (Title 26 and 51 O.S. 10), the official state courts
    network publication.
  * Internet Archive Wayback Machine: CDX listings and archived copies of
    public SEB result pages (third-party archive; labeled as such).
  * County discovery: the KellPro OKCounties county list (a vendor directory,
    not an election authority) and every listed county home page; then the
    county election board pages found from those home pages for the 26
    priority counties, plus a small number of bounded PDFs they link.

Run from the repository root:
  PYTHONDONTWRITEBYTECODE=1 uv run --with truststore==0.10.0 python3 -I senate/2026/oklahoma/data/results-sources/acquire.py
  PYTHONDONTWRITEBYTECODE=1 uv run python3 -I senate/2026/oklahoma/data/results-sources/acquire.py --verify
truststore makes certificate verification use the operating-system store; without
it, hosts with incomplete chains (www.ok.gov, oklegislature.gov) fail verification.
Verification is never disabled.
  ... acquire.py --refetch statute-,wb-   # refetch only ids with these prefixes; reuse the rest
OSCN (Cloudflare Turnstile) and the Wayback Machine throttle bursts: requests to
them are spaced and retried after pauses. A challenge page is never solved; if
it persists the record is kept and labeled as a challenge, not as source text.
A fresh run overwrites raw/ files and rewrites the manifest; rebuild afterwards.
"""
import csv
import gzip
import hashlib
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:  # verify TLS against the operating-system trust store when available (some state hosts send incomplete chains)
    import truststore
    truststore.inject_into_ssl()
    TLS_TRUST = 'operating-system trust store (truststore)'
except ImportError:
    TLS_TRUST = 'Python default trust store'

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'raw'
MANIFEST = ROOT / 'source-manifest.json'
BUNDLE_OUT = ROOT / 'oker-bundle-endpoints.json'
UA = 'Mozilla/5.0 (compatible; election-research/1.0)'
CAP = 8_000_000
KEEP_HEADERS = ['content-type', 'content-length', 'last-modified', 'etag', 'date', 'server', 'x-cache', 'age',
                'cache-control', 'x-amz-meta-s3b-last-modified', 'x-amz-version-id', 'content-encoding',
                'x-archive-orig-last-modified', 'x-archive-orig-date', 'memento-datetime', 'location']

SEB = 'https://oklahoma.gov/elections'
RES = SEB + '/elections-results/election-results'
OSCN = 'https://www.oscn.net/applications/oscn/DeliverDocument.asp?CiteID='
WB = 'https://web.archive.org'
EIS = 'https://stats.okelections.gov'

# id, url, kind, parent, channel, note
STATE = [
    ('seb-home', 'http://elections.ok.gov/', 'html', None, 'seb', 'Legacy SEB domain linked by several county pages; redirect chain retained.'),
    ('seb-results-index', RES + '.html', 'html', None, 'seb', 'SEB election results index (years 1907-2026).'),
    ('seb-results-2026', RES + '/2026-election-results.html', 'html', 'seb-results-index', 'seb', '2026 results list; November 3 row checked for a link.'),
    ('seb-results-2026-june', RES + '/2026-election-results/june-primary-election.html', 'html', 'seb-results-2026', 'seb', 'June 16, 2026 primary page linking OKER elecDate=20260616.'),
    ('seb-results-2026-august', RES + '/2026-election-results/august-runoff-primary-election.html', 'html', 'seb-results-2026', 'seb', 'August 25, 2026 runoff page linking OKER elecDate=20260825.'),
    ('seb-results-2024', RES + '/2024-election-results.html', 'html', 'seb-results-index', 'seb', '2024 results list (historical precedent for when a general-election row gains its link).'),
    ('seb-results-2024-november', RES + '/2024-election-results/november-general-election.html', 'html', 'seb-results-2024', 'seb', 'November 5, 2024 general page (now OFFICIAL RESULTS).'),
    ('seb-next-election', SEB + '/elections-results/next-election.html', 'html', None, 'seb', 'Next Election page: links the November 3 list of elections; poll hours.'),
    ('seb-election-list-nov2026', 'http://hosting.okelections.us/electionlist.html', 'html', 'seb-next-election', 'seb', 'NOVEMBER / 2026 List of Elections, all 77 counties (exact href printed on the Next Election page).'),
    ('seb-early-voting-page', SEB + '/voters/early-voting.html', 'html', 'seb-next-election', 'seb', 'Early voting rules; links the early-voting location list.'),
    ('seb-earlyvote-nov2026', 'https://hosting.okelections.us/earlyvote.html', 'html', 'seb-early-voting-page', 'seb', 'November 3 Election - Early Voting Locations, all counties.'),
    ('seb-dates-deadlines', SEB + '/elections-results/dates-and-deadlines.html', 'html', None, 'seb', 'Poll hours and calendar links.'),
    ('seb-voter-info-calendar-2026', SEB + '/elections-results/next-election/voter-information-calendar.html', 'html', 'seb-dates-deadlines', 'seb', '2026 calendar: Nov 3 registration/absentee deadlines, early voting days.'),
    ('seb-straight-party', SEB + '/elections-results/straight-party-voting.html', 'html', None, 'seb', 'Straight-party option semantics (R/D/L; none for Independents).'),
    ('seb-county-election-boards', SEB + '/about-us/county-election-boards.html', 'html', None, 'seb', 'SEB page linking the county election board contact directory.'),
    ('seb-cebinfo', 'https://okvoterportal.okelections.gov/cebinfo', 'html', 'seb-county-election-boards', 'seb', 'County Election Board Information table: all 77 boards (code, phone, secretary, address, email).'),
    ('seb-ceb-addresses-pdf', 'https://oklahoma.gov/content/dam/ok/en/elections/ceb-physical-addresses/ceb-physical-addresses.pdf', 'pdf', None, 'seb', 'SEB PDF of county election board information (ut2300 report).'),
    ('seb-uocava-2026-general', SEB + '/voters/military-overseas-voters/2026-election-notice-general-election.html', 'html', None, 'seb', 'UOCAVA notice: offices on the November 3, 2026 ballot.'),
    ('seb-voting-devices', SEB + '/security-integrity/voting-devices.html', 'html', None, 'seb', 'eScan A/T; results media; SEB-owned network to county boards.'),
    ('seb-election-security', SEB + '/security-integrity/election-security.html', 'html', None, 'seb', 'Uniform system; canvass/certification; recount petition deadline.'),
    ('seb-ballot-status', SEB + '/voters/ballot-status.html', 'html', None, 'seb', 'When ballots are counted; absentee/provisional handling.'),
    ('seb-absentee-voting', SEB + '/voters/absentee-voting.html', 'html', None, 'seb', 'Absentee receipt deadline 7 p.m. election day.'),
    ('seb-newsroom', SEB + '/newsroom.html', 'html', None, 'seb-news', 'Newsroom index (listing is script-rendered; the static HTML carries no release list).'),
    ('seb-news-2026-06-12-tips', SEB + '/newsroom/2026/june/state-election-board-offers-tips-and-reminders-ahead-of-june-16-.html', 'html', None, 'seb-news', 'Release: results after 7 p.m.; auto-refresh recommended.'),
    ('seb-news-2026-07-08-ballot-order', SEB + '/newsroom/2026/june/republican-party-to-receive-top-position-on-the-general-election.html', 'html', None, 'seb-news', 'Release: November party order R, D, L; Independents in lot order.'),
    ('seb-news-2026-07-17-security', SEB + '/newsroom/2026/july/state-election-board-secretary-highlights-oklahoma-s-robust-elec.html', 'html', None, 'seb-news', 'Release: devices not networked; county canvass of printed totals.'),
    ('seb-news-2026-10-07-deadlines', SEB + '/newsroom/2026/october/deadlines-approaching-for-november-3-general-election.html', 'html', None, 'seb-news', 'Release: Nov 3 registration and absentee-request deadlines.'),
    ('seb-news-2026-10-13-statement', SEB + '/newsroom/2026/october/statement-from-secretary-of-the-state-election-board.html', 'html', None, 'seb-news', 'Release: Oct 13 evacuation; Secretary says no impact on conducting elections.'),
    ('seb-meetings-2026', SEB + '/about-us/meeting-notices-agendas-and-minutes.html', 'html', None, 'seb-certification', '2026 SEB meetings, including Nov 10, 2026 (agenda TBA).'),
    ('seb-minutes-2026-06-23', 'https://oklahoma.gov/content/dam/ok/en/elections/minutes/2026-minutes/minutes-06232026.pdf', 'pdf', 'seb-meetings-2026', 'seb-certification', 'Scanned minutes of June 23, 2026 certification meeting (image-only PDF).'),
    ('seb-meetings-2024', SEB + '/about-us/meeting-notices-agendas-and-minutes-archives/2024-agendas-and-minutes.html', 'html', None, 'seb-certification', '2024 SEB meetings incl. Nov 12, 2024 (Tuesday after the general).'),
    ('oker-shell-20261103', 'https://results.okelections.us/OKER/?elecDate=20261103', 'html', None, 'oker', 'OKER app shell for 2026-11-03; static shell, identical for every elecDate.'),
    ('oker-shell-20260825', 'https://results.okelections.us/OKER/?elecDate=20260825', 'html', 'seb-results-2026-august', 'oker', 'OKER app shell for the exact runoff link printed on the SEB page.'),
    ('oker-static-config', 'https://results.okelections.gov/OKER/assets/config.json', 'json', 'oker-shell-20261103', 'oker', 'Static public app configuration (API base URLs).'),
    ('eis-home', 'https://stats.okelections.gov/', 'html', None, 'eis', 'SEB Interactive Statistics home (dashboard list).'),
    ('eis-page-AbsByCounty', EIS + '/Home/AbsByCounty', 'html', 'eis-home', 'eis', 'Absentee Statistics By County page (initialDashboardId AbsStatsByCounty).'),
    ('eis-dashboard-AbsStatsByCounty', EIS + '/dashboardControl/dashboards/AbsStatsByCounty', 'json', 'eis-page-AbsByCounty', 'eis', 'DevExpress dashboard definition.'),
    ('statute-26-7-104', OSCN + '78544', 'html', None, 'statute', '26 O.S. 7-104 polling hours 7 a.m.-7 p.m.'),
    ('statute-26-7-116.1', OSCN + '441134', 'html', None, 'statute', '26 O.S. 7-116.1 provisional ballots; no information before 1 p.m. Friday.'),
    ('statute-26-7-136', OSCN + '78592', 'html', None, 'statute', '26 O.S. 7-136 canvass: county Friday 5 p.m., SEB Tuesday 5 p.m.'),
    ('statute-26-12-101', OSCN + '78668', 'html', None, 'statute', '26 O.S. 12-101 U.S. Senate vacancy; no special election when full term already scheduled.'),
    ('statute-26-12-105', OSCN + '78672', 'html', None, 'statute', '26 O.S. 12-105 special-election winner serves unexpired term.'),
    ('statute-26-14-104', OSCN + '78712', 'html', None, 'statute', '26 O.S. 14-104 absentee return by 7 p.m. election day.'),
    ('statute-26-14-123', OSCN + '78741', 'html', None, 'statute', '26 O.S. 14-123 outer envelopes removed from Thursday before.'),
    ('statute-26-14-125', OSCN + '78743', 'html', None, 'statute', '26 O.S. 14-125 absentee counting; no results before 7 p.m.'),
    ('statute-51-10', OSCN + '80268', 'html', None, 'statute', '51 O.S. 10(C) Governor appoints U.S. Senate replacement until successor elected.'),
    ('statute-26-14-115.4', OSCN + '439351', 'html', None, 'statute', '26 O.S. 14-115.4 in-person absentee (early) media sealed until county count.'),
    ('statute-os26-legislature', 'https://oklegislature.gov/OK_Statutes/CompleteTitles/os26.pdf', 'pdf', None, 'statute', 'Oklahoma Legislature compiled Title 26 (official compilation PDF); cross-check of the OSCN sections.'),
    ('statute-os51-legislature', 'https://oklegislature.gov/OK_Statutes/CompleteTitles/os51.pdf', 'pdf', None, 'statute', 'Oklahoma Legislature compiled Title 51 (official compilation PDF); cross-check of 51 O.S. 10.'),
]

EIS_ITEMS = [
    ('eis-abs-election-dates', 'comboBoxDashboardItem2', None, 'Election Date combo values.'),
    ('eis-abs-20261103-pivot', 'pivotDashboardItem1', '2026-11-03', 'County pivot: Total/Sent/Received/Rejected for the Nov 3, 2026 election.'),
    ('eis-abs-20261103-card-sent', 'cardDashboardItem3', '2026-11-03', 'Statewide Sent card.'),
    ('eis-abs-20261103-card-received', 'cardDashboardItem5', '2026-11-03', 'Statewide Received card.'),
    ('eis-abs-20261103-card-rejected', 'cardDashboardItem4', '2026-11-03', 'Statewide Rejected card.'),
    ('eis-abs-20261103-ballot-types', 'pieDashboardItem1', '2026-11-03', 'Ballot type pie.'),
    ('eis-abs-20261103-app-sources', 'pieDashboardItem2', '2026-11-03', 'Application source pie.'),
    ('eis-abs-20241105-pivot', 'pivotDashboardItem1', '2024-11-05', 'County pivot for the Nov 5, 2024 general (historical comparator).'),
]

WAYBACK = [
    ('wb-cdx-oker-enrapi', WB + '/cdx/search/cdx?url=results.okelections.gov/OKERS/enrapi/&matchType=prefix&output=json&fl=timestamp,original,statuscode,mimetype,length,digest&limit=2000', 'json',
     'CDX listing of archived OKER API URLs (metadata only; no archived API body is fetched here).'),
    ('wb-cdx-seb-2024-november', WB + '/cdx/search/cdx?url=oklahoma.gov/elections/elections-results/election-results/2024-election-results/november-general-election.html&output=json&fl=timestamp,statuscode,length,digest&limit=200', 'json',
     'CDX listing of archived copies of the SEB 2024 general results page.'),
    ('wb-cdx-seb-2026-august', WB + '/cdx/search/cdx?url=oklahoma.gov/elections/elections-results/election-results/2026-election-results/august-runoff-primary-election.html&output=json&fl=timestamp,statuscode,length,digest&limit=200', 'json',
     'CDX listing of archived copies of the SEB 2026 runoff results page.'),
    ('wb-cdx-seb-2026-june', WB + '/cdx/search/cdx?url=oklahoma.gov/elections/elections-results/election-results/2026-election-results/june-primary-election.html&output=json&fl=timestamp,statuscode,length,digest&limit=200', 'json',
     'CDX listing for the SEB 2026 primary results page.'),
]
WB_PAGES = [
    ('wb-seb-2024-november-20241105223112', '20241105223112', 'seb-results-2024-november', 'Election day 16:31 CST, before polls closed.'),
    ('wb-seb-2024-november-20241106020407', '20241106020407', 'seb-results-2024-november', 'Election night 20:04 CST.'),
    ('wb-seb-2024-november-20241108164759', '20241108164759', 'seb-results-2024-november', 'Friday after election 10:47 CST.'),
    ('wb-seb-2026-august-20260827122028', '20260827122028', 'seb-results-2026-august', 'Thursday after the runoff (unofficial phase).'),
    ('wb-seb-2026-august-20260910093956', '20260910093956', 'seb-results-2026-august', 'After the September 1 certification.'),
]
WB_TARGET = {'seb-results-2024-november': RES + '/2024-election-results/november-general-election.html',
             'seb-results-2026-august': RES + '/2026-election-results/august-runoff-primary-election.html'}

OKCOUNTIES = 'https://okcounties.org/countyData.json'

# Priority-county pages found by following links from each county home page
# (or, where stated, from a page that itself links it). fips -> [(id, url, kind, parent, note)]
PRIORITY_PAGES = {
    '40109': [('cty-40109-board', 'https://www.oklahomacounty.org/Departments/Election-Board', 'html', 'home-40109', 'Oklahoma County Election Board page (linked from county home).'),
              ('cty-40109-sample-ballots-notice', 'https://www.oklahomacounty.org/Portals/0/DNNGalleryPro/uploads/2026/9/29/SampleBallotsAvailablefor11-03-2026GeneralElection.pdf', 'pdf', 'cty-40109-board', 'Board press release 2026-09-29: sample ballots via OK Voter Portal.'),
              ('cty-40109-absentee-notice', 'https://www.oklahomacounty.org/Portals/0/DNNGalleryPro/uploads/2026/9/18/AbsenteeBallotInformationfor11-03-2026GeneralElection.pdf', 'pdf', 'cty-40109-board', 'Board press release 2026-09-18: absentee request deadline.')],
    '40143': [('cty-40143-www2', 'https://www2.tulsacounty.org/', 'html', 'home-40143', 'Target of the JavaScript redirect on www.tulsacounty.org.'),
              ('cty-40143-board', 'https://www2.tulsacounty.org/electionboard/', 'html', 'cty-40143-www2', 'Tulsa County Election Board home.'),
              ('cty-40143-results', 'https://www2.tulsacounty.org/electionboard/elections/election-results/', 'html', 'cty-40143-board', 'Board Election Results page (links SEB result pages).'),
              ('cty-40143-next-election', 'https://www2.tulsacounty.org/electionboard/elections/next-election/', 'html', 'cty-40143-board', 'Board Next Election page.'),
              ('cty-40143-absentee', 'https://www2.tulsacounty.org/electionboard/voting/absentee-voting/', 'html', 'cty-40143-board', 'Board absentee/early-voting page.')],
    '40027': [('cty-40027-county-board', 'https://www.clevelandcountyok.com/171/County-Election-Board', 'html', 'home-40027', 'County site Election Board page.'),
              ('cty-40027-board', 'https://www.clevelandcountyelectionboard.com/', 'html', 'cty-40027-county-board', 'Cleveland County Election Board site.'),
              ('cty-40027-results', 'https://www.clevelandcountyelectionboard.com/elections-results', 'html', 'cty-40027-board', 'Board Elections & Results list.'),
              ('cty-40027-results-2024-general', 'https://www.clevelandcountyelectionboard.com/election-results/general-election-november-5-2024', 'html', 'cty-40027-results', 'Board page for the 2024 general.'),
              ('cty-40027-certificate-2024-general', 'https://www.clevelandcountyelectionboard.com/sites/default/files/Official%20Certificate%20of%20Votes%2011-5-2024.pdf', 'pdf', 'cty-40027-results-2024-general', 'County Official Certificate of Votes, Nov 5, 2024 (precinct x candidate).'),
              ('cty-40027-results-2026-runoff', 'https://www.clevelandcountyelectionboard.com/election-results/runoff-primary-august-25-2026', 'html', 'cty-40027-results', 'Board page for the Aug 25, 2026 runoff.'),
              ('cty-40027-certificate-2026-runoff', 'https://www.clevelandcountyelectionboard.com/sites/default/files/2026-08/Official_Certificate_of_Votes_8-25-26.pdf', 'pdf', 'cty-40027-results-2026-runoff', 'County Official Certificate of Votes, Aug 25, 2026 (includes U.S. Senator Democratic runoff).'),
              ('cty-40027-sample-ballots-nov2026', 'https://www.clevelandcountyelectionboard.com/sample-ballots-november-3-2026-general-election', 'html', 'cty-40027-board', 'Precinct sample ballot list, Nov 3, 2026.'),
              ('cty-40027-sample-ballot-140100', 'https://www.clevelandcountyelectionboard.com/sites/default/files/2026-10/20261103_140100_REGNP_NON_FSC.pdf', 'pdf', 'cty-40027-sample-ballots-nov2026', 'One bounded sample: precinct 140100 general ballot.')],
    '40017': [('cty-40017-directory', 'https://www.canadiancounty.org/directory.aspx', 'html', 'home-40017', 'County staff directory (lists Election Board).'),
              ('cty-40017-board', 'https://www.canadiancounty.org/930/Election-Board', 'html', 'cty-40017-directory', 'County site Election Board page.')],
    '40131': [('cty-40131-offices', 'https://www.rogerscounty.org/180/Offices', 'html', 'home-40131', 'County Offices page linking the board site.'),
              ('cty-40131-board', 'https://rogerscountyelectionboard.org/', 'html', 'cty-40131-offices', 'Rogers County Election Board site.'),
              ('cty-40131-results', 'https://rogerscountyelectionboard.org/election-results/', 'html', 'cty-40131-board', 'Board Election Results page (links an OKER election).')],
    '40145': [('cty-40145-board', 'https://www.wagonercounty.ok.gov/335/Election-Board', 'html', 'home-40145', 'County site Election Board page.'),
              ('cty-40145-dates', 'https://www.wagonercounty.ok.gov/338/Election-Dates-Early-Voting-Information', 'html', 'cty-40145-board', 'Election dates and early-voting sites.')],
    '40031': [('cty-40031-board', 'https://www.comanchecountyok.gov/m/directory/department?did=24', 'html', 'home-40031', 'County directory entry for the Election Board.')],
    '40037': [('cty-40037-board', 'https://www.creekcountyonline.com/election-board', 'html', 'home-40037', 'County site Election Board page.'),
              ('cty-40037-results', 'https://www.creekcountyonline.com/upages.php?id=691', 'html', 'cty-40037-board', '"Oklahoma Election Results" page (links SEB).')],
    '40119': [('cty-40119-board', 'https://votepaynecounty.com', 'html', 'home-40119', 'Payne County Election Board site (linked from county home).')],
    '40125': [('cty-40125-board', 'https://www.pottawatomiecountyok.gov/160/County-Election-Board', 'html', 'home-40125', 'County site Election Board page.')],
    '40051': [('cty-40051-board', 'https://www.gradycountyok.com/m/directory/department?did=25', 'html', 'home-40051', 'County directory entry for the Election Board.')],
    '40101': [('cty-40101-board', 'https://muskogee.okcounties.org/departments/election-board', 'html', 'home-40101', 'OKCounties-hosted Election Board page.')],
    '40083': [('cty-40083-board', 'https://www.logancountyok.com/168/Election-Board', 'html', 'home-40083', 'County site Election Board page ("Election Night Reporting" link).')],
    '40147': [('cty-40147-board', 'https://washingtoncountyok.gov/election-board', 'html', 'home-40147', 'County site Election Board page.')],
    '40047': [],
    '40087': [('cty-40087-board', 'https://mcclain-co-ok.us/offices/county-election-board/', 'html', 'home-40087', 'Board page named by a web-rendered read of the county home page (raw home returned 403).')],
    '40113': [('cty-40113-board', 'https://osage.okcounties.org/departments/election-board', 'html', 'home-40113', 'OKCounties-hosted Election Board page.')],
    '40019': [('cty-40019-county-boards', 'https://cartercountyok.us/government/county_boards/index.php', 'html', 'home-40019', 'County Boards page; its "Election Board" menu item links the legacy SEB host.'),
              ('cty-40019-board-link', 'https://www.ok.gov/elections/', 'html', 'cty-40019-county-boards', 'Target of the Carter "Election Board" link (legacy SEB host).')],
    '40079': [],
    '40137': [],
    '40041': [('cty-40041-board', 'https://delaware.okcounties.org/departments/election-board', 'html', 'home-40041', 'OKCounties-hosted Election Board page.')],
    '40021': [('cty-40021-board', 'https://cherokee.okcounties.org/departments/election-board', 'html', 'home-40021', 'OKCounties-hosted Election Board page.')],
    '40013': [('cty-40013-board', 'https://bryan.okcounties.org/departments/election-board', 'html', 'home-40013', 'OKCounties-hosted Election Board page.')],
    '40121': [('cty-40121-board', 'https://pittsburg.okcounties.org/departments/election-board', 'html', 'home-40121', 'OKCounties-hosted Election Board page.')],
    '40097': [('cty-40097-board', 'https://mayes.okcounties.org/departments/election-board', 'html', 'home-40097', 'OKCounties-hosted Election Board page.')],
    '40071': [('cty-40071-board', 'https://www.courthouse.kay.ok.us/180/Election-Board', 'html', 'home-40071', 'County site Election Board page.')],
}

rows = []


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Redirects(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.chain = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append({'status': code, 'from': req.full_url, 'location': newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def http(url, headers=None):
    h = {'User-Agent': UA, 'Accept': '*/*'}
    h.update(headers or {})
    red = Redirects()
    opener = urllib.request.build_opener(red)
    meta = {'url': url, 'request_headers': h, 'retrieval_utc': now(), 'tls_trust': TLS_TRUST}
    body, status, final, hdrs, err = b'', None, url, {}, None
    try:
        with opener.open(urllib.request.Request(url, headers=h), timeout=45) as r:
            status, final = r.status, r.geturl()
            hdrs = {k.lower(): v for k, v in r.headers.items()}
            body = r.read(CAP + 1)
    except urllib.error.HTTPError as e:
        status, hdrs = e.code, {k.lower(): v for k, v in e.headers.items()}
        try:
            body = e.read(CAP + 1)
        except Exception:
            body = b''
    except Exception as e:  # transport errors are evidence, not silent gaps
        err = f'{type(e).__name__}: {e}'[:300]
    meta.update({'completed_utc': now(), 'status': status, 'final_url': final, 'redirects': red.chain, 'error': err,
                 'response_headers': {k: v for k, v in hdrs.items() if k in KEEP_HEADERS},
                 'truncated': len(body) > CAP})
    body = body[:CAP]
    if hdrs.get('content-encoding') == 'gzip' and body[:2] == b'\x1f\x8b':
        meta['wire_gzip_sha256'] = sha(body)
        body = gzip.decompress(body)
    return meta, body


def store(key, kind, meta, body, parent=None, channel=None, note=None, keep=True):
    rec = {'id': key, 'kind': kind, 'parent': parent, 'channel': channel, 'note': note}
    rec.update(meta)
    rec['original_sha256'] = sha(body)
    rec['original_bytes'] = len(body)
    if not keep or not body:
        rec['path'] = None
        rec['storage'] = 'not retained' if body else 'empty body'
    else:
        if kind == 'pdf':
            path = RAW / f'{key}.pdf'
            path.write_bytes(body)
            rec['storage'] = 'original bytes'
        else:
            path = RAW / f'{key}.{kind}.gz'
            path.write_bytes(gzip.compress(body, mtime=0))
            rec['storage'] = 'gzip (mtime=0) of original entity bytes'
        stored = path.read_bytes()
        rec['path'] = path.relative_to(ROOT).as_posix()
        rec['stored_sha256'] = sha(stored)
        rec['stored_bytes'] = len(stored)
    rows.append(rec)
    print(f"{rec['status']} {key} {len(body)} {meta.get('error') or ''}", flush=True)
    return body


OLD = {}
REFETCH = None  # None = fetch everything; else tuple of id prefixes to refetch, others reused from the manifest
CHALLENGE = b'OSCN Turnstile'


def reuse(key):
    r = OLD[key]
    rows.append(r)
    print(f"REUSE {r['status']} {key}", flush=True)
    if not r.get('path'):
        return b''
    b = (ROOT / r['path']).read_bytes()
    return gzip.decompress(b) if r['path'].endswith('.gz') else b


def acceptable(url, meta, body):
    if 'oscn.net' in url:
        return meta['status'] == 200 and CHALLENGE not in body and b'Cite as' in body
    if 'web.archive.org' in url:
        return meta['status'] == 200
    return True


def fetch(key, url, kind, parent=None, channel=None, note=None, headers=None):
    if REFETCH is not None and not key.startswith(REFETCH) and key in OLD:
        return reuse(key)
    if REFETCH is not None and key in OLD and OLD[key].get('path'):
        (ROOT / OLD[key]['path']).unlink(missing_ok=True)
    attempts = []
    for wait in (0, 30, 90, 180):
        if wait:
            time.sleep(wait)
        if 'oscn.net' in url or 'web.archive.org' in url:
            time.sleep(6)
        meta, body = http(url, headers)
        if acceptable(url, meta, body):
            break
        attempts.append({'retrieval_utc': meta['retrieval_utc'], 'status': meta['status'], 'bytes': len(body),
                         'challenge_page': CHALLENGE in body, 'note': 'rejected attempt (rate limit or challenge page); not solved, retried after a pause'})
    if attempts:
        meta['rejected_attempts'] = attempts
    if not acceptable(url, meta, body):
        note = (note or '') + ' FINAL RESPONSE IS A CHALLENGE/ERROR PAGE, NOT THE SOURCE TEXT.'
    return store(key, kind, meta, body, parent, channel, note)


def oker_bundle():
    """Fetch the public bundle, derive route names; never store or print credentials."""
    if REFETCH is not None and not 'oker-main-bundle'.startswith(REFETCH) and 'oker-main-bundle' in OLD:
        reuse('oker-main-bundle')
        return
    shell = gzip.decompress((RAW / 'oker-shell-20261103.html.gz').read_bytes()).decode('utf-8', 'replace')
    m = re.search(r'src="(main\.[0-9a-f]+\.bundle\.js)"', shell)
    url = 'https://results.okelections.gov/OKER/' + m.group(1)
    meta, body = http(url)
    store('oker-main-bundle', 'js', meta, body, 'oker-shell-20261103', 'oker',
          'Public app bundle; bytes not retained because the bundle embeds the app sign-in credential. Derived route list only.', keep=False)
    js = body.decode('utf-8', 'replace')
    routes = {}
    for mm in re.finditer(r'enrapi/([A-Za-z]+)/', js):
        name = mm.group(1)
        ctx = js[max(0, mm.start() - 700):mm.end() + 300]
        r = routes.setdefault(name, {'occurrences': 0, 'bearer_header_in_context': False, 'authenticated_flag_checked_in_context': False})
        r['occurrences'] += 1
        r['bearer_header_in_context'] |= 'Bearer ' in ctx
        r['authenticated_flag_checked_in_context'] |= 'authenticated' in ctx
    login_put = bool(re.search(r'http\.put\([a-z],\{Username:', js))
    out = {
        'bundle_url': url, 'bundle_sha256': sha(body), 'bundle_bytes': len(body), 'retrieval_utc': meta['retrieval_utc'],
        'stored': False,
        'why_not_stored': 'The bundle embeds the anonymous app sign-in credential; by research-owner decision it is neither stored nor used.',
        'routes': routes,
        'sign_in_route_present': 'login' in routes, 'sign_in_uses_http_put_with_username_password_object': login_put,
        'polling_interval_source': 'repository.getInterval() returns apiConfig.pollingInterval from the getconfig API response (sign-in-gated).',
        'note': 'Every data route is called with an Authorization: Bearer header after the app sign-in. None was called by this research.',
    }
    BUNDLE_OUT.write_text(json.dumps(out, indent=1) + '\n')


def eis():
    for key, item, date, note in EIS_ITEMS:
        if REFETCH is not None and not key.startswith(REFETCH) and key in OLD:
            reuse(key)
            continue
        q = {'dashboardId': 'AbsStatsByCounty', 'itemId': item}
        if date:
            f = {'dimensions': [{'@DataMember': 'ElectionDate', '@DefaultId': 'DataItem0', '@ItemType': 'Dimension', '@DateTimeGroupInterval': 'DayMonthYear'}],
                 'values': [[date + 'T00:00:00.000']]}
            q['query'] = json.dumps({'Filter': [f]}, separators=(',', ':'))
        url = EIS + '/dashboardControl/data/DashboardItemGetAction?' + urllib.parse.urlencode(q)
        meta, body = http(url, {'Accept': 'application/json'})
        meta['params'] = q
        store(key, 'json', meta, body, 'eis-dashboard-AbsStatsByCounty', 'eis', note)


def wayback():
    for key, url, kind, note in WAYBACK:
        fetch(key, url, kind, None, 'wayback-third-party', note)
        time.sleep(1.5)
    for key, ts, target, note in WB_PAGES:
        fetch(key, f'{WB}/web/{ts}id_/{WB_TARGET[target]}', 'html', target, 'wayback-third-party',
              f'Internet Archive copy of {WB_TARGET[target]} captured {ts} UTC. {note}')
        time.sleep(1.5)


def links(base, body):
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', body.decode('utf-8', 'replace'), flags=re.S | re.I)
    out = []
    for m in re.finditer(r'<a\b[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>', t, re.S | re.I):
        txt = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', m.group(2)))).strip()
        out.append([urllib.parse.urljoin(base, html.unescape(m.group(1).strip())), txt[:100]])
    return out


def counties():
    data = json.loads(fetch('okcounties-countydata', OKCOUNTIES, 'json', None, 'county-discovery',
                            'KellPro OKCounties county list (vendor directory of county home pages; not an election authority).'))
    with open(ROOT.parent / 'county-turnout.csv', newline='') as fh:
        turn = {r['oker_county_label'].replace(' ', '').lower(): r for r in csv.DictReader(fh)}
    for c in data:
        key = c['name'].replace(' ', '').lower()
        fips = turn[key]['county_fips']
        if not str(c.get('link', '')).startswith('http'):
            continue
        fetch(f'home-{fips}', c['link'], 'html', 'okcounties-countydata', 'county-discovery', f"{c['name']} County home page as listed by OKCounties.")
    for fips, pages in PRIORITY_PAGES.items():
        for key, url, kind, parent, note in pages:
            fetch(key, url, kind, parent, 'county-priority', note)


def verify():
    bad = 0
    for r in json.loads(MANIFEST.read_text()):
        if not r.get('path'):
            continue
        stored = (ROOT / r['path']).read_bytes()
        data = gzip.decompress(stored) if r['path'].endswith('.gz') else stored
        if sha(stored) != r['stored_sha256'] or sha(data) != r['original_sha256'] or len(data) != r['original_bytes']:
            print('MISMATCH', r['id']); bad += 1
    print('verify:', 'OK' if not bad else f'{bad} mismatches')
    return bad


def main():
    if '--verify' in sys.argv:
        sys.exit(1 if verify() else 0)
    global REFETCH
    RAW.mkdir(exist_ok=True)
    if '--refetch' in sys.argv:
        REFETCH = tuple(sys.argv[sys.argv.index('--refetch') + 1].split(','))
        OLD.update({r['id']: r for r in json.loads(MANIFEST.read_text())})
    else:
        for f in RAW.iterdir():
            f.unlink()
    for key, url, kind, parent, channel, note in STATE:
        fetch(key, url, kind, parent, channel, note)
    oker_bundle()
    eis()
    wayback()
    counties()
    MANIFEST.write_text(json.dumps(rows, indent=1) + '\n')
    print(f'{len(rows)} records; raw bytes stored {sum(r.get("stored_bytes", 0) for r in rows)}')


if __name__ == '__main__':
    main()
