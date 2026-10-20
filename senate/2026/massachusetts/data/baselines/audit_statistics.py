import gzip,json
from extract_originals import ROOT,dump,sha
def main():
    own=json.loads((ROOT/'statistics-controls.json').read_text());body=(ROOT/'peer-audit/turnout-statistics-controls.json.gz').read_bytes();peer=json.loads(gzip.decompress(body));checks=[]
    for p in peer:
        year=str(p['year']);r=own['registration_statewide_asof'][year];t=own['turnout_page_state_elections'][year];m=own['method_page_state_elections'][year]
        assert p['registration']==r['registered'] and p['registration_date']==r['date']
        assert p['turnout_table_TotalVotesCast']==t['TotalVotesCast'] and p['turnout_table_percent_literal']==t['turnout_percent_printed']
        assert p['method_index_TotalBallotsCast']==m['TotalBallotsCast']
        for pk,ok in [('mail','mail_percent_printed'),('early','early_percent_printed'),('election_day','ElectionDay_percent_printed')]:assert p['method_index_percentages_literal'][pk]==m[ok]
        checks.append(dict(year=year,registration_date_total_turnout_methods_literal_state_controls_match=True))
    dump(ROOT/'peer-audit/statistics-comparison.json',dict(status='pass_shared_state_controls_with_qualified_additional347row_browser_extraction',checks=checks,peer_original_sha256=sha(gzip.decompress(body)),peer_stored_sha256=sha(body),own_precomparison_freeze_sha256=sha((ROOT/'source/statistics-original-first-freeze.json').read_bytes()),coverage_difference='Peer appropriately leaves municipal registration null. Own supplemental browser representation retains347 printed2024 municipal rows and all14 county controls, four absent names and unallocated municipal/county discrepancies. No original-byte or native-registration coverage is claimed by either worker.'))
if __name__=='__main__':main()
