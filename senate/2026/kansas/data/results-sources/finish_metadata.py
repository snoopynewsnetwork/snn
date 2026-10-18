#!/usr/bin/env python3
"""Deterministic interpreted observations; raw HTTP clocks remain separate."""
import json,pathlib
R=pathlib.Path(__file__).resolve().parent
J=lambda p:json.loads(p.read_text())
a=J(R/'acquisition.json');m={x['id']:x for x in a}
sc=J(R/'native-source-scopes.json');sc['status']='source scopes frozen for coordinator review; no current geography/feed approval'
if not any(x.get('election_id')=='122433' for x in sc['inspected_vendor_scopes']):sc['inspected_vendor_scopes'].append({'county':'Miami','election_id':'122433','date':'2024-11-05','scope':'actual archive elections.json identifies2024general; all5JSON variants downloaded; no November2026identity'})
(R/'native-source-scopes.json').write_text(json.dumps(sc,indent=2)+'\n')
obs=[]
for sid,date,clock,zone,status,scope in [
 ('court-injunction-july16','2026-07-16','08:33',None,'signed temporary injunction','statewide SB4 injunction; ordinary advance mail former rule restored pending further order; mirrored primary judicial document'),
 ('court-supreme-july30','2026-07-30',None,None,'emergency review denied','majority disposition distinct from dissent; mirror not court docket'),
 ('court-appeal-oct2','2026-10-02','16:18',None,'renewed stay denied','130839; temporary injunction remains pending merits; not final merits'),
 ('court-docket-122','2026-11-24','10:00','Central inferred from Topeka','scheduled merits argument','official court-hosted docket, not complete later-disposition history'),
 ('johnson-notice','2026-11-03',None,'Central','revised general-election notice','printed3 Senate candidates; poll hours7–7; October revised source'),
 ('riley-canvass','2026-11-12','10:00','Central inferred from Manhattan','signed September9 notice/publishedSeptember26','actualNovembercountycanvass; manual visual page1'),
 ('riley-2024','2024-11-05','11/18/2024 03:03PM',None,'Final All Groups / Official Results','county alternative summary differs acceptedSOS named -393; cause unavailable'),
 ('riley-2024-abstract','2024-11-05','canvassed November14,2024; PDFcreatedNovember18',None,'signed abstract','highlighted presidential totals match acceptedSOS; source difference retained'),
 ('reno-original-pdf','2024-11-05','11/13/2024 13:46:57',None,'Official Final Canvass','actualPDF recovered via viewerinput, not HTMLshell'),
 ('ellis-2024','2024-11-05','11/18/2024 6:45AM',None,'OFFICIAL RESULTS','scannedPDF visual controls and literal methodcolumns'),
 ('barton-2024','2024-11-05','11/12/2024 10:44AM',None,'Official Final including Provisionals','reported42/42,complete29,partial13; no November implication'),
 ('sumner-2024-original','2024-11-05','11/18/2024 16:11',None,'official summary per archive/filename','matching indexedvendororiginal; county relative link404 retained'),
 ('franklin-primary','2026-08-04',None,None,'OFFICIAL RESULTS printed','scannedcounty primary5153 vs acceptedSOS5205; no cause/change inferred'),
 ('riley-primaryofficial','2026-08-04',None,None,'Official Final Results Without Hand Counts','literal caveat; not complete candidate/ballot coverage inferred'),
 ('finney-primary','2026-08-04',None,None,'page OFFICIAL / filename UNOFFICIAL','conflicting labels preserved, no invented chronology'),
 ('pottawatomie-report',None,None,None,'No Results at this time','successfulPDF without election/contest/count identity; not zero'),
 ('sos-av1',None,'formrevision2026-09-28',None,'official application/contact form','105contactblocks; entryvintages can differ from revision'),
 ('saline-general-notice','2026-11-03',None,None,'general election notice','scannedoriginal confirms3printedSenatecandidates; no writeinaffidavitroster')]:
 obs.append({'source_id':sid,'requested_url':m[sid]['url'],'original_sha256':m[sid].get('original_sha256'),'election_or_event_date':date,'source_clock_literal':clock,'source_timezone':zone,'source_status_literal_or_interpretation':status,'scope':scope,'http_retrieved_at_utc':m[sid]['retrieved_at_utc'],'clock_policy':'HTTP Date/Last-Modified/retrieval are not election clocks; null is unavailable/unprinted, not UTC or zero'})
(R/'source-observations.json').write_text(json.dumps({'observations':obs,'vendor_source_clocks':'vendor-extracts.json preserves full GeneratedDate/config/status/global objects; no normalization that discards sourceoffsets','all_other_sources':'complete original bytes, returned HTTPheaders and visible text preserve other dates/labels; uninterpreted dates are not operational schedule claims'},indent=2)+'\n')
