"""Deterministic report from retained source findings; no network."""
from acquire import *
from build import NOTES
def main():
    parents=json.loads((HERE/'parent-index.json').read_bytes());rows=[]
    for p in parents:
        v=json.loads((STATE/p['path']).read_bytes());d=v['full_current_SOS_directory_block'];link=d['landing_link']
        label=d['county_label'];local=f"[{label}](data/results-sources/parents/{v['frozen_county_context']['fips']}.json)"
        href=f"[{link['label']}]({link['href']})" if link else 'Website href absent'
        rows.append('| '+ ' | '.join([local,d['clerk_label'],href,NOTES[p['directory_index']]])+' |')
    table='| County / complete investigation | Exact SOS clerk label | Exact printed website label and literal href | Independently followed chain and limit |\n|---|---|---|---|\n'+'\n'.join(rows)
    rs=[json.loads(f.read_bytes()) for f in (HERE/'receipts').glob('*.json')]
    lo=min(r['observation_started_utc'] for r in rs);hi=max(r['observation_finished_utc'] for r in rs)
    snapshot=f"The retained raw acquisition window is **{lo} through {hi}**. There are **{len(rs)} actual bounded request receipts**; successful responses, redirects, failures, public export attempts and legal originals each retain their own stage and scope. This is a source snapshot, not measured election-night cadence."
    negative=json.loads((HERE/'negative-fixtures.json').read_bytes())['negative_cases']
    s=(HERE/'report-template.md').read_text().replace('@COUNTIES@',table).replace('@SNAPSHOT@',snapshot).replace('@NEGCASES@',str(negative))
    (STATE/'official-results.md').write_text(s)
if __name__=='__main__':main()
