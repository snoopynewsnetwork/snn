"""Offline source-specific appendix, complete decoding controls and legal scope."""
from pathlib import Path
import json,html,re,xml.etree.ElementTree as ET
from urllib.parse import quote
import acquire as a

def run():
    rows=[json.loads(p.read_bytes())for p in sorted((a.OUT/'receipts').glob('*.json'))];rr={r['id']:r for r in rows}
    parents=json.loads((a.OUT/'parent-investigations.json').read_bytes());dec=[]
    for r in rows:
        if 'path'not in r:
            dec.append(dict(source=r['id'],HTTP_status=r.get('status'),entity_available=False,reason=r.get('error')));continue
        wire=a.entity(r);raw=a.body(r)
        assert len(wire)==r['entity_bytes']and a.sha(wire)==r['entity_sha256']
        if r.get('raw_sha256'):assert a.sha(raw)==r['raw_sha256']and len(raw)==r['raw_bytes']
        dec.append(dict(source=r['id'],HTTP_status=r['status'],entity_available=True,entity_bytes=len(wire),entity_sha256=a.sha(wire),content_encoding=r['content_encoding'],decoded_bytes=len(raw),decoded_sha256=a.sha(raw),original_receipt_decoded_hash_present='raw_sha256'in r,complete=r.get('entity_complete'),storage=r['storage']))
    a.save(a.OUT/'decoding-controls.json',dec)
    def src(sid):
        r=rr[sid];return dict(source_id=sid,receipt='data/results-sources/receipts/'+sid+'.json',requested_url=r['requested_url'],status=r.get('status'),entity_sha256=r.get('entity_sha256'),source_time_scope='HTTP Date/Last-Modified and retrieval UTC are not vote-update times')
    legal=dict(status='bounded_current_primary_instructions_and_actual_disposition_verified_with_explicit_operative_scope_gaps',
       evidence=[src(s)for s in ['sos-elections','sample-ballot','qualifying-parent-iframe','clarification-sept10','clarification-sept10-child-2','county-handbook','calendar','calendar-1','calendar-2','sos-absentee-current','absentee-sept21','admin-code-current-secretary-query','admin-rule-current-linked-confirmation','hb859-history-current-curl','hb859-current-pdf-curl','hb859-current-html-curl','scotus-docket','fifth-circuit-query','fifth-sept9-doc255','court-case-info','court-district-home','code-lexis','sos-yall-vote-linked-6','ecfr-api-title-metadata','ecfr-part71-current-xml','nist-dst-2026','nist-zone-faq']],
       ordinary_US_Senate_rule='plurality per actual SOS Sept10 parent-linked chart; not2018specialmajority/runoff',
       candidate_publication=dict(election='2026-11-03 regularClassII',SAMPLE_order=[dict(name='Scott Colom',party='Democrat'),dict(name='Cindy Hyde-Smith',party='Republican'),dict(name='Ty Pinkins',party='Independent'),dict(name='Write-in',party=None)],signed_final_certification_verified=False,full_eligible_named_writein_universe=None,withdrawal_substitution_resolution=None,official_result_IDs=None),
       method_categories=dict(ordinary_Election_Day='Polls7am-7pm and in-line closing exception; actual extensions not exhaustively audited',in_person_absentee='Excused eligible voters; directly machine-scanned paper per Sept21/FAQ, counted after close; Oct31noon deadline',mail_absentee='Nov3postmark/Nov10receipt per currentSOS; calendar5pm; eligibility/witness and acceptance remain separate',UOCAVA='Calendar/handbook email/fax7pm ElectionDay, postal receipt separately scoped, FPCA/FWAB/electronic signature exceptions; no complete every-exception order audit',signature_mismatch_cure='Current app-linked Part17 rules4.1/4.2/form: noon10thcalendar day (Nov13); distinct one-business-day notice phrases retained',photo_ID_affidavit_cure='Calendar Nov10at5pm for acceptable ID/religiousobjection; not signature-cure deadline',provisional_affidavit='Sealed ElectionDay ballots adjudicated during canvass; never automatically included or exactSenatevotes'),
       certification=dict(county_return_delivery_calendar='2026-11-13',state_ascertainment_calendar='2026-12-03',automatic_web_completion_or_cadence=False,complete_current_Senate_tie_contest_recount_route_verified=False),
       HB859=dict(official_history_disposition='Law',chapter=385,effective_date='2026-07-01',history_approval='03/19 Approved by Governor',current_HTML_label='As Sent to Governor',current_PDF_label='As Passed the House',label_conflict_cause=None,section26_scope='daily aggregate inpersonabsentee OMR report available on request',public_OMR_endpoint=None,candidate_allocation=None),
       court=dict(case='24-60395',actual_document='255-1',filed='2026-09-09',PDF_pages=2,result='District court judgment AFFIRMED on SupremeCourt remand in light of Watson',raw_bytes=116710,raw_sha256='ac0eb5911e6a3c6f6f95ffb655f33916380bbd3226b928a6140fc9484941f408',complete_later_mandate_rehearing_stay_district_docket_verified=False,public_docket_routes='PACER/login/setup or unavailable page; no authenticated/paid request',SupremeCourt_docket_dates=['2026-06-29 reversal/remand','2026-07-31 Judgment Issued'],old2024opinion_sufficient_current_rule=False),
       stale_code=dict(current_linked_PDF_copyright=2017,current_Lexis_container='HTTP200 JavaScript shell',operative_current_code_consolidation_verified=False),
       complete_current_legal_coverage=False,
       unresolved=['Signed final candidate certification and any withdrawal/substitution/eligiblewritein resolution','Complete later mandate/rehearing/stay/district-remand docket','Full current code consolidation and all cure/witness/UOCAVA exceptions or later operative orders','Exact federal statewide tie and Senate-specific protest/recount route','Actual poll extensions and election-specific counting/publication completion notices','Current candidate/native/method result IDs and candidate allocations'])
    md=json.loads(a.body(rr['ecfr-api-title-metadata']));t=next(x for x in md['titles']if x['number']==49)
    root=ET.fromstring(a.body(rr['ecfr-part71-current-xml']));sects={n.attrib['N']:' '.join(n.itertext())for n in root.iter()if n.attrib.get('TYPE')=='SECTION'}
    assert all(k in sects for k in ['71.2','71.5','71.6','71.7'])
    legal['timezone']=dict(source_currency=t,complete_part71_entity=src('ecfr-part71-current-xml'),sections_checked=['71.2','71.5','71.6','71.7'],published_boundary_result='Mississippi lies between eastern/central and central/mountain boundaries: statewide Central is a geographic inference from complete primary rules, not a county native-unit crosswalk.',zone='America/Chicago',normal_Nov3_7pm_UTC='2026-11-04T01:00:00Z',offset=-6,DST_end='2026-11-01T02:00:00 local',future_or_poll_extension_order_audit_complete=False,earlier_HTML_challenges_retained=True)
    shared=[]
    for sid in ['watson-bound-opinion','watson-scotus-docket']:
        rp=a.ROOT/'data/coordinator-legal-preparation'/(sid+'.receipt.json');receipt=json.loads(rp.read_bytes());p=receipt['body']['stored_path']
        if p.startswith('senate/2026/mississippi/'):p=p[len('senate/2026/mississippi/'):]
        b=(a.ROOT/p).read_bytes();raw=__import__('gzip').decompress(b)
        assert a.sha(b)==receipt['body']['stored_sha256']and a.sha(raw)==receipt['body']['raw_sha256']
        shared.append(dict(source_id=sid,receipt_pin=a.pin(rp),original_pin=a.pin(a.ROOT/p),raw_bytes=len(raw),raw_sha256=a.sha(raw),source_scope='Exact existing primary original reused read-only; coordinator preparation is not an independent duplicate source or complete later-order audit.'))
    legal['read_only_original_dependencies']=shared
    a.save(a.OUT/'legal-observations.json',legal)
    lines=['# All82 county-parent publication investigations','',
      'Observed October19,2026UTC. These are82 county-parent investigations,77 priority parents. Each of887 priority children explicitly shares its parent inspection; no887 independent feeds. All849remainder children and five nonpriority parents remain. Complete fields/arrays/sources are exact read-only references in [scope](scope-reference.json), not reduced replacement bodies. [Full HTTP ledger](source-ledger.json) retains requested/final URLs, complete headers/errors/entities and UTC.','',
      'County directory references identify actual clerks/commissions; local rawHTTP depth varies. A200 page, primary/historical document, sample, site-search or setup is not a current November feed. No current election/contest/candidate/native/method ID, exact Senate remainder or cadence is approved.','',
      '| County / frozen parent | Priority children | Full native | Remainder | County-specific requests / HTTP200 |','| --- | ---: | ---: | ---: | ---: |']
    for p in parents:lines.append(f"| [{p['county']}](#county-{p['county_fips']}) / {p['county_fips']} | {p['priority_child_count']} | {p['full_native_count']} | {p['remainder_native_count']} | {p['current_primary_requests']} / {p['current_primary_HTTP200_observations']} |")
    for i,p in enumerate(parents):
        h=p['preferred_historical_publication'];u=quote(h['url'],safe=':/?&=%+#')
        lines+=['',f"<a id=\"county-{p['county_fips']}\"></a>",f"## {p['county']} ({p['county_fips']})",'',
          f"{'Priority parent'if p['priority_parent']else 'Nonpriority parent inventory'}: {p['priority_child_count']} priority / {p['full_native_count']} full native / {p['remainder_native_count']} remainder. {p['depth']}.",'',
          f"Actual [SOS directory](https://www.sos.ms.gov/MSCountyElectionInfo/) record ordinal `{p['directory_app_key']}`, literal county `{p['directory_county_label_literal']}`, clerk **{html.unescape(p['clerk_name_literal'])}**, {p['commissioner_record_count']} source commissioner entries. Complete original-derived fields at `county-authority-payload.json#{p['state_directory_pointer']}`. No directory ordinal/nativeID equivalence.",'',
          f"Historical [preferred original]({u}) `{h['source_id']}`: rawSHA256 `{h['original']['raw_sha256']}`. Fresh actual parent chain: `{' → '.join(h['chain'])}`; literal href and source hash are in `parent-investigations.json#/{i}/preferred_historical_publication`. Alternative packets remain in full frozen dependencies.",'',
          f"Full preferred schema has {p['all_preferred_columns']} source columns / {p['historical_named_numeric_positions']} numeric and {p['historical_named_null_positions']} null named positions. Roles: `{json.dumps(p['historical_source_role_counts'],sort_keys=True)}`. Complete parent/full-child/priority-child/source and other-year objects remain reachable from `parent-investigations.json#/{i}`. No alias, method allocation or source residual repair.",'',p['investigation_note'],'',
          'Current March-primary index links (publication scope only):']
        for x in p['current_primary_county_links']:lines.append(f"- `{x['index_source']}`: [{x['link']['text'].strip()}]({quote(x['link']['url'],safe=':/?&=%+#')})")
        if not p['current_primary_county_links']:lines.append('- No literal county label in the retained party indexes; not zero and not evidence that a result publication does not exist.')
        lines+=['','Actual county-specific observations:','', '| Source / scope | HTTP / transport | Actual requested URL |','| --- | --- | --- |']
        for sid in p['current_source_observation_ids']:
            r=rr[sid];status=r.get('status');outcome=str(status)if status is not None else str(r.get('error_type'))+': '+str(r.get('error'))
            scope='secondary site discovery only'if'discovery-profile'in sid else str(r.get('scope')or r.get('relation')or'actual linked original')
            scope=scope if len(scope)<180 else scope[:177]+'…'
            lines.append(f"| [{sid}](receipts/{sid}.json) — {scope.replace('|','/')} | {outcome.replace('|','/')} | [requested]({quote(r['requested_url'],safe=':/?&=%+#')}) |")
        if not p['current_source_observation_ids']:lines.append('| State directory and complete historical source only | Current local mechanism unavailable in this bounded review | [SOS county authority](https://www.sos.ms.gov/elections-voting/county-election-information) |')
        lines+=['','Current IDs, candidate/method allocations, source vote-update clock/timezone, exact outstanding Senate votes and guaranteed cadence remain **null/unverified**. Parent totals, native constituents, method totals, alternatives and vendor views must not be added together.']
    (a.OUT/'parent-publication-notes.md').write_text('\n'.join(lines)+'\n')
    return dict(receipts=len(rows),parents=len(parents),legal_complete=False)
if __name__=='__main__':print(run())
