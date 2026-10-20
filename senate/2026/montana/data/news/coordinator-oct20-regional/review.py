"""Offline bounded Montana newsroom/raw public client and XML audit."""
from pathlib import Path
import gzip, hashlib, html, json, re, xml.etree.ElementTree as ET
H = Path(__file__).resolve().parent
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def pin(path):
    raw = path.read_bytes()
    return dict(path=path.name, bytes=len(raw), sha256=sha(raw))

def full_node(element):
    return dict(tag=element.tag, attributes=dict(element.attrib), text=element.text,
                tail=element.tail, children=[full_node(x) for x in element])

def main():
    sources = {}
    observations = []
    for path in sorted(H.glob('*.receipt.json')):
        row = json.loads(path.read_bytes())
        assert row['status'] == 200 and row['requested_UTC'] and row['completed_UTC']
        for hop in row['hops']:
            packed = (H/hop['body_path']).read_bytes()
            raw = gzip.decompress(packed)
            assert (len(packed), sha(packed), len(raw), sha(raw)) == (
                hop['stored_bytes'], hop['stored_sha256'], hop['raw_bytes'], hop['raw_sha256'])
            assert hop['request_headers'] and hop['response_headers']
        sources[row['id']] = raw
        title = re.search(r'<title[^>]*>(.*?)</title>', raw.decode(errors='replace'), re.S | re.I)
        observations.append(dict(id=row['id'], receipt=pin(path), URL=row['final_url'], status=row['status'],
                                 raw_bytes=len(raw), raw_sha256=sha(raw),
                                 title=html.unescape(title[1]) if title else None))
    assert len(observations) == 5
    page = sources['ktvq-results'].decode()
    assert 'testing purposes and do not reflect real results' in page
    assert 'data-xml-file-location="http://mediaassets.ktvq.com/NWT/electionresults/elections.xml"' in page
    assert '//assets.scrippsdigital.com/cms/election-results/BS-ElectionResults-uncompressed.js' in page
    client = sources['ktvq-results-client'].decode()
    assert 'this.$module.data("xml-file-location")' in client
    timer = re.search(r'this\.refreshInt = setInterval\(function\(\).*?30000\);', client, re.S)
    assert timer
    xml = ET.fromstring(sources['ktvq-literal-xml'])
    assert xml.tag == 'DATA'
    races = xml.findall('RACE')
    assert len(races) == 8
    summary = []
    for race in races:
        info = race.find('RACE_INFO')
        candidates = race.findall('CANDIDATE_INFO/CANDIDATE')
        labels = [info.findtext('RACE_NAME'+str(i)) for i in range(1, 5)]
        summary.append(dict(literal_labels=labels, race_id=info.findtext('RACE_ID'),
                            jurisdiction_id=info.findtext('JURISDICTION_ID'),
                            updated_literal=info.findtext('UPDATED'), candidate_count=len(candidates),
                            candidate_vote_sum=sum(int(x.findtext('VOTE_TOTAL')) for x in candidates),
                            allcand_votes_literal=info.findtext('ALLCAND_VOTES'),
                            precinct_total_literal=info.findtext('PRECINCTS_TOTAL'),
                            precinct_reporting_literal=info.findtext('PRECINCTS_REPORTING')))
        assert any('WYOMING' in x for x in labels if x)
    transcript = H/'complete-XML-object.json'
    transcript.write_text(json.dumps(full_node(xml), indent=2, ensure_ascii=False)+'\n')
    daily = sources['daily-interlake-primary'].decode()
    assert 'Statewide and Flathead County primary election results' in daily
    result = dict(status='pass_bounded_Montana_northwest_eastern_newsroom_research',
                  complete_requests=5, HTTP200=5, observations=observations,
                  literal_public_constructor=dict(page='ktvq-results', attribute='data-xml-file-location',
                     value='http://mediaassets.ktvq.com/NWT/electionresults/elections.xml',
                     script='https://assets.scrippsdigital.com/cms/election-results/BS-ElectionResults-uncompressed.js',
                     declared_refresh_milliseconds=30000, actual_genuine_update_cadence_measured=False),
                  complete_XML_object=pin(transcript), XML_races=len(races),
                  RUN_DATE_literal=xml.findtext('RUN_DATE'), RUN_EPOCH_literal=xml.findtext('RUN_EPOCH'),
                  race_source_summaries=summary,
                  qualifications=['KTVQ results page explicitly marks displayed results as test-only.',
                    'Its literal XML has eight Wyoming-labelled races with August18 race clocks; current RUN clock does not turn them into Montana November returns.',
                    'Declared JavaScript timer is not measured data publication cadence. Candidate/control/clock/null/attribute/order fields and full XML are retained.',
                    'Daily Inter Lake is a June3 primary article, not November counts. No account/login requests or paid-content decoding performed.',
                    'Cross-state geography, election stage, calls and raw precinct-zero values require explicit source validation; no admitted current IDs or count stream.'],
                  current_counts_ids_legal_geometry_cadence_or_outstanding_approved=False,
                  earlier_news_manifest=dict(path='../manifest.json', bytes=(H.parent/'manifest.json').stat().st_size,
                                             sha256=sha((H.parent/'manifest.json').read_bytes())))
    (H/'review.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    target = H/'asset-manifest.json'
    rows = [pin(x) for x in sorted(H.iterdir()) if x.is_file() and x!=target]
    assert all(x['bytes'] < 40000000 for x in rows)
    target.write_text(json.dumps(dict(assets=rows, excludes_only=target.name), indent=2)+'\n')
    print(dict(requests=5, assets=len(rows), review=pin(H/'review.json')))

if __name__ == '__main__':
    main()
