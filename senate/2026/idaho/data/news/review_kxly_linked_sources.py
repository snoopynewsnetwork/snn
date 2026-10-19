"""Read-only source parsing of complete KXLY observations; no vote admission."""
from pathlib import Path
import gzip, hashlib, json
from bs4 import BeautifulSoup

N=Path(__file__).resolve().parent
S=N.parent.parent
O=N/'coordinator-oct19-recheck'

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
    b=p.read_bytes()
    return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))

def main():
    source=O/'acquisition-KXLY-stage-v2.json'
    rows=json.loads(source.read_bytes());by={r['id']:r for r in rows}
    assert len(rows)==len(by)==15
    bodies={}
    for r in rows:
        z=(S/r['asset_path']).read_bytes();raw=gzip.decompress(z)
        assert len(z)==r['stored_bytes'] and sha(z)==r['stored_sha256']
        assert len(raw)==r['raw_bytes'] and sha(raw)==r['raw_sha256']
        bodies[r['id']]=raw
    home=BeautifulSoup(bodies['kxly-home'],'html.parser')
    assert any(a.get('href')=='/news/politics/election-results/' for a in home.find_all('a'))
    dom=BeautifulSoup(bodies['kxly-linked-results'],'html.parser')
    races=[]
    for v in dom.select('.elections-race'):
        info=v.select_one('.election-race-info');results=v.select_one('.election-race-results')
        link=info.select_one('a.issue-inner');candidate=[]
        for row in results.select('tbody tr'):
            name=row.select_one('.candidate-name')
            percent=row.select_one('.vote-pct');votes=row.select_one('.vote-totals')
            candidate.append(dict(literal_name=name.get_text(' ',strip=True) if name else None,
                literal_party_title=name.select_one('[title]').get('title') if name and name.select_one('[title]') else None,
                source_classes=name.get('class') if name else None,
                links=[dict(href=a.get('href'),text=a.get_text(' ',strip=True)) for a in name.find_all('a',href=True)] if name else [],
                literal_percent=percent.get_text(' ',strip=True) if percent else None,
                literal_votes=votes.get_text(' ',strip=True) if votes else None))
        races.append(dict(source_table_id=info.get('id'),literal_race_name=link.get_text(' ',strip=True),
            actual_race_href=link.get('href'),info_cells=[td.get_text(' ',strip=True) for td in info.select('tbody td')],
            candidates=candidate,footer_literal=results.select_one('tfoot').get_text(' ',strip=True),
            source_time_attributes=[dict(t.attrs) for t in results.find_all('time')],
            parsed_HTML_derivative=str(v)))
    assert len(races)==61
    selected=[x for x in races if x['literal_race_name']=='IDAHO US SENATOR'];assert len(selected)==1
    senate=selected[0];assert [x['literal_name'] for x in senate['candidates']]==['JIM RISCH','MATT LOESBY','TODD ACHILLES','NATALIE FLEMING']
    assert [x['literal_party_title'] for x in senate['candidates']]==['Republican party','Libertarian party','Independent party','Independent party']
    assert all(x['literal_votes']=='0' for x in senate['candidates'])
    assert senate['footer_literal'].startswith('(100%) precincts reporting')
    assert senate['source_time_attributes'][0]['datetime']=='2026-10-06T15:50:32-07:00'
    derivative=O/'kxly-complete61race-source-derivative.json.gz'
    b=gzip.compress((json.dumps(races,indent=2)+'\n').encode(),mtime=0)
    if derivative.exists():assert derivative.read_bytes()==b
    else:derivative.write_bytes(b)
    out=dict(status='pass_bounded_KXLY_current_setup_source_not_returns',
        immutable15_observation_acquisition=pin(source),prior13_witness_preserved=pin(O/'acquisition-complete-v1.json'),
        complete_source_race_derivative=pin(derivative),race_blocks=61,
        senate=senate,all_original_bytes_and_count_source_fields_preserved=True,
        nominal_count_completion_not_admitted=True,
        final_official_candidate_universe_established=False,
        supplier_cadence_and_current_choice_IDs_unverified=True,
        qualification='Actual homepage link resolves61 mixed-state race blocks. Idaho Senate4choices are zero with100% completion and an October6 clock before election day. This is a newsroom setup observation, not votes, final official ballot, eligible-write-in exhaustion or current result-ID approval. Page warning about Washington multi-day counting is not Idaho law. No shared-supplier independence inferred.')
    p=O/'kxly-linked-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
    if p.exists():assert p.read_bytes()==b
    else:p.write_bytes(b)
    print(json.dumps(pin(p)))

if __name__=='__main__':main()
