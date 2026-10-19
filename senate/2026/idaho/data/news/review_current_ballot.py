"""Bounded original county ballot review; raw parent access limits retained."""
from pathlib import Path
import gzip, hashlib, json, subprocess, tempfile

N=Path(__file__).resolve().parent
S=N.parent.parent
O=N/'coordinator-oct19-recheck'

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
    b=p.read_bytes()
    return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))

def main():
    source=O/'acquisition-ballot-stage-v3.json'
    rows=json.loads(source.read_bytes());by={r['id']:r for r in rows}
    assert len(rows)==len(by)==22
    bodies={}
    for r in rows:
        z=(S/r['asset_path']).read_bytes();raw=gzip.decompress(z)
        assert len(z)==r['stored_bytes']<40_000_000 and sha(z)==r['stored_sha256']
        assert len(raw)==r['raw_bytes'] and sha(raw)==r['raw_sha256']
        bodies[r['id']]=raw
    key='TwinFalls-linked-LD24-ballot';r=by[key];raw=bodies[key]
    assert r['status']==200 and len(raw)==592959
    assert sha(raw)=='9e89d002a415548d1b4670637652761f8c248432fc2a98eb0a93a7030d6cc926'
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'original.pdf';p.write_bytes(raw)
        subprocess.run(['pdftoppm','-f','1','-l','1','-scale-to','2000','-singlefile','-png',str(p),str(Path(d)/'page1')],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        b=(Path(d)/'page1.png').read_bytes()
    render=O/'TwinFalls-LD24-complete-original-page1.png'
    if render.exists():assert render.read_bytes()==b
    else:render.write_bytes(b)
    out=dict(status='pass_bounded_original_county_sample_ballot_review',
        immutable22_observations=pin(source),original_source=r,
        whole_original_first_page=pin(render),actually_visually_inspected=True,
        printed_date='November 3, 2026',printed_county='Twin Falls County',
        printed_ballot_scope='SAMPLE; Legislative Dist24; ABS LD24 GEN; No0049',
        printed_Senate_choices_in_source_order=[['Todd Achilles','IND'],['Natalie M Fleming','IND'],['Matt Loesby','LIB'],['Jim Risch','REP']],
        original_first_page_Senate_writein_line_printed=False,
        exact_primary_web_reader_chain=[
            dict(url='https://voteidaho.gov/idaho-general-election/',actual_link='Twin Falls',href='https://www.twinfallscounty.org/'),
            dict(url='https://twinfallscounty.org/',actual_link='Election Information',href='https://twinfallscounty.org/election/'),
            dict(url='https://twinfallscounty.org/election/',actual_link='Sample Ballots',href='https://twinfallscounty.org/election/sample_ballots/'),
            dict(url='https://twinfallscounty.org/election/sample_ballots/',actual_link='Legislative District24-County',href=r['url'])],
        reader_observation_date='2026-10-19',exact_reader_retrieval_UTC_not_available=None,
        raw_parent_outcomes={k:by[k]['status'] for k in ['TwinFalls-SOS-linked-home','TwinFalls-linked-elections','TwinFalls-linked-sample-parent']},
        parent_source_limits='Primary web reader resolved actual links; direct network parent requests returned406 and are retained separately. Original linked PDF itself returned200. No raw parent success invented.',
        all_official_statewide_eligible_writeins_or_later_signed_ballot_scope_exhausted=False,
        current_result_choice_ID_or_geographic_join_approved=False,
        qualification='Stronger bounded primary publication than newsroom setup, with four printed candidates and election-specific labels. No current Democrat is manufactured from historical nominees, all non-R voters or a generic coalition. This county sample does not prove statewide/later write-in completeness or current result IDs.')
    p=O/'current-ballot-original-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
    if p.exists():assert p.read_bytes()==b
    else:p.write_bytes(b)
    print(json.dumps(pin(p)))

if __name__=='__main__':main()
