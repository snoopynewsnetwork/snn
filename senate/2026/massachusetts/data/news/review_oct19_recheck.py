"""Independent bounded regional-source raw-body replay; no count admission."""
from pathlib import Path
import gzip
import hashlib
import json
from html.parser import HTMLParser

S = Path(__file__).resolve().parents[2]
O = S / 'data/news/coordinator-oct19-recheck'


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)


def main():
    source = O / 'acquisition-complete-v1.json'
    records = json.loads(source.read_bytes())
    assert len(records)==10 and len({r['id'] for r in records})==10
    by = {r['id']:r for r in records}
    bodies = {}
    for row in records:
        stored = (S/row['asset_path']).read_bytes()
        raw = gzip.decompress(stored)
        assert len(stored)==row['stored_bytes']<40_000_000
        assert hashlib.sha256(stored).hexdigest()==row['stored_sha256']
        assert len(raw)==row['raw_bytes'] and hashlib.sha256(raw).hexdigest()==row['raw_sha256']
        bodies[row['id']] = raw
    assert by['telegram-home']['status']==402 and by['capecodtimes-home']['status']==402
    assert by['wpri-home']['status']==403
    assert by['vineyardgazette-primary']['status']==by['worcester-local-primary']['status']==200
    stream = by['worcester-official-stream']['literal_iframes']
    assert any(x.get('title')=='City of Worcester State Primary Election Results Video Stream' for x in stream)
    pdfs = []
    for year in ['2024','2026']:
        row = by['worcester-original-'+year]
        assert row['status']==200 and bodies[row['id']].startswith(b'%PDF')
        pdfs.append(dict(id=row['id'],raw_bytes=row['raw_bytes'],raw_sha256=row['raw_sha256'],
                         requested_url=row['url'],source_label=row['literal_label'],
                         exact_acquired_original=True,visual_inspection_or_candidate_extraction_claimed=False))
    news = []
    for key in ['vineyardgazette-primary','worcester-local-primary']:
        parser=Text();parser.feed(bodies[key].decode('utf-8',errors='replace'))
        text=' '.join(' '.join(parser.parts).split())
        assert '2026' in text and ('primary' in text.lower())
        news.append(dict(id=key,url=by[key]['url'],scope='Original local September primary reporting; no genuine November feed or measured cadence.',
                         raw_bytes=by[key]['raw_bytes'],raw_sha256=by[key]['raw_sha256']))
    output=dict(status='pass_bounded_original_regional_source_recheck',complete_response_bodies=10,
                immutable_inventory=dict(path=str(source.relative_to(S)),bytes=source.stat().st_size,
                                         sha256=hashlib.sha256(source.read_bytes()).hexdigest()),
                explicit_access_limits={'WorcesterTelegram':402,'CapeCodTimes':402,'WPRI':403},
                original_local_reporting=news,complete_city_PDF_originals=pdfs,
                municipal_stream_observation=dict(url=by['worcester-official-stream']['url'],
                                                  complete_actual_iframe_attributes=stream,
                                                  title_remains_State_Primary=True,actual_video_playback_claimed=False),
                complete_city_results_page=dict(url=by['worcester-official-results']['url'],
                                                actual_results_links=[x for x in by['worcester-official-results']['literal_links'] if 'election-results/' in x['url']]),
                November_feed_admitted=False,independent_count_supplier_proved=False,
                measured_publication_cadence=False,optional_preparation_not_worker_build_dependency=True)
    p=O/'review.json';p.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(dict(path=str(p.relative_to(S)),bytes=p.stat().st_size,
                          sha256=hashlib.sha256(p.read_bytes()).hexdigest())))


if __name__=='__main__':
    main()
