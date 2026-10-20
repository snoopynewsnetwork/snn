"""Offline review of bounded Louisiana primary-newsroom observations."""
from pathlib import Path
import gzip, hashlib, html, json, re
H = Path(__file__).resolve().parent

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def pin(path):
    raw = path.read_bytes()
    return dict(path=path.name, bytes=len(raw), sha256=sha(raw))

def main():
    sources = {}
    observations = []
    for path in sorted(H.glob('*.receipt.json')):
        receipt = json.loads(path.read_bytes())
        assert receipt['status'] == 200
        assert receipt['requested_UTC'] and receipt['completed_UTC']
        for hop in receipt['hops']:
            packed = (H/hop['body_path']).read_bytes()
            raw = gzip.decompress(packed)
            assert (len(packed), sha(packed), len(raw), sha(raw)) == (
                hop['stored_bytes'], hop['stored_sha256'], hop['raw_bytes'], hop['raw_sha256'])
            assert hop['request_headers'] and hop['response_headers']
        source = raw.decode('utf-8', errors='replace')
        sources[receipt['id']] = source
        title = re.search(r'<title[^>]*>(.*?)</title>', source, re.S | re.I)
        observations.append(dict(id=receipt['id'], receipt=pin(path), url=receipt['final_url'],
                                 status=receipt['status'], title=html.unescape(title[1]) if title else None,
                                 raw_bytes=len(raw), raw_sha256=sha(raw)))
    assert len(observations) == 5
    links = json.loads((H/'knoe-home.election-links.json').read_bytes())
    for target in ('https://www.knoe.com/politics/election-results',
                   'https://www.knoe.com/2026/10/19/november-2026-arklamiss-election-guide/'):
        assert any(x['url'] == target for x in links)
    widgets = []
    for name in ('knoe-results', 'kalb-results'):
        source = sources[name]
        cache = json.JSONDecoder().raw_decode(source.split('Fusion.contentCache=', 1)[1])[0]
        complete = {key: value for key, value in cache.items() if 'election' in key}
        out = H/(name+'-complete-embedded-election-cache.json')
        out.write_text(json.dumps(complete, indent=2, ensure_ascii=False, allow_nan=False)+'\n')
        query, response = next(iter(complete['gsync-elections'].items()))
        data = response['data']
        parameters = json.loads(query)
        assert parameters['includeTestResults'] is False
        election = data['selectedElection']
        if name == 'knoe-results':
            assert election == {'id': None} and data['elections'] == []
        else:
            assert election['id'] == '2519' and election['name'] == 'June 27 Election'
            assert election['isActive'] is False and len(election['races']) == 40
            assert data['elections'][0]['isTest'] is False
            assert len([x for x in election['races'] if x['name'].startswith('U.S. Senate')]) == 2
        widgets.append(dict(id=name, complete_object=pin(out), backend_parameters=parameters,
                            selected_election_without_races={k:v for k,v in election.items() if k!='races'},
                            complete_race_objects=len(election.get('races', [])),
                            complete_Senate_objects=[x for x in election.get('races', []) if x['name'].startswith('U.S. Senate')],
                            all_list_entries=data['elections'],
                            data_updatedDate=data['updatedDate'], data_transformedAt=data['dataTransformedAt'],
                            literal_display_test_flag_contexts=re.findall(r'.{0,70}displayTestData.{0,100}', source)))
    articles = []
    for name in ('knoe-november-guide', 'knoe-june-test-notice'):
        source = sources[name]
        article = json.JSONDecoder().raw_decode(source.split('Fusion.globalContent=', 1)[1])[0]
        out = H/(name+'-complete-public-article.json')
        out.write_text(json.dumps(article, indent=2, ensure_ascii=False, allow_nan=False)+'\n')
        paragraphs = [x.get('content', '') for x in article.get('content_elements', [])]
        if name == 'knoe-june-test-notice':
            assert any('mock results' in x and 'testing purposes' in x for x in paragraphs)
        else:
            assert any('Nov. 3' in x for x in paragraphs)
            assert any('https://www.knoe.com/politics/election-results/' in x for x in paragraphs)
        articles.append(dict(id=name, full_object=pin(out), headline=article['headlines']['basic'],
                             published_UTC=article.get('publish_date'), updated_UTC=article.get('last_updated_date'),
                             scope='Primary newsroom context, not official legal authority or an admitted vote stream'))
    old = H.parent/'manifest.json'
    result = dict(status='pass_bounded_Louisiana_northeast_central_newsroom_research',
                  complete_requests=5, HTTP200=5, observations=observations, complete_widgets=widgets,
                  complete_primary_articles=articles,
                  previous_news_manifest=dict(path='../manifest.json', bytes=old.stat().st_size, sha256=sha(old.read_bytes())),
                  qualification='KNOE current results cache has an explicit null selected ID and empty election list; this is this complete response, not proof of future or historical absence. Its current November guide links the results product. KALB retains inactive June27 product2519 with40 complete races/two Senate primary races. Primary source updatedDate and current transformedAt clocks remain distinct. Frontend displayTestData true, backend includeTestResults false and listing isTest false are separate fields, never overrides. KNOE June24 testing notice is explicitly historical. Shared Gray infrastructure does not provide independent statewide votes. No November count/choice/roster/cadence/outstanding/legal/geography approval.',
                  current_November_counts_or_measured_cadence_approved=False)
    (H/'review.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    target = H/'asset-manifest.json'
    rows = [pin(p) for p in sorted(H.iterdir()) if p.is_file() and p!=target]
    assert all(row['bytes'] < 40000000 for row in rows)
    target.write_text(json.dumps(dict(assets=rows, excludes_only=target.name), indent=2)+'\n')
    print(dict(requests=5, assets=len(rows), review=pin(H/'review.json')))

if __name__ == '__main__':
    main()
