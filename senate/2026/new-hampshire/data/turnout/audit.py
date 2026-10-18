#!/usr/bin/env python3
"""Document administrative equations, source positions and primary conflicts."""
import collections
import gzip
import html
import json
import re
import sys
sys.dont_write_bytecode = True
from extract import ROOT, dump, sha


def main():
    controls=json.loads((ROOT/'controls.json').read_text())
    reconciliations=json.loads((ROOT/'reconciliation.json').read_text())
    result=[]
    for sid,c in controls.items():
        if 'ballots-cast' not in sid and 'checklist' not in sid:continue
        rows=[json.loads(x)for x in gzip.decompress((ROOT/'native'/f'{sid}.jsonl.gz').read_bytes()).splitlines()]
        rr=next(x for x in reconciliations if x['source_id']==sid)
        checks=[]
        for scope,rs in [('native',rows),('county_footer',c['footers']),('summary',list(c['summary'].values()))]:
            for r in rs:
                f=r['fields'];parts=['regular','absentee']if 'ballots-cast'in sid else ['republican','democratic','undeclared']
                total='ballots_total'if 'ballots-cast'in sid else 'checklist_total'
                for equation,pp,tt in [('method'if total=='ballots_total'else 'checklist_party',parts,total),*([('polling_place_registrations',['polling_place_registered_republican','polling_place_registered_democratic','polling_place_registered_undeclared'],'polling_place_registered_total')]if 'polling_place_registered_republican'in f else [])]:
                    available=all(f.get(k)is not None for k in pp+[tt])
                    delta=sum(f[k]for k in pp)-f[tt]if available else None
                    if delta!=0:
                        checks.append(dict(scope=scope,county=r['county'],native_label=r['native_label'],locator=r['source_locator'],equation=equation,components={k:f.get(k)for k in pp},reported_total=f.get(tt),components_minus_reported_total=delta,status='source_discrepancy_retained'if available else 'unavailable_not_zero'))
        result.append(dict(source_id=sid,native_rows=len(rows),state_summary=rr['state'],native_numeric_sums=rr['native_numeric_sums'],native_minus_state=rr['native_minus_state'],county_disagreements=[x for x in rr['counties']if any(v not in [0,None]for v in list(x['detail_minus_footer'].values())+list(x['footer_minus_summary'].values()))],equation_disagreements=checks))
    dump('administrative-audit.json',result)
    shared=json.loads((ROOT/'source/shared-originals.json').read_text())
    own=[]
    for p in sorted((ROOT/'source').glob('*.json')):
        m=json.loads(p.read_text())
        if isinstance(m,dict)and 'body_path'in m:own.append(m)
    ids={m['id']for m in shared+own}
    inventory=[]
    for m in shared+own:
        sid=m['id'];url=m.get('requested_url',m.get('url'));headers=m.get('headers',{})
        if 'headers_path'in m:
            headers=(ROOT/'source'/m['headers_path']).read_text()
            lm=re.findall(r'(?im)^(?:x-archive-orig-)?last-modified:\s*(.*)$',headers)
            mem=re.findall(r'(?im)^memento-datetime:\s*(.*)$',headers)
        else:
            lm=[v for k,v in headers.items()if k.lower()in ['last-modified','x-archive-orig-last-modified']]
            mem=[v for k,v in headers.items()if k.lower()=='memento-datetime']
        archive=re.search(r'/web/(\d{14})id_/(.*)',url or '')
        parents=[]
        if m.get('parent_source_id'):parents.append(dict(id=m['parent_source_id'],retained=m['parent_source_id']in ids))
        if sid=='sos-2024-president-archived-original':parents.extend([dict(id='archive-cdx-2024-president-xls',retained=True),dict(id='archived-2024-results-index',retained=True)])
        if sid.startswith('sos-archived-2022-'):parents.append(dict(id='archive-cdx-2022-inline-senate',retained=True))
        if sid=='sos-2020-senate-archived-original':parents.append(dict(id='archive-cdx-2020-senate-pdf',retained=True))
        inventory.append(dict(source_id=sid,requested_url=url,final_url=m.get('final_url'),retrieved_utc=m.get('retrieved_utc',m.get('retrieved_at_utc')),http_status=m.get('status'),original_url=archive[2]if archive else url,archive_capture=archive[1]if archive else None,last_modified_headers=lm,memento_headers=mem,parent_chain=parents,original_sha256=m.get('decoded_original_sha256',m.get('raw_sha256')),original_bytes=m.get('decoded_original_bytes',m.get('bytes')),stored_sha256=m['stored_sha256'],stored_bytes=len((ROOT/m['shared_path']).read_bytes())if 'shared_path'in m else m.get('stored_bytes'),path=m['shared_path']if 'shared_path'in m else 'source/'+m['body_path'],metadata_path='source/shared-originals.json'if 'shared_path'in m else 'source/'+sid+'.json',status_scope='Official historical archived original when usable; a failed body is access evidence, never data.',clock_limit='Capture/Last-Modified/retrieval/election header do not establish correction cause or release chronology.'))
    dump('source-inventory.json',inventory)
    candidates=[]
    identities={'harris_walz':('Kamala D. Harris and Tim Walz','d','Democratic','printed_ticket'),'trump_vance':('Donald J. Trump and JD Vance','r','Republican','printed_ticket'),'oliver_ter_maat':('Chase Oliver and Mike ter Maat','l','Libertarian','printed_ticket'),'stein_ware':('Jill Stein and Rudolph Ware','g','Green','printed_ticket'),'bolduc':('Donald C. Bolduc','r','Republican','printed_candidate'),'hassan':('Maggie Hassan','d','Democratic','printed_candidate'),'kauffman':('Jeremy Kauffman','l','Libertarian','printed_candidate'),'messner':('Corky Messner','r','Republican','printed_candidate'),'shaheen':('Jeanne Shaheen','d','Democratic','printed_candidate'),'odonnell':("Justin O'Donnell",'l / lib','Libertarian','printed_candidate'),'generic_write_ins':('Write-Ins',None,None,'generic_write_in_scope_unallocated'),'scatter':('Scatter',None,None,'generic_scatter_scope_unallocated'),'undervotes':('Undervotes',None,None,'noncandidate_undervote'),'overvotes':('Overvotes',None,None,'noncandidate_overvote')}
    for sid,c in controls.items():
        if 'ballots-cast'in sid or 'checklist'in sid:continue
        headerrows=[]
        path=ROOT/'extracts'/f'{sid}-rows.jsonl.gz'
        if path.exists():
            for r in [json.loads(x)for x in gzip.decompress(path.read_bytes()).splitlines()]:
                label=str(r['values'][0]).strip()if r['values']else ''
                if label=='Summary By Counties'or label.endswith(' County'):
                    headerrows.append(dict(sheet=r['sheet'],source_row=r['source_row'],literal_header_cells=r['values']))
        else:
            path=ROOT/'extracts'/f'{sid}-lines.jsonl.gz'
            headerrows=[r for r in [json.loads(x)for x in gzip.decompress(path.read_bytes()).splitlines()]if any(k in r['text']for k in ['Messner,','Shaheen,',"O'Donnell,",'Bolduc,','Hassan,','Kauffman,'])]
        fields=[]
        for k,v in c['summary']['TOTALS']['fields'].items():
            name,code,party,role=identities[k]
            fields.append(dict(project_field_key=k,source_numeric_candidate_id=None,reported_name=name,source_party_code=code,party_expansion=party,role=role,statewide_source_count=v,named_valid_write_in_allocation='not supplied'if k in ['generic_write_ins','scatter']else 'not applicable'))
        candidates.append(dict(source_id=sid,fields=fields,literal_headers=headerrows,identity_scope='Project semantic keys map distinct actual header fields. Every repeated sheet/column header remains preserved, no source candidate key is dropped or added.'))
    dump('contest-candidates.json',candidates)
    body=gzip.decompress((ROOT/'source/archived-2024-results-index.body.gz').read_bytes())
    meta=json.loads((ROOT/'source/archived-2024-results-index.json').read_text())
    if meta['http_content_decoding']=='gzip':body=gzip.decompress(body)
    links=[]
    for match in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',body.decode(),re.S):
        if re.search('president|ballots-cast|checklist',match[1],re.I):links.append(dict(literal_href=html.unescape(match[1]),anchor_text=html.unescape(re.sub('<[^>]+>','',match[2])),source_character_position=match.start()))
    dump('source/official-index-links.json',dict(source_id='archived-2024-results-index',decoded_original_sha256=meta['decoded_original_sha256'],links=links))
    # Preserve current official indexed observations even when direct body is a
    # retained 403. Do not label an indexed excerpt as downloaded original bytes.
    dump('source/indexed-official-observations.json',dict(observed_date_utc='2026-10-18',method='Web search exposed current indexed official text; direct requests separately retained.',observations=[dict(url='https://www.sos.nh.gov/elections/2026-2027-political-calendar',fields=dict(state_primary_date='2026-09-08',general_date='2026-11-03'),original_body_retrieved=False),dict(url='https://www.sos.nh.gov/2024-general-election-results',fields=dict(controls=['Ballots Cast','Names on Checklist','President','Governor','House District 1','House District 2'],senate_contest_listed=False),original_body_retrieved=False,archive_recovered='archived-2024-results-index'),dict(url='https://www.sos.nh.gov/elections/2020-election-results/2020-general-election-results',fields=dict(source_status_label='Official Results',separate_products=['Ballots Cast','Names on Checklist (Registered Voters)','President','President Write-ins','Senate']),original_body_retrieved=False)]))
    print(json.dumps(dict(administrative_sources=len(result),retained_request_inventory=len(inventory),known_equation_disagreements=sum(len(x['equation_disagreements'])for x in result))))


if __name__=='__main__':main()
