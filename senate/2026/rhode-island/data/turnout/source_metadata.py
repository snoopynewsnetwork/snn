"""Source graph, method descriptions and lossless archive-view discrepancies."""
import collections,urllib.parse
from common import *
from acquire import allreceipts
def run():
    rs=allreceipts();edges=[]
    for r in rs:
        if r.get('status')!=200 or 'stored_path'not in r:continue
        b=original(r)
        if b.startswith(b'<!DOCTYPE')or b.startswith(b'<html'):
            for label,u in links(b):
                absolute=urllib.parse.urljoin(r['url'],u)
                for dest in rs:
                    if dest['url']==absolute:edges.append(dict(parent_id=r['id'],parent_raw_sha256=r['raw_sha256'],literal_href=u,label=label,requested_url=absolute,child_id=dest['id']))
    dump(ROOT/'source/source-graph.json',dict(observations=rs,literal_download_and_parent_edges=edges))
    allrows=[json.loads(l) for l in gzip.decompress((ROOT/'extracts/all-long-rows.jsonl.gz').read_bytes()).splitlines()]
    changes=[];summaries=[]
    for year in ['2020','2022','2024']:
        rr=[r for r in allrows if year in r['source_id']];root={(r['fields']['contest'],r['fields']['candidate'],r['fields']['reporting_code']):r for r in rr if '/'not in r['member']}
        nested=[r for r in rr if '/'in r['member'] and 'setup'not in r['member'].lower()]
        for row in nested:
            f=row['fields']
            if f['contest_title'].strip() not in (['Governor']if year=='2022' else ['Senator in Congress','Presidential Electors For:']):continue
            baseline=root[(f['contest'],f['candidate'],f['reporting_code'])]
            for field in ['total']+['group_'+str(i) for i in range(1,15)]:
                if f[field]!=baseline['fields'][field]:changes.append(dict(year=year,root_key=baseline['key'],nested_key=row['key'],field=field,root_raw=baseline['fields'][field],nested_raw=f[field]))
        groups=collections.defaultdict(lambda:[0]*15)
        for row in rr:
            f=row['fields'];title=f['contest_title'].strip()
            if title not in (['Governor']if year=='2022' else ['Senator in Congress','Presidential Electors For:']):continue
            key=(row['member'],f['contest'],f['candidate'],f['party'],f['candidate_name']);v=[int(f['total'])]+[int(f['group_'+str(i)])for i in range(1,15)];groups[key]=[a+b for a,b in zip(groups[key],v)]
        summaries.extend(dict(year=year,member=k[0],contest=k[1],candidate=k[2],party=k[3],candidate_name=k[4],total_and_14groups=v) for k,v in groups.items())
    dump(ROOT/'extracts/archive-view-comparison.json',dict(nonadditive=True,interpretation='Root matches independent Board controls; nested/setup are retained separate views. No cause, test designation or chronology inferred from names/ZIP clocks.',differing_selected_row_counts={y:len({r['root_key'] for r in changes if r['year']==y})for y in ['2020','2022','2024']},candidate_view_controls=summaries,differing_selected_numeric_fields=changes))
    dump(ROOT/'source/method-scopes.json',dict(format2020=dict(source_id='ri-2020-observed-format-description',labels=['Election Day','Mail Ballots']+[None]*12,third_slot='unlabelled in the linked 2016 format PDF'),format2022_and2024=dict(source_id='ri-2022-description',labels=['Election Day','Mail Ballots','Early Voting']+[None]*11),html2020=dict(source_id='ri-2020-observed-state-summary',labels=['Polling place','Mail ballots','Emergency ballots']),html2022=dict(source_id='ri-2022-observed-historical-seed',labels=['Polling place','Mail ballots','Early Voting']),html2024=dict(source_id='ri-2024-general-old-authority',labels=['Polling place','Mail ballots','Early Voting']),workbook2020=dict(source_id='board2020-xlsx',columns=['Total','Election Day','Mail','Emergency']),workbook2022=dict(source_id='board2022-xlsx',columns=['Total','Election Day','Mail','Early Voting']),workbook2024=dict(source_id='board2024-xlsx',columns=['Total','Election Day','Mail','Early Voting']),rule='14 numbered slots are preserved. Labels are publication-specific, not cross-year/current-method aliases. Blank labels remain null; literal numeric zeroes are retained. Registration method zeroes do not define registration by voting method.'))
    print('Archive selected numeric differences',dict(collections.Counter(r['year']for r in changes)))
if __name__=='__main__':run()
